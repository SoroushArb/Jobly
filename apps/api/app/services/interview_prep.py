"""Interview preparation service using LLM for structured generation"""
import re
from typing import List, Dict, Optional
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
from app.schemas.profile import UserProfile
from app.schemas.job import JobPosting
from app.schemas.packet import Packet
from app.services.llm import get_llm_provider


class InterviewPrepService:
    """Service for generating interview preparation materials"""
    
    def __init__(self):
        """Initialize interview prep service with LLM provider"""
        self.llm_provider = get_llm_provider()
    
    async def generate_interview_pack(
        self,
        profile: UserProfile,
        job: JobPosting,
        packet: Packet
    ) -> InterviewPack:
        """
        Generate complete interview preparation pack
        
        Args:
            profile: User's profile
            job: Target job posting
            packet: Application packet (for context)
            
        Returns:
            InterviewPack with grounded STAR stories and other materials
        """
        
        # Extract role/company info from job description
        role_digest = self._extract_role_digest(job)
        company_digest, integrity_note = self._extract_company_digest(job)
        
        # Generate 30/60/90 day plan
        plans = await self._generate_30_60_90_plan(profile, job)
        
        # Generate STAR stories grounded in experience
        star_stories = await self._generate_star_stories(profile, job)
        
        # Generate questions to ask interviewer
        questions = await self._generate_interview_questions(job)
        
        # Generate study checklist (placeholders)
        study_checklist = self._generate_study_checklist(profile, job, packet)
        
        return InterviewPack(
            packet_id=str(packet.id) if hasattr(packet, 'id') else "",
            job_id=job.id if hasattr(job, 'id') else "",
            profile_id=str(profile.id) if hasattr(profile, 'id') else "",
            company_name=job.company,
            role_title=job.title,
            role_digest=role_digest,
            company_digest=company_digest,
            integrity_note=integrity_note,
            plan_30_days=plans["30"],
            plan_60_days=plans["60"],
            plan_90_days=plans["90"],
            star_stories=star_stories,
            questions_to_ask=questions,
            study_checklist=study_checklist
        )
    
    async def generate_technical_qa(
        self,
        profile: UserProfile,
        job: JobPosting,
        packet: Packet
    ) -> TechnicalQA:
        """
        Generate technical Q&A based on gaps and job requirements
        
        Args:
            profile: User's profile
            job: Target job posting
            packet: Application packet (contains gap analysis)
            
        Returns:
            TechnicalQA with topic-grouped questions
        """
        
        # Identify priority topics from gaps and job requirements
        priority_topics = self._identify_priority_topics(profile, job, packet)
        
        # Generate questions for each topic
        topics = await self._generate_qa_topics(priority_topics, job)
        
        return TechnicalQA(
            packet_id=str(packet.id) if hasattr(packet, 'id') else "",
            job_id=job.id if hasattr(job, 'id') else "",
            profile_id=str(profile.id) if hasattr(profile, 'id') else "",
            priority_topics=priority_topics,
            topics=topics
        )
    
    def _extract_role_digest(self, job: JobPosting) -> str:
        """Extract role summary from job description only"""
        description = job.description_clean or job.description_raw or ""
        
        # Simple extraction: take first few sentences or key responsibilities
        lines = [line.strip() for line in description.split('\n') if line.strip()]
        digest_lines = []
        
        for line in lines[:10]:  # Look at first 10 lines
            if any(keyword in line.lower() for keyword in ['responsible', 'will', 'role', 'position', 'duties']):
                digest_lines.append(line)
                if len(digest_lines) >= 3:
                    break
        
        if digest_lines:
            return " ".join(digest_lines)
        else:
            # Fallback: return first paragraph
            return " ".join(lines[:3]) if lines else f"Details available in job description for {job.title}"
    
    def _extract_company_digest(self, job: JobPosting) -> tuple[str, str | None]:
        """
        Extract company info from job description only
        
        Returns:
            Tuple of (digest, integrity_note)
        """
        description = job.description_clean or job.description_raw or ""
        
        # Look for company information in description
        company_lines = []
        for line in description.split('\n'):
            if any(keyword in line.lower() for keyword in ['company', 'we are', 'about us', 'our mission', 'founded']):
                company_lines.append(line.strip())
        
        if company_lines:
            digest = " ".join(company_lines[:3])
            integrity_note = None
        else:
            digest = f"Company information not provided in job description. Research {job.company} independently."
            integrity_note = "Limited company information available from job description. Recommend independent research."
        
        return digest, integrity_note
    
    async def _generate_30_60_90_plan(
        self,
        profile: UserProfile,
        job: JobPosting
    ) -> Dict[str, List[str]]:
        """Generate 30/60/90 day plan using LLM"""
        
        prompt = f"""Generate a realistic 30/60/90 day plan for someone starting as a {job.title} at {job.company}.

Profile skills: {', '.join([s for sg in profile.skills for s in sg.skills])}
Job description excerpt: {(job.description_clean or job.description_raw or '')[:1000]}

Create actionable, specific goals for each period. Focus on learning, relationships, and deliverables.
Return 3-5 goals per period.

IMPORTANT: Output must be in English only."""
        
        # Define inline schema for 30/60/90 plan
        from pydantic import BaseModel
        
        class Plan306090(BaseModel):
            plan_30_days: List[str]
            plan_60_days: List[str]
            plan_90_days: List[str]
        
        try:
            plan = await self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=Plan306090,
                system_prompt="You are an expert career coach helping candidates prepare for new roles. Always output in English.",
                temperature=0.7
            )
            
            return {
                "30": plan.plan_30_days,
                "60": plan.plan_60_days,
                "90": plan.plan_90_days
            }
        except Exception as e:
            # Fallback to generic plan
            return {
                "30": [
                    "Complete onboarding and setup development environment",
                    "Meet with team members and key stakeholders",
                    "Understand codebase architecture and documentation",
                    "Complete first small feature or bug fix"
                ],
                "60": [
                    "Deliver first significant feature independently",
                    "Participate in code reviews and provide feedback",
                    "Identify areas for process improvement",
                    "Begin mentoring or pairing with junior developers"
                ],
                "90": [
                    "Own a complete feature from design to deployment",
                    "Contribute to technical discussions and architecture decisions",
                    "Demonstrate expertise in key technologies",
                    "Set goals for next quarter aligned with team objectives"
                ]
            }
    
    async def _generate_star_stories(
        self,
        profile: UserProfile,
        job: JobPosting
    ) -> List[STARStory]:
        """
        Generate STAR stories grounded in user's experience
        
        Creates stories that map to actual experience bullets
        """
        
        # Extract user's experience bullets as grounding material
        experience_context = []
        for idx, role in enumerate(profile.experience):
            for bullet_idx, bullet in enumerate(role.bullets):
                experience_context.append({
                    "role_index": idx,
                    "bullet_index": bullet_idx,
                    "company": role.company,
                    "title": role.title,
                    "text": bullet.text,
                    "evidence": bullet.evidence_ref
                })
        
        if not experience_context:
            return []  # No experience to ground stories in
        
        # Format experience for prompt
        experience_text = "\n".join([
            f"Experience {i}: [{exp['company']} - {exp['title']}] {exp['text']}"
            for i, exp in enumerate(experience_context)
        ])
        
        prompt = f"""Create 3-5 STAR format interview stories based ONLY on the following real experience.
DO NOT invent or fabricate any details not present in the experience bullets.

Role applying for: {job.title}
Key skills needed: {', '.join((job.description_clean or job.description_raw or '')[:500].split()[:20])}

Candidate's Real Experience:
{experience_text}

For each story:
1. Choose experience bullets that demonstrate relevant skills
2. Structure them in STAR format (Situation, Task, Action, Result)
3. Include metrics/outcomes if mentioned in original bullets
4. Reference which experience bullets you're using (by index)
5. Only use information that exists in the experience bullets

IMPORTANT: 
- Output must be in English only
- Ground each story in actual experience entries
- Do not invent achievements or metrics
- If no relevant experience exists for a skill, skip that story"""
        
        from pydantic import BaseModel
        
        class GroundingRef(BaseModel):
            experience_index: int
            evidence_text: str
        
        class STARStoryModel(BaseModel):
            title: str
            situation: str
            task: str
            action: str
            result: str
            skills_demonstrated: List[str]
            grounding_refs: List[GroundingRef]
        
        class STARStoriesResponse(BaseModel):
            stories: List[STARStoryModel]
        
        try:
            response = await self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=STARStoriesResponse,
                system_prompt="You are an interview coach who helps candidates structure their real experience into compelling STAR stories. Never fabricate details. Always output in English.",
                temperature=0.5  # Lower temperature for more grounded output
            )
            
            # Convert to InterviewPack STARStory format with proper grounding
            stories = []
            for story in response.stories:
                # Map experience indices to actual experience bullets
                grounding_refs = []
                for ref in story.grounding_refs:
                    if 0 <= ref.experience_index < len(experience_context):
                        exp = experience_context[ref.experience_index]
                        grounding_refs.append(GroundingReference(
                            experience_index=exp["role_index"],
                            bullet_index=exp["bullet_index"],
                            evidence_text=ref.evidence_text
                        ))
                
                stories.append(STARStory(
                    title=story.title,
                    situation=story.situation,
                    task=story.task,
                    action=story.action,
                    result=story.result,
                    skills_demonstrated=story.skills_demonstrated,
                    grounding_refs=grounding_refs
                ))
            
            return stories[:5]  # Limit to 5 stories
            
        except Exception as e:
            # Return empty list on failure - better than fabricated stories
            return []
    
    async def _generate_interview_questions(self, job: JobPosting) -> List[InterviewQuestion]:
        """Generate thoughtful questions to ask the interviewer"""
        
        prompt = f"""Generate 5-7 insightful questions to ask during an interview for a {job.title} position at {job.company}.

Job description excerpt: {(job.description_clean or job.description_raw or '')[:800]}

Create questions that:
1. Show genuine interest in the role and company
2. Help assess cultural fit
3. Understand growth opportunities
4. Clarify technical expectations
5. Are specific to this role/company (avoid generic questions)

Categorize each question as: role, team, culture, growth, or technical

IMPORTANT: Output must be in English only."""
        
        from pydantic import BaseModel
        
        class QuestionModel(BaseModel):
            question: str
            category: str
            reasoning: str
        
        class QuestionsResponse(BaseModel):
            questions: List[QuestionModel]
        
        try:
            response = await self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=QuestionsResponse,
                system_prompt="You are an interview coach helping candidates prepare thoughtful questions. Always output in English.",
                temperature=0.7
            )
            
            return [
                InterviewQuestion(
                    question=q.question,
                    category=q.category,
                    reasoning=q.reasoning
                )
                for q in response.questions
            ]
            
        except Exception as e:
            # Fallback to generic but good questions
            return [
                InterviewQuestion(
                    question=f"What does success look like for someone in the {job.title} role after 6 months?",
                    category="role",
                    reasoning="Helps understand expectations and success criteria"
                ),
                InterviewQuestion(
                    question="How does the team approach technical decision-making and code reviews?",
                    category="team",
                    reasoning="Reveals team culture and collaboration practices"
                ),
                InterviewQuestion(
                    question=f"What are the biggest challenges facing the team/product right now?",
                    category="role",
                    reasoning="Shows interest and reveals what you'd be working on"
                )
            ]
    
    def _generate_study_checklist(
        self,
        profile: UserProfile,
        job: JobPosting,
        packet: Packet
    ) -> List[StudyResource]:
        """
        Generate study checklist with placeholders (no external links)
        
        Focuses on gaps identified in the packet
        """
        gaps = packet.tailoring_plan.gaps
        
        resources = []
        
        # Create placeholder resources for each gap
        for gap in gaps[:10]:  # Limit to top 10 gaps
            resources.append(StudyResource(
                topic=gap,
                resource_type="documentation",
                description=f"Review official {gap} documentation and best practices"
            ))
            
            # Add practice resource for technical skills
            if any(keyword in gap.lower() for keyword in ['python', 'java', 'sql', 'algorithm', 'data structure']):
                resources.append(StudyResource(
                    topic=gap,
                    resource_type="practice problems",
                    description=f"Practice {gap} coding problems and exercises"
                ))
        
        # Add general interview prep resources
        resources.append(StudyResource(
            topic="System Design",
            resource_type="tutorial",
            description="Study system design patterns relevant to this role"
        ))
        
        resources.append(StudyResource(
            topic="Behavioral Questions",
            resource_type="practice",
            description="Practice common behavioral questions using STAR format"
        ))
        
        return resources
    
    def _identify_priority_topics(
        self,
        profile: UserProfile,
        job: JobPosting,
        packet: Packet
    ) -> List[str]:
        """Identify priority technical topics based on gaps and job requirements"""
        
        # Start with gaps from tailoring plan
        priority_topics = packet.tailoring_plan.gaps[:5]  # Top 5 gaps
        
        # Add key skills from job description
        job_desc = (job.description_clean or job.description_raw or "").lower()
        
        # Common technical topics to check for
        technical_keywords = {
            "algorithms": ["algorithm", "data structure", "complexity"],
            "system design": ["system design", "architecture", "scalability", "distributed"],
            "python": ["python"],
            "sql": ["sql", "database", "query"],
            "api design": ["api", "rest", "graphql"],
            "testing": ["test", "tdd", "unit test"],
            "cloud": ["aws", "azure", "gcp", "cloud"],
        }
        
        # Use set for faster lookups
        priority_set = set(priority_topics)
        
        for topic, keywords in technical_keywords.items():
            if any(keyword in job_desc for keyword in keywords):
                topic_title = topic.title()
                if topic_title not in priority_set:
                    priority_topics.append(topic_title)
                    priority_set.add(topic_title)
        
        return priority_topics[:7]  # Limit to 7 topics
    
    async def _generate_qa_topics(
        self,
        priority_topics: List[str],
        job: JobPosting
    ) -> List[TechnicalQATopic]:
        """Generate technical Q&A for each priority topic"""
        
        topics = []
        
        for topic in priority_topics:
            questions = await self._generate_topic_questions(topic, job)
            if questions:
                topics.append(TechnicalQATopic(
                    topic=topic,
                    questions=questions
                ))
        
        return topics
    
    async def _generate_topic_questions(
        self,
        topic: str,
        job: JobPosting
    ) -> List[TechnicalQuestion]:
        """Generate questions for a specific technical topic"""
        
        prompt = f"""Generate 6-9 technical interview questions for the topic: {topic}

Context: Preparing for a {job.title} role
Create questions at three difficulty levels (easy, medium, hard) with:
- 2-3 questions per difficulty level
- High-quality detailed answers
- 1-3 follow-up questions per question
- Key concepts being tested

Focus on practical, real-world scenarios relevant to {job.title}.

IMPORTANT: Output must be in English only."""
        
        from pydantic import BaseModel
        
        class QuestionModel(BaseModel):
            question: str
            difficulty: DifficultyLevel
            answer: str
            follow_ups: List[str]
            key_concepts: List[str]
        
        class TopicQuestionsResponse(BaseModel):
            questions: List[QuestionModel]
        
        try:
            response = await self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=TopicQuestionsResponse,
                system_prompt="You are a technical interviewer creating high-quality interview questions with detailed answers. Always output in English.",
                temperature=0.6
            )
            
            return [
                TechnicalQuestion(
                    question=q.question,
                    difficulty=q.difficulty,
                    answer=q.answer,
                    follow_ups=q.follow_ups,
                    key_concepts=q.key_concepts
                )
                for q in response.questions
            ]
            
        except Exception as e:
            # Return empty list on failure
            return []
