from flask import Blueprint
from app.controllers.notification_controller import NotificationController
from app.middlewares.auth_middleware import token_required

notification_bp = Blueprint('notifications', __name__)
notification_controller = NotificationController()

@notification_bp.route('', methods=['GET'])
@token_required
def get_notifications():
    """Retrieve active alerts list."""
    return notification_controller.get_notifications()

@notification_bp.route('/<int:notif_id>/read', methods=['POST'])
@token_required
def mark_read(notif_id):
    """Mark a specific alert read."""
    return notification_controller.mark_read(notif_id)

@notification_bp.route('/read-all', methods=['POST'])
@token_required
def mark_all_read():
    """Mark all active alerts read."""
    return notification_controller.mark_all_read()
