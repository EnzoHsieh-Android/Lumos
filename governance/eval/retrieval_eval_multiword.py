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
import hashlib
import json
import os
import pathlib
import random
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from retrieval_eval import ndcg_at_k, mrr, precision_at_k  # noqa: E402  ★單一實作來源★

ROOT = pathlib.Path(__file__).resolve().parents[2]
LUMOS = ROOT / "scripts" / "lumos"


def search_files(vault, query, any_terms):
    """回 [rel, ...] 依系統排序;空 = 該系統對此查詢什麼都沒回。

    ★對照臂必須★顯式★傳 --no-any,不能只是「不加 --any」★(2026-08-03 code-loop r1,
    slot4 與 Codex 兩席獨立抓到,皆附實測):本工具寫成的當下回退還是預設關,那時
    「不加旗標」==「關掉回退」;同一份 diff 把預設翻開之後,★對照臂會靜默繼承新預設★,
    兩臂都變成有回退,量出來是「有回退 vs 有回退」——而這支工具存在的唯一理由就是
    量那個差異,它會對自己要量的東西視而不見。
    實測對照:修前跑同一份語料印「候選 2→2、nDCG 0.860→0.860」(兩臂相同),
    而翻預設★之前★跑出的歷史存證是「候選 0→80」。
    ★通則:翻預設時,所有「靠不傳旗標來表示舊行為」的呼叫端都是待修清單★。
    """
    args = [sys.executable, str(LUMOS), "--vault", str(vault), "search", query, "--files-only"]
    args.append("--any" if any_terms else "--no-any")
    r = subprocess.run(args, capture_output=True, text=True)
    out = []
    for ln in r.stdout.splitlines():
        ln = ln.strip()
        if ".md" in ln and ln.endswith(")"):
            out.append(ln.rsplit(" (", 1)[0])
    return out


POOL_SALT = "lumos-mw-pool-v1"


def load_labels(path):
    """標註檔兩種格式都吃:扁平({節點: 分數})與含各評審意見({節點: {final, ...}})。

    ★2026-09-15 修(Issues/多詞評測吃錯標註檔直接拋例外)★:原本只吃扁平那份,
    餵含各評審意見那份會在算相關數時拿字典去跟數字比大小,直接拋 TypeError,
    而訊息完全沒提到是檔案拿錯——同一個目錄裡兩份檔名只差一個字。
    """
    raw = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    out = {}
    for cid, per_node in raw.items():
        if not isinstance(per_node, dict):
            raise SystemExit(f"ERROR: 標註檔 {path} 的 {cid} 不是「節點→分數」的對應,讀不下去")
        flat = {}
        for node, v in per_node.items():
            if isinstance(v, dict):
                if "final" not in v:
                    raise SystemExit(
                        f"ERROR: 標註檔 {path} 的 {cid} / {node} 是含各評審意見的格式,"
                        f"但裡面沒有最終分那一欄,無法取用")
                v = v["final"]
            if v is None:
                continue          # 未裁決:當成沒標,不當 0 分
            flat[node] = v
        out[cid] = flat
    return out


def contaminated(vault, pool):
    """回 [(題號, 查詢, [逐字含這串的筆記])] ——查詢字面出現在語料裡的題。

    ★為什麼要檢查★(Issues/評測題目寫進圖譜就毀掉那一題):圖譜本身就是這套評測的
    語料。查詢字串一旦逐字寫進任何一篇筆記,「整串當片語查」那一臂就有命中,
    拆詞那一臂便不觸發(它只在整串全庫零命中時啟動),兩臂結果一模一樣、測不到
    任何東西,而且不會有任何錯誤訊息。2026-09-15 查出十題裡三題已被污染,
    其中兩題是被這套評測自己的設計文件寫進去的,壞了一個多月沒人發現。
    """
    vp = pathlib.Path(vault)
    docs = {}
    for f in vp.rglob("*.md"):
        try:
            docs[str(f.relative_to(vp))] = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    bad = []
    for cid in sorted(pool):
        q = pool[cid]["query"]
        hits = sorted(n for n, txt in docs.items() if q in txt)
        if hits:
            bad.append((cid, q, hits))
    return bad, docs


