# -*- coding: utf-8 -*-
"""从金山文档在线花名册 webhook 取数，组装 roster_v2.json
所有日期列按表头名称定位（列结构可能变动）。
输出：当前目录 roster_v2.json
"""
import json, urllib.request, io, datetime, os

URL = os.environ["KDOCS_WEBHOOK_URL"]
TOKEN = os.environ["KDOCS_AIRSCRIPT_TOKEN"]
EPOCH = datetime.date(1899, 12, 30)

def call(argv, tries=3):
    body = json.dumps({"Context": {"argv": argv}}).encode("utf-8")
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(URL, data=body, method="POST")
            req.add_header("Content-Type", "application/json")
            req.add_header("AirScript-Token", TOKEN)
            req.add_header("User-Agent", "Mozilla/5.0 (dashboard-updater)")
            with urllib.request.urlopen(req, timeout=180) as resp:
                d = json.loads(resp.read().decode("utf-8"))
            res = d.get("data", {}).get("result")
            if isinstance(res, str):
                res = json.loads(res)
            if res and res.get("ok"):
                return res
            last = res
        except Exception as e:
            last = repr(e)
    raise RuntimeError("webhook call failed: %r" % (last,))

def serial_to_date(s):
    try:
        n = float(s)
    except Exception:
        return s
    if not (20000 <= n <= 80000):
        return s
    return (EPOCH + datetime.timedelta(days=n)).strftime("%Y-%m-%d")

def fetch_sheet(name, total_rows, chunk=120):
    rows = []
    for start in range(1, total_rows + 1, chunk):
        end = min(start + chunk - 1, total_rows)
        res = call({"sheet": name, "from": start, "to": end})
        rows.extend(res.get("rows") or [])
    return rows

def convert_dates_by_header(rows, date_header_names):
    """在前3行内找到含目标列名的表头行，按列名定位日期列，转换 Excel 序列值为 YYYY-MM-DD"""
    if not rows:
        return rows
    header_i, idxs = None, []
    for hi in range(min(3, len(rows))):
        cand = rows[hi] or []
        found = [i for i, h in enumerate(cand) if h and str(h).strip() in date_header_names]
        if found:
            header_i, idxs = hi, found
            break
    if header_i is None:
        return rows
    for r in rows[header_i + 1:]:
        for c in idxs:
            if c < len(r) and r[c]:
                r[c] = serial_to_date(r[c])
    return rows

print("1) sheets info...")
info = call({})
sheets = {s["name"]: s for s in info["sheets"]}

mc_name = [n for n in sheets if n.strip() == "全员名册"][0]
zb_name = [n for n in sheets if n.strip() == "总表"][0]
jobs_name = [n for n in sheets if n.strip() == "招聘职位登记表"][0]
hire_name = [n for n in sheets if n.strip() == "录用登记"][0]

print("2) fetch 全员名册 ...")
mc_rows = fetch_sheet(mc_name, sheets[mc_name]["rows"])
print("3) fetch 总表 ...")
zb_rows = fetch_sheet(zb_name, sheets[zb_name]["rows"])
print("4) fetch 招聘职位登记表 ...")
jobs_rows = fetch_sheet(jobs_name, sheets[jobs_name]["rows"])
print("5) fetch 录用登记 ...")
hire_rows = fetch_sheet(hire_name, sheets[hire_name]["rows"])

# 日期列全部按表头名称定位
mc_rows = convert_dates_by_header(mc_rows, {"入职时间", "转正日期", "劳动合同到期日", "离职日期", "出生日期", "参加工作日期", "毕业时间"})
zb_rows = convert_dates_by_header(zb_rows, {"月份"})
jobs_rows = convert_dates_by_header(jobs_rows, {"发起日期", "计划入职日期", "关闭日期", "到岗时间"})
hire_rows = convert_dates_by_header(hire_rows, {"入职时间", "毕业时间"})

out = {
    mc_name: {"max_row": len(mc_rows), "max_col": sheets[mc_name]["cols"], "rows": mc_rows},
    zb_name: {"max_row": len(zb_rows), "max_col": sheets[zb_name]["cols"], "rows": zb_rows},
    jobs_name: {"max_row": len(jobs_rows), "max_col": sheets[jobs_name]["cols"], "rows": jobs_rows},
    hire_name: {"max_row": len(hire_rows), "max_col": sheets[hire_name]["cols"], "rows": hire_rows},
}
io.open("roster_v2.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print("DONE -> roster_v2.json")
