#!/usr/bin/env python3
from planner_core import IMPORTED_RECIPES, imported_recipes, save_json


def main() -> None:
    payload = imported_recipes()
    save_json(IMPORTED_RECIPES, payload)
    print(f"imported {payload['count']} recipes -> {IMPORTED_RECIPES}")
    for source in payload["sources"]:
        print(f"- {source['name']}: {source['root']}")


if __name__ == "__main__":
    main()
