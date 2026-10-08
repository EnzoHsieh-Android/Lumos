#!/opt/homebrew/bin/python3
"""從 V0_blame_max|now 被標的段落,固定種子抽 30 段,產出人工判定用卷宗 out/sample30/NN.txt 與 out/sample30.json。"""
import ast, json, os, random, re, subprocess, sys
EXP = sys.argv[1]
VAR = sys.argv[2] if len(sys.argv) > 2 else "V0_blame_max|now"
REPO = f"{EXP}/rtb"
M = json.load(open(f"{EXP}/out/stats.json"))["measure_commit"]
paras = [json.loads(l) for l in open(f"{EXP}/out/paragraphs.jsonl")]
flagged = [p for p in paras if p[VAR]]
rng = random.Random(20260930)
sample = rng.sample(flagged, 30)
os.makedirs(f"{EXP}/out/sample30", exist_ok=True)


def git(*a):
    return subprocess.run(["git", "-C", REPO, "-c", "core.quotepath=off", *a], capture_output=True).stdout.decode("utf-8", "replace")


def defs(src, name):
    try:
        tree = ast.parse(src)
    except Exception:
        return []
    out = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == name:
            out.append(ast.get_source_segment(src, n))
        elif isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
            out.append(ast.get_source_segment(src, n))
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id == name:
            out.append(ast.get_source_segment(src, n))
    return out


def evidence(name, h):
    subj = git("log", "-1", "--format=%h %ci %s", h).strip()
    lines = [f"  -- {subj}"]
    if name.startswith("file:"):
        path = name[5:]
        d = git("show", "--format=", "--stat", h, "--", path).strip()
        lines.append("     " + d.replace("\n", "\n     "))
        body = git("show", "--format=", "-U1", h, "--", path).splitlines()
        body = [l for l in body if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
        lines += ["     " + l[:160] for l in body[:25]]
        return lines
    files = [f for f in git("show", "--format=", "--name-only", h).split("\n") if f.startswith(("src/", "tests/"))]
    shown = 0
    for f in files:
        old = git("show", f"{h}^:{f}") if f.endswith(".py") else ""
        new = git("show", f"{h}:{f}") if f.endswith(".py") else ""
        do, dn = defs(old, name), defs(new, name)
        if do != dn:
            lines.append(f"     [{f}] 定義 {len(do)}→{len(dn)} 處")
            import difflib
            dl = list(difflib.unified_diff("\n".join(do).splitlines(), "\n".join(dn).splitlines(), lineterm="", n=1))[2:]
            lines += ["     " + l[:160] for l in dl[:30]]
            shown += 1
        elif not do and not dn:
            diff = git("show", "--format=", "-U0", h, "--", f).splitlines()
            hit = [l for l in diff if l.startswith(("+", "-")) and not l.startswith(("+++", "---")) and re.search(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])", l)]
            if hit:
                lines.append(f"     [{f}] 出現次數變動行:")
                lines += ["     " + l[:160] for l in hit[:8]]
                shown += 1
        if shown >= 4:
            break
    return lines


out = []
for i, p in enumerate(sample, 1):
    trig = p[VAR + "|trig"]
    buf = [f"#{i:02d} {p['note']} L{p['start']}-{p['end']} kind={p['kind']}",
           f"blame_max={git('log','-1','--format=%h %ci %s',p['p_max']).strip()}",
           "---- 段落 ----", p["text"], "---- 觸發 ----"]
    for name, hs in trig.items():
        buf.append(f"* {name}: {hs}")
        for h in hs[-2:]:
            buf += evidence(name, h)
    open(f"{EXP}/out/sample30/{i:02d}.txt", "w").write("\n".join(buf) + "\n")
    out.append({"i": i, "note": p["note"], "start": p["start"], "end": p["end"], "kind": p["kind"], "trig": trig})
json.dump(out, open(f"{EXP}/out/sample30.json", "w"), ensure_ascii=False, indent=1)
print(len(flagged), "flagged; sampled 30")
