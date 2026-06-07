from fastapi import APIRouter

from backend.graph.neo4j_client import neo4j_client
from backend.rag.chroma_client import chroma_rag
from backend.semantic.cube_client import cube_client
from backend.utils.llm import llm_client

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "healthcare-analytics-copilot"}


@router.get("/health/cube")
async def health_cube():
    try:
        meta = await cube_client.meta()
        cubes = [c.get("name") for c in meta.get("cubes", [])]
        return {"status": "ok", "cube_connected": True, "cubes": cubes}
    except Exception as e:
        return {"status": "degraded", "cube_connected": False, "error": str(e)}


@router.get("/health/neo4j")
async def health_neo4j():
    ok = await neo4j_client.health()
    return {"status": "ok" if ok else "degraded", "neo4j_connected": ok}


@router.get("/health/rag")
async def health_rag():
    try:
        counts = chroma_rag.ingest_all()
        return {"status": "ok", "collections": counts}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


@router.get("/health/llm")
async def health_llm():
    return {"status": "ok" if llm_client.available else "no_key", "llm_available": llm_client.available}
