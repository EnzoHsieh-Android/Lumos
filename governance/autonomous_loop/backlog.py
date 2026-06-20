import json
from pathlib import Path

INIT_SCORE = 0.5

def load_backlog(path):
    p = Path(path)
    if not p.exists(): return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

def _save(path, rows):
    Path(path).write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else ""),
        encoding="utf-8")

def add_gaps(path, gaps, today):
    rows = load_backlog(path)
    seen = {r["weakness"]: r for r in rows}
    for g in gaps:
        if g["weakness"] in seen:
            seen[g["weakness"]]["last_seen"] = today
        else:
            row = {"weakness": g["weakness"], "suggestion": g.get("suggestion", ""),
                   "source_date": today, "value_score": INIT_SCORE, "last_seen": today}
            rows.append(row); seen[g["weakness"]] = row
    _save(path, rows)

def decay_and_prune(path, today, rate=0.95, floor=0.2):
    rows = load_backlog(path)
    kept = []
    for r in rows:
        r["value_score"] = r.get("value_score", INIT_SCORE) * rate
        if r["value_score"] >= floor: kept.append(r)
    _save(path, kept)

def pop_top(path):
    rows = load_backlog(path)
    if not rows: return None
    rows.sort(key=lambda r: r.get("value_score", 0), reverse=True)
    top = rows.pop(0); _save(path, rows); return top
