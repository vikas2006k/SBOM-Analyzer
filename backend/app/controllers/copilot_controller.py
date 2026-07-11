import json
from flask import request, g
from app.services.ai_service import AIService
from app.models.copilot import AIConversation
from app.database.connection import db
from app.utils.response_helper import ResponseHelper
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class CopilotController:
    """Controller handling NLP Copilot chat integrations endpoints."""

    def __init__(self):
        self.ai_service = AIService()

    def chat(self):
        """Send message, trigger agents reasoning, and return AI security recommendation response."""
        try:
            data = request.get_json() or {}
            app_id = data.get("application_id")
            message = data.get("message")
            
            if not app_id or not message:
                return ResponseHelper.error("Missing required parameters: application_id, message", 400)
                
            user_id_val = g.current_user.id if hasattr(g, 'current_user') else 1
            
            # Find or create conversation history record in DB
            conversation = AIConversation.query.filter_by(
                user_id=user_id_val,
                application_id=app_id,
                is_deleted=False
            ).first()
            
            history = []
            if conversation:
                try:
                    history = json.loads(conversation.message_history)
                except Exception:
                    history = []
            else:
                conversation = AIConversation(
                    user_id=user_id_val,
                    application_id=app_id,
                    message_history="[]"
                )
                db.session.add(conversation)
                db.session.commit()
                
            # Process query using AI Agent network
            result = self.ai_service.process_query(user_id_val, app_id, message, history)
            
            # Update history logs
            history.append({"sender": "user", "text": message})
            history.append({
                "sender": "copilot", 
                "text": result["response"],
                "referenced_items": result.get("referenced_items", [])
            })
            
            conversation.message_history = json.dumps(history)
            db.session.commit()
            
            return ResponseHelper.success({
                "response": result["response"],
                "referenced_items": result.get("referenced_items", []),
                "history_length": len(history)
            }, "Security Copilot query completed successfully")
            
        except Exception as e:
            logger.error(f"Copilot Chat API failed: {str(e)}")
            return ResponseHelper.error(f"AI Assistant Error: {str(e)}", 500)

    def get_history(self, app_id):
        """Retrieve conversation history list for an application."""
        try:
            user_id_val = g.current_user.id if hasattr(g, 'current_user') else 1
            conversation = AIConversation.query.filter_by(
                user_id=user_id_val,
                application_id=app_id,
                is_deleted=False
            ).first()
            
            history = []
            if conversation:
                try:
                    history = json.loads(conversation.message_history)
                except Exception:
                    history = []
                    
            return ResponseHelper.success(history, "AI conversation history retrieved successfully")
        except Exception as e:
            logger.error(f"Get Copilot History API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to fetch conversation history: {str(e)}", 500)
