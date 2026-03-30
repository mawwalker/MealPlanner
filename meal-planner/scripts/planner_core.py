#!/usr/bin/env python3
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "diet"

IMPORTED_RECIPES = DATA_DIR / "imported_recipes.json"
REFINED_RECIPE_POOL = DATA_DIR / "refined_recipe_pool.json"
STRUCTURED_RECIPE_POOL = DATA_DIR / "structured_recipe_pool.json"
MEAL_POOL = DATA_DIR / "meal_pool.json"
RECIPE_POOL = DATA_DIR / "recipe_pool.json"
STATE = DATA_DIR / "state.json"
WEEKLY_MEAL_PLAN = DATA_DIR / "weekly_meal_plan.md"
PREFERENCES = DATA_DIR / "preferences.json"

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_CN = {
    "Monday": "周一",
    "Tuesday": "周二",
    "Wednesday": "周三",
    "Thursday": "周四",
    "Friday": "周五",
    "Saturday": "周六",
    "Sunday": "周日",
}

USER_PROFILE = {
    "age": 28,
    "weightKg": 67,
    "goal": "maintain",
    "household": 1,
    "cookPattern": "午餐主做，晚餐复热",
    "style": ["home-cooking", "healthy", "balanced", "jiangxi-light-spicy"],
    "shoppingPattern": {
        "mainPurchaseDays": ["Saturday", "Sunday"],
        "replenishDays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    },
}

BREAKFAST_TEMPLATES = [
    {"id": "bf-oat-egg-yogurt", "name": "燕麦 + 鸡蛋 + 酸奶 + 水果", "tags": ["quick", "high-protein"]},
    {"id": "bf-toast-egg-milk", "name": "全麦面包 + 鸡蛋 + 牛奶 + 水果", "tags": ["quick"]},
    {"id": "bf-corn-egg-fruit", "name": "玉米/红薯 + 鸡蛋 + 水果", "tags": ["quick"]},
    {"id": "bf-congee-egg", "name": "杂粮粥 + 鸡蛋 + 酸奶", "tags": ["warm", "quick"]},
]

SOURCE_CONFIGS = {
    "HowToCook": {
        "roots": [Path("/tmp/HowToCook-master"), Path("/tmp/howtocook_repo"), Path("/tmp/howtocook_repo_nolfs")],
    },
    "CookLikeHOC": {
        "roots": [Path("/tmp/cooklikehoc_repo")],
    },
}

COOKLIKEHOC_ALLOWED_TOP = {
    "主食",
    "凉拌",
    "卤菜",
    "早餐",
    "汤",
    "炒菜",
    "炖菜",
    "炸品",
    "烤类",
    "烫菜",
    "煮锅",
    "砂锅菜",
    "蒸菜",
}
COOKLIKEHOC_BLOCKED_TOP = {"配料", "饮品", "docs", "docker_support", "images", ".vitepress"}

INGREDIENT_HEADINGS = {"原料", "材料", "食材", "配料", "辅料", "调料", "必备原料", "主料"}
STEP_HEADINGS = {"步骤", "做法", "制作", "操作", "烹饪步骤", "烹饪", "流程"}

SEMI_FINISHED_HINTS = {
    "预制", "料包", "火锅底料", "半成品", "蒜蓉辣酱", "黑椒汁", "照烧汁", "中央厨房", "调理", "复合调味"
}
CHAIN_STYLE_HINTS = {
    "调味料配制", "基础酱", "老鸡汤", "汤汁", "酱料", "蒸柜", "出品", "餐具中", "份", "码味", "走菜", "净菜",
    "熟制", "鸡汁", "豉油汁", "蚕豆酱", "预制", "原味鸡汤", "糊辣油", "红烧牛肉片", "牛杂", "卤料",
}
HEAVY_HINTS = {"炸", "干锅", "锅包", "肥肠", "扣肉", "红油", "大份", "烧烤", "油焖", "香辣蟹", "小龙虾"}
LIGHT_HINTS = {"清蒸", "蒸", "白灼", "清炒", "凉拌", "汤", "羹", "炖", "焖", "豆腐", "西兰花", "番茄"}
SPICY_HINTS = {"辣", "麻", "剁椒", "泡椒", "麻婆", "鱼香", "宫保", "小炒", "干煸", "豆瓣", "红油"}
REHEAT_HINTS = {"炖", "焖", "煲", "红烧", "卤", "酱", "麻婆", "鱼香", "咖喱", "茄汁", "牛腩", "排骨"}
FAST_HINTS = {"炒", "蒸蛋", "凉拌", "白灼"}
WEEKDAY_BAD_HINTS = {"小龙虾", "火锅", "烤鱼", "整鱼", "烧烤", "肥肠", "鸭头", "羊排", "盖饭", "拌面", "炒面"}
STAPLE_HINTS = {"饭", "面", "粉", "粥", "饺", "包", "馄饨", "面包", "三明治", "焖饭"}
SOUP_HINTS = {"汤", "羹", "煲"}
BREAKFAST_HINTS = {"早餐", "吐司", "燕麦", "三明治", "煎蛋", "蒸蛋", "粥"}

PROTEIN_KEYWORDS = [
    ("fish", ["鲈鱼", "鳕鱼", "鱼头", "鱼块", "鱼片", "鱼柳", "黑鱼", "草鱼", "鲢鱼", "黄鳝", "蟹", "海参", "生蚝", "蛏", "贝", "鱼"]),
    ("shrimp", ["大虾", "虾仁", "河虾", "鲜虾", "基围虾", "罗氏虾", "明虾", "虾"]),
    ("egg", ["鸡蛋", "蛋"]),
    ("tofu", ["日本豆腐", "豆腐", "豆干", "香干", "腐竹"]),
    ("beef", ["牛腩", "牛柳", "肥牛", "牛腱", "牛肉"]),
    ("pork", ["排骨", "里脊", "五花肉", "肉丝", "肉末", "猪肉", "腊肉"]),
    ("chicken", ["鸡腿", "鸡翅", "鸡胸", "鸡丁", "鸡块", "鸡肉", "土鸡", "鸡"]),
]
FALSE_PROTEIN_PHRASES = {
    "fish": {"鱼香", "章鱼小丸子"},
}
PROTEIN_BLOCKLIST = {
    "鸡精", "鸡油", "鸡汁", "鸡汤", "老鸡汤", "高汤", "味精", "生抽", "老抽", "蒸鱼豉油", "豉油", "蚝油",
    "白糖", "盐", "醋", "豆油", "熟猪油", "猪油", "蒜蓉酱", "调味料", "酱料", "汤汁", "料", "卤料", "汁",
}
SHOPPING_EXCLUDE_HINTS = PROTEIN_BLOCKLIST | {
    "食用油", "香油", "芝麻香油", "植物油", "淀粉", "生粉", "料酒", "厨房纸", "平底煎锅", "刷子", "锅",
    "牛奶", "纯牛奶", "橄榄油", "味极鲜酱油", "酱油", "白砂糖", "糖", "胡椒粉", "豆瓣酱", "小米椒",
}
SIDE_STYLE_HINTS = {"清炒", "凉拌", "蒜蓉", "白灼", "手撕", "炝炒", "上汤", "蚝油", "素炒"}
RAW_PROTEIN_HINTS = {
    "beef": {"牛", "牛肉", "牛腩", "牛柳"},
    "chicken": {"鸡", "鸡肉", "鸡腿", "鸡丁", "鸡块"},
    "pork": {"猪", "猪肉", "排骨", "五花肉", "肉丝", "肉末"},
    "fish": {"鱼", "鲈鱼", "鳕鱼", "黑鱼", "草鱼", "鲢鱼", "蟹", "鳝", "海参", "生蚝", "蛏", "贝", "蛤"},
    "shrimp": {"大虾", "虾仁", "河虾", "鲜虾", "基围虾", "罗氏虾", "明虾"},
    "tofu": {"豆腐", "豆干", "香干", "腐竹"},
    "egg": {"蛋", "鸡蛋"},
}
SUBSTANTIAL_TOFU_MAIN_HINTS = {"麻婆豆腐", "家常豆腐", "豆腐煲", "日本豆腐", "砂锅豆腐", "豆腐堡"}
NON_MAIN_TITLE_HINTS = {"红酱", "酱汁", "蘸料", "锅底", "底料", "调料", "面酱", "油泼辣子"}
SIDE_ANIMAL_PROTEIN_LIMIT = {"beef", "pork", "chicken", "fish", "shrimp"}
HEAVY_SOUP_TITLE_HINTS = {"乳鸽", "排骨", "牛", "鱼", "虾", "鸡", "鸭"}
WHOLE_FISH_WEEKDAY_HINTS = {"鱼头", "鲈鱼", "鳜鱼", "鲤鱼", "整鱼", "生蚝", "海参", "蟹"}
SIDE_STAPLE_EXCLUDE_HINTS = {"粥", "饼", "饭", "面", "馄饨", "饺", "包子", "烧麦"}
WEAK_MAIN_TITLE_HINTS = {"鲮鱼油麦菜", "豆豉鲮鱼", "油麦菜", "青菜", "生菜", "空心菜", "花菜"}

VEG_GROUPS = {
    "leafy": {"青菜", "生菜", "油麦菜", "菠菜", "菜心", "空心菜", "娃娃菜", "包菜", "芥蓝", "白菜"},
    "cruciferous": {"西兰花", "花菜", "菜花", "卷心菜", "芥蓝"},
    "fungi": {"香菇", "平菇", "金针菇", "木耳", "口蘑", "杏鲍菇", "菌菇"},
    "colorful": {"番茄", "西红柿", "青椒", "彩椒", "胡萝卜", "南瓜", "茄子", "西葫芦"},
    "root": {"土豆", "萝卜", "山药", "藕", "冬瓜"},
    "fresh": {"黄瓜", "豆芽", "芹菜", "莴笋"},
}

SEASON_VEG_BONUS = {
    "spring": {"leafy", "fresh"},
    "summer": {"fresh", "colorful"},
    "autumn": {"root", "cruciferous"},
    "winter": {"root", "fungi"},
}

DAY_PROFILES = {
    "Monday": {"maxMinutes": 30, "preferLight": True, "preferReheat": True},
    "Tuesday": {"maxMinutes": 30, "preferLight": True, "preferReheat": True},
    "Wednesday": {"maxMinutes": 35, "preferLight": False, "preferReheat": True},
    "Thursday": {"maxMinutes": 35, "preferLight": False, "preferReheat": True},
    "Friday": {"maxMinutes": 35, "preferLight": False, "preferReheat": True},
    "Saturday": {"maxMinutes": 55, "preferLight": False, "preferReheat": False},
    "Sunday": {"maxMinutes": 45, "preferLight": True, "preferReheat": False},
}


@dataclass
class SourceScan:
    source_name: str
    root: Path


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def default_preferences() -> dict:
    return {
        "version": 1,
        "updatedAt": None,
        "blacklist": {
            "exactTitles": [],
            "titleKeywords": [],
            "sourcePaths": [],
        },
    }


def load_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload) -> None:
    ensure_data_dir()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_preferences() -> dict:
    prefs = load_json(PREFERENCES, default=default_preferences())
    blacklist = prefs.setdefault("blacklist", {})
    blacklist.setdefault("exactTitles", [])
    blacklist.setdefault("titleKeywords", [])
    blacklist.setdefault("sourcePaths", [])
    return prefs


