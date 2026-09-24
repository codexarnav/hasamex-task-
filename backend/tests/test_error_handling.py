"""Tests for API error handling and validation responses."""
import pytest
from uuid import uuid4
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_not_found_errors(client: AsyncClient):
    """Verify clean 404 responses for non-existent entities."""
    non_existent_id = uuid4()
    
    res = await client.get(f"/api/v1/projects/{non_existent_id}")
    assert res.status_code == 404
    data = res.json()
    assert "not found" in data["error"].lower()

    res = await client.get(f"/api/v1/transcripts/{non_existent_id}")
    assert res.status_code == 404

    res = await client.get(f"/api/v1/evidence/{non_existent_id}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_empty_file_upload_error(client: AsyncClient):
    """Verify clean 400 response when uploading empty files."""
    p_res = await client.post("/api/v1/projects", json={"name": "Upload Error Test"})
    project_id = p_res.json()["id"]

    res = await client.post(
        f"/api/v1/projects/{project_id}/guide",
        files={"file": ("guide.txt", b"", "text/plain")},
    )
    assert res.status_code == 400
