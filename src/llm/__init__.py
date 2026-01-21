"""LLM provider module."""

import os
from typing import TYPE_CHECKING

from .base import BaseLLMProvider

if TYPE_CHECKING:
    pass


def get_llm_provider(config: dict) -> BaseLLMProvider:
    """
    Get the appropriate LLM provider based on configuration.
    
    Args:
        config: LLM configuration dictionary
        
    Returns:
        Configured LLM provider instance
    """
    provider = config.get("provider", "openai").lower()
    model = config.get("model", "gpt-4o")
    
    if provider == "openai":
        from .openai_provider import OpenAIProvider
        api_key = os.environ.get(config.get("api_key_env", "OPENAI_API_KEY"))
        if not api_key:
            raise ValueError(
                f"API key not found in environment variable: "
                f"{config.get('api_key_env', 'OPENAI_API_KEY')}"
            )
        return OpenAIProvider(api_key=api_key, model=model)
    
    elif provider == "anthropic":
        from .anthropic_provider import AnthropicProvider
        api_key = os.environ.get(config.get("api_key_env", "ANTHROPIC_API_KEY"))
        if not api_key:
            raise ValueError(
                f"API key not found in environment variable: "
                f"{config.get('api_key_env', 'ANTHROPIC_API_KEY')}"
            )
        return AnthropicProvider(api_key=api_key, model=model)
    
    elif provider == "ollama":
        from .ollama_provider import OllamaProvider
        ollama_config = config.get("ollama", {})
        base_url = ollama_config.get("base_url", "http://localhost:11434")
        return OllamaProvider(base_url=base_url, model=model)
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


__all__ = ["get_llm_provider", "BaseLLMProvider"]
