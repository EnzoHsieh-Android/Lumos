preflight-4: ran

# r1 收貨紀錄(前掃)

前掃由一個 sonnet 代理照固定四項清單掃計劃真檔(未定義的詞、壞引用、範圍矛盾、機械宣稱驗語意),只讀。①②③類命中直接修真檔、不算發現;④語意類逐條記在下面(修改前→修改後),席位可以覆核推翻。

## 語意類修正(修改前 → 修改後)

1. 〈用詞〉被問到之後的路
   - 前:「盲判對不上就擋;判不了只能由人段放行,AI 下的放行列到有人確認為止」
   - 後:擋的是缺段、缺列、答案形狀不對、缺第一盲判、不一致又沒仲裁;證據樣式對不上與仲裁多數判作者沒照做只提醒;段放行人或 AI 都能下,AI 下的列到有人確認。
   - 依據:前掃讀 scripts/lumos 的 `_kt_sit_shape`、`_kt_sit_check`、`_kt_sit_verdict_one`、`cmd_lint_waive`。
2. 〈用詞〉公開名稱第③類
   - 前:「③列舉值與物件常數,寫成 `類別.名稱`(例 `SharingStarted.Lazily`、…、`Dispatchers.IO`)。都排除:…名稱含 `$` 的」
   - 後:兩種來源——大寫開頭的 static field;object(有 INSTANCE)或 `$Companion` 裡不帶參數、非 synthetic 的 `get<大寫>` 讀取函式還原成屬性名;排除「還原之後仍含 `$`」的。
   - 依據:1.10.2 `.api` 原檔裡 `Dispatchers.IO` 只有 `getIO()`,`SharingStarted.Lazily` 是 `SharingStarted$Companion` 的 `getLazily()`;照原寫法錨點名稱永遠抽不到。
3. 範圍 1 歸屬比對方向
   - 前:「那個名稱要能被那一列的某個觸發字以整字比對命中」
   - 後:方向寫死為「觸發字經 `_kt_trigger_re` 的正規式搜名稱」,附反方向會把 `launch` 誤算進 `viewModelScope.launch` 的理由。
   - 依據:前掃本機實測五組組合(見前掃回報第 4 節第 3 條)。
4. 範圍 2 誰會跑自檢
   - 前:「接進 `catalog_problems`,所以 `--catalog-only` 與推送前的規則包自檢都會跑」
   - 後:推送前閘與 CI 不直接跑 `check.py`,是跑直接呼叫 `catalog_problems` 的型錄測試;`skills/` 改動不會被判成純文件。
   - 依據:前掃找不到 pre-push 或 CI 直接執行 `check.py`;編排者另讀 scripts/lumos 純文件判定(`_DOCS_ONLY_PATHS` 不含 `skills/`,註解明寫 skills/ 的 markdown 一律跑全套)。
   - 附帶發現的筆記錯誤:[[Systems/kotlin規則包]] 摘要裡「推送前的規則包自檢與 --catalog-only 都會跑」同一句也不對;實作時一併改寫。
5. 〈實務隱患〉片段包裝
   - 前:「切段只看文字,不影響比對」
   - 後:剝註解與字串是詞法掃描,落單引號會吃掉後段;這種片段照判,判不中就進表並寫明理由。
   - 依據:前掃讀 `_kt_strip_spans`。

## 其他直接修的(①②③類)

- 補〈用詞〉:型錄主表列編號、會擋的規則、通電批次欄與範本 T<n>、停用列與停用字表、段放行、代碼審;`.api` 門面類別與 synthetic 的意思寫進公開名稱那條。
- PRIOR-ART 的「1.10.2 到主線」改成「1.10.2 與 1.11.0 兩版比對」(編排者另抓 1.11.0 原檔比過,多 17 個函式)。
- S5 綁的測試已存在,條款註明「擴充既有的統計核對測試」。
- 預期值表 S2 第一列的現況:D-4 已補 `flatMapConcat`,測試要在型錄複本上改壞;條款本身不變。

## 使用者同輪補充(不在本案範圍)

使用者 2026-11-12 定最終目標:情境題答案要引規格出處、規格沒寫就擋交人。寫進計劃〈天花板〉5 與一行 REVISIT,另開後續計劃。

# r1 席報告收貨(四席到齊後)

## 收貨三道

- report-normalize:四份都已是正規化格式。
- quote-check:通才、正確性、架構對齊全數錨定;邊界席原報告沒用「引句:」格式,經續談請它只補自己講過的逐字引句(不改內容),併回報告後 11 句錨定 10 句。
- refcheck:四份 missing 0,只有架構對齊席的 `configs/ast-grep/kotlin-android/api/` 是計劃標(新增)的目錄。
- seat-check:派工單材料格式判 vacuous,不判漏查。
- git status:repo 沒被席位動過(只有本會談自己的計劃、卷證與 lumos 帳檔)。

## 機械重現(錨不到的引句與關鍵佐證)

