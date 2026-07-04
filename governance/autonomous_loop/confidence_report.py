import json
from pathlib import Path

def build_report(canary_log, loop_id, residual_risks, tier=None, hits=None, reported_tier=None):
    rows = []
    p = Path(canary_log)
    if p.exists():
        for l in p.read_text(encoding="utf-8").splitlines():
            if not l.strip(): continue
            r = json.loads(l)
            if r.get("loop") == loop_id: rows.append(r)
    lines = [f"## 收斂可信度報告(loop={loop_id})", ""]
    if tier:
        mismatch = (f"(⚠ result JSON 自報 `{reported_tier}` ≠ 自算——紅標,查參數謊報)"
                    if reported_tier not in (None, "", tier) else "")
        lines.append(f"**風險級 tier=`{tier}`(wrapper 對最終 spec 自算)**{mismatch}")
        for h in (hits or []):
            lines.append(f"- hit `{h.get('class')}`:…{h.get('excerpt', '')}…")
        lines.append("")
    lines += [f"**共 {len(rows)} 輪:**", ""]
    for i, r in enumerate(rows, 1):
        lines.append(f"- R{i}: `{r.get('kind')}` / severity=`{r.get('severity')}` / "
                     f"auditor=`{r.get('auditor','?')}` — {r.get('note','')}")
    lines += ["", "### ⚠ 這個迴圈沒檢查到的維度(品質最可能爛在這、放行請特別盯)", ""]
    lines += [f"- {risk}" for risk in residual_risks]
    lines += ["", "> 放行的人是最後也是唯一真兜底。上列是這個迴圈**結構上沒能自動檢查**的維度——不是它查過沒問題,是它根本沒查;請你的眼睛盯這幾處。"]
    return "\n".join(lines)
