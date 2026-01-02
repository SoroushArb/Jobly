from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        if cls.client is None:
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            cls.client = AsyncIOMotorClient(mongodb_uri)
        return cls.client
    
    @classmethod
    def get_database(cls):
        db_name = os.getenv("MONGODB_DB_NAME", "jobly")
        return cls.get_client()[db_name]
    
    @classmethod
    async def close(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None


def get_profiles_collection():
    """Get the profiles collection"""
    db = Database.get_database()
    return db["profiles"]


def get_jobs_collection():
    """Get the jobs collection"""
    db = Database.get_database()
    return db["jobs"]


def get_matches_collection():
    """Get the matches collection"""
    db = Database.get_database()
    return db["matches"]


def get_packets_collection():
    """Get the packets collection"""
    db = Database.get_database()
    return db["packets"]

