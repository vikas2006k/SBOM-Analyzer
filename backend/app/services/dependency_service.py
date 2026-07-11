import networkx as nx
from app.database.connection import db
from app.repositories.dependency_repository import DependencyRepository
from app.repositories.application_repository import ApplicationRepository
from app.repositories.library_repository import LibraryRepository
from app.models.dependency import Dependency
from app.models.library import Library
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class DependencyService:
    """Service handling directed acyclic dependency graphs operations and traversals using NetworkX."""

    def __init__(self):
        self.dep_repo = DependencyRepository()
        self.app_repo = ApplicationRepository()
        self.lib_repo = LibraryRepository()

    def build_networkx_graph(self, application_id):
        """Construct a NetworkX DiGraph representing dependency edges for an application."""
        app = self.app_repo.find_by_id(application_id)
        if not app:
            raise ValueError(f"Application with ID {application_id} not found")
            
        dg = nx.DiGraph()
        
        # Root Application Node Key: (app_name, app_version)
        root_key = (app.name, app.version)
        dg.add_node(root_key, type="application", label=f"{app.name} v{app.version}", depth=0)
        
        # Retrieve edges
        edges = self.dep_repo.find_edges_by_application(application_id)
        
        for edge in edges:
            child = edge.child_library
            if not child:
                continue
                
            child_key = (child.name, child.version)
            dg.add_node(child_key, type="library", label=f"{child.name} v{child.version}", ecosystem=child.ecosystem, license=child.license_name)
            
            if edge.parent_library_id:
                parent = edge.parent_library
                if parent:
                    parent_key = (parent.name, parent.version)
                    dg.add_edge(parent_key, child_key)
            else:
                # Direct dependency of the application root
                dg.add_edge(root_key, child_key)
                
        return dg, root_key

    def get_adjacency_matrix(self, application_id):
        """Compile nodes and edges structured JSON suitable for React Flow UI component visualization."""
        try:
            dg, root_key = self.build_networkx_graph(application_id)
            
            # Perform topological sort or simple BFS traversal to calculate node coordinates
            nodes_json = []
            edges_json = []
            
            # Use shortest path lengths from root to define columns/depths
            try:
                depths = nx.single_source_shortest_path_length(dg, root_key)
            except Exception:
                # Fallback if circular reference or unreachable elements exist
                depths = {node: 1 for node in dg.nodes}
                depths[root_key] = 0
                
            # Track nodes positioned per depth to increment vertical spacing offset
            depth_counts = {}
            
            for node_key in dg.nodes:
                node_data = dg.nodes[node_key]
                depth = depths.get(node_key, 1)
                
                # Increment horizontal and vertical positioning spacing
                if depth not in depth_counts:
                    depth_counts[depth] = 0
                else:
                    depth_counts[depth] += 1
                    
                x_coord = depth * 280
                y_coord = depth_counts[depth] * 120
                
                node_id = f"{node_key[0]}@{node_key[1]}"
                
                nodes_json.append({
                    "id": node_id,
                    "type": "customNode" if depth > 0 else "input",
                    "data": {
                        "label": node_data.get("label", f"{node_key[0]} v{node_key[1]}"),
                        "name": node_key[0],
                        "version": node_key[1],
                        "depth": depth,
                        "ecosystem": node_data.get("ecosystem", "unknown"),
                        "license": node_data.get("license", "Unknown")
                    },
                    "position": {"x": x_coord, "y": y_coord}
                })
                
            # Map edge properties
            for edge in dg.edges:
                parent_id = f"{edge[0][0]}@{edge[0][1]}"
                child_id = f"{edge[1][0]}@{edge[1][1]}"
                
                edges_json.append({
                    "id": f"e-{parent_id}-->{child_id}",
                    "source": parent_id,
                    "target": child_id,
                    "animated": True,
                    "style": {"stroke": "#10b981"} # Emerald green highlight edge
                })
                
            return {
                "nodes": nodes_json,
                "edges": edges_json,
                "metrics": {
                    "nodes_count": len(nodes_json),
                    "edges_count": len(edges_json),
                    "max_depth": max(depths.values()) if depths else 0
                }
            }
        except Exception as e:
            logger.error(f"Failed to generate adjacency graph details: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to resolve dependency graph: {str(e)}")

    def detect_cycles(self, application_id):
        """Identify circular dependency references inside application graph."""
        try:
            dg, _ = self.build_networkx_graph(application_id)
            cycles = list(nx.simple_cycles(dg))
            
            cycles_formatted = []
            for cycle in cycles:
                cycles_formatted.append(" -> ".join([f"{n[0]}@{n[1]}" for n in cycle]) + f" -> {cycle[0][0]}@{cycle[0][1]}")
                
            return {
                "has_cycles": len(cycles) > 0,
                "cycles": cycles_formatted
            }
        except Exception as e:
            logger.error(f"Cycles check fail: {str(e)}")
            raise ValueError(f"Failed cycle check: {str(e)}")

    def resolve_transitive_depths(self, application_id):
        """Compute the shortest path lengths from application root to update edges depth in DB."""
        logger.info(f"Resolving transitive depths for application {application_id}...")
        dg, root_key = self.build_networkx_graph(application_id)
        
        try:
            depths = nx.single_source_shortest_path_length(dg, root_key)
        except Exception as e:
            logger.warning(f"Shortest path calculation fallback: {str(e)}")
            return False
            
        # Update each edge depth in the database
        edges = self.dep_repo.find_edges_by_application(application_id)
        for edge in edges:
            child = edge.child_library
            if not child:
                continue
                
            child_key = (child.name, child.version)
            depth = depths.get(child_key, 1)
            
            edge.depth = depth
            edge.is_transitive = depth > 1
            db.session.add(edge)
            
        db.session.commit()
        return True
