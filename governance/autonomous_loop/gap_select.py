import json, subprocess
from pathlib import Path
from . import backlog


def read_report_gaps(report_path):
    p = Path(report_path)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("gaps", []) or []
    except Exception:
        return []


def pending_exists(mode, pending_dir):
    if mode == "dryrun":
        return any(Path(pending_dir).glob("*.md"))
    out = subprocess.run(
        ["gh", "pr", "list", "--search", "head:auto/spec-", "--state", "open", "--json", "number"],
        capture_output=True, text=True)
    return out.returncode == 0 and out.stdout.strip() not in ("", "[]")


def load_covered(covered_path):
    """已被既有 spec 覆蓋(orchestrator 判過 skip)的 gap weakness 集合——永久排除,不再選/不重加。"""
    if not covered_path:
        return set()
    p = Path(covered_path)
    if not p.exists():
        return set()
    return {json.loads(l)["weakness"] for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}


def mark_covered(covered_path, weakness):
    """orchestrator 判某 gap 已被既有 spec 覆蓋 → 記下,以後 add_gaps/select 都跳過它。"""
    with open(covered_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"weakness": weakness}, ensure_ascii=False) + "\n")


def select(report_path, backlog_path, pending_dir, mode, today, covered_path=None):
    covered = load_covered(covered_path)
    gaps = [g for g in read_report_gaps(report_path) if g.get("weakness") not in covered]
    backlog.add_gaps(backlog_path, gaps, today)          # covered 的不再加回(堵重加洞)
    if pending_exists(mode, pending_dir):
        return None
    while True:                                           # pop top,丟棄殘留的 covered
        top = backlog.pop_top(backlog_path)
        if top is None:
            return None
        if top.get("weakness") not in covered:
            return top
