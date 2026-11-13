#!/usr/bin/env python3
"""生成 retrieval goldset 骨架 + 人工標註表(spec:檢索優化_計劃 §6)。stdlib。
跑法: python3 governance/eval/build_goldset.py
產出: retrieval-goldset.json(骨架,labels 空) + retrieval-labeling-sheet.md(人標)
"""
import json, subprocess, sys, hashlib, random, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LUMOS = ROOT / "scripts" / "lumos"
VAULT = next((ROOT / "docs").glob("*-knowledge"))
SALT = "lumos-retr-v1"

SEARCH_QUERIES = {
    "zh_short": ["殺傷力", "收斂", "漏改", "治理", "留痕", "稻草人", "事故", "回滾", "合約", "排序", "冪等", "審計"],
    "identifier": ["guard kill", "cochange", "code-loop", "design-loop", "pitfalls", "anchor", "kill_recipes", "worktree"],
    "acronym": ["BM25F", "TTL", "SARIF", "HMAC", "BFS", "canary"],
    "single_char": ["閘", "坑", "審", "帳"],
}


def lum_json(*args, stdin=None):
    r = subprocess.run([sys.executable, str(LUMOS), "--vault", str(VAULT), *args],
                       capture_output=True, text=True, input=stdin, cwd=ROOT)
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {}


def lum_lines(*args):
    r = subprocess.run([sys.executable, str(LUMOS), "--vault", str(VAULT), *args],
                       capture_output=True, text=True, cwd=ROOT)
    return [l for l in r.stdout.splitlines() if l.strip()]


def split_of(cid):
    h = hashlib.sha256((cid + SALT).encode()).hexdigest()
    return "train" if int(h[:8], 16) % 10 < 6 else "held"


def search_pool(q):
    """池 = legacy 命中前 8 ∪ ranked 前 8(去識別:只留節點名,洗牌)"""
  # ★必須顯式 --no-any★:2026-08-03 起多詞回退是 search 預設,「不傳旗標」不再等於
  # 舊行為。本函式要的是★片語語意的候選池★,吃到回退擴召回會讓 goldset/評測基線
  # 靜默混入 OR 召回的結果。(code-loop r2 全局哨兵抓到,真庫實測:
  #  `search "殺傷力 SARIF" --legacy` → 21 篇,加 --no-any → 0 篇)
    legacy = [l.split(" (")[0] for l in lum_lines("search", q, "--no-any", "--legacy", "--files-only")
              if l.split(" (")[0].endswith(".md") and "/" in l][:8]
    ranked = [x["node"] for x in lum_json("search", q, "--no-any", "--ranked", "--top", "8", "--json").get("results", [])]
    pool = list(dict.fromkeys(legacy + ranked))
    rnd = random.Random(hashlib.sha256((q + SALT).encode()).hexdigest())
    rnd.shuffle(pool)
    return pool


def _edit_quota(edit):
    """題庫裡每支檔已佔的名額與已用過的 (檔, 提交)、(檔, 改動片段)——加題與抽題兩端共用同一套「算不算重複」。"""
    per, commits, deltas = {}, set(), set()
    for e in edit:
        f = e.get("file")
        per[f] = per.get(f, 0) + 1
        commits.add((f, str(e.get("commit", ""))[:8]))
        deltas.add((f, e.get("delta")))
    return per, commits, deltas


