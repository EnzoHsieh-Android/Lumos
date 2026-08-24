#!/usr/bin/env python3
"""檢索評測器(治理面,非 lumos 子命令)。spec:Projects/檢索優化_計劃 §6。
零依賴 stdlib。跑法:
  python3 governance/eval/retrieval_eval.py --auto      # cochange proxy 自動金標(related 面,免人工)
  python3 governance/eval/retrieval_eval.py --goldset governance/eval/retrieval-goldset.json [--split held]
指標:nDCG@k / MRR / P@k / Recall@k。逐輪 append retrieval-eval-history.jsonl。
"""
import json, math, subprocess, sys, os, argparse, hashlib, datetime
from pathlib import Path

_SELF_ROOT = Path(__file__).resolve().parents[2]
# LUMOS_EVAL_ROOT:測試/跨庫導向目標 repo(worktree 釘定的 git 根);預設=本體 repo
ROOT = Path(os.environ.get("LUMOS_EVAL_ROOT") or _SELF_ROOT)
# 目標 repo 有 vendored scripts/lumos 就用它,否則回退本體版本(與 refresh_labels._setup 同語意)
LUMOS = (ROOT / "scripts" / "lumos") if (ROOT / "scripts" / "lumos").exists() \
    else _SELF_ROOT / "scripts" / "lumos"
_VENV = os.environ.get("LUMOS_EVAL_VAULT")
VAULT = Path(_VENV) if _VENV else next((ROOT / "docs").glob("*-knowledge"), None)
SNAP_ROOT = None   # 語料快照 worktree 根(釘定時設);impact 走 --repo,不理 --vault


