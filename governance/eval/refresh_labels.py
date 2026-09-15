#!/usr/bin/env python3
"""標註刷新工具(治理面;spec:Projects/標註刷新_計劃 r1 收斂版)。零依賴 stdlib。

子命令:
  delta   對目標語料算評測母體、diff labels → 未標清單+delta 標註表(觀測,恆 rc0;輸入壞 rc2)
          ★清單端出去之前先排序再洗牌★,不然順序就是現行排序的名次([S8] 評測尺修復)
  material 給評審讀的題目卷:★只有題目、沒有任何標註★(rc0;輸入壞 rc2)。派工詞要指這份,
          不要叫評審去開題庫檔——那個檔裡同時存著既有答案([S13],實跑逃逸過一次)
  repin   評測母體 unjudged==0 才寫 snapshot_commit(rc0=已重釘/rc1=有未標硬擋/rc2=輸入壞)
  merge   雙評審輸出合併:一致(同值)→agreed;不一致→disputed;B 席缺→degraded 全 disputed
  apply   人放行動作:把 merge(+人裁 adjudication)寫進 goldset labels(atomic;唯一寫 labels 入口)
  signal  讀 history 最後一筆考卷的 unjudged_rate,advisory 輸出(週閘薄接線消費)

母體/未標判定=retrieval_eval.collect_unjudged 單一實作(S0 同源紀律,禁另寫)。
"""
import argparse
import re
import datetime
import importlib.util
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

# 洗牌用的固定鹽——跟建題庫那支同名同值(build_goldset.py:12),兩邊是同一套去識別化;
# 值改了等於既有題庫的洗法全變,不要隨手動。
SHUFFLE_SALT = "lumos-retr-v1"

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