def append_edit_cases(gs, new_pairs, per_file=1):
    """★加題:只加不碰既有(2026-08-22)★ — 回**新的** gs(不就地竄改輸入)。

    new_pairs = [(case_dict, pool_list), ...];case_dict 至少要有 file/delta/commit。

    ★為什麼是 append 不是重建★:既有 labels 是累積數月的雙評審資產
    (`build_goldset` 的裸跑防護就是為它立的——全量重建會整本清空)。
    加題如果動到既有題目或標註,等於用一個「擴充」動作偷偷換尺,
    而換尺會讓整本 history 的比較失效(見 Projects/標註刷新_計劃)。

    會被跳過的新題:
      ① 那支檔的題數已到上限 per_file(題庫裡已有的算進名額;預設 1=舊規則「同檔只出一題」)。
         ★放寬的依據(2026-11-12,Projects/改檔題庫擴充_計劃 S2)★:舊理由「同檔候選池幾乎一樣」對常改的
         大檔不成立——同檔不同改動推出的前 8 名兩兩重疊 0 到 0.2,排序是被改動片段帶動的;但同檔的題不完全
         獨立,所以只放寬到有上限。
      ② 同檔同提交、或同檔同改動片段(那是同一題)
      ③ 候選池空(dotfile/vendor 那類,進了卷面就是廢題——見 _is_junk_edit_file)
      ④ 垃圾檔(同上,雙保險)

    新題的 labels 一律 `{"final": None}` = 未標,接著走
    `refresh_labels.py delta → merge → apply` 補標;**本函式不碰任何既有鍵**。
    """
    import copy
    out = copy.deepcopy(gs)
    per, seen_commits, seen_deltas = _edit_quota(out.get("edit", []))
    used = {e.get("id") for e in out.get("edit", [])}
    n = 0
    for e in out.get("edit", []):
        eid = str(e.get("id", ""))
        if eid.startswith("E") and eid[1:].isdigit():
            n = max(n, int(eid[1:]))
    for case, pool in new_pairs:
        f = case.get("file")
        if not f or per.get(f, 0) >= per_file or _is_junk_edit_file(f) or not pool:
            continue
        if (f, str(case.get("commit", ""))[:8]) in seen_commits or (f, case.get("delta")) in seen_deltas:
            continue
        n += 1
        cid = f"E{n:02d}"
        while cid in used:                 # 防既有編號有洞/重複時撞號
            n += 1
            cid = f"E{n:02d}"
        used.add(cid)
        per[f] = per.get(f, 0) + 1
        seen_commits.add((f, str(case.get("commit", ""))[:8]))
        seen_deltas.add((f, case.get("delta")))
        out.setdefault("edit", []).append({"id": cid, **case, "split": split_of(cid)})
        out.setdefault("labels", {})[cid] = {x: {"final": None} for x in pool}
    return out


def _is_junk_edit_file(f):
    """★出題垃圾過濾(2026-08-22)★ — True = 不該當 edit 題。

    症狀:2026-08-22 實測既有 20 題裡 4 題候選池全空、labels 無鍵、eval 直接跳過——
    `.gitignore` x2、`vendor/*.min.js` x2。train 名義 8 實際 6、held 名義 12 實際 10。
    ★「樣本太小」有一半是這裡撿到的垃圾,不是題庫真的小。★

    兩類:
      ① dotfile —— 設定檔,圖譜不會有節點在講它,`impact` 撈不到東西。
      ② 壓縮/vendored 產物 —— 第三方最小化檔,delta 抓出來是一長串無意義字元,
         而且不是我們的 code,沒有對應的圖譜節點。
      ③ 規則範例與測試資料(路徑裡有 samples/fixtures/testdata 這一層,2026-11-12)—— 副檔名是程式、
         掛鉤也會觸發,但它們是規則的好壞範例,一條規則一組、幾百支長得差不多;實測放寬同檔上限後
         500 個候選有 469 個是 kotlin-android 的範例檔,不擋會把題庫淹掉(Projects/改檔題庫擴充_計劃 S1)。
    """
    import posixpath
    base = posixpath.basename(f)
    if base.startswith("."):
        return True
    if f.startswith("vendor/") or "/vendor/" in f:
        return True
    if base.endswith((".min.js", ".min.css")):
        return True
    return bool({"samples", "fixtures", "testdata", "__fixtures__"} & set(f.split("/")[:-1]))


HOOK = Path(__file__).resolve().parents[2] / "scripts" / "hooks" / "claude" / "impact-hook.py"


