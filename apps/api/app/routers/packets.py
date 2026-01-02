"""Packets router for CV generation and application materials"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional
from pathlib import Path

from app.schemas.packet import (
    GeneratePacketRequest,
    PacketResponse,
    PacketListResponse,
    Packet,
    PacketInDB,
    TailoringPlan,
)
from app.schemas.profile import UserProfile
from app.schemas.job import JobPosting
from app.models.database import get_profiles_collection, get_jobs_collection
from app.services.tailoring import TailoringService
from app.services.packet_storage import PacketStorageService
from bson import ObjectId


router = APIRouter(prefix="/packets", tags=["packets"])

tailoring_service = TailoringService()
storage_service = PacketStorageService()


async def get_user_profile() -> UserProfile:
    """Get the user's profile (simplified - assumes single user)"""
    collection = get_profiles_collection()
    profile_data = await collection.find_one({})
    
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found. Please create a profile first.")
    
    profile_data["_id"] = str(profile_data["_id"])
    return UserProfile(**profile_data)


async def get_job_by_id(job_id: str) -> JobPosting:
    """Get job posting by ID"""
    collection = get_jobs_collection()
    
    try:
        job_data = await collection.find_one({"_id": ObjectId(job_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data["_id"] = str(job_data["_id"])
    return JobPosting(**job_data)


@router.post("/generate", response_model=PacketResponse)
async def generate_packet(request: GeneratePacketRequest):
    """
    Generate a tailored application packet for a job.
    
    Creates:
    - Tailored CV (.tex and .pdf if compilation available)
    - Recruiter message
    - Common answers
    - Cover letter (if requested)
    """
    # Get profile and job
    profile = await get_user_profile()
    job = await get_job_by_id(request.job_id)
    
    # Generate tailoring plan
    plan = tailoring_service.generate_tailoring_plan(
        profile=profile,
        job=job,
        user_emphasis=request.user_emphasis
    )
    plan.profile_id = "profile"  # Simplified
    
    # Generate packet ID (will be replaced after DB insert)
    from datetime import datetime
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
    
    # Generate recruiter message
    recruiter_msg = tailoring_service.generate_recruiter_message(profile, job, plan)
    recruiter_file = storage_service.save_file(
        packet_id=temp_id,
        filename="recruiter_message.txt",
        content=recruiter_msg,
        file_type="txt"
    )
    
    # Generate common answers
    answers = tailoring_service.generate_common_answers(profile, job)
    answers_file = storage_service.save_file(
        packet_id=temp_id,
        filename="common_answers.md",
        content=answers,
        file_type="md"
    )
    
    # Generate cover letter if requested
    cover_letter_file = None
    if request.include_cover_letter:
        cover_letter = tailoring_service.generate_cover_letter(profile, job, plan)
        cover_letter_file = storage_service.save_file(
            packet_id=temp_id,
            filename="cover_letter.txt",
            content=cover_letter,
            file_type="txt"
        )
    
    # Create packet
    packet = Packet(
        job_id=request.job_id,
        profile_id="profile",
        tailoring_plan=plan,
        cv_tex=cv_tex,
        cv_pdf=cv_pdf,
        cover_letter=cover_letter_file,
        recruiter_message=recruiter_file,
        common_answers=answers_file
    )
    
    # Save to database
    packet_in_db = await storage_service.save_packet(packet)
    
    # Rename temp directory to actual packet ID
    import shutil
    temp_dir = storage_service._get_packet_dir(temp_id)
    actual_dir = storage_service._get_packet_dir(packet_in_db.id)
    
    if temp_dir.exists() and temp_dir != actual_dir:
        shutil.move(str(temp_dir), str(actual_dir))
        
        # Update file paths in packet
        packet_in_db.cv_tex.filepath = packet_in_db.cv_tex.filepath.replace(temp_id, packet_in_db.id)
        if packet_in_db.cv_pdf:
            packet_in_db.cv_pdf.filepath = packet_in_db.cv_pdf.filepath.replace(temp_id, packet_in_db.id)
        if packet_in_db.cover_letter:
            packet_in_db.cover_letter.filepath = packet_in_db.cover_letter.filepath.replace(temp_id, packet_in_db.id)
        packet_in_db.recruiter_message.filepath = packet_in_db.recruiter_message.filepath.replace(temp_id, packet_in_db.id)
        packet_in_db.common_answers.filepath = packet_in_db.common_answers.filepath.replace(temp_id, packet_in_db.id)
        
        # Update in database
        await storage_service.update_packet(
            packet_in_db.id,
            {
                "cv_tex": packet_in_db.cv_tex.model_dump(),
                "cv_pdf": packet_in_db.cv_pdf.model_dump() if packet_in_db.cv_pdf else None,
                "cover_letter": packet_in_db.cover_letter.model_dump() if packet_in_db.cover_letter else None,
                "recruiter_message": packet_in_db.recruiter_message.model_dump(),
                "common_answers": packet_in_db.common_answers.model_dump(),
            }
        )
    
    return PacketResponse(
        packet=packet_in_db,
        message=f"Packet generated successfully. PDF compilation: {'successful' if cv_pdf else 'not available (install latexmk)'}"
    )


@router.get("/{packet_id}", response_model=PacketResponse)
async def get_packet(packet_id: str):
    """Get packet details by ID"""
    packet = await storage_service.get_packet(packet_id)
    
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    return PacketResponse(packet=packet)


@router.get("", response_model=PacketListResponse)
async def list_packets(
    profile_id: Optional[str] = Query(None, description="Filter by profile ID"),
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100)
):
    """List all packets with optional filtering"""
    skip = (page - 1) * per_page
    
    packets, total = await storage_service.list_packets(
        profile_id=profile_id,
        job_id=job_id,
        skip=skip,
        limit=per_page
    )
    
    return PacketListResponse(
        packets=packets,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{packet_id}/download/{file_type}")
async def download_file(packet_id: str, file_type: str):
    """
    Download a file from the packet.
    
    file_type: tex, pdf, cover_letter, recruiter_message, common_answers
    """
    packet = await storage_service.get_packet(packet_id)
    
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    # Map file type to packet file
    file_map = {
        "tex": packet.cv_tex,
        "pdf": packet.cv_pdf,
        "cover_letter": packet.cover_letter,
        "recruiter_message": packet.recruiter_message,
        "common_answers": packet.common_answers,
    }
    
    packet_file = file_map.get(file_type)
    
    if not packet_file:
        raise HTTPException(status_code=404, detail=f"File type '{file_type}' not available for this packet")
    
    file_path = storage_service.get_file_path(packet_file)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=packet_file.filename,
        media_type="application/octet-stream"
    )
