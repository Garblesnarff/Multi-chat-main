"""
__init__.py - Flask app factory for multi-provider LLM chat app

Initializes the Flask application, loads configuration, and registers blueprints.

Dependencies:
- flask
- config.Config
- app.routes (chat_bp, history_bp)

@author Auto-refactored by Cline
"""

import os
from flask import Flask
from config import Config

from app.routes import chat_bp, history_bp

def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: Configured Flask app instance.
    """
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'),
        static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static'),
        static_url_path='/static'
    )
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    app.register_blueprint(chat_bp)
    app.register_blueprint(history_bp)

    return app
