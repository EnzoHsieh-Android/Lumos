severity: minor

## Finding 1
severity: minor
blocking: 否

規則的呼叫名比對 `^(Outlined)?TextField\s*\(|^BasicTextField2?\s*\(` 的兩個 `^` 錨點沒有任何案例釘住。我在規則副本上把兩個 `^` 拿掉,再對 `_KTSEC_CASES` 裡全部 26 個密碼欄案例(C95 到 C120)跑一遍,預期值零差異。
- 把 `^` 拿掉後,`MyTextField(…PasswordVisualTransformation())` 和 `androidx.compose.material3.TextField(…)` 從不報變成各報一次。〈天花板〉明寫這兩種是漏報,而且形狀已凍結雜湊。
- 錨點被改壞時,測試不會翻紅,凍結形狀量出的 7.5% 誤報率也跟著失準。
- 受影響的是〈天花板〉對「自訂元件名、完整套件名」的說法。預期值表 S1 沒有列這兩種,所以這條不算驗收條款漏測。
- 歸因:有證據的原有漏查。修補只動了測試和計劃兩支檔,規則檔與型錄在 84a2a61 到 b3561e6 之間 `git diff --stat` 為空。
- 重現:規則取自 `compose.yml` 末段,見 `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第三批/審查二-sonnet/mut/` 的 `mm.py`、`run.py`、`x/`。修前修後規則相同,結果相同(原版 0 筆,拿掉錨點 2 筆,26 案全綠)。
- 修法建議:加一例 `MyTextField(…)` 預期不報,把天花板那句釘住。

引句:「regex: '^(Outlined)?TextField\s*\(|^BasicTextField2?\s*\('」
file: `configs/ast-grep/kotlin-android/rules/compose.yml:` 第三批新增那段(r2-snapshot.patch 的 compose.yml hunk)

## Finding 2
severity: minor
blocking: 否

〈天花板〉說字面 `KeyboardOptions(…)` 會漏報的情形是「括號裡有函式呼叫」和「註解裡有括號」。但規則實際用 `\([^()]*\)`,括號裡出現任何一對括號都不報,不限於函式呼叫。
- 輸入:`TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Text, imeAction = if (x) ImeAction.Done else ImeAction.Next))`。
- 這裡的 `if (x)` 不是函式呼叫,實跑卻不報(我的 b12 案例)。keyboardType 明明是 Text,是漏報。
- 同樣的 `/* KeyboardType.Password */` 區塊註解實跑也不報(b05)。這個屬於天花板已列的「註解寫到密碼鍵盤」。
- `// plain (note)` 這種註解有括號,實跑漏報(b03),天花板已列。
- 歸因:有證據的原有漏查。規則與天花板那句在修補前後都沒動。上輪才補的「註解裡有括號」沒有一併把 `if (…)`、`when (…)` 這類巢狀括號寫進去。
- 修法建議:把天花板那句改成「括號裡再出現任何括號」。

引句:「變數、`.copy(…)`、括號裡有函式呼叫,或 `keyboardType` 是變數;字面 `KeyboardOptions(…)` 裡的註解寫到 `KeyboardType.Password`」

## 三問
①原問題的修復效果:
- 修補在 `_KTSEC_CASES` 補了 C117(逗號分支)、C118 和 C119(兩個 AsProperty 名字)、C120(註解天花板)。
- 我把 C117 對應的逗號分支從規則副本拿掉,C95、C96、C101、C102、C103、C107、C108、C117 都翻紅。可是我用的是破壞性替換,不是只拿掉逗號那一支,所以這個結果只能說規則整體被弄壞後測試會紅,證明不了 C117 單獨能抓到逗號分支被拿掉。
- 要單獨驗逗號分支,我另外跑了 `a13`:`keyboardType = KeyboardType.Text, imeAction = ImeAction.Done` 實跑 HIT,行為正確。
- 我另外跑了 `a13`/`b02` 的多行與尾逗號變體,都 HIT,正確。

②修補處的相鄰路徑:
- 正常路徑成立:Password、NumberPassword、`.copy`、變數、桌面四項排除、沒有 keyboardOptions 的案例,實跑都符合預期。
- 錯誤路徑:C103 後接右括號、C117 後接逗號、多行加尾逗號都報。
- 相鄰路徑:keyboardOptions 排在最後、尾隨 lambda、位置參數(`TextField(p, {}, V)`)等都符合預期。
- 破壞性替換驗證:拿掉 `(Number)?` 讓 C104 翻紅,拿掉 `\s*$` 讓一批案例翻紅。

③新發現的同一案例修前修後:
- Finding 1 和 Finding 2 的規則與型錄在 84a2a61 與 b3561e6 間無差異(`git diff --stat` 為空),修前修後結果必然相同。
- 修補本身(測試加例、引號改雙引號、放置表第四格改放排除清單、說明文字)沒有引入新洞。`extra[0] if extra else _KTSEC_IGNORES` 在放置表兩種形狀下都成立,S4 斷言完整。
- 我在 HEAD 帶 `-k kotlin_rulepack_security_rules` 跑,67 passed。HEAD 比 b3561e6 新,但 configs 無差異。

## 其他核對
- 〈預期值表〉C95 到 C120 逐列與規則形狀一致。表上沒列的常見寫法我實跑了這些:
  - 尾隨 lambda、位置參數、參數換位、`remember { PasswordVisualTransformation() }`、`PasswordVisualTransformation('*')`。
  - keyboardOptions 在其他參數之後、多行、尾逗號。
  - `KeyboardType.Companion.Password`:不報,是正確的,因為它設了密碼鍵盤。
  - `.copy()` 接在字面後面:不報,屬天花板。
  - 沒有發現天花板之外的誤擋。
- 拿掉 `^visualTransformation`、`^keyboardOptions`、`\b` 這三個比對的修飾,測試照綠。我講不出具體失敗場景,所以不另列(`keyboardOptions` 前綴誤配要有 `fooKeyboardOptions = …` 之類的參數名才會出事)。
- 我用沒有 `.` 的接收者、`?.`、`!!.` 的 Jackson 呼叫試過,行為與天花板一致。
- 放置表尾端多了三個空白行,我用 `ruff --select E3 --isolated` 檢查,沒有被標。

## 圖譜固定席逐條判
- 測試假綠形態(★INVARIANT★:還原翻紅釘要配前置斷言):這份 diff 沒改到那條合約綁的 `t_slim_uninstall_manifest_parent_cleanup_is_best_effort` 等測試。新案例 C117 到 C120 本身也是「該報就報、不該報就不報」的雙向預期,不影響。
- 授權與歸屬(★INVARIANT★):沒動 `_VENDORED_TOOLKIT` 白名單、授權檔與 SPDX 標頭。`scripts/test_lumos.py` 的標頭沒變,不影響。
- lumos-cli-read(★INVARIANT★ search 預設排除 superseded):沒碰 search 路徑,不影響。
- bound-tests-gate(★INVARIANT★):沒改閘邏輯。測試檔有改,所以要走錨點簽名,屬流程,不影響合約。
- canary-audit(★INVARIANT★ record 與 second):不相關,不影響。
- arch-alignment-lens、test-quality-handbook:那兩個筆記講的是審查席與測試品質的做法,diff 只增加逐例表與放置表,不衝突。
- 回頭重讀指紋不因主線前進失效_計劃(★RISK★):不牽涉。
- 只列名的節點(guard-kill、slim 系列、design-loop 等):diff 未改相關程式,不影響。

## 建立過的路徑
- `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第三批/審查二-sonnet/`,其下有 `src/`、`mut/`、`tl.py`。

最高等級 minor;blocking 0 條
