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
    # 逐行容錯(code-r1 s3-f3/conf-f1):covered 跟 backlog 同款 append-only jsonl,
    # 一行壞資料不該讓整條迴圈死在選題之前;壞行進 .bad 側檔保留。
    got, bad = set(), []
    for l in p.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        try:
            w = json.loads(l).get("weakness")
        except ValueError:
            bad.append(l); continue
        if w:
            got.add(w)
    if bad:
        import sys
        print(f"covered:跳過 {len(bad)} 行壞資料({p}),{backlog._stash_bad(p, bad)}", file=sys.stderr)
    return got


def mark_covered(covered_path, weakness):
    """orchestrator 判某 gap 已被既有 spec 覆蓋 → 記下,以後 add_gaps/select 都跳過它。"""
    with open(covered_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"weakness": weakness}, ensure_ascii=False) + "\n")


def requeue_unconverged(backlog_path, gap, covered_path, decay=0.7, max_unconv=3):
    """未收斂(撞 cap / cross-family disputed)的 gap:降分 + 累計 unconverged 回 backlog,
    不立即消失(堵『pop 消費後丟失』洞);累計達 max_unconv → covered(放棄自動、留人手動)。
    回 'requeued' 或 'covered'。"""
    n = gap.get("unconverged", 0) + 1
    w = gap.get("weakness", "")
    if n >= max_unconv:
        mark_covered(covered_path, w)
        return "covered"
    g = dict(gap)
    g["unconverged"] = n
    g["value_score"] = round(g.get("value_score", backlog.INIT_SCORE) * decay, 4)
    rows = [r for r in backlog.load_backlog(backlog_path) if r.get("weakness") != w]
    rows.append(g)
    backlog._save(backlog_path, rows)
    return "requeued"


def requeue_pipeline_fail(backlog_path, gap, covered_path, max_fail=3):
    """管線失敗(NO_JSON/PARSE_FAIL/anchor 早退)的 gap:原列原分放回(不是它的錯,
    不降分、不走 add_gaps 免被重置 0.5)+ 累計 pipeline_failures;
    滿 max_fail → covered(放棄自動、留人)——鏡射 requeue_unconverged 的熔斷語意,
    不讓穩定觸發管線死的題無限反覆燒錢。回 'requeued' 或 'covered'。"""
    n = gap.get("pipeline_failures", 0) + 1
    w = gap.get("weakness", "")
    if n >= max_fail:
        try:
            mark_covered(covered_path, w)
            return "covered"
        except OSError as e:
            # covered 本身寫不進(唯讀/磁碟滿)時,熔斷不能變成「拋例外丟件」——
            # 退而求其次留在 backlog(分數不動、計數照累),下輪再試熔斷(r2 d-f1 連環案)
            import sys
            print(f"pipeline 熔斷寫 covered 失敗({e}),gap 退回 backlog 續留", file=sys.stderr)
    g = dict(gap)
    g["pipeline_failures"] = n
    rows = [r for r in backlog.load_backlog(backlog_path) if r.get("weakness") != w]
    rows.append(g)
    backlog._save(backlog_path, rows)
    return "requeued"


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
