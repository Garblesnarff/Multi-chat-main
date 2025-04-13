# app/providers/

This directory contains classes that implement support for different Large Language Model (LLM) APIs.

## Purpose

- Encapsulate API calls to Groq, Gemini, Anthropic, OpenAI, and Cerebras
- Manage conversation history and streaming responses
- Provide a consistent interface for chat and reasoning features

## Important Files

- `base.py` — Abstract `LLMProvider` base class with shared logic
- `groq-provider.py` — `GroqProvider` implementation
- `gemini-provider.py` — `GeminiProvider` implementation
- `anthropic-provider.py` — `AnthropicProvider` implementation
- `openai-provider.py` — `OpenAIProvider` implementation
- `cerebras-provider.py` — `CerebrasProvider` implementation
- `__init__.py` — (optional) for imports or shared setup

## Interaction

- Routes instantiate provider classes based on user selection
- Providers handle API calls, maintain conversation state, and generate responses
- All providers inherit from `LLMProvider` base class

## Usage Example

```python
from app.providers.groq-provider import GroqProvider

provider = GroqProvider()
response = provider.generate_response("Hello", "groq-model")
