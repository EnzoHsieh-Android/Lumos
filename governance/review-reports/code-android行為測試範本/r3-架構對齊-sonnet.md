severity: minor

**① 分層與依賴方向**

查證結果:r2 指出的三處分岔,主表和批次值兩處真的收斂了,圍欄判定則仍保留一份複本,屬於有守衛的複本。

- 主表只剩 `main_rows` 一種讀法。`catalog_problems` 呼叫 `main_rows(text, problems)`,舊的內嵌迴圈已刪。測試端的 `_kt_main_rows` 和 `_kt_behavior_value` 已刪,改呼叫 `m.main_rows()` 和 `m.behavior_value()`。這點成立。
- 依賴方向是測試單向載入兩邊。`t_kotlin_template_fence_parity` 同時用 `_ktpack()` 載入 check.py、用 `_load_lumos_module()` 載入 lumos。兩個模組互不 import,這個載入方式在既有測試裡很常見(`scripts/test_lumos.py:689` 一帶),方向合慣例。
- 圍欄判定在 check.py 裡仍是第二份,但做法合既有慣例。既有先例是 `scripts/hooks/claude/ci-status-hook.py:48`:標明是複本,獨立檔 import 不到,有測試盯著兩份一致。這份補丁照同一模式做了,宣稱「對齊」也屬實:`_fence_regions` 的縮排 ≤3、tab 不算、收尾同字元且不短於開頭、strict 才要求收尾後只有空白,逐條對上 `scripts/lumos:5369`。`_visible_lines` 的「嚴格讀完還有圍欄沒關就整份退回寬鬆」也對上 `scripts/lumos:5326`。所以不算新的第二種做法。

引句:「圍欄判定跟 lumos 一致:{name}」

**② 命名與錯誤處理**

F1
severity: minor
blocking: 否
引句:「rows, seen = {}, set()」
`main_rows(text=None, problems=None)` 用「傳進一個 list 讓函式往裡塞」的方式回報問題。check.py 其他函式都是自己回傳 list:`catalog_problems`(`configs/ast-grep/kotlin-android/check.py:131`)、`template_problems`(`check.py:289`)、`message_problems`(`check.py:315`)。這是同模組裡第一個靠改傳入參數回報的函式,結構沒錯,但跟既有慣例不一致。
另外,重複編號時,獨立呼叫 `main_rows()` 的結果從「先到先贏」(原本的 `setdefault`)變成「後到為準」。docstring 有寫,但沒有測試鎖住這個語意。

F2
severity: minor
blocking: 否
引句:「check(f"S1 圍欄判定跟 lumos 一致:{name}", mine == theirs」
比對測試只有 11 組手寫案例,而且只比 `_visible_lines`(`keep_fenced=False`)。`_fence_regions(lines, strict)` 這個函式本身沒有跟 `scripts/lumos:5369` 直接比對,測試端的 `_kt_kotlin_blocks` 卻直接呼叫它(`strict=True`)。
lumos 自己在抽出共用原語時,是用大量隨機輸入證明新舊零差異(`scripts/test_lumos.py:13888` 附近的註記)。這裡守的是兩份獨立的實作,口徑上弱了一階。結構對,但守衛強度不如既有先例。

**③ 第二種做法**

F3
severity: minor
blocking: 否
引句:「if j in visible and lines[j].startswith("## "):」
`_kt_template_sections` 的「組」起點改走 check.py 的 `template_sections`,但組的終點和小節切分仍在測試端自己判斷(`startswith("## ")`、`startswith("### ")`)。`_kt_kotlin_blocks` 判斷是不是 kotlin 圍欄,也是測試端自己 `lstrip("`~").startswith("kotlin")`。
標題規則被拆在兩處:check.py 的 `TEMPLATE_HEADING_RE` 只認 `## T<n>`,測試端卻把任何 `## ` 都當作組的終點。目前行為相容,r2 點名的三項(主表、批次值、組起點)也確實收斂了。但這是同一份範本檔結構的第二種切法,以後標題規則一改就可能漂移。

F4 ⚠ 交編排者
severity: minor
blocking: 否
引句:「scripts/lumos 沒有 .py 副檔名,不能 import 借用」
這句理由只說明了 check.py 執行時不能借用,但同一個補丁的測試端正是用 `_load_lumos_module` 的 SourceFileLoader 載入它。複本成立與否,取決於 check.py 在消費專案或 CI 裡能不能拿到 scripts/lumos。這點我沒在 repo 裡找到明確依據,需要編排者確認。若 check.py 一定與 scripts/lumos 同 repo 執行,這份複本的存在理由就變弱了。

不對齊共 4 條,其中會擋的 0 條
