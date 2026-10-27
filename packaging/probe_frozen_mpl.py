"""Run inside the frozen app tree to verify matplotlib imports.

Usage (from repo root, after PyInstaller build):

    .\\.venv\\Scripts\\python.exe packaging\\probe_frozen_mpl.py
"""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERNAL = ROOT / "dist" / "NGOFundraising" / "_internal"


def main() -> int:
    if not INTERNAL.exists():
        print("Missing", INTERNAL)
        return 1

    # Mimic frozen layout: prefer _internal packages on sys.path.
    sys.path.insert(0, str(INTERNAL))
    os.environ.setdefault(
        "MPLCONFIGDIR",
        str(Path(os.environ.get("LOCALAPPDATA", ".")) / "NGOFundraisingManager" / "mplconfig"),
    )
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLBACKEND", "QtAgg")

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    try:
        import matplotlib

        print("matplotlib", matplotlib.__version__, "from", matplotlib.__file__)
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure

        fig = Figure(figsize=(3, 2))
        canvas = FigureCanvasQTAgg(fig)
        print("QtAgg canvas OK", type(canvas))
        return 0
    except Exception:
        traceback.print_exc()
        return 2
    finally:
        app.quit()


if __name__ == "__main__":
    raise SystemExit(main())
