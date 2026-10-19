---
type: project
status: doing
created: 2026-10-15
updated: 2026-10-15
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/test-profile-multiplatform
  - Systems/規格閘
  - Systems/bound-tests-gate
  - Systems/筆記內容閘
  - Systems/lumos-guard
  - Systems/guard-kill
related:
  - "[[Projects/多平台合約測試綁定_計劃]]"
decisions:
  - content: 測試綁定收自由字串測試名:Vitest/Jest/Playwright(連帶 Dart)的 it/test/describe 標題整串比對,含中文與空白;條款懸空時規格閘不再印 ✓,改印警示並逐條列出。推翻 Projects/多平台合約測試綁定_計劃 D4 與 Systems/test-profile-multiplatform「識別字名才可綁、含空白 NO MATCH」的設計(那是正文設計,不是該篇的決策紀錄;該篇 d1 多根多 profile 照樣成立、不作廢)
    id: d1
    context: Web 示範前端(order-web)15 條條款全懸空:前端慣例是句子名,lumos 掃描只收識別字,規格閘卻印「條款綁定 ✓」讓人以為綁好了;多平台設定下 test.method_regex 逃生口也收不到。舊設計當時的理由:不動 IDENT_RE 免得牽動 C#/Kotlin 守衛、避免部分擷取的假證據、當時沒有網頁 repo。替代方案:①維持舊設計,要求前端測試改識別字名(違反前端生態慣例,示範證明不會有人照做);②只修規格閘的 ✓ 顯示、不收句子名(懸空照舊,綁定機制對前端等於不存在);③加引號包名的新語法收任意字元(同類新語法先前被否決,舊筆記讀不懂)
    why_chosen: 使用者 2026-10-15 裁。舊理由只剩第一條要處理,改成 IDENT_RE 只留給產程式碼的 guard scaffold、綁定另用一條名稱規則;部分擷取的問題靠擷取整個字串字面解掉;沒有網頁 repo 的前提已經不在。不加新語法,舊筆記一字不改照讀
    decided: 2026-10-15
    valid: true
pending_questions:
  - id: Q1
    text: 風險高的計劃有懸空條款時,規格閘要不要從只警示改成擋下?(建議:先只警示,上線 4 週看警示後有沒有人補綁,沒有再改擋)
    class: 守衛強度
    stage: 實作
    status: 延後
    reason: 使用者這次只要求懸空要明顯標出,沒有要求擋;先看警示有沒有效
---
# 測試名收自由字串_計劃

> 白話:前端的測試習慣用一句話當名字(`it('下單後按鈕會停用')`),lumos 目前只認得 `pay_guard` 這種「識別字」名,句子名一律掃不到,條款綁上去全部懸空,規格閘卻還印「✓」。這份計劃讓測試綁定收整串句子(含中文與空白),懸空時規格閘改印明顯的警示,跑測試時把句子安全地交給測試工具的名稱篩選。來源:Web 示範前端(order-web)15 條條款全懸空,比對表見 [[Projects/Web示範前端缺口_調研]] 的 W1。

