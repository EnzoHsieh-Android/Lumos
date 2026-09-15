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
import stat
import subprocess
import tempfile
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
    # ★也吃「題庫外殼」那種形狀★:合併與寫回兩步沿用既有的標註工具,而那支要求檔案
    # 有 labels / search / edit 三個鍵(search 與 edit 在這裡是空的——本題庫的題目存在
    # 候選池檔裡)。沿用而不自己再寫一份,是因為那支帶著寫入鎖、原子寫入,以及
    # 「還有人裁沒填就不准寫」那道閘;自己重寫一份等於把那三樣一起重寫。
    if isinstance(raw, dict) and "labels" in raw and isinstance(raw["labels"], dict):
        raw = raw["labels"]
    out = {}
    for cid, per_node in raw.items():
        if not isinstance(per_node, dict):
            print(f"ERROR: 標註檔 {path} 的 {cid} 不是「節點→分數」的對應,讀不下去", file=sys.stderr)
            raise SystemExit(2)
        flat = {}
        for node, v in per_node.items():
            if isinstance(v, dict):
                if "final" not in v:
                    print(f"ERROR: 標註檔 {path} 的 {cid} / {node} 是含各評審意見的格式,"
                          f"但裡面沒有最終分那一欄,無法取用", file=sys.stderr)
                    raise SystemExit(2)
                v = v["final"]
            if v is None:
                continue          # 未裁決:當成沒標,不當 0 分
            # 值的型別要驗(r1 邊界席:字串型分數會在算分深處拋 TypeError,訊息看不懂)
            if isinstance(v, bool) or not isinstance(v, int):
                print(f"ERROR: 標註檔 {path} 的 {cid} / {node} 分數是 {v!r},"
                      f"要的是整數 0/1/2", file=sys.stderr)
                raise SystemExit(2)
            if v not in (0, 1, 2):
                print(f"ERROR: 標註檔 {path} 的 {cid} / {node} 分數是 {v},"
                      f"只接受 0(不相干)/1(有用)/2(必看)", file=sys.stderr)
                raise SystemExit(2)
            flat[node] = v
        out[cid] = flat
    return out


def search_hits(vault, query, any_terms=False):
    """回 {節點: 命中次數}——★語意完全由搜尋自己決定,這支不再自己判斷什麼算命中★。

    2026-09-15 代碼審 r1 四席各自抓到同一個根因:原本這裡自己掃原始 Markdown
    做 `q in txt`,而真正的搜尋做的是另一套。實測三處不一致,每一處都會讓結果錯:
      ①搜尋不分大小寫,原本的比對分——大小寫不同的污染漏擋
      ②搜尋預設排除程式碼區塊、行內程式碼與作廢節點,原本的比對全都算進去
        ——只出現在範例指令裡的字串會被誤判成污染,而本工具的文件慣例正好
        就是用程式碼區塊寫查詢範例
      ③中文重疊命中:Python 的 count 對「哈哈哈」數「哈哈」只回 1,實際有兩處
    所以改成問搜尋,不自己算。附帶好處是不必把整個語料讀進記憶體。
    """
    args = [sys.executable, str(LUMOS), "--vault", str(vault), "search", query, "--files-only",
            "--any" if any_terms else "--no-any"]
    r = subprocess.run(args, capture_output=True, text=True)
    out = {}
    for ln in r.stdout.splitlines():
        ln = ln.strip()
        if ".md" not in ln or not ln.endswith(")"):
            continue
        node, _, cnt = ln.rpartition(" (")
        try:
            out[node] = int(cnt[:-1])
        except ValueError:
            out[node] = 1
    return out


def contaminated(vault, pool):
    """回 [(題號, 查詢, [搜尋撈得到這串片語的筆記])] ——查詢字面在語料裡查得到的題。

    ★為什麼要檢查★(Issues/評測題目寫進圖譜就毀掉那一題):圖譜本身就是這套評測的
    語料。查詢字串一旦寫進任何一篇筆記,「整串當片語查」那一臂就有命中,
    拆詞那一臂便不觸發(它只在整串無命中時啟動),兩臂結果一模一樣、測不到
    任何東西,而且不會有任何錯誤訊息。2026-09-15 查出十題裡三題已被污染,
    其中兩題是被這套評測自己的設計文件寫進去的,壞了一個多月沒人發現。

    ★判準就是搜尋自己的判準★:問它「這串片語查不查得到」,查得到就是污染。
    """
    bad = []
    for cid in sorted(pool):
        q = pool_query(pool, cid)
        hits = sorted(search_hits(vault, q, any_terms=False))
        if hits:
            bad.append((cid, q, hits))
    return bad


