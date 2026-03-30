# Script Entry Points

## Import

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/import_sources.py
```

Writes `diet/imported_recipes.json`.

## Refine

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/refine_recipe_pool.py
```

Writes `diet/refined_recipe_pool.json`.

## Build grouped pool

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/build_structured_pool.py
```

Writes:
- `diet/structured_recipe_pool.json`
- `diet/meal_pool.json`
- `diet/recipe_pool.json`

## Plan current week

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/plan_week.py
```

Writes:
- `diet/state.json`
- `diet/weekly_meal_plan.md`

## Render outputs

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/generate_weekly_plan.py
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/generate_daily_plan.py
```

## Add blacklist

```bash
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/add_blacklist.py --title "宫保鸡丁的做法"
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/add_blacklist.py --keyword "鸡爪"
python3 /home/dsm/workspace/MealPlanner/meal-planner/scripts/add_blacklist.py --path "dishes/meat_dish/宫保鸡丁/宫保鸡丁.md"
```
