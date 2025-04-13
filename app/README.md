# app/

This package contains the core server-side logic for the multi-provider LLM chat application.

## Purpose

- Initialize the Flask app
- Define API routes and blueprints
- Provide LLM provider classes for different APIs (Groq, Gemini, Anthropic, OpenAI, Cerebras)

## Structure

- `__init__.py` — Flask app factory
- `routes/` — Flask blueprints and route handlers
- `providers/` — LLM provider classes, one per API

## Interaction

- The app factory initializes Flask and registers blueprints from `routes/`
- Routes handle chat requests, instantiate providers from `providers/`
- Providers encapsulate API calls and conversation management

## Usage

Import `create_app()` from `app` to initialize the Flask application.

```python
from app import create_app

app = create_app()
