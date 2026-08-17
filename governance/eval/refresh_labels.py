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
    """tmp(pid 後綴)+os.replace;goldset 寫入紀律(spec S2)。
    ★單次寫入原子性;跨進程互斥另靠 _goldset_lock(code-r1 資源席:固定 tmp 名+無鎖
    曾實測出「一方標註靜默消失+另一方假成功」)★"""
    p = Path(path)
    tmp = p.with_suffix(p.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)


class _goldset_lock:
    """goldset 寫入互斥鎖(flock 非阻塞):apply/repin 讀改寫全程持有。
    搶不到=另一寫入進行中 → 快速失敗,呼叫端 rc 非零、goldset 不動。"""
    def __init__(self, goldset_path):
        self.path = str(goldset_path) + ".lock"
        self.fh = None
    def __enter__(self):
        import fcntl
        self.fh = open(self.path, "w")
        try:
            fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.fh.close()
            self.fh = None
            raise BlockingIOError("goldset 寫入鎖被占用")
        return self
    def __exit__(self, *a):
        import fcntl
        if self.fh:
            fcntl.flock(self.fh, fcntl.LOCK_UN)
            self.fh.close()
        return False


def _setup(re_mod, repo, snapshot=None):
    """把 retrieval_eval 指向目標 repo/語料;--snapshot 走 worktree 釘定。
    釘定失敗=硬性失敗(呼叫端 rc2),不退回現況——與 retrieval_eval main() 的 fallback 語意不同。"""
    root = Path(repo).resolve()
    re_mod.ROOT = root
    vault = next((root / "docs").glob("*-knowledge"), None)
    if vault is None:
        print(f"ERROR: {root} 下找不到 docs/*-knowledge", file=sys.stderr)
        return False
    re_mod.VAULT = vault
    # ★LUMOS 在 import 當下用「refresh_labels 所在 repo」算死——跨庫 --repo 必須跟著換,
    # 否則用錯版本的 lumos 算池且零錯誤訊息(code-r1 整合席 F1,逐字重現)★
    target_lumos = root / "scripts" / "lumos"
    if target_lumos.exists():
        re_mod.LUMOS = target_lumos
    elif root != Path(__file__).resolve().parents[2]:
        print(f"⚠ {root} 無 scripts/lumos,沿用本體版本(跨庫版本可能不同步)", file=sys.stderr)
    if snapshot:
        if not re_mod.pin_snapshot(snapshot):
            print("ERROR: 快照釘定失敗——本工具不退回現況(硬性失敗)", file=sys.stderr)
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
    # delta 表為觀測性產物(可重跑重算,非權威金標)——裸寫可接受,毋須 atomic(code-r1 f12 裁定)
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
    # ★head 解析失敗=硬擋★(code-r1 bug 席 F3:非 git repo 時原判斷短路,
    # 捏造 target 可被原樣寫入 snapshot_commit 而零驗證)
    if not head:
        print(f"ERROR: {root} 不是 git repo 或 HEAD 解析失敗——repin 需要可驗證的語料版本", file=sys.stderr)
        return 2
    target = args.target or head
    # target 必須是真 commit(存在性驗證,不靠後續 worktree 碰運氣)
    v = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "--quiet",
                        f"{target}^{{commit}}"], capture_output=True, text=True)
    if v.returncode != 0:
        print(f"ERROR: --target {target} 不是本 repo 可解析的 commit", file=sys.stderr)
        return 2
    # 斷言對象=要釘的那個語料:target≠HEAD 才需 worktree 釘定,否則直接用工作樹
    snap = target if target != head else None
    if not _setup(re_mod, args.repo, snap):
        return 2
    u = re_mod.collect_unjudged(gs, args.split)
    if u["count"] > 0:
        print(f"⛔ repin 擋下:評測母體尚有 {u['count']} 筆未標(先跑 delta→補標→apply):", file=sys.stderr)
        for cid, nodes in sorted(u["per_case"].items()):
            for n in nodes:
                print(f"  {cid}: {n}", file=sys.stderr)
        return 1
    try:
        with _goldset_lock(args.goldset):
            # 鎖內重讀再寫:母體計算期間若有併發 apply 寫入新標註,不得被本次整檔覆蓋回舊版
            gs2 = _read_goldset(args.goldset)
            if gs2 is None:
                return 2
            gs2["snapshot_commit"] = target
            _atomic_write_json(args.goldset, gs2)
    except BlockingIOError:
        print("⛔ goldset 寫入鎖被占用(另一個 apply/repin 進行中),稍後再試;本次未寫入。", file=sys.stderr)
        return 1
    print(f"✓ repin: snapshot_commit → {target}(未標 0/{u['denom']};labels 未動)")
    return 0


def cmd_merge(args):
    def _load_rater(path):
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
    a = _load_rater(args.a)
    if a is None:
        print(f"ERROR: A 席檔讀取失敗: {args.a}", file=sys.stderr)
        return 2
    b = _load_rater(args.b) if args.b else None
    degraded = b is None
    agreed, disputed = {}, {}
    for cid, nodes in a.items():
        for n, av in nodes.items():
            bv = (b or {}).get(cid, {}).get(n)
            if degraded or bv is None or int(av) != int(bv):
                # 一致=同值(1 vs 2=不一致);degraded=B 席缺→全人裁(單席值放 a)
                disputed.setdefault(cid, {})[n] = {"a": int(av),
                                                   "b": None if (degraded or bv is None) else int(bv)}
            else:
                agreed.setdefault(cid, {})[n] = int(av)
    result = {"agreed": agreed, "disputed": disputed, "degraded": degraded}
    if degraded:
        print("⚠ degraded:single-rater——B 席輸出缺/壞,全部進人裁桶", file=sys.stderr)
    if args.out:
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        # 人讀 diff 預覽(spec S2 放行介面:逐筆 node/建議 final/兩席原值——防盲簽,code-r1 spec 席縮水修回)
        for cid in sorted(set(agreed) | set(disputed)):
            for n, val in sorted(agreed.get(cid, {}).items()):
                print(f"  一致  {cid} {n} → 建議 final={val}(A={val} B={val})")
            for n, v in sorted(disputed.get(cid, {}).items()):
                print(f"  人裁  {cid} {n} A={v['a']} B={v['b']} → 待 adjudication")
    n_a = sum(len(v) for v in agreed.values())
    n_d = sum(len(v) for v in disputed.values())
    print(f"merge: 一致 {n_a} / 人裁 {n_d}{'(degraded)' if degraded else ''}", file=sys.stderr)
    return 0


