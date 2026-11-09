severity: minor

整體判斷:放的層都對,也沒有放錯地方的內容。有三處寫法跟既有做法不完全一致,都是 minor。

**1. 分層與依賴方向:對。**
- 「X 不列:原因」的定義放在型錄〈輸入與口徑〉(`skills/kotlin-idioms/checks-catalog.md:14`),跟既有的「名稱標(出處不全)」等定義同一節,位置對。
- 〈待查證〉刪列、〈統計〉改數、〈接電證據〉補列,都還在型錄原本的節裡。測試錨點(`scripts/test_lumos.py` 的 `_KT_STATS_LINES` 與 `_KT_STATS_MUTATIONS`)跟著型錄的家走,沒有另開地方。
- 家筆記是 `Systems/kotlin規則包`。它的 about_code 有列 `skills/kotlin-idioms/checks-catalog.md`,所以那條 WHY 放對家。
- 驗證紀錄的欄位(type、status、date、valid_under、revalidate_when、tags、plan_refs、system_refs)跟鄰居 `Verification/2026-11-09_Android現成檢查範本在兩個公開專案實跑.md:1-14` 一致。
- 新樣本 ARCH-4、UI-67、UI-98 放在既有的 `samples/lint-wiring/` 目錄,副檔名也照 `UI-16.kt.txt` 的 `.kt.txt`。
- 修補補丁(`r2-repair.patch`)的內容是:
  - 把「無:」全改成「無(…)」。
  - 把 UI-47 的通電批次改成「未接(還沒有規則)」。
  - 驗證紀錄補 `plan_refs`、`system_refs`。
  - 這三項都是往既有寫法靠攏,沒有帶進新的不一致。

**2. 命名與寫法:大致一致,有兩處小偏差。**
- 「無」的寫法:既有列是「無」加括號說明(例:API-14、UI-104、ARCH-14),或「無(自寫 ast-grep kt-xxx)」。修補後新列也用「無(…)」,這點一致。
- 通電批次值全在既有集合內:「未接(還沒有規則)」原本就有 17 列,「批四(CI 範本:Android Lint)」有 102 列,「批一、批四(…)」有 `批一(只有提示級規則,預設不接)、批四(…)` 的先例。
- 標籤:`IDE:`、`編譯器`、`dagger-lint`、`Hilt 編譯器` 在既有型錄都有出現。
- 出處不全的用法:UI-61 名稱後綴「(出處不全)」同時來源欄有〔查證〕,符合〈輸入與口徑〉第 13 行。TEST-12 拿掉後,來源欄補了〔查證 2026-11-09:…〕。
- 接電證據新列的欄位順序與「出處」欄〔真跑 日期:樣本〕寫法,都跟 `UI-16` 的列一致。

**3. 第二種做法:有,見 B1、B2、B3。**
- 括號內的日期寫法(「,2026-11-08 讀官方檢查頁」、「(2026-11-08 第一次真跑)」)既有型錄就有,不算新做法。
- 「只靠實跑的列把結果與日期寫在現成規則欄、來源欄的查證標記只收網址」這條規則只寫在驗證紀錄和〈統計〉,沒進〈輸入與口徑〉。因為上面的日期寫法有先例,這點不單獨列為發現。

B1
severity: minor
blocking: 否
引句:「無(detekt 210 條、sonar-kotlin、Android Lint 629 條都沒有迴圈裡字串 +=(2026-11-09));靠自寫提示級規則」
說明:
- 「靠自寫規則」和「靠自寫提示級規則」是型錄原本沒有的詞,基準版這個詞出現 0 次,〈輸入與口徑〉也沒定義。
- 既有表達「有自寫規則」的寫法是「無(自寫 ast-grep kt-…)」或「自寫 ast-grep;…」(例:API-40、DATA-87)。
- 這次補丁內部也不一致:DATA-30、PERF-9、PERF-2 同樣有自寫規則,現成規則欄卻沒寫「靠自寫規則」。
file: `skills/kotlin-idioms/checks-catalog.md:1113`(僅指出該句所在檔;實際行號依 PERF-23 列為準,審材外佐證另見基準版 API-40 列的「無(自寫 ast-grep kt-webview-file-url-access)」)

B2
severity: minor
blocking: 否
引句:「nowinandroid(AGP 9.3.2、Kotlin 2.3.0)真跑,報在第 3 行六位色碼」
說明:
- 〈接電證據〉的「真跑環境」總行(`skills/kotlin-idioms/checks-catalog.md:813`)沒有更新,仍只列 2026-11-08 的 AGP 8.13.2 那組。
- 既有慣例是環境版本寫進這一行,例外要在這一行加註(例:「第三包 ARCH-76 到 PERF-38 那次…」)。
- 新增的 6 筆把 2026-11-09 的環境寫進每列的「理由」格,是第二種記環境的做法。
- 另有一處小不一致:UI-16 新列的出處〔真跑 2026-11-08:…〕,理由卻提到 2026-11-09 的 nowinandroid 結果。
file: `skills/kotlin-idioms/checks-catalog.md:813`

B3
severity: minor
blocking: 否
引句:「WHY:型錄現成規則欄寫某條檢查涵蓋這列,要拿這列壞寫法實跑過、或有寫明判斷條件的原始碼與說明原文;只確認代號存在不算」
說明:
- ⚠ 判不準。這條 WHY 的 `[出處:…]` 寫成純文字路徑「Verification/2026-11-09_…」,沒用 `[[ ]]`。
- 同一個家筆記裡,多數 WHY 的出處是 `[[Projects/…]]` 連結,所以這條不會進圖譜連結。
- 它也沒有 `[test:]`。這個欄位選填,但鄰近的 WHY 多半有。
- 家筆記的 `verified_by` 已補連結,損害有限。
file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:67`

不對齊共 3 條,其中 major 0 條
