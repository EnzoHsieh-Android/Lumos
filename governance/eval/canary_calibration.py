#!/usr/bin/env python3
"""[T7 design-loop重設計] canary 離線校準:凍結語料+植入清單 × 各配置審查報告 → caught 矩陣。

★fault seeding 的文獻本職★:量「哪種模型×prompt 配置抓得到哪型植入缺陷」,結果用來選配置
(如密集 spec 直接上 opus)——★不進任何單輪 gate★(d4:逐輪 canary 是觀測,校準在這裡離線做)。

跑法:
  python3 governance/eval/canary_calibration.py --plants plants.json --reports <dir> [--config <名>]

plants.json 格式: [{"id":"P1","file":"f1.md","type":"b","token":"--strict-phrase",
                    "nature":"未定義旗標"}, ...]
reports 目錄: 每席一個 .md(檔名=席名);判定=報告文字(正規化後)含該植入的 token(正規化後)
              ★且★點名其性質類詞(nature 逐字或 token 前後 80 字內出現「未定義/不存在/沒有定義」)。
判定沿 quote-check 的正規化精神(NFC+剝記號+空白摺疊)——★單一份實作,從 scripts/lumos import★。
輸出: 人讀矩陣 + 追加一行 JSONL 到 governance/eval/calibration-log.jsonl(累積帳)。
★誠實邊界★:token 子字串判定是寬判(提到≠正確指出),嚴判(caught 語意)仍需人抽驗;
本工具產的是★校準訊號★不是裁決。
"""
import argparse
import datetime
import importlib.machinery
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
_loader = importlib.machinery.SourceFileLoader("lumos_cli", str(ROOT / "scripts" / "lumos"))
_spec = importlib.util.spec_from_loader("lumos_cli", _loader)
_m = importlib.util.module_from_spec(_spec)
_loader.exec_module(_m)
_norm = _m._quote_norm   # ★單一實作:不複製正規化(2026-08-02 兩份實作漂移教訓)★

HINTS = ("未定義", "不存在", "沒有定義", "找不到", "查無", "undefined")


def judge(report_text, plant):
    t = _norm(report_text)
    tok = _norm(plant["token"])
    if tok not in t:
        return "missed"
    i = t.find(tok)
    window = t[max(0, i - 80): i + len(tok) + 80]
    nat = _norm(plant.get("nature", ""))
    if (nat and nat in t) or any(h in window for h in HINTS):
        return "caught"
    return "mentioned"   # 提到 token 但沒點性質——寬嚴之間,單獨列


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plants", required=True)
    ap.add_argument("--reports", required=True)
    ap.add_argument("--config", default="unnamed", help="這批報告的配置名(模型×prompt)")
    ap.add_argument("--no-log", action="store_true", help="不寫累積帳(試跑)")
    a = ap.parse_args()
    plants = json.loads(pathlib.Path(a.plants).read_text(encoding="utf-8"))
    rdir = pathlib.Path(a.reports)
    reports = sorted(rdir.glob("*.md"))
    if not plants or not reports:
        print("ERROR: 植入清單或報告目錄為空(驗不了≠通過)", file=sys.stderr)
        return 2
    rows = []
    print(f"=== canary 校準:config={a.config}  植入 {len(plants)} × 席 {len(reports)} ===")
    for rp in reports:
        text = rp.read_text(encoding="utf-8")
        verdicts = {p["id"]: judge(text, p) for p in plants}
        c = sum(1 for v in verdicts.values() if v == "caught")
        m = sum(1 for v in verdicts.values() if v == "mentioned")
        rows.append({"seat": rp.stem, "verdicts": verdicts, "caught": c, "mentioned": m})
        print(f"  {rp.stem:24} caught {c}/{len(plants)}  (另 mentioned {m})  "
              + " ".join(f"{k}:{{'caught': '✓', 'mentioned': '~', 'missed': '✗'}}[v]".format() if False else f"{k}:{ {'caught':'✓','mentioned':'~','missed':'✗'}[v] }" for k, v in verdicts.items()))
    total = sum(r["caught"] for r in rows)
    print(f"\n  合計 caught {total}/{len(plants) * len(reports)}"
          f"  ★寬判訊號,嚴判需人抽驗;不進任何 gate★")
    if not a.no_log:
        log = ROOT / "governance" / "eval" / "calibration-log.jsonl"
        entry = {"ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                 "config": a.config, "plants": len(plants), "seats": len(rows),
                 "caught_total": total, "rows": rows}
        with log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"  已記入 {log.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
