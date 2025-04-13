"""
__init__.py - Register all Flask blueprints for the app.routes package

Imports and exposes:
- chat_bp: Chat endpoints
- history_bp: Conversation history endpoints

@author Auto-refactored by Cline
"""

from app.routes.chat_routes import chat_bp
from app.routes.history_routes import history_bp

__all__ = ["chat_bp", "history_bp"]
