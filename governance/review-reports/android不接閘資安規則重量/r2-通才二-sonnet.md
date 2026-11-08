severity: minor

## Finding 1
severity: minor
blocking: 否
判準:spec 說改動「只寫原文支持的主張」,但型錄列的形狀欄沒跟著改,和移除的規則及實際規則形狀不符。
spec 段落:範圍 5 的三條移出規則與「拿掉沒出處的半句」。
問題:TEST-31 列的形狀欄還寫「`onNodeWithText("中文字面")`」,對應的 kt-compose-test-node-by-literal-text 已移出規則包。TEST-33 列的形狀欄還寫「Robolectric 測試類別沒有 @Config」,但 spec 說固定 SDK 那半沒出處、已刪。規則 kt-robolectric-legacy-looper 只比對 `@LooperMode(LEGACY)`(實際規則只有那一行 regex),從來就不報缺 @Config。ARCH-3 列的形狀欄提到 currentDestination,是 View 半邊遺留。型錄的自檢和測試都沒抓到這種不一致,所以測試全綠。
引句:「8 列找到原文:拿掉出處不全、只寫原文支持的主張、來源欄補〔查證 2026-11-08:網址〕」
佐證:型錄 TEST-31 列的形狀欄原文寫「形狀:…onNodeWithText("中文字面")」,該規則已移除。
``file: `skills/kotlin-idioms/checks-catalog.md:676` ``
``file: `skills/kotlin-idioms/checks-catalog.md:678` ``
``file: `configs/ast-grep/kotlin-android/rules-unwired/testing.yml:29` ``

## Finding 2
severity: minor
blocking: 否
判準:補丁和原文銜接處的新不一致。8 條保留規則「還沒量過誤報」,但型錄通電批次寫成不同的理由。
spec 段落:範圍 5 的「通電批次改寫成跟其他不接閘規則同一句。引用它們的規則照舊在 `rules-unwired/`(還沒量過誤報…)」。
問題:改寫後的句子是「規則在 rules-unwired/:樣本外誤報超過一成或量不夠」。這句對從沒量過樣本外的 8 條規則不實,例如 FLOW-14、CO-37 的 kt-mutex-reentrant、STATE-9。讀型錄的人會以為量過且沒過。同一份 spec 又寫「沒量過誤報」,兩處說法互相矛盾。
佐證:``file: `skills/kotlin-idioms/checks-catalog.md:222` ``。FLOW-14 列沒有任何實測數字,卻寫「樣本外誤報超過一成或量不夠」。

## Finding 3
severity: minor
blocking: 否
判準:補進來的段落自帶未查證宣稱。
spec 段落:範圍 5 的「規則訊息照原文改寫」,以及〈出處補查〉ARCH-3 那列。
問題:代理報告明說「堆疊重複頁」沒有原文,後果欄也寫了連點兩下與兩個後果之間沒有原文連結。改寫後的規則訊息仍寫「導航轉場開始後還會處理點擊、重複導航」。原文(dropUnlessResumed KDoc 與 Lifecycle 2.8.0-alpha02 版本說明)只支持「轉場開始後還處理點擊事件」。ARCH-3 列的後果欄也寫了「重複導航」。「只寫原文支持的主張」在這裡沒做到。
佐證:``file: `configs/ast-grep/kotlin-android/rules-unwired/architecture.yml:4` ``;``file: `governance/review-reports/android不接閘資安規則重量/experiment/source-recheck-a.md:1` ``(「堆疊重複頁」沒有原文)。

## Finding 4
severity: minor
blocking: 否
判準:spec 對實際改動的計數與說法要一致。
spec 段落:〈回退〉的「六條規則訊息」、〈出處補查〉的 API-14 列。
問題:規則訊息實際改了 7 條:async、click、mutex、whilesubscribed、clock、robolectric、node-by-index。去掉形狀也改了的 async 和 click 後剩 5 條,回退清單的「六條」兩種算法都對不上。API-14 列把 #1493 當成「別的 scope 那例與維護者說法衝突」的依據。我讀了議題原文:非等價的脈絡是 DATABASE_CONTEXT 建在 GlobalScope 加 NonCancellable 上,維護者沒有談同一 scope 的 async 和 withContext 是否等價。收窄掉兩個樣式的依據因此是代理的推論,不是維護者說的。規則訊息仍建議同 scope 改用 withContext。計劃決策 d1 還出現正文從未解釋的「DATA-12 改成人裁列那半照舊」。
引句:「kt-async-await-immediately 拿掉「別的 scope 的 async 再 await」兩個樣式(維護者說它跟 withContext 不等價)」
``file: `configs/ast-grep/kotlin-android/rules-unwired/api.yml:77` ``

## 已讀,無 finding 的部分
- 規則包數量:`rules-unwired/` 實數 27 條(6+1+3+3+1+1+12)。三條移除的規則在 rules-unwired、samples 的壞例好例都已刪,`compose.yml` 已整支刪除。
- 收窄形狀:我用 ast-grep 實跑,`scope.async(Dispatchers.IO){…}.await()` 與 `GlobalScope.async` 不報,`coroutineScope { async {…}.await() }` 報,和預期值表 S4 一致。
- 測試:子集 `kotlin_rulepack_unwired_dir`(11 項)、`kotlin_rulepack_samples`(27 項)、`kotlin_catalog_rows_wired`(20 項)都通過。統計的寫死值 226/hint 47/27、出處不全 27、525 列與型錄實際相符。
- 實驗表、重量 7 條的型錄補句、第二份語料與判準 v2、依據來源與驗收條款已讀,沒有發現與卷證或型錄不符。

## 固定席逐條判
固定席節點 Systems/kotlin規則包(掛 0 份計劃、0 行 KEY、0 條合約):不影響。理由:該節點沒有合約行可破壞。spec 要求更新的「不接閘目錄那行改 27 條」與實際一致,會擋目錄 `rules/` 一條都沒動。

## 實務隱患逐類
- 金流:無。只改規則包不接閘目錄、型錄文字、測試和圖譜。
- 對外送出:無。實驗階段抓語料不在消費專案的執行路徑。
- 不可逆:無。全是 repo 內文字檔,退回提交即還原。
- 守衛面:無。會擋的 `rules/` 沒動,消費專案推送前的行為不變。
- 併發寫入:不考慮,依威脅模型單人依序操作。

建過的路徑:`/tmp/lumos-seat-work/android不接閘資安規則重量/通才二-sonnet/`(含 `t.kt`、`sgconfig.yml`、`sgconfig-unwired.yml`)。另外在 `/tmp/lumos-seat-work/x.kt` 的寫入可能失敗,屬誤操作,若存在請一併清除。repo 沒有被我修改。

最高等級 minor;blocking 0 條
