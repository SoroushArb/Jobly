from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime
import hashlib


class JobPosting(BaseModel):
    """Job posting schema with deduplication and source tracking"""
    
    # Core job information
    company: str
    title: str
    url: str  # Job posting URL
    location: Optional[str] = None  # Full location string
    country: Optional[str] = None
    city: Optional[str] = None
    remote_type: str = "unknown"  # onsite/hybrid/remote/unknown
    
    # Job description
    description_raw: Optional[str] = None  # Original HTML/text
    description_clean: Optional[str] = None  # Cleaned text
    
    # Optional fields
    posted_date: Optional[datetime] = None
    employment_type: Optional[str] = None  # full-time/part-time/contract/internship
    
    # Source metadata
    source_name: str  # e.g., "Google Careers", "Stack Overflow RSS"
    source_type: str  # company/rss/api
    source_compliance_note: Optional[str] = None  # Legal compliance note
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Deduplication
    dedupe_hash: str = ""  # sha256 hash for deduplication
    
    # Persistence tracking
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    
    def model_post_init(self, __context) -> None:
        """Generate dedupe_hash after initialization if not set"""
        if not self.dedupe_hash:
            self.dedupe_hash = self.generate_hash()
    
    def generate_hash(self) -> str:
        """Generate SHA256 hash for deduplication based on normalized fields"""
        # Normalize fields for consistent hashing
        normalized_company = self.company.lower().strip()
        normalized_title = self.title.lower().strip()
        normalized_url = self.url.lower().strip()
        
        # Create hash from stable fields
        hash_string = f"{normalized_company}|{normalized_title}|{normalized_url}"
        return hashlib.sha256(hash_string.encode()).hexdigest()


class JobPostingInDB(JobPosting):
    """Job posting as stored in database with MongoDB ID"""
    id: Optional[str] = Field(alias="_id", default=None)
    
    class Config:
        populate_by_name = True


class JobPostingResponse(BaseModel):
    """Response for single job posting"""
    job: JobPostingInDB
    message: str = "Job retrieved successfully"


class JobListResponse(BaseModel):
    """Response for job listing with pagination"""
    jobs: list[JobPostingInDB]
    total: int
    page: int = 1
    per_page: int = 50
    message: str = "Jobs retrieved successfully"


class IngestResponse(BaseModel):
    """Response from job ingestion"""
    jobs_fetched: int
    jobs_new: int
    jobs_updated: int
    sources_processed: list[str]
    message: str = "Ingestion completed successfully"
