#!/usr/bin/env python3
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path('/home/dsm/.openclaw/workspace')
RECIPES = BASE / 'diet' / 'structured_recipe_pool.json'
STATE = BASE / 'diet' / 'state.json'
WEEKDAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

# Multiple valid protein patterns — rotated each week for variety
# Constraints preserved: chicken x2, beef x1-2, pork x1, fish/shrimp x2, tofu x1
PROTEIN_PATTERNS = [
    ['beef',  'chicken','pork',   'tofu',   'chicken','fish',  'shrimp'],
    ['chicken','beef',  'fish',   'chicken','pork',   'shrimp','tofu'],
    ['pork',  'chicken','beef',   'fish',   'chicken','tofu',  'shrimp'],
    ['fish',  'chicken','beef',   'tofu',   'pork',   'chicken','shrimp'],
    ['chicken','pork',  'fish',   'beef',   'chicken','shrimp','tofu'],
    ['shrimp','chicken','pork',   'chicken','beef',   'fish',  'tofu'],
    ['beef',  'fish',   'chicken','pork',   'shrimp', 'chicken','tofu'],
]

BREAKFASTS = {
    'Monday':    '`燕麦 + 鸡蛋2个 + 无糖酸奶 + 香蕉`',
    'Tuesday':   '`全麦面包 + 鸡蛋2个 + 牛奶 + 苹果`',
    'Wednesday': '`玉米 + 鸡蛋2个 + 无糖酸奶 + 橙子`',
    'Thursday':  '`燕麦粥 + 茶叶蛋2个 + 梨`',
    'Friday':    '`全麦吐司 + 鸡蛋2个 + 牛奶`',
    'Saturday':  '`山药粥 + 水煮蛋2个 + 苹果`',
    'Sunday':    '`杂粮粥 + 鸡蛋2个 + 酸奶`',
}

