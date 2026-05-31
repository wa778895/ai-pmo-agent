"""Parse defect records from JSON/YAML files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import DefectRecord

DEFECT_EXTENSIONS = {".json", ".yaml", ".yml"}
DEFECT_FILENAMES = {
    "defect.json",
    "defects.json",
    "bug.json",
    "bugs.json",
    "issue.json",
    "issues.json",
}


def _load_text(path: Path) -> Any:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "PyYAML is required for .yaml/.yml files. Install with: pip install pyyaml"
            ) from exc
        return yaml.safe_load(text)
    raise ValueError(f"Unsupported format: {path.suffix}")


def _normalize_payload(payload: Any, source_file: str) -> list[DefectRecord]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [
            DefectRecord.from_dict(item, source_file=source_file)
            for item in payload
            if isinstance(item, dict)
        ]
    if isinstance(payload, dict):
        if "defects" in payload and isinstance(payload["defects"], list):
            return _normalize_payload(payload["defects"], source_file)
        if "issues" in payload and isinstance(payload["issues"], list):
            return _normalize_payload(payload["issues"], source_file)
        return [DefectRecord.from_dict(payload, source_file=source_file)]
    return []


def is_defect_file(path: Path) -> bool:
    name = path.name.lower()
    if name in DEFECT_FILENAMES:
        return True
    if path.suffix.lower() in DEFECT_EXTENSIONS and "defect" in name:
        return True
    if path.suffix.lower() in DEFECT_EXTENSIONS and name.startswith("def-"):
        return True
    if path.parent.name.lower() in {"defects", "bugs", "issues"}:
        return path.suffix.lower() in DEFECT_EXTENSIONS
    return False


def parse_file(path: Path) -> list[DefectRecord]:
    payload = _load_text(path)
    return _normalize_payload(payload, source_file=str(path.resolve()))
