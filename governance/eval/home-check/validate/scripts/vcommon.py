"""Validation-run helpers. Same logic as homescan-exp/scripts/common.py + build_prompt.py (V3),
parametrised over two repos (rtb, tool). The V3 prompt template (HEAD, HIST_V3) is imported
verbatim from a byte-identical copy of the original build_prompt.py (scripts/orig/)."""
import subprocess, re, json, os, sys
sys.dont_write_bytecode = True
VAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, VAL + "/scripts/orig")
import build_prompt as ORIG          # original module (its own common binds to homescan-exp/rtb; we only reuse constants/pure fns)
from common import about_code        # original frontmatter parser, pure function

HEAD = ORIG.HEAD
HIST_V3 = ORIG.HIST_V3
DIFF_CAP = ORIG.DIFF_CAP
numbered = ORIG.numbered
split_diff = ORIG.split_diff

REPOS = {
    "rtb": dict(path=VAL + "/rtb", kb="docs/rtb-production-agent-demo-knowledge"),
    "tool": dict(path=VAL + "/tool", kb="docs/lumos-toolchain-knowledge"),
}

TOOL_EXT = (".py", ".sh", ".ps1", ".js", ".ts", ".toml")

def is_code(repo, p):
    if repo == "rtb":   # identical to original common.is_code
        return p.startswith(("src/", "tests/", "scripts/")) and not p.startswith("docs/")
    # tool: program files under scripts/, governance/, slim/ (.py/.sh/.ps1/...); extensionless files only under scripts/ (scripts/lumos, hooks)
    if not p.startswith(("scripts/", "governance/", "slim/")):
        return False
    base = p.rsplit("/", 1)[-1]
    if p.endswith(TOOL_EXT):
        return True
    return p.startswith("scripts/") and "." not in base

