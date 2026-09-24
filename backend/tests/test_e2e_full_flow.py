import asyncio
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

SAMPLE_GUIDE = """# European Medical Device Adoption Guide

Discussion Areas:
1. What are the key clinical workflow bottlenecks during initial deployment?
2. How do regional reimbursement and statutory insurance models influence hospital purchasing?
"""

UK_TRANSCRIPT = """
00:02:10 - 00:02:40
Dr. Sarah Jenkins:
"In the NHS system, capital purchasing requires business case sign-off by the Trust board."

00:02:45 - 00:03:20
Dr. Sarah Jenkins:
"Our primary workflow barrier was nursing staff cross-training, which required three weeks of scheduled dry-runs."
"""

GERMANY_TRANSCRIPT = """
00:05:15 - 00:05:55
Dr. Klaus Weber:
"Under statutory health insurance in Germany, G-BA approval is the decisive factor for novel reimbursement codes."

00:06:00 - 00:06:40
Dr. Klaus Weber:
"Clinicians adapted within days, but administrative billing setup took several months."
"""

FRANCE_TRANSCRIPT = """
00:08:10 - 00:08:50
Dr. Pierre Dubois:
"In France, hospital procurement for advanced surgical systems goes through regional hospital groups (GHT) and requires national HAS evaluation."

00:08:55 - 00:09:30
Dr. Pierre Dubois:
"The main operational hurdle was sterilization turnaround times and instrument reprocessing schedules between surgical cases."
"""


@pytest.mark.asyncio
async def test_full_pipeline_end_to_end():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        health_resp = await client.get("/api/v1/health")
        assert health_resp.status_code == 200
        assert health_resp.json()["status"] == "ok"
        print("\n[Step 1] Health check passed.")

        proj_resp = await client.post(
            "/api/v1/projects",
            json={
                "name": "Robotic Surgery Adoption in European Hospitals",
                "objective": "Evaluate adoption barriers, clinical bottlenecks, and procurement across UK, Germany, and France.",
            },
        )
        assert proj_resp.status_code == 201
        project_id = proj_resp.json()["id"]
        print(f"[Step 2] Project created: {project_id}")

        guide_file = io.BytesIO(SAMPLE_GUIDE.encode("utf-8"))
        guide_resp = await client.post(
            f"/api/v1/projects/{project_id}/guide",
            files={"file": ("guide.txt", guide_file, "text/plain")},
        )
        assert guide_resp.status_code == 201
        questions_data = guide_resp.json()
        assert len(questions_data["questions"]) >= 2
        print(f"[Step 3] Guide uploaded, extracted {len(questions_data['questions'])} research questions dynamically.")

        exp1_resp = await client.post(
            f"/api/v1/projects/{project_id}/experts",
            json={
                "name": "Dr. Sarah Jenkins",
                "role": "Clinical Director",
                "market": "UK",
                "organization": "NHS Trust",
            },
        )
        assert exp1_resp.status_code == 201
        exp1_id = exp1_resp.json()["id"]

        exp2_resp = await client.post(
            f"/api/v1/projects/{project_id}/experts",
            json={
                "name": "Dr. Klaus Weber",
                "role": "Head of Surgical Services",
                "market": "Germany",
                "organization": "Charité Berlin",
            },
        )
        assert exp2_resp.status_code == 201
        exp2_id = exp2_resp.json()["id"]

        exp3_resp = await client.post(
            f"/api/v1/projects/{project_id}/experts",
            json={
                "name": "Dr. Pierre Dubois",
                "role": "Procurement Lead",
                "market": "France",
                "organization": "AP-HP Paris",
            },
        )
        assert exp3_resp.status_code == 201
        exp3_id = exp3_resp.json()["id"]
        print(f"[Step 4] Registered 3 experts: UK ({exp1_id}), Germany ({exp2_id}), France ({exp3_id}).")

        uk_file = io.BytesIO(UK_TRANSCRIPT.encode("utf-8"))
        t1_resp = await client.post(
            f"/api/v1/projects/{project_id}/transcripts",
            data={"expert_id": exp1_id},
            files={"file": ("uk_transcript.txt", uk_file, "text/plain")},
        )
        assert t1_resp.status_code == 201
        assert t1_resp.json()["status"] == "ready"

        de_file = io.BytesIO(GERMANY_TRANSCRIPT.encode("utf-8"))
        t2_resp = await client.post(
            f"/api/v1/projects/{project_id}/transcripts",
            data={"expert_id": exp2_id},
            files={"file": ("germany_transcript.txt", de_file, "text/plain")},
        )
        assert t2_resp.status_code == 201
        assert t2_resp.json()["status"] == "ready"

        fr_file = io.BytesIO(FRANCE_TRANSCRIPT.encode("utf-8"))
        t3_resp = await client.post(
            f"/api/v1/projects/{project_id}/transcripts",
            data={"expert_id": exp3_id},
            files={"file": ("france_transcript.txt", fr_file, "text/plain")},
        )
        assert t3_resp.status_code == 201
        assert t3_resp.json()["status"] == "ready"
        print("[Step 5] Uploaded and indexed 3 transcripts in Qdrant successfully.")

        t1_id = t1_resp.json()["id"]
        utts_resp = await client.get(f"/api/v1/transcripts/{t1_id}/utterances")
        assert utts_resp.status_code == 200
        utts = utts_resp.json()["utterances"]
        assert len(utts) >= 2
        print(f"[Step 6] Utterances verified for transcript {t1_id}: {len(utts)} utterances.")

        print("[Step 7] Triggering full qualitative analysis pipeline (LangGraph workflows)...")
        analysis_resp = await client.post(f"/api/v1/projects/{project_id}/analysis")
        assert analysis_resp.status_code == 200
        analysis_data = analysis_resp.json()
        assert analysis_data["status"] == "completed"
        assert len(analysis_data["questions"]) >= 2
        print(f"[Step 7] Analysis pipeline completed. Synthesized answers for {len(analysis_data['questions'])} questions.")

        ev_resp = await client.get(f"/api/v1/projects/{project_id}/evidence")
        assert ev_resp.status_code == 200
        evidence_list = ev_resp.json()["evidence"]
        assert len(evidence_list) > 0
        print(f"[Step 8] Evidence verified: {len(evidence_list)} grounded evidence items with timestamps.")

        diff_resp = await client.get(f"/api/v1/projects/{project_id}/differences")
        assert diff_resp.status_code == 200
        differences = diff_resp.json()["differences"]
        assert len(differences) > 0
        print(f"[Step 9] Differences verified: {len(differences)} cross-expert differences synthesized.")

        ins_resp = await client.get(f"/api/v1/projects/{project_id}/insights")
        assert ins_resp.status_code == 200
        insights = ins_resp.json()["insights"]
        assert len(insights) > 0
        print(f"[Step 10] Insights verified: {len(insights)} strategic insights synthesized.")

        copilot_resp = await client.post(
            f"/api/v1/projects/{project_id}/ask",
            json={"question": "What did the UK expert say about capital purchasing in NHS?"},
        )
        assert copilot_resp.status_code == 200
        copilot_data = copilot_resp.json()
        assert len(copilot_data["answer"]) > 0
        assert len(copilot_data["evidence"]) > 0
        print(f"[Step 11] Research Copilot answered successfully with {len(copilot_data['evidence'])} citations.")
        print("--- Copilot Answer Snippet ---")
        print(copilot_data["answer"][:250])
        print("-------------------------------")


if __name__ == "__main__":
    asyncio.run(test_full_pipeline_end_to_end())
