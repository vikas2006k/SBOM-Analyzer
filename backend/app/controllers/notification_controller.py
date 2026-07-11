from flask import request, g
from app.services.notification_service import NotificationService
from app.utils.response_helper import ResponseHelper
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class NotificationController:
    """Controller handling alerts notifications actions for security analysts."""

    def __init__(self):
        self.notif_service = NotificationService()

    def get_notifications(self):
        """Retrieve list of active notifications for the current authenticated user."""
        try:
            user_id = g.current_user.id if hasattr(g, 'current_user') else 1
            unread_only = request.args.get("unread_only", "false").lower() == "true"
            
            notifs = self.notif_service.get_notifications_for_user(user_id, unread_only)
            results = []
            for n in notifs:
                results.append({
                    "id": n.id,
                    "title": n.title,
                    "message": n.message,
                    "is_read": n.is_read,
                    "created_at": n.created_at.isoformat() if n.created_at else None
                })
            return ResponseHelper.success(results, "Notifications retrieved successfully")
        except Exception as e:
            logger.error(f"Get Notifications API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to fetch notifications: {str(e)}", 500)

    def mark_read(self, notif_id):
        """Dismiss a specific notification by marking it read."""
        try:
            user_id = g.current_user.id if hasattr(g, 'current_user') else 1
            self.notif_service.mark_notification_as_read(notif_id, user_id)
            return ResponseHelper.success(None, "Notification marked as read successfully")
        except ValueError as ve:
            return ResponseHelper.error(str(ve), 404)
        except Exception as e:
            logger.error(f"Dismiss Notification API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to dismiss notification: {str(e)}", 500)

    def mark_all_read(self):
        """Dismiss all unread alerts logs."""
        try:
            user_id = g.current_user.id if hasattr(g, 'current_user') else 1
            count = self.notif_service.mark_all_as_read(user_id)
            return ResponseHelper.success({"dismissed_count": count}, f"Dismissed {count} notifications successfully")
        except Exception as e:
            logger.error(f"Dismiss All Notifications API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to dismiss all notifications: {str(e)}", 500)
