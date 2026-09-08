---
name: swift-idioms
description: 寫或審 Swift（Swift Concurrency／SwiftUI／iOS）代碼前必讀——通用不變量層的慣例規則：並行等待、Task 生命週期、actor 隔離、主執行緒紀律、SwiftUI 狀態與 body 純淨、記憶體與可選處理。每條附壞例→好例與機檢對照（SwiftLint／編譯器嚴格併發）。框架選擇（SwiftUI vs UIKit、TCA vs MVVM、Alamofire vs URLSession）不在此裁——查該專案圖譜。
---

# Swift 慣例（通用不變量層）

**這份文件治的病**：AI 寫出「正確但笨」的 Swift——串聯了本該 `async let` 並行的等待、Task 開了沒人取消、跨 `await` 假設 actor 狀態沒變、把大 JSON 解碼放在 `@MainActor`、SwiftUI `body` 裡建物件。這些不炸在單元測試上，炸在卡頓（hang）、洩漏、上架後的 MetricKit 報表、以及 Swift 6 嚴格併發一開就滿屏紅。

**分層原則**：只寫不隨框架選擇改變的原則。SwiftUI 還是 UIKit、TCA 還是 MVVM、哪家網路層——查該專案的知識圖譜與 CLAUDE.md（`lumos search <關鍵字>` 起手）。規則以「可注入」「可替換」等能力措辭，不點名框架。

**機檢欄說明**：`SwiftLint:規則名`＝有現成規則（⚠ 註明 opt-in 的預設沒開，`.swiftlint.yml` 要列進 `opt_in_rules`）；`編譯器`＝Swift 6 語言模式或 `-strict-concurrency=complete` 會擋；`Instruments`＝量得到但不擋；`不可機檢`＝只有本文件與審查鏡頭能守——這類排最前面。

> **誠實邊界（2026-09-08）**：本文件是網搜＋官方文件整理，**尚未在任何真 iOS 專案上實跑**；第一個接入的專案要把踩到的坑回填進來（同 kotlin-idioms 走過的路）。

---

## 一、並行與 Swift Concurrency（本文件存在的理由）

> **審查時機管道**：本文標「⚠ 不可機檢」的效能／適用性條目，其載重問已由 lumos 效能檢核機制在三時機自動推送（動手前 impact hook 注入／push 前 pitfalls advisory／終審 code-loop 鏡頭；內容源＝lumos-toolchain 圖譜 Systems/效能檢核目錄 iOS 段，雙向同步義務）——可機檢條目歸 SwiftLint／編譯器，勿靠人記。

### R1. 互不依賴的等待必須並行 ⚠ 不可機檢，頭號條款
```swift
// ✗ 笨（延遲相加）：orders 根本不需要 profile 的結果
let profile = try await api.profile()
let orders  = try await api.orders()

// ✓ async let：兩個一起飛，用到時才等
async let profile = api.profile()
async let orders  = api.orders()
let (p, o) = try await (profile, orders)

// ✓ 多筆同型：TaskGroup（要限流就自己數 addTask，或分批）
try await withThrowingTaskGroup(of: Item.self) { group in
    for id in ids { group.addTask { try await api.item(id) } }
    for try await item in group { collect(item) }
}
```
- 判斷順序：先確認無資料依賴，再確認無共享資源（同一個非 actor 物件被兩邊寫＝先隔離再並行），才並行。
- 依據：[Swift Concurrency — Calling Asynchronous Functions in Parallel](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)

