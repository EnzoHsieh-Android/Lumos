preflight-4: ran

# r1 前掃收貨(Projects/Android儀器測試範本與架構測試_計劃)

前掃四項固定清單:①未定義詞 6 ②壞引用 5 ③範圍矛盾 7 ④機械宣稱驗語意 10。①②③直接修進計劃;④逐條寫「修改前 → 後」。決策 d1(K1、K2 用 ArchUnit)、d2(產生器 Konsist 先不換)沒有改動。

## ① 未定義的詞(6,全修)

1. 第五批/前半/調研稿 → 〈用詞〉新增「第五批、前半、後半」一條,含第五批調研稿。
2. 通電批次欄 → 〈用詞〉新增一條,指到型錄〈輸入與口徑〉。
3. 會談暫存區 → 〈用詞〉新增一條(實作會談自己的 scratchpad、不進 repo、做完刪)。
4. lab、lab 複本 → 〈用詞〉新增一條。
5. r1、F 編號 → 〈用詞〉新增一條(前半設計審第一輪、卷證路徑、席名加編號)。
6. K2 → 見 ③2。

## ② 壞引用(5)

1. 「實驗 S4 那格會實證」(S4 是條款,沒有對應實驗) → 新增實驗 E12「LeakCanary 在 debug 建置拿得到堆積」,審計修正紀錄那句改指 E12;拿不到時 TEST-35 改回「未接(儀器批)」。
2. `t_kotlin_catalog_instrumented_batch_notes` 沒標新增 → 條款 S6、〈做法〉3、〈回退〉都標「新增」。
3. 四支既有測試內容不夠 → 見 ③3、④4。
4. 節名〈Android 資料層(Room)〉不精確 → 改成〈Android 資料層(Room)的撰寫補充〉並在〈做法〉4 寫檔案路徑 `skills/lumos-project-notes/commands/test-quality-standard.md`(做法 4、S7、預期值表三處)。
5. 已驗存在的引用 → 不改。

## ③ 範圍自相矛盾(7)

1. 列數全對 → 不改。
2. K2 定義與前半衝突 → 〈用詞〉K 測試寫明「前半的 K2 掛 CO-5,本計劃改掛 CO-1,其餘代號沿用」,「前半」一條也註明只有 K2 改了;白話段改成「前半打算做成架構測試 K1–K3 的三列(API-9、CO-5、UI-39)」並說 K2 改掛 CO-1;〈做〉表 T12 列寫「另含 K2(CO-1,型錄 CO-1 列不改值)」。
3. 〈做法〉3 只寫一支、說「允許的值不新增」 → 改成五支測試逐支寫要改什麼:c_rows 範本組擴成 T0–T13、`_KT_UNWIRED` 拿掉兩個舊值、寫死的 32 列改照新範圍;sections 新寫內容檢查;content_guards 的組清單 T0–T13;linked 加 S7;instrumented_batch_notes 新增。
4. E9 退路是「不接(代碼審或真機)」與 S1 計數衝突 → E9 改成跟其他移出列一樣回「未接(儀器批)」,端到端驗收會紅那句改寫進驗證紀錄。
5. 「四個打穿點」實為六條發現 → 立案段改「共六條發現,打穿的是四種寫法:…」,決定 1 改「打穿的四種寫法」。
6. DATA-21 的 `runCatching` 沒寫 → 〈做法〉1 T6 補「壞寫法丟 `SQLiteException`(too many SQL variables),先 `runCatching` 接住再斷言筆數」。
7. Q1 題文說 detekt「只看新增的行或要型別資訊」,跟正文矛盾 → **沒改**:Q1 已由編排者結題、指向決策 d1,題文屬那筆裁定的紀錄;不準處只在題文的理由句,不影響 d1 的結論。正文分工表已寫對(`GlobalCoroutineUsage` 不要型別資訊、`InjectDispatcher` 要)。列給編排者決定要不要另記一句更正。

## ④ 機械宣稱驗語意(10)

1. room-guard 符合 → 不改。
2. `assertion_failure` 符合 → 不改。
3. `template_problems` 符合,只驗「有那一節」 → 不改(內容檢查由 ④4 補)。
4. S2 說 `t_kotlin_test_templates_sections` 驗骨架含 `sdk=34`、`testInstrumentationRunner`。
   - 修改前:〈做法〉3 只提 c_rows 一支,S2 默認既有測試做得到。
   - 修改後:〈做法〉3 明寫 sections 這支要「新寫內容檢查」(T6–T13 八節、骨架節、`sdk=34`、`testInstrumentationRunner`),並註明現在只驗 `template_problems` 與三種改壞。
5. `kt-uistate-mutable-field` 實為 PERF-30。
   - 修改前:分工表 UI-39 列寫規則包 `kt-uistate-mutable-field`;表下「三者訊息都以型錄編號開頭;改型錄那列的標準寫法時三邊一起看」。
   - 修改後:UI-39 列寫「沒有直接對應的規則;同形的 `kt-uistate-mutable-field` 訊息以 `[PERF-30]` 開頭,掛在型錄 PERF-30(級 A+B,不在本批)」;表下改成「改 API-9、CO-1 時規則包、detekt、T12 三邊一起看;改 UI-39 時要連 PERF-30 與它的規則一起看,T13 節開頭寫這一句」。CO-1 列補「訊息以 `[CO-1]` 開頭」(已核 coroutines.yml)。
6. 「規則包:這次新增的行」。
   - 修改前:分工表寫規則「這次新增的行,語法樹判」。
   - 修改後:「語法樹判整支檔,新增告警閘只報這次新增的行」;表下「規則包(經新增告警閘)與 detekt(推送前只給改到的檔時)管這次寫的」。