def ensure_preferences_file() -> dict:
    prefs = load_preferences()
    if not PREFERENCES.exists():
        save_json(PREFERENCES, prefs)
    return prefs


def repo_sources() -> list[SourceScan]:
    scans = []
    for source_name, config in SOURCE_CONFIGS.items():
        for root in config["roots"]:
            if root.exists():
                scans.append(SourceScan(source_name=source_name, root=root))
                break
    return scans


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def season_for_month(month: int) -> str:
    if month in {3, 4, 5}:
        return "spring"
    if month in {6, 7, 8}:
        return "summer"
    if month in {9, 10, 11}:
        return "autumn"
    return "winter"


def week_start_for_day(today: date) -> str:
    return (today - timedelta(days=today.weekday())).isoformat()


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def strip_markdown(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`+", "", text)
    text = re.sub(r"[*_>#]", "", text)
    return normalize_space(text)


def heading_label(line: str) -> str | None:
    match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", line)
    if not match:
        return None
    return strip_markdown(match.group(1)).replace("：", "").replace(":", "").strip()


def title_from_text(text: str, fallback: str) -> str:
    for line in text.splitlines():
        label = heading_label(line)
        if label:
            return label
    return fallback


def text_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = defaultdict(list)
    current = "__preamble__"
    for raw_line in text.splitlines():
        label = heading_label(raw_line)
        if label:
            current = label
            continue
        sections[current].append(raw_line.rstrip())
    return sections


def line_is_ingredient(line: str) -> bool:
    line = strip_markdown(line).strip("-*+ ")
    if not line or len(line) > 48:
        return False
    if re.match(r"^[0-9]+[.、)]", line):
        return False
    if any(token in line for token in {"步骤", "做法", "小贴士", "备注", "Tips"}):
        return False
    return bool(re.search(r"[克个勺匙片条块朵把根只张盒袋瓣mlML毫升适量少许]", line)) or len(line) <= 12


def extract_ingredient_lines(text: str) -> list[str]:
    sections = text_sections(text)
    collected: list[str] = []
    for title, lines in sections.items():
        normalized = title.replace("：", "").replace(":", "")
        if any(key in normalized for key in INGREDIENT_HEADINGS):
            for line in lines:
                clean = strip_markdown(line).strip("-*+ ")
                if line_is_ingredient(clean):
                    collected.append(clean)
    if collected:
        return unique_preserve(collected)[:18]
    fallback = []
    for raw_line in text.splitlines():
        clean = strip_markdown(raw_line).strip("-*+ ")
        if line_is_ingredient(clean):
            fallback.append(clean)
    return unique_preserve(fallback)[:18]


def line_is_step(line: str) -> bool:
    line = strip_markdown(line)
    if not line:
        return False
    if re.match(r"^([0-9]+|[一二三四五六七八九十])[.、)]", line):
        return True
    return any(token in line for token in {"加入", "下入", "放入", "翻炒", "焖", "煮", "蒸", "炖", "煎", "烧"})


def extract_step_lines(text: str) -> list[str]:
    sections = text_sections(text)
    steps: list[str] = []
    for title, lines in sections.items():
        normalized = title.replace("：", "").replace(":", "")
        if any(key in normalized for key in STEP_HEADINGS):
            for line in lines:
                clean = strip_markdown(line).strip()
                if line_is_step(clean):
                    steps.append(clean)
    if steps:
        return unique_preserve(steps)[:8]
    fallback = []
    for raw_line in text.splitlines():
        clean = strip_markdown(raw_line).strip()
        if line_is_step(clean):
            fallback.append(clean)
    return unique_preserve(fallback)[:8]


def summarize_method(step_lines: list[str]) -> str:
    if not step_lines:
        return "参考原文步骤制作。"
    compact = [re.sub(r"^([0-9]+|[一二三四五六七八九十])[.、)]\s*", "", line) for line in step_lines[:3]]
    return "；".join(compact)[:140]


def normalize_ingredient_name(line: str) -> str:
    line = strip_markdown(line)
    line = re.sub(r"[（(].*?[)）]", "", line)
    line = re.sub(r"[0-9./]+", "", line)
    line = re.sub(r"[g克mlML毫升适量少许大勺小勺匙茶匙汤匙个只片条块朵把根盒袋张颗斤]", "", line)
    line = re.sub(r"[:：,，;；、/]", " ", line)
    line = normalize_space(line)
    return line[:20]


def unique_preserve(values: Iterable[str]) -> list[str]:
    seen = set()
    output = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output


def path_tokens(relative_path: str) -> list[str]:
    return [part for part in Path(relative_path).parts if part]


def infer_minutes(title: str, relative_path: str, method: str) -> int:
    text = f"{title} {relative_path} {method}"
    if any(token in text for token in {"炖", "煲", "卤", "牛腩", "排骨", "焖"}):
        return 45
    if any(token in text for token in {"蒸", "白灼", "凉拌", "汤"}):
        return 20
    if any(token in text for token in {"炒", "滑", "煎"}):
        return 25
    return 35


def infer_primary_protein(title: str, ingredients: list[str], relative_path: str) -> str:
    title_text = f"{title} {relative_path}"
    for protein, keywords in PROTEIN_KEYWORDS:
        filtered_title = title_text
        for phrase in FALSE_PROTEIN_PHRASES.get(protein, set()):
            filtered_title = filtered_title.replace(phrase, "")
        if protein == "chicken":
            filtered_title = filtered_title.replace("鸡蛋", "")
        if any(keyword in filtered_title for keyword in keywords):
            return protein
    filtered_ingredients = [
        item for item in ingredients
        if not any(token in item for token in PROTEIN_BLOCKLIST)
    ]
    text = " ".join(filtered_ingredients)
    for protein, keywords in PROTEIN_KEYWORDS:
        false_phrases = FALSE_PROTEIN_PHRASES.get(protein, set())
        if any(phrase in text for phrase in false_phrases):
            filtered_text = text
            for phrase in false_phrases:
                filtered_text = filtered_text.replace(phrase, "")
        else:
            filtered_text = text
        if protein == "chicken":
            filtered_text = filtered_text.replace("鸡蛋", "")
        if any(keyword in filtered_text for keyword in keywords):
            return protein
    return "other"


def infer_veg_types(title: str, ingredients: list[str]) -> list[str]:
    text = " ".join([title, *ingredients])
    hits = [group for group, keywords in VEG_GROUPS.items() if any(keyword in text for keyword in keywords)]
    return hits or ["other"]


def infer_cooking_tags(title: str, relative_path: str, ingredients: list[str], method: str) -> list[str]:
    text = " ".join([title, relative_path, *ingredients, method])
    tags = []
    if any(token in text for token in SPICY_HINTS):
        tags.append("spicy-friendly")
    if any(token in text for token in REHEAT_HINTS):
        tags.append("reheats-well")
    if any(token in text for token in LIGHT_HINTS):
        tags.append("light")
    if any(token in text for token in FAST_HINTS):
        tags.append("quick")
    if any(token in text for token in HEAVY_HINTS):
        tags.append("heavy")
    return sorted(set(tags))


def infer_dish_role(source_name: str, relative_path: str, title: str, protein: str, ingredients: list[str]) -> str:
    tokens = path_tokens(relative_path)
    top = tokens[0] if tokens else ""
    joined = " ".join(tokens + [title])
    ingredient_text = " ".join(ingredients)
    obvious_veg = any(keyword in f"{title} {ingredient_text}" for group in VEG_GROUPS.values() for keyword in group)
    if source_name == "HowToCook" and relative_path.startswith("dishes/breakfast/"):
        return "breakfast"
    if source_name == "HowToCook" and relative_path.startswith("dishes/staple/"):
        return "staple"
    if source_name == "HowToCook" and relative_path.startswith("dishes/soup/"):
        return "soup"
    if source_name == "HowToCook" and relative_path.startswith("dishes/vegetable_dish/"):
        if protein in {"chicken", "beef", "pork", "fish", "shrimp"}:
            return "main"
        return "side"
    if source_name == "HowToCook":
        return "main"

    if top == "早餐" or any(token in joined for token in BREAKFAST_HINTS):
        return "breakfast"
    if top == "主食" or any(token in title for token in STAPLE_HINTS):
        return "staple"
    if top == "汤" or any(token in title for token in SOUP_HINTS):
        return "soup"
    if top == "凉拌":
        return "side"
    if top in {"炒菜", "炖菜", "蒸菜", "砂锅菜", "煮锅", "卤菜", "烫菜", "炸品", "烤类"}:
        if obvious_veg and protein in {"other", "egg", "tofu"}:
            return "side"
        if protein in {"other", "egg", "tofu"}:
            return "side"
        return "main"
    return "other"


def infer_difficulty(minutes: int, title: str, method: str) -> int:
    text = f"{title} {method}"
    score = 2
    if minutes >= 40:
        score += 1
    if any(token in text for token in {"炸", "焖", "炖", "卤", "发酵", "包"}):
        score += 1
    if any(token in text for token in {"快炒", "凉拌", "蒸蛋"}):
        score -= 1
    return max(1, min(5, score))


def home_score(recipe: dict) -> int:
    text = " ".join(
        [
            recipe["title"],
            recipe["relativePath"],
            recipe.get("method", ""),
            " ".join(recipe.get("ingredients", [])),
        ]
    )
    score = 0
    if recipe["role"] in {"main", "side", "soup"}:
        score += 3
    if recipe["protein"] in {"chicken", "beef", "pork", "fish", "shrimp", "tofu", "egg"}:
        score += 2
    if "reheats-well" in recipe["tags"]:
        score += 2
    if "light" in recipe["tags"]:
        score += 1
    if "quick" in recipe["tags"]:
        score += 1
    if any(token in text for token in SEMI_FINISHED_HINTS):
        score -= 4
    if any(token in text for token in CHAIN_STYLE_HINTS):
        score -= 3
    if any(token in text for token in HEAVY_HINTS):
        score -= 2
    if len(recipe.get("ingredients", [])) < 2:
        score -= 1
    if recipe["sourceName"] == "CookLikeHOC" and len(recipe.get("ingredients", [])) <= 3:
        score -= 1
    if recipe["role"] == "main" and any(recipe["title"].startswith(prefix) for prefix in SIDE_STYLE_HINTS):
        score -= 3
    if recipe["role"] == "staple":
        score -= 2
    if recipe["role"] == "other":
        score -= 4
    return score


def nutrition_score(recipe: dict) -> int:
    score = 0
    veg_types = recipe.get("vegTypes", [])
    if recipe["role"] in {"side", "soup"} and any(vt != "other" for vt in veg_types):
        score += 3
    if recipe["role"] == "main" and recipe["protein"] in {"chicken", "beef", "pork", "fish", "shrimp", "tofu"}:
        score += 3
    if recipe["protein"] in {"fish", "shrimp", "tofu"}:
        score += 1
    if "heavy" in recipe["tags"]:
        score -= 1
    return score


def weekday_friendly(recipe: dict) -> bool:
    if recipe["estimatedMinutes"] > 40:
        return False
    text = f'{recipe["title"]} {recipe["method"]}'
    if any(token in text for token in WEEKDAY_BAD_HINTS):
        return False
    return True


def recipe_signature(recipe: dict) -> str:
    seed = "|".join(
        [
            recipe["title"],
            recipe["sourceName"],
            recipe["relativePath"],
            ",".join(sorted(recipe.get("ingredients", []))),
        ]
    )
    return sha1_text(seed)[:12]


def has_raw_protein_anchor(recipe: dict) -> bool:
    text = " ".join([recipe["title"], *recipe.get("ingredients", [])])
    return any(hint in text for hint in RAW_PROTEIN_HINTS.get(recipe["protein"], set()))


def title_has_main_anchor(recipe: dict) -> bool:
    hints = RAW_PROTEIN_HINTS.get(recipe["protein"], set())
    return any(hint in recipe["title"] for hint in hints)


def canonical_dedupe_key(title: str, role: str) -> str:
    clean = re.sub(r"[\s·•\-_/]", "", title.lower())
    clean = clean.replace("家常", "").replace("简易", "").replace("懒人", "")
    return f"{role}:{clean}"


def is_blacklisted(recipe: dict, preferences: dict) -> tuple[bool, str | None]:
    blacklist = preferences.get("blacklist", {})
    title = recipe.get("title", "")
    relative_path = recipe.get("relativePath", "")

    exact_titles = set(blacklist.get("exactTitles", []))
    if title in exact_titles:
        return True, f"title:{title}"

    for keyword in blacklist.get("titleKeywords", []):
        if keyword and keyword in title:
            return True, f"keyword:{keyword}"

    source_paths = set(blacklist.get("sourcePaths", []))
    if relative_path in source_paths:
        return True, f"path:{relative_path}"

    return False, None


def is_valid_recipe_file(source_name: str, root: Path, path: Path) -> bool:
    if path.suffix.lower() != ".md":
        return False
    if path.name.upper() == "README.MD":
        return False
    relative = path.relative_to(root).as_posix()
    if source_name == "HowToCook":
        if not relative.startswith("dishes/"):
            return False
        if any(relative.startswith(prefix) for prefix in [
            "dishes/condiment/",
            "dishes/drink/",
            "dishes/dessert/",
            "dishes/template/",
            "dishes/semi-finished/",
        ]):
            return False
        return True
    top = relative.split("/", 1)[0]
    if top in COOKLIKEHOC_BLOCKED_TOP:
        return False
    return top in COOKLIKEHOC_ALLOWED_TOP


def imported_recipes() -> dict:
    scans = repo_sources()
    recipes = []
    skipped = []
    for scan in scans:
        for path in sorted(scan.root.rglob("*.md")):
            if not is_valid_recipe_file(scan.source_name, scan.root, path):
                skipped.append(path.relative_to(scan.root).as_posix())
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            relative = path.relative_to(scan.root).as_posix()
            title = title_from_text(text, path.stem)
            ingredients_raw = extract_ingredient_lines(text)
            ingredients = [normalize_ingredient_name(item) for item in ingredients_raw]
            ingredients = [item for item in ingredients if item]
            steps = extract_step_lines(text)
            method = summarize_method(steps)
            protein = infer_primary_protein(title, ingredients, relative)
            role = infer_dish_role(scan.source_name, relative, title, protein, ingredients)
            recipe = {
                "id": f"{scan.source_name}:{relative}",
                "sourceName": scan.source_name,
                "sourceRoot": str(scan.root),
                "sourcePath": str(path),
                "relativePath": relative,
                "title": title,
                "ingredients": unique_preserve(ingredients)[:12],
                "steps": steps[:6],
                "method": method,
                "protein": protein,
                "role": role,
                "vegTypes": infer_veg_types(title, ingredients),
                "tags": infer_cooking_tags(title, relative, ingredients, method),
                "estimatedMinutes": infer_minutes(title, relative, method),
                "difficulty": infer_difficulty(infer_minutes(title, relative, method), title, method),
                "signature": recipe_signature(
                    {
                        "title": title,
                        "sourceName": scan.source_name,
                        "relativePath": relative,
                        "ingredients": ingredients,
                    }
                ),
            }
            recipes.append(recipe)
    return {
        "version": 2,
        "generatedAt": datetime.now().isoformat(),
        "sources": [{"name": scan.source_name, "root": str(scan.root)} for scan in scans],
        "count": len(recipes),
        "skippedNonRecipes": len(skipped),
        "recipes": recipes,
    }


def refine_recipes(imported: dict) -> dict:
    chosen: dict[str, dict] = {}
    rejected = []
    preferences = ensure_preferences_file()
    blacklisted_count = 0
    for recipe in imported.get("recipes", []):
        recipe = dict(recipe)
        recipe["homeScore"] = home_score(recipe)
        recipe["nutritionScore"] = nutrition_score(recipe)
        recipe["weekdayFriendly"] = weekday_friendly(recipe)
        recipe["isPractical"] = recipe["homeScore"] >= 2 and recipe["role"] in {"main", "side", "soup"}
        recipe["useFrequency"] = "weekly-core" if recipe["homeScore"] >= 5 else "rotation"
        recipe["blacklistReason"] = None
        if recipe["role"] == "main" and recipe["protein"] == "other":
            recipe["isPractical"] = False
        if recipe["role"] == "main" and recipe["protein"] == "egg":
            recipe["isPractical"] = False
        if recipe["role"] == "main" and recipe["protein"] == "tofu" and not any(
            hint in recipe["title"] for hint in SUBSTANTIAL_TOFU_MAIN_HINTS
        ):
            recipe["isPractical"] = False
        if recipe["role"] == "main" and not has_raw_protein_anchor(recipe):
            recipe["isPractical"] = False
        if recipe["role"] == "main" and any(hint in recipe["title"] for hint in NON_MAIN_TITLE_HINTS):
            recipe["isPractical"] = False
        if recipe["role"] == "main" and recipe["sourceName"] == "HowToCook" and "dishes/vegetable_dish/" in recipe["relativePath"] and not title_has_main_anchor(recipe):
            recipe["isPractical"] = False
        if recipe["role"] == "main" and any(hint in recipe["title"] for hint in WEAK_MAIN_TITLE_HINTS):
            recipe["isPractical"] = False
        if any(token in recipe["method"] for token in CHAIN_STYLE_HINTS) and recipe["sourceName"] == "CookLikeHOC":
            recipe["isPractical"] = False
        if recipe["role"] == "main" and any(token in recipe["title"] for token in {"清炒", "凉拌"}) and recipe["protein"] not in {"beef", "chicken", "pork", "fish", "shrimp"}:
            recipe["isPractical"] = False
        if recipe["role"] == "main" and any(recipe["title"].startswith(prefix) for prefix in SIDE_STYLE_HINTS) and recipe["protein"] not in {"beef", "chicken", "pork", "fish", "shrimp"}:
            recipe["isPractical"] = False
        if recipe["role"] == "main" and any(token in recipe["title"] for token in {"小龙虾", "烤鱼", "火锅", "拌面", "盖饭"}):
            recipe["isPractical"] = False
        if recipe["role"] in {"side", "soup"} and recipe["nutritionScore"] <= 0:
            recipe["isPractical"] = False
        if recipe["role"] in {"side", "soup"} and any(token in recipe["title"] for token in SIDE_STAPLE_EXCLUDE_HINTS):
            recipe["isPractical"] = False
        if recipe["role"] == "soup" and any(token in recipe["title"] for token in HEAVY_SOUP_TITLE_HINTS) and not any(
            token in recipe["title"] for token in {"豆腐", "蛋花", "鸡蛋", "金针菇", "番茄", "黄瓜皮蛋", "罗宋"}
        ):
            recipe["isPractical"] = False
        blocked, reason = is_blacklisted(recipe, preferences)
        if blocked:
            recipe["isPractical"] = False
            recipe["blacklistReason"] = reason
            blacklisted_count += 1
        key = canonical_dedupe_key(recipe["title"], recipe["role"])
        prev = chosen.get(key)
        if prev is None:
            chosen[key] = recipe
            continue
        score_tuple = (
            recipe["isPractical"],
            recipe["homeScore"] + recipe["nutritionScore"],
            recipe["weekdayFriendly"],
            -recipe["difficulty"],
            recipe["sourceName"] == "HowToCook",
        )
        prev_tuple = (
            prev["isPractical"],
            prev["homeScore"] + prev["nutritionScore"],
            prev["weekdayFriendly"],
            -prev["difficulty"],
            prev["sourceName"] == "HowToCook",
        )
        if score_tuple > prev_tuple:
            rejected.append(prev)
            chosen[key] = recipe
        else:
            rejected.append(recipe)
    recipes = sorted(
        chosen.values(),
        key=lambda item: (
            item["isPractical"],
            item["role"] == "main",
            item["homeScore"] + item["nutritionScore"],
            item["weekdayFriendly"],
        ),
        reverse=True,
    )
    return {
        "version": 2,
        "generatedAt": datetime.now().isoformat(),
        "count": len(recipes),
        "recipes": recipes,
        "rejectedDuplicates": len(rejected),
        "blacklistedCount": blacklisted_count,
    }


def structured_pool(refined: dict) -> dict:
    practical = [recipe for recipe in refined.get("recipes", []) if recipe.get("isPractical")]
    mains = [recipe for recipe in practical if recipe["role"] == "main"]
    sides = [recipe for recipe in practical if recipe["role"] == "side"]
    soups = [recipe for recipe in practical if recipe["role"] == "soup"]
    pool_signature = sha1_text(
        "|".join(sorted(f'{recipe["id"]}:{recipe["signature"]}' for recipe in practical))
    )[:16]
    stats = {
        "sourceCounts": dict(Counter(recipe["sourceName"] for recipe in practical)),
        "roleCounts": dict(Counter(recipe["role"] for recipe in practical)),
        "proteinCounts": dict(Counter(recipe["protein"] for recipe in mains)),
        "weekdayFriendlyMainCount": sum(1 for recipe in mains if recipe["weekdayFriendly"]),
    }
    return {
        "version": 2,
        "generatedAt": datetime.now().isoformat(),
        "poolSignature": pool_signature,
        "profile": USER_PROFILE,
        "breakfastTemplates": BREAKFAST_TEMPLATES,
        "mains": mains,
        "sides": sides,
        "soups": soups,
        "recipes": practical,
        "stats": stats,
    }


def compatibility_recipe_pool(structured: dict) -> dict:
    return {
        "version": 3,
        "source": {
            "primary": "https://github.com/Anduin2017/HowToCook",
            "secondary": "https://github.com/Gar-b-age/CookLikeHOC",
        },
        "profile": structured["profile"],
        "breakfasts": structured["breakfastTemplates"],
        "mains": [
            compact_recipe(recipe)
            for recipe in structured["mains"][:120]
        ],
        "sides": [
            compact_recipe(recipe)
            for recipe in structured["sides"][:120]
        ] + [compact_recipe(recipe) for recipe in structured["soups"][:40]],
    }


def compact_recipe(recipe: dict) -> dict:
    return {
        "id": recipe["id"],
        "name": recipe["title"],
        "protein": recipe["protein"],
        "role": recipe["role"],
        "source": recipe["relativePath"],
        "tags": recipe["tags"],
        "ingredients": recipe["ingredients"][:6],
        "method": recipe["method"],
        "estimatedMinutes": recipe["estimatedMinutes"],
    }


def meal_pool(structured: dict) -> dict:
    return {
        "version": 2,
        "generatedAt": structured["generatedAt"],
        "poolSignature": structured["poolSignature"],
        "profile": structured["profile"],
        "breakfasts": structured["breakfastTemplates"],
        "mains": structured["mains"],
        "sides": structured["sides"],
        "soups": structured["soups"],
        "stats": structured["stats"],
    }


def protein_targets(pool: dict) -> list[str]:
    available = Counter(recipe["protein"] for recipe in pool["mains"])
    target_order = ["chicken", "fish", "beef", "pork", "shrimp", "chicken", "beef"]
    final = []
    fallback = [protein for protein, _count in available.most_common()]
    for protein in target_order:
        if available.get(protein, 0) > 0:
            final.append(protein)
        else:
            replacement = next((item for item in fallback if item not in final), fallback[0] if fallback else "chicken")
            final.append(replacement)
    return final


def history_penalties(history: list[dict]) -> tuple[dict[str, int], dict[str, int]]:
    main_penalty: dict[str, int] = {}
    side_penalty: dict[str, int] = {}
    today = date.today()
    for entry in history[-8:]:
        try:
            start = datetime.strptime(entry["weekStart"], "%Y-%m-%d").date()
        except Exception:
            continue
        weeks_ago = max(1, (today - start).days // 7)
        weight = max(1, 6 - weeks_ago)
        for recipe_id in entry.get("usedMainIds", []):
            main_penalty[recipe_id] = max(main_penalty.get(recipe_id, 0), weight)
        for recipe_id in entry.get("usedSideIds", []):
            side_penalty[recipe_id] = max(side_penalty.get(recipe_id, 0), weight)
    return main_penalty, side_penalty


def score_main_candidate(
    recipe: dict,
    day_name: str,
    target_protein: str,
    season: str,
    protein_counts: Counter,
    used_main_ids: set[str],
    recent_penalty: dict[str, int],
    previous_protein: str | None,
) -> int:
    profile = DAY_PROFILES[day_name]
    score = recipe["homeScore"] + recipe["nutritionScore"]
    if recipe["protein"] == target_protein:
        score += 6
    if recipe["weekdayFriendly"] and day_name in {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}:
        score += 3
    if recipe["estimatedMinutes"] <= profile["maxMinutes"]:
        score += 2
    else:
        score -= 3
    if profile["preferLight"] and "light" in recipe["tags"]:
        score += 2
    if profile["preferReheat"] and "reheats-well" in recipe["tags"]:
        score += 3
    if recipe["protein"] in {"fish", "shrimp"} and day_name in {"Monday", "Tuesday"} and not recipe["weekdayFriendly"]:
        score -= 3
    if day_name in {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"} and any(
        token in recipe["title"] for token in WHOLE_FISH_WEEKDAY_HINTS
    ):
        score -= 4
    if protein_counts[recipe["protein"]] >= 2:
        score -= 3
    if previous_protein and previous_protein == recipe["protein"]:
        score -= 2
    if recipe["id"] in used_main_ids:
        score -= 8
    if any(group in SEASON_VEG_BONUS[season] for group in recipe["vegTypes"]):
        score += 1
    score -= recent_penalty.get(recipe["id"], 0)
    if any(token in recipe["title"] for token in STAPLE_HINTS):
        score -= 4
    return score


def side_kind(recipe: dict) -> str:
    if recipe["role"] == "soup":
        return "soup"
    if recipe["protein"] == "egg":
        return "egg"
    if recipe["protein"] == "tofu":
        return "tofu"
    return "veg"


def score_side_candidate(
    recipe: dict,
    main_recipe: dict,
    season: str,
    side_counts: Counter,
    used_side_ids: set[str],
    recent_penalty: dict[str, int],
    previous_side_kind: str | None,
) -> int:
    score = recipe["homeScore"] + recipe["nutritionScore"]
    kind = side_kind(recipe)
    if kind == "soup" and main_recipe["estimatedMinutes"] > 35:
        score -= 2
    if main_recipe["estimatedMinutes"] <= 30 and kind == "veg":
        score += 1
    if main_recipe["protein"] in {"beef", "pork", "chicken"} and kind in {"veg", "soup"}:
        score += 2
    if main_recipe["protein"] in {"fish", "shrimp"} and "fresh" in recipe["vegTypes"]:
        score += 2
    if main_recipe["protein"] == "tofu" and kind in {"egg", "veg"}:
        score += 1
    if recipe["protein"] in SIDE_ANIMAL_PROTEIN_LIMIT:
        score -= 3
    if kind == "soup" and recipe["protein"] in {"egg", "tofu", "other"}:
        score += 1
    if main_recipe["protein"] in {"fish", "shrimp"} and kind == "soup" and recipe["protein"] in SIDE_ANIMAL_PROTEIN_LIMIT:
        score -= 2
    if main_recipe["protein"] in {"beef", "pork", "chicken"} and kind == "veg" and any(v in recipe["vegTypes"] for v in {"leafy", "cruciferous", "fresh"}):
        score += 1
    if any(group in SEASON_VEG_BONUS[season] for group in recipe["vegTypes"]):
        score += 2
    if side_counts[kind] >= 3:
        score -= 2
    if previous_side_kind and previous_side_kind == kind:
        score -= 1
    if recipe["id"] in used_side_ids:
        score -= 6
    score -= recent_penalty.get(recipe["id"], 0)
    return score


def choose_weighted(rng: random.Random, ranked: list[tuple[int, dict]]) -> dict:
    top = ranked[: min(5, len(ranked))]
    if len(top) == 1:
        return top[0][1]
    weights = []
    for index, (score, _item) in enumerate(top):
        weights.append(max(1, 6 - index) + max(0, score - top[-1][0]))
    return rng.choices([item for _score, item in top], weights=weights, k=1)[0]


def choose_breakfast(day_name: str, rng: random.Random) -> dict:
    weekday_index = WEEKDAYS.index(day_name)
    template = BREAKFAST_TEMPLATES[weekday_index % len(BREAKFAST_TEMPLATES)]
    return template


def collect_shopping(days: dict) -> dict:
    proteins = Counter()
    fresh = Counter()
    durable = Counter()
    breakfast = Counter()
    durable_keywords = {
        "土豆", "萝卜", "洋葱", "冬瓜", "南瓜", "胡萝卜", "包菜", "西兰花", "花菜", "香菇", "木耳",
        "金针菇", "豆腐", "豆干", "香干", "莴笋", "山药", "藕", "芹菜", "娃娃菜", "番茄",
    }
    for entry in days.values():
        for recipe in [entry["main"], entry["side"]]:
            for ingredient in recipe.get("ingredients", []):
                if any(token in ingredient for token in SHOPPING_EXCLUDE_HINTS):
                    continue
                if any(token in ingredient for token in {"鸡", "牛", "猪", "鱼", "虾", "豆腐", "蛋"}):
                    proteins[ingredient] += 1
                elif any(token in ingredient for token in {"番茄", "黄瓜", "青菜", "菠菜", "生菜", "油麦菜", "芹菜", "豆芽"}):
                    fresh[ingredient] += 1
                elif any(token in ingredient for token in durable_keywords):
                    durable[ingredient] += 1
        breakfast[choose_breakfast(entry["weekday"], random.Random(0))["name"]] += 1
    return {
        "protein": [item for item, _count in proteins.most_common(8)],
        "freshVeg": [item for item, _count in fresh.most_common(10)],
        "durableVeg": [item for item, _count in durable.most_common(10)],
        "breakfastStaples": ["燕麦", "鸡蛋", "酸奶", "全麦面包", "牛奶", "水果"],
        "fruitExtra": ["香蕉", "苹果", "橙子/梨", "小米椒/剁椒"],
    }


def compact_plan_recipe(recipe: dict) -> dict:
    return {
        "id": recipe["id"],
        "name": recipe["title"],
        "sourceName": recipe["sourceName"],
        "relativePath": recipe["relativePath"],
        "protein": recipe["protein"],
        "vegTypes": recipe["vegTypes"],
        "ingredients": recipe["ingredients"][:8],
        "method": recipe["method"],
        "estimatedMinutes": recipe["estimatedMinutes"],
        "weekdayFriendly": recipe["weekdayFriendly"],
        "tags": recipe["tags"],
    }


def plan_week(pool: dict, today: date | None = None) -> dict:
    today = today or date.today()
    start = week_start_for_day(today)
    state = load_json(STATE, default={"history": []})
    active = state.get("activeWeek")
    if active and active.get("weekStart") == start and active.get("poolSignature") == pool["poolSignature"]:
        return active

    season = season_for_month(today.month)
    targets = protein_targets(pool)
    history = state.get("history", [])
    main_penalty, side_penalty = history_penalties(history)
    seed = int(sha1_text(f"{start}|{pool['poolSignature']}")[:8], 16)
    rng = random.Random(seed)

    mains = pool["mains"]
    side_candidates = pool["sides"] + pool["soups"]
    days = {}
    protein_counts: Counter = Counter()
    side_counts: Counter = Counter()
    used_main_ids: set[str] = set()
    used_side_ids: set[str] = set()
    previous_protein = None
    previous_side_kind = None

    for day_name, target in zip(WEEKDAYS, targets):
        ranked_mains = sorted(
            (
                (
                    score_main_candidate(
                        recipe,
                        day_name,
                        target,
                        season,
                        protein_counts,
                        used_main_ids,
                        main_penalty,
                        previous_protein,
                    ),
                    recipe,
                )
                for recipe in mains
            ),
            key=lambda item: item[0],
            reverse=True,
        )
        main_recipe = choose_weighted(rng, ranked_mains)
        used_main_ids.add(main_recipe["id"])
        protein_counts[main_recipe["protein"]] += 1
        previous_protein = main_recipe["protein"]

        ranked_sides = sorted(
            (
                (
                    score_side_candidate(
                        recipe,
                        main_recipe,
                        season,
                        side_counts,
                        used_side_ids,
                        side_penalty,
                        previous_side_kind,
                    ),
                    recipe,
                )
                for recipe in side_candidates
            ),
            key=lambda item: item[0],
            reverse=True,
        )
        side_recipe = choose_weighted(rng, ranked_sides)
        used_side_ids.add(side_recipe["id"])
        previous_side_kind = side_kind(side_recipe)
        side_counts[previous_side_kind] += 1

        breakfast = choose_breakfast(day_name, rng)
        note_parts = []
        if "spicy-friendly" in main_recipe["tags"]:
            note_parts.append("可做微辣家常版")
        if main_recipe["estimatedMinutes"] > 40:
            note_parts.append("更适合周末或提前备菜")
        if not note_parts:
            note_parts.append("午餐主做，晚餐复热")

        days[day_name] = {
            "weekday": day_name,
            "weekdayCn": WEEKDAY_CN[day_name],
            "breakfast": breakfast["name"],
            "main": compact_plan_recipe(main_recipe),
            "side": compact_plan_recipe(side_recipe),
            "cookSet": f'{main_recipe["title"]} + {side_recipe["title"]} + 米饭',
            "dinnerReuse": "中午多做一份，晚上直接复热",
            "note": "；".join(note_parts),
        }

    weekly_buy = collect_shopping(days)
    weekly_plan = {
        "weekStart": start,
        "generatedAt": datetime.now().isoformat(),
        "poolSignature": pool["poolSignature"],
        "season": season,
        "proteinTargets": targets,
        "proteinCounts": dict(protein_counts),
        "days": days,
        "weeklyBuy": weekly_buy,
    }

    history.append(
        {
            "weekStart": start,
            "usedMainIds": [entry["main"]["id"] for entry in days.values()],
            "usedSideIds": [entry["side"]["id"] for entry in days.values()],
            "proteinCounts": dict(protein_counts),
            "poolSignature": pool["poolSignature"],
        }
    )
    history = history[-12:]
    save_json(
        STATE,
        {
            "version": 2,
            "updatedAt": datetime.now().isoformat(),
            "activeWeek": weekly_plan,
            "history": history,
        },
    )
    return weekly_plan


def render_week_markdown(weekly_plan: dict) -> str:
    lines = [
        "# 本周菜单",
        "",
        f"- 周起始: `{weekly_plan['weekStart']}`",
        f"- 季节偏好: `{weekly_plan['season']}`",
        f"- 做饭节奏: `午餐主做，晚餐复热`",
        "",
        "## 每日安排",
    ]
    for day_name in WEEKDAYS:
        entry = weekly_plan["days"][day_name]
        lines.extend(
            [
                f"### {entry['weekdayCn']}",
                f"- 早餐: `{entry['breakfast']}`",
                f"- 主菜: `{entry['main']['name']}`",
                f"- 配菜: `{entry['side']['name']}`",
                f"- 套餐: `{entry['cookSet']}`",
                f"- 备注: `{entry['note']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## 周采购建议",
            f"- 蛋白质: {'、'.join(f'`{item}`' for item in weekly_plan['weeklyBuy']['protein'])}",
            f"- 绿叶/鲜蔬: {'、'.join(f'`{item}`' for item in weekly_plan['weeklyBuy']['freshVeg'])}",
            f"- 耐放蔬菜: {'、'.join(f'`{item}`' for item in weekly_plan['weeklyBuy']['durableVeg'])}",
            f"- 早餐常备: {'、'.join(f'`{item}`' for item in weekly_plan['weeklyBuy']['breakfastStaples'])}",
            f"- 水果/调味: {'、'.join(f'`{item}`' for item in weekly_plan['weeklyBuy']['fruitExtra'])}",
        ]
    )
    return "\n".join(lines)