SIDES = [
    {'name':'蒜蓉西兰花',     'method':'`西兰花焯水后淋蒜蓉汁。`',             'vegType':'cruciferous','light':True,'substantial':2,'kind':'veg'},
    {'name':'凉拌黄瓜',       'method':'`黄瓜拍碎切段凉拌。`',                  'vegType':'fresh',      'light':True,'substantial':0,'kind':'cold'},
    {'name':'炒青菜',         'method':'`大火快炒至断生。`',                     'vegType':'leafy',      'light':True,'substantial':1,'kind':'veg'},
    {'name':'蚝油生菜',       'method':'`生菜快炒后淋蚝油汁。`',                 'vegType':'leafy',      'light':True,'substantial':1,'kind':'veg'},
    {'name':'凉拌木耳',       'method':'`木耳焯水后凉拌。`',                     'vegType':'fungi',      'light':True,'substantial':1,'kind':'cold'},
    {'name':'西红柿豆腐汤羹', 'method':'`番茄炒出汁后加豆腐煮开。`',             'vegType':'colorful',   'light':True,'substantial':2,'kind':'soup'},
    {'name':'蒜泥菠菜',       'method':'`菠菜焯水后加蒜泥拌匀。`',               'vegType':'leafy',      'light':True,'substantial':1,'kind':'veg'},
    {'name':'清炒油麦菜',     'method':'`油麦菜大火快炒，保持脆嫩。`',           'vegType':'leafy',      'light':True,'substantial':1,'kind':'veg'},
    {'name':'凉拌番茄',       'method':'`番茄切块后简单凉拌。`',                  'vegType':'colorful',   'light':True,'substantial':0,'kind':'cold'},
    {'name':'清炒包菜',       'method':'`包菜大火快炒到断生。`',                  'vegType':'leafy',      'light':True,'substantial':2,'kind':'veg'},
    {'name':'香菇青菜',       'method':'`香菇和青菜同炒，鲜味更足。`',            'vegType':'fungi',      'light':True,'substantial':2,'kind':'mixed'},
    {'name':'番茄炒蛋',       'method':'`番茄炒出汁后下蛋快速翻匀。`',            'vegType':'colorful',   'light':True,'substantial':2,'kind':'egg'},
    {'name':'木耳炒鸡蛋',     'method':'`木耳和鸡蛋快炒，口感更扎实。`',          'vegType':'fungi',      'light':True,'substantial':2,'kind':'egg'},
    {'name':'炝炒豆芽',       'method':'`豆芽大火快炒，保持脆爽。`',              'vegType':'fresh',      'light':True,'substantial':1,'kind':'veg'},
    {'name':'青椒炒鸡蛋',     'method':'`青椒和鸡蛋快炒，香味足也下饭。`',        'vegType':'colorful',   'light':True,'substantial':2,'kind':'egg'},
    {'name':'西葫芦炒鸡蛋',   'method':'`西葫芦切片后和鸡蛋快炒。`',              'vegType':'colorful',   'light':True,'substantial':2,'kind':'egg'},
    {'name':'家常豆腐',       'method':'`豆腐煎到定型后再烧入味。`',              'vegType':'other',      'light':False,'substantial':2,'kind':'tofu'},
    {'name':'青椒豆干',       'method':'`豆干和青椒一起快炒，更有咬劲。`',         'vegType':'colorful',   'light':True,'substantial':2,'kind':'tofu'},
    {'name':'香干芹菜',       'method':'`香干和芹菜快炒，清爽又有层次。`',          'vegType':'fresh',      'light':True,'substantial':2,'kind':'tofu'},
    {'name':'黄瓜木耳炒蛋',   'method':'`黄瓜木耳和鸡蛋一起快炒，口感更完整。`',  'vegType':'fungi',      'light':True,'substantial':2,'kind':'egg'},
    {'name':'蒜蓉娃娃菜',     'method':'`娃娃菜蒜蓉快炒或蒸后淋汁。`',            'vegType':'leafy',      'light':True,'substantial':2,'kind':'veg'},
    {'name':'上汤娃娃菜',     'method':'`娃娃菜加高汤煮到入味。`',                'vegType':'leafy',      'light':True,'substantial':2,'kind':'soup'},
    {'name':'手撕包菜',       'method':'`包菜手撕后大火快炒，更有锅气。`',         'vegType':'leafy',      'light':True,'substantial':2,'kind':'veg'},
    {'name':'蒜蓉空心菜',     'method':'`空心菜大火快炒，保持爽脆。`',             'vegType':'leafy',      'light':True,'substantial':2,'kind':'veg'},
    {'name':'金针菇日本豆腐煲','method':'`豆腐和金针菇烧入味，口感更完整。`',      'vegType':'fungi',      'light':True,'substantial':3,'kind':'tofu'},
    {'name':'菠菜炒鸡蛋',     'method':'`菠菜焯后和鸡蛋快炒，扎实又顺口。`',      'vegType':'leafy',      'light':True,'substantial':2,'kind':'egg'},
    {'name':'鸡蛋火腿炒黄瓜', 'method':'`黄瓜、鸡蛋和火腿快炒，更像完整配菜。`', 'vegType':'fresh',      'light':True,'substantial':2,'kind':'mixed'},
    {'name':'冬瓜排骨汤',     'method':'`排骨焯水后和冬瓜慢炖，清甜鲜香。`',      'vegType':'colorful',   'light':True,'substantial':3,'kind':'soup'},
    {'name':'蒜蓉炒豆角',     'method':'`豆角焯水后蒜蓉大火快炒。`',              'vegType':'fresh',      'light':True,'substantial':2,'kind':'veg'},
    {'name':'素炒三丝',       'method':'`土豆丝、胡萝卜丝、青椒丝大火翻炒。`',    'vegType':'colorful',   'light':True,'substantial':2,'kind':'veg'},
    {'name':'白灼芥蓝',       'method':'`芥蓝焯水后淋生抽蒜油。`',               'vegType':'cruciferous','light':True,'substantial':2,'kind':'veg'},
    {'name':'香煎杏鲍菇',     'method':'`杏鲍菇切片煎到两面金黄，撒盐出锅。`',    'vegType':'fungi',      'light':True,'substantial':2,'kind':'veg'},
    {'name':'蒜蓉粉丝蒸南瓜', 'method':'`南瓜铺粉丝蒸熟后淋蒜蓉汁。`',           'vegType':'colorful',   'light':True,'substantial':3,'kind':'mixed'},
]

