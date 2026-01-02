"""Application tracking schemas for job applications"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ApplicationStatus(str, Enum):
    """Status of a job application"""
    PREPARED = "prepared"  # Packet generated, ready to apply
    INTENT_CREATED = "intent_created"  # Prefill intent created
    PREFILLING = "prefilling"  # Browser is filling the form
    PREFILLED = "prefilled"  # Form filled, waiting for user confirmation
    APPLIED = "applied"  # User confirmed submission
    REJECTED = "rejected"  # Application rejected
    INTERVIEWING = "interviewing"  # In interview process
    OFFERED = "offered"  # Job offer received
    ACCEPTED = "accepted"  # Offer accepted
    DECLINED = "declined"  # Offer declined
    WITHDRAWN = "withdrawn"  # Application withdrawn


class PrefillIntent(BaseModel):
    """Intent to prefill a job application form"""
    
    # References
    packet_id: str
    job_url: str
    
    # User data for filling
    user_fields: Dict[str, Any] = Field(default_factory=dict)  # Canonical field -> value mapping
    attachments: Dict[str, str] = Field(default_factory=dict)  # attachment_type -> file_path
    common_answers: Dict[str, str] = Field(default_factory=dict)  # question_key -> answer
    
    # Authentication
    auth_token: Optional[str] = None  # Short-lived token for local agent
    token_expires_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, in_progress, completed, failed


class PrefillIntentInDB(PrefillIntent):
    """PrefillIntent as stored in database"""
    id: Optional[str] = Field(alias="_id", default=None)
    
    class Config:
        populate_by_name = True


class PrefillLog(BaseModel):
    """Log of a prefill operation"""
    
    # Reference
    intent_id: str
    
    # ATS detection
    detected_ats: Optional[str] = None  # greenhouse, lever, workday, linkedin, generic
    detection_confidence: float = 0.0
    
    # Field filling results
    filled_fields: List[Dict[str, Any]] = Field(default_factory=list)  # [{field_name, value, success}]
    missing_fields: List[str] = Field(default_factory=list)  # Fields we couldn't find/fill
    errors: List[Dict[str, str]] = Field(default_factory=list)  # [{field, error_message}]
    
    # Attachments
    resume_attached: bool = False
    attachment_errors: List[str] = Field(default_factory=list)
    
    # Artifacts
    screenshot_paths: List[str] = Field(default_factory=list)  # Paths to screenshots
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: float = 0.0
    stopped_before_submit: bool = True  # Safety flag
    
    # Field mapping learned
    field_mappings: Dict[str, Dict[str, str]] = Field(default_factory=dict)  # canonical_field -> {selector, type}


class PrefillLogInDB(PrefillLog):
    """PrefillLog as stored in database"""
    id: Optional[str] = Field(alias="_id", default=None)
    
    class Config:
        populate_by_name = True


class Application(BaseModel):
    """Job application tracking"""
    
    # References
    job_id: str
    packet_id: str
    profile_id: str
    
    # Application details
    job_title: str
    company_name: str
    job_url: str
    
    # Status tracking
    status: ApplicationStatus = ApplicationStatus.PREPARED
    status_history: List[Dict[str, Any]] = Field(default_factory=list)  # [{status, timestamp, note}]
    
    # Prefill tracking
    prefill_intent_id: Optional[str] = None
    prefill_log_id: Optional[str] = None
    last_prefill_at: Optional[datetime] = None
    
    # User notes
    notes: str = ""
    
    # Dates
    applied_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ApplicationInDB(Application):
    """Application as stored in database"""
    id: Optional[str] = Field(alias="_id", default=None)
    
    class Config:
        populate_by_name = True


class CreateApplicationRequest(BaseModel):
    """Request to create an application from a packet"""
    packet_id: str
    job_id: str
    notes: Optional[str] = None


class UpdateApplicationStatusRequest(BaseModel):
    """Request to update application status"""
    status: ApplicationStatus
    note: Optional[str] = None


class PrefillIntentRequest(BaseModel):
    """Request to create a prefill intent"""
    application_id: str


class PrefillResultRequest(BaseModel):
    """Request from local agent to report prefill results"""
    intent_id: str
    log: PrefillLog
    auth_token: str  # Must match the intent's token
