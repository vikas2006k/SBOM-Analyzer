import os
import json
import csv
import re
import networkx as nx
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class ParserService:
    """Service handling parsing logic and structural validations for multiple SBOM formats."""

    @staticmethod
    def parse_purl(purl):
        """Parse Package URL (purl) to extract name, version, and ecosystem."""
        if not purl or not isinstance(purl, str):
            return None, None, "unknown"
        
        match = re.match(r'^pkg:([a-zA-Z0-9_\-\.]+)/((?:[^@#\?]+/)?)([^@#\?]+)@([^#\?]+)', purl)
        if match:
            ecosystem = match.group(1)
            namespace = match.group(2)
            name = match.group(3)
            version = match.group(4)
            if namespace:
                namespace_clean = namespace.strip('/')
                full_name = f"{namespace_clean}/{name}"
            else:
                full_name = name
            return full_name, version, ecosystem
        
        return purl, "unknown", "unknown"

    @classmethod
    def parse_cyclonedx(cls, data):
        """Parse CycloneDX JSON SBOM structure."""
        logger.info("Parsing CycloneDX JSON SBOM...")
        metadata = data.get("metadata", {})
        root_component = metadata.get("component", {})
        app_name = root_component.get("name", "Unknown CycloneDX App")
        app_version = root_component.get("version", "1.0.0")
        
        libraries = []
        purl_map = {}
        
        root_purl = root_component.get("purl") or f"pkg:application/{app_name}@{app_version}"
        purl_map[root_component.get("bom-ref", root_purl)] = (app_name, app_version, "application")
        
        components = data.get("components", [])
        for comp in components:
            name = comp.get("name")
            version = comp.get("version")
            if not name or not version:
                continue
                
            purl = comp.get("purl")
            parsed_name, parsed_version, ecosystem = cls.parse_purl(purl)
            
            final_name = parsed_name if parsed_name else name
            final_version = parsed_version if parsed_version else version
            if ecosystem == "unknown":
                ecosystem = "npm"
                
            license_name = "Unknown"
            licenses = comp.get("licenses", [])
            if licenses:
                lic_data = licenses[0].get("license", {})
                license_name = lic_data.get("id") or lic_data.get("name") or "Unknown"
                
            libraries.append({
                "name": final_name,
                "version": final_version,
                "ecosystem": ecosystem,
                "license_name": license_name
            })
            
            bom_ref = comp.get("bom-ref") or purl or f"{final_name}@{final_version}"
            purl_map[bom_ref] = (final_name, final_version, ecosystem)
            
        dependency_relationships = []
        relationships = data.get("dependencies", [])
        for rel in relationships:
            parent_ref = rel.get("ref")
            depends_on = rel.get("dependsOn", [])
            
            if not parent_ref:
                continue
                
            parent_info = purl_map.get(parent_ref)
            if not parent_info:
                p_name, p_ver, p_eco = cls.parse_purl(parent_ref)
                if p_name:
                    parent_info = (p_name, p_ver, p_eco)
                else:
                    continue
                    
            parent_name, parent_ver, _ = parent_info
            
            for child_ref in depends_on:
                child_info = purl_map.get(child_ref)
                if not child_info:
                    c_name, c_ver, _ = cls.parse_purl(child_ref)
                    if c_name:
                        child_info = (c_name, c_ver, "unknown")
                    else:
                        continue
                        
                child_name, child_ver, _ = child_info
                if parent_name == child_name and parent_ver == child_ver:
                    continue
                    
                dependency_relationships.append({
                    "parent_name": parent_name,
                    "parent_version": parent_ver,
                    "child_name": child_name,
                    "child_version": child_ver
                })
                
        return {
            "application_name": app_name,
            "application_version": app_version,
            "libraries": libraries,
            "dependencies": dependency_relationships
        }

    @classmethod
    def parse_spdx(cls, data):
        """Parse SPDX JSON SBOM structure."""
        logger.info("Parsing SPDX JSON SBOM...")
        app_name = data.get("name", "Unknown SPDX App")
        app_version = "1.0.0"
        
        packages = data.get("packages", [])
        libraries = []
        spdx_id_map = {}
        
        for pkg in packages:
            name = pkg.get("name")
            version = pkg.get("versionInfo") or "unknown"
            spdx_id = pkg.get("SPDXID")
            
            if not name or not spdx_id:
                continue
                
            purposes = pkg.get("primaryPackagePurpose", [])
            is_app = False
            if isinstance(purposes, list):
                is_app = "APPLICATION" in purposes
            elif isinstance(purposes, str):
                is_app = purposes == "APPLICATION"
                
            if is_app or name == app_name:
                app_name = name
                app_version = version
                spdx_id_map[spdx_id] = (name, version, "application")
                continue
                
            license_name = pkg.get("licenseDeclared") or pkg.get("licenseConcluded") or "Unknown"
            ecosystem = "npm"
            
            purl = None
            external_refs = pkg.get("externalRefs", [])
            for ref in external_refs:
                if ref.get("referenceType") == "purl":
                    purl = ref.get("referenceLocator")
                    break
                    
            if purl:
                parsed_name, parsed_version, eco = cls.parse_purl(purl)
                if parsed_name:
                    name = parsed_name
                    version = parsed_version
                    ecosystem = eco
            
            libraries.append({
                "name": name,
                "version": version,
                "ecosystem": ecosystem,
                "license_name": license_name
            })
            spdx_id_map[spdx_id] = (name, version, ecosystem)
            
        dependency_relationships = []
        relationships = data.get("relationships", [])
        for rel in relationships:
            rel_type = rel.get("relationshipType")
            if rel_type != "DEPENDS_ON":
                continue
                
            parent_id = rel.get("spdxElementId")
            child_id = rel.get("relatedSpdxElement")
            
            parent_info = spdx_id_map.get(parent_id)
            child_info = spdx_id_map.get(child_id)
            
            if parent_info and child_info:
                p_name, p_ver, _ = parent_info
                c_name, c_ver, _ = child_info
                if p_name == c_name and p_ver == c_ver:
                    continue
                    
                dependency_relationships.append({
                    "parent_name": p_name,
                    "parent_version": p_ver,
                    "child_name": c_name,
                    "child_version": c_ver
                })
                
        return {
            "application_name": app_name,
            "application_version": app_version,
            "libraries": libraries,
            "dependencies": dependency_relationships
        }

    @classmethod
    def parse_csv(cls, file_path, app_name="CSV App", app_version="1.0.0"):
        """Parse CSV dependencies."""
        logger.info("Parsing CSV SBOM...")
        libraries = []
        dependency_relationships = []
        seen_libs = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                required_cols = {'library_name', 'version'}
                if not required_cols.issubset(set(reader.fieldnames or [])):
                    raise ValueError(f"CSV missing required columns: {required_cols}")
                    
                for row in reader:
                    lib_name = row.get("library_name")
                    version = row.get("version")
                    ecosystem = row.get("ecosystem") or "npm"
                    license_name = row.get("license") or "Unknown"
                    
                    if not lib_name or not version:
                        continue
                        
                    lib_key = (lib_name, version, ecosystem)
                    if lib_key not in seen_libs:
                        libraries.append({
                            "name": lib_name,
                            "version": version,
                            "ecosystem": ecosystem,
                            "license_name": license_name
                        })
                        seen_libs.add(lib_key)
                        
                    parent_name = row.get("parent_name")
                    parent_version = row.get("parent_version")
                    
                    if parent_name and parent_version:
                        dependency_relationships.append({
                            "parent_name": parent_name,
                            "parent_version": parent_version,
                            "child_name": lib_name,
                            "child_version": version
                        })
                    else:
                        dependency_relationships.append({
                            "parent_name": app_name,
                            "parent_version": app_version,
                            "child_name": lib_name,
                            "child_version": version
                        })
                        
            return {
                "application_name": app_name,
                "application_version": app_version,
                "libraries": libraries,
                "dependencies": dependency_relationships
            }
        except Exception as e:
            logger.error(f"CSV Parse error: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to parse CSV: {str(e)}")

    @classmethod
    def parse_custom_json(cls, data):
        """Parse custom standard JSON format mapping."""
        app_name = data.get("application_name", "Unknown Custom App")
        app_version = data.get("application_version", "1.0.0")
        
        libraries = []
        for lib in data.get("libraries", []):
            libraries.append({
                "name": lib.get("name"),
                "version": lib.get("version"),
                "ecosystem": lib.get("ecosystem", "npm"),
                "license_name": lib.get("license", "Unknown")
            })
            
        dependency_relationships = []
        for rel in data.get("dependencies", []):
            dependency_relationships.append({
                "parent_name": rel.get("parent_name"),
                "parent_version": rel.get("parent_version"),
                "child_name": rel.get("child_name"),
                "child_version": rel.get("child_version")
            })
            
        return {
            "application_name": app_name,
            "application_version": app_version,
            "libraries": libraries,
            "dependencies": dependency_relationships
        }

    @classmethod
    def parse_sbom_file(cls, file_path, file_format, app_name=None, app_version=None):
        """Dynamic entrypoint dispatcher for parsing file based on format."""
        if file_format.lower() == 'csv':
            return cls.parse_csv(file_path, app_name or "CSV Application", app_version or "1.0.0")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"Invalid JSON file format: {str(e)}")
            
        if "bomFormat" in data and data.get("bomFormat") == "CycloneDX":
            return cls.parse_cyclonedx(data)
        elif "spdxVersion" in data:
            return cls.parse_spdx(data)
        elif "application_name" in data:
            return cls.parse_custom_json(data)
        else:
            raise ValueError("Unsupported SBOM JSON structure type. Must be CycloneDX, SPDX, or custom schema.")

    @classmethod
    def validate_sbom(cls, parsed_data):
        """Run structural validations on parsed SBOM components.
        Checks for:
        - Required fields
        - Version format (Semantic pattern match warnings)
        - Duplicate libraries
        - Missing parent/child libraries declarations
        - Circular relationships
        - Invalid or placeholder licenses
        Returns validation report dict.
        """
        logger.info("Executing validation on parsed SBOM...")
        errors = []
        warnings = []
        
        app_name = parsed_data.get("application_name")
        app_version = parsed_data.get("application_version")
        
        if not app_name:
            errors.append("Application name is missing from SBOM metadata")
        if not app_version:
            errors.append("Application version is missing from SBOM metadata")
            
        libraries = parsed_data.get("libraries", [])
        dependencies = parsed_data.get("dependencies", [])
        
        # Track components defined
        declared_libs = set()
        seen_duplicates = set()
        
        # Compile keys (name, version)
        for lib in libraries:
            name = lib.get("name")
            version = lib.get("version")
            license_name = lib.get("license_name", "Unknown")
            
            if not name or not version:
                errors.append(f"Library definition lacks required name/version fields: {lib}")
                continue
                
            lib_key = (name, version)
            if lib_key in declared_libs:
                seen_duplicates.add(lib_key)
            declared_libs.add(lib_key)
            
            # Semantic version format warnings check
            semver_regex = r'^\d+\.\d+(\.\d+)?(-[a-zA-Z0-9\.]+)?$'
            if not re.match(semver_regex, version):
                warnings.append(f"Library '{name}' has non-standard version formatting: '{version}'")
                
            # Invalid/Placeholder license check
            if license_name.lower() in {'unknown', 'none', 'null', '', 'invalid'}:
                warnings.append(f"Library '{name}@{version}' has an unknown or placeholder license")
                
        # Register duplicate warnings
        for dup in seen_duplicates:
            warnings.append(f"Duplicate library definition detected for component '{dup[0]}@{dup[1]}'")
            
        # Verify edge declarations
        dg = nx.DiGraph()
        # Add root application context to graph to anchor relationships
        dg.add_node((app_name, app_version))
        
        for dep in dependencies:
            p_name = dep.get("parent_name")
            p_ver = dep.get("parent_version")
            c_name = dep.get("child_name")
            c_ver = dep.get("child_version")
            
            if not p_name or not p_ver or not c_name or not c_ver:
                errors.append(f"Invalid dependency edge lacking name/version components: {dep}")
                continue
                
            p_key = (p_name, p_ver)
            c_key = (c_name, c_ver)
            
            # Check missing component definitions
            # Root app is not defined in components, so exclude it
            if p_key != (app_name, app_version) and p_key not in declared_libs:
                warnings.append(f"Dependency parent '{p_name}@{p_ver}' is not declared in libraries inventory")
            if c_key not in declared_libs:
                warnings.append(f"Dependency child '{c_name}@{c_ver}' is not declared in libraries inventory")
                
            dg.add_edge(p_key, c_key)
            
        # Circular References cycle check
        try:
            cycles = list(nx.simple_cycles(dg))
            if cycles:
                for cycle in cycles:
                    cycle_str = " -> ".join([f"{n[0]}@{n[1]}" for n in cycle])
                    errors.append(f"Circular dependency cycle detected: {cycle_str} -> {cycle[0][0]}@{cycle[0][1]}")
        except Exception as ge:
            logger.error(f"Cycle check error: {str(ge)}")
            
        is_valid = len(errors) == 0
        
        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "metrics": {
                "libraries_count": len(libraries),
                "dependencies_count": len(dependencies),
                "has_cycles": len(errors) > 0 and any("Circular" in e for e in errors)
            }
        }