def pool_query(pool, cid):
    """取一題的查詢字串,形狀不對就講人話再結束(r1 邊界席:原本會拋 KeyError 看不懂)。"""
    item = pool.get(cid)
    if not isinstance(item, dict) or not isinstance(item.get("query"), str) or not item["query"].strip():
        print(f"ERROR: 題庫裡 {cid} 這一題沒有可用的查詢字串,題庫檔壞了", file=sys.stderr)
        raise SystemExit(2)
    return item["query"]


def rebuild_pool(vault, pool_old):
    """重組候選池:三個來源聯集,其中兩個不經排序器。

    來源一 拆詞那一臂的前 10——現行系統自己撈到的。
    來源二 每個詞各自命中次數最多的前 3 篇——不經排序器,但命中判準問搜尋。
    來源三 所有詞都命中的篇,依「命中次數最少的那個詞」取前 10——同樣不經排序器。
    ★編號以這裡為準★(2026-09-15 r2 外家否決席:結尾那段誠實邊界原本把「逐詞前 3」
    叫成第三來源,跟這裡對不上,看輸出的人會拿到錯的偏差說明)。
           ★2026-09-15 新增,但不要把它說得太滿★(r2 外家否決席訂正):它減輕的是
           「只標到現行排序器排前面的那批」,★不是★「更好的系統找得到的都會進池」——
           三個來源都以同一組查詢字面為入口,靠同義詞或圖關係才找得到的節點還是不會進。
           要跟另一個系統比,仍然必須把那個系統的輸出併進池再補標。

    池的順序打散(固定亂數種子,同一份輸入每次結果一樣)——標註的人不該看到名次。
    """
    out = {}
    for cid in sorted(pool_old):
        q = pool_query(pool_old, cid)
        terms = q.split()
        if not terms:
            print(f"ERROR: 題庫裡 {cid} 這一題的查詢拆不出任何詞,題庫檔壞了", file=sys.stderr)
            raise SystemExit(2)
        per_term = {t: search_hits(vault, t, any_terms=False) for t in terms}

        s1 = list(search_hits(vault, q, any_terms=True))[:10]
        s2 = []
        for t in terms:
            h = per_term[t]
            s2 += [k for k, _ in sorted(h.items(), key=lambda kv: (-kv[1], kv[0]))[:3]]
        s2 = list(dict.fromkeys(s2))
        common = set.intersection(*[set(h) for h in per_term.values()]) if per_term else set()
        s3 = [k for k, _ in sorted(((k, min(per_term[t].get(k, 0) for t in terms)) for k in common),
                                   key=lambda kv: (-kv[1], kv[0]))[:10]]

        pool = list(dict.fromkeys(s1 + s2 + s3))
        rnd = random.Random(hashlib.sha256((q + POOL_SALT).encode("utf-8")).hexdigest())
        rnd.shuffle(pool)
        out[cid] = {"query": q, "pool": pool,
                    "n_any": len(s1), "n_term": len(s2), "n_cooccur": len(s3),
                    "n_pool": len(pool)}
    return out


