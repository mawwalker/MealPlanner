# Runbook

## Simplified operating model

The default operating model is:
- maintain a reusable recipe pool
- generate one weekly plan
- generate one weekly shopping recommendation
- generate daily execution reminders from the saved week plan

Do not manage inventory or purchased-item state by default.

## Full rebuild

Run when source repositories or parsing/scoring rules change:

```bash
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/rebuild_pipeline.py
```

This runs:
- `import_sources.py`
- `refine_recipe_pool.py`
- `build_structured_pool.py`
- `plan_week.py`
- `generate_daily_plan.py`

## Weekly planning path

Use:
```bash
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/plan_week.py
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/generate_weekly_plan.py
```

## Daily reminder path

Use:
```bash
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/plan_week.py
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/generate_daily_plan.py
```

`plan_week.py` should preserve an already-generated week when still current.

Delivery rule:
- on Monday, `generate_daily_plan.py` should output the weekly plan and weekly shopping recommendation first, then today's plan
- on non-Monday days, it may output only today's plan
