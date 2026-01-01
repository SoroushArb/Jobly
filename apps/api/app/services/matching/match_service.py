"""Service for generating and managing job matches"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from bson import ObjectId

from app.schemas.profile import UserProfile
from app.schemas.job import JobPostingInDB
from app.schemas.match import Match, ScoreBreakdown
from app.services.embeddings.factory import EmbeddingProviderFactory
from app.services.embeddings.cache import EmbeddingCache
from app.services.matching.scoring import ScoringUtils
from app.services.matching.config import MatchConfig
from app.models.database import Database


class MatchGenerationService:
    """Service for computing job matches"""
    
    def __init__(self):
        self.embedding_provider = EmbeddingProviderFactory.create_provider()
        self.embedding_cache = EmbeddingCache()
        self.weights = MatchConfig.get_weights()
        self.matches_collection = Database.get_database()["matches"]
        self.jobs_collection = Database.get_database()["jobs"]
    
    async def create_profile_embedding(self, profile: UserProfile) -> List[float]:
        """
        Create embedding for user profile
        
        Combines: summary + skills + key experience bullets
        
        Args:
            profile: User profile
            
        Returns:
            Embedding vector
        """
        # Build profile text
        parts = []
        
        # Add summary
        if profile.summary:
            parts.append(profile.summary)
        
        # Add skills
        all_skills = []
        for skill_group in profile.skills:
            all_skills.extend(skill_group.skills)
        if all_skills:
            parts.append("Skills: " + ", ".join(all_skills))
        
        # Add key experience bullets (top 3 most recent roles, top 3 bullets each)
        for exp in profile.experience[:3]:
            parts.append(f"{exp.title} at {exp.company}")
            for bullet in exp.bullets[:3]:
                parts.append(bullet.text)
        
        profile_text = "\n".join(parts)
        
        # Check cache
        model_name = self.embedding_provider.get_model_name()
        cached = await self.embedding_cache.get(profile_text, model_name)
        
        if cached:
            return cached
        
        # Generate embedding
        embedding = await self.embedding_provider.get_embedding(profile_text)
        
        # Cache it
        await self.embedding_cache.set(profile_text, model_name, embedding)
        
        return embedding
    
    async def create_job_embedding(self, job: JobPostingInDB) -> List[float]:
        """
        Create embedding for job posting
        
        Args:
            job: Job posting
            
        Returns:
            Embedding vector
        """
        # Build job text
        parts = [
            job.title,
            f"at {job.company}",
        ]
        
        if job.description_clean:
            # Use first 2000 chars to stay within token limits
            parts.append(job.description_clean[:2000])
        
        job_text = "\n".join(parts)
        
        # Check cache
        model_name = self.embedding_provider.get_model_name()
        cached = await self.embedding_cache.get(job_text, model_name)
        
        if cached:
            return cached
        
        # Generate embedding
        embedding = await self.embedding_provider.get_embedding(job_text)
        
        # Cache it
        await self.embedding_cache.set(job_text, model_name, embedding)
        
        return embedding
    
    def compute_match_score(
        self,
        profile: UserProfile,
        job: JobPostingInDB,
        profile_embedding: List[float],
        job_embedding: List[float],
    ) -> Tuple[float, ScoreBreakdown]:
        """
        Compute match score and breakdown
        
        Args:
            profile: User profile
            job: Job posting
            profile_embedding: Profile embedding vector
            job_embedding: Job embedding vector
            
        Returns:
            Tuple of (total_score, breakdown)
        """
        breakdown = ScoreBreakdown()
        
        # 1. Semantic similarity
        breakdown.semantic = ScoringUtils.cosine_similarity_score(
            profile_embedding, job_embedding
        )
        
        # 2. Skill overlap
        user_skills = ScoringUtils.get_user_skills(profile)
        job_skills = ScoringUtils.extract_skills_from_job(job)
        breakdown.skill_overlap = ScoringUtils.skill_overlap_score(user_skills, job_skills)
        
        # 3. Seniority fit
        user_seniority = ScoringUtils.infer_user_seniority(profile)
        job_seniority = ScoringUtils.infer_seniority_from_title(job.title)
        breakdown.seniority_fit = ScoringUtils.seniority_fit_score(user_seniority, job_seniority)
        
        # 4. Location fit
        breakdown.location_fit = ScoringUtils.location_fit_score(profile, job)
        
        # 5. Recency
        breakdown.recency = ScoringUtils.recency_score(job)
        
        # Compute weighted total
        total_score = (
            breakdown.semantic * self.weights["semantic"] +
            breakdown.skill_overlap * self.weights["skill_overlap"] +
            breakdown.seniority_fit * self.weights["seniority_fit"] +
            breakdown.location_fit * self.weights["location_fit"] +
            breakdown.recency * self.weights["recency"]
        )
        
        return total_score, breakdown
    
    def generate_explainability(
        self,
        profile: UserProfile,
        job: JobPostingInDB,
        breakdown: ScoreBreakdown,
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Generate explainability: reasons, gaps, recommendations
        
        Args:
            profile: User profile
            job: Job posting
            breakdown: Score breakdown
            
        Returns:
            Tuple of (top_reasons, gaps, recommendations)
        """
        reasons = []
        gaps = []
        recommendations = []
        
        # Analyze each component
        user_skills = ScoringUtils.get_user_skills(profile)
        job_skills = ScoringUtils.extract_skills_from_job(job)
        
        # Skill overlap analysis
        matched_skills = user_skills & job_skills
        missing_skills = job_skills - user_skills
        
        if matched_skills:
            skill_list = ", ".join(list(matched_skills)[:3])
            reasons.append(f"Matching skills: {skill_list}")
        
        if missing_skills:
            missing_list = list(missing_skills)[:3]
            gaps.append(f"Missing skills: {', '.join(missing_list)}")
            recommendations.append(f"Consider learning: {missing_list[0]}")
        
        # Seniority analysis
        user_seniority = ScoringUtils.infer_user_seniority(profile)
        job_seniority = ScoringUtils.infer_seniority_from_title(job.title)
        
        if breakdown.seniority_fit >= 0.7:
            reasons.append(f"Good seniority match for {job.title}")
        elif user_seniority < job_seniority:
            gaps.append("Job may require more seniority/experience")
            recommendations.append("Highlight leadership and impact in your experience bullets")
        
        # Location analysis
        if breakdown.location_fit >= 0.8:
            if job.remote_type == "remote":
                reasons.append("Matches your remote work preference")
            else:
                reasons.append(f"Good location match: {job.city or job.country or 'location'}")
        elif breakdown.location_fit < 0.5:
            if job.remote_type in ["onsite", "hybrid"]:
                gaps.append(f"Location may not match preferences ({job.city or job.country})")
        
        # Recency
        if breakdown.recency >= 0.8:
            reasons.append("Recently posted position")
        
        # Semantic similarity
        if breakdown.semantic >= 0.7:
            reasons.append("Strong overall profile match")
        
        # Limit to top 5 reasons
        reasons = reasons[:5]
        
        return reasons, gaps, recommendations
    
    async def generate_match(
        self,
        profile: UserProfile,
        profile_id: str,
        job: JobPostingInDB,
    ) -> Match:
        """
        Generate a single match
        
        Args:
            profile: User profile
            profile_id: Profile ObjectId as string
            job: Job posting
            
        Returns:
            Match object
        """
        # Get embeddings
        profile_embedding = await self.create_profile_embedding(profile)
        job_embedding = await self.create_job_embedding(job)
        
        # Compute scores
        total_score, breakdown = self.compute_match_score(
            profile, job, profile_embedding, job_embedding
        )
        
        # Generate explainability
        reasons, gaps, recommendations = self.generate_explainability(
            profile, job, breakdown
        )
        
        # Create match
        match = Match(
            profile_id=profile_id,
            job_id=str(job.id) if hasattr(job, 'id') and job.id else "",
            score_total=total_score,
            score_breakdown=breakdown,
            top_reasons=reasons,
            gaps=gaps,
            recommendations=recommendations,
            embedding_model=self.embedding_provider.get_model_name(),
            posted_date=job.posted_date or job.fetched_at,
        )
        
        return match
    
    async def recompute_all_matches(self, profile_id: str) -> int:
        """
        Recompute all matches for a profile
        
        Args:
            profile_id: Profile ObjectId as string
            
        Returns:
            Number of matches computed
        """
        # Get profile
        from app.models.database import get_profiles_collection
        profiles_collection = get_profiles_collection()
        
        profile_doc = await profiles_collection.find_one({"_id": ObjectId(profile_id)})
        if not profile_doc:
            raise ValueError(f"Profile not found: {profile_id}")
        
        # Convert to UserProfile
        profile = UserProfile(**profile_doc)
        
        # Get all jobs
        cursor = self.jobs_collection.find({})
        jobs = await cursor.to_list(length=None)
        
        matches_computed = 0
        
        # Generate matches for each job
        for job_doc in jobs:
            # Convert to JobPostingInDB
            job_doc["id"] = str(job_doc["_id"])
            job = JobPostingInDB(**job_doc)
            
            # Generate match
            match = await self.generate_match(profile, profile_id, job)
            
            # Store match (upsert)
            match_dict = match.model_dump()
            
            await self.matches_collection.update_one(
                {
                    "profile_id": profile_id,
                    "job_id": match.job_id,
                },
                {"$set": match_dict},
                upsert=True
            )
            
            matches_computed += 1
        
        return matches_computed
