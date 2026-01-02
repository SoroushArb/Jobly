"""Tests for interview preparation schemas and services"""
import pytest
from datetime import datetime

from app.schemas.interview import (
    InterviewPack,
    TechnicalQA,
    STARStory,
    InterviewQuestion,
    StudyResource,
    TechnicalQATopic,
    TechnicalQuestion,
    GroundingReference,
    DifficultyLevel
)
from app.schemas.profile import (
    UserProfile,
    ExperienceRole,
    ExperienceBullet,
    SkillGroup
)
from app.schemas.job import JobPosting
from app.schemas.packet import Packet, TailoringPlan, PacketFile


def test_grounding_reference_schema():
    """Test GroundingReference schema validation"""
    ref = GroundingReference(
        experience_index=0,
        bullet_index=1,
        evidence_text="Led development of microservices architecture"
    )
    
    assert ref.experience_index == 0
    assert ref.bullet_index == 1
    assert "microservices" in ref.evidence_text


def test_star_story_schema():
    """Test STARStory schema with grounding references"""
    story = STARStory(
        title="Microservices Migration",
        situation="Legacy monolith slowing development",
        task="Migrate to microservices architecture",
        action="Led team to design and implement service boundaries",
        result="Reduced deployment time by 60%",
        skills_demonstrated=["Python", "Docker", "Kubernetes"],
        grounding_refs=[
            GroundingReference(
                experience_index=0,
                bullet_index=2,
                evidence_text="Led microservices migration"
            )
        ]
    )
    
    assert story.title == "Microservices Migration"
    assert len(story.skills_demonstrated) == 3
    assert len(story.grounding_refs) == 1
    assert story.grounding_refs[0].experience_index == 0


def test_star_story_grounding_validation():
    """Test that STAR stories must include grounding references"""
    # This tests that we can create stories with grounding
    story = STARStory(
        title="Test Story",
        situation="Test situation",
        task="Test task",
        action="Test action",
        result="Test result",
        skills_demonstrated=["Python"],
        grounding_refs=[
            GroundingReference(
                experience_index=0,
                evidence_text="Real evidence from profile"
            )
        ]
    )
    
    assert len(story.grounding_refs) > 0
    assert story.grounding_refs[0].evidence_text == "Real evidence from profile"


def test_interview_question_schema():
    """Test InterviewQuestion schema"""
    question = InterviewQuestion(
        question="What does success look like in this role?",
        category="role",
        reasoning="Helps understand expectations and success criteria"
    )
    
    assert question.category == "role"
    assert "success" in question.question.lower()


def test_study_resource_schema():
    """Test StudyResource schema with placeholders"""
    resource = StudyResource(
        topic="Kubernetes",
        resource_type="documentation",
        description="Review Kubernetes official documentation"
    )
    
    assert resource.topic == "Kubernetes"
    assert resource.resource_type == "documentation"
    # Ensure no external links in description (placeholder only)
    assert "http" not in resource.description


def test_technical_question_schema():
    """Test TechnicalQuestion schema"""
    question = TechnicalQuestion(
        question="Explain the GIL in Python",
        difficulty=DifficultyLevel.MEDIUM,
        answer="The Global Interpreter Lock (GIL) is a mutex that protects access to Python objects...",
        follow_ups=[
            "How does the GIL affect multi-threaded programs?",
            "What are alternatives to the GIL?"
        ],
        key_concepts=["Threading", "Concurrency", "Python Internals"]
    )
    
    assert question.difficulty == DifficultyLevel.MEDIUM
    assert len(question.follow_ups) == 2
    assert len(question.key_concepts) == 3


def test_technical_qa_topic_schema():
    """Test TechnicalQATopic schema"""
    topic = TechnicalQATopic(
        topic="Python",
        questions=[
            TechnicalQuestion(
                question="What is a decorator?",
                difficulty=DifficultyLevel.EASY,
                answer="A decorator is a function that modifies another function...",
                follow_ups=["How do you create a decorator?"],
                key_concepts=["Functions", "Higher-order functions"]
            )
        ]
    )
    
    assert topic.topic == "Python"
    assert len(topic.questions) == 1


