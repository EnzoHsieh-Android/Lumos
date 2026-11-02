severity: minor

審查範圍:`r2-snapshot.patch` 全部,加上 `r2-repair.patch`(修前 e7c5a0d55 → 修後 9ddf8f796)。鄰居檔我是實際打開比對的。我沒開 r1- 開頭的任何檔。

## 問 1:分層與依賴方向

**對齊。** 這份 diff 沒有跨層直呼,新碼放的位置也跟鄰居一樣。

- **新測試**
  - 三支 Kotlin 測試放在 `scripts/test_lumos.py:65477` 一帶,都透過 `_load_lumos_inproc()`(`scripts/test_lumos.py:238`)讀 `_STACK_QUESTION_SPECS`,或直接讀文件。這跟 `t_arch_target_ddd_template_valid`(`scripts/test_lumos.py:15465`)、`t_tension_doc_sync` 是同一種做法,沒有繞過公開入口去動 `scripts/lumos` 內部。
  - Android 單元節的測試緊貼 `t_test_quality_standard_android_room_section`(`scripts/test_lumos.py:120024`)。
- **修補後的守門**
  - 修補把自寫的 `raise _SrcOnly(...)` 全換成共用的 `_need_src`(`scripts/test_lumos.py:146`),跟全檔約 20 處用法一致。
  - 修補前 `_kotlin_idioms_text` 自己寫 `is_file()` 加 `_SrcOnly`,那是第二種寫法;現在收斂了。
  - `GRAPHCTL` 在 `scripts/test_lumos.py:30` 就已經 `resolve()`,所以 `_kotlin_idioms_text` 少寫 `.resolve()` 不影響行為。
- **審查題**
  - `kt-flow`、`kt-leaks` 的 id 沒動,只改措辭,符合 `效能檢核目錄.md` 的「改措辭不改 id」規則。
  - 目錄那一列也同步改了(雙向同步義務)。
  - 題裡引用「idioms R19」「idioms R20」的寫法,跟既有的「idioms R5」(`scripts/lumos` 的 kt-flow 題)一樣。
- **手冊**
  - 新增「五、Android 特有(只有 Android 專案適用)」,對照 `skills/java-idioms/SKILL.md:174` 的「六、Android 特有(只有 Android 專案適用)」,標題形式相同。
  - 條款格式(`### Rn.` 標題、`- 機檢:`、`- 依據:`)跟 `skills/kotlin-idioms/SKILL.md` 的 R1–R18 與 `skills/swift-idioms/SKILL.md:40-65` 一致。
  - 審查鏡頭條號範圍 R1–R18 改成 R1–R22,並有測試釘住。
- **圖譜筆記**
  - 計劃筆記的 frontmatter、「審計修正紀錄」段,跟 `Projects/Room資料庫測試守衛_計劃.md:175` 一致。
  - Verification 筆記的欄位、`test-quality-cli.md` 新增一節的寫法,也都跟鄰居一致。

## 問 2:命名與錯誤處理

**大致對齊,一處不對齊(B1)。**

- **測試命名**:`t_kt_*`、`t_kotlin_idioms_*`、`t_test_quality_standard_android_unit_section` 是 `t_` 加蛇形,跟全檔一致。
- **收尾輸出**:`print("  ✓ t_...")` 放在結尾,跟 DDD 與張力那幾支一致。Room 那支把 `print` 放在開頭,但全檔兩種都有。
- **外部工具缺失**:修補後 detekt 不存在時,印 `⚠ 這台沒有 detekt,…沒驗到` 然後 `return`,跟 `scripts/test_lumos.py:25583-25586` 的 dart 真機段逐字同形。修補前的版本沒有這個明顯對照,現在對齊。
- **暫存目錄與別名**:`import re as _re, shutil as _sh, subprocess as _sp, tempfile as _tf` 跟 `scripts/test_lumos.py:86553` 一帶一致。`mkdtemp(prefix="lumos-kt-idioms-detekt-")` 沒有用 `gctl-` 前綴(`gctl-` 約 755 處,其他前綴約 110 處)。這不是硬規則,不計條。
- **檢查函式**:全部用 `check(...)`,沒有自己發明斷言方式。

**B1(minor):新節的「上一節」指錯對象。**
- 既有:兄弟節的交叉參照指向真正的相鄰節。
  - Room 節在 `skills/lumos-project-notes/commands/test-quality-standard.md:66`。
  - 原生收證節在同檔 `:84`。
  - 新節在 `:100`,它的上一節是原生收證,不是 Room。
- 這次:新節同一段裡,「上一節」同時指兩個不同的節。
  - 「收證照上一節:用 `lumos test-quality capture`」指原生收證節,正確。
  - 「資料庫照上一節〈Android 資料層(Room)〉」和「Room 不用 Robolectric 跑(上一節)」指的是往上兩節的 Room,這兩處不對。
  - 計劃筆記「做法」第 1 點也寫「Room 照上一節」,同樣錯。
- 修補沒有發現這個問題。修補只加了單源指向,新節位置沒變。
- 不一致:1 檔(`test-quality-standard.md`),另有計劃筆記同一句。
- 結構本身是對的:新節插在原生收證之後,是計劃裡 Enzo 選的位置,測試也釘了這個位置。
- 修法是把兩處「上一節」改成「前面的〈Android 資料層(Room)〉節」。

引句:「資料庫照上一節〈Android 資料層(Room)〉」
對照:`skills/lumos-project-notes/commands/test-quality-standard.md:66`(Room 節實際位置)
severity: minor
blocking: no

## 問 3:第二種做法

**沒有引入第二種做法。** 我逐項查過:

- **detekt 實跑測試**
  - 專案原本就有「外部工具在才跑,不在就印沒驗到」的慣例(dart `scripts/test_lumos.py:25583`,另有 `ruff`、`claude`、`java` 等)。這次是同一個慣例。
  - 修補後 docstring 還明寫「_SrcOnly 專指缺來源 repo 的產物,不拿來表示缺外部工具」,與該慣例的區分一致。
- **守門**:全部走共用的 `_need_src`,修補已消除自寫的 `_SrcOnly` 判斷。
- **斷言形狀**:S4 改成斷言退出碼 2 加命中行 `A.kt:7`,仍是 `check()`,沒有引入新的斷言工具或新的外部依賴。
- **審查題**:沒有新增題 id,也沒有改 `when` 觸發字。S2 用 `_KT_LEAKS_WHEN_BEFORE` 釘住不變,這跟 `t_stack_question_triggers` 釘整張表的作法同方向。
- **手冊**:「要型別資訊」的說明段、機檢欄附註,沿用既有的「機檢欄說明」格式,沒有另立標記系統。

## 修訂輪另核對

修補本身只引入 B1 那一類既有缺口,沒有自己新增不一致:

- **`_need_src` 替換**:四處都改完,新舊寫法沒有並存。
- **S4 修補**:docstring、`check` 文字、Verification 筆記「代碼審 r1 之後」段三處說法一致(退出碼 2、`[GlobalCoroutineUsage]`、少一個右大括號會紅)。
- **R22 補上 `UnconfinedTestDispatcher(testScheduler)`**:跟新節「Flow」那條的寫法逐字同形。
- **R19–R22 的 `⚠ 不可機檢` 與 `- 機檢:` 並用**:既有手冊兩種並存(R7 只有機檢行,R8 只有標題),不算不一致。

不對齊共 1 條,其中 major 0 條
