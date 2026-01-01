import pytest
from app.schemas import (
    UserProfile,
    ExperienceRole,
    ExperienceBullet,
    SkillGroup,
    Education,
    Preferences,
)


def test_preferences_schema():
    """Test Preferences schema validation"""
    prefs = Preferences(
        europe=True,
        remote=True,
        countries=["Germany", "Netherlands"],
        cities=["Berlin", "Amsterdam"],
        skill_tags=["Python", "FastAPI"],
        role_tags=["Backend Developer"],
        visa_required=True,
        languages=["English", "German"]
    )
    
    assert prefs.europe is True
    assert prefs.remote is True
    assert len(prefs.countries) == 2
    assert "Germany" in prefs.countries


def test_experience_bullet_schema():
    """Test ExperienceBullet schema with evidence reference"""
    bullet = ExperienceBullet(
        text="Developed REST API using FastAPI",
        evidence_ref="page 1"
    )
    
    assert bullet.text == "Developed REST API using FastAPI"
    assert bullet.evidence_ref == "page 1"


def test_experience_role_schema():
    """Test ExperienceRole schema"""
    role = ExperienceRole(
        company="Tech Corp",
        title="Backend Developer",
        dates="Jan 2020 - Dec 2022",
        bullets=[
            ExperienceBullet(text="Built APIs", evidence_ref="page 1")
        ],
        tech=["Python", "FastAPI", "MongoDB"]
    )
    
    assert role.company == "Tech Corp"
    assert role.title == "Backend Developer"
    assert len(role.tech) == 3
    assert len(role.bullets) == 1


def test_skill_group_schema():
    """Test SkillGroup schema"""
    skills = SkillGroup(
        category="Programming Languages",
        skills=["Python", "JavaScript", "TypeScript"]
    )
    
    assert skills.category == "Programming Languages"
    assert len(skills.skills) == 3


def test_user_profile_schema():
    """Test complete UserProfile schema"""
    profile = UserProfile(
        name="John Doe",
        email="john@example.com",
        links=["https://linkedin.com/in/johndoe"],
        summary="Experienced backend developer",
        skills=[
            SkillGroup(
                category="Programming Languages",
                skills=["Python", "JavaScript"]
            )
        ],
        experience=[
            ExperienceRole(
                company="Tech Corp",
                title="Backend Developer",
                dates="Jan 2020 - Present",
                bullets=[
                    ExperienceBullet(text="Built APIs", evidence_ref="page 1")
                ],
                tech=["Python", "FastAPI"]
            )
        ],
        projects=[],
        education=[
            Education(
                institution="University of Technology",
                degree="BSc",
                field="Computer Science",
                dates="2016-2020"
            )
        ],
        preferences=Preferences(
            europe=True,
            remote=True
        )
    )
    
    assert profile.name == "John Doe"
    assert profile.email == "john@example.com"
    assert profile.schema_version == "1.0.0"
    assert len(profile.skills) == 1
    assert len(profile.experience) == 1
    assert profile.preferences.europe is True


def test_user_profile_defaults():
    """Test UserProfile with minimal required fields"""
    profile = UserProfile(
        name="Jane Doe",
        email="jane@example.com"
    )
    
    assert profile.name == "Jane Doe"
    assert profile.email == "jane@example.com"
    assert profile.skills == []
    assert profile.experience == []
    assert profile.projects == []
    assert profile.education == []
    assert isinstance(profile.preferences, Preferences)
    assert profile.preferences.europe is False
    assert profile.preferences.remote is False
