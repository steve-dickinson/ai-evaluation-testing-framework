from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseChatbot(ABC):
    """Abstract base class for chatbot implementations."""

    @abstractmethod
    def send_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Sends a message to the chatbot and returns the response."""
        pass

class BaseEvaluator(ABC):
    """Abstract base class for response evaluators."""

    @abstractmethod
    def evaluate(self, prompt: str, response: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluates a chatbot response.
        Returns a dictionary containing metrics (e.g., score, passed, reason).
        """
        pass
