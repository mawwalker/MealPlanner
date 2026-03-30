# Meal Planner Data Model

## Pipeline layers

### 1. Imported source layer
[`/home/dsm/workspace/MealPlanner/diet/imported_recipes.json`](/home/dsm/workspace/MealPlanner/diet/imported_recipes.json)

One entry per imported markdown recipe.

Important fields:
- `id`
- `sourceName`
- `relativePath`
- `title`
- `ingredients`
- `steps`
- `method`
- `protein`
- `role`
- `vegTypes`
- `tags`
- `estimatedMinutes`
- `difficulty`

### 2. Refined candidate layer
[`/home/dsm/workspace/MealPlanner/diet/refined_recipe_pool.json`](/home/dsm/workspace/MealPlanner/diet/refined_recipe_pool.json)

Adds planning heuristics:
- `homeScore`
- `nutritionScore`
- `weekdayFriendly`
- `isPractical`
- `useFrequency`

This is the main filter that removes:
- non-meal content
- obvious non-home-cooking entries
- weak main dishes
- chain-kitchen style recipes that depend on prebuilt bases

### 3. Structured planning pool
[`/home/dsm/workspace/MealPlanner/diet/structured_recipe_pool.json`](/home/dsm/workspace/MealPlanner/diet/structured_recipe_pool.json)

Planner-ready grouped pool:
- `mains`
- `sides`
- `soups`
- `recipes`
- `breakfastTemplates`
- `stats`
- `poolSignature`

### 4. Compatibility view
[`/home/dsm/workspace/MealPlanner/diet/meal_pool.json`](/home/dsm/workspace/MealPlanner/diet/meal_pool.json)
[`/home/dsm/workspace/MealPlanner/diet/recipe_pool.json`](/home/dsm/workspace/MealPlanner/diet/recipe_pool.json)

These keep a grouped view that is easier for agents or older integrations to consume.

### 5. Persistent runtime state
[`/home/dsm/workspace/MealPlanner/diet/state.json`](/home/dsm/workspace/MealPlanner/diet/state.json)

State contains:
- `activeWeek`
- `history`
- `updatedAt`

`activeWeek` contains:
- `weekStart`
- `generatedAt`
- `poolSignature`
- `season`
- `proteinTargets`
- `proteinCounts`
- `days`
- `weeklyBuy`

### 6. User preference overrides
[`/home/dsm/workspace/MealPlanner/diet/preferences.json`](/home/dsm/workspace/MealPlanner/diet/preferences.json)

Current supported override:
- `blacklist.exactTitles`
- `blacklist.titleKeywords`
- `blacklist.sourcePaths`

### 7. Human-readable week file
[`/home/dsm/workspace/MealPlanner/diet/weekly_meal_plan.md`](/home/dsm/workspace/MealPlanner/diet/weekly_meal_plan.md)

Compact markdown rendering of the current saved week.
