severity: minor

## F1 「從嚴的代價很小」這句判斷,對「合法的舊 panel 設計審」這條路不成立(雖然目前打不到)

severity: minor
blocking: no

**這在做什麼**:r3 把「編號 code 開頭卻不是 code-,看不出是哪一種審查」這種灰色地帶,從第二版的「從寬」改回「從嚴」——一律當代碼審處理,要求 `--report` 與 `--snapshot` 都帶齊。程式碼註解與圖譜筆記都用同一句話說服自己「這樣做代價很小」:

引句:「從嚴的代價很小:設計審進了處置閘之後本來也要帶這兩個。訊息照既有那幾處的說法講,不硬說它是代碼審。」

**我怎麼查的**:專案裡真的有兩個歷史迴圈編號落在這個灰色地帶——`code側刪除傳播守衛`(每筆帳其實都帶了 report/snapshot,不受影響)和 `codestage`(2026-07-18,panel 型舊迴圈,九筆帳**沒有一筆**帶 report/snapshot,見 `docs/.canary-log.jsonl:139`-`141`)。我用臨時 repo/vault(`/tmp/lh-r3-vault`)實際跑了 `lumos loop status <legacy-loop> --panel --min-seats 1`,confirm 這條「panel 回放」路徑(`_panel_retired_for` 判 cutoff=2026-08-26,codestage 全部早於此)完全不查 `report_path`/`snapshot_path`(`scripts/lumos:7961` 的 `_panel_retired_for`、`scripts/lumos:7975` 的 `_panel_round_conjuncts` 都沒有這兩個欄位的檢查)。也就是說「設計審進了處置閘之後本來也要帶這兩個」這句話**只對 2026-08-25 之後開的、走 `--disposal` 新閘的設計審成立**(`scripts/lumos:18049`-`18052` 那段 `[disposal] 留痕` 確實對任何 loop kind 都無條件要求 report+snapshot);對 codestage 這種舊 panel 型設計審不成立——它合法、仍在用的收斂路徑(`--panel`)從沒要求過這兩個欄位,r3 的說法沒有把這條路徑算進去。

**為什麼目前沒被打到**:我在乾淨 vault 裡真的對這個灰色地帶的 loop id 補跑了一次 `canary record`(不帶 --report/--snapshot),結果卡在一條**更早就存在、與這次 patch 無關**的規則:`scripts/lumos:7615`-`7618`(2026-08-26 起「審查席記帳一定要附 --report」,對任何 loop id 都成立,不分 code/design)。這條舊規則已經先一步擋死了「幫 codestage 這類舊迴圈補一筆新帳」的路,所以 r3 新加的 `--snapshot` 要求目前打不到真正的案例——但這只是運氣好(舊帳全部沒有 report,--report 先擋),不是 r3 的「從嚴」判斷本身站得住腳。

**結論**:這句判斷是過度概括,圖譜筆記與程式碼裡的說法應該更精確地寫成「走 `--disposal` 新閘的設計審才需要」,而不是「設計審……本來就要」。目前無實際可觸發的壞影響(report 先擋),不擋這次通過,但下次有人動 `--report` 那條規則或開一條新的「補記舊帳」旁路時,這句過度概括的判斷可能會被沿用出真正的誤擋。

## 驗過的路徑(其餘攻擊面)

- **同檔三處既有呼叫點對 None 是否真的都是從嚴**:核對 `_gated_seats_for`(`scripts/lumos:17688`-`17692`,None 不 skip、當代碼審處理走資安席)、`_disposal_clause_step`(`scripts/lumos:17812`-`17815`,None 不 skip、當設計審處理走條款綁定)、`_disposal_landing_step`(`scripts/lumos:17869`,同上邏輯)——三處對 None 確實都不放行(skip),方向與 r3 新增的第四處(`cmd_canary` 裡 `_rk != "design"`)一致,`_rk` 判斷本身(`_roster_kind`,`scripts/lumos:9646`-`9653`)也照抄同一支函式,沒有另立一套判準。
- **訊息在三種情況下各印什麼**:實跑驗證(`/tmp/lh-r3-vault`)——`_rk=="code"` 印「代碼審(<loop>)」;`_rk is None` 印「迴圈 <loop>(編號 code 開頭卻不是 code-,看不出是哪一種審查,照最嚴的當代碼審)」,不再硬講成代碼審;`_rk=="design"` 完全不進這段新邏輯,落到既有 T6 定錨區塊(`scripts/lumos:7748`-`7751`,未被本次 patch 動到)。三種各自的訊息互不混淆。
- **`--outcome` 互斥排除是否真的必要/正確**:確認 `outcome is not None` 時,上游 `scripts/lumos:7603`-`7606` 早已拒收任何審查欄位(含 report/snapshot)並回 rc2,所以新增的 `outcome is None` 判斷條件雖是防禦性重複,但邏輯無害、測試 ⑥ 也驗證了通過。
- **`_codeloop_record_valid` 的 returncode 分流(128 vs 1)**:用真 git repo 驗證 `git merge-base --is-ancestor` 對不存在的 sha 回 128(非 0/1),`scripts/lumos:7710`(對應行,即新增的 `anc.returncode not in (0, 1)` 分支)正確攔截並給出「找不到」訊息而非「壓過提交」訊息,不會誤導。
- **`_codeloop_guard_verdict` 接回 `_vwhy` 是否有未賦值風險**:`_vwhy = None` 初始化在前(`scripts/lumos:29147`),只有 `rec_sha != marker_sha` 且 `rec_status in (passed, skipped)` 才會被賦成非 None,其餘分支安全落回舊的固定字串(`scripts/lumos:29161`),沒有 NameError 或誤用舊值的路徑。
- **翻紅釘/mutation 測試**:把 `_rk != "design"` 改回 `_rk == "code"`(模擬 r2 的「從寬」bug)在臨時複本上重跑,`t_code_loop_record_requires_provenance_from_first_row` 的 ⑤ 兩個斷言如預期翻紅(6 passed, 2 failed)——確認這支測試真的釘住了 r3 這個修正,不是空測試。
- **實際跑測試**(真跑不是讀):`t_code_loop_record_requires_provenance_from_first_row`(8 passed)、`t_codeloop_record_invalid_after_squash_says_why`(4 passed)、`t_codeloop_check_after_squash_says_why`(3 passed)、`t_canary_record_*`(29 passed)、`t_codeloop_record_*`、`t_codeloop_guard_*`(22 passed)全綠,無回歸。
- **patch 完整性**:`sha256sum` 核對凍結 patch 與派工單宣稱的 `2ce96382…` 一致;`wc -l` 核對 234 行一致。
- **筆記與程式碼對得上的部分**:圖譜筆記(`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`)描述的「r1/r2 方向相反、r3 照既有慣例裁從嚴」與程式碼的實際判斷(`_rk != "design"`)、訊息差異化都對得上,唯一對不上的就是上面 F1 那句過度概括的「代價很小」。
