# MealPlanner

A reusable `meal-planner` skill for OpenClaw and similar agent workflows.

It turns large cookbook repositories into a planning-ready meal pool, then uses that pool to:
- generate a weekly meal plan
- generate daily meal recommendations from the saved week
- maintain a persistent blacklist for dishes you never want recommended again

The default operating model is:
- rebuild the recipe pool only when sources or rules change
- generate one weekly plan
- generate daily recommendations from the saved weekly state

## Quick start

If you already have an OpenClaw workspace, the shortest path is:

```bash
rsync -a ./meal-planner/ /home/dsm/.openclaw/workspace/skills/meal-planner/
rsync -a ./diet/ /home/dsm/.openclaw/workspace/diet/
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/plan_week.py
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/generate_daily_plan.py
```

This copies the skill, copies the current generated data, creates the current week, and renders today's recommendation.

## What is included

- [`meal-planner/`](./meal-planner)  
  The skill package: `SKILL.md`, scripts, and references.

- [`diet/`](./diet)  
  Example/generated data files: recipe pools, current state, preferences, and a rendered weekly plan.

## Recipe sources

Current supported source repositories:
- `Anduin2017/HowToCook`
- `Gar-b-age/CookLikeHOC`

`HowToCook` is treated as the primary home-cooking source.  
`CookLikeHOC` is supplemental and filtered more aggressively when entries look too chain-kitchen or semi-finished.

## Sync into OpenClaw

If your OpenClaw workspace is at `/home/dsm/.openclaw/workspace`, sync the skill with:

```bash
rsync -a ./meal-planner/ /home/dsm/.openclaw/workspace/skills/meal-planner/
rsync -a ./diet/ /home/dsm/.openclaw/workspace/diet/
```

After that, OpenClaw will have:
- `/home/dsm/.openclaw/workspace/skills/meal-planner`
- `/home/dsm/.openclaw/workspace/diet`

## Daily usage

Normal day-to-day usage does **not** require rebuilding the whole recipe pipeline.

### Generate this week's plan

```bash
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/plan_week.py
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/generate_weekly_plan.py
```

### Generate today's recommendation

```bash
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/generate_daily_plan.py
```

## Blacklist a dish

The skill supports a persistent blacklist file:

- [`diet/preferences.json`](./diet/preferences.json)

You can update it directly or use:

```bash
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/add_blacklist.py --title "宫保鸡丁"
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/rebuild_pipeline.py
```

Supported blacklist scopes:
- `exactTitles`
- `titleKeywords`
- `sourcePaths`

## Full rebuild

Only do this when:
- source repositories changed
- blacklist or preference rules changed
- import / scoring / filtering logic changed
- the current recipe pool is stale or broken

```bash
python3 /home/dsm/.openclaw/workspace/skills/meal-planner/scripts/rebuild_pipeline.py
```

This will:
1. import recipes from source repos
2. refine and filter them
3. build grouped meal pools
4. generate a weekly plan
5. render weekly and daily outputs

If you synced this repo into OpenClaw and then changed the skill code, re-run the two `rsync` commands before rebuilding.

## Preparing source repositories for rebuild

The importer looks for local source checkouts in these paths:
- `/tmp/HowToCook-master`
- `/tmp/howtocook_repo`
- `/tmp/howtocook_repo_nolfs`
- `/tmp/cooklikehoc_repo`

Recommended setup:

### HowToCook

```bash
curl -L https://codeload.github.com/Anduin2017/HowToCook/zip/refs/heads/master -o /tmp/howtocook.zip
unzip -q -o /tmp/howtocook.zip -d /tmp
```

### CookLikeHOC

```bash
git clone https://github.com/Gar-b-age/CookLikeHOC /tmp/cooklikehoc_repo
```

## Repository layout

```text
meal-planner/
  SKILL.md
  scripts/
  references/
diet/
  imported_recipes.json
  refined_recipe_pool.json
  structured_recipe_pool.json
  meal_pool.json
  recipe_pool.json
  state.json
  preferences.json
  weekly_meal_plan.md
```

## Notes

- Titles are normalized during import, so rendered plans use natural dish names like `红烧鱼` instead of `红烧鱼的做法`.
- The skill is designed for `weekly plan + daily reminder`, not full pantry/inventory management.
- If you update this repo and want OpenClaw to stay in sync, re-run the two `rsync` commands above.
