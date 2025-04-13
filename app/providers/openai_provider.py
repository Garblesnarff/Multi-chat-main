"""
openai-provider.py - OpenAI LLM API provider implementation

Implements the OpenAIProvider class, which extends LLMProvider to interact with the OpenAI API.
Supports chat, reasoning, and streaming responses.

Dependencies:
- openai
- Python standard library
- Logging module
- app.providers.base.LLMProvider

@author Auto-refactored by Cline
"""

import os
import logging

from openai import OpenAI

from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    """
    LLMProvider implementation for OpenAI API.

    Attributes:
        client (OpenAI): OpenAI API client instance.
    """

    def __init__(self, max_history=10):
        """
        Initialize OpenAIProvider.

        Args:
            max_history (int): Maximum conversation history length.
        """
        super().__init__(max_history)
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    def generate_response(self, message, model):
        """
        Generate a response from OpenAI API.

        Args:
            message (str): User input message.
            model (str): Model identifier.

        Returns:
            str: Generated response.
        """
        try:
            self.add_to_history("user", message)
            response = self.client.chat.completions.create(
                model=model,
                messages=self.get_conversation_history()
            )
            assistant_response = response.choices[0].message.content
            self.add_to_history("assistant", assistant_response)
            return assistant_response
        except Exception as e:
            logger.error(f"Error in OpenAIProvider.generate_response: {str(e)}")
            raise

    def generate_response_with_reasoning(self, message, model):
        """
        Generate a response with reasoning from OpenAI API.

        Args:
            message (str): User input message.
            model (str): Model identifier.

        Returns:
            str: Reasoning and final response.
        """
        try:
            self.add_to_history("user", message)
            reasoning_prompt = f"Reason step-by-step about the following message: {message}"
            reasoning_response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": reasoning_prompt}]
            ).choices[0].message.content

            final_prompt = f"Based on the following reasoning, provide a final response:\n\nReasoning:\n{reasoning_response}\n\nFinal response:"
            final_response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": final_prompt}]
            ).choices[0].message.content

            self.add_to_history("assistant", final_response)
            return f"Reasoning:\n{reasoning_response}\n\nFinal Response:\n{final_response}"
        except Exception as e:
            logger.error(f"Error in OpenAIProvider.generate_response_with_reasoning: {str(e)}")
            raise

    def generate_stream(self, message, model, use_reasoning=False):
        """
        Generate a streaming response from OpenAI API.

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
                reasoning_prompt = f"Reason step-by-step about the following message: {message}"
                reasoning_stream = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": reasoning_prompt}],
                    stream=True
                )
                yield "Reasoning:\n"
                for chunk in reasoning_stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content

                final_prompt = f"Based on the reasoning, provide a final response."
                final_stream = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": final_prompt}],
                    stream=True
                )
                yield "\n\nFinal Response:\n"
                for chunk in final_stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
            else:
                stream = self.client.chat.completions.create(
                    model=model,
                    messages=self.get_conversation_history(),
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error in OpenAIProvider.generate_stream: {str(e)}")
            raise
