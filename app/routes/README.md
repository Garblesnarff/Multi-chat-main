# app/routes/

This directory contains Flask blueprints and route handlers for the multi-provider LLM chat app.

## Purpose

- Define HTTP endpoints for chat, clearing history, and other API calls
- Organize route logic into focused modules
- Register blueprints with the main Flask app

## Important Files

- `chat_routes.py` — Handles `/chat` and `/` endpoints, supports streaming and reasoning
- `history_routes.py` — Handles `/clear_history` endpoint
- `provider_factory.py` — Contains logic to instantiate LLM provider classes based on user selection
- `__init__.py` — Registers all blueprints for import by the app factory

## Interaction

- Blueprints are registered in `app/__init__.py`
- Routes call provider factory to get LLM instances
- Providers handle API calls and conversation management

## Usage Example

```python
from app.routes.chat_routes import chat_bp
app.register_blueprint(chat_bp)
