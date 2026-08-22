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


def append_edit_cases(gs, new_pairs):
    """★加題:只加不碰既有(2026-08-22)★ — 回**新的** gs(不就地竄改輸入)。

    new_pairs = [(case_dict, pool_list), ...];case_dict 至少要有 file/delta/commit。

    ★為什麼是 append 不是重建★:既有 labels 是累積數月的雙評審資產
    (`build_goldset` 的裸跑防護就是為它立的——全量重建會整本清空)。
    加題如果動到既有題目或標註,等於用一個「擴充」動作偷偷換尺,
    而換尺會讓整本 history 的比較失效(見 Projects/標註刷新_計劃)。

    三種會被跳過的新題:
      ① 檔案已經有題(同一個檔出兩題,候選池幾乎一樣,是灌水不是加樣本)
      ② 候選池空(dotfile/vendor 那類,進了卷面就是廢題——見 _is_junk_edit_file)
      ③ 垃圾檔(同上,雙保險)

    新題的 labels 一律 `{"final": None}` = 未標,接著走
    `refresh_labels.py delta → merge → apply` 補標;**本函式不碰任何既有鍵**。
    """
    import copy
    out = copy.deepcopy(gs)
    have_files = {e.get("file") for e in out.get("edit", [])}
    used = {e.get("id") for e in out.get("edit", [])}
    n = 0
    for e in out.get("edit", []):
        eid = str(e.get("id", ""))
        if eid.startswith("E") and eid[1:].isdigit():
            n = max(n, int(eid[1:]))
    for case, pool in new_pairs:
        f = case.get("file")
        if not f or f in have_files or _is_junk_edit_file(f) or not pool:
            continue
        n += 1
        cid = f"E{n:02d}"
        while cid in used:                 # 防既有編號有洞/重複時撞號
            n += 1
            cid = f"E{n:02d}"
        used.add(cid)
        have_files.add(f)
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
    """
    import posixpath
    base = posixpath.basename(f)
    if base.startswith("."):
        return True
    if f.startswith("vendor/") or "/vendor/" in f:
        return True
    if base.endswith((".min.js", ".min.css")):
        return True
    return False


def edit_cases(n=20):
    """從 git 歷史取近期改過的 code 檔 + 真實 delta 片段。"""
    r = subprocess.run(["git", "-C", str(ROOT), "log", "--no-merges", "-400",
                        "--pretty=format:%H", "--name-only"], capture_output=True, text=True)
    files, seen = [], set()
    cur_sha = None
    for line in r.stdout.splitlines():
        if re.fullmatch(r"[0-9a-f]{40}", line.strip()):
            cur_sha = line.strip()
        elif line.strip() and not line.startswith("docs/") and not line.startswith("governance/golden"):
            f = line.strip()
            if f in seen or not (ROOT / f).exists():
                continue
            if f.endswith((".md", ".jsonl", ".json")) and "eval" not in f:
                continue
            if _is_junk_edit_file(f):      # ★dotfile / vendor 壓縮檔 → 必是空池廢題★
                continue
            seen.add(f)
            files.append((f, cur_sha))
        if len(files) >= n:
            break
    cases = []
    for f, sha in files[:n]:   # 注意:呼叫端可傳 n*2 多撈一批,供「空池丟棄後補位」
        show = subprocess.run(["git", "-C", str(ROOT), "show", sha, "--", f],
                              capture_output=True, text=True).stdout
        hunk = ""
        for l in show.splitlines():
            if l.startswith("+") and not l.startswith("+++") and len(l) > 8:
                hunk = l[1:].strip()[:100]
                break
        cases.append({"file": f, "delta": hunk or "(結構性變更)", "commit": sha[:8]})
    return cases


def edit_pool(file, delta):
    payload = json.dumps({"query": delta, "prospective": {}})
    ranked = lum_json("impact", "--file", file, "--ranked", "--top", "8",
                      "--stdin-payload", "--json", stdin=payload).get("results", [])
    legacy = lum_json("impact", "--file", file, "--json")
    legacy_nodes = [x["node"] for x in legacy.get("direct", [])[:5]] + \
                   [x["node"] for x in legacy.get("indirect", [])[:5]]
    pool = list(dict.fromkeys([x["node"] for x in ranked] + legacy_nodes))[:12]
    rnd = random.Random(hashlib.sha256((file + SALT).encode()).hexdigest())
    rnd.shuffle(pool)
    return pool


def _run_append(n):
    """`--append N` 的執行路徑:讀既有 goldset → 多撈候選 → 建池 → append → 寫回。
    ★不重建、不碰既有 labels★;寫回前先比對既有區塊沒被動過(寫後自驗)。"""
    out_dir = Path(__file__).parent
    gpath = out_dir / "retrieval-goldset.json"
    gs = json.loads(gpath.read_text(encoding="utf-8"))
    before_edit = json.dumps(gs.get("edit", []), ensure_ascii=False, sort_keys=True)
    before_labels = json.dumps(gs.get("labels", {}), ensure_ascii=False, sort_keys=True)

    have = {e.get("file") for e in gs.get("edit", [])}
    pairs = []
    for c in edit_cases(n * 4):          # 多撈:要扣掉已有檔與空池
        if len(pairs) >= n:
            break
        if c["file"] in have:
            continue
        pool = edit_pool(c["file"], c["delta"])
        if not pool:
            print(f"  (跳過空池題:{c['file']})", file=sys.stderr)
            continue
        pairs.append((c, pool))
    if not pairs:
        print("沒有可加的新題(近期改過的檔都已出過題,或候選池全空)", file=sys.stderr)
        return 1

    new_gs = append_edit_cases(gs, pairs)
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
    args = ap.parse_args()
    if args.append:
        return _run_append(args.append)
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
