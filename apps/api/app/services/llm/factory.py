"""Factory for creating LLM provider instances"""
import os
from typing import Optional
from .base import LLMProvider
from .openai_provider import OpenAILLMProvider


def get_llm_provider(
    provider_type: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> LLMProvider:
    """
    Factory function to create LLM provider instances
    
    Args:
        provider_type: Type of provider ("openai"). If None, uses LLM_PROVIDER env var
        api_key: API key for the provider. If None, uses provider-specific env var
        model: Model name to use. If None, uses provider default
        
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If provider_type is unsupported
    """
    if provider_type is None:
        provider_type = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider_type == "openai":
        return OpenAILLMProvider(
            api_key=api_key,
            model=model or os.getenv("LLM_MODEL", "gpt-4o-mini")
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_type}")
