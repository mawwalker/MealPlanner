# Meal Planner Data Model

## Overview

The planner currently uses a multi-stage data pipeline instead of a static week-template file.

## File graph

### 1. Raw import layer
`diet/imported_recipes.json`

Contains raw normalized imports from source repositories.
Each recipe entry typically includes:
- `id`
- `name`
- `sourceRepo`
- `sourcePath`
- `protein`
- `tags`
- `ingredients`
- `method`

### 2. Refined candidate layer
`diet/refined_recipe_pool.json`

Contains first-pass cleaned and deduplicated recipe candidates.
Additional fields may include:
- `estimatedMinutes`
- `homeScore`
- `reheatScore`
- `weekdayFriendly`
- `light`
- `spicyFriendly`
- `vegHits`

### 3. Structured planner layer
`diet/structured_recipe_pool.json`

Contains planner-ready recipes used directly by the weekly planner.
Each entry should be compact and stable for planning:
- `id`
- `name`
- `sourceRepo`
- `sourcePath`
- `protein`
- `vegTypes`
- `tags`
- `ingredients`
- `method`
- `estimatedMinutes`
- `reheatScore`
- `weekdayFriendly`
- `light`
- `spicyFriendly`
- `homeScore`

### 4. Persistent runtime state
`diet/state.json`

Current runtime state for the planner.
This file is the continuity anchor and should persist only the planning state that is actually needed:
- current generated week start
- generated timestamp
- `generatedWeekPlan`
- optional lightweight history / planning metadata

Do not turn this into a full inventory ledger unless explicitly requested.

### 5. Human policy layer
`diet/weekly_meal_plan.md`

Human-readable planning assumptions, user preferences, shopping cadence, and nutrition policy.

## `generatedWeekPlan` structure

The generated plan currently stores:
- `weekStart`
- `days`
  - per weekday:
    - `breakfast`
    - `main`
    - `side`
    - `cookOnce`
    - `dinnerReuse`
    - `purchaseMode`
    - `note`
- `weeklyBuy`
  - `protein`
  - `durableVeg`
  - `breakfastStaples`
  - `fruitExtra`
  - `replenishFresh`
- optional analytics fields such as:
  - `proteinCounts`
  - `sideDiversity`

## Semantics

### Daily cooking rhythm
- breakfast is independent
- lunch is the main cooked meal
- dinner usually reuses lunch

### Shopping rhythm
- shopping is handled at the **weekly recommendation** level by default
- daily reminders reference the saved weekly plan instead of generating daily shopping lists

### Continuity rule
Daily messages should be rendered from the saved weekly state, not re-planned from scratch each day.
