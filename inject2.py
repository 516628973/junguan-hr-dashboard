# -*- coding: utf-8 -*-
"""读取 roster_v2.json 与模板，生成 index.html（GitHub Actions 版，相对路径）"""
import json, io

tpl = io.open('dashboard_template_v2.html', encoding='utf-8').read()
data = json.load(io.open('dashboard_data_v2.json', encoding='utf-8'))
js = json.dumps(data, ensure_ascii=False)
out = tpl.replace('/*__DATA__*/', js)
io.open('index.html', 'w', encoding='utf-8').write(out)
print('OK, size:', len(out))
