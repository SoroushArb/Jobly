"""Tests for SSE events"""
import pytest
import asyncio
from datetime import datetime
from app.schemas.sse import SSEEvent, EventType
from app.services.sse_service import SSEService


@pytest.mark.asyncio
class TestSSEService:
    """Test SSE service functionality"""
    
    async def test_subscribe_and_emit(self):
        """Test subscribing to events and receiving them"""
        service = SSEService()
        
        # Subscribe
        queue = service.subscribe(user_id="test_user")
        
        # Emit an event
        event = SSEEvent(
            event_type=EventType.JOB_CREATED,
            data={"job_id": "123", "type": "job_ingestion"},
            user_id="test_user"
        )
        await service.emit(event)
        
        # Check that event was received
        received_event = await asyncio.wait_for(queue.get(), timeout=1.0)
        
        assert received_event.event_type == EventType.JOB_CREATED
        assert received_event.data["job_id"] == "123"
        
        # Cleanup
        service.unsubscribe(queue, user_id="test_user")
    
    async def test_multiple_subscribers(self):
        """Test that events are sent to all subscribers"""
        service = SSEService()
        
        # Create multiple subscribers
        queue1 = service.subscribe(user_id="user1")
        queue2 = service.subscribe(user_id="user1")
        
        # Emit an event
        event = SSEEvent(
            event_type=EventType.JOB_PROGRESS,
            data={"job_id": "456", "progress": 50},
            user_id="user1"
        )
        await service.emit(event)
        
        # Both should receive the event
        event1 = await asyncio.wait_for(queue1.get(), timeout=1.0)
        event2 = await asyncio.wait_for(queue2.get(), timeout=1.0)
        
        assert event1.data["progress"] == 50
        assert event2.data["progress"] == 50
        
        # Cleanup
        service.unsubscribe(queue1, user_id="user1")
        service.unsubscribe(queue2, user_id="user1")
    
    async def test_user_scoped_events(self):
        """Test that events are scoped to correct users"""
        service = SSEService()
        
        # Subscribe different users
        queue_user1 = service.subscribe(user_id="user1")
        queue_user2 = service.subscribe(user_id="user2")
        
        # Emit event for user1
        event = SSEEvent(
            event_type=EventType.JOB_COMPLETED,
            data={"job_id": "789"},
            user_id="user1"
        )
        await service.emit(event)
        
        # Only user1 should receive it
        try:
            event1 = await asyncio.wait_for(queue_user1.get(), timeout=1.0)
            assert event1.data["job_id"] == "789"
        except asyncio.TimeoutError:
            pytest.fail("User1 should have received the event")
        
        # User2 should not receive it
        try:
            await asyncio.wait_for(queue_user2.get(), timeout=0.5)
            pytest.fail("User2 should not have received the event")
        except asyncio.TimeoutError:
            pass  # Expected
        
        # Cleanup
        service.unsubscribe(queue_user1, user_id="user1")
        service.unsubscribe(queue_user2, user_id="user2")
    
    async def test_event_types(self):
        """Test different event types"""
        service = SSEService()
        queue = service.subscribe()
        
        # Test all event types
        event_types = [
            EventType.JOB_CREATED,
            EventType.JOB_PROGRESS,
            EventType.JOB_COMPLETED,
            EventType.JOB_FAILED,
            EventType.APPLICATION_STATUS_CHANGE,
        ]
        
        for event_type in event_types:
            event = SSEEvent(
                event_type=event_type,
                data={"test": event_type}
            )
            await service.emit(event)
            
            received = await asyncio.wait_for(queue.get(), timeout=1.0)
            assert received.event_type == event_type
        
        # Cleanup
        service.unsubscribe(queue)
    
    async def test_event_payload_format(self):
        """Test that event payloads have required fields"""
        event = SSEEvent(
            event_type=EventType.JOB_PROGRESS,
            data={
                "job_id": "123",
                "type": "job_ingestion",
                "progress": 75,
                "message": "Processing..."
            },
            user_id="test_user"
        )
        
        # Validate structure
        assert event.event_type == EventType.JOB_PROGRESS
        assert "job_id" in event.data
        assert "progress" in event.data
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)
