"""OpenAI-powered progress update parser (CSV storage)."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Optional

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL
from services.risk_detector import compute_risk, refresh_all_risks
from storage import csv_store
from storage.models import ParsedProjectUpdate, ProgressUpdateResult, Project


def _build_project_context(projects: list[Project]) -> str:
    return "\n".join(
        f"- {p.name} | stage={p.current_stage} | progress={p.progress}% | status={p.status}"
        for p in projects
    )


def _parse_with_llm(text: str, projects: list[Project]) -> list[ParsedProjectUpdate]:
    if not OPENAI_API_KEY:
        return _parse_with_rules(text, projects)

    client = OpenAI(api_key=OPENAI_API_KEY)
    system_prompt = """你是半導體 AI 專案 PMO 助理。解析使用者週報文字，回傳 JSON：
{"updates": [{"project_name":"...", "stage": 5, "progress": 90, "status": "In Progress", "next_action": "...", "summary": "..."}]}
"""
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"已知專案：\n{_build_project_context(projects)}\n\n使用者回報：\n{text}"},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content or "{}")
    items = data.get("updates", []) if isinstance(data, dict) else data
    return [ParsedProjectUpdate(**item) for item in items if isinstance(item, dict)]


def _parse_with_rules(text: str, projects: list[Project]) -> list[ParsedProjectUpdate]:
    import re

    name_map = {p.name.lower(): p.name for p in projects}
    aliases = {
        "cow": "CoW Xray", "cos": "CoS Xray", "duc": "DUC",
        "foundation model": "Foundation Model", "cleanroom": "Cleanroom Monitoring",
        "aoi agent": "AOI Agent", "2/o aoi": "2/O AOI", "2/o": "2/O AOI",
        "sat": "SAT", "icos amd": "ICOS AMD", "icos tsmc": "ICOS TSMC",
    }
    name_map.update(aliases)

    blocks = re.split(r"\n\s*\n", text.strip())
    if len(blocks) == 1:
        blocks = [ln for ln in text.strip().splitlines() if ln.strip()]

    results: list[ParsedProjectUpdate] = []
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        header = lines[0].strip().rstrip(":")
        key = header.lower()
        matched = name_map.get(key)
        if not matched:
            for nk, nv in name_map.items():
                if nk in key or key in nk:
                    matched = nv
                    break
        if not matched:
            continue

        body = " ".join(lines[1:]) if len(lines) > 1 else header
        progress = stage = None
        m = re.search(r"(\d+)\s*%", body)
        if m:
            progress = float(m.group(1))
        m = re.search(r"stage\s*[=:]?\s*(\d+)", body, re.I)
        if m:
            stage = int(m.group(1))
        elif "管理平台" in body or ("串接" in body and "CIM" not in body):
            stage = 5
        elif "CIM" in body or "API" in body:
            stage = 4
        elif "模型" in body or "資料清理" in body:
            stage = 3

        results.append(ParsedProjectUpdate(
            project_name=matched, stage=stage, progress=progress, summary=body[:200],
        ))
    return results


def _resolve_project(name: str) -> Optional[Project]:
    p = csv_store.get_project_by_name(name)
    if p:
        return p
    for proj in csv_store.get_projects():
        if name.lower() in proj.name.lower() or proj.name.lower() in name.lower():
            return proj
    return None


def apply_progress_updates(text: str) -> ProgressUpdateResult:
    projects = csv_store.get_projects()
    parsed = _parse_with_llm(text, projects)
    applied: list[dict] = []
    errors: list[str] = []

    for item in parsed:
        project = _resolve_project(item.project_name)
        if not project:
            errors.append(f"找不到專案：{item.project_name}")
            continue

        stage_before = project.current_stage
        progress_before = project.progress
        updates: dict[str, Any] = {}

        if item.stage is not None:
            updates["current_stage"] = item.stage
        if item.progress is not None:
            updates["progress"] = min(100.0, max(0.0, item.progress))
        if item.status:
            updates["status"] = item.status
        if item.next_action:
            updates["next_action"] = item.next_action
        elif item.stage is not None:
            updates["next_action"] = csv_store.infer_next_action(item.stage)
        if updates.get("progress") == 100:
            updates["status"] = updates.get("status") or "Completed"

        project = csv_store.update_project(project, updates)
        project.risk = compute_risk(project)
        csv_store.save_projects(csv_store.get_projects())

        csv_store.record_project_update(
            project, raw_input=text,
            summary=item.summary or f"更新至 stage {project.current_stage}, {project.progress}%",
            stage_before=stage_before, progress_before=progress_before,
        )
        applied.append(asdict(project) if hasattr(project, "__dataclass_fields__") else project.__dict__)

    refresh_all_risks()
    return ProgressUpdateResult(
        parsed=[asdict(p) if hasattr(p, "__dataclass_fields__") else p.__dict__ for p in parsed],
        applied=applied,
        errors=errors,
    )
