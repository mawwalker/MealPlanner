#!/usr/bin/env python3
import json, re
from pathlib import Path

BASE = Path('/home/dsm/.openclaw/workspace')
INP = BASE / 'diet' / 'imported_recipes.json'
OUT = BASE / 'diet' / 'refined_recipe_pool.json'

WEEKDAY_BAD = ['炸', '鸡爪', '肥肠', '扣肉', '大份', '嗨嗨锅', '锅', '烤鸭', '炸物桶', '鸡米花']
SEMI_FINISHED_HINTS = ['料包', '酱料', '中央厨房', '调理', '预制']
GOOD_REHEAT = ['炖', '煲', '烧', '焖', '牛腩', '麻婆', '鱼香', '豆腐', '黄焖']
FAST_HINTS = ['炒', '丝', '丁', '滑', '蒸蛋']
LIGHT_HINTS = ['蒸', '清', '汤', '凉拌', '豆腐', '西兰花', '生菜']
SPICY_HINTS = ['辣', '鱼香', '麻婆', '剁椒', '宫保', '贵州', '小炒']
VEG = ['青菜','生菜','油麦菜','西兰花','番茄','西红柿','黄瓜','木耳','香菇','土豆','青椒','萝卜','菠菜','菜心','娃娃菜','西葫芦']


def infer_minutes(name, method):
    s = name + ' ' + method
    if any(k in s for k in ['炖','煲','牛腩','黄焖']): return 45
    if any(k in s for k in ['蒸','汤羹']): return 20
    if any(k in s for k in ['炒','丝','丁']): return 20
    return 30


def score_home(rec):
    s = 0
    name = rec['name']; method = rec['method']; txt = name + ' ' + method + ' ' + ' '.join(rec.get('ingredients', []))
    if any(k in txt for k in SEMI_FINISHED_HINTS): s -= 3
    if any(k in name for k in WEEKDAY_BAD): s -= 3
    if any(k in txt for k in GOOD_REHEAT): s += 2
    if any(k in txt for k in FAST_HINTS): s += 1
    if any(k in txt for k in LIGHT_HINTS): s += 1
    if any(k in txt for k in SPICY_HINTS): s += 1
    if rec.get('protein') in {'beef','chicken','pork','tofu','fish','shrimp'}: s += 2
    if len(rec.get('ingredients', [])) <= 8: s += 1
    return s


def main():
    data = json.loads(INP.read_text())
    seen = {}
    refined = []
    for rec in data['recipes']:
        name = rec['name'].strip()
        rec['estimatedMinutes'] = infer_minutes(name, rec.get('method',''))
        rec['homeScore'] = score_home(rec)
        rec['reheatScore'] = 2 if any(k in (name + rec.get('method','')) for k in GOOD_REHEAT) else 0
        rec['weekdayFriendly'] = rec['estimatedMinutes'] <= 35 and not any(k in name for k in WEEKDAY_BAD)
        rec['light'] = any(k in (name + rec.get('method','')) for k in LIGHT_HINTS)
        rec['spicyFriendly'] = any(k in (name + rec.get('method','')) for k in SPICY_HINTS)
        rec['vegHits'] = [v for v in VEG if v in ' '.join(rec.get('ingredients', [])) or v in name]
        key = re.sub(r'\s+', '', name)
        old = seen.get(key)
        if old is None or rec['homeScore'] > old['homeScore']:
            seen[key] = rec
    refined = sorted(seen.values(), key=lambda x: (x['homeScore'], x['weekdayFriendly'], x['reheatScore']), reverse=True)
    OUT.write_text(json.dumps({'version': 1, 'count': len(refined), 'recipes': refined}, ensure_ascii=False, indent=2))
    usable = [r for r in refined if r['homeScore'] >= 2 and r['protein'] in {'beef','chicken','pork','tofu','fish','shrimp'}]
    print(f'refined={len(refined)} usable={len(usable)} top10=')
    for r in usable[:10]:
        print(f"- {r['name']} | {r['protein']} | score={r['homeScore']} | {r['sourceRepo']}")

if __name__ == '__main__':
    main()
