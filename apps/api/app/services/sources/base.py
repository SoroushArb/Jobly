from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from app.schemas import JobPosting


@dataclass
class RawJob:
    """Raw job data before parsing into JobPosting schema"""
    title: str
    url: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    posted_date: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)  # Store original data for debugging


class Source(ABC):
    """Abstract base class for job sources"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize source with configuration
        
        Args:
            config: Source configuration dict from job_sources_config.yaml
        """
        self.name = config.get("name", "Unknown")
        self.source_type = config.get("type", "unknown")
        self.url = config.get("url", "")
        self.compliance_note = config.get("compliance_note", "")
        self.rate_limit_seconds = config.get("rate_limit_seconds", 60)
        self.enabled = config.get("enabled", True)
        self.config = config
    
    @abstractmethod
    async def fetch(self) -> List[RawJob]:
        """
        Fetch raw job data from the source
        
        Returns:
            List of RawJob objects
        
        Raises:
            Exception if fetching fails
        """
        pass
    
    @abstractmethod
    def parse(self, raw_job: RawJob) -> JobPosting:
        """
        Parse raw job data into JobPosting schema
        
        Args:
            raw_job: RawJob object to parse
            
        Returns:
            JobPosting object
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if source is enabled"""
        return self.enabled
