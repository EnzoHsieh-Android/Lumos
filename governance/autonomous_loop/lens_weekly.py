#!/usr/bin/env python3
"""推播漏網週跑(Projects/推播miss量測_計劃 S4)。

自主迴圈的週期觀測段每週叫一次(run_lens_weekly,照 run_replay 的慣例):存「上一個完整 ISO 週」的推導列。
週用本機時區算(逐字稿時間是 UTC,換成本機時區再算,跟 shell 端 `date +%G-W%V` 同一個時區)。
輸出:第一行 JSON 摘要,之後 `LOG:` 行給 shell 逐行記——模組炸掉就不會印出 JSON,shell 不蓋週戳、明天重試。
寫兩份檔:版控的 weekly/<週>.json(只有推導列)與 gitignore 的 local/<週>-queries.json(零命中查詢字串)。
用法: python3 lens_weekly.py <repo> [--week 2026-W37] [--projects …] [--codex-sessions …] [--archive-dir …] [--budget 300]
"""
from __future__ import annotations
import argparse, datetime, json, os, sys
from pathlib import Path


def last_complete_week(today: datetime.date | None = None) -> str:
    d = (today or datetime.date.today()) - datetime.timedelta(days=7)
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def _load_recount():
    import importlib.util
    from importlib.machinery import SourceFileLoader
    path = Path(__file__).resolve().parents[1] / "eval" / "lens-utilization" / "recount.py"
    loader = SourceFileLoader("lens_recount_weekly", str(path)); spec = importlib.util.spec_from_loader("lens_recount_weekly", loader)
    m = importlib.util.module_from_spec(spec); loader.exec_module(m)
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("repo")
    ap.add_argument("--week", help="ISO 週(例 2026-W37);沒給就是上一個完整週(漏跑的週用這個手動補)")
    ap.add_argument("--projects", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--codex-sessions", default=os.path.join(os.environ.get("CODEX_HOME") or os.path.expanduser("~/.codex"), "sessions"))
    ap.add_argument("--archive-dir", help="預設 <repo>/governance/eval/lens-utilization")
    ap.add_argument("--budget", type=float, default=300.0, help="總時間預算(秒;同 replay_weekly 的 BUDGET_SECONDS)")
    ap.add_argument("--impact-timeout", type=float, default=60.0)
    a = ap.parse_args()
    repo = Path(a.repo).resolve()
    week = a.week or last_complete_week()
    arc = Path(a.archive_dir) if a.archive_dir else repo / "governance" / "eval" / "lens-utilization"
    m = _load_recount()
    rep = m.run_misses(repo, a.projects, a.codex_sessions, week=week, budget=a.budget, impact_timeout=a.impact_timeout)
    weekly, local = m.write_archive(rep, week, arc)
    s = rep["summary"]
    print(json.dumps({"week": week, "rows": s["rows"], "miss_by_class": s["miss_by_class"], "zero_push_rows": s["zero_push_rows"],
                      "search_zero": s["search_zero"], "budget_hit": s["budget_hit"]}, ensure_ascii=False))
    print(f"LOG:{week} 編輯 {s['rows']} 列(零推播 {s['zero_push_rows']}、冷卻窗內沿用前一次推播 {s['cooldown_rows']}、推播清單不完整 {s['incomplete_rows']});"
          f"漏網 {s['miss_by_class']}(另有事後才有 {s['after_the_fact']});搜尋 {s['searches']} 次、零命中 {s['search_zero']}、判不出 {s['search_undetermined']}")
    print(f"LOG:逐字稿壞行 {s['bad_lines']} 行(只跳那一行)、Codex 版本不認得跳過 {s['codex_version_skipped']} 份、"
          f"缺時間的編輯 {s['edits_without_time']} 筆(不收)、整份讀不了 {s['broken_files']} 份")
    if s["budget_hit"] or s["impact_timeouts"]:
        print(f"LOG:總預算用完={s['budget_hit']}(沒掃到的逐字稿 {s['files_unscanned']} 份、沒問 git 的筆記 {s['git_skipped']} 篇)、"
              f"impact 逾時 {s['impact_timeouts']} 次——資料不完整,那些檔的漏網分類記判不出")
    print(f"LOG:寫到 {weekly.relative_to(arc)}(版控)與 {local.relative_to(arc)}(本機,不進版控)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
