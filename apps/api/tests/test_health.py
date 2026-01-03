"""Tests for health and readiness endpoints"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health check endpoints"""
    
    async def test_health_endpoint(self):
        """Test basic health check"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    
    async def test_healthz_endpoint(self):
        """Test Kubernetes-style health check"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/healthz")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    
    async def test_readyz_endpoint(self):
        """Test readiness check (requires database)"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/readyz")
            
            # Should be 200 if database is available, 503 if not
            # We accept both since we might not have a test database set up
            assert response.status_code in (200, 503)
            
            data = response.json()
            assert "status" in data
            
            if response.status_code == 200:
                assert data["status"] == "ready"
                assert data["database"] == "connected"
            else:
                assert data["status"] == "not ready"
    
    async def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/")
            
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "version" in data
            assert "endpoints" in data
            assert data["version"] == "7.0.0"
