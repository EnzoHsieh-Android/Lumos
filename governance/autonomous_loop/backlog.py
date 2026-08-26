import json, os
from pathlib import Path

INIT_SCORE = 0.5

def _stash_bad(src_path, bad_lines):
    """壞行進 .bad 側檔保留,且**已在側檔的行不重覆疊**(r2 d-f4:covered 永遠 append-only
    無整檔重寫,同一壞行每次 load 都會再撈一次,無界增長)。回傳描述字串供 log。"""
    p = Path(src_path)
    bad_file = p.with_name(p.name + ".bad")
    try:
        seen = set(bad_file.read_text(encoding="utf-8").splitlines()) if bad_file.exists() else set()
        fresh = [l for l in bad_lines if l not in seen]
        if fresh:
            with open(bad_file, "a", encoding="utf-8") as f:
                for l in fresh:
                    f.write(l + "\n")
        return f"已撈到 {p.name}.bad 保留(新 {len(fresh)} 行/已在檔 {len(bad_lines)-len(fresh)} 行)"
    except OSError as e:
        return f"連 .bad 側檔都寫不進({e})——壞行只剩這行 log 有記錄"


def load_backlog(path):
    """逐行讀 backlog;壞行跳過並在 stderr 記一句(一行壞資料不該讓整條迴圈當機——
    set -euo pipefail 下未捕捉例外=從此天天早退,auto-loop-repair-v2 s2-f5)。"""
    p = Path(path)
    if not p.exists(): return []
    rows, bad = [], []
    for l in p.read_text(encoding="utf-8").splitlines():
        if not l.strip(): continue
        try:
            rows.append(json.loads(l))
        except ValueError:
            bad.append(l)
    if bad:
        import sys
        # 壞行不能只是跳過——之後任何正常 _save 都會整檔覆寫,等於把它無聲永久刪除
        # (code-r1 ext-f3)。撈到 .bad 側檔保留(去重),人可回收。
        print(f"backlog:跳過 {len(bad)} 行壞資料({path}),{_stash_bad(p, bad)};檔案疑似寫到一半被中斷,值得看一眼", file=sys.stderr)
    return rows

def _save(path, rows):
    """原子寫:先寫暫存檔再整檔替換——寫到一半被中斷(launchd 逾時/睡眠)不會留半個檔。"""
    p = Path(path)
    tmp = p.with_name(f"{p.name}.{os.getpid()}.tmp")   # 帶 PID:並行不共用暫存檔(主防線是整跑鎖)
    tmp.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else ""),
        encoding="utf-8")
    os.replace(tmp, p)

def add_gaps(path, gaps, today):
    rows = load_backlog(path)
    seen = {r["weakness"]: r for r in rows}
    for g in gaps:
        if g["weakness"] in seen:
            r = seen[g["weakness"]]
            r["last_seen"] = today
            # 再現=世界重複投票:分數補回初始(不超過、不疊加)。連日被點名維持 0.5 是
            # 接受的行為——真做不動的由 pipeline_failures / unconverged 熔斷接住。
            r["value_score"] = max(r.get("value_score", INIT_SCORE), INIT_SCORE)
        else:
            row = {"weakness": g["weakness"], "suggestion": g.get("suggestion", ""),
                   "source_date": today, "value_score": INIT_SCORE, "last_seen": today}
            rows.append(row); seen[g["weakness"]] = row
    _save(path, rows)

def pop_top(path):
    """三鍵排序:分數 → last_seen 新者 → source_date 新者。同分同日時新題贏,
    不再依賴 stable sort 的插入位置(153 筆凍分變 FIFO 的病根之一)。"""
    rows = load_backlog(path)
    if not rows: return None
    rows.sort(key=lambda r: (r.get("value_score", 0),
                             r.get("last_seen", ""),
                             r.get("source_date", "")), reverse=True)
    top = rows.pop(0); _save(path, rows); return top

def decay_and_prune(path, today, rate=0.95, floor=0.2, days=1):
    """衰減 days 個日份(rate**days),低於 floor 的淘汰。回傳被淘汰的列——
    呼叫端負責先歸檔後刪(見 daily_decay);直接呼叫本函式會就地存檔(相容舊測試)。"""
    rows = load_backlog(path)
    kept, pruned = [], []
    for r in rows:
        r["value_score"] = r.get("value_score", INIT_SCORE) * (rate ** days)
        (kept if r["value_score"] >= floor else pruned).append(r)
    _save(path, kept)
    return pruned

def daily_decay(path, archive_path, state_path, today, rate=0.95, floor=0.2):
    """冪等的每日衰減:sidecar 狀態檔記上次衰減日,同日重跑不動(skip-continue 會讓
    select() 一天被叫多次,衰減不能掛那裡);先把淘汰列寫進 archive、讀回自驗
    (回報成功≠已落盤),自驗過才縮 live——中斷最壞重複、不會遺失。
    回傳 {"status": ok|noop|archive-fail, "days": n, "pruned": n}。"""
    import datetime, sys
    state = Path(state_path)
    last = None
    if state.exists():
        try:
            last = json.loads(state.read_text(encoding="utf-8")).get("last_decayed")
        except ValueError:
            last = None   # 狀態檔壞了:當第一次跑(衰減 1 日份),不當機
    days = 1
    if last:
        try:
            days = (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(last)).days
        except ValueError:
            days = 1
        if days <= 0:
            return {"status": "noop", "days": 0, "pruned": 0}
    rows = load_backlog(path)
    kept, pruned = [], []
    for r in rows:
        r = dict(r)
        r["value_score"] = r.get("value_score", INIT_SCORE) * (rate ** days)
        (kept if r["value_score"] >= floor else pruned).append(r)
    if pruned:
        arch = Path(archive_path)
        try:
            # 前次中斷可能留下沒換行的半行:先補一個換行,新列不黏在壞行後面(code-r1 s3-f2 附帶)
            prefix = ""
            if arch.exists():
                old = arch.read_text(encoding="utf-8")
                if old and not old.endswith("\n"):
                    prefix = "\n"
            with open(arch, "a", encoding="utf-8") as f:
                f.write(prefix)
                for r in pruned:
                    rec = dict(r); rec["archived"] = today; rec["reason"] = "decay-floor"
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            # 讀回自驗:只 parse「自己剛寫的尾段」——歷史壞行不關這批的事,掃全檔會讓
            # 一行陳年壞資料把衰減永久卡死且不自癒(code-r1 s3-f2 blocker)
            tail_lines = [l for l in arch.read_text(encoding="utf-8").splitlines() if l.strip()][-len(pruned):]
            tail = [json.loads(l) for l in tail_lines]
            if [t.get("weakness") for t in tail] != [r.get("weakness") for r in pruned]:
                raise OSError("讀回內容對不上")
        except (OSError, ValueError) as e:
            print(f"backlog 歸檔失敗({e}):live 不動、狀態不前進,明天重試——絕不無痕淘汰", file=sys.stderr)
            return {"status": "archive-fail", "days": days, "pruned": 0}
    # state 先落、live 後縮(都原子)。中斷在兩者之間=今天標了已衰但 live 沒縮=少衰一天,
    # 方向安全;反過來(先縮後標)中斷=明天對已衰過的列再衰一次,分數靜默多掉
    # (code-r1 ext-f4/s2-f4——原實作就是錯的那個方向)。
    state_tmp = state.with_name(state.name + ".tmp")
    state_tmp.write_text(json.dumps({"last_decayed": today}) + "\n", encoding="utf-8")
    os.replace(state_tmp, state)
    _save(path, kept)
    return {"status": "ok", "days": days, "pruned": len(pruned)}
