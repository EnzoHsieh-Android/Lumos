preflight-4: ran

首輪前掃四類:①未定義的詞 1 條、②壞引用 0 條、③範圍自相矛盾 2 條、④機械宣稱驗語意 4 條(不成立 2、部分成立 2)。①③ 直接修了真檔;④ 每條都開檔讀碼核對過(`cmd_guard_trace`、`cmd_guard_settle` 與 `_guard_settle_locked`、`TEST_PROFILES` 的 attr_hint、`_dispositions_split_test`),前掃的說法都成立,一樣直接修了真檔,修改前→修改後列在下表。被審的計劃:`docs/lumos-toolchain-knowledge/Projects/測試名收自由字串_計劃.md`。

另外照編排者的裁定(名字含半形逗號或方括號的測試不收,回頭條件照留),做法 2 補寫掃描時怎麼處理這兩種名字,並新增條款 S26、S27;guard trace 那條另補 S28。

**升級為正式 finding**:無。這次修補都沒有改到決策 d1 的裁定(收句子名、懸空要標出、推翻識別字限制)。「含逗號或方括號不收」本來就是計劃〈不做〉裡的取捨,編排者已確認,只是把掃描端的行為補寫出來。

| # | 類 | 位置 | 修改前 | 修改後 |
|---|---|---|---|---|
| 1 | ① 未定義的詞 | 做法 3 懸空種類 | 「懸空種類(寫錯/設定認不到/只被提到/壞名)」,四種都沒解釋 | 四種各附一句定義;「只被提到」=名字在程式碼文字裡出現過,但不是掃描認得的測試宣告(例如寫在註解或一般字串裡),對應 `clause_bindings` 的 mentioned 狀態 |
| 2 | ③ 自相矛盾 | 做法 6 表格 | 一列寫「`guard settle --test` 的 `IDENT_RE` 換成 `_test_name_ok`」,另一列又寫「守衛紀錄轉正…都走 `resolve_test_refs`,不另改」 | `guard settle` 拆成獨立一列,寫明 `cmd_guard_settle` 直接用 `IDENT_RE` 判、`_guard_settle_locked` 直接寫 `[test:{名}]`,不走 `resolve_test_refs`;改法是 `IDENT_RE` 換成 `_test_name_ok`。「不另改」那列拿掉守衛紀錄轉正 |
| 3 | ③ 自相矛盾 | 做法 2 對〈不做〉 | 做法 2 說掃描收「完整字串字面」,沒排除任何字元;〈不做〉卻說含半形逗號或方括號的不收 | 做法 2 補一條:這兩種標題掃描照樣比對到,但還原後的名稱過不了 `_test_name_ok` 就丟掉、不進測試集合,所以怎麼綁都是懸空;條款綁定那一格的值有半形逗號、切出來的段又都不是真測試時,多印一句「含逗號或方括號的測試名綁不了」的提示。新增條款 S26(掃描不收)、S27(切段懸空與提示) |
| 4 | ④ 不成立 | 做法 6 表格 guard trace | 「guard trace 走 `resolve_test_refs`,不另改」 | 讀碼:`cmd_guard_trace` 用 `strip_test_refs` 取名,再用 ASCII 模式的 `\b…\b` 在驗證紀錄全文裡找,中文名稱的詞界失效,跟 `cmd_archive` 同一個病。改成獨立一列:兩處共用同一支邊界規則(名稱頭尾是英數底線才加邊界)。新增條款 S28 |
| 5 | ④ 不成立 | 做法 6 表格 守衛紀錄轉正 | 同 #2(說守衛紀錄轉正走 `resolve_test_refs`) | 同 #2 |
| 6 | ④ 部分成立 | 做法 7 attr_hint | 「`TEST_PROFILES` 各家的 `attr_hint`(現在寫『識別字名才可綁,含空白 NO MATCH』)」 | 讀碼:只有 node-jest(node-vitest 共用)是這句,dart 寫「識別字名才可綁,同 playwright」,playwright 沒寫限制。改成逐家講:前兩處改成新規則,playwright 補一句「標題整串比對,不收半形逗號與方括號」 |
| 7 | ④ 部分成立 | 做法 6 表格 處置帳 | 「`_dispositions_split_test` 切法已同規則」 | 讀碼:它只切冒號前綴,不切逗號。改成:冒號前綴跟 `resolve_test_refs` 相同、不切逗號(一筆證據一支名稱),再加 `_test_name_ok`,含半形逗號或方括號的判不合法;不改成切逗號 |

