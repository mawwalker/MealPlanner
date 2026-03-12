#!/usr/bin/env python3
import json
from pathlib import Path

STATE = Path('/home/dsm/.openclaw/workspace/diet/state.json')
CN = {'Monday':'周一','Tuesday':'周二','Wednesday':'周三','Thursday':'周四','Friday':'周五','Saturday':'周六','Sunday':'周日'}
ORDER = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

state = json.loads(STATE.read_text())
wp = state.get('generatedWeekPlan')
if not wp:
    raise SystemExit('No generated week plan found')

lines = []
lines.append('【本周菜谱计划】')
lines.append('日期 | 主菜 | 配菜 | 备注')
for d in ORDER:
    e = wp['days'][d]
    lines.append(f"{CN[d]} | `{e['main']['name']}` | `{e['side']['name']}` | {e['note']}")
lines.append('')
lines.append('【本周采购建议】')
lines.append('类别 | 食材')
wb = wp['weeklyBuy']
lines.append('蛋白质 | ' + '、'.join(f'`{x}`' for x in wb.get('protein', [])))
lines.append('耐放蔬菜 | ' + '、'.join(f'`{x}`' for x in wb.get('durableVeg', [])))
lines.append('快手配菜 | ' + '、'.join(f'`{x}`' for x in wb.get('sideSupport', [])))
lines.append('早餐/主食 | ' + '、'.join(f'`{x}`' for x in wb.get('breakfastStaples', [])))
lines.append('水果/补充 | ' + '、'.join(f'`{x}`' for x in wb.get('fruitExtra', [])))
lines.append('')
lines.append('【备注】')
lines.append('- `午餐主做，晚餐复热`')
lines.append(f"- `本周起始：{wp['weekStart']}`")
print('\n'.join(lines))
