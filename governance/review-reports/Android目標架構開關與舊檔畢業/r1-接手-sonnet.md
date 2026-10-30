severity: major

這份 spec 的核心設計能做,但有 6 條 major,多數是機制本身的缺口。有 3 條是「spec 沒交代、照做會壞掉」。

固定席 `Systems/arch-alignment-lens`:不影響。
- 它的兩行 KEY 只管對照組選法和 major 錨,畢業判定碰不到。
- 它的正文(`docs/lumos-toolchain-knowledge/Systems/arch-alignment-lens.md` 的〈目標架構基準〉段)寫著「分支改的宣告下一次推送才生效」。畢業做完後這句會變成過期說法,必須在同一次提交改掉。這屬於 finding 8。

## Finding 1:舊的 Android 範本測試會紅,spec 沒處理
severity: major
blocking: 是 — 步驟 5 把規則與骨架搬走後,兩支現有測試必紅,而 spec 沒寫怎麼處理。

- 對應段落:「最小解」步驟 5、「回退」。
- 引句:「技能文件改成講開關與訪談題目,指向產生器;不再內嵌規則與測試全文。」
- 引句:「畢業判定函式及兩處呼叫、七支測試」
- 查證:file: `scripts/test_lumos.py:109195-109222` 的 `_android_template_block` 與 `t_arch_target_android_template_valid`,要求範本文件有「## 範本」節和 markdown 圍欄,且讀到 12 條 RULE。
- 查證:file: `scripts/test_lumos.py:109236-109250` 的 `t_arch_target_android_template_konsist_names_match`,要求有「## Konsist 骨架」節和 kotlin 圍欄。
- 輸入:照步驟 5 改完技能文件。預期:這兩支測試被改寫或刪除並登記。實際:它們在「前置:『## 範本』那一節有一個 markdown 圍欄」直接紅。
- 七支新測試是 S1 到 S7,不含這兩支,回退清單也沒提到它們。
- 前一份計劃 `Projects/Android的MVVM與DDD目標架構範本_計劃` 的 S1、S3 條款綁了這兩支測試,`arch-alignment-lens` 那篇也引用它們,spec 都沒說處理方式。

## Finding 2:畢業判定看結果、不看形狀,「審得更多」不成立
severity: major
blocking: 是 — spec 自稱已關上的繞過口,實際沒有關。

- 對應段落:S5、「實務隱患/守衛面」、步驟 4。
- 引句:「頂端改判成起點版沒有的節點、頂端新增 none 或刪掉目標宣告」
- 引句:「範圍限定成只能把 none 改成起點版本就有的目標節點(審得更多,不是更少)」
- 條件只看「起點判 none、頂端判成起點版就有的某個目標節點」,不限於刪 none 那行。
- 輸入:起點版宣告為 `[{legacy/** none}, {app/** Systems/Android目標架構}, {tools/** Systems/輕量目標}]`,其中「輕量目標」只有 1 條 RULE。分支在 none 行之前加 `{"path":"app/legacy/Big.kt","node":"Systems/輕量目標"}`。
- 預期:Big.kt 不算畢業。實際:頂端判成起點版就有的目標節點,符合 S5。Big.kt 改套 1 條規則審,失去鄰居比對,審得更少。
- 起點版的節點若沒有有效 RULE 行,doctor 的說法是「這些檔審查時會照鄰居」(file: `scripts/lumos:57527-57530`)。這種節點也能被拿來當畢業目標。
- 修法方向是把條件收窄成「頂端判成的節點等於起點版最後一條涵蓋該檔的目標節點」,或只認「刪行」。這裡先列出缺口,不替 spec 選擇。

## Finding 3:`new-only` 在真實 Android 專案幾乎不能用,上限邊緣還會悄悄丟掉目標宣告
severity: major
blocking: 是 — 主打模式有硬上限,超過就沒有同時保有「舊檔照舊」與「畢業」的替代路徑。

