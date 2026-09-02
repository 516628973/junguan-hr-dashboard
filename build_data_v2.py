# -*- coding: utf-8 -*-
import json, io, datetime as _dt
from collections import Counter

d = json.load(io.open(r'roster_v2.json', encoding='utf-8'))
hmc = d['全员名册']['rows']
zb  = d['总表 ']['rows']

# ---------- 全员名册行（列表，保留同名）----------
# 按表头名称定位列（表结构可能变动，避免固定索引错位）
hm = {}
for _i, _h in enumerate(hmc[0]):
    if _h and _h.strip():
        hm.setdefault(_h.strip(), _i)

def hmcol(*names):
    for name in names:
        if name in hm:
            return hm[name]
    raise KeyError("全员名册缺少列: %s" % "/".join(names))

C_NAME    = hmcol("姓名")
C_COMPANY = hmcol("合同所属公司", "所属分公司")
C_ID      = hmcol("工号")
C_D1      = hmcol("一级部门")
C_D2      = hmcol("二级部门")
C_JOB     = hmcol("职位")
C_GENDER  = hmcol("性别")
C_STATUS  = hmcol("员工状态")
C_CAT     = hmcol("员工类别")
C_HIRE    = hmcol("入职时间", "入职日期")
C_PROB    = hmcol("转正日期")
C_CON     = hmcol("劳动合同到期日", "劳动合同签订日期")
C_LEAVE   = hmcol("离职日期")
C_TEN     = hmcol("司龄")
C_OFFICE  = hmcol("办公点", "办公地")
C_BIRTH   = hmcol("出生日期")
C_AGE     = hmcol("年龄")
C_WY      = hmcol("工龄")
C_EDU     = hmcol("学历")
C_SCHOOL  = hmcol("毕业院校")
C_MAJOR   = hmcol("所学专业")
C_LEVEL   = hmcol("职级")
C_JCLASS  = hmcol("按职业分类")
C_LTYPE   = hmcol("离职类型")
C_LREASON = hmcol("离职原因")
C_ETYPE   = hmcol("入职类型")

def excel_date(v):
    """把单元格值规范为 YYYY-MM-DD；Excel 序列号自动转换。"""
    if not v:
        return ""
    s = str(v).strip()
    if s in ("0", "-"):
        return ""
    import re as _re
    if _re.fullmatch(r"\d{5}(\.\d+)?", s):  # Excel 日期序列号
        try:
            return (_dt.date(1899, 12, 30) + _dt.timedelta(days=int(float(s)))).isoformat()
        except Exception:
            return s[:10]
    return s[:10]

def _num(v):
    try:
        return float(str(v).strip())
    except Exception:
        return None

PEOPLE = []
seen = Counter()
for r in hmc[1:]:
    def g(idx):
        return r[idx].strip() if len(r) > idx and r[idx] else ""
    if not g(C_NAME):
        continue
    seen[g(C_NAME)] += 1
    PEOPLE.append({
        "id": g(C_ID), "name": g(C_NAME), "company": g(C_COMPANY), "dept1": g(C_D1), "dept2": g(C_D2), "job": g(C_JOB),
        "gender": g(C_GENDER), "status": g(C_STATUS), "category": g(C_CAT),
        "hire": excel_date(g(C_HIRE)), "probation": excel_date(g(C_PROB)), "contract": excel_date(g(C_CON)),
        "leave_date": excel_date(g(C_LEAVE)), "tenure": g(C_TEN), "office": g(C_OFFICE),
        "birth": g(C_BIRTH)[:10], "age": g(C_AGE), "work_years": g(C_WY),
        "edu": g(C_EDU), "school": g(C_SCHOOL), "major": g(C_MAJOR), "level": g(C_LEVEL),
        "job_class": g(C_JCLASS), "leave_type": g(C_LTYPE), "leave_reason": g(C_LREASON), "entry_type": g(C_ETYPE),
    })
print("名册人数:", len(PEOPLE), "| 同名:", {k: v for k, v in seen.items() if v > 1})

