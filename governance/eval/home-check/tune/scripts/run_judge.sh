#!/bin/bash
# usage: run_judge.sh <cid> <variant>
EXP="$(cd "$(dirname "$0")/.." && pwd)"
cd "$EXP/judge-cwd" || exit 1
P="$EXP/prompts/$1.$2.txt"; O="$EXP/outputs/$1.$2.json"
[ -s "$O" ] && grep -q '"is_error":false' "$O" && { echo "skip $1.$2"; exit 0; }
s=$(date +%s)
claude -p --model sonnet --tools "" --setting-sources "" --strict-mcp-config --no-session-persistence --output-format json < "$P" > "$O" 2> "$EXP/outputs/$1.$2.err"
e=$(date +%s)
echo "{\"cid\":\"$1\",\"variant\":\"$2\",\"wall_s\":$((e-s)),\"prompt_bytes\":$(wc -c < "$P")}" > "$EXP/outputs/$1.$2.wall.json"
echo "done $1.$2 $((e-s))s"
