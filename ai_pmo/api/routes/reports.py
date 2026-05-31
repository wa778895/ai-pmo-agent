"""Progress update and weekly report routes."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api import crud
from api.database import get_db
from api.schemas import ProgressUpdateRequest, ProgressUpdateResponse, WeeklyReportOut
from services.progress_agent import apply_progress_updates
from services.report_agent import create_and_save_report, generate_weekly_report_md

router = APIRouter(tags=["agents"])


@router.post("/updates/progress", response_model=ProgressUpdateResponse)
def submit_progress_update(body: ProgressUpdateRequest, db: Session = Depends(get_db)):
    return apply_progress_updates(db, body.text)


@router.get("/reports/weekly/preview")
def preview_weekly_report(
    week_start: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    content = generate_weekly_report_md(db, week_start)
    return {"week_start": (week_start or crud.get_week_start()).isoformat(), "content_md": content}


@router.post("/reports/weekly/generate", response_model=WeeklyReportOut)
def generate_weekly_report(
    week_start: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    week_start = week_start or crud.get_week_start()
    content = create_and_save_report(db, week_start)
    report = crud.get_latest_weekly_report(db)
    assert report is not None
    return report
