"""
provider_factory.py - Factory function for LLM provider instances

Contains the get_llm_provider() function, which instantiates or restores provider classes
based on the provider name and session data.

Dependencies:
- flask.session
- app.providers.* (GroqProvider, GeminiProvider, AnthropicProvider, OpenAIProvider, CerebrasProvider)

@author Auto-refactored by Cline
"""

from flask import session

from app.providers.groq_provider import GroqProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.cerebras_provider import CerebrasProvider

def get_llm_provider(provider, new_instance=False):
    """
    Factory function to get or restore an LLM provider instance.

    Args:
        provider (str): Provider name ('groq', 'gemini', 'anthropic', 'openai', 'cerebras').
        new_instance (bool): If True, create a new instance ignoring session state.

    Returns:
        LLMProvider: An instance of the requested provider.

    Raises:
        ValueError: If the provider name is unknown.
    """
    if new_instance or provider not in session.get('llm_provider', {}):
        if provider == 'groq':
            return GroqProvider()
        elif provider == 'gemini':
            return GeminiProvider()
        elif provider == 'anthropic':
            return AnthropicProvider()
        elif provider == 'openai':
            return OpenAIProvider()
        elif provider == 'cerebras':
            return CerebrasProvider()
        else:
            raise ValueError(f"Unknown provider: {provider}")
    else:
        llm_dict = session['llm_provider'][provider]
        if provider == 'groq':
            return GroqProvider.from_dict(llm_dict)
        elif provider == 'gemini':
            return GeminiProvider.from_dict(llm_dict)
        elif provider == 'anthropic':
            return AnthropicProvider.from_dict(llm_dict)
        elif provider == 'openai':
            return OpenAIProvider.from_dict(llm_dict)
        elif provider == 'cerebras':
            return CerebrasProvider.from_dict(llm_dict)
