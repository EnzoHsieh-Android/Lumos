import json

def extract_json(s):
    """從 orchestrator result 文字裡提取最後一個合法 JSON object。
    容錯:result 常在真 JSON 前夾敘述,且敘述可能含 {clean,minor} 這種非 JSON 花括號。
    從最後一個 '{' 往前試,回第一個能 json.loads 成 dict 的。"""
    starts = [i for i, c in enumerate(s) if c == '{']
    for start in reversed(starts):
        for end in range(len(s), start, -1):
            if s[end - 1] != '}':
                continue
            try:
                obj = json.loads(s[start:end])
                if isinstance(obj, dict):
                    return obj
            except Exception:
                continue
    return None


def _num(v):
    """只認真數字。字串/None/list 一律回 None——寧可沒有,不要記出假數字。"""
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def extract_cost(o):
    """從 `claude -p --output-format json` 的頂層物件抽這輪的成本。

    這些數字 CLI 本來就吐,以前沒人接。回 dict;完全抽不到任何一項回 None。
    ★fail-open★:形狀一變就回 None,絕不讓記帳失敗把 loop 打斷。

    tokens 只算 input+output,★不含 cache_read★——快取讀取的計價與新 token 差一個
    量級,加進去會把「這輪多貴」灌水。cache_read 另存一欄供日後分析。
    """
    if not isinstance(o, dict):
        return None
    usd = _num(o.get("total_cost_usd"))
    ms = _num(o.get("duration_ms"))
    turns = _num(o.get("num_turns"))
    u = o.get("usage")
    tokens = cache_read = None
    if isinstance(u, dict):
        i, out = _num(u.get("input_tokens")), _num(u.get("output_tokens"))
        if i is not None or out is not None:
            tokens = (i or 0) + (out or 0)
        cache_read = _num(u.get("cache_read_input_tokens"))
    wallclock_min = round(ms / 60000) if ms is not None else None
    if usd is None and wallclock_min is None and tokens is None and turns is None:
        return None
    return {"usd": usd, "wallclock_min": wallclock_min,
            "tokens": tokens, "turns": turns, "cache_read": cache_read}


def cost_cli_args(cost):
    """把成本轉成 `lumos canary record` 的既有欄參數。

    ★只用既有的兩個欄(--tokens / --wallclock-min),不發明新欄★。沒量到的不送 0
    冒充量過——少一個參數,帳上就是空的,一眼看得出沒量。
    """
    if not isinstance(cost, dict):
        return []
    args = []
    if cost.get("tokens") is not None:
        args += ["--tokens", str(int(cost["tokens"]))]
    if cost.get("wallclock_min") is not None:
        args += ["--wallclock-min", str(int(cost["wallclock_min"]))]
    return args
