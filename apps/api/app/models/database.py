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


def get_interview_packs_collection():
    """Get the interview packs collection"""
    db = Database.get_database()
    return db["interview_packs"]


def get_technical_qa_collection():
    """Get the technical QA collection"""
    db = Database.get_database()
    return db["technical_qa"]


def get_applications_collection():
    """Get the applications collection"""
    db = Database.get_database()
    return db["applications"]


def get_prefill_intents_collection():
    """Get the prefill intents collection"""
    db = Database.get_database()
    return db["prefill_intents"]


def get_prefill_logs_collection():
    """Get the prefill logs collection"""
    db = Database.get_database()
    return db["prefill_logs"]


def get_cv_documents_collection():
    """Get the CV documents collection"""
    db = Database.get_database()
    return db["cv_documents"]


def get_background_jobs_collection():
    """Get the background jobs collection"""
    db = Database.get_database()
    return db["background_jobs"]

