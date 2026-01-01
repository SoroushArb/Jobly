"""Match API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from bson import ObjectId

from app.schemas.match import (
    MatchResponse,
    MatchListResponse,
    RecomputeMatchesResponse,
    MatchWithJob,
    MatchInDB,
)
from app.services.matching.match_service import MatchGenerationService
from app.models.database import get_matches_collection, get_jobs_collection, get_profiles_collection

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/recompute", response_model=RecomputeMatchesResponse)
async def recompute_matches():
    """
    Recompute all matches for the current profile vs stored jobs
    
    Note: This assumes a single profile. In a multi-user system,
    you would get the profile_id from authentication.
    """
    # Get the profile (for now, get the first/only profile)
    profiles_collection = get_profiles_collection()
    profile = await profiles_collection.find_one({})
    
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found. Please create a profile first.")
    
    profile_id = str(profile["_id"])
    
    # Get job count
    jobs_collection = get_jobs_collection()
    jobs_count = await jobs_collection.count_documents({})
    
    if jobs_count == 0:
        raise HTTPException(status_code=404, detail="No jobs found. Please run job ingestion first.")
    
    # Recompute matches
    service = MatchGenerationService()
    matches_computed = await service.recompute_all_matches(profile_id)
    
    return RecomputeMatchesResponse(
        matches_computed=matches_computed,
        profile_id=profile_id,
        jobs_processed=jobs_count,
        message=f"Successfully computed {matches_computed} matches"
    )


@router.get("", response_model=MatchListResponse)
async def list_matches(
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum match score"),
    remote: Optional[bool] = Query(None, description="Filter for remote jobs"),
    europe: Optional[bool] = Query(None, description="Filter for Europe jobs"),
    country: Optional[str] = Query(None, description="Filter by country"),
    city: Optional[str] = Query(None, description="Filter by city"),
    skill_tag: Optional[str] = Query(None, description="Filter by skill tag"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
):
    """
    List matches with optional filters
    
    Results are sorted by score (descending), then by posted_date (descending), then by _id
    """
    # Get profile
    profiles_collection = get_profiles_collection()
    profile = await profiles_collection.find_one({})
    
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found")
    
    profile_id = str(profile["_id"])
    
    # Build match query
    match_query = {"profile_id": profile_id}
    
    if min_score is not None:
        match_query["score_total"] = {"$gte": min_score}
    
    # Get matches
    matches_collection = get_matches_collection()
    
    # Count total
    total = await matches_collection.count_documents(match_query)
    
    # Get paginated matches with deterministic sorting
    skip = (page - 1) * per_page
    cursor = matches_collection.find(match_query).sort([
        ("score_total", -1),  # Highest score first
        ("posted_date", -1),  # Most recent first
        ("_id", 1),  # Stable tie-breaker
    ]).skip(skip).limit(per_page)
    
    match_docs = await cursor.to_list(length=per_page)
    
    # Get corresponding jobs
    jobs_collection = get_jobs_collection()
    
    results = []
    for match_doc in match_docs:
        # Convert match
        match_doc["id"] = str(match_doc["_id"])
        match = MatchInDB(**match_doc)
        
        # Get job
        job_doc = await jobs_collection.find_one({"_id": ObjectId(match.job_id)})
        
        if not job_doc:
            continue  # Skip if job was deleted
        
        # Convert job _id
        job_doc["id"] = str(job_doc["_id"])
        
        # Apply job-level filters
        if remote is not None:
            if remote and job_doc.get("remote_type") != "remote":
                continue
        
        if europe is not None:
            european_countries = {
                "germany", "france", "uk", "united kingdom", "netherlands", "spain",
                "italy", "poland", "sweden", "norway", "denmark", "finland",
                "austria", "belgium", "switzerland", "ireland", "portugal", "greece"
            }
            job_country = (job_doc.get("country") or "").lower()
            if europe and job_country not in european_countries:
                continue
        
        if country:
            job_country = (job_doc.get("country") or "").lower()
            if country.lower() not in job_country:
                continue
        
        if city:
            job_city = (job_doc.get("city") or "").lower()
            if city.lower() not in job_city:
                continue
        
        if skill_tag:
            # Check if skill appears in job description
            description = (job_doc.get("description_clean") or "").lower()
            title = job_doc.get("title", "").lower()
            if skill_tag.lower() not in description and skill_tag.lower() not in title:
                continue
        
        results.append(MatchWithJob(match=match, job=job_doc))
    
    return MatchListResponse(
        matches=results,
        total=len(results),  # Note: filtered count, not total matches
        page=page,
        per_page=per_page,
        message=f"Found {len(results)} matches"
    )


@router.get("/{job_id}", response_model=MatchResponse)
async def get_match(job_id: str):
    """
    Get match details for a specific job
    """
    # Get profile
    profiles_collection = get_profiles_collection()
    profile = await profiles_collection.find_one({})
    
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found")
    
    profile_id = str(profile["_id"])
    
    # Get match
    matches_collection = get_matches_collection()
    match_doc = await matches_collection.find_one({
        "profile_id": profile_id,
        "job_id": job_id
    })
    
    if not match_doc:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Convert match
    match_doc["id"] = str(match_doc["_id"])
    match = MatchInDB(**match_doc)
    
    # Get job
    jobs_collection = get_jobs_collection()
    job_doc = await jobs_collection.find_one({"_id": ObjectId(job_id)})
    
    if job_doc:
        job_doc["id"] = str(job_doc["_id"])
    
    return MatchResponse(
        match=match,
        job=job_doc,
        message="Match retrieved successfully"
    )
