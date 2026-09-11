severity: minor
# 對答案報告

severity: minor

## 方法

讀畢 `Projects/每支檔有家_計劃.md`(239 行、[S1]–[S40] 共 39 條驗收條款)、三份 diff(程式 1792 行、測試 1321 行、文件 858 行),並在 worktree(`/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome`,HEAD=`5d9eae74`)裡實際跑了測試(唯讀,只執行不改檔):

```
python3 scripts/test_lumos.py -k nodehome            → 148 passed, 0 failed
python3 scripts/test_lumos.py -k lands_in             → 4 passed
python3 scripts/test_lumos.py -k disposal_gate_requires_landing        → 5 passed
python3 scripts/test_lumos.py -k disposal_landing_requires_spec_in_vault → 1 passed
python3 scripts/test_lumos.py -k design_dispatch_shows_landing         → 3 passed
python3 scripts/test_lumos.py -k new_system_with_code  → 5 passed
python3 scripts/test_lumos.py -k precommit_runs_home   → 5 passed
python3 scripts/test_lumos.py -k prepush_runs_home     → 6 passed
python3 scripts/test_lumos.py -k code_exts             → 26 passed
```
合計 203 項斷言全線通過、0 失敗——跟計劃「驗收怎麼跑」列的子集指令逐字一致。

## 逐條 [SN] 判定

