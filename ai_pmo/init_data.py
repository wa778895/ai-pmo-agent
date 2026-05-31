"""Initialize CSV data files (CLI)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.risk_detector import refresh_all_risks
from storage import csv_store


def main(force: bool = False) -> None:
    count = csv_store.seed_projects(force=force)
    refresh_all_risks()
    print(f"CSV ready: {count} projects")
    print(f"  → {csv_store.PROJECTS_CSV}")
    print(f"  → {csv_store.UPDATES_CSV}")
    print(f"  → {csv_store.TASKS_CSV}")
    print(f"  → {csv_store.REPORTS_CSV}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
