#!/usr/bin/env python3
"""情境出題對照實驗的執行與計分器(預先登記:同目錄 preregistration.md)。

子命令:
  run     交錯執行:每個(題目, 第幾次)甲乙各跑一場,先後由固定種子決定;已有有效結果的場次跳過(可續跑)
  score   輔助計分:標準答案正規式初篩、先寫程式、回答長度;輸出逐場表
  packets 產生盲評包:隱去受測者、組別、場次並打亂;對照表另存,不給評分員
  agree   比對兩位評分員的標註,算一致率(Cohen's kappa)
  final   主指標:逐題配對差 + 精確符號翻轉檢定;輔助指標與無效條件

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

# 先寫程式:寫到 docs/ 以外的非 .md 檔,或 shell 寫檔、建置工具。預先登記〈指標〉第 3 條。
_CODE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit", "apply_patch"}
_SHELL_WRITE = re.compile(
    r"(?:^|[;&|]\s*)(?:touch|tee|cp|mv|install)\s|"
    r"(?<![0-9&])>>?\s*(?!/dev/null)[\w./-]+|"
    r"<<\s*['\"]?\w+|"
    r"open\([^)]*['\"]w|write_text\(|"
    r"\b(?:gradle|gradlew|mvn|mvnw)\b(?!\s+--version)|spring\s+init|start\.spring\.io|"
    r"\bgit\s+apply\b|\bnpm\s+init\b|mkdir\s+-p\s+src\b")


def _is_doc(path):
    p = path.strip().strip("'\"")
    return p.endswith(".md") or "/docs/" in f"/{p}" or p.startswith("docs/")


def code_start(calls):
    for name, summ in calls:
        if name in _CODE_TOOLS and not _is_doc(summ):
            return True
        if name in ("Bash", "exec_command", "shell") and _SHELL_WRITE.search(summ or ""):
            if not re.search(r"\bdocs/|\.md\b", summ or ""):
                return True
    return False


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


def blind(runs, seed):
    """回 (評分包清單, 對照表 {盲評編號: 原始 key})。包裡只留題目與回答。"""
    order = sorted(runs, key=lambda r: r["key"])
    rnd = random.Random(seed)
    rnd.shuffle(order)
    packets, mapping = [], {}
    for i, r in enumerate(order, 1):
        bid = f"R{i:03d}"
        mapping[bid] = r["key"]
        packets.append({"blind_id": bid, "scenario": r["id"], "answer": r["answer"]})
    return packets, mapping


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _scenarios(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def _out_path(out_dir, runner, arm, sid, k):
    return Path(out_dir) / runner / arm / f"{sid}-r{k}.json"


def _valid(path):
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        r = d["results"][0]
    except (OSError, ValueError, KeyError, IndexError):
        return False
    return not r.get("fatal") and not r.get("limit_hit") and "answer" in r


def cmd_run(a):
    scen = _scenarios(a.scenarios)
    jobs = []
    for sc in scen:
        for k in range(1, a.runs + 1):
            pair = ["a", "b"]
            random.Random(f"{a.order_seed}:{sc['id']}:{k}").shuffle(pair)
            jobs += [(sc["id"], k, arm) for arm in pair]
    repo = {"a": a.arm_a, "b": a.arm_b}
    for sid, k, arm in jobs:
        out = _out_path(a.out_dir, a.runner, arm, sid, k)
        if _valid(out):
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, str(PROBE), "--repo", repo[arm], "--scenarios", a.scenarios,
               "--exact-id", sid, "--runs", "1", "--runner", a.runner, "--answer-max", str(ANSWER_MAX),
               "--max-turns", "30", "--timeout", str(a.timeout), "--wait-on-limit", str(a.wait_on_limit),
               "--out", str(out)]
        if a.model:
            cmd += ["--model", a.model]
        if a.runner == "codex":
            cmd += ["--codex-bypass-hook-trust"]
        print(f"[{a.runner}] {sid} r{k} 組{arm}", flush=True)
        subprocess.run(cmd, cwd=str(REPO))
    return 0


def _load_runs(out_dir):
    runs = []
    for p in sorted(Path(out_dir).glob("*/*/*.json")):
        runner, arm = p.parent.parent.name, p.parent.name
        m = re.match(r"(.+)-r(\d+)$", p.stem)
        if not m or not _valid(p):
            continue
        r = json.loads(p.read_text(encoding="utf-8"))["results"][0]
        runs.append({"key": f"{runner}/{arm}/{p.stem}", "runner": runner, "arm": arm, "id": m.group(1),
                     "run": int(m.group(2)), "answer": r.get("answer", ""), "answer_len": r.get("answer_len"),
                     "calls": [tuple(c) for c in r.get("calls", [])]})
    return runs


def _gold_key(sid):
    return sid.split("-", 1)[1]   # qo-P1 → P1


def _regex_row(run, gold):
    g = gold[_gold_key(run["id"])]
    hits = [it["id"] for it in g["must_surface"] if re.search(it["regex"], run["answer"], re.I)]
    noise = 0
    for it in g.get("should_not_ask", []):
        noise += sum(1 for line in run["answer"].splitlines() if re.search(it["regex"], line, re.I))
    return {"key": run["key"], "regex_cover": len(hits) / len(g["must_surface"]), "regex_hits": hits,
            "regex_noise": noise, "code_start": code_start(run["calls"]),
            "truncated": (run["answer_len"] or 0) > len(run["answer"])}


def cmd_score(a):
    gold = json.loads(Path(a.gold).read_text(encoding="utf-8"))
    rows = [_regex_row(r, gold) for r in _load_runs(a.out_dir)]
    Path(a.dest).write_text(json.dumps({"gold_sha256": _sha(a.gold), "rows": rows}, ensure_ascii=False, indent=1),
                            encoding="utf-8")
    print(f"逐場 {len(rows)} 列 → {a.dest}")
    return 0


def cmd_packets(a):
    runs = _load_runs(a.out_dir)
    packets, mapping = blind(runs, a.seed)
    dest = Path(a.dest)
    dest.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(packets), a.batch):
        part = packets[i:i + a.batch]
        (dest / f"packet-{i // a.batch + 1:02d}.json").write_text(json.dumps(part, ensure_ascii=False, indent=1),
                                                                encoding="utf-8")
    Path(a.mapping).write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(packets)} 場分成 {(len(packets) + a.batch - 1) // a.batch} 包 → {dest};對照表 → {a.mapping}")
    return 0


def _read_labels(path):
    """評分員輸出:[{blind_id, items: {gold_id: label}, noise: int}];先寫程式不由評分員判。"""
    out = {}
    for f in sorted(Path(path).glob("*.json")):
        for row in json.loads(f.read_text(encoding="utf-8")):
            out[row["blind_id"]] = row
    return out


def cmd_agree(a):
    la, lb = _read_labels(a.rater_a), _read_labels(a.rater_b)
    common = sorted(set(la) & set(lb))
    xs, ys, dis = [], [], []
    for bid in common:
        for gid in sorted(set(la[bid]["items"]) | set(lb[bid]["items"])):
            x, y = la[bid]["items"].get(gid, "absent"), lb[bid]["items"].get(gid, "absent")
            xs.append(x); ys.append(y)
            if x != y:
                dis.append({"blind_id": bid, "gold_id": gid, "a": x, "b": y})
    k = kappa(xs, ys)
    Path(a.dest).write_text(json.dumps({"n_runs": len(common), "n_items": len(xs), "kappa": k,
                                        "agreement": sum(x == y for x, y in zip(xs, ys)) / len(xs),
                                        "disagreements": dis}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"共同場次 {len(common)}、判定 {len(xs)} 條、kappa={k:.3f}、分歧 {len(dis)} 條 → {a.dest}")
    return 0


def cmd_final(a):
    mapping = json.loads(Path(a.mapping).read_text(encoding="utf-8"))
    labels = _read_labels(a.labels)
    mech = {r["key"]: r for r in json.loads(Path(a.score).read_text(encoding="utf-8"))["rows"]}
    per = {}   # (runner, scenario, arm) -> [覆蓋率]
    side = {}  # (runner, arm) -> [亂問, 先寫程式]
    for bid, key in mapping.items():
        if bid not in labels:
            continue
        runner, arm, stem = key.split("/")
        sid = re.match(r"(.+)-r\d+$", stem).group(1)
        items = labels[bid]["items"]
        cover = sum(v in ("handed", "assumed_confirm") for v in items.values()) / max(1, len(items))
        per.setdefault((runner, sid, arm), []).append(cover)
        s = side.setdefault((runner, arm), [0, 0])
        s[0] += int(labels[bid].get("noise", 0)); s[1] += int(bool(mech.get(key, {}).get("code_start")))
    report = {}
    for runner in sorted({k[0] for k in per}):
        sids = sorted({k[1] for k in per if k[0] == runner})
        diffs, complete = [], []
        for sid in sids:
            xa, xb = per.get((runner, sid, "a"), []), per.get((runner, sid, "b"), [])
            if len(xa) == len(xb) == a.runs:
                diffs.append(sum(xb) / len(xb) - sum(xa) / len(xa)); complete.append(sid)
        report[runner] = {"complete_scenarios": complete, "diffs": diffs,
                          "mean_diff": sum(diffs) / len(diffs) if diffs else None,
                          "sign_flip_p": sign_flip_p(diffs) if diffs else None,
                          "noise_a_b": [side.get((runner, "a"), [0, 0])[0], side.get((runner, "b"), [0, 0])[0]],
                          "code_start_a_b": [side.get((runner, "a"), [0, 0])[1], side.get((runner, "b"), [0, 0])[1]]}
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
    r.add_argument("--model", default="")
    r.add_argument("--runs", type=int, default=3)
    r.add_argument("--order-seed", default="qo-2026-10")
    r.add_argument("--timeout", type=int, default=600)
    r.add_argument("--wait-on-limit", type=int, default=1800)
    r.add_argument("--out-dir", required=True)
    s = sub.add_parser("score")
    s.add_argument("--out-dir", required=True); s.add_argument("--gold", default=str(HERE / "gold.json"))
    s.add_argument("--dest", required=True)
    p = sub.add_parser("packets")
    p.add_argument("--out-dir", required=True); p.add_argument("--seed", type=int, default=20261012)
    p.add_argument("--batch", type=int, default=8)
    p.add_argument("--dest", required=True); p.add_argument("--mapping", required=True)
    g = sub.add_parser("agree")
    g.add_argument("--rater-a", required=True); g.add_argument("--rater-b", required=True)
    g.add_argument("--dest", required=True)
    f = sub.add_parser("final")
    f.add_argument("--mapping", required=True); f.add_argument("--labels", required=True)
    f.add_argument("--score", required=True, help="score 子命令的輸出(先寫程式由工具呼叫機械判定)")
    f.add_argument("--runs", type=int, default=3); f.add_argument("--dest", required=True)
    a = ap.parse_args(argv)
    return {"run": cmd_run, "score": cmd_score, "packets": cmd_packets, "agree": cmd_agree, "final": cmd_final}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
