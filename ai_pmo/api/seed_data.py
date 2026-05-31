"""Seed initial project data."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from api.models import Project

INITIAL_PROJECTS = [
    {
        "name": "2/O AOI",
        "customer": "新進",
        "process": "AOI",
        "current_stage": 1,
        "progress": 10.0,
        "status": "In Progress",
        "remark": "機台尚未進機",
        "next_action": "確認需求文件",
    },
    {
        "name": "DUC",
        "customer": "新進",
        "process": "AOI",
        "current_stage": 4,
        "progress": 80.0,
        "status": "In Progress",
        "remark": "待確認管理平台串接",
        "next_action": "確認 API 格式",
    },
    {
        "name": "CoW Xray",
        "customer": "新進",
        "process": "Xray",
        "current_stage": 5,
        "progress": 90.0,
        "status": "In Progress",
        "remark": "待確認正式上線",
        "next_action": "確認正式上線計畫",
    },
    {
        "name": "CoS Xray",
        "customer": "新進",
        "process": "Xray",
        "current_stage": 5,
        "progress": 90.0,
        "status": "In Progress",
        "remark": "待確認正式上線",
        "next_action": "確認正式上線計畫",
    },
    {
        "name": "SAT",
        "customer": "新進",
        "process": "SAT",
        "current_stage": 0,
        "progress": 0.0,
        "status": "Not Started",
        "remark": "尚未開始",
        "next_action": "啟動需求商談",
    },
    {
        "name": "ICOS AMD",
        "customer": "AMD",
        "process": "AOI",
        "current_stage": 5,
        "progress": 70.0,
        "status": "Waiting",
        "remark": "待討論正式格式",
        "next_action": "確認管理平台 API 規格",
    },
    {
        "name": "ICOS TSMC",
        "customer": "TSMC",
        "process": "AOI",
        "current_stage": 5,
        "progress": 100.0,
        "status": "Completed",
        "remark": "格式尚未標準化",
        "next_action": "文件歸檔",
    },
    {
        "name": "Foundation Model",
        "customer": "Internal",
        "process": "AI/ML",
        "current_stage": 3,
        "progress": 30.0,
        "status": "In Progress",
        "remark": "模型開發中",
        "next_action": "完成資料清理與前處理",
    },
    {
        "name": "Cleanroom Monitoring",
        "customer": "Internal",
        "process": "Monitoring",
        "current_stage": 3,
        "progress": 30.0,
        "status": "In Progress",
        "remark": "監控功能開發中",
        "next_action": "完成模型訓練與驗證",
    },
    {
        "name": "AOI Agent",
        "customer": "Internal",
        "process": "AOI",
        "current_stage": 0,
        "progress": 10.0,
        "status": "Planning",
        "remark": "流程設計中",
        "next_action": "確認需求文件",
    },
]


def seed_projects(db: Session, force: bool = False) -> int:
    """Insert initial projects if table is empty (or force reseed)."""
    if force:
        db.query(Project).delete()
        db.commit()

    existing = db.query(Project).count()
    if existing > 0:
        return existing

    now = datetime.utcnow()
    for i, data in enumerate(INITIAL_PROJECTS):
        # Stagger last_updated for demo risk detection variety
        last_updated = now - timedelta(days=i * 3)
        stage_entered = now - timedelta(days=i * 5 + 10)

        project = Project(
            **data,
            risk="LOW",
            due_date=date.today() + timedelta(days=30 + i * 7),
            last_updated=last_updated,
            stage_entered_at=stage_entered,
            created_at=now,
        )
        db.add(project)

    db.commit()
    return len(INITIAL_PROJECTS)
