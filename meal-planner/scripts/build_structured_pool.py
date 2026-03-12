#!/usr/bin/env python3
import json, re
from pathlib import Path

BASE = Path('/home/dsm/.openclaw/workspace')
INP = BASE / 'diet' / 'refined_recipe_pool.json'
OUT = BASE / 'diet' / 'structured_recipe_pool.json'

PROTEIN_PRIORITY = [
    ('牛腩', 'beef'), ('牛柳', 'beef'), ('牛肉', 'beef'),
    ('鸡腿', 'chicken'), ('鸡翅', 'chicken'), ('鸡块', 'chicken'), ('鸡丁', 'chicken'), ('鸡', 'chicken'),
    ('排骨', 'pork'), ('肉丝', 'pork'), ('肉末', 'pork'), ('猪肉', 'pork'),
    ('虾仁', 'shrimp'), ('虾', 'shrimp'),
    ('鱼头', 'fish'), ('鱼块', 'fish'), ('鱼', 'fish'),
    ('豆腐', 'tofu')
]
LEAFY = ['青菜','生菜','油麦菜','菠菜','菜心','娃娃菜','空心菜','包菜']
CRUCIF = ['西兰花','花菜']
FUNGI = ['木耳','香菇','金针菇','菌菇']
COLOR = ['番茄','西红柿','青椒','胡萝卜','南瓜']
AVOID = ['README','料','蘸料','酱料','调味','饮品']
LIGHT_MAIN_HINTS = ['蒸','清','汤','滑','豆腐','鱼','虾']
HEAVY_HINTS = ['炸','扣肉','肥肠','鸡爪','大份','锅']


def infer_protein(name, ingredients):
    text = name + ' ' + ' '.join(ingredients)
    for key, val in PROTEIN_PRIORITY:
        if key in text:
            return val
    return 'other'

def infer_veg_types(name, ingredients):
    text = name + ' ' + ' '.join(ingredients)
    kinds = []
    if any(x in text for x in LEAFY): kinds.append('leafy')
    if any(x in text for x in CRUCIF): kinds.append('cruciferous')
    if any(x in text for x in FUNGI): kinds.append('fungi')
    if any(x in text for x in COLOR): kinds.append('colorful')
    return kinds or ['other']

def simplify_method(method):
    method = re.sub(r'\s+', ' ', method).strip('；; ')
    parts = [p.strip() for p in re.split(r'[；;]', method) if p.strip()]
    clean = []
    for p in parts:
        if any(bad in p for bad in ['份数 *', '覆盖锅底', '180℃', '程序员', '灵魂操作']):
            continue
        clean.append(p)
    if not clean:
        return '参考原文步骤制作。'
    return '；'.join(clean[:2])[:60]

def normalize(r):
    name = r['name']
    ingredients = r.get('ingredients', [])
    text = name + ' ' + ' '.join(ingredients) + ' ' + r.get('method','')
    return {
        'id': r['id'],
        'name': name,
        'sourceRepo': r['sourceRepo'],
        'sourcePath': r['sourcePath'],
        'protein': infer_protein(name, ingredients),
        'vegTypes': infer_veg_types(name, ingredients),
        'tags': r.get('tags', []),
        'ingredients': ingredients[:6],
        'method': simplify_method(r.get('method', '')),
        'estimatedMinutes': r.get('estimatedMinutes', 30),
        'reheatScore': r.get('reheatScore', 0),
        'weekdayFriendly': bool(r.get('weekdayFriendly')),
        'light': bool(r.get('light')) or any(k in text for k in LIGHT_MAIN_HINTS),
        'heavy': any(k in text for k in HEAVY_HINTS),
        'spicyFriendly': bool(r.get('spicyFriendly')),
        'homeScore': r.get('homeScore', 0)
    }

raw = json.loads(INP.read_text())['recipes']
out = []
for r in raw:
    if any(x in r['name'] for x in AVOID):
        continue
    nr = normalize(r)
    if nr['protein'] == 'other':
        continue
    if nr['homeScore'] < 2:
        continue
    out.append(nr)
OUT.write_text(json.dumps({'version':1,'count':len(out),'recipes':out}, ensure_ascii=False, indent=2))
print(f'structured={len(out)} -> {OUT}')
counts = {}
for r in out:
    counts[r['protein']] = counts.get(r['protein'],0)+1
print(counts)
