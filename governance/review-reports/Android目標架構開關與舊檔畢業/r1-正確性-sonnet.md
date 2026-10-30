severity: major

審的是 `r1-snapshot.md`。已核對的現況假設:`arch_targets` 只認 `path` 與 `node`、第一段必須是寫死的資料夾名、派工鏡頭宣告上限 500 條、推送前風險分級沒有上限、`_VENDORED_TREE_FILES` 逐檔登記。內部交叉引用 `[[Projects/架構對齊可宣告目標架構_計劃]]`、`[[Projects/Android的MVVM與DDD目標架構範本_計劃]]`、`[[Systems/arch-alignment-lens]]` 目標都存在。

## Finding

**F1(「最小解」第 3 點、〈開關〉`legacy` 列)**
severity: major
blocking: 是——legacy=dirs 產出的 Konsist 測試會掃到範圍外的舊碼,產出的組合本身就會紅。
- 問題:第 3 點說 Konsist「讀同一份 config 的 none 宣告跳過舊檔」。`dirs` 模式只有目標宣告、沒有 none,所以測試無從排除目錄外的舊碼。`legacy=all` 的單條宣告範圍與測試用的根套件也沒有對應關係。
- 引句:「Konsist 測試讀同一份 `.lumos/config.json` 的 none 宣告跳過舊檔,不另存清單。」
- 例:`legacy=dirs`、指定目錄 `app/src/main/java/com/x/feature/new`,範圍外 `.../legacy/` 有舊碼違規。輸入是 dirs 模式的產出。預期是範圍外照鄰居審、Konsist 不碰。實際是宣告沒有 none,測試依 `$appRoot.domain..` 套件掃全專案,範圍外舊碼讓測試紅。
- 參照:現行骨架 `skills/lumos-project-notes/commands/target-arch-android-template.md:176` 的過濾條件是名稱與套件,不看宣告。

**F2(「最小解」第 3 點)**
severity: major
blocking: 是——舊碼和新碼混著的專案裡,規則 3 的測試會靜默變綠。
- 問題:若「跳過舊檔」是先把 none 檔從 `scope` 濾掉,`aggregatesReferenceOthersByIdOnly` 的 `rootNames` 就只含新檔的聚合根。
- 例:新聚合根 `Order` 持有舊檔聚合根 `Customer` 物件。預期是違反「聚合之間只用識別碼」而紅。實際是 `Customer` 在 none 檔裡不進 `rootNames`,`others` 缺它,測試綠。
- 參照:骨架 `target-arch-android-template.md:219-232`(`val roots = scope.classes().filter{...}`、`rootNames`、`others`)。spec 沒說只過濾被檢查的檔、還是整個 scope。

**F3(「最小解」第 4 點、S5、S6、「舊否決對照」)**
severity: major
blocking: 是——畢業的範圍定義前後矛盾,放行範圍和 S6 的說明句無法同時成立。
- 問題:判定以單檔為單位:起點 none、頂端判成起點版就有的目標節點。但第 44 行說「新增宣告、改節點、刪目標宣告都照舊」,畢業只開「刪 none 行」這一個口。S5 沒排除在 none 行前面新增、或調序出一條起點版已有的目標節點宣告。
- 引句:「範圍因此只開一個口:起點判 none、頂端改判成起點版本就有的目標節點;規則原文照讀起點版,新增宣告、改節點、刪目標宣告都照舊。」
- 例 1(整批畢業):起點 `[Old1.kt none, Old2.kt none, app/** → Systems/A]`。頂端在最前面加 `app/legacy/** → Systems/A`。判定上全部 legacy 檔畢業,但沒有任何 none 行被刪。S6 的「只有畢業(刪掉 none 行)」無法歸類它:算「其他宣告改動」就兩句都印,算畢業就只印「已照目標審」。
- 例 2(逃審):起點另有一個目標節點 `Systems/B`,它沒有有效 RULE 行(doctor 判「照鄰居」)或規則很鬆。頂端把 `Old1.kt` 改判到 B 就算畢業。
  - 預期:Old1.kt 照鄰居審,至少受 A 的規則約束。
  - 實際:`_arch_alignment_hints` 對 `in_target` 的檔不找鄰居(`scripts/lumos:57688,57694`),B 又沒規則可附(`_ARCH_TARGET_TAIL_NONE` 只要求審查員自己開筆記)。這支檔等於兩邊都沒審到。
  - 這正是 RETIRE-IF 第二條要防的情形,但判準沒有「同一個目標節點」的限制。
