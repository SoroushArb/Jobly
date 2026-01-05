"""Tests for GridFS storage"""
import pytest
from app.services.storage.gridfs_storage import GridFSStorage
from app.services.storage.filesystem_storage import FilesystemStorage


@pytest.mark.asyncio
class TestGridFSStorage:
    """Test GridFS storage implementation"""
    
    @pytest.fixture
    def storage(self):
        """Create a GridFS storage instance for testing"""
        # Note: This requires a MongoDB connection
        # In a real test environment, you'd use a test database
        return GridFSStorage(bucket_name="test_artifacts")
    
    async def test_save_and_get_file(self, storage):
        """Test saving and retrieving a file"""
        content = b"Hello, World!"
        
        # Save file
        metadata = await storage.save_file(
            file_id="test_file_1",
            filename="test.txt",
            content=content,
            content_type="text/plain"
        )
        
        assert metadata["file_id"] == "test_file_1"
        assert metadata["filename"] == "test.txt"
        assert metadata["size"] == len(content)
        assert "hash" in metadata
        assert "storage_id" in metadata
        
        # Retrieve file
        retrieved = await storage.get_file("test_file_1")
        assert retrieved == content
        
        # Cleanup
        await storage.delete_file("test_file_1")
    
    async def test_file_exists(self, storage):
        """Test checking if file exists"""
        content = b"Test content"
        
        # File doesn't exist yet
        exists = await storage.file_exists("test_file_2")
        assert not exists
        
        # Save file
        await storage.save_file(
            file_id="test_file_2",
            filename="test2.txt",
            content=content
        )
        
        # File should exist now
        exists = await storage.file_exists("test_file_2")
        assert exists
        
        # Cleanup
        await storage.delete_file("test_file_2")
    
    async def test_get_file_metadata(self, storage):
        """Test getting file metadata without downloading"""
        content = b"Metadata test"
        
        # Save file
        await storage.save_file(
            file_id="test_file_3",
            filename="test3.txt",
            content=content,
            content_type="text/plain",
            metadata={"custom": "value"}
        )
        
        # Get metadata
        metadata = await storage.get_file_metadata("test_file_3")
        
        assert metadata is not None
        assert metadata["file_id"] == "test_file_3"
        assert metadata["filename"] == "test3.txt"
        assert metadata["size"] == len(content)
        assert metadata["content_type"] == "text/plain"
        assert "upload_date" in metadata
        
        # Cleanup
        await storage.delete_file("test_file_3")
    
    async def test_delete_file(self, storage):
        """Test deleting a file"""
        content = b"Delete me"
        
        # Save file
        await storage.save_file(
            file_id="test_file_4",
            filename="test4.txt",
            content=content
        )
        
        # File exists
        exists = await storage.file_exists("test_file_4")
        assert exists
        
        # Delete file
        deleted = await storage.delete_file("test_file_4")
        assert deleted
        
        # File no longer exists
        exists = await storage.file_exists("test_file_4")
        assert not exists
    
    async def test_get_nonexistent_file(self, storage):
        """Test getting a file that doesn't exist"""
        retrieved = await storage.get_file("nonexistent_file")
        assert retrieved is None
        
        metadata = await storage.get_file_metadata("nonexistent_file")
        assert metadata is None


@pytest.mark.asyncio
class TestFilesystemStorage:
    """Test filesystem storage implementation"""
    
    @pytest.fixture
    def storage(self):
        """Create a filesystem storage instance for testing"""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        return FilesystemStorage(base_dir=temp_dir)
    
    async def test_save_and_get_file(self, storage):
        """Test saving and retrieving a file"""
        content = b"Hello, Filesystem!"
        
        # Save file
        metadata = await storage.save_file(
            file_id="fs_test_1",
            filename="test.txt",
            content=content,
            content_type="text/plain"
        )
        
        assert metadata["file_id"] == "fs_test_1"
        assert metadata["filename"] == "test.txt"
        assert metadata["size"] == len(content)
        
        # Retrieve file
        retrieved = await storage.get_file("fs_test_1")
        assert retrieved == content
        
        # Cleanup
        await storage.delete_file("fs_test_1")
    
    async def test_file_exists(self, storage):
        """Test checking if file exists"""
        content = b"Exists test"
        
        # File doesn't exist yet
        exists = await storage.file_exists("fs_test_2")
        assert not exists
        
        # Save file
        await storage.save_file(
            file_id="fs_test_2",
            filename="test2.txt",
            content=content
        )
        
        # File should exist now
        exists = await storage.file_exists("fs_test_2")
        assert exists
        
        # Cleanup
        await storage.delete_file("fs_test_2")
