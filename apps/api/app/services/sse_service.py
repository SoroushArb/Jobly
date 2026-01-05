"""
Server-Sent Events (SSE) service for real-time updates
"""
import asyncio
import logging
from typing import AsyncGenerator, Optional, Dict, Any
from datetime import datetime
import json

from app.schemas.sse import SSEEvent, EventType
from app.models.database import Database

logger = logging.getLogger(__name__)


class SSEService:
    """Service for managing Server-Sent Events"""
    
    def __init__(self):
        self._subscribers: Dict[str, list[asyncio.Queue]] = {}
    
    def subscribe(self, user_id: Optional[str] = None) -> asyncio.Queue:
        """Subscribe to events for a user"""
        key = user_id or "global"
        if key not in self._subscribers:
            self._subscribers[key] = []
        
        queue = asyncio.Queue(maxsize=100)
        self._subscribers[key].append(queue)
        logger.info(f"New subscriber for {key}, total: {len(self._subscribers[key])}")
        return queue
    
    def unsubscribe(self, queue: asyncio.Queue, user_id: Optional[str] = None):
        """Unsubscribe from events"""
        key = user_id or "global"
        if key in self._subscribers and queue in self._subscribers[key]:
            self._subscribers[key].remove(queue)
            logger.info(f"Subscriber removed for {key}, remaining: {len(self._subscribers[key])}")
            
            # Clean up empty lists
            if not self._subscribers[key]:
                del self._subscribers[key]
    
    async def emit(self, event: SSEEvent):
        """Emit an event to all subscribers"""
        key = event.user_id or "global"
        
        # Also store in database for reconnect support
        await self._store_event(event)
        
        if key in self._subscribers:
            dead_queues = []
            for queue in self._subscribers[key]:
                try:
                    await asyncio.wait_for(queue.put(event), timeout=1.0)
                except asyncio.TimeoutError:
                    logger.warning(f"Queue full for subscriber, dropping event")
                    dead_queues.append(queue)
                except Exception as e:
                    logger.error(f"Error emitting event: {e}")
                    dead_queues.append(queue)
            
            # Remove dead queues
            for dead_queue in dead_queues:
                self.unsubscribe(dead_queue, event.user_id)
    
    async def _store_event(self, event: SSEEvent):
        """Store event in database for reconnect support"""
        try:
            db = Database.get_database()
            events_collection = db["events"]
            
            event_dict = event.model_dump(by_alias=True, exclude={"id"})
            await events_collection.insert_one(event_dict)
            
            # Keep only last 1000 events per user
            # This is a simple approach; for production, consider TTL indexes
            count = await events_collection.count_documents({"user_id": event.user_id})
            if count > 1000:
                # Delete oldest events
                cursor = events_collection.find(
                    {"user_id": event.user_id}
                ).sort("timestamp", 1).limit(count - 1000)
                
                ids_to_delete = [doc["_id"] async for doc in cursor]
                if ids_to_delete:
                    await events_collection.delete_many({"_id": {"$in": ids_to_delete}})
        except Exception as e:
            logger.error(f"Error storing event: {e}")
    
    async def get_recent_events(
        self,
        user_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 50,
    ) -> list[SSEEvent]:
        """Get recent events for reconnect support"""
        try:
            db = Database.get_database()
            events_collection = db["events"]
            
            query = {"user_id": user_id}
            if since:
                query["timestamp"] = {"$gt": since}
            
            cursor = events_collection.find(query).sort("timestamp", -1).limit(limit)
            
            events = []
            async for event_data in cursor:
                event_data["_id"] = str(event_data["_id"])
                events.append(SSEEvent(**event_data))
            
            return list(reversed(events))  # Return in chronological order
        except Exception as e:
            logger.error(f"Error getting recent events: {e}")
            return []
    
    async def stream_events(
        self,
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream events as SSE format"""
        queue = self.subscribe(user_id)
        
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
            
            while True:
                try:
                    # Wait for events with a timeout to send keepalive
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    
                    # Format as SSE
                    event_data = event.model_dump(by_alias=True, exclude={"id"})
                    # Convert datetime to ISO format
                    event_data["timestamp"] = event_data["timestamp"].isoformat()
                    
                    yield f"event: {event.event_type}\n"
                    yield f"data: {json.dumps(event_data)}\n\n"
                    
                except asyncio.TimeoutError:
                    # Send keepalive comment
                    yield ": keepalive\n\n"
                    
        except asyncio.CancelledError:
            logger.info("SSE stream cancelled")
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
        finally:
            self.unsubscribe(queue, user_id)


# Global SSE service instance
sse_service = SSEService()
