"""Storage service for application packets"""
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

from app.schemas.packet import Packet, PacketFile, PacketInDB
from app.models.database import get_packets_collection
from bson import ObjectId


class PacketStorageService:
    """Service for storing and retrieving application packets"""
    
    def __init__(self):
        self.packets_dir = Path(os.getenv("PACKETS_DIR", "/tmp/jobly_packets"))
        self.packets_dir.mkdir(parents=True, exist_ok=True)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove any path separators and dangerous characters
        safe_name = filename.replace('/', '_').replace('\\', '_').replace('..', '')
        # Only allow alphanumeric, dash, underscore, dot
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '._-')
        return safe_name
    
    def _get_packet_dir(self, packet_id: str) -> Path:
        """Get directory for a specific packet"""
        safe_id = self._sanitize_filename(packet_id)
        packet_dir = self.packets_dir / safe_id
        packet_dir.mkdir(parents=True, exist_ok=True)
        return packet_dir
    
    def save_file(
        self, 
        packet_id: str, 
        filename: str, 
        content: str,
        file_type: str
    ) -> PacketFile:
        """
        Save a file to the packet directory.
        
        Returns PacketFile with metadata.
        """
        safe_filename = self._sanitize_filename(filename)
        packet_dir = self._get_packet_dir(packet_id)
        
        file_path = packet_dir / safe_filename
        file_path.write_text(content, encoding='utf-8')
        
        # Compute hash
        from app.services.tailoring import compute_file_hash
        content_hash = compute_file_hash(content)
        
        # Relative path from PACKETS_DIR
        relative_path = f"{packet_id}/{safe_filename}"
        
        return PacketFile(
            filename=safe_filename,
            filepath=relative_path,
            content_hash=content_hash,
            file_type=file_type
        )
    
    def save_binary_file(
        self,
        packet_id: str,
        filename: str,
        source_path: Path,
        file_type: str
    ) -> PacketFile:
        """
        Save a binary file (like PDF) to the packet directory.
        
        Returns PacketFile with metadata.
        """
        safe_filename = self._sanitize_filename(filename)
        packet_dir = self._get_packet_dir(packet_id)
        
        dest_path = packet_dir / safe_filename
        shutil.copy2(source_path, dest_path)
        
        # Compute hash
        import hashlib
        content_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        
        # Relative path from PACKETS_DIR
        relative_path = f"{packet_id}/{safe_filename}"
        
        return PacketFile(
            filename=safe_filename,
            filepath=relative_path,
            content_hash=content_hash,
            file_type=file_type
        )
    
    def get_file_path(self, packet_file: PacketFile) -> Path:
        """Get absolute path to a packet file"""
        return self.packets_dir / packet_file.filepath
    
    def read_file(self, packet_file: PacketFile) -> str:
        """Read text content of a packet file"""
        file_path = self.get_file_path(packet_file)
        return file_path.read_text(encoding='utf-8')
    
    async def save_packet(self, packet: Packet) -> PacketInDB:
        """Save packet metadata to MongoDB"""
        collection = get_packets_collection()
        
        packet_dict = packet.model_dump(by_alias=True, exclude={"id"})
        result = await collection.insert_one(packet_dict)
        
        packet_in_db = PacketInDB(**packet_dict, id=str(result.inserted_id))
        return packet_in_db
    
    async def get_packet(self, packet_id: str) -> Optional[PacketInDB]:
        """Retrieve packet metadata from MongoDB"""
        collection = get_packets_collection()
        
        try:
            packet_data = await collection.find_one({"_id": ObjectId(packet_id)})
        except:
            return None
        
        if not packet_data:
            return None
        
        packet_data["_id"] = str(packet_data["_id"])
        return PacketInDB(**packet_data)
    
    async def list_packets(
        self,
        profile_id: Optional[str] = None,
        job_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[list[PacketInDB], int]:
        """List packets with optional filtering"""
        collection = get_packets_collection()
        
        query = {}
        if profile_id:
            query["profile_id"] = profile_id
        if job_id:
            query["job_id"] = job_id
        
        total = await collection.count_documents(query)
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        
        packets = []
        async for packet_data in cursor:
            packet_data["_id"] = str(packet_data["_id"])
            packets.append(PacketInDB(**packet_data))
        
        return packets, total
    
    async def update_packet(self, packet_id: str, updates: dict) -> Optional[PacketInDB]:
        """Update packet metadata"""
        collection = get_packets_collection()
        
        updates["updated_at"] = datetime.utcnow()
        
        try:
            result = await collection.find_one_and_update(
                {"_id": ObjectId(packet_id)},
                {"$set": updates},
                return_document=True
            )
        except:
            return None
        
        if not result:
            return None
        
        result["_id"] = str(result["_id"])
        return PacketInDB(**result)
    
    def cleanup_packet_files(self, packet_id: str):
        """Delete all files for a packet"""
        packet_dir = self._get_packet_dir(packet_id)
        if packet_dir.exists():
            shutil.rmtree(packet_dir)