_HOOK_CACHE = {}   # 掛鉤路徑 → 載入的模組(行程內;同主程式 _REPO_FILES_CACHE 那種字典快取)


def _load_hook():
    """載入改檔前掛鉤當模組(檔名有連字號,只能照路徑載;載法同鄰居 refresh_labels._load_re)。
    第一次用到才載:出題腳本被單獨複製去跑裸跑防護測試時旁邊沒有掛鉤,模組頂層就載會在走到防護前崩潰。
    掛鉤的模組層級只有常數與函式定義,讀標準輸入與寫事件都在它自己的 __main__ 底下,載入沒有副作用。"""
    key = str(HOOK)
    if key not in _HOOK_CACHE:
        import importlib.util
        spec = importlib.util.spec_from_file_location("lumos_impact_hook_for_goldset", HOOK)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _HOOK_CACHE[key] = m
    return _HOOK_CACHE[key]


def _hook_would_fire(f, root):
    """★出題母體=改檔前掛鉤會觸發的檔★(Projects/改檔題庫擴充_計劃 S1)。
    直接呼叫掛鉤自己那支單檔判斷(副檔名清單、無副檔名看直譯器宣告、排除路徑),不在這裡另抄一份清單——
    兩份清單一定漂移(這個目錄的 retrieval_eval_multiword 早有同樣教訓)。帶 repo 根,無副檔名檔才會去讀宣告行。"""
    return _load_hook()._decide_one(f, str(root)) is not None


def _first_added_line(root, sha, f):
    """那個提交對這支檔的第一行新增(去頭尾空白、最長 100 字);沒有就回「(結構性變更)」。"""
    show = subprocess.run(["git", "-C", str(root), "show", sha, "--", f],
                          capture_output=True, text=True, errors="replace", check=False).stdout
    for ln in show.splitlines():
        if ln.startswith("+") and not ln.startswith("+++") and len(ln) > 8:
            return ln[1:].strip()[:100]
    return "(結構性變更)"


def edit_cases(n=20, per_file=1, window=400, root=None):
    """從 git 歷史取近期改過的 code 檔 + 真實 delta 片段(提交新到舊)。

    per_file=同一支檔最多取幾題(預設 1=舊行為);同檔的題出自不同提交、且改動片段不同。
    只收改檔前掛鉤會觸發的檔(_hook_would_fire),再過既有的垃圾過濾。root 預設本 repo(測試指向暫存 repo)。"""
    root = Path(root) if root is not None else ROOT
    r = subprocess.run(["git", "-C", str(root), "-c", "core.quotepath=false", "log", "--no-merges", f"-{int(window)}",
                        "--pretty=format:%H", "--name-only"], capture_output=True, text=True, errors="replace",
                       check=False)
    cases, per, deltas = [], {}, set()
    cur_sha = None
    for line in r.stdout.splitlines():
        if len(cases) >= n:
            break
        if re.fullmatch(r"[0-9a-f]{40}", line.strip()):
            cur_sha = line.strip()
            continue
        f = line.strip()
        if not f or not cur_sha or f.startswith(("docs/", "governance/golden")):
            continue
        if per.get(f, 0) >= per_file or not (root / f).exists():
            continue
        if f.endswith((".md", ".jsonl", ".json")) and "eval" not in f:
            continue
        if _is_junk_edit_file(f):      # ★dotfile / vendor 壓縮檔 → 必是空池廢題★
            continue
        if not _hook_would_fire(f, root):
            continue
        delta = _first_added_line(root, cur_sha, f)
        if (f, delta) in deltas:
            continue
        deltas.add((f, delta))
        per[f] = per.get(f, 0) + 1
        cases.append({"file": f, "delta": delta, "commit": cur_sha[:8]})
    return cases


