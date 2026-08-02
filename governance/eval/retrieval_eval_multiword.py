#!/usr/bin/env python3
"""多詞查詢回退(--any)的量測(spec:Projects/檢索多詞回退_計劃 M4)。stdlib。

跑法:
  python3 governance/eval/retrieval_eval_multiword.py --labels <裁決後的 labels.json> \\
      --pool <mw-pool.json> --vault <釘定快照的 vault>

★為什麼另開一支而不是塞進 retrieval_eval.py★:那支比的是「legacy vs ranked」兩臂,
而本題比的是「有無 --any」——實驗組 10 題在**兩臂**下都回 0 候選,塞進去會讓既有
gate 的分母出現 0 而失義。★但計分函式一律從 retrieval_eval import,不另寫一份★
(2026-08-02 教訓:預檢與主迴圈兩份實作立刻就漂移了)。

★誠實邊界(必讀)★:
- 候選池有一半來自 `--any` 自己的 top-10 → **pooling bias**:被它排前面的一定被標到,
  而「更好的系統會找到、但它沒找到」的節點★可能不在池裡★,偽陰性量不到。
  緩解=池的第三來源是「逐詞出現次數 top-3」,★不經 BM25F★,是獨立來源。仍不完全乾淨。
- IDCG 以「池內標到的最佳排列」為基準,故分數是★池內相對值★,不是絕對召回品質。
"""
import argparse
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from retrieval_eval import ndcg_at_k, mrr, precision_at_k  # noqa: E402  ★單一實作來源★

ROOT = pathlib.Path(__file__).resolve().parents[2]
LUMOS = ROOT / "scripts" / "lumos"


def search_files(vault, query, any_terms):
    """回 [rel, ...] 依系統排序;空 = 該系統對此查詢什麼都沒回。"""
    args = [sys.executable, str(LUMOS), "--vault", str(vault), "search", query, "--files-only"]
    if any_terms:
        args.append("--any")
    r = subprocess.run(args, capture_output=True, text=True)
    out = []
    for ln in r.stdout.splitlines():
        ln = ln.strip()
        if ".md" in ln and ln.endswith(")"):
            out.append(ln.rsplit(" (", 1)[0])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True)
    ap.add_argument("--pool", required=True)
    ap.add_argument("--vault", required=True)
    ap.add_argument("-k", type=int, default=5)
    a = ap.parse_args()

    labels = json.loads(pathlib.Path(a.labels).read_text(encoding="utf-8"))
    pool = json.loads(pathlib.Path(a.pool).read_text(encoding="utf-8"))
    k = a.k

    print(f"=== 多詞回退量測(k={k};語料釘 {a.vault}) ===")
    rows = []
    for cid in sorted(pool):
        q = pool[cid]["query"]
        gold = labels.get(cid, {})
        # ★IDCG 基準=該題全部金標(不是取回集自證)★——否則「什麼都沒回」零懲罰,
        # 兩臂不在同一把尺(retrieval_eval 的 r1 panel s4 major 同一條)。
        all_rels = list(gold.values())
        n_rel = sum(1 for v in all_rels if v >= 1)

        base = search_files(a.vault, q, any_terms=False)
        fb = search_files(a.vault, q, any_terms=True)
        base_lab = [gold.get(x, 0) for x in base]
        fb_lab = [gold.get(x, 0) for x in fb]

        row = {
            "cid": cid, "query": q, "n_rel": n_rel,
            "base_n": len(base), "fb_n": len(fb),
            "base_ndcg": round(ndcg_at_k(base_lab, k, all_rels), 4),
            "fb_ndcg": round(ndcg_at_k(fb_lab, k, all_rels), 4),
            "base_mrr": round(mrr(base_lab), 4), "fb_mrr": round(mrr(fb_lab), 4),
            "base_p": round(precision_at_k(base_lab, k), 4),
            "fb_p": round(precision_at_k(fb_lab, k), 4),
            "top1": (fb[0] if fb else None),
            "top1_label": (gold.get(fb[0], 0) if fb else None),
        }
        rows.append(row)
        flag = "★" if row["top1_label"] == 0 else " "
        print(f"  {cid} {q:<20} 候選 {row['base_n']:>2}→{row['fb_n']:<3} "
              f"nDCG@{k} {row['base_ndcg']:.3f}→{row['fb_ndcg']:.3f}  "
              f"P@{k} {row['fb_p']:.2f}  {flag}top1={row['top1_label']}")

    n = len(rows)
    def mac(key):
        return round(sum(r[key] for r in rows) / n, 4) if n else 0.0
    print()
    print(f"[實驗組 n={n}] nDCG@{k}: 無回退={mac('base_ndcg')} 有回退={mac('fb_ndcg')}")
    print(f"  MRR: {mac('base_mrr')} → {mac('fb_mrr')} | P@{k}: {mac('base_p')} → {mac('fb_p')}")
    top1_good = sum(1 for r in rows if (r["top1_label"] or 0) >= 2)
    top1_any = sum(1 for r in rows if (r["top1_label"] or 0) >= 1)
    print(f"  ★第一名品質★:標 2(必看) {top1_good}/{n}｜標 ≥1(至少有用) {top1_any}/{n}")
    zero = [r["cid"] for r in rows if r["fb_ndcg"] == 0]
    if zero:
        print(f"  ★回退後仍 0 分的題★: {zero}")
    print()
    print("★誠實邊界★:候選池半數來自 --any 自己的 top-10(pooling bias),"
          "「更好的系統會找到但它沒找到」的節點可能不在池裡;"
          "第三來源(逐詞出現次數 top-3,不經 BM25F)是獨立來源但不完全乾淨。"
          "分數為★池內相對值★,非絕對召回品質。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
