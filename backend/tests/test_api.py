"""API integration tests for all InsightOS endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health endpoint."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_and_get_project(client: AsyncClient):
    """Test creating a project and retrieving it."""
    # Create project
    create_payload = {
        "name": "MedTech Robotic Adoption Study",
        "objective": "Understand clinical barriers to adoption in European hospitals.",
    }
    create_res = await client.post("/api/v1/projects", json=create_payload)
    assert create_res.status_code == 201
    project_data = create_res.json()
    assert project_data["name"] == create_payload["name"]
    assert "id" in project_data

    project_id = project_data["id"]

    # Get project by ID
    get_res = await client.get(f"/api/v1/projects/{project_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == project_id

    # List projects
    list_res = await client.get("/api/v1/projects")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


@pytest.mark.asyncio
async def test_upload_guide_and_get_questions(client: AsyncClient):
    """Test uploading an interview guide and fetching extracted research questions."""
    # Create project
    p_res = await client.post("/api/v1/projects", json={"name": "Guide Test Project"})
    project_id = p_res.json()["id"]

    # Upload guide file
    guide_content = b"""
    # Robotic Surgery Guide
    Q1: What are primary capital expense barriers?
    Q2: How do surgeon learning curves affect procedure times?
    """
    files = {"file": ("guide.txt", guide_content, "text/plain")}
    upload_res = await client.post(f"/api/v1/projects/{project_id}/guide", files=files)
    assert upload_res.status_code == 201
    data = upload_res.json()
    assert data["total"] == 2
    assert len(data["questions"]) == 2

    # Get questions
    q_res = await client.get(f"/api/v1/projects/{project_id}/questions")
    assert q_res.status_code == 200
    assert q_res.json()["total"] == 2


@pytest.mark.asyncio
async def test_expert_and_transcript_endpoints(client: AsyncClient):
    """Test expert creation and transcript ingestion endpoints."""
    # Create project
    p_res = await client.post("/api/v1/projects", json={"name": "Expert Test Project"})
    project_id = p_res.json()["id"]

    # Create expert
    expert_payload = {
        "name": "Dr. Sarah Jenkins",
        "role": "Chief of Surgery",
        "market": "UK",
        "organization": "NHS Trust",
    }
    exp_res = await client.post(f"/api/v1/projects/{project_id}/experts", json=expert_payload)
    assert exp_res.status_code == 201
    expert_id = exp_res.json()["id"]

    # Upload transcript
    transcript_text = b"""
00:01:00 - 00:01:30
Dr. Sarah Jenkins:
"Procurement takes approximately six months through the regional health authority."
"""
    files = {"file": ("uk_expert.txt", transcript_text, "text/plain")}
    data = {"expert_id": expert_id}
    t_res = await client.post(
        f"/api/v1/projects/{project_id}/transcripts",
        files=files,
        data=data,
    )
    assert t_res.status_code == 201
    transcript_id = t_res.json()["id"]

    # Get transcript detail
    detail_res = await client.get(f"/api/v1/transcripts/{transcript_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["utterance_count"] == 1
