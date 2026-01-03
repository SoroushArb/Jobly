"""
Server-Sent Events (SSE) schemas for real-time updates
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of SSE events"""
    JOB_CREATED = "job.created"
    JOB_PROGRESS = "job.progress"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    APPLICATION_STATUS_CHANGE = "application.status_change"


class SSEEvent(BaseModel):
    """Server-Sent Event model"""
    event_type: EventType = Field(..., description="Event type", alias="type")
    data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = Field(None, description="User ID for scoped events")
    
    class Config:
        populate_by_name = True


class SSEEventInDB(SSEEvent):
    """SSE Event as stored in database"""
    id: str = Field(..., alias="_id")
    
    class Config:
        populate_by_name = True
