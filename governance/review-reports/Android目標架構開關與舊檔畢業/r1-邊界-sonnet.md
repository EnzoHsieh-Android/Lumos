severity: major

固定席 `Systems/arch-alignment-lens` 判「不影響」。節點宣稱的是只判跟既有的一不一樣、對照組選法、major 只給兩種情形,這份設計沒動這些。畢業只是改變哪幾支檔被歸進「目標」組。不過該節點沒有記「宣告只讀起點版」這條合約。這條保護在 `scripts/lumos:57397`(`_arch_targets_at`)的 docstring 與上游計劃裡,下面 finding 4 會碰到它。

逐節結果:
- 「用語」、「問題與最小解」第 1、5 點、「開關」表、「回退」:已讀,除下列 finding 外無其他 finding。
- 驗收條款 S1、S2、S7:已讀,除 finding 7 外無 finding。
- 所有交叉引用:`_VENDORED_TREE_FILES`(`scripts/lumos:31963`)、`_ARCH_TARGET_LENS_DECLS_MAX`(`scripts/lumos:57281`)、`_trusted_decl_ref`、`_arch_target_split`、`_glob_first_match`、`--arch-target` 旗標、`skills/lumos-project-notes/commands/target-arch-android-template.md` 都存在。`[[Projects/架構對齊可宣告目標架構_計劃]]` 與 `[[Projects/Android的MVVM與DDD目標架構範本_計劃]]` 的存在性我沒逐一開檔核對。

1. 產生器寫出的宣告沒有任何條款要求它能被讀法接受(「問題與最小解」第 2、3 點、S3、S4)
引句:「吃六個開關與根套件、範圍目錄,預設只印預覽」
severity: major
blocking: 是(讀法一條不合法就整份作廢,全部審查退回比鄰居,而且沒有任何條款抓得到)
- `_arch_targets_config`(`scripts/lumos:57307`)只要一條 path 不合法就整份作廢、全部照鄰居審。實跑結果:
  - `Root.kt`、`[x]/src/A.kt` 被拒,原因是第一段不是寫死的資料夾、或不到兩段。
  - 含反斜線的 path、含 U+202E 控制字元的 path 也被拒。
- 「範圍目錄」參數的形狀沒定義。輸入 `""` 或 `.`,會產生 `**`,被讀法拒絕。輸入 `app/` 會產生 `app//**`,fnmatch 命中不了任何檔。輸入 `./app`、`/abs` 也被拒。
- S3、S4 只驗「條數、順序、lint 0 問題」,沒有一條要求產出的 `arch_targets` 經 `_arch_targets_config` 讀出同樣的條數。
- 輸入 `--write` 加範圍目錄 `.` → 預期拒絕或寫出合法宣告 → 實際寫出讀法會整份丟掉的宣告。派工鏡頭附 `⚠` 警告,但 Konsist 會照 config 擋舊檔。兩邊判斷分裂。
- 舊檔檔名含反斜線或控制字元時,逐檔 none 行同樣會讓整份作廢。

2. 逐檔 none 把檔名當萬用字元樣式,含 `[` `]` `*` `?` 的檔名會失效或誤吞(「問題與最小解」第 3 點、S3)
引句:「逐一寫成 none 宣告,最後一條才是目標節點」
severity: minor
blocking: 否(只有檔名含這幾個字元才觸發)
- 實跑 `_glob_first_match("app/src/Foo[1].kt", ["app/src/Foo[1].kt", "app/src/**"])`,回 1(命中目標宣告),不是 0。那條 none 命不中自己,舊檔被當目標檔審。
- 實跑 none `app/src/Foo*.kt` 對 `app/src/Foo2/Bar.kt` 回 0。星號跨斜線,會順帶吞掉同前綴的新檔。
- spec 沒寫跳脫(例如 `[[]`)或拒絕這類檔名的規則。S3 只要求「每支各寫成一條」。

3. 多模組與 `new-only` 組合沒有可行的宣告寫法;「程式檔」沒有定義(S3、「開關」表)
引句:「把範圍內 git 已追蹤的每支程式檔各寫成一條 none」
severity: major
blocking: 是(新增「多模組」是立案三件事之一,在最常見的組合上產不出可用宣告)
- 讀法要求第一段必須是寫死的資料夾名(`scripts/lumos:57326`)。`*/src/main/**` 這類跨模組樣式會被拒。
- `new-only` 的描述是「最後一條才是目標節點」,只有一條。`app/`、`core/data/`、`feature/x/` 沒有共同的寫死前綴,一條宣告蓋不住多個模組。
- 只有 `dirs` 模式「每個指定目錄一條」,而 `dirs` 沒有 none 行,無法表達「同一目錄內舊檔照舊」。
- 「範圍內現有的程式檔」沒有判準。`_arch_code_file`(`scripts/lumos:57420` 前後)只排除測試檔與文件、圖片副檔名。實跑:`res/layout/a.xml`、`build.gradle.kts`、`AndroidManifest.xml`、`src/androidTest/.../B.kt` 都回 True。
- 如果產生器只列 `.kt`,xml 與 gradle 檔的審查歸屬就和 Konsist 不一致。如果全列,範圍內有 480 支 `.kt` 加 30 支 xml 就超過 500 上限被拒。

