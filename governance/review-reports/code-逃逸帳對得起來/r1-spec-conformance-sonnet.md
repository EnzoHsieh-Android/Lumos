severity: clean

已看,無:逐條核對 [S1]–[S21] 與〈做法〉一~四節,實作與綁定測試皆與設計條款相符,未發現遺漏、驗到別的東西、或做了設計沒說的事。細節如下(每條結論):

- [S1] 做到。`_escape_loop_kind(loop_id, review_ids)`只看 loop 欄與 `_review_loop_ids`(排除 kind=spec-gate);手動與自動記帳都寫入 `loop_kind`;`_escape_stats` 對舊列也是即時呼叫同一支函式推,不是讀存量欄位。測試 `t_escape_loop_kind_written_and_inferred` 直接測函式三分支、驗規格閘留痕不入 `review_ids`、驗手動記帳寫進欄位,確實驗到條款本體。
- [S2] 做到。sha/defect_ref 去空白皆空且 `--missing-defect-ref` 未給或理由太短 → 擋;`--sha` 一律寫入 `rec["sha"]`;理由寫進 `defect_ref_missing`(且只在真的沒有 sha/defect_ref 時才寫)。測試 `t_escape_manual_requires_defect_ref` 逐一驗證擋下訊息、`--sha` 落欄、理由落 `defect_ref_missing`。
- [S3] 做到。統計端全部經由中央函式 `_escape_rows_for`(預設不含撤回/被撤列),問閘尾漏斗(第 2303 行)、治理帳統計(第 7084 行)、doctor 撤除條件分子(第 19005 行)、escape-stats、rule-gap 皆呼叫此函式或共用判斷函式,結構上自動排除撤回列;`--list` 保留全列但標「已撤回」。測試驗到 escape-stats 與 `--list`/`--list --withdrawn` 的行為切換。
- [S4] 做到。目標不存在/自撤/撤回者空白/理由不足四字實字皆擋且帳不變;鎖逾時經真實 `main()` 入口驗證印「擋下」且 rc=2、不冒例外。測試 `t_escape_withdraw_validation` 覆蓋全部分支,含監補 `_vault_write_lock` 讓其拋 RuntimeError 驗證不外洩。
- [S5] 做到。`_auto_escape` 去重讀取改用 `include_withdrawn=True`,撤回過的 (loop,stage,sha) 仍在 existing 集合中,同觸發不補回。測試直接呼叫 `_auto_escape` 驗證回傳 0。
- [S6] 做到。`leaked`/`released` 皆是以迴圈 id 為元素的 set,同迴圈多筆逃逸只算一次;`released` 只收 kind=converged 且審查帳有紀錄的迴圈,cap-reached 不算。測試驗證三筆逃逸只算一個迴圈、cap-reached 不進分母。放行數 0 的類別因 `cats` 只從 `released` 集合建構,結構上不會出現在輸出裡,測試未特別造 0 例但邏輯上蹈空成立。
- [S7] 做到。`_ESCAPE_NEXT_STAGES=("實作","code-loop")` 加 `startswith("push-gate")` 歸下一站接住;其餘已知漏網站名歸 leak,未知站名同樣歸 leak 並另計入 `unknown_stage`。測試 `t_escape_stats_next_stage_and_unknown_stage` 同時驗證了「next 不進 leaked」與「未知站名進 leaked 又進 unknown_stage 計數」兩件事。
- [S8] 做到。`_escape_row_bucket` 依序判 unreleased→no_evidence→unattributed(僅在 `ev_loops`,即分母母體內比對),兩者皆 `continue` 不進任何類別分子。測試以「甲/乙同 sha、丙未放行」精確區分 unattributed 與 unreleased 兩桶。
- [S9] 做到。沿用既有 `_loop_anchor_tier`(帳上第一筆帶 tier 的值)取分級,沒有則「未定錨」;`_escape_plan_scopes` 對多個 `scope/` 標籤逐一回傳、`_cats` 對每個 scope 各建一個類別。測試驗證未定錨、分級取第一筆(standard 蓋過後補的 high)、兩個範圍標籤各自成類別。
- [S10] 做到。`_plan_for_loop` 新增去 `code-` 前綴與雙邊 NFC 正規化(先精確比對,失敗再列目錄名 NFC 比對)。測試以 NFD 檔名驗證找得到。
- [S11] 做到。`small_sample = n < 20`,輸出行同時印「★樣本太少不下結論★」與原始 `released` 數字。測試驗證文字與數字皆在。
- [S12] 做到。`_escape_released_loops` 要求 `lid in review_ids` 才收進 `released`,治理帳有 converged 但審查帳沒有該迴圈的("幽靈")不進分母。測試驗證分母總數排除該迴圈。
- [S13] 做到。`cmd_rule_gap` 保留自訂找檔邏輯(standalone 佈局),讀到列後另用共用判斷函式 `_escape_is_withdraw`/`_escape_withdrawn_targets` 過濾撤回,不是自己重寫一套判斷。測試以獨立 repo(非 vault 佈局)驗證撤回列被排除、其餘規則缺口計數正確。
- [S14] 做到。撤回紀錄本身在 `_escape_rows_for` 永遠被濾掉(`not _escape_is_withdraw(d)`);由於各讀者(問閘尾、治理統計、健檢分子、rule-gap、escape-stats)皆走同一組共用函式,結構上撤回紀錄不會被任何一個當成逃逸列。測試直接驗 `_escape_rows_for` 回空、escape-stats 的 `plan`/`no_evidence` 兩個計數不誤把撤回紀錄算進去、`gov --stats` 不崩。
- [S15] 做到。`_escape_raw_rows` 用 `isinstance(d, dict)` 過濾非物件 JSON 行,不拋例外。測試以 `null`/`[1,2]`/`"s"` 混雜一筆合法紀錄驗證只留一筆。
- [S16] 做到。`_escape_released_loops` 只挑 `kind=="converged"` 的治理帳列建立 `released` 集合,同迴圈是否還有 cap-reached/rewrite 的其他列不影響判斷。測試以三筆治理帳紀錄(cap-reached、converged、rewrite 同迴圈)驗證仍算放行。
- [S17] 做到。撤回時檢查 `target in _escape_withdrawn_targets(rows)`,已撤過的再撤會擋。測試驗證第二次撤回同一 token 被擋且訊息含「已經撤回過」。
- [S18] 做到。共用的 `_escape_log_guard` 在撤回與手動記帳兩處都會先擋 symlink 帳本;測試對同一顆 symlink 帳本分別驗證撤回與手動記帳皆擋、連結目標檔案內容未變。
- [S19] 做到。`--withdraw` 與 `--list`/`--auto`/任何記帳參數(含 `--stage`、`--sha` 等)混用時在 `_escape_withdraw` 開頭擋下。測試 `t_escape_withdraw_no_mixed_flags` 逐一驗證四種混用組合皆擋。
- [S20] 做到。`_escape_shared_evidence` 只在 `key and lid in released` 時才建立佐證→迴圈映射,無佐證列與母體外迴圈皆不參與比對。測試以「同 sha 出現在母體外的『計劃乙』」與「兩筆無佐證列」精準區分:leaked 仍算 1(未被誤判歸因不明)、`unattributed==0`、`no_evidence==2`,且無佐證列彼此不互相比對——這是本案裡對條款規則掐得最緊的一條測試,確實驗到「先剔無佐證」與「只在母體內比對」兩個子句,而不只是驗到表面的「歸因不明桶存在」。
- [S21] 做到。`code` 類別輸出行固定附加「(code 類只含手動記的逃逸,低估)」文字。測試驗證該字串出現在 `code × standard` 那一行。此條款本質是一則提醒文字,測試也只驗文字存在,與條款要求相符(條款本身未要求驗證自動記逃逸永遠不落在 code 類——那件事是靠既有的 `_auto_escape` 一律用計劃名而非 `code-` 編號記帳這個既有行為保證的,不在本次改動範圍內)。

補充觀察(非阻塞、不對應任何 [SN] 編號,屬〈做法〉第三節散文而非條款):`--withdrawn` 單獨給(沒有 `--list`)應擋下且提示的分支(`if withdrawn and not list_mode`)讀碼確認存在,但沒有找到對應測試直接命中這個分支;因為它不是掛 `[test:]` 的條款,不算違反設計,只是覆蓋率上的小洞,不升等。

共 21 條,全部「做到」。
