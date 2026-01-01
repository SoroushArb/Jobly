"""Match schemas for job matching results"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of match score components"""
    semantic: float = 0.0
    skill_overlap: float = 0.0
    seniority_fit: float = 0.0
    location_fit: float = 0.0
    recency: float = 0.0


class Match(BaseModel):
    """Job match with scoring and explainability"""
    
    # Reference IDs
    profile_id: str  # ObjectId as string
    job_id: str  # ObjectId as string
    
    # Scoring
    score_total: float  # Final weighted score (0-1)
    score_breakdown: ScoreBreakdown
    
    # Explainability
    top_reasons: List[str] = Field(default_factory=list, max_length=5)
    gaps: List[str] = Field(default_factory=list)  # Missing skills/evidence
    recommendations: List[str] = Field(default_factory=list)  # Actionable advice
    
    # Metadata
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    embedding_model: str = "text-embedding-3-small"
    
    # For deterministic sorting
    posted_date: Optional[datetime] = None


class MatchInDB(Match):
    """Match as stored in database with MongoDB ID"""
    id: Optional[str] = Field(alias="_id", default=None)
    
    class Config:
        populate_by_name = True


class MatchWithJob(BaseModel):
    """Match combined with job details for API responses"""
    match: MatchInDB
    job: Dict  # Job posting details
    

class MatchResponse(BaseModel):
    """Response for single match"""
    match: MatchInDB
    job: Optional[Dict] = None
    message: str = "Match retrieved successfully"


class MatchListResponse(BaseModel):
    """Response for match listing"""
    matches: List[MatchWithJob]
    total: int
    page: int = 1
    per_page: int = 50
    message: str = "Matches retrieved successfully"


class RecomputeMatchesResponse(BaseModel):
    """Response from match recomputation"""
    matches_computed: int
    profile_id: str
    jobs_processed: int
    message: str = "Matches recomputed successfully"