def render_weekly_message(weekly_plan: dict) -> str:
    lines = ["【本周菜谱计划】", "日期 | 主菜 | 配菜 | 备注"]
    for day_name in WEEKDAYS:
        entry = weekly_plan["days"][day_name]
        lines.append(
            f"{entry['weekdayCn']} | `{entry['main']['name']}` | `{entry['side']['name']}` | `{entry['note']}`"
        )
    lines.extend(
        [
            "",
            "【本周采购建议】",
            "类别 | 食材",
            "蛋白质 | " + "、".join(f'`{item}`' for item in weekly_plan["weeklyBuy"]["protein"]),
            "鲜蔬 | " + "、".join(f'`{item}`' for item in weekly_plan["weeklyBuy"]["freshVeg"]),
            "耐放菜 | " + "、".join(f'`{item}`' for item in weekly_plan["weeklyBuy"]["durableVeg"]),
            "早餐/主食 | " + "、".join(f'`{item}`' for item in weekly_plan["weeklyBuy"]["breakfastStaples"]),
            "水果/补充 | " + "、".join(f'`{item}`' for item in weekly_plan["weeklyBuy"]["fruitExtra"]),
        ]
    )
    return "\n".join(lines)


def render_daily_message(weekly_plan: dict, today: date | None = None) -> str:
    today = today or date.today()
    day_name = WEEKDAYS[today.weekday()]
    entry = weekly_plan["days"][day_name]
    lines = []
    if day_name == "Monday":
        lines.append(render_weekly_message(weekly_plan))
        lines.append("")
    lines.extend(
        [
            f"【今日菜谱｜{entry['weekdayCn']}】",
            "餐次 | 内容 | 备注",
            f"早餐 | `{entry['breakfast']}` | `简单高蛋白`",
            f"午餐 | `{entry['cookSet']}` | `{entry['note']}`",
            f"晚餐 | `{entry['dinnerReuse']}` | `不再重新选菜`",
            "",
            "【做法提示】",
            f"主菜 | `{entry['main']['method']}`",
            f"配菜 | `{entry['side']['method']}`",
            "",
            "【备注】",
            f"- `本周起始：{weekly_plan['weekStart']}`",
            "- `今天按本周计划执行，避免日内重排`",
        ]
    )
    return "\n".join(lines)
