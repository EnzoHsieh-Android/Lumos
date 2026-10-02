severity: major

# 架構對齊審查(設計審第 2 輪,架構對齊-sonnet 席)

對照碼 repo 根:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/negguard`(以下路徑相對於它)。慣例 skill:python-idioms(本案是單檔 CLI 內的規則組,慣例以鄰居程式為準)。

## 1. 分層與依賴方向
- 第①道借 `_classify_test_refs` 是對的:它原本就是兩個閘共用(推送前合約測試閘與修正關卡第 3 項,見 `scripts/lumos:40248` 說明與 `scripts/lumos:12366` 的呼叫),本案是第三個消費者,依賴方向沒有新增,單檔內以名稱呼叫也沒有載入順序問題。
- 第②道從 `_dispositions_check_test`(`scripts/lumos:41244`)抽 `_test_in_tree`,放在 `_git_tree_has`/`_git_tree_text`(`scripts/lumos:41218`、`41224`)旁邊的「在被推的版本找東西」一族,命名與落點一致;抽出後表態閘改呼叫它是由下往上的共用,沒有跨層直呼。唯一的方向疑點在 F4(逾時與跨 repo 兩種狀況回傳語意)。
- 新組在 `cmd_note_shape` 於 `_note_shape_eval` 之後串接、`_note_shape_report` 多收一組,跟格子規則的接法同形(`scripts/lumos:28629-28636`)。
- 本案新引入的依賴:note-shape(讀被檢查版本、不看工作目錄,`scripts/lumos:28555` 說明明寫)第①道要讀工作目錄索引。鄰居表態閘有同樣的兩道先例,且設計有〈做法〉5 保險,見 F2(minor)。

## 2. 命名與錯誤處理
- `_note_shape_test_refs_parse` 對應 `_note_shape_slots_parse`(`scripts/lumos:28113`)與 `_note_shape_negation_parse`;`_ns_slots_mode` 式的總開關與子開關合併、壞值照 warn 並印一句、整組丟例外只印一行不影響其他規則(同 `_ns_slots_prepare` 的 `scripts/lumos:28007-28027` 寫法),都對齊。
- 帳本 `extra` 多鍵併進同一字典、`check` 不動,對齊 `_ns_slot_extra(…, mixed=…)` 的併法(`scripts/lumos:28685-28720`)。
- doctor S20 接在 S19 後面、`warn_soft`、不寫帳、`--ci` 與否另述,對齊 S17–S19(`scripts/lumos:2513-2547`);S16–S19 共用 `_note_summary_entries` 讀摘要,本案若 doctor 另寫抽取會變第二路,設計寫了「同一支吃全文的函式」,字面方向對。
- 不一致處:名稱串切分(F3)、`_test_in_tree` 沿用 dispositions 命名的逾時環境變數(F4),皆 minor。

## 3. 第二種做法
- 唯一的 major:`rows_out` 是第二個「從 `_note_shape_eval` 取回新寫行與全文」的容器,既有的 `slots` 容器本來就只是取貨用的袋子,設計對它的前提(會連帶打開格子規則)與程式不符(F1)。
- 預設 `warn`、靠設定分開上線與開擋:設計說鄰居是筆記格子,實際筆記格子是靠掛鉤記號 `_SLOTS_GOLIVE_MARK`(`scripts/lumos:27993`)上線、預設 block。但 repo 內有另一個真先例:`note_lint.gate` 沒設=warn(見 `Systems/lumos-cli-read` 的 RULE 行),所以「程式預設 warn、專案設定開擋」不是第二種做法,只是設計引用的鄰居說錯,不列 finding。
- 名稱抽取走 `slot_parse` 而非 `TEST_REF_RE`:設計 r2 已明講為了不要第二套寫寬鬆正則,方向可接受,細節差異列 F3。

## 4. 落點
- `lands_in` 列的四篇(筆記內容閘、lumos-cli-read、bound-tests-gate、棧別提問表態閘)與每支新函式的家對得上:規則組與開關在筆記內容閘、doctor S20 在 lumos-cli-read(S16–S19 的說明就在那篇)、`_test_in_tree` 在表態閘、第①道只是借用、記在 bound-tests-gate。無 finding。

## F1 `rows_out` 是第二個取回新寫行的容器,而既有 `slots` 容器本來就不會連帶開格子
severity: major
blocking: 是
引句:「`_note_shape_eval` 加一個新參數 `rows_out`(呼叫端給容器、它把向 `_notelines_new` 要到的 rows 放進去;不動既有的 `slots` 參數,所以不會連帶打開格子規則)」
file: `scripts/lumos:28408-28414`
file: `scripts/lumos:28307-28313`
file: `scripts/lumos:28089-28105`
file: `scripts/lumos:28007-28027`
1. 設計的前提是「傳 `slots` 會連帶打開格子規則」。讀碼:`_note_shape_eval` 對 `slots` 只做兩件事,把 `slots.get("mark2")` 轉給 `_notelines_new`(沒 mark2 就是 None,什麼都不多收),再把 `notes, old_by` 放回 `slots["notes"]`、`slots["old_by"]`。格子規則本身是之後由 `_ns_slots_violations(…, slots)` 另外判的(`scripts/lumos:28307-28313`),不是 eval 裡跑的。所以傳一個空的 `{}` 不會開任何格子規則。
2. 既有先例正是這樣用:`_ns_skip_slot_extra` 傳 `slots = {}` 給 `_note_shape_eval`,只為了拿 notes(`scripts/lumos:28089-28105`);「要不要跑格子」由 `_ns_slots_prepare` 決定是否準備 `mark2`(`scripts/lumos:28007-28027`),不是由有沒有傳容器。
3. `slots["notes"]` 的每筆已經是 `(路徑, 全文, 新寫行 rows)`(`scripts/lumos:27364` 一帶 `_notelines_new` 的回傳)。所以設計〈做法〉2 另說「讀內容:碰到的筆記…全文,用 note-shape 讀終點的同一個讀檔零件」也是重讀一次已拿到的東西。
4. 結果:照設計實作會在 `_note_shape_eval` 簽名上新增第四個容器參數(已有 `hints`、`tags`、`slots`),並在碰到的筆記上第二次讀全文;同一份資料有兩條取法,與提交時單次跳過算 `test_refs` 的路徑(設計〈做法〉8 說「先用 `rows_out` 算一次」)也跟 `_ns_skip_slot_extra` 的現成寫法分叉。
5. 對齊做法:新組吃 `slots` 同款容器(或把容器改名成中性的取貨袋、供兩組共用),直接用 `["notes"]` 裡的全文與 rows;不需要新參數,S25 條款(傳 `rows_out` 沒傳 `slots` 時格子不跑)改成直接驗「傳空 `slots` 不開格子」或整條拿掉。
6. 未實測,依據是讀碼。⚠ 若設計想要的是「`slots` 容器改名」那種語意清理,這是編排者的取捨;但現在的理由(會連帶開格子)與程式不符。

## F2 note-shape 第一次讀工作目錄索引,偏離該閘「內容與設定都從被檢查版本讀」的既定原則
severity: minor
blocking: 否
引句:「第①道過、第②道找得到 → 指得到;第①道沒過、或第②道找不到 → 指不到」
file: `scripts/lumos:28555-28557`
file: `scripts/lumos:41244-41250`
1. `cmd_note_shape` 說明寫「設定與內容都從被檢查的版本讀…工作目錄沒暫存的東西不算」;設計第①道用工作目錄索引,是 note-shape 內第一個依賴工作目錄的規則。
2. 鄰居表態閘 `_dispositions_check_test` 有同樣的兩道結構(工作樹 discovery 加被推版本 `git grep`),設計也有〈做法〉5 的保險;所以結構上有先例、不是第二種做法。
3. 缺的是:note-shape 的說明與 [[Systems/筆記內容閘]] 要補一句「這組規則是例外、為什麼」,否則 `cmd_note_shape` 的說明跟實作互相矛盾。〈做法〉11 的同步清單沒列 `cmd_note_shape` 說明與 `_note_shape_eval` 說明字串。

## F3 名稱串的切分是第三支切分器,且要靠重新包成 `[test:名]` 才餵得進 `_classify_test_refs`
severity: minor
blocking: 否
引句:「再用半形或全形逗號切開、去前後空白、去掉空項」
file: `scripts/lumos:5160-5166`
file: `scripts/lumos:5169-5192`
file: `scripts/lumos:12366`
1. 既有全庫驗存在的路徑都走 `invariant_test_refs`(只認半形逗號、用 `TEST_REF_RE`)再接 `resolve_test_refs` 切平台前綴;設計選 `slot_parse`(格子的同一判法,與格子規則對齊,可接受)再自己切全形逗號與前綴空白,等於在 `slot_parse` 與 `invariant_test_refs` 之外多一支切分。
2. `_classify_test_refs` 的入參是含 `[test:…]` 的文字(`scripts/lumos:40248`);設計沒寫怎麼餵。鄰居修正關卡的做法是逐名重包 `f"[test:{t}]"`(`scripts/lumos:12366`);若照字面實作而重包前沒先濾掉全形逗號或內含 `]` 的名稱,會被 `TEST_REF_RE` 吃成別的東西。
3. 對齊做法:設計寫明「逐名重包 `[test:名]` 後呼叫 `_classify_test_refs`,同修正關卡」,並把切分器抽成一支給 note-shape 規則與 doctor S20 共用(doctor 那段已要求共用抽取,但切分沒說)。

## F4 `_test_in_tree` 抽出後逾時、跨 repo 兩種狀況的呼叫端對應沒寫,逾時環境變數沿用 dispositions 命名
severity: minor
blocking: 否
引句:(把表態閘 `_dispositions_check_test` 裡做這件事的那段抽成共用小函式 `_test_in_tree`,表態閘改用它、行為不變)
file: `scripts/lumos:41209-41216`
file: `scripts/lumos:41244-41282`
1. 原函式遇到 git 逾時是往上拋 `TimeoutExpired`(`_disp_git_timeout` 說明明寫「由每題的例外接手判無法驗證(擋,不放行)」),git rc 非 0 且非 1 是回 False 加訊息,平台根在 repo 外回 True(只做第①道)。
2. 設計的三態把這三種全收成「判不了」,note-shape 端不擋;表態閘端卻必須維持「擋」與「跨 repo 放行」,否則 S24 的「判定一樣」會破。兩端的對應表(三態轉回 `(bool, 訊息)`)與回傳型別(鄰居 `_git_tree_has` 回 bool、`_git_tree_text` 回 None 當失敗)沒寫。
3. 另外 `_disp_git_timeout()` 讀 `LUMOS_DISP_GIT_TIMEOUT`,note-shape 借用會讓一個叫 DISP 的環境變數管筆記閘的 git 逾時;設計又另設整組 20 秒上限。要明寫共用或另設。

不對齊共 4 條,其中 major 1 條
最高等級:major,blocking 共 1 條
