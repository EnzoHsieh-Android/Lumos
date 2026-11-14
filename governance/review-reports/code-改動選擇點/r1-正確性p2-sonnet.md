severity: major

(派工詞說明材料有分段、後段可能改過前段,所以我以 repo 現況 `scripts/lumos` 為準。repo 裡 `killing_test` 帶平台前綴的寫法和 patch 裡的舊版不同。我在臨時副本跑了 `-k choice_kill`,51 個全綠。)

## c21 有弱證據的 survived 被記成 survived,規格要求記 no_result(對應 be-api-compat 無關,屬規格對照)
severity: major
blocking: 是——測試抓不住這個改壞(51 個 choice_kill 測試照綠),而它保護的是 S9 的必要行為。

- **輸入**:一支守的測試的壞法那次測試是綠的(`survived`),但那條配方被 `cmd_guard_kill` 標成 weak。最實際的來源是 `_mtime_unsure`(寫檔後修改時間沒錯開,Gradle 可能吃到舊的編譯快取,壞法其實沒被編進去)。
- **路徑**:`_KillHooks.flush` 把 `weak=True` 交給 `on_row`。`_ChoiceKillRun.on_row` 存進 `p["rows"]`,每支測試都有列後呼叫 `finish`。`_choice_kill_judge` 的三個檢查只看 `r["verdict"] in _CHOICE_JUDGE_WEAK`(killed_unattributed、killed、drifted、error)。`survived` 不在清單裡,最後 `all survived` 成立,回 `survived`。
- **預期 vs 實際**:S9 寫「沒有強 killed 而有弱證據 … 應記 no_result」,〈用詞〉殺掉判定的清單也明列 `weak`。實際是帶 weak 的 survived 被記成 `survived`,後果有三個:
  - 壞法沒被編進去,卻誤判成「沒有測試守著」。
  - 作者被要求寫條款或放行。
  - 它進入回報上限的抽中集合,可能擋推送。
- **重現**(臨時副本、in-proc,已清掉):
  ```
  m._choice_kill_judge([("kotlin-junit","alphaCase")],
    {("kotlin-junit","alphaCase"): {"verdict":"survived","weak":True,"weak_why":["修改時間沒錯開(可能吃到舊的編譯快取)"],"compile_error":False}})
  → ('survived', None, '', '', [])      # 預期 ('no_result', None, '…', …)
  ```
- 修法方向:`survived` 且 `r.get("weak")` 要落進「弱證據」那一檢。

引句:「("弱證據或結果不明", lambda r: r["verdict"] in _CHOICE_JUDGE_WEAK))」
file: `scripts/lumos:77633`(`_choice_kill_judge`,repo 現況)
file: `scripts/lumos:28392`(`_KillHooks.flush` 已把 `weak` 交出來,`_choice_kill_judge` 沒用它判 survived)

## c22 守的測試雜湊只含測試名,原地補強測試內容不會讓 survived 的行自動重跑
severity: minor
blocking: 否——有 `--only` 可繞,訊息也有指引,不是破壞合約。

- **輸入**:某行 `survived`。作者在同一支綁定測試裡加斷言(測試名不變),提交後跑 `lumos choice-kill`。
- **路徑**:`_choice_tests_sha` 只雜湊「平台:測試名」。`_choice_kill_pick` 判 `evs[-1].get("tests_sha") == tests_sha`,結果進 `carried`。
- **實際**:印「上次存活、守的測試沒變,這次不重跑(補測試或改綁後會自動重跑…)」,rc 1,那一行不重跑。
- **為什麼是 minor**:這符合 S11 字面的「守的測試集合雜湊」。但「補強測試」最常見的做法就是改測試內容,訊息讓人以為補測試會自動重跑。只有 `--only` 能重跑。
- **誠實邊界**:我沒實跑這條路徑,是讀碼推出來的。

引句:「keys = sorted({f"{t['plat']}:{t['name']}" for t in tests})」
file: `scripts/lumos:77470`(`_choice_tests_sha`;patch 對應 `r1-p2.patch:968`)

## 已走過、判對的點(都沒有具體失敗輸入)
- **兩條 ★INVARIANT★(guard kill 輸出與 rc 不變)**:不傳新參數時 `_KillHooks.on` 為 False,`between`、`flush`、`note` 全部直接 return。`_kill_log_rows` 是原樣抽出,`source` 只在有值時才寫。`verdicts` 過濾 `skipped` 只在 `stop_group_on` 時才會出現那種列。rc 優先序沒動。
- **Ctrl-C 與時限**:`finish` 在 `flush` 之後才檢查 `should_stop`,上一條的列一定先交出。`_KillHalt` 從 `with _isolated_worktree` 跳出,`finally` 收掉工作樹並從 `_KILL_WT_LIVE` 拿掉。被中斷或時限到了的半套壞法不記帳,對得上 S12。
- **lint-waive**:鍵是 `choice:<檔>:<fp>`,從右邊切最後一個冒號,檔名含冒號沒問題。理由先過 10 實字檢查再過 `<標籤>:<理由>` 檢查。重複放行回 rc 1。
- **situation-rule `--point`**:
  - 冪等:先驗 `--point` 與 `--seg` 互斥,再用 `new_sha` 比對人裁事件,重跑回 rc 0。
  - 帳:point 事件用 `_spec_gate_ruled_events` 排除,不免預期值表列;`_gov_situation_spec_counts` 也排除,不重複計數。
  - 條款已存在時只記事件、不插第二條。
- **既有情境段路徑**:`_situation_rule_platform_for` 抽出時,`plat == pdata["default_platform"]` 條件讓情境段路徑的行為不變。
- **圖譜鏡頭**:這次沒附固定席節點(鏡頭計算超時),我沒有逐條判的對象。以上是我自己讀 diff 與 repo 的判斷。

最嚴重:major;blocking 共 1 條
