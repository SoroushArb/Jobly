"""
Filesystem storage implementation for local development
"""
import hashlib
import logging
import os
from typing import Optional, BinaryIO
from pathlib import Path
from io import BytesIO
import json

from .base import ArtifactStorage

logger = logging.getLogger(__name__)


class FilesystemStorage(ArtifactStorage):
    """Filesystem-based storage for local development"""
    
    def __init__(self, base_dir: str = "/tmp/jobly_artifacts"):
        """
        Initialize filesystem storage.
        
        Args:
            base_dir: Base directory for storing files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, file_id: str) -> Path:
        """Get path for a file"""
        # Use first 2 chars of file_id for subdirectory to avoid too many files in one dir
        subdir = file_id[:2] if len(file_id) >= 2 else "00"
        dir_path = self.base_dir / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / file_id
    
    def _get_metadata_path(self, file_id: str) -> Path:
        """Get path for metadata file"""
        return self._get_file_path(file_id).with_suffix(".meta.json")
    
    async def save_file(
        self,
        file_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None,
    ) -> dict:
        """Save a file to filesystem"""
        file_path = self._get_file_path(file_id)
        meta_path = self._get_metadata_path(file_id)
        
        # Compute hash
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Save file
        file_path.write_bytes(content)
        
        # Save metadata
        file_metadata = {
            "storage_id": file_id,
            "file_id": file_id,
            "filename": filename,
            "size": len(content),
            "hash": content_hash,
            "content_type": content_type,
            "metadata": metadata or {},
        }
        
        meta_path.write_text(json.dumps(file_metadata, indent=2))
        
        logger.info(f"Saved file {filename} to filesystem with ID {file_id}")
        
        return file_metadata
    
    async def get_file(self, file_id: str) -> Optional[bytes]:
        """Retrieve file content by file_id"""
        file_path = self._get_file_path(file_id)
        
        if not file_path.exists():
            logger.warning(f"File {file_id} not found in filesystem")
            return None
        
        return file_path.read_bytes()
    
    async def get_file_stream(self, file_id: str) -> Optional[BinaryIO]:
        """Get a stream to read file content"""
        file_path = self._get_file_path(file_id)
        
        if not file_path.exists():
            logger.warning(f"File {file_id} not found in filesystem")
            return None
        
        content = file_path.read_bytes()
        return BytesIO(content)
    
    async def get_file_metadata(self, file_id: str) -> Optional[dict]:
        """Get file metadata without downloading content"""
        meta_path = self._get_metadata_path(file_id)
        
        if not meta_path.exists():
            return None
        
        return json.loads(meta_path.read_text())
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from filesystem"""
        file_path = self._get_file_path(file_id)
        meta_path = self._get_metadata_path(file_id)
        
        if not file_path.exists():
            return False
        
        file_path.unlink()
        if meta_path.exists():
            meta_path.unlink()
        
        logger.info(f"Deleted file {file_id} from filesystem")
        return True
    
    async def file_exists(self, file_id: str) -> bool:
        """Check if a file exists in filesystem"""
        file_path = self._get_file_path(file_id)
        return file_path.exists()
