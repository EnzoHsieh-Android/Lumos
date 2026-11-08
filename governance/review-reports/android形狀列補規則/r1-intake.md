# r1 收貨紀錄(android形狀列補規則)

preflight-4: ran

## 前掃(派審查員之前,一個代理照固定清單掃)

- ① 未定義的詞 8 條、③ 範圍矛盾 3 條:直接修計劃(補〈用詞〉:新增告警閘、lint-waive、通電批次的值、〈統計〉、〈待查證〉、樣本內、保留集、壞例好例樣本、逐例表;〈範圍〉補 API-1 同一處更正、API-2 移出〈待查證〉、〈統計〉各數、規則包節點那行現在的條數)。
- ② 壞引用:無。
- ④ 機械宣稱驗語意(逐條改前 → 改後):

| # | 改前 | 程式實際 | 改後 |
|---|---|---|---|
| 1 | S3:型錄自檢會驗「四列現成規則欄指到存在的規則 id」 | `t_kotlin_catalog_rows_wired` 只呼叫 `catalog_problems()`,現成規則欄只拿來抽第四批候選、找「待查」、算被會擋規則守到的列數,寫錯 id 不會紅 | S3 只留「問題數 0」;id 存在另立 S5,綁新增的 `t_kotlin_shape_rows_rules`;寫法改成型錄既有的「自寫 ast-grep <id>」 |
| 2 | S2:逐例表驗「ARCH-59 報 a」 | 既有逐例表只數 (規則, 檔) 命中次數,分不出報 a 還是 b | 新測試比對報在哪幾行;預期值表加「兩個沒加 + 一個加了 → 報兩行、不報加了的」 |
| 3 | S2:用 `t_kotlin_rulepack_security_rules` 的逐例表 | 那張表把每段程式包進 `fun case(...) { … }`,Kotlin 不准在函式裡宣告 interface | 另開 `t_kotlin_shape_rows_rules`,每例是完整 kt 檔;不改既有表的包法(會牽動一百多例) |
| 4 | S1:樣本自測「驗壞例報、好例不報」 | 實際要求壞例至少 2 處、好例零命中且至少 2 段頂格宣告;已知誤報要放 `review-fp-` 檔才豁免 | 〈用詞〉寫明這些要求;API-2 加一份 `review-fp-` 樣本記 Play services Task |

- 另:〈用詞〉原寫「rules/ 的 error 等級在推送前擋」,程式實際是 rules/ 收 error 與 warning,擋不擋看消費專案宣告的 sgconfig 與新增告警閘;已改寫。
- 沒有動到核心裁定。

## 收貨

- 四席(通才、出處、規則可行、架構對齊)全部交回後,一次從逐字稿原樣存檔;四份都已是正規化格式,quote-check 全數錨定,refcheck 全部對得上。收貨時 git status 沒有席位造成的 repo 改動。
- 席位臨時目錄 /tmp/lumos-seat-work/android形狀列補規則/ 收貨後刪除。

## 編號與處置

編號照報告順序:通才 g1–g7、出處 p1–p6、規則可行 f1–f9、架構對齊 c1–c6。

依根因分組:A 形狀比出處寬或引錯出處(p1、p2、p3、p5、p6)、B ARCH-59 限定詞判斷方向(g1、f1、p4)、C UI-33 與既有 UI-32 重疊(c2、g3、f7)、D 測試設計(c5、f2、f3、c3、g6、f9、g5、f4)、E 升級路徑(g2)、F 解析器與漏報範圍(f5、f6、f8、g4)、G 文件精度(c1、c4、c6、g7)。

