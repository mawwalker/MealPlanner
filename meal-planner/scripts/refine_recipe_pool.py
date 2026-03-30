#!/usr/bin/env python3
from planner_core import IMPORTED_RECIPES, REFINED_RECIPE_POOL, load_json, refine_recipes, save_json


def main() -> None:
    imported = load_json(IMPORTED_RECIPES, default={"recipes": []})
    payload = refine_recipes(imported)
    save_json(REFINED_RECIPE_POOL, payload)
    practical = [recipe for recipe in payload["recipes"] if recipe["isPractical"]]
    mains = [recipe for recipe in practical if recipe["role"] == "main"]
    sides = [recipe for recipe in practical if recipe["role"] in {"side", "soup"}]
    print(f"refined={payload['count']} practical={len(practical)} mains={len(mains)} sides={len(sides)}")
    for recipe in practical[:10]:
        print(
            f"- {recipe['title']} | role={recipe['role']} | protein={recipe['protein']} "
            f"| score={recipe['homeScore'] + recipe['nutritionScore']} | {recipe['sourceName']}"
        )


if __name__ == "__main__":
    main()
