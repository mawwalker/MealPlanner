#!/usr/bin/env python3
import json, re
from pathlib import Path

OUT = Path('/home/dsm/.openclaw/workspace/diet/imported_recipes.json')
SRC1 = Path('/tmp/howtocook_repo/HowToCook-master')
SRC2 = Path('/tmp/cooklikehoc_repo/CookLikeHOC-main')

PROTEIN_MAP = [
    ('牛', 'beef'), ('鸡', 'chicken'), ('猪', 'pork'), ('排骨', 'pork'),
    ('鱼', 'fish'), ('虾', 'shrimp'), ('豆腐', 'tofu'), ('蛋', 'egg')
]
VEG_HINTS = ['青菜','生菜','油麦菜','西兰花','番茄','西红柿','黄瓜','木耳','香菇','土豆','青椒','萝卜','菠菜','菜心']
SPICY_HINTS = ['辣','剁椒','泡椒','麻婆','鱼香','宫保','贵州']
REHEAT_GOOD = ['炖','煲','烧','焖','黄焖','牛腩','豆腐','鱼香','麻婆']


def protein_of(name, text):
    s = name + '\n' + text
    for k,v in PROTEIN_MAP:
        if k in s:
            return v
    return 'other'


def tags_of(name, text):
    tags = []
    s = name + '\n' + text
    if any(k in s for k in SPICY_HINTS): tags.append('spicy')
    if any(k in s for k in REHEAT_GOOD): tags.append('reheats-well')
    if any(k in s for k in ['炒','丝','丁']): tags.append('workday')
    if any(k in s for k in ['鱼香','麻婆','剁椒','小炒','辣子鸡']): tags.append('jiangxi-friendly')
    return sorted(set(tags))


def ingredients_from(text):
    lines = [x.strip('-* 	') for x in text.splitlines()]
    vals = []
    in_section = False
    for ln in lines:
        if not ln or ln.startswith('![') or ln.startswith('#'):
            continue
        if any(h in ln for h in ['原料','配料','必备原料']):
            in_section = True
            continue
        if any(h in ln for h in ['步骤', '操作', '做法', '附加内容']):
            in_section = False
        if not in_section:
            continue
        if len(ln) > 30:
            continue
        if any(bad in ln for bad in ['推荐', '灵魂', '创作', '中央厨房', '详细成分']):
            continue
        clean = re.sub(r'[（(].*?[)）]', '', ln).strip('：:，,。.;； ')
        if not clean or len(clean) < 2:
            continue
        vals.append(clean)
        if len(vals) >= 8:
            break
    return list(dict.fromkeys(vals))[:8]


def method_from(text):
    lines = [x.strip('-* 	') for x in text.splitlines() if x.strip()]
    step_lines = [ln for ln in lines if re.match(r'^[0-9一二三四五六七八九十]+[.、]', ln) or '下入' in ln or '加入' in ln or '翻炒' in ln or '焖' in ln or '蒸' in ln]
    brief = '；'.join(step_lines[:3])
    return brief[:120] if brief else '参考原文步骤制作。'


def scan_md(root, source_name):
    items = []
    for p in root.rglob('*.md'):
        if 'README' in p.name: continue
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        name = p.stem
        if len(text) < 30: continue
        items.append({
            'id': f'{source_name}:{p.relative_to(root).as_posix()}',
            'name': name,
            'sourceRepo': source_name,
            'sourcePath': str(p),
            'protein': protein_of(name, text),
            'tags': tags_of(name, text),
            'ingredients': ingredients_from(text),
            'method': method_from(text)
        })
    return items

all_items = []
if SRC1.exists(): all_items += scan_md(SRC1, 'HowToCook')
if SRC2.exists(): all_items += scan_md(SRC2, 'CookLikeHOC')
OUT.write_text(json.dumps({'version':1,'count':len(all_items),'recipes':all_items}, ensure_ascii=False, indent=2))
print(f'imported {len(all_items)} recipes -> {OUT}')