BAD_MAINS        = {'葱煎豆腐','黄瓜皮蛋汤','鲜肉烧卖','香辣牛肉面','鱼香茄子','鱼香肉丝'}
BAD_WEEKDAY_MAINS = {'红烧鲤鱼','红烧鱼','小龙虾','鲜肉烧卖','笋子鸡丁盖饭','香辣牛肉面',
                     '香辣鸡丁拌面','盖饭','包菜炒鸡蛋粉丝','拌面','炒面','雪菜肉丝面'}
BAD_WEEKEND_MAINS = {'小龙虾','鲜肉烧卖','香辣牛肉面'}
TOFU_EXCEPTIONS  = {'麻婆豆腐'}

# How many recent weeks to penalise (avoids repeating same dishes too soon)
HISTORY_PENALTY_WEEKS = 4

def load(p): return json.loads(p.read_text())
def save(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
def week_start(dt): return (dt - timedelta(days=dt.weekday())).date().isoformat()


def build_recent_penalty(history):
    """Return {recipe_id: penalty_score} for recipes used in recent weeks."""
    penalty = {}
    now = datetime.now().date()
    for entry in history:
        try:
            ws = datetime.strptime(entry['weekStart'], '%Y-%m-%d').date()
        except Exception:
            continue
        weeks_ago = (now - ws).days // 7
        if weeks_ago <= 0:
            continue  # skip current week's own entry if any
        if weeks_ago <= HISTORY_PENALTY_WEEKS:
            # heavier penalty for more recent weeks
            p = max(1, 6 - weeks_ago)   # weeks_ago=1 → 5, =2 → 4, =3 → 3, =4 → 2
            for rid in entry.get('usedRecipeIds', []):
                penalty[rid] = max(penalty.get(rid, 0), p)
    return penalty


def pick_protein_pattern(history):
    """Pick a protein pattern that rotates differently each week."""
    if not history:
        return PROTEIN_PATTERNS[0]
    # Use week index modulo number of patterns
    # Count how many weeks of history we have to advance the pattern
    week_index = len(history)
    return PROTEIN_PATTERNS[week_index % len(PROTEIN_PATTERNS)]


def score_main(r, desired, used_names, protein_counts, weekday, prev_protein, recent_penalty):
    s = r['homeScore']
    animal = {'chicken','beef','pork','fish','shrimp'}
    is_weekday = weekday in ('Monday','Tuesday','Wednesday','Thursday','Friday')
    is_weekend = weekday in ('Saturday','Sunday')

    if r['protein'] == desired:               s += 6
    if r['protein'] in animal:                s += 3
    if protein_counts.get(r['protein'], 0) == 0: s += 2
    if r['reheatScore'] > 0:                  s += 2
    if is_weekday and r['weekdayFriendly']:   s += 2
    if r['spicyFriendly']:                    s += 1
    if r['name'] in used_names:               s -= 8   # stronger same-week penalty
    if protein_counts.get(r['protein'], 0) >= 2: s -= 2
    if prev_protein and prev_protein == r['protein']: s -= 3
    if is_weekday and r['estimatedMinutes'] > 40: s -= 2
    if is_weekday and r.get('heavy'):         s -= 2
    if r['name'] in BAD_MAINS:               s -= 5
    if is_weekday and r['name'] in BAD_WEEKDAY_MAINS: s -= 6
    if is_weekend and r['name'] in BAD_WEEKEND_MAINS: s -= 5
    if r['protein'] in {'tofu','egg'}:        s -= 5
    if r['protein'] == 'tofu' and r['name'] in TOFU_EXCEPTIONS: s += 2
    if r['protein'] in {'tofu','fish','shrimp'} and not r['light']: s -= 1
    if is_weekday and any(k in r['name'] for k in ['鱼','虾']) and not r['weekdayFriendly']:
        s -= 3
    if is_weekend and any(k in r['name'] for k in ['蒸','烧','焖','炖']):
        s += 1
    # Penalise noodle/rice-bowl style dishes (not suitable as main + side structure)
    if any(k in r['name'] for k in ['面','饭','拌','盖浇']):
        s -= 6

    # Cross-week history penalty
    rid = r.get('id', r['name'])
    s -= recent_penalty.get(rid, 0)

    return s


def choose_main(recipes, desired, used_names, protein_counts, weekday, prev_protein, recent_penalty):
    ranked = sorted(
        recipes,
        key=lambda r: score_main(r, desired, used_names, protein_counts, weekday, prev_protein, recent_penalty),
        reverse=True
    )
    # Pick from top-3 candidates with weighted randomness to ensure variety
    pool = ranked[:3]
    weights = [4, 2, 1][:len(pool)]
    return random.choices(pool, weights=weights, k=1)[0]


def score_side(s, side_counts, side_name_counts, main, prev_side_name, recent_side_names):
    desired_order = ['leafy','cruciferous','fungi','colorful','fresh']
    if main.get('spicyFriendly'):
        desired_order = ['leafy','fungi','colorful','fresh','cruciferous']
    main_name = main.get('name', '')

    x = 0
    x -= side_counts.get(s['vegType'], 0) * 3
    x -= side_counts.get(s.get('kind', 'veg'), 0) * 2
    x -= side_name_counts.get(s['name'], 0) * 4
    if s['name'] == prev_side_name:                       x -= 8
    if s['name'] in recent_side_names:                    x -= 3
    if main.get('heavy') and s['light']:                  x += 2
    if main.get('spicyFriendly') and s['vegType'] in {'leafy','fungi','colorful'}: x += 2
    x += s.get('substantial', 0) * 2
    if s.get('kind') == 'cold':                           x -= 1
    if s.get('kind') in {'egg','tofu','mixed','soup'}:    x += 3
    if s['vegType'] in {'leafy','cruciferous','colorful','fungi'}: x += 1

    if any(k in main_name for k in ['鸡丁','宫保','小炒','排骨','肉']) and s.get('kind') in {'veg','mixed','soup'}:
        x += 2
    if any(k in main_name for k in ['鸡丁','宫保']) and s['name'] in {'香菇青菜','上汤娃娃菜','蒜蓉西兰花','清炒包菜'}:
        x += 2
    if any(k in main_name for k in ['鱼']) and s.get('kind') in {'veg','fungi','cold','egg'}:
        x += 2
    if any(k in main_name for k in ['鱼']) and s['name'] in {'蒜蓉西兰花','番茄炒蛋','香菇青菜','凉拌木耳'}:
        x += 2
    if any(k in main_name for k in ['豆腐']) and s.get('kind') in {'veg','egg','mixed'}:
        x += 2
    if any(k in main_name for k in ['牛肉']) and s['vegType'] in {'leafy','cruciferous','colorful'}:
        x += 2
    if any(k in main_name for k in ['牛肉']) and s['name'] in {'清炒包菜','上汤娃娃菜','蒜蓉西兰花'}:
        x += 2
    x -= desired_order.index(s['vegType']) if s['vegType'] in desired_order else 99
    return x


def choose_side(side_counts, side_name_counts, main, prev_side_name, recent_side_names):
    ranked = sorted(
        SIDES,
        key=lambda s: score_side(s, side_counts, side_name_counts, main, prev_side_name, recent_side_names),
        reverse=True
    )
    # Pick from top-3 side candidates
    pool = ranked[:3]
    weights = [4, 2, 1][:len(pool)]
    return random.choices(pool, weights=weights, k=1)[0]


def build_weekly_buy(days):
    """Generate a shopping list tailored to this week's actual plan."""
    proteins_needed = set()
    for entry in days.values():
        p = entry['main']['protein']
        if p == 'chicken':   proteins_needed.add('鸡肉')
        elif p == 'beef':    proteins_needed.add('牛肉')
        elif p == 'pork':    proteins_needed.add('猪肉/排骨')
        elif p == 'fish':    proteins_needed.add('鱼')
        elif p == 'shrimp':  proteins_needed.add('虾')
        elif p == 'tofu':    proteins_needed.add('豆腐')
    proteins_needed.add('鸡蛋')  # always needed for breakfast

    sides_needed = set()
    for entry in days.values():
        vt = entry['side']['vegType']
        if vt == 'leafy':       sides_needed.update(['菠菜/青菜','娃娃菜'])
        elif vt == 'cruciferous': sides_needed.add('西兰花/芥蓝')
        elif vt == 'fungi':     sides_needed.update(['香菇','木耳'])
        elif vt == 'colorful':  sides_needed.update(['番茄','青椒'])
        elif vt == 'fresh':     sides_needed.update(['黄瓜','豆芽'])

    return {
        'protein':         sorted(proteins_needed),
        'durableVeg':      ['土豆','洋葱','西兰花','胡萝卜','冬瓜/南瓜'],
        'sideSupport':     sorted(sides_needed) + ['豆干/香干','鸡蛋'],
        'breakfastStaples':['燕麦','大米','全麦面包','酸奶','牛奶'],
        'fruitExtra':      ['香蕉','苹果','橙子/梨','小米椒/剁椒'],
    }


def main():
    rec = load(RECIPES)['recipes']
    state = load(STATE)
    start = week_start(datetime.now())

    # Skip if this week's plan already exists
    if state.get('generatedWeekStart') == start and state.get('generatedWeekPlan'):
        print('existing'); return

    history = state.get('history', [])
    recent_penalty = build_recent_penalty(history)
    recent_side_names = set()
    for entry in history[-2:]:   # avoid sides from last 2 weeks too
        recent_side_names.update(entry.get('usedSideNames', []))

    pattern = pick_protein_pattern(history)

    used_names = set()
    protein_counts = {}
    side_counts = {}
    side_name_counts = {}
    prev_side_name = None
    prev_protein = None
    days = {}

    for day, want in zip(WEEKDAYS, pattern):
        candidates = [r for r in rec if r['protein'] in {'beef','chicken','pork','tofu','fish','shrimp'}]
        if day in ('Monday','Tuesday','Wednesday','Thursday','Friday'):
            animal_candidates = [r for r in candidates if r['protein'] in {'beef','chicken','pork','fish','shrimp'}]
            if animal_candidates:
                candidates = animal_candidates

        main_recipe = choose_main(candidates, want, used_names, protein_counts, day, prev_protein, recent_penalty)
        used_names.add(main_recipe['name'])
        protein_counts[main_recipe['protein']] = protein_counts.get(main_recipe['protein'], 0) + 1
        prev_protein = main_recipe['protein']

        side = choose_side(side_counts, side_name_counts, main_recipe, prev_side_name, recent_side_names)
        prev_side_name = side['name']
        side_counts[side['vegType']] = side_counts.get(side['vegType'], 0) + 1
        side_name_counts[side['name']] = side_name_counts.get(side['name'], 0) + 1

        days[day] = {
            'breakfast':   BREAKFASTS[day],
            'main':        main_recipe,
            'side':        side,
            'cookOnce':    f"`{main_recipe['name']} + {side['name']} + 米饭`",
            'dinnerReuse': '`中午留一份，晚上复热`',
            'note':        '`可做微辣版`' if main_recipe['spicyFriendly'] else '`口味清爽`',
        }

    weekly_plan = {
        'weekStart':      start,
        'days':           days,
        'weeklyBuy':      build_weekly_buy(days),
        'proteinCounts':  protein_counts,
        'sideDiversity':  side_counts,
    }

    # Save this week to history (keep last 8 weeks max)
    history_entry = {
        'weekStart':      start,
        'usedRecipeIds':  [d['main'].get('id', d['main']['name']) for d in days.values()],
        'usedRecipeNames':[d['main']['name'] for d in days.values()],
        'usedSideNames':  [d['side']['name'] for d in days.values()],
        'proteinPattern': pattern,
    }
    history.append(history_entry)
    if len(history) > 8:
        history = history[-8:]

    state['generatedWeekStart'] = start
    state['generatedAt']        = datetime.now().isoformat()
    state['generatedWeekPlan']  = weekly_plan
    state['history']            = history
    save(STATE, state)
    print('generated')


if __name__ == '__main__':
    main()
