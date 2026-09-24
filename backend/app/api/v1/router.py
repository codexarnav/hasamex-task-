"""Central v1 API router aggregating all resource routers."""
from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.projects import router as projects_router
from app.api.v1.guides import router as guides_router
from app.api.v1.experts import router as experts_router
from app.api.v1.transcripts import router as transcripts_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.evidence import router as evidence_router
from app.api.v1.differences import router as differences_router
from app.api.v1.insights import router as insights_router
from app.api.v1.copilot import router as copilot_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(projects_router)
api_v1_router.include_router(guides_router)
api_v1_router.include_router(experts_router)
api_v1_router.include_router(transcripts_router)
api_v1_router.include_router(analysis_router)
api_v1_router.include_router(evidence_router)
api_v1_router.include_router(differences_router)
api_v1_router.include_router(insights_router)
api_v1_router.include_router(copilot_router)
