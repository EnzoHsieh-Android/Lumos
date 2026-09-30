#!/opt/homebrew/bin/python3
"""唯讀參考實作:存量版的舊句檢查。把 m1 的「消失名稱」來源從「一次推送範圍」換成「量測點可達的全部非 merge 提交」,
其餘(程式檔判準、定義抽法、形狀過濾、終點語料、名稱正規化、先篩、逐行掃描、撤除節、句內歷史字眼)直接呼叫
本 repo 的 scripts/lumos 裡 m1 的函式(或 LUMOS_SCRIPT 指定的那一支)。

用法: oldnames_ref.py --repo <clone> --tip <sha> --vault <docs/x-knowledge> --out <prefix> [--workers 8]
產出: <prefix>.findings.jsonl(每行一筆發現,含 A/B 兩版判定)、<prefix>.gone.json(消失名稱與事件)、<prefix>.stats.json
不寫任何 repo;m1 的定義快取關掉(run.cache=None),不碰 ~/.cache。"""
import argparse
import collections
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor

# 預設用本 repo 的 scripts/lumos(本檔在 governance/eval/old-names/ 底下);要對別版本跑就設 LUMOS_SCRIPT
LUMOS = os.environ.get("LUMOS_SCRIPT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts", "lumos")
M = None


