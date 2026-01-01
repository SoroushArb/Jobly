"""Tailoring service for generating job-specific CVs and application materials"""
import os
import re
import hashlib
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from app.schemas.packet import TailoringPlan, BulletSwap
from app.schemas.profile import UserProfile, ExperienceRole
from app.schemas.job import JobPosting


class TailoringService:
    """Service for tailoring CVs to specific jobs"""
    
    def __init__(self):
        # Setup Jinja2 environment with custom delimiters to avoid LaTeX conflicts
        template_dir = Path(__file__).parent.parent / "templates" / "latex"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            block_start_string='(%',
            block_end_string='%)',
            variable_start_string='(((',
            variable_end_string=')))',
            comment_start_string='(#',
            comment_end_string='#)',
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def generate_tailoring_plan(
        self, 
        profile: UserProfile, 
        job: JobPosting,
        user_emphasis: Optional[List[str]] = None
    ) -> TailoringPlan:
        """
        Generate a structured tailoring plan for a job.
        
        This is a deterministic, rule-based approach that:
        - Rewrites summary to mention job title/company
        - Prioritizes skills that match job description
        - Suggests bullet improvements (without fabrication)
        - Identifies gaps
        """
        job_desc = (job.description_clean or job.description_raw or "").lower()
        
        # Extract key requirements from job
        required_skills = self._extract_skills_from_job(job_desc)
        
        # Rewrite summary
        summary_rewrite = self._rewrite_summary(profile, job)
        
        # Prioritize matching skills
        skills_priority = self._prioritize_skills(profile, required_skills)
        
        # Suggest bullet swaps
        bullet_swaps = self._suggest_bullet_swaps(profile, job, required_skills)
        
        # Identify gaps
        gaps = self._identify_gaps(profile, required_skills)
        
        # Generate integrity notes
        integrity_notes = []
        if len(gaps) > 3:
            integrity_notes.append(
                f"This role requires {len(gaps)} skills not explicitly in your profile. "
                "Ensure any claimed experience is truthful."
            )
        
        return TailoringPlan(
            job_id=str(job.dedupe_hash),
            profile_id="profile",  # Will be set by caller
            summary_rewrite=summary_rewrite,
            skills_priority=skills_priority,
            bullet_swaps=bullet_swaps,
            keyword_inserts={
                "experience": [s for s in required_skills[:5] if s in job_desc]
            },
            gaps=gaps,
            integrity_notes=integrity_notes
        )
    
    def _extract_skills_from_job(self, job_desc: str) -> List[str]:
        """Extract technical skills from job description"""
        # Common tech skills to look for
        skill_patterns = [
            # Languages
            r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\btypescript\b',
            r'\bc\+\+\b', r'\bc#\b', r'\bgo\b', r'\brust\b', r'\bruby\b',
            r'\bphp\b', r'\bswift\b', r'\bkotlin\b', r'\bscala\b',
            # Frameworks
            r'\breact\b', r'\bangular\b', r'\bvue\b', r'\bnode\.?js\b',
            r'\bdjango\b', r'\bflask\b', r'\bspring\b', r'\b\.net\b',
            r'\bexpress\b', r'\bfastapi\b',
            # Databases
            r'\bpostgresql\b', r'\bmysql\b', r'\bmongodb\b', r'\bredis\b',
            r'\belasticsearch\b', r'\bcassandra\b', r'\bdynamodb\b',
            # Cloud & DevOps
            r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\bdocker\b', r'\bkubernetes\b',
            r'\bk8s\b', r'\bterraform\b', r'\bjenkins\b', r'\bgithub\s+actions\b',
            r'\bci/cd\b', r'\bansible\b',
            # Tools & Methods
            r'\bgit\b', r'\brest\s+api\b', r'\bgraphql\b', r'\bmicroservices\b',
            r'\bagile\b', r'\bscrum\b', r'\btdd\b', r'\bml\b', r'\bai\b',
        ]
        
        found_skills = []
        for pattern in skill_patterns:
            match = re.search(pattern, job_desc, re.IGNORECASE)
            if match:
                # Normalize the skill name
                skill = match.group(0).strip()
                if skill.lower() not in [s.lower() for s in found_skills]:
                    found_skills.append(skill)
        
        return found_skills[:20]  # Limit to top 20
    
    def _rewrite_summary(self, profile: UserProfile, job: JobPosting) -> str:
        """Rewrite summary to mention the job/company"""
        base_summary = profile.summary or "Experienced professional"
        
        # Simple rewrite: prepend interest in the role
        rewrite = f"Motivated {job.title} candidate with strong interest in {job.company}. {base_summary}"
        
        # Keep it concise (max 3 sentences)
        sentences = rewrite.split('.')[:3]
        return '.'.join(sentences) + '.'
    
    def _prioritize_skills(self, profile: UserProfile, required_skills: List[str]) -> List[str]:
        """Order user's skills to emphasize matches with job requirements"""
        user_skills = []
        for skill_group in profile.skills:
            user_skills.extend(skill_group.skills)
        
        # Normalize for comparison
        user_skills_lower = [s.lower() for s in user_skills]
        required_lower = [s.lower() for s in required_skills]
        
        # Matching skills first
        matching = [user_skills[i] for i, s in enumerate(user_skills_lower) if s in required_lower]
        
        # Then other skills
        non_matching = [user_skills[i] for i, s in enumerate(user_skills_lower) if s not in required_lower]
        
        return (matching + non_matching)[:30]  # Limit to top 30
    
    def _suggest_bullet_swaps(
        self, 
        profile: UserProfile, 
        job: JobPosting, 
        required_skills: List[str]
    ) -> List[BulletSwap]:
        """Suggest bullet point improvements without fabricating content"""
        swaps = []
        job_desc_lower = (job.description_clean or job.description_raw or "").lower()
        
        # For each role, check if we can emphasize relevant skills
        for idx, role in enumerate(profile.experience[:3]):  # Focus on top 3 roles
            for bullet in role.bullets[:2]:  # Only suggest for first 2 bullets per role
                # Check if bullet mentions any required skill
                bullet_lower = bullet.text.lower()
                mentioned_skills = [s for s in required_skills if s.lower() in bullet_lower]
                
                if mentioned_skills and len(mentioned_skills) > 0:
                    # Suggest emphasizing the skill
                    skill = mentioned_skills[0]
                    # Don't actually modify - just suggest emphasis
                    swaps.append(BulletSwap(
                        role_index=idx,
                        original_bullet=bullet.text,
                        suggested_bullet=bullet.text,  # Keep same for now (truthful)
                        evidence_ref=bullet.evidence_ref,
                        reason=f"Emphasizes {skill}, which is required for this role"
                    ))
        
        return swaps[:5]  # Limit to 5 suggestions
    
    def _identify_gaps(self, profile: UserProfile, required_skills: List[str]) -> List[str]:
        """Identify skills required by job but not in profile"""
        user_skills = []
        for skill_group in profile.skills:
            user_skills.extend([s.lower() for s in skill_group.skills])
        
        # Also check experience bullets for implicit skills
        for role in profile.experience:
            for bullet in role.bullets:
                # Extract skills from bullet text
                for skill in required_skills:
                    if skill.lower() in bullet.text.lower() and skill.lower() not in user_skills:
                        user_skills.append(skill.lower())
        
        gaps = []
        for skill in required_skills:
            if skill.lower() not in user_skills:
                gaps.append(skill)
        
        return gaps
    
    def render_latex_cv(
        self, 
        profile: UserProfile, 
        plan: TailoringPlan,
        max_roles: int = 4,
        bullets_per_role: int = 4,
        max_projects: int = 3
    ) -> str:
        """
        Render a tailored CV as LaTeX.
        
        Uses deterministic budgeting to fit within 2 pages:
        - max_roles: max experience entries
        - bullets_per_role: max bullets per role
        - max_projects: max project entries
        """
        template = self.jinja_env.get_template("base.tex.j2")
        
        # Apply tailoring plan
        tailored_profile = self._apply_tailoring(profile, plan)
        
        # Render with budget constraints
        latex_content = template.render(
            name=tailored_profile.name,
            email=tailored_profile.email,
            links=tailored_profile.links,
            summary=plan.summary_rewrite,
            skills=self._reorder_skills(tailored_profile.skills, plan.skills_priority),
            experience=tailored_profile.experience,
            projects=tailored_profile.projects,
            education=tailored_profile.education,
            max_roles=max_roles,
            bullets_per_role=bullets_per_role,
            max_projects=max_projects
        )
        
        return latex_content
    
    def _apply_tailoring(self, profile: UserProfile, plan: TailoringPlan) -> UserProfile:
        """Apply tailoring plan to profile (without modifying original)"""
        # Create a copy with modifications
        import copy
        tailored = copy.deepcopy(profile)
        
        # Apply bullet swaps (for now, we keep original bullets)
        # In future, could apply AI-generated rewrites here
        
        return tailored
    
    def _reorder_skills(self, skill_groups, priority_skills: List[str]):
        """Reorder skill groups to show prioritized skills first"""
        import copy
        reordered = copy.deepcopy(skill_groups)
        
        # For each group, reorder skills based on priority
        priority_lower = [s.lower() for s in priority_skills]
        
        for group in reordered:
            skills_with_priority = []
            for skill in group.skills:
                if skill.lower() in priority_lower:
                    priority_idx = priority_lower.index(skill.lower())
                    skills_with_priority.append((priority_idx, skill))
                else:
                    skills_with_priority.append((9999, skill))
            
            # Sort by priority
            skills_with_priority.sort(key=lambda x: x[0])
            group.skills = [s[1] for s in skills_with_priority]
        
        return reordered
    
    def compile_latex(self, tex_content: str, output_dir: Path) -> Optional[Path]:
        """
        Compile LaTeX to PDF using latexmk.
        
        Returns path to PDF if successful, None otherwise.
        """
        # Check if latexmk is available
        try:
            subprocess.run(
                ["latexmk", "-version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None  # latexmk not available
        
        # Write tex file
        tex_file = output_dir / "cv.tex"
        tex_file.write_text(tex_content, encoding='utf-8')
        
        # Compile with latexmk
        try:
            result = subprocess.run(
                ["latexmk", "-pdf", "-interaction=nonstopmode", str(tex_file)],
                cwd=output_dir,
                capture_output=True,
                timeout=30  # 30 second timeout
            )
            
            pdf_file = output_dir / "cv.pdf"
            if pdf_file.exists():
                return pdf_file
            else:
                return None
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return None
    
    def generate_cover_letter(
        self, 
        profile: UserProfile, 
        job: JobPosting,
        plan: TailoringPlan
    ) -> str:
        """Generate a simple cover letter"""
        today = datetime.utcnow().strftime("%B %d, %Y")
        
        cover_letter = f"""Dear Hiring Manager at {job.company},

I am writing to express my strong interest in the {job.title} position. With my background in {', '.join(plan.skills_priority[:3])}, I believe I would be a valuable addition to your team.

{plan.summary_rewrite}

I am particularly drawn to {job.company} and excited about the opportunity to contribute to your team. I am confident that my skills and experience align well with the requirements of this role.

Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to {job.company}.

Sincerely,
{profile.name}
"""
        return cover_letter
    
    def generate_recruiter_message(
        self,
        profile: UserProfile,
        job: JobPosting,
        plan: TailoringPlan
    ) -> str:
        """Generate a brief message for recruiters/hiring managers"""
        message = f"""Hi,

I noticed the {job.title} opening at {job.company} and wanted to reach out directly. With my experience in {', '.join(plan.skills_priority[:3])}, I believe I could make a strong contribution to your team.

I've attached my resume tailored for this role. I'd love to discuss how my background aligns with what you're looking for.

Looking forward to connecting!

Best regards,
{profile.name}
"""
        return message
    
    def generate_common_answers(
        self,
        profile: UserProfile,
        job: JobPosting
    ) -> str:
        """Generate common application question answers"""
        answers = f"""# Common Application Answers for {job.title} at {job.company}

## Salary Expectation
- Research the market rate for this position and location
- Consider your experience level and the company size
- Provide a range rather than a specific number
- Example: "Based on my research and experience, I'm targeting $X - $Y"

## Start Date
- Standard: 2-4 weeks notice if currently employed
- Immediate: If currently available
- Custom: Specify if you have commitments

## Work Authorization
- Specify your current authorization status
- Mention if you require sponsorship
- Note any visa restrictions or timelines

## Why This Company?
- Research {job.company}'s mission, values, and recent achievements
- Connect your skills and interests to their work
- Mention specific projects or initiatives that excite you

## Why This Role?
- The {job.title} position aligns with my background in {', '.join([sg.category for sg in profile.skills[:2]])}
- Opportunity to work with technologies I'm passionate about
- Chance to grow and take on new challenges

## Questions for Interviewer
1. What does success look like in this role in the first 90 days?
2. How does the team approach collaboration and decision-making?
3. What are the biggest challenges the team is currently facing?
4. What opportunities are there for professional development and growth?
5. What is the typical career path for someone in this role?
"""
        return answers


def compute_file_hash(content: str) -> str:
    """Compute SHA256 hash of file content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
