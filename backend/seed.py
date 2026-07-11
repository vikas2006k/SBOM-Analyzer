import os
import sys
from datetime import datetime, timedelta

# Adjust path to import app module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database.connection import db
from app.models.role import Role
from app.models.user import User
from app.models.license import License
from app.models.license_rule import LicenseRule
from app.models.vulnerability import Vulnerability
from app.models.maintenance import MaintenanceRecord
from app.models.application import Application
from app.utils.crypto_helper import CryptoHelper

def seed_db():
    app = create_app(os.getenv("APP_ENV", "development"))
    with app.app_context():
        print("Recreating database tables...")
        db.create_all()
        
        # 1. Seed Roles
        print("Seeding roles...")
        roles_data = [
            {"name": "admin", "permissions": '["all"]'},
            {"name": "security_officer", "permissions": '["read", "write_rules", "recalculate"]'},
            {"name": "developer", "permissions": '["read", "upload"]'},
            {"name": "viewer", "permissions": '["read"]'}
        ]
        
        roles = {}
        for r_data in roles_data:
            role = Role.query.filter_by(name=r_data["name"]).first()
            if not role:
                role = Role(name=r_data["name"], permissions=r_data["permissions"])
                db.session.add(role)
            roles[r_data["name"]] = role
        db.session.commit()
        
        # Reload roles to get IDs
        for name in roles:
            roles[name] = Role.query.filter_by(name=name).first()

        # 2. Seed Users
        print("Seeding users...")
        users_data = [
            {"username": "admin", "email": "admin@sentinel.io", "password": "admin123", "role": "admin"},
            {"username": "security", "email": "security@sentinel.io", "password": "security123", "role": "security_officer"},
            {"username": "developer", "email": "developer@sentinel.io", "password": "developer123", "role": "developer"},
            {"username": "viewer", "email": "viewer@sentinel.io", "password": "viewer123", "role": "viewer"}
        ]
        
        for u_data in users_data:
            user = User.query.filter_by(username=u_data["username"]).first()
            if not user:
                hashed = CryptoHelper.hash_password(u_data["password"])
                user = User(
                    username=u_data["username"],
                    email=u_data["email"],
                    password_hash=hashed,
                    role_id=roles[u_data["role"]].id
                )
                db.session.add(user)
        db.session.commit()

        # Seed Applications
        print("Seeding applications...")
        apps_data = [
            {"id": 1, "name": "PaymentGateway", "version": "1.0.0", "business_criticality": "High", "description": "Enterprise Payment Gateway Service Processing Transactions"},
            {"id": 2, "name": "AuthService", "version": "1.2.0", "business_criticality": "Critical", "description": "Identity Provider and Access Control Token Service"},
            {"id": 3, "name": "PaymentAPI", "version": "2.0.0", "business_criticality": "Medium", "description": "REST APIs interface for financial operations"}
        ]
        for a_data in apps_data:
            app_obj = db.session.get(Application, a_data["id"])
            if not app_obj:
                app_obj = Application(
                    id=a_data["id"],
                    name=a_data["name"],
                    version=a_data["version"],
                    business_criticality=a_data["business_criticality"],
                    description=a_data["description"]
                )
                db.session.add(app_obj)
        db.session.commit()

        # 3. Seed License Rules (License Compliance Policies)
        print("Seeding license rules...")
        rules_data = [
            {
                "license_category": "Permissive", 
                "commercial_allowed": True, 
                "proprietary_linkable": True,
                "description": "Permissive licenses allow usage, modification, and proprietary distribution without source code disclosure requirements."
            },
            {
                "license_category": "Weak-Copyleft", 
                "commercial_allowed": True, 
                "proprietary_linkable": True,
                "description": "Weak copyleft licenses require library modifications to be open sourced, but allow dynamic/static linking in proprietary applications."
            },
            {
                "license_category": "Copyleft", 
                "commercial_allowed": False, 
                "proprietary_linkable": False,
                "description": "Strong copyleft licenses require any derived work or linking application to be fully licensed under the same open-source terms (GPL/AGPL)."
            },
            {
                "license_category": "Proprietary", 
                "commercial_allowed": True, 
                "proprietary_linkable": True,
                "description": "Commercial proprietary licenses govern closed-source purchased components."
            },
            {
                "license_category": "Unknown", 
                "commercial_allowed": False, 
                "proprietary_linkable": False,
                "description": "Unknown or custom licenses require security review due to undefined legal compliance implications."
            }
        ]
        
        for r in rules_data:
            rule = LicenseRule.query.filter_by(license_category=r["license_category"]).first()
            if not rule:
                rule = LicenseRule(
                    license_category=r["license_category"],
                    commercial_allowed=r["commercial_allowed"],
                    proprietary_linkable=r["proprietary_linkable"],
                    description=r["description"]
                )
                db.session.add(rule)
        db.session.commit()

        # 4. Seed Licenses
        print("Seeding licenses...")
        licenses_data = [
            {"spdx_identifier": "MIT", "name": "MIT License", "category": "Permissive"},
            {"spdx_identifier": "Apache-2.0", "name": "Apache License 2.0", "category": "Permissive"},
            {"spdx_identifier": "BSD-3-Clause", "name": "BSD 3-Clause 'New' or 'Revised' License", "category": "Permissive"},
            {"spdx_identifier": "BSD-2-Clause", "name": "BSD 2-Clause 'Simplified' License", "category": "Permissive"},
            {"spdx_identifier": "LGPL-3.0", "name": "GNU Lesser General Public License v3.0", "category": "Weak-Copyleft"},
            {"spdx_identifier": "LGPL-2.1", "name": "GNU Lesser General Public License v2.1", "category": "Weak-Copyleft"},
            {"spdx_identifier": "MPL-2.0", "name": "Mozilla Public License 2.0", "category": "Weak-Copyleft"},
            {"spdx_identifier": "GPL-3.0", "name": "GNU General Public License v3.0", "category": "Copyleft"},
            {"spdx_identifier": "GPL-2.0", "name": "GNU General Public License v2.0", "category": "Copyleft"},
            {"spdx_identifier": "AGPL-3.0", "name": "GNU Affero General Public License v3.0", "category": "Copyleft"},
            {"spdx_identifier": "Proprietary", "name": "Proprietary Commercial License", "category": "Proprietary"},
            {"spdx_identifier": "Unknown", "name": "Unidentified / Unknown License", "category": "Unknown"}
        ]
        
        for l in licenses_data:
            lic = License.query.filter_by(spdx_identifier=l["spdx_identifier"]).first()
            if not lic:
                lic = License(
                    spdx_identifier=l["spdx_identifier"],
                    name=l["name"],
                    category=l["category"]
                )
                db.session.add(lic)
        db.session.commit()

        # 5. Seed Vulnerabilities (CVE database)
        print("Seeding CVE vulnerability intelligence database...")
        vulns_data = [
            {
                "cve_id": "CVE-2021-44228",
                "cvss_score": 10.0,
                "severity": "Critical",
                "description": "Apache Log4j2 2.0-beta9 through 2.15.0 JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints.",
                "patched_version": "2.16.0"
            },
            {
                "cve_id": "CVE-2021-44832",
                "cvss_score": 6.6,
                "severity": "Medium",
                "description": "Apache Log4j2 vulnerability where an attacker with permission to modify the logging configuration file can construct a malicious configuration using a JDBC Appender with a data source referencing a JNDI URI.",
                "patched_version": "2.17.1"
            },
            {
                "cve_id": "CVE-2023-3635",
                "cvss_score": 8.1,
                "severity": "High",
                "description": "Deserialization of untrusted data in Jackson-databind before 2.15.2 allows remote code execution when specific gadgets are available in the classpath.",
                "patched_version": "2.15.2"
            },
            {
                "cve_id": "CVE-2023-34036",
                "cvss_score": 7.5,
                "severity": "High",
                "description": "Spring Security before version 6.1.2 contains a bypass vulnerability when pattern-matching path rules are mapped with double wildcards under specific URL configurations.",
                "patched_version": "3.1.3"
            },
            {
                "cve_id": "CVE-2023-51074",
                "cvss_score": 9.8,
                "severity": "Critical",
                "description": "jsonwebtoken (JWT) node module before version 9.0.1 is vulnerable to key confusion / algorithm confusion attacks causing signature verification bypass under specific key configurations.",
                "patched_version": "9.0.1"
            },
            {
                "cve_id": "CVE-2023-32681",
                "cvss_score": 6.1,
                "severity": "Medium",
                "description": "Python requests library before version 2.31.0 has a leak vulnerability where proxy authentication credentials can be leaked to downstream sites during cross-origin redirects.",
                "patched_version": "2.31.0"
            },
            {
                "cve_id": "CVE-2023-43804",
                "cvss_score": 5.3,
                "severity": "Medium",
                "description": "urllib3 before version 2.0.7 leaks the Cookie header to third-party domains on redirects if the request uses a custom Cookie header.",
                "patched_version": "2.0.7"
            },
            {
                "cve_id": "CVE-2023-46918",
                "cvss_score": 7.5,
                "severity": "High",
                "description": "Express.js framework vulnerability in query parsing logic causing potential denial of service (DoS) or unexpected parameter pollution when nested JSON query strings are parsed.",
                "patched_version": "4.18.3"
            }
        ]
        
        for v in vulns_data:
            vuln = Vulnerability.query.filter_by(cve_id=v["cve_id"]).first()
            if not vuln:
                vuln = Vulnerability(
                    cve_id=v["cve_id"],
                    cvss_score=v["cvss_score"],
                    severity=v["severity"],
                    description=v["description"],
                    patched_version=v["patched_version"]
                )
                db.session.add(vuln)
        db.session.commit()
        
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_db()
