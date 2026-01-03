"""
GridFS storage implementation for MongoDB
"""
import hashlib
import logging
from typing import Optional, BinaryIO
from io import BytesIO
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from bson import ObjectId

from app.models.database import Database
from .base import ArtifactStorage

logger = logging.getLogger(__name__)


class GridFSStorage(ArtifactStorage):
    """GridFS-based storage for application artifacts"""
    
    def __init__(self, bucket_name: str = "artifacts"):
        """
        Initialize GridFS storage.
        
        Args:
            bucket_name: Name of the GridFS bucket (default: "artifacts")
        """
        self.bucket_name = bucket_name
        self._bucket: Optional[AsyncIOMotorGridFSBucket] = None
    
    def _get_bucket(self) -> AsyncIOMotorGridFSBucket:
        """Get or create GridFS bucket"""
        if self._bucket is None:
            db = Database.get_database()
            self._bucket = AsyncIOMotorGridFSBucket(db, bucket_name=self.bucket_name)
        return self._bucket
    
    async def save_file(
        self,
        file_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Save a file to GridFS.
        
        Returns dict with:
        - storage_id: GridFS file ID
        - filename: Original filename
        - size: File size in bytes
        - hash: SHA256 hash of content
        - content_type: MIME type
        - metadata: Additional metadata
        """
        bucket = self._get_bucket()
        
        # Compute hash
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Prepare metadata
        file_metadata = metadata or {}
        file_metadata.update({
            "file_id": file_id,
            "hash": content_hash,
            "content_type": content_type,
        })
        
        # Upload to GridFS
        storage_id = await bucket.upload_from_stream(
            filename,
            BytesIO(content),
            metadata=file_metadata
        )
        
        logger.info(f"Saved file {filename} to GridFS with ID {storage_id}")
        
        return {
            "storage_id": str(storage_id),
            "file_id": file_id,
            "filename": filename,
            "size": len(content),
            "hash": content_hash,
            "content_type": content_type,
            "metadata": file_metadata,
        }
    
    async def get_file(self, file_id: str) -> Optional[bytes]:
        """Retrieve file content by file_id"""
        bucket = self._get_bucket()
        
        # Find file by metadata.file_id
        cursor = bucket.find({"metadata.file_id": file_id})
        files = await cursor.to_list(length=1)
        
        if not files:
            logger.warning(f"File {file_id} not found in GridFS")
            return None
        
        file_doc = files[0]
        grid_out = await bucket.open_download_stream(file_doc._id)
        content = await grid_out.read()
        
        return content
    
    async def get_file_stream(self, file_id: str) -> Optional[BinaryIO]:
        """Get a stream to read file content"""
        bucket = self._get_bucket()
        
        # Find file by metadata.file_id
        cursor = bucket.find({"metadata.file_id": file_id})
        files = await cursor.to_list(length=1)
        
        if not files:
            logger.warning(f"File {file_id} not found in GridFS")
            return None
        
        file_doc = files[0]
        grid_out = await bucket.open_download_stream(file_doc._id)
        
        # Read all content and return as BytesIO
        # Note: For very large files, consider using grid_out directly
        # But that requires async iteration which doesn't work well with
        # FastAPI's StreamingResponse directly
        content = await grid_out.read()
        return BytesIO(content)
    
    async def get_file_metadata(self, file_id: str) -> Optional[dict]:
        """Get file metadata without downloading content"""
        bucket = self._get_bucket()
        
        # Find file by metadata.file_id
        cursor = bucket.find({"metadata.file_id": file_id})
        files = await cursor.to_list(length=1)
        
        if not files:
            return None
        
        file_doc = files[0]
        
        return {
            "storage_id": str(file_doc._id),
            "file_id": file_id,
            "filename": file_doc.filename,
            "size": file_doc.length,
            "upload_date": file_doc.upload_date,
            "content_type": file_doc.metadata.get("content_type", "application/octet-stream"),
            "hash": file_doc.metadata.get("hash"),
            "metadata": file_doc.metadata,
        }
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from GridFS"""
        bucket = self._get_bucket()
        
        # Find file by metadata.file_id
        cursor = bucket.find({"metadata.file_id": file_id})
        files = await cursor.to_list(length=1)
        
        if not files:
            return False
        
        file_doc = files[0]
        await bucket.delete(file_doc._id)
        
        logger.info(f"Deleted file {file_id} from GridFS")
        return True
    
    async def file_exists(self, file_id: str) -> bool:
        """Check if a file exists in GridFS"""
        bucket = self._get_bucket()
        
        # Find file by metadata.file_id
        cursor = bucket.find({"metadata.file_id": file_id})
        files = await cursor.to_list(length=1)
        
        return len(files) > 0
