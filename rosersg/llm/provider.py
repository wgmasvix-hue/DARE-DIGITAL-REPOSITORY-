"""Abstract LLM Provider interface"""

from abc import ABC, abstractmethod
from typing import List, Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers

    Defines the interface for language model backends.
    Implementations can use Ollama, OpenAI, Gemini, etc.
    """

    @abstractmethod
    def generate(self, prompt: str, stream: bool = False, **kwargs) -> str:
        """
        Generate text from a prompt

        Args:
            prompt: The input prompt
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        Generate embeddings for text (vector representation)

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the provider is healthy and responsive

        Returns:
            True if healthy, False otherwise
        """
        pass
