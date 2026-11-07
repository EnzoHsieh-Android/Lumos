severity: minor

F1 缺節訊息與 S2 內容檢查歸位已照 r1 方向修好。F2 標準文件指路句也已改成既有格式。這輪新抽出的函式與圍欄比對都重用既有判定,只有幾處寫法不齊。

**① 模組邊界**

沒有跨層直呼,也沒有放錯地方。
- 範本與型錄的改動仍在 `skills/kotlin-idioms/`,標準文件只動指路句。
- 內容檢查與資料測試都留在 `scripts/test_lumos.py`,跟 `_kt_turbine_problems` 同層。
- `check.py` 在這個 patch 裡沒被碰。
- 新抽出的 `_kt_ui39_problems(rows, io)` 吃的是 `m.main_rows()` 的列與〈輸入與口徑〉內文,沒有另寫型錄讀法。這跟既有 `t_kotlin_catalog_c_rows_batch_resolved` 的做法一致(`scripts/test_lumos.py:127030` 一帶「主表與批次值的讀法都呼叫 check.py」)。
- r1 F1 後半已照方向修。後半 S2 的內容檢查與整組改壞案例,從 `t_kotlin_test_templates_sections`(`scripts/test_lumos.py:126476`,[S1] 型錄自檢)搬進 `t_kotlin_test_templates_content_guards`(同檔 126810)。

引句:「# 後半 S2:儀器批與架構測試的內容檢查,真檔零問題,逐道改壞各自報(代碼審 r1 架構對齊 F1:從」

**② 命名與錯誤處理**

r1 F1 前半已修,錯誤處理的形狀一致,只有兩處小不齊。
- 缺節訊息改成「範本檔沒有 {g} 節」,跟 `configs/ast-grep/kotlin-android/check.py:312` 的「範本檔沒有 {g} 節」同一句。
- `_kt_ui39_problems` 回傳問題字串清單,跟 `_kt_instr_template_problems`、`_kt_turbine_problems` 同形。
- 改壞案例用「改壞真的改到」先驗證、再驗報錯,對照既有 `_in_t12_fence` 的「沒改到就丟 AssertionError」,做法一致。

**F1**
severity: minor
blocking: 否
引句:「n_real = len(_re.findall(r"@Test\b", "\n".join(_kt_kotlin_blocks(m, t9.get("測試", "")))))」
`_kt_instr_wording_problems`(`scripts/test_lumos.py:126967`)已經用 `_kt_template_sections` 切出 `groups`,後面又改用 `text.split("\n## ", 1)[0]`、`text.index("\n## T9 ")`、`text.index("\n## T11 ")` 加 `.index("\n### ")` 手切字串(126971、126976–126977、126985–126986)。
這幾條不看圍欄,而同一組檔案裡 `_kt_template_sections`(126631)與 `_kt_instr_template_problems` 都是「圍欄裡的不算」。
T9 開頭、T11 開頭的字串可以直接取自 `groups["T9"]`、`groups["T11"]`,或沿用 `m._visible_lines`。
結構是同一層,只是切法沒跟既有口徑一致,所以判 minor。
另外 `__import__("re").sub(...)`(126997)夾在已有 `_re` 的檔案裡,檔內其他幾處也有這種寫法,不算新增。

**F2**
severity: minor
blocking: 否
引句:「lang = seg[a0].lstrip(" ").lstrip("`~").strip()」
這行判圍欄語言的運算式,既有 `_kt_kotlin_blocks`(`scripts/test_lumos.py:126652`)已經有(`.lstrip(" ").lstrip("`~").startswith("kotlin")`)。
patch 在 `_kt_instr_template_problems`(126792)與測試內的 `_in_t12_fence`(126887)又各寫一份。
三處的比對方式還不同:這處用 `lang in fenced`(整字相等),`_in_t12_fence` 用 `startswith(lang)`,`_kt_kotlin_blocks` 也是 `startswith`。
`_fence_regions` 本身有重用,沒另起圍欄判定;只是語言標籤的取法被複製。
把 `_kt_kotlin_blocks` 一般化成「取某語言圍欄內容」可以收成一份,所以判 minor。

**③ 第二種做法**

沒有另起一套圍欄解析。
- 圍欄內比對 key=value 的寫法,是呼叫 `m._fence_regions(seg, True)` 取區段,再逐行 `strip()` 比整行相等。區段來源與 `_kt_kotlin_blocks` 同一條路,不是另寫的正則或配對。
- `_kt_ui39_problems`、`_kt_instr_wording_problems` 都沿用既有的資料測試路徑:`m.main_rows`、`_kt_template_sections`、`_kt_kotlin_blocks`。
- 唯一偏離口徑的是上面 F1 的手切字串,以及 F2 重複抄的語言標籤取法。這兩處都不改變判定的結果,只是同一件事有兩種寫法。

引句:「for a0, b0 in m._fence_regions(seg, True)[0]:」

r1 F2 已照方向修好。`skills/lumos-project-notes/commands/test-quality-standard.md:157` 現在是「照抄起手:…(T7–T11 節;…照該檔〈Android 實驗專案骨架〉節)」,跟同檔 147、155 的格式同型。`sdk=34` 與 `robolectric.properties` 的細節已不在標準文件裡,只指到骨架節,兩處維護的問題解掉了。
測試也跟著改成斷言「照抄起手:」加「(T7–T11 節」,並檢查沒重抄 `sdk=34`。

引句:「- 照抄起手:要 Android 框架的測試(Fragment、LiveData、WorkManager、Compose、Paging)的範本在」

不對齊共 2 條,其中會擋的 0 條。
