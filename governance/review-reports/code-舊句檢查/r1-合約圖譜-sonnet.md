severity: minor

## F1 drift check 的說明頁一句話沒跟上 m1
severity: minor
blocking: 否
引句:「舊句檢查(m1)要再帶觸發的名稱,一個名稱一個 `--name=<名稱>`」
file: `scripts/lumos:37889`
敘述:
1. 在 clone 跑 `python3 scripts/lumos drift check --help`,輸出的「什麼時候用」仍是「轉正了還留著預告句就擋,其他只列出」(定義在 `scripts/lumos:37889` 的 "drift check" 說明字典,patch 沒動它)。
2. m1 在 `drift_check.old_sentence=block` 時,要處理的舊句也會擋(rc1),還會有一行結論與治理帳;這句說明沒提 m1、也沒提第二個開關,跟 commands/04 與 08 的說法(m1 同一支指令、另一個開關)不一致。
3. `drift ack --help` 有新參數 `--name`(有說明,且寫明一律等號寫法),這部分是對的;`drift check` 沒有新參數,所以只是說明文字落後。

## F2 存量漂移守衛說 gov 統計會把 c 類與 m1 兩筆折成一筆,只在部分情況成立
severity: minor
blocking: 否
引句:「同一次推送會有 c 類與 m1 兩筆,`gov` 的統計會把同提交同筆記的兩筆折成一筆,量 m1 一律讀原始帳。」
file: `scripts/lumos:7321-7327`
敘述:
1. 去重鍵是 (commit, nodes, gate, kind, token)(`scripts/lumos:7324`)。m1 的 kind 由 `_drift_m1_ledger` 決定(passed/warned/blocked/skipped),nodes 只取「要處理」那幾篇。
2. 只有 kind 與 nodes 都相同才折;例如 c 類 warned、m1 passed 就不折,m1 零筆時 nodes 是空,也不會跟 c 類折。
3. 結論(量 m1 讀原始帳)正確,前半句因果說得太滿;不影響行為,只是這句筆記本身偏差。

## 圖譜鏡頭逐條判定
- lumos-cli-read(search 預設排除 superseded):不影響;patch 沒動 search 與濾網。
- bound-tests-gate(code-loop check 逐支真跑綁定測試):不影響;沒動 code-loop、綁定測試邏輯。
- guard-kill(rc 優先序、--json 純度):不影響;m1 走 drift check,沒碰 guard kill。
- 授權與歸屬(SPDX/MIT 檔頭、_VENDORED_TOOLKIT):不影響;檔頭未動,沒新增被複製的檔。
- 測試假綠形態、lumos-cli-lifecycle(re-inject)、design-loop(處置閘):不影響;沒有相關路徑被改。`_home_cache_write` 抽出 subdir 參數並改回傳 bool,唯二呼叫端(派工鏡頭與 drift-defs)都吃得下,派工鏡頭仍寫 dispatch-lens。
- pitfalls-code-loop、其餘只列名節點:不影響;無可指出的受影響行為。

## 筆記與程式一致性核對(通過項)
- 說明頁:`drift ack --help` 有 `--name` 與 kind 含 m1;commands/04、08、INDEX 說的「gate=off 仍跑 m1、要全關須寫 old_sentence: off」與 `_drift_check_c` 及 `cmd_drift_check` 一致;54 個歷史字眼、30 秒、14 天快取、4096 位元組都跟程式對得上。
- Systems/存量漂移守衛新增 RULE 行 `[since]` `[retire]` `[confirmed]` 三欄齊;新增行沒有 FACT/FLOW/DEP;反引號檔案都是該節點 about_code 已列的家(scripts/lumos、old_sentence_exp.py、hooks、ci.yml)。
- 實跑 `lumos lint` 三篇(存量漂移守衛、舊句檢查計劃、治理帳 Issue)0 問題;`note-shape --diff` 與 `home check --diff` 對 25f6a459..620a6f73 無輸出(無違規)。
- 計劃與 Systems 引用的 t_drift_m1_* 測試名在 `scripts/test_lumos.py` 都存在。
- 沒有破壞任何 ★INVARIANT★ 合約。

最高等級:minor
