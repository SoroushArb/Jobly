"""Storage factory and initialization"""
from typing import Optional
import os
import logging

from .base import ArtifactStorage
from .gridfs_storage import GridFSStorage
from .filesystem_storage import FilesystemStorage
from app.utils import parse_bool

logger = logging.getLogger(__name__)

_storage_instance: Optional[ArtifactStorage] = None


def get_storage() -> ArtifactStorage:
    """
    Get the configured storage backend.
    
    Returns GridFSStorage if USE_GRIDFS=true, otherwise FilesystemStorage.
    """
    global _storage_instance
    
    if _storage_instance is None:
        use_gridfs = parse_bool(os.getenv("USE_GRIDFS", "false"))
        
        if use_gridfs:
            logger.info("Using GridFS storage for artifacts")
            _storage_instance = GridFSStorage()
        else:
            packets_dir = os.getenv("PACKETS_DIR", "/tmp/jobly_artifacts")
            logger.info(f"Using filesystem storage for artifacts at {packets_dir}")
            _storage_instance = FilesystemStorage(base_dir=packets_dir)
    
    return _storage_instance


def reset_storage():
    """Reset storage instance (useful for testing)"""
    global _storage_instance
    _storage_instance = None
