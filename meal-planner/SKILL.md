---
name: meal-planner
description: Curate a large multi-source home-cooking recipe pool, classify it into planning-ready buckets, generate a balanced weekly meal plan, and render daily reminders. Use when the user wants recipe-pool building, home-cooking filtering, weekly meal planning, or daily menu delivery from GitHub cookbook sources.
---

# Meal Planner

Use this skill when the task is not "pick a few dishes right now", but "maintain a reusable recipe pool and plan a real week of home cooking from it".

The system is built around four layers:
- source import from cookbook repositories
- recipe feature extraction and practical filtering
- grouped meal pool generation
- weekly planning plus daily reminder rendering

## Default usage

For normal day-to-day use, treat this skill as a `weekly plan + daily reminder` system.

Default behavior:
- at the start of a new week, generate or refresh the weekly plan
- on normal days, only render today's recommendation from saved state
- do not rebuild the recipe pool unless sources, blacklist rules, or filtering logic changed

If the user simply asks for today's meals or this week's meals, prefer the persisted week state instead of re-curating the whole recipe pool.

## Agent playbook

When another agent uses this skill, follow these defaults.

### If the user asks "这周吃什么" / "生成本周计划"

Do:
1. run `plan_week.py`
2. run `generate_weekly_plan.py`
3. return the rendered weekly plan

Do not:
- rebuild the recipe pool by default
- re-import source repositories by default

### If the user asks "今天吃什么" / "生成今日推荐"

Do:
1. ensure a current week exists, running `plan_week.py` only if the saved week is missing or stale
2. run `generate_daily_plan.py`
3. return today's rendered recommendation

Do not:
- regenerate the whole week every day
- rebuild the recipe pool for normal daily usage

### If the user says "以后不要这个菜"

Do:
1. add a blacklist rule to [`/home/dsm/workspace/MealPlanner/diet/preferences.json`](/home/dsm/workspace/MealPlanner/diet/preferences.json)
2. run the full rebuild pipeline
3. regenerate the week if needed

Prefer:
- `exactTitles` when the user names one specific dish
- `titleKeywords` when the user means a dish family such as `鸡爪`
- `sourcePaths` only when the exact source entry matters

### If the user asks to refresh the recipe pool or changes source/filter rules

Do:
1. update preferences or source/filter logic as needed
2. run `rebuild_pipeline.py`

Use the full rebuild path only for data/pool changes, not routine daily requests.

## Planning assumptions

Default user profile:
- adult male, maintenance-oriented
- lunch is the main cooking session
- dinner usually reuses lunch
- breakfast is simpler and template-based
- target is practical, balanced home cooking, not restaurant recreation

Planning principles:
- main dishes should be real lunch anchors, not sauces, condiments, or thin egg-only dishes
- side dishes should complement the main and improve weekly vegetable balance
- weekly planning should vary proteins and avoid repeating the same dishes too often
- the plan should be stable within the week and reused for daily reminders

## Current sources

Supported cookbook repositories:
- `Anduin2017/HowToCook`
- `Gar-b-age/CookLikeHOC`

Source policy:
- `HowToCook` is the primary home-cooking source
- `CookLikeHOC` is supplemental and should be down-ranked when entries depend on chain-kitchen bases, prebuilt sauces, or semi-finished components

## Canonical files

Generated data lives in [`/home/dsm/workspace/MealPlanner/diet/imported_recipes.json`](/home/dsm/workspace/MealPlanner/diet/imported_recipes.json), [`/home/dsm/workspace/MealPlanner/diet/refined_recipe_pool.json`](/home/dsm/workspace/MealPlanner/diet/refined_recipe_pool.json), [`/home/dsm/workspace/MealPlanner/diet/structured_recipe_pool.json`](/home/dsm/workspace/MealPlanner/diet/structured_recipe_pool.json), [`/home/dsm/workspace/MealPlanner/diet/meal_pool.json`](/home/dsm/workspace/MealPlanner/diet/meal_pool.json), and [`/home/dsm/workspace/MealPlanner/diet/state.json`](/home/dsm/workspace/MealPlanner/diet/state.json).

Human-readable output lives in [`/home/dsm/workspace/MealPlanner/diet/weekly_meal_plan.md`](/home/dsm/workspace/MealPlanner/diet/weekly_meal_plan.md).

