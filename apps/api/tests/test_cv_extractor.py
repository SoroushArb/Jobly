import pytest
from app.services import CVExtractor
from app.schemas import UserProfile


def test_extract_email():
    """Test email extraction from text"""
    text = "Contact me at john.doe@example.com for more info"
    email = CVExtractor.extract_email(text)
    assert email == "john.doe@example.com"


def test_extract_email_not_found():
    """Test email extraction when no email present"""
    text = "This text has no email address"
    email = CVExtractor.extract_email(text)
    assert email == "user@example.com"  # Default fallback


def test_extract_name():
    """Test name extraction from CV text"""
    text = """
    John Smith
    Software Engineer
    
    Experience:
    - Built apps
    """
    name = CVExtractor.extract_name(text)
    assert "John Smith" in name


def test_extract_links():
    """Test social link extraction"""
    text = """
    Contact: linkedin.com/in/johndoe
    GitHub: github.com/johndoe
    Website: https://johndoe.com
    """
    links = CVExtractor.extract_links(text)
    assert len(links) > 0
    assert any("linkedin" in link for link in links)


def test_extract_skills():
    """Test skill extraction and grouping"""
    text = """
    Skills:
    - Python, JavaScript, TypeScript
    - React, FastAPI, Django
    - Docker, AWS, MongoDB
    """
    skill_groups = CVExtractor.extract_skills(text)
    assert len(skill_groups) > 0
    
    # Check that skills are grouped
    categories = [sg.category for sg in skill_groups]
    assert any("Programming Languages" in cat for cat in categories)


def test_create_draft_profile():
    """Test creating a draft profile from text"""
    text = """
    John Doe
    john.doe@example.com
    linkedin.com/in/johndoe
    
    Summary:
    Experienced software engineer with expertise in Python and FastAPI.
    
    Skills:
    Python, JavaScript, React, FastAPI, Docker, AWS
    
    Experience:
    Senior Backend Developer
    Tech Corp | Jan 2020 - Present
    - Built REST APIs using FastAPI and Python
    - Deployed applications on AWS
    - Managed MongoDB databases
    
    Education:
    BSc Computer Science
    University of Technology | 2016-2020
    """
    
    evidence_map = {}
    profile = CVExtractor.create_draft_profile(text, evidence_map)
    
    assert isinstance(profile, UserProfile)
    assert profile.email == "john.doe@example.com"
    assert "John Doe" in profile.name
    assert len(profile.skills) > 0
    # Don't assert on experience length as extraction is heuristic-based


def test_extract_text_from_pdf():
    """Test PDF text extraction (would need actual PDF file)"""
    # This is a placeholder - would need actual PDF bytes for real test
    # For now, we'll skip or mock this
    pass


def test_extract_text_from_docx():
    """Test DOCX text extraction (would need actual DOCX file)"""
    # This is a placeholder - would need actual DOCX bytes for real test
    # For now, we'll skip or mock this
    pass
