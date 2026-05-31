"""Executive dashboard chart routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import DashboardCharts
from services.charts import build_all_charts

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/charts", response_model=DashboardCharts)
def get_dashboard_charts(db: Session = Depends(get_db)):
    charts = build_all_charts(db)
    return DashboardCharts(**charts)
