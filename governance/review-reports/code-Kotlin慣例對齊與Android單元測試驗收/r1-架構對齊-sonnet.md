severity: minor

我只讀了 patch 和鄰居檔,沒有跑測試。這份報告沒有「[目標架構]」段,所以全部照「比鄰居」判。

## 1. 分層與依賴方向:大致對齊,有一處守門方式不同

**對齊的部分:**
- **載入 lumos 模組:** 新測試用 `_load_lumos_inproc()` 載入。鄰居 `t_dart_profile_discovery`、`t_java_*` 的取題也是這樣載(`scripts/test_lumos.py:37032`、`:37090`)。
- **取檔路徑:** `Path(GRAPHCTL).parent.parent / "skills" / ...`。`GRAPHCTL` 在 `scripts/test_lumos.py:30` 已經 resolve 過,和鄰居 `t_test_quality_standard_android_room_section`(`:120019`)寫法等價。
- **外部工具不在時:**
  - `t_kotlin_idioms_detekt_snippet_runs` 沒裝 detekt 就印「⚠ 這台沒有 detekt…沒驗到」後 `return`。
  - 這和 `scripts/test_lumos.py:25583` 的 dart 寫法一字形一致。
  - 臨時目錄也是 `mkdtemp` 加 `finally: rmtree`。
- **新文件小節的位置:**
  - 單元測試驗收標準放在原生收證節之後,是 Enzo 選的。
  - 圖譜記一行放在 `Systems/test-quality-cli.md` 的 Room 節之後,標題格式和鄰居一致。
  - 審查題只改 `scripts/lumos` 的 `q` 字串,id 和 `when` 不動,沒有跨層直呼。

**不對齊:** 見 A1。

## 2. 命名與錯誤處理:大致對齊,有三處小差異

**對齊的部分:**
- 測試命名 `t_` 加底線,和鄰居一致。
- docstring 的 `[S1]` 條款釘:本檔約 746 處用這個形式,對照 `"""[Projects/…` 約 17 處。
- docstring 的「翻紅釘:」寫法和鄰居一致。
- check 訊息的「前置:」用法,本檔約 136 處用同樣寫法。
- 結尾 `print("  ✓ t_…")` 和 `print("t_…")` 開頭印在本檔兩種都有(約 429 對 634),不算偏離。
- 手冊機檢欄把「要型別資訊」併進括號,沿用既有 `（預設開）` 的形式。

**不對齊:** 見 A1、A2、A3。

## 3. 第二種做法:沒有 major

- **沒有新讀檔工具,也沒有另一套略過測試的方式。**
  - 略過一律是 `_SrcOnly`,沒有發明新例外或旗標。
  - 找審查題用的模組級 `_kt_question` 只是 `next(...)`。
  - 鄰居自己就有三種寫法:`:36860` 的行內 `next`、`:37032` 的區域 lambda、`:52182` 的 list-comp。鄰居本身不一致,這個我不計(⚠ 不硬判)。
- **`_KT_LEAKS_WHEN_BEFORE` 是字面清單釘觸發字。** 這和 `t_stack_question_triggers`(`:64550`)用字面集合釘 id 是同一種做法,不算第二種。
- **新增的四支 `t_kt_*` 測試插在 `t_tension_lens_and_gov` 和 `t_tension_doc_sync` 之間。**
  - 同棧鄰居在 `:64503`、`:64550`(Kotlin 題觸發)和 `:111087` 以後。
  - 這只是放哪裡的差別,不影響結構,我不計。

## Findings

**A1 守門的做法和鄰居不同(測試)**
- **既有:** 檔案存在性的守門有現成的 `_need_src(*rels)`(`scripts/test_lumos.py:146`,全檔約 193 處呼叫),並且守門放在函式最前面。例子是 `t_prepush_room_guard_wired`。
- **這次:** 三處自己手寫 `is_file()` 再 `raise _SrcOnly`,全是 `_need_src` 剛好能涵蓋的情形:
  - `_kotlin_idioms_text` 手寫。
  - `t_kt_flow_question_events_as_state` 在做完 Flow 題的 check 之後才檢查目錄檔,最後才 `raise _SrcOnly`,所以守門在函式中段,不在最前。
  - `t_test_quality_standard_android_unit_section` 手寫。
- **不一致:** 3 檔處(同一檔 `scripts/test_lumos.py` 內 3 個函式)。
- 鄰居 `t_tension_doc_sync`(`:65570`)也是手寫 `exists()` 加 `raise _SrcOnly`,所以專案內本來就有兩種。這條是「結構對、做法偏少數」,不到第二種做法。
- 引句:「raise _SrcOnly("消費端沒有來源圖譜,效能檢核目錄那一列沒驗到")」
severity: minor
- blocking: no

**A2 手冊新小節的標題與依據寫法和鄰居不同(`kotlin-idioms`)**
- **既有:**
  - `skills/java-idioms/SKILL.md:174` 的 Android 專屬節寫成「## 六、Android 特有（只有 Android 專案適用）」,節標題帶適用範圍。
  - 節標題不帶日期。日期寫在條款正文裡,例如 `skills/kotlin-idioms/SKILL.md:117` 的 R15。
  - 依據是每條自己一行 `- 依據：[…](url)`(`:42`、`:53`、`:80`、`:119`)。
- **這次:**
  - 標題寫成「五、Android 官方架構建議（2026-11-01 補）」,日期放標題,沒有「只有 Android 適用」。
  - 「R1–R22 逐條掃」這句照所有 Kotlin 審查生效,而 Kotlin 題組另有 Spring 後端(`kt-springdata`)。
  - R19 到 R22 的依據只在節首統一寫一次(R22 另有行內連結),沒有逐條的 `- 依據：` 行。
- **不一致:** 1 檔(`skills/kotlin-idioms/SKILL.md`,對照 `skills/java-idioms/SKILL.md`)。
- 引句:「## 五、Android 官方架構建議（2026-11-01 補）」
severity: minor
- blocking: no

**A3 測試品質標準新小節少了單源指標**
- **既有:** 兩個兄弟節開頭都標明單源計劃:
  - 〈網頁前端〉:`單源=[[Projects/前端知識與風險詞_計劃]] 做法 8`(`skills/lumos-project-notes/commands/test-quality-standard.md:56`)。
  - 〈Android 資料層(Room)〉:`單源=[[Projects/Room資料庫測試守衛_計劃]]`(`:68`)。
- **這次:** 〈Android 本機單元測試的驗收標準〉開頭沒有單源指標,只寫「官方條目 2026-11-01 核對」。
- **不一致:** 1 檔(`skills/lumos-project-notes/commands/test-quality-standard.md`)。
- 引句:「沿共用規範驗需求答案與相關故障。這一節講跑在電腦 JVM 上的本機單元測試」
severity: minor
- blocking: no

不對齊共 3 條,其中 major 0 條。

主要檔案:
- `/Users/enzo/harness/lumos-android-ui-events/scripts/test_lumos.py`
- `/Users/enzo/harness/lumos-android-ui-events/skills/kotlin-idioms/SKILL.md`
- `/Users/enzo/harness/lumos-android-ui-events/skills/lumos-project-notes/commands/test-quality-standard.md`
