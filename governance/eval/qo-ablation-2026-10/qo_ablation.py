#!/usr/bin/env python3
"""情境出題對照實驗的執行與計分器(預先登記:同目錄 preregistration.md)。

子命令(照順序跑):
  run       交錯執行:每個(題目, 第幾次)甲乙各跑一場,先後由固定種子決定;已有有效結果且版本相符的場次跳過
  score     機械計分:先寫程式、截斷、gold 正規式輔助指標
  packets   盲評包:隱去受測者、組別、場次並打亂,遮掉回答裡自報的身分與組別路徑;對照表另存
  agree     兩位評分員:嚴格檢查完整性後算 kappa,列出要仲裁的分歧
  adj-pack  把分歧做成仲裁包(不標哪個標籤來自誰)
  merge     合併兩位評分員與仲裁結果,得到最終標籤
  final     主指標與無效條件,逐受測者給 PASS / FAIL / INCONCLUSIVE,另報各評分員單獨判的敏感度

只用標準庫。算法照預先登記,改算法要先改預先登記。
"""
import argparse
import hashlib
import itertools
import json
import random
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
PROBE = REPO / "scripts" / "scenario_probe.py"
ANSWER_MAX = 20000
LABELS = ("handed", "assumed_confirm", "absent")   # 交給人決定 / 自己假設但請人確認 / 沒提或自己定了
N_GOLD = 6
NOISE_SCENARIOS = {"qo-P1", "qo-P2", "qo-P3", "qo-P6"}

# ── 先寫程式(預先登記〈指標〉第 3 條)──────────────────────────────────────────
_CODE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit", "apply_patch", "file_change"}
_SHELL_WRITE_V1 = re.compile(
    r"(?:^|[;&|]\s*)(?:touch|tee|cp|mv|install)\s|"
    r"(?<![0-9&])>>?\s*(?!/dev/null)[\w./-]+|"
    r"<<\s*['\"]?\w+|"
    r"open\([^)]*['\"]w|write_text\(|"
    r"\bsed\s+(?:-[a-zA-Z]*i|--in-place)|\bperl\s+-[a-zA-Z]*i|"
    r"\b(?:gradle|gradlew|mvn|mvnw)\b(?!\s+--version)|spring\s+init|start\.spring\.io|"
    r"\bgit\s+apply\b|\bnpm\s+init\b|mkdir\s+-p\s+src\b")
# 第 2 版(2026-10-12 實跑後):建置工具只在指令位置(行首、; && || | 之後)才算執行;
# 第 1 版把 grep 搜尋字串裡的 gradle 也算進去(Claude 乙組 P3 第 3 次誤判)。兩版並列報告。
_SHELL_WRITE = re.compile(_SHELL_WRITE_V1.pattern.replace(r"\b(?:gradle|gradlew|mvn|mvnw)\b(?!\s+--version)|", ""))
_BUILD_CMD = re.compile(r"(?:^|[;&|]\s*)(?:\./)?(?:gradle|gradlew|mvn|mvnw)\b(?!\s+--version)")
_QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")


def _shell_writes_v2(cmd):
    """第 2 版:建置工具要在去掉引號字串後、出現在指令位置才算。"""
    return bool(_SHELL_WRITE.search(cmd) or _BUILD_CMD.search(_QUOTED.sub("''", cmd)))


_PATH_TOKEN = re.compile(r"(?<![\w/])(?:[\w.-]+/)+[\w.-]+|[\w-]+\.\w{1,8}\b")


def _is_doc(path):
    p = path.strip().strip("'\"")
    return p.endswith(".md") or "/docs/" in f"/{p}" or p.startswith("docs/")


