原 finding 裁決：不成立；本次分支把錯誤手冊改為符合實作的判準，沒有引入互斥說明。

severity: clean  
blocking: 否  
引句:「只有結論 green 才算過;red 要處理;timeout/no-run/unavailable/undetermined 都不算綠,rc0 不等於 CI 成功」  
file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:32`

理由：

- `scripts/lumos` 相對 `origin/main...HEAD` 無差異；舊 help 不是提交 `7506c90b` 引入。
- `origin/main` 的既有指南早已寫明「rc0 不等於綠」。file: `skills/lumos-code-loop/SKILL.md:55`
- `cmd_ci_wait` 的契約明列未定、逾時、no-run、工具缺席皆回 rc0。file: `scripts/lumos:41938`
- JSON 明確另給 `verdict`，不能只靠 rc 判定。file: `scripts/lumos:41944`
- 原報告的重現：
  ```sh
  ! python3 scripts/lumos ci-wait --help | rg -q '綠 rc0/紅 rc1'
  ```
  實際 `rc=0`，沒有翻紅。`ci-wait --help` 顯示的是空格版「綠 rc0 紅 rc1」，來源為 file: `scripts/lumos:48748`；斜線版只存在頂層 parser 摘要。file: `scripts/lumos:49530`

無落檔的 in-memory probe 實際輸出：

```json
{"case": "green", "rc": 0, "verdict": "green"}
{"case": "red", "rc": 1, "verdict": "red"}
{"case": "undetermined", "rc": 0, "verdict": "undetermined"}
{"case": "no-run", "rc": 0, "verdict": "no-run"}
{"case": "timeout", "rc": 0, "verdict": "timeout"}
{"case": "unavailable", "rc": 0, "verdict": "unavailable"}
```

對應 return 路徑：file: `scripts/lumos:41971`、`scripts/lumos:41985`、`scripts/lumos:41993`、`scripts/lumos:42025`、`scripts/lumos:42042`、`scripts/lumos:42051`。

範圍外舊 CLI 教學風險仍成立，建議另案修正，不阻擋本分支。

severity: major  
blocking: 否  
引句:「push 後等 CI 結論,綠 rc0 紅 rc1;結果進治理帳。別用 gh run list。」  
file: `scripts/lumos:48748`

這句雖未邏輯斷言「rc0 必為 green」，但省略五種非 green 的 rc0；依一般 shell 成功碼慣例，呼叫者可能寫成 `lumos ci-wait && 發布`，把未確認的 CI 當成功。頂層摘要也有同型風險。file: `scripts/lumos:49530`

能翻紅的最小重現：

```sh
python3 scripts/lumos ci-wait --help |
  rg -q 'rc0 不等於|只有結論 green'
```

目前 `rc=1`。建議同步修正 `_COMMAND_GUIDE["ci-wait"]`、parser 摘要及函式 docstring，明示「只認 JSON `verdict=green`；rc0 也可能是其他狀態」。

總結：最嚴重 severity major（範圍外舊風險），blocking 0 條；本次 diff 已讀，無 finding。
