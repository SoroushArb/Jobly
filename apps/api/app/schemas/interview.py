"""Interview preparation schemas"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Difficulty levels for technical questions"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class GroundingReference(BaseModel):
    """Reference to existing experience/evidence in user profile"""
    experience_index: int  # Index in profile.experience list
    bullet_index: Optional[int] = None  # Index in role.bullets list, if applicable
    evidence_text: str  # Snippet of the referenced text for verification


class STARStory(BaseModel):
    """STAR format interview story grounded in real experience"""
    title: str  # Brief title/theme of the story
    situation: str  # Context/background
    task: str  # Challenge or responsibility
    action: str  # What you specifically did
    result: str  # Outcome/impact with metrics if available
    skills_demonstrated: List[str] = Field(default_factory=list)  # Skills this story showcases
    grounding_refs: List[GroundingReference] = Field(default_factory=list)  # References to profile experience


class InterviewQuestion(BaseModel):
    """Question to ask the interviewer"""
    question: str
    category: str  # e.g., "role", "team", "culture", "growth", "technical"
    reasoning: str  # Why this question is relevant for this specific job


class StudyResource(BaseModel):
    """Study resource placeholder (no external links)"""
    topic: str
    resource_type: str  # e.g., "documentation", "tutorial", "practice problems"
    description: str  # What to study, placeholder for user to fill in actual links


class InterviewPack(BaseModel):
    """Complete interview preparation pack for a job"""
    
    # References
    packet_id: str
    job_id: str
    profile_id: str
    
    # Role/company digest (derived from job description only)
    company_name: str
    role_title: str
    role_digest: str  # Summary of role/responsibilities from job description
    company_digest: str  # What we know about company from job description only
    integrity_note: Optional[str] = None  # Warning if info is limited/missing
    
    # 30/60/90 day plan
    plan_30_days: List[str] = Field(default_factory=list)  # Goals for first 30 days
    plan_60_days: List[str] = Field(default_factory=list)  # Goals for 60 days
    plan_90_days: List[str] = Field(default_factory=list)  # Goals for 90 days
    
    # STAR stories mapped to experience
    star_stories: List[STARStory] = Field(default_factory=list)  # 3-5 grounded stories
    
    # Questions to ask interviewer
    questions_to_ask: List[InterviewQuestion] = Field(default_factory=list)  # 5-10 questions
    
    # Study checklist (placeholders only)
    study_checklist: List[StudyResource] = Field(default_factory=list)
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    schema_version: str = "1.0.0"


class TechnicalQuestion(BaseModel):
    """Technical interview question with answer and follow-ups"""
    question: str
    difficulty: DifficultyLevel
    answer: str  # High-quality detailed answer
    follow_ups: List[str] = Field(default_factory=list)  # 1-3 follow-up questions
    key_concepts: List[str] = Field(default_factory=list)  # Main concepts tested


class TechnicalQATopic(BaseModel):
    """Group of technical questions by topic"""
    topic: str  # e.g., "Python", "System Design", "Algorithms", "SQL"
    questions: List[TechnicalQuestion] = Field(default_factory=list)


class TechnicalQA(BaseModel):
    """Technical interview Q&A preparation"""
    
    # References
    packet_id: str
    job_id: str
    profile_id: str
    
    # Gap-aware topic prioritization
    priority_topics: List[str] = Field(default_factory=list)  # Topics to focus on (gaps/weak areas)
    
    # Questions grouped by topic
    topics: List[TechnicalQATopic] = Field(default_factory=list)
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    schema_version: str = "1.0.0"


class InterviewPackInDB(InterviewPack):
    """Interview pack as stored in database with MongoDB ID"""
    id: Optional[str] = Field(alias="_id", default=None)
    
    class Config:
        populate_by_name = True


class TechnicalQAInDB(TechnicalQA):
    """Technical Q&A as stored in database with MongoDB ID"""
    id: Optional[str] = Field(alias="_id", default=None)
    
    class Config:
        populate_by_name = True


class GenerateInterviewRequest(BaseModel):
    """Request to generate interview preparation materials"""
    packet_id: str


class InterviewPackResponse(BaseModel):
    """Response for interview pack retrieval"""
    interview_pack: InterviewPackInDB
    technical_qa: TechnicalQAInDB
    message: str = "Interview materials retrieved successfully"
