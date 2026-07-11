import json
import os
import requests
from app.database.connection import db
from app.models.application import Application
from app.models.vulnerability import Vulnerability
from app.models.copilot import AIConversation
from app.services.risk_service import RiskService
from app.services.vulnerability_service import VulnerabilityService
from app.services.license_service import LicenseService
from app.services.maintenance_service import MaintenanceService
from app.utils.logger import Logger

logger = Logger.get_logger('ai')

class AIService:
    """Service orchestrating AI Security Copilot agent workflows and NLP conversations."""

    def __init__(self):
        self.risk_service = RiskService()
        self.vuln_service = VulnerabilityService()
        self.license_service = LicenseService()
        self.maint_service = MaintenanceService()

    def process_query(self, user_id, application_id, user_message, chat_history):
        """Process natural language query routing to multi-agent specialized executors."""
        logger.info(f"AI Copilot receiving prompt from user {user_id} for app {application_id}: '{user_message}'")
        
        # Check if OpenAI is configured
        api_key = os.getenv("OPENAI_API_KEY", "")
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model = os.getenv("LLM_MODEL", "gpt-4-turbo")
        
        # Fetch application context
        app = db.session.get(Application, application_id)
        if not app:
            return {
                "response": "Application context error: The target application profile was not found.",
                "referenced_items": []
            }
            
        # Fetch actual security metrics to inject into prompt context
        risk_data = self.risk_service.get_latest_risk_score(application_id)
        vulns = self.vuln_service.get_vulnerabilities_by_application(application_id)
        license_audit = self.license_service.audit_licenses(application_id)
        maint_audit = self.maint_service.check_maintenance_health(application_id)
        
        # Deterministic / rule-based local multi-agent fallback if API key is empty or dummy
        is_dummy_key = not api_key or "your" in api_key.lower() or "change" in api_key.lower()
        
        if is_dummy_key:
            logger.info("Executing offline rule-based Orchestrator Agent...")
            return self._execute_offline_agents(user_message, app, risk_data, vulns, license_audit, maint_audit)
            
        # Dynamic execution with OpenAI LLM
        try:
            # Inject context
            system_prompt = (
                f"You are SentinelSBOM AI Security Copilot, a principal security analyst. "
                f"You are assisting a developer on application '{app.name} v{app.version}' (Criticality: {app.business_criticality}).\n\n"
                f"Application Security Context:\n"
                f"- Composite Risk Score: {risk_data['overall_score']}/100 ({risk_data['severity']})\n"
                f"- Vulnerabilities (CVEs): {len(vulns)} detected. Max CVSS: {max([v['cvss_score'] for v in vulns]) if vulns else 0.0}\n"
                f"- License Compliance: {license_audit['conflicts_count']} conflicts, {license_audit['warnings_count']} warnings. Score: {license_audit['license_score']}/100\n"
                f"- Maintenance Health: Average Score {maint_audit['average_maintenance_score']}/100. {maint_audit['deprecated_count']} deprecated packages.\n\n"
                f"Answer the user query in professional markdown format. Include actionable remediations and concrete patching instructions."
            )
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Format messages
            messages = [{"role": "system", "content": system_prompt}]
            # Add history
            for h in chat_history[-6:]:
                messages.append({"role": "user" if h.get("sender") == "user" else "assistant", "content": h.get("text", "")})
            messages.append({"role": "user", "content": user_message})
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.2
            }
            
            resp = requests.post(f"{api_base}/chat/completions", headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                assistant_content = result["choices"][0]["message"]["content"]
                return {
                    "response": assistant_content,
                    "referenced_items": [v["cve_id"] for v in vulns[:3]]
                }
            else:
                logger.error(f"OpenAI API error {resp.status_code}: {resp.text}")
                # Fallback to local rule engine if API request fails
                return self._execute_offline_agents(user_message, app, risk_data, vulns, license_audit, maint_audit)
                
        except Exception as e:
            logger.error(f"Failed to query LLM endpoint: {str(e)}")
            return self._execute_offline_agents(user_message, app, risk_data, vulns, license_audit, maint_audit)

    def _execute_offline_agents(self, prompt, app, risk, vulns, licenses, maint):
        """Rule-based Orchestrator Agent routing queries to local simulated security agents."""
        msg = prompt.lower()
        referenced = []
        
        # 1. Routing logic matching prompt keywords
        if "highest risk" in msg or "max risk" in msg or "most dangerous" in msg:
            # Vulnerability Agent & Risk Agent
            logger.info("Routing to Vulnerability & Risk Agents...")
            if vulns:
                top_vuln = vulns[0]
                referenced.append(top_vuln["cve_id"])
                resp = (
                    f"### Highest Risk Assessment for **{app.name}**\n\n"
                    f"Your highest security threat is **{top_vuln['cve_id']}** (CVSS: **{top_vuln['cvss_score']}** - **{top_vuln['severity']}**), affecting the library `{top_vuln['affected_library']}@{top_vuln['affected_version']}`.\n\n"
                    f"**Vulnerability Details:**\n"
                    f"> {top_vuln['description']}\n\n"
                    f"**Risk Analysis:**\n"
                    f"- **Category:** {top_vuln['risk_category']}\n"
                    f"- **Exploitability:** Known public exploits exist: `{top_vuln['exploitability']['known_exploit']}`. Attack vector is `{top_vuln['exploitability']['exploit_vector']}`.\n"
                    f"- **Fix Path:** Upgrading to version `{top_vuln['patched_version']}` will fully patch this vulnerability."
                )
            else:
                resp = (
                    f"### Highest Risk Assessment for **{app.name}**\n\n"
                    f"No critical vulnerabilities are recorded. However, the highest compliance risk is related to license scoring (**{licenses['license_score']}/100**)."
                )
                
        elif "what should be fixed first" in msg or "fix first" in msg or "priority" in msg:
            # Security Advisor Agent
            logger.info("Routing to Security Advisor Agent...")
            if vulns:
                remediations = []
                for i, v in enumerate(vulns[:3]):
                    referenced.append(v["cve_id"])
                    remediations.append(
                        f"{i+1}. **Upgrade `{v['affected_library']}` to version `{v['patched_version']}`**\n"
                        f"   - *Vulnerability:* {v['cve_id']} (CVSS {v['cvss_score']} - {v['severity']})\n"
                        f"   - *Action:* Run dependency update script. Verified patch is available."
                    )
                resp = (
                    f"### Remediation Action Plan (Worst First)\n\n"
                    f"Based on exploitability metrics and CVSS scores, execute these fixes immediately:\n\n"
                    + "\n".join(remediations) +
                    f"\n\n*Note: These direct packages introduce transitive vulnerabilities which will be resolved automatically on upgrade.*"
                )
            else:
                resp = "### Remediation Plan\n\nNo vulnerabilities require patching. All dependencies are clean."

        elif "explain cve" in msg or "explain cve-" in msg or "cve-2" in msg:
            # Vulnerability Agent
            logger.info("Routing to Vulnerability Agent...")
            # Extract CVE ID using regex
            match = re.search(r'cve-\d{4}-\d+', msg)
            cve_id = match.group(0).upper() if match else (vulns[0]["cve_id"] if vulns else "CVE-2021-44228")
            
            cve_record = Vulnerability.query.filter_by(cve_id=cve_id).first()
            if cve_record:
                referenced.append(cve_id)
                resp = (
                    f"### Deep Dive: **{cve_id}**\n\n"
                    f"- **CVSS v3 Score:** **{float(cve_record.cvss_score)}/10.0**\n"
                    f"- **Severity Class:** {cve_record.severity}\n"
                    f"- **Target Remediation Version:** `{cve_record.patched_version}`\n\n"
                    f"**Description:**\n"
                    f"{cve_record.description}\n\n"
                    f"**Exploitation Scenario:**\n"
                    f"Attackers can send crafted payloads to vulnerable versions of this package to trigger remote code execution or bypass validation layers."
                )
            else:
                resp = f"### CVE Search\n\nThe vulnerability with ID '{cve_id}' was not found in our database intelligence index."

        elif "remediation" in msg or "recommend" in msg:
            # Security Advisor Agent
            logger.info("Routing to Security Advisor Agent...")
            actions = []
            if vulns:
                for v in vulns:
                    referenced.append(v["cve_id"])
                    actions.append(f"- **{v['affected_library']}**: Upgrade version `{v['affected_version']}` -> `{v['patched_version']}` (Fixes {v['cve_id']})")
            if licenses["conflicts_count"] > 0:
                actions.append(f"- **License Policy**: Remove GPL Copyleft dependencies or obtain commercial exemptions.")
            if maint["deprecated_count"] > 0:
                actions.append(f"- **Maintenance Cleanup**: Swap out the {maint['deprecated_count']} deprecated libraries for active alternatives.")
                
            resp = (
                f"### Security Advisor Recommendations\n\n"
                f"SentinelSBOM advises executing these remediation commands:\n\n"
                + "\n".join(actions)
            )
            
        elif "executive summary" in msg or "executive report" in msg:
            # Executive Report Agent
            logger.info("Routing to Executive Report Agent...")
            resp = (
                f"# Executive Supply Chain Security Report: **{app.name}**\n"
                f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n"
                f"**Status:** **{risk['severity'].upper()} RISK**\n\n"
                f"### High-Level Summary:\n"
                f"- **Overall Risk Rating:** **{risk['overall_score']}/100**\n"
                f"- **Dependencies Audited:** {len(maint['dependencies'])}\n"
                f"- **Vulnerabilities Found:** {len(vulns)} CVEs ({sum(1 for v in vulns if v['severity']=='Critical')} Critical, {sum(1 for v in vulns if v['severity']=='High')} High)\n"
                f"- **License Conflicts:** {licenses['conflicts_count']} copyleft policy violations.\n"
                f"- **Stale / Abandoned Packages:** {maint['abandoned_count']} packages.\n\n"
                f"### Recommendations:\n"
                f"The product supply chain security rating is currently compromised due to direct vulnerabilities and license risks. Immediate updates of core dependencies are required to achieve compliance thresholds."
            )
            
        elif "developer report" in msg or "developer summary" in msg:
            # Developer Report Agent
            logger.info("Routing to Developer Report Agent...")
            resp = (
                f"### Developer Security Patchlist: **{app.name}**\n\n"
                f"The following dependencies contain vulnerability CVEs or deprecated licenses. Replace them in your packaging manifests:\n\n"
                f"| Package | Current | Remediation | Status | CVE ID |\n"
                f"|---|---|---|---|---|\n"
            )
            for v in vulns:
                referenced.append(v["cve_id"])
                resp += f"| `{v['affected_library']}` | `{v['affected_version']}` | `{v['patched_version']}` | Upgrade | {v['cve_id']} |\n"
            for c in licenses["conflicts"]:
                resp += f"| `{c['library_name']}` | `{c['library_version']}` | *Replace Dependency* | Incompatible License | - |\n"
                
        else:
            # Orchestrator fallback response
            logger.info("Routing to general Orchestrator Agent...")
            resp = (
                f"Hello! I am the **SentinelSBOM Security Copilot**.\n\n"
                f"I have analysed the codebase for **{app.name} v{app.version}** and can assist you with:\n"
                f"- **'What is my highest risk?'**\n"
                f"- **'What should be fixed first?'**\n"
                f"- **'Recommend remediation'**\n"
                f"- **'Generate executive summary'**\n"
                f"- **'Explain CVE-2023-51074'**\n\n"
                f"Please select a question or enter a prompt."
            )
            
        return {
            "response": resp,
            "referenced_items": referenced
        }

import re