def _lum(*args):
    r = subprocess.run([sys.executable, str(LUMOS), "--vault", str(VAULT), *args],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {}


def dcg(rels):
    return sum(r / math.log2(i + 2) for i, r in enumerate(rels))


def ndcg_at_k(ranked_labels, k, all_rels=None):
    """all_rels=該案例完整金標 label 清單(IDCG 基準)。省略時退回取回集自證——
    僅限「各系統共用同一候選集」的相對比較(edit ablation);跨系統絕對比較必傳,
    否則漏檢索零懲罰、兩系統不在同一把尺(r1 panel s4 major)。"""
    ideal = sorted(all_rels if all_rels is not None else ranked_labels, reverse=True)
    idcg = dcg(ideal[:k])
    return dcg(ranked_labels[:k]) / idcg if idcg > 0 else 0.0


def mrr(ranked_labels):
    for i, r in enumerate(ranked_labels):
        if r >= 1:
            return 1.0 / (i + 1)
    return 0.0


def precision_at_k(ranked_labels, k):
    top = ranked_labels[:k]
    return sum(1 for r in top if r >= 1) / len(top) if top else 0.0


def cochange_goldset():
    """cochange 規則→related 金標(免人工):兩端皆 knowledge 節點的高 conf 對。"""
    rules = _lum("cochange", "rules", "--json").get("rules", [])
    gold = {}
    kg = f"docs/{VAULT.name}/"
    for r in rules:
        a, b = r["lhs"], r["rhs"]
        if a.startswith(kg) and b.startswith(kg):
            seed = a[len(kg):]
            tgt = b[len(kg):]
            gold.setdefault(seed, {})[tgt] = 2 if r["confidence"] >= 0.9 else 1
    return gold


def eval_related(gold, k=8):
    """對每個 seed 節點跑 context --recommend,用金標算指標。"""
    rows = []
    for seed, rel_map in gold.items():
        recos = _lum("context", f"Systems/{Path(seed).stem}", "--recommend",
                     "--top", str(k), "--json").get("recommend", [])
        if not recos:
            recos = _lum("context", seed.replace(".md", ""), "--recommend",
                         "--top", str(k), "--json").get("recommend", [])
        labels = [rel_map.get(Path(x["node"]).name, rel_map.get(x["node"], 0)) for x in recos]
        if not labels and not recos:
            continue
        rows.append({"seed": seed, "ndcg": ndcg_at_k(labels, k),
                     "mrr": mrr(labels), "p": precision_at_k(labels, k),
                     "n_gold": len(rel_map), "n_reco": len(recos)})
    return rows


def recall_at_k(ranked_labels, n_relevant, k):
    if n_relevant <= 0:
        return None
    return sum(1 for r in ranked_labels[:k] if r >= 1) / n_relevant


def _lum_lines(*args):
    r = subprocess.run([sys.executable, str(LUMOS), "--vault", str(VAULT), *args],
                       capture_output=True, text=True, cwd=ROOT)
    return [l for l in r.stdout.splitlines() if l.strip()]


def _labels_of(gs, cid):
    """{node: int_final};final 為 None 視為未標=0。
    ★計分專用★——「未標 vs 已判0」在此被刻意收斂(計分尺不變);
    未標判定禁用本函式,走 collect_unjudged(標註刷新 S0 三態)。"""
    out = {}
    for node, v in gs["labels"].get(cid, {}).items():
        f = v.get("final")
        out[node] = int(f) if f is not None else 0
    return out


# ── 標註刷新共用原語(S0 評測母體;delta/repin/unjudged-rate 三處同源單點)──

def _search_arms(q):
    """search 題兩臂(與 eval_search 同一組呼叫;--no-any 紀律同該處註解)。"""
    legacy = [l.split(" (")[0] for l in _lum_lines("search", q, "--no-any", "--legacy", "--files-only")
              if l.split(" (")[0].endswith(".md") and "/" in l]
    ranked = [x["node"] for x in
              _lum("search", q, "--no-any", "--ranked", "--top", "10", "--json").get("results", [])]
    return legacy, ranked


def edit_universe(case):
    """edit 題候選撈取=impact --top 50 原始 results(含 pinned 欄,固定席不受名額限制)。
    file 不存在(相對快照/現況語料)→ None=skip:file-gone(★S0 刻意行為變更,非重構等價:
    舊碼靠 impact 反查不需檔案在磁碟,本版明確短路——code-r1 整合席記錄★);輸出不可解 → None。"""
    base = SNAP_ROOT or ROOT
    if not (Path(base) / case["file"]).exists():
        return None
    payload = json.dumps({"query": case.get("delta", ""), "prospective": {}})
    r = subprocess.run([sys.executable, str(LUMOS),
                        "impact", "--file", case["file"],
                        "--repo", os.environ.get("LUMOS_EVAL_REPO") or str(SNAP_ROOT or ROOT),
                        "--ranked", "--top", os.environ.get("LUMOS_EVAL_IMPACT_TOP", "50"),
                        "--stdin-payload", "--json"],
                       capture_output=True, text=True, input=payload, cwd=ROOT)
    try:
        d = json.loads(r.stdout.strip().splitlines()[-1])
        # pin-denoise-a-v4:lane 是獨立頂層鍵——合併進候選清單(lane 項保留 "lane" 欄位標記),
        # 下游一律用明文鍵過濾(split_buckets),不靠 pinned 二分
        return d.get("results", []) + d.get("lane", [])
    except (ValueError, IndexError):
        return None


# 計分觸及邊界(落地後發現 2026-08-18):全母體口徑實測連原快照都 54% 未標
# (399/738;金標只批過出卷小池)→ repin 永不可過。未標判定收斂到「未標了會
# 實際影響分數」的位置:search=兩臂各前 10(nDCG@5/MRR/R@10 觸及帶+餘裕)、
# edit=free 前 k(P@top_k/nDCG 觸及)+全部固定席(pin_noise=事故指標,不受名額限制)。
SEARCH_TOUCH = 10


def _touched_search(legacy, ranked):
    """search 題計分觸及集=兩臂各前 SEARCH_TOUCH,保序去重。"""
    seen, out = set(), []
    for n in legacy[:SEARCH_TOUCH] + ranked[:SEARCH_TOUCH]:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def split_buckets(res):
    """★三桶分流的唯一實作★(pin-denoise-a-v4 arch:同檔兩種 free 定義=接手的人要猜):
    pins=pinned 真值;lane=帶 lane 欄位(參考道,不進 P@8 計分、視同 pins 納入未標檢查);
    free=其餘(★含 rescued——它進 P@8 母體是 2026-08-07 具名護欄「誠實計噪」的刻意設計,勿排★)。"""
    pins = [x for x in res if x.get("pinned")]
    lane = [x for x in res if not x.get("pinned") and x.get("lane")]
    free = [x for x in res if not x.get("pinned") and not x.get("lane")]
    return pins, free, lane


def _touched_edit(res, k=8):
    """edit 題計分觸及集=free 前 k+全部 pins+全部 lane(lane 視同 pins:人看得到就要標過)。"""
    _p, _f, _l = split_buckets(res)
    free = [x["node"] for x in _f]
    pins = [x["node"] for x in _p] + [x["node"] for x in _l]
    seen, out = set(), []
    for n in free[:k] + pins:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def ablation_blocked(gs, split=None, k=8):
    """★消融前置閘(2026-08-22)★ — 回 (blocked: bool, count: int, msg: str)。

    要擋的事:**這把尺對「改善」有系統性偏見。**
    候選池是 goldset 建檔當時從系統自己的 top-N 抓的;計分把未標當 0
    (`_labels_of`,那是 Projects/標註刷新_計劃 2026-08-17 明文裁過的——
    bpref/condensed-list 這類「只算已判」的改尺方案被拒,理由是一改尺既有門檻
    數字與整本 history 全失效;解法定為 delta 補標消滅未標,不動尺)。

    於是:**改善檢索 → 浮出新節點 → 新節點沒標過 → 全部計 0 → 改動被罰。**

    2026-08-22 實例:`_rank_tokenize` 補英文去尾 s,edit train 的未標從 4 個變 9 個,
    多出的 5 個全計 0;edit train 有效題 6 × k=8 = 分母 48——**5 個零分足以解釋
    整個 -0.036(-5.4%)**,而那個數字當時被讀成「改動有害」並據此撤回。

    ★該計劃當初設計的觸發情境是「語料前進」,沒想到「code 改動」也會讓候選浮出。★
    本閘補的是這個缺口,不是改尺。
    """
    u = collect_unjudged(gs, split, k=k)
    n = u["count"]
    if not n:
        return False, 0, ""
    cases = ", ".join(sorted(u["per_case"])[:6])
    more = "…" if len(u["per_case"]) > 6 else ""
    msg = (
        f"這輪有 {n} 個候選從來沒標過(散在 {len(u['per_case'])} 題:{cases}{more}),"
        f"計分時它們一律算 0 分。\n"
        f"改動如果讓新節點浮上來,那些新節點就落在這 {n} 個裡面,"
        f"分數一定往下掉——★掉的是尺的偏見,不是改動的效果,這輪結果不能拿來比。★\n"
        f"先把那幾筆補標,再回來量:\n"
        f"    python3 governance/eval/refresh_labels.py delta --goldset <goldset.json>\n"
        f"(接著 merge → apply;補完 unjudged 歸零這道閘就會放行)"
    )
    return True, n, msg


def collect_unjudged(gs, split=None, k=8):
    """S0 三態的唯一未標判定:計分觸及集內「labels 無此鍵或 final is None」=未標;
    已判(含0)不算。回 {"per_case", "skipped", "denom", "count", "rate"}。"""
    per_case, skipped, denom, count = {}, [], 0, 0
    def _unj(cid, nodes):
        nonlocal denom, count
        lab = gs["labels"].get(cid, {})
        unj = [n for n in nodes
               if n not in lab or lab[n].get("final") is None]
        denom += len(nodes)
        count += len(unj)
        if unj:
            per_case[cid] = unj
    for case in gs["search"]:
        if split and case["split"] != split:
            continue
        legacy, ranked = _search_arms(case["query"])
        _unj(case["id"], _touched_search(legacy, ranked))
    for case in gs["edit"]:
        if split and case["split"] != split:
            continue
        res = edit_universe(case)
        if res is None:
            skipped.append(f"{case['id']}:file-gone")
            continue
        _unj(case["id"], _touched_edit(res, k))
    return {"per_case": per_case, "skipped": skipped, "denom": denom,
            "count": count, "rate": (count / denom) if denom else 0.0}


def pin_snapshot(sha):
    """語料快照釘定(從 main 抽出;refresh_labels 共用):worktree+atexit 清理。
    成功→設 VAULT/SNAP_ROOT 回 True;失敗→印警告回 False(呼叫端自行決定退回現況)。"""
    global VAULT, SNAP_ROOT
    import tempfile, shutil, atexit
    _wt = Path(tempfile.mkdtemp(prefix="lumos-eval-snap-"))
    r = subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach",
                        str(_wt), sha], capture_output=True, text=True)
    if r.returncode == 0:
        # ★worktree add 一成功就註冊清理★(code-r1 bug 席:原重構把註冊搬進 _sv 判斷內,
        # 「add 成功但該 commit 無 vault」路徑只 rmtree 不 worktree remove → git 登記殘影)
        def _cleanup():
            subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(_wt)],
                           capture_output=True, text=True)
            shutil.rmtree(_wt, ignore_errors=True)
        atexit.register(_cleanup)
        _sv = next((_wt / "docs").glob("*-knowledge"), None)
        if _sv is not None:
            VAULT = _sv
            SNAP_ROOT = _wt
            return True
        _cleanup()   # 無 vault:當場清(worktree remove+rmtree),atexit 重跑冪等
        print(f"⚠ snapshot {sha} 內無 docs/*-knowledge,釘定失敗", file=sys.stderr)
        return False
    shutil.rmtree(_wt, ignore_errors=True)   # 失敗路徑不留殘目錄
    print(f"⚠ snapshot worktree 失敗({r.stderr.strip()[:80]})", file=sys.stderr)
    return False


