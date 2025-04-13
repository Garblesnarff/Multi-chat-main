"""
groq-provider.py - Groq LLM API provider implementation

Implements the GroqProvider class, which extends LLMProvider to interact with the Groq API.
Supports chat, reasoning, and streaming responses.

Dependencies:
- groq
- Python standard library
- Logging module
- app.providers.base.LLMProvider

@author Auto-refactored by Cline
"""

import os
import logging

from groq import Groq

from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class GroqProvider(LLMProvider):
    """
    LLMProvider implementation for Groq API.

    Attributes:
        client (Groq): Groq API client instance.
    """

    def __init__(self, max_history=10):
        """
        Initialize GroqProvider.

        Args:
            max_history (int): Maximum conversation history length.
        """
        super().__init__(max_history)
        self.client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

    def generate_response(self, message, model):
        """
        Generate a response from Groq API.

        Args:
            message (str): User input message.
            model (str): Model identifier.

        Returns:
            str: Generated response.
        """
        try:
            self.add_to_history("user", message)
            chat_completion = self.client.chat.completions.create(
                messages=self.get_conversation_history(),
                model=model,
            )
            response = chat_completion.choices[0].message.content
            self.add_to_history("assistant", response)
            return response
        except Exception as e:
            logger.error(f"Error in GroqProvider.generate_response: {str(e)}")
            raise

    def generate_response_with_reasoning(self, message, model):
        """
        Generate a response with reasoning from Groq API.

        Args:
            message (str): User input message.
            model (str): Model identifier.

        Returns:
            str: Reasoning and final response.
        """
        try:
            self.add_to_history("user", message)
            reasoning_prompt = f"Reason step-by-step about the following message: {message}"
            reasoning_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": reasoning_prompt}],
                model=model,
            )
            reasoning_response = reasoning_completion.choices[0].message.content

            final_prompt = f"Based on the following reasoning, provide a final response:\n\nReasoning:\n{reasoning_response}\n\nFinal response:"
            final_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": final_prompt}],
                model=model,
            )
            final_response = final_completion.choices[0].message.content

            self.add_to_history("assistant", final_response)
            return f"Reasoning:\n{reasoning_response}\n\nFinal Response:\n{final_response}"
        except Exception as e:
            logger.error(f"Error in GroqProvider.generate_response_with_reasoning: {str(e)}")
            raise

    def generate_stream(self, message, model, use_reasoning=False):
        """
        Generate a streaming response from Groq API.

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
                    messages=[{"role": "user", "content": reasoning_prompt}],
                    model=model,
                    stream=True,
                )
                yield "Reasoning:\n"
                for chunk in reasoning_stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content

                final_prompt = f"Based on the reasoning, provide a final response."
                final_stream = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": final_prompt}],
                    model=model,
                    stream=True,
                )
                yield "\n\nFinal Response:\n"
                for chunk in final_stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
            else:
                stream = self.client.chat.completions.create(
                    messages=self.get_conversation_history(),
                    model=model,
                    stream=True,
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error in GroqProvider.generate_stream: {str(e)}")
            raise
