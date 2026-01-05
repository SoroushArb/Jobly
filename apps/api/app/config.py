"""
Environment configuration and validation
"""
import os
import sys
import logging
from typing import Optional
from app.utils import parse_bool

logger = logging.getLogger(__name__)


class Config:
    """Application configuration from environment variables"""
    
    # Required environment variables
    REQUIRED_VARS = [
        "MONGODB_URI",
    ]
    
    # Optional with defaults
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "jobly")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # OpenAI (optional for embeddings/LLM)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "openai")
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    # Storage
    PACKETS_DIR: str = os.getenv("PACKETS_DIR", "/tmp/jobly_packets")
    USE_GRIDFS: bool = parse_bool(os.getenv("USE_GRIDFS", "false"))
    
    # MongoDB URI
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate required environment variables.
        
        Returns True if all required vars are set, False otherwise.
        Logs warnings for optional vars that are not set.
        """
        all_valid = True
        
        # Check required variables
        for var in cls.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                logger.error(f"Required environment variable {var} is not set")
                all_valid = False
        
        # Warn about optional but important variables
        if not cls.OPENAI_API_KEY:
            logger.warning(
                "OPENAI_API_KEY not set - embeddings and LLM features will not work"
            )
        
        # Validate PORT is a valid number
        try:
            port = int(os.getenv("PORT", "8000"))
            if port < 1 or port > 65535:
                logger.error(f"PORT must be between 1 and 65535, got {port}")
                all_valid = False
        except ValueError:
            logger.error(f"PORT must be a valid integer, got {os.getenv('PORT')}")
            all_valid = False
        
        # Log configuration
        if all_valid:
            logger.info("Environment validation successful")
            logger.info(f"MongoDB Database: {cls.MONGODB_DB_NAME}")
            logger.info(f"CORS Origins: {cls.CORS_ORIGINS}")
            logger.info(f"Port: {cls.PORT}")
            logger.info(f"GridFS Storage: {cls.USE_GRIDFS}")
            logger.info(f"LLM Provider: {cls.LLM_PROVIDER}")
            logger.info(f"Embedding Provider: {cls.EMBEDDING_PROVIDER}")
        
        return all_valid
    
    @classmethod
    def validate_or_exit(cls):
        """Validate environment and exit if invalid"""
        if not cls.validate():
            logger.error("Environment validation failed. Exiting.")
            sys.exit(1)


# Singleton instance
config = Config()
