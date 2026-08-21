#!/usr/bin/env bash
# external-seat.sh — 外家審查席單發呼叫(Gemini API)。
# 用法:  scripts/external-seat.sh <prompt檔> [輸出檔]
#   模型: $EXTERNAL_SEAT_MODEL(預設 gemini-3-flash-preview;pro 系本 key 額度=0,勿預設)
#   金鑰: $GEMINI_API_KEY 或 ~/.gemini/.env
# 為什麼存在:外家席歷來每 session 手打 curl,2026-08-20 實測連摔兩次逾時(預設 30-60s 不夠,
# flash 實測 12s+ 起跳)。固定成腳本=呼叫方式不再漂。恆單發無狀態,不落任何帳——記帳歸 loop 紀律。
set -euo pipefail
PROMPT_FILE="${1:?用法: external-seat.sh <prompt檔> [輸出檔]}"
OUT="${2:-/dev/stdout}"
MODEL="${EXTERNAL_SEAT_MODEL:-gemini-3-flash-preview}"
if [[ -z "${GEMINI_API_KEY:-}" && -f "$HOME/.gemini/.env" ]]; then
  set -a; . "$HOME/.gemini/.env"; set +a
fi
: "${GEMINI_API_KEY:?無 GEMINI_API_KEY(env 或 ~/.gemini/.env)}"
python3 - "$PROMPT_FILE" "$OUT" "$MODEL" "$GEMINI_API_KEY" <<'PY'
import sys, json, subprocess
pf, out, model, key = sys.argv[1:5]
with open(pf, encoding="utf-8") as _f:
    prompt_text = _f.read()
body = json.dumps({"contents": [{"parts": [{"text": prompt_text}]}],
                   "generationConfig": {"temperature": 0.3, "maxOutputTokens": 8000}})
r = subprocess.run(["curl", "-sS", "-m", "180",
    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
    "-H", "Content-Type: application/json", "-d", body], capture_output=True, text=True)
try:
    d = json.loads(r.stdout)
except ValueError:
    sys.exit(f"ERROR: 非 JSON 回應(逾時/網路):{r.stdout[:200]} {r.stderr[:200]}")
if "candidates" not in d:
    sys.exit(f"ERROR: {json.dumps(d.get('error', d), ensure_ascii=False)[:300]}")
txt = d["candidates"][0]["content"]["parts"][0]["text"]
if out == "/dev/stdout":
    print(txt)
else:
    with open(out, "w", encoding="utf-8") as _f:
        _f.write(txt)
u = d.get("usageMetadata", {})
print(f"[external-seat] model={model} tokens={u.get('totalTokenCount')} tier={u.get('serviceTier')}", file=sys.stderr)
PY
