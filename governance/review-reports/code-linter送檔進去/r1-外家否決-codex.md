severity: major
<!-- 來源:codex exec 逐字稿的最終回覆本體(席位唯讀無法寫檔,由編排者原樣切出;逐字稿裡同一份報告會印兩次,這裡只留最終那一份,內容一字未改。完整逐字稿見 job tmp/codex-r1b.log) -->

1. 未對齊時全面降級，推送閘無法補上所有合法宣告

severity: major
引句:「_tier_claims = (lint_claims if filtered_marker is not False else []) + claims」
blocking: 是
位置：`scripts/lumos:20968`

例如宣告 `ruff check src --output-format sarif -o {LINT_SARIF_OUT}`，這是合法且原本能正常運作的指令。只要工作區多一個未追蹤檔，`_lint_aligned` 就回 False；即使 linter 抓到這次新增的問題，只要內建規則沒命中，分級仍降成 standard。

推送閘雖然確實不依賴工作區對齊，卻在 `scripts/lumos:18394` 跳過所有沒有 `{LINT_FILES}` 的命令，最後得到不阻擋的 `not-checked`。因此這類宣告同時失去風險升級與新增告警攔截。應先確認該命令有快照檢查覆蓋，不能一律排除。

2. 信任檢查失敗後仍允許寫入，重新引入更新遺失

severity: major
引句:「if not _trusted_private_dir(lock.parent, ".cache", "lumos", "vault-lock"):」
blocking: 是
位置：`scripts/lumos:11161`

當鎖目錄是 symlink，或目錄可由群組寫入，新分支直接 `yield`，讓兩個程序同時進入讀—改—寫。這也會發生在自行搬移快取目錄的正常環境，不需要攻擊者。

以記憶體替代磁碟、模擬信任檢查失敗與兩次交錯更新，兩次操作都完成，最終只剩 A，B 被覆蓋。受影響的不只是筆記，還包括使用同一把鎖的告警放行紀錄。警告不能維持資料完整性；無法取得可信鎖時應中止寫入。新增測試只檢查函式內是否出現檢查名稱，抓不到這個失效路徑。

3. 共用圍欄解析器會提早關閉圍欄，讓樣板冒充前掃宣告

severity: major
引句:「hits = [ln for _no, ln in _visible_lines(text.split("\n"))」
blocking: 是
位置：`scripts/lumos:5386`

共用函式把同字元、長度足夠的標記當成結尾，沒有要求後面只能有空白。以下字串中的 `~~~python` 不是合法結尾，宣告實際仍在外層圍欄內：

````text
~~~
```
~~~python
preflight-4: ran
```
~~~
````

唯讀、記憶體內重現結果：舊判定為 False，新判定為 True。這會把未執行的前掃算成已執行，污染留痕與滾動窗統計。應修正共用函式的結尾判定，並補上這種反向案例；目前新增測試只覆蓋正常結尾。