class Repo:
    def __init__(self, name):
        self.name = name; self.path = REPOS[name]["path"]; self.kb = REPOS[name]["kb"]
        self._cat = None; self._blob_ac = {}; self._hm = {}
    def git(self, *a, check=True):
        r = subprocess.run(["git", "-c", "core.quotepath=off", "-C", self.path, *a], capture_output=True, text=True)
        if check and r.returncode != 0:
            raise RuntimeError(r.stderr)
        return r.stdout
    def changed_files(self, c):
        return [l for l in self.git("show", "--name-only", "--format=", c).splitlines() if l]
    def code_files(self, c):
        return [f for f in self.changed_files(c) if is_code(self.name, f)]
    def note_at(self, rev, note):
        r = subprocess.run(["git", "-C", self.path, "show", f"{rev}:{self.kb}/{note}"], capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None
    def _blob(self, sha):
        if self._cat is None:
            self._cat = subprocess.Popen(["git", "-C", self.path, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self._cat.stdin.write((sha + "\n").encode()); self._cat.stdin.flush()
        hdr = self._cat.stdout.readline().split()
        n = int(hdr[2]); data = self._cat.stdout.read(n); self._cat.stdout.read(1)
        return data.decode("utf-8", "replace")
    def homes_ordered(self, rev):
        """file -> [(index_in_about_code, note)] for all notes at rev"""
        if rev in self._hm: return self._hm[rev]
        m = {}
        for line in self.git("-c", "core.quotepath=off", "ls-tree", "-r", rev, self.kb).splitlines():
            meta, path = line.split("\t", 1)
            if not path.endswith(".md"): continue
            sha = meta.split()[2]
            if sha not in self._blob_ac: self._blob_ac[sha] = about_code(self._blob(sha))
            for i, f in enumerate(self._blob_ac[sha]):
                m.setdefault(f, []).append((i, path[len(self.kb) + 1:]))
        self._hm[rev] = m
        return m

def home_notes(repo, c, code=None):
    """Notes whose about_code lists a changed code file, ordered by (earliest about_code index of a changed file, path)."""
    code = code if code is not None else repo.code_files(c)
    hm = repo.homes_ordered(c)
    best = {}
    for f in code:
        for i, n in hm.get(f, []):
            best[n] = min(best.get(n, 10**9), i)
    return [n for n, _ in sorted(best.items(), key=lambda kv: (kv[1], kv[0]))]

def truncated_diff(repo, commit, files, cap=DIFF_CAP):
    # identical algorithm to original build_prompt.truncated_diff
    if not files:
        return "(無)", False, 0, 3
    d = repo.git("show", "--format=", "-U3", commit, "--", *files)
    total = len(d)
    for u in (3, 1, 0):
        d = repo.git("show", "--format=", f"-U{u}", commit, "--", *files)
        if len(d) <= cap:
            return d, u != 3, total, u
    parts = split_diff(d)
    order = sorted(range(len(parts)), key=lambda i: len(parts[i]))
    out = [None] * len(parts); remaining = cap; left = len(parts)
    for i in order:
        share = remaining // left
        p = parts[i]
        if len(p) <= share:
            out[i] = p
        else:
            cut = p[:share]; cut = cut[:cut.rfind("\n") + 1]
            omitted = p[len(cut):].count("\n")
            out[i] = cut + f"[截斷:本檔 diff 另有 {omitted} 行未列出]\n"
        remaining -= len(out[i]); left -= 1
    return "".join(out), True, total, 0

def orphan_tests(repo, commit, code, mine):
    hm = repo.homes_ordered(commit)
    if repo.name == "rtb":   # identical to original rule
        pkgs = {f.split("/")[2] for f in mine if f.startswith("src/rtb/") and f.count("/") >= 3}
        return [f for f in code if f.startswith("tests/") and f not in hm and f not in mine
                and f.count("/") >= 2 and f.split("/")[1] in pkgs]
    # tool analogue: test files (test_*.py or under a tests/ dir) with no home, in the same directory as a home file
    dirs = {f.rsplit("/", 1)[0] for f in mine if "/" in f}
    out = []
    for f in code:
        if f in hm or f in mine or "/" not in f: continue
        d, base = f.rsplit("/", 1)
        is_test = base.startswith("test_") or "/tests/" in "/" + f
        dd = d[:-len("/tests")] if d.endswith("/tests") else d
        if is_test and (d in dirs or dd in dirs):
            out.append(f)
    return out

def build_v3(repo, commit, note):
    """Exactly the original build(commit, note, 'V3') flow, over `repo`."""
    text = repo.note_at(commit, note)
    ac = about_code(text)
    code = repo.code_files(commit)
    mine = [f for f in code if f in ac]
    ot = orphan_tests(repo, commit, code, mine)
    given = mine + ot
    others = [f for f in code if f not in given]
    diff, trunc, total, ctx = truncated_diff(repo, commit, given)
    others_s = "無" if not others else ("、".join(others[:40]) + (f" …等共 {len(others)} 支" if len(others) > 40 else ""))
    trunc_s = ""
    if ot:
        trunc_s += ",另加同套件目錄裡沒有家的測試檔(" + "、".join(ot) + ")"
    if trunc:
        trunc_s += f"(原始 diff {total} 字元,超過 {DIFF_CAP} 上限:上下文縮成 {ctx} 行" + (",仍超過的再各檔平均截斷,截掉處有註明" if "[截斷:" in diff else "") + ")"
    meta = {"repo": repo.name, "commit": commit, "note": note, "variant": "V3", "home_files": mine, "orphan_tests": ot, "diff_context": ctx,
            "diff_chars_given": len(diff), "other_code_files": len(others), "diff_chars_full": total, "diff_truncated": trunc,
            "note_lines": text.count("\n") + 1, "note_chars": len(text)}
    p = HEAD.format(histrule=HIST_V3, trunc=trunc_s, others=others_s, partial="全文",
                    extra="", evfield="", diff=diff, note=note, commit=commit, notetext=numbered(text))
    meta["prompt_chars"] = len(p)
    return p, meta
