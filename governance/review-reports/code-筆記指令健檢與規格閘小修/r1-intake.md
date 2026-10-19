# code-筆記指令健檢與規格閘小修 r1 收貨與修正

七席(正確性、邊界、資源、整合、通才、架構對齊、資安)共 36 條:major 8(正1、正2、正3、邊1、整1、整2、安1;正2 與正1、安1 同根),其餘 minor。全部修,駁回 0 條。修正紀錄 `r1-fix.json`(base 55da596f)。

## 錨不到的四句引句:機械重現

| 編號 | 指令 | 輸出 | 判 |
|---|---|---|---|
| 邊2 | `git show 55da596f:scripts/lumos \| grep -nF 'return "git 列不出檔案清單,沒辦法先跑筆記形狀擋"'` | `43864:        return "git 列不出檔案清單,沒辦法先跑筆記形狀擋"` | HIT(引的是 diff 外既有的 `_drift_fix_shape_err`) |
| 整4 | `git show 55da596f:docs/command-reference.md \| grep -nF 'lumos summary-line <node> "<old fragment>" "<new fragment>"   # change one summary line without hand-editing the header fields'` | `53:lumos summary-line <node> …` | HIT(diff 外的文件) |
| 整5 | `git show 55da596f:docs/lumos-toolchain-knowledge/Projects/雙向門放行_計劃.md \| grep -nF '推送前**:讀審查帳裡 \`kind: spec-gate\`、計劃仍 \`doing\`、**且本次推送範圍碰到該計劃檔'` | `212:- **推送前**:讀審查帳裡 …` | HIT(diff 外的筆記) |
| 架3 | `git show 55da596f:scripts/lumos \| grep -nF 'print("    4. 在同一個工作目錄跑 lumos spec-gate'` | (無輸出);放寬成 `grep -n '4\. 在同一個工作目錄跑 lumos spec-gate'` → `9225:        print(f"    4. 在同一個工作目錄跑 lumos spec-gate {…} 拿到紅與留痕,再 git resto…` | 字面 MISS(原文是 `print(f"`,引句少了 f);內容 HIT,照內容修 |

## 先紅後綠

每個程式根因先寫測試、在 55da596f 的程式上跑紅,修完綠。重現與紅的證據:
- (A) 正1、正2、安1:三支新測試在修之前全紅,輸出是「提醒:甲_計劃 已完成,留痕對不上…不擋」「留痕裡的測試找不到…不擋」——跟正確性席 exp1、exp2 的重現一致。
- (B) 正3、邊2:gate=off、gate=warn 時 summary-add/summary-line 被「現況描述沒寫來源」擋 rc2;非 git 目錄 summary-line 印「git 列不出檔案清單」rc2。
- (C) 邊1:`src/app v2/gone.py` 被截成 `src/app: ok`,`src/中文 目錄/不存在.py` 變成 `src/中文: missing`。
- (D) 資1:3000 個空白的已排除行 48.91 秒;資2:8000 對路徑 8.30 秒(上限 4 秒)。
- (F) 邊3、邊4、安2:「只要求尚未上線」「等到期尚未付款」「尚未上線前/後都一樣」「尚未部署前-測」「FACT:目前還沒有提交前/推送前掛鉤」五句修前都不唸。
- (G) 正4:`TypeError: '>' not supported between instances of 'tuple' and 'float'`;正5:`scripts/runtime/` 列 missing;邊6:`--nth 2` 沒 `--after` 照寫;邊5:同時印綠勾;安3:有未提交改動時沒警告。

## 根因組與修法

