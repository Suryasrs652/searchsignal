import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import init_db

@pytest.mark.asyncio
async def test_api_root_and_auth():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Root endpoint
        root_resp = await client.get("/")
        assert root_resp.status_code == 200
        root_data = root_resp.json()
        assert root_data["name"] == "SearchSignal"
        assert root_data["crawler_version"] == "4.2.0"
        assert root_data["geo_model_version"] == "GEO-2026.1"

        # Auth login
        login_resp = await client.post("/api/v1/auth/login", json={"email": "admin@searchsignal.ai", "password": "admin"})
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()["data"]

        # Projects list
        proj_resp = await client.get("/api/v1/projects")
        assert proj_resp.status_code == 200
        projs = proj_resp.json()["data"]
        assert isinstance(projs, list)

@pytest.mark.asyncio
async def test_project_and_audit_creation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create Project
        create_resp = await client.post("/api/v1/projects", json={
            "name": "Synthetic Test Site Project",
            "root_url": "http://127.0.0.1:8089",
            "crawl_config": {"max_urls": 10, "respect_robots": True}
        })
        assert create_resp.status_code == 200
        project_id = create_resp.json()["data"]["id"]

        # Launch Audit
        audit_resp = await client.post(f"/api/v1/projects/{project_id}/audits", json={
            "crawl_mode": "quick",
            "max_urls": 10,
            "respect_robots": True
        })
        assert audit_resp.status_code == 200
        audit_id = audit_resp.json()["data"]["audit_id"]

        # Get Audit status
        status_resp = await client.get(f"/api/v1/audits/{audit_id}")
        assert status_resp.status_code == 200
        assert status_resp.json()["data"]["id"] == audit_id
