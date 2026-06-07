from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.v1.analytics import router as analytics_router
from backend.api.v1.chat import router as chat_router
from backend.api.v1.health import router as health_router
from backend.rag.chroma_client import chroma_rag

app = FastAPI(
    title="Healthcare Analytics Copilot API",
    description="GenAI analytics platform for pharma and healthcare sales",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    try:
        # force=True ensures newly added .md files are always ingested
        chroma_rag.ingest_all(force=True)
    except Exception:
        pass


@app.get("/")
async def root():
    return {
        "service": "Healthcare Analytics Copilot",
        "docs": "/docs",
        "cube_playground": "http://localhost:4000",
    }
