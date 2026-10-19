# code-前端框架從vue分出 r2 收貨與處置

七席收齊,共 28 條(編號照編排者:正1–5、邊1–4、資1–2、整1–6、通1–6、架1–3、安1–2):major 10 條(邊1、正1、架1、資1、正4、資2、正2、整1、通1、通2)、其餘 18 條 minor。全部折入,駁回 0 條。每個程式根因先寫會紅的測試再改(改前跑紅、改後跑綠),另做一輪「把修法拿掉」的翻紅,見下表。修補範圍:base b9ff5494 → 本輪提交。

## 根因組

| 根因組 | 條目 | 修法 | 守它的測試 | 歸因 |
|---|---|---|---|---|
| (A) 剝註解不認字串 | 邊1、正1 | `_kt_strip_comments` 改成一條從左到右的交替式掃描(`_KT_SCAN_TOKEN`:三引號原始字串、雙引號、單引號、`//`、`/* */`),字串原樣留下、只拿掉註解,未閉合的區塊註解或原始字串吃到檔尾。先搜過既有的 `_strip_string_literals`:它是逐行挖空字串、不認註解也不認跨行原始字串,不能共用 | t_kt_strip_comments_strings_aware、t_kt_strip_comments_linear_on_hostile_input、既有 t_kt_build_comments_and_ktor_dependency_not_server | 修復回歸(r1 才加的剝註解) |
| (B) 架構:第二種快取做法、名字、時鐘 | 架1、架2、架3 | 判定記憶改模組層 `_KT_BUILD_VERDICT_CACHE`(自己管 64 份上限、丟最早的),拿掉中段 `import functools`;`_NODE_FLAVOR_CACHE` 改名 `_WORKTREE_TEXT_CACHE`;`_ROLE_CLOCK` 模組全域改成 `_review_roles(..., now=None)` 參數(預設呼叫當下取 `time.monotonic`——第一版照先例寫 `now=time.monotonic`,讓既有 t_review_role_bookkeeping_remaining_budget 對 `time.monotonic` 的 patch 失效而紅,改成 None) | t_kt_build_verdict_cache_bounded、t_review_roles_kt_build_verdict_memo(改成數掃描次數)、t_worktree_text_shared_reader(hasattr 改成共用快取的行為)、t_review_roles_classify_loop_respects_budget(改用 now=) | 修復回歸(r1 折入時帶進來) |
| (C) 匯入樣式 `^\s*` 搭多行旗標 | 資1、正4 | 全檔 grep 出 8 處 `^\s*` 搭 `re.M`/`(?m)` 一次改成 `^[ \t]*`:`_ROLE_ANDROID_IMPORT`、`_ROLE_UIKIT_IMPORT`、`_ROLE_UI_IMPORT` 三種、另有 3 處別的功能(`def` 搜尋、引句正規化的 `>`、決策 `id:` 搜尋;引句正規化之後會把空白摺疊,行為不變);加一支掃原始碼的守衛 | t_role_import_regexes_blank_lines_fast、t_no_multiline_caret_whitespace_star | 原有漏查(r1 只修了點名的那條) |
| (D) 批次讀取把超限當成不存在 | 資2、正2 | `_review_roles` 先問大小(`_nodehome_cat_sizes`)再帶 `sizes=` 讀,物件在但超過單檔或整批上限沒讀的回空字串(在但讀不了,停在那一層),跟工作樹路徑同語意 | t_review_roles_oversize_build_stops_not_climbs、t_review_roles_total_cap_stops_not_climbs | 原有漏查(修前已如此,r1 的總量上限多一條觸發路徑) |
| (E) 文件 | 整1–整6、邊2 | 整1:d2 content 用 decision-amend 改成跟程式一致(先剝註解、行首 `android {`、只認外掛宣告、依賴座標與 ktor-server 不算),〈做法〉B10 訊號同改;整2:B10 接線(張力候選只出適用題、整組派生一處)與讀法④(共用讀檔、判定記憶、超限停住);整3:F1 判定寫成依賴優先、跑過證據樣式寫現行版、S1 補「依賴看不出測試工具」前提;整4:lumos-cli-lifecycle 斷句;整5:效能檢核目錄三題標 android_only、min_lines 寫「增行,推播數全部」;整6:lint-waivers 第一條理由更正為「修前 600d7b02 就是 13,本修補沒讓它變複雜」;邊2:選「文件明講」——表態閘與效能檢核目錄寫明改檔前推播送來的是 old_string 加 new_string,分不出增刪,刻意數全部 | 文件條目沒有自己的測試;fix.json G5 用同主題的程式測試守(t_kt_spring_dependency_coordinate_not_server 等) | 整1–整5 修復回歸(r1 改程式沒回頭改計劃);整6、邊2 原有漏查 |
| (F) 測試缺口 | 通1–通6 | 通1:t_ran_evidence_bounded_middle_fast(`"Tests: 1 " * 15000` 無 passed,3 秒內;席位給的 `"Tests 1 "` 輸入在安2 把開頭錨回 `Tests:` 或行首之後只剩一個起點、拿掉上限也照綠,翻紅時發現,換成帶冒號的輸入——每個 `Tests:` 都是起點,拿掉上限 22 秒、有上限 0.07 秒);通2:t_review_roles_total_cap_stops_not_climbs(上限調成 120 位元組,斷言判不出);通3:t_kt_flavor_reads_with_limits(超限 Android 建置檔判不出,攔參數看 head 與 max_bytes);通4:eslint 守衛改成對 ESLint 文件列的檔名雙向比;通5:S35 docstring 改成 8 萬字與 45 秒;通6:`_node_pkg_text` 內聯(唯一呼叫處直接呼叫 `_worktree_text`),兩條 hasattr 結構斷言拿掉或改成行為 | 同左 | 原有漏查(通1–通4、通6);通5 修復回歸 |
| (G) 測試檔判定 | 邊3、安1 | 「檔名本身是 test/spec」改成只認小寫 `(?-i:test|spec)` 加 `[cm]?[jt]sx?` 副檔名;`/tests?/` 改成 `(?:^|/)tests?/`,repo 根也算 | t_test_pat_lowercase_test_ext_only、既有 S43 與 t_test_pat_bare_names_and_irreversible_shared | 修復回歸(Test.tsx、test.py);原有漏查(根目錄 tests/) |
| (H) 判定口徑 | 邊4、正3、正5 | 邊4:eslintConfig 的值要是物件;正3:Spring 只認 `id(…)`/`id '…'`/`apply plugin:` 形式與 Maven 的 spring-boot-maven-plugin、spring-boot-starter-parent,依賴座標不算;正5:`_stack_platform_excluded` 不數工作樹已不存在的 .kt | t_eslint_config_key_must_be_object、t_kt_spring_dependency_coordinate_not_server、t_kt_deleted_file_not_counted | 邊4 修復回歸;正3 未判定(r1 就是這個樣式);正5 原有漏查 |
| (I) 跑過證據錨定 | 安2 | 開頭錨回 `Tests:` 或行首(允許空白與色碼)的 `Tests`,仍限長、數字前不是數字、空白不跨行 | t_ran_evidence_anchored_to_summary_line、既有 t_ran_evidence_colored_per_line_reader | 修復回歸(r1 放寬時拿掉了錨) |

