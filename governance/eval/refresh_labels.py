#!/usr/bin/env python3
"""標註刷新工具(治理面;spec:Projects/標註刷新_計劃 r1 收斂版)。零依賴 stdlib。

子命令:
  delta   對目標語料算評測母體、diff labels → 未標清單+delta 標註表(觀測,恆 rc0;輸入壞 rc2)
  repin   評測母體 unjudged==0 才寫 snapshot_commit(rc0=已重釘/rc1=有未標硬擋/rc2=輸入壞)
  merge   雙評審輸出合併:一致(同值)→agreed;不一致→disputed;B 席缺→degraded 全 disputed
  apply   人放行動作:把 merge(+人裁 adjudication)寫進 goldset labels(atomic;唯一寫 labels 入口)
  signal  讀 history 最後一筆考卷的 unjudged_rate,advisory 輸出(週閘薄接線消費)

母體/未標判定=retrieval_eval.collect_unjudged 單一實作(S0 同源紀律,禁另寫)。
"""
import argparse
import datetime
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load_re():
    spec = importlib.util.spec_from_file_location("retrieval_eval", HERE / "retrieval_eval.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _read_goldset(path):
    try:
        gs = json.loads(Path(path).read_text(encoding="utf-8"))
        gs["labels"]; gs["search"]; gs["edit"]
        return gs
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"ERROR: goldset 讀取/結構失敗: {e}", file=sys.stderr)
        return None


def _atomic_write_json(path, obj):
    """tmp+os.replace;goldset 寫入紀律(spec S2)。"""
    p = Path(path)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)


def _setup(re_mod, repo, snapshot=None):
    """把 retrieval_eval 指向目標 repo/語料;--snapshot 走 worktree 釘定。"""
    root = Path(repo).resolve()
    re_mod.ROOT = root
    vault = next((root / "docs").glob("*-knowledge"), None)
    if vault is None:
        print(f"ERROR: {root} 下找不到 docs/*-knowledge", file=sys.stderr)
        return False
    re_mod.VAULT = vault
    if snapshot:
        if not re_mod.pin_snapshot(snapshot):
            return False
    return True


def _orphans(re_mod, gs):
    """labels 有鍵、目標語料查無節點檔(rename/刪除產物)→ 人工遷移清單。"""
    out = []
    base = re_mod.SNAP_ROOT or re_mod.ROOT
    vault = next((Path(base) / "docs").glob("*-knowledge"), re_mod.VAULT)
    for cid, nodes in gs["labels"].items():
        for n in nodes:
            if not (vault / n).exists():
                out.append(f"{cid}:{n}")
    return out


def cmd_delta(args):
    gs = _read_goldset(args.goldset)
    if gs is None:
        return 2
    re_mod = _load_re()
    if not _setup(re_mod, args.repo, args.snapshot):
        return 2
    u = re_mod.collect_unjudged(gs, args.split)
    orphans = _orphans(re_mod, gs)
    target = args.snapshot or "worktree"
    cases = [{"id": cid, "unjudged": nodes} for cid, nodes in sorted(u["per_case"].items())]
    result = {"target": target, "cases": cases, "skipped": u["skipped"], "orphans": orphans,
              "count": u["count"], "denom": u["denom"], "rate": round(u["rate"], 4)}
    out = args.out or str(HERE / "retrieval-delta")
    sheet = ["# 檢索評測 delta 標註表(增量補標)",
             "",
             "> ★本卷為 delta 片段,案例不連號屬正常★——只列未標候選,已判金標不重出。",
             "**怎麼標**:每個候選節點後面填 `2`(必看)或 `1`(有用);留白 = 0(噪音)。",
             ""]
    qmap = {c["id"]: c for c in gs["search"]}
    fmap = {c["id"]: c for c in gs["edit"]}
    for c in cases:
        cid = c["id"]
        head = (f"搜尋:「{qmap[cid]['query']}」" if cid in qmap
                else f"編輯:`{fmap[cid]['file']}`")
        sheet.append(f"## {cid}｜{head}")
        for n in c["unjudged"]:
            sheet.append(f"- [ ] {n} ｜標:____")
        sheet.append("")
    Path(out + "-sheet.md").write_text("\n".join(sheet), encoding="utf-8")
    Path(out + ".json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"delta: 未標 {u['count']}/{u['denom']}(rate={result['rate']});"
              f"skipped {len(u['skipped'])};orphans {len(orphans)} → {out}-sheet.md")
    return 0






def cmd_repin(args):
    gs = _read_goldset(args.goldset)
    if gs is None:
        return 2
    re_mod = _load_re()
    root = Path(args.repo).resolve()
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    target = args.target or head
    if not target:
        print("ERROR: 取不到 repo HEAD 且未給 --target", file=sys.stderr)
        return 2
    # 斷言對象=要釘的那個語料:target≠HEAD 才需 worktree 釘定,否則直接用工作樹
    snap = target if (head and target != head) else None
    if not _setup(re_mod, args.repo, snap):
        return 2
    u = re_mod.collect_unjudged(gs, args.split)
    if u["count"] > 0:
        print(f"⛔ repin 擋下:評測母體尚有 {u['count']} 筆未標(先跑 delta→補標→apply):", file=sys.stderr)
        for cid, nodes in sorted(u["per_case"].items()):
            for n in nodes:
                print(f"  {cid}: {n}", file=sys.stderr)
        return 1
    gs["snapshot_commit"] = target
    _atomic_write_json(args.goldset, gs)
    print(f"✓ repin: snapshot_commit → {target}(未標 0/{u['denom']};labels 未動)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("delta", help="未標清單+delta 標註表(觀測)")
    d.add_argument("--goldset", default=str(HERE / "retrieval-goldset.json"))
    d.add_argument("--repo", default=str(HERE.parents[1]))
    d.add_argument("--snapshot", help="對歷史 commit 語料算(worktree 釘定)")
    d.add_argument("--split", choices=["train", "held"])
    d.add_argument("--json", action="store_true")
    d.add_argument("--out", help="輸出前綴(產 <out>-sheet.md 與 <out>.json)")

    r = sub.add_parser("repin", help="unjudged==0 才寫 snapshot_commit(rc0/1/2)")
    r.add_argument("--goldset", default=str(HERE / "retrieval-goldset.json"))
    r.add_argument("--repo", default=str(HERE.parents[1]))
    r.add_argument("--target", help="要釘的 sha(預設=repo HEAD short;≠HEAD 走 worktree 釘定)")
    r.add_argument("--split", choices=["train", "held"])

    args = ap.parse_args()
    return {"delta": cmd_delta, "repin": cmd_repin}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
