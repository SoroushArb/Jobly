"""
Company careers page source implementation using selectolax for HTML parsing.

Selectolax chosen over BeautifulSoup for:
- Performance: 5-25x faster than BeautifulSoup
- Memory efficiency: Lower memory footprint
- Simple API: Easy CSS selector support
- Good enough for our needs: We only need basic HTML parsing

Reference: https://github.com/rushter/selectolax
"""

from typing import List, Dict, Any, Optional
import httpx
from selectolax.parser import HTMLParser
from datetime import datetime
from .base import Source, RawJob
from app.schemas import JobPosting


class CompanySource(Source):
    """Company careers page source with template-based HTML parsing"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.user_agent = config.get("user_agent", "Jobly/1.0 (Job Aggregator)")
        self.parser_config = config.get("parser_config", {})
        
        # CSS selectors from config
        self.job_list_selector = self.parser_config.get("job_list_selector", ".job-listing")
        self.title_selector = self.parser_config.get("title_selector", ".job-title")
        self.location_selector = self.parser_config.get("location_selector", ".job-location")
        self.link_selector = self.parser_config.get("link_selector", "a")
        self.description_selector = self.parser_config.get("description_selector", ".job-description")
    
    async def fetch(self) -> List[RawJob]:
        """
        Fetch jobs from company careers page by parsing HTML
        
        Returns:
            List of RawJob objects parsed from HTML
        """
        raw_jobs = []
        
        try:
            # Fetch HTML page
            async with httpx.AsyncClient() as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(
                    self.url,
                    headers=headers,
                    timeout=30.0,
                    follow_redirects=True
                )
                response.raise_for_status()
            
            # Parse HTML with selectolax
            parser = HTMLParser(response.text)
            
            # Find all job listings
            job_elements = parser.css(self.job_list_selector)
            
            # Extract each job
            for job_elem in job_elements:
                try:
                    raw_job = self._parse_job_element(job_elem)
                    if raw_job:
                        raw_jobs.append(raw_job)
                except Exception as e:
                    # Log error but continue with other jobs
                    print(f"Error parsing job element from {self.name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching company page from {self.name}: {e}")
            raise
        
        return raw_jobs
    
    def _parse_job_element(self, element) -> Optional[RawJob]:
        """Parse a single job HTML element into RawJob"""
        # Extract title
        title_elem = element.css_first(self.title_selector)
        title = title_elem.text(strip=True) if title_elem else None
        
        if not title:
            return None
        
        # Extract URL
        link_elem = element.css_first(self.link_selector)
        url = ""
        if link_elem:
            url = link_elem.attributes.get("href", "")
            # Make absolute URL if relative
            if url and not url.startswith("http"):
                from urllib.parse import urljoin
                url = urljoin(self.url, url)
        
        if not url:
            return None
        
        # Extract location
        location_elem = element.css_first(self.location_selector)
        location = location_elem.text(strip=True) if location_elem else None
        
        # Extract description if available
        description_elem = element.css_first(self.description_selector)
        description = description_elem.text(strip=True) if description_elem else None
        
        # Company name from source config
        company = self.name.replace(" Careers", "").strip()
        
        return RawJob(
            title=title,
            url=url,
            company=company,
            location=location,
            description=description,
            posted_date=None,  # Usually not available in listing pages
            raw_data={"html": element.html}
        )
    
    def parse(self, raw_job: RawJob) -> JobPosting:
        """
        Parse RawJob into JobPosting schema
        
        Args:
            raw_job: RawJob from HTML parsing
            
        Returns:
            JobPosting with normalized fields
        """
        # Parse location into country/city if possible
        country = None
        city = None
        remote_type = "unknown"
        
        if raw_job.location:
            location_lower = raw_job.location.lower()
            # Basic remote detection
            if "remote" in location_lower:
                remote_type = "remote"
            elif "hybrid" in location_lower:
                remote_type = "hybrid"
            elif "on-site" in location_lower or "onsite" in location_lower or "office" in location_lower:
                remote_type = "onsite"
            
            # Try to extract country/city (simple heuristic)
            parts = [p.strip() for p in raw_job.location.split(",")]
            if len(parts) >= 2:
                city = parts[0]
                country = parts[1]
            elif len(parts) == 1 and remote_type != "remote":
                # Single location could be city or country
                location_str = parts[0]
                # Common countries
                countries = ["USA", "UK", "Canada", "Germany", "France", "Netherlands", "Spain", "Italy"]
                if any(c.lower() in location_str.lower() for c in countries):
                    country = location_str
                else:
                    city = location_str
        
        return JobPosting(
            company=raw_job.company,
            title=raw_job.title,
            url=raw_job.url,
            location=raw_job.location,
            country=country,
            city=city,
            remote_type=remote_type,
            description_raw=raw_job.description,
            description_clean=raw_job.description,  # Already cleaned in HTML parsing
            posted_date=None,
            source_name=self.name,
            source_type=self.source_type,
            source_compliance_note=self.compliance_note
        )
