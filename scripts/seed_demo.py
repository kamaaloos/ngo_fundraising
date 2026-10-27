"""Load demo projects/donors into the local database (developer / QA only).

Customer builds never auto-seed. Use this script only on a throwaway DB.

Usage (from project folder, venv active):

    python scripts/seed_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.database import init_db
from app.db.seed import seed_demo_data


def main() -> int:
    init_db()
    result = seed_demo_data(force=True)
    print("Demo seed result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
