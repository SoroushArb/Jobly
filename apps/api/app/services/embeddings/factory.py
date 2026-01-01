"""Factory for creating embedding providers"""
import os
from typing import Optional
from .base import EmbeddingProvider
from .openai_provider import OpenAIEmbeddingProvider


class EmbeddingProviderFactory:
    """Factory for creating embedding providers based on configuration"""
    
    @staticmethod
    def create_provider(
        provider_type: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> EmbeddingProvider:
        """
        Create an embedding provider based on configuration
        
        Args:
            provider_type: Type of provider ("openai" or None for default)
            model: Model name to use (provider-specific)
            api_key: API key for the provider
            
        Returns:
            Configured EmbeddingProvider instance
        """
        # Default to OpenAI if not specified
        provider_type = provider_type or os.getenv("EMBEDDING_PROVIDER", "openai")
        
        if provider_type.lower() == "openai":
            model = model or os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            return OpenAIEmbeddingProvider(api_key=api_key, model=model)
        else:
            raise ValueError(f"Unknown embedding provider: {provider_type}")