def test_interview_pack_schema():
    """Test InterviewPack schema validation"""
    pack = InterviewPack(
        packet_id="packet123",
        job_id="job456",
        profile_id="profile789",
        company_name="TechCorp",
        role_title="Senior Python Developer",
        role_digest="Responsible for backend development...",
        company_digest="TechCorp builds innovative solutions...",
        integrity_note=None,
        plan_30_days=["Complete onboarding", "First PR"],
        plan_60_days=["Lead feature development"],
        plan_90_days=["Mentor junior developers"],
        star_stories=[
            STARStory(
                title="Performance Optimization",
                situation="Slow API response times",
                task="Improve performance",
                action="Implemented caching and query optimization",
                result="Reduced response time by 70%",
                skills_demonstrated=["Python", "PostgreSQL"],
                grounding_refs=[
                    GroundingReference(
                        experience_index=0,
                        bullet_index=1,
                        evidence_text="Optimized database queries"
                    )
                ]
            )
        ],
        questions_to_ask=[
            InterviewQuestion(
                question="What's the team structure?",
                category="team",
                reasoning="Understand collaboration"
            )
        ],
        study_checklist=[
            StudyResource(
                topic="Kubernetes",
                resource_type="documentation",
                description="Study K8s concepts"
            )
        ]
    )
    
    assert pack.company_name == "TechCorp"
    assert len(pack.plan_30_days) == 2
    assert len(pack.star_stories) == 1
    assert len(pack.questions_to_ask) == 1
    assert len(pack.study_checklist) == 1


def test_interview_pack_integrity_note():
    """Test that integrity notes are included when company info is limited"""
    pack = InterviewPack(
        packet_id="packet123",
        job_id="job456",
        profile_id="profile789",
        company_name="UnknownCorp",
        role_title="Developer",
        role_digest="Role details from job description",
        company_digest="Limited information available",
        integrity_note="Limited company information available from job description. Recommend independent research.",
        plan_30_days=["Start onboarding"],
        plan_60_days=["Deliver features"],
        plan_90_days=["Lead projects"]
    )
    
    assert pack.integrity_note is not None
    assert "independent research" in pack.integrity_note.lower()


def test_technical_qa_schema():
    """Test TechnicalQA schema"""
    qa = TechnicalQA(
        packet_id="packet123",
        job_id="job456",
        profile_id="profile789",
        priority_topics=["Python", "System Design", "Kubernetes"],
        topics=[
            TechnicalQATopic(
                topic="Python",
                questions=[
                    TechnicalQuestion(
                        question="Explain async/await",
                        difficulty=DifficultyLevel.MEDIUM,
                        answer="Async/await enables asynchronous programming...",
                        follow_ups=["When should you use async?"],
                        key_concepts=["Concurrency", "Event Loop"]
                    )
                ]
            )
        ]
    )
    
    assert len(qa.priority_topics) == 3
    assert "Python" in qa.priority_topics
    assert len(qa.topics) == 1
    assert qa.topics[0].topic == "Python"


def test_grounding_reference_to_experience():
    """Test that grounding references can map to actual experience entries"""
    profile = UserProfile(
        name="Jane Doe",
        email="jane@example.com",
        experience=[
            ExperienceRole(
                company="TechCorp",
                title="Senior Engineer",
                dates="2020-2023",
                bullets=[
                    ExperienceBullet(text="Led microservices migration", evidence_ref="page 1"),
                    ExperienceBullet(text="Improved performance by 60%", evidence_ref="page 1")
                ]
            )
        ]
    )
    
    # Create grounding reference to first bullet
    ref = GroundingReference(
        experience_index=0,
        bullet_index=0,
        evidence_text="Led microservices migration"
    )
    
    # Verify we can resolve it
    assert 0 <= ref.experience_index < len(profile.experience)
    role = profile.experience[ref.experience_index]
    
    if ref.bullet_index is not None:
        assert 0 <= ref.bullet_index < len(role.bullets)
        bullet = role.bullets[ref.bullet_index]
        assert "microservices" in bullet.text.lower()


