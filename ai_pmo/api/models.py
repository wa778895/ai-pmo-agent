"""SQLAlchemy ORM models (SQLAlchemy 1.4+ compatible)."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from api.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False)
    customer = Column(String(100), default="")
    process = Column(String(50), default="")
    current_stage = Column(Integer, default=0)
    progress = Column(Float, default=0.0)
    status = Column(String(50), default="Not Started")
    risk = Column(String(50), default="LOW")
    next_action = Column(Text, default="")
    due_date = Column(Date, nullable=True)
    remark = Column(Text, default="")
    stage_entered_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    updates = relationship("ProjectUpdate", back_populates="project")
    tasks = relationship("WeeklyTask", back_populates="project")


class ProjectUpdate(Base):
    __tablename__ = "project_updates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    raw_input = Column(Text, default="")
    summary = Column(Text, default="")
    stage_before = Column(Integer, default=0)
    stage_after = Column(Integer, default=0)
    progress_before = Column(Float, default=0.0)
    progress_after = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="updates")


class WeeklyTask(Base):
    __tablename__ = "weekly_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    week_start = Column(Date, nullable=False)
    content_md = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