7. Fragment `lifecycleScope` 那半實際沒人接 → **本計劃接**。
   - 修改前:〈做法〉T12「節開頭寫明由規則包與 AndroidX Lint 管」;天花板 4「那半靠規則包、AndroidX Lint 與代碼審」;分工表「Fragment `lifecycleScope` 那半不判」;E5「Fragment 裡 `lifecycleScope.launch`(綠——記下這是天花板)」。
   - 修改後:T11 新增小節〈測試:API-9 Fragment 畫面銷毀後〉(`FragmentScenario` 移到 CREATED 後再發一筆,壞寫法 Fragment 自己的 `lifecycleScope` 碰已銷毀的 view、`runCatching` 後斷言;好寫法 `viewLifecycleOwner.lifecycleScope` 加 `repeatOnLifecycle`,型錄 API-9 標準寫法);〈做〉表 T11 列補「另接 API-9 的 Fragment 那半」;型錄 API-9 值仍是「範本 T12」,T12 節開頭指到 T11 這個小節;T12 寫明「規則包也沒有規則判它(只有 STATE-5、PERF-4、ARCH-50 碰 `lifecycleScope`)」;分工表改「由 T11 的行為測試接」並註明規則包沒有規則;天花板 4 改成「那半只有 T11 的行為測試接,專案沒照範本寫就沒接上,規則包沒有對應規則」;E5 改「T12 綠——那半由 T11 的 API-9 小節接」。
8. `goAsync` 差異。
   - 修改前:K1 允許類別只有 `Application` 子類別與 `@Module`,沒提 `goAsync`。
   - 修改後:T12 加一個豁免「同一個方法裡也呼叫了 `BroadcastReceiver.goAsync()` 就豁免」,與規則包 `kt-unmanaged-scope-launch` 的排除對齊;E5 加兩個樣本(有 `goAsync` 綠、沒有紅);E7 改成三個豁免各改壞一次;分工表兩邊都註明 `goAsync` 豁免。
9. `lumos arch-template android` 相關敘述符合 → 不改。
10. `FreezingArchRule` 建清單檔的設定。
    - 修改前:沒寫。
    - 修改後:T12 寫 `src/test/resources/archunit.properties` 放 `freeze.store.default.allowStoreCreation=true`;E5 加「先不放這個檔跑一次,記下 ArchUnit 預設准不准建清單檔」。

## 動到決策的

- 沒有。d1、d2 的內容與結論都沒改;只有 ③7 涉及 Q1 題文,留給編排者。

## 收貨(r1 四席)

- 四席全 sonnet:通才、可行性(實跑 ArchUnit 1.5.1+Kotlin 2.2.21、Robolectric 4.16+AGP 8.13.2+JDK 17)、依據(WebFetch 逐頁核對)、架構對齊。外家預設不派,結論寫成「單家族視角下」。
- 從逐字稿存檔,全正規化;架構對齊 8 句有 1 句錨不到(該席自己標明作廢的那條 F3 舊引句,不採信,以更正版 F3 為準),其餘全錨。席位沒改 repo;臨時目錄已清。
- 架構對齊 F1(K1/K2 用 ArchUnit 撞到 Projects/Android的MVVM與DDD目標架構範本_計劃 的舊否決):已問使用者,使用者 2026-11-06 原話「A」裁定翻案,記為決策 d3;F1 的處置改成「計劃補寫翻案理由與兩套函式庫分工」。

## 先查世界與裁決(編排者)

- PRIOR-ART: ArchUnit 凍結清單——官方手冊 8.6.2 寫 `freeze.store.default.allowStoreCreation` 預設 false、必須設 true 才能建新清單(https://www.archunit.org/userguide/html/000_Index.html );可行性席實跑證實常駐 true 時刪清單檔會全綠並把新違規一起凍結。採用:範本預設 false,只在初次建清單時以環境變數或單次參數打開;寫明 `freeze.store.default.path` 並教使用者提交清單檔;E5 預期照實跑改寫。
- PRIOR-ART: Kotlin 編譯產生的合成類別(suspend lambda 狀態機 `X$f$1`、`Companion`、`load$default`)——判允許類別改看最外層宣告類別(ArchUnit `JavaClass.getEnclosingClass` 遞迴到頂層),函式預設值的 `$default` 跟建構子預設值同理豁免;測試源集排除要針對 AGP 路徑實測。
- PRIOR-ART: 協程裡丟的例外 `runCatching` 接不到——官方協程例外處理頁:launch 的例外交給 CoroutineExceptionHandler(https://kotlinlang.org/docs/exception-handling.html );範本改用可觀測的旗標或假依賴記錄來斷言(例:假 binding 記下「被已銷毀的 view 呼叫」次數),不靠接例外。WorkManager 取消壞寫法同理換成可觀測的形狀(斷言取消後假資源的 close 次數或迴圈計數),並防空轉卡死(測試加明確的計數上限)。
- PRIOR-ART: Room 3 已穩定(官方版本頁 3.0.3,2026-09-09;遷移測試頁範例已是 room3),T6 同時寫 Room 2.8.5 與 Room 3.0.3 兩份〈依賴〉;MigrationTestHelper 一律具名參數。

## 逐條去向

全部折入(通才 8、可行性 10、依據 6、架構對齊 4,共 28 條;架構對齊作廢的舊 F3 不計),細目由計劃〈審計修正紀錄〉逐條對照。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 架3 | 架構對齊報告中第一個 F3 | 席位在報告內自行宣告作廢、以下一條更正版 F3(記為 架4)為準 | MISS:席位自行作廢,不是發現 |
| 可1 | 可行性 F1 | 刪 archunit_store 後重跑 | HIT(席位實跑):全綠並凍結新違規 |

refuted: 架3
