severity: major

審查範圍:docs patch 為主,tests patch 為輔,對照 `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/` 的修補後狀態(只讀)。

三份設計迴圈手冊的 spec-freeze 流程與程式一致。我逐項對過 `_spec_freeze_from_commit`、`_spec_freeze_out_path`、`cmd_spec_freeze`、`_SPEC_FREEZE_FAIL_CODES`:
- 計劃在別的工作樹時,只跑不帶 `--out` 的路徑寫法,不留檔。
- 回會談目錄用提交寫法帶 `--out governance/review-reports/<編號>/rN-snapshot.md`,不建新提交。
- 失敗代碼九個,與計劃一致。
- `--reviewed` 填 `sha256sum <rN-snapshot.md>` 沒問題,因為快照與派工當下的計劃是同一份位元組。

沒挑出問題的項目:
- 入口 WHY(`lumos-cli-lifecycle.md`)的 `[代價:]`、範圍外(`GIT_DIR`/`GIT_WORK_TREE` 不清)、五條 `[test:]` 都在,測試函式都存在。
- 我另外查了新增或修改的每一個 `[test:]` 標籤,指到的測試函式都存在。
- 這次動到的 `★INVARIANT★` 合約行(`design-loop.md`、`lumos-cli-lifecycle.md`)沒被破壞。

以下是發現。