def output_top3_must(res, lab):
    """★成績單乙案(2026-08-24 Enzo 裁):輸出前 3 名的必看命中率★(Projects/固定席扇出降權_計劃 調研節)。
    量的是「人打開 hook 先看到的三行是不是該看的」——不限固定席(甲案 pin_top3_must 是死表:
    必看 15/69 坐固定席、事故恆最前,前 3 席組成幾乎不變)。res 順序=impact 輸出順序(pins→free→rescued)。
    = 前 3 項裡標 2 的個數 / min(3, 該題標 2 總數);沒標 2 → None。只印、進 verdict/history,★不進 gate★。
    歸因:數字動了要分是 about 還是排序,拿 LUMOS_IMPACT_ABOUT=0 離線對照。"""
    must_total = sum(1 for v in lab.values() if v == 2)
    if must_total == 0:
        return None
    top = [x for x in res if not x.get("lane")][:3]   # v4-r2 Codex:lane 是掛「參考」標籤的獨立小節,不算首屏前三
    hit = sum(1 for x in top if lab.get(x["node"], 0) == 2)
    return round(hit / min(3, must_total), 4)


def pin_noise_ratchet(history, rev, split, count):
    """★固定席噪音棘輪(pin-denoise-a-v4 #4b,2026-08-24 knob 轉正時啟用)★——方向與 must 棘輪相反:只准降不准升。
    比同 goldset rev 最近一筆 PASS 的 pin_noise;沒基線 → 放行並建基線。回 (ok, msg)。"""
    base = None
    for rec in reversed(history):
        if not rec.get("pass") or rec.get("goldset_rev") != rev:
            continue
        v = (rec.get("verdicts") or {}).get(split) or {}   # verdicts={split: verdict}(同 must_ratchet 讀法)
        if isinstance(v, dict) and v.get("pin_noise") is not None:
            base = v["pin_noise"]
            break
    if base is None:
        return True, f"噪音棘輪:這版答案(標註版本 {rev[:6]})還沒有基線,這次的 {count} 條當基線,下次不准比它多"
    if count > base:
        return False, (f"噪音棘輪擋下:固定席不相干筆記從 {base} 條漲到 {count} 條。"
                       f"降噪是本案主目標,回漲就是回歸——先查是哪條保送路徑鬆了。")
    return True, ""


