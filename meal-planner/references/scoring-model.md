# Meal Planner Scoring Model

## Goal

Score recipe candidates so weekly selection is constrained, explainable, and repeatable rather than ad hoc.

The planner should optimize for:
- nutrition balance across the week
- home-cooking practicality
- weekday reheating suitability
- shopping efficiency
- taste alignment with Jiangxi-friendly light spicy preferences
- stable week-level diversity

## Current scoring dimensions

### 1. Protein-fit score
Reward recipes whose protein category helps satisfy the desired weekly distribution.

Examples:
- `+6` if recipe protein matches the target slot for the day
- `+2` if that protein category has not appeared yet this week
- `-2` if that protein category is already over-represented

Additional adequacy rule:
- weekday default lunch should strongly prefer an animal-protein-led main dish
- tofu-led mains should be down-ranked unless clearly substantial and suitable as the user's main cooked meal

### 2. Reheat suitability score
Reward dishes that remain acceptable for dinner reuse.

Examples:
- `+2` if tagged `reheats-well`
- `-2` if assigned to a weekday but poor for reheating

### 3. Weekday practicality score
Reward dishes that are better suited to weekday reality.

Examples:
- `+2` if `weekdayFriendly`
- `-2` if active cooking time is too high for a weekday
- `-4` if the dish is awkward as a weekday lunch default (for example whole fish, crayfish, obvious feast-style dishes, or heavy carb-forward one-plate dishes)

### 4. Home-cooking score
Use `homeScore` from refinement as the baseline quality score.
This should reflect:
- recipe clarity
- home practicality
- reduced dependence on industrial/pre-mixed ingredients
- ingredient sanity

### 5. Taste-alignment score
Reward dishes that fit the user's flavor preferences without becoming too heavy.

Examples:
- `+1` if `spicyFriendly`
- `+1` if compatible with Jiangxi-style light spicy adaptation

### 6. Duplicate / monotony penalty
Penalize repetition.

Examples:
- `-6` if exact same dish name already used this week
- `-2` if the same protein category has appeared too many times
- hard-exclude dishes that are known to be misleading fits for the planner's core-protein assumptions even if their names suggest otherwise
- down-rank obvious `拌面 / 面 / 盖饭` style dishes as default weekday mains when they reduce meal completeness

### 7. Side adequacy rule
The side dish should make the full set feel complete.

Examples:
- reward sides that add meaningful vegetable volume or freshness
- penalize repeated thin sides too many days in a row
- prefer more substantial, clean, home-style sides over perfunctory filler sides
- reward sides that add mushrooms / egg / tofu / higher vegetable volume when the set would otherwise feel too weak
- allow side dishes to be broader than pure vegetables: egg dishes, tofu dishes, fungi dishes, mixed stir-fries, or soups can all be valid if they improve meal completeness without stealing the role of the main protein anchor
- reward side dishes that are complementary to the main rather than merely acceptable in isolation
- strongly penalize repeated side types across adjacent days
- strongly penalize exact repeated side dishes within the same week
- strongly prefer substantial home-style sides over thin cold dishes when the overall meal would otherwise feel weak
- penalize back-to-back same-protein mains when that makes the week feel monotonous
- reward more classic home-style main/side pairings rather than merely acceptable pairings

## Side-dish pairing logic

Main dishes should be paired with sides that improve weekly balance.

Prefer:
- leafy or fresh sides after heavy/spicy mains
- cruciferous/fungi sides if those categories are underrepresented
- soup/light sides when the main is rich

## Future improvements

The scoring model should later incorporate:
- ingredient reuse efficiency within 2-3 day windows
- explicit calorie/protein estimates
- stronger duplicate-family detection (not only exact names)
- bridge-week scoring for midweek starts

Do not add inventory-state complexity by default; prefer simpler weekly shopping recommendations unless the user explicitly asks for inventory tracking.
