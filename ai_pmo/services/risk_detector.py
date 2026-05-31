"""Risk detection service."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from storage import csv_store
from storage.models import Project
from config import RISK_STAGE_STUCK_DAYS, RISK_STALE_DAYS


def compute_risk(project: Project, now: Optional[datetime] = None) -> str:
    now = now or datetime.utcnow()
    days_since_update = (now - project.last_updated).days
    days_in_stage = (now - project.stage_entered_at).days

    if project.status in {"Completed", "Cancelled"}:
        return "LOW"
    if days_in_stage > RISK_STAGE_STUCK_DAYS:
        return "CRITICAL"
    if days_since_update > RISK_STALE_DAYS:
        return "HIGH"
    if project.progress < 30 and project.current_stage >= 3:
        return "MEDIUM"
    if project.progress < 50 and project.current_stage >= 4:
        return "MEDIUM"
    return "LOW"


def refresh_all_risks() -> list[Project]:
    projects = csv_store.get_projects()
    for p in projects:
        p.risk = compute_risk(p)
    csv_store.save_projects(projects)
    return projects
