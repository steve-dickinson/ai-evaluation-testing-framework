import os
from typing import Any, Dict, Optional
from openai import OpenAI
from src.framework.core.interfaces import BaseChatbot

class OpenAIChatbot(BaseChatbot):
    """OpenAI chatbot implementation."""

    def __init__(self, model: str = "o4-mini", api_key: Optional[str] = None):
        self.model = model
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def send_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Sends a message to OpenAI and returns the content."""
        messages = []
        
        # Add system prompt if present in context
        if context and "system_prompt" in context:
            messages.append({"role": "system", "content": context["system_prompt"]})
            
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            # In a real app we might want to log this properly or retry
            raise ConnectionError(f"OpenAI API call failed: {e}")
