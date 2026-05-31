"""Data models for CSV storage."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Project:
    id: int
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
    stage_entered_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProjectUpdate:
    id: int
    project_id: int
    project_name: str = ""
    raw_input: str = ""
    summary: str = ""
    stage_before: int = 0
    stage_after: int = 0
    progress_before: float = 0.0
    progress_after: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WeeklyTask:
    id: int
    project_id: int
    project_name: str = ""
    week_start: date = field(default_factory=date.today)
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WeeklyReport:
    id: int
    week_start: date
    content_md: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ParsedProjectUpdate:
    project_name: str
    stage: Optional[int] = None
    progress: Optional[float] = None
    status: Optional[str] = None
    next_action: Optional[str] = None
    summary: str = ""


@dataclass
class ProgressUpdateResult:
    parsed: list
    applied: list
    errors: list
