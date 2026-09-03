# 派工攔截點實測(2026-09-03)原始證據

## 怎麼重跑

1. 備份 `~/.claude/settings.json`。
2. 在 `hooks.PreToolUse` 陣列**追加**(不是取代)一條:

```json
{ "matcher": "Agent|Task|Subagent",
  "hooks": [{ "type": "command",
              "command": "{ echo \"--- fired $(date +%T)\"; cat; echo; } >> /tmp/hooktest.log",
              "timeout": 10 }] }
```

3. 派任何一個子代理,看 `/tmp/hooktest.log`。
4. 測「擋不擋得住」:把 command 換成一支腳本,讀 stdin、命中條件時印

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"擋下的理由"}}
```

不命中就印 `{}`。
5. 測完把追加的那條移除,跟備份逐欄比對確認沒動到別的。

## 2026-09-03 實測結果(Claude Code 2.1.259)

- ✅ `PreToolUse` matcher 匹配得到派子代理,`tool_name` = **`Agent`**
- ✅ `tool_input` 帶 **`prompt`(派工詞全文)**、`description`、`subagent_type`、`model`
  (實測方式=派工詞裡埋哨兵字串 `SENTINEL-9f3a`,在 hook 收到的 JSON 裡逐字出現)
- ✅ 回 `permissionDecision: "deny"` → ★該次派工完全沒有執行★,`permissionDecisionReason` 原文回饋給模型
- ✅ 對照組(不命中條件)照常派出、正常回覆 → 不誤擋
- ❌ `SubagentStart` 也會 fire,但 input ★只有 `agent_id` / `agent_type`,沒有派工詞★ → 這條路不能用

原始 hook 輸出見 `2026-09-03-raw-hook-log.txt`。
