#!/usr/bin/env python3
import subprocess
from pathlib import Path

BASE = Path('/home/dsm/.openclaw/workspace/skills/meal-planner/scripts')
steps = [
    BASE / 'import_sources.py',
    BASE / 'refine_recipe_pool.py',
    BASE / 'build_structured_pool.py',
    BASE / 'plan_week.py',
    BASE / 'generate_daily_plan.py',
]

for step in steps:
    print(f'==> {step.name}')
    result = subprocess.run(['python3', str(step)], capture_output=True, text=True)
    print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr.strip())
        raise SystemExit(result.returncode)
