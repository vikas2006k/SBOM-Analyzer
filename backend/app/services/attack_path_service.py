import networkx as nx
from app.services.dependency_service import DependencyService
from app.services.vulnerability_service import VulnerabilityService
from app.models.application import Application
from app.models.library import Library
from app.models.dependency import Dependency
from app.database.connection import db
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class AttackPathService:
    """Service performing graph traversal, reachability, and attack path analysis using NetworkX."""

    def __init__(self):
        self.dep_service = DependencyService()
        self.vuln_service = VulnerabilityService()

    def analyze_attack_paths(self, application_id):
        """Map vulnerability exposure paths from root project through transitive graphs."""
        logger.info(f"Analyzing attack paths for application {application_id}...")
        
        app = db.session.get(Application, application_id)
        if not app:
            raise ValueError(f"Application with ID {application_id} not found")
            
        dg, root_key = self.dep_service.build_networkx_graph(application_id)
        vulns = self.vuln_service.get_vulnerabilities_by_application(application_id)
        
        # 1. Map CVEs by library key for rapid lookups during traversal
        lib_vulns = {}
        for v in vulns:
            # key is (library_name, library_version)
            key = (v["affected_library"], v["affected_version"])
            if key not in lib_vulns:
                lib_vulns[key] = []
            lib_vulns[key].append(v)
            
        attack_paths = []
        critical_chains = []
        shared_vulnerabilities = {}
        root_causes = {}
        shortest_paths = {}
        
        # Find paths to vulnerable nodes
        for node in dg.nodes:
            if node == root_key:
                continue
                
            # Check if library is vulnerable
            node_vulns = lib_vulns.get(node, [])
            if not node_vulns:
                continue
                
            # If vulnerable, evaluate reachability and paths
            node_id = f"{node[0]}@{node[1]}"
            root_id = f"{root_key[0]}@{root_key[1]}"
            
            # Find paths from root to this vulnerable node
            try:
                paths = list(nx.all_simple_paths(dg, root_key, node))
            except Exception:
                paths = []
                
            if paths:
                # Resolve shortest path
                s_path = min(paths, key=len)
                shortest_paths[node_id] = [f"{n[0]}@{n[1]}" for n in s_path]
                
                # Resolve Root Cause (direct dependency at depth 1 that introduced this)
                if len(s_path) > 2:
                    direct_dep = s_path[1] # index 0 is app root, index 1 is direct dep
                    direct_id = f"{direct_dep[0]}@{direct_dep[1]}"
                    if direct_id not in root_causes:
                        root_causes[direct_id] = []
                    root_causes[direct_id].append({
                        "introduced_library": node_id,
                        "vulnerabilities_count": len(node_vulns)
                    })
                    
                # Format attack paths
                for p in paths:
                    path_nodes = [f"{n[0]}@{n[1]}" for n in p]
                    cve_ids = [v["cve_id"] for v in node_vulns]
                    max_cvss = max(v["cvss_score"] for v in node_vulns)
                    
                    path_data = {
                        "path": path_nodes,
                        "length": len(path_nodes) - 1,
                        "target_vulnerabilities": cve_ids,
                        "max_cvss": max_cvss,
                        "severity": self.vuln_service.classify_severity(max_cvss)
                    }
                    
                    attack_paths.append(path_data)
                    
                    # If high risk or critical, classify as Critical Chain
                    if max_cvss >= 7.0:
                        critical_chains.append(path_data)
                        
            # Aggregate shared vulnerabilities
            for v in node_vulns:
                cve = v["cve_id"]
                if cve not in shared_vulnerabilities:
                    shared_vulnerabilities[cve] = {
                        "description": v["description"],
                        "cvss_score": v["cvss_score"],
                        "severity": v["severity"],
                        "patched_version": v["patched_version"],
                        "affected_libraries": []
                    }
                shared_vulnerabilities[cve]["affected_libraries"].append(node_id)
                
        # 2. Build Interactive UI Visual Graph Nodes & Edges (with colors)
        nodes_json = []
        edges_json = []
        
        # Calculate depths from root
        try:
            depths = nx.single_source_shortest_path_length(dg, root_key)
        except Exception:
            depths = {node: 1 for node in dg.nodes}
            depths[root_key] = 0
            
        depth_counts = {}
        for node in dg.nodes:
            depth = depths.get(node, 1)
            if depth not in depth_counts:
                depth_counts[depth] = 0
            else:
                depth_counts[depth] += 1
                
            x_coord = depth * 280
            y_coord = depth_counts[depth] * 120
            
            node_id = f"{node[0]}@{node[1]}"
            node_vulns = lib_vulns.get(node, [])
            
            # Determine color and type
            if depth == 0:
                color = "#4f46e5"  # Indigo (application root)
                status = "application"
            elif not node_vulns:
                color = "#10b981"  # Emerald green (secure library)
                status = "secure"
            else:
                max_cvss = max(v["cvss_score"] for v in node_vulns)
                if max_cvss >= 9.0:
                    color = "#ef4444"  # Red (Critical vuln)
                elif max_cvss >= 7.0:
                    color = "#f97316"  # Orange (High vuln)
                elif max_cvss >= 4.0:
                    color = "#eab308"  # Yellow (Medium vuln)
                else:
                    color = "#3b82f6"  # Blue (Low vuln)
                status = "vulnerable"
                
            nodes_json.append({
                "id": node_id,
                "type": "customNode" if depth > 0 else "input",
                "data": {
                    "label": f"{node[0]} v{node[1]}",
                    "name": node[0],
                    "version": node[1],
                    "depth": depth,
                    "vulnerabilities": [{
                        "cve_id": v["cve_id"],
                        "cvss_score": v["cvss_score"],
                        "severity": v["severity"],
                        "risk_category": v["risk_category"]
                    } for v in node_vulns],
                    "status": status,
                    "color": color
                },
                "position": {"x": x_coord, "y": y_coord}
            })
            
        # Draw directed edges (highlight edges leading to vulnerabilities in red)
        # Find all edges that are on any attack path to color them red
        red_edges = set()
        for p in attack_paths:
            nodes_list = p["path"]
            for i in range(len(nodes_list) - 1):
                red_edges.add((nodes_list[i], nodes_list[i+1]))
                
        for edge in dg.edges:
            parent_id = f"{edge[0][0]}@{edge[0][1]}"
            child_id = f"{edge[1][0]}@{edge[1][1]}"
            
            is_critical_path = (parent_id, child_id) in red_edges
            edge_color = "#ef4444" if is_critical_path else "#94a3b8"  # Red vs Gray
            
            edges_json.append({
                "id": f"e-{parent_id}-->{child_id}",
                "source": parent_id,
                "target": child_id,
                "animated": is_critical_path,
                "style": {"stroke": edge_color, "strokeWidth": 2 if is_critical_path else 1}
            })
            
        return {
            "application_id": application_id,
            "attack_paths_count": len(attack_paths),
            "critical_chains_count": len(critical_chains),
            "attack_paths": attack_paths,
            "critical_chains": critical_chains,
            "root_cause_analysis": [{
                "direct_dependency": k,
                "introduced_vulnerabilities": v
            } for k, v in root_causes.items()],
            "shortest_paths": shortest_paths,
            "shared_vulnerabilities": [{
                "cve_id": k,
                "details": v
            } for k, v in shared_vulnerabilities.items()],
            "graph_visualization": {
                "nodes": nodes_json,
                "edges": edges_json
            }
        }