def load():
    global M
    if M is None:
        loader = importlib.machinery.SourceFileLoader("_lumos_inproc", LUMOS)
        spec = importlib.util.spec_from_loader("_lumos_inproc", loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        M = mod
    return M


def git(root, *a):
    return subprocess.run(["git", "-C", root, *a], capture_output=True, check=True).stdout


def new_run(root, base, tip, vault):
    """m1 的 run 物件;截止時間放很遠(不量時限),定義快取關掉。"""
    r = M._DriftM1Run(root, base, tip, vault, time.monotonic() + 10 ** 6, time.monotonic)
    r.cache = None
    r.res = M._drift_m1_new_res()
    return r


# ── 階段一:逐提交粗候選(平行,每個 worker 一段連續提交) ──

_W = {}


def _w_init(root, vault):
    load()
    _W["root"], _W["vault"] = root, vault
    _W["info"] = collections.OrderedDict()


def _w_chunk(pairs):
    """pairs=[(C, P)] → (事件 [(名稱, 類別 def|path, C, P, 起點路徑)], 歷史定義名集合, 剖不動清單, 秒數)。"""
    t0 = time.time()
    root, vault, info = _W["root"], _W["vault"], _W["info"]
    events, ever, unparsable = [], set(), []
    for c, p in pairs:
        run = new_run(root, p, c, vault)
        run.info = info                                  # 跨提交共用剖析結果(以內容編號為鍵,內容不變)
        changes = M._drift_m1_changes(run)
        coded = M._drift_m1_classify(run, changes)
        if coded:
            tf, tall, tl = run.listing(c)
            _bf, _ball, bl = run.listing(p)
            defs, paths = M._drift_m1_rough(run, coded, tl, bl, tall)
            for n, o in defs.items():
                for f in o:
                    events.append((n, "def", c, p, f))
            for n, o in paths.items():
                for f in o:
                    events.append((n, "path", c, p, f))
            # 「歷史上存在過」= 改到的 Python 檔在父提交那一版的定義名(m1 抽法)
            for st, path, k, bpy, _tpy in coded:
                if k == "py" and st != "A" and bpy:
                    bi = run.blob_info(run.spec(p, bl, path))
                    if bi[0] == "ast":
                        ever.update(*bi[1])
                    else:
                        ever.update(bi[2])
            unparsable += [(c, x) for x in run.res["unparsable"]]
        while len(info) > 300:
            info.popitem(last=False)
    return events, ever, unparsable, time.time() - t0


def history(root, tip, vault, workers):
    lines = git(root, "rev-list", "--no-merges", "--topo-order", "--parents", tip).decode().split("\n")
    order, pairs = {}, []
    for i, ln in enumerate(x for x in lines if x):
        parts = ln.split()
        order[parts[0]] = i                              # 0 = 最新
        if len(parts) == 2:
            pairs.append((parts[0], parts[1]))
    # 所有提交的拓撲序(含 merge),判「最後一次消失」用
    allc = git(root, "rev-list", "--topo-order", tip).decode().split()
    topo = {c: i for i, c in enumerate(allc)}
    pairs.reverse()                                      # 由舊到新,連續提交共用剖析結果
    n = max(1, workers)
    size = (len(pairs) + n * 4 - 1) // (n * 4) or 1
    chunks = [pairs[i:i + size] for i in range(0, len(pairs), size)]
    events, ever, unparsable, wsec = [], set(), [], 0.0
    with ProcessPoolExecutor(max_workers=n, initializer=_w_init, initargs=(root, vault)) as ex:
        for ev, e2, un, sec in ex.map(_w_chunk, chunks):
            events += ev
            ever |= e2
            unparsable += un
            wsec += sec
    return events, ever, unparsable, topo, len(pairs), len(allc), wsec


# ── 階段二:量測點 ──

def about_env(root, where, vault, cache):
    """那個提交的 {筆記: about_code 清單}(m1 的 _drift_m1_about 判法)。"""
    if where not in cache:
        env = M._drift_tree_env(root, where, vault)
        out = {}
        if env is not None:
            for rel, nn in env.notes.items():
                t = None if M._note_unreadable(nn) else M.env_text(env, rel)
                if t:
                    out[rel] = set(M._drift_m1_about(t))
        cache[where] = out
    return cache[where]


def blame_lines(root, tip, path, lines):
    """{行號: 提交} ;一次呼叫多個 -L。"""
    args = ["blame", "--porcelain"]
    for ln in sorted(set(lines)):
        args += ["-L", f"{ln},{ln}"]
    raw = git(root, *args, tip, "--", path).decode("utf-8", errors="replace").split("\n")
    out, cur = {}, None
    for r in raw:
        parts = r.split(" ")
        if len(parts) >= 3 and len(parts[0]) == 40 and all(ch in "0123456789abcdef" for ch in parts[0]):
            out[int(parts[2])] = parts[0]
    return out


_ANC = {}


def is_anc(root, a, b):
    key = (a, b)
    if key not in _ANC:
        _ANC[key] = subprocess.run(["git", "-C", root, "merge-base", "--is-ancestor", a, b]).returncode == 0
    return _ANC[key]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--vault", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    load()
    root = os.path.abspath(a.repo)
    tip = git(root, "rev-parse", a.tip).decode().strip()
    T = {}
    t0 = time.time()
    events, ever, unparsable, topo, n_pairs, n_all, wsec = history(root, tip, a.vault, a.workers)
    T["history_wall"] = time.time() - t0
    T["history_worker_sum"] = wsec

    # 每個名稱的消失事件 → 最後一次消失(拓撲序最新)
    by = collections.defaultdict(list)
    for n, kind, c, p, f in events:
        by[n].append((kind, c, p, f))
    t1 = time.time()
    run = new_run(root, None, tip, a.vault)
    tf, tall, tl = run.listing(tip)
    alive = M._drift_m1_corpus(run, tf, tl)
    tip_bases = {x.rsplit("/", 1)[-1] for x in tall}
    tall_set = set(tall)
    T["corpus"] = time.time() - t1

    gone, meta = {}, {}
    for n, evs in by.items():
        kinds = {e[0] for e in evs}
        # 定義名:量測點語料沒有(m1 的 _drift_m1_corpus);路徑名:完整路徑量測點不在、裸檔名量測點任何位置都沒有同名檔
        # (差異:m1 一次推送裡被刪的路徑一定不在終點,不必再查;存量版可能後來又加回來)
        keep = ("def" in kinds and n not in alive) or \
               ("path" in kinds and ((("/" in n) and n not in tall_set) or ("/" not in n and n not in tip_bases)))
        if not keep:
            continue
        last = min(evs, key=lambda e: topo.get(e[1], 10 ** 9))
        gone[n] = {e[3] for e in evs}
        meta[n] = {"kinds": sorted(kinds), "vanish": last[1], "last_had": last[2],
                   "origins": sorted({e[3] for e in evs}), "n_events": len(evs),
                   "events": sorted({(e[1], e[3]) for e in evs}, key=lambda x: topo.get(x[0], 0))[:20]}
    names = {n: o for n, o in gone.items() if M._drift_m1_name_canon(n) is not None}

    t2 = time.time()
    env = M._drift_tree_env(root, tip, a.vault)
    texts = {r: M.env_text(env, r) for r, nn in env.notes.items() if not M._note_unreadable(nn)}
    idx = M._drift_m1_name_index(M._drift_m1_prefilter(names, [t for t in texts.values() if t], run.check_time),
                                 run.check_time)
    run.res = M._drift_m1_new_res()
    for rel in sorted(texts):
        if texts[rel]:
            M._drift_m1_scan_note(run, rel, texts[rel], idx, names, set())
    T["scan"] = time.time() - t2

    # 層:摘要行(scan 已判)或那個名稱的起點檔的家(量測點、消失提交、消失提交的父提交三個樹任一邊 about_code 列了它)
    t3 = time.time()
    acache = {}
    tip_about = about_env(root, tip, a.vault, acache)
    rows = []
    for f in run.res["handle"] + run.res["listed"]:
        f = dict(f)
        f["layer_reason"] = "summary" if f["layer"] == "handle" else None
        if f["layer"] != "handle":
            for n in f["names"]:
                mm = meta[n]
                for where in (tip, mm["vanish"], mm["last_had"]):
                    ab = tip_about if where == tip else about_env(root, where, a.vault, acache)
                    if ab.get(f["path"], set()) & set(mm["origins"]):
                        f["layer"], f["layer_reason"] = "handle", f"home@{where[:8]}:{n}"
                        break
                if f["layer"] == "handle":
                    break
        f["meta"] = {n: {k: meta[n][k] for k in ("kinds", "vanish", "last_had", "origins")} for n in f["names"]}
        rows.append(f)
    T["homes"] = time.time() - t3

    # 變體 B:那一行的 blame 提交是名稱消失提交的嚴格祖先
    t4 = time.time()
    byfile = collections.defaultdict(list)
    for f in rows:
        byfile[f["path"]].append(f["line"])
    bl = {}
    for rel, lns in byfile.items():
        bl[rel] = blame_lines(root, tip, a.vault.rstrip("/") + "/" + rel, lns)
    for f in rows:
        x = bl[f["path"]].get(f["line"])
        f["blame"] = x
        f["B_names"] = [n for n in f["names"] if x and x != meta[n]["vanish"] and is_anc(root, x, meta[n]["vanish"])]
        f["B"] = bool(f["B_names"])
    T["blame"] = time.time() - t4
    T["total"] = time.time() - t0

    with open(a.out + ".findings.jsonl", "w") as fh:
        for f in rows:
            fh.write(json.dumps(f, ensure_ascii=False) + "\n")
    json.dump({n: meta[n] for n in sorted(gone)}, open(a.out + ".gone.json", "w"), ensure_ascii=False, indent=1)
    st = {
        "tip": tip, "commits_all": n_all, "nonmerge_with_parent": n_pairs, "events": len(events),
        "ever_defs": len(ever), "rough_names": len(by), "alive": len(alive), "gone": len(gone),
        "gone_def": sum(1 for n in gone if "def" in meta[n]["kinds"]),
        "gone_path_only": sum(1 for n in gone if meta[n]["kinds"] == ["path"]),
        "names_canon": len(names), "notes": len(texts),
        "A_handle": sum(1 for f in rows if f["layer"] == "handle"),
        "A_listed": sum(1 for f in rows if f["layer"] != "handle"),
        "A_handle_summary": sum(1 for f in rows if f["layer_reason"] == "summary"),
        "B_handle": sum(1 for f in rows if f["B"] and f["layer"] == "handle"),
        "B_listed": sum(1 for f in rows if f["B"] and f["layer"] != "handle"),
        "unparsable_events": len(unparsable), "unparsable_files": sorted({x for _c, x in unparsable}),
        "long_lines": run.res["long_lines"], "long_other": run.res["long_other"],
        "text_defs_tip": run.res["text_defs"], "times_sec": {k: round(v, 1) for k, v in T.items()},
    }
    json.dump(st, open(a.out + ".stats.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(st, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
