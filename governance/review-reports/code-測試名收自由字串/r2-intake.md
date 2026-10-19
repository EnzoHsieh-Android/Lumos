# code-測試名收自由字串 r2 收貨與修正

七席報告(`r2-{正確性,邊界,資源,整合,通才,架構對齊,資安}-sonnet.md`)共 31 條,編號照編排者:正1–6、邊1–5、資1–2、整1–6、通1–6、架1–6(資安 clean)。major 11 條(正1、正2、正3、邊1、整1、通1、通2、通3、架1、架2、架3),blocking 10 條(架3 判 major 但不擋)。每條都開程式或實跑核對過,全部成立,**全部折入,無駁回**;資1 照編排者指示寫回頭條件、不改程式。base 5f8f8e48。

## 根因組

| 根因組 | 條目 | 修法 | 守它的測試 | 歸因 |
|---|---|---|---|---|
| A Playwright 結尾錨定 | 正1、正2、正4、正5、邊3、邊4、邊5、整1 | 實跑確認(見下)後統一一條規則:`-g` 展開成 `\s<跳脫後>(?:\s@\S+)*$`——後面容許 Playwright 接上的 tag(含 describe 繼承的);前面用 `\s` 不用 `(?:^|\s)`(-g 比的字串以檔名開頭,標題前總有空白),包裝字元沒有 `|`、`^`、`<`(Windows cmd.exe 的管線、跳脫、轉向)。撞名比之前拿掉標題尾巴的 @tag;自己那支只由「種類是測試、文字相同」的第一個佔用;describe 結尾加測試標題拼起來等於名字的另算撞名(`_name_collisions_across`,Jest 子字串、Playwright 整個標題,只看一層);字串標題頭尾有空白不收。文件改成「綁 describe 在 Playwright 上 No tests found、判紅」 | `t_playwright_tail_tags_and_own`(錨定式、包裝字元、describe 同名、標題寫 @tag、帶 tag 與同名的實跑判綠)、`t_name_collision_describe_plus_test`、`t_titled_names_with_edge_spaces_not_collected`、`t_playwright_name_filter_anchored`(期望改新錨定式) | 正1、正2、邊3:修復回歸(上一輪錨定沒算 tag、own 不看種類、包裝帶 \| ^);正5、邊4:原有漏查;邊5:修復回歸(實跑確認 Playwright 不修剪標題);正4:測試缺口;整1:修復造成的文件錯 |
| B 多行字串裡的 /* | 邊1 | `_C_STRIP_RE` 把三個雙引號(Kotlin、Swift、C# 11、Dart;Swift 前後的 # 留在程式碼)、三個單引號(Dart)、C# 的 @ 加雙引號(可跨行,兩個雙引號是跳脫)排在最前面一起認,一樣是展開式寫法;沒收尾的 /* 仍刪到檔尾(只有這樣才線性) | `t_comment_strip_multiline_strings`(Kotlin、Swift、C#、Dart 各一格) | 修復回歸 |
| C 第二種做法 | 架1、架2、架3、架4、架5、架6、正6、資2 | 架1:`_split_test_ref_ex` 多回「有沒有明寫前綴」並收 lenient 模式(殺傷力配方),`_kill_method_name`、`_bind_name_problem` 不再自己切;架2:`_strip_inline_markup` 加 `keep_test_fields`,欄位邊界走 `_slot_scan`,`_clause_visible` 只是一行包裝;架3:照編排者裁定兩條列舉路並存,`discover_test_methods` 旁註解分工(兩條都走 `_walk_test_files`、`_strip_test_comments`);架4:`_REGEX_FILTERS` 集中 regex 族;架5、正6、資2:檔名錨提示的「名字 → 檔」對照依 (根, profile 名, 錨) 掃一次快取(`_ANCHOR_MAP_CACHE`);架6:`_TEST_NAME_RULE_ZH` 搬到 `_test_name_ok` 旁、講齊 200 字與 Windows 字元,guard kill 兩處訊息也用它 | `t_kill_method_name_prefix_rules`、`t_bind_name_problem_pass_and_fullwidth`、`t_clause_test_tag_keeps_inline_code`、`t_clause_visible_linear`、`t_anchor_hint_scans_once`、`t_test_name_rule_text_complete` | 架1、架2、架5、正6:修復新增的重複;架3、架4、架6:修復新增、不一致;資2:修復新增的成本 |
| D 測試只比結構 | 正3、通1、通2、通3、通4、通5、通6 | 正3/通1:新增實跑 `guard kill --json` 的測試(撞名配方 verdict error、原因講撞名);通2:實跑 `guard settle`(不合法名 rc 2、守衛紀錄不動;前後空白去掉後寫入);通3/通4:`_bind_name_problem` 照讀取端同一支判(會被當成未定義前綴的才擋),補放行分支與全形冒號;通5:記憶體測試在 Windows 用 `_SrcOnly` 跳過、docstring 門檻改成跟斷言一致的 300MB;通6:Windows 上那半改成 `_SrcOnly`,不再空轉 | `t_guard_kill_collision_cli`、`t_guard_settle_name_checks_cli`、`t_bind_name_problem_pass_and_fullwidth`、`t_comment_strip_big_string_memory`、`t_test_name_ok_windows_shell_chars` | 測試缺口(修前沒有對應測試,不算回歸);通4:修復造成的寫讀不一致 |
| E 效能 | 邊2、資1 | 邊2:`_strip_inline_markup(keep_test_fields)` 走 `_slot_scan`(一趟、沒收尾就停)加兩邊由左到右的單趟比對,不再每個 [test: 各掃到行尾;資1:照編排者指示寫成 Systems/test-profile-multiplatform 的 REVISIT:2027-01-15,不改 | `t_clause_visible_linear`(4 萬字沒收尾、反引號兩種,< 1 秒) | 邊2:修復回歸;資1:原有(修後已減半) |
| F 文件 | 整2、整3、整4、整5、整6 | 整2:計劃剝註解那段首段標明是 r1 前說法、現行以子項為準,並補 r2 多行字串;整3:規格閘撞名那行改成 regex/regex_tail/plain、看全部標題、plain 分大小寫;整4:playwright profile 的程式註解改 regex_tail;整5:兩篇舊 Android 計劃「必須是識別字」各處加「已被取代」註;整6:計劃做法 1、Systems 的 `_test_name_ok` 那條補 Windows 字元,S64 寫齊八個字元 | (文件) | 整2:r1 留下;整3、整4、整6:修復遺漏;整5:原有漏查 |

## Playwright 實跑(order-web 副本 `/tmp/lumos-fix-web-gaps/ow`,1.64.1)

夾具:`test('login', {tag:'@smoke'})`、`test('pay')`、`test.describe('checkout', {tag:['@slow','@x']}){ test('checkout'); test('inner', {tag:'@a'}) }`、`test('trail ')`、`test(' lead')`、`test.describe('Foo'){ test('Bar') }`、`test('Foo Bar')`、`test('mid @tag text')`。

| -g | 選中 |
|---|---|
| `(?:^|\s)login(?:\s@\S+)*$` | login(帶 tag)1 支 |
| `(?:^|\s)checkout(?:\s@\S+)*$` | 只有 checkout › checkout 那支測試(describe 同名不算) |
| `(?:^|\s)inner(?:\s@\S+)*$` | inner(自己的 tag 加 describe 繼承的 tag)1 支 |
| `(?:^|\s)trail(?:\s@\S+)*$` | No tests found(標題是 `trail `,Playwright 不修剪) |
| `(?:^|\s)Foo Bar(?:\s@\S+)*$` | Foo › Bar 與 Foo Bar 兩支(describe 加測試拼名) |
| `\slogin(?:\s@\S+)*$` | login 1 支(只用 `\s` 也成立;單專案、雙專案都一樣) |
| `\sa.spec.ts(?:\s@\S+)*$` | No tests found(檔名碰不到) |

## 機械重現與紅綠(全部 HIT,無駁回)

| 編號 | 指令 | 輸出 | HIT/MISS |
|---|---|---|---|
| 正1、正2、邊3、邊4、邊5、正5 | 舊版(172db095)跑 `t_playwright_tail_tags_and_own`、`t_name_collision_describe_plus_test`、`t_titled_names_with_edge_spaces_not_collected` | `0 passed, 5 failed`、`1 passed, 2 failed`、`0 passed, 2 failed` | HIT |
| 邊1 | 舊版跑 `t_comment_strip_multiline_strings` | `0 passed, 4 failed` | HIT |
| 邊2 | 舊版跑 `t_clause_visible_linear` | `1 passed, 1 failed`(4 萬字沒收尾 4.48 秒) | HIT |
| 正3/通1 | guard kill 的 `if _coll:` 改成 `if False and _coll:`,跑 `t_guard_kill_collision_cli` | `0 passed, 1 failed` | HIT |
| 通2 | settle 的 `_bind_name_problem(` 改成註解,跑 `t_guard_settle_name_checks_cli` | `0 passed, 2 failed` | HIT |
| 通3/通4 | `_bind_name_problem` 改回「有冒號一律擋」,跑 `t_bind_name_problem_pass_and_fullwidth` | `1 passed, 2 failed` | HIT |
| 架5 | 提示改回不快取,跑 `t_anchor_hint_scans_once` | `1 passed, 1 failed` | HIT |
| 架6 | 舊版跑 `t_test_name_rule_text_complete` | `0 passed, 1 failed` | HIT |
| 其餘故障變體 | 錨定改回 `(?:^|\s)…$`、own 不看種類、拼名拿掉、頭尾空白照收、多行字串拿掉 | 對應測試各自翻紅(`3/2`、`3/2`、`1/2`、`0/2`、`0/4`) | HIT |

量時間與記憶體的四支(`t_clause_visible_linear`、`t_comment_strip_big_string_memory`、`t_js_comment_strip_linear`、`t_ran_evidence_vitest_playwright`)在背景同時跑全部相關子集的高負載下各跑三次,全綠。

## 跑過的子集

profile 75、discover 58、check_t 25(背景高負載那次 `t_codeloop_check_tension_warns` 一次 list index 例外,單獨重跑 9/9、整組重跑 25/25 綠,判為負載下的不穩,跟這次改動無關)、note_shape 279、spec_gate 265、clause 287、guard 915、kill 467、disposition 114、archive 25、bound_tests 156、test_refs 86、fix_check 174、spec_trace 23、binding 72、wording 66、trace 47、residual 466、question 150、lens 1130、nodehome 721、free_string 30、collision 27、playwright 21;`scripts/test_autonomous_loop.py` 191 支 OK。規格閘:76 條、綠 75、靠人 1、紅 0、弱證據 0(S74、S75 兩條句式被規格閘判看不懂,改寫措辭,綁的測試不變)。全套交給推送前閘。
