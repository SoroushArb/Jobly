"""
Abstract storage interface for application artifacts
"""
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
from pathlib import Path


class ArtifactStorage(ABC):
    """Abstract interface for storing application artifacts (packets, CVs, etc.)"""
    
    @abstractmethod
    async def save_file(
        self,
        file_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Save a file to storage.
        
        Args:
            file_id: Unique identifier for the file
            filename: Original filename
            content: File content as bytes
            content_type: MIME type of the file
            metadata: Optional metadata dictionary
            
        Returns:
            dict with file metadata including storage_id, size, hash, etc.
        """
        pass
    
    @abstractmethod
    async def get_file(self, file_id: str) -> Optional[bytes]:
        """
        Retrieve file content by ID.
        
        Args:
            file_id: File identifier
            
        Returns:
            File content as bytes, or None if not found
        """
        pass
    
    @abstractmethod
    async def get_file_stream(self, file_id: str) -> Optional[BinaryIO]:
        """
        Get a stream to read file content.
        
        Args:
            file_id: File identifier
            
        Returns:
            File stream, or None if not found
        """
        pass
    
    @abstractmethod
    async def get_file_metadata(self, file_id: str) -> Optional[dict]:
        """
        Get file metadata without downloading content.
        
        Args:
            file_id: File identifier
            
        Returns:
            Metadata dict, or None if not found
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_id: File identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def file_exists(self, file_id: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            file_id: File identifier
            
        Returns:
            True if exists, False otherwise
        """
        pass
