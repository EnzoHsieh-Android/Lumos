import subprocess, re, json, os
EXP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RTB = EXP + "/rtb"
KB = "docs/rtb-production-agent-demo-knowledge"
CODE_PREFIX = ("src/", "tests/", "scripts/")
CODE_EXT = (".py", ".sh", ".toml", ".js", ".ts", ".html", ".css")

def git(*a, check=True):
    r = subprocess.run(["git", "-c", "core.quotepath=off", "-C", RTB, *a], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(r.stderr)
    return r.stdout

def changed_files(c):
    return [l for l in git("show", "--name-only", "--format=", c).splitlines() if l]

def is_code(p):
    return p.startswith(CODE_PREFIX) and not p.startswith("docs/")

def about_code(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m: return []
    fm = m.group(1)
    out, inblk = [], False
    for line in fm.splitlines():
        if re.match(r"^about_code:\s*$", line):
            inblk = True; continue
        if inblk:
            mm = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if mm: out.append(mm.group(1).strip().strip('"\'')); continue
            if re.match(r"^\S", line): inblk = False
    return out

def note_at(rev, note):
    r = subprocess.run(["git", "-C", RTB, "show", f"{rev}:{KB}/{note}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

def all_notes_at(rev):
    return [l[len(KB)+1:] for l in git("ls-tree", "-r", "--name-only", rev, KB).splitlines() if l.endswith(".md")]

def homes_map(rev):
    """file -> [notes] whose about_code lists it"""
    m = {}
    for n in all_notes_at(rev):
        t = note_at(rev, n) or ""
        for f in about_code(t):
            m.setdefault(f, []).append(n)
    return m
