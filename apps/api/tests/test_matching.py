"""Tests for match scoring and embedding services"""
import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timedelta

from app.schemas.profile import UserProfile, Preferences, SkillGroup, ExperienceRole, ExperienceBullet
from app.schemas.job import JobPostingInDB
from app.services.matching.scoring import ScoringUtils
from app.services.matching.config import MatchConfig


@pytest.fixture
def sample_profile():
    """Create a sample user profile"""
    return UserProfile(
        name="John Doe",
        email="john@example.com",
        summary="Experienced software engineer with focus on Python and cloud technologies",
        skills=[
            SkillGroup(category="Languages", skills=["Python", "JavaScript", "Go"]),
            SkillGroup(category="Frameworks", skills=["FastAPI", "React", "Django"]),
            SkillGroup(category="Cloud", skills=["AWS", "Docker", "Kubernetes"]),
        ],
        experience=[
            ExperienceRole(
                company="Tech Corp",
                title="Senior Software Engineer",
                dates="2020-2023",
                bullets=[
                    ExperienceBullet(text="Built scalable microservices using Python and FastAPI"),
                    ExperienceBullet(text="Deployed applications on AWS with Kubernetes"),
                ],
                tech=["Python", "AWS", "Kubernetes"]
            ),
            ExperienceRole(
                company="StartupCo",
                title="Software Engineer",
                dates="2018-2020",
                bullets=[
                    ExperienceBullet(text="Developed web applications using Django and React"),
                ],
                tech=["Python", "Django", "React"]
            ),
        ],
        preferences=Preferences(
            remote=True,
            europe=True,
            countries=["Germany", "Netherlands"],
            skill_tags=["python", "aws", "kubernetes"],
        )
    )


@pytest.fixture
def sample_job():
    """Create a sample job posting"""
    return JobPostingInDB(
        id="507f1f77bcf86cd799439011",
        company="CloudTech GmbH",
        title="Senior Python Engineer",
        url="https://example.com/job/123",
        location="Berlin, Germany",
        country="Germany",
        city="Berlin",
        remote_type="remote",
        description_clean="We are looking for a Senior Python Engineer with experience in FastAPI, AWS, and Kubernetes. You will build scalable microservices and work with modern cloud technologies.",
        posted_date=datetime.utcnow() - timedelta(days=5),
        employment_type="full-time",
        source_name="Test Source",
        source_type="company",
    )


