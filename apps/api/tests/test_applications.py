"""Tests for application tracking schemas and endpoints"""
import pytest
from datetime import datetime
from app.schemas.application import (
    ApplicationStatus,
    PrefillIntent,
    PrefillLog,
    Application,
    CreateApplicationRequest,
    UpdateApplicationStatusRequest,
    PrefillIntentRequest,
)


def test_application_status_enum():
    """Test ApplicationStatus enum values"""
    assert ApplicationStatus.PREPARED.value == "prepared"
    assert ApplicationStatus.APPLIED.value == "applied"
    assert ApplicationStatus.PREFILLED.value == "prefilled"


def test_prefill_intent_schema():
    """Test PrefillIntent schema validation"""
    intent = PrefillIntent(
        packet_id="123",
        job_url="https://example.com/job",
        user_fields={"name": "John", "email": "john@example.com"},
        attachments={"resume": "/path/to/resume.pdf"},
        common_answers={"question1": "answer1"},
    )
    
    assert intent.packet_id == "123"
    assert intent.job_url == "https://example.com/job"
    assert intent.user_fields["name"] == "John"
    assert intent.status == "pending"
    assert isinstance(intent.created_at, datetime)


def test_prefill_log_schema():
    """Test PrefillLog schema validation"""
    log = PrefillLog(
        intent_id="123",
        detected_ats="greenhouse",
        detection_confidence=0.8,
        filled_fields=[
            {"field_name": "email", "value": "test@example.com", "success": True}
        ],
        missing_fields=["phone"],
        errors=[],
        resume_attached=True,
        attachment_errors=[],
        screenshot_paths=["/path/to/screenshot.png"],
        duration_seconds=45.5,
        stopped_before_submit=True,
    )
    
    assert log.intent_id == "123"
    assert log.detected_ats == "greenhouse"
    assert log.detection_confidence == 0.8
    assert len(log.filled_fields) == 1
    assert log.filled_fields[0]["field_name"] == "email"
    assert log.resume_attached is True
    assert log.stopped_before_submit is True


def test_application_schema():
    """Test Application schema validation"""
    app = Application(
        job_id="job123",
        packet_id="packet123",
        profile_id="profile123",
        job_title="Software Engineer",
        company_name="Tech Corp",
        job_url="https://example.com/job",
        status=ApplicationStatus.PREPARED,
        status_history=[
            {
                "status": ApplicationStatus.PREPARED.value,
                "timestamp": datetime.utcnow().isoformat(),
                "note": "Created"
            }
        ],
        notes="Test application",
    )
    
    assert app.job_title == "Software Engineer"
    assert app.company_name == "Tech Corp"
    assert app.status == ApplicationStatus.PREPARED
    assert len(app.status_history) == 1
    assert app.notes == "Test application"


def test_create_application_request():
    """Test CreateApplicationRequest schema"""
    request = CreateApplicationRequest(
        packet_id="packet123",
        job_id="job123",
        notes="Test notes"
    )
    
    assert request.packet_id == "packet123"
    assert request.job_id == "job123"
    assert request.notes == "Test notes"


def test_update_application_status_request():
    """Test UpdateApplicationStatusRequest schema"""
    request = UpdateApplicationStatusRequest(
        status=ApplicationStatus.APPLIED,
        note="Application submitted"
    )
    
    assert request.status == ApplicationStatus.APPLIED
    assert request.note == "Application submitted"


def test_prefill_intent_request():
    """Test PrefillIntentRequest schema"""
    request = PrefillIntentRequest(application_id="app123")
    
    assert request.application_id == "app123"


def test_application_status_history():
    """Test application status history tracking"""
    app = Application(
        job_id="job123",
        packet_id="packet123",
        profile_id="profile123",
        job_title="Software Engineer",
        company_name="Tech Corp",
        job_url="https://example.com/job",
        status=ApplicationStatus.APPLIED,
        status_history=[
            {
                "status": "prepared",
                "timestamp": "2024-01-01T00:00:00",
                "note": "Created"
            },
            {
                "status": "applied",
                "timestamp": "2024-01-02T00:00:00",
                "note": "Submitted"
            }
        ],
    )
    
    assert len(app.status_history) == 2
    assert app.status_history[0]["status"] == "prepared"
    assert app.status_history[1]["status"] == "applied"
