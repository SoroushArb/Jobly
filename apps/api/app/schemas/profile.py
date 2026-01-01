from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class Preferences(BaseModel):
    """User job search preferences"""
    europe: bool = False
    remote: bool = False
    countries: list[str] = Field(default_factory=list)
    cities: list[str] = Field(default_factory=list)
    skill_tags: list[str] = Field(default_factory=list)
    role_tags: list[str] = Field(default_factory=list)
    visa_required: Optional[bool] = None
    languages: list[str] = Field(default_factory=list)


class ExperienceBullet(BaseModel):
    """Experience bullet point with evidence reference"""
    text: str
    evidence_ref: Optional[str] = None  # e.g., "page 1", "section 2, para 3"


class ExperienceRole(BaseModel):
    """Work experience role"""
    company: str
    title: str
    dates: str  # e.g., "Jan 2020 - Dec 2022"
    bullets: list[ExperienceBullet] = Field(default_factory=list)
    tech: list[str] = Field(default_factory=list)


class SkillGroup(BaseModel):
    """Group of related skills"""
    category: str  # e.g., "Programming Languages", "Frameworks", "Tools"
    skills: list[str] = Field(default_factory=list)


class Project(BaseModel):
    """Project information"""
    name: str
    description: Optional[str] = None
    tech: list[str] = Field(default_factory=list)
    url: Optional[str] = None


class Education(BaseModel):
    """Education information"""
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    dates: Optional[str] = None
    details: list[str] = Field(default_factory=list)


class UserProfile(BaseModel):
    """Complete user profile schema"""
    # Basic info
    name: str
    email: EmailStr
    links: list[str] = Field(default_factory=list)  # LinkedIn, GitHub, portfolio, etc.
    summary: Optional[str] = None
    
    # Skills grouped by category
    skills: list[SkillGroup] = Field(default_factory=list)
    
    # Experience
    experience: list[ExperienceRole] = Field(default_factory=list)
    
    # Projects
    projects: list[Project] = Field(default_factory=list)
    
    # Education
    education: list[Education] = Field(default_factory=list)
    
    # Preferences
    preferences: Preferences = Field(default_factory=Preferences)
    
    # Versioning
    schema_version: str = "1.0.0"
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserProfileUpdate(BaseModel):
    """Schema for partial profile updates"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    links: Optional[list[str]] = None
    summary: Optional[str] = None
    skills: Optional[list[SkillGroup]] = None
    experience: Optional[list[ExperienceRole]] = None
    projects: Optional[list[Project]] = None
    education: Optional[list[Education]] = None
    preferences: Optional[Preferences] = None


class UploadCVResponse(BaseModel):
    """Response from CV upload endpoint"""
    extracted_text: str
    draft_profile: UserProfile
    message: str = "CV processed successfully"


class ProfileResponse(BaseModel):
    """Response from profile retrieval"""
    profile: UserProfile
    message: str = "Profile retrieved successfully"


class ProfileSaveResponse(BaseModel):
    """Response from profile save operation"""
    profile_id: str
    message: str = "Profile saved successfully"