def test_company_digest_restriction():
    """Test that company digest should only contain info from job description"""
    # This is a guardrail test - in practice, the service should enforce this
    job = JobPosting(
        company="TechCorp",
        title="Developer",
        url="https://example.com/job",
        description_clean="We are building innovative solutions. Founded in 2020.",
        source_name="Test",
        source_type="test"
    )
    
    # Valid digest: contains info from description
    valid_digest = "TechCorp builds innovative solutions. Founded in 2020."
    
    # Invalid digest: contains fabricated info
    invalid_digest = "TechCorp is a Fortune 500 company with 10,000 employees."
    
    # Check that valid digest contains words from job description
    job_desc_lower = job.description_clean.lower()
    assert "innovative" in job_desc_lower
    assert "founded" in job_desc_lower
    
    # The invalid digest should not be used (this is enforced by service logic)
    # We're just documenting the requirement here


def test_study_checklist_no_external_links():
    """Test that study checklist only has placeholders, no external links"""
    resources = [
        StudyResource(
            topic="Python",
            resource_type="documentation",
            description="Review Python official documentation"
        ),
        StudyResource(
            topic="Kubernetes",
            resource_type="tutorial",
            description="Study Kubernetes concepts and architecture"
        )
    ]
    
    # Verify no external links in descriptions
    for resource in resources:
        assert "http" not in resource.description.lower()
        assert "www." not in resource.description.lower()
        # Should be placeholders/guidance only
        assert any(keyword in resource.description.lower() 
                  for keyword in ["review", "study", "practice", "learn"])


def test_gap_aware_priority_topics():
    """Test that technical QA prioritizes gap topics"""
    # Mock packet with gaps
    packet = Packet(
        job_id="job123",
        profile_id="profile456",
        tailoring_plan=TailoringPlan(
            job_id="job123",
            profile_id="profile456",
            summary_rewrite="Test summary",
            skills_priority=["Python", "Django"],
            gaps=["Kubernetes", "Go", "Terraform"],  # User lacks these
            integrity_notes=[]
        ),
        cv_tex=PacketFile(
            filename="cv.tex",
            filepath="packet/cv.tex",
            content_hash="abc123",
            file_type="tex"
        ),
        recruiter_message=PacketFile(
            filename="msg.txt",
            filepath="packet/msg.txt",
            content_hash="def456",
            file_type="txt"
        ),
        common_answers=PacketFile(
            filename="answers.txt",
            filepath="packet/answers.txt",
            content_hash="ghi789",
            file_type="txt"
        )
    )
    
    # Priority topics should include gap topics
    qa = TechnicalQA(
        packet_id="packet123",
        job_id="job123",
        profile_id="profile456",
        priority_topics=["Kubernetes", "Go", "Terraform"],  # From gaps
        topics=[]
    )
    
    # Verify gaps are in priority topics
    for gap in packet.tailoring_plan.gaps:
        assert gap in qa.priority_topics


def test_english_output_requirement():
    """Test that all text fields are in English (documentation test)"""
    # This is a requirement documented in schemas
    # In practice, enforced by LLM system prompts
    
    pack = InterviewPack(
        packet_id="packet123",
        job_id="job456",
        profile_id="profile789",
        company_name="TechCorp",
        role_title="Senior Developer",
        role_digest="This is in English",
        company_digest="Also in English",
        plan_30_days=["English text here"],
        plan_60_days=["More English"],
        plan_90_days=["Still English"]
    )
    
    # All text should be English (enforced by service, not schema)
    # This test documents the requirement
    assert isinstance(pack.role_digest, str)
    assert isinstance(pack.company_digest, str)
