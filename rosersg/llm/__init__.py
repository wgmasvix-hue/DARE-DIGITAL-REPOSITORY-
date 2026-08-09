"""LLM Provider abstraction for pluggable AI backends"""

from .provider import LLMProvider
from .ollama import OllamaProvider

__all__ = ["LLMProvider", "OllamaProvider"]