def cmd_material(args):
    """[S13] 產一份給評審讀的材料:★只有題目,沒有任何答案★。

    出身(實跑逃逸 2026-09-15):派工詞叫評審去讀題庫檔取查詢字串,而那個檔裡
    ★同時就存著既有標註答案★,某席自陳「初讀題庫時意外顯示部分既有 labels」。
    用被既有答案錨定過的標註去驗排序,等於讓尺被它要量的東西污染。

    ★這跟 [S8] 的名次洩漏是兩條不同的路徑★——洗牌補的是順序,這支補的是內容;
    補了一條不等於補了另一條。派工詞要改成指向這份材料,不要再指題庫檔。

    ★誠實天花板:這支★只提供一份乾淨材料,沒有任何機械手段擋住評審自己去開題庫檔★
    (2026-09-15 資安席)——上次的洩漏正是這樣發生的:派工詞叫評審去讀題庫,他就讀了。
    這支讓「照派工詞做」的人不會再看到答案,但擋不住「多開一個檔」的人。
    要真的擋住,得讓評審在讀不到題庫檔的環境裡工作(例如只掛載這份材料的沙箱),
    那是派工環境的事、不是這支腳本能做的。
    REVISIT:2026-11-15 若又發生一次同型逃逸,就不能再只靠派工詞,要把評審環境收窄。
    """
    gs = _read_goldset(args.goldset)
    if gs is None:
        return 2
    out = Path(args.out or (HERE / "rater-material.md"))
    lines = ["# 檢索評測題目卷(給評審讀)",
             "",
             "> ★這份刻意不含任何既有標註★——評審看到既有答案就不再是獨立判斷,",
             "> 而這些判斷是不可逆尺切換的依據。要查答案請找編排者,不要去開題庫檔。",
             ""]
    lines.append("## 搜尋題")
    lines.append("")
    # ★缺欄位不要整支炸★(2026-09-15 邊界輸入席):同檔 delta 對缺欄位用的是安全預設,
    # 新寫的這支卻直接索引,同一支腳本兩種脾氣。題庫壞掉時要照本檔慣例回 rc2 或標出來,
    # 不是拋一個沒人接的 KeyError。
    for c in sorted(gs.get("search", []), key=lambda x: str(x.get("id", ""))):
        lines.append(f"- {c.get('id', '(缺編號)')}｜查詢:「{c.get('query', '(缺查詢字)')}」")
    lines.append("")
    # ★改動片段要先遮掉節點路徑★(2026-09-15 外家席 blocker):那個欄位是★原封不動抄來的
    # 程式片段★,而這個 repo 的註解到處寫節點路徑;片段裡一旦出現某篇節點,等於直接把
    # 「這題的答案可能是它」告訴評審。現況題庫剛好零命中,★但那是運氣不是守衛★——
    # 防線要擋在輸出端,不能靠題庫每次重建都剛好乾淨。
    _NODE_PATH = re.compile(
        r"(?:Systems|Projects|Issues|Verification|MOC|Decisions)/[^\s\"`,;)\]]+")
    def _mask(s):
        return _NODE_PATH.sub("(節點路徑已遮)", str(s))
    lines.append("## 編輯題")
    lines.append("")
    for c in sorted(gs.get("edit", []), key=lambda x: str(x.get("id", ""))):
        lines.append(f"- {c.get('id', '(缺編號)')}｜改到的檔:`{c.get('file', '(缺檔名)')}`"
                     f"｜改動:{_mask(c.get('delta', '(未記)'))}")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"material: 搜尋題 {len(gs.get('search', []))}、編輯題 {len(gs.get('edit', []))} → {out}"
          f"(不含任何標註)")
    return 0


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
    # ★端給標註者之前要洗牌★([S8] Projects/評測尺修復_計劃;2026-09-15 代碼審資安席獨立再撞到):
    # 未標判定回傳的順序★就是現行排序的名次★,原樣端出去等於先告訴標註者「系統認為誰該排前面」,
    # 標出來的答案就不再獨立於被它驗證的那個排序——而那些答案正是不可逆尺切換的依據。
    # 建題庫那支腳本早就在洗(build_goldset.py 兩處 rnd.shuffle),這支漏了。
    # ★用固定種子★:同一份題庫跑兩次順序必須一樣,否則標註結果回溯不到當初看的是什麼;
    # 種子綁題庫身分與案例編號,不同案例各自洗、不同題庫也不會洗成同一種排法。
    import random as _random
    # ★洗牌的做法照建題庫那支的既有前例★(2026-09-15 架構對齊席):
    # 那邊一律 `random.Random(hashlib.sha256((鍵 + SALT).encode()).hexdigest())`,
    # 用同一個模組常數當鹽(build_goldset.py:52,166;規格 governance/golden/retrieval/spec.md:266)。
    # ★鍵裡要帶題庫指紋★(外家席):原本直接拿 split_salt 當種子是錯的——那是分組用的版本
    # 常數(現值 lumos-retr-v1),兩份不同題庫很可能一樣,於是不同題庫洗出同一種排法,
    # 「跨題庫隔離」是假宣稱。把題庫內容指紋放進鍵,兩個要求就同時滿足:
    # 形狀跟既有前例一致,而且題庫變了順序就變、同一份跑幾次都一樣。
    _ident = json.dumps({"s": gs.get("search"), "e": gs.get("edit"),
                         "c": gs.get("snapshot_commit")}, ensure_ascii=False, sort_keys=True)
    _gs_fp = hashlib.sha256(_ident.encode("utf-8")).hexdigest()[:16]
    cases = []
    for cid, nodes in sorted(u["per_case"].items()):
        # ★先排序再洗★:上游給的順序★本身就不穩定★(2026-09-15 實測:同一份題庫同一份語料
        # 連跑三次,有四題的候選順序跑出不同排法)。直接洗不穩定的輸入=同種子也洗不出同結果,
        # 「可重現」就是假的。先按節點名排成唯一的正規順序,洗出來才真的可重現。
        # 副作用剛好是要的:排序也把名次序一併洗掉了。
        if not all(isinstance(_n, str) for _n in nodes):
            # ★本檔慣例是印 ERROR: 回 rc2,不是拋沒人接的 TypeError★(2026-09-15 邊界輸入席)
            print(f"ERROR: 案例 {cid} 的候選裡有非字串項,未標清單來源壞了", file=sys.stderr)
            return 2
        _shuffled = sorted(nodes)
        _random.Random(hashlib.sha256(
            (f"{_gs_fp}|{cid}" + SHUFFLE_SALT).encode("utf-8")).hexdigest()).shuffle(_shuffled)
        cases.append({"id": cid, "unjudged": _shuffled})
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
        # ★這裡★不再★逐筆印出候選★(2026-09-15 外家席):原本按未標判定的順序把
        # 每個候選印出來,而那順序就是現行排序的名次——等於開了第三條洩漏路徑,
        # 只要標註者看得到這段診斷輸出就前功盡棄。改成只給數量與「去哪裡拿洗過的清單」。
        print(f"⛔ repin 擋下:評測母體尚有 {u['count']} 筆未標(散在 {len(u['per_case'])} 題)",
              file=sys.stderr)
        print("  要補標請跑 delta 產洗過順序的清單,不要照這裡的順序標:", file=sys.stderr)
        print("    python3 governance/eval/refresh_labels.py delta --goldset <題庫> --out <輸出前綴>",
              file=sys.stderr)
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

    mt = sub.add_parser("material", help="[S13] 給評審讀的題目卷(★不含任何標註★)")
    mt.add_argument("--goldset", default=str(HERE / "retrieval-goldset.json"))
    mt.add_argument("--out", help="輸出檔(預設 rater-material.md)")

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
    return {"delta": cmd_delta, "material": cmd_material, "repin": cmd_repin,
            "merge": cmd_merge, "apply": cmd_apply, "signal": cmd_signal}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
