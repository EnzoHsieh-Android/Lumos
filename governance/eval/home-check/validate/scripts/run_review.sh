#!/bin/bash
# usage: run_review.sh <rid>   cwd = code snapshot dir of that commit (after/ before/)
V="$(cd "$(dirname "$0")/.." && pwd)"
row=$(awk -F'\t' -v r="$1" '$1==r' "$V/review/sample.tsv")
repo=$(echo "$row" | cut -f3); c=$(echo "$row" | cut -f4)
cd "$V/review/snap/${repo}_${c}" || exit 1
P="$V/review/prompts/$1.txt"; O="$V/review/outputs/$1.json"
[ -s "$O" ] && grep -q '"is_error":false' "$O" && { echo "skip $1"; exit 0; }
claude -p --model sonnet --tools "Read,Grep,Glob" --allowedTools "Read,Grep,Glob" --setting-sources "" --strict-mcp-config --no-session-persistence --max-budget-usd 1.0 --output-format json < "$P" > "$O" 2> "$V/review/outputs/$1.err"
echo "done $1 $(grep -o '"total_cost_usd":[0-9.]*' "$O")"
