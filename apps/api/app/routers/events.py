"""
Server-Sent Events (SSE) API endpoints for real-time updates
"""
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import Optional

from app.services.sse_service import sse_service


router = APIRouter(prefix="/events", tags=["events"])


@router.get("/stream")
async def event_stream(
    user_id: Optional[str] = Query(None, description="User ID for scoped events (optional for single-user mode)")
):
    """
    Subscribe to real-time events via Server-Sent Events (SSE).
    
    Event types:
    - job.created: New background job created
    - job.progress: Job progress update
    - job.completed: Job completed successfully
    - job.failed: Job failed
    - application.status_change: Application status changed
    
    In a multi-user system, you would get user_id from authentication.
    For now, this is a simplified single-user implementation.
    """
    return StreamingResponse(
        sse_service.stream_events(user_id=user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
