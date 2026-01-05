"""
Background job management service
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from bson import ObjectId

from app.schemas.job_queue import (
    BackgroundJob,
    BackgroundJobInDB,
    JobType,
    JobStatus,
)
from app.models.database import get_background_jobs_collection

logger = logging.getLogger(__name__)


class JobService:
    """Service for managing background jobs"""
    
    # Job lock duration in seconds (5 minutes)
    LOCK_DURATION = 300
    
    async def create_job(
        self,
        job_type: JobType,
        params: Dict[str, Any] = None,
        user_id: Optional[str] = None,
    ) -> BackgroundJobInDB:
        """Create a new background job"""
        collection = get_background_jobs_collection()
        
        job = BackgroundJob(
            type=job_type,
            status=JobStatus.QUEUED,
            params=params or {},
            user_id=user_id,
        )
        
        job_dict = job.model_dump(by_alias=True, exclude={"id"})
        result = await collection.insert_one(job_dict)
        
        job_dict["_id"] = str(result.inserted_id)
        return BackgroundJobInDB(**job_dict)
    
    async def get_job(self, job_id: str) -> Optional[BackgroundJobInDB]:
        """Get a job by ID"""
        collection = get_background_jobs_collection()
        
        try:
            job_data = await collection.find_one({"_id": ObjectId(job_id)})
        except Exception:
            return None
        
        if not job_data:
            return None
        
        job_data["_id"] = str(job_data["_id"])
        return BackgroundJobInDB(**job_data)
    
    async def list_jobs(
        self,
        user_id: Optional[str] = None,
        job_type: Optional[JobType] = None,
        status: Optional[JobStatus] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[BackgroundJobInDB], int]:
        """List jobs with optional filters"""
        collection = get_background_jobs_collection()
        
        query = {}
        if user_id:
            query["user_id"] = user_id
        if job_type:
            query["type"] = job_type
        if status:
            query["status"] = status
        
        total = await collection.count_documents(query)
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        
        jobs = []
        async for job_data in cursor:
            job_data["_id"] = str(job_data["_id"])
            jobs.append(BackgroundJobInDB(**job_data))
        
        return jobs, total
    
    async def acquire_job(self, worker_id: str) -> Optional[BackgroundJobInDB]:
        """
        Atomically acquire a queued job for processing.
        
        This uses MongoDB's findOneAndUpdate with a filter to ensure
        only one worker can acquire the job.
        """
        collection = get_background_jobs_collection()
        
        now = datetime.utcnow()
        lock_expires = now + timedelta(seconds=self.LOCK_DURATION)
        
        # Find a queued job or a job whose lock has expired
        result = await collection.find_one_and_update(
            {
                "$or": [
                    {"status": JobStatus.QUEUED},
                    {
                        "status": JobStatus.RUNNING,
                        "lock_expires_at": {"$lt": now}
                    }
                ]
            },
            {
                "$set": {
                    "status": JobStatus.RUNNING,
                    "worker_id": worker_id,
                    "lock_expires_at": lock_expires,
                    "started_at": now,
                }
            },
            sort=[("created_at", 1)],  # FIFO
            return_document=True,
        )
        
        if not result:
            return None
        
        result["_id"] = str(result["_id"])
        return BackgroundJobInDB(**result)
    
    async def update_progress(
        self,
        job_id: str,
        progress: int,
        message: Optional[str] = None,
    ) -> Optional[BackgroundJobInDB]:
        """Update job progress"""
        collection = get_background_jobs_collection()
        
        update_data = {
            "progress": progress,
        }
        if message is not None:
            update_data["message"] = message
        
        try:
            result = await collection.find_one_and_update(
                {"_id": ObjectId(job_id)},
                {"$set": update_data},
                return_document=True,
            )
        except Exception:
            return None
        
        if not result:
            return None
        
        result["_id"] = str(result["_id"])
        return BackgroundJobInDB(**result)
    
    async def complete_job(
        self,
        job_id: str,
        result: Optional[Dict[str, Any]] = None,
        resource_refs: Optional[Dict[str, Any]] = None,
    ) -> Optional[BackgroundJobInDB]:
        """Mark job as succeeded"""
        collection = get_background_jobs_collection()
        
        update_data = {
            "status": JobStatus.SUCCEEDED,
            "progress": 100,
            "finished_at": datetime.utcnow(),
            "worker_id": None,
            "lock_expires_at": None,
        }
        
        if result is not None:
            update_data["result"] = result
        if resource_refs is not None:
            update_data["resource_refs"] = resource_refs
        
        try:
            result_doc = await collection.find_one_and_update(
                {"_id": ObjectId(job_id)},
                {"$set": update_data},
                return_document=True,
            )
        except Exception:
            return None
        
        if not result_doc:
            return None
        
        result_doc["_id"] = str(result_doc["_id"])
        return BackgroundJobInDB(**result_doc)
    
    async def fail_job(
        self,
        job_id: str,
        error: str,
    ) -> Optional[BackgroundJobInDB]:
        """Mark job as failed"""
        collection = get_background_jobs_collection()
        
        try:
            result = await collection.find_one_and_update(
                {"_id": ObjectId(job_id)},
                {
                    "$set": {
                        "status": JobStatus.FAILED,
                        "error": error,
                        "finished_at": datetime.utcnow(),
                        "worker_id": None,
                        "lock_expires_at": None,
                    }
                },
                return_document=True,
            )
        except Exception:
            return None
        
        if not result:
            return None
        
        result["_id"] = str(result["_id"])
        return BackgroundJobInDB(**result)
    
    async def renew_lock(
        self,
        job_id: str,
        worker_id: str,
    ) -> Optional[BackgroundJobInDB]:
        """Renew job lock to prevent expiration"""
        collection = get_background_jobs_collection()
        
        now = datetime.utcnow()
        lock_expires = now + timedelta(seconds=self.LOCK_DURATION)
        
        try:
            result = await collection.find_one_and_update(
                {
                    "_id": ObjectId(job_id),
                    "worker_id": worker_id,
                    "status": JobStatus.RUNNING,
                },
                {
                    "$set": {
                        "lock_expires_at": lock_expires,
                    }
                },
                return_document=True,
            )
        except Exception:
            return None
        
        if not result:
            return None
        
        result["_id"] = str(result["_id"])
        return BackgroundJobInDB(**result)