class TestScoringDeterminism:
    """Tests for deterministic scoring behavior"""
    
    def test_cosine_similarity_deterministic(self):
        """Test that cosine similarity is deterministic"""
        embedding1 = [0.1, 0.2, 0.3, 0.4, 0.5]
        embedding2 = [0.2, 0.3, 0.4, 0.5, 0.6]
        
        # Call multiple times
        score1 = ScoringUtils.cosine_similarity_score(embedding1, embedding2)
        score2 = ScoringUtils.cosine_similarity_score(embedding1, embedding2)
        score3 = ScoringUtils.cosine_similarity_score(embedding1, embedding2)
        
        # Should be identical
        assert score1 == score2 == score3
        assert 0 <= score1 <= 1
    
    def test_skill_extraction_deterministic(self, sample_job):
        """Test that skill extraction is deterministic"""
        skills1 = ScoringUtils.extract_skills_from_job(sample_job)
        skills2 = ScoringUtils.extract_skills_from_job(sample_job)
        skills3 = ScoringUtils.extract_skills_from_job(sample_job)
        
        # Should be identical
        assert skills1 == skills2 == skills3
        
        # Should extract expected skills
        assert "python" in skills1
        assert "fastapi" in skills1
        assert "aws" in skills1
        assert "kubernetes" in skills1
    
    def test_skill_overlap_score_deterministic(self, sample_profile):
        """Test that skill overlap scoring is deterministic"""
        user_skills = ScoringUtils.get_user_skills(sample_profile)
        job_skills = {"python", "fastapi", "aws", "docker"}
        
        score1 = ScoringUtils.skill_overlap_score(user_skills, job_skills)
        score2 = ScoringUtils.skill_overlap_score(user_skills, job_skills)
        score3 = ScoringUtils.skill_overlap_score(user_skills, job_skills)
        
        assert score1 == score2 == score3
        assert 0 <= score1 <= 1
    
    def test_seniority_inference_deterministic(self):
        """Test that seniority inference is deterministic"""
        titles = [
            "Junior Software Engineer",
            "Software Engineer",
            "Senior Software Engineer",
            "Staff Engineer",
            "Principal Engineer",
        ]
        
        for title in titles:
            level1 = ScoringUtils.infer_seniority_from_title(title)
            level2 = ScoringUtils.infer_seniority_from_title(title)
            level3 = ScoringUtils.infer_seniority_from_title(title)
            
            assert level1 == level2 == level3
            assert 1 <= level1 <= 5
    
    def test_location_fit_deterministic(self, sample_profile, sample_job):
        """Test that location fit scoring is deterministic"""
        score1 = ScoringUtils.location_fit_score(sample_profile, sample_job)
        score2 = ScoringUtils.location_fit_score(sample_profile, sample_job)
        score3 = ScoringUtils.location_fit_score(sample_profile, sample_job)
        
        assert score1 == score2 == score3
        assert 0 <= score1 <= 1
    
    def test_recency_score_deterministic(self, sample_job):
        """Test that recency scoring is deterministic"""
        score1 = ScoringUtils.recency_score(sample_job)
        score2 = ScoringUtils.recency_score(sample_job)
        score3 = ScoringUtils.recency_score(sample_job)
        
        assert score1 == score2 == score3
        assert 0 <= score1 <= 1


class TestSkillExtraction:
    """Tests for skill extraction logic"""
    
    def test_extract_common_tech_skills(self):
        """Test extraction of common tech skills"""
        job = JobPostingInDB(
            company="Test",
            title="Python Developer",
            url="https://test.com",
            description_clean="Looking for Python, JavaScript, React, and AWS experience. Knowledge of Docker and Kubernetes is a plus.",
            source_name="Test",
            source_type="test",
        )
        
        skills = ScoringUtils.extract_skills_from_job(job)
        
        assert "python" in skills
        assert "javascript" in skills
        assert "react" in skills
        assert "aws" in skills
        assert "docker" in skills
        assert "kubernetes" in skills
    
    def test_extract_from_title_only(self):
        """Test skill extraction from title when no description"""
        job = JobPostingInDB(
            company="Test",
            title="Senior Python Developer with AWS",
            url="https://test.com",
            description_clean=None,
            source_name="Test",
            source_type="test",
        )
        
        skills = ScoringUtils.extract_skills_from_job(job)
        
        assert "python" in skills
        assert "aws" in skills
    
    def test_no_duplicate_skills(self):
        """Test that duplicate skills are not counted twice"""
        job = JobPostingInDB(
            company="Test",
            title="Python Python Python Developer",
            url="https://test.com",
            description_clean="Python Python Python",
            source_name="Test",
            source_type="test",
        )
        
        skills = ScoringUtils.extract_skills_from_job(job)
        
        # Should only have one "python" in the set
        assert skills.count("python") == 1 if "python" in skills else 0


class TestSeniorityInference:
    """Tests for seniority level inference"""
    
    def test_junior_titles(self):
        """Test detection of junior level"""
        titles = [
            "Junior Software Engineer",
            "Junior Developer",
            "Entry Level Engineer",
            "Graduate Developer",
        ]
        
        for title in titles:
            level = ScoringUtils.infer_seniority_from_title(title)
            assert level == 1, f"Failed for title: {title}"
    
    def test_mid_titles(self):
        """Test detection of mid level"""
        titles = [
            "Software Engineer",
            "Developer",
            "Software Engineer II",
        ]
        
        for title in titles:
            level = ScoringUtils.infer_seniority_from_title(title)
            assert level in [2], f"Failed for title: {title}"
    
    def test_senior_titles(self):
        """Test detection of senior level"""
        titles = [
            "Senior Software Engineer",
            "Senior Developer",
            "Software Engineer III",
        ]
        
        for title in titles:
            level = ScoringUtils.infer_seniority_from_title(title)
            assert level == 3, f"Failed for title: {title}"
    
    def test_lead_titles(self):
        """Test detection of lead/staff level"""
        titles = [
            "Staff Engineer",
            "Lead Developer",
            "Principal Engineer",
            "Architect",
        ]
        
        for title in titles:
            level = ScoringUtils.infer_seniority_from_title(title)
            assert level in [4, 5], f"Failed for title: {title}"


