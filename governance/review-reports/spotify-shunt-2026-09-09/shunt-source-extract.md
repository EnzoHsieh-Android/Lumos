# Spotify portal-ai-plugins / shunt 原始碼節錄(2026-09-09 抓取,main 分支)

來源:https://github.com/spotify/portal-ai-plugins/tree/main/plugins/shunt ;部落格:https://engineering.atspotify.com/2026/9/portal-by-spotify-cut-my-claude-code-token-usage-by-90


## hooks/hooks.json

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/check-file-size"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/check-bash-read"
          }
        ]
      }
    ]
  }
}
```

## hooks/check-file-size

```
#!/bin/bash
# Block full-file reads on large files, redirect to /bulk-reader skill
# Self-contained: all routing logic lives here, no CLAUDE.md needed

MIN_LINES="${SHUNT_MIN_LINES:-350}"
case "$MIN_LINES" in ''|*[!0-9]*) MIN_LINES=350 ;; esac

input=$(cat)

file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
offset=$(echo "$input" | jq -r '.tool_input.offset // empty')
limit=$(echo "$input" | jq -r '.tool_input.limit // empty')

# Allow targeted reads (offset or limit set) — Claude already knows what it needs
if [ -n "$offset" ] || [ -n "$limit" ]; then
  echo '{"decision": "allow"}'
  exit 0
fi

# Allow if file doesn't exist or path is empty
if [ -z "$file_path" ] || [ ! -f "$file_path" ]; then
  echo '{"decision": "allow"}'
  exit 0
fi

# Allow small files — delegation overhead isn't worth it
lines=$(wc -l < "$file_path" 2>/dev/null | tr -d ' ' || echo "0")
if [ "$lines" -le "$MIN_LINES" ]; then
  echo '{"decision": "allow"}'
  exit 0
fi

echo "{\"decision\": \"block\", \"reason\": \"File is ${lines} lines (threshold: ${MIN_LINES}). Use the /bulk-reader skill to delegate this read to AiKA instead of reading it directly. If you need exact content for editing, re-read with an offset/limit for just the section you need.\"}"
```

## hooks/check-bash-read

```
#!/bin/bash
# Block Bash commands that read large files, redirect to /bulk-reader skill
# Catches cat/head/tail/less/more that bypass the Read hook

MIN_LINES="${SHUNT_MIN_LINES:-350}"
case "$MIN_LINES" in ''|*[!0-9]*) MIN_LINES=350 ;; esac

input=$(cat)

command=$(echo "$input" | jq -r '.tool_input.command // empty')
[ -z "$command" ] && { echo '{"decision": "allow"}'; exit 0; }

# Skip piped commands (cat file | grep) — those are targeted reads
echo "$command" | grep -qE '\|' && { echo '{"decision": "allow"}'; exit 0; }

# Skip redirections (cat file > out) — not a read-into-context operation
echo "$command" | grep -qE '>' && { echo '{"decision": "allow"}'; exit 0; }

# Extract file path from read commands, stripping flags (e.g. cat -n, head -100)
file_path=""
if echo "$command" | grep -qE '^(cat|head|tail|less|more) '; then
  # Remove the command name, then strip any flags (-n, -100, --number, etc.)
  args=$(echo "$command" | sed -E 's/^(cat|head|tail|less|more) +//')
  for arg in $args; do
    case "$arg" in
      -*) continue ;;
      *)  file_path=$(echo "$arg" | tr -d '"'"'"); break ;;
    esac
  done
fi

[ -z "$file_path" ] && { echo '{"decision": "allow"}'; exit 0; }
[ ! -f "$file_path" ] && { echo '{"decision": "allow"}'; exit 0; }

lines=$(wc -l < "$file_path" 2>/dev/null | tr -d ' ' || echo "0")
if [ "$lines" -gt "$MIN_LINES" ]; then
  echo "{\"decision\": \"block\", \"reason\": \"File is ${lines} lines (threshold: ${MIN_LINES}). Use the /bulk-reader skill to delegate this read to AiKA instead of cat/head/tail.\"}"
else
  echo '{"decision": "allow"}'
fi
```

## skills/bulk-reader/SKILL.md

```
---
name: bulk-reader
description: "Delegate bulk file reading to AiKA. Use when you need to read files >350 lines, answer questions across 3+ files, or summarize large diffs."
---

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/bulk-read --question "<question>" --paths <file1> [<file2> ...]
```

Each call is independent. To ask a follow-up, ask again with the same `--paths` — the files
go to AiKA, never into your context, so re-sending them costs you nothing.

Verify specific line numbers or exact values before using them in edits.
```

