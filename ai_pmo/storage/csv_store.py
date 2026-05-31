"""
CSV-based data storage.

All project data is stored in data/*.csv — no SQLite or server required.
Suitable for Windows local single-user usage.
"""

from __future__ import annotations

import csv
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from config import DATA_DIR, STAGES, STAGE_SUBTASKS
from storage.models import Project, ProjectUpdate, WeeklyReport, WeeklyTask

PROJECTS_CSV = DATA_DIR / "projects.csv"
UPDATES_CSV = DATA_DIR / "project_updates.csv"
TASKS_CSV = DATA_DIR / "weekly_tasks.csv"
REPORTS_CSV = DATA_DIR / "weekly_reports.csv"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _parse_dt(value: str) -> datetime:
    if not value:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.utcnow()


def _parse_date(value: str) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _fmt_dt(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    ensure_data_dir()
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _next_id(rows: list[dict]) -> int:
    if not rows:
        return 1
    return max(int(r.get("id") or 0) for r in rows) + 1


def _row_to_project(row: dict) -> Project:
    return Project(
        id=int(row["id"]),
        name=row["name"],
        customer=row.get("customer", ""),
        process=row.get("process", ""),
        current_stage=int(row.get("current_stage") or 0),
        progress=float(row.get("progress") or 0),
        status=row.get("status", "Not Started"),
        risk=row.get("risk", "LOW"),
        next_action=row.get("next_action", ""),
        due_date=_parse_date(row.get("due_date", "")),
        remark=row.get("remark", ""),
        stage_entered_at=_parse_dt(row.get("stage_entered_at", "")),
        last_updated=_parse_dt(row.get("last_updated", "")),
        created_at=_parse_dt(row.get("created_at", "")),
    )


def _project_to_row(p: Project) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "customer": p.customer,
        "process": p.process,
        "current_stage": p.current_stage,
        "progress": p.progress,
        "status": p.status,
        "risk": p.risk,
        "next_action": p.next_action,
        "due_date": p.due_date.isoformat() if p.due_date else "",
        "remark": p.remark,
        "stage_entered_at": _fmt_dt(p.stage_entered_at),
        "last_updated": _fmt_dt(p.last_updated),
        "created_at": _fmt_dt(p.created_at),
    }


PROJECT_FIELDS = [
    "id", "name", "customer", "process", "current_stage", "progress",
    "status", "risk", "next_action", "due_date", "remark",
    "stage_entered_at", "last_updated", "created_at",
]

UPDATE_FIELDS = [
    "id", "project_id", "project_name", "raw_input", "summary",
    "stage_before", "stage_after", "progress_before", "progress_after", "created_at",
]

TASK_FIELDS = [
    "id", "project_id", "project_name", "week_start", "description", "completed", "created_at",
]

REPORT_FIELDS = ["id", "week_start", "content_md", "created_at"]


def get_projects() -> list[Project]:
    rows = _read_csv(PROJECTS_CSV)
    projects = [_row_to_project(r) for r in rows]
    return sorted(projects, key=lambda p: p.name)


def save_projects(projects: list[Project]) -> None:
    _write_csv(PROJECTS_CSV, PROJECT_FIELDS, [_project_to_row(p) for p in projects])


def get_project_by_id(project_id: int) -> Optional[Project]:
    for p in get_projects():
        if p.id == project_id:
            return p
    return None


def get_project_by_name(name: str) -> Optional[Project]:
    for p in get_projects():
        if p.name == name:
            return p
    return None


def update_project(project: Project, updates: dict) -> Project:
    projects = get_projects()
    stage_changed = False
    for key, value in updates.items():
        if value is not None and hasattr(project, key):
            if key == "current_stage" and value != project.current_stage:
                stage_changed = True
            setattr(project, key, value)
    project.last_updated = datetime.utcnow()
    if stage_changed:
        project.stage_entered_at = datetime.utcnow()
    for i, p in enumerate(projects):
        if p.id == project.id:
            projects[i] = project
            break
    save_projects(projects)
    return project


def record_project_update(
    project: Project,
    raw_input: str,
    summary: str,
    stage_before: int,
    progress_before: float,
) -> ProjectUpdate:
    rows = _read_csv(UPDATES_CSV)
    entry = ProjectUpdate(
        id=_next_id(rows),
        project_id=project.id,
        project_name=project.name,
        raw_input=raw_input,
        summary=summary,
        stage_before=stage_before,
        stage_after=project.current_stage,
        progress_before=progress_before,
        progress_after=project.progress,
        created_at=datetime.utcnow(),
    )
    rows.append({
        "id": entry.id,
        "project_id": entry.project_id,
        "project_name": entry.project_name,
        "raw_input": entry.raw_input,
        "summary": entry.summary,
        "stage_before": entry.stage_before,
        "stage_after": entry.stage_after,
        "progress_before": entry.progress_before,
        "progress_after": entry.progress_after,
        "created_at": _fmt_dt(entry.created_at),
    })
    _write_csv(UPDATES_CSV, UPDATE_FIELDS, rows)
    return entry


def get_week_start(ref: Optional[date] = None) -> date:
    ref = ref or date.today()
    return ref - timedelta(days=ref.weekday())