| 發現 | 命令 | 結果 | 判定 |
|---|---|---|---|
| b8 | `grep -n "情境列「對應檢查」欄每個編號" r1-snapshot.md` | 第 32 行命中原文;引句內再包「」被收貨截斷 | HIT,採信 |
| g1 | 讀 1.10.2 `.api`:`Channel$Factory` 只有 `BUFFERED`、`CONFLATED`、`RENDEZVOUS`、`UNLIMITED` 等 static field | 照原抽法還原成 `Channel$Factory.UNLIMITED`,含 `$` 被排除 | HIT |
| g2/c2/b11 | klib 清單 `grep -n "trySend\|limitedParallelism"` | 第 116、428 行是成員宣告,JVM 原抽法三種名稱都不收成員 | HIT |
| c1 | 讀 scripts/lumos `_kt_situation_segments` 的路徑篩選 `_PITFALL_DIFF_TEST_PAT`、`_stack_changed_ok` | 測試檔不出情境段;反查用 `_kt_sit_text_segments` 不經這道 | HIT |
| g5/c4/b6 | 讀 `rules/api.yml` 的 kt-map-await-deferred | 只兩個 map 樣式,檔內註解寫不收 forEach | HIT |
| g10/c6/b7 | `sweep2.py.txt`(拿掉原腳本的長度過濾) | 去掉停用列、含(無)列:184 個、叫不出 95 個;原 180/91 是長度過濾少算 | HIT,改計劃數字 |
| c5/b7 | 比對 1.10.2 與 1.11.0 `.api` | 17 個條目、10 個不重複名稱 | HIT,改依據來源寫法 |

## 分組與處置(33 條真發現全部折入;c7 是正確性席自報「已讀無問題」的段落,不是缺陷,記放行)

1. 母體定義(g1、g2、g8、c2、c5、b3、b4、b11、g11、a4):改用 klib 清單為主、JVM 清單補;名稱一個一列、不分多載與同名工廠;兩份檔核 sha256;錨點加 `UNLIMITED`、`trySend`,總數下限 300。
2. 改由要能驗(g3、g5、c4、b6):兩節共用一組改由;規則要片段在壞例樣本、完整自檢實跑;範本排除 T0、要有那個對應檢查的壞寫法小節;停用字表裡的決策點改標 `決策不問`,不准寫 `無決策`。
3. 歸屬與同步(c3、b1、b2、g6):反向同步跟正向同方向(觸發字搜名稱);新增 `撞名 D-n`;沒有情境列的決策點標 `決策不問:代碼審`,列進天花板 6。
4. 反查路徑(c1):反查先過推送前同一道路徑篩選,`TEST-` 片段用測試路徑。
5. 補字品質(g4、g9):新觸發字只准母體或官方公開名稱;換掉 D-60 的 `in bigList`;頻率量法寫明腳本、補完量整體命中比例。
6. 宣稱範圍(g7):白話改成「沒被問到的都要列表、寫明誰抓」;天花板補別名匯入、壞在沒寫、沒有情境列三項。
7. 接法(b5、a1、a2、b10、a3):照 `situation_sample_problems(lumos=)` 另串、不進 `catalog_problems`;參數傳入型錄、樣本、母體;新節放〈接電證據〉之後;回報形狀與 `_api_names` 私有寫明;測試用暫存母體、不上網。
8. 口徑與小項(g10、g12、c6、b7、b8、b9):單位與數字照重數;停用列不算、(無)列算;S3 綁兩支測試;剝字串的會吃字元補齊。

## 先查世界

- 母體來源 PRIOR-ART:查 BCV 的 klib 支援,設計文件與 kotlinx.coroutines repo 的 `.klib.api`(https://github.com/Kotlin/binary-compatibility-validator/blob/master/docs/design/KLibSupport.md 、https://github.com/Kotlin/kotlinx.coroutines/blob/1.10.2/kotlinx-coroutines-core/api/kotlinx-coroutines-core.klib.api )。klib 清單用原始碼名稱、含成員、沒有雜湊,採用;它不含 JVM 平台,所以 JVM 清單當補來源;官方標 klib 格式實驗性、版本間改過排版,所以釘檔加雜湊。排除:只用 JVM 清單還原(r1 三席舉出四種還原失敗)。
- 改由規則 PRIOR-ART:Semgrep 規則測試用逐行 `ruleid:`/`ok:` 標註,每一行都要被報或不報(https://semgrep.dev/docs/writing-rules/testing-rules ),ast-grep 的 valid/invalid 同理(https://ast-grep.github.io/guide/test-rule.html )。採用「片段在壞例樣本、完整自檢實跑確認那一行被報」。排除:只核規則編號(三席實測放過 `forEach { it.await() }`)。
- 其他六組是本專案內部口徑(路徑篩選、接法、數數口徑、措辭),照既有程式與既有自檢的先例改;這六組沒有另外上網查(判斷是內部口徑對齊,不是做法選擇)。

## 折入後鏡像核對

派一個 sonnet 代理只讀改寫前後與席報告、intake,核對八組有沒有改到、舊說法殘留、段落之間矛盾。回報六條,全部修:
1. `api_decision_problems` 參數補樣本目錄與範本全文(改由核對要用)。
2. `--sg` 完整模式實跑規則補落點:新增 `route_rule_hits_problems`,兩節的 `規則 <id>` 都實跑;S5 補〈API 決策點〉那一半。
3. S3 指明 API-8 壞寫法欄的片段 `flatMapMerge`(D-4 已有 `flatMapConcat`,只拿掉 `flatMapMerge` 時那段仍叫得出)。
4. 範圍 5 寫明 D-4 補 `mapLatest`、`transformLatest`,回退段跟著提。
5. 白話的分類補「撞名」,跟範圍 1 的四種一致。
6. 天花板 4 的 `onClick` 不在母體,改成「不在母體的進〈叫不出的壞寫法〉」。
另補第二組只改一半的那條:停用字表裡的名稱標 `無決策` 要以「停用字,不帶決策:」開頭並寫理由,自檢核;S1 補撞名是假的、停用字無決策、`決策不問:不是寫法`、名稱少於 300 四個案例;範圍 2 補「任一列理由空白」總則;S4 寫明指到真型錄。
