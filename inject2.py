# -*- coding: utf-8 -*-
"""读取模板与数据，生成 index.html（GitHub Actions 版，相对路径）。
ECharts 直接内联进 HTML，彻底去除外部 CDN 依赖，避免浏览器广告拦截/网络封锁导致图表空白。"""
import json, io

tpl = io.open('dashboard_template_v2.html', encoding='utf-8').read()
data = json.load(io.open('dashboard_data_v2.json', encoding='utf-8'))
js = json.dumps(data, ensure_ascii=False)

ech = io.open('echarts.min.js', encoding='utf-8').read()
assert '</script' not in ech.lower(), 'echarts source contains </script> which would break inline embedding'

out = tpl.replace('/*__ECHARTS__*/', ech).replace('/*__DATA__*/', js)
io.open('index.html', 'w', encoding='utf-8').write(out)
print('OK, size:', len(out))
