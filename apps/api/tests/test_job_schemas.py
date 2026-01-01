"""
Tests for job schemas and deduplication logic
"""

import pytest
from datetime import datetime
from app.schemas import JobPosting, JobPostingInDB


def test_job_posting_schema():
    """Test JobPosting schema validation"""
    job = JobPosting(
        company="Tech Corp",
        title="Senior Python Developer",
        url="https://techcorp.com/jobs/123",
        location="Berlin, Germany",
        country="Germany",
        city="Berlin",
        remote_type="hybrid",
        description_raw="<p>Great job opportunity</p>",
        description_clean="Great job opportunity",
        source_name="Tech Corp Careers",
        source_type="company",
        source_compliance_note="Public careers page"
    )
    
    assert job.company == "Tech Corp"
    assert job.title == "Senior Python Developer"
    assert job.remote_type == "hybrid"
    assert job.dedupe_hash != ""  # Hash should be generated
    assert isinstance(job.fetched_at, datetime)
    assert isinstance(job.first_seen, datetime)
    assert isinstance(job.last_seen, datetime)


def test_job_posting_minimal():
    """Test JobPosting with minimal required fields"""
    job = JobPosting(
        company="Test Co",
        title="Developer",
        url="https://test.com/job",
        source_name="Test Source",
        source_type="rss"
    )
    
    assert job.company == "Test Co"
    assert job.remote_type == "unknown"  # Default
    assert job.location is None
    assert job.country is None
    assert job.city is None


def test_dedupe_hash_generation():
    """Test that dedupe hash is generated consistently"""
    job1 = JobPosting(
        company="Tech Corp",
        title="Developer",
        url="https://techcorp.com/jobs/1",
        source_name="Source 1",
        source_type="rss"
    )
    
    job2 = JobPosting(
        company="Tech Corp",
        title="Developer",
        url="https://techcorp.com/jobs/1",
        source_name="Source 2",  # Different source
        source_type="company"
    )
    
    # Same company/title/url should generate same hash
    assert job1.dedupe_hash == job2.dedupe_hash


def test_dedupe_hash_different_jobs():
    """Test that different jobs generate different hashes"""
    job1 = JobPosting(
        company="Tech Corp",
        title="Developer",
        url="https://techcorp.com/jobs/1",
        source_name="Source",
        source_type="rss"
    )
    
    job2 = JobPosting(
        company="Tech Corp",
        title="Developer",
        url="https://techcorp.com/jobs/2",  # Different URL
        source_name="Source",
        source_type="rss"
    )
    
    assert job1.dedupe_hash != job2.dedupe_hash


def test_dedupe_hash_case_insensitive():
    """Test that dedupe hash is case-insensitive"""
    job1 = JobPosting(
        company="Tech Corp",
        title="Developer",
        url="https://techcorp.com/jobs/1",
        source_name="Source",
        source_type="rss"
    )
    
    job2 = JobPosting(
        company="TECH CORP",  # Different case
        title="DEVELOPER",
        url="HTTPS://TECHCORP.COM/JOBS/1",
        source_name="Source",
        source_type="rss"
    )
    
    # Should generate same hash (case-insensitive)
    assert job1.dedupe_hash == job2.dedupe_hash


def test_job_posting_with_dates():
    """Test JobPosting with optional date fields"""
    posted_date = datetime(2024, 1, 15, 10, 30)
    
    job = JobPosting(
        company="Tech Corp",
        title="Developer",
        url="https://techcorp.com/jobs/1",
        source_name="Source",
        source_type="rss",
        posted_date=posted_date,
        employment_type="full-time"
    )
    
    assert job.posted_date == posted_date
    assert job.employment_type == "full-time"


def test_job_posting_remote_types():
    """Test different remote_type values"""
    remote_types = ["onsite", "hybrid", "remote", "unknown"]
    
    for remote_type in remote_types:
        job = JobPosting(
            company="Tech Corp",
            title="Developer",
            url=f"https://techcorp.com/jobs/{remote_type}",
            source_name="Source",
            source_type="rss",
            remote_type=remote_type
        )
        assert job.remote_type == remote_type
