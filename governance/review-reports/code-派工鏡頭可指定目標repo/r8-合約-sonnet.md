severity: minor

這輪機械面對得上。S45–S51 各條款的 `[test:]` 跟 13 支新測試一一對應,每支在 `scripts/test_lumos.py` 都有定義。`spec-trace` 回 51 條款全綁、懸空 0。計劃、派工鏡頭、arch-alignment-lens 三篇 `lint` 都是 0 問題,codex-harness 只有 2 條既有的 FACT 警告。我另跑了 `lens_repo_notes`、`arch_target_text`、`rule_show`、`target_rule_quote`、`residual_refs`、`diff_text_total`、`backtick_paths` 七組子集,全綠。

常數與程式一致:
- 規則截 200:`_ARCH_TARGET_RULE_SHOW` 是 200。
- 檔名清單 1000 字、也不超過分配的四分之一:`_ARCH_TARGET_LENS_FILES_CHARS` 是 1000,程式用 `min(1000, budget//4)`。
- 殘留指標 12:`_LENS_RESIDUAL_REFS_MAX` 是 12。
- 整段 12 萬:`_LENS_TEXT_MAX` 是 120000。
- 計劃掃描 20 萬:`_ARCH_TARGET_SPEC_SCAN_MAX` 是 200000。
- 3 節點:`_ARCH_TARGET_LENS_NODES` 是 3。

「看不見」清單沒有殘留:S45 列的七個類別與七個像空白字,跟 `_lens_hidden_char`、`_PQ_BLANK_LOOKALIKES`、掛鉤的 `SPEC_NAME_BLANK_LOOKALIKES` 三處一致。r6 手列清單 `_LENS_NAME_INVISIBLE_RANGES` 在 `scripts` 與 `docs` 都已查無。templates.md §7.6 跟 `_ARCH_TARGET_TAIL` 的措辭一致,「規則沒附」「讀不到規則」兩個字樣也跟程式輸出對得上。

severity: minor
blocking: 否 — 回頭條件在 2026-12-15 才到期,現在不影響行為,但照現在寫的做法查不出東西
引句:「找出派工詞附過框內名字(帶 ‹ › 的計劃路徑、節點名、檔名)的輪次」
問題:新寫的 REVISIT 要人用 `rN-dispatch.json` 找出附過框內名字的輪次,但這個檔沒有記這件事。
- 我讀了 `r7-dispatch.json`,欄位只有 loop、round、base_commit、materials、seats。裡面沒有派工詞,`‹` 出現 0 次。
- 只有設計審的提交寫法會有 `spec_commit`,代碼審的輪次完全沒有可辨認的欄位。
- 接著的輔助 glob `r*-*-*.md` 只比對兩個連字號以上的檔名。倉庫裡一個連字號的席報告(例如 `r1-通才.md`,我數到 155 份)全被排除。
- 「要排除 `r*-snapshot.md` 與 `r*-intake.md`」也是多餘的,這兩種檔名只有一個連字號,glob 本來就不會比對到。
具體失敗情境:2026-12-15 doctor 叫人回頭,照做 `rN-dispatch.json` 的第一步找不到輪次,實際只能把每一輪都當候選。改用這個 glob 之後,舊命名的席報告又被漏掉。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭可指定目標repo_計劃.md:210`,file: `docs/lumos-toolchain-knowledge/Systems/派工鏡頭.md:75`,file: `governance/review-reports/code-派工鏡頭可指定目標repo/r7-dispatch.json`

severity: minor
blocking: 否 — 只是條款分段標題沒更新,不影響行為
引句:「代碼審 r3–r6 補的條款(這幾輪新加的行為與守衛」
問題:S45–S51 是 r7 才加的,但它們掛在這個小節標題底下,標題還寫 r3–r6。同一篇實作紀錄已改成「S25 起是代碼審 r3–r7 補的」,兩處對不上。
具體失敗情境:下一個 session 看標題以為 S45 以後不是這幾輪的產物。S27 的 `_LR4_CLAUSE_TESTS` 清單也依 r3–r7 算,讀標題的人會對不起來。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭可指定目標repo_計劃.md:165`

severity: minor
blocking: 否 — 筆記跟程式對不上,但程式行為是對的,以程式碼為準
引句:「帶值的內容加框(寫死的段首與尾句在框外,r7)」
問題:這輪 arch-alignment-lens 寫明目標規則原文在框內,但姊妹計劃 `架構對齊可宣告目標架構_計劃` 沒跟著改,有兩處殘留:
- 第 98 行的注入說明寫「目標規則是專案寫的自由文字,放在框外並標明是材料」,與程式現況相反。`_arch_target_text` 現在把規則原文包進 `_frame_injected`。
- 第 36 行的 RETIRE-IF 用 `grep -rl '目標規則：'`(全形冒號)。範本與程式實際輸出的是半形的 `目標規則:「`。我查卷證目錄,全形只命中 4 份、半形 25 份。
具體失敗情境:2027-04-09 人裁時照這條 grep 數「架構對齊席報告帶引句的發現有沒有被折入」,會嚴重低估,可能因此撤掉仍有人在用的目標架構宣告。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/架構對齊可宣告目標架構_計劃.md:98`,file: `docs/lumos-toolchain-knowledge/Projects/架構對齊可宣告目標架構_計劃.md:36`,file: `scripts/lumos:45235`

severity: minor
blocking: 否 — 程式輸出是對的,只是被截斷時的指引有誤、條款文字沒跟上測試
引句:「名字長到撐破時整段截在」
問題:
- S40 仍寫名字太長時「整段截在 `_LENS_SPEC_TEXT_MAX` 字內並講明」。這輪 `t_arch_target_text_total_capped` 的檢查 ② 已改成「放不下的列名行併進『另有 M 個目標節點沒列名』」,不再斷言「附加段超過」。條款描述的是舊行為。
- 做法 6 末句仍寫 `listed`、`shown` 照實際印出的篇數。S43 這輪才拆成 listed 含只列名、shown 不含,做法 6 沒跟著改。
- S51 與 `_lens_text_cap` 的截斷註腳寫「要全文就手動跑 lumos dispatch-lens <範圍> 看」。手動跑走同一支函式、同一個上限(程式 `out = {"text": _lens_text_cap(_text)...}`),拿不到全文。
具體失敗情境:席位或編排者被指引去手動重跑,結果還是被截,白跑一趟。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭可指定目標repo_計劃.md:182`,file: `scripts/lumos:50674`

已讀,無 finding:
- 條款與綁定測試的對應。
- S27 變異清單。我對照 `t_lens_repo_notes_r4_clauses_and_limits` 與 `_spec_freeze_and_entry`,清單列的每一項都有對應的變異。
- templates.md §7.6 與目標架構段實際輸出。
- 規則截 200 含欄位:程式現在先剝尾端欄位再截,S49 與派工鏡頭 WHY 的寫法一致。
- 「標題不含在分配」的舊說法:程式與 S47 都已是「分配含標題行」,沒有殘留。
- 段首尾在框內的舊說法:程式與 S48 一致,段首與尾句在框外。
- 常數與 S45–S51 數字。

最高等級 minor,blocking 0 條。
