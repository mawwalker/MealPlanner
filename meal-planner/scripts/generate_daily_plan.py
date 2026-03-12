#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

BASE = Path('/home/dsm/.openclaw/workspace')
STATE = BASE / 'diet' / 'state.json'
WEEKDAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
CN = {'Monday':'周一','Tuesday':'周二','Wednesday':'周三','Thursday':'周四','Friday':'周五','Saturday':'周六','Sunday':'周日'}

def load_json(p):
    return json.loads(p.read_text())

def concise_method(name, raw):
    raw = (raw or '').strip('` ')
    if any(k in name for k in ['鸡丁','肉丝','牛肉','牛柳']):
        return '`肉先炒香，再下配菜大火快炒，最后调味收汁。`'
    if any(k in name for k in ['麻婆豆腐','豆腐']):
        return '`先炒香肉末和酱料，再下豆腐小火烧入味。`'
    if any(k in name for k in ['鱼']):
        return '`鱼先处理干净，再煎/烧至入味，出锅前收汁。`'
    if any(k in name for k in ['鸡','黄焖']):
        return '`鸡肉先炒香，再和配菜一起焖到入味。`'
    return f'`{raw[:28]}...`' if len(raw) > 30 else f'`{raw}`'


def render():
    state = load_json(STATE)
    wp = state.get('generatedWeekPlan')
    if not wp:
        raise RuntimeError('No generated week plan found; run plan_week.py first')
    day = WEEKDAYS[datetime.now().weekday()]
    entry = wp['days'][day]
    lines = []
    lines.append(f'【今日菜谱｜{CN[day]}】')
    lines.append('餐次 | 内容 | 备注')
    lines.append(f"早餐 | {entry['breakfast']} | `简单高蛋白`")
    lines.append(f"午餐 | {entry['cookOnce']} | {entry['note']}")
    lines.append(f"晚餐 | {entry['dinnerReuse']} | `一天只做一次菜`")
    lines.append('')
    lines.append('【做法】')
    lines.append(f"主菜 | {concise_method(entry['main']['name'], entry['main']['method'])}")
    lines.append(f"配菜 | {entry['side']['method']}")
    lines.append('')
    lines.append('【备注】')
    lines.append('- `本周采购按周计划执行`')
    lines.append(f"- `本周起始：{wp['weekStart']}`")
    return '\n'.join(lines)

if __name__ == '__main__':
    print(render())
