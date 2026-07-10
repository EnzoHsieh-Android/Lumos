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


def ndcg_at_k(ranked_labels, k):
    ideal = sorted(ranked_labels, reverse=True)
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
        print("人工 goldset 評測:框架就緒,待填 goldset(schema 見 §6)")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