### R2. Task 生命週期跟著擁有者走 ⚠ 不可機檢
```swift
// ✗ 畫面走了 Task 還在跑，回來寫已經不存在的 state
.onAppear { Task { await vm.load() } }

// ✓ .task 修飾子：畫面消失自動取消；ID 變了重跑
.task(id: vm.query) { await vm.load() }

// ✓ 手持 Task 的類別：deinit 或 stop() 一定 cancel
private var loader: Task<Void, Never>?
func start() { loader = Task { await run() } }
func stop()  { loader?.cancel(); loader = nil }
```
- 機檢：`自訂`（掃 `Task {` 出現在 `onAppear` 內、或類別有 `Task<` 屬性卻沒有 `.cancel()`）。
- 依據：[SwiftUI .task(id:priority:_:)](https://developer.apple.com/documentation/swiftui/view/task(id:priority:_:))

### R3. 取消是合作制：長工作要檢查、不吞 CancellationError
- 長迴圈／分段工作每輪 `try Task.checkCancellation()` 或看 `Task.isCancelled`；被取消時**不要**把 `CancellationError` 當一般錯誤記 log 或轉成使用者可見錯誤。
- 機檢：`自訂`（catch 區塊沒排除 `is CancellationError` 卻做了 UI 錯誤呈現）。

### R4. actor 隔離不准繞：`nonisolated(unsafe)`／`@unchecked Sendable` 每處要書面理由
- Swift 6 語言模式（或 `-strict-concurrency=complete`）把資料競爭變成編譯錯；繞過它的兩個逃生口只准在「包舊 C 函式庫／已被鎖保護」時用，且旁邊一行註解寫為什麼安全。
- 機檢：`編譯器`（開嚴格併發）＋ `自訂`（grep 逃生口無註解）。
- 依據：[Migrating to Swift 6](https://www.swift.org/migration/documentation/migrationguide/)

### R5. actor 重入：跨 `await` 之後別假設狀態沒變 ⚠ 不可機檢
```swift
actor Cache {
    var entries: [Key: Value] = [:]
    func value(for key: Key) async throws -> Value {
        if let v = entries[key] { return v }
        let v = try await fetch(key)      // ← 這裡別人可能已經寫進同一個 key
        entries[key] = v                  // ✗ 可能蓋掉更新的值 / 重複 fetch
        return v
    }
}
```
- 修法：await 回來後**重新讀**再決定要不要寫；或用 in-flight Task 字典去重（同 key 只 fetch 一次）。
- 依據：[SE-0306 Actors — Reentrancy](https://github.com/apple/swift-evolution/blob/main/proposals/0306-actors.md#actor-reentrancy)

### R6. `@MainActor` 只做 UI；解碼／IO／大計算離開主執行緒 ⚠ 不可機檢
- `@MainActor` 類別（ViewModel 常見）裡的 `await` 之後的重活還是在主執行緒；重活包成 `nonisolated` 函式或丟給非主 actor／`Task.detached` 再回來。
- 機檢：`Instruments`（Hangs、Time Profiler）；review 先問。
- 依據：[WWDC — Analyze hangs with Instruments](https://developer.apple.com/videos/play/wwdc2023/10248/)

---

## 二、記憶體與生命週期

### R7. 逃逸 closure／Timer／NotificationCenter／Combine sink 抓 `self` 要 `[weak self]`
```swift
// ✗ 循環引用：timer 抓 self，self 抓 timer
timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in self.tick() }

// ✓
timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in self?.tick() }
```
- 例外：**非逃逸**閉包（map/filter/forEach）與 `Task { }` 內短命工作不需要——但 R2 的手持 Task 仍要 cancel。
- 機檢：`SwiftLint:unowned_variable_capture`（opt-in，抓 unowned）、`Instruments`（Leaks／Memory Graph）；`[weak self]` 漏寫本身無現成規則＝`自訂`。

### R8. 值語意優先：`struct` ＋ `let`；`class` 只在需要身份或共享可變狀態時
- 資料模型、UI state、API 回應一律 struct（Sendable 免費得到，跨 actor 不用想）。需要引用語意的（快取、連線、協調器）才用 class，並明確標 `final` 與隔離。
- 機檢：`SwiftLint:final_class`（opt-in 版本名依版本異動，查當前 rule 清單）。

---

## 三、SwiftUI 狀態與 body

### R9. `body` 純淨：不做 IO、不建昂貴物件、不做 side effect ⚠ 不可機檢
```swift
// ✗ 每次重算 body 都新建 formatter / 解碼 / 排序
var body: some View {
    let f = DateFormatter(); f.dateStyle = .medium
    List(items.sorted { $0.date < $1.date }) { Text(f.string(from: $0.date)) }
}

// ✓ 昂貴物件 static / 注入；排序在 model 層做一次
private static let f: DateFormatter = { let f = DateFormatter(); f.dateStyle = .medium; return f }()
var body: some View { List(vm.sortedItems) { Text(Self.f.string(from: $0.date)) } }
```
- 機檢：`Instruments`（SwiftUI instrument：body 更新次數與時長）。
- 依據：[WWDC25 — Optimize SwiftUI performance with Instruments](https://developer.apple.com/videos/play/wwdc2025/)

### R10. 觀察範圍最小化：葉節點只拿它要的值，別把整個 store 傳到底 ⚠ 不可機檢
- `@Observable` 追蹤到屬性級，但你把整個大物件傳進子 view 又在 body 讀了它的多個屬性，任一屬性變就整棵重算。子 view 收「值」或收小型子物件。
- `@State` 只給 view 私有的狀態；跨 view 的狀態放 model 由外注入（`@Environment`／參數），避免 source-of-truth 分裂。
- 依據：[Managing model data in your app](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)

### R11. `List`／`ForEach` 的 `id` 必須穩定
- 用 `Identifiable` 的持久 id；**不要**用 `\.self` 配可變 struct、更不要用索引——會讓 diff 失效、動畫亂跳、cell 狀態錯位。
- 機檢：`自訂`（掃 `ForEach(... , id: \.self)` 與 `indices`）。

---

## 四、錯誤、可選、邊界

### R12. 非測試碼禁止 `!` 強制解包、`try!`、`as!`
- 這三個是「我保證不會 nil／不會 throw」的宣示，而 AI 最常在**不保證**的地方寫它。用 `guard let`／`if let`／`try?`＋明確錯誤路徑。
- 機檢：`SwiftLint:force_unwrapping`（**opt-in**）、`SwiftLint:force_try`、`SwiftLint:force_cast`（後兩者預設開）、`SwiftLint:implicitly_unwrapped_optional`（opt-in）。

### R13. 錯誤要有型別邊界，`catch { }` 不准吞
- 對外 API 的錯誤在邊界轉成領域錯誤（enum），內部不要一路 `Error` 到 UI；空的 `catch {}` 與只 `print` 的 catch 等於吞。
- 機檢：`自訂`（空 catch／catch 只 print）；Swift 6 typed throws（`throws(MyError)`）可讓編譯器幫忙。

### R14. 不可逆的外部動作（付款、送出、刪除雲端資料）要防重送
- 按鈕點兩下、`.task(id:)` 重跑、重試機制，三者都會讓同一個動作跑兩次。冪等 key／in-flight 旗標／按下即 disable，擇一並寫進節點的 `[guard:]`。
- 機檢：`不可機檢`；這一條對應圖譜 ★IRREVERSIBLE★ 合約的 rollback／guard 要求。

---

### R15. 型別抹除與 layout 反覆：少用 `AnyView`、`GeometryReader`、大樹隱式動畫 ⚠ 不可機檢
- 條件分支回傳不同型別、或包成 `AnyView`，讓 SwiftUI 的 diff 失效整段重建；`GeometryReader`／深層堆疊／preference 鏈會讓 layout 多跑幾遍；`.animation(...)` 掛在大樹上等於每個子節點都動畫。貴的子樹用 `equatable()` 或把輸入包成值型別擋重算。
- 機檢：`Instruments`（SwiftUI instrument 看更新次數）；`自訂`（掃 `AnyView(`）。
- 依據：[WWDC25 — Optimize SwiftUI performance with Instruments](https://developer.apple.com/videos/play/wwdc2025/306/)

### R16. 耗電：背景工作走系統 API、網路請求合併 ⚠ 不可機檢
- 背景持續定位／輪詢／計時器是電池殺手：定位精度按需（`desiredAccuracy`、significant-change）、背景工作用系統背景任務框架而不是自己開 timer；網路請求合併批次、快取、重用連線——能量大宗是無線電喚醒，零散小請求最貴。
- 機檢：`不可機檢`；prod 端 MetricKit 的背景耗電報表歸 ops，code review 只能先問。
- 依據：[Apple — Energy Efficiency Guide for iOS Apps](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/EnergyGuide-iOS/)

---

## 接線表（裝了不等於開了）

| 規則 | SwiftLint 規則 | 預設 | 動作 |
|---|---|---|---|
| R12 強制解包 | `force_unwrapping` | **opt-in** | `.swiftlint.yml` 的 `opt_in_rules` 加進去，等級升 error |
| R12 `try!`／`as!` | `force_try`／`force_cast` | 開（warning） | 升 error |
| R12 隱式解包 | `implicitly_unwrapped_optional` | opt-in | 加進 opt_in_rules（IBOutlet 例外用 `excluded`） |
| R7 unowned | `unowned_variable_capture` | opt-in | 加進 opt_in_rules |
| R4 隔離逃生口 | 編譯器 `-strict-concurrency=complete`／Swift 6 語言模式 | 依專案 | 新專案直接開；舊專案先 `minimal`→`targeted`→`complete` 分階段 |
| 全部 | SARIF 進審查 | — | `swiftlint --reporter sarif --output <檔>` 登進 `.lumos/lint.json`（見圖譜 linter精選目錄 Swift 段） |

**依據總表**：[The Swift Programming Language — Concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)、[SE-0306 Actors](https://github.com/apple/swift-evolution/blob/main/proposals/0306-actors.md)、[Migrating to Swift 6](https://www.swift.org/migration/documentation/migrationguide/)、[SwiftLint rule directory](https://realm.github.io/SwiftLint/rule-directory.html)、[Apple — Managing model data](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)。
