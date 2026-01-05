"""Tests for job service and background jobs"""
import pytest
from datetime import datetime, timedelta
from app.schemas.job_queue import JobType, JobStatus, BackgroundJob
from app.services.job_service import JobService


@pytest.mark.asyncio
class TestJobService:
    """Test job service functionality"""
    
    async def test_create_job(self):
        """Test creating a new job"""
        service = JobService()
        
        job = await service.create_job(
            job_type=JobType.JOB_INGESTION,
            params={"test": "value"},
            user_id="test_user"
        )
        
        assert job.type == JobType.JOB_INGESTION
        assert job.status == JobStatus.QUEUED
        assert job.params["test"] == "value"
        assert job.user_id == "test_user"
        assert job.progress == 0
        assert job.id is not None
    
    async def test_get_job(self):
        """Test retrieving a job"""
        service = JobService()
        
        # Create a job
        created_job = await service.create_job(
            job_type=JobType.MATCH_RECOMPUTE,
            params={}
        )
        
        # Retrieve it
        retrieved_job = await service.get_job(created_job.id)
        
        assert retrieved_job is not None
        assert retrieved_job.id == created_job.id
        assert retrieved_job.type == JobType.MATCH_RECOMPUTE
    
    async def test_list_jobs(self):
        """Test listing jobs with filters"""
        service = JobService()
        
        # Create multiple jobs
        await service.create_job(job_type=JobType.JOB_INGESTION, params={})
        await service.create_job(job_type=JobType.MATCH_RECOMPUTE, params={})
        await service.create_job(job_type=JobType.JOB_INGESTION, params={})
        
        # List all jobs
        jobs, total = await service.list_jobs()
        assert total >= 3
        
        # List by type
        jobs, total = await service.list_jobs(job_type=JobType.JOB_INGESTION)
        assert total >= 2
        assert all(j.type == JobType.JOB_INGESTION for j in jobs)
    
    async def test_acquire_job_atomic(self):
        """Test that job acquisition is atomic (only one worker gets it)"""
        service = JobService()
        
        # Create a job
        await service.create_job(job_type=JobType.PACKET_GENERATION, params={})
        
        # Two workers try to acquire
        worker1_job = await service.acquire_job("worker1")
        worker2_job = await service.acquire_job("worker2")
        
        # Only one should get a job
        assert worker1_job is not None
        assert worker2_job is None  # No more queued jobs
        assert worker1_job.status == JobStatus.RUNNING
        assert worker1_job.worker_id == "worker1"
    
    async def test_update_progress(self):
        """Test updating job progress"""
        service = JobService()
        
        # Create a job
        job = await service.create_job(job_type=JobType.JOB_INGESTION, params={})
        
        # Update progress
        updated = await service.update_progress(job.id, 50, "Half done")
        
        assert updated is not None
        assert updated.progress == 50
        assert updated.message == "Half done"
    
    async def test_complete_job(self):
        """Test completing a job successfully"""
        service = JobService()
        
        # Create and acquire a job
        job = await service.create_job(job_type=JobType.JOB_INGESTION, params={})
        acquired = await service.acquire_job("worker1")
        
        # Complete it
        completed = await service.complete_job(
            job.id,
            result={"jobs_new": 10},
            resource_refs={"job_id": "some_id"}
        )
        
        assert completed is not None
        assert completed.status == JobStatus.SUCCEEDED
        assert completed.progress == 100
        assert completed.result["jobs_new"] == 10
        assert completed.resource_refs["job_id"] == "some_id"
        assert completed.finished_at is not None
        assert completed.worker_id is None  # Cleared after completion
    
    async def test_fail_job(self):
        """Test failing a job"""
        service = JobService()
        
        # Create and acquire a job
        job = await service.create_job(job_type=JobType.MATCH_RECOMPUTE, params={})
        acquired = await service.acquire_job("worker1")
        
        # Fail it
        failed = await service.fail_job(job.id, "Something went wrong")
        
        assert failed is not None
        assert failed.status == JobStatus.FAILED
        assert failed.error == "Something went wrong"
        assert failed.finished_at is not None
        assert failed.worker_id is None
    
    async def test_job_lock_expiration(self):
        """Test that expired locks can be reacquired"""
        service = JobService()
        
        # Create a job
        job = await service.create_job(job_type=JobType.INTERVIEW_GENERATION, params={})
        
        # Worker 1 acquires it
        acquired1 = await service.acquire_job("worker1")
        assert acquired1 is not None
        assert acquired1.worker_id == "worker1"
        
        # Simulate lock expiration by manually updating the lock_expires_at
        from app.models.database import get_background_jobs_collection
        from bson import ObjectId
        collection = get_background_jobs_collection()
        await collection.update_one(
            {"_id": ObjectId(job.id)},
            {"$set": {"lock_expires_at": datetime.utcnow() - timedelta(seconds=1)}}
        )
        
        # Worker 2 should be able to acquire it now
        acquired2 = await service.acquire_job("worker2")
        assert acquired2 is not None
        assert acquired2.id == job.id
        assert acquired2.worker_id == "worker2"
    
    async def test_renew_lock(self):
        """Test renewing a job lock"""
        service = JobService()
        
        # Create and acquire a job
        job = await service.create_job(job_type=JobType.PACKET_GENERATION, params={})
        acquired = await service.acquire_job("worker1")
        
        original_expiry = acquired.lock_expires_at
        
        # Wait a bit
        import asyncio
        await asyncio.sleep(1)
        
        # Renew lock
        renewed = await service.renew_lock(job.id, "worker1")
        
        assert renewed is not None
        assert renewed.lock_expires_at > original_expiry
