"""Runtime hook: production-safe defaults for the frozen Windows build."""

import os
import sys
import tempfile
from pathlib import Path


# Never auto-load demo data in customer builds.
os.environ.setdefault("NGO_SKIP_DEMO_SEED", "1")
os.environ.pop("NGO_SEED_DEMO", None)

# Matplotlib needs a writable config/cache dir inside frozen apps.
if getattr(sys, "frozen", False):
    mpl_dir = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / (
        "NGOFundraisingManager" if os.name == "nt" else "ngo-fundraising"
    ) / "mplconfig"
    try:
        mpl_dir.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", str(mpl_dir))
    except OSError:
        os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())
    os.environ.setdefault("MPLBACKEND", "QtAgg")

# Ensure the frozen app can import the `app` package next to the executable.
if getattr(sys, "frozen", False):
    base = getattr(sys, "_MEIPASS", None)
    if base and base not in sys.path:
        sys.path.insert(0, base)
