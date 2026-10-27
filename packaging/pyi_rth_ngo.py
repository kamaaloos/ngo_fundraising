"""Runtime hook: production-safe defaults for the frozen Windows build."""

import os
import sys

# Never auto-load demo data in customer builds.
os.environ.setdefault("NGO_SKIP_DEMO_SEED", "1")
os.environ.pop("NGO_SEED_DEMO", None)

# Ensure the frozen app can import the `app` package next to the executable.
if getattr(sys, "frozen", False):
    base = getattr(sys, "_MEIPASS", None)
    if base and base not in sys.path:
        sys.path.insert(0, base)
