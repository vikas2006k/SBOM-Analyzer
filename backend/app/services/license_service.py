import re
from app.database.connection import db
from app.models.license import License
from app.models.license_rule import LicenseRule
from app.models.dependency import Dependency
from app.models.application import Application
from app.models.library import Library
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class LicenseService:
    """Service handling licenses audits, compliance checking, and compatibility policies mapping."""

    def __init__(self):
        pass

    def detect_category(self, license_name):
        """Map license identifier string to standard SPDX category."""
        if not license_name:
            return "Unknown"
        
        license_name = license_name.strip()
        # Find matching license definition in DB
        lic = License.query.filter(
            (License.spdx_identifier.ilike(license_name)) |
            (License.name.ilike(license_name))
        ).first()
        
        if lic:
            return lic.category
            
        # Fallback keyword checks
        name_lower = license_name.lower()
        if any(x in name_lower for x in ['gpl', 'agpl', 'gnu general']):
            if 'lesser' in name_lower or 'lgpl' in name_lower:
                return "Weak-Copyleft"
            return "Copyleft"
        elif any(x in name_lower for x in ['mit', 'apache', 'bsd', 'isc', 'unlicense', 'wtfpl']):
            return "Permissive"
        elif any(x in name_lower for x in ['mpl', 'cddl', 'epl', 'eclipse']):
            return "Weak-Copyleft"
        elif any(x in name_lower for x in ['proprietary', 'commercial', 'closed']):
            return "Proprietary"
            
        return "Unknown"

    def audit_licenses(self, application_id):
        """Execute license scanning and compliance evaluation for all project dependencies."""
        logger.info(f"Auditing licenses for application {application_id}...")
        
        app = db.session.get(Application, application_id)
        if not app:
            raise ValueError(f"Application with ID {application_id} not found")
            
        edges = Dependency.query.filter_by(application_id=application_id, is_deleted=False).all()
        libraries = {edge.child_library for edge in edges if edge.child_library}
        
        # Load rules from DB
        rules = {rule.license_category: rule for rule in LicenseRule.query.all()}
        
        conflicts = []
        warnings = []
        recommendations = []
        licenses_count = {}
        
        for lib in libraries:
            license_name = lib.license_name or "Unknown"
            
            # Detect dual-licensing (e.g. "GPL-2.0 OR MIT", "Dual MIT/GPL")
            is_dual = False
            dual_options = []
            if any(x in license_name.upper() for x in [" OR ", " AND ", " / ", "DUAL"]):
                is_dual = True
                # Extract identifiers
                tokens = re.split(r'\s+OR\s+|\s+AND\s+|/|\s+DUAL\s+', license_name, flags=re.IGNORECASE)
                dual_options = [t.strip().strip("()") for t in tokens if t.strip()]
                
            # If dual licensed, let's see if one of the options is permissive
            resolved_category = "Unknown"
            if is_dual:
                categories = [self.detect_category(opt) for opt in dual_options]
                # If any option is permissive, recommend using the permissive option
                if "Permissive" in categories:
                    permissive_idx = categories.index("Permissive")
                    resolved_category = "Permissive"
                    recommendations.append(
                        f"Library '{lib.name}@{lib.version}' is dual-licensed ({license_name}). "
                        f"Select the permissive option '{dual_options[permissive_idx]}' to ensure commercial compatibility."
                    )
                else:
                    resolved_category = categories[0]
            else:
                resolved_category = self.detect_category(license_name)
                
            # Track count
            licenses_count[license_name] = licenses_count.get(license_name, 0) + 1
            
            # Get rule parameters
            rule = rules.get(resolved_category)
            if not rule:
                # Default safety fallback
                rule = rules.get("Unknown") or LicenseRule(commercial_allowed=False, proprietary_linkable=False)
                
            # Commercial compliance check (only for High/Critical apps with Copyleft licenses)
            is_commercial_app = app.business_criticality in ['High', 'Critical']
            
            if is_commercial_app and not rule.commercial_allowed and resolved_category not in ('Unknown',):
                conflict_msg = (
                    f"Compliance Conflict: License '{license_name}' (Category: {resolved_category}) on "
                    f"library '{lib.name}@{lib.version}' violates the commercial policy of application "
                    f"with business criticality '{app.business_criticality}'."
                )
                conflicts.append({
                    "library_name": lib.name,
                    "library_version": lib.version,
                    "license_name": license_name,
                    "category": resolved_category,
                    "type": "Commercial Policy Violation",
                    "description": conflict_msg
                })
                recommendations.append(
                    f"Replace '{lib.name}@{lib.version}' ({license_name}) with a permissively licensed alternative, "
                    f"or isolate it in a separate service to avoid GPL viral compliance obligations."
                )
                
            # Proprietary linking check — Copyleft is ALWAYS a linking risk, regardless of app criticality
            if resolved_category == "Copyleft" and not rule.proprietary_linkable:
                linking_msg = (
                    f"Linking Risk: Strong Copyleft License '{license_name}' on library '{lib.name}@{lib.version}' "
                    f"is dynamically/statically linked. This requires the parent application source code to be open-sourced under the same terms."
                )
                # Only add if not already in conflicts to avoid duplicates
                already_added = any(c['library_name'] == lib.name and c['library_version'] == lib.version and c['type'] == 'Viral Copyleft Linking Warning' for c in conflicts)
                if not already_added:
                    conflicts.append({
                        "library_name": lib.name,
                        "library_version": lib.version,
                        "license_name": license_name,
                        "category": resolved_category,
                        "type": "Viral Copyleft Linking Warning",
                        "description": linking_msg
                    })
                    recommendations.append(
                        f"Replace or isolate '{lib.name}@{lib.version}' ({license_name}) — GPL/AGPL viral terms require your application to also be open-source."
                    )
                
            # Unknown licenses → warnings only (require manual legal review)
            if resolved_category == "Unknown":
                warnings.append({
                    "library_name": lib.name,
                    "library_version": lib.version,
                    "license_name": license_name,
                    "description": f"Library '{lib.name}@{lib.version}' has an unidentified license ('{license_name}'). Manual legal review recommended."
                })
                recommendations.append(
                    f"Audit the source code repository of '{lib.name}@{lib.version}' to locate the LICENSE file and manually classify the license."
                )
                
        # Generate summary score (100 down to 0)
        penalty = (len(conflicts) * 20) + (len(warnings) * 5)
        license_score = max(0, 100 - penalty)
        
        return {
            "application_id": application_id,
            "license_score": license_score,
            "conflicts_count": len(conflicts),
            "warnings_count": len(warnings),
            "conflicts": conflicts,
            "warnings": warnings,
            "recommendations": recommendations,
            "license_distribution": licenses_count
        }

    def check_compliance_conflicts(self, license_names):
        """Validate if a list of licenses violates policies."""
        conflicted = False
        conflicts = []
        
        # Load rules from DB
        rules = {rule.license_category: rule for rule in LicenseRule.query.all()}
        
        for name in license_names:
            category = self.detect_category(name)
            rule = rules.get(category)
            
            if rule and not rule.commercial_allowed:
                conflicted = True
                conflicts.append({
                    "license_name": name,
                    "category": category,
                    "description": f"License category '{category}' is flagged as restricted/incompatible under default policy rules."
                })
                
        return {
            "conflicted": conflicted,
            "conflicts": conflicts
        }

