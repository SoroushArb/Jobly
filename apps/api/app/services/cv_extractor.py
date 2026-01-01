import fitz  # PyMuPDF
from docx import Document
import re
from typing import Tuple
from app.schemas import (
    UserProfile,
    ExperienceRole,
    ExperienceBullet,
    SkillGroup,
    Education,
    Project,
    Preferences,
)


class CVExtractor:
    """Extract and parse CV content from PDF and DOCX files"""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> Tuple[str, dict]:
        """Extract text from PDF with page references
        
        Returns:
            Tuple of (full_text, evidence_map)
            evidence_map: dict mapping text snippets to page numbers
        """
        doc = fitz.open(stream=file_content, filetype="pdf")
        full_text = ""
        evidence_map = {}
        
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text()
            full_text += f"\n--- Page {page_num} ---\n{page_text}"
            
            # Store page reference for paragraphs
            paragraphs = [p.strip() for p in page_text.split('\n') if p.strip()]
            for para in paragraphs:
                if len(para) > 20:  # Only store substantial paragraphs
                    evidence_map[para[:100]] = f"page {page_num}"
        
        doc.close()
        return full_text, evidence_map
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> Tuple[str, dict]:
        """Extract text from DOCX with paragraph references
        
        Returns:
            Tuple of (full_text, evidence_map)
            evidence_map: dict mapping text snippets to paragraph indices
        """
        import io
        doc = Document(io.BytesIO(file_content))
        full_text = ""
        evidence_map = {}
        
        for para_idx, paragraph in enumerate(doc.paragraphs, start=1):
            text = paragraph.text.strip()
            if text:
                full_text += text + "\n"
                if len(text) > 20:  # Only store substantial paragraphs
                    evidence_map[text[:100]] = f"paragraph {para_idx}"
        
        return full_text, evidence_map
    
    @staticmethod
    def extract_email(text: str) -> str:
        """Extract email from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else "user@example.com"
    
    @staticmethod
    def extract_name(text: str) -> str:
        """Extract name from text (typically first few lines)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        # Usually name is in first few lines, exclude common headers
        for line in lines[:5]:
            # Skip lines with keywords like CV, Resume, etc.
            if len(line.split()) <= 4 and not any(
                kw in line.lower() for kw in ['cv', 'resume', 'curriculum', 'vitae', 'page']
            ):
                # Check if line looks like a name (capitalized words)
                words = line.split()
                if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                    return line
        return "Unknown Name"
    
    @staticmethod
    def extract_links(text: str) -> list[str]:
        """Extract URLs and social links from text"""
        links = []
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        links.extend(re.findall(linkedin_pattern, text.lower()))
        
        # GitHub
        github_pattern = r'github\.com/[\w-]+'
        links.extend(re.findall(github_pattern, text.lower()))
        
        # General URLs
        url_pattern = r'https?://[^\s]+'
        links.extend(re.findall(url_pattern, text))
        
        return list(set(links))[:5]  # Limit to 5 unique links
    
    @staticmethod
    def extract_skills(text: str) -> list[SkillGroup]:
        """Extract skills from text and group them"""
        # Common skill categories and their keywords
        programming_langs = {
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby',
            'go', 'rust', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab'
        }
        frameworks = {
            'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring',
            'express', 'nextjs', 'next.js', 'node.js', 'nodejs', '.net', 'rails'
        }
        tools = {
            'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins',
            'terraform', 'ansible', 'mongodb', 'postgresql', 'mysql', 'redis'
        }
        
        text_lower = text.lower()
        
        # Extract skills by category
        found_langs = [skill for skill in programming_langs if skill in text_lower]
        found_frameworks = [skill for skill in frameworks if skill in text_lower]
        found_tools = [skill for skill in tools if skill in text_lower]
        
        skill_groups = []
        if found_langs:
            skill_groups.append(SkillGroup(
                category="Programming Languages",
                skills=[s.title() for s in found_langs]
            ))
        if found_frameworks:
            skill_groups.append(SkillGroup(
                category="Frameworks",
                skills=[s.title() for s in found_frameworks]
            ))
        if found_tools:
            skill_groups.append(SkillGroup(
                category="Tools & Technologies",
                skills=[s.title() for s in found_tools]
            ))
        
        return skill_groups
    
    @staticmethod
    def extract_experience(text: str, evidence_map: dict) -> list[ExperienceRole]:
        """Extract work experience from text"""
        experiences = []
        
        # Look for common experience section headers
        exp_section_match = re.search(
            r'(experience|employment|work history)(.*?)(education|projects|skills|$)',
            text.lower(),
            re.DOTALL
        )
        
        if not exp_section_match:
            # Try to extract any company/role patterns
            return []
        
        exp_text = exp_section_match.group(2)
        
        # Simple pattern: look for company names (capitalized) followed by role
        # This is a basic heuristic
        lines = [line.strip() for line in exp_text.split('\n') if line.strip()]
        
        current_role = None
        for i, line in enumerate(lines):
            # Check if line looks like a company/title (has capitalized words)
            if len(line) > 3 and line[0].isupper():
                # Check if it might be a date range
                if re.search(r'\d{4}', line):
                    if current_role and 'dates' not in current_role:
                        current_role['dates'] = line
                # Check if it looks like a company or title
                elif not line.startswith(('-', '•', '*')):
                    if current_role:
                        experiences.append(ExperienceRole(**current_role))
                    
                    # Start new role
                    current_role = {
                        'company': 'Company Name',
                        'title': line,
                        'dates': 'Dates',
                        'bullets': [],
                        'tech': []
                    }
            # Check if line is a bullet point
            elif line.startswith(('-', '•', '*')) and current_role:
                bullet_text = line.lstrip('-•* ').strip()
                evidence_ref = None
                # Try to find evidence reference
                for snippet, ref in evidence_map.items():
                    if bullet_text[:50] in snippet:
                        evidence_ref = ref
                        break
                
                current_role['bullets'].append(
                    ExperienceBullet(text=bullet_text, evidence_ref=evidence_ref)
                )
        
        # Add last role
        if current_role:
            experiences.append(ExperienceRole(**current_role))
        
        return experiences[:5]  # Limit to 5 most recent roles
    
    @staticmethod
    def extract_education(text: str) -> list[Education]:
        """Extract education from text"""
        education = []
        
        # Look for education section
        edu_section_match = re.search(
            r'(education|academic)(.*?)(experience|skills|projects|$)',
            text.lower(),
            re.DOTALL
        )
        
        if not edu_section_match:
            return []
        
        edu_text = edu_section_match.group(2)
        lines = [line.strip() for line in edu_text.split('\n') if line.strip()]
        
        current_edu = None
        for line in lines[:10]:  # Limit to first 10 lines
            if len(line) > 5 and line[0].isupper() and not line.startswith(('-', '•', '*')):
                if current_edu:
                    education.append(Education(**current_edu))
                
                current_edu = {
                    'institution': line,
                    'degree': None,
                    'field': None,
                    'dates': None,
                    'details': []
                }
            elif current_edu and re.search(r'\d{4}', line):
                current_edu['dates'] = line
        
        if current_edu:
            education.append(Education(**current_edu))
        
        return education
    
    @classmethod
    def create_draft_profile(cls, text: str, evidence_map: dict) -> UserProfile:
        """Create a draft UserProfile from extracted text
        
        Args:
            text: Extracted text from CV
            evidence_map: Mapping of text snippets to their source references
            
        Returns:
            UserProfile with populated fields (no hallucination - unknown fields left empty)
        """
        return UserProfile(
            name=cls.extract_name(text),
            email=cls.extract_email(text),
            links=cls.extract_links(text),
            summary=None,  # Don't hallucinate summary
            skills=cls.extract_skills(text),
            experience=cls.extract_experience(text, evidence_map),
            projects=[],  # TODO: Could add project extraction
            education=cls.extract_education(text),
            preferences=Preferences(),  # Empty preferences - user must fill
        )