- [S1] 已實作 — 第五份清單 `_NODEHOME_CODE_EXTS`(scripts/lumos:17385)接進 `t_code_exts_four_lists_agree`,實跑確認五份與 pre-commit 一致。
- [S2] 已實作 — `_nodehome_homes`(scripts/lumos:17677)只認 doing/done/stale、只看欄位值、字面比對鍵;`t_nodehome_home_definition`+`t_nodehome_other_branch_rename_uses_commit_spelling` 兩支都真的在驗這條(後者專測跨分支大小寫改名不誤判)。
- [S3] 已實作 — `_nodehome_evaluate` 的 `new-homeless` 分支(scripts/lumos:17787 起);`t_nodehome_check_blocks_new_homeless_file` 驗新增沒家擋、順手建家過、改名成新路徑擋,三種情境都對上條文。
- [S4] 已實作 — `home-removed` 分支;`t_nodehome_check_blocks_home_removal` 驗拿掉/刪節點/降狀態擋、改 stale 不擋(四種情境),精確對上「改成 stale 不算」那句。
- [S5] 已實作 — `legacy-homeless` reminder vs `write-back-homeless` block 分流;`t_nodehome_touched_legacy_homeless_warns_without_write_back` 驗「沒寫回只提醒/有寫回轉擋」,對應決策 d4。
- [S6] 已實作 — `_nodehome_render` 分資料夾分組、候選家、樣板、`_NODEHOME_MSG_CAP=10`(跟既有「改程式沒動圖譜」擋下訊息的 `${f:0:10}` 上限逐字一致,pre-commit:181);`t_nodehome_check_message_groups_and_truncates` 五項斷言都對上條文,非驗別的。
- [S34] 已實作 — 新專案首個提交(B=None)時所有新增檔都進 `code_added`,沒家即擋;`t_nodehome_birth_commit_requires_homes` 驗到。
- [S7] 已實作 — `_node_code_ref_tokens`(scripts/lumos:16172)被 `_refcheck_scan`、`_impact_reverse_lookup`、`_nodehome_refs` 三處共用;`t_nodehome_foreign_ref_uses_impact_extraction` 用 AST 靜態驗三者都呼叫同一支、且不再各自跑 `INLINE_CODE_RE`,再用行為面驗證推筆記與每支檔有家認得同一支檔——這條測的正是條文要求的「同一支」,不是驗別的。
- [S8] 已實作 — `_nodehome_refs`(scripts/lumos:17691)只收 `req`(需要家的檔)+裸檔名唯一才認;`t_nodehome_foreign_ref_definition` 驗測試檔/非程式檔不算、裸檔名唯一才算、不唯一不算認領,三項都對上。
- [S9] 已實作 — `foreign_now - foreign_before` 只算新增、`foreign-awakened` 另外處理「新增檔喚醒舊節點」;`t_nodehome_check_blocks_new_foreign_ref`+`t_nodehome_new_file_awakens_foreign_ref` 兩支合起來覆蓋條文的兩個子句(含「新開的節點全部算新」)。「已經寫在裡面的舊檔名只提醒」由決策 d1 定位在健檢(S28/S9 段)而非 home check 當場印,兩處口徑一致,非漏做。
- [S10] 已實作 — 訊息帶「它的家是 X——改寫成節點連結 [[X]]」與「還沒有家的指回安家」;`t_nodehome_foreign_message_points_to_home` 驗兩種情境。
- [S11] 已實作 — `code_touched` 非空才進規則三、`groups` 逐提交配對(`g_code`);`t_nodehome_route_skips_docs_only_commit`+`t_nodehome_route_counts_deleted_files`+`t_nodehome_diff_route_per_commit` 三支合起來覆蓋純圖譜提交跳過、刪檔算改動、逐提交隔離三個子句。
- [S12] 已實作 — `_nodehome_parse_note` 的 `sig`=(摘要,decisions 解析後值,正文),`t_nodehome_route_content_change_definition` 逐項驗四種欄位變動(簿記不算/摘要算/決策算/正文算)+驗不沿用正文雜湊;`t_nodehome_decisions_compared_by_value` 單獨驗「引號等價寫法不算」。
- [S13] 已實作 — `content_changed` 只收狀態能當家的節點,寫回要落在 `mine & routed[rel]`;`t_nodehome_check_blocks_write_back_to_non_home` 驗寫進非家節點擋、寫進家過、新開一篇不管任何改動檔也擋。
- [S13b] 已實作 — `write-back-homeless` 分支(僅當 `wb_files` 非空即有寫回時觸發);`t_nodehome_write_back_requires_every_changed_file_homed` 精確重現「散文塞進有家節點」的原始事故場景並驗擋、補家後放行。
- [S14] 已實作 — 訊息「兩條路」+「不另開逃生口」(scripts/lumos:17929 起 `_nodehome_render`);`t_nodehome_route_message_offers_two_ways` 驗兩條路都在、且沒有 `--allow` 這類單條放行旗標。
- [S15] 已實作 — `nudge`/`nudge-many` 用既有 `LUMOS_IMPACT_ABOUT_MAX`(預設 8)門檻;`t_nodehome_sync_nudge_by_home` 驗照家點名、超過 8 篇只印一句,兩者都對上。
- [S35] 已實作 — 規則三只在 `code_touched` 有內容變動的節點才擋,未寫任何說明時完全不擋;`t_nodehome_route_does_not_require_content_change` 驗到。
- [S36] manual — 天花板承認寫在計劃裡,`[manual:]` 未要求機械測試,屬性質相符。
- [S16] 已實作 — `_nodehome_resp_ok`(scripts/lumos:17454)長度+實字判準、`responsibility` 進 `SCALAR_KEYS`(scripts/lumos:10627);`t_nodehome_responsibility_field_validation` 連 `lumos set` 實際寫入都驗了。
- [S17] 已實作 — `becomes_home` 判斷含「b is None(新開)」與「狀態升格」兩種出生;`t_nodehome_check_blocks_new_node_without_responsibility`+`t_nodehome_planned_to_doing_requires_responsibility` 分別驗兩種出生情境。
- [S18] 已實作 — `cnt_now > cnt_before and cnt_now > cfg["max_files"]`(只數還存在的檔)、`max_files` 型別檢查含 bool 陷阱;`t_nodehome_check_blocks_growth_past_limit_without_responsibility` 四項情境(含「多的那項是刪掉的檔不算變多」)都驗到,含 bool/0/字串/合法值四種壞值。
- [S19] **縮水(測試面,見下方 finding F1)** — 實作正確(`cmd_new` scripts/lumos:12420 明寫 system/issue 都能用 `--code`),但綁定測試只驗了 system 與(project 的拒絕),沒有對 issue 正向建檔跑一次。
- [S20] 已實作 — `lands_in` 進 `LIST_KEYS`(scripts/lumos:10628)、`_lands_in_bad`(scripts/lumos:15010)驗格式;`t_lands_in_field_format` 驗白名單、合法/非法格式六種寫法、`lumos append` 真寫入。
- [S21] 已實作 — `_disposal_landing_step`(scripts/lumos:15020)照條款綁定同形狀(生效日 `_LANDING_GATE_SINCE`=2026-09-12、只認圖譜內 Projects 下 type:project 的 .md);`t_disposal_gate_requires_landing`(5 情境)+`t_disposal_landing_requires_spec_in_vault`(圖譜外冒充)兩支覆蓋條文全部子句。
- [S22] 已實作 — `_nodehome_landing_sizes`(scripts/lumos:22594)印計劃數/KEY 行數/合約數/管幾支檔/有沒有負責範圍;`t_design_dispatch_shows_landing_sizes` 逐項數字核對(2 份計劃、3 行 KEY、1 條合約、管 1 支檔)。
- [S23] 已實作(manual)— `skills/lumos-design-loop/templates.md` 架構對齊席派工範本加第四問「落點合不合理」,`t_nodehome_rules_in_hint_skill_and_discipline` 順帶機械驗到該節有這一問(雖然它的正式綁定是 [manual:]);人工那半(「下一次設計審報告裡看到它回答了」)確實要等下一次真實迴圈,計劃自己也承認這點,不算縮水。
- [S24] 已實作 — `cmd_home_check`(scripts/lumos:18078)、互斥群組防兩旗標同給;`t_nodehome_check_cli_modes`+`t_nodehome_cli_rejects_both_modes` 覆蓋四種放行/擋/fail-open 情境+用法錯誤。
- [S25] 已實作 — pre-commit Gate H 位置(scripts/hooks/pre-commit:115,在 Gate L 逐篇 lint 之後、Gate 3「改程式沒動圖譜」之前);`t_precommit_runs_home_check` 直接用字串位置斷言+行為面驗證五種情境(含合併提交跳過)。
- [S26] 已實作 — pre-push 新分支起點計算(scripts/hooks/pre-push:177-196,`_hrange` 邏輯)+`_nodehome_clamp_base`(scripts/lumos:17772);`t_prepush_runs_home_check`(6 情境:全新/一般更新/新分支/已在遠端/擋下/lumos 出錯放行)+`t_nodehome_diff_clamps_to_golive`(上線點回拉)完整覆蓋。
- [S27] 已實作 — `_gate_event_or_warn(..., "nodehome-check", ...)`(scripts/lumos:18078 起)含 `pairs`/`notes` 拆分、50/100 上限;`t_nodehome_check_gov_events_registered`+`t_nodehome_gov_event_shape`+`t_nodehome_gov_shows_pairs` 三支分別驗閘名登記、事件形狀(nodes/notes/pairs 各自對)、`gov --full` 印得出配對。
- [S37] 已實作 — `_NODEHOME_GATE_VALUES`(scripts/lumos:17393)on/warn/off,壞值退回 on;`t_nodehome_gate_switch` 驗三種模式+健檢開頭提醒。
- [S38] 已實作 — `_nodehome_reader`/`_nodehome_side` 的 `share`/`changed` 機制(scripts/lumos:17556、17612);`t_nodehome_reads_index_not_worktree`+`t_nodehome_diff_shares_unchanged_notes`+`t_nodehome_config_and_vendored_from_snapshot` 三支分別驗「讀索引不讀工作目錄」「起點側只讀有變動節點」「設定/工具自裝檔從被檢查版本讀」。
- [S28] 已實作 — doctor S8/S9/S10 三段(scripts/lumos ~2100 起,對照 a-patch)排在合約條數段之後、[H] 之前;`t_doctor_nodehome_sections`+`t_doctor_nodehome_lists_non_utf8_names` 驗順序與內容。
- [S29] 已實作 — `_nodehome_ledger` 與 `cmd_home_check`/`_nodehome_evaluate` 共用 `_nodehome_side`/`_nodehome_required`/`_nodehome_homes`/`_nodehome_refs`/`_nodehome_config`;`t_doctor_nodehome_sections_share_check_logic` 用 AST 直接驗共用關係,非驗輸出巧合一致。
- [S39] 已實作 — `_nodehome_golive`(scripts/lumos:17762)算上線點、三段各自分「上線後/上線前」;`t_doctor_nodehome_splits_bypassed_from_legacy`+`t_doctor_nodehome_bypass_split_all_sections` 分別驗單段與三段全覆蓋(含改名繞過算上線後)。
- [S30] 已實作 — SKILL.md、09-節點還原.md(快查表+完整版 reference.md)、graph-discipline.md(同步進 CLAUDE.md/AGENTS.md)、templates.md 五處都提到「每支檔有家」且給 `--code`/`--responsibility` 寫法;`t_nodehome_rules_in_hint_skill_and_discipline` 逐處機械核對,已實跑通過。
- [S31] 已實作 — `-z` 分隔、`nfc(os.fsdecode(...))` 無損解碼、`_nodehome_show` 顯示時才替代字元;`t_nodehome_check_edge_paths` 用真的非 UTF-8 檔名(`\xa4\xa4\xa4\xe5.py`)驗不炸、不擋、提醒。
- [S32] 已實作(manual)— `Verification/2026-09-11_每支檔有家落地.md` 記了提交前 0.65s、推送前 1 個提交 0.75s、10 個提交 0.81s,跟計劃「實務隱患」段的數字一致,量測方法與 [S38] 的共用機制對應。
- [S40] 已實作 — `_nodehome_list` 只收 `100644`/`100755`(scripts/lumos:17514);`t_nodehome_skips_symlinks_and_submodules` 造真的 symlink 與 160000 子模組項驗不算需要家的檔。

