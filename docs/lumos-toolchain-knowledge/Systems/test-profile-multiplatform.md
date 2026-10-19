---
type: system
status: done
created: 2026-07-02
updated: 2026-10-15
self_audit: sonnet/2026-08-21
about_code_stamp: batch-2026-08-23/2026-08-23/082e219ba898
related:
  - "[[Systems/check-t-sentinel]]"
verified_by:
  - "[[Verification/2026-07-02_multiplatform-test-binding]]"
  - "[[Verification/2026-07-25_CheckT-Python-profile]]"
  - "[[Verification/2026-08-21_L4交叉審計30節點清帳]]"
  - "[[Verification/2026-09-08_iOS與Node補棧合成樣本測試]]"
  - "[[Verification/2026-09-12_Java補棧合成樣本測試]]"
plan_refs:
  - "[[Projects/多平台合約測試綁定_計劃]]"
tags:
  - type/system
  - status/done
  - scope/guards-gates
summary: |-
  KEY:單一圖譜跨平台綁測試——config 從單 test_profile 擴為 platforms 多根多 profile map;`[test:]` 的「平台:名稱」寫法 的**平台前綴**(android/backend/maestro/playwright)★注意:平台前綴≠profile 名★——profile 名截至 2026-09-12 共 10 個鍵(csharp-xunit/kotlin-junit/java-junit/maestro/playwright/dart/python/swift-xctest/node-jest/node-vitest,其中 node-vitest 是 node-jest 的別名)——★這串每次補棧都要跟著改★:2026-09-08 加 swift/node、2026-09-11 加 python 時都漏了,2026-09-12 補回;兩者同名的只有 maestro/playwright,android 對應 kotlin-junit、backend 對應 csharp-xunit
  KEY:向後相容以「config 有無 platforms 鍵」為信號(multiplatform bool)——無 platforms=legacy,resolve 不切分整串當方法名,舊 test_profile/裸 `[test:]` 只寫名稱 照舊
  KEY:default_platform 規則——多平台缺省即報錯(不猜);未定義平台前綴 `[test:]` 寫了沒定義的平台前綴 Check T 明確報錯(不 fallback)
  KEY:新增內建 profile maestro(綁 flow name:,file_must_match=^appId: 濾非flow yaml,\s*$ 錨多字 name NO MATCH)/ playwright(2026-10-15 起改收句子名:標題整串比對,見 [[Projects/測試名收自由字串_計劃]];maestro 刻意不跟)
  KEY:file_must_match 是 discover 選填 knob(讀檔後去註解前過濾,.get() 相容無此鍵的舊 profile)
  KEY:guard bind/scaffold --platform 旗標——平台另帶(2026-10-15 起 bind 收句子名、名稱有冒號時必帶 --platform;scaffold 拿名字產程式碼,維持識別字,見 [[Projects/測試名收自由字串_計劃]]),bind 寫 `[test:]` 的「平台:名稱」 去重/verify 比完整 ref;scaffold 範本/scaffold_ext/測試目錄偵測跟平台 root 走
  KEY:天花板——Check T 只驗測試識別子存在,不驗跑綠(CI 的事);E2E 要裝置/瀏覽器(無裝置才 skip);跨 repo 只讀不寫
  KEY:swift-xctest / node-jest(=node-vitest 別名) profile(2026-09-08,[[Projects/iOS與Node後端補棧_計劃]];★尚無真專案跑過,只有合成樣本測試★)=第 7、8 個 profile:SWIFT_TEST_RE 兩代並收(XCTest `func test*` 靠 lookahead 限前綴、Swift Testing `@Test` 巨集任意名,修飾詞可夾中間)+suffix 目錄模式(頂層 *Tests,pure/state 排除 *UITests,behavioral 只認 *UITests);JEST_TEST_RE 認 test/it/describe('名') 含 .only/.skip/.concurrent(2026-10-15 起標題整串比對)+檔名錨 *.test.*/*.spec.*(`__tests__/` 下無後綴檔不在錨內=天花板)+scaffold_name {m}.test [test:t_swift_profile_discovery] [test:t_node_jest_profile_discovery]
  KEY:dart profile(2026-07-26,taroko_app Flutter 接入)=第 6 個 profile:DART_TEST_RE 認 test('名')/testWidgets('名')(2026-10-15 起標題整串比對,$ 插值不收,見 [[Projects/測試名收自由字串_計劃]])+檔名錨 *_test.dart+comment_strip=c-style(Dart 有雙式註解;2026-10-15 起 c-style 剝註解認得字串)+scaffold_name={m}_test;dirs pure=test/、behavioral 含 integration_test/ [test:t_dart_profile_discovery]
  KEY:python profile(2026-07-25,[[Projects/CheckT-Python-profile_計劃]])=第 5 個 profile:行首錨 PYTHON_TEST_RE+檔名錨 file_name_match(basename fnmatch,新欄位,與 maestro file_must_match 內容錨是兩機制)+comment_strip="none"+scaffold_name 模板;discover_test_methods 的註解剝離改語言感知(c-style 預設向後相容)——根因:原對所有語言剝 /*..*/,Python 檔中文註解/字串的巧合配對會吃掉大段內容(本 repo 實測 260→94)。新欄位放 TEST_PROFILES dict 靜態值(multiplatform 路徑繞過 load_test_profile,dict 直達兩路徑都吃到)
  KEY:★[2026-09-12 代碼審 r1 三席同報]JAVA_TEST_RE 原本的無界中段是個洞,不是取捨★——①資安席造出可用的假證據:掛註解的誘餌方法不是 void、後面一支完全沒掛註解的空方法被 discover_test_methods 收成真測試,合約閘照樣放行(打穿 bound-tests-gate 的核心保證) ②正確性席:@DisplayName 這類帶字串的註解裡若出現 void 某某( ,真測試整支消失 ③外家席與邊界席各自量到 1MB 的檔要 43 秒,而這支掃描每次健檢與推送前都跑。修法三件一起:中段改成括號感知且不准跨 ; 與方法體大括號、上限 600 字元;java-junit profile 的 comment_strip 改 "c-style+strings"(掃描前連字串字面一起剝,新模式,其他 profile 不受影響);方法名首字允許非 ASCII。★KOTLIN_TEST_RE 同病(席位量到兩萬個註解 11 秒)也加了上限★ [test:t_java_profile_discovery,t_test_regex_scan_bounded]
  KEY:[2026-09-12 Java 補棧]加內建 profile java-junit(exts=.java、目錄慣例照抄 kotlin-junit 的 test/androidTest)。★方法正則不能照抄 Kotlin 那條★——Kotlin 版用 [^{]*? 擋住跨方法體,但 Java 的參數化註解自己帶大括號(@ValueSource(ints = {1, 2, 3})),照抄會整支漏掉;JAVA_TEST_RE 改用非貪婪 .*?,靠「JUnit 規定測試方法必須回傳 void」收斂成「註解之後最近的一個 void 方法名」。代價:@Test 標在非 void 方法上(JUnit 會拒跑)會抓到下一個 void 方法名。補上這支 profile 的副作用是 .java 的 symbol_profile 不再被標「猜得很弱」(反查的搭檔判定找得到同語言的測試 profile 了) [test:t_java_profile_discovery]
  DEP:[[Systems/check-t-sentinel]]
  TEST:t_maestro_profile_discover｜t_playwright_profile_discover｜t_load_platforms｜t_resolve_test_refs｜t_multiplatform_guard_list｜t_multiplatform_doctor_check_t｜t_archive_live_guard_multiplatform｜t_guard_trace_multiplatform｜t_guard_bind_scaffold_platform(全綠(★「333」為當時全量口徑,已漂;相關 9 支測試現合計 25 斷言全過(2026-08-21 程式碼實證)★))
  VERIFY:[[Verification/2026-07-02_multiplatform-test-binding]]
  WHY:[2026-10-15 [[Projects/筆記指令健檢與規格閘小修_計劃]]]平台 root 不存在的警告同一次執行只印一次(模組層集合記 (平台, root)),load_platforms 每個呼叫端共用 [出處:web 示範規格閘一次跑印三行同一句] [因:重複的警告讓人以為有三個問題] [test:t_platform_root_warning_once]
aliases:
  - 多平台合約測試綁定
about_code:
  - scripts/lumos
---
# 多平台合約測試綁定（test-profile multiplatform）

讓**單一知識圖譜**把 ★INVARIANT★ 的 `[test:]` 綁到**不同平台**的測試（C# xunit / Kotlin JUnit / Maestro E2E / Playwright），解決舊機制「一 repo 一 profile、只掃自己 repo」的三道牆。設計與審計全紀錄見計劃節點 [[Projects/多平台合約測試綁定_計劃]]（design-loop 4 輪收斂）。

## 核心元件（scripts/lumos）

- `load_platforms(repo_root)`：讀 `.lumos/config.json` 的 `platforms` map（多根多 profile）。回 `{multiplatform, default_platform, platforms:{plat:{profile,root}}}`。無 `platforms` 鍵 → legacy 單一條目（向後相容）。
- `resolve_test_refs(inv_text, platforms, default_platform)`：`[test:...]` → `[(platform, name)]`。(2026-10-15 起每一格交給 `_split_test_ref`,規則見下面〈測試名收自由字串〉那段:單平台整串是名稱;多平台冒號前是已定義平台才是前綴,只有「半形冒號而且前面長得像平台名」的未定義前綴才 raise,其他整串是名稱。)
- `_platform_test_index(repo_root)`：惰性建「平台 → (method set, code haystack)」索引，Check T / `classify_invariants` / `cmd_archive` 共用（haystack 也跨 repo）。
- 新內建 profile `maestro` / `playwright`（見 `TEST_PROFILES`），`discover_test_methods` 新增 `file_must_match` 選填 knob。
- **本節點亦為 `test_profile` 機制（原 P5，`csharp-xunit`/`kotlin-junit`）的權威說明**——P5 當初未建 Systems 節點，此處一併涵蓋四 profile，不另建重複節點（L4 審計 2026-07-02 決策）。`csharp-xunit`=預設（`.cs`/`[Fact]`/頂層 `*Tests` suffix）、`kotlin-junit`=Android 單元（`.kt`/`@Test`/`src/` 下 rglob）。
- `guard bind` / `guard scaffold` 新增 `--platform` 旗標。

## vitest 與 .jsx(2026-10-15,[[Projects/前端框架從vue分出_計劃]] F1)

- 測試 profile 沒有新增:`node-vitest` 仍是 `node-jest` 的別名(同語法、同檔名錨),init 對 Vite 專案寫 `node-vitest` 只是讓設定看得出跑法;跑過證據那份表也加了同一個別名,見 [[Systems/bound-tests-gate]]。
- 符號 profile `typescript` 收 `.jsx`(原本沒有任何 profile 認領,純 `.jsx` 專案 init 猜不出 symbol_profile)。測試 t_init_skeleton_jsx_symbol_profile。

## 剝註解改成認字串(2026-10-15,[[Projects/前端框架從vue分出_計劃]] 代碼審 r3 G1)

`_strip_test_comments` 的 c-style 與 c-style+strings 兩種模式改走共用的 `_strip_c_comments`(Kotlin 建置檔判平台也用它,不留第二套):一條從左到右的掃描,字串裡的 `//` 與 `/*` 不再被當成註解(原本先剝註解再清字串,字串裡的網址會被截斷、`"/*"` 會吃掉後面一大段);c-style+strings 照舊把字串內容清空、保留引號。掃描本體跟測試名收自由字串那支 `_C_STRIP_RE` 合成一套(合併主線時收掉 `_C_SCAN_RE`):多認三個雙引號、三個單引號、C# 的 @ 加雙引號與反引號字串,量詞用佔有式。沒閉合的字串吃到行尾(多行字串與區塊註解吃到檔尾),不回溯,`"\` 重複這種 512KB 輸入也在毫秒級。python profile 照舊不剝。測試 t_strip_c_comments_shared_and_linear、t_strip_test_comments_strings_mode_kept。

## 相關系統
- [[Systems/check-t-sentinel]]（Check T/K 機制；本機制擴充其 discover 面為多平台多根）

## 測試名收自由字串(2026-10-15)

前端慣例是用一句話當測試名,舊設計「識別字名才可綁」讓示範專案 15 條條款全懸空。改法與理由在 [[Projects/測試名收自由字串_計劃]](推翻本篇原本 playwright 與 dart 的 NO MATCH 設計;多根多 profile 那條決策照樣成立)。

- 名稱規則一支 `_test_name_ok`:不空、至多 200 字、不以減號開頭、不含方括號與半形逗號、沒有控制或格式字元;中文、空白、括號、冒號、引號、全形標點都可以。Windows 上另外不收 `& | < > ^ % " !`(cmd.exe 不認單引號);擋下訊息的白話是 `_TEST_NAME_RULE_ZH` 一句。 [test:t_test_name_ok_rules]
- 一格 `[test:]` → (平台, 名稱) 一支 `_split_test_ref`(`resolve_test_refs`、`_test_names_of`、`_kill_method_name`、`_dispositions_split_test` 都改呼叫它):單平台整串是名稱;多平台第一個冒號(半形或全形)前是已定義平台才是前綴,長得像平台名的未定義前綴照擋(不猜),其他整串是名稱;只切半形逗號;反引號整串包住才拆殼。 [test:t_test_ref_split_rules]
- 字串標題型 profile(node-jest/node-vitest、playwright、dart;`name_filter` 是 regex、regex_tail 或 plain)收第一個引數的完整字面:後面要接逗號或右括號、前面不能是點號或識別字、只認 \' \" \\ \` \$ 跳脫、Dart 的 $ 插值不收、字面限 200 字;過不了名稱規則的(含逗號、方括號)不收進集合。Kotlin 反引號名照舊。 [test:t_js_free_string_test_names_discovered] [test:t_js_title_partial_or_member_not_collected] [test:t_kotlin_backtick_comma_name_still_collected]
- 剝註解的 `c-style`(所有用它的語言,不只這幾家;代碼審 code-測試名收自由字串 r1 編排者裁)改成一趟認字串(原樣留)與註解(刪掉),展開式正規式、沒結尾的 `/*` 刪到檔尾,時間與記憶體都線性;java 的 `c-style+strings` 走同一趟、另把字串內容清空(見上〈剝註解改成認字串〉)。已知限制:JS 的正規表示式字面(`/'/`)會被當成字串開頭。 [test:t_js_comment_strip_keeps_strings] [test:t_js_comment_strip_linear]
- playwright 補檔名錨 `*.spec.*`/`*.test.*`;自訂測試檔名的專案在設定寫 `file_name_match`(單平台 `test` 裡,多平台寫在那個平台),舊綁定在不合錨的檔裡時 doctor 會講。Playwright 的宣告字面後面要接逗號(測試本體裡的 `test.skip('原因')` 不算宣告)。 [test:t_playwright_file_anchor_hint] [test:t_playwright_free_string_names_discovered]
- 多平台每個平台設定(跟 run_cmd 同一層)也收 `exts`/`scaffold_ext`/`method_regex`/`file_name_match` 覆蓋(`_apply_test_overrides`)。 [test:t_multiplatform_method_regex_override]
- `guard bind` 收句子名,多平台名稱有冒號時必帶 `--platform`;`guard scaffold` 拿名字產程式碼,維持識別字,擋下時指去 guard bind;`guard trace` 找驗證紀錄改用 `_test_name_boundary_re`(英數頭尾才加邊界)。 [test:t_guard_bind_free_string_name] [test:t_guard_scaffold_rejects_free_string_name] [test:t_archive_and_trace_free_string_names]
- 撞名(`_name_collision_reason`,推送前閘、規格閘、guard kill 共用)數的是「篩選選得到的全部標題」(`_raw_test_titles`,含掃描不收的 skip、樣板、逗號名),不只可綁定的。Playwright 的 `-g` 比「專案名 檔名 describe 標題」整串,所以 name_filter 是 regex_tail:名字錨在結尾 `\s<名字>(?:\s@\S+)*$`(容許 Playwright 接在標題後面的 tag;不用 `|`、`^`,Windows cmd.exe 會當管線),撞名只數結尾是這個名字的測試標題(比法見下面代碼審 r3 那條(用實際篩選式比、不先剝 tag);describe 同名不搶自己那支;describe 加測試拼起來等於這個名字也算);綁 describe 標題在 Playwright 上會選到零支,印 No tests found 並回 1,判紅。標題頭尾有空白的不收。剝註解另認多行字串(三個雙引號、三個單引號、C# 的 @ 加雙引號)。 [test:t_playwright_tail_tags_and_own] [test:t_comment_strip_multiline_strings] [test:t_name_collision_sees_skipped_titles]
- 撞名的已知天花板:跨標題的比對(Jest 拿「describe 標題 + 空白 + 測試標題」整串比、Vitest 用「 > 」連,綁的名稱剛好橫跨兩段)數不到。
- FACT:名稱篩選都是拿正規式比對完整名稱的子字串;Jest 30.5.2 的 -t 不分大小寫、describe 與測試標題用空白連;Vitest 5.0.4 的 -t 分大小寫、用「 > 」連,對不到也回 0;Playwright 1.64.1 的 -g 不分大小寫、標題路徑用空白連,頭尾都是斜線的字串當正規式字面,對不到印 No tests found 並回 1;-g 比的字串含專案名、檔名、describe 與標題(-g login 連 login.spec.ts 整檔都選中、-g chromium 選中整個專案),錨在結尾只選中標題結尾是它的;比的字串在標題後面接上 tag(含 describe 繼承的),標題頭尾的空白不修剪,describe 與測試同名時錨定只選中那支測試 [來源:外部] [confirmed:2026-10-15] [查:order-web 的副本實跑 -t/-g,Jest 用 npx 快取裡的 30.5.2]
- REVISIT:2026-12-15 查消費專案的測試檔有沒有「單引號的正規表示式字面(`/'/`)後面接著被註解掉的測試」讓假名字被收進測試集合的案例;有就給 c-style 剝法加正規表示式字面的辨認(代碼審 code-測試名收自由字串 r1 資安席)。
- REVISIT:2027-01-15 查消費專案有沒有單一測試檔裡幾十 MB、滿是跳脫字元的字串(c-style 剝註解的展開式正規式對跳脫字元每個仍佔一格狀態,45MB 全是跳脫要 2GB 以上;代碼審 code-測試名收自由字串 r2 資源席);有就把跳脫也併進同一段字元類或改手寫掃描。
- (代碼審 r3)撞名一律拿執行器實際會用的篩選式比每個標題(regex_tail 用錨定式對「空白 + 標題」search,不先剝 tag);describe 加測試的拼名只在同一支檔裡配對(`_raw_test_titles` 帶來源檔);標題索引 `_TitleIndex` 每個平台建一次,每個綁定名只比含這個名字的標題。 [test:t_name_collision_across_same_file_only] [test:t_name_collision_uses_real_filter] [test:t_name_collision_scales]
- (代碼審 r3)頭尾有空白的標題不收只用在 Playwright(regex_tail);Jest、Vitest、Flutter 照收修剪後的名字。Windows 上 {method} 改用 list2cmdline。剝註解與撞名掃描的正規式量詞改佔有式,8MB 塞滿孤立引號的多行字串額外記憶體從 350MB 以上降到個位數 MB。 [test:t_titled_names_with_edge_spaces_not_collected] [test:t_run_cmd_windows_quoting] [test:t_comment_strip_multiline_memory]

