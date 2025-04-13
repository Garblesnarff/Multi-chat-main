"""
config.py - Configuration class for multi-provider LLM chat app

Loads API keys and secret key from environment variables.

Dependencies:
- os.environ

@author Auto-refactored by Cline
"""

import os

class Config:
    """
    Configuration class for Flask app and LLM providers.

    Class Attributes:
        SECRET_KEY (str): Flask secret key.
        GROQ_API_KEY (str): Groq API key.
        GEMINI_API_KEY (str): Gemini API key.
        ANTHROPIC_API_KEY (str): Anthropic API key.
        OPENAI_API_KEY (str): OpenAI API key.
        CEREBRAS_API_KEY (str): Cerebras API key.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    CEREBRAS_API_KEY = os.environ.get('CEREBRAS_API_KEY')

    @classmethod
    def get_cerebras_api_key(cls):
        """
        Get the Cerebras API key or raise an error if not set.

        Returns:
            str: Cerebras API key.

        Raises:
            ValueError: If the API key is not set.
        """
        if cls.CEREBRAS_API_KEY is None:
            raise ValueError("CEREBRAS_API_KEY is not set in the environment variables")
        return cls.CEREBRAS_API_KEY