- 對應段落:步驟 3、S3、「實務隱患/效能」。
- 引句:「舊檔數加一超過派工鏡頭讀得到的宣告上限時應拒絕並提示改用 dirs」
- 查證:file: `scripts/lumos:57281` 的 `_ARCH_TARGET_LENS_DECLS_MAX = 500`。
- 輸入:一個有 800 支 Kotlin 檔的 Android app 選 `new-only`。預期:能建立。實際:被拒,只剩 `dirs`。`dirs` 沒有 none,所以沒有「按檔畢業」的路徑。
- 沒提到按目錄寫 none(`legacy/**`)這個更省條數的選項。
- spec 沒定義「程式檔」是否套用 `_arch_code_file`(file: `scripts/lumos:57420`,排除測試檔與略過副檔名)。若產生器算得比它寬,測試檔會白佔 500 條額度。
- 輸入:產生器恰好產出 499 個 none 加 1 條目標,共 500 條,剛好吃滿。專案後來手動加任何一條宣告(例如新增一個 none 目錄)。這條必須插在目標宣告前面,501 條時目標宣告落到 `rules[:500]` 之外(file: `scripts/lumos:57438-57440`)。派工鏡頭對所有新檔不再附目標規則,只在 `cut` 印一行原因。
- 同時 pitfalls 與 doctor 仍判成目標。這個兩條路判不同的狀況,spec 只說「產生器產出的宣告判得一樣」。

## Finding 4:`dirs` 模式與 Konsist 範圍沒有銜接
severity: major
blocking: 是 — 沒有任何機制讓 Konsist 只掃指定目錄。

- 對應段落:步驟 3、S3。
- 引句:「Konsist 測試讀同一份 `.lumos/config.json` 的 none 宣告跳過舊檔,不另存清單」
- 查證:`legacy=dirs` 時宣告只有「每個目錄一條目標」,沒有 none。
- 輸入:`dirs=[feature/cart]`,其他目錄的舊碼沒有任何 none。預期:Konsist 只掃 `feature/cart`。實際:Konsist 只會跳過 none,整個根套件的舊檔都被掃,架構測試在採用當下就整片紅。
- 在 `legacy=all` 但有「範圍目錄」時同樣沒說 Konsist 怎麼限縮。
- Kotlin 測試要讀 JSON,需要 JSON 解析依賴。Gradle 單元測試的工作目錄是模組目錄,不是 repo 根,`.lumos/config.json` 的定位方式也沒定義。
- REVISIT 的「路徑比對在子模組也對」只涵蓋 none 比對,沒涵蓋這個。

## Finding 5:多模組專案寫不出一條宣告
severity: major
blocking: 是 — S3 在 `modules=multi` 時自相矛盾。

- 對應段落:S3、開關表。
- 引句:「legacy=all 時只有一條目標宣告」
- 查證:file: `scripts/lumos:57324-57325`,`path` 第一段含 `*?[` 會整份 `arch_targets` 作廢(「第一段要是寫死的資料夾名、而且至少兩段」)。
- 輸入:`modules=multi`,模組是 `app/`、`core/data/`、`feature/home/`。預期:`legacy=all` 產一條。實際:`*/src/main/**` 或 `**/src/main/**` 會被整份拒用,必須每個模組各一條。
- 產生器參數只有「根套件、範圍目錄」(單數),沒說多模組的路徑從哪裡來。

## Finding 6:舊檔搬移或改名後掉出 none,畫面照舊的承諾失效
severity: major
blocking: 是 — 改名這種常見動作會當場讓 Konsist 紅,spec 沒處理。

- 對應段落:步驟 3、4。
- 查證:file: `scripts/lumos:57424-57428` 的 `_arch_target_changed_files` 把改名算成新路徑。none 是按檔名逐檔列的。
- 輸入:`git mv app/.../legacy/Foo.kt app/.../legacy/Bar.kt`(或 IDE 重構改套件)。預期:仍算舊檔。實際:新路徑不在 none 清單,命中最後一條目標宣告。審查席改套目標規則,Konsist 因為不再跳過它而紅。純改名的人被迫整檔重構。
- 舊路徑的 none 條目留成死行。doctor 對這種行印「命中 0 支檔」,條目累積後噪音越來越多(file: `scripts/lumos:57512-57514`)。

