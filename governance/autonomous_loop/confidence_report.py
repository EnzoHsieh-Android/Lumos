import json
from pathlib import Path

def build_report(canary_log, loop_id, residual_risks):
    rows = []
    p = Path(canary_log)
    if p.exists():
        for l in p.read_text(encoding="utf-8").splitlines():
            if not l.strip(): continue
            r = json.loads(l)
            if r.get("loop") == loop_id: rows.append(r)
    lines = [f"## 收斂可信度報告(loop={loop_id})", "", f"**共 {len(rows)} 輪:**", ""]
    for i, r in enumerate(rows, 1):
        lines.append(f"- R{i}: `{r.get('kind')}` / severity=`{r.get('severity')}` / "
                     f"auditor=`{r.get('auditor','?')}` — {r.get('note','')}")
    lines += ["", "### 殘留風險(自動模式已知未兜底)", ""]
    lines += [f"- {risk}" for risk in residual_risks]
    lines += ["", "> 放行的人是最後也是唯一真兜底:收斂只證連 2 輪醒著的 opus 沒挑出 "
              "blocker/major,severity 判定仍自評。"]
    return "\n".join(lines)
