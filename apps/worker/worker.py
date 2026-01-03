"""
Background worker for processing jobs
"""
import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Optional

# Add parent directory to path to import from api
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from dotenv import load_dotenv
load_dotenv()

from app.config import config
from app.models.database import Database
from app.services.job_service import JobService
from app.services.sse_service import sse_service
from app.schemas.job_queue import JobType, BackgroundJobInDB
from app.schemas.sse import SSEEvent, EventType

# Import handlers
from handlers.job_ingestion_handler import handle_job_ingestion
from handlers.match_recompute_handler import handle_match_recompute
from handlers.packet_generation_handler import handle_packet_generation
from handlers.interview_generation_handler import handle_interview_generation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(worker_id)s] %(message)s'
)
logger = logging.getLogger(__name__)


class Worker:
    """Background job worker"""
    
    def __init__(self):
        self.worker_id = f"worker-{uuid.uuid4().hex[:8]}"
        self.job_service = JobService()
        self.running = False
        self.current_job: Optional[BackgroundJobInDB] = None
        
        # Map job types to handlers
        self.handlers = {
            JobType.JOB_INGESTION: handle_job_ingestion,
            JobType.MATCH_RECOMPUTE: handle_match_recompute,
            JobType.PACKET_GENERATION: handle_packet_generation,
            JobType.INTERVIEW_GENERATION: handle_interview_generation,
        }
    
    async def start(self):
        """Start the worker"""
        logger.info(f"Worker {self.worker_id} starting...")
        
        # Validate environment
        config.validate_or_exit()
        
        # Initialize database
        Database.get_client()
        logger.info("Database connection initialized")
        
        self.running = True
        logger.info(f"Worker {self.worker_id} started and polling for jobs...")
        
        try:
            while self.running:
                await self.poll_and_execute()
                await asyncio.sleep(2)  # Poll every 2 seconds
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.shutdown()
    
    async def poll_and_execute(self):
        """Poll for a job and execute it"""
        try:
            # Acquire a job
            job = await self.job_service.acquire_job(self.worker_id)
            
            if not job:
                return  # No jobs available
            
            self.current_job = job
            logger.info(f"Acquired job {job.id} of type {job.type}")
            
            # Emit job started event
            await sse_service.emit(SSEEvent(
                event_type=EventType.JOB_PROGRESS,
                data={
                    "job_id": job.id,
                    "type": job.type,
                    "status": "running",
                    "progress": 0,
                    "message": f"Job started"
                },
                user_id=job.user_id
            ))
            
            # Execute the job
            try:
                handler = self.handlers.get(job.type)
                if not handler:
                    raise ValueError(f"No handler for job type {job.type}")
                
                # Execute handler
                result = await handler(job, self.job_service, sse_service)
                
                # Mark job as completed
                await self.job_service.complete_job(
                    job_id=job.id,
                    result=result.get("result"),
                    resource_refs=result.get("resource_refs")
                )
                
                logger.info(f"Job {job.id} completed successfully")
                
                # Emit completion event
                await sse_service.emit(SSEEvent(
                    event_type=EventType.JOB_COMPLETED,
                    data={
                        "job_id": job.id,
                        "type": job.type,
                        "status": "succeeded",
                        "progress": 100,
                        "message": result.get("message", "Job completed"),
                        "result": result.get("result")
                    },
                    user_id=job.user_id
                ))
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Job {job.id} failed: {error_msg}", exc_info=True)
                
                # Mark job as failed
                await self.job_service.fail_job(
                    job_id=job.id,
                    error=error_msg
                )
                
                # Emit failure event
                await sse_service.emit(SSEEvent(
                    event_type=EventType.JOB_FAILED,
                    data={
                        "job_id": job.id,
                        "type": job.type,
                        "status": "failed",
                        "error": error_msg
                    },
                    user_id=job.user_id
                ))
            
            finally:
                self.current_job = None
                
        except Exception as e:
            logger.error(f"Error in poll_and_execute: {e}", exc_info=True)
    
    async def shutdown(self):
        """Shutdown the worker"""
        logger.info(f"Worker {self.worker_id} shutting down...")
        self.running = False
        
        # Close database connection
        await Database.close()
        logger.info("Database connection closed")


async def main():
    """Main entry point"""
    worker = Worker()
    await worker.start()


if __name__ == "__main__":
    # Add worker_id to logging context
    old_factory = logging.getLogRecordFactory()
    
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.worker_id = "worker"
        return record
    
    logging.setLogRecordFactory(record_factory)
    
    asyncio.run(main())