## 名詞段對照

- **需要家的檔**:四個條件(版控一般檔/程式副檔名或 #!/排除清單/UTF-8 檔名)都在 `_nodehome_required`(scripts/lumos:17639)逐一實作,`t_nodehome_required_files_definition` 十項子斷言(①–⑩)逐條對上,含「排除表跟 pre-commit `should_exclude` 逐字一致」的機械比對。
- **測試檔**:`_nodehome_is_test`(scripts/lumos:17462)先問測試地圖、再套 `_test`/`_spec` 等結尾規則,對上「Go 的 `foo_test.go`」這個計劃自己在「實作時對計劃的修訂」段落提到的補丁。
- **`node_home.ignore`**:`_nodehome_config` 的 `ignore` 處理與 `_cochange_excluded` 共用同一套 `fnmatch`/`**/` 前綴邏輯,測試驗了根目錄檔與非清單/非字串項的降級。
- **家**:見 [S2]。
- **別人的檔**:見 [S7][S8]。
- **內容有變**:見 [S12]。
- **讀哪個版本**:`_nodehome_reader`/`_nodehome_side`/`cmd_home_check` 內的 `from_snapshot=True` 讀法(config、vendored、圖譜位置都從 `tip_where`/`index` 讀,不讀磁碟),對應 [S38] 三支測試,已實跑驗證。

## 發現

### F1 [S19] 的「--code 給 issue 用」子句,綁定測試只驗了 system,沒有正向驗 issue
severity: minor
blocking: 否 — 實作本身正確(`cmd_new` 明寫允許 system/issue 兩種類型帶 `--code`,程式行為對得上條文),差的只是 `t_new_system_with_code_and_responsibility` 這支綁定測試沒有加一組 `new("issue", ...) --code ...` 的正向案例去證實 issue 那條路真的能過;全庫也搜不到任何其他測試補了這個案例。純測試覆蓋缺口,不影響行為,也不影響其餘 148+ 項驗收全線通過。
引句:「`--code` 事故筆記（issue）也能用」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md:131`
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/lumos:12420`(實作允許 issue)
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/wt-nodehome/scripts/test_lumos.py:36346`(綁定測試本體,通篇沒有 issue 案例)

## 總結

總結:最高 severity minor,blocking 共 0 條
