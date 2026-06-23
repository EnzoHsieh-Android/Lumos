"""放行前跨家族複核:呼叫 qwen3-max(DashScope 國際 endpoint)補 opus 同門盲點。

設計見 docs/design/2026-06-22-cross-family-audit.md。
- 無第三方依賴(僅標準庫 urllib),與既有模組一致。
- verdict 判定在 orchestrator(prompt 層);本模組只回 status + worst_severity。
"""
import json
import os
import re
import urllib.request
import urllib.error
import ssl
from pathlib import Path

ENDPOINT = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
_SEV_ORDER = {"clean": 0, "minor": 1, "major": 2, "blocker": 3}


def _ssl_context():
    """探測可用 cert bundle 建 SSL context。homebrew python(orchestrator PATH 優先)常無 cert
    (ssl cafile=None)→ 不指定會 CERTIFICATE_VERIFY_FAILED;探測系統/certifi cert 修之。"""
    cands = []
    d = ssl.get_default_verify_paths()
    if d.cafile:
        cands.append(d.cafile)
    try:
        import certifi
        cands.append(certifi.where())
    except ImportError:
        pass
    cands += ["/etc/ssl/cert.pem", "/private/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"]
    for p in cands:
        if p and os.path.exists(p):
            return ssl.create_default_context(cafile=p)
    return ssl.create_default_context()


def _parse_worst(text):
    """抓「最嚴重 severity = X」;抓不到 → 掃內文最高 severity;全無 → clean。"""
    m = re.search(r"最嚴重\s*severity\s*[=:：]?\s*\*{0,2}(clean|minor|major|blocker)", text)
    if m:
        return m.group(1)
    found = [s for s in _SEV_ORDER if s in text]
    return max(found, key=lambda s: _SEV_ORDER[s]) if found else "clean"


def _read_evidence(canary_log_path, loop_id):
    """讀 canary-log,過濾 loop==loop_id(沿用 confidence_report 讀法),組收斂證據。"""
    p = Path(canary_log_path)
    if not p.exists():
        return ""
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("loop") == loop_id:
            out.append(f"{r.get('kind')}/{r.get('severity')}: {r.get('note', '')}")
    return "\n".join(out)


def run_cross_audit(spec_text, canary_log_path, loop_id, ground_truth,
                    key_path="~/.config/ai-daily/qwen_api_key",
                    model="qwen3-max", timeout=120, temperature=0.2):
    """回傳 dict,status 三態:
      {"status":"ok","worst_severity":<sev>,"findings":str,"usage":dict}
      {"status":"degraded","worst_severity":None,"reason":"no_key"}
      {"status":"degraded","worst_severity":None,"reason":"http_<code>"|"timeout"|"error:..."}
    """
    kp = Path(os.path.expanduser(key_path))
    if not kp.exists():
        return {"status": "degraded", "worst_severity": None, "reason": "no_key"}
    key = kp.read_text(encoding="utf-8").strip()
    evidence = _read_evidence(canary_log_path, loop_id)
    prompt = (
        "你是獨立設計審計員。基於提供的真實代碼審以下 spec,逐節找洞"
        "(未定義詞/壞引用/不一致/矛盾/可執行性 gap),每條標 severity。\n"
        f"=== 收斂證據(逐輪)===\n{evidence}\n"
        f"=== ground-truth 真實代碼片段 ===\n{ground_truth}\n"
        f"=== 待審 SPEC ===\n{spec_text}\n"
        "最後一行輸出「最嚴重 severity = <clean|minor|major|blocker>」。")
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        return {"status": "degraded", "worst_severity": None, "reason": f"http_{e.code}"}
    except Exception as e:
        reason = "timeout" if "timed out" in str(e).lower() else f"error:{e}"
        return {"status": "degraded", "worst_severity": None, "reason": reason}
    findings = data["choices"][0]["message"]["content"]
    return {"status": "ok", "worst_severity": _parse_worst(findings),
            "findings": findings, "usage": data.get("usage", {})}
