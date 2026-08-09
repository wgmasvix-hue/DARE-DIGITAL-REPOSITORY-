"""Ollama LLM Provider implementation"""

import logging
import requests
from typing import List, Optional
from .provider import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama LLM Provider - uses local or remote Ollama instance"""

    def __init__(
        self,
        endpoint: str = "http://localhost:11434",
        model: str = "mistral",
        temperature: float = 0.7,
        timeout: int = 60,
    ):
        """
        Initialize Ollama provider

        Args:
            endpoint: Ollama API endpoint
            model: Model name to use for generation (e.g., 'mistral')
            temperature: Sampling temperature (0.0-1.0)
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.embedding_model = "nomic-embed-text"

    def generate(self, prompt: str, stream: bool = False, **kwargs) -> str:
        """
        Generate text using Ollama

        Args:
            prompt: Input prompt
            stream: Whether to stream response
            **kwargs: Additional parameters (temperature, top_p, etc.)

        Returns:
            Generated text
        """
        try:
            url = f"{self.endpoint}/api/generate"

            # Merge kwargs with defaults
            temperature = kwargs.get("temperature", self.temperature)

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "temperature": temperature,
            }

            response = requests.post(
                url, json=payload, timeout=self.timeout, verify=True
            )
            response.raise_for_status()

            if stream:
                # Return iterator for streaming
                return response.iter_lines()
            else:
                # Return full response
                result = response.json()
                return result.get("response", "")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama generation error: {str(e)}")
            raise

    def embed(self, text: str) -> List[float]:
        """
        Generate embeddings using Ollama

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding
        """
        try:
            url = f"{self.endpoint}/api/embed"
            payload = {"model": self.embedding_model, "input": text}

            response = requests.post(
                url, json=payload, timeout=self.timeout, verify=True
            )
            response.raise_for_status()

            data = response.json()
            embeddings = data.get("embeddings", [])

            # Return first embedding if multiple returned
            if embeddings and isinstance(embeddings[0], list):
                return embeddings[0]
            return embeddings

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama embedding error: {str(e)}")
            raise

    def health_check(self) -> bool:
        """
        Check if Ollama is healthy and responsive

        Returns:
            True if Ollama is responding, False otherwise
        """
        try:
            response = requests.get(
                f"{self.endpoint}/api/tags", timeout=5, verify=True
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
