"""
Job ingestion service - orchestrates fetching from sources and storing in MongoDB
"""

from typing import List, Dict, Any
import yaml
import asyncio
from pathlib import Path
from datetime import datetime

from app.services.sources import Source, RSSSource, CompanySource
from app.schemas import JobPosting, JobPostingInDB
from app.models.database import Database


class JobIngestionService:
    """Service for ingesting jobs from configured sources"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize job ingestion service
        
        Args:
            config_path: Path to job_sources_config.yaml
        """
        if config_path is None:
            # Default to config in api directory
            api_dir = Path(__file__).parent.parent.parent
            config_path = api_dir / "job_sources_config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.sources = self._initialize_sources()
        self.last_fetch_times = {}  # Track last fetch time per source for rate limiting
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config from {self.config_path}: {e}")
            return {"sources": [], "settings": {}}
    
    def _initialize_sources(self) -> List[Source]:
        """Initialize source objects from config"""
        sources = []
        settings = self.config.get("settings", {})
        
        for source_config in self.config.get("sources", []):
            # Skip disabled sources
            if not source_config.get("enabled", True):
                continue
            
            # Add global settings to source config
            source_config["user_agent"] = settings.get("user_agent", "Jobly/1.0")
            
            # Create appropriate source type
            source_type = source_config.get("type", "")
            
            try:
                if source_type == "rss":
                    source = RSSSource(source_config)
                elif source_type == "company":
                    source = CompanySource(source_config)
                else:
                    print(f"Unknown source type: {source_type}")
                    continue
                
                sources.append(source)
            except Exception as e:
                print(f"Error initializing source {source_config.get('name')}: {e}")
                continue
        
        return sources
    
    async def ingest_all(self) -> Dict[str, Any]:
        """
        Ingest jobs from all enabled sources
        
        Returns:
            Dict with ingestion statistics
        """
        total_fetched = 0
        total_new = 0
        total_updated = 0
        sources_processed = []
        
        for source in self.sources:
            try:
                # Respect rate limiting
                await self._check_rate_limit(source)
                
                print(f"Fetching jobs from {source.name}...")
                
                # Fetch raw jobs
                raw_jobs = await source.fetch()
                total_fetched += len(raw_jobs)
                
                # Parse and store jobs
                new_count, updated_count = await self._process_jobs(source, raw_jobs)
                total_new += new_count
                total_updated += updated_count
                
                sources_processed.append(source.name)
                
                # Update last fetch time
                self.last_fetch_times[source.name] = datetime.utcnow()
                
                print(f"✓ {source.name}: {len(raw_jobs)} fetched, {new_count} new, {updated_count} updated")
                
            except Exception as e:
                print(f"Error ingesting from {source.name}: {e}")
                continue
        
        return {
            "jobs_fetched": total_fetched,
            "jobs_new": total_new,
            "jobs_updated": total_updated,
            "sources_processed": sources_processed
        }
    
    async def _check_rate_limit(self, source: Source):
        """Check and enforce rate limiting for a source"""
        if source.name not in self.last_fetch_times:
            return
        
        last_fetch = self.last_fetch_times[source.name]
        elapsed = (datetime.utcnow() - last_fetch).total_seconds()
        
        if elapsed < source.rate_limit_seconds:
            wait_time = source.rate_limit_seconds - elapsed
            print(f"Rate limiting {source.name}: waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
    
    async def _process_jobs(self, source: Source, raw_jobs: List) -> tuple[int, int]:
        """
        Parse raw jobs and store in database with deduplication
        
        Returns:
            Tuple of (new_count, updated_count)
        """
        new_count = 0
        updated_count = 0
        
        db = Database.get_database()
        jobs_collection = db["jobs"]
        
        for raw_job in raw_jobs:
            try:
                # Parse into JobPosting
                job_posting = source.parse(raw_job)
                
                # Check if job already exists by dedupe_hash
                existing = await jobs_collection.find_one({"dedupe_hash": job_posting.dedupe_hash})
                
                if existing:
                    # Update last_seen
                    await jobs_collection.update_one(
                        {"dedupe_hash": job_posting.dedupe_hash},
                        {"$set": {"last_seen": datetime.utcnow()}}
                    )
                    updated_count += 1
                else:
                    # Insert new job
                    job_dict = job_posting.model_dump()
                    await jobs_collection.insert_one(job_dict)
                    new_count += 1
                    
            except Exception as e:
                print(f"Error processing job from {source.name}: {e}")
                continue
        
        return new_count, updated_count
    
    def get_sources_info(self) -> List[Dict[str, Any]]:
        """Get information about configured sources"""
        return [
            {
                "name": source.name,
                "type": source.source_type,
                "url": source.url,
                "enabled": source.is_enabled(),
                "compliance_note": source.compliance_note
            }
            for source in self.sources
        ]
