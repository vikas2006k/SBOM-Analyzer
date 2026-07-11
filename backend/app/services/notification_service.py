from app.database.connection import db
from app.models.notification import Notification
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class NotificationService:
    """Service handling dashboard alerts logs and email-ready delivery architecture."""

    def __init__(self):
        pass

    def create_notification(self, user_id, title, message):
        """Create a new notification entry in the database."""
        logger.info(f"Generating alert notification for user {user_id}: '{title}'")
        try:
            notif = Notification(
                user_id=user_id,
                title=title,
                message=message,
                is_read=False
            )
            db.session.add(notif)
            db.session.commit()
            return notif
        except Exception as e:
            logger.error(f"Failed to create notification: {str(e)}")
            db.session.rollback()
            return None

    def get_notifications_for_user(self, user_id, unread_only=False):
        """Retrieve notifications checklist for a specific user ID."""
        query = Notification.query.filter_by(user_id=user_id, is_deleted=False)
        if unread_only:
            query = query.filter_by(is_read=False)
        # Order by newest first
        return query.order_by(Notification.created_at.desc()).all()

    def mark_notification_as_read(self, notification_id, user_id):
        """Dismiss a specific notification by ID (marking it as read)."""
        notif = Notification.query.filter_by(id=notification_id, user_id=user_id, is_deleted=False).first()
        if not notif:
            raise ValueError(f"Notification with ID {notification_id} not found or access denied")
            
        notif.is_read = True
        db.session.commit()
        return notif

    def mark_all_as_read(self, user_id):
        """Dismiss all unread notifications for a user."""
        unread = Notification.query.filter_by(user_id=user_id, is_read=False, is_deleted=False).all()
        for notif in unread:
            notif.is_read = True
        db.session.commit()
        return len(unread)

    def trigger_critical_risk_alert(self, user_id, app_name, cve_id, cvss_score):
        """Trigger an immediate high-priority alert when a critical CVE is detected."""
        title = f"CRITICAL SECURITY ALERT: {cve_id} detected in {app_name}"
        message = (
            f"A critical security vulnerability ({cve_id}) with a CVSS score of {cvss_score} "
            f"has been identified in the software supply chain of '{app_name}'. "
            f"Immediate developer patching is required to mitigate remote exploitation risks."
        )
        # This acts as an entry point for emails sending hooks in staging/prod
        self.send_mock_email(user_id, title, message)
        return self.create_notification(user_id, title, message)

    def send_mock_email(self, user_id, title, message):
        """Email Delivery Hook Skeleton."""
        # Logs the email trigger for security audits
        logger.info(f"[EMAIL DELIVERY SIMULATOR] Sending email alert to user {user_id} | Subject: {title}")
        return True
