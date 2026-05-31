"""Project API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api import crud
from api.database import get_db
from api.schemas import ProjectCreate, ProjectOut, ProjectUpdateSchema
from services.risk_detector import refresh_all_risks

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    refresh_all_risks(db)
    return crud.get_projects(db)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(body: ProjectCreate, db: Session = Depends(get_db)):
    if crud.get_project_by_name(db, body.name):
        raise HTTPException(status_code=409, detail="Project name already exists")
    return crud.create_project(db, body.model_dump())


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, body: ProjectUpdateSchema, db: Session = Depends(get_db)):
    project = crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    return crud.update_project(db, project, data)


@router.post("/refresh-risks", response_model=list[ProjectOut])
def refresh_risks(db: Session = Depends(get_db)):
    return refresh_all_risks(db)
