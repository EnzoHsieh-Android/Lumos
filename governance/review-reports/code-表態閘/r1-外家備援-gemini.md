severity: major

### f1 治理帳鑑別子碰撞導致表態統計失效
severity: major
blocking: 否
file: `scripts/lumos:4731`
引句:「"token": ((d.get("ts", "") + d.get("note", "")) if (d.get("gate") == "canary" and d.get("kind") == "blocked") else d.get("ts", "") if (d.get("gate") == "code-loop" and d.get("kind") in ("dispositions", "recall-miss")) else ""),」
`_codeloop_git_ts` 拿的是 commit 的時間戳而非系統時間,若對同一 commit 重複執行 `dispositions`(如修正填錯的內容),治理帳內多筆記錄的 `ts` 會完全相同。由於 `gov` 載入時以此 `token` 進行去重,導致 `gov --stats` 的「棧別提問表態」統計段落會丟失歷史記錄,僅剩一筆。

### f2 棧別觸發正規化漏掉行內註解
severity: minor
blocking: 否
file: `scripts/lumos:15277`
引句:「if not s or s.startswith(("#", "//", "--", "/*", "*")):」
`_stack_norm_line` 僅過濾以註解符號開