"""End-to-End Vertical Slice Integration Test.

Tests the full research analysis lifecycle from project inception to Copilot inquiry:
Project -> Guide -> Questions -> Experts -> Transcripts -> Utterances ->
Evidence -> Answers -> Differences -> Insights -> Copilot.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_vertical_slice_journey(client: AsyncClient):
    """Execute complete V1 end-to-end qualitative research workflow."""
    
    p_res = await client.post(
        "/api/v1/projects",
        json={
            "name": "Endoscopic Innovation Analysis 2026",
            "objective": "Evaluate global adoption barriers and reimbursement nuances across European hospital systems.",
        },
    )
    assert p_res.status_code == 201
    project_id = p_res.json()["id"]

    guide_content = b"""
    # European Medical Device Adoption Guide
    
    Discussion Areas:
    1. What are the key clinical workflow bottlenecks during initial deployment?
    2. How do regional reimbursement and statutory insurance models influence hospital purchasing?
    """
    guide_upload = await client.post(
        f"/api/v1/projects/{project_id}/guide",
        files={"file": ("guide.txt", guide_content, "text/plain")},
    )
    assert guide_upload.status_code == 201
    questions_data = guide_upload.json()
    assert questions_data["total"] == 2
    q1_id = questions_data["questions"][0]["id"]
    q2_id = questions_data["questions"][1]["id"]

    exp1_res = await client.post(
        f"/api/v1/projects/{project_id}/experts",
        json={
            "name": "Dr. Sarah Jenkins",
            "role": "Director of Interventional Pulmonology",
            "market": "UK",
            "organization": "Imperial College Healthcare",
        },
    )
    assert exp1_res.status_code == 201
    exp1_id = exp1_res.json()["id"]

    exp2_res = await client.post(
        f"/api/v1/projects/{project_id}/experts",
        json={
            "name": "Dr. Klaus Weber",
            "role": "Head of Endoscopy Services",
            "market": "Germany",
            "organization": "Charite Berlin",
        },
    )
    assert exp2_res.status_code == 201
    exp2_id = exp2_res.json()["id"]

    transcript1_text = b"""
00:02:10 - 00:02:40
Dr. Sarah Jenkins:
"In the NHS system, capital purchasing requires business case sign-off by the Trust board."

00:02:45 - 00:03:20
Dr. Sarah Jenkins:
"Our primary workflow barrier was nursing staff cross-training, which required three weeks of scheduled dry-runs."
"""
    t1_upload = await client.post(
        f"/api/v1/projects/{project_id}/transcripts",
        files={"file": ("uk_transcript.txt", transcript1_text, "text/plain")},
        data={"expert_id": exp1_id},
    )
    assert t1_upload.status_code == 201

    transcript2_text = b"""
00:05:15 - 00:05:55
Dr. Klaus Weber:
"Under statutory health insurance in Germany, G-BA approval is the decisive factor for novel reimbursement codes."

00:06:00 - 00:06:40
Dr. Klaus Weber:
"Clinicians adapted within days, but administrative billing setup took several months."
"""
    t2_upload = await client.post(
        f"/api/v1/projects/{project_id}/transcripts",
        files={"file": ("germany_transcript.txt", transcript2_text, "text/plain")},
        data={"expert_id": exp2_id},
    )
    assert t2_upload.status_code == 201

    analysis_res = await client.post(f"/api/v1/projects/{project_id}/analysis")
    assert analysis_res.status_code == 200
    analysis_data = analysis_res.json()
    assert analysis_data["project_id"] == project_id
    assert len(analysis_data["questions"]) == 2

    for q_item in analysis_data["questions"]:
        assert len(q_item["answers"]) >= 1
        for ans in q_item["answers"]:
            assert ans["answer_text"]
            assert len(ans["evidence"]) >= 1
            ev = ans["evidence"][0]
            assert ev["quote"]
            assert ev["expert"]["name"] in ["Dr. Sarah Jenkins", "Dr. Klaus Weber"]
            assert ev["timestamp"]["start"] is not None

    diff_res = await client.get(f"/api/v1/projects/{project_id}/differences")
    assert diff_res.status_code == 200
    diff_data = diff_res.json()
    assert diff_data["total"] >= 1
    diff_item = diff_data["differences"][0]
    assert diff_item["title"]
    assert len(diff_item["perspectives"]) >= 1

    insight_res = await client.get(f"/api/v1/projects/{project_id}/insights")
    assert insight_res.status_code == 200
    insight_data = insight_res.json()
    assert insight_data["total"] >= 1
    assert insight_data["insights"][0]["title"]
    assert insight_data["insights"][0]["summary"]

    copilot_res = await client.post(
        f"/api/v1/projects/{project_id}/ask",
        json={"question": "What did the German expert say about G-BA reimbursement approval?"},
    )
    assert copilot_res.status_code == 200
    copilot_data = copilot_res.json()
    assert copilot_data["answer"]
    assert not copilot_data["insufficient_evidence"]
    assert len(copilot_data["evidence"]) >= 1
    assert copilot_data["evidence"][0]["quote"]
    assert copilot_data["evidence"][0]["timestamp"]["start"] is not None
