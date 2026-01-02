"""
Tests for CV document management and multi-CV support
"""

import pytest
from app.schemas import (
    CVDocument,
    CVDocumentInDB,
    CVListResponse,
    SetActiveCVRequest,
    UserProfile,
    Preferences,
)
from datetime import datetime


def test_cv_document_schema():
    """Test CVDocument schema validation"""
    cv = CVDocument(
        user_email="test@example.com",
        filename="resume.pdf",
        extracted_text="Sample CV text",
        parsed_profile={
            "name": "John Doe",
            "email": "test@example.com",
            "links": [],
            "skills": [],
            "experience": [],
            "projects": [],
            "education": [],
            "preferences": {
                "europe": False,
                "remote": False,
                "countries": [],
                "cities": [],
                "skill_tags": [],
                "role_tags": [],
                "visa_required": None,
                "languages": []
            },
            "schema_version": "1.0.0",
            "updated_at": datetime.utcnow().isoformat()
        },
        is_active=True,
        upload_date=datetime.utcnow()
    )
    
    assert cv.user_email == "test@example.com"
    assert cv.filename == "resume.pdf"
    assert cv.is_active is True
    assert "John Doe" in str(cv.parsed_profile)


def test_cv_document_in_db_schema():
    """Test CVDocumentInDB schema with MongoDB _id"""
    cv = CVDocumentInDB(
        id="507f1f77bcf86cd799439011",
        user_email="test@example.com",
        filename="resume.pdf",
        extracted_text="Sample CV text",
        parsed_profile={"name": "John Doe"},
        is_active=True,
        upload_date=datetime.utcnow()
    )
    
    assert cv.id == "507f1f77bcf86cd799439011"
    assert cv.user_email == "test@example.com"


def test_cv_list_response_schema():
    """Test CVListResponse schema"""
    response = CVListResponse(
        cvs=[],
        total=0,
        message="No CVs found"
    )
    
    assert response.total == 0
    assert response.message == "No CVs found"
    assert len(response.cvs) == 0


def test_set_active_cv_request_schema():
    """Test SetActiveCVRequest schema"""
    request = SetActiveCVRequest(
        cv_id="507f1f77bcf86cd799439011",
        user_email="test@example.com"
    )
    
    assert request.cv_id == "507f1f77bcf86cd799439011"
    assert request.user_email == "test@example.com"


def test_cv_document_default_active_false():
    """Test that default is_active is False"""
    cv = CVDocument(
        user_email="test@example.com",
        filename="resume.pdf",
        extracted_text="text",
        parsed_profile={}
    )
    
    assert cv.is_active is False


def test_multiple_cvs_one_active():
    """Test scenario with multiple CVs where only one is active"""
    cv1 = CVDocument(
        user_email="test@example.com",
        filename="resume_v1.pdf",
        extracted_text="text",
        parsed_profile={},
        is_active=True
    )
    
    cv2 = CVDocument(
        user_email="test@example.com",
        filename="resume_v2.pdf",
        extracted_text="text",
        parsed_profile={},
        is_active=False
    )
    
    cvs = [cv1, cv2]
    active_cvs = [cv for cv in cvs if cv.is_active]
    
    assert len(active_cvs) == 1
    assert active_cvs[0].filename == "resume_v1.pdf"


def test_cv_document_preserves_upload_date():
    """Test that upload_date is preserved correctly"""
    upload_time = datetime(2024, 1, 15, 10, 30, 0)
    cv = CVDocument(
        user_email="test@example.com",
        filename="resume.pdf",
        extracted_text="text",
        parsed_profile={},
        upload_date=upload_time
    )
    
    assert cv.upload_date == upload_time