## 六席收貨與處置

六席報告(`r1-{正確性,邊界,整合,資源併發,回滾,架構對齊}-sonnet.md`)共 **38 條**:major 17、minor 21,blocking 17(都是 major)。編號照各報告 finding 順序:正1–正7、邊1–邊9、整1–整7、資1–資4、回1–回4、架1–架7。

四類條數(同 preflight 的分法):①未定義的詞 0;②壞引用 0(席位引的程式位置逐一開檔核對,都對得上);③範圍自相矛盾 3(整1 落點、回2 部分收回、整6 豁免敘述);④機械宣稱驗語意 35(其餘全部)。

每條的「觀察」都開程式或實跑核對過,全部成立,**全部折入,無駁回**。實跑核對的幾條:
- `_strip_test_comments(src, "c-style")` 對正1/資1 的五行輸入,輸出 `"it('開啟 http:\nit('GET /api\nit('結帳', ()=>{})\n"`(三支只剩一支)。
- `_kill_method_name("API: 逾時 顯示重試", True)` 回 ` 逾時 顯示重試`(正3/邊3)。
- `_test_names_of(slot_parse("x [test:API: 逾時]"))` 回 `['API:逾時']`(邊4)。
- `_dispositions_split_test("test:API: 逾時", {}, "py")` 回「這個專案沒開多平台…」(正4)。
- `KOTLIN_TEST_RE` 對 `` @Test fun `when offline, shows banner`() `` 收到含逗號的名稱(邊5)。
- `\btest\(\s*'([^']*)'` 對 `expect(/^\d+$/.test('hello world'))` 收到 `hello world`(邊2)。
- `_RAN_EVIDENCE` 只有 swift-xctest、csharp-xunit、node-jest、python 四筆,只有 python 帶 `count_re`;`_ran_count` 與 `_spec_gate_declared` 只在規格閘那支呼叫(正2/資2)。
- 沒能本機驗的:Jest/Playwright 篩選不分大小寫、Playwright 把 `/…/` 當正規式字面(邊6、正6)。照保守方向折(撞名不分大小寫數、斜線也跳脫),多數只會更嚴。

