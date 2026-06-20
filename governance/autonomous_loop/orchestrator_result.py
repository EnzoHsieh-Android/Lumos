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