# 在职口径：含待离职（仍在职）
active = [p for p in PEOPLE if p["status"] in ("在职", "待离职")]
pending = [p for p in PEOPLE if p["status"] == "待离职"]
left = [p for p in PEOPLE if p["status"] == "离职"]
print("在职(含待离职):", len(active), "待离职:", len(pending), "离职:", len(left))

# ---------- 总表：按表头名称定位列，年度离职块 + 月度趋势 ----------
zb_header = zb[0]
def hcol(*names):
    for name in names:
        for i, h in enumerate(zb_header):
            if h and h.strip() == name:
                return i
    return None

annual = None
trend = []
i_start, i_hire, i_leave = hcol("年初在职"), hcol("当年入职"), hcol("当年离职")
i_vol, i_invol, i_cur = hcol("年主动离职人数"), hcol("年被动离职人数"), hcol("当前在职")
i_prob, i_prob_vol, i_prob_invol = hcol("试用期离职总人数"), hcol("试用期主动离职"), hcol("试用期被动离职")
i_avg = hcol("年平均人数")
i_m, i_ms, i_mh, i_ml = hcol("月份"), hcol("月初在职"), hcol("当月入职"), hcol("当月离职")
i_mv, i_mi = hcol("当月主动离职"), hcol("当月被动离职")

for r in zb[1:]:
    if i_start is not None and r[i_start] and annual is None:
        annual = {"start": r[i_start].strip(), "hire": r[i_hire].strip(), "leave": r[i_leave].strip(),
                  "vol": r[i_vol].strip(), "invol": r[i_invol].strip(), "current": r[i_cur].strip(),
                  "prob": r[i_prob].strip(), "prob_vol": r[i_prob_vol].strip(), "prob_invol": r[i_prob_invol].strip(),
                  "avg_hc": r[i_avg].strip()}
    if i_m is not None and r[i_m] and r[i_ms] != "":
        s = float(r[i_ms]); h = float(r[i_mh] or 0); l = float(r[i_ml] or 0)
        trend.append({"m": r[i_m][:7], "start": s, "hire": h, "leave": l,
                      "vol": float(r[i_mv] or 0), "invol": float(r[i_mi] or 0),
                      "end": s + h - l})
print("年度块:", annual)
print("月度趋势:", [(t["m"], t["start"], t["hire"], t["leave"], t["end"]) for t in trend])

avg_hc = float(annual["avg_hc"]) if annual and annual["avg_hc"] else 96.14
leave_n = int(float(annual["leave"])); vol_n = int(float(annual["vol"])); invol_n = int(float(annual["invol"]))
prob_n = int(float(annual["prob"])); prob_vol = int(float(annual["prob_vol"])); prob_invol = int(float(annual["prob_invol"]))

# ---------- 指标 ----------
def cnt(items, key):
    return dict(Counter(p[key] for p in items if p.get(key)))

dept1_active = cnt(active, "dept1")
dept2_active = cnt(active, "dept2")
company_active = cnt(active, "company")
gender = cnt(active, "gender")
office = cnt(active, "office")
edu = cnt(active, "edu")
level = cnt(active, "level")
jobclass = cnt(active, "job_class")

ages = [v for v in (_num(p["age"]) for p in active if p.get("age")) if v is not None and 15 <= v <= 70]
tens = [v for v in (_num(p["tenure"]) for p in active if p.get("tenure") != "") if v is not None and 0 <= v <= 60]

def buckets(vals, edges, labels):
    out = {L: 0 for L in labels}
    for v in vals:
        for i, e in enumerate(edges):
            if v < e:
                out[labels[i]] += 1; break
        else:
            out[labels[-1]] += 1
    return out

age_b = buckets(ages, [25, 30, 35, 40, 200], ["21-25岁", "26-30岁", "31-35岁", "36-40岁", "41岁+"])
ten_b = buckets(tens, [1, 2, 3, 5, 200], ["<1年", "1-2年", "2-3年", "3-5年", "5年+"])

lv_order = ["M2", "M1", "P5", "P4", "P3", "P2", "P1"]
levels = {k: level.get(k, 0) for k in lv_order}
mgmt = levels["M2"] + levels["M1"]; prof = sum(levels[k] for k in ["P5","P4","P3","P2","P1"])

