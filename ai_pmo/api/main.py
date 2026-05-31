"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import SessionLocal, init_db
from api.routes import dashboard, projects, reports, tasks
from api.seed_data import seed_projects
from services.risk_detector import refresh_all_risks


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_projects(db)
        refresh_all_risks(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="AI PMO Agent API",
    description="半導體 AI 專案管理 Agent 後端",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/api/health")
def health():
    db = SessionLocal()
    try:
        from api import crud

        count = len(crud.get_projects(db))
    finally:
        db.close()
    return {"status": "ok", "project_count": count}


if __name__ == "__main__":
    import uvicorn

    from config import API_HOST, API_PORT

    uvicorn.run("api.main:app", host=API_HOST, port=API_PORT, reload=True)
