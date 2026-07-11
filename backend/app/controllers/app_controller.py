from app.repositories.application_repository import ApplicationRepository
from app.services.dependency_service import DependencyService
from app.models.dependency import Dependency
from app.utils.response_helper import ResponseHelper
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class AppController:
    """Controller handling application details queries and graph visualizations endpoints."""

    def __init__(self):
        self.app_repo = ApplicationRepository()
        self.dep_service = DependencyService()

    def get_application(self, app_id):
        """Retrieve details metadata for a specific application."""
        try:
            app = self.app_repo.find_by_id(app_id)
            if not app:
                return ResponseHelper.error(f"Application with ID {app_id} not found", 404)
                
            return ResponseHelper.success({
                "id": app.id,
                "name": app.name,
                "version": app.version,
                "description": app.description,
                "business_criticality": app.business_criticality,
                "created_at": app.created_at.isoformat() if app.created_at else None
            }, "Application metadata retrieved successfully")
        except Exception as e:
            logger.error(f"Get App API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to fetch application profile: {str(e)}", 500)

    def get_application_graph(self, app_id):
        """Retrieve the adjacency matrix representing node relationships for React Flow display."""
        try:
            graph_data = self.dep_service.get_adjacency_matrix(app_id)
            return ResponseHelper.success(graph_data, "Adjacency matrix resolved successfully")
        except ValueError as ve:
            return ResponseHelper.error(str(ve), 404)
        except Exception as e:
            logger.error(f"Get Graph API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to resolve dependency graph: {str(e)}", 500)

    def get_application_dependencies(self, app_id):
        """Retrieve flat inventory list of parsed libraries with depth levels for an application."""
        try:
            # Query edges
            edges = Dependency.query.filter_by(application_id=app_id, is_deleted=False).all()
            
            dependencies_list = []
            seen_libs = set()
            
            for edge in edges:
                child = edge.child_library
                if not child:
                    continue
                    
                lib_key = (child.name, child.version)
                if lib_key not in seen_libs:
                    dependencies_list.append({
                        "id": child.id,
                        "name": child.name,
                        "version": child.version,
                        "ecosystem": child.ecosystem,
                        "license": child.license_name,
                        "depth": edge.depth,
                        "is_transitive": edge.is_transitive
                    })
                    seen_libs.add(lib_key)
                    
            # Sort by depth and then name
            dependencies_list.sort(key=lambda x: (x['depth'], x['name']))
            
            return ResponseHelper.success(dependencies_list, "Application dependencies catalog retrieved successfully")
        except Exception as e:
            logger.error(f"Get Dependencies API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to fetch dependencies inventory: {str(e)}", 500)