cross = {}
for p in active:
    if p["level"]:
        cross.setdefault(p["dept1"], {}).setdefault(p["level"], 0)
        cross[p["dept1"]][p["level"]] += 1
cross_out = sorted(cross.items(), key=lambda x: -sum(x[1].values()))

dept_age = {}
for p in active:
    if p.get("age"):
        _a = _num(p["age"])
        if _a is not None and 15 <= _a <= 70:
            dept_age.setdefault(p["dept1"], []).append(_a)
dept_avg_age = {k: round(sum(v)/len(v), 1) for k, v in dept_age.items()}

left_dept = cnt(left, "dept1")
left_type = cnt(left, "leave_type")
left_reason = Counter(p["leave_reason"] for p in left if p["leave_reason"]).most_common(10)

# ---------- 招聘职位登记表（表头在第2行，按列名定位，避免列变动错位） ----------
jobs_rows = d.get("招聘职位登记表", {}).get("rows", [])
job_items = []
jh = {}
j_header_i = None
for hi in range(min(3, len(jobs_rows))):
    cand = jobs_rows[hi] or []
    if any(h and str(h).strip() == "编号" for h in cand) and any(h and str(h).strip() == "招聘状态" for h in cand):
        j_header_i = hi
        for i, h in enumerate(cand):
            if h and str(h).strip():
                jh.setdefault(str(h).strip(), i)
        break
def jcol(r, name):
    i = jh.get(name)
    return (r[i].strip() if i is not None and len(r) > i and r[i] else "")
if j_header_i is not None:
    for r in jobs_rows[j_header_i + 1:]:
        if not r or not jcol(r, "编号"):
            continue
        job_items.append({
            "id": jcol(r, "编号"), "dept": jcol(r, "部门"), "job": jcol(r, "职位"),
            "salary": jcol(r, "薪资区间"), "headcount": jcol(r, "人数"), "urgency": jcol(r, "紧急程度"),
            "start_date": jcol(r, "发起日期")[:10],
            "plan_date": jcol(r, "计划入职日期")[:10],
            "close_date": jcol(r, "关闭日期")[:10],
            "arrive_date": jcol(r, "到岗时间")[:10],
            "cycle": jcol(r, "招聘周期"),
            "candidate": jcol(r, "人选姓名"),
            "owner": jcol(r, "主负责人"),
            "status": jcol(r, "招聘状态"),
            "remark": jcol(r, "备注"),
        })
recruiting = [j for j in job_items if j["status"] == "进行中"]
jobs_summary = {
    "all_count": len(job_items),
    "items": sorted(job_items, key=lambda j: (j["status"] != "进行中", j["id"])),
    "recruiting": recruiting,
    "recruiting_count": len(recruiting),
    "urgent_count": sum(1 for j in recruiting if j["urgency"] in ("加急", "紧急")),
    "recruiting_by_dept": dict(Counter(j["dept"] for j in recruiting if j["dept"])),
}

# ---------- 近期待办（未办理 / 未到来口径） ----------
_today = _dt.date.today()
_asof = _today.strftime("%Y-%m-%d")
_LIMIT = (_today + _dt.timedelta(days=45)).strftime("%Y-%m-%d")

# 待入职：录用登记中 录用状态=待入职（已入职/已放弃自动排除）
hire_rows = d.get("录用登记", {}).get("rows", [])
tasks_onboarding = []
if hire_rows:
    hh = hire_rows[0]
    hi_dept = hh.index("部门") if "部门" in hh else 1
    hi_job  = hh.index("岗位") if "岗位" in hh else 2
    hi_name = hh.index("人员") if "人员" in hh else 3
    hi_st   = hh.index("录用状态") if "录用状态" in hh else 6
    hi_dt   = hh.index("入职时间") if "入职时间" in hh else 8
    for r in hire_rows[1:]:
        st = (r[hi_st] or "").strip() if len(r) > hi_st else ""
        dt = (r[hi_dt] or "").strip()[:10] if len(r) > hi_dt else ""
        if st == "待入职":
            tasks_onboarding.append({"name": (r[hi_name] or "").strip(), "dept": (r[hi_dept] or "").strip(),
                                     "job": (r[hi_job] or "").strip(), "date": dt or "待定"})

