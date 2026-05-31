"""Weekly tasks API routes."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api import crud
from api.database import get_db
from api.schemas import WeeklyTaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/weekly", response_model=list[WeeklyTaskOut])
def list_weekly_tasks(
    week_start: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    tasks = crud.get_weekly_tasks(db, week_start)
    result = []
    for t in tasks:
        result.append(
            WeeklyTaskOut(
                id=t.id,
                project_id=t.project_id,
                project_name=t.project.name,
                week_start=t.week_start,
                description=t.description,
                completed=t.completed,
            )
        )
    return result


@router.post("/weekly/generate", response_model=list[WeeklyTaskOut])
def generate_weekly_tasks(
    week_start: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    tasks = crud.generate_weekly_tasks(db, week_start)
    return [
        WeeklyTaskOut(
            id=t.id,
            project_id=t.project_id,
            project_name=t.project.name,
            week_start=t.week_start,
            description=t.description,
            completed=t.completed,
        )
        for t in tasks
    ]