| id | 一句 | 重現 | 處置 |
|---|---|---|---|
| g1 | ARCH-59 清單外註解當限定詞,對照組帶 @IntoSet、@Suppress 會讓無辜函式被報(多報,不是少報) | HIT:同 f1,席位實跑三處誤報 | 折:改成只認確定的限定詞(@Named、同檔 @Qualifier 宣告),多重綁定兩邊都不算,其他註解判不準就不報 |
| g2 | API-2 的 review-fp 樣本在搬到 rules/ 後不再豁免 | HIT:check.py 的 review_ids 只含 rules-review、rules-unwired | 折:範圍 4 寫明 API-2 過了就拿掉 review-fp 樣本、誤報寫進實測狀態欄 |
| g3 | UI-33 規則不看註冊呼叫,跟型錄形狀不一致,有註冊時建議方向反 | HIT:既有 rules/compose.yml 的 kt-compose-dispose-empty-cleanup 已管有註冊那半 | 折:同 c2 |
| g4 | ARCH-62 不認泛型寫法、多元件、對應表只測了一組 | HIT:EntryPointAccessors.kt 每個方法都有 reified 多載 | 折:加泛型寫法、多元件含允許的就不報,逐例表四個 fromX 各一例 |
| g5 | 統計改壞案例寫死的 51 列沒列進範圍 | HIT:test_lumos.py 的 _KT_STATS_MUTATIONS | 折:同 f4 |
| g6 | S5 寫死目錄,搬到 rules/ 會紅 | HIT:讀條款 | 折:目錄以逐例表登記為準,搬動時同提交改登記 |
| g7 | 「命中應能到 20」的依據是關鍵字檔數不是壞寫法命中 | HIT:讀實驗節 | 折:改寫成檔數不等於命中、不到 20 就留只登記 |
| p1 | API-2 的 forEach 樣式出處沒講到 | HIT:awaitAll KDoc 與 IntelliJ 檢查頁都只講 map | 折:拿掉 forEach,逐例表加一例 forEach 不報 |
| p2 | ARCH-62 四組對應,引的兩頁只撐兩組 | HIT:兩頁確實只有 fromApplication 例;另查 Hilt 原始碼 EntryPointAccessors.kt 的 KDoc,四個方法各寫明只能用在哪個元件 | 折:出處改引原始碼 KDoc,對應表照 KDoc(fromView 含 ViewNoFragmentComponent);依據來源表分開寫每個網址撐哪一部分 |
| p3 | API-7 不寫的理由「分不出是不是 Flow」站不住 | HIT:import 看得到 | 折:理由改寫成出處只說明預設行為、要上限的原則在另一頁,要兩頁拼起來,照判法不算直接(仍不寫) |
| p4 | ARCH-59 清單沒寫全、多重綁定怎麼算沒說 | HIT:同 g1 | 折:同 g1,清單列全 |
| p5 | UI-33 規則與型錄形狀欄不一致 | HIT:型錄情境欄寫無註冊呼叫 | 折:同 c2,型錄情境欄照規則改寫 |
| p6 | IJ 檢查名沒附網址、ARCH-62 的 dagger.dev 網址沒撐對應 | HIT:讀依據來源表;自己開 IntelliJ 檢查頁,原文 Reports map { it.await() } calls on collections of Deferred | 折:依據來源表補 IntelliJ 頁、EntryPointAccessors.kt、javax.inject.Named,ARCH-62 的 dagger.dev 換掉 |
| f1 | ARCH-59 誤報(@IntoSet、@Suppress) | HIT:席位實跑 | 折:同 g1 |
| f2 | scan 只回 (規則, 檔),比對行號沒寫怎麼取 | HIT:check.py 的 scan 只取 ruleId 與 file | 折:scan 加選填參數多回行號,既有呼叫端不變;寫明報的是節點起始行 |
| f3 | 預期值表每條只測一個樣式,刪樣式測試不紅 | HIT:讀預期值表 | 折:每個樣式至少一例,預期值表擴到 21 列 |
| f4 | _KT_STATS_MUTATIONS 寫死的數字會讓改壞不生效 | HIT:讀那段 replace | 折:範圍 5 列進,改成新數 |
| f5 | 解析器限制也影響 ARCH-59 的 object | HIT:席位實跑 M3、M6 | 折:實驗節與天花板改成兩條都受影響 |
| f6 | API-2 漏報與 Flow 的 map 誤報 | HIT:席位實跑 | 折:寫進天花板 |
| f7 | UI-33 提早返回的 return@DisposableEffect onDispose { } 被報,建議放進好例 | HIT:席位實跑 | 放行:提早返回那支也是沒註冊卻寫空 onDispose,出處原文說空 onDispose 不是好做法,照報才對;範圍 1 寫明不放進好例 |
| f8 | ARCH-62 不認具名參數、完整套件名、巢狀名,import 別名可能誤報;regex 不支援往前看 | HIT:席位實跑 | 折:天花板寫明;規則用 all 加 not 的寫法 |
| f9 | 同 g6 | HIT | 折:同 g6 |
| c1 | 沒寫各條放哪支 yml;compose.yml 已刪 | HIT:rules-unwired 只有七支 | 折:範圍 1 每條寫明檔名,compose.yml 重開 |
| c2 | UI-33 命名沒照 kt-compose- 前綴,也沒講跟 UI-32 的分界 | HIT:rules/compose.yml 第 171 行 | 折:改名 kt-compose-dispose-not-needed,改成 UI-32 的互補,註冊判斷抽成 utils 共用 |
| c3 | 新測試沒做目錄、訊息、路徑排除檢查 | HIT:_KTSEC_PLACE 那段 | 折:四條加進 _KTSEC_PLACE |
| c4 | 條款編號順序亂 | HIT | 折:照順序排 |
| c5 | 另開新測試是第二種做法;擴充既有逐例表可用選填欄位(_KTSEC_PLACE 有先例) | HIT:_KTSEC_PLACE 用 (d, fname, cat, *extra) | 折:不另開,逐例表加選填第五欄 |
| c6 | 圖譜只改條數、沒補記放置的那條 WHY | HIT:Systems/kotlin規則包 記各批放置的 WHY | 折:範圍 6 補 |

--refuted-set none。

## 先查世界

- PRIOR-ART:A 組(出處)——開 IntelliJ 檢查說明頁 MapAwaitOnCollectionOfDeferred(原文只講 map { it.await() })、Hilt 原始碼 EntryPointAccessors.kt(四個方法的 KDoc 各寫明允許的元件)、Hilt 官方頁(限定詞定義與 @Qualifier 寫法)、javax.inject.Named javadoc(String-based qualifier)。dagger.dev 的 dev-guide 頁找不到限定詞段,不採用。
- PRIOR-ART:B 組(限定詞判斷)——Dagger 的判定是「被 @Qualifier 標註的註解才是限定詞」,單檔只看得到同檔宣告與 @Named;採用正向認定(確定是才算),判不準就不報,跟靜態分析工具「寧可漏報不誤報」的做法一致,不再用排除清單反推。
- PRIOR-ART:C 組——規則包既有 UI-32 規則已管一半,照「同一份判斷只有一份」的家規抽成 utils 共用。
- PRIOR-ART:D 組——照既有 _KTSEC_PLACE 用選填項擴充的先例,不另開測試。
