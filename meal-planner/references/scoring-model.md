# Meal Planner Scoring Model

## Goal

Use explicit heuristics so recipe-pool curation and weekly planning are explainable.

## Import/refine scoring

### `homeScore`

Rewards:
- clear home-cooking structure
- usable ingredients
- reheatable or light home-style dishes
- proper main/side/soup role

Penalizes:
- semi-finished or chain-style sauce dependence
- heavy or feast-style dishes
- weak ingredient lists
- non-meal entries or wrong roles

### `nutritionScore`

Rewards:
- true protein anchors for mains
- meaningful vegetable content for sides and soups
- fish/shrimp/tofu variety support

Penalizes:
- heavy dishes that add little weekly balance

### `weekdayFriendly`

Derived from:
- estimated cooking time
- awkwardness for weekday cooking
- reheating practicality

## Weekly ranking

Main-dish ranking considers:
- target protein for the day
- weekday time fit
- reheating fit
- same-week duplicate penalty
- recent-history penalty
- season/lightness preference

Side ranking considers:
- complementarity with the chosen main
- weekly vegetable diversity
- recent-history penalty
- same-week duplicate penalty

## Important filters

The refiner deliberately excludes:
- obvious non-recipes
- condiments or sauce bases
- egg-only mains
- weak tofu mains
- chain-standardized entries that depend on prepared bases
- false-positive main dishes inferred only from condiment words
