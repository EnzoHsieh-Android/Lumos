severity: major

審查範圍是修後版本 20df2187 與修前版本 f14f6808 的 `scripts/lumos`。我把兩版各取出一份,載入真實函式比對。暫存的測試 repo 已用字面路徑刪掉。這份報告的內容與等級沒改,只補了每條底下的 severity 與 blocking 兩行,並把第 4 條的引句換成凍結審材裡的逐字原文。

## Findings

**1. e2e 資料夾裡的 .sql 和 .yml 改動會被當成產品程式掃,風險分級被拉成 high**

severity: major
blocking: 是

- 位置:`_is_test_infra_file`,以及 `_pitfall_diff_collect` 裡由 `_TEST_INFRA_PATH_RE.search(cur_file)` 改成 `_is_test_infra_file(cur_file)` 的那一行。
- 問題:新函式多加了副檔名條件,只有 sh、py 和 node 家族的副檔名才算 infra。路徑落在 e2e 的 `.sql`、`.yml`、`.java` 因此不再被跳過,會被拿去比對「交易包裹」這類產品型樣。修前這一行只看路徑,任何副檔名都跳過。
- 具體例:一個提交加入 `e2e/reset.sql`(內容 `DELETE FROM users`)、`docker-compose.e2e.yml`、`e2e/Helper.java`、`e2e/seed.js`、`e2e/run.py`。
  - 修前:`_pitfall_diff_collect` 回 `claims == []`,tier 是 `standard`。
  - 修後:三個檔各出一條「併發/寫入有沒有交易包裹」claim,tier 變成 `high`,理由是「命中風險型樣或新告警」。`seed.js` 和 `run.py` 照舊被跳過。
  - 後果:只改 e2e 的種子資料或 compose,推送就被要求過代碼審。
- 測試缺口:`t_test_infra_path_e2e_inner_lib_src` 只斷言 `e2e/app/Main.kt` 的 Kotlin 會被掃,沒有任何一條測試涵蓋 e2e 底下的 `.sql` 或 `.yml`。把 `_is_test_infra_file` 改回只看路徑,現有測試對 sql 與 yml 不會紅。
- 歸因:有證據的修復回歸(修前 `claims == []`,修後 3 條)。
- 引句:「Path(file_rel).suffix.lstrip(".").lower() in _INFRA_CODE_EXTS and bool(_TEST_INFRA_PATH_RE.search(file_rel))」

**2. 加了「點後接英數不切」之後,閘與 `pitfalls --check` 兩條路在這類輸入上又不一致**

severity: minor
blocking: 否

- 位置:`_PITFALL_SEND_CLAUSE`。這一版的註解說,邊界字表加上「門先 NFKC、check 不 NFKC」,兩條路才一致。
- 具體例:`請求送出．v1 外部`(全形句點接 v1),`請求送出：//external`,`請求送出.ｖ1 外部`。
  - 修後:原文比對 `external-send` 是 False,NFKC 後是 True。
  - 修前:`．v1` 那條是原文 True、NFKC False,方向相反,也不一致;後兩條兩邊都是 False。
- 原因:全形的 `．`、`：` 在原文裡屬於停止字,NFKC 之後變成半形的 `.`、`:`,後面又接英數或斜線,就被「不切」的規則放過。
- 影響:閘(NFKC 之後)比 check 嚴,只是兩邊結論不同,不會漏攔。
- 測試缺口:`t_door_keyword_send_nfkc_stops_both_paths` 的樣本只有「……」「｡」「﹐」後面接「給客戶」,沒有「全形點加英數」。
- 歸因:`．v1` 是原有問題,方向反轉;`：//` 與 `ｖ1` 兩條是有證據的修復回歸。
- 引句:「(?:[^" + "".join("\\" + c if c in "\\]^-" else c for c in _PITFALL_SEND_STOPS) + r"]|[.:](?=[A-Za-z0-9/])){0,80}?"」

**3. xargs 的選項參數寫法太寬,會把 `echo kill`、`grep kill` 當成殺程序**

severity: minor
blocking: 否