def code_start(calls, shell_re=None):
    match = (lambda c: bool(shell_re.search(c))) if shell_re else _shell_writes_v2
    for name, summ in calls:
        if name in _CODE_TOOLS:
            paths = [x for x in re.split(r"[\s,]+", summ or "") if x]
            if any(not _is_doc(x) for x in paths):   # 一次改多檔:任一支不是文件就算
                return True
        if name in ("Bash", "exec_command", "shell") and match(summ or ""):
            paths = _PATH_TOKEN.findall(summ or "")
            if not paths or any(not _is_doc(x) for x in paths):   # 看不出路徑就保守算;任一支不是文件就算
                return True
    return False


# ── 統計 ──────────────────────────────────────────────────────────────────────
def sign_flip_p(diffs):
    """單側精確符號翻轉檢定:所有正負號組合中,總和 ≥ 觀察總和的比例。"""
    obs = sum(diffs)
    combos = list(itertools.product((1, -1), repeat=len(diffs)))
    hits = sum(1 for c in combos if sum(s * d for s, d in zip(c, diffs)) >= obs - 1e-12)
    return hits / len(combos)


def kappa(a, b):
    n = len(a)
    if n == 0 or n != len(b):
        raise ValueError("兩組標註數量要相同且非空")
    cats = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def delivery_rate(items, n=N_GOLD):
    """交付率:handed 或 assumed_confirm 的項目數 ÷ 固定分母(每題 6 項)。"""
    return sum(v in ("handed", "assumed_confirm") for v in items.values()) / n


def _round_half_up(x):
    return int(x + 0.5)


# ── 盲評 ──────────────────────────────────────────────────────────────────────
_LEAK = re.compile(r"(?i)\bcodex\b|\bclaude\b|\bgpt[\w.-]*|\bopenai\b|\bsonnet\b|\bopus\b|\bhaiku\b|\banthropic\b|"
                   r"AGENTS\.md|CLAUDE\.md|/qo[/_-][ab]\b|order-svc-[ab]\b|\barm[\s_-]?[ab]\b|[甲乙]組")


def mask_leaks(text):
    return _LEAK.subn("⟨遮罩⟩", text)


def blind(runs, seed):
    """回 (評分包清單, 對照表 {盲評編號: 原始 key})。包裡只留題目與遮罩後的回答。"""
    order = sorted(runs, key=lambda r: r["key"])
    rnd = random.Random(seed)
    rnd.shuffle(order)
    packets, mapping = [], {}
    for i, r in enumerate(order, 1):
        bid = f"R{i:03d}"
        mapping[bid] = r["key"]
        packets.append({"blind_id": bid, "scenario": r["id"], "answer": mask_leaks(r["answer"])[0]})
    return packets, mapping