def rebuild_pool(vault, pool_old, docs):
    """重組候選池:三個來源聯集,其中兩個不經排序器。

    來源一 拆詞那一臂的前 10——現行系統自己撈到的。
    來源二 每個詞各自出現次數最多的前 3 篇——只數字面出現次數,不經排序器。
    來源三 三個詞全都出現在同一篇、依「最少的那個詞出現幾次」取前 10——同樣不經排序器。
           ★2026-09-15 新增★:前兩個來源合起來仍有一半來自現行系統,
           「更好的系統會找到、而現行系統沒找到」的節點不在池裡就永遠標不到,
           量出來會讓新系統看起來更差(與本專案已踩過四次的「拿不同批互比」同一族)。

    池的順序打散(固定亂數種子,同一份輸入每次結果一樣)——標註的人不該看到名次。
    """
    def term_top(term, n=3):
        c = {k: v.count(term) for k, v in docs.items()}
        return [k for k, _ in sorted(((k, v) for k, v in c.items() if v),
                                     key=lambda kv: (-kv[1], kv[0]))[:n]]

    def cooccur_top(terms, n=10):
        sc = {}
        for k, v in docs.items():
            cs = [v.count(t) for t in terms]
            if all(cs):
                sc[k] = min(cs)
        return [k for k, _ in sorted(sc.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]

    out = {}
    for cid in sorted(pool_old):
        q = pool_old[cid]["query"]
        terms = q.split()
        s1 = search_files(vault, q, any_terms=True)[:10]
        s2 = list(dict.fromkeys(sum([term_top(t) for t in terms], [])))
        s3 = cooccur_top(terms)
        pool = list(dict.fromkeys(s1 + s2 + s3))
        rnd = random.Random(hashlib.sha256((q + POOL_SALT).encode("utf-8")).hexdigest())
        rnd.shuffle(pool)
        out[cid] = {"query": q, "pool": pool,
                    "n_any": len(s1), "n_term": len(s2), "n_cooccur": len(s3),
                    "n_pool": len(pool)}
    return out


def write_json_atomic(path, data):
    """先寫暫存再換名——中途中斷不會在樹上留下半份檔(改共用檔的家規)。"""
    path = pathlib.Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", help="標註檔;量測時必填,只重組候選池時不用")
    ap.add_argument("--pool", required=True)
    ap.add_argument("--vault", required=True)
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--rebuild-pool", metavar="出檔",
                    help="重組候選池寫到這個檔,然後結束;★不量測、不碰標註★")
    a = ap.parse_args()

    pool = json.loads(pathlib.Path(a.pool).read_text(encoding="utf-8"))

    # ★污染檢查,兩條路徑都先跑★:查詢字面出現在語料裡,拆詞那一臂就不會啟動。
    bad, docs = contaminated(a.vault, pool)
    if bad:
        print("這幾題的查詢字面已經出現在語料裡,拆詞那一臂不會啟動,兩臂會量出一樣的數字:",
              file=sys.stderr)
        for cid, q, hits in bad:
            print(f"  {cid} 「{q}」 ← 出現在 {', '.join(hits)}", file=sys.stderr)
        print("  為什麼在意:那一題從此測不到任何東西,而且不會有錯誤訊息,"
              "數字看起來正常、其實是兩臂相同。", file=sys.stderr)
        print("  處置:把那幾篇筆記裡的查詢改成用斜線分隔(像「圖譜／同步／閘」),"
              "查詢字面只留在題庫檔裡。", file=sys.stderr)
        if a.rebuild_pool:
            print("  ★重組候選池時不接受污染★:改乾淨再跑一次。", file=sys.stderr)
            return 2

    if a.rebuild_pool:
        newpool = rebuild_pool(a.vault, pool, docs)
        write_json_atomic(a.rebuild_pool, newpool)
        tot = sum(v["n_pool"] for v in newpool.values())
        print(f"✓ 候選池重組好了:{len(newpool)} 題、共 {tot} 筆候選 → {a.rebuild_pool}")
        for cid in sorted(newpool):
            v = newpool[cid]
            print(f"  {cid} {v['query']:<20} 池 {v['n_pool']:>3} 筆"
                  f"(拆詞臂前10 {v['n_any']}、逐詞前3 {v['n_term']}、三詞同篇前10 {v['n_cooccur']})")
        print("  接下來要標註:池裡每一筆都要判「對這個查詢有多相關」,"
              "走既有的雙評審加人裁,標完才量得出分數。")
        return 0

    if not a.labels:
        print("ERROR: 量測要有標註檔,請帶 --labels(只想重組候選池就帶 --rebuild-pool)",
              file=sys.stderr)
        return 2
    labels = load_labels(a.labels)
    k = a.k

    print(f"=== 中文多詞查詢的「0 筆回退」量測(整串查無 → 拆詞 OR 再查;語料釘 {a.vault}) ===")
    print(f"  每行:題號 查詢 | 候選數 無回退→有回退 | 排序品質 nDCG@{k} 無→有 | 前 {k} 名對的比例 | 第一名的標註(2=必看/1=有用/0=不相干,★=第一名不相干)")
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
    print(f"整體({n} 題,原本整串查是 0 筆的那種):")
    print(f"  排序品質 nDCG@{k}:無回退 {mac('base_ndcg')} → 有回退 {mac('fb_ndcg')}    ← 回退有沒有把對的撈回來、還排得前")
    print(f"  第一個對的答案多靠前(MRR):{mac('base_mrr')} → {mac('fb_mrr')}  |  前 {k} 名對的比例:{mac('base_p')} → {mac('fb_p')}")
    top1_good = sum(1 for r in rows if (r["top1_label"] or 0) >= 2)
    top1_any = sum(1 for r in rows if (r["top1_label"] or 0) >= 1)
    print(f"  第一名的品質:{top1_good}/{n} 題第一名就是必看、{top1_any}/{n} 題第一名至少有用(剩下的第一名是雜訊)")
    # ★訊息講錯過一次(2026-09-15)★:原本寫「回退了還是一篇都撈不到」,
    # 但 nDCG 為 0 是「前幾名裡沒有標成相關的」,不是「沒有候選」——那幾題各有
    # 三四百個候選。照原訊息會把「標註過期」誤判成「分詞救不了」,我自己就誤判了一次。
    zero = [(r["cid"], r["fb_n"]) for r in rows if r["fb_ndcg"] == 0]
    if zero:
        print("  ★拆詞之後前幾名裡一個標成相關的都沒有的題★:")
        for cid, n in zero:
            print(f"      {cid}(候選 {n} 筆,不是沒撈到,是撈到的前幾名沒一個被標成相關)")
        print("      可能是排序沒把對的推上來,★也可能是這些候選根本還沒標過★——"
              "標註如果比語料舊,沒標的一律當 0 分,看起來就會像排序爛掉。先確認標註是不是最新的。")
    print()
    print("★誠實邊界★:候選池半數來自 --any 自己的 top-10(pooling bias),"
          "「更好的系統會找到但它沒找到」的節點可能不在池裡;"
          "第三來源(逐詞出現次數 top-3,不經 BM25F)是獨立來源但不完全乾淨。"
          "分數為★池內相對值★,非絕對召回品質。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
