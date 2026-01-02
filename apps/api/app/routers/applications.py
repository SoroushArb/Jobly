"""Applications router for job application tracking"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.schemas.application import (
    Application,
    ApplicationInDB,
    ApplicationStatus,
    CreateApplicationRequest,
    UpdateApplicationStatusRequest,
)
from app.schemas.packet import PacketInDB
from app.schemas.job import JobPosting
from app.models.database import (
    get_applications_collection,
    get_packets_collection,
    get_jobs_collection,
    get_profiles_collection,
)


router = APIRouter(prefix="/applications", tags=["applications"])


async def get_packet_by_id(packet_id: str) -> PacketInDB:
    """Get packet by ID"""
    collection = get_packets_collection()
    
    try:
        packet_data = await collection.find_one({"_id": ObjectId(packet_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid packet ID format")
    
    if not packet_data:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    packet_data["_id"] = str(packet_data["_id"])
    return PacketInDB(**packet_data)


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


async def get_user_profile_id() -> str:
    """Get the user's profile ID (simplified - assumes single user)"""
    collection = get_profiles_collection()
    profile_data = await collection.find_one({})
    
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return str(profile_data["_id"])


@router.post("/create", response_model=ApplicationInDB)
async def create_application(request: CreateApplicationRequest):
    """
    Create an application from a packet.
    
    This creates a tracked application record that can later be used
    for prefilling and status tracking.
    """
    # Validate packet and job exist
    packet = await get_packet_by_id(request.packet_id)
    job = await get_job_by_id(request.job_id)
    profile_id = await get_user_profile_id()
    
    # Check if application already exists
    collection = get_applications_collection()
    existing = await collection.find_one({
        "packet_id": request.packet_id,
        "job_id": request.job_id
    })
    
    if existing:
        existing["_id"] = str(existing["_id"])
        return ApplicationInDB(**existing)
    
    # Create application
    application = Application(
        job_id=request.job_id,
        packet_id=request.packet_id,
        profile_id=profile_id,
        job_title=job.title,
        company_name=job.company,
        job_url=job.url,
        status=ApplicationStatus.PREPARED,
        status_history=[{
            "status": ApplicationStatus.PREPARED.value,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Application created"
        }],
        notes=request.notes or ""
    )
    
    # Save to database
    result = await collection.insert_one(application.model_dump(by_alias=True, exclude={"id"}))
    
    # Retrieve and return
    app_data = await collection.find_one({"_id": result.inserted_id})
    app_data["_id"] = str(app_data["_id"])
    
    return ApplicationInDB(**app_data)


@router.get("", response_model=List[ApplicationInDB])
async def list_applications(
    status: Optional[ApplicationStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    List applications with optional status filter.
    
    Returns applications sorted by most recently updated first.
    """
    collection = get_applications_collection()
    
    # Build query
    query = {}
    if status:
        query["status"] = status.value
    
    # Execute query
    cursor = collection.find(query).sort("updated_at", -1).skip(skip).limit(limit)
    applications = []
    
    async for app_data in cursor:
        app_data["_id"] = str(app_data["_id"])
        applications.append(ApplicationInDB(**app_data))
    
    return applications


@router.get("/{application_id}", response_model=ApplicationInDB)
async def get_application(application_id: str):
    """Get a specific application by ID"""
    collection = get_applications_collection()
    
    try:
        app_data = await collection.find_one({"_id": ObjectId(application_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid application ID format")
    
    if not app_data:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app_data["_id"] = str(app_data["_id"])
    return ApplicationInDB(**app_data)


@router.patch("/{application_id}/status", response_model=ApplicationInDB)
async def update_application_status(
    application_id: str,
    request: UpdateApplicationStatusRequest
):
    """Update the status of an application"""
    collection = get_applications_collection()
    
    # Get existing application
    try:
        app_data = await collection.find_one({"_id": ObjectId(application_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid application ID format")
    
    if not app_data:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Add to status history
    status_entry = {
        "status": request.status.value,
        "timestamp": datetime.utcnow().isoformat(),
        "note": request.note or ""
    }
    
    # Update fields
    update_fields = {
        "status": request.status.value,
        "updated_at": datetime.utcnow(),
        "$push": {"status_history": status_entry}
    }
    
    # If status is APPLIED, set applied_at
    if request.status == ApplicationStatus.APPLIED and not app_data.get("applied_at"):
        update_fields["applied_at"] = datetime.utcnow()
    
    # Update in database
    await collection.update_one(
        {"_id": ObjectId(application_id)},
        {"$set": update_fields}
    )
    
    # Retrieve and return
    app_data = await collection.find_one({"_id": ObjectId(application_id)})
    app_data["_id"] = str(app_data["_id"])
    
    return ApplicationInDB(**app_data)
