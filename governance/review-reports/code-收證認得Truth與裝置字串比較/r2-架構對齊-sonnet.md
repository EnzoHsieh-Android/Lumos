severity: major

**1. 分層與依賴方向:對齊(沒有跨層直呼)**
- 判定邏輯仍只放在 `assertion_failure` 同一個函式的同一條 `if not kind` 分支。這個函式共用的兩個消費端,收證與安全證據閘,沿用原來的呼叫路徑。`scripts/lumos` 只換了指紋表一個雜湊值。
- 我用 sha256 驗過這個雜湊跟修後的 `test_quality.py` 一致,不是殘留值。這做法跟計劃寫的「改了 test_quality.py 要一併更新指紋表」相同。
  - file: `scripts/test_quality.py:111-145`
  - file: `scripts/lumos:69691`
- 安全證據閘的新測試沒有繞過閘本身。它沿用 `_sg_junit` 的狀態表(新增 `failure_truth`),`capture` 裡的對應表照 `failure_rt` 的寫法擴充,走原有的 `_SgRepo`、`_sg_eval`、`_sg_kind`。
  - file: `scripts/test_lumos.py:113846-113990`
  - file: `scripts/test_lumos.py:114399-114430`
- 筆記的歸屬也對:收證歸因的 PITFALL 放在 `Systems/test-quality-cli.md`(收證工具的家),沒有把別人的檔路徑寫進去。
  - file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:40`

**2. 命名與錯誤處理**

不對齊 A:新增的測試函式前綴跟鄰居兩個家族都不同。
- 安全證據閘鄰居用 `t_secev_sNN_*`(NN 是安全證據閘計劃自己的條款號)或 `t_secev_r1_*`。新的 `t_secev_drill_s5_*` 是演練計劃的 S5,跟既有的 `t_secev_s05_junit_invalid_shapes` 號碼容易撞義。
  - file: `scripts/test_lumos.py:114335`
  - file: `scripts/test_lumos.py:117090`
- 測試品質家族鄰居全是 `t_test_quality_*`,新的 `t_drill_quality_cli_cases_present` 另起 `t_drill_` 前綴。
  - 引句:「def t_drill_quality_cli_cases_present():」
  - 對照:`t_test_quality_standard_android_drill_lessons`(file: `scripts/test_lumos.py:120127`)
- 結構(`t_` 開頭自動收、docstring 寫「守的錯／翻紅釘」)跟 `drill_lessons` 一致,只有名字不齊。

severity: minor

不對齊 B:`test_quality.py` 的註解沒跟著名單更新。
- 「Measured Truth 1.0.1 local JVM type attribute…」這句只講 Truth,但同一個 tuple 現在多了 JUnit 的 `org.junit.internal.ArrayComparisonFailure`。這個型別沒有「Measured」註記,筆記說它來自本機報告。鄰居每個型別分支都有一句來源註解。
  - 引句:「# Measured Truth 1.0.1 local JVM type attribute; device XML from AGP has no」
  - file: `scripts/test_quality.py:115-118`

severity: minor

不對齊 C:回頭條件的寫法跟 CLAUDE.md 鐵則 4 與鄰居計劃不同。
- 三行 `REVISIT:2026-12-15 …` 的格式對,但掛在〈卷證放哪〉標題底下,講的卻是 Semgrep、其他語言 runner、裝置類別篩選。鄰居的 REVISIT 緊貼它所屬的段落。
  - file: `docs/lumos-toolchain-knowledge/Projects/Android單元測試標準實機演練_計劃.md:82-89`
- 另有幾句承認風險的散文沒拆成 REVISIT 行,鐵則 4 要求拆。
  - 引句:「這批沒動,排進下一份計劃查」
    - file: `docs/lumos-toolchain-knowledge/Verification/2026-11-01_Android單元測試標準實機演練.md:88`
  - Verification 第 87 行「收據是演練當時工作樹版本…判定可能因為裝置規則收窄而不同」。
  - 計劃「實務隱患」對外送出那條的「沒有查網路流量,不能排除」。
    - file: `docs/lumos-toolchain-knowledge/Projects/Android單元測試標準實機演練_計劃.md:110`
- 其餘格式對齊鄰居:
  - PITFALL 帶出處、根因、防回歸三欄。
  - WHY 帶出處、因、不選、代價、applies。
  - RETIRE-IF 帶 `[retire:人裁] [until:]`,同款寫法見 file: `docs/lumos-toolchain-knowledge/Projects/Android本機單元測試驗收標準_計劃.md:30`。
  - 審計修正紀錄用「代碼審 r1(…)」,跟 file: `docs/lumos-toolchain-knowledge/Projects/代碼審資安席_計劃.md:148` 同形。

severity: minor

**3. 第二種做法:有一處**

不對齊 D:公開 repo 只放去識別化摘要,能重跑的完整卷證留在考場私有分支,這是專案原本沒有的歸檔做法。
- 計劃自己也承認,並用 WHY、`[applies:]`、`[retire:人裁][until:2027-11-01]` 圍起來,這是使用者拍板的決定。
  - 引句:「這是專案原本沒有的歸檔做法,適用條件與撤除條件見下面〈卷證放哪〉。」
  - 引句:「## 卷證放哪(這次新增的做法)」
  - file: `docs/lumos-toolchain-knowledge/Projects/Android單元測試標準實機演練_計劃.md:79-85`
- 對照:上一次原生收證是全放公開 repo(file: `governance/eval/results/test-quality-native-consumers-20261008`)。
- 依嚴重度錨,「引入第二種做法」判 major。它有 WHY 與撤除條件、也是人裁,⚠ 交編排者決定是否以理由接受。
- 這條修補前就在,這輪只是補上 WHY 與撤除條件。

severity: major

- `t_drill_quality_cli_cases_present` 用文字比對檢查測試檔裡有沒有指定的方法名,這個守衛手法專案裡沒有先例。它跟 `drill_lessons`(用文字比對檢查標準)同一類,所以我只算在命名那條,不另列為第二種做法。
- 其他新寫法都有先例:
  - 回歸測試的做法照 `test_runtime_exception_mentioning_truth_type_is_not_attributed`。
  - 單調時鐘計時的大輸入測試,`test_test_quality_cli.py` 已有同款(例如 file: `scripts/test_test_quality_cli.py:521`)。
  - `re.compile(...).search(text, pos)` 是為了用起點參數,仍在同一函式內,不算新機制。

**修補三問**
- ① 上一輪指出的四項現況:
  - 筆記小節缺綁定:已補。Systems 的「實機演練之後同一節補了…」那句現在帶「綁的測試 `t_test_quality_standard_android_drill_lessons`」,跟同節 `unit_section` 的寫法一致(file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:84`)。
  - 標準連結位置:已修。修前的內文行內連結(`[kotlinx-coroutines-test 說明](…)`)改成純文字,連結收進節尾「來源」行,跟 Room 與前端節一致(file: `skills/lumos-project-notes/commands/test-quality-standard.md:124` 與 `:153`)。
  - 卷證檔名:公開卷證目錄 `android-unit-standard-drill-20261101` 是英數加日期,跟 `test-quality-native-consumers-20261008` 同形,席報告資料夾仍是 `<迴圈名>/r<N>-<席>-<模型>.md`。
  - 新測試名前綴:修前沒有這幾支新測試,只有名字對得上家族的 `drill_lessons`,所以我無法比較修前修後。修後新加的三支屬於不對齊 A。
- ② 既有寫法有沒有被弄亂:沒有。`assertion_failure` 其他分支原樣,`drill_lessons` 的檢查詞只換成更精確的字串,`_sg_junit` 是擴充狀態表。
- ③ 新發現的修前修後:
  - A、B、D:修前沒有對應物,是修補引入的。D 的底下做法修前就在,修補把它補上 WHY 與撤除條件。
  - C:修前計劃沒有這幾行 REVISIT 與延伸文字,是修補新增的。

不對齊共 4 條,其中 major 1 條