class TestLocationFitScoring:
    """Tests for location fit scoring logic"""
    
    def test_remote_preference_match(self, sample_profile):
        """Test scoring when remote preference matches"""
        job = JobPostingInDB(
            company="Test",
            title="Engineer",
            url="https://test.com",
            remote_type="remote",
            source_name="Test",
            source_type="test",
        )
        
        score = ScoringUtils.location_fit_score(sample_profile, job)
        assert score >= 0.8  # Should score high for remote match
    
    def test_country_preference_match(self, sample_profile):
        """Test scoring when country preference matches"""
        job = JobPostingInDB(
            company="Test",
            title="Engineer",
            url="https://test.com",
            country="Germany",
            remote_type="onsite",
            source_name="Test",
            source_type="test",
        )
        
        score = ScoringUtils.location_fit_score(sample_profile, job)
        assert score >= 0.9  # Should score high for country match
    
    def test_no_location_match(self):
        """Test scoring when location doesn't match preferences"""
        profile = UserProfile(
            name="Test",
            email="test@test.com",
            preferences=Preferences(
                remote=False,
                europe=False,
                countries=["USA"],
            )
        )
        
        job = JobPostingInDB(
            company="Test",
            title="Engineer",
            url="https://test.com",
            country="Japan",
            remote_type="onsite",
            source_name="Test",
            source_type="test",
        )
        
        score = ScoringUtils.location_fit_score(profile, job)
        assert score < 0.5  # Should score low for no match


class TestRecencyScoring:
    """Tests for recency scoring logic"""
    
    def test_very_recent_job(self):
        """Test scoring for job posted < 7 days ago"""
        job = JobPostingInDB(
            company="Test",
            title="Engineer",
            url="https://test.com",
            posted_date=datetime.utcnow() - timedelta(days=3),
            source_name="Test",
            source_type="test",
        )
        
        score = ScoringUtils.recency_score(job)
        assert score == 1.0
    
    def test_recent_job(self):
        """Test scoring for job posted 7-30 days ago"""
        job = JobPostingInDB(
            company="Test",
            title="Engineer",
            url="https://test.com",
            posted_date=datetime.utcnow() - timedelta(days=15),
            source_name="Test",
            source_type="test",
        )
        
        score = ScoringUtils.recency_score(job)
        assert 0.6 <= score <= 0.9
    
    def test_old_job(self):
        """Test scoring for job posted > 90 days ago"""
        job = JobPostingInDB(
            company="Test",
            title="Engineer",
            url="https://test.com",
            posted_date=datetime.utcnow() - timedelta(days=120),
            source_name="Test",
            source_type="test",
        )
        
        score = ScoringUtils.recency_score(job)
        assert score <= 0.3


class TestWeightsConfiguration:
    """Tests for scoring weights configuration"""
    
    def test_default_weights_sum_to_one(self):
        """Test that default weights sum to 1.0"""
        weights = MatchConfig.get_weights()
        total = sum(weights.values())
        
        assert abs(total - 1.0) < 0.001  # Allow for floating point imprecision
    
    def test_all_components_present(self):
        """Test that all required components have weights"""
        weights = MatchConfig.get_weights()
        required_components = ["semantic", "skill_overlap", "seniority_fit", "location_fit", "recency"]
        
        for component in required_components:
            assert component in weights
            assert 0 <= weights[component] <= 1