def write_json_atomic(path, data):
    """先寫暫存再換名,★暫存檔名不可預測、不跟著符號連結、換名保留原權限★。

    2026-09-15 代碼審 r1(資安席實跑、架構對齊席、邊界席、外家席各自抓到):
    原本用固定的「<輸出>.tmp」,三個後果都實測重現過——
      ①資安席先把那個固定名字建成指向別的檔的符號連結,再跑一次重組:
        受害檔被整個覆寫,而工具印的是成功
      ②兩個行程同時寫同一個輸出:一方 os.replace 時暫存檔已被對方換走,拋
        FileNotFoundError;另一方靜默獲勝,沒有任何訊息說前一份不見了
      ③覆寫既有檔時權限被暫存檔的新建權限取代(實測 600 變 644)
    這個 repo 已經為同一個反模式付過兩次學費(標註刷新那支、主程式那支),
    兩處的正解都是不可預測的暫存名。這裡照做:用 mkstemp(O_EXCL、不跟連結),
    並在目標檔已存在時把它的權限抄過來。
    """
    path = pathlib.Path(path)
    if path.parent and not path.parent.is_dir():
        print(f"ERROR: 輸出目錄不存在,寫不了 {path}", file=sys.stderr)
        raise SystemExit(2)
    # ★只有目標是普通檔才抄它的權限★(2026-09-15 r2 資安席實測:目標若是預先埋好的
    # 符號連結,讀到的是連結自己那組幾乎全開的位元,抄過來會讓產出的檔在某些系統上
    # 變成全世界可寫,而且照印成功。內容不會被寫穿(換名是整個替換不解參照),
    # 被放寬的是權限)。
    mode = None
    try:
        st = os.stat(path, follow_symlinks=False)
        if stat.S_ISREG(st.st_mode):
            mode = st.st_mode & 0o777
    except OSError:
        pass
    fd, tmp = tempfile.mkstemp(dir=str(path.parent or "."), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1)
            fh.flush()
            os.fsync(fh.fileno())
        if mode is not None:
            os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_inputs(vault, pool_path):
    """驗語料路徑與題庫檔,過了回題庫、不過印原因回 None(呼叫端回退出碼 2)。

    抽成獨立一支是因為新增告警閘判 main 太複雜(2026-09-15 推送前擋下);
    這幾道檢查本來就是一組「進場前先驗輸入」,放在一起也比較好讀。
    每一道的出身見 t_mw_bad_input_says_what_is_wrong 的說明。
    """
    vp = pathlib.Path(vault)
    if not vp.is_dir():
        print(f"ERROR: 語料目錄不存在或不是目錄:{vault}", file=sys.stderr)
        return None
    if not any(vp.rglob("*.md")):
        print(f"ERROR: 語料目錄裡一篇筆記都沒有:{vault}——路徑是不是指錯了?", file=sys.stderr)
        return None
    try:
        pool = json.loads(pathlib.Path(pool_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as ex:
        print(f"ERROR: 題庫檔讀不進來({ex});要的是一份「題號→{{query, pool}}」的 JSON", file=sys.stderr)
        return None
    if not isinstance(pool, dict) or not pool:
        print("ERROR: 題庫檔的形狀不對:要一份題號對應題目的 JSON 物件,而且不能是空的", file=sys.stderr)
        return None
    return pool


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", help="標註檔;量測時必填,只重組候選池時不用")
    ap.add_argument("--pool", required=True)
    ap.add_argument("--vault", required=True)
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--rebuild-pool", metavar="出檔",
                    help="重組候選池寫到這個檔,然後結束;★不量測、不碰標註★")
    ap.add_argument("--allow-contaminated", action="store_true",
                    help="★明知有題目被污染仍要跑量測★:分數會含測不到東西的題,只在刻意重現舊結果時用")
    a = ap.parse_args()

    pool = load_inputs(a.vault, a.pool)
    if pool is None:
        return 2

    # ★污染檢查,兩條路徑都擋★:查詢字面查得到,拆詞那一臂就不會啟動。
    bad = contaminated(a.vault, pool)
    if bad:
        print("這幾題的查詢在語料裡查得到,拆詞那一臂不會啟動,兩臂會量出一樣的數字:",
              file=sys.stderr)
        for cid, q, hits in bad:
            print(f"  {cid} 「{q}」 ← 查得到它的筆記:{', '.join(hits)}", file=sys.stderr)
        print("  為什麼在意:那一題從此測不到任何東西,而且不會有錯誤訊息,"
              "數字看起來正常、其實是兩臂相同。", file=sys.stderr)
        print("  處置:把那幾篇筆記裡的查詢改成用斜線分隔(像「圖譜／同步／閘」),"
              "查詢字面只留在題庫檔裡。", file=sys.stderr)
        # ★量測路徑一樣要擋★(2026-09-15 r1 資安席與正確性席各自抓到):
        # 原本只在重組時擋,量測時只印 stderr 就照算,把 stderr 丟掉就看不出來——
        # 而量測正是產出治理數字的那條路,漏在這裡等於守衛沒有守到要守的東西。
        # ★重組候選池一律不接受污染,逃生旗標對它無效★(2026-09-15 r2 折入驗收席實測:
        # 原本兩條路共用同一道閘,加了旗標連重組都照組,而且★把造成污染的那篇筆記
        # 收進池裡★——那等於把壞掉的題目烤進資料,後面每一次量測都繼承)。
        # 量測那條留逃生口是為了重現舊結果,重組沒有這種需要。
        if a.rebuild_pool:
            print("  ★重組候選池不接受污染,也不吃 --allow-contaminated★:改乾淨再跑一次。",
                  file=sys.stderr)
            return 2
        if not a.allow_contaminated:
            print("  ★這一輪不跑★:改乾淨再來;真的要拿污染的題跑(例如重現舊結果),"
                  "明著加 --allow-contaminated。", file=sys.stderr)
            return 2
        # ★用了逃生旗標就要留在報告本體裡★(2026-09-15 r2 資安席:原本警告只印在
        # 錯誤輸出,標準輸出跟乾淨結果一字不差,事後從報告完全看不出來——
        # 遇到擋就加旗標讓它變綠,是同等級的審計盲點)。
        print("★★★ 這份結果是在允許污染的情況下跑的,不得當成證據 ★★★")
        for cid, q, _h in bad:
            print(f"    受影響的題:{cid}「{q}」——它的兩臂量出來是一樣的")
        print()

    if a.rebuild_pool:
        newpool = rebuild_pool(a.vault, pool)
        write_json_atomic(a.rebuild_pool, newpool)
        tot = sum(v["n_pool"] for v in newpool.values())
        print(f"✓ 候選池重組好了:{len(newpool)} 題、共 {tot} 筆候選 → {a.rebuild_pool}")
        for cid in sorted(newpool):
            v = newpool[cid]
            print(f"  {cid} {v['query']:<20} 池 {v['n_pool']:>3} 筆"
                  f"(拆詞臂前10 {v['n_any']}、逐詞前3 {v['n_term']}、全詞同篇前10 {v['n_cooccur']})")
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
        # ★沒標過 ≠ 判過不相干★(r1 正確性席:兩者在算分時都變成 0,承諾的區分沒有實效)。
        # 算分沿用 0(改成別的會讓這把尺跟姊妹工具不同口徑),但★把沒標過的數出來★,
        # 下面會逐題印,並在整體結果標成弱證據——不讓它靜靜地被當成「判過不相干」。
        n_unjudged = sum(1 for x in fb[:k] if x not in gold)

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
            "n_unjudged": n_unjudged,
        }
        rows.append(row)
        unj = f"  ★前{k}名有 {n_unjudged} 筆沒標過(當 0 分算,分數被低估)★" if n_unjudged else ""
        flag = "★" if row["top1_label"] == 0 else " "
        print(f"  {cid} {q:<20} 候選 {row['base_n']:>2}→{row['fb_n']:<3} "
              f"nDCG@{k} {row['base_ndcg']:.3f}→{row['fb_ndcg']:.3f}  "
              f"P@{k} {row['fb_p']:.2f}  {flag}top1={row['top1_label']}{unj}")

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
        # 迴圈變數不要叫 n(r1 正確性席:會遮蔽上面算平均用的題數;目前呼叫順序下
        # 不影響輸出,但之後在這個迴圈後面再加統計就會靜默算錯分母)
        for cid, n_cand in zero:
            print(f"      {cid}(候選 {n_cand} 筆,不是沒撈到,是撈到的前幾名沒一個被標成相關)")
        print("      可能是排序沒把對的推上來,★也可能是這些候選根本還沒標過★——"
              "標註如果比語料舊,沒標的一律當 0 分,看起來就會像排序爛掉。先確認標註是不是最新的。")
    tot_unj = sum(r["n_unjudged"] for r in rows)
    if tot_unj:
        print()
        print(f"  ★弱證據★:計分視窗裡有 {tot_unj} 筆候選從來沒標過,算分時一律當 0 分。")
        print("      「沒標過」跟「判過不相干」在分數上分不出來,所以上面的分數是★被低估的下限★,")
        print("      不得拿來判「退步」。要有結論就先補標(把新撈上來的候選標完再跑一次)。")
    print()
    print("★誠實邊界★:分數是★池內相對值★,不是絕對召回品質。")
    print("  候選池三個來源:拆詞那一臂的前 10、每個詞各自命中最多的前 3、所有詞都命中的前 10。")
    print("  ★三個來源都以同一組查詢字面為入口★(2026-09-15 代碼審 r2 外家否決席訂正:"
          "前一版把後兩個來源說成解決了跨系統的取樣偏差,那句話說得太滿)。")
    print("  ★所以這把尺只比得了「現在這兩臂」★:靠同義詞、別名或圖關係才找得到、"
          "但不含這些字面的節點,永遠不會進池、也永遠不會被標;")
    print("  換一個系統來比之前,要先把那個系統的輸出併進池、把新增的標完,"
          "否則它找到的好東西會被當成 0 分。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
