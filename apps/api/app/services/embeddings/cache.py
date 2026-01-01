"""Embedding cache service for storing and retrieving embeddings"""
import hashlib
from typing import Optional, List
from datetime import datetime
from app.models.database import Database


class EmbeddingCache:
    """Cache for storing and retrieving embeddings in MongoDB"""
    
    def __init__(self):
        self.collection = Database.get_database()["embeddings"]
    
    @staticmethod
    def _generate_cache_key(text: str, model: str) -> str:
        """Generate cache key from text and model"""
        # Create hash from text + model to use as cache key
        hash_input = f"{model}:{text}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    async def get(self, text: str, model: str) -> Optional[List[float]]:
        """
        Get embedding from cache
        
        Args:
            text: Text that was embedded
            model: Model name used for embedding
            
        Returns:
            Embedding vector if found, None otherwise
        """
        cache_key = self._generate_cache_key(text, model)
        doc = await self.collection.find_one({"cache_key": cache_key})
        
        if doc:
            return doc.get("embedding")
        return None
    
    async def set(self, text: str, model: str, embedding: List[float]) -> None:
        """
        Store embedding in cache
        
        Args:
            text: Text that was embedded
            model: Model name used
            embedding: Embedding vector to cache
        """
        cache_key = self._generate_cache_key(text, model)
        
        doc = {
            "cache_key": cache_key,
            "text": text,
            "model": model,
            "embedding": embedding,
            "created_at": datetime.utcnow(),
        }
        
        # Upsert to handle duplicates
        await self.collection.update_one(
            {"cache_key": cache_key},
            {"$set": doc},
            upsert=True
        )
    
    async def get_batch(self, texts: List[str], model: str) -> dict[str, Optional[List[float]]]:
        """
        Get multiple embeddings from cache
        
        Args:
            texts: List of texts
            model: Model name
            
        Returns:
            Dictionary mapping text to embedding (or None if not cached)
        """
        cache_keys = {self._generate_cache_key(text, model): text for text in texts}
        
        cursor = self.collection.find({"cache_key": {"$in": list(cache_keys.keys())}})
        docs = await cursor.to_list(length=None)
        
        # Map cache keys back to original texts
        result = {text: None for text in texts}
        for doc in docs:
            original_text = cache_keys[doc["cache_key"]]
            result[original_text] = doc["embedding"]
        
        return result
    
    async def set_batch(self, texts: List[str], model: str, embeddings: List[List[float]]) -> None:
        """
        Store multiple embeddings in cache
        
        Args:
            texts: List of texts
            model: Model name
            embeddings: List of embedding vectors
        """
        if len(texts) != len(embeddings):
            raise ValueError("Number of texts and embeddings must match")
        
        docs = []
        for text, embedding in zip(texts, embeddings):
            cache_key = self._generate_cache_key(text, model)
            docs.append({
                "cache_key": cache_key,
                "text": text,
                "model": model,
                "embedding": embedding,
                "created_at": datetime.utcnow(),
            })
        
        # Bulk upsert
        for doc in docs:
            await self.collection.update_one(
                {"cache_key": doc["cache_key"]},
                {"$set": doc},
                upsert=True
            )
