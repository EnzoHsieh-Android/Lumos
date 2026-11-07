# r1 收貨紀錄(android行為測試範本與架構測試)

preflight-4: ran

## 前掃(便宜 agent,四項固定清單)

- ①未定義詞:T6–T11、K4–K5 內容沒列 → 用詞節補列;STATE-23 為何不在 T3 → 儀器批定義補理由;macrobench-lab 位置 → 補本機路徑;「第三批情境表態的答案」→ 改指決策 d1。
- ②壞引用:條款綁的五支測試名尚不存在,屬計劃要新建(實作時建),不改。
- ③範圍矛盾:API-10 預設與 d2 不一致 → 做法 1 與天花板 3 改寫;S1「37 列」在 E4/E5 移出時會自紅 → 預期值表與做法 4 補條件;「統計節數字會變」不成立 → 改寫;`template_problems` 掛哪條路徑 → 寫明。

## 語意類命中(修改前 → 後)

- ④1 Konsist 版本:計劃說「產生器檔頭註解與技能文件依賴行改成官方現行版」→ 程式實際兩處都沒有具體版本(依賴行是佔位 `konsist:<版本>`);改寫成「從佔位改寫成具體版本、檔頭新增一行」。
- ④2 Konsist 換版連到 lumos 自己的程式:計劃只列資料檔與技能文件 → `scripts/lumos` 的 `_arch_tpl_konsist_test` 照 0.17.3 反組譯判測試原始碼集,1.0.0-beta.1 改 `scopeFromProduction` 收檔範圍後會分歧;做法 5 補一項要重核並更新、E8 驗兩者一致;另補 Systems/android-arch-template 與 2026-10-30 驗證紀錄寫死 0.17.3 的同步。
- ④3 `resideInPackage` 範圍:補明資料檔三處;新名字以 E8 編譯為準(依據只有發行說明)。
- ④4–④6 成立(`assertion_failure` 判準、正向約束只查接電方式欄、規則數基準 9→12 已補)。
- 以上沒有動到核心裁定(決策 d1–d3)。

## 收貨(r1 四席)

- 四席全 sonnet:通才、可行性(實跑 Gradle 8.13 + Kotlin 2.2.21 最小專案、javap 讀 Konsist 1.0.0-beta.1)、依據(WebFetch 逐頁核對)、架構對齊。外家預設不派,結論寫成「單家族視角下」。
- 從逐字稿存檔,都已正規化;quote-check:依據席 19 句有 2 句錨不到(不採信那兩句,所屬條目另有審材外佐證照採),其餘全錨。席位沒改 repo,臨時目錄已清。

## 先查世界與裁決(編排者)

- PRIOR-ART: 計劃一次引入四樣新東西(圍欄資訊字串標頭、`--lab` 寫檔入口、`涵蓋:` 與 `// 型錄:` 兩種認領語法、K1–K3 加 Konsist 換版),四席共 20 條 major 有 14 條落在這四樣上。照「每個新機制下一輪都是新的審查面、先寫不加它的最小解為什麼不夠」:
  - 範本與型錄的對應:最小解是沿用型錄既有的「通電批次」欄(已被 `catalog_problems` 讀表檢查),把值從「行為測試或正向約束=批五」改成「行為測試或正向約束=範本 T1」這種帶組代號的寫法,自檢只多驗「組代號在範本檔有那一節」;不新造 `涵蓋:`、`// 型錄:`(架構席 F6)。
  - 範本格式:照 DDD 與前端照抄型範本的既有寫法,節用 `## T1 …` 標題、程式用一般 ```kotlin 圍欄,不加資訊字串標頭(架構席 F4);紅綠矩陣是文件表格,由實作時人工逐格跑、寫進驗證紀錄。
  - 實驗專案抽出:拿掉 `check.py --lab`(架構席 F2:自檢是唯讀職責;通才 F2/F3、可行性 F1/F7:標頭無變體、Gradle 骨架無來源)。實驗由實作者在暫存區照範本手工組專案,骨架與 repositories(含 `google()`)寫進範本檔開頭的〈實驗專案骨架〉一節,驗證紀錄附每格結果。
  - K1–K3 與 Konsist 換版:整組移出本批(通才 F4–F8、可行性 F4–F6、依據 F13/F14、架構 F3)。理由:規則包已有同形的三條規則接在新增告警閘;兩席各自打穿 K1–K3 的判斷形狀(函式內建 scope、`rememberCoroutineScope`、sealed UiState、DI 模組);Konsist 1.0.0-beta.1 是兩天前的 beta。另開後續計劃,決策 d3 作廢。
- PRIOR-ART: `MainDispatcherRule` 照 nowinandroid 原檔預設 `UnconfinedTestDispatcher`,會讓 TEST-4 壞測試對正確程式也綠(依據席 F1);改照既有標準 `test-quality-standard.md`「預設用 StandardTestDispatcher」,範本建構時明傳。
- PRIOR-ART: Turbine 收尾照型錄 TEST-18 與既有標準:`expectNoEvents()` 或明確 `cancelAndIgnoreRemainingEvents()`(依據席 F4),不另立更嚴的規矩。

## 逐條去向

全部折入計劃(major 與 minor 都折,這輪不放行),細目由計劃〈審計修正紀錄〉逐條對照;移出本批的條目(K1–K3、Konsist、`--lab`)折法是「移到不做清單並寫理由」。
