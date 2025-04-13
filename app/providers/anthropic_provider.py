"""
anthropic-provider.py - Anthropic LLM API provider implementation

Implements the AnthropicProvider class, which extends LLMProvider to interact with the Anthropic API.
Supports chat, reasoning, and streaming responses.

Dependencies:
- anthropic
- Python standard library
- Logging module
- app.providers.base.LLMProvider

@author Auto-refactored by Cline
"""

import os
import logging

from anthropic import Anthropic

from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class AnthropicProvider(LLMProvider):
    """
    LLMProvider implementation for Anthropic API.

    Attributes:
        client (Anthropic): Anthropic API client instance.
    """

    def __init__(self, max_history=10):
        """
        Initialize AnthropicProvider.

        Args:
            max_history (int): Maximum conversation history length.
        """
        super().__init__(max_history)
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_response(self, message, model):
        """
        Generate a response from Anthropic API.

        Args:
            message (str): User input message.
            model (str): Model identifier.

        Returns:
            str: Generated response.
        """
        try:
            self.add_to_history("user", message)
            prompt = "\n\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.get_conversation_history()])
            prompt += "\n\nAssistant:"
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                max_tokens_to_sample=300
            )
            self.add_to_history("assistant", response.completion)
            return response.completion
        except Exception as e:
            logger.error(f"Error in AnthropicProvider.generate_response: {str(e)}")
            raise

    def generate_response_with_reasoning(self, message, model):
        """
        Generate a response with reasoning from Anthropic API.

        Args:
            message (str): User input message.
            model (str): Model identifier.

        Returns:
            str: Reasoning and final response.
        """
        try:
            self.add_to_history("user", message)
            reasoning_prompt = f"Reason step-by-step about the following message: {message}\n\nAssistant:"
            reasoning_response = self.client.completions.create(
                model=model,
                prompt=reasoning_prompt,
                max_tokens_to_sample=300
            ).completion

            final_prompt = f"Based on the following reasoning, provide a final response:\n\nReasoning:\n{reasoning_response}\n\nFinal response:\n\nAssistant:"
            final_response = self.client.completions.create(
                model=model,
                prompt=final_prompt,
                max_tokens_to_sample=300
            ).completion

            self.add_to_history("assistant", final_response)
            return f"Reasoning:\n{reasoning_response}\n\nFinal Response:\n{final_response}"
        except Exception as e:
            logger.error(f"Error in AnthropicProvider.generate_response_with_reasoning: {str(e)}")
            raise

    def generate_stream(self, message, model, use_reasoning=False):
        """
        Generate a streaming response from Anthropic API.

        Args:
            message (str): User input message.
            model (str): Model identifier.
            use_reasoning (bool): Whether to include reasoning.

        Yields:
            str: Streamed response chunks.
        """
        try:
            self.add_to_history("user", message)
            if use_reasoning:
                reasoning_prompt = f"Reason step-by-step about the following message: {message}\n\nAssistant:"
                reasoning_stream = self.client.completions.create(
                    model=model,
                    prompt=reasoning_prompt,
                    max_tokens_to_sample=300,
                    stream=True
                )
                yield "Reasoning:\n"
                for completion in reasoning_stream:
                    if completion.completion:
                        yield completion.completion

                final_prompt = f"Based on the reasoning, provide a final response.\n\nAssistant:"
                final_stream = self.client.completions.create(
                    model=model,
                    prompt=final_prompt,
                    max_tokens_to_sample=300,
                    stream=True
                )
                yield "\n\nFinal Response:\n"
                for completion in final_stream:
                    if completion.completion:
                        yield completion.completion
            else:
                prompt = "\n\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.get_conversation_history()])
                prompt += "\n\nAssistant:"
                stream = self.client.completions.create(
                    model=model,
                    prompt=prompt,
                    max_tokens_to_sample=300,
                    stream=True
                )
                for completion in stream:
                    if completion.completion:
                        yield completion.completion
        except Exception as e:
            logger.error(f"Error in AnthropicProvider.generate_stream: {str(e)}")
            raise
