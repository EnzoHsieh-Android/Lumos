severity: minor

**① 模組邊界**

沒有放錯地方,也沒有跨層直呼。

- 範本本體寫在 `skills/kotlin-idioms/test-templates.md`。
- 型錄欄值改在 `skills/kotlin-idioms/checks-catalog.md`。
- 標準文件只放指路句。
- 內容檢查和資料測試都留在 `scripts/test_lumos.py`,跟 T0–T5 的 `_kt_turbine_problems`、`t_kotlin_test_templates_content_guards` 同一層。
- `check.py` 沒被改動:`TEMPLATE_HEADING_RE`(`configs/ast-grep/kotlin-android/check.py:206`)的 `T\d+` 已涵蓋 T10–T13,`template_problems`(同檔 289)只管「指得到那一節」,範本內容的對錯本來就不在它管轄內。
- 新的 `_kt_instr_template_problems` 切節時直接呼叫 `m.template_sections` 與 `m._visible_lines`,沒有另寫圍欄判定。

引句:「groups = _kt_template_sections(m, text)」

對照:`scripts/test_lumos.py:126670`(`_kt_template_sections` 既有的切法)、`configs/ast-grep/kotlin-android/check.py:279`。

**② 命名與錯誤處理**

結構一致,有兩處措辭不齊。

- 章節編號 `## T6`~`## T13`、欄值「範本 T<n>」、「未接(儀器批)」、「不接(代碼審或真機)」、測試名 `t_kotlin_*`,都沿用既有格式。
- 每節的小節順序是〈依據〉〈依賴〉〈測試〉〈假依賴〉〈好寫法〉〈壞寫法〉〈紅綠矩陣〉,跟 T1–T5 相同(範本乙、丙 patch 的 `+### 依據` 到 `+### 紅綠矩陣`),「跑在哪」也寫在節開頭,跟 T4 開頭的寫法同型。
- 作廢值用 `_KT_RETIRED_VALUES` 逐值斷言不再出現,是既有「不再出現批五」那種斷言的延伸。

**F1**
severity: minor
blocking: 否
引句:「probs.append(f"沒有 ## {g} 那一節")」
範本缺節的訊息在既有的 `template_problems` 是「範本檔沒有 T<n> 節」(`configs/ast-grep/kotlin-android/check.py:312`)。新寫成「沒有 ## T<n> 那一節」,同一件事兩種說法。
另外,測試 `scripts/test_lumos.py:126476`(`t_kotlin_test_templates_sections`,docstring 標 `[S1] 型錄自檢`)裡新塞進「後半 S2」的內容檢查,按既有分工應放進 `t_kotlin_test_templates_content_guards`(同檔 126829)。

**F2**
severity: minor
blocking: 否
引句:「- **要 Android 框架的測試**(Fragment、LiveData、WorkManager、Compose、Paging):先看 `skills/kotlin-idioms/test-templates.md` 的範本 T7–T11」
`test-quality-standard.md` 既有的指路句是「照抄起手:<情境>的測試範本在 `…test-templates.md`(Tx 節)」,在 `skills/lumos-project-notes/commands/test-quality-standard.md:147` 與 155。
新句改成獨立粗體條目,措辭不同,還把 `robolectric.properties` 的 `sdk=34` 釘法寫進標準文件。這段細節在範本〈Android 實驗專案骨架〉已有,等於兩處維護。

**③ 第二種做法**

沒有第二種做法。

- 沒有新增解析範本或型錄的方式,型錄值仍走 `m.main_rows()`、`m.behavior_value`,範本節仍走 `m.template_sections`。
- 新章節格式跟 T1–T5 相同。
- 新增的〈Android 實驗專案骨架〉與既有的〈實驗專案骨架〉(`skills/kotlin-idioms/test-templates.md:23`、56)並列,是因為純 JVM 骨架撐不起 Android 組,屬於不同堆疊的第二份骨架。
- 骨架節的必有字(`sdk=34`、`targetSdk = 36`、`testInstrumentationRunner`)用「`## ` 標題到下一個可見標題」手切,是因為它不是 T<n> 組,`template_sections` 切不到,不算另一套解析。

引句:「vis_set = {no - 1 for no, _ln in m._visible_lines(lines)}」

不對齊共 2 條,其中會擋的 0 條。