- 位置:`_INFRA_CMD` 的 xargs 分支 `xargs(?:\s+-\S+(?:\s+[^-\s]\S*)?)*\s+`。
- 問題:任何選項後面都可以吞掉一個非橫線的詞當參數,所以 `-t`、`-r`、`-0` 這類不帶參數的旗標,會把後面的指令名吃掉,讓接著的詞落在「指令位置」。
- 具體例,修後 `infra-pid` 全部命中:`xargs -t echo kill`、`xargs -r grep -l kill`、`xargs -n1 echo kill the process`、`xargs -I{} echo kill`。
- 影響:只是多亮一題 infra-pid,不會漏攔。
- 對照:`-I {}`、`-n 1`、`--`、`-P0 -n1`、`--max-args 1`、`-d '\n' -n 1`、`-a file` 修前大多沒命中,修後全部命中,修復有效。`xargs -I {} sh -c 'kill {}'` 修前修後都沒命中(引號內不在指令位置),屬原有限制。
- 歸因:有證據的修復回歸(修前 `xargs -t echo kill` 不亮,修後亮)。
- 引句:「|(?<![A-Za-z0-9_])xargs(?:\s+-\S+(?:\s+[^-\s]\S*)?)*\s+)」

**4. `.kill\s*\(` 漏掉 `os.killpg(`**

severity: minor
blocking: 否

- 位置:`infra-pid` 的 `.kill(` 觸發條件。這一題的問句本身提到「0 與 -1 會打到整個程序群組」。
- 具體例:`os.killpg(pgid, 15)` 修前修後都不命中。Python 打整個程序群組的慣用法正是它。
- 歸因:原有漏查。
- 引句:「(pid 檔可能被別人預放、pid 可能被重用;0 與 -1 會打到整個程序群組)」

**5. 送出的去處詞裡,英文 `vendor` 沒有詞界**

severity: minor
blocking: 否

- 位置:`_PITFALL_SEND_DEST`。
- 具體例:`請求送出 vendor`、`請求送出 Vendors` 修後在 NFKC 之後命中,修前沒命中。前端日常有 vite 的 vendor chunk。`external` 本來也沒詞界(`externalize` 命中,修前就有),只是多加了一個同類詞。
- 影響:只是少排除一次,不會漏攔。
- 歸因:有證據的修復回歸。
- 引句:「|銀行|物流|平台方|partner|vendor|external)"」

## 三問的回答

**① 原問題的修復效果**

- **80/81 字窗口:** `請求送出`加 n 個「甲」加`外部`,n=78、79、80 命中,n=81、82 不命中。向後(外部在送出之前)n≤80 命中。邊界與修前相同。
- **子句邊界:** 逗號、頓號、句號(`．` 與 `。`)與全形逗號都會切句,`請求送出,外部` 與 `請求送出。外部` 不命中。
- **網址與版本號:** `請求送出 api.vendor.com/x 外部`、`v1.2`、`192.168.1.1`、`file.txt 給客戶`,修前因為點被當句界而漏攔,修後命中,修復有效。
- **去處單字:** `表單送出到後端` 修前命中、修後不命中,符合設計。
- **未驗範圍:**
  - 後面不是 `外部` 等名詞的外部服務,例如 `請求送出到 Twilio`,修後不命中。這是設計取捨,沒有另列為 finding。
  - 效能實測 8 萬到 18 萬字的退化輸入(重複送出、`a.b` 重複、一萬個點)全在 0.1 秒內,線性成立。
- **e2e 路徑組合:**
  - `e2e/src/lib/a.ts`、`e2e/lib/a.ts`、`tests/e2e/lib/util.ts` 修後算 infra,修前不算,與修補宣稱一致。
  - `src/e2e/*`、`lib/x/e2e/*`、`apps/web/src/e2e/lib/*` 兩版都不算。
  - `.e2e.` 檔名、`run-e2e.sh`、`E2E/` 大寫都算。
  - `crypto/e2e/` 仍會被誤當 infra,是註解自承的天花板。
  - `src/e2e/` 下的真正 e2e 腳本被當產品碼,是設計取捨。
- **xargs 與 kill:** 見 finding 3 與 4。`.kill (`、`child.kill ('SIGTERM')`、`os.kill(`、`child.kill()` 都命中。

**② 修補處的正常、錯誤與相鄰呼叫路徑**

相鄰的 claims 路徑出了回歸,見 finding 1。棧別鍵(`_stack_key_for_file`)對 `e2e/x.kt` 回非 infra,與 claims 判斷一致,這部分成立。

**③ 新發現在修前、修後各是什麼結果**

四條都有兩版對照,附在各條裡。「未判定」的只有 finding 2 的 `．v1` 那條,修前就不一致,只是方向相反。

最嚴重 severity:major,blocking 共 1 條(finding 1)。
