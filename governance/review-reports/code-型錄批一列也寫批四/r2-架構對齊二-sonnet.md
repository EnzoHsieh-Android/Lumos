severity: minor

我沒有跑測試,只讀了 `r2-repair.patch` 和鄰近既有檔。結論:結構與既有做法一致,沒有第二種判法或跨層呼叫;不對齊的地方有一條,是 `check.py` 的 docstring 沒跟著改。

**1. 分層與依賴方向:對齊。**
- 新字樣「間接」「相關」「需標註」直接加進 `_B4_SKIP` 這個既有元組,沒有另開常數或函式。
  - 引句:「_B4_SKIP = ("待查", "預設關", "相近", "opt-in", "間接", "相關", "需標註")」
  - 既有位置:`configs/ast-grep/kotlin-android/check.py:119`、`:130`(`any(w in seg for w in _B4_SKIP)`)。
- 口徑說明的位置也一樣:`check.py` 在元組上方寫註解,型錄〈輸入與口徑〉那一句判定口徑追加字樣,筆記 WHY 補一句。
  - 引句:「而且那一段不含「待查」「預設關」「相近」「opt-in」「間接」「相關」「需標註」」
- 但 `check.py` 的 docstring 沒跟著改,見下面第 1 條。

**2. 命名與寫法:大致對齊,有一條不一致。**
- 型錄 UI-1 補的註記放在該規則碼後的括號裡,和既有的 `(待查:…)`、`(待查是否涵蓋 Cursor)` 同形。
  - 引句:「androidx:ConstantContentStateKeyInItemsCall(相關:管 items 裡元件的內容狀態 key 不重複,不管 items 有沒有 key =,2026-11-08 讀官方檢查頁)」
  - 既有寫法的出現處:`skills/kotlin-idioms/checks-catalog.md`(grep 到的「(待查…)」括號註記)。
  - 補充:既有括號註記只出現「待查」字樣,「(相關:…)」是新用法,但它正好就是被排除的字樣,屬於同一套寫法。
- 測試斷言用同一個 `check(label, 條件, 訊息)` 形狀,改壞例子也是往既有的元組表追加一列。
  - 引句:「("批一的列拿掉 compose-rules 那種批四", i_b1cr, f"告警帶寫法=批一、批四({cr})", "告警帶寫法=批一")」
  - 既有位置:`scripts/test_lumos.py:129128`(`t_kt_catalog_batch4_wiring`)。
- 筆記是改寫既有那條 WHY,沒有另開新行。這和「同一個決定一條 WHY」的鄰居做法相同,只是這條的「不選」欄改成了新內容。
  - 引句:「[不選:逐列寫例外(用註記字樣判,同一條口徑;代碼審 r1 審查席 F1)]」
  - 既有位置:`docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:57`。

**3. 第二種做法:沒有。**
- 測試呼叫的是同一個 `tags(...)`,也就是 `batch4_expected_tags`,沒有在測試裡另寫排除判法。
  - 引句:「check(f"r1 折入 段裡註記「{w}」→ 不標", tags(f"內建:WrongThread({w})") == [], str(tags(f"內建:WrongThread({w})")))」
- 三列退回批一(UI-1、TEST-23、PERF-2)只改型錄資料,沒有加例外清單。

**不對齊的條目**

1. `check.py` 的 `batch4_expected_tags` docstring 還寫著舊字樣表,沒隨 `_B4_SKIP` 加三個字同步。
   - 引句:「而且那段不含待查、預設關、相近、opt-in,規則碼不是 B4_DEFAULT_OFF 才算。」
   - 證據:`configs/ast-grep/kotlin-android/check.py:127`(docstring 仍是四字),`:119`(元組已是七字)。
   - 影響:型錄口徑句與筆記都已改成七字,只有這處留舊。
   - 為什麼標 minor:這是文字不一致,結構沒錯。

severity: minor
blocking: 否

不對齊共 1 條,其中 major 0 條
