"""Folder scanner for defect files."""

from __future__ import annotations

from pathlib import Path

from .models import ScanResult
from .parser import is_defect_file, parse_file


def scan_folder(
    root: str | Path,
    *,
    recursive: bool = True,
    include_hidden: bool = False,
) -> ScanResult:
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {root_path}")

    result = ScanResult(
        root_path=str(root_path),
        scanned_at=ScanResult.now_iso(),
        files_scanned=0,
        defects_found=0,
    )

    iterator = root_path.rglob("*") if recursive else root_path.iterdir()
    for path in iterator:
        if not path.is_file():
            continue
        if not include_hidden and any(part.startswith(".") for part in path.parts):
            continue
        if not is_defect_file(path):
            continue
        result.files_scanned += 1
        try:
            records = parse_file(path)
            result.records.extend(records)
            result.defects_found += len(records)
        except Exception as exc:  # noqa: BLE001 — collect per-file errors for report
            result.errors.append(f"{path}: {exc}")

    return result
