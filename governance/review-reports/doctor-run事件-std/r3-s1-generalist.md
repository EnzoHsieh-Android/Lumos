# doctor-run事件-std r3-s1 對抗審計 — LENS: generalist

審對象:`/tmp/doctor-run事件-std-r3.md`(第三輪 delta 覆核;r1 major×1+minor×4 已折入,r2 僅 minor×2 措辭、未改動）。以獨立第三方角度重讀設計，並與真代碼逐條核對。

## 核對方法

逐條把設計節的機制性主張對到真代碼行為（未實作——這是實作前設計審），檢查是否會「一落地就不成立」：

1. `_append_governance_log`(scripts/lumos:421-441)：`if not events: return` 屬實，設計聲明「不改」與此一致；`gov_events` 只在 `if ci:`(scripts/lumos ~1327)才會被送進此函式，純 `doctor` 不受影響——`t_governance_log_write` 的 `gov-log: 純 doctor 不寫` 斷言不會被本案破壞。
2. `cmd_gov` 的 governance mapper（scripts/lumos ~2985-2986）讀的是 `"detail": d.get("note", "")`，證實設計標的「鍵名 `note`」正確；若沿用舊 `detail` 鍵會讓 `d.get("note")` 拿到空字串，note 內容整段消失——這正是 light r1 M1 抓到、std 版本已修正的點。
3. `cmd_gov` 的 `else` 分支（非 `--full`）恰有兩個對 `ded` 的迴圈：一個建 `agg`/標 `_agg`/`_drop`（scripts/lumos ~3050 起），一個實際印（~3057 起，未命中 `_agg` 的行落到無條件 `print(...)`）。`doctor-run` 的 `kind` 是 `"ran"`，`_is_advisory` 只認 `kind == "warned"`，故不會被摺；若不加專屬 `continue` 就會落到那行無條件 print，逐筆灌畫面——與設計文引的 std r1 s1 major 診斷完全一致，補丁位置（兩迴圈各自 continue，不動 `ded`）技術上可行。
4. `_render_gov_stats(rows, ded, ...)`（scripts/lumos:2910-2955）直接吃參數 `ded`，與顯示迴圈的 `continue` 無關——顯示層過濾不會波及 stats 的 `a["ded"]` 計數，兩次不同 commit 的 `doctor --ci` 因 dedup 鍵含 `commit` 而各自成一列，`--stats` 讀到的去重筆數確實會是 2，t_gov_hides_run_marker_unless_full 的 `== 2` 斷言站得住。
5. gate 字面值漂移釘（t_gov_stats_gate_drift，scripts/test_lumos.py:3047-3065）掃描 `"gate": "字面值"` 並要求全部落在 `_KNOWN_GATES`——新增 `{"gate": "doctor-run", ...}` 屬字面值寫法（非動態），會被此測試逼進 `_KNOWN_GATES`，且不會讓 `dyn`（動態 gate 寫點）計數變化,原本恰 1 處（讀側 passthrough）維持不變。
6. `_BOOKKEEPING_FILES`（scripts/lumos:10299-10300）已含 `docs/.governance-log.jsonl`，pitfalls --diff 排除與 code-loop「只准簿記檔案 commit」豁免不需要為本案新增任何項目——本案只是在既有簿記檔多寫一行，不是新開檔案。
7. pre-push hook（scripts/hooks/pre-push:148）與 `.github/workflows/ci.yml`（Graph doctor 步驟）都只看 `doctor --ci` 的 return code，不解析輸出內容/帳檔行數，本案不改 rc，兩處消費者不受影響。
8. 掃過 test_lumos.py 中所有 `doctor", "--ci"` 呼叫點與 `.governance-log.jsonl` 讀取點的交集，僅 `t_governance_log_write` 一處在同函式內同時出現，其斷言用 `"check-r" in log.read_text(...)` 子字串判定，不受多一行 `doctor-run` 影響；未發現任何測試對真實 `doctor --ci` 後的帳檔行數做精確計數（`len(...) == N`）會被新增的一行打破。
9. node 縮限模式：`ded = [r for r in ded if q in r["nodes"]]`，`doctor-run` 的 `nodes` 恆為 `[]`，`q in []` 恆假，天然被濾除，不需要特判——與設計文的主張一致。

## 結論

未發現新的 blocker/major。r1 的既有 major（過濾誤落在 `ded` 上連 stats 一起濾掉）在本版設計文中已正確改為「只動顯示迴圈的印出動作」，經對照真代碼確認此修法可行、不會產生新的迴歸；r2 的兩條 minor（措辭）未變動，本輪未發現需要升級或新增的項目。「已清」推導法（run 標記只畫邊界、不列節點）在目前 doctor 各檢查的觸發條件下邏輯自洽，屬已知限制而非本案引入的缺陷，未達 major 門檻。

severity counts: blocker=0, major=0, minor=0
