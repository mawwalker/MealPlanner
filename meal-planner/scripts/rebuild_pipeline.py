#!/usr/bin/env python3
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
STEPS = [
    BASE / "import_sources.py",
    BASE / "refine_recipe_pool.py",
    BASE / "build_structured_pool.py",
    BASE / "plan_week.py",
    BASE / "generate_weekly_plan.py",
    BASE / "generate_daily_plan.py",
]


def main() -> None:
    for step in STEPS:
        print(f"==> {step.name}")
        result = subprocess.run(["python3", str(step)], capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.returncode != 0:
            if result.stderr.strip():
                print(result.stderr.strip())
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
