---
type: system
status: doing
created: 2026-10-06
updated: 2026-10-06
responsibility: Claude 外掛 lumos-context:對話壓縮前在摘要指示後附交棒要求段。不負責:安裝與移除(lumos-cli-lifecycle)、市集檔(lumos事件帳)、壓縮後重新注入規矩(開場 hook)、會談編號(實測不成立,另開題)
aliases: []
about_code:
  - mods/claude/lumos-context/hooks/register.ts
  - mods/claude/lumos-context/hooks/context.test.ts
  - mods/claude/lumos-context/hooks/hooks.json
  - mods/claude/lumos-context/.claude-plugin/plugin.json
  - mods/claude/lumos-context/tsconfig.json
tags:
  - type/system
  - status/doing
  - scope/agent-dag
summary: |-
  WHY:壓縮前改摘要指示用外掛做,不用官方 PreCompact hook [出處:2026-10-06 核對官方 hook 文件] [因:PreCompact 只能讀指示、整個擋,改不了] [不選:壓縮後重新注入規矩——開場 hook 壓縮後本來就會再跑]
  WHY:附加段用詞不帶 lumos 專用名詞 [出處:Claude-mod第二批 設計審第二輪] [因:外掛裝在使用者層,所有專案的壓縮都會附]
  WHY:不做會談編號交給 lumos [出處:2026-10-06 實測] [因:外掛只看得到 claude 啟動時繼承的環境,看不到交給 Bash 的官方編號]
verified_by:
  - "[[Verification/2026-10-06_會談編號外掛實測]]"
---
# lumos-context

白話:對話快滿、要壓縮成摘要之前,這支外掛在給摘要器的指示後面多附一段固定要求,叫它逐字留住使用者的裁定、目前做到哪、還在跑的背景代理、沒提交的改動、待回覆的問題。子代理壓縮時附精簡版。

- 附加段第一行是固定標記行,指示裡已有那一行(整行相等)就不重附;使用者 `/compact <文字>` 的原文一字不改,接在後面。
- 掛鉤自己出錯時照原樣交下去,不影響壓縮。用 `.catch(($, e, next) => next(e))` 寫,不像事件帳外掛在每個掛鉤裡自己吞錯:事件帳只觀察、吞錯就等於放行;這支會改寫壓縮的輸入,能擋流程的掛鉤沒掛 `.catch` 時 `claude plugin validate` 會列出來,`.catch` 裡的 `next` 不會重跑(壓縮已做完就交回原結果)。審查席隔離分支的外掛也是這樣寫。
- 檔:`hooks/register.ts` 是掛鉤與附加段文字,`hooks/context.test.ts` 綁條款 S1–S3 的測試(`claude plugin test` 跑),`hooks/hooks.json` 只載入 register.ts,`.claude-plugin/plugin.json` 是外掛描述檔,`tsconfig.json` 沿用引擎給的型別設定。
- 決策與範圍:[[Projects/Claude-mod第二批_計劃]];會談編號那項為什麼沒做:[[Verification/2026-10-06_會談編號外掛實測]]。
