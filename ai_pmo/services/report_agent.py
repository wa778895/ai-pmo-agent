"""Weekly report generation (CSV storage)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, STAGES
from services.risk_detector import compute_risk
from storage import csv_store
from storage.models import Project


def _project_snapshot(projects: list[Project]) -> str:
    lines = []
    for p in projects:
        stage_name = STAGES.get(p.current_stage, str(p.current_stage))
        risk = compute_risk(p)
        lines.append(
            f"| {p.name} | {p.customer} | {p.process} | {stage_name} | "
            f"{p.progress}% | {p.status} | {risk} | {p.remark} |"
        )
    header = "| 專案 | 客戶 | 製程 | 階段 | 進度 | 狀態 | 風險 | 備註 |\n|---|---|---|---|---|---|---|---|"
    return header + "\n" + "\n".join(lines)


def generate_weekly_report_md(week_start: Optional[date] = None) -> str:
    week_start = week_start or csv_store.get_week_start()
    projects = csv_store.get_projects()
    recent = csv_store.get_recent_updates(days=7)
    tasks = csv_store.get_weekly_tasks(week_start)

    risk_projects = [p for p in projects if compute_risk(p) in {"HIGH", "CRITICAL"}]
    completed = [p for p in projects if p.status == "Completed" or p.progress >= 100]
    in_progress = [p for p in projects if p.status not in {"Completed", "Not Started", "Cancelled"}]

    updates_text = "\n".join(
        f"- **{u.project_name}**: {u.summary} (stage {u.stage_before}→{u.stage_after}, "
        f"{u.progress_before}%→{u.progress_after}%)"
        for u in recent[:15]
    ) or "- 本週尚無結構化更新紀錄"

    tasks_text = "\n".join(
        f"- [{t.project_name}] {t.description}" for t in tasks[:30]
    ) or "- 請先產生本週待辦事項"

    template = f"""# AI PMO 週報

**週次起始日：** {week_start.isoformat()}

## 專案摘要

共 {len(projects)} 個專案，進行中 {len(in_progress)} 個，已完成 {len(completed)} 個。

{_project_snapshot(projects)}

## 風險專案

"""
    if risk_projects:
        for p in risk_projects:
            template += f"- **{p.name}** [{compute_risk(p)}]: {p.remark} (最後更新: {p.last_updated.date()})\n"
    else:
        template += "- 本週無高風險專案\n"

    template += f"""
## 本週完成事項

{updates_text}

## 下週計畫

{tasks_text}
"""

    if not OPENAI_API_KEY:
        return template

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "你是半導體 AI PMO 週報撰寫專家。整理成繁體中文 Markdown，不虛構數據。"},
            {"role": "user", "content": f"請優化以下週報草稿：\n\n{template}"},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or template


def create_and_save_report(week_start: Optional[date] = None) -> str:
    week_start = week_start or csv_store.get_week_start()
    content = generate_weekly_report_md(week_start)
    csv_store.save_weekly_report(week_start, content)
    return content
