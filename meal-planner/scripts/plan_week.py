#!/usr/bin/env python3
from planner_core import MEAL_POOL, WEEKLY_MEAL_PLAN, load_json, plan_week, render_week_markdown


def main() -> None:
    pool = load_json(MEAL_POOL, default={})
    if not pool:
        raise SystemExit("meal_pool.json missing; run build_structured_pool.py first")
    weekly_plan = plan_week(pool)
    WEEKLY_MEAL_PLAN.write_text(render_week_markdown(weekly_plan), encoding="utf-8")
    print(f"generated week {weekly_plan['weekStart']}")
    for day_name, entry in weekly_plan["days"].items():
        print(f"- {entry['weekdayCn']}: {entry['main']['name']} + {entry['side']['name']}")


if __name__ == "__main__":
    main()
