severity: major

本輪發現 1 條 major(點名測試任務的新判法對字串模板失明,是修補造成的回歸),另有 4 條 minor。三類各節如下。

## ①提示注入

已看,無。候選訊息裡的外來字串(檔名、測試名、區塊開頭)都過 `_out_clean`。`_lint_waive_show` 新加的清洗,實測連 ESC、C1、U+2028/2029、方向標記都清掉;`(AI 放的…)` 標記接在被截短的理由後面,藏不掉。單行外來文字回顯照 repo 的威脅模型放行。

## ②讀寫與執行越界

已看,無。已查三處:
- 比對工具只透過 `_lens_git_dl` 的參數陣列叫 git,沒有 shell 插值,也沒有寫檔。
- 新版 `_tg_retry_ok` 的 `git show <提交>:<路徑>` 以提交編號開頭,不會被當成選項。
- 公開檔沒有私有考場識別字:drill 的 README、cases、history、semgrep 樣本與兩篇 Verification 都已去識別化。掃過套件名、信箱、密鑰形狀、`/Users/`,只有 `s.example.com` 與文件網址,專案名 `mOrangePos` 與 `SM-X710` 屬已明寫的容許範圍。

### S1 點名測試任務改看「引號裡整個是任務名」後,字串模板與 GString 寫的任務名讓關測試不被列
severity: major
blocking: 是 — 單步、照常的 Gradle 寫法就讓 `enabled = false`、`onlyIf { false }` 這類關測試設定不被列,守衛直接放過
引句:「_TG_TASK_NAME_Q = re.compile(r'["\']:?(?:[\w-]+:)*[\w-]*[Tt][Ee][Ss][Tt][\w-]*["\']')」
file: `scripts/lumos:48859`(任務名正規式),`scripts/lumos:48970`(`_tg_names_test_task`)
攻擊路徑:
- 誰:照常操作的 AI(要讓建置變綠而關掉單元測試),或使用者本人手寫變體迴圈。
- 從哪:編輯 `app/build.gradle(.kts)`,用 Android 很常見的逐變體寫法 `tasks.named("test${variant}UnitTest")` 或 `tasks.getByName("test${…}")`。
- 送什麼:在該區塊或同一行加 `enabled = false` 或 `onlyIf { false }`。
- 拿到什麼:任務名裡的 `$`、`{`、`.` 讓引號內容不符 `[\w-]` 形狀,整段被判成「不是測試任務」。`enabled=false` 與 `onlyIf` 只在測試區塊才算,所以 `test-guard` 回 0 條、rc=0,新增告警閘整道放過。修前版本在同一份輸入會列 `tq/build-config`。
重現(兩版各跑一次,臨時 repo 在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/資安-sonnet/g_tpl1`):
```
python3.14 lumos_before test-guard --repo …/g_tpl1 --diff A..B   # 作弊候選 1 條,rc=1
python3.14 lumos_after  test-guard --repo …/g_tpl1 --diff A..B   # 作弊候選 0 條,rc=0
```
變體實測(修前都列、修後都不列):
- `tasks.named("test${v}UnitTest") {` 換行 `enabled = false`
- `tasks.named("test$v") { enabled = false }`
- `tasks.named("test${v}UnitTest") { onlyIf { false } }`
- Groovy `tasks.getByName("test${variant.name.capitalize()}UnitTest").enabled = false`
- `tasks.matching { it.name.startsWith("test$flavor") }.configureEach {` 換行 `enabled = false`
- 單行 `…tasks.named("test${name.replaceFirstChar{…}}UnitTest") { onlyIf { false } }`

對照:`tasks.named("testDebugUnitTest") {` 與 `tasks.withType<Test> {` 修後仍列。

這個缺口沒寫進 `_TG_LIMITS` 的「抓不到」清單,計劃筆記與 `Systems/test-guard` 也查不到。

另外,`val n = "testDebugUnitTest"` 加 `tasks.named(n) { enabled = false }` 這種用變數指任務的寫法,修前修後都不列,屬同一類原有漏查。
歸因:有證據的修復回歸。`lumos_before`(22cc6675)對 tpl1、tpl3、onlyif、groovy_gstring、kts_matching_tpl、kts_oneline 全部列出,`lumos_after`(fcd27439)全部 `[]`。原因是舊的 `_TG_TASK_REF` 加 `_TG_QUOTED` 允許引號內任何字元,新正規式收窄成純任務名形狀。

### S2 assume 與門檻身分改成「整個敘述去掉全部空白」後,字串常值裡的空白差異被抹平
severity: minor
blocking: 否 — 要在 assume 條件的字串常值裡動空白才有效,屬縱深防禦;但這是一步編輯就讓既有放行的指紋沿用到「永遠跳過」的新條件
引句:「    return re.sub(r"\s+", "", t[i:k]), k」
file: `scripts/lumos:48967`(`_tg_stmt_at`),`scripts/lumos:48940`(身分組成)
攻擊路徑:
- 誰:照常操作的 AI(或手滑的使用者)。
- 從哪:編輯測試檔裡一個已存在、已放行(或在基準裡)的 `assumeTrue(env == "ci")`。
- 送什麼:把字串常值改成含空白的 `"c i"` 或 `"Lin ux"`,條件變成永遠為假,測試永遠被跳過。
- 拿到什麼:去空白後身分仍是 `assumeTrue(env=="ci")`,沒有新的 `tq/skip-added`,既有放行指紋順帶放掉這次變更。
重現:`t5.py` 的 `string_space`、`string_space2`。修前列 `tq/skip-added`(逐行只壓縮空白、不刪除),修後 `[]`。
歸因:有證據的修復回歸。`lumos_before` 與 `lumos_after` 的結果如上。修補同時修好了跨行 assume 的後幾行沒進身分的原有漏查(`later_line_change` 修前 `[]`、修後有列)。

### S3 測試檔超長行抹掉後照比:藏在超長行裡的作弊只剩一條可放行的 tq/too-large
severity: minor
blocking: 否 — 這是設計取捨,不是繞過:候選仍然出現且要放行,修補反而縮小了盲區。若要攻擊,需要刻意製造 2 萬字的行,屬刻意偽造,不是非刻意走過
引句:「extra=f"有一行超過 {_TG_MAX_LINE_CHARS} 字,那幾行沒比對,其餘照比"))」
file: `scripts/lumos:49295`
攻擊路徑:
- 誰:刻意要繞過的 AI。
- 從哪:在測試檔的 `@Ignore` 後面接 20,050 個空白(trailing spaces),或把斷言改弱寫在那一行。
- 送什麼:一支新的 blob。
- 拿到什麼:實測只剩 `tq/too-large`(extra 寫「那幾行沒比對」),沒有 `tq/skip-added`。要裁掉就用 `lint-waive`,理由欄 AI 可以自填。指紋綁新 blob 編號,所以每次改都要重新放行。
重現:`t2.py` 的 `ignore_pad`。修前與修後都只有一條 too-large。`weaken_pad` 與 `assert_deleted_pad` 修後才額外列出 `tq/no-assertion`、`tq/assert-weakened`(同檔其他改動照比,盲區縮小)。
補充:
- 用未閉合的 `/* … */` 夾住超長行也試過,修後會多列 `tq/test-removed`,不構成繞過。
- 非刻意走過的情況沒找到:超長行只要出現在 base 或 head 任一端,就一定會列 too-large,而且只在這支檔有被改動時才會被讀到。
歸因:有證據的原有漏查。修前版本同一輸入也只有 too-large,而且整支檔都不比對。

### S4 行註解被「單獨的 CR」或 Java 的 \u000a 提前結束時,註解後面生效的 @Ignore 不被看見
severity: minor
blocking: 否 — 需要刻意造行終止字元的怪檔,屬刻意偽造語法,且是原有行為;順手提一句
引句:「"""剝註解(keep_strings=False 時連字串內容一起換成空白),位置跟原文一一對應:在剝過的文字找位置、回原文取字。"""」
file: `scripts/lumos:48412`、`scripts/lumos:6784`(`_strip_c_comments`)
攻擊路徑:
- 誰:刻意繞過的 AI。
- 從哪:寫 `// note` 接一個單獨的 `\r`(或 Java 的 `// note \u000a @org.junit.Ignore`),再接 `@Ignore`。
- 送什麼:Kotlin 與 Java 的語法都以單獨 CR 結束行註解,Java 另外先處理 unicode 跳脫。
- 拿到什麼:`@Ignore` 在編譯器眼中是有效註記,剝註解把它當成註解尾巴,`test-guard` 不列。
重現:`.kt` 版 `// note\r@Ignore\n@Test fun a()` 修前修後都是 `[]`;Java 版 `\u000a` 也是 `[]`。Java 版的 `\r` 變體因為整支被看成函式不見,列了 `tq/test-removed`,所以不構成 bypass。編譯器那一側的行為依 JLS 3.3、3.4 推出,這裡沒有 javac 實跑。
歸因:有證據的原有漏查。這不是這輪修補造成的,修前版本同樣是 `[]`。

### S5 assume 敘述最多看 2000 字,超過的尾段改動不進身分
severity: minor
blocking: 否 — 需要原本就有超過 2000 字的 assume 敘述,縱深防禦
引句:「_TG_STMT_MAX = 2000」
file: `scripts/lumos:48945`
攻擊路徑:
- 誰:刻意或搭配多步操作的 AI。
- 從哪:一支基準裡本來就有超過 2000 字的 assume 敘述(註解會被換成空白、算進長度)。
- 送什麼:把尾端的條件改成 `false`。
- 拿到什麼:身分只取前 2000 字,指紋不變。
重現:`t3.py` 的 `cap_multiline_comment`,修前修後都是 `[]`。同一份輸入的短版 `short_multiline`,修前 `[]`、修後有列。
歸因:有證據的原有漏查。修補把短敘述的盲區補上了,2000 字以上的仍是盲區。

## ③非刻意、一步就能繞過的守衛

已看,無新增(S1 就是此類中唯一成立的,已列在上面)。
- `LUMOS_SKIP_LINT_NEW` 全 repo 只有 `scripts/lumos:38951` 一處讀取,且只認 `"1"`。hooks、CI、安裝腳本都沒有「有設就關」的另一處。
- 殘留的 `=1` 會走 `_lint_new_off`,在背後跑比對,有候選或比對出錯才記 `skipped-env` 帳,所以留有痕跡。
- `_tg_read` 失敗回 None,被當成「沒跑完」而擋下,不會變成可放行的 `tq/unreadable`。
- 檔名帶空白、中文,或不是 UTF-8、帶換行,都由 `-z` 路徑與 `tq/unreadable` 處理,沒找到走過去的路。
- `_lint_new_autopass` 統一寫 `autopass_reason`,全 repo 只剩兩處把 `autopass` 設成 True,原因都有填。

總結:這輪修補的新面裡,字串模板的測試任務名讓 `enabled=false` 這類關測試設定從「列出」變成「不列」,是 major 回歸;其餘 4 條為 minor、不擋。

臨時 repo 與實驗腳本都在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/資安-sonnet/`(`exp.py`、`t1.py` 到 `t6.py`、`lumos_before`、`lumos_after`),我沒有刪。