def _macro(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return round(sum(vals) / len(vals), 4) if vals else None


def eval_search(gs, split=None, k=5):
    """search 面:legacy 現行順序 vs ranked BM25F。主指標 nDCG@5;輔 MRR/Recall@10。"""
    rows = []
    for case in gs["search"]:
        if split and case["split"] != split:
            continue
        cid, q = case["id"], case["query"]
        lab = _labels_of(gs, cid)
        if not lab or not any(v >= 1 for v in lab.values()):
            continue  # 無相關項的案例對 nDCG 無定義,跳過並記數
        n_rel = sum(1 for v in lab.values() if v >= 1)
        # ★兩臂都必須顯式 --no-any★:2026-08-03 起多詞回退是 search 預設,「不傳旗標」
        # 不再等於舊行為。本 gate 是「legacy vs ranked」的受控比較,吃到回退擴召回會讓
        # 兩臂同時混入 OR 召回結果、基線失義。(code-loop r2 全局哨兵抓到;目前 goldset
        # 唯一的多詞題「guard kill」剛好字面存在故回退不觸發——★是還沒踩到,不是沒有★,
        # 下次換題就會中。)呼叫收斂進 _search_arms(與評測母體同源,標註刷新 T2)。
        legacy, ranked = _search_arms(q)
        row = {"id": cid, "split": case["split"], "n_rel": n_rel}
        all_rels = sorted(lab.values(), reverse=True)   # IDCG=完整金標(漏檢有懲罰,兩系統同尺)
        for name, order in (("legacy", legacy), ("ranked", ranked)):
            labels = [lab.get(n, 0) for n in order]
            row[f"{name}_ndcg"] = round(ndcg_at_k(labels, k, all_rels=all_rels), 4)
            row[f"{name}_mrr"] = round(mrr(labels), 4)
            row[f"{name}_r10"] = recall_at_k(labels, n_rel, 10)
        rows.append(row)
    return rows


def _graph_score(r):
    if r.get("kind") == "direct":
        return 1.0
    return 0.60 * min(1.0, 2.0 / (2 ** r.get("hop", 2)))


def eval_edit(gs, split=None, k=8):
    """edit/hook 面:impact --ranked。P@top_k/nDCG@top_k(非固定席);
    ablation=同候選集重排(fusion=score/BM25-only=L/graph-only=結構分)。
    固定席另計(安全機保,不算噪音);label2 固定席 recall 檢核。"""
    rows = []
    for case in gs["edit"]:
        if split and case["split"] != split:
            continue
        cid = case["id"]
        lab = _labels_of(gs, cid)
        if not lab or not any(v >= 1 for v in lab.values()):
            continue
        # impact 自行從 --repo 解析 vault(不吃全域 --vault)→ 快照釘定須走 --repo(r1 終審親驗)
        # 呼叫收斂進 edit_universe(與評測母體同源,標註刷新 T2);None=file-gone/不可解,照舊跳。
        res = edit_universe(case)
        if res is None:
            continue
        pins, free, lane_items = split_buckets(res)   # v4:free 不含 lane(P@8 母體);out_nodes 含 lane(下方讀完整 res)
        row = {"id": cid, "split": case["split"], "n_free": len(free), "n_pin": len(pins)}
        # edit 面 nDCG 沿用候選集自證 IDCG:三排序共用同一 free 集,相對比較有效;
        # 絕對值偏高(漏檢不罰),不得跨面引用(r1 panel s4)。
        orders = {
            "fusion": sorted(free, key=lambda x: (-x["score"], x["node"])),
            "bm25": sorted(free, key=lambda x: (-x.get("L", 0.0), x["node"])),
            "graph": sorted(free, key=lambda x: (-_graph_score(x), x["node"])),
        }

        n_rel_free = sum(1 for x in free if lab.get(x["node"], 0) >= 1)
        for name, order in orders.items():
            labels = [lab.get(x["node"], 0) for x in order]
            kk = min(k, len(labels)) or 1
            row[f"{name}_p"] = round(precision_at_k(labels, kk), 4) if labels else None
            row[f"{name}_ndcg"] = round(ndcg_at_k(labels, k), 4) if labels else None
        row["n_rel_free"] = n_rel_free
        # must-see 兩指標分開記(r1 panel codex blocker:混稱=證據失真):
        # in_out=出現在輸出(含自由席,top-k 聚合下可能被截) / pinned=真固定席(唯一機械保證)
        out_nodes = {x["node"] for x in res}
        pin_nodes = {x["node"] for x in pins}
        must = [n for n, v in lab.items() if v == 2]
        row["must_total"] = len(must)
        row["must_in_out"] = sum(1 for n in must if n in out_nodes)
        row["must_pinned"] = sum(1 for n in must if n in pin_nodes)
        row["pin_noise"] = sum(1 for x in pins if lab.get(x["node"], 0) == 0)
        row["out_top3_must"] = output_top3_must(res, lab)   # #10 乙案:輸出前 3 名必看命中率(res=人看到的順序)
        rows.append(row)
    return rows


def _pctl(vals, p):
    if not vals:
        return None
    s = sorted(vals)
    return s[min(len(s) - 1, int(round(p * (len(s) - 1))))]


def report_goldset(gs, split=None, k_search=5, k_edit=8):
    tag = split or "all"
    _n_s = sum(1 for c in gs["search"] if not split or c["split"] == split)
    _n_e = sum(1 for c in gs["edit"] if not split or c["split"] == split)
    _tag_plain = {"train": "調參用的那一半(train)", "held": "沒見過的那一半(held,防背題)", "all": "全部題目"}.get(tag, tag)
    print(f"=== 考卷:{_tag_plain}——{_n_s} 題搜尋、{_n_e} 題改程式 ===")
    srows = eval_search(gs, split, k=k_search)
    verdict = {}
    if srows:
        ln, rn = _macro(srows, "legacy_ndcg"), _macro(srows, "ranked_ndcg")
        lm, rm = _macro(srows, "legacy_mrr"), _macro(srows, "ranked_mrr")
        lr, rr = _macro(srows, "legacy_r10"), _macro(srows, "ranked_r10")
        lift = (rn - ln) / ln * 100 if ln else 0.0   # ln=0 → fail-closed(不給 inf 免費過 gate)
        print(f"搜尋(打一句話找筆記,{len(srows)} 題有答案):")
        print(f"  前 {k_search} 名的品質 {rn}(舊排序 {ln}),{'好了' if lift >= 0 else '★退了★'} {abs(lift):.1f}%    ← 這是主要的尺(nDCG@{k_search})")
        print(f"  第一個對的答案多靠前:{rm}(舊 {lm};1.0=都在第一名)  |  前 10 名撈到該撈的比例:{rr}(舊 {lr})")
        verdict["search_lift_pct"] = round(lift, 1)
        verdict["search_gate"] = ln > 0 and lift >= 15.0
    erows = eval_edit(gs, split, k=k_edit)
    # A/B 逐題對帳(hook必看召回修復 r2 折入):history 只存 rounded 比例,+1 筆判定
    # 需整數逐題 rows——env 指定路徑時把 erows 落 JSON,兩臂各 dump 一份對帳。
    _dump = os.environ.get("LUMOS_EVAL_DUMP_ROWS")
    if _dump:
        # 恆覆寫(code-loop 外家審修):erows 空時寫 [],否則上一輪殘檔會被當本臂證據
        with open(_dump, "w", encoding="utf-8") as f:
            json.dump({"split": split, "k_edit": k_edit, "edit_rows": erows},
                      f, ensure_ascii=False)
    if erows:
        fp, fn = _macro(erows, "fusion_p"), _macro(erows, "fusion_ndcg")
        bp, bn = _macro(erows, "bm25_p"), _macro(erows, "bm25_ndcg")
        gp, gn = _macro(erows, "graph_p"), _macro(erows, "graph_ndcg")
        print(f"改程式時的推薦(給一支檔,推該看的筆記,{len(erows)} 題有答案):")
        _pct = lambda x: f"{x*100:.0f}%" if x is not None else "無資料"
        print(f"  前 {k_edit} 名裡對的比例 {_pct(fp)}    ← 主要的尺(P@{k_edit});只比文字 {_pct(bp)}、只比圖結構 {_pct(gp)}——綜合要贏這兩個才算有用")
        print(f"  對的有沒有排前面(nDCG@{k_edit}):{fn}(只比文字 {bn}、只比圖 {gn})")
        pt3 = _macro(erows, "out_top3_must")
        print(f"  輸出前 3 名是必看的比率:{pt3}    ← 人打開 hook 先看到的三行準不準;只看不閘(歸因用 LUMOS_IMPACT_ABOUT=0 對照)")

        frees = [r["n_free"] for r in erows]
        med, p95 = _pctl(frees, 0.5), _pctl(frees, 0.95)
        must_t = sum(r["must_total"] for r in erows)
        must_hit = sum(r["must_in_out"] for r in erows)
        must_pin = sum(r["must_pinned"] for r in erows)
        pin_noise = sum(r["pin_noise"] for r in erows)
        print(f"  推薦量:每題通常推 {med} 篇、最多的題推 {p95} 篇(關卡用全部題目算:一般題 ≤{k_edit}、最多的題 ≤{k_edit + 2})")
        print(f"  必看的筆記:{must_t} 篇裡 {must_hit} 篇有推出來;其中 {must_pin} 篇是靠合約/事故硬保的固定席,其餘靠排序、沒有保底")
        print(f"  固定席裡不相干的筆記:{pin_noise} 條    ← 噪音,越少越好(目前只印不閘)")
        verdict["hook_p"] = fp
        verdict["free_median"] = med
        verdict["free_p95"] = p95
        verdict["hook_p_gate"] = fp is not None and fp >= 0.70
        verdict["hook_p"] = fp
        # fusion 各勝至少一主指標,另一指標不倒退超過 0.02
        def beats(a_p, a_n, b_p, b_n):
            return ((a_p > b_p and a_n >= b_n - 0.02) or
                    (a_n > b_n and a_p >= b_p - 0.02))
        verdict["fusion_vs_bm25"] = beats(fp, fn, bp, bn)
        verdict["fusion_vs_graph"] = beats(fp, fn, gp, gn)
        verdict["free_median_le_topk"] = med is not None and med <= k_edit
        verdict["free_p95_le_topk2"] = p95 is not None and p95 <= k_edit + 2
        verdict["must_in_out_recall"] = round(must_hit / must_t, 4) if must_t else None
        verdict["must_pinned_count"] = must_pin   # 唯一機保=固定席;in_out 含自由席無保底,勿混讀
        verdict["must_in_out_count"] = must_hit   # ★棘輪比的是個數不是比率★——
        verdict["must_total"] = must_t            #   比率會被「總數變了」稀釋,個數不會
        verdict["out_top3_must"] = pt3            # #10 乙案(2026-08-24):只觀測不閘;舊 key pin_top3_must 語意不同不沿用
        verdict["pin_noise"] = pin_noise          # v4 #4b:進 verdict,棘輪讀它
    return {"split": tag, "search": srows, "edit": erows, "verdict": verdict}


def _read_history():
    """讀 history jsonl → list[dict]。壞行跳過(帳是 append-only,torn 行不該讓評測掛掉)。
    路徑解析與寫入端同源:LUMOS_EVAL_HISTORY 優先(測試 fixture 帳,不污染真帳)。"""
    hp = Path(os.environ.get("LUMOS_EVAL_HISTORY")
              or Path(__file__).parent / "retrieval-eval-history.jsonl")
    if not hp.exists():
        return []
    rows = []
    for line in hp.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def goldset_rev(gs):
    """labels 的穩定短 hash = 「這把尺的版本」。

    補標、加題、移題都會改 labels → rev 變 → ★換尺★。history 每列記這個,
    比較只在同 rev 內做——不然會拿舊尺的數字擋新尺的結果,變成恆紅。
    (Projects/標註刷新_計劃 2026-08-22:一本帳 + goldset_rev,不分兩本;
     分兩本最後一定沒人看第二本。)
    """
    payload = json.dumps(gs.get("labels", {}), ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def must_ratchet(history, rev, split, count):
    """★must-see 棘輪(2026-08-22)★ — 回 (ok: bool, msg: str)。

    判準:必看項(labels 標 2)出現在輸出內的**個數**,不准比「同一 goldset_rev 下
    最近一筆 PASS」少。少一個就 FAIL。

    ★為什麼是棘輪不是數字門檻★:定門檻一定被問「為什麼 0.75 不是 0.8」,而且要定得
    有依據就得反覆看 held(違反 held 紀律)。棘輪不用選數字、不用看 held,
    **語意也對——標 2 的意思就是「必看」,掉一個就是缺陷,沒有「掉 20% 以內可接受」**。

    ★守的是什麼★:2026-08-22 實測 train 的 21 個 must-see 只有 7 個坐固定席(機械保證),
    其餘 14 個靠排序撐。排序一動把某個必看項擠出前 k,棘輪立刻紅——
    這比任何比率門檻都貼近事故的形狀。

    無同 rev 的 PASS 基線 → **放行並註明建立基線**(不能因為沒對照就擋,那是恆紅)。
    """
    base = None
    for row in reversed(history):
        if not row.get("pass"):
            continue                      # ★只拿 PASS 輪當基線★:FAIL 輪的數字不算數
        if row.get("goldset_rev") != rev:
            continue                      # ★換尺不比★
        v = (row.get("verdicts") or {}).get(split) or {}
        if v.get("must_in_out_count") is not None:
            base = v["must_in_out_count"]
            break
    if base is None:
        return True, f"必看棘輪:這版答案(標註版本 {rev[:6]})還沒有通過的紀錄可以比,這次的 {count} 篇就當基線,下次不准比它少"
    if count < base:
        return False, (f"必看棘輪擋下:必看的筆記上次推出 {base} 篇、這次只剩 {count} 篇。"
                       f"必看少推一篇就是缺陷,不是「掉一點點可接受」的那種數字。"
                       f"先看是排序把它擠出前幾名,還是那題的標註該重看。")
    return True, ""


def _history_record(args, gates, ok, reports, unj, pinned_sha):
    """history 逐筆組裝(純函式,標註刷新 T5)。新欄:goldset_snapshot=實際釘定 sha、
    unjudged_count/unjudged_rate(評測母體口徑;unj=None 時欄位保留值 None)。
    --snapshot 覆寫輪(過渡雙跑的舊快照輪)mode 寫 goldset-transition——
    autonomous-loop「取最後一筆 goldset 列」判定不受干擾。"""
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    knobs = {k: v for k, v in os.environ.items()
             if k.startswith("LUMOS_IMPACT_") or k.startswith("LUMOS_RANK_")}
    return {"mode": "goldset-transition" if getattr(args, "snapshot", None) else "goldset",
            "ts": datetime.date.today().isoformat(),
            "goldset_rev": getattr(args, "_goldset_rev", None),   # 這把尺的版本,比較只在同 rev 內做
            "eval_head": head, "goldset_snapshot": pinned_sha,
            "knobs": knobs or "frozen-defaults",
            "vault_note": "活語料:節點增修致數字 ±1pp 漂移;重現=checkout eval_head 重跑",
            "k": args.k, "gates": gates, "pass": ok,
            "unjudged_count": (unj or {}).get("count"),
            "unjudged_rate": (unj or {}).get("rate"),
            "verdicts": {r["split"]: r["verdict"] for r in reports}}


def main():
    global VAULT, SNAP_ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto", action="store_true", help="cochange proxy 自動金標(related 面)")
    ap.add_argument("--goldset", help="人工標註 goldset.json 路徑")
    ap.add_argument("--split", choices=["train", "held"], help="只跑該切分")
    ap.add_argument("--live-vault", action="store_true", help="用現況 vault(預設釘 goldset snapshot;探索/漂移觀測用)")
    ap.add_argument("--snapshot", help="覆寫釘定 sha(過渡雙跑的舊快照輪;該輪 mode=goldset-transition)")
    ap.add_argument("--ablation", action="store_true",
                    help="消融模式(比較改動前後用):★有任何未標候選就擋下、rc 3★。"
                         "不帶這旗標維持原行為(只印警告不擋)")
    ap.add_argument("-k", type=int, default=8)
    args = ap.parse_args()
    if VAULT is None:
        print("ERROR: 找不到 vault", file=sys.stderr); return 2
    if args.auto:
        gold = cochange_goldset()
        rows = eval_related(gold, k=args.k)
        if not rows:
            print("(cochange proxy 金標為空——knowledge git 史太稀薄,退回人工 goldset)")
            return 0
        agg = {m: round(sum(r[m] for r in rows) / len(rows), 4) for m in ("ndcg", "mrr", "p")}
        print(f"cochange-proxy related 評測(n={len(rows)} seeds, k={args.k}):")
        print(f"  nDCG@{args.k}={agg['ndcg']}  MRR={agg['mrr']}  P@{args.k}={agg['p']}")
        hist = Path(__file__).parent / "retrieval-eval-history.jsonl"
        with open(hist, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"mode": "auto-cochange", "k": args.k, "n": len(rows),
                                 **agg}, ensure_ascii=False) + "\n")
        return 0
    if args.goldset:
        try:
            gs = json.loads(Path(args.goldset).read_text(encoding="utf-8"))
            gs["labels"]; gs["search"]; gs["edit"]
        except (OSError, ValueError, KeyError, TypeError) as e:
            print(f"ERROR: goldset 讀取/結構失敗: {e}", file=sys.stderr)
            return 2
        # 語料快照釘定(r1 終審折入,可重現性正解):labels 對應出題當下的 vault——
        # 之後新增的未標節點若進候選池一律計噪音,gate 會被「寫文件」這種無關演進打翻。
        # 預設把評測 vault 釘在 goldset.snapshot_commit 的 worktree;--live-vault 才用現況(探索用)。
        _snap = args.snapshot or gs.get("snapshot_commit")
        # ★goldset_snapshot 帳面語意=「這輪實際用的語料」★:只有真的釘定成功才記 sha;
        # --live-vault/LUMOS_EVAL_VAULT 繞過釘定=用現況語料,帳面必須記 None(code-r1 bug 席 F2)。
        _pinned = None
        if _snap and not args.live_vault and not os.environ.get("LUMOS_EVAL_VAULT"):
            if pin_snapshot(_snap):
                _pinned = _snap
                print(f"(語料釘定 snapshot={_snap};--live-vault 可用現況)")
            else:
                print("(釘定失敗,退回現況 vault)", file=sys.stderr)
        unl = sum(1 for c in gs["labels"].values() for v in c.values() if v.get("final") is None)
        if unl:
            print(f"⚠ 尚有 {unl} 個候選未定稿(final=None,視為 0)", file=sys.stderr)
        if args.ablation:
            # ★母體口徑★:用 collect_unjudged 而非上面那個 unl——後者只數 labels 內
            # final=None,漏掉「根本不在候選池」的新節點,而那正是消融踩到的地雷。
            _blocked, _n, _msg = ablation_blocked(gs, args.split, k=args.k)
            if _blocked:
                print(f"\n⛔ 消融模式擋下這輪\n{_msg}", file=sys.stderr)
                return 3
        reports = []
        splits = [args.split] if args.split else [None, "train", "held"]
        for sp in splits:
            reports.append(report_goldset(gs, sp, k_edit=args.k))
            print()
        # gate 判定:全體 15% 提升 + held 不倒退 + hook P@k + fusion 雙勝
        v_all = next(r["verdict"] for r in reports if r["split"] == "all") \
            if not args.split else reports[0]["verdict"]
        gates = {"search nDCG@5 提升≥15%": v_all.get("search_gate"),
                 "hook P@top_k ≥0.70": v_all.get("hook_p_gate"),
                 "fusion 勝 BM25-only": v_all.get("fusion_vs_bm25"),
                 "fusion 勝 graph-only": v_all.get("fusion_vs_graph"),
                 "非固定中位 ≤ top_k": v_all.get("free_median_le_topk"),
                 "非固定 p95 ≤ top_k+2": v_all.get("free_p95_le_topk2")}
        if not args.split:
            v_held = next(r["verdict"] for r in reports if r["split"] == "held")
            gates["held-out 不倒退(lift>0)"] = (v_held.get("search_lift_pct") or 0) > 0
        # ★must-see 棘輪(2026-08-22)★:P@8 抓「推了一堆垃圾」,棘輪抓「該推的沒推」——
        # 兩種壞都要擋,所以★並存不是擇一★。
        # ☆刻意不換掉 hook P@top_k☆:換掉就是把現在 FAIL 的門檻拿走,動機會被讀成
        #   「gate 紅了就換尺」。並存才誠實。
        _rev = goldset_rev(gs)
        args._goldset_rev = _rev
        # per-split 棘輪(pin-denoise-a-v4 #5):全體之外 held 單獨也不准退——
        # 「held 少一筆、train 多一筆,全體不退」的漏洞(Codex r3 f4)由此關上
        _rat_splits = [args.split] if args.split else ["all", "held"]
        _hist_rows = _read_history()
        for _rat_split in _rat_splits:
            _rat_v = next((r["verdict"] for r in reports if r["split"] == _rat_split), None)
            if _rat_v is None:
                continue
            _rat_n = _rat_v.get("must_in_out_count")
            if _rat_n is None:
                continue
            _rat_ok, _rat_msg = must_ratchet(_hist_rows, _rev, _rat_split, _rat_n)
            _gname = "must-see 不退步(棘輪)" if _rat_split in ("all", args.split) else f"must-see 不退步({_rat_split} 棘輪)"
            gates[_gname] = _rat_ok
            if _rat_msg:
                print(f"  ↳ [{_rat_split}] {_rat_msg}")
            _pn = _rat_v.get("pin_noise")
            if _pn is not None:
                _pn_ok, _pn_msg = pin_noise_ratchet(_hist_rows, _rev, _rat_split, _pn)
                gates["固定席噪音不回漲(棘輪)" if _rat_split in ("all", args.split) else f"固定席噪音不回漲({_rat_split} 棘輪)"] = _pn_ok
                if _pn_msg:
                    print(f"  ↳ [{_rat_split}] {_pn_msg}")
        print(f"=== {len(gates)} 道關卡(全過才算這次改動沒把東西弄壞) ===")
        ok = all(val is True for val in gates.values())  # fail-closed:無資料(None)不放行
        _lift_all = v_all.get("search_lift_pct")
        _lift_held = (next((r["verdict"] for r in reports if r["split"] == "held"), {}) or {}).get("search_lift_pct") if not args.split else None
        _hp = v_all.get("hook_p")
        _plain = {   # ★history 的 key 不動(帳本連續),只有印出來的字換白話★
            "search nDCG@5 提升≥15%": f"搜尋:新排序比舊法好 {_lift_all:+.1f}%(門檻:至少 +15%)" if _lift_all is not None else "搜尋:新排序要比舊法好至少 15%(無資料)",
            "hook P@top_k ≥0.70": f"推薦:前 8 名裡 {_hp*100:.0f}% 是對的(門檻:至少 70%)" if _hp is not None else "推薦:前 8 名至少 70% 是對的(無資料)",
            "fusion 勝 BM25-only": "推薦:綜合排序沒輸給「只比文字」(輸了=圖譜那部分是裝飾)",
            "fusion 勝 graph-only": "推薦:綜合排序沒輸給「只比圖結構」(輸了=文字那部分是裝飾)",
            "非固定中位 ≤ top_k": f"推薦量:一般題推 {v_all.get('free_median')} 篇,沒超過 {args.k or 8}",
            "非固定 p95 ≤ top_k+2": f"推薦量:最多的題推 {v_all.get('free_p95')} 篇,沒超過 {(args.k or 8) + 2}",
            "held-out 不倒退(lift>0)": f"沒見過的題(搜尋)也沒退步:{_lift_held:+.1f}%(怕的是只在調參題上變好)" if _lift_held is not None else "沒見過的題也沒退步(無資料)",
            "must-see 不退步(棘輪)": "必看的筆記沒有比上次少推(棘輪:只准上不准下;少一篇就紅)",
            "must-see 不退步(held 棘輪)": "沒見過的那一半單獨看,必看也沒少推(防「訓練題多推、生題少推」互抵)",
            "固定席噪音不回漲(棘輪)": "固定席裡不相干的筆記沒有比上次多(降噪主目標的守門,只准降不准升)",
            "固定席噪音不回漲(held 棘輪)": "沒見過的那一半單獨看,噪音也沒回漲",
        }
        for name, val in gates.items():
            mark = "✅" if val else ("❌" if val is False else "–(無資料,照規矩當沒過)")
            print(f"  {mark} {_plain.get(name, name)}")
        print(f"gate 總判定: {f'PASS — {len(gates)} 關全過,這次改動可以留' if ok else 'FAIL — 有關卡沒過,上面 ❌ 那條就是要處理的'}")
        # S4 未標率(評測母體口徑;held 專屬,train 不計)——與 delta/repin 同源 collect_unjudged
        unj = collect_unjudged(gs, "held")
        print(f"沒批過答案的候選 unjudged(held 評測母體): {unj['count']}/{unj['denom']}(rate={round(unj['rate'], 4)})"
              + (f" skipped={unj['skipped']}" if unj["skipped"] else "")
              + ("    ← 不是 0 的話分數會被「沒批=算錯」拖低,先補標再比" if unj["count"] else "    ← 0 = 分數沒被「沒批=算錯」拖低"))
        # LUMOS_EVAL_HISTORY:測試導向 fixture 帳,避免 e2e 測試污染真 history(code-r1 修)
        hist = Path(os.environ.get("LUMOS_EVAL_HISTORY")
                    or Path(__file__).parent / "retrieval-eval-history.jsonl")
        with open(hist, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(_history_record(args, gates, ok, reports, unj, _pinned),
                                ensure_ascii=False) + "\n")
        return 0 if ok else 1
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