severity: major
blocking: 是 — 計劃自己列的「要一起改」兩處手冊沒改,照著做會跑出被程式拒絕的指令,或把檔寫進別人的工作目錄。
引句:「要一起改的說法(列全)」
問題:計劃做法 11 列了 `skills/lumos-project-notes/reference.md` 的 dispatch-lens 那格和 `skills/lumos-project-notes/commands/05-設計審查迴圈.md` 的指令表,都要一起改。這份 patch 與目前工作樹都沒改它們,兩處還在教舊的一步寫法:「在計劃所在的工作樹跑 `lumos spec-freeze <計劃.md> --out <rN-snapshot.md>`」。`commands/05` 是專案 CLAUDE.md 指定的指令速查入口。
具體失敗情境:
- 編排者照 `commands/05` 在別的工作樹敲 `--out rN-snapshot.md`。這個位置不在 `governance/review-reports/` 底下,回 `out_outside_repo`,rc 2。
- 編排者改成補上 `governance/review-reports/x/` 再敲。快照就寫進那個工作樹,那可能是別的會談的工作目錄。r2 的 G3 修的正是這件事,全域規則也禁止碰別的會談的工作目錄。
- 新增的手冊守衛 `t_design_loop_manuals_spec_freeze_wording` 只讀 SKILL、templates、reference 三份,抓不到這兩處。
佐證:file: `skills/lumos-project-notes/commands/05-設計審查迴圈.md:31`、file: `skills/lumos-project-notes/reference.md:83`、file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭可指定目標repo_計劃.md:121`

severity: minor
blocking: 否 — 計劃文字自相矛盾和過期的條款數,程式行為以新寫法為準。
引句:「計劃在別的工作樹時,在那個工作樹跑 `lumos spec-freeze <計劃> --out <快照>`」
問題:做法 8 在同一節內互相矛盾。第 39 行(patch 沒動)還寫繞法要帶 `--out <快照>`,patch 新增的第 42 行(`SPEC_FREEZE_HINT`)寫「不帶 `--out`」。程式與掛鉤用的是不帶 `--out` 的新寫法。另外〈實作紀錄〉開頭仍是「S1–S22 各一支測試」,但條款已加到 S24。
具體失敗情境:實作者或下一個 session 讀到第 39 行,會把掛鉤說明行改回帶 `--out`。因為 `t_dispatch_lens_hook_spec_worktree_fail_notice` 只比對 `lumos spec-freeze` 和 `LUMOS-SPEC:` 字樣,改回去測試照綠(見第 4 條)。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭可指定目標repo_計劃.md:86`、file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭可指定目標repo_計劃.md:195`

severity: minor
blocking: 否 — 守衛只比對固定字串,手冊的流程被改回舊的不寫檔寫法時不會紅。
引句:「都寫了 --out 放 governance/review-reports/ 與會談目錄的提交寫法」
問題:`_lr2_design_loop_manual_problems` 只查三件事:
- 關鍵句存在。
- 五個舊說法子字串不在。
- 檔裡有 `governance/review-reports/` 和 `<完整提交編號>:<路徑> --out` 這兩個字串。

它不查「別的工作樹那一步不帶 `--out`」,也不查舊的 `--out <rN-snapshot.md>` 單步寫法。`_LR2_FREEZE_OLD` 也漏了 `{工作副本路徑}`,而 `templates.md` §7.6 的「被審材料:{工作副本路徑}」仍指向工作副本(它是代碼審與設計審共用的格子,至少該加註設計審用 rN-snapshot)。
具體失敗情境:把 SKILL 第 3 步的「(不帶 `--out`:只建不掛分支的提交…)」改成「帶 `--out governance/review-reports/…`」。關鍵句和提交寫法字串都還在,測試全綠,但流程已退回「在別人工作樹留檔」。這支測試的變異只涵蓋「拿掉關鍵句」和「加回指向工作副本」兩種。
佐證:file: `skills/lumos-design-loop/templates.md:332`、file: `scripts/test_lumos.py`(patch 內 `_LR2_FREEZE_OLD` 與 `_lr2_design_loop_manual_problems`)

severity: minor
blocking: 否 — 條款 S24 的一半由沒綁定的測試守;繞法句的新內容沒被釘住。
引句:「(另由 t_spec_freeze_out_only_review_reports 守)」
問題:
- S24 的「`--out` 是 `.lumos/evil.json`、`.claude/settings.json`、`.GIT/…` 兩種寫法都回 `out_outside_repo`」這一半,寫在括號裡,不是 `[test:]`。綁定測試 `t_spec_freeze_commit_form_from_session` 並沒有測這些情況。
- S23 只列 repo 外、符號連結、`..`、`.git`,沒有「只收 `governance/review-reports/`」這條正向規則。這是 r2 最重要的收窄,卻沒有任何一條條款帶 `[test:t_spec_freeze_out_only_review_reports]`。
- 掛鉤的新繞法句(不帶 `--out`、回會談目錄凍快照)沒有被任何測試釘住。S13 測試只比對 `lumos spec-freeze` 與 `LUMOS-SPEC:`,把繞法句改回舊的 `--out <快照>` 照綠。

具體失敗情境:把 `_spec_freeze_out_path` 的 `_SPEC_FREEZE_OUT_DIR` 檢查拿掉,`.lumos/evil.json` 又寫得出去。`t_spec_freeze_out_must_stay_in_repo` 與 S24 綁定的 `t_spec_freeze_commit_form_from_session` 都不測這個,只有沒綁在任何條款上的 `t_spec_freeze_out_only_review_reports` 會紅,條款層看不出缺口。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭可指定目標repo_計劃.md:162`、file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭可指定目標repo_計劃.md:163`、file: `scripts/hooks/claude/dispatch-lens-hook.py:73`、file: `scripts/test_lumos.py:43018`

severity: minor
blocking: 否 — `r2-fix.json` 的文件條目有一筆綁了守不到內容的測試,另一處改動沒有對應條目。
引句:「修法:`_vault_node_path` 先驗圖譜資料夾本身與上層每一段都不是符號連結」
問題:
- `r2-fix.json` G4 把「`Systems/派工鏡頭.md:_vault_node_path`」綁到 `t_lens_repo_notes_spec_freeze_and_entry`。這支測試只查派工鏡頭節點沒有輪次流水帳(`### 代碼審 r1 修正`、`四個分支`),完全不看 `_vault_node_path` 那些 PITFALL 內容在不在,條目與測試無關。
- 這份 patch 改了 `codex-harness.md`(掛鉤改照 `spec_source` 判計劃類失敗),G4 裡沒有 codex-harness 的條目。
- SKILL、templates、reference 三個條目共用同一支只比對字串的測試,見第 3 條。

具體失敗情境:有人把派工鏡頭節點的 `_vault_node_path` PITFALL 整條刪掉,帳面顯示 `fixed` 且綁測試,測試照綠。
佐證:file: `governance/review-reports/code-派工鏡頭可指定目標repo/r2-fix.json`(G4 的 `Systems/派工鏡頭.md:_vault_node_path` 條目)、file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md`

最高等級 major,blocking 1 條。