def edit_pool(file, delta):
    payload = json.dumps({"query": delta, "prospective": {}})
    _rk = lum_json("impact", "--file", file, "--ranked", "--top", "8",
                   "--stdin-payload", "--json", stdin=payload)
    ranked = _rk.get("results", []) + _rk.get("lane", [])   # v4:lane 候選人看得到,要進未來標註池
    legacy = lum_json("impact", "--file", file, "--json")
    legacy_nodes = [x["node"] for x in legacy.get("direct", [])[:5]] + \
                   [x["node"] for x in legacy.get("indirect", [])[:5]]
    pool = list(dict.fromkeys([x["node"] for x in ranked] + legacy_nodes))[:12]
    rnd = random.Random(hashlib.sha256((file + SALT).encode()).hexdigest())
    rnd.shuffle(pool)
    return pool


def _run_append(n, per_file=1, window=400, gpath=None):
    """`--append N` 的執行路徑:讀既有 goldset → 多撈候選 → 建池 → append → 寫回。
    ★不重建、不碰既有 labels★;寫回前先比對既有區塊沒被動過(寫後自驗)。"""
    if per_file < 1 or window < 1:
        print("ERROR: --per-file 與 --window 要是正整數", file=sys.stderr)
        return 2
    gpath = Path(gpath) if gpath is not None else Path(__file__).parent / "retrieval-goldset.json"
    gs = json.loads(gpath.read_text(encoding="utf-8"))
    before_edit = json.dumps(gs.get("edit", []), ensure_ascii=False, sort_keys=True)
    before_labels = json.dumps(gs.get("labels", {}), ensure_ascii=False, sort_keys=True)

    # 先在這裡扣掉名額已滿與重複的,省下建池(每題兩次影響查詢);最後把關仍是 append_edit_cases 的同一套判斷
    per, seen_commits, seen_deltas = _edit_quota(gs.get("edit", []))
    pairs = []
    for c in edit_cases(n * 4 + sum(per.values()) * per_file, per_file=per_file, window=window):
        if len(pairs) >= n:
            break
        f = c["file"]
        if per.get(f, 0) >= per_file or (f, c["commit"]) in seen_commits or (f, c["delta"]) in seen_deltas:
            continue
        pool = edit_pool(c["file"], c["delta"])
        if not pool:
            print(f"  (跳過空池題:{c['file']})", file=sys.stderr)
            continue
        pairs.append((c, pool))
        per[f] = per.get(f, 0) + 1
    if not pairs:
        print("沒有可加的新題(近期改過的檔都已出過題,或候選池全空)", file=sys.stderr)
        return 1

    new_gs = append_edit_cases(gs, pairs, per_file=per_file)
    # ★寫後自驗:既有區塊必須一字不差★——加題偷偷換尺是這裡最怕的事
    kept_edit = json.dumps(new_gs["edit"][:len(gs.get("edit", []))], ensure_ascii=False, sort_keys=True)
    if kept_edit != before_edit:
        print("ERROR: 既有 edit 題被動到了,中止不寫", file=sys.stderr)
        return 2
    for cid, v in json.loads(before_labels).items():
        if new_gs["labels"].get(cid) != v:
            print(f"ERROR: 既有標註 {cid} 被動到了,中止不寫", file=sys.stderr)
            return 2

    gpath.write_text(json.dumps(new_gs, ensure_ascii=False, indent=1), encoding="utf-8")
    added = [e["id"] for e in new_gs["edit"][len(gs.get("edit", [])):]]
    print(f"✓ 加了 {len(added)} 題:{', '.join(added)}(既有題目與標註未動)")
    print("  新題的標註還沒填。接著跑:")
    print("    python3 governance/eval/refresh_labels.py delta --goldset "
          f"{gpath}")
    print("  (再 merge → apply;補完 unjudged 歸零,--ablation 那道閘才會放行)")
    return 0