## skills/code-writer/SKILL.md

```
---
name: code-writer
description: "Delegate boilerplate code generation to AiKA. Use for tests, config, docstrings, type stubs, or any generation where >80% is predictable from reference files."
---

```bash
# Generate and write directly to target file
${CLAUDE_PLUGIN_ROOT}/scripts/code-write --spec "<what to generate>" --reference <reference-file> --target <output-path>

# Output to stdout instead (omit --target)
${CLAUDE_PLUGIN_ROOT}/scripts/code-write --spec "<what to generate>" --reference <reference-file>
```

Each call is independent. To build on what was just generated, pass that file as the
`--reference` for the next call.

Review the output and make surgical edits for the ~5-20% that needs Claude-level judgment.
```

## evals/benchmarks.json

```
{
  "description": "Token savings benchmarks — measures Claude context tokens with vs without shunt",
  "token_estimate": "chars / 4 (conservative approximation for code)",
  "benchmarks": [
    {
      "id": 1,
      "name": "single-large-file",
      "description": "Read a 602-line service and summarize exports",
      "type": "bulk-read",
      "question": "What are all the exported items and what do they do?",
      "paths": ["fixtures/websocket-handler.ts"]
    },
    {
      "id": 2,
      "name": "multi-file-cross-read",
      "description": "Read three files and answer a cross-cutting question",
      "type": "bulk-read",
      "question": "Which classes and interfaces are exported across these files, and how do they relate to each other?",
      "paths": ["fixtures/websocket-handler.ts", "fixtures/user-service.ts", "fixtures/order-service.test.ts"]
    },
    {
      "id": 3,
      "name": "source-plus-test",
      "description": "Read source and test pair to understand coverage",
      "type": "bulk-read",
      "question": "What methods does UserService have, and which ones would be covered if we wrote tests following the OrderService test pattern?",
      "paths": ["fixtures/user-service.ts", "fixtures/order-service.test.ts"]
    },
    {
      "id": 4,
      "name": "code-generation",
      "description": "Generate unit tests from reference",
      "type": "code-write",
      "spec": "Write unit tests for UserService following the exact same patterns, structure, and assertions as the OrderService tests.",
      "reference": "fixtures/order-service.test.ts",
      "context_files": ["fixtures/user-service.ts", "fixtures/order-service.test.ts"]
    }
  ]
}
```

## README 節錄(benchmark 表)

3:A Claude Code plugin that shunts I/O-heavy work to AiKA modes, saving 82-94% of tokens on large file reads and boilerplate generation.
44:  "instructions": "You are a precise code analyst. Read the provided files and answer the question concisely. Output structured bullets only. No greetings, no prose, no preambles, no summaries. Lead every bullet with the exact name, type, or line number. Use nested bullets for details. Skip anything the caller did not ask for.",
130:Fires on every `Read` tool call. Blocks full-file reads on files exceeding `MIN_LINES` (default: 350, configurable via `SHUNT_MIN_LINES` env var). Allows through:
149:| `SHUNT_MIN_LINES` | `350` | Line count above which the Read hook blocks and redirects |
152:| `SHUNT_MAX_PAYLOAD_BYTES` | `400000` (`120000` on Linux) | Request ceiling, since input travels through argv |
153:| `SHUNT_TIMEOUT_SECONDS` | `180` | Timeout for one action invocation |
177:Tested against a 162K-line Java monorepo:
181:| Single large file | 4,014 | 33,684 tokens | 5,737 tokens | 82% |
182:| Source + test pair | 7,408 | 75,990 tokens | 4,148 tokens | 94% |
183:| Multi-file cross-service | 1,281 | 16,221 tokens | 821 tokens | 94% |
186:Mean bulk-read savings: **90%**
190:- **No enforcement for code-writer** — only bulk-reader has hook enforcement. Code-writer relies on Claude recognizing when to use it via the skill description.
191:- **Request size** — `aika:invoke-chat` input is passed on the command line, so a request must fit in `ARG_MAX` (1 MB on macOS, shared with the environment; Linux additionally caps a single argument at 128 KiB). shunt refuses anything over `SHUNT_MAX_PAYLOAD_BYTES` with a clear error rather than failing with `E2BIG`. Split into smaller batches.
192:- **Invocation timeout** — shunt caps one action invocation at `SHUNT_TIMEOUT_SECONDS` (default 180). Very large generations can exceed it; raise the timeout or split the spec into smaller calls.
