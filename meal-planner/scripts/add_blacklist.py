#!/usr/bin/env python3
import argparse
from datetime import datetime

from planner_core import PREFERENCES, ensure_preferences_file, save_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Add recipe blacklist rules to preferences.json")
    parser.add_argument("--title", help="Exact recipe title to blacklist")
    parser.add_argument("--keyword", help="Title keyword to blacklist")
    parser.add_argument("--path", help="Relative source path to blacklist")
    args = parser.parse_args()

    if not any([args.title, args.keyword, args.path]):
        raise SystemExit("Provide at least one of --title, --keyword, or --path")

    preferences = ensure_preferences_file()
    blacklist = preferences["blacklist"]

    if args.title and args.title not in blacklist["exactTitles"]:
        blacklist["exactTitles"].append(args.title)
    if args.keyword and args.keyword not in blacklist["titleKeywords"]:
        blacklist["titleKeywords"].append(args.keyword)
    if args.path and args.path not in blacklist["sourcePaths"]:
        blacklist["sourcePaths"].append(args.path)

    blacklist["exactTitles"].sort()
    blacklist["titleKeywords"].sort()
    blacklist["sourcePaths"].sort()
    preferences["updatedAt"] = datetime.now().isoformat()
    save_json(PREFERENCES, preferences)
    print(f"updated blacklist -> {PREFERENCES}")


if __name__ == "__main__":
    main()