| 根因組 | 條目 | 折法 |
|---|---|---|
| 剝註解不認字串,截斷句子名、吞掉後面的測試、二次方時間 | 正1、邊1、資1、架4、資3 | 做法 2 改成統一規則:JS 三家與 Dart 用一趟字串感知的剝法(字串照留、只刪註解,沒結尾的 `/*` 刪到檔尾,線性);效能量測改成「大量沒結尾 `/*`」與 repo 全掃;Playwright 補檔名錨。條款 S29、S30、S47 |
| 「選到多支判弱證據」對 JS 三家與 Dart 不存在;大小寫;零支的理由寫錯 | 正2、資2、邊6、正6 | 做法 4 改成跟輸出無關的事前撞名檢查 `_name_filter_collisions`(宣告名稱含綁定名的有幾個,regex 平台不分大小寫),規格閘判弱證據、推送前閘判證不出;零支的實際防線照實寫,實作時實跑補 `_RAN_EVIDENCE`;斜線加進跳脫字元集。條款 S36–S39 |
| 冒號前綴切法四處各寫一份 | 正3、邊3、正4、邊4 | 做法 1 新增 `_split_test_ref`,`resolve_test_refs`、`_test_names_of`、`_kill_method_name`、`_dispositions_split_test` 都改呼叫它;單平台整串當名稱、多平台只認已定義平台的前綴;全形冒號前綴容錯保留(限已定義平台)。條款 S40–S43 |
| 掃描誤收別的呼叫、只拿得到一部分的字面、沒還原的跳脫 | 正5、邊2、邊7 | 做法 2:字面後要接逗號或右括號、呼叫前不能是點號或識別字、只認三種跳脫(其他跳脫與 Dart 插值不收)。條款 S31–S33 |
| 反引號拆殼深度不一致;丟掉逗號名的過濾誤傷 Kotlin | 正7、邊5 | 做法 1 拆殼只有「整串被一對反引號包住」一條規則;做法 2 的 `_test_name_ok` 過濾只套字串標題型 profile。條款 S34、S35 |
| 落點寫錯(lumos-guard 是外掛的家) | 整1、架6、架7 | lands_in 拿掉 Systems/lumos-guard、加 Systems/lumos-cli-write;做法 7 逐項寫明現況說明落哪一篇(guard bind/scaffold/trace 落 test-profile-multiplatform,settle/kill 落 guard-kill,歸檔落 lumos-cli-write) |
| 手冊、註解、舊筆記的舊說法沒列全 | 整3 | 做法 7 列完整清單(attr_hint、程式註解、reference.md 三處、06 手冊、Systems 三行含 maestro 拆半、舊計劃 D4 與 Maestro 段、調研 W1 列);S25 改成照清單逐處 grep |
| 印給人貼的指令沒引號、「guard bind 綁不了」說法會變錯 | 整2 | 做法 6 新增 `_kill_binding_msg` 一列並改 settle 那列:兩處 `IDENT_RE` 換規則、貼上用的名稱一律經 `_kill_cmd_arg`;手冊 06 那句跟著改。條款 S44 |
| 既有測試會紅或意思反過來,沒列 | 邊8、整4、回4 | 新增做法 8 逐支列出(node/dart/playwright 掃描測試、note-shape 寬鬆語法、處置閘懸空斷言)並註明改測試檔要先 anchor approve;⚠ 行保留「懸空 k 只提醒不擋」字樣,S11 加處置閘 |
| 回退後的殘局沒交代;部分收回寫端讀端不一致 | 回1、回2 | 〈回退〉重寫:列三條還原後會擋推送的路、怎麼找出來、怎麼處置;部分收回與 RETIRE-IF 都要寫端讀端一起收;「已排除:不可逆」理由改成誠實版本 |
| 相容宣稱只掃了本 repo | 整7、回3 | 〈實務隱患〉相容改寫:範圍限本 repo,講明消費專案全形逗號寫法會怎樣、怎麼改 |
| 點號後綴比對與「整串相等」衝突 | 整5 | 做法 1:`類別.方法` 拿最後一段比,只在點號兩邊都是識別字時才用。條款 S46 |
| 「只換測試綁定」豁免敘述不精確 | 整6 | 〈不做〉改寫:英文句子名也不豁免;做法 6 那列補間接呼叫 `_test_names_of` 但不受影響的理由 |
| 懸空變可綁之後每支都起一次測試工具 | 資4 | 〈實務隱患〉加耗時一條;做法 7 的提示文字補 `bound_tests.parallel` |
| 新邊界規則跟既有 `\b` 並存 | 架1 | 做法 6 末段寫明 `_test_name_boundary_re` 只管歸檔與 guard trace 的測試名,其他 `\b` 不動 |
| 新訊息沒照三段式 | 架2 | 做法 3 加一條:新增或改寫的訊息照三段式 |
| ⚠ 跟回傳 ok 對不上 | 架3 | 做法 3 寫明刻意如此、呼叫端看回傳狀態不比對字樣(grep 主程式沒有比對 `條款綁定: ✓` 的地方) |
| 控制字元判法另寫一份 | 架5 | 做法 1:`_test_name_ok` 用既有的 `_path_special_chars`(`_PATH_SPECIAL_CATS`) |
| 條款精度(固定輸入、長度邊界、效能門檻、壓縮檔) | 邊9 | S24 補固定輸入;新增 S45(200/201/全空白);S30 定門檻 1 秒;字面主體限 200 字,壓縮檔也線性 |

駁回重現表:無(沒有駁回的條目)。

升級為正式 finding:無。折入都沒有改決策 d1 的裁定;全形冒號前綴容錯的保留,是讓 d1「整串比對」跟既有 note-shape 寬鬆語法相容的做法,沒有改 d1 的內容。
