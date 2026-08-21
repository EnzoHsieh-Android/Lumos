# doctor-run 事件案 std r2 — generalist delta 審計

角色：獨立第三方複審，把文件當外部投稿讀。范圍：驗證 std r1 摺回是否完整、抓新洞。**本輪一律對照真代碼**（尚未實作——`scripts/lumos` 內完全找不到 `doctor-run` / `doctor_run` 字面值，`_KNOWN_GATES`（scripts/lumos:2891-2892）也還沒有它，故本審計是「設計文件對真代碼現況的描述是否準確」）。

## std r1 摺回覆核（逐條對真代碼）

1. **note 鍵名**（light r1 M1 修正）：`cmd_gov` 的 governance mapper 確認讀 `d.get("note", "")`（scripts/lumos:2986），非 `detail`——文件「★欄位名 `note`」的描述與真代碼消費端一致。✅
2. **過濾不可動 `ded`**（std r1 s1 major）：確認 `_render_gov_stats(_raw, ded, loaded, since_days, cutoff, node)`（scripts/lumos:3142）與顯示迴圈共用同一個 `ded` 物件，且該呼叫發生在顯示迴圈（`if full:` / `else:` 兩分支，scripts/lumos:3030-3078）**之後**——若過濾寫成重新賦值 `ded = [...]` 而非在印出處 `continue`，會如 s1 所料把 `doctor-run` 一併從 `--stats` 分母濾掉。文件現在的寫法（「過濾只作用在顯示迴圈的印出動作」）方向正確。✅ 但見下方「新洞」一條，指出「兩處各自 continue」的定位敘述可能誤導實作者。
3. **`_is_advisory` 不吃 doctor-run**：`_is_advisory`（scripts/lumos:3020-3021）判準為 `kind == "warned" and not token and not detail`；設計把 `kind` 定為 `"ran"`、`note` 恆非空字串（`issues=<n> gates=<n>`），兩個條件都不成立，doctor-run 天生繞過摺疊路徑，不需要靠 `_is_advisory` 特判——與文件「不是靠 `_is_advisory` 摺疊」的說法一致。✅
4. **`_KNOWN_GATES` 漂移測試不受影響**：`t_gov_stats_gate_drift`（scripts/test_lumos.py:3047-3061）驗兩件事——字面值全在 `_KNOWN_GATES` 內、動態 `"gate":` 寫點恰 1 處。`doctor-run` 是字面值寫法，不新增動態寫點，兩條斷言都不受影響。✅
5. **`node` 縮限模式**：`ded = [r for r in ded if q in r["nodes"]]`（scripts/lumos:3021 一帶）對 `nodes: []` 的 doctor-run 事件天然濾空，不需特判——與文件「無需特判」一致。✅
6. **check-\* 事件涵蓋完整性**：`run_doctor` 內所有會落 `gov_events` 的 gate 字面值只有 `check-r`（scripts/lumos:785/789/792）、`check-s`（819/825）、`check-e1`（866）、`check-e2`（948）、`check-e3`（989）、`check-k`（1030）、`check-j`（1308，另 j_gov 內部 shallow-skip 也是 `check-j`，check_regen_provenance 內）——全部 `check-*` 前綴，`note` 裡「gates=<本次有事件的 check-\* gate 數>」的口徑不會漏算既有 gate。✅
7. **簿記白名單**：`docs/.governance-log.jsonl` 已在 `_BOOKKEEPING_FILES`（scripts/lumos:10299-10300），doctor-run 事件走同一寫入路徑，不會新產生 pitfalls-diff / code-loop 簿記例外問題。✅

## 新洞

**minor｜審計修正紀錄的「已記入」provenance 與真實圖譜節點不符。**

引句：「記入 [[Issues/寫下風險當成處理風險]] 類待辦」（docs/lumos-toolchain-knowledge/Projects/doctor-run事件_計劃.md:43）

核對 `docs/lumos-toolchain-knowledge/Issues/寫下風險當成處理風險.md` 全文，找不到任何一處提到 gitignore、`.governance-log.jsonl`、或帳檔誤入版控——`grep` 零命中；該節點目前收錄的三個 2026-08-20 實例（鏡像分家/slim 凍結/gov --stats 限制聲明）與判準表，跟 s3 抓到的「vault 範本 .gitignore 放錯層」是不同題目。真正落地的地方其實是另一個節點：

引句：「reversibility 寫「帳檔皆 gitignore」(已進版控)」（docs/lumos-toolchain-knowledge/Verification/2026-08-21_L4交叉審計30節點清帳.md:56）

且已在 `Systems/reversibility-governance-ledger.md:26`／`:86` 以「★(2026-08-21 程式碼實證)帳檔已入 git 追蹤,非 gitignore★」訂正——這條路徑事實本身是對的、也確實留了痕，只是**指向的節點名對不上**：文件寫「記入 Issues/寫下風險當成處理風險」，實際落點是 Systems/reversibility-governance-ledger（性質也不同：後者是「事實已訂正」的陳述句，不是待辦類 Issue）。不影響 doctor-run 本身的實作正確性，但屬於本案審計紀錄自身的可追溯性瑕疵——之後有人照著這條 wikilink 去查「這件事後續有沒有人接」會撲空。建議把該句改指向 `Systems/reversibility-governance-ledger`，或直接說明「已訂正、非待辦」。

## 結論

std r1 的摺回（display-loop-only 過濾、stats 斷言 count==2、note 鍵名、「已清」推導語意）逐條核對真代碼與既有測試骨架，皆吻合，未發現摺回不完整之處。本輪新增一條 minor（審計紀錄裡的 wikilink 指向錯節點），無 blocker、無 major。

**severity count: blocker=0, major=0, minor=1**