# 转正：员工类别仍为「试用」且有转正日期（已转正式自动排除）
tasks_regular = [{"id": p["id"], "name": p["name"], "dept": p["dept1"], "job": p["job"], "date": p["probation"]}
                 for p in active if p["category"] == "试用" and p["probation"]]
# 待离职：仅状态=待离职（已离职的不展示）
tasks_leaving = [{"id": p["id"], "name": p["name"], "dept": p["dept1"], "job": p["job"],
                  "date": p["leave_date"] or "待定"}
                 for p in active if p["status"] == "待离职"]
# 劳动合同到期：到期日未更新为远期（≤今天+45天，含已逾期未续签）
tasks_contract = [{"id": p["id"], "name": p["name"], "dept": p["dept1"], "job": p["job"], "date": p["contract"]}
                  for p in active if p["contract"] and p["contract"] <= _LIMIT]
tasks = {
    "asof": _asof,
    "limit": _LIMIT,
    "onboarding": sorted(tasks_onboarding, key=lambda x: x["date"]),
    "regularization": sorted(tasks_regular, key=lambda x: x["date"]),
    "leaving": sorted(tasks_leaving, key=lambda x: x["date"]),
    "contract": sorted(tasks_contract, key=lambda x: x["date"]),
}
print("近期待办: 待入职%d 转正%d 待离职%d 合同到期%d" % (len(tasks["onboarding"]), len(tasks["regularization"]), len(tasks["leaving"]), len(tasks["contract"])))

# 明细表排序：在职(含待离职)组在前、离职组在后；组内按入职日期从早到晚（升序）
_rows_sorted = sorted(PEOPLE, key=lambda p: p["hire"] or "")
_rows_sorted = sorted(_rows_sorted, key=lambda p: 0 if p["status"] in ("在职", "待离职") else 1)
result = {
    "snapshot": _dt.date.today().strftime("%Y-%m-%d"),
    "source": "金山文档《均冠花名册》在线文档（webhook 实时取数）",
    "total_active": len(active), "total_pending": len(pending), "total_register": len(PEOPLE),
    "dept1_count": len(dept1_active),
    "avg_age": round(sum(ages)/len(ages), 1), "avg_tenure": round(sum(tens)/len(tens), 1),
    "cover": {"age": len(ages), "tenure": len(tens), "level": sum(level.values())},
    "gender": gender, "office": office, "edu": edu,
    "levels": levels, "mgmt": mgmt, "prof": prof,
    "jobclass": jobclass,
    "age_buckets": age_b, "tenure_buckets": ten_b,
    "dept1": dept1_active, "dept2": dept2_active, "company": company_active,
    "dept_level": cross_out, "dept_avg_age": dept_avg_age,
    "trend": trend,
    "attrition_ytd": {"start": int(float(annual["start"])), "current": int(float(annual["current"] or 0)), "hire": int(float(annual["hire"])), "leave": leave_n,
        "vol": vol_n, "invol": invol_n, "prob": prob_n, "prob_vol": prob_vol, "prob_invol": prob_invol,
        "avg_hc": round(avg_hc, 1),
        "vol_rate": round(vol_n / avg_hc * 100, 1), "invol_rate": round(invol_n / avg_hc * 100, 1),
        "total_rate": round(leave_n / avg_hc * 100, 1)},
    "attrition_hist": {"dept": left_dept, "type": left_type, "reason": left_reason,
        "count": len(left), "monthly_leave": [(t["m"], int(t["leave"])) for t in trend if t["leave"] > 0]},
    "jobs": jobs_summary,
    "tasks": tasks,
    "rows": _rows_sorted,
}
io.open(r'dashboard_data_v2.json', 'w', encoding='utf-8').write(
    json.dumps(result, ensure_ascii=False, indent=1))
print("DONE")
