---
type: verification
status: pass
date: 2026-10-07
valid_under: Claude Code 2.1.292
revalidate_when: Claude Code 升版,更新說明裡有 mod、plugin 或 hook 相關改動
tags:
  - type/verification
  - status/pass
  - scope/agent-dag
plan_refs:
  - "[[Projects/Claude-mod第二批_計劃]]"
---
# 2026-10-07_Claude-Code-2.1.292-mod異動

白話:Claude Code 2.1.291、2.1.292 的更新說明裡,跟 mod(外掛函式掛鉤)有關的改動,以及它們對 lumos 三支外掛的影響。2.1.291 只修兩個回歸問題,跟 mod 無關;mod 相關的都在 2.1.292。來源是本機 `~/.claude/cache/changelog.md` 的 2.1.292 段。

## 驗了什麼

- 用 2.1.292 對主線 `de1fb54f` 的三支外掛重跑 `claude plugin test` 與 `claude plugin validate`:[[Systems/lumos事件帳]] 29 支、[[Systems/lumos-context]] 6 支、[[Systems/lumos-guard]] 95 支全綠,三支 validate 都合格。新版把「測試註冊的掛鉤裡斷言失敗」改成判紅,三支沒有受影響。

## 跟三支外掛直接有關的改動

- `agent.spawn` 掛鉤開始包含 workflow 代理,並帶它的 run 與 index,外掛可以拒絕它。審查席隔離外掛因此也看得到 workflow 派出的代理(標記判準照舊),事件帳會多記到 workflow 的派工。
- `tool.call` 掛鉤改成看到「參數名修正之後」的輸入;同版 Grep 接受 `file_path` 當 `path`。審查席隔離外掛判搜尋範圍只讀 `path`,照更新說明,修正後才交給掛鉤,不會從 `file_path` 漏掉(實測排在下面的回頭條件)。
- 守衛類掛鉤在另一支外掛的呼叫底下,`.catch` 原本可能被靜默跳過,現在照樣執行。
- 外掛擋下 Write、Edit、NotebookEdit 與單筆 Read、Grep、Glob 時,畫面現在顯示擋下的理由。
- `claude plugin validate`:透過被重新宣告或重新賦值的頂層 `var` 讀 `$.state` 的外掛會被拒絕;同一個常數做大量 `$.state` 呼叫的外掛載入變快。審查席隔離外掛沒有前一種寫法。

## 沒驗的

- workflow 派出的代理經過 `agent.spawn` 時,審查席隔離外掛與事件帳的實際行為:只照更新說明推論。
- 審查席用 Grep 帶 `file_path` 時掛鉤看到的是不是修正後的 `path`:只照更新說明推論。
- 兩件都排在下面的回頭條件裡實測。

## 新能力(目前沒用到)

- `prompt.autocomplete`:外掛可以往輸入框的自動完成清單加項目。
- `$.model.complete` 支援提示快取。
- Agent 工具多了 `effort` 參數,可以指定子代理的推理強度。
- `claude plugin install --marketplace <source>`:需要時先加市集再裝外掛。

## 後續優化方向

REVISIT:2026-11-06 查清 workflow 派工時 agent.spawn 輸入裡 run 與 index 的欄位名,加進事件帳的 spawn 事件(workflow 派出的審查席照擋、事件帳記得到席位,2026-10-07 已實測,見 Verification/2026-10-07_審查席隔離真引擎實測)
REVISIT:2026-11-06 在有 Grep 工具的建置上實測一次審查席用 Grep 帶 file_path 指向席報告暫存處時照樣被擋(2026-10-07 本機建置的子代理沒有 Grep 工具,測不了),結果寫回 Systems/lumos-guard
REVISIT:2026-11-06 決定設計審與代碼審的派工範本要不要用 Agent 的 effort 參數分級(例如資安、合約席拉高,架構對齊用預設);要用就改 skills/lumos-design-loop/templates.md
REVISIT:2026-12-06 決定 lumos install 的外掛安裝要不要改用 claude plugin install --marketplace 一步完成,省掉自己先查再加市集那段
REVISIT:2026-12-06 決定要不要做一支 prompt.autocomplete 外掛,把常用的 lumos 指令放進輸入框自動完成