def cmd_apply(args):
    # ★鎖覆蓋整段讀改寫★(code-r1 資源席 F1:兩個 apply 併發=一方標註靜默消失+假成功)
    try:
        lock = _goldset_lock(args.goldset)
        lock.__enter__()
    except BlockingIOError:
        print("⛔ goldset 寫入鎖被占用(另一個 apply/repin 進行中),稍後再試;本次未寫入。", file=sys.stderr)
        return 1
    try:
        return _apply_locked(args)
    finally:
        lock.__exit__(None, None, None)


def _apply_locked(args):
    gs = _read_goldset(args.goldset)
    if gs is None:
        return 2
    try:
        m = json.loads(Path(args.merge).read_text(encoding="utf-8"))
        m["agreed"]; m["disputed"]
    except (OSError, ValueError, KeyError) as e:
        print(f"ERROR: merge 檔讀取失敗: {e}", file=sys.stderr)
        return 2
    adj = {}
    if args.adjudication:
        try:
            adj = json.loads(Path(args.adjudication).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"ERROR: adjudication 檔讀取失敗: {e}", file=sys.stderr)
            return 2
    missing = [f"{cid}:{n}" for cid, nodes in m["disputed"].items()
               for n in nodes if adj.get(cid, {}).get(n, {}).get("final") is None]
    if missing:
        print(f"⛔ apply 擋下:{len(missing)} 筆人裁缺 final(補進 adjudication 檔再跑):", file=sys.stderr)
        for x in missing:
            print(f"  {x}", file=sys.stderr)
        return 1
    today = datetime.date.today().isoformat()
    n_new = 0
    for cid, nodes in m["agreed"].items():
        for n, val in nodes.items():
            gs["labels"].setdefault(cid, {})[n] = {
                "final": int(val), "claude": int(val), "gemini": int(val), "labeled_at": today}
            n_new += 1
    for cid, nodes in m["disputed"].items():
        for n, votes in nodes.items():
            a = adj[cid][n]
            entry = {"final": int(a["final"]), "claude": votes.get("a"),
                     "gemini": votes.get("b"), "labeled_at": today,
                     "by": a.get("by", "deep-read")}
            if a.get("why"):
                entry["why"] = a["why"]
            gs["labels"].setdefault(cid, {})[n] = entry
            n_new += 1
    _atomic_write_json(args.goldset, gs)
    note = f";note={args.note}" if args.note else ""
    print(f"✓ apply: 寫入 {n_new} 筆(人放行動作即本指令{note})")
    return 0


def cmd_signal(args):
    """advisory:讀 history 最後一筆考卷輪(mode∈{goldset,goldset-transition})的 unjudged 欄。
    輸出單行 `unjudged_rate=<x> count=<n> over=<yes|no>`;無欄=NA;恆 rc0(檔缺=rc2)。
    週閘 bash 只 grep over=yes,邏輯全在此受測(spec T7 薄接線)。"""
    try:
        lines = Path(args.history).read_text(encoding="utf-8").splitlines()
    except OSError as e:
        print(f"ERROR: history 讀取失敗: {e}", file=sys.stderr)
        return 2
    last = None
    for ln in lines:
        try:
            d = json.loads(ln)
        except ValueError:
            continue
        if d.get("mode") in ("goldset", "goldset-transition"):
            last = d
    rate = (last or {}).get("unjudged_rate")
    count = (last or {}).get("unjudged_count")
    if rate is None:
        print("unjudged_rate=NA count=NA over=no")
        return 0
    over = "yes" if rate >= args.threshold else "no"
    print(f"unjudged_rate={rate} count={count} over={over}")
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

    mg = sub.add_parser("merge", help="雙評審合併(一致=同值;B 缺=degraded)")
    mg.add_argument("--a", required=True, help="A 席 rater json({cid:{node:0|1|2}})")
    mg.add_argument("--b", help="B 席 rater json;缺=degraded 全人裁")
    mg.add_argument("--json", action="store_true")
    mg.add_argument("--out", help="merge 結果輸出檔")

    apl = sub.add_parser("apply", help="人放行:merge(+adjudication)寫進 goldset labels")
    apl.add_argument("--merge", required=True)
    apl.add_argument("--goldset", default=str(HERE / "retrieval-goldset.json"))
    apl.add_argument("--adjudication", help="人裁檔({cid:{node:{final,by,why}}})")
    apl.add_argument("--note", help="放行留言(印進輸出)")

    sg = sub.add_parser("signal", help="讀 history 尾筆 unjudged_rate(advisory)")
    sg.add_argument("--history", default=str(HERE / "retrieval-eval-history.jsonl"))
    sg.add_argument("--threshold", type=float, default=0.10)

    args = ap.parse_args()
    return {"delta": cmd_delta, "repin": cmd_repin,
            "merge": cmd_merge, "apply": cmd_apply, "signal": cmd_signal}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
