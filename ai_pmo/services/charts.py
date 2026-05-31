"""Plotly chart generation for executive dashboard."""

from __future__ import annotations

import json
from datetime import timedelta

from config import STAGES
from services.risk_detector import compute_risk
from storage import csv_store


def _fig_to_dict(fig) -> dict:
    return json.loads(fig.to_json())


def _stage_label(stage: int) -> str:
    return STAGES.get(stage, f"Stage {stage}")


def build_progress_bar_chart(projects: list) -> dict:
    import plotly.graph_objects as go

    active = [p for p in projects if p.status != "Cancelled"]
    active.sort(key=lambda x: x.progress, reverse=True)
    fig = go.Figure(go.Bar(
        x=[p.progress for p in active], y=[p.name for p in active],
        orientation="h", text=[f"{p.progress:.0f}%" for p in active],
        textposition="outside",
        marker=dict(color=[p.progress for p in active], colorscale="Blues", showscale=False),
    ))
    fig.update_layout(title="專案進度", xaxis_title="Progress (%)", height=max(400, len(active) * 40),
                      margin=dict(l=120), xaxis=dict(range=[0, 110]))
    return _fig_to_dict(fig)


def build_stage_distribution(projects: list) -> dict:
    import plotly.express as px

    stage_counts: dict[str, int] = {}
    for p in projects:
        label = _stage_label(p.current_stage)
        stage_counts[label] = stage_counts.get(label, 0) + 1
    fig = px.pie(names=list(stage_counts.keys()), values=list(stage_counts.values()),
                 title="專案階段分布", hole=0.35)
    fig.update_layout(height=450)
    return _fig_to_dict(fig)


def build_risk_distribution(projects: list) -> dict:
    import plotly.graph_objects as go

    risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for p in projects:
        risk_counts[compute_risk(p)] += 1
    colors = {"LOW": "#2ecc71", "MEDIUM": "#f39c12", "HIGH": "#e74c3c", "CRITICAL": "#8e044b"}
    fig = go.Figure(go.Bar(
        x=list(risk_counts.keys()), y=list(risk_counts.values()),
        marker_color=[colors[k] for k in risk_counts], text=list(risk_counts.values()), textposition="auto",
    ))
    fig.update_layout(title="專案風險分布", height=400)
    return _fig_to_dict(fig)


def build_gantt_chart(projects: list) -> dict:
    import plotly.express as px
    import plotly.graph_objects as go

    rows = []
    for p in projects:
        start = p.created_at.date()
        end = p.due_date or (p.last_updated.date() + timedelta(days=14))
        if end < start:
            end = start + timedelta(days=7)
        rows.append(dict(Project=p.name, Start=start.isoformat(), Finish=end.isoformat(),
                         Stage=_stage_label(p.current_stage), Progress=p.progress))
    if not rows:
        fig = go.Figure()
        fig.update_layout(title="甘特圖（無資料）", height=400)
        return _fig_to_dict(fig)
    fig = px.timeline(rows, x_start="Start", x_end="Finish", y="Project", color="Stage", title="專案甘特圖")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=max(450, len(rows) * 35))
    return _fig_to_dict(fig)


def build_all_charts() -> dict:
    projects = csv_store.get_projects()
    return {
        "progress_bar": build_progress_bar_chart(projects),
        "stage_distribution": build_stage_distribution(projects),
        "risk_distribution": build_risk_distribution(projects),
        "gantt": build_gantt_chart(projects),
    }
