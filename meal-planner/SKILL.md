---
name: meal-planner
description: Build, maintain, and run a stateful meal-planning system for home cooking. Use when the user wants weekly meal planning, grocery planning, nutrition-balanced home cooking, recurring daily menu reminders, recipe-pool curation from GitHub cookbooks, or a persistent meal workflow that remembers current-week plans and shopping cadence.
---

# Meal Planner

Use this skill to manage meal planning as a **persistent weekly planning system** rather than a one-off reminder.

Do **not** overengineer inventory tracking or purchased-item tracking unless the user explicitly asks for it. The default design is: weekly plan + weekly shopping recommendation + daily execution reminder.

The current implementation is built around:
- recipe ingestion from GitHub cookbook repositories
- recipe cleaning / normalization / scoring
- weekly plan generation
- one weekly shopping recommendation
- daily reminder generation from the saved week plan
- model-assisted final daily phrasing/selection refinement when needed

## Current recipe sources

Primary source repositories:
- `Anduin2017/HowToCook`
- `Gar-b-age/CookLikeHOC`

Use `HowToCook` mainly as the home-cooking base source.
Use `CookLikeHOC` as a supplemental source for flavor patterns, structured dish naming, and standardized combinations, but down-rank recipes that depend too heavily on semi-finished sauces or central-kitchen style inputs.

## Real user constraints

Always plan around these persistent constraints:
- user is a `28-year-old`, `67kg`, maintenance-oriented adult male
- goal is `health + stable body shape + practical home cooking`
- user usually cooks **once per day**
- the cooked meal is mainly for **lunch**, and **dinner usually reuses lunch**
- breakfast can be separate and simpler
- **weekend = main purchase window**
- **weekday = replenishment window**
- flavor can be adjusted toward **Jiangxi-friendly light spicy home style**
- output must be **Telegram-mobile-friendly** and compact

## Required files and their roles

### Source and normalization layers
- `/home/dsm/.openclaw/workspace/diet/imported_recipes.json`
  - raw imported recipes from supported source repositories
- `/home/dsm/.openclaw/workspace/diet/refined_recipe_pool.json`
  - first-pass cleaned recipes with deduplication, tags, scores, and usability filtering
- `/home/dsm/.openclaw/workspace/diet/structured_recipe_pool.json`
  - planner-ready structured recipe pool used by the weekly planner

### Persistent planning layers
- `/home/dsm/.openclaw/workspace/diet/state.json`
  - generated week state, active weekly plan, and planning continuity
- `/home/dsm/.openclaw/workspace/diet/weekly_meal_plan.md`
  - human-readable nutrition policy, shopping cadence, and high-level planning assumptions

### Scripts
- `scripts/import_sources.py`
  - import markdown recipes from source repositories into `diet/imported_recipes.json`
- `scripts/refine_recipe_pool.py`
  - clean, score, and deduplicate imported recipes into `diet/refined_recipe_pool.json`
- `scripts/build_structured_pool.py`
  - convert refined recipes into planner-ready structured entries in `diet/structured_recipe_pool.json`
- `scripts/plan_week.py`
  - generate the current week's meal plan from the structured pool and write it into `diet/state.json`
- `scripts/generate_daily_plan.py`
  - read the persisted week plan from `diet/state.json` and render today's reminder

## Canonical workflow

### 1. Update recipe sources when needed
Run this when source repositories change or when importing a new cookbook source:

1. Run `scripts/import_sources.py`
2. Run `scripts/refine_recipe_pool.py`
3. Run `scripts/build_structured_pool.py`

Do not skip refinement/structuring and jump straight from raw imports into planning.

### 2. Generate or refresh the weekly plan
Run `scripts/plan_week.py` when:
- a new week begins
- shopping cadence changes
- the user changes taste / health / cooking assumptions
- the recipe pool has materially changed
- the current saved week is missing or invalid

Do **not** regenerate a week plan every day unless the saved plan is clearly stale or broken.

### 3. Generate the daily reminder
Run `scripts/generate_daily_plan.py` for the daily reminder.
The daily reminder must be derived from the persisted weekly plan instead of ad hoc re-selection.

## Planning method

Use explicit constraints instead of intuition-only selection.

### Weekly structure
For each day, generate:
- breakfast
- one lunch main dish
- one side dish or soup
- dinner reuse note
- short method notes

For each week, generate separately:
- one weekly shopping recommendation
- one compact weekly menu view

Important delivery rule:
- on `Monday`, include the **weekly plan + weekly shopping recommendation first**, then append the current day's plan
- on other days, daily reminders may send only the current day's plan

### Cross-week variety (key design)

`plan_week.py` maintains variety across weeks via three mechanisms:

1. **History tracking**: `state.json` records the last 8 weeks of used recipe IDs and side names.
   - Recipes used in the last 1-4 weeks receive a diminishing penalty score.
   - Sides used in the last 2 weeks receive an additional penalty.

2. **Protein pattern rotation**: 7 valid protein patterns are pre-defined. Each new week picks the next pattern in the cycle (by history length modulo 7). All patterns satisfy the weekly protein target.

3. **Controlled randomness**: Instead of always picking the top-ranked recipe, the planner selects from the top-3 candidates using weighted random choice (weights 4:2:1). This prevents the same dish appearing even if it re-enters the top spot.

Noodle/rice-bowl style dishes (`面`,`饭`,`盖浇`, etc.) are penalized globally so they don't displace proper main+side meals.

### Weekly nutrition logic
Prefer a weekly protein distribution close to:
- `chicken`: 2 days
- `beef`: 1-2 days
- `pork`: 1 day
- `tofu / bean protein`: 1 day
- `fish / shrimp`: 2 days

Prefer weekly vegetable diversity across:
- leafy greens
- cruciferous vegetables
- colorful vegetables
- fungi / mushrooms / wood ear

### Weekday practicality
Weekday mains should usually be:
- reheatable
- not too oily
- not too complex
- suitable for one cooking session
- generally around `<= 35-40` minutes active effort when possible

### Weekend shopping logic
Weekend main purchase should cover:
- core proteins
- durable vegetables
- breakfast staples
- fruit / spicy add-ons

Weekday replenishment should focus on:
- leafy greens
- mushrooms
- tomatoes / cucumbers / fresh vegetables
- fruit
- temporary ingredient gaps

## Output rules

For Telegram/mobile delivery:
- optimize for scanability and information density
- use compact tables or pseudo-tables only when they remain readable in Telegram
- keep all key fields present: meals, shopping, method, note, week continuity
- avoid long narrative paragraphs in scheduled reminders
- prefer concise code formatting for dish names, ingredients, and key fields

## References

Read these when changing planning quality:
- `references/scoring-model.md` — scoring and balancing rules
- `references/selection-rules.md` — weekly plan constraints and decision rules
- `references/data-model.md` — current persistent file/data model
- `references/integration-sources.md` — source import and merge policy
- `references/telegram-format.md` — output layout guidance
- `references/runbook.md` — operational run path and rebuild procedure

## When updating the system

Whenever behavior changes, update **both** code and documentation.

Specifically, when you change scripts or data flow, also update:
- `SKILL.md`
- `references/data-model.md`
- `references/selection-rules.md`
- `references/scoring-model.md`
- `references/integration-sources.md` if import/source behavior changed

Do not leave the skill docs describing an old architecture after scripts evolve.
