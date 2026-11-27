severity: minor

我逐 hunk 讀了測試與筆記這包,並對照主程式包與規格。這一輪沒有 blocker 或 major,只有 2 條 minor。

已查證沒問題的部分:
- 筆記裡寫的 `[test:]` 名稱都存在於 `scripts/test_lumos.py`,每個都恰好一份,沒有重名。名單:`t_choice_compile_batch`、`t_choice_compile_probe`、`t_choice_compile_env_failopen`、`t_choice_compile_restore`、`t_choice_cov_audit`、`t_choice_compile_gov`、`t_choice_cov_src_pkgs_edges`、`t_choice_cov_base_read_rejects`、`t_choice_merge_stray_empty_suite`。
- 新 kind `invalid`、`cov-audit` 已登記在 `LOOP_NOT_CLOSE_EVENTS`(`scripts/lumos:21146` 一帶)。
- 新欄位 `at_sha`、`blob`、`compile`、`cleared`、`killed`、`wrong`、`compile_batches`、`invalid_n`、`exhausted_n` 已進 `_GOV_FIELD_TYPES`、gov 讀取白名單與 gov 分派表。我也查了治理帳裡沒有別的事件用到同名欄位,所以型別限制不會誤殺舊事件。
- `_choice_ledger_index` 仍只收 `choice-kill`。`_choice_ledger_aux` 會略過型別不對的行,`t_choice_compile_gov` 有塞壞行驗證不中斷。
- 跳過集合只有 `_choice_invalid_live` 一個定義。choice-points、`situation-rule --point`、choice-kill、推送前讀 B 版帳都走它,所以挑到同一個候選。
- `exhausted` 的狀態字樣已加進 `_CHOICE_STATUS_TEXT`。`_choice_push_judge` 只處理 `mutant` 與 `not_unique`,所以 `exhausted` 的行不擋。
- S17、S19、S22、S24 的字面都有測試守住。S22 的截斷案和單獨編綠案都是真有編不過的壞法,只因截斷或單獨編綠才不記 invalid。S24 涵蓋例外、行程內中斷和真 SIGINT 三條路,並驗了還原內容與覆蓋基準狀態。
- `_choice_merge_ghost_suite` 已不在程式碼裡,筆記改寫成指向 `JUnitRejected.ghost`,兩邊一致。

---

severity: minor
blocking: 否
`docs/lumos-toolchain-knowledge/Projects/選擇點存活回指條款_計劃.md:117`、`:119`、`:123`(規格)對不上 `scripts/lumos:80473`(`_choice_cov_wrong`)與 `:80715`(寫入 cov-audit 事件)。
場景:規格範圍 4 只列 cov-audit 的欄位 `file、fp、new_sha、killed、killing_test、run_id`。範圍 5 與範圍 6 寫「帳上有 `cov-audit killed: true` 的 `at_sha`」就不判 `none`。實際程式多寫了 `reach`、`wrong`、`head_sha`,且只認 `wrong` 為真的事件。clause 行抽到後被經過子集內的測試殺掉時,`killed: true` 但 `wrong: false`,程式不會停判 `none`。照規格字面實作的接手者會做出不同行為。這批筆記補了 `wrong`、`head_sha`,但規格本文沒同步。
引句:「帳上 wrong 的 head_sha 之後同一個 at_sha 再跑不判 none,帶過去規則也不帶那個 at_sha 的 via cov 存活」
修法:把規格範圍 4、5、6 的 cov-audit 欄位與判錯條件改成 `wrong` 加 `head_sha`。

severity: minor
blocking: 否
`scripts/test_lumos.py:150305`(Groovy 測試改版)。
場景:Groovy 真跑那一半現在只有設了 `LUMOS_TEST_GROOVY_JAR` 才會跑,預設與 CI 都只做靜態檢查。改了 init script 的選任務比對後,沒有任何自動檢查。測試說明與 Issue 進度節只寫「本機手動打開」,沒有任何 `REVISIT:` 回頭條件。全域規則要求承認「沒機械守衛」時把回頭條件拆成獨立一行。
引句:「②是改分析腳本時在本機手動打開的驗法(第一段末輪邊界 #2)」
修法:補一行 `REVISIT:[when-file:…][by:…]`,條件是 init script 分析段有改動時要手動跑一次。

總結:最高等級是 minor