def main():
    # ★裸跑防護(標註刷新 T1,2026-08-18)★:全量重建會把既有 labels 整本清空
    # (下方對每題 {"final": None} 重建+覆寫檔案)。人工金標是累積數月的資產,
    # 手滑跑一次即歸零——重建必須顯式帶 --force-full 表達意圖。
    import argparse
    ap = argparse.ArgumentParser(
        description="出卷器:全量重建 goldset+標註表(★會清空既有人工標註★)")
    ap.add_argument("--force-full", action="store_true",
                    help="確認全量重建(既有 labels 全部歸零重出);增量補標請改用 refresh_labels.py delta")
    ap.add_argument("--append", type=int, metavar="N",
                    help="★只加 N 道新 edit 題,既有題目與標註一字不動★。"
                         "新題標註未填,接著走 refresh_labels.py delta → merge → apply 補標")
    ap.add_argument("--per-file", type=int, default=1, metavar="N",
                    help="搭配 --append:同一支檔最多幾題(題庫裡已有的算進名額;預設 1)")
    ap.add_argument("--window", type=int, default=400, metavar="N",
                    help="搭配 --append:往回看幾個提交找題(預設 400)")
    args = ap.parse_args()
    if args.append:
        return _run_append(args.append, per_file=args.per_file, window=args.window)
    if not args.force_full:
        ap.print_usage(sys.stderr)
        print("ERROR: 全量重建會清空既有人工標註,必須顯式 --force-full;"
              "增量補標走 refresh_labels.py delta。", file=sys.stderr)
        return 2
    random.seed(SALT)
    gs = {"snapshot_commit": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                                            capture_output=True, text=True).stdout.strip(),
          "split_salt": SALT, "search": [], "edit": [], "labels": {}}
    sheet = ["# 檢索評測標註表(人工金標)",
             "",
             "**怎麼標**:每個候選節點後面填 `2`(必看——回答這查詢/改這檔一定要看它)或 `1`(有用)。",
             "**留白 = 0(噪音)**,所以只要標有價值的,省力。標完存檔告訴 Claude 解析回 goldset。",
             ""]
    i = 0
    for cat, qs in SEARCH_QUERIES.items():
        for q in qs:
            i += 1
            cid = f"S{i:02d}"
            pool = search_pool(q)
            gs["search"].append({"id": cid, "query": q, "cat": cat, "split": split_of(cid)})
            gs["labels"][cid] = {n: {"final": None} for n in pool}
            sheet.append(f"## {cid}｜搜尋:「{q}」({cat}, {split_of(cid)})")
            if not pool:
                sheet.append("- (無候選——查詢在 vault 無命中,標註跳過)")
            for n in pool:
                sheet.append(f"- [ ] {n} ｜標:____")
            sheet.append("")
    # ★空池丟棄 + 補位(2026-08-22)★:多撈一倍候選,建出候選池才知道空不空;
    # 空池題進了卷面就是廢題(eval 跳過、白佔一個編號、讓 n 看起來比實際大)。
    want, j = 20, 0
    for c in edit_cases(want * 2):
        if j >= want:
            break
        pool = edit_pool(c["file"], c["delta"])
        if not pool:
            print(f"  (跳過空池題:{c['file']})", file=sys.stderr)
            continue
        j += 1
        cid = f"E{j:02d}"
        gs["edit"].append({"id": cid, **c, "split": split_of(cid)})
        gs["labels"][cid] = {n: {"final": None} for n in pool}
        sheet.append(f"## {cid}｜編輯:{c['file']} ({split_of(cid)})")
        sheet.append(f"> delta 樣本:`{c['delta'][:80]}`")
        for n in pool:
            sheet.append(f"- [ ] {n} ｜標:____")
        sheet.append("")
    out = Path(__file__).parent
    (out / "retrieval-goldset.json").write_text(json.dumps(gs, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "retrieval-labeling-sheet.md").write_text("\n".join(sheet), encoding="utf-8")
    n_lab = sum(len(v) for v in gs["labels"].values())
    print(f"✓ {len(gs['search'])} search + {len(gs['edit'])} edit 案例;候選標註列 {n_lab} 行")
    print(f"  標註表: governance/eval/retrieval-labeling-sheet.md")


if __name__ == "__main__":
    sys.exit(main())
