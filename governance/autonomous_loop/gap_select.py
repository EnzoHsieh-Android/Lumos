import json, subprocess
from pathlib import Path
from . import backlog

def read_report_gaps(report_path):
    p = Path(report_path)
    if not p.exists(): return []
    try: return json.loads(p.read_text(encoding="utf-8")).get("gaps", []) or []
    except Exception: return []

def pending_exists(mode, pending_dir):
    if mode == "dryrun":
        return any(Path(pending_dir).glob("*.md"))
    out = subprocess.run(
        ["gh", "pr", "list", "--search", "head:auto/spec-", "--state", "open", "--json", "number"],
        capture_output=True, text=True)
    return out.returncode == 0 and out.stdout.strip() not in ("", "[]")

def select(report_path, backlog_path, pending_dir, mode, today):
    gaps = read_report_gaps(report_path)
    backlog.add_gaps(backlog_path, gaps, today)
    if pending_exists(mode, pending_dir):
        return None
    return backlog.pop_top(backlog_path)
