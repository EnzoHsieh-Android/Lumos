# code-測試名收自由字串 r1 收貨與修正

七席報告(`r1-{正確性,邊界,資源,整合,通才,架構對齊,資安}-sonnet.md`)共 34 條,編號照編排者:正1–7(正確性第 8 條 ⚠ 提問併入邊2)、邊1–5、資1–3、整1–5、通1–9、架1–3、安1–2。major 8 條(正1、正2、邊1、邊2、通1、通2、架1、架2),blocking 7 條(架2 判 major 但不擋)。每條都開程式或實跑核對過,全部成立,**全部折入,無駁回**。base_commit 960cd3e6。

## 根因組

| 根因組 | 條目 | 修法 | 守它的測試 |
|---|---|---|---|
| A 撞名只看可綁定的標題 | 正1、邊1、通1 | 撞名改數「篩選選得到的全部標題」:新增 `_raw_test_titles`(刻意放寬的掃描:it.skip、帶 ${ 的樣板、.each、含逗號或方括號、沒還原的跳脫、超過 200 字都算,只拿來數撞名);判定收成一支 `_name_collision_reason`;自己那支只扣一次,同名的第二支照算 | `t_name_collision_sees_skipped_titles`(五種被丟掉的標題各一格,加「沒撞名照常綠」對照) |
| B Playwright -g 比整串路徑 | 邊2(含正確性 ⚠) | 實跑確認後(見下),playwright 的 `name_filter` 改成 `regex_tail`:名字跳脫後錨在結尾 `(?:^|\s)<名字>$`;撞名只數結尾是這個名字、前面隔空白或整串相等的**測試**標題(describe、檔名、專案名都碰不到) | `t_playwright_name_filter_anchored` |
| C 守衛測試缺口 | 正2、通2、正4、通4、通7、通3、通5、通6 | 每條補一支拿掉實作會紅的測試;測試名不副實的改名、漏搬的斷言搬回、說明裡不存在的故障變體改寫 | `t_archive_protects_free_string_guard_name_cli`(實跑 archive)、`t_ran_evidence_vitest_playwright`、`t_test_ref_split_edges`、`t_clause_hang_list_capped`、`t_playwright_profile_discover`、`t_dart_profile_discovery_titles`、`t_js_free_string_test_names_discovered` |
| D 切法另寫一套、訊息三份 | 架1、架3 | `_dispositions_split_test` 只呼叫 `_split_test_ref`(新增 `_TestRefPrefixError` 帶前綴,訊息自己講);同族多找到一處:doctor Check T 的存在性檢查也自己 `split(":")`,一起改成 `_split_test_ref`;合法性白話收成 `_TEST_NAME_RULE_ZH` | `t_test_ref_split_edges`、`t_dispositions_free_string_names`、`t_bind_name_problem_shared` |
| E 剝註解 | 架2、資1 | 照編排者裁定:`c-style` 整個換成認得字串、保留字串內容的一趟剝法,所有用 c-style 的 profile 一起改(Kotlin、Swift、C#、Maestro、JS 三家、Dart),`c-style+strings` 保留;剝法從三種變兩種(`c-style-strings-kept` 拿掉)。正規式改展開式(`_C_STRIP_RE`,塊註解也展開) | `t_comment_strip_keeps_strings_all_c_style`(Kotlin、Swift 字串裡的 /*)、`t_comment_strip_big_string_memory`(8MB 字串、子程序量最大常駐記憶體)、`t_js_comment_strip_linear` |
| F guard kill 沒有撞名檢查 | 正3、邊3 | guard kill 跑配方前呼叫同一支 `_name_collision_reason`,撞名記錯誤不跑 | `t_guard_kill_shares_collision_check` |
| G 其他 | 正5、正6、正7、邊4、邊5、資2、資3、通8、通9、安1、安2 | 正5:`_bind_name_problem` 給 bind 與 settle 共用(去頭尾空白、多平台冒號名要寫已定義前綴);正6:`_apply_test_overrides` 收 `file_name_match`,doctor 懸空/偽證據那段加 `_anchor_migration_hint`;正7:`_test_in_tree` 每種引號的跳脫寫法各找一次;邊4:新增 `_clause_visible`,看得見的 [test:] 欄位裡的行內反引號照字面留(條款綁定、規格閘、待決問題共用);邊5:Playwright 宣告字面後面要接逗號;資2:小寫在 `_raw_test_titles` 先做好、每平台一次;資3:vitest 證據 `[^\n]{0,200}?` 限長;通8:`_kill_method_name` 拿掉布林路徑,未定義、長得像平台、冒號後緊接名稱照舊版剝前綴;通9:補回 swift/node 測試前的可信度註解;安1:Windows 上名稱含 `& | < > ^ % " !` 判不合法;安2:JS 正規式字面的限制寫成 Systems 節點的 REVISIT | `t_bind_name_problem_shared`、`t_playwright_file_anchor_hint`、`t_test_in_tree_escaped_title`、`t_clause_test_tag_keeps_inline_code`、`t_playwright_runtime_skip_not_collected`、`t_ran_evidence_vitest_playwright`(④ 長單行)、`t_kill_method_name_prefix_rules`、`t_test_name_ok_windows_shell_chars` |
| H 文件 | 整1–整5 | 整1:三篇計劃在 web-fe-knowledge、web-ledger、web-notes 三支分支上,合併後就存在,不改;整2:reference.md 那句與 Systems/linter精選目錄 的 dart 說法改寫,S25 grep 詞加「必須是識別字」「識別字名」;整3:test-profile-multiplatform 的 resolve_test_refs 條目改寫;整4:計劃做法 2 改成五種跳脫、做法 3 改成實際句式,做法 2/4 補 r1 後的改法;整5:調研筆記三處殘缺補字,W1 在「各組條數」與「多查到的」兩處改成已處理 | (文件) |

## (B) 實跑確認

order-web 副本(`/tmp/lumos-fix-web-gaps/ow`,Playwright 1.64.1,兩個專案 chromium、firefox):

| 指令 | 選中 |
|---|---|
| `-g 'login'` | 6 支(login.spec.ts 整檔、兩個專案) |
| `-g 'spec.ts'` | 6 支 |
| `-g 'chromium'` | 3 支(整個專案) |
| `-g 'Grp'` | 6 支(describe) |
| `-g 'login$'` | 2 支(只有標題是 login 的那支 × 兩個專案) |
| `-g '(?:^|\s)login$'` | 標題 login 與 `a (b) login` |
| `-g '(?:^|\s)relogin$'` | 只有 relogin |
| `-g '(?:^|\s)Grp$'` | No tests found |

結論:-g 比的是「專案名 檔名 describe 標題」整串;錨在結尾後只選中標題結尾是這個名字的測試,撞名只要數這種標題。

## 機械重現(全部 HIT,無駁回)

| 編號 | 指令 | 輸出 | HIT/MISS |
|---|---|---|---|
| 正1/邊1/通1 | 舊版 `scripts/lumos` 跑 `t_name_collision_sees_skipped_titles` | `1 passed, 5 failed` | HIT |
| 邊2 | 上表 `-g 'login'` | 6 tests in 1 file | HIT |
| 正2 | 歸檔 `guard_re` 換回 ASCII `\b`,跑 `t_archive_protects_free_string_guard_name_cli` | `1 passed, 1 failed` | HIT |
| 通2 | vitest 樣式改成 NEVERMATCH、playwright 樣式改成空字串、vitest 不限長,各跑 `t_ran_evidence_vitest_playwright` | 三種各 `3 passed, 1 failed` | HIT |
| 正4/通4 | 拿掉 `s.count("`") == 2`;拿掉「半形冒號才擋」,跑 `t_test_ref_split_edges` | `3 passed, 1 failed`;`2 passed, 2 failed` | HIT |
| 通7 | `_CLAUSE_HANG_SHOW = 1000`,跑 `t_clause_hang_list_capped` | `0 passed, 1 failed` | HIT |
| 資1 | `_C_STRIP_RE` 改回群組加星號,跑 `t_comment_strip_big_string_memory` | `0 passed, 1 failed` | HIT |
| 架2 | 舊版跑 `t_comment_strip_keeps_strings_all_c_style` | `0 passed, 3 failed` | HIT |
| 正3/邊3 | guard kill 那行改成 `_coll = None`,跑 `t_guard_kill_shares_collision_check` | `2 passed, 1 failed`(只有結構檢查那條紅;判定本身由 ①② 守) | HIT |
| 正5 | settle 改回只判 `_test_name_ok`,跑 `t_bind_name_problem_shared` | `2 passed, 1 failed`(同上,結構檢查) | HIT |
| 邊2 | 拿掉結尾錨,跑 `t_playwright_name_filter_anchored` | `3 passed, 1 failed` | HIT |
| 整2 | `grep -n 必須是識別字 skills/lumos-project-notes/reference.md`(修正前) | `1196:- 要綁的 Kotlin 測試函式名也必須是識別字——反引號中文名綁不上。` | HIT |
| 其餘 | 舊版跑新測試:`t_playwright_file_anchor_hint` 0/2、`t_test_in_tree_escaped_title` 1/1 紅、`t_clause_test_tag_keeps_inline_code` 0/2、`t_playwright_runtime_skip_not_collected` 0/1、`t_kill_method_name_prefix_rules` 2/1 紅、`t_test_name_ok_windows_shell_chars` 1/1 紅 | 見左 | HIT |

整1 不修的理由:那三篇計劃在別的分支上,合併後連結就成立;現在改成「待開」反而要再改回來。

## 順帶改的既有測試

- `t_doctor_kill_recipe_drift` ⑪b:doctor Check T 改走 `_split_test_ref` 之後,前綴含控制字元的 `[test:b\x1b[2K:…]` 不再被當平台前綴(不像平台名)。這格要守的是「未定義前綴那行要跳脫控制字元」,夾具改成 `[test:b:Test\x1b[2KLimitFive]`(前綴 b 未定義、控制字元在名稱裡),照樣守得住。
- 測試 `t_playwright_anchor_migration_hint` 改名 `t_playwright_file_anchor_hint`:名字裡的 migration 會被規格閘當成「不可逆」關鍵字。

## 跑過的子集

profile 75、discover 58、check_t 25、note_shape 279、spec_gate 265、clause 285、guard 912、kill 466(⑪b 修夾具後 30/30)、disposition 114、archive 25、bound_tests 156、test_refs 86、fix_check 174、spec_trace 23、binding 72、wording 66、trace 47、residual 466、question 150、lens 1130、nodehome 721,全綠。規格閘:64 條、綠 63、靠人 1、紅 0、弱證據 0。全套交給推送前閘。
