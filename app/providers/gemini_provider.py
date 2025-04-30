"""
gemini-provider.py - Gemini LLM API provider implementation

Implements the GeminiProvider class, which extends LLMProvider to interact with the Google Gemini API.
Supports chat, reasoning, and streaming responses.

Dependencies:
- google-generativeai
- Python standard library
- Logging module
- app.providers.base.LLMProvider

@author Auto-refactored by Cline
"""

import os
import logging

import google.generativeai as genai

from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class GeminiProvider(LLMProvider):
    """
    LLMProvider implementation for Google Gemini API.

    Attributes:
        None
    """

    def __init__(self, max_history=10):
        """
        Initialize GeminiProvider.

        Args:
            max_history (int): Maximum conversation history length.
        """
        super().__init__(max_history)
        self.api_key = os.environ.get('GEMINI_API_KEY')
        genai.configure(api_key=self.api_key)

    def generate_response(self, message, model):
        """
        Generate a response from Gemini API.

        Args:
            message (str): User input message.
            model (str): Model identifier.

        Returns:
            str: Generated response.
        """
        try:
            self.add_to_history("user", message)
            
            gemini_history = []
            for entry in self.get_conversation_history():
                if entry['role'] == 'user':
                    gemini_history.append({"role": "user", "parts": [{"text": entry['content']}]})
                elif entry['role'] == 'assistant':
                    gemini_history.append({"role": "model", "parts": [{"text": entry['content']}]})

            genai_model = genai.GenerativeModel(model)
            chat = genai_model.start_chat(history=gemini_history)
            response = chat.send_message(message)
            self.add_to_history("assistant", response.text)
            return response.text
        except Exception as e:
            logger.error(f"Error in GeminiProvider.generate_response: {str(e)}")
            raise

    def generate_response_with_reasoning(self, message, model):
        """
        Generate a response with reasoning from Gemini API.

        Args:
            message (str): User input message.
            model (str): Model identifier.

        Returns:
            str: Reasoning and final response.
        """
        try:
            self.add_to_history("user", message)
            
            reasoning_prompt = f"Reason step-by-step about the following message: {message}"
            genai_model = genai.GenerativeModel(model)
            reasoning_response = genai_model.generate_content(reasoning_prompt).text

            final_prompt = f"Based on the following reasoning, provide a final response:\n\nReasoning:\n{reasoning_response}\n\nFinal response:"
            final_response = genai_model.generate_content(final_prompt).text

            self.add_to_history("assistant", final_response)
            return f"Reasoning:\n{reasoning_response}\n\nFinal Response:\n{final_response}"
        except Exception as e:
            logger.error(f"Error in GeminiProvider.generate_response_with_reasoning: {str(e)}")
            raise

    def generate_stream(self, message, model, use_reasoning=False):
        """
        Generate a streaming response from Gemini API.

        Args:
            message (str): User input message.
            model (str): Model identifier.
            use_reasoning (bool): Whether to include reasoning.

        Yields:
            str: Streamed response chunks.
        """
        try:
            self.add_to_history("user", message)
            
            gemini_history = []
            for entry in self.get_conversation_history():
                if entry['role'] == 'user':
                    gemini_history.append({"role": "user", "parts": [{"text": entry['content']}]})
                elif entry['role'] == 'assistant':
                    gemini_history.append({"role": "model", "parts": [{"text": entry['content']}]})

            genai_model = genai.GenerativeModel(model)
            
            if use_reasoning:
                reasoning_prompt = f"Reason step-by-step about the following message: {message}"
                yield "Reasoning:\n"
                for chunk in genai_model.generate_content(reasoning_prompt, stream=True):
                    if chunk.text:
                        yield chunk.text
                
                final_prompt = f"Based on the reasoning, provide a final response."
                yield "\n\nFinal Response:\n"
                for chunk in genai_model.generate_content(final_prompt, stream=True):
                    if chunk.text:
                        yield chunk.text
            else:
                chat = genai_model.start_chat(history=gemini_history)
                for chunk in chat.send_message(message, stream=True):
                    if chunk.text:
                        yield chunk.text
        except Exception as e:
            logger.error(f"Error in GeminiProvider.generate_stream: {str(e)}")
            raise
