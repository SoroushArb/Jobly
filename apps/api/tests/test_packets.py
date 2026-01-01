"""Tests for packet schemas and services"""
import pytest
from datetime import datetime
from pathlib import Path

from app.schemas.packet import (
    BulletSwap,
    TailoringPlan,
    PacketFile,
    Packet,
    GeneratePacketRequest,
)
from app.schemas.profile import (
    UserProfile,
    ExperienceRole,
    ExperienceBullet,
    SkillGroup,
    Education,
)
from app.schemas.job import JobPosting
from app.services.tailoring import TailoringService, compute_file_hash


def test_bullet_swap_schema():
    """Test BulletSwap schema validation"""
    swap = BulletSwap(
        role_index=0,
        original_bullet="Developed features",
        suggested_bullet="Developed Python features using Django",
        evidence_ref="page 1",
        reason="Emphasizes Python and Django skills"
    )
    
    assert swap.role_index == 0
    assert "Python" in swap.suggested_bullet
    assert swap.evidence_ref == "page 1"


def test_tailoring_plan_schema():
    """Test TailoringPlan schema validation"""
    plan = TailoringPlan(
        job_id="job123",
        profile_id="profile456",
        summary_rewrite="Experienced Python developer interested in Company X",
        skills_priority=["Python", "Django", "PostgreSQL"],
        bullet_swaps=[],
        keyword_inserts={"experience": ["Python", "AWS"]},
        gaps=["Kubernetes", "Go"],
        integrity_notes=["Ensure all claims are truthful"]
    )
    
    assert plan.job_id == "job123"
    assert len(plan.skills_priority) == 3
    assert len(plan.gaps) == 2
    assert len(plan.integrity_notes) == 1


def test_packet_file_schema():
    """Test PacketFile schema validation"""
    file = PacketFile(
        filename="cv.tex",
        filepath="packet123/cv.tex",
        content_hash="abc123",
        file_type="tex"
    )
    
    assert file.filename == "cv.tex"
    assert file.file_type == "tex"
    assert file.content_hash == "abc123"


def test_generate_packet_request():
    """Test GeneratePacketRequest schema"""
    request = GeneratePacketRequest(
        job_id="job123",
        include_cover_letter=True,
        user_emphasis=["emphasize AWS experience"]
    )
    
    assert request.job_id == "job123"
    assert request.include_cover_letter is True
    assert len(request.user_emphasis) == 1


def test_compute_file_hash():
    """Test file hash computation"""
    content = "Hello, World!"
    hash1 = compute_file_hash(content)
    hash2 = compute_file_hash(content)
    
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex length
    
    # Different content = different hash
    hash3 = compute_file_hash("Different content")
    assert hash1 != hash3


def test_tailoring_service_extract_skills():
    """Test skill extraction from job description"""
    service = TailoringService()
    
    job_desc = """
    We are looking for a Python developer with experience in Django and PostgreSQL.
    Knowledge of AWS, Docker, and Kubernetes is required.
    Familiarity with React and TypeScript is a plus.
    """
    
    skills = service._extract_skills_from_job(job_desc.lower())
    
    assert "Python" in skills or "python" in skills
    assert any("django" in s.lower() for s in skills)
    assert any("postgresql" in s.lower() for s in skills)
    assert any("aws" in s.lower() for s in skills)


def test_tailoring_service_rewrite_summary():
    """Test summary rewriting"""
    service = TailoringService()
    
    profile = UserProfile(
        name="John Doe",
        email="john@example.com",
        summary="Experienced software engineer with 5 years in web development."
    )
    
    job = JobPosting(
        company="TechCorp",
        title="Senior Python Developer",
        url="https://example.com/job",
        source_name="Test",
        source_type="test"
    )
    
    rewrite = service._rewrite_summary(profile, job)
    
    assert "Senior Python Developer" in rewrite
    assert "TechCorp" in rewrite
    assert len(rewrite) > 0


def test_tailoring_service_prioritize_skills():
    """Test skill prioritization"""
    service = TailoringService()
    
    profile = UserProfile(
        name="John Doe",
        email="john@example.com",
        skills=[
            SkillGroup(category="Languages", skills=["Python", "Java", "JavaScript"]),
            SkillGroup(category="Databases", skills=["PostgreSQL", "MySQL", "MongoDB"])
        ]
    )
    
    required_skills = ["python", "postgresql", "kubernetes"]
    
    prioritized = service._prioritize_skills(profile, required_skills)
    
    # Python and PostgreSQL should be first (matching)
    assert "Python" in prioritized[:3]
    assert "PostgreSQL" in prioritized[:3]


def test_tailoring_service_identify_gaps():
    """Test gap identification"""
    service = TailoringService()
    
    profile = UserProfile(
        name="John Doe",
        email="john@example.com",
        skills=[
            SkillGroup(category="Languages", skills=["Python", "Java"])
        ]
    )
    
    required_skills = ["Python", "Kubernetes", "Go", "Terraform"]
    
    gaps = service._identify_gaps(profile, required_skills)
    
    assert "Kubernetes" in gaps
    assert "Go" in gaps
    assert "Terraform" in gaps
    assert "Python" not in gaps  # User has this


