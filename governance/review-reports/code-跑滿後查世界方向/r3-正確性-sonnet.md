severity: clean

這一輪修補我找不到錯的地方。修補區間只有一個程式提交(4ef433e84),我逐條走過讀帳失敗分支、兩支新測試和生效常數的比法。原 repo 與 `docs/.governance-log.jsonl` 都沒動。實驗用 clone 和我留下的一個 `gctl-run-` 暫存現場已刪。

## 修補逐點核對

**讀帳失敗分支(`cmd_loop_cap_decision`,`scripts/lumos:22963-22966`)**
- 走過的輸入有四種:
  - 讀帳失敗、extra-round:替身 `{"decision": "extra-round"}` 沒有 `ts`,`_cap_world_case` 在 `k is None` 那行回 `required`,會提醒補 world_check。
  - 讀帳失敗、accept-risk:回 `optional`,不提醒。
  - 讀得動:照舊取帳上最後一筆人裁,行為沒變。
  - `gerr` 這個名字被重新指派:前面的 `gerr` 已在 `if gerr: return 2` 之後不再用,沒有副作用。
- 修前、修後的證據:
  - 我把修補那一行還原成 `next(...evs)` 後,`t_cap_decision_world_fill_ledger_unreadable` 翻紅(讀帳失敗時 `dec=None` 回 `ignored`,沒有提醒)。
  - 還原時前置斷言「讀帳那一步真的被模擬成讀不動」仍綠,所以新測試確實走到被測分支,不是假綠。
  - 這證明測試的分辨力,不證明現場一定會讀帳失敗。
  - 方向上的限制:這個分支在帳讀不動時一律判 `required`。生效日(2026-11-05)之前記的 extra-round 在這個分支會多收到補 world_check 的提醒,正常讀得動時則是 `ignored` 不提醒。這是作者明寫的偏嚴,沒有造成錯誤擋下,只是提醒多一句。

**`--template --write` 被擋(`scripts/lumos:23041`)**
- 我把 `_cap_world_case(dec)` 換成 `None` 後,`t_cap_retro_template_write_world_fill` 的「生效後」那組翻紅。
- 把常數改成早於 `_CR_TS_OLD` 後,「生效前不提醒」那組翻紅。所以正負兩邊都真的在驗。
- 沒有測試的相鄰路徑:`_retro_path_unsafe == "dossier"` 那條(`scripts/lumos:23035`)也傳了 `case`,但沒有測試走到它。它只會多附一句提醒,不是錯誤行為。

**生效常數說明與提交日測試**
- 測試比法是 `day < since[:10]`,跟計劃做法 7 寫的「早於常數日期(同日不算)」一致。
- 目前提交日是 2026-11-04,早於常數日,測試綠。
- `t_cap_since_last_change_sees_value_edit` 用兩筆只改值的提交,驗到比法在同日時為偽、前一日為真。

## 本席多做的時鐘炸彈檢查

測試用的是真實時鐘(`_cr_decide` 在 38 支測試裡用現在時間)。我把常數暫時改成 `2026-01-01`,模擬生效日之後,再跑 `-k cap_`、`-k retro`、`-k cap_decision`。

- 失敗的都是「依賴 `_CR_TS_OLD = 2026-10-05` 仍早於常數」的案例,這是我改常數造成的,不是日期一到才現形的問題。
- 沒有發現會在 11-05 之後才變紅的測試。
- `t_cap_hint_world_check_first` 裡依真實時鐘的那一組(`c3`)已自己用 `now_req` 判斷,日期一到不會壞。

## 其他路徑

走過但沒找到洞:

- **`_cap_world_case`**:輸入走過 ts 為 `None`、非字串、無時區、`0001-01-01`、`9999-12-31`、ISO 週格式,都不丟例外。
- **`_retro_world_check` 與 `_retro_world_empty`**:邊界走過,包括 bool 版本、`wc=[]`、骨架空殼、重複網址。
- **`retro-stats`**:`world_verdicts` 計數用 `wv` 判斷,例外路徑也有重設,不會污染計數。
- **新舊互讀**:version 1 配 `optional` 或 `ignored` 照過;version 1 配 `required` 會被擋並講清楚。

## 圖譜鏡頭

- `loop-convergence-recording` 是跑滿提示的家。改的那行 WHY 與程式行為一致,不影響其他 KEY、INVARIANT。
- 那行 WHY 的 `[test:]` 只列 `t_cap_hint_world_check_first` 和 `t_cap_decision_world_fill_reads_ledger`,沒有綁新增的 `t_cap_decision_world_fill_ledger_unreadable`。這只是筆記綁定的完整度,不影響程式行為,我不列為發現。
- `loop-retro` 與 `每輪修補差異派工` 的 diff 沒被這次修補改動,宣稱的行為(五處共用一支判定、先查世界擴成查方向)不受影響。

## 三問

- 原問題的修復效果有何行為證據:有。還原修補後新測試翻紅,復原後轉綠(同上)。
- 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立:成立。讀得動時的路徑與修前完全相同;accept-risk 與沒有卷證資料夾的路徑沒被碰到。
- 新發現的同一案例在修前、修後各是什麼結果:沒有新發現,故不適用。

我沒有發現需要擋下的問題,這一輪可以過。