## Finding 7:`modules=multi` 無條件拿掉領域純度測試,但沒問領域是不是獨立模組
severity: major
blocking: 是 — 開關的前提從未被訪談確認,拿掉測試後會留下沒有守衛的規則。

- 對應段落:開關表 `modules` 列。
- 引句:「multi 加一條模組依賴規則(交給編譯器擋),拿掉兩支分層 Konsist 測試」
- 查證:file: `skills/lumos-project-notes/commands/target-arch-android-template.md:224-228` 的條件是「領域層若拆成純 Kotlin 模組」,第一條才由編譯器擋。
- 輸入:專案選 `multi`,但模組是依功能切的 Android library(`feature-a`、`feature-b`),各自內含 `domain` 套件,沒有純 Kotlin 的 domain 模組。預期:領域層不碰 android 仍有機器守。實際:`layersDependOnlyInward` 與 `domainHasNoAndroidImports` 被拿掉,「domain 是純 Kotlin」規則只剩審查席語意判,沒有任何編譯器或測試擋。
- 同一份文件第 4 行又寫骨架只在「單一模組、依層分套件」跑過。multi 的 Konsist 套件寫法也沒驗過,只在 REVISIT 提到。

## Finding 8:周邊文件、指令與計數會跟新行為打架
severity: minor
blocking: 否 — 都是同步遺漏,不影響機制本身是否能做。

- 對應段落:步驟 5、「回退」。
- 引句:「畢業判定函式及兩處呼叫、七支測試」
- 查證:實際有三處呼叫端要接畢業判定,spec 只提兩處。
  - 推送前風險分級:file: `scripts/lumos:58456-58461`。
  - 派工鏡頭:file: `scripts/lumos:63861-63864`。
  - code-loop check 的「只有畢業」判斷:file: `scripts/lumos:57639-57664`,而且 `57635` 那行印出的「(依改動起點的宣告)」在畢業後對畢業檔不再正確。