# ── 結果檔與版本 ──────────────────────────────────────────────────────────────
def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _scenarios(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def _out_path(out_dir, runner, arm, sid, k):
    return Path(out_dir) / runner / arm / f"{sid}-r{k}.json"


def _meta_path(out):
    return Path(str(out) + ".meta.json")


def _write_meta(out, meta):
    _meta_path(out).write_text(json.dumps(meta, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _meta_ok(out, meta):
    try:
        return json.loads(_meta_path(out).read_text(encoding="utf-8")) == meta
    except (OSError, ValueError):
        return False


def _valid(path):
    """有效結果:沒有致命、撞上限、儀器例外,也沒被截斷(原始長度要等於保存長度)。"""
    try:
        r = json.loads(Path(path).read_text(encoding="utf-8"))["results"][0]
    except (OSError, ValueError, KeyError, IndexError):
        return False
    if r.get("fatal") or r.get("limit_hit") or r.get("truncated"):
        return False
    if str(r.get("reason", "")).startswith("儀器例外"):
        return False
    ans, n = r.get("answer"), r.get("answer_len")
    return isinstance(ans, str) and isinstance(n, int) and n == len(ans)


def _cli_version(runner):
    exe = "claude" if runner == "claude" else "codex"
    r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=60)   # 外呼一律帶逾時
    return (r.stdout or r.stderr).strip()


def job_order(scen, runs, seed, arms=("a", "b")):
    """每個(題目, 第幾次)甲乙先後由種子決定;只跑子集時保留全集裡的相對順序。"""
    jobs = []
    for sc in scen:
        for k in range(1, runs + 1):
            pair = ["a", "b"]
            random.Random(f"{seed}:{sc['id']}:{k}").shuffle(pair)
            jobs += [(sc["id"], k, arm) for arm in pair if arm in arms]
    return jobs


def cmd_run(a):
    if not a.model:
        print("✗ --model 必須明寫(不讓本機設定決定受測模型)", file=sys.stderr)
        return 2
    meta = {"runner": a.runner, "model": a.model, "cli": _cli_version(a.runner), "answer_max": ANSWER_MAX}
    if a.runner == "codex":   # 推理強度等寫在本機設定檔,設定一改就不准混用
        cfg = Path.home() / ".codex" / "config.toml"
        meta["codex_config_sha256"] = _sha(cfg) if cfg.exists() else None
    jobs = job_order(_scenarios(a.scenarios), a.runs, a.order_seed, tuple(a.arms.split(",")))
    repo = {"a": a.arm_a, "b": a.arm_b}
    for sid, k, arm in jobs:
        out = _out_path(a.out_dir, a.runner, arm, sid, k)
        if out.exists() and not _meta_ok(out, meta):
            print(f"✗ {out} 的版本紀錄跟這次不同(或沒有),不混用;要重跑請先移走舊結果", file=sys.stderr)
            return 2
        if _valid(out):
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        _write_meta(out, meta)
        cmd = [sys.executable, str(PROBE), "--repo", repo[arm], "--scenarios", a.scenarios,
               "--exact-id", sid, "--runs", "1", "--runner", a.runner, "--answer-max", str(ANSWER_MAX),
               "--max-turns", "30", "--timeout", str(a.timeout), "--wait-on-limit", str(a.wait_on_limit),
               "--model", a.model, "--out", str(out)]
        if a.runner == "codex":
            cmd += ["--codex-bypass-hook-trust"]
        print(f"[{a.runner}] {sid} r{k} 組{arm}", flush=True)
        subprocess.run(cmd, cwd=str(REPO))
    return 0


def _load_runs(out_dir, valid_only=True):
    runs = []
    for p in sorted(Path(out_dir).glob("*/*/*.json")):
        if p.name.endswith(".meta.json"):
            continue
        runner, arm = p.parent.parent.name, p.parent.name
        m = re.match(r"(.+)-r(\d+)$", p.stem)
        if not m or (valid_only and not _valid(p)):
            continue
        r = json.loads(p.read_text(encoding="utf-8"))["results"][0]
        runs.append({"key": f"{runner}/{arm}/{p.stem}", "runner": runner, "arm": arm, "id": m.group(1),
                     "run": int(m.group(2)), "answer": r.get("answer", ""), "answer_len": r.get("answer_len"),
                     "calls": [tuple(c) for c in r.get("calls", [])], "valid": _valid(p)})
    return runs


# ── 機械計分 ──────────────────────────────────────────────────────────────────
def _gold_key(sid):
    return sid.split("-", 1)[1]   # qo-P1 → P1


def _regex_row(run, gold):
    g = gold[_gold_key(run["id"])]
    hits = [it["id"] for it in g["must_surface"] if re.search(it["regex"], run["answer"], re.I)]
    noise = sum(1 for it in g.get("should_not_ask", []) for line in run["answer"].splitlines()
                if re.search(it["regex"], line, re.I))
    return {"key": run["key"], "valid": run["valid"], "regex_cover": len(hits) / len(g["must_surface"]),
            "regex_hits": hits, "regex_noise": noise, "code_start": code_start(run["calls"]),
            "code_start_v1": code_start(run["calls"], _SHELL_WRITE_V1),
            "truncated": not run["valid"] and (run["answer_len"] or 0) > len(run["answer"])}


def cmd_score(a):
    gold = json.loads(Path(a.gold).read_text(encoding="utf-8"))
    rows = [_regex_row(r, gold) for r in _load_runs(a.out_dir, valid_only=False)]
    Path(a.dest).write_text(json.dumps({"gold_sha256": _sha(a.gold), "rows": rows}, ensure_ascii=False, indent=1),
                            encoding="utf-8")
    print(f"逐場 {len(rows)} 列(有效 {sum(r['valid'] for r in rows)})→ {a.dest}")
    return 0


def cmd_packets(a):
    dest, mapping_path = Path(a.dest).resolve(), Path(a.mapping).resolve()
    if dest in mapping_path.parents:
        print("✗ 對照表不得放在評分包目錄裡", file=sys.stderr)
        return 2
    runs = _load_runs(a.out_dir)
    if a.expect_runs and len(runs) != a.expect_runs:
        print(f"✗ 有效場次 {len(runs)} 不等於預期 {a.expect_runs},不產生評分包", file=sys.stderr)
        return 2
    packets, mapping = blind(runs, a.seed)
    masked = {r["key"]: mask_leaks(r["answer"])[1] for r in runs}
    dest.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(packets), a.batch):
        (dest / f"packet-{i // a.batch + 1:02d}.json").write_text(
            json.dumps(packets[i:i + a.batch], ensure_ascii=False, indent=1), encoding="utf-8")
    mapping_path.write_text(json.dumps({"mapping": mapping, "masked_counts": masked}, ensure_ascii=False, indent=1),
                            encoding="utf-8")
    print(f"{len(packets)} 場 → {dest};遮罩 {sum(masked.values())} 處;對照表 → {mapping_path}")
    return 0


# ── 評分員標註 ────────────────────────────────────────────────────────────────
def _read_labels(path):
    out = {}
    for f in sorted(Path(path).glob("*.json")):
        for row in json.loads(f.read_text(encoding="utf-8")):
            if row["blind_id"] in out:
                raise ValueError(f"{row['blind_id']} 重複標註")
            out[row["blind_id"]] = row
    return out


def _scenario_of(key):
    return re.match(r"(.+)-r\d+$", key.split("/")[2]).group(1)


def check_labels(labels, mapping, gold_topics):
    """每個盲評編號都要有、每場恰好那題的 6 個 gold_id、標籤只能三選一、亂問是非負整數。"""
    missing = sorted(set(mapping) - set(labels))
    extra = sorted(set(labels) - set(mapping))
    if missing or extra:
        raise ValueError(f"標註不完整:缺 {missing[:5]}… 多 {extra[:5]}…")
    for bid, key in mapping.items():
        want = {g["gold_id"] for g in gold_topics[_scenario_of(key)]}
        row = labels[bid]
        if set(row["items"]) != want:
            raise ValueError(f"{bid} 的 gold 項目不對:{sorted(set(row['items']) ^ want)}")
        bad = {k: v for k, v in row["items"].items() if v not in LABELS}
        if bad:
            raise ValueError(f"{bid} 有不合法標籤 {bad}")
        if not isinstance(row.get("noise"), int) or row["noise"] < 0:
            raise ValueError(f"{bid} 的 noise 要是非負整數")


def _load_ctx(a):
    m = json.loads(Path(a.mapping).read_text(encoding="utf-8"))["mapping"]
    gt = json.loads(Path(a.gold_topics).read_text(encoding="utf-8"))
    return m, gt


def cmd_agree(a):
    mapping, gt = _load_ctx(a)
    la, lb = _read_labels(a.rater_a), _read_labels(a.rater_b)
    check_labels(la, mapping, gt); check_labels(lb, mapping, gt)
    xs, ys, dis = [], [], []
    for bid in sorted(mapping):
        for gid in sorted(la[bid]["items"]):
            x, y = la[bid]["items"][gid], lb[bid]["items"][gid]
            xs.append(x); ys.append(y)
            if x != y:
                dis.append({"blind_id": bid, "gold_id": gid, "labels": sorted([x, y])})
        if _scenario_of(mapping[bid]) in NOISE_SCENARIOS and abs(la[bid]["noise"] - lb[bid]["noise"]) > 1:
            dis.append({"blind_id": bid, "gold_id": "noise", "labels": sorted([la[bid]["noise"], lb[bid]["noise"]])})
    k = kappa(xs, ys)
    Path(a.dest).write_text(json.dumps({"n_runs": len(mapping), "n_items": len(xs), "kappa": k,
                                        "agreement": sum(x == y for x, y in zip(xs, ys)) / len(xs),
                                        "disagreements": dis}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"場次 {len(mapping)}、判定 {len(xs)} 條、kappa={k:.3f}、要仲裁 {len(dis)} 條 → {a.dest}")
    return 0


def cmd_adj_pack(a):
    """仲裁包:每條分歧附該場回答、題目與兩個候選(候選順序打亂,不標來源)。"""
    agree = json.loads(Path(a.agree).read_text(encoding="utf-8"))
    gt = json.loads(Path(a.gold_topics).read_text(encoding="utf-8"))
    mapping = json.loads(Path(a.mapping).read_text(encoding="utf-8"))["mapping"]
    packets = {}
    for f in sorted(Path(a.packets).glob("packet-*.json")):
        for p in json.loads(f.read_text(encoding="utf-8")):
            packets[p["blind_id"]] = p
    rnd = random.Random(a.seed)
    out = []
    for d in agree["disagreements"]:
        cands = list(d["labels"]); rnd.shuffle(cands)
        topic = ("把 README 已寫的事當問題問人的主題數" if d["gold_id"] == "noise" else
                 next(g["topic"] for g in gt[_scenario_of(mapping[d["blind_id"]])] if g["gold_id"] == d["gold_id"]))
        out.append({"blind_id": d["blind_id"], "gold_id": d["gold_id"], "topic": topic, "candidates": cands,
                    "scenario": packets[d["blind_id"]]["scenario"], "answer": packets[d["blind_id"]]["answer"]})
    Path(a.dest).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"仲裁 {len(out)} 條 → {a.dest}")
    return 0


def merge(la, lb, adj):
    """兩位一致就照用;不一致用仲裁;亂問差 ≤1 取平均四捨五入(0.5 進位),差 >1 用仲裁。缺仲裁就報錯。"""
    out = {}
    for bid in la:
        items = {}
        for gid, x in la[bid]["items"].items():
            y = lb[bid]["items"][gid]
            if x == y:
                items[gid] = x
            elif (bid, gid) in adj:
                if adj[(bid, gid)] not in (x, y):
                    raise ValueError(f"{bid}/{gid} 的仲裁 {adj[(bid, gid)]!r} 不是兩個候選之一")
                items[gid] = adj[(bid, gid)]
            else:
                raise ValueError(f"{bid}/{gid} 兩位不一致卻沒有仲裁")
        na, nb = la[bid]["noise"], lb[bid]["noise"]
        if abs(na - nb) > 1:
            if (bid, "noise") not in adj:
                raise ValueError(f"{bid} 的亂問數差 >1 卻沒有仲裁")
            noise = adj[(bid, "noise")]
            if not isinstance(noise, int) or not min(na, nb) <= noise <= max(na, nb):
                raise ValueError(f"{bid} 的亂問數仲裁 {noise!r} 不在兩位評分員的值之間")
        else:
            noise = _round_half_up((na + nb) / 2)
        out[bid] = {"blind_id": bid, "items": items, "noise": noise}
    return out


def _read_adj(path):
    adj = {}
    if path:
        for row in json.loads(Path(path).read_text(encoding="utf-8")):
            adj[(row["blind_id"], row["gold_id"])] = row["choice"]
    return adj


def cmd_merge(a):
    mapping, gt = _load_ctx(a)
    la, lb = _read_labels(a.rater_a), _read_labels(a.rater_b)
    check_labels(la, mapping, gt); check_labels(lb, mapping, gt)
    adj = _read_adj(a.adjudication)
    merged = merge(la, lb, adj)
    check_labels(merged, mapping, gt)
    Path(a.dest).mkdir(parents=True, exist_ok=True)
    (Path(a.dest) / "merged.json").write_text(json.dumps(list(merged.values()), ensure_ascii=False, indent=1),
                                               encoding="utf-8")
    print(f"合併 {len(merged)} 場(用了仲裁 {len(adj)} 條)→ {a.dest}")
    return 0


# ── 最後判定 ──────────────────────────────────────────────────────────────────
def verdict(s):
    """回 (PASS|FAIL|INCONCLUSIVE, 理由清單)。先看無效條件,再看門檻。"""
    why = []
    if s["truncated_any"]:
        why.append("有回答被截斷")
    if s["kappa"] < 0.6:
        why.append(f"評分員 kappa {s['kappa']:.2f} < 0.6")
    if s["complete"] < 5:
        why.append(f"完整題目只有 {s['complete']} 題")
    if s["all_zero"]:
        why.append("兩組交付率全為 0")
    if why:
        return "INCONCLUSIVE", why
    if s["mean_diff"] < 0.15:
        why.append(f"平均差 {s['mean_diff']:.3f} < 0.15")
    if s["p"] > 0.05:
        why.append(f"符號翻轉檢定 p={s['p']:.4f} > 0.05")
    if s["noise_b"] > s["noise_a"]:
        why.append(f"乙組亂問 {s['noise_b']} > 甲組 {s['noise_a']}")
    if s["code_b"] > s["code_a"]:
        why.append(f"乙組先寫程式 {s['code_b']} > 甲組 {s['code_a']}")
    return ("FAIL", why) if why else ("PASS", ["三條門檻都成立"])


def final_gate(main, sensitivity):
    """主判定與兩個單一評分員判定不一致 → 攤給人裁(預先登記〈評分〉自我偏好)。"""
    return main if all(v == main for v in sensitivity) else "NEEDS_HUMAN"


def _summarize(runner, labels, mapping, mech, runs_per_cell, kap):
    per, noise, code, truncated = {}, {"a": 0, "b": 0}, {"a": 0, "b": 0}, False
    for row in mech.values():
        if row["key"].startswith(f"{runner}/") and row["truncated"]:
            truncated = True
    for bid, key in mapping.items():
        r, arm, _ = key.split("/")
        if r != runner:
            continue
        sid = _scenario_of(key)
        per.setdefault((sid, arm), []).append(delivery_rate(labels[bid]["items"]))
        if sid in NOISE_SCENARIOS:
            noise[arm] += labels[bid]["noise"]
        code[arm] += int(bool(mech[key]["code_start"]))
    sids = sorted({s for s, _ in per})
    diffs, complete = [], []
    for sid in sids:
        xa, xb = per.get((sid, "a"), []), per.get((sid, "b"), [])
        if len(xa) == len(xb) == runs_per_cell:
            diffs.append(sum(xb) / len(xb) - sum(xa) / len(xa)); complete.append(sid)
    allv = [v for vs in per.values() for v in vs]
    s = {"kappa": kap, "truncated_any": truncated, "complete": len(complete), "complete_scenarios": complete,
         "all_zero": bool(allv) and all(v == 0 for v in allv), "diffs": diffs,
         "mean_diff": sum(diffs) / len(diffs) if diffs else 0.0, "p": sign_flip_p(diffs) if diffs else 1.0,
         "noise_a": noise["a"], "noise_b": noise["b"], "code_a": code["a"], "code_b": code["b"]}
    s["verdict"], s["reasons"] = verdict(s)
    return s


def cmd_final(a):
    mapping, gt = _load_ctx(a)
    la, lb = _read_labels(a.rater_a), _read_labels(a.rater_b)
    check_labels(la, mapping, gt); check_labels(lb, mapping, gt)
    merged = merge(la, lb, _read_adj(a.adjudication))   # 當場重算,不收「據稱合併過」的資料夾
    check_labels(merged, mapping, gt)
    agree = json.loads(Path(a.agree).read_text(encoding="utf-8"))
    mech = {r["key"]: r for r in json.loads(Path(a.score).read_text(encoding="utf-8"))["rows"]}
    sens = {"rater_a": la, "rater_b": lb}
    report = {}
    for runner in sorted({k.split("/")[0] for k in mapping.values()}):
        main_s = _summarize(runner, merged, mapping, mech, a.runs, agree["kappa"])
        main_s["sensitivity"] = {}
        for name, lab in sens.items():
            s = _summarize(runner, lab, mapping, mech, a.runs, agree["kappa"])
            main_s["sensitivity"][name] = {"verdict": s["verdict"], "mean_diff": s["mean_diff"], "p": s["p"]}
        gated = final_gate(main_s["verdict"], [v["verdict"] for v in main_s["sensitivity"].values()])
        if gated != main_s["verdict"]:
            main_s["reasons"] = main_s["reasons"] + [f"主判定 {main_s['verdict']} 與單一評分員判定不一致"]
            main_s["verdict"] = gated
        report[runner] = main_s
    Path(a.dest).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--arm-a", required=True); r.add_argument("--arm-b", required=True)
    r.add_argument("--scenarios", default=str(HERE / "scenarios.jsonl"))
    r.add_argument("--runner", choices=["claude", "codex"], required=True)
    r.add_argument("--model", default="", help="必填:受測模型 id")
    r.add_argument("--runs", type=int, default=3)
    r.add_argument("--order-seed", default="qo-2026-10")
    r.add_argument("--arms", default="a,b", help="只跑其中幾組,逗號分隔(小實驗只重跑乙組時用)")
    r.add_argument("--timeout", type=int, default=600)
    r.add_argument("--wait-on-limit", type=int, default=1800)
    r.add_argument("--out-dir", required=True)
    s = sub.add_parser("score")
    s.add_argument("--out-dir", required=True); s.add_argument("--gold", default=str(HERE / "gold.json"))
    s.add_argument("--dest", required=True)
    p = sub.add_parser("packets")
    p.add_argument("--out-dir", required=True); p.add_argument("--seed", type=int, default=20261012)
    p.add_argument("--batch", type=int, default=8); p.add_argument("--expect-runs", type=int, default=0)
    p.add_argument("--dest", required=True); p.add_argument("--mapping", required=True)
    for name in ("agree", "merge", "final"):
        q = sub.add_parser(name)
        q.add_argument("--mapping", required=True)
        q.add_argument("--gold-topics", default=str(HERE / "gold-topics.json"))
        q.add_argument("--dest", required=True)
        if name in ("agree", "merge"):
            q.add_argument("--rater-a", required=True); q.add_argument("--rater-b", required=True)
        if name == "merge":
            q.add_argument("--adjudication", default="")
        if name == "final":
            q.add_argument("--agree", required=True); q.add_argument("--score", required=True)
            q.add_argument("--rater-a", required=True); q.add_argument("--rater-b", required=True)
            q.add_argument("--adjudication", default="", help="仲裁結果;final 會自己重算合併")
            q.add_argument("--runs", type=int, default=3)
    j = sub.add_parser("adj-pack")
    j.add_argument("--agree", required=True); j.add_argument("--packets", required=True)
    j.add_argument("--mapping", required=True); j.add_argument("--gold-topics", default=str(HERE / "gold-topics.json"))
    j.add_argument("--seed", type=int, default=20261013); j.add_argument("--dest", required=True)
    a = ap.parse_args(argv)
    return {"run": cmd_run, "score": cmd_score, "packets": cmd_packets, "agree": cmd_agree, "adj-pack": cmd_adj_pack,
            "merge": cmd_merge, "final": cmd_final}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
