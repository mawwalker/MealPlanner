# Recipe Source Integration

## Current sources
- `Anduin2017/HowToCook`
- `Gar-b-age/CookLikeHOC`

## Source roles

### `Anduin2017/HowToCook`
Use as the main home-cooking reference source.
Strengths:
- clearer home-cooking steps
- stronger generic household applicability
- better default source for family-style weekly planning

### `Gar-b-age/CookLikeHOC`
Use as the supplemental standardization/flavor source.
Strengths:
- structured dish naming
- chain-style flavor references
- useful for standardized combinations and flavor direction

Caution:
- some recipes depend on semi-finished sauces, industrial ingredients, or central-kitchen style assumptions
- these should be adapted or down-ranked before entering the planner-ready pool

## Import pipeline

Current source-processing flow:

1. `scripts/import_sources.py`
   - crawl supported repositories' markdown recipes
   - produce `diet/imported_recipes.json`

2. `scripts/refine_recipe_pool.py`
   - deduplicate near-identical dishes
   - infer home usability / weekday suitability / reheat score / spicy fit
   - produce `diet/refined_recipe_pool.json`

3. `scripts/build_structured_pool.py`
   - normalize refined candidates into planner-ready shape
   - produce `diet/structured_recipe_pool.json`

## Normalization target

Planner-ready recipes should contain:
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

## Merge policy

When near-duplicate dishes exist across sources:
- keep the version with clearer home execution and better planner compatibility
- preserve source metadata if useful for traceability
- prefer a home-practical interpretation over a chain-kitchen interpretation

## When a new repo is added

When adding another cookbook source:
- extend `import_sources.py`
- re-run the full pipeline: import -> refine -> build structured pool
- update this reference file and `SKILL.md`
- verify that the scoring/selection logic still matches the expanded pool
