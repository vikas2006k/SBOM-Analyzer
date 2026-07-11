from flask import Blueprint
from app.controllers.sbom_controller import SBOMController
from app.middlewares.auth_middleware import token_required

sbom_bp = Blueprint('sbom', __name__)
sbom_controller = SBOMController()

@sbom_bp.route('/upload', methods=['POST'])
@token_required
def upload_sbom():
    """Endpoint: Upload SBOM JSON/CSV files.
    Authentication: Required
    """
    return sbom_controller.upload_sbom()

@sbom_bp.route('/parse/<int:upload_id>', methods=['POST'])
@token_required
def parse_sbom(upload_id):
    """Endpoint: Trigger SBOM parsing and validation.
    Authentication: Required
    """
    return sbom_controller.parse_sbom(upload_id)

@sbom_bp.route('/uploads', methods=['GET'])
@token_required
def list_uploads():
    """Endpoint: Get list of all SBOM uploads.
    Authentication: Required
    """
    return sbom_controller.list_uploads()
