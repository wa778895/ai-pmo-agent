"""Database CRUD operations."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from api.models import Project, ProjectUpdate, WeeklyReport, WeeklyTask
from config import STAGES, STAGE_SUBTASKS


def get_projects(db: Session) -> list[Project]:
    return db.query(Project).order_by(Project.name).all()


def get_project_by_id(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def get_project_by_name(db: Session, name: str) -> Project | None:
    return db.query(Project).filter(Project.name == name).first()


def create_project(db: Session, data: dict) -> Project:
    project = Project(**data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project: Project, data: dict) -> Project:
    stage_changed = False
    if "current_stage" in data and data["current_stage"] != project.current_stage:
        stage_changed = True

    for key, value in data.items():
        if value is not None and hasattr(project, key):
            setattr(project, key, value)

    project.last_updated = datetime.utcnow()
    if stage_changed:
        project.stage_entered_at = datetime.utcnow()

    db.commit()
    db.refresh(project)
    return project


def record_project_update(
    db: Session,
    project: Project,
    raw_input: str,
    summary: str,
    stage_before: int,
    progress_before: float,
) -> ProjectUpdate:
    entry = ProjectUpdate(
        project_id=project.id,
        raw_input=raw_input,
        summary=summary,
        stage_before=stage_before,
        stage_after=project.current_stage,
        progress_before=progress_before,
        progress_after=project.progress,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_week_start(ref: date | None = None) -> date:
    """Return Monday of the week containing ref (or today)."""
    ref = ref or date.today()
    return ref - timedelta(days=ref.weekday())


def get_weekly_tasks(db: Session, week_start: date | None = None) -> list[WeeklyTask]:
    week_start = week_start or get_week_start()
    return (
        db.query(WeeklyTask)
        .filter(WeeklyTask.week_start == week_start)
        .order_by(WeeklyTask.project_id, WeeklyTask.id)
        .all()
    )


def generate_weekly_tasks(db: Session, week_start: date | None = None) -> list[WeeklyTask]:
    """Generate tasks for all active projects based on current stage."""
    week_start = week_start or get_week_start()

    # Remove existing tasks for this week before regenerating
    db.query(WeeklyTask).filter(WeeklyTask.week_start == week_start).delete()
    db.commit()

    created: list[WeeklyTask] = []
    for project in get_projects(db):
        if project.status in {"Completed", "Cancelled"}:
            continue

        stage = max(project.current_stage, 1) if project.current_stage == 0 else project.current_stage
        if project.status == "Planning" or project.current_stage == 0:
            stage = 1

        subtasks = STAGE_SUBTASKS.get(stage, STAGE_SUBTASKS.get(1, []))
        for desc in subtasks:
            task = WeeklyTask(
                project_id=project.id,
                week_start=week_start,
                description=desc,
                completed=False,
            )
            db.add(task)
            created.append(task)

        # Set next_action on project if empty
        if not project.next_action and subtasks:
            project.next_action = subtasks[0]

    db.commit()
    for t in created:
        db.refresh(t)
    return created


def save_weekly_report(db: Session, week_start: date, content_md: str) -> WeeklyReport:
    report = WeeklyReport(week_start=week_start, content_md=content_md)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_latest_weekly_report(db: Session) -> WeeklyReport | None:
    return db.query(WeeklyReport).order_by(WeeklyReport.created_at.desc()).first()


def get_recent_updates(db: Session, days: int = 7) -> list[ProjectUpdate]:
    since = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(ProjectUpdate)
        .filter(ProjectUpdate.created_at >= since)
        .order_by(ProjectUpdate.created_at.desc())
        .all()
    )


def infer_next_action(stage: int) -> str:
    tasks = STAGE_SUBTASKS.get(stage, [])
    return tasks[0] if tasks else f"推進 {STAGES.get(stage, '下一階段')}"