User preference overrides live in [`/home/dsm/workspace/MealPlanner/diet/preferences.json`](/home/dsm/workspace/MealPlanner/diet/preferences.json).

## Scripts

- [`/home/dsm/workspace/MealPlanner/meal-planner/scripts/import_sources.py`](/home/dsm/workspace/MealPlanner/meal-planner/scripts/import_sources.py)
  Imports only recipe markdown from supported repositories.
- [`/home/dsm/workspace/MealPlanner/meal-planner/scripts/refine_recipe_pool.py`](/home/dsm/workspace/MealPlanner/meal-planner/scripts/refine_recipe_pool.py)
  Scores, filters, and deduplicates imported recipes.
- [`/home/dsm/workspace/MealPlanner/meal-planner/scripts/build_structured_pool.py`](/home/dsm/workspace/MealPlanner/meal-planner/scripts/build_structured_pool.py)
  Builds planning-ready grouped pools: mains, sides, soups, breakfast templates.
- [`/home/dsm/workspace/MealPlanner/meal-planner/scripts/plan_week.py`](/home/dsm/workspace/MealPlanner/meal-planner/scripts/plan_week.py)
  Generates the current week's plan and persists it.
- [`/home/dsm/workspace/MealPlanner/meal-planner/scripts/generate_weekly_plan.py`](/home/dsm/workspace/MealPlanner/meal-planner/scripts/generate_weekly_plan.py)
  Renders the saved weekly plan.
- [`/home/dsm/workspace/MealPlanner/meal-planner/scripts/generate_daily_plan.py`](/home/dsm/workspace/MealPlanner/meal-planner/scripts/generate_daily_plan.py)
  Renders today's reminder from persisted state.
- [`/home/dsm/workspace/MealPlanner/meal-planner/scripts/rebuild_pipeline.py`](/home/dsm/workspace/MealPlanner/meal-planner/scripts/rebuild_pipeline.py)
  Runs the full import -> refine -> pool build -> weekly plan -> render pipeline.
- [`/home/dsm/workspace/MealPlanner/meal-planner/scripts/add_blacklist.py`](/home/dsm/workspace/MealPlanner/meal-planner/scripts/add_blacklist.py)
  Adds user blacklist rules into `diet/preferences.json`.

## Blacklist entry

If the user says a dish should never be suggested again, add it to [`/home/dsm/workspace/MealPlanner/diet/preferences.json`](/home/dsm/workspace/MealPlanner/diet/preferences.json) and rebuild the pipeline.

Supported blacklist scopes:
- `exactTitles`: exact recipe titles
- `titleKeywords`: partial title keywords
- `sourcePaths`: exact imported relative paths

Convenient command:

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/add_blacklist.py --title "宫保鸡丁的做法"
```

## Operating workflow

### Daily default path

This is the default operational path the agent should prefer:

1. Weekly: run `plan_week.py` and `generate_weekly_plan.py`
2. Daily: run `generate_daily_plan.py`

Only use the full rebuild path when:
- source repositories changed
- blacklist / preference rules changed
- parsing or filtering logic changed
- the existing planning pool is clearly stale or broken

### Full rebuild

Run when source repositories or filtering heuristics changed:

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/rebuild_pipeline.py
```

### Weekly refresh

Run when starting a new week or when the saved week is missing/stale:

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/plan_week.py
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/generate_weekly_plan.py
```

### Daily delivery

Run on normal days:

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/generate_daily_plan.py
```

## References

- [`references/data-model.md`](/home/dsm/workspace/MealPlanner/meal-planner/references/data-model.md): generated file layout and state model
- [`references/selection-rules.md`](/home/dsm/workspace/MealPlanner/meal-planner/references/selection-rules.md): weekly planning constraints
- [`references/scoring-model.md`](/home/dsm/workspace/MealPlanner/meal-planner/references/scoring-model.md): recipe filtering and ranking heuristics
- [`references/integration-sources.md`](/home/dsm/workspace/MealPlanner/meal-planner/references/integration-sources.md): source-specific import policy
- [`references/runbook.md`](/home/dsm/workspace/MealPlanner/meal-planner/references/runbook.md): operational usage

When the pipeline changes, update both code and these references together.