4. `new-only` 的 500 上限讓一般規模的舊專案無法採用,退路 `dirs` 無法表達舊新混在同資料夾(S3、「實務隱患」效能)
引句:「舊檔數加一超過派工鏡頭讀得到的宣告上限時應拒絕並提示改用 dirs」
severity: major
blocking: 是(核心情境「舊 class 維護照舊」在稍大的專案不可用)
- 舊檔數加一大於 500,即 500 支舊檔以上就被拒,提示改用 `dirs`。真實 Android 專案的 `.kt` 超過 500 支很常見。
- 邊界:499 支舊檔共 500 條宣告通過;500 支舊檔共 501 條被拒,由 `rs=rules[:max_rules]`(`scripts/lumos:57440`)截斷。S3 與此一致,但上限 500 是 `scripts/lumos:57281` 的常數,產生器要引用它。
- `dirs` 只對舊新分居不同資料夾的專案成立。舊新混居的專案(多數專案)兩個都用不了,spec 沒有第三條路,也沒把這個限制寫成已知限制。
- 另一個副作用:`new-only` 寫入的 none 行會隨舊檔刪除、改名變成「命中 0 支」。`_arch_target_doctor_lines` 對每條各印一條提醒,數百條提醒會淹沒其他提醒。spec 沒有清理或合併機制。

5. Konsist 讀 config 跳過舊檔的設計有四個洞(「問題與最小解」第 3 點、「回頭」REVISIT)
引句:「Konsist 測試讀同一份 `.lumos/config.json` 的 none 宣告跳過舊檔,不另存清單」
引句:「拿一個多模組的 Android 專案套一次,確認路徑比對在子模組也對」
severity: major
blocking: 是(同一份 config 的兩個讀者判得不一致;`dirs` 模式下整套測試全紅)
- (a) `dirs` 模式沒有 none 行。Konsist 現行骨架是 `Konsist.scopeFromProduction()` 掃整個專案。只讀 none 的話,未列入的舊目錄全被當目標檢查,整批紅。spec 只說「讀 none 宣告」,沒說要讀目標宣告當白名單。
- (b) 比對語意。lumos 是「第一條命中算數」、fnmatch、星號跨斜線、`**/` 去前綴、NFC。spec 沒規定 Kotlin 端要實作哪些。輸入:target 宣告在 none 宣告之前,lumos 判目標,只讀 none 的 Konsist 判跳過。
- (c) 路徑基準。宣告是 repo 根的 git 相對路徑。Gradle 子模組的單元測試工作目錄是模組目錄,`.lumos/config.json` 與 `file.path` 的基準都不是 repo 根。spec 把這件事放到 `REVISIT:2027-01-31`,但「找不到或讀不懂 config 時 Konsist 該紅、該綠還是該跳過」完全沒定義。預設全套 `domain` 規則落到舊檔,是紅;若靜默跳過,則是整套測試變空殼。
- (d) JSON 解析依賴。Android 本機單元測試的 `org.json` 是 stub,用了會拋「not mocked」。spec 只說「不加依賴」(針對 lumos),沒說明 Kotlin 端用什麼解析 JSON。

6. 同分支可改 config,卻影響 Konsist 的判斷;spec 守的是 LLM 審查席那一半(「守衛面」、舊否決對照)
引句:「理由是被審分支不能自己改宣告決定自己怎麼被審」
引句:「Konsist 測試讀同一份 `.lumos/config.json` 的 none 宣告跳過舊檔,不另存清單」
severity: major
blocking: 是(機械守衛的結構測試可被同一分支繞過,與 spec 自己說的保護目的矛盾)
- lumos 審查席只讀起點版宣告,理由是被審分支不能自己改宣告決定自己怎麼被審。Konsist 讀的是工作目錄這一版的 config,是分支頂端。
- 輸入:分支新增違規檔 `app/.../NewBad.kt`,同時在 config 加 `{"path":"app/.../NewBad.kt","node":"none"}` → 預期架構測試仍紅 → 實際 Konsist 跳過,結構測試綠。
- LLM 席因讀起點版仍會審它,但機械那一半已經被繞過。spec 的「守衛面」只論證了畢業這一種改動,沒討論 Konsist 這條讀頭端版的路。
- 判準 ⚠:專案威脅模型寫明不防 AI 刻意偽造。若編排者認為此項屬於該放行的範圍,可降為 minor,但 spec 本身把這條保護當成立案理由。

