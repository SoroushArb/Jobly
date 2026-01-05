"""Packet generation handler"""
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

from app.schemas.job_queue import BackgroundJobInDB
from app.services.job_service import JobService
from app.services.sse_service import SSEService
from app.schemas.sse import SSEEvent, EventType
from app.services.tailoring import TailoringService
from app.services.packet_storage import PacketStorageService
from app.models.database import get_profiles_collection, get_jobs_collection
from app.schemas.profile import UserProfile
from app.schemas.job import JobPosting
from bson import ObjectId
from datetime import datetime

logger = logging.getLogger(__name__)


async def handle_packet_generation(
    job: BackgroundJobInDB,
    job_service: JobService,
    sse_service: SSEService
) -> dict:
    """
    Handle packet generation background job.
    
    Generates a tailored application packet for a job.
    """
    logger.info(f"Starting packet generation for job {job.id}")
    
    job_id = job.params.get("job_id")
    user_emphasis = job.params.get("user_emphasis")
    
    if not job_id:
        raise ValueError("job_id is required in job params")
    
    # Update progress
    await job_service.update_progress(job.id, 10, "Loading profile and job data...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 10,
            "message": "Loading profile and job data..."
        },
        user_id=job.user_id
    ))
    
    # Get profile and job
    profiles_collection = get_profiles_collection()
    profile_data = await profiles_collection.find_one({})
    if not profile_data:
        raise ValueError("No profile found")
    
    profile_data["_id"] = str(profile_data["_id"])
    profile = UserProfile(**profile_data)
    
    jobs_collection = get_jobs_collection()
    job_data = await jobs_collection.find_one({"_id": ObjectId(job_id)})
    if not job_data:
        raise ValueError(f"Job {job_id} not found")
    
    job_data["_id"] = str(job_data["_id"])
    job_posting = JobPosting(**job_data)
    
    # Update progress
    await job_service.update_progress(job.id, 30, "Generating tailoring plan...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 30,
            "message": "Generating tailoring plan..."
        },
        user_id=job.user_id
    ))
    
    # Generate tailoring plan
    tailoring_service = TailoringService()
    storage_service = PacketStorageService()
    
    plan = tailoring_service.generate_tailoring_plan(
        profile=profile,
        job=job_posting,
        user_emphasis=user_emphasis
    )
    plan.profile_id = "profile"  # Simplified
    
    # Update progress
    await job_service.update_progress(job.id, 50, "Rendering LaTeX CV...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 50,
            "message": "Rendering LaTeX CV..."
        },
        user_id=job.user_id
    ))
    
    # Generate packet ID
    temp_id = f"temp_{int(datetime.utcnow().timestamp())}"
    
    # Render LaTeX CV
    latex_content = tailoring_service.render_latex_cv(profile, plan)
    
    # Save .tex file
    cv_tex = storage_service.save_file(
        packet_id=temp_id,
        filename="cv.tex",
        content=latex_content,
        file_type="tex"
    )
    
    # Update progress
    await job_service.update_progress(job.id, 70, "Compiling PDF...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 70,
            "message": "Compiling PDF..."
        },
        user_id=job.user_id
    ))
    
    # Try to compile to PDF
    cv_pdf = None
    packet_dir = storage_service._get_packet_dir(temp_id)
    pdf_path = tailoring_service.compile_latex(latex_content, packet_dir)
    
    if pdf_path and pdf_path.exists():
        cv_pdf = storage_service.save_binary_file(
            packet_id=temp_id,
            filename="cv.pdf",
            source_path=pdf_path,
            file_type="pdf"
        )
    
    # Generate other materials
    await job_service.update_progress(job.id, 85, "Generating application materials...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 85,
            "message": "Generating application materials..."
        },
        user_id=job.user_id
    ))
    
    recruiter_message = tailoring_service.generate_recruiter_message(profile, job_posting, plan)
    common_answers = tailoring_service.generate_common_answers(profile, job_posting, plan)
    
    recruiter_file = storage_service.save_file(
        packet_id=temp_id,
        filename="recruiter_message.txt",
        content=recruiter_message,
        file_type="txt"
    )
    
    answers_file = storage_service.save_file(
        packet_id=temp_id,
        filename="common_answers.txt",
        content=common_answers,
        file_type="txt"
    )
    
    # Build packet
    from app.schemas.packet import Packet
    packet = Packet(
        profile_id="profile",
        job_id=job_id,
        job_title=job_posting.title,
        company_name=job_posting.company,
        tailoring_plan=plan,
        cv_tex=cv_tex,
        cv_pdf=cv_pdf,
        recruiter_message=recruiter_file,
        common_answers=answers_file,
        created_at=datetime.utcnow()
    )
    
    # Save to database
    packet_in_db = await storage_service.save_packet(packet)
    
    logger.info(f"Packet generation completed: {packet_in_db.id}")
    
    return {
        "result": {"packet_id": packet_in_db.id},
        "resource_refs": {"packet_id": packet_in_db.id},
        "message": f"Packet {packet_in_db.id} generated successfully"
    }
