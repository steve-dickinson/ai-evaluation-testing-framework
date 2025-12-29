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
        
        # Extract parameters from context
        kwargs = {}
        if context:
            if "system_prompt" in context:
                messages.insert(0, {"role": "system", "content": context["system_prompt"]})
            # Pass through other supported params
            if "temperature" in context:    
                kwargs["temperature"] = context["temperature"]
            if "max_tokens" in context:
                kwargs["max_tokens"] = context["max_tokens"]
        
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            # In a real app we might want to log this properly or retry
            raise ConnectionError(f"OpenAI API call failed: {e}")
