"""
Job queue schemas for background job execution
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class JobType(str, Enum):
    """Types of background jobs"""
    JOB_INGESTION = "job_ingestion"
    MATCH_RECOMPUTE = "match_recompute"
    PACKET_GENERATION = "packet_generation"
    INTERVIEW_GENERATION = "interview_generation"


class JobStatus(str, Enum):
    """Status of background jobs"""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class BackgroundJob(BaseModel):
    """Background job model"""
    user_id: Optional[str] = Field(None, description="User ID (for multi-user systems)")
    type: JobType = Field(..., description="Job type")
    status: JobStatus = Field(default=JobStatus.QUEUED, description="Job status")
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    message: Optional[str] = Field(None, description="Progress or status message")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    # Resource references
    resource_refs: Dict[str, Any] = Field(default_factory=dict, description="Resource references (job_id, packet_id, etc)")
    
    # Job parameters
    params: Dict[str, Any] = Field(default_factory=dict, description="Job parameters")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Worker tracking
    worker_id: Optional[str] = Field(None, description="ID of worker processing this job")
    lock_expires_at: Optional[datetime] = Field(None, description="Job lock expiration time")
    
    # Result data
    result: Optional[Dict[str, Any]] = Field(None, description="Job result data")


class BackgroundJobInDB(BackgroundJob):
    """Background job as stored in database"""
    id: str = Field(..., alias="_id")
    
    class Config:
        populate_by_name = True


class JobCreateRequest(BaseModel):
    """Request to create a new job"""
    type: JobType
    params: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None


class JobResponse(BaseModel):
    """Response for job creation"""
    job_id: str
    type: JobType
    status: JobStatus
    message: str


class JobListResponse(BaseModel):
    """Response for listing jobs"""
    jobs: list[BackgroundJobInDB]
    total: int
    page: int
    per_page: int
