"""
base.py - Abstract base class for LLM providers

Defines the LLMProvider class, which manages conversation history and provides an interface
for generating responses and streams from different LLM APIs.

Dependencies:
- Python standard library
- Logging module

@author Auto-refactored by Cline
"""

import logging

logger = logging.getLogger(__name__)

class LLMProvider:
    """
    Abstract base class for Large Language Model providers.

    Manages conversation history and defines the interface for generating responses.

    Attributes:
        conversation_history (list): List of message dicts with 'role' and 'content'.
        max_history (int): Maximum number of messages to retain in history.
    """

    def __init__(self, max_history=10):
        """
        Initialize the provider.

        Args:
            max_history (int): Maximum conversation history length.
        """
        self.conversation_history = []
        self.max_history = max_history

    def generate_response(self, message, model):
        """
        Generate a response from the LLM.

        Args:
            message (str): User input message.
            model (str): Model identifier.

        Returns:
            str: Generated response.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def generate_response_with_reasoning(self, message, model):
        """
        Generate a response with step-by-step reasoning.

        Args:
            message (str): User input message.
            model (str): Model identifier.

        Returns:
            str: Reasoning and final response.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def generate_stream(self, message, model, use_reasoning=False):
        """
        Generate a streaming response.

        Args:
            message (str): User input message.
            model (str): Model identifier.
            use_reasoning (bool): Whether to include reasoning.

        Yields:
            str: Streamed response chunks.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def add_to_history(self, role, content):
        """
        Add a message to the conversation history.

        Args:
            role (str): 'user' or 'assistant'.
            content (str): Message content.
        """
        self.conversation_history.append({"role": role, "content": content})
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def get_conversation_history(self):
        """
        Get the current conversation history.

        Returns:
            list: List of message dicts.
        """
        return self.conversation_history

    def to_dict(self):
        """
        Serialize provider state to a dictionary.

        Returns:
            dict: Provider state.
        """
        return {
            "max_history": self.max_history,
            "conversation_history": self.conversation_history
        }

    @classmethod
    def from_dict(cls, data):
        """
        Deserialize provider state from a dictionary.

        Args:
            data (dict): Serialized provider state.

        Returns:
            LLMProvider: New instance with restored state.
        """
        provider = cls(max_history=data.get("max_history", 10))
        provider.conversation_history = data.get("conversation_history", [])
        return provider
