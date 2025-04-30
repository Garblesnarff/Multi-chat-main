"""
main.py - Entrypoint for multi-provider LLM chat app

Creates and runs the Flask application.

Dependencies:
- app.create_app()

@author Auto-refactored by Cline
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5152)
