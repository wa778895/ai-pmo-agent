"""Data models for defect records."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class DefectStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    CLOSED = "closed"
    WONT_FIX = "wont_fix"
    UNKNOWN = "unknown"


@dataclass
class DefectRecord:
    id: str
    title: str
    severity: str = Severity.UNKNOWN.value
    status: str = DefectStatus.UNKNOWN.value
    category: str = "uncategorized"
    description: str = ""
    source_file: str = ""
    component: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None
    reporter: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any], source_file: str = "") -> DefectRecord:
        known = {
            "id",
            "title",
            "severity",
            "status",
            "category",
            "description",
            "component",
            "tags",
            "created_at",
            "updated_at",
            "reporter",
        }
        extra = {k: v for k, v in data.items() if k not in known}
        defect_id = str(data.get("id") or data.get("defect_id") or "")
        if not defect_id and source_file:
            defect_id = source_file
        return cls(
            id=defect_id,
            title=str(data.get("title") or data.get("name") or "Untitled"),
            severity=str(data.get("severity", Severity.UNKNOWN.value)).lower(),
            status=str(data.get("status", DefectStatus.UNKNOWN.value)).lower(),
            category=str(data.get("category") or data.get("type") or "uncategorized"),
            description=str(data.get("description") or data.get("summary") or ""),
            source_file=source_file,
            component=str(data.get("component") or data.get("module") or ""),
            tags=list(data.get("tags") or []),
            created_at=data.get("created_at") or data.get("date"),
            updated_at=data.get("updated_at"),
            reporter=str(data.get("reporter") or data.get("author") or ""),
            extra=extra,
        )


@dataclass
class ScanResult:
    root_path: str
    scanned_at: str
    files_scanned: int
    defects_found: int
    records: list[DefectRecord] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @staticmethod
    def now_iso() -> str:
        return datetime.now().isoformat(timespec="seconds")