## 翻紅驗證(把修法拿掉,確認對應測試紅;每次都還原並比對原檔一致)

| 拿掉的修法 | -k | 結果 |
|---|---|---|
| 剝註解改回兩趟、不認字串 | strings_aware | 4 紅 |
| 判定記憶不設上限 | cache_bounded | 1 紅 |
| `_ROLE_ANDROID_IMPORT` 改回 `^\s*` | role_import_regexes | 1 紅(時間斷言) |
| 超限的檔回 None | oversize_build | 1 紅 |
| Spring 依賴座標也算伺服端 | dependency_coordinate | 1 紅 |
| 刪掉的 .kt 照數 | deleted_file_not | 1 紅 |
| 跑過證據中段不限長 | bounded_middle | 第一版測試 0 紅(見上通1);換輸入後 1 紅 |
| 跑過證據不錨 `Tests:`/行首 | anchored_to_summary | 1 紅 |
| 檔名 test/spec 改回不分大小寫、任何副檔名 | lowercase_test_ext | 5 紅 |
| eslintConfig 不看值的型別 | key_must_be_object | 4 紅 |
| 工作樹建置檔不帶大小上限 | reads_with_limits | 2 紅 |

量時間的測試(blank_lines_fast、role_import_regexes、linear_on_hostile、bounded_middle、long_line_fast、classify_loop)在 6 個 CPU 滿載程序下各跑三輪,全綠;門檻都是 3 秒,對照的壞寫法在同輸入是 20 秒以上,classify_loop 用虛擬時鐘不看牆鐘。

## 駁回與機械重現

駁回 0 條。席位的觀察在 b9ff5494 上都重現得出來(新測試改前跑紅即是重現):邊1/正1 兩個反例、資1 13 萬空行、資2 子模組超限、正3 Spring 依賴座標、正5 刪檔、通1 拿掉上限照綠(改前樣式本身有上限,所以新測試改前是綠的;用翻紅表證明它守得住)、邊3 Test.tsx、邊4 eslintConfig null、安2 行中 Tests 2 passed。

## 沒做到的部分

- 邊2 選了「文件明講」而不是改 hook:hook 送來的內容是新舊字串接在一起,要只數新字串得改受錨點保護的 hook 與它的送出格式,這輪不動;只會多問、不漏問。
