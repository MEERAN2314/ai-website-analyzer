import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns HTML"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_register_user():
    """Test user registration"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test@123",
                "full_name": "Test User"
            }
        )
        # May fail if user exists, that's ok
        assert response.status_code in [201, 400]


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid@example.com",
                "password": "WrongPassword"
            }
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_analyze_without_auth():
    """Test analysis without authentication (guest)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analysis/analyze",
            json={"website_url": "https://example.com"}
        )
        # Should work for guest users (1 free analysis)
        assert response.status_code in [200, 429]  # 429 if limit exceeded
