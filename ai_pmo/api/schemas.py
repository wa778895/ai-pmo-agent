"""Pydantic schemas for API request/response."""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    name: str
    customer: str = ""
    process: str = ""
    current_stage: int = 0
    progress: float = 0.0
    status: str = "Not Started"
    risk: str = "LOW"
    next_action: str = ""
    due_date: Optional[date] = None
    remark: str = ""


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdateSchema(BaseModel):
    customer: Optional[str] = None
    process: Optional[str] = None
    current_stage: Optional[int] = None
    progress: Optional[float] = None
    status: Optional[str] = None
    risk: Optional[str] = None
    next_action: Optional[str] = None
    due_date: Optional[date] = None
    remark: Optional[str] = None


class ProjectOut(ProjectBase):
    id: int
    last_updated: datetime
    stage_entered_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class ProgressUpdateRequest(BaseModel):
    text: str = Field(..., description="使用者週報文字，例如多行專案進度")


class ParsedProjectUpdate(BaseModel):
    project_name: str
    stage: Optional[int] = None
    progress: Optional[float] = None
    status: Optional[str] = None
    next_action: Optional[str] = None
    summary: str = ""

    model_config = {"extra": "ignore"}


class ProgressUpdateResponse(BaseModel):
    parsed: List[ParsedProjectUpdate]
    applied: List[ProjectOut]
    errors: List[str] = []


class WeeklyTaskOut(BaseModel):
    id: int
    project_id: int
    project_name: str
    week_start: date
    description: str
    completed: bool

    model_config = {"from_attributes": True}


class WeeklyReportOut(BaseModel):
    id: int
    week_start: date
    content_md: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardCharts(BaseModel):
    progress_bar: dict
    stage_distribution: dict
    risk_distribution: dict
    gantt: dict


class HealthResponse(BaseModel):
    status: str
    project_count: int
