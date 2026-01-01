"""
Tests for job source parsing (RSS and HTML)
"""

import pytest
from app.services.sources import RawJob, RSSSource, CompanySource
from app.schemas import JobPosting


def test_raw_job_creation():
    """Test RawJob dataclass creation"""
    raw_job = RawJob(
        title="Python Developer",
        url="https://example.com/job/1",
        company="Tech Corp",
        location="Berlin, Germany",
        description="Great opportunity"
    )
    
    assert raw_job.title == "Python Developer"
    assert raw_job.company == "Tech Corp"
    assert raw_job.raw_data == {}  # Default empty dict


def test_rss_source_initialization():
    """Test RSS source initialization"""
    config = {
        "name": "Test RSS",
        "type": "rss",
        "url": "https://example.com/feed.rss",
        "enabled": True,
        "compliance_note": "Public feed",
        "rate_limit_seconds": 60
    }
    
    source = RSSSource(config)
    
    assert source.name == "Test RSS"
    assert source.source_type == "rss"
    assert source.url == "https://example.com/feed.rss"
    assert source.is_enabled() is True


def test_rss_source_parse():
    """Test RSS source parsing of RawJob into JobPosting"""
    config = {
        "name": "Test RSS Feed",
        "type": "rss",
        "url": "https://example.com/feed",
        "compliance_note": "Public RSS feed",
        "rate_limit_seconds": 60
    }
    
    source = RSSSource(config)
    
    raw_job = RawJob(
        title="Backend Developer",
        url="https://example.com/job/123",
        company="Example Inc",
        location="Remote",
        description="<p>Job description</p>"
    )
    
    job_posting = source.parse(raw_job)
    
    assert isinstance(job_posting, JobPosting)
    assert job_posting.title == "Backend Developer"
    assert job_posting.company == "Example Inc"
    assert job_posting.url == "https://example.com/job/123"
    assert job_posting.remote_type == "remote"  # Detected from location
    assert job_posting.source_name == "Test RSS Feed"
    assert job_posting.source_type == "rss"
    assert "Job description" in job_posting.description_clean  # HTML cleaned


def test_rss_source_parse_location():
    """Test location parsing in RSS source"""
    config = {
        "name": "Test RSS",
        "type": "rss",
        "url": "https://example.com/feed",
        "compliance_note": "Public feed",
        "rate_limit_seconds": 60
    }
    
    source = RSSSource(config)
    
    # Test with city and country
    raw_job = RawJob(
        title="Developer",
        url="https://example.com/job/1",
        company="Company",
        location="Berlin, Germany"
    )
    
    job_posting = source.parse(raw_job)
    assert job_posting.city == "Berlin"
    assert job_posting.country == "Germany"


def test_rss_source_parse_remote_detection():
    """Test remote type detection from location"""
    config = {
        "name": "Test RSS",
        "type": "rss",
        "url": "https://example.com/feed",
        "compliance_note": "Public feed",
        "rate_limit_seconds": 60
    }
    
    source = RSSSource(config)
    
    test_cases = [
        ("Remote", "remote"),
        ("Hybrid - Berlin", "hybrid"),
        ("On-site Berlin", "onsite"),
        ("Berlin Office", "unknown"),
    ]
    
    for location, expected_remote_type in test_cases:
        raw_job = RawJob(
            title="Developer",
            url=f"https://example.com/job/{location}",
            company="Company",
            location=location
        )
        
        job_posting = source.parse(raw_job)
        assert job_posting.remote_type == expected_remote_type, f"Failed for location: {location}"


def test_company_source_initialization():
    """Test Company source initialization"""
    config = {
        "name": "Google Careers",
        "type": "company",
        "url": "https://careers.google.com/jobs/",
        "enabled": True,
        "compliance_note": "Public careers page",
        "rate_limit_seconds": 120,
        "parser_config": {
            "job_list_selector": ".job-card",
            "title_selector": ".job-title",
            "location_selector": ".job-location",
            "link_selector": "a.job-link"
        }
    }
    
    source = CompanySource(config)
    
    assert source.name == "Google Careers"
    assert source.source_type == "company"
    assert source.job_list_selector == ".job-card"
    assert source.title_selector == ".job-title"


def test_company_source_parse():
    """Test Company source parsing of RawJob into JobPosting"""
    config = {
        "name": "Google Careers",
        "type": "company",
        "url": "https://careers.google.com/",
        "compliance_note": "Public careers page",
        "rate_limit_seconds": 120,
        "parser_config": {}
    }
    
    source = CompanySource(config)
    
    raw_job = RawJob(
        title="Software Engineer",
        url="https://careers.google.com/jobs/123",
        company="Google",  # Will be extracted from source name
        location="Mountain View, CA, USA"
    )
    
    job_posting = source.parse(raw_job)
    
    assert isinstance(job_posting, JobPosting)
    assert job_posting.title == "Software Engineer"
    assert job_posting.company == "Google"  # Extracted from source name
    assert job_posting.url == "https://careers.google.com/jobs/123"
    assert job_posting.source_name == "Google Careers"
    assert job_posting.source_type == "company"


def test_html_cleaning():
    """Test HTML cleaning in RSS source"""
    config = {
        "name": "Test RSS",
        "type": "rss",
        "url": "https://example.com/feed",
        "compliance_note": "Public feed",
        "rate_limit_seconds": 60
    }
    
    source = RSSSource(config)
    
    html = "<p>This is a <strong>great</strong> job with <a href='#'>benefits</a>.</p>"
    cleaned = source._clean_html(html)
    
    assert "<p>" not in cleaned
    assert "<strong>" not in cleaned
    assert "<a" not in cleaned
    assert "great" in cleaned
    assert "benefits" in cleaned
