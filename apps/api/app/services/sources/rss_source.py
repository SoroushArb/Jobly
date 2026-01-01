"""
RSS source implementation for job ingestion.

Uses feedparser to parse RSS/Atom feeds from job boards.
Chosen over BeautifulSoup for RSS parsing as feedparser is purpose-built for feeds.
"""

from typing import List, Dict, Any
import httpx
import feedparser
from datetime import datetime
from .base import Source, RawJob
from app.schemas import JobPosting


class RSSSource(Source):
    """Generic RSS/Atom feed source for job postings"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.user_agent = config.get("user_agent", "Jobly/1.0 (Job Aggregator)")
    
    async def fetch(self) -> List[RawJob]:
        """
        Fetch jobs from RSS feed
        
        Returns:
            List of RawJob objects parsed from RSS entries
        """
        raw_jobs = []
        
        try:
            # Fetch RSS feed with httpx
            async with httpx.AsyncClient() as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(
                    self.url,
                    headers=headers,
                    timeout=30.0,
                    follow_redirects=True
                )
                response.raise_for_status()
                
            # Parse RSS feed
            feed = feedparser.parse(response.text)
            
            # Extract job entries
            for entry in feed.entries:
                try:
                    raw_job = self._parse_entry(entry)
                    raw_jobs.append(raw_job)
                except Exception as e:
                    # Log error but continue with other entries
                    print(f"Error parsing RSS entry from {self.name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching RSS feed from {self.name}: {e}")
            raise
        
        return raw_jobs
    
    def _parse_entry(self, entry) -> RawJob:
        """Parse a single RSS entry into RawJob"""
        # Extract basic fields
        title = entry.get("title", "").strip()
        url = entry.get("link", "").strip()
        
        # Description from summary or content
        description = ""
        if hasattr(entry, "summary"):
            description = entry.summary
        elif hasattr(entry, "content"):
            description = entry.content[0].value if entry.content else ""
        
        # Try to extract company name (varies by feed)
        company = "Unknown"
        if hasattr(entry, "author"):
            company = entry.author
        elif hasattr(entry, "dc_creator"):
            company = entry.dc_creator
        
        # Try to parse published date
        posted_date = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                posted_date = datetime(*entry.published_parsed[:6]).isoformat()
            except:
                pass
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            try:
                posted_date = datetime(*entry.updated_parsed[:6]).isoformat()
            except:
                pass
        
        # Try to extract location from tags or category
        location = None
        if hasattr(entry, "tags"):
            for tag in entry.tags:
                # Common location tag patterns
                if "location" in tag.get("term", "").lower():
                    location = tag.get("term", "")
                    break
        
        return RawJob(
            title=title,
            url=url,
            company=company,
            location=location,
            description=description,
            posted_date=posted_date,
            raw_data=dict(entry)
        )
    
    def parse(self, raw_job: RawJob) -> JobPosting:
        """
        Parse RawJob into JobPosting schema
        
        Args:
            raw_job: RawJob from RSS feed
            
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
            elif "on-site" in location_lower or "onsite" in location_lower:
                remote_type = "onsite"
            
            # Try to extract country/city (simple heuristic)
            # Format often: "City, Country" or just "Country"
            parts = [p.strip() for p in raw_job.location.split(",")]
            if len(parts) >= 2:
                city = parts[0]
                country = parts[1]
            elif len(parts) == 1:
                country = parts[0]
        
        # Parse posted_date
        posted_date = None
        if raw_job.posted_date:
            try:
                posted_date = datetime.fromisoformat(raw_job.posted_date.replace("Z", "+00:00"))
            except:
                pass
        
        # Clean description (remove HTML tags if present)
        description_clean = self._clean_html(raw_job.description) if raw_job.description else None
        
        return JobPosting(
            company=raw_job.company,
            title=raw_job.title,
            url=raw_job.url,
            location=raw_job.location,
            country=country,
            city=city,
            remote_type=remote_type,
            description_raw=raw_job.description,
            description_clean=description_clean,
            posted_date=posted_date,
            source_name=self.name,
            source_type=self.source_type,
            source_compliance_note=self.compliance_note
        )
    
    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags from text"""
        # Simple HTML cleaning - remove tags
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html_text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