| 根因組 | 條目 | 修法 | 守它的測試 |
|---|---|---|---|
| A 推送閘對 done 計劃寬待過頭 | 正1、正2、安1;整5 併入 | 寬待只給推送範圍起點就已是 done 的(`_spec_gate_status_at` 讀起點那一版的 status;這次才改 done 的照 doing 嚴);寬待時過期改走 `_spec_gate_push_nogo_only` 照查不做清單,找不到的測試只拿掉那幾支、其餘照跑、紅了照擋。d3 翻案標註補在雙向門放行〈推送前〉那段與規格閘那行 KEY | t_prepush_spec_gate_done_stale_still_checks_nogo、t_prepush_spec_gate_done_gone_still_runs_rest、t_prepush_spec_gate_done_this_push_is_strict、t_prepush_spec_gate_done_in_range(④⑤ 改成起點就 done 的情境) |
| B 摘要寫前檢查不看開關、非 git 退步 | 正3、邊2;整3、整4、整7 併入 | `_summary_write_shape_check` 先判是不是 git:summary-line(nongit_ok)跳過、summary-add 擋並講要在 git 專案用;再讀 note_shape 總開關:off 不跑、warn 只提醒。寫入原語數字、兩份指令參考、三篇 updated 同步 | t_summary_write_follows_gate_and_nongit |
| C refcheck 截斷帶空白路徑 | 邊1 | `_ref_cmdline_token` 只在第一個詞之後有 `-` 開頭的旗標時才截;沒旗標的帶空白路徑照整串核對 | t_ref_path_spaced_dir_not_cut、t_ref_path_first_word_of_command |
| D 推送前擋下 | 整1、整2 | 計劃 S10 的 `[[Systems/x]]` 包反引號;test-profile-multiplatform 四處示意 `[test:…]` 包反引號、一行程式碼推得出的 FLOW 舊行刪掉(改它就要補來源,但它講的是程式流程,依紀律不該寫) | `doctor --ci` 與 `note-shape --diff 0beb6d7d..HEAD` 都 rc0(提交後跑,見回報) |
| E 效能 | 資1、資2 | 已排除行先數冒號,不到兩個就不交給 `_EXCLUDED_RE`(不改正則,免動門規則版本);標了新增的集合在 refcheck 與 doctor P 段都移出迴圈 | t_lint_excluded_line_many_spaces_fast、t_refcheck_planned_many_paths_linear |
| F 條件詞與子句標點太寬 | 邊3、邊4、安2 | 條件開頭詞拿掉「只要」「等到」;「時」「前」後面的子句標點改明列清單 `_NS_NEG_CLAUSE_PUNCT`(斜線、連字號、底線不算);量測程式同步 `COND_OPEN_V4`、`CLAUSE_PUNCT_V4`,釘常數的測試補一對 | t_note_shape_negation_condition_clause、t_note_shape_negation_lexicon_pinned、t_note_shape_negation_v4_matches_measure |
| G 其他程式小問題 | 正4、正5、邊5、邊6、邊7、安3、架1–架8 | 正4 讀不懂的 ts 當 -inf、同時間取後列的;正5 送 git 時保留結尾斜線;邊5 有 pending 時不印綠勾;邊6 `--nth` 要配 `--after`;邊7 S32 條款改寫成「工作目錄的路徑樹只列一次」;安3 印補跑步驟前先看 `git status --porcelain`,有未提交改動先警告,換回那步用 `--source=HEAD`;架1 有改的那半用 `_nodehome_changed_vs_disk`、讀磁碟加捷徑守衛;架2 cochange check 沒帶範圍也照 --staged;架3 指令獨立一行;架4 `_doctor_s14_plan_status`;架5「同一條」收成 `_probe_cond_keys`(推送閘 `_drift_probe_old` 與 lint 共用);架6 `_summary_line_rebuild` 改呼叫 `_fm_touch_updated`、`_fmt_decision_value` 改用 `_has_line_break`;架7 留痕不走 `_gate_event_fit` 並註明理由(裁掉 tests 等於少跑測試);架8 doctor S14 段改合讀兩本帳 | t_spec_gate_pick_bad_ts、t_ref_path_ignored_dir_trailing_slash、t_doctor_s8_sees_worktree_home、t_summary_add_nth_needs_after、t_spec_gate_manual_red_checks_uncommitted、t_home_and_note_shape_default_staged、t_cochange、t_doctor_s14_labels_red_at_gate_time、t_lint_born_old_line_quiet、t_summary_line_replace、t_spec_gate_record_in_governance_log |
| H 測試 | 通1–通4 | 通1 刪新寫的重複 `_sg_records`;通2 ③ 改直接斷言總目錄那句在;通3 補「other.py 不被列」與「不同時印綠勾」兩條;通4 欄位清單改對照 `SCALAR_KEYS`/`COND_KEYS` 常數 | t_set_help_lists_keys、t_docs_catalog_count_wording、t_doctor_s8_sees_worktree_home |
| I 文件 | 整3、整6、整7 | 見 B、G 兩組;整6 計劃第 7 節改寫成實際輸出「○ planned」與統計行字樣 | — |

## 改到既有測試的期望(行為照修法改)

- t_prepush_spec_gate_done_in_range ④⑤:寬待只剩「起點就已完成」,④ 先讓測試綠、⑤ 改成先提交 done 再改名。
- t_cochange 「皆缺 rc2」:改成照 --staged(架2,三支一致)。
- t_spec_gate_pick_bad_ts ②:同時間取後列的(兩本帳同秒寫入時新的那筆在後,t_spec_gate_record_in_governance_log ③ 抓到)。