PRIOR-ART: 不新建機制、不加新語法。①名稱照原樣整串比對,沿用 Kotlin 反引號測試名早已收空白名的做法(KOTLIN_TEST_RE 收 `` `名` ``、`_kill_norm_method` 拆殼);②測試工具那邊:Jest 的 `-t`、Vitest 的 `-t`、Playwright 的 `-g` 都是拿正規式比對「完整名稱」的子字串,flutter 的 `--plain-name` 是純文字子字串——所以跳脫只對前三者做,跳脫字元集照 MDN 的 escapeRegExp(`.*+?^${}()|[]\`);③平台逃生口沿用單平台已有的 `test.method_regex` 與 `_safe_user_regex`,只是讓多平台也讀得到。曾被否決的 `[test:名稱(理由)]` 新語法(Projects/測試綁定一行一支提醒_計劃)本計劃不碰:舊寫法一字不改照讀,只放寬「名字裡可以有什麼字」。
RETIRE-IF: 上線 8 週內,自由字串綁定造成的假綠(綁定判成綁好、測試工具卻跑了別支或零支而閘報綠)出現 2 次以上,而同期它幫忙抓到的懸空與紅燈少於這個數——把 JS 三家與 Dart 的掃描收回只認識別字,規格閘的懸空警示保留。

## 舊決策與為何翻案

舊設計在 [[Projects/多平台合約測試綁定_計劃]] 的 D4 與 [[Systems/test-profile-multiplatform]] 的摘要:「識別字名才可綁,含空白的 title NO MATCH,是刻意設計」。當時三個理由:

1. 不改 `IDENT_RE`,免得牽動 C#/Kotlin 既有守衛;
2. 擷取群組 `([A-Za-z_]\w*)` 後面要緊接閉合引號,多字 title 整個不匹配,不會「抓到前半個字」製造假證據;
3. 當時沒有任何網頁 repo,Playwright profile「先內建、不接線」。

為何翻案(使用者 2026-10-15 裁):

- 理由 3 不在了:這次示範就是真的網頁專案,15 條條款全懸空,前端的慣例就是句子名——要求改成識別字等於要求整個前端生態改寫法。
- 理由 2 照樣守得住:新的掃描擷取「整個字串字面」,不是前半段;部分擷取的假證據不會出現。
- 理由 1 改成分開處理:`IDENT_RE` 只留給會「產生程式碼與檔名」的 `guard scaffold`,綁定名稱另用一條名稱規則(做法 1),C#/Kotlin/Python 的識別字名照樣合法、判法不變。
- 舊設計還有一個沒寫出來的代價:掃不到的句子名在規格閘只算「懸空、只提醒」,而那一行仍印「✓」,作者以為綁好了。

舊計劃的決策 d1(設定改成多根多 profile)跟這件事無關、照樣成立,不作廢;被推翻的是 D4 那段正文設計與 Systems 節點的兩行摘要,實作時在那兩處標明被這篇取代(做法 7)。

## 做法

### 1. 一條名稱規則、一套切法

- **名稱合法性只有一支函式** `_test_name_ok(name)`:去頭尾空白後不是空的、至多 200 字、沒有控制字元與換行、不以 `-` 開頭、不含 `[` `]` `,`(半形逗號)。中文、空白(中間的空白原樣保留、不壓縮)、括號、冒號、引號、全形標點都可以。Kotlin 反引號包住的名稱照舊先拆殼再判。
- 取代目前分散的三種判法:`_KILL_METHOD_OK_RE`(`^[\w .]+$`,不收括號、冒號、引號)、綁定路徑上的 `IDENT_RE`、`_NsTrJudge._plat` 自己寫的「含方括號就壞名」。
- **切法照 `resolve_test_refs` 現行規則**,只把各處抄的版本對齊它:
  - 一個標記裡多支用半形逗號分開;**全形逗號是名稱的一部分**(中文句子常有「，」)。`_test_names_of`(note-shape 與 doctor S20 用的那支)目前連全形逗號也切、全形冒號也當平台前綴,改成跟 `resolve_test_refs` 一樣。2026-10-15 全庫 grep:`[test:` 值裡用全形逗號或全形冒號的 0 處,改了不影響舊筆記。
  - 多平台時第一個半形冒號前面是平台前綴,前綴沒定義就判壞名(舊規則「不猜」不變)。名字本身有冒號(`API: 逾時顯示重試`)就要寫平台前綴(`[test:web:API: 逾時顯示重試]`);壞名訊息補一句這個寫法。單平台照舊整串當名字。
  - 標記的邊界:`TEST_REF_RE` 用「到第一個 `]`」,`slot_parse` 數方括號層數,兩者對含方括號的值切法不同;名稱規則不收方括號之後,合法名稱兩邊切出來一樣,含方括號的兩邊都判壞名。這兩支本身不改。
- 名字比對一律整串相等(去頭尾空白後),不做大小寫或空白正規化。

### 2. 掃描收整個字串字面

- `JEST_TEST_RE`、`PLAYWRIGHT_TEST_RE`、`DART_TEST_RE` 改成收第一個引數的完整字串字面:單引號、雙引號、不含 `${` 的反引號樣板三種,字面裡的跳脫(`\'`、`\"`、`\\`)還原。`.each` 與帶 `${` 的樣板照舊不收(名字跑的時候才算得出來)。
- **含半形逗號或方括號的標題不收進測試集合**(編排者 2026-10-15 定:這兩種名字不收,見〈不做〉):掃描照樣比對到,但還原出來的名稱過不了 `_test_name_ok` 就丟掉,不進 `discover_test_methods` 的結果。所以不管怎麼綁都是懸空,不會因為被逗號切成兩半而各自配到別支。條款綁定列懸空時,如果那一格 `[test:]` 的值裡有半形逗號、切出來的幾段又都不是真測試,那一行多印一句「這一格有半形逗號,被當成好幾支;含逗號或方括號的測試名綁不了,請改測試名或寫 [manual:]」。
- 修飾:Jest/Vitest 收 `.only/.skip/.concurrent/.todo/.fails`;Playwright 收 `test(`、`test.only/skip/fixme/fail(`、`test.describe(`(含 `.serial/.parallel/.only/.skip`);`test.step(` 不是測試,不收。
- 一個正規式裡三種引號是三個分支,擷取群組不只一個:新增 `_test_name_of_match(m)`(回第一個有值的群組並還原跳脫),`discover_test_methods`、`_residual_test_files`、派工鏡頭備援段的受影響測試都改用它;使用者自訂的 `method_regex` 也走它,只有一個群組的舊寫法結果不變。
- 正規式不准有巢狀量詞(字面主體是 `(?:[^'\\\n]|\\.)*` 這種單層),長檔照舊線性時間。
- Maestro(`name:` 欄位)不在這次範圍,見〈不做〉。

### 3. 懸空要明顯標出

- `_clause_check`(規格閘與處置閘第五步共用)目前懸空時仍印 `條款綁定: ✓ — N 條全標(…懸空 k 只提醒不擋…)`。改成:有懸空就印 `條款綁定: ⚠ — N 條都有標,其中 k 條懸空(綁的測試找不到)`,下面逐條一行列出編號、名稱與懸空種類(寫錯=程式碼裡完全找不到這個名字;設定認不到=檔裡有這個名字的宣告、掃描設定不收;只被提到=名字在程式碼文字裡出現過,但不是掃描認得的測試宣告,例如寫在註解或一般字串裡;壞名=平台前綴未定義或名稱不合法),最多 15 行、其餘講總數;沒懸空才印 `✓`。
- 擋不擋不變:風險高照舊只提醒、rc 不變;風險低本來就要求測試存在(`_clause_check_twoway`),照舊擋。要不要讓懸空在風險高也擋,記成待決問題 Q1,不在這次改。
- `_spec_gate_runnable` 在條款全都懸空時目前印「沒有綁 [test:] 的條款,沒東西可跑」,會讓人以為根本沒綁;改成「k 條綁了測試但全懸空,沒東西可跑」。

### 4. 跑測試時名字怎麼交給測試工具

- profile 加一個鍵 `name_filter`:`regex`(node-jest、node-vitest、playwright)、`plain`(dart)、`ident`(其餘;名字本來就是識別字,行為不變)。多平台每個平台跟著它的 profile 走。
- `_run_cmd_expand(run_cmd, method, name_filter="ident")`:`regex` 時先跳脫 `.*+?^${}()|[]\`,再照舊 `shlex.quote`;`plain` 與 `ident` 只做 `shlex.quote`。呼叫端都已經拿得到平台設定,各自傳那個平台的 `name_filter`:
  - `_run_bound_tests`(規格閘跑紅綠、相依回歸、推送前合約測試閘、修正關卡第 4 項共用這支);
  - `guard kill` 跑配方那段;
  - 過濾探針 `_FILTER_PROBE_NAME` 是識別字,跳不跳脫一樣,照傳。
- 篩選是子字串比對:短句名可能同時選中別支。這不用新規則,既有的「篩到幾支」判法(`_ran_count` 與 `_spec_gate_declared`)會把選到兩支以上判成弱證據,`_spec_gate_declared` 本來就用子字串數宣告數,句子名照算。

### 5. 多平台的 method_regex 逃生口

- 把 `load_test_profile` 裡套用 `exts`、`scaffold_ext`、`method_regex` 覆蓋的那段抽成 `_apply_test_overrides(prof, ov, where)`,單平台照舊傳 `cfg["test"]`;`load_platforms` 的多平台分支對每個平台傳那個平台的設定物件(跟 `run_cmd` 同一層),警告訊息帶平台名。`init` 骨架的多平台格式不用改,沒寫就沿用內建。

### 6. 其他讀 [test:] 的路徑,逐條交代

| 路徑 | 怎麼處理 |
|---|---|
| 條款綁定 `clause_bindings`(spec-trace、接手視圖、處置閘第五步、doctor S5 都用它) | 走 `resolve_test_refs` 與掃描結果;做法 1、2 改完就收得到,不另改 |
| doctor Check T、`guard list`、`classify_invariants`(`_classify_one`) | 同上,不另改 |
| 推送前合約測試閘與修正關卡第 3 項(`_classify_test_refs`) | `_KILL_METHOD_OK_RE` 換成 `_test_name_ok` |
| note-shape 的測試綁定要存在、doctor S20(`_test_names_of`、`_NsTrJudge._plat`) | 切法對齊做法 1;壞名判法換成 `_test_name_ok` |
| note-shape 一行一支提醒(`_ns_wd_binding_hit`) | 用同一支 `_test_names_of`,跟著對齊;「整個被引號包住的名稱算舉例」照舊 |
| `guard bind`(`_cmd_guard_bind_locked`) | `IDENT_RE` 換成 `_test_name_ok`,名稱照原樣寫進 `[test:平台:名]` |
| `guard settle --test`(守衛紀錄轉正,`cmd_guard_settle` 直接用 `IDENT_RE` 判、`_guard_settle_locked` 直接寫 `[test:{名}]`,不走 `resolve_test_refs`) | `IDENT_RE` 換成 `_test_name_ok`,寫法不變 |
| `guard scaffold` | 保留 `IDENT_RE`(它拿名字產程式碼和檔名);擋下訊息改講「句子名先自己寫好測試,再用 guard bind 綁」 |
| `guard kill`、`kill-add`、doctor P2 的配方檢查(`_kill_method_name` 之後三處 `_KILL_METHOD_OK_RE`) | 換成 `_test_name_ok`;跑的時候照做法 4 跳脫 |
| 歸檔時「還護著存活合約的驗證紀錄不歸檔」(`cmd_archive`) | 現在用 ASCII 模式的 `\b` 包名稱,中文開頭或結尾的名稱永遠配不到,驗證紀錄會被當成沒人護而歸檔;改成名稱頭尾是英數底線才加「前後不是英數底線」的邊界,否則不加 |
| 待決問題「已驗」的測試名(`_pq_clause_tests`)、漂移 C5(`_drift_c5_test`) | 都走 `resolve_test_refs`,不另改 |
| `guard trace`(`cmd_guard_trace`:`strip_test_refs` 取名後,用 ASCII 模式的 `\b…\b` 在驗證紀錄全文找) | 跟歸檔同一個病:中文開頭或結尾的名稱永遠配不到。兩處改用同一支邊界規則(名稱頭尾是英數底線才加「前後不是英數底線」,否則不加),不各寫一份 |
| 代碼審處置帳 `test:<名>` 證據(`_dispositions_split_test`) | 冒號前綴的切法跟 `resolve_test_refs` 相同,但不切逗號(一筆證據就是一支名稱);加 `_test_name_ok` 檢查,含半形逗號或方括號的判不合法,不改成切逗號 |
| 每支檔有家「只換測試綁定不算寫說明」(`_nodehome_test_tag_value_ok`) | 不改,見〈不做〉 |
| 派工鏡頭備援段的受影響測試 | 改用 `_test_name_of_match` 取名;列出時照舊只列識別字名,句子名只算進「沒列出」的數字,見〈不做〉 |

### 7. 文件與舊筆記

- `TEST_PROFILES` 的 `attr_hint`:node-jest(node-vitest 共用)寫「識別字名才可綁,含空白 NO MATCH」、dart 寫「識別字名才可綁,同 playwright」,這兩處改成新規則;playwright 那條本來沒寫限制,補一句「標題整串比對,不收半形逗號與方括號」。
- [[Systems/test-profile-multiplatform]] 摘要裡 playwright 與 dart 的 NO MATCH 那兩行,實作時改寫並指到這篇;[[Projects/多平台合約測試綁定_計劃]] D4 那段開頭加一行「本段的識別字限制已被 Projects/測試名收自由字串_計劃 取代(2026-10-15)」。
- 規格閘與推送前合約測試閘的現況落在 [[Systems/規格閘]]、[[Systems/bound-tests-gate]],note-shape 那組落在 [[Systems/筆記內容閘]],guard 那組落在 [[Systems/lumos-guard]] 與 [[Systems/guard-kill]]。

## 驗收條款

- [S1] 當 Vitest/Jest 測試檔有 `it('下單後 按鈕會停用')`、`test("shows error (500)")`、`describe('訂單 表單')` 時,`discover_test_methods` 應收到這三個完整字串;同一支檔裡的 `it.each` 與帶 `${` 的樣板字串不應收。[test: t_js_free_string_test_names_discovered]
- [S2] 當 Playwright 測試檔有 `test('登入後 看得到訂單')`、`test.describe("結帳 流程")` 時,掃描應收到這兩個完整字串;同一支檔裡的 `test.step('…')` 不應收。[test: t_playwright_free_string_names_discovered]
- [S3] 當 Dart 測試檔有 `testWidgets('下單 鈕 停用')` 時,掃描應收到完整字串。[test: t_dart_free_string_names_discovered]
- [S4] 當條款綁的名稱是 `下單後 按鈕會停用`、測試檔有同名的 `it` 時,條款綁定應判綁了。[test: t_clause_binds_free_string_exact]
- [S5] 當條款綁的名稱只是測試標題的前半 `下單後` 時,條款綁定應判懸空。[test: t_clause_free_string_prefix_hangs]
- [S6] 當多平台設定寫 `[test:web:API: 逾時 顯示重試]` 時,應解成平台 web、名稱 `API: 逾時 顯示重試`。[test: t_free_string_ref_platform_prefix]
- [S7] 當多平台設定寫 `[test:API: 逾時]` 而 API 不是平台時,應判壞名,訊息應講名稱有冒號要寫平台前綴。[test: t_free_string_ref_colon_needs_prefix]
- [S8] 當標記值是 `甲 乙,丙` 時,`resolve_test_refs` 與 `_test_names_of` 都應切成 `甲 乙`、`丙` 兩支。[test: t_test_ref_split_half_width_comma]
- [S9] 當標記值是 `甲，乙`(全形逗號)時,`resolve_test_refs` 與 `_test_names_of` 都應當成一支名稱。[test: t_test_ref_full_width_comma_is_name]
- [S10] 當名稱含方括號、控制字元或以減號開頭時,推送前合約測試閘應判壞名。[test: t_test_name_ok_rejects_unsafe]
- [S11] 當計劃有懸空條款時,規格閘條款綁定那一行不應出現 ✓,應印 ⚠ 並逐條列出懸空的編號與名稱,回傳碼應跟改前一樣。[test: t_spec_gate_marks_hanging_clauses]
- [S12] 當計劃的條款全都懸空時,規格閘跑測試那一行應講「綁了測試但全懸空」。[test: t_spec_gate_run_line_all_hanging]
- [S13] 當 node-jest 平台展開名稱 `shows error (500) + retry?` 時,指令應是 `npx jest -t 'shows error \(500\) \+ retry\?'`。[test: t_run_cmd_escapes_regex_name_filter]
- [S14] 當 dart 平台展開同一個名稱時,指令應只加 shell 引號、不跳脫正規式字元。[test: t_run_cmd_plain_name_filter]
- [S15] 當名稱含單引號、`$`、反引號、分號時,展開後的指令交給 shell 應剛好切出一個名稱引數。[test: t_run_cmd_free_string_shell_safe]
- [S16] 當多平台設定某個平台寫了 `method_regex` 時,那個平台的掃描應用它。[test: t_multiplatform_method_regex_override]
- [S17] 當多平台設定某個平台的 `method_regex` 寫成巢狀量詞時,應印帶平台名的警告並沿用內建。[test: t_multiplatform_method_regex_rejected]
- [S18] 當 `guard bind` 給含空白的中文名稱而那支測試存在時,應寫出 `[test:web:下單後 按鈕會停用]`。[test: t_guard_bind_free_string_name]
- [S19] 當 `guard scaffold` 給含空白的中文名稱時,應擋下並指去 `guard bind`。[test: t_guard_scaffold_rejects_free_string_name]
- [S20] 當殺傷力配方綁的是句子名時,`guard kill` 應照平台跳脫後去跑,不應再判「test 名不合法」。[test: t_guard_kill_free_string_name]
- [S21] 當驗證紀錄提到存活合約綁的中文句子名時,歸檔應把它列為仍受護、不歸檔。[test: t_archive_protects_free_string_guard_name]
- [S22] 當筆記綁的句子名指得到真測試時,doctor S20 應不列它。[test: t_note_test_refs_free_string_found]
- [S23] 當筆記綁的句子名找不到測試時,doctor S20 應列出它。[test: t_note_test_refs_free_string_missing]
- [S24] 當綁定是既有的識別字名(C#、Kotlin、Python)時,判定結果與展開的測試指令應跟改前一樣。[test: t_identifier_test_bindings_unchanged]
- [S25] 當讀 profile 的提示文字與 Systems/test-profile-multiplatform 時,應看不到「識別字名才可綁、含空白 NO MATCH」的舊說法。[manual: grep 這兩處沒有 NO MATCH 舊句,且 Systems 節點指到本篇]
- [S26] 當測試檔有 `it('when offline, shows banner')` 或 `it('顯示 [草稿] 標籤')` 時,掃描不應把它收進測試集合。[test: t_free_string_names_with_comma_or_bracket_not_collected]
- [S27] 當條款綁 `when offline, shows banner` 這一格而切出來的兩段都不是真測試時,條款綁定應判懸空,並印出含逗號的測試名綁不了的提示。[test: t_clause_comma_split_hint]
- [S28] 當驗證紀錄提到存活合約綁的中文句子名時,`guard trace` 應列出那篇驗證紀錄。[test: t_guard_trace_free_string_name]

## 實務隱患

- 已排除:金流:不碰付款、點數或任何金額。
- 已排除:對外送出:不寄信、不呼叫外部服務,跑的測試指令照舊只在本機。
- 已排除:不可逆:只改判定與印出,還原提交即可回到舊行為;寫進筆記的句子名在舊版只會回到懸空,不會壞檔。
- 守衛面:會碰。綁定合法性、推送前合約測試閘、規格閘、guard kill 的「拒注入」白名單都在這次範圍:
  - 放寬白名單之後,指令安全靠 `shlex.quote`(本來就有)加「不以減號開頭」;測試要造含單引號、`$`、反引號、分號的名稱,確認展開後 shell 切出來剛好一個引數。
  - 假綠:跳脫寫錯會選中零支——既有的「跑過的證據」判法把零支判成沒證明、不是綠;選中多支——判弱證據。測試要各造一次。
  - 掃描放寬可能把字串裡剛好長得像 `it('…')` 的東西收成測試:c-style 註解照舊先剝;字串裡的假呼叫不另處理(Java 那條同類問題用剝字串解,JS 不能剝字串,否則名字就沒了)。
- REVISIT:2026-12-15 查消費專案有沒有「字串裡的假 it(…) 被當成真測試、讓綁定判成綁好」的案例,有就改成只認行首或分號後的呼叫。
- 效能:新的字面正規式單層無巢狀量詞;實作後拿 1MB、全是未閉合引號的測試檔量一次掃描時間,跟改前比。
- 相容:舊筆記一字不改照讀;全形逗號、全形冒號不再切的那條,2026-10-15 全庫 0 處受影響。

## 不做

- 名字含半形逗號或方括號的測試不收:那要新語法(引號包名),先前同類的新語法被否決過(要改解析、索引、doctor 好幾處,舊筆記也讀不懂)。這種測試改名,或條款寫 `[manual:]`。
- REVISIT:2026-12-15 數消費專案的筆記與測試檔:有沒有因為名稱含逗號或方括號而綁不上的,有 3 筆以上就另開計劃談引號包名。
- Maestro 的 `name:` 多字名不收:Maestro 跑測試是指定檔案、不靠名稱篩選,而 `\s*$` 行尾錨是為了擋部分擷取的假證據才加的,這次沒有它的真專案可驗。
- `guard scaffold` 不收句子名(它拿名字產程式碼和檔名)。
- 「只換測試綁定不算寫說明」的豁免不放寬到中文名:句子名剛好等於一句說明,就能把說明藏進綁定繞過寫回落點([[Projects/只換測試綁定不算寫說明_計劃]] 的撤除條件講的就是這個);不放寬的代價只是換一個中文名會被當成寫了說明,方向安全。
- 派工鏡頭備援段只列識別字名(餵給審查席的文字,句子名不轉印),句子名只算數字。
- Kotlin 反引號名經 Gradle `--tests` 跑的跳脫不在這次範圍(那是 Gradle 的萬用字元,不是正規式)。
- 懸空在風險高時要不要擋,這次不改(待決問題 Q1)。

## 回退

- 一個功能一個提交,還原那個提交即可。還原後:句子名的綁定回到懸空(規格閘印回舊的 ✓ 行),`_test_names_of` 回到也切全形逗號,沒有資料要搬或清。
- 實作中途發現某一條路徑(例如 guard kill)放寬有問題,可以只讓那一處改回 `_KILL_METHOD_OK_RE`,其他路徑不受影響,但要在〈審計修正紀錄〉記一筆。

## 合約候選

(空)

## 審計修正紀錄

(空)
