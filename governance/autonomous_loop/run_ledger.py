"""自主迴圈的結局帳讀側(auto-loop-repair-v2 [S3]⑤/[S4])。

資料源=既有 canary 帳(docs/.canary-log.jssonl 之類)裡 loop 名 auto-* 的列;
逐筆遍歷、絕不以 loop id 當鍵——同日多筆已是現場事實(08-25 兩筆同 id 不同結局),
以 id 當鍵會讓後寫的蓋掉先寫的。舊格式列(無 outcome 欄)只計跑次與成本、結局歸
「舊格式」桶明示,不冒充算過。
"""
import json
import re
import datetime
from pathlib import Path


def _auto_rows(canary_log, today, days=7):
    """過去 days 個日曆天(含今天)內 loop 名 auto-* 的列;壞行/壞 ts 跳過。"""
    p = Path(canary_log)
    if not p.exists():
        return []
    try:
        cutoff = datetime.date.fromisoformat(today) - datetime.timedelta(days=days - 1)
    except ValueError:
        return []
    rows = []
    for l in p.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        try:
            r = json.loads(l)
        except ValueError:
            continue
        # 只收 auto-<日期> 形狀——auto-smoke / auto-loop-repair-v2(設計審 loop id)這類
        # 同字首但非每日結局帳的列要排除,否則彙總被假數字灌水(實作當天煙測就撞到)
        if not re.fullmatch(r"auto-\d{4}-\d{2}-\d{2}", str(r.get("loop", ""))):
            continue
        try:
            d = datetime.date.fromisoformat(str(r.get("ts", ""))[:10])
        except ValueError:
            continue
        if cutoff <= d <= datetime.date.fromisoformat(today):
            rows.append(r)
    return rows


def summarize_week(canary_log, today):
    rows = _auto_rows(canary_log, today)
    s = {"runs": len(rows), "usd": 0.0, "converged": 0, "pending_ready": 0,
         "pipeline_fail": 0, "legacy": 0}
    for r in rows:
        if r.get("usd") is not None:
            try:
                s["usd"] += float(r["usd"])
            except (TypeError, ValueError):
                pass
        o = r.get("outcome")
        if o is None:
            s["legacy"] += 1
        elif o == "converged":
            s["converged"] += 1
            s["pending_ready"] += 1   # converged 只在 pending 寫入成功後才記(寫側保證)
        elif str(o).startswith("pipeline_fail"):
            s["pipeline_fail"] += 1
    s["usd"] = round(s["usd"], 2)
    return s


def format_week_line(s):
    return ("過去 7 天:跑 %d 次、燒 $%.2f、收斂 %d、備好待放行 %d、管線死 %d"
            "(另 %d 筆舊格式帳,只計跑次與成本不計結局)" % (
                s["runs"], s["usd"], s["converged"], s["pending_ready"],
                s["pipeline_fail"], s["legacy"]))


def consecutive_fail_days(canary_log, today, need=2):
    """最近 need 個「有跑日」是否全是失敗日。有跑日=當日有帶 outcome 的列(舊格式日不算);
    失敗日=當日帶 outcome 的列全部 pipeline_fail。中間沒跑的日子不算斷。"""
    by_day = {}
    for r in _auto_rows(canary_log, today, days=30):
        o = r.get("outcome")
        if o is None:
            continue
        by_day.setdefault(str(r.get("ts", ""))[:10], []).append(str(o))
    run_days = sorted(by_day)[-need:]
    if len(run_days) < need:
        return False
    return all(all(o.startswith("pipeline_fail") for o in by_day[d]) for d in run_days)
