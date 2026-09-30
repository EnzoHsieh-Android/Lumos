#!/bin/bash
# usage: run_judge.sh <unit>   (same flags as homescan-exp/scripts/run_judge.sh)
V="$(cd "$(dirname "$0")/.." && pwd)"
cd "$V/judge-cwd" || exit 1
P="$V/prompts/$1.txt"; O="$V/outputs/$1.json"
[ -s "$O" ] && grep -q '"is_error":false' "$O" && { echo "skip $1"; exit 0; }
s=$(date +%s)
claude -p --model sonnet --tools "" --setting-sources "" --strict-mcp-config --no-session-persistence --output-format json < "$P" > "$O" 2> "$V/outputs/$1.err"
e=$(date +%s)
echo "{\"unit\":\"$1\",\"wall_s\":$((e-s)),\"prompt_bytes\":$(wc -c < "$P")}" > "$V/outputs/$1.wall.json"
echo "done $1 $((e-s))s $(grep -o '"total_cost_usd":[0-9.]*' "$O")"
