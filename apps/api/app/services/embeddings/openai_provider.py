"""OpenAI embedding provider implementation"""
import os
from typing import List
from openai import AsyncOpenAI
from .base import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider using text-embedding-3-small model"""
    
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embedding provider
        
        Args:
            api_key: OpenAI API key (if None, will use OPENAI_API_KEY env var)
            model: Model name to use for embeddings
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY env var")
        
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Model dimensions - text-embedding-3-small has 1536 dimensions
        self._dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for a single text"""
        # Clean and truncate text if needed (OpenAI has token limits)
        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty")
        
        response = await self.client.embeddings.create(
            input=text,
            model=self.model
        )
        
        return response.data[0].embedding
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embedding vectors for multiple texts"""
        # Clean texts
        texts = [t.strip() for t in texts]
        if not all(texts):
            raise ValueError("All texts must be non-empty")
        
        response = await self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        
        # Sort by index to ensure order matches input
        sorted_data = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_data]
    
    def get_model_name(self) -> str:
        """Get the model name"""
        return self.model
    
    def get_dimension(self) -> int:
        """Get the embedding dimension"""
        return self._dimensions.get(self.model, 1536)
