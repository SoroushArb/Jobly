"""Packet schemas for tailored CV generation and application materials"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class BulletSwap(BaseModel):
    """Suggested bullet point swap for experience role"""
    role_index: int  # Index in experience list
    original_bullet: str
    suggested_bullet: str
    evidence_ref: Optional[str] = None
    reason: str  # Why this swap improves the match


class TailoringPlan(BaseModel):
    """Structured plan for tailoring a CV to a specific job"""
    
    # Job and profile references
    job_id: str
    profile_id: str
    
    # Tailoring components
    summary_rewrite: str  # Tailored professional summary
    skills_priority: List[str] = Field(default_factory=list)  # Ordered skills to emphasize
    bullet_swaps: List[BulletSwap] = Field(default_factory=list)  # Suggested bullet improvements
    keyword_inserts: Dict[str, List[str]] = Field(default_factory=dict)  # Section -> keywords to naturally include
    
    # Integrity tracking
    gaps: List[str] = Field(default_factory=list)  # Skills/requirements user lacks
    integrity_notes: List[str] = Field(default_factory=list)  # Warnings about truthfulness
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_version: str = "1.0.0"


class PacketFile(BaseModel):
    """File information for a packet asset"""
    filename: str
    filepath: str  # Relative to PACKETS_DIR
    content_hash: str  # SHA256 for integrity
    file_type: str  # tex, pdf, md, txt
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Packet(BaseModel):
    """Application packet with tailored materials for a job"""
    
    # References
    job_id: str
    profile_id: str
    match_id: Optional[str] = None  # Link to the match that triggered generation
    
    # Tailoring plan
    tailoring_plan: TailoringPlan
    
    # Generated files
    cv_tex: PacketFile
    cv_pdf: Optional[PacketFile] = None  # Only if compilation succeeded
    cover_letter: Optional[PacketFile] = None  # Optional
    recruiter_message: PacketFile
    common_answers: PacketFile
    
    # User customizations
    user_notes: Optional[str] = None
    regeneration_count: int = 0  # Track how many times regenerated
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PacketInDB(Packet):
    """Packet as stored in database with MongoDB ID"""
    id: Optional[str] = Field(alias="_id", default=None)
    
    class Config:
        populate_by_name = True


class GeneratePacketRequest(BaseModel):
    """Request to generate a new packet"""
    job_id: str
    include_cover_letter: bool = False
    user_emphasis: Optional[List[str]] = None  # e.g., ["emphasize project X", "highlight AWS experience"]


class PacketResponse(BaseModel):
    """Response for single packet"""
    packet: PacketInDB
    message: str = "Packet generated successfully"


class PacketListResponse(BaseModel):
    """Response for packet listing"""
    packets: List[PacketInDB]
    total: int
    page: int = 1
    per_page: int = 50
    message: str = "Packets retrieved successfully"