- 判準應綁在「刪掉的是 none 行、而且該檔改判後落在原本接在後面的那條目標宣告」,不能只看節點名是否出現在起點版。

**F4(S5、「回退」)**
severity: minor
blocking: 否——只是 S5 的條件沒寫全,實作時會各自補洞。
- 問題:S5 沒定義 `_trusted_decl_ref` 回 None 或退回起點本身時畢業怎麼判。
  - 沒有主線:推送前分級讀起點本身(`no_mainline_reads_base=True`,`scripts/lumos:57387-57394`),派工鏡頭 `ref is None` 就完全不附目標段(`scripts/lumos:63862-63865`)。
  - 無共同祖先、git 失敗:只回說明,沒有可信起點版。
- 例:專案沒有本地 main。推送前分級把畢業檔放進目標節點,派工鏡頭卻不附規則。畢業檔「照目標審」但審查席看不到規則,又沒有鄰居可比。
- 缺口:S5 只寫了「頂端宣告讀不懂」,沒寫「起點版讀不到」。

**F5(S6、`_arch_target_check_lines`)**
severity: minor
blocking: 否——說明句會有一個漏印情形,不影響審查本身。
- 問題:現行 `changed` 有兩個來源:宣告不同、或範圍內改到了目標節點筆記(`scripts/lumos:57644-57654`)。S6 只談宣告改動。
- 引句:「當這段範圍的宣告改動只有畢業(刪掉 none 行)時,代碼審判定印的說明應寫這幾支檔本次已照目標審,不應印「下次推送才生效」」
- 例:同一範圍既刪 none 行又改了目標節點的 RULE 行。規則原文仍讀起點版。預期是「下次推送才生效」要印。照 S6 寫法會漏印,因為宣告改動只有畢業。
- 另:該函式第一行「目標 … 支檔(依改動起點的宣告)」在畢業後把畢業檔也算進去,標籤不再準確。

**F6(最小解第 1、4、5 點、「回退」)**
severity: minor
blocking: 否——可執行性 gap,實作者會先撞到紅的舊測試。
- 問題:「回退」只列「畢業判定函式及兩處呼叫、七支測試」。
  - 實際要改畢業判定的呼叫點有三個:`scripts/lumos:58457`(pitfalls)、`:63861`(派工鏡頭)、`:57639`(check_lines,S6 要改)。
  - 第 5 點把規則與骨架全文搬出技能文件,但現有三支測試依賴文件內嵌內容,spec 沒說要改或退役。