def get_weekly_tasks(week_start: Optional[date] = None) -> list[WeeklyTask]:
    week_start = week_start or get_week_start()
    ws = week_start.isoformat()
    tasks = []
    for row in _read_csv(TASKS_CSV):
        if row.get("week_start", "")[:10] != ws:
            continue
        tasks.append(WeeklyTask(
            id=int(row["id"]),
            project_id=int(row["project_id"]),
            project_name=row.get("project_name", ""),
            week_start=_parse_date(row["week_start"]) or week_start,
            description=row.get("description", ""),
            completed=row.get("completed", "").lower() in {"true", "1", "yes"},
            created_at=_parse_dt(row.get("created_at", "")),
        ))
    return sorted(tasks, key=lambda t: (t.project_id, t.id))


def generate_weekly_tasks(week_start: Optional[date] = None) -> list[WeeklyTask]:
    week_start = week_start or get_week_start()
    ws = week_start.isoformat()

    # Keep tasks from other weeks, replace this week
    all_rows = _read_csv(TASKS_CSV)
    kept = [r for r in all_rows if r.get("week_start", "")[:10] != ws]
    next_id = _next_id(all_rows)

    created: list[WeeklyTask] = []
    projects = get_projects()

    for project in projects:
        if project.status in {"Completed", "Cancelled"}:
            continue
        stage = project.current_stage
        if project.status == "Planning" or stage == 0:
            stage = 1
        subtasks = STAGE_SUBTASKS.get(stage, STAGE_SUBTASKS.get(1, []))
        for desc in subtasks:
            task = WeeklyTask(
                id=next_id,
                project_id=project.id,
                project_name=project.name,
                week_start=week_start,
                description=desc,
                completed=False,
                created_at=datetime.utcnow(),
            )
            next_id += 1
            created.append(task)
            kept.append({
                "id": task.id,
                "project_id": task.project_id,
                "project_name": task.project_name,
                "week_start": ws,
                "description": task.description,
                "completed": "false",
                "created_at": _fmt_dt(task.created_at),
            })
        if not project.next_action and subtasks:
            update_project(project, {"next_action": subtasks[0]})

    _write_csv(TASKS_CSV, TASK_FIELDS, kept)
    return created


def get_recent_updates(days: int = 7) -> list[ProjectUpdate]:
    since = datetime.utcnow() - timedelta(days=days)
    result = []
    for row in _read_csv(UPDATES_CSV):
        created = _parse_dt(row.get("created_at", ""))
        if created < since:
            continue
        result.append(ProjectUpdate(
            id=int(row["id"]),
            project_id=int(row["project_id"]),
            project_name=row.get("project_name", ""),
            raw_input=row.get("raw_input", ""),
            summary=row.get("summary", ""),
            stage_before=int(row.get("stage_before") or 0),
            stage_after=int(row.get("stage_after") or 0),
            progress_before=float(row.get("progress_before") or 0),
            progress_after=float(row.get("progress_after") or 0),
            created_at=created,
        ))
    return sorted(result, key=lambda u: u.created_at, reverse=True)


def save_weekly_report(week_start: date, content_md: str) -> WeeklyReport:
    rows = _read_csv(REPORTS_CSV)
    report = WeeklyReport(
        id=_next_id(rows),
        week_start=week_start,
        content_md=content_md,
        created_at=datetime.utcnow(),
    )
    rows.append({
        "id": report.id,
        "week_start": week_start.isoformat(),
        "content_md": content_md,
        "created_at": _fmt_dt(report.created_at),
    })
    _write_csv(REPORTS_CSV, REPORT_FIELDS, rows)
    return report


def infer_next_action(stage: int) -> str:
    tasks = STAGE_SUBTASKS.get(stage, [])
    return tasks[0] if tasks else f"推進 {STAGES.get(stage, '下一階段')}"


def seed_projects(force: bool = False) -> int:
    """Create initial CSV files with 10 projects."""
    from storage.seed_data import INITIAL_PROJECTS

    ensure_data_dir()
    if PROJECTS_CSV.exists() and not force:
        return len(get_projects())

    now = datetime.utcnow()
    projects: list[Project] = []
    for i, data in enumerate(INITIAL_PROJECTS):
        projects.append(Project(
            id=i + 1,
            name=data["name"],
            customer=data["customer"],
            process=data["process"],
            current_stage=data["current_stage"],
            progress=data["progress"],
            status=data["status"],
            risk="LOW",
            next_action=data["next_action"],
            due_date=date.today() + timedelta(days=30 + i * 7),
            remark=data["remark"],
            stage_entered_at=now - timedelta(days=i * 5 + 10),
            last_updated=now - timedelta(days=i * 3),
            created_at=now,
        ))
    save_projects(projects)

    # Initialize empty companion files
    if not UPDATES_CSV.exists():
        _write_csv(UPDATES_CSV, UPDATE_FIELDS, [])
    if not TASKS_CSV.exists():
        _write_csv(TASKS_CSV, TASK_FIELDS, [])
    if not REPORTS_CSV.exists():
        _write_csv(REPORTS_CSV, REPORT_FIELDS, [])

    return len(projects)
