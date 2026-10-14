severity: minor

審查範圍:計劃(S25–S44、做法 5/6/8、REVISIT)、Systems/派工鏡頭、Systems/codex-harness、Systems/arch-alignment-lens,以及測試差異。我另外在 lens-repo 跑了 `spec-trace`、四篇 `lint`,並用 `PYTHONDONTWRITEBYTECODE=1` 跑了 `-k t_lens_repo_notes` 與 `-k t_dispatch_lens_hook_fixed`。`spec-trace` 是 44 條款全綁、懸空 0;`lint` 是 0 error(codex-harness 有 2 條舊的 FACT 警告,不是這輪改的);`-k t_lens_repo_notes` 與 `-k t_dispatch_lens_hook_fixed` 的結果是 107 passed、15 passed,0 failed。

severity: minor
blocking: 否 — 只是筆記說法與條款文字的小落差,不影響行為,各條綁定的測試照綠。
引句:「變異照實是這些:清單裡每支測試各拿掉一次綁它的條款、S13 三個寫法各改一次、三個輪次字樣各加回一次」
問題:S27 說「變異照實是這些」,可是列舉不全。`t_lens_repo_notes_spec_freeze_and_entry` 裡還有四個變異沒列進去:
- 把做法 9 的 `out_outside_repo` 改掉。
- 拿掉 `[test:t_spec_freeze_out_must_stay_in_repo]` 那條款。
- 派工鏡頭拿掉 `_vault_node_path`、`_vault_node_read`、`_lens_author_name_show` 三條守則行。
- codex-harness 拿掉 `spec_source` 那行。

這輪修補要做的就是讓 S27 照實列,結果仍有漏列。
具體失敗情境:下一輪有人依 S27 的清單判斷「這四項沒有變異守著」,多寫一支重複的測試。或者以為守衛只涵蓋清單上的項目,把清單外的測試當成多餘而刪掉。
佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/test_lumos.py:47383-47410`,以及 `t_lens_repo_notes_r4_clauses_and_limits` 的 `muts` 區塊(約 `47830` 起)。

severity: minor
blocking: 否 — 回頭條件仍可執行,只是篩選條件偏窄。
引句:「先跑 `grep -rlF '‹' governance/review-reports/*/r*-*.md` 列出引到框內名字的席報告,逐份看有沒有席位照著框內名字裡的句子做事」
問題:回頭條件要找的是「席位照著名字裡的句子做事」。但照做的席位多半不會在報告裡引用 ‹ ›,所以用 `‹` 篩出來的,是「有引用框內名字」的報告,正好漏掉靜默照做的那種。這個 grep 還會撈到不是席報告的檔:
- `r*-snapshot.md`:凍結計劃的副本,必含 ‹。
- `r*-intake.md`:收貨紀錄,也可能含 ‹。

原本寫的「翻席報告與派工單」範圍較廣,這次改窄了。
具體失敗情境:2026-12-15 到期時,有席位照檔名裡的句子回報 clean 卻沒引用名字,grep 列不到它的報告,回頭條件判成「沒有人照做」。
佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/governance/review-reports/code-派工鏡頭可指定目標repo/`。這個目錄的檔名有 `r*-正確性-sonnet.md`、`r*-snapshot.md`、`r*-intake.md` 等,`r*-*.md` 全部撈進來。
建議:把 grep 當輔助,另外加上「讀每輪 `rN-dispatch.json` 記的派工詞出現過名字句的輪次、對照該輪席報告的結論」。

severity: minor
blocking: 否 — 條款文字與測試斷言各自成立,只是一句話兩處說法不同。
引句:「撐過上限時 `listed`、`shown` 等於實際印出的標題數、`text_truncated` 是 true。」
問題:S43 寫 `listed`、`shown` 都「等於實際印出的標題數」,但測試的斷言是 `listed == len(heads)`(含「只列名」的行)、`shown == len(full)`(排除「只列名」)。兩個數字在這個情境裡不相等,條款字面讀起來卻像同一個數。
具體失敗情境:有人依條款字面改實作,讓 `shown` 也數「只列名」的標題,條款讀起來合規,綁定測試卻紅。
佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:51206-51216`(`listed`/`shown` 由 `_lens_spec_cap_and_count` 回),以及測試 patch 的 `t_dispatch_lens_spec_cap_by_node_and_json_counts` 最後一個 `check`。
建議:條款拆成「`listed` 等於印出的標題行數(含只列名)、`shown` 等於貼了內容的標題數」。

已讀,無 finding:
- **條款與綁定測試**:S38–S44 各自綁的測試都存在,斷言與條款一一對得上。9 支新測試全在 `_LR4_CLAUSE_TESTS` 清單裡。S35 新綁的 `t_dispatch_lens_hook_fail_reason_notice` 確實斷言範圍值帶反引號或 `$(` 時印 `<範圍>`。
- **數字與程式常數**:全部一致。
  - 20:`_ARCH_TARGET_LENS_NAMED`、`_LENS_SPEC_MAX_NAMED`。
  - 12000:`_LENS_SPEC_TEXT_MAX`。
  - 200:`_ARCH_TARGET_RULE_SHOW`。
  - 2000、500:`_ARCH_TARGET_LENS_FILES_MAX`、`_ARCH_TARGET_LENS_DECLS_MAX`。
  - 5.0 秒:`_ARCH_TARGET_LENS_BUDGET`。
  - 5000:`_LENS_SPEC_COMMIT_CANDS_MAX`。
  - 80、300:`_LENS_SPEC_NODE_NAME_MAX`、`_LENS_SPEC_PATH_MAX`。
  - S41 的隱形字碼位範圍與程式的 `_LENS_NAME_INVISIBLE_RANGES`、掛鉤的 `SPEC_NAME_INVISIBLE` 逐項一致。
- **筆記與程式現況**:
  - `_arch_target_text` 確實沒有 `show` 參數,出口、加框、上限都在裡面,代碼審與設計審兩條路都經它,筆記說法正確。
  - 掛鉤的 `*_NOTE` 加框、`*_TAIL` 在框外,與 codex-harness 新 WHY 和 S44 一致。
  - 範圍算不出時的手動指令確實寫 `<範圍>` 並講明去哪拿。
  - 做法 8 改指 S35 後,「被 `_spec_what` 取代」那句還在,變異仍能抓到。
- **目標架構段兩篇的說法**:Systems/arch-alignment-lens 與 Systems/派工鏡頭一致。兩篇都說兩條路經名字出口、整段加框、有總量上限;宣告讀分叉點版,可信的只有宣告,檔名是投稿者寫的。arch-alignment-lens 這輪只改了句子,沒有新增反引號路徑,沒有寫別人的檔。
- **目標段警告行**:警告文字只有固定字樣和第幾條,不回填專案寫的值,不需要名字出口。
- **REVISIT 與 `[因:]`**:Systems/派工鏡頭 WHY 的 `[因:]` 已拿掉字元集前提,與 r5 起「防線是框與標記、不是字元集」一致。計劃的 REVISIT 與派工鏡頭的 REVISIT 兩條同步更新,都含「框內名字」字樣,`_LR5_PLAN_REVISIT` 守衛仍成立。

最高等級 minor,blocking 0 條。
