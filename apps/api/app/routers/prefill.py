"""Prefill router for local agent communication"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from datetime import datetime, timedelta
from bson import ObjectId
import secrets
import hashlib

from app.schemas.application import (
    PrefillIntent,
    PrefillIntentInDB,
    PrefillIntentRequest,
    PrefillLog,
    PrefillLogInDB,
    PrefillResultRequest,
    ApplicationInDB,
    ApplicationStatus,
)
from app.schemas.profile import UserProfile
from app.models.database import (
    get_applications_collection,
    get_prefill_intents_collection,
    get_prefill_logs_collection,
    get_profiles_collection,
    get_packets_collection,
)


router = APIRouter(prefix="/prefill", tags=["prefill"])

# Token expiry duration (15 minutes)
TOKEN_EXPIRY_MINUTES = 15


def generate_auth_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash a token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()


async def get_user_profile() -> UserProfile:
    """Get the user's profile"""
    collection = get_profiles_collection()
    profile_data = await collection.find_one({})
    
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile_data["_id"] = str(profile_data["_id"])
    return UserProfile(**profile_data)


@router.post("/create-intent", response_model=dict)
async def create_prefill_intent(request: PrefillIntentRequest):
    """
    Create a prefill intent for a job application.
    
    Returns:
    - intent_id: ID of the created intent
    - auth_token: Short-lived token for local agent (plain text, only shown once)
    - expires_at: Token expiration timestamp
    """
    # Get application
    apps_collection = get_applications_collection()
    try:
        app_data = await apps_collection.find_one({"_id": ObjectId(request.application_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid application ID format")
    
    if not app_data:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = ApplicationInDB(**{**app_data, "_id": str(app_data["_id"])})
    
    # Get user profile for field mapping
    profile = await get_user_profile()
    
    # Get packet for attachments
    packets_collection = get_packets_collection()
    try:
        packet_data = await packets_collection.find_one({"_id": ObjectId(application.packet_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid packet ID")
    
    if not packet_data:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    # Build user fields from profile
    user_fields = {
        "name": f"{profile.basics.name} {profile.basics.surname}",
        "email": profile.basics.email,
        "phone": profile.basics.phone or "",
        "linkedin": profile.basics.linkedin or "",
        "github": profile.basics.github or "",
        "location_city": profile.preferences.location_city or "",
        "location_country": profile.preferences.location_country or "",
    }
    
    # Build attachments
    attachments = {}
    if packet_data.get("cv_pdf"):
        cv_pdf = packet_data["cv_pdf"]
        attachments["resume"] = cv_pdf.get("filepath", "")
    
    # Build common answers
    common_answers = {}
    if packet_data.get("common_answers"):
        # Common answers file exists - would need to parse it
        # For now, just indicate it's available
        common_answers["_file_available"] = True
    
    # Generate auth token
    auth_token = generate_auth_token()
    token_hash = hash_token(auth_token)
    expires_at = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    
    # Create intent
    intent = PrefillIntent(
        packet_id=application.packet_id,
        job_url=application.job_url,
        user_fields=user_fields,
        attachments=attachments,
        common_answers=common_answers,
        auth_token=token_hash,  # Store hashed version
        token_expires_at=expires_at,
        status="pending"
    )
    
    # Save to database
    intents_collection = get_prefill_intents_collection()
    result = await intents_collection.insert_one(
        intent.model_dump(by_alias=True, exclude={"id"})
    )
    intent_id = str(result.inserted_id)
    
    # Update application status
    await apps_collection.update_one(
        {"_id": ObjectId(request.application_id)},
        {
            "$set": {
                "status": ApplicationStatus.INTENT_CREATED.value,
                "prefill_intent_id": intent_id,
                "updated_at": datetime.utcnow(),
            },
            "$push": {
                "status_history": {
                    "status": ApplicationStatus.INTENT_CREATED.value,
                    "timestamp": datetime.utcnow().isoformat(),
                    "note": "Prefill intent created"
                }
            }
        }
    )
    
    return {
        "intent_id": intent_id,
        "auth_token": auth_token,  # Return plain token (only time it's shown)
        "expires_at": expires_at.isoformat(),
        "message": "Intent created. Use the auth_token in the local agent."
    }


@router.get("/intent/{intent_id}", response_model=PrefillIntentInDB)
async def get_prefill_intent(
    intent_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get a prefill intent by ID.
    
    Requires: Authorization header with Bearer token
    """
    # Validate authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    token_hash = hash_token(token)
    
    # Get intent
    collection = get_prefill_intents_collection()
    try:
        intent_data = await collection.find_one({"_id": ObjectId(intent_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid intent ID format")
    
    if not intent_data:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    intent = PrefillIntentInDB(**{**intent_data, "_id": str(intent_data["_id"])})
    
    # Validate token
    if intent.auth_token != token_hash:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check expiration
    if intent.token_expires_at and intent.token_expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token expired")
    
    return intent


@router.post("/report-result")
async def report_prefill_result(request: PrefillResultRequest):
    """
    Report the result of a prefill operation from the local agent.
    
    Validates the auth token and saves the log.
    """
    # Get intent
    collection = get_prefill_intents_collection()
    try:
        intent_data = await collection.find_one({"_id": ObjectId(request.intent_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid intent ID format")
    
    if not intent_data:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    intent = PrefillIntentInDB(**{**intent_data, "_id": str(intent_data["_id"])})
    
    # Validate token
    token_hash = hash_token(request.auth_token)
    if intent.auth_token != token_hash:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check expiration
    if intent.token_expires_at and intent.token_expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token expired")
    
    # Save log
    logs_collection = get_prefill_logs_collection()
    log_data = request.log.model_dump(by_alias=True, exclude={"id"})
    result = await logs_collection.insert_one(log_data)
    log_id = str(result.inserted_id)
    
    # Update intent status
    await collection.update_one(
        {"_id": ObjectId(request.intent_id)},
        {"$set": {"status": "completed"}}
    )
    
    # Find and update application
    apps_collection = get_applications_collection()
    app = await apps_collection.find_one({"prefill_intent_id": request.intent_id})
    
    if app:
        new_status = ApplicationStatus.PREFILLED if not request.log.errors else ApplicationStatus.INTENT_CREATED
        
        await apps_collection.update_one(
            {"_id": app["_id"]},
            {
                "$set": {
                    "status": new_status.value,
                    "prefill_log_id": log_id,
                    "last_prefill_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
                "$push": {
                    "status_history": {
                        "status": new_status.value,
                        "timestamp": datetime.utcnow().isoformat(),
                        "note": f"Prefill completed with {len(request.log.filled_fields)} fields filled"
                    }
                }
            }
        )
    
    return {
        "message": "Prefill result recorded",
        "log_id": log_id,
        "filled_fields_count": len(request.log.filled_fields),
        "errors_count": len(request.log.errors)
    }