def test_tailoring_service_generate_plan():
    """Test full tailoring plan generation"""
    service = TailoringService()
    
    profile = UserProfile(
        name="Jane Smith",
        email="jane@example.com",
        summary="Software engineer with Python experience",
        skills=[
            SkillGroup(category="Languages", skills=["Python", "JavaScript"]),
            SkillGroup(category="Frameworks", skills=["Django", "React"])
        ],
        experience=[
            ExperienceRole(
                company="OldCorp",
                title="Software Engineer",
                dates="2020-2023",
                bullets=[
                    ExperienceBullet(text="Developed Python applications"),
                    ExperienceBullet(text="Built REST APIs with Django")
                ]
            )
        ],
        education=[
            Education(institution="University", degree="BS Computer Science")
        ]
    )
    
    job = JobPosting(
        company="NewCorp",
        title="Senior Python Engineer",
        url="https://example.com/job",
        description_clean="Looking for Python expert with Django and AWS experience. Kubernetes knowledge is a plus.",
        source_name="Test",
        source_type="test"
    )
    
    plan = service.generate_tailoring_plan(profile, job)
    
    assert plan.job_id is not None
    assert "Senior Python Engineer" in plan.summary_rewrite or "NewCorp" in plan.summary_rewrite
    assert len(plan.skills_priority) > 0
    assert "Python" in plan.skills_priority or "python" in [s.lower() for s in plan.skills_priority]
    
    # Should identify gaps
    assert len(plan.gaps) > 0


def test_tailoring_service_render_latex():
    """Test LaTeX CV rendering"""
    service = TailoringService()
    
    profile = UserProfile(
        name="John Doe",
        email="john@example.com",
        links=["https://linkedin.com/in/johndoe", "https://github.com/johndoe"],
        summary="Experienced developer",
        skills=[
            SkillGroup(category="Languages", skills=["Python", "Java", "JavaScript"])
        ],
        experience=[
            ExperienceRole(
                company="TechCorp",
                title="Senior Developer",
                dates="2020-Present",
                bullets=[
                    ExperienceBullet(text="Led development of microservices"),
                    ExperienceBullet(text="Improved system performance by 50%")
                ]
            )
        ],
        education=[
            Education(
                institution="MIT",
                degree="BS Computer Science",
                dates="2016-2020"
            )
        ]
    )
    
    plan = TailoringPlan(
        job_id="job123",
        profile_id="profile456",
        summary_rewrite="Motivated developer interested in YourCompany",
        skills_priority=["Python", "Java", "JavaScript"],
        bullet_swaps=[],
        keyword_inserts={},
        gaps=[],
        integrity_notes=[]
    )
    
    latex = service.render_latex_cv(profile, plan)
    
    # Check LaTeX structure
    assert "\\documentclass" in latex
    assert "\\begin{document}" in latex
    assert "\\end{document}" in latex
    
    # Check content is present
    assert "John Doe" in latex or "John" in latex
    assert "john@example.com" in latex
    assert "TechCorp" in latex
    assert "Senior Developer" in latex
    assert "Python" in latex
    
    # Check it's properly formatted
    assert "\\section{" in latex
    assert "\\cventry{" in latex or "\\cvitem{" in latex


def test_tailoring_service_generate_recruiter_message():
    """Test recruiter message generation"""
    service = TailoringService()
    
    profile = UserProfile(
        name="Jane Smith",
        email="jane@example.com",
        skills=[
            SkillGroup(category="Languages", skills=["Python", "JavaScript"])
        ]
    )
    
    job = JobPosting(
        company="TechCorp",
        title="Software Engineer",
        url="https://example.com/job",
        source_name="Test",
        source_type="test"
    )
    
    plan = TailoringPlan(
        job_id="job123",
        profile_id="profile456",
        summary_rewrite="Test",
        skills_priority=["Python", "JavaScript"],
        bullet_swaps=[],
        keyword_inserts={},
        gaps=[],
        integrity_notes=[]
    )
    
    message = service.generate_recruiter_message(profile, job, plan)
    
    assert "Jane Smith" in message
    assert "TechCorp" in message
    assert "Software Engineer" in message
    assert len(message) > 0


def test_tailoring_service_generate_answers():
    """Test common answers generation"""
    service = TailoringService()
    
    profile = UserProfile(
        name="John Doe",
        email="john@example.com",
        skills=[
            SkillGroup(category="Languages", skills=["Python"])
        ]
    )
    
    job = JobPosting(
        company="TechCorp",
        title="Software Engineer",
        url="https://example.com/job",
        source_name="Test",
        source_type="test"
    )
    
    answers = service.generate_common_answers(profile, job)
    
    assert "TechCorp" in answers
    assert "Software Engineer" in answers
    assert "Salary" in answers
    assert "Work Authorization" in answers
    assert len(answers) > 0