7. 畢業判定的範圍與落點含糊,「兩處呼叫」數目與實際不符(最小解第 4 點、S5、S6、「回退」)
引句:「畢業判定函式及兩處呼叫、七支測試」
引句:「而且那個節點在起點版本就是目標節點時」
severity: minor
blocking: 否(實作時一查就能補,不影響行為方向)
- 「起點版本就是目標節點」沒定義。是出現在起點版某條非 none 宣告,還是節點筆記在起點版存在且有有效 RULE 行。輸入:起點宣告有指向、但節點筆記在起點版不存在的節點。`_arch_target_doctor_lines` 會警告「不存在」,畢業後檔拿到「規則沒附」。
- 讀宣告的點不只兩處:`scripts/lumos:58457`(風險分級)、`scripts/lumos:63864`(派工鏡頭)、`scripts/lumos:57642`(`_arch_target_check_lines`,S6 要改的)。「回退」寫「畢業判定函式及兩處呼叫」,漏掉 S6 的那處。
- 頂端版的宣告在派工鏡頭路是否套 500 條與 5 秒上限沒寫,而風險分級路不套。手寫超過 500 條的宣告兩條路畢業判定會不同。
- S6 的「只有畢業」要怎麼機械判斷沒寫(頂端宣告是否等於起點宣告刪去若干 none 行)。節點筆記的 RULE 同時被修改時,算「其他宣告改動」與否也沒寫。畢業的檔不在本次改動集合時,說明句要印什麼也沒寫。

8. 現有三支 Android 範本測試與「不再內嵌規則與測試全文」衝突,spec 沒交代(最小解第 5 點、「回退」)
引句:「技能文件改成講開關與訪談題目,指向產生器;不再內嵌規則與測試全文」
severity: minor
blocking: 否(實作時推送閘會馬上翻紅,屬於補寫缺漏)
- file: `scripts/test_lumos.py:109204` `t_arch_target_android_template_valid` 要求範本區塊讀出十二條有效 RULE 行。
- file: `scripts/test_lumos.py:109236` `t_arch_target_android_template_konsist_names_match` 要求 Konsist 骨架段有 `class ArchitectureRulesTest` 圍欄與至少七支 `@Test`。
- 兩支測試綁在 `Projects/Android的MVVM與DDD目標架構範本_計劃` 的 S1、S3。技能文件改成只講開關後兩支必紅。
- spec 的「七支測試」只列新增的,沒寫這三支舊測試(含 `t_arch_target_android_template_linked_from_usage`)是改寫、刪除還是保留,也沒寫舊計劃的 S1、S3 綁定要怎麼處理。

9. `--write` 對怪格式 `.lumos/config.json` 的行為與「原樣保留」沒有定義(S4、「實務隱患」併發)
引句:「設定檔存在但沒有這一鍵時,只加這一鍵、其他鍵原樣保留」
severity: minor
blocking: 否(邊界情境;採 read-modify-write 的標準做法時才會踩)
- 輸入:config 是壞 JSON、非 UTF-8、頂層不是物件、或帶 BOM。S4 只規定「已有 `arch_targets` 鍵就拒」。
- 讀法端對「讀不懂但原文提到 arch_targets」有特別處理(`scripts/lumos:57410`)。產生器端沒有對應規則。
- 「其他鍵原樣保留」若用 `json.dump` 重寫,中文鍵值預設會被轉成 `\uXXXX`,縮排與鍵序也會變。「原樣」是指語意還是位元組沒寫。
- `{"arch_targets": null}` 或 `[]` 是否算「已有這一鍵」沒寫。讀法把 `null` 當沒宣告(`scripts/lumos:57316`)。

**實務隱患鏡頭(補充):**
- 效能:已涵蓋於 finding 3、4。畢業多讀一次頂端宣告在上限內可接受,未另發現問題。
- 併發:產生器本身只寫新檔,無共用狀態。但主線在採用分支合併前新增的舊風格檔不在 none 清單裡,合併後 Konsist 會對它們紅。這是 `new-only` 凍結清單的天然限制,spec 沒寫處理方式,不單獨成條。
- 守衛面:見 finding 6。
- 檔名與編碼:中文與空白檔名通過讀法(實跑 `app/src/中文/畫面.kt`、`app/src/a b/Foo.kt` 皆 OK)。NFC 轉換有做。Kotlin 端比對是否做 NFC 沒寫,併入 finding 5(b)。
- 金流、對外送出、不可逆:同意 spec 的「已排除」。

最嚴重 severity 為 major,blocking 共 5 條(finding 1、3、4、5、6)。