- 參照:`scripts/test_lumos.py:109204`(`t_arch_target_android_template_valid`,讀範本區塊與十二條 RULE)、`:109236`(`t_arch_target_android_template_konsist_names_match`,讀「## Konsist 骨架」節)。搬走後這兩支會翻紅,舊計劃的 S1、S3 也沒被正式取代。

**F7(〈開關〉`modules`)**
severity: major
blocking: 是——modules=multi 產出的規則 1 少了唯一的結構檢查,而且理由不一定成立。
- 問題:multi「加一條模組依賴規則(交給編譯器擋),拿掉兩支分層 Konsist 測試」。這兩支是 `layersDependOnlyInward` 與 `domainHasNoAndroidImports`。
- 引句:「multi 加一條模組依賴規則(交給編譯器擋),拿掉兩支分層 Konsist 測試」
- 現行範本的限制條件更窄:`target-arch-android-template.md` 的〈調整與撤除〉寫「領域層若拆成純 Kotlin 模組(不套 Android 外掛),第一條由編譯器擋,`domainHasNoAndroidImports` 可以拿掉」。spec 把條件拿掉,也沒定義「多模組」怎麼切。
- 例:multi 按功能切(PRIOR-ART 借的 Now in Android 就是 core/feature 拆法),domain 在 Android library 模組內。預期是 domain 的 `import android.*` 仍被擋,實際沒有任何東西擋。
  - 編譯器不會因為 domain 引用 android 而失敗。
  - 兩支測試都被拿掉,規則 1 變成沒有測試綁定的純語意規則。

**F8(〈開關〉`ddd=lite`)**
severity: minor
blocking: 否——S2 只驗規則存在與否,不驗措辭一致。
- 問題:lite 只拿掉三條規則,並把「搬進聚合根」改成「搬進領域層」,但其餘規則仍含「聚合」。
- 規則 4 寫「以聚合為單位整包載入與存回」。
- 規則 6 寫「載入聚合、呼叫聚合的行為方法」。
- 規則 12 寫「經由聚合根與用例的公開方法驗」。
- 例:ddd=lite 產出的節點裡沒有聚合根規則,卻要求 Repository 以聚合為單位、用例呼叫聚合方法。S1、S2 只數規則數,抓不到。

**F9(〈開關〉`interfaces=always`)**
severity: minor
blocking: 否——規則 6 的測試仍存在,只是失去殺傷力。
- 問題:always 讓用例變成介面加 `FooUseCaseImpl`,但 `useCasesExposeSingleInvoke` 的篩選是 `scope.classes().filter { it.name.endsWith("UseCase") }`。
- 引句:「always 換成「用例與 Repository 一律介面加 Impl」規則與測試」
- 例:usecase=required 且 interfaces=always。介面不在 `classes()`,`...UseCaseImpl` 不以 `UseCase` 結尾,測試一個類別都沒選到就綠。骨架自己註明這種篩選落空也是綠(`target-arch-android-template.md:73`)。
- 參照:`target-arch-android-template.md:176`。

**F10(用語「宣告」、〈開關〉`modules`、S3)**
severity: minor
blocking: 否——只影響多模組專案,S3 沒要求產生器處理。
- 問題:目標宣告的 `path` 受 `_arch_targets_config` 限制:第一段必須是寫死的資料夾名,不能是萬用字元(`scripts/lumos:57326-57329`)。
- 例:`modules=multi`、`legacy=all`,模組是 `app/`、`core/data/`、`feature/home/`。S3 說「legacy=all 時只有一條目標宣告」,但單一範圍目錄寫不出能涵蓋 `app` 與 `core` 與 `feature` 的合法樣式(`**/src/main/**` 會讓整份宣告被丟棄)。S3 沒有定義多模組怎麼產宣告。

**F11(S3、「最小解」第 3 點)**
severity: minor
blocking: 否——可以靠定義「程式檔」解決。
- 問題:「範圍內 git 已追蹤的每支程式檔」沒定義。
- `_arch_code_file` 只排除測試檔與一批文件副檔名,`.xml`、`.kts`、`.png`、`.java` 都算程式檔(`scripts/lumos:37511-37513`、`:57420`)。
- 例:`app/` 有 300 支 `.kt` 加 250 支 res xml 與圖。若用這個判準,551 條超過 500 就被拒絕改用 dirs。
- 若只列 `.kt`,則舊的 `.java` 檔以後被修改時會被當成目標檔審。
- 這兩種結果和 Konsist 只認 Kotlin 都對不上。

**F12(「最小解」第 2、3 點)**
severity: minor
blocking: 否——產生器介面欄位沒寫全。
- 產生器吃「六個開關、根套件、範圍目錄」,沒有節點名,也沒有 Konsist 測試檔路徑與所屬模組。
- RULE 行的 `[test:]` 綁定要靠 `platforms` 前綴才找得到測試所在平台,產生器只加 `arch_targets` 一鍵、不寫平台宣告。多平台專案裡綁定可能解析到預設平台,S1 的「lint 0 問題」只在夾具上成立。
- 設定檔存在但壞 JSON、頂層不是物件,或鍵值為 `null`,spec 只說「已有 arch_targets 這一鍵」就拒寫,沒定義讀不懂時的處置。
- 「整批拒寫」只檢查寫之前的存在性,不是交易:節點、測試已寫、設定檔暫存替換失敗時,重跑會因「節點已存在」被擋住。
- ⚠ Konsist 在 Gradle 下的工作目錄是模組目錄,`.lumos/config.json` 在儲存庫根。spec 沒說測試從哪裡找設定檔,只在 REVISIT 提到多模組路徑,判不準單模組是否同樣有此問題,交編排者。

**F13(「最小解」第 1 點)**
severity: minor
blocking: 否——登記有必要,但寫的理由方向反了,會讓人誤判。
- 問題:spec 說不登記「會被當成專案自己的檔、風險分級被降」。`_vendored_skip` 是跳過「原封不動的工具自帶檔」(`scripts/lumos:32085`),登記了才會被降級,沒登記反而照專案程式算。
- 真正需要登記的原因是 `_vendored_pending` 與 `lumos update` 的分發靠這張表(`scripts/lumos:32260`),以及逐檔比對的測試。
- 引句:「同時登記進工具自帶檔清單 `_VENDORED_TREE_FILES`,不然推送時會被當成專案自己的檔、風險分級被降」

## 逐節

- 用語:見 F3(畢業定義)、F11(程式檔)。
- 問題與最小解:第 1、3、4、5 點見 F1-F3、F6、F12、F13。第 2 點見 F12。
- 開關:組合 `modules=multi`、`ddd=lite`、`interfaces=always` 各有衝突,見 F7-F9。`usecase=optional` 與 `ui_state` 的組合沒找到產不出合法規則的情形。
- 驗收條款:S1、S2 見 F8、F9(只驗數量不驗措辭與測試是否空轉)。S5、S6 見 F3-F5。S3 見 F10、F11。S4 見 F12。S7:已讀,無 finding。
- 回退:見 F6。
- 實務隱患、REVISIT:效能與守衛面的描述屬實(500 條上限、5 秒預算、推送前分級無上限),另補 F3 的守衛面缺口。

## 實務隱患鏡頭

- 效能:無新隱患,已承認推送前分級與派工鏡頭兩條路對超過 500 條的宣告判得不同,產生器產出不超過上限。
- 併發:partial-write 見 F12。
- 守衛面:F3(畢業範圍的判準不是「刪 none 行」)。
- 路徑與跨平台(Konsist 與 Python 的 glob 實作是否一致):產生器產出只有字面路徑與 `目錄/**`,但使用者手改的 config 可能用到 `**/` 前置與 `[]`。Kotlin 端比對要和 `_glob_first_match` 的語意逐條對齊,S1 到 S7 沒有任何測試守這件事。
- 資安:根套件與範圍目錄進 Kotlin 與 RULE 行的輸入沒說明跳脫;依「lumos 威脅模型」(單人、AI 依序操作、自用框架)放行。
- 對外送出、金流、不可逆:同 spec 已排除理由,無新增。

## 固定席節點判斷

- `Systems/arch-alignment-lens`:KEY 只有「只判跟專案既有的一不一樣」與「major 只給引入第二種做法或跨層直呼」,不是合約行。畢業把檔從鄰居基準切到目標基準,這兩條 KEY 不受影響。該節點第 77 行寫的「只讀起點版」與本計劃改動會不一致,落地時要同步改。F3 若不收斂,畢業會讓檔案在鄰居與目標兩種審法都落空,實質影響到「只判跟專案既有的一不一樣」的覆蓋。

最嚴重 severity: major,blocking 共 4 條(F1、F2、F3、F7)。
