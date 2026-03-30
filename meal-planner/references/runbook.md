# Runbook

## Default day-to-day usage

Most of the time, do not rebuild the full recipe pipeline.

Preferred operating model:
1. once per week, generate or refresh the weekly plan
2. each day, render today's recommendation from the saved week

Use the full rebuild path only when recipe sources or filtering rules changed.

## Agent request mapping

Use this mapping by default:

- User asks for `本周吃什么`:
  run `plan_week.py` then `generate_weekly_plan.py`

- User asks for `今天吃什么`:
  run `generate_daily_plan.py`
  if current week is missing or stale, run `plan_week.py` first

- User says `以后不要这个菜`:
  update `diet/preferences.json` or run `add_blacklist.py`, then run `rebuild_pipeline.py`

- User changes recipe sources / filtering rules / blacklist:
  run `rebuild_pipeline.py`

## Full rebuild

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/rebuild_pipeline.py
```

This performs:
1. source import
2. recipe refinement
3. structured pool build
4. weekly planning
5. weekly rendering
6. daily rendering

## Weekly refresh

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/plan_week.py
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/generate_weekly_plan.py
```

Use this when:
- a new week begins
- `diet/state.json` is missing
- the saved week is stale
- the pool was just rebuilt

## Daily rendering

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/generate_daily_plan.py
```

Use this for routine daily use.
It should read from the persisted weekly state rather than re-planning the week.

## Add blacklist rule

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/add_blacklist.py --title "宫保鸡丁的做法"
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/rebuild_pipeline.py
```

## Expected outputs

- new imported/refined/pool files in `diet/`
- updated [`/home/dsm/workspace/MealPlanner/diet/state.json`](/home/dsm/workspace/MealPlanner/diet/state.json)
- updated [`/home/dsm/workspace/MealPlanner/diet/weekly_meal_plan.md`](/home/dsm/workspace/MealPlanner/diet/weekly_meal_plan.md)
