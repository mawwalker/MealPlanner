#!/usr/bin/env python3
from planner_core import STATE, load_json, render_daily_message


def main() -> None:
    state = load_json(STATE, default={})
    weekly_plan = state.get("activeWeek")
    if not weekly_plan:
        raise SystemExit("No active week found; run plan_week.py first")
    print(render_daily_message(weekly_plan))


if __name__ == "__main__":
    main()
