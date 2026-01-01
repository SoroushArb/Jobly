"""Scoring utilities for job matching"""
import re
import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
from app.schemas.profile import UserProfile
from app.schemas.job import JobPostingInDB
from .config import MatchConfig


class ScoringUtils:
    """Utilities for computing match scores"""
    
    @staticmethod
    def cosine_similarity_score(embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        # Reshape for sklearn
        emb1 = np.array(embedding1).reshape(1, -1)
        emb2 = np.array(embedding2).reshape(1, -1)
        
        # Compute cosine similarity
        similarity = cosine_similarity(emb1, emb2)[0][0]
        
        # Normalize to [0, 1] range (cosine similarity is in [-1, 1])
        return (similarity + 1) / 2
    
    @staticmethod
    def extract_skills_from_job(job: JobPostingInDB) -> Set[str]:
        """
        Extract skills from job posting using deterministic rules
        
        Args:
            job: Job posting
            
        Returns:
            Set of extracted skill keywords
        """
        skills = set()
        
        # Common skill patterns to look for
        # This is a simple deterministic extractor
        text = f"{job.title} {job.description_clean or ''}".lower()
        
        # Common tech skills (extendable list)
        common_skills = [
            "python", "java", "javascript", "typescript", "go", "rust", "c++", "c#",
            "react", "vue", "angular", "node.js", "django", "flask", "fastapi",
            "kubernetes", "docker", "aws", "azure", "gcp", "terraform",
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "machine learning", "ml", "ai", "data science", "deep learning",
            "rest", "api", "graphql", "microservices", "agile", "scrum",
            "git", "ci/cd", "jenkins", "gitlab", "github actions",
            "sql", "nosql", "data engineering", "etl", "spark",
        ]
        
        for skill in common_skills:
            # Look for whole word matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text):
                skills.add(skill)
        
        return skills
    
    @staticmethod
    def get_user_skills(profile: UserProfile) -> Set[str]:
        """
        Extract all skills from user profile
        
        Args:
            profile: User profile
            
        Returns:
            Set of user skills (normalized to lowercase)
        """
        skills = set()
        
        # Add from skill groups
        for skill_group in profile.skills:
            for skill in skill_group.skills:
                skills.add(skill.lower())
        
        # Add from preferences skill tags
        for tag in profile.preferences.skill_tags:
            skills.add(tag.lower())
        
        # Add from experience tech
        for exp in profile.experience:
            for tech in exp.tech:
                skills.add(tech.lower())
        
        # Add from projects
        for project in profile.projects:
            for tech in project.tech:
                skills.add(tech.lower())
        
        return skills
    
    @staticmethod
    def skill_overlap_score(user_skills: Set[str], job_skills: Set[str]) -> float:
        """
        Compute skill overlap score
        
        Args:
            user_skills: Set of user skills
            job_skills: Set of job required skills
            
        Returns:
            Overlap score between 0 and 1
        """
        if not job_skills:
            return 0.5  # No specific skills required, neutral score
        
        if not user_skills:
            return 0.0  # User has no skills listed
        
        # Calculate Jaccard similarity
        intersection = len(user_skills & job_skills)
        union = len(user_skills | job_skills)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    @staticmethod
    def infer_seniority_from_title(title: str) -> int:
        """
        Infer seniority level from job title
        
        Args:
            title: Job title
            
        Returns:
            Seniority level (1-5)
        """
        title_lower = title.lower()
        
        # Check for lead/principal first (highest)
        for keyword in MatchConfig.LEAD_KEYWORDS:
            if keyword in title_lower:
                return 4
        
        # Check for senior
        for keyword in MatchConfig.SENIOR_KEYWORDS:
            if keyword in title_lower:
                return 3
        
        # Check for mid
        for keyword in MatchConfig.MID_KEYWORDS:
            if keyword in title_lower:
                return 2
        
        # Check for junior
        for keyword in MatchConfig.JUNIOR_KEYWORDS:
            if keyword in title_lower:
                return 1
        
        # Default to mid-level if no indicators
        return 2
    
    @staticmethod
    def infer_user_seniority(profile: UserProfile) -> int:
        """
        Infer user's seniority level from their experience
        
        Args:
            profile: User profile
            
        Returns:
            Seniority level (1-5)
        """
        # Count years of experience (rough estimate)
        years_experience = len(profile.experience)
        
        # Check titles for seniority indicators
        max_seniority = 2  # Default to mid
        
        for exp in profile.experience:
            title_seniority = ScoringUtils.infer_seniority_from_title(exp.title)
            max_seniority = max(max_seniority, title_seniority)
        
        # Adjust based on experience count
        if years_experience >= 10:
            max_seniority = max(max_seniority, 4)
        elif years_experience >= 5:
            max_seniority = max(max_seniority, 3)
        
        return max_seniority
    
    @staticmethod
    def seniority_fit_score(user_seniority: int, job_seniority: int) -> float:
        """
        Compute seniority fit score
        
        Args:
            user_seniority: User's seniority level (1-5)
            job_seniority: Job's seniority level (1-5)
            
        Returns:
            Fit score between 0 and 1
        """
        # Perfect match
        if user_seniority == job_seniority:
            return 1.0
        
        # One level difference
        if abs(user_seniority - job_seniority) == 1:
            return 0.7
        
        # Two levels difference
        if abs(user_seniority - job_seniority) == 2:
            return 0.4
        
        # More than two levels difference
        return 0.2
    
    @staticmethod
    def location_fit_score(profile: UserProfile, job: JobPostingInDB) -> float:
        """
        Compute location fit score based on preferences
        
        Args:
            profile: User profile with preferences
            job: Job posting
            
        Returns:
            Location fit score between 0 and 1
        """
        prefs = profile.preferences
        score = 0.0
        
        # Remote preference
        if prefs.remote and job.remote_type == "remote":
            score = 1.0
        elif job.remote_type == "remote":
            score = 0.8  # Remote jobs are generally good even if not explicitly preferred
        
        # Europe preference
        european_countries = {
            "germany", "france", "uk", "united kingdom", "netherlands", "spain",
            "italy", "poland", "sweden", "norway", "denmark", "finland",
            "austria", "belgium", "switzerland", "ireland", "portugal", "greece"
        }
        
        job_country = (job.country or "").lower()
        
        if prefs.europe and job_country in european_countries:
            score = max(score, 0.9)
        
        # Country preference
        if prefs.countries:
            for country in prefs.countries:
                if country.lower() in job_country:
                    score = max(score, 1.0)
                    break
        
        # City preference
        if prefs.cities and job.city:
            job_city = job.city.lower()
            for city in prefs.cities:
                if city.lower() in job_city:
                    score = max(score, 1.0)
                    break
        
        # If hybrid or onsite and no location match, reduce score
        if job.remote_type in ["onsite", "hybrid"] and score < 0.5:
            score = 0.3
        
        # If we have no preferences set, give neutral score
        if not any([prefs.remote, prefs.europe, prefs.countries, prefs.cities]):
            score = 0.5
        
        return score
    
    @staticmethod
    def recency_score(job: JobPostingInDB) -> float:
        """
        Compute recency score based on posting date
        
        Args:
            job: Job posting
            
        Returns:
            Recency score between 0 and 1
        """
        if not job.posted_date:
            # Use fetched_at as fallback
            posted_date = job.fetched_at
        else:
            posted_date = job.posted_date
        
        # Calculate age in days
        age_days = (datetime.utcnow() - posted_date).days
        
        # Decay function: 1.0 for new jobs, decreasing with age
        if age_days <= 7:
            return 1.0
        elif age_days <= 30:
            return 0.8
        elif age_days <= 60:
            return 0.6
        elif age_days <= MatchConfig.RECENCY_DECAY_DAYS:
            return 0.4
        else:
            return 0.2
