"""Base interface for embedding providers"""
from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        pass
    
    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embedding vectors for multiple texts (batch operation)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name/identifier of the embedding model
        
        Returns:
            Model name string
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimensionality of the embedding vectors
        
        Returns:
            Dimension as integer
        """
        pass
