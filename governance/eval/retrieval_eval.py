#!/usr/bin/env python3
"""檢索評測器(治理面,非 lumos 子命令)。spec:Projects/檢索優化_計劃 §6。
零依賴 stdlib。跑法:
  python3 governance/eval/retrieval_eval.py --auto      # cochange proxy 自動金標(related 面,免人工)
  python3 governance/eval/retrieval_eval.py --goldset governance/eval/retrieval-goldset.json [--split held]
指標:nDCG@k / MRR / P@k / Recall@k。逐輪 append retrieval-eval-history.jsonl。
"""
import json, math, subprocess, sys, os, argparse, hashlib, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LUMOS = ROOT / "scripts" / "lumos"
_VENV = os.environ.get("LUMOS_EVAL_VAULT")
VAULT = Path(_VENV) if _VENV else next((ROOT / "docs").glob("*-knowledge"), None)


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
    """{node: int_final};final 為 None 視為未標=0。"""
    out = {}
    for node, v in gs["labels"].get(cid, {}).items():
        f = v.get("final")
        out[node] = int(f) if f is not None else 0
    return out


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
        legacy = [l.split(" (")[0] for l in _lum_lines("search", q, "--legacy", "--files-only")
                  if l.split(" (")[0].endswith(".md") and "/" in l]
        ranked = [x["node"] for x in
                  _lum("search", q, "--ranked", "--top", "10", "--json").get("results", [])]
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
        payload = json.dumps({"query": case.get("delta", ""), "prospective": {}})
        r = subprocess.run([sys.executable, str(LUMOS), "--vault", str(VAULT),
                            "impact", "--file", case["file"], "--ranked",
                            "--top", "50", "--stdin-payload", "--json"],
                           capture_output=True, text=True, input=payload, cwd=ROOT)
        try:
            data = json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            continue
        res = data.get("results", [])
        pins = [x for x in res if x.get("pinned")]
        free = [x for x in res if not x.get("pinned")]
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
        rows.append(row)
    return rows


def _pctl(vals, p):
    if not vals:
        return None
    s = sorted(vals)
    return s[min(len(s) - 1, int(round(p * (len(s) - 1))))]


def report_goldset(gs, split=None, k_search=5, k_edit=8):
    tag = split or "all"
    print(f"=== 人工 goldset 評測(split={tag}) ===")
    srows = eval_search(gs, split, k=k_search)
    verdict = {}
    if srows:
        ln, rn = _macro(srows, "legacy_ndcg"), _macro(srows, "ranked_ndcg")
        lm, rm = _macro(srows, "legacy_mrr"), _macro(srows, "ranked_mrr")
        lr, rr = _macro(srows, "legacy_r10"), _macro(srows, "ranked_r10")
        lift = (rn - ln) / ln * 100 if ln else 0.0   # ln=0 → fail-closed(不給 inf 免費過 gate)
        print(f"[search n={len(srows)}] nDCG@{k_search}: legacy={ln} ranked={rn} (提升 {lift:+.1f}%)")
        print(f"  MRR: legacy={lm} ranked={rm} | Recall@10: legacy={lr} ranked={rr}")
        verdict["search_lift_pct"] = round(lift, 1)
        verdict["search_gate"] = ln > 0 and lift >= 15.0
    erows = eval_edit(gs, split, k=k_edit)
    if erows:
        fp, fn = _macro(erows, "fusion_p"), _macro(erows, "fusion_ndcg")
        bp, bn = _macro(erows, "bm25_p"), _macro(erows, "bm25_ndcg")
        gp, gn = _macro(erows, "graph_p"), _macro(erows, "graph_ndcg")
        print(f"[edit n={len(erows)}] P@{k_edit}: fusion={fp} bm25={bp} graph={gp}")
        print(f"  nDCG@{k_edit}: fusion={fn} bm25={bn} graph={gn}")
        frees = [r["n_free"] for r in erows]
        med, p95 = _pctl(frees, 0.5), _pctl(frees, 0.95)
        must_t = sum(r["must_total"] for r in erows)
        must_hit = sum(r["must_in_out"] for r in erows)
        must_pin = sum(r["must_pinned"] for r in erows)
        pin_noise = sum(r["pin_noise"] for r in erows)
        print(f"  非固定項數: 中位={med} p95={p95} | must-see(標2) {must_hit}/{must_t} 在輸出內"
              f"(僅 {must_pin} 個坐固定席——機械保證只涵蓋合約/事故類,其餘經排序無保底)"
              f" | 固定席噪音 {pin_noise} 條")
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
    return {"split": tag, "search": srows, "edit": erows, "verdict": verdict}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto", action="store_true", help="cochange proxy 自動金標(related 面)")
    ap.add_argument("--goldset", help="人工標註 goldset.json 路徑")
    ap.add_argument("--split", choices=["train", "held"], help="只跑該切分")
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
        unl = sum(1 for c in gs["labels"].values() for v in c.values() if v.get("final") is None)
        if unl:
            print(f"⚠ 尚有 {unl} 個候選未定稿(final=None,視為 0)", file=sys.stderr)
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
        print("=== §6 gate ===")
        ok = all(val is True for val in gates.values())  # fail-closed:無資料(None)不放行
        for name, val in gates.items():
            mark = "✅" if val else ("❌" if val is False else "–(無資料,fail-closed)")
            print(f"  {mark} {name}")
        print(f"gate 總判定: {'PASS — 可翻預設' if ok else 'FAIL — 維持 dormant'}")
        hist = Path(__file__).parent / "retrieval-eval-history.jsonl"
        with open(hist, "a", encoding="utf-8") as fh:
            head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
            fh.write(json.dumps({"mode": "goldset", "ts": datetime.date.today().isoformat(),
                                 "eval_head": head, "vault_note": "活語料:節點增修致數字 ±1pp 漂移;重現=checkout eval_head 重跑",
                                 "k": args.k, "gates": gates, "pass": ok,
                                 "verdicts": {r["split"]: r["verdict"] for r in reports}},
                                ensure_ascii=False) + "\n")
        return 0 if ok else 1
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
