#!/usr/bin/env python3
from planner_core import (
    MEAL_POOL,
    RECIPE_POOL,
    REFINED_RECIPE_POOL,
    STRUCTURED_RECIPE_POOL,
    compatibility_recipe_pool,
    load_json,
    meal_pool,
    save_json,
    structured_pool,
)


def main() -> None:
    refined = load_json(REFINED_RECIPE_POOL, default={"recipes": []})
    structured = structured_pool(refined)
    save_json(STRUCTURED_RECIPE_POOL, structured)
    save_json(MEAL_POOL, meal_pool(structured))
    save_json(RECIPE_POOL, compatibility_recipe_pool(structured))
    print(
        f"structured={len(structured['recipes'])} mains={len(structured['mains'])} "
        f"sides={len(structured['sides'])} soups={len(structured['soups'])}"
    )
    print(f"poolSignature={structured['poolSignature']}")
    print(f"sourceCounts={structured['stats']['sourceCounts']}")


if __name__ == "__main__":
    main()
