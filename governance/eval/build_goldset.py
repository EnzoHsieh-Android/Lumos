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
    legacy = [l.split(" (")[0] for l in lum_lines("search", q, "--legacy", "--files-only")
              if l.split(" (")[0].endswith(".md") and "/" in l][:8]
    ranked = [x["node"] for x in lum_json("search", q, "--ranked", "--top", "8", "--json").get("results", [])]
    pool = list(dict.fromkeys(legacy + ranked))
    rnd = random.Random(hashlib.sha256((q + SALT).encode()).hexdigest())
    rnd.shuffle(pool)
    return pool


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
            seen.add(f)
            files.append((f, cur_sha))
        if len(files) >= n:
            break
    cases = []
    for f, sha in files[:n]:
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


def main():
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
    for j, c in enumerate(edit_cases(20), 1):
        cid = f"E{j:02d}"
        pool = edit_pool(c["file"], c["delta"])
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
    main()
