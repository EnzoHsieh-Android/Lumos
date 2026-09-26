severity: clean

已看,無:第 3 輪(最後一輪)累積差異已在 `exp3-正確性/`(從 main 40fcad7b clone、乾淨套用 `r3-snapshot.patch`,套用零衝突)實跑驗證,方法如下:

1. `python3 scripts/test_lumos.py -k escape`(128 passed)、`-k rule_gap`(6 passed)、`-k plan_for_loop`(1 passed)全綠。
2. 把真實 `docs/.escape-log.jsonl`(28 列)、`docs/.canary-log.jsonl`(1948 列)、`docs/.governance-log.jsonl`(85880 列)複製進實驗 vault,對著真帳跑 `lumos loop escape-stats`、`lumos loop escape --list`,並用 in-process 載入 `scripts/lumos` 逐列印出 `_escape_row_kind`/`_escape_row_bucket` 的判定,交叉核對派工詞點名的三處第 2 輪修正:
   - **plan 列排除歸因比對**:真帳裡 `雙向門放行`、`逃逸自動記`、`筆記欄位關卡補齊`、`驗收前提欄位可改` 等 loop 的逃逸列全部正確落在 `plan` 桶(因為審查帳裡沒有這些迴圈的審查紀錄,`_escape_row_kind` 推回 `plan`),`_escape_shared_evidence` 建 `ev_loops` 前先濾掉這些列,不會把它們的 sha/defect_ref 拿去跟真正放行的設計/代碼審迴圈比對。額外用 `_mk_escape_fixture` 重跑過 `t_escape_review_r2_fixes` 裡的夾具(甲/乙同 sha、乙記成 plan)確認 `leaked==1、unattributed==0`,吻合設計文件第四節。
   - **一次讀帳**:確認 `_escape_stats` 只呼叫一次 `_escape_raw_rows(env)`(逃逸帳)與一次 `_escape_review_rows_by_loop(env)`(審查帳),`cmd_loop_escape_stats` 顯示層沒有另外重讀;真帳 87856 行規模下執行 `escape-stats` 在合理時間內完成、輸出穩定。
   - **站名不認得算全體**:真帳裡站名 `消費專案真推送(pos-ios)` 因不在 `_ESCAPE_LEAK_STAGES=("CI","prod","使用者回報")` 白名單裡被歸類為 `unknown`,逐列核對後確認即使該列的 bucket 是 `counted`(有佐證、單一命中),仍被算進 `totals["unknown_stage"]`——與 r2 修正「不論落在哪一桶」的說法一致;程式碼裡 `_escape_stats` 對每一列先判 `unknown` 再判 bucket,兩者互不影響,沒看到漏算或重複扣分。
3. 額外懷疑過一個看起來像 double-count 的地方:`_escape_row_bucket` 回 `no_evidence` 之後,`_escape_stats` 沒有 `continue`,會讓這列同時計入 `totals["no_evidence"]` 又落進所屬類別的 `leaked`/`next`(真帳裡 `code-每支檔有家` 的 ESC-18f03ede 就是這樣,把 `code × high × node-content` 這一格衝到「放行1、漏網1、率100%」)。追到函式自己的 docstring 明寫「no_evidence(**仍算進它的迴圈**)」,且這行為從第 1 輪(`r1-snapshot.patch` 456/465-466 行)就存在、未曾被第 2、3 輪改過,是設計本身的意圖(無佐證不等於沒發生,只是不能拿去做歸因比對),不是這兩輪修正引入的回歸,判為不成立、未列為缺陷。
4. 順手確認 r3 新增的其他驗收點(清單印 token、`--repo` 不准跟撤回混用、同 defect_ref 不同 sha 也算歸因不明、token 重複不准撤、`--withdrawn` 單獨擋、路徑字元擋 `_plan_for_loop`、錯誤訊息清洗控制碼、8 位元 C1 控制碼清洗)都對照真帳資料或既有測試跑過一次,沒有出現與設計文件〈逃逸帳對得起來_計劃〉條款矛盾的地方。

共 0 條。
