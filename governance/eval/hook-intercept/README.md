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

## 追測:updatedInput 能不能改寫派工詞(2026-09-03,同版本)

把 hook 的 command 換成一支腳本,讀 stdin、命中條件時輸出:

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow",
 "updatedInput":{ ...原 tool_input,但 prompt 後面接上要注入的文字... }}}
```

然後派一個子代理,問它「你收到的必查清單有哪幾項」——★派工詞本身不可提到任何清單內容★,
它列得出來就證明注入生效。

**結果:✅ 有效。** 子代理原封不動列出只存在於注入文字裡的三個節點名。

★兩條實測出來的約束★:
1. 注入內容寫成「暗號是 XXXX」這種形狀時,子代理**拒答並指認為提示注入測試**;
   換成長得像真實清單的內容才成功。**注入內容必須看起來是正當的系統附加。**
2. 這個機制與提示注入技術上同一件事,差別只在善意——該 hook 本身**必須進錨點保護清單**。
