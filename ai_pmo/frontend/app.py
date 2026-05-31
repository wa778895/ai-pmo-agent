"""Legacy frontend — redirects to standalone app.py."""

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[1] / "app.py"))
