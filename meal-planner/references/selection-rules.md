# Weekly Selection Rules

## Objective

Build a weekly meal plan that is:
- nutritionally balanced
- practical for one-person home cooking
- compatible with lunch-cook / dinner-reuse behavior
- compatible with weekend bulk purchase + weekday replenishment
- stable enough to persist across the week without daily replanning drift

## Daily structure rule

Each day should include:
- breakfast
- one lunch main dish
- one side dish or soup
- dinner reuse note
- short method notes

Each week should separately include:
- one weekly shopping recommendation
- one compact weekly menu view

## Single-meal adequacy rule

The main cooked meal for the day must feel like a complete lunch that can also be reused for dinner.

Default rule:
- at least one dish in the main lunch set should be built around **animal protein** (`chicken`, `beef`, `pork`, `fish`, `shrimp`)
- tofu / egg dishes may appear, but should not usually serve as the sole core protein for the day's default lunch plan
- if a tofu dish is kept, it should usually be paired with a meaningful animal-protein component or be clearly justified as an exception

## Meal rhythm rule

- breakfast changes independently
- lunch is the only main cooking session
- dinner usually reuses lunch
- the planner should prefer dishes that remain acceptable after reheating

## Weekly protein target

Prefer a week close to:
- chicken: 2 days
- beef: 1-2 days
- pork: 1 day
- tofu / bean protein: 1 day
- fish / shrimp: 2 days

Do not repeat the same protein too heavily across adjacent days unless forced by candidate quality.

## Weekly vegetable diversity target

Across a week, try to cover:
- leafy greens >= 2-3 appearances
- cruciferous vegetables >= 1-2 appearances
- colorful vegetables >= 2-3 appearances
- fungi / mushrooms / wood ear >= 1-2 appearances
- refreshing cold/fresh side dishes when the main is heavy or spicy

## Recipe suitability rule

Prefer recipes that are:
- clearly described
- home-executable
- not overly dependent on proprietary/pre-mixed sauces
- reheatable when assigned to weekdays
- not excessively oily for routine use
- compatible with Jiangxi-friendly light spicy adaptation when appropriate

For weekday defaults, avoid dishes that feel awkward as an office-day lunch anchor, such as:
- whole-fish-forward dishes
- crayfish / shell-heavy dishes
- feast-style or highly hands-on dishes
- carb-heavy one-plate dishes such as obvious `拌面 / 面 / 盖饭` when they weaken the lunch+dinner reuse structure
- misleading or pseudo-meat dishes that do not actually provide the intended core protein load for the meal

Also avoid making the side dish too thin. A normal daily set should feel like a real meal, not just `一个主菜 + 一个过于单薄的小配菜`.

Prefer side dishes with at least one of these properties:
- enough vegetable volume
- mushrooms / tofu / egg support that makes the set feel more complete
- better contrast against a spicy main
- may be a substantial home-style side stir-fry rather than only a pure vegetable dish

Do not limit sides to pure vegetables only. A side may be:
- vegetable dish
- egg dish
- tofu dish
- fungi dish
- light mixed stir-fry
- soup
as long as the full meal remains nutritionally balanced and the main dish remains the primary protein anchor.

Prefer complementary pairing instead of random pairing. Examples:
- spicy chicken / pork mains -> pair with a lighter vegetable, fungi, or soup side
- fish mains -> pair with refreshing or lighter vegetable/fungi sides
- beef mains -> pair with vegetable-forward sides for balance
- tofu mains -> pair with a more complete vegetable/egg/mixed side so the set does not feel weak

## Shopping rule

Generate one **weekly shopping recommendation** that covers:
- major proteins
- durable vegetables
- breakfast staples
- fruit / spicy add-ons

Daily execution reminders should focus on today's meals and method notes.
Do not simulate daily inventory management by default.

## Midweek-start rule

If the planning cycle starts midweek:
- do not pretend a full weekend purchase already happened
- produce a bridge plan for the remaining days
- allow the next weekend to become the true main-purchase pivot

## Source merge rule

When multiple source repositories exist:
- keep the richer, more home-practical version of near-duplicate dishes
- keep alternate source metadata when useful
- favor recipes with better clarity and better suitability for weekly planning
