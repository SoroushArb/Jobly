"""
CV Document schemas for multi-CV support
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CVDocument(BaseModel):
    """CV document with extracted data"""
    user_email: EmailStr
    filename: str
    extracted_text: str
    parsed_profile: dict  # Snapshot of UserProfile as dict
    is_active: bool = False
    upload_date: datetime = datetime.utcnow()


class CVDocumentInDB(CVDocument):
    """CV document as stored in MongoDB"""
    _id: Optional[str] = None
    

class CVDocumentResponse(BaseModel):
    """Response for CV document operations"""
    cv_id: str
    message: str = "CV processed successfully"


class CVListResponse(BaseModel):
    """Response for listing CVs"""
    cvs: list[CVDocumentInDB]
    total: int
    message: str = "CVs retrieved successfully"


class SetActiveCVRequest(BaseModel):
    """Request to set active CV"""
    cv_id: str
    user_email: EmailStr