- 查證:未列入計劃的過期敘述。
  - file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:37` 寫著「只讀改動起點版的宣告(分支自己改宣告下次推送才生效)」,並稱「Android… 抄…十二條與 Konsist 骨架」。
  - file: `skills/lumos-project-notes/SKILL.md:11` 寫著「附 Konsist 架構測試骨架」。
  - file: `docs/lumos-toolchain-knowledge/Systems/arch-alignment-lens.md` 的「宣告只讀改動起點那一版…下一次推送才生效」。
  - 現有的 `t_arch_target_android_template_linked_from_usage` 只比對檔名,不會抓到這些文字衝突。
- 輸入:三個月後的 AI 讀 06 的那一列,以為刪 none 行要等下次推送。預期:文件說得出同分支當場生效。實際:文件說相反的話。

## Finding 9:新增頂層子命令觸發的守衛
severity: minor
blocking: 否 — 是會紅的測試,不影響設計成立與否。

- 對應段落:步驟 2。
- 查證:`lumos arch-template` 是新頂層命令,需補 `HELP_WHEN`(file: `scripts/lumos:68739`)。
- 查證:`t_every_subcommand_has_when`(file: `scripts/test_lumos.py:11877`)要求 `--help` 有「什麼時候用:」。
- 查證:`t_command_index_complete`(file: `scripts/test_lumos.py:11243`)要求 `commands/*.md` 提到 `lumos arch-template`。`INDEX.md` 現為 4500 字元,剛好壓在上限 4500(同測試檢查),任何一字增加都會讓長度檢查翻紅。
- 這些都不在 spec 的做法或測試清單裡。

## Finding 10:產生器產出的 `[test:…]` 綁定與 `platforms` 設定的關係沒交代
severity: minor
blocking: 否 — 不確定是否真的會紅,交編排者確認。
⚠ 判不準:我沒跑,只讀文件。

- 對應段落:步驟 2、S4。
- 引句:「設定檔存在但沒有這一鍵時,只加這一鍵、其他鍵原樣保留」
- 查證:現有文件 file: `skills/lumos-project-notes/commands/target-arch-android-template.md:225` 說,架構測試不在預設平台目錄時,要先宣告 `platforms`,再寫 `[test:<平台>:<測試名>]`。
- 輸入:Android 專案預設平台是儀器測試,Konsist 放在 `app/src/test`。預期:產出的 RULE 綁定可解析。實際:只寫 `arch_targets`,綁定的平台前綴不見,S1 與 S4 只驗名字同檔與 lint,沒驗綁定能解析。

## Finding 11:產生器的命令介面完全沒定義
severity: minor
blocking: 否 — 屬可執行性缺口,實作者要自己決定。

- 對應段落:步驟 2、S1、S7。
- 引句:「預設只印預覽,`--write` 才寫節點、宣告、架構測試三樣」
- 查證:六個開關的旗標名、必填或預設值、根套件與範圍目錄的旗標、`legacy=dirs` 的目錄怎麼傳、各開關的預設值,spec 都沒寫。
- 輸入:S1 要「跑遍六個開關的全部組合」,實作者無從知道旗標形狀。S7 要比對的「開關名與選項」也沒有第一手定義。

## Finding 12:已採用舊範本的專案沒有升級路徑
severity: minor
blocking: 否 — 影響範圍限於已採用者。

- 對應段落:步驟 2、S4。
- 引句:「節點檔或架構測試檔已存在、或 `.lumos/config.json` 已有 `arch_targets` 這一鍵,就整批拒寫」
- 查證:spec 自己說 macrobench-lab 已驗過,那個專案照舊範本(節點名 `Android目標架構`)已建節點與宣告。
- 輸入:該專案要改成開關式。預期:有改法。實際:產生器因節點檔已存在、`arch_targets` 已有而拒寫,只說明哪一個存在,沒有「怎麼遷移」。

## Finding 13:doctor 輸出在 500 條宣告下失控
severity: minor
blocking: 否 — 純輸出品質問題。

- 對應段落:「實務隱患/效能」。
- 查證:file: `scripts/lumos:2283-2291` 把 `_atl` 全部用 `";".join` 串成單一一行 `ok(...)`。file: `scripts/lumos:57512-57514` 的 `hits==0` 問題行不限條數。
- 輸入:499 條 none 加 1 條目標的專案跑 `lumos doctor`。預期:可讀的摘要。實際:一行含 500 項,檔案被刪或搬走後每條死 none 再多一行警告。spec 的效能段沒提 doctor。

## 各節檢查
- 用語、問題與最小解:已讀,除上述外無其他 finding;立案紀錄、舊否決對照的交叉引用(`Projects/Android的MVVM與DDD目標架構範本_計劃`、`Projects/架構對齊可宣告目標架構_計劃`)存在。
- 驗收條款:S1 到 S7 的測試名都標為將新增;S2、S4 沒涵蓋 Finding 4 和 Finding 6 的情境。
- `_VENDORED_TREE_FILES` 登記:這張表在 `scripts/lumos:31963-31987`,登記方式可行,不算 finding。

### 實務隱患鏡頭,逐類
- 效能:見 Finding 3、13。
- 併發:spec 說「先寫暫存再整檔替換」。目標專案若同時有另一個會談改 `.lumos/config.json`,先讀後寫之間沒有鎖。這屬單人框架的威脅模型,不列。
- 守衛面:見 Finding 2。
- 安全:產生器寫的 `path` 取自 `git ls-files` 的檔名,檔名含 `*?[` 時會在宣告裡變成萬用字元,命中不了自己或誤命中別檔;spec 沒說要不要跳脫。檔名含控制字元會讓整份宣告作廢(`scripts/lumos:57326`)。已知模式、單人框架,放行附理由。
- 金流、對外送出、不可逆:同意 spec 的「已排除」。

總結:最嚴重 major,blocking 共 7 條(Finding 1 到 7)。
