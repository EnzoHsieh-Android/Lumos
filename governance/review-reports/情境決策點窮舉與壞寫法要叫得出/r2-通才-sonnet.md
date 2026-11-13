severity: major

我逐節讀完整份 spec,並實跑了 klib 與 JVM 清單、`sweep2.py.txt` 和 `scripts/lumos` 的相關函式。r1 已修的項目沒有重報。

**固定席(圖譜節點宣稱的行為與合約)**
- 圖譜鏡頭檔我沒有讀到:題目只給了 `LUMOS-SPEC` 的提交與路徑,沒有附節點內容。
- 能判的部分:spec 的「不做」節聲明不改 `scripts/lumos`,也不改情境題、表態、盲判、段放行的判定。我驗證過 `_kt_situation_segments`、`_kt_sit_text_segments` 都只是被借用。就這個範圍,不會破壞既有行為。
- 節點本身的細部合約我無從逐條判,標 ⚠。

**實務隱患(風險類)**
- 金流、對外送出、不可逆:無。spec 自己排除,我也同意,因為只讀型錄、只動 repo 內檔案。
- 守衛面:有。本案新增的兩道自檢會讓型錄測試擋人。最大的洞是下面的 F1。
- 效能:無。我實跑一次 `sweep2.py.txt` 的全表掃描(184 段),時間不顯著。
- 授權:在 repo 內放兩份 Apache-2.0 的第三方檔,spec 沒提授權或 NOTICE。我標為 minor 的 ⚠(見 F8)。
- 母體過時:見 F6。

---

**F1 〈API 決策點〉的「改由」核對沒有對應檢查可比**(用詞「改由」、範圍 2)

引句:「`規則 <id>`:那條規則在會擋的 `rules/` 目錄,訊息開頭引的編號等於對應檢查」

- 〈API 決策點〉的表只有「名稱 | 歸屬 | 理由」三欄,名稱沒有「對應檢查」。
- 「訊息開頭引的編號等於對應檢查」和「`範本 T<n>`:n 等於對應檢查列通電批次欄的值」,在 API 這側沒有可比的對象。
- 只有括號補了「名稱要在壞例樣本裡出現」和「範本壞寫法小節的程式碼含這個名稱」。n 因此可以任填,規則 id 也只剩「存在」。
- 名稱級背書偏鬆,而這正是 r1 的「規則宣稱擋得住其實擋不住」那一類。
  - 規則只要有一行含該名稱的壞例被報,就算替整個名稱背書。
  - 我實查 `rules/api.yml` 的 `kt-map-await-deferred`,它只收 `$L.map { it.await() }` 這兩種樣式,卻足以替整個名稱 `await` 背書。
  - 範本側也一樣:`launch`、`delay` 這種泛字在每組範本程式碼都出現,「程式碼含這個名稱」恆為真。
- S1、S5 的案例只測「樣本沒有這個名稱」,沒測這兩個缺口。
- 建議:API 側改成明確的對照(名稱→規則 id→樣本行),並要求規則報的那一行是該名稱的壞用法。
- blocking: 是。核心核對在 API 側無法照字面實作,實作者得自行發明語意。
severity: major

**F2 JVM 補來源的抽法規格不完整,實測會產生垃圾名,也漏掉真名**(用詞「公開名稱」第二點、PRIOR-ART)

引句:「補來源 JVM 清單:只收「正規化後 klib 裡沒有」的名稱。」

我照 spec 的正規化規則在 1.10.2 的 `.api` 上實跑,得到:
- 雜湊後綴不是 7 位十六進位,而是 base64 風格,例如 `debounce-HG0u8IE`、`WhileSubscribed-5qebJ5I`、`closed-JP2dKIU`。`equals-impl0` 也不被「`-impl` 後綴」規則涵蓋。
- JVM 的 `@JvmName` 讓名稱和原始碼不同:JVM 的 `from(Executor)` 其實是原始碼的 `asCoroutineDispatcher`。母體會多出沒人寫的名字 `from`。
- 全大寫常數的 getter 還原出 `rECOVER_STACK_TRACES`(`getRECOVER_STACK_TRACES`)。
- 還有 `isInstalled$kotlinx_coroutines_debug` 這種帶 `$` 的內部修飾名,以及 `INSTANCE`、`_state` 這類欄位。spec 沒說欄位收不收。
- 「套件路徑含 internal 的不收」只寫在 klib 那條。JVM 清單裡 `kotlinx/coroutines/debug/internal/`(`DebugProbesImpl`、`AgentInstallationType`、`DebuggerInfo`…)和 `flow/internal/` 都會被收進來。
- klib 側也沒說巢狀成員怎麼判套件。成員行本身不帶套件路徑,例如 `ChannelFlow.capacity`,只有行尾註解才有。
- 同一處:klib 的伴生物件名不是 `Companion`,像 `Channel.Factory`、各個 `Key`,不在排除清單內,會被當名稱收進母體。
- 後果:每次升版都要手動清這批垃圾。我比對 1.11.0 的 JVM `.api`,多出 `addNext`、`peek`、`synchronized`、`unwrap` 這類內部條目。
- 目前 `from` 對應的真名 `asCoroutineDispatcher` 因 klib 的 `Window` 擴充恰好有而沒漏,這是巧合。
- blocking: 否。minor,現況靠錨點與人工歸類能擋住,但規格要補齊。
severity: minor

**F3 「叫不出 95 個」的數字和 spec 自己的口徑對不上**(用詞「壞寫法片段」「叫得出」、範圍 5)

引句:「單位是(情境列, 對應檢查, 片段);2026-11-12 用 `sweep/` 的腳本照這個口徑數:184 個,叫不出 95 個。」

- 我實跑 `sweep2.py.txt`:182 段、叫不出 93,而且它跳過觸發字為(無)的列。
- 把腳本改成含(無)列(D-2),得 184 段、叫不出 95。這個 95 沒套用 r2 新增的路徑篩選。
- 再套用 spec 口徑(`TEST-` 一律叫不出),得 184 段、叫不出 103。多出的 8 段在 `TEST-` 檢查下,例如 `D-21 TEST-15 UnconfinedTestDispatcher`、`D-49 TEST-6 runTest {…}`、`D-50 TEST-18 flow.test { awaitItem() }`。
- 範圍 5 的「95 段逐條處理」、驗證紀錄、統計節的數都會偏,這是補丁和原文銜接處的新不一致。
- `sweep/` 的腳本也還是 `X.kt` 路徑,不是 spec 定義的 main / test 路徑。
- blocking: 否。數字漂移,自檢實作時會自己揭出來。
severity: minor

**F4 帶點觸發字的比對規則和 klib 巢狀實際寫法不合,正向與反向不對稱**(範圍 1 第一種歸屬、範圍 2 反向)

引句:「觸發字帶點的(`SharingStarted.Lazily`)比名稱前加上外層宣告的寫法(`SharingStarted.Lazily`),兩種寫法任一搜得到就算。」

- file: `klib.api:88`:`Lazily` 的完整路徑是 `SharingStarted.Companion.Lazily`。
- file: `klib.api:158`:`UNLIMITED` 是 `Channel.Factory.UNLIMITED`。
- 使用者實際寫的是 `SharingStarted.Lazily` 和 `Channel.UNLIMITED`,都跳過了伴生物件。
- spec 沒說「外層宣告」要不要略過伴生物件。照字面串接,「外層宣告」會得到 `SharingStarted.Companion.Lazily`,例子自己就搜不到。
- 反向檢查只說「觸發字的正規式搜得到名稱」,沒說帶點觸發字也比外層寫法。日後新增 `SharingStarted.Lazily` 這種觸發字,正向會過,反向漏掉。
- 目前真型錄的帶點觸發字(如 `viewModelScope.launch`、`Result.retry`)都不在母體,尚未爆。
- blocking: 否。
severity: minor

**F5 「推送前閘一定跑到這些測試」說過頭**(範圍 4 末句)

引句:「型錄在 `skills/` 底下,推送前閘不會把它的改動判成純文件,一定跑到這些測試。」

- file: `scripts/lumos:64943`:推功能分支時,掛鉤會用 `pushed_mainline` 與 `suite_computed` 把 full 降成子集,全套交給 PR 的 CI。
- 「不是純文件」成立。但「推送前閘一定跑到」對功能分支不成立,實際靠 CI 全套兜底。
- 這點直接影響「本案新增的兩道自檢何時才會擋人」。
- 建議改成「推主線與 CI 全套會跑到」。
- blocking: 否。
severity: minor

**F6 母體釘在 1.10.2,但 spec 自己引用的 1.11.0 已存在,且沒有升版的回頭條件**(用詞「API 母體」、依據來源)

- 1.11.0 在 spec 自己的依據來源裡就有。我下載比對:JVM 新增 `associate*`、`groupBy*` 等流運算子,同時移除了 `offer`、`poll`、`receiveOrNull`、`getOnReceiveOrNull`。
- 母體在本案上線當天就已落後一版。釘 1.10.2 的理由只有「和行為測試範本用的 1.10.2 一致」。我確認 `test-templates.md:154` 確實寫 1.10.2。
- 新版 API 的決策點要等人手動換母體才會被分類。spec 沒有 `REVISIT`(只有 RETIRE-IF 提到升版後的處置),違反 CLAUDE.md 鐵則 4(承認風險要附回頭條件)。
- 建議加一條綁母體升版或日期的 `REVISIT`。
- blocking: 否。
severity: minor

**F7 頻率門檻的量法沒有可重現的基準**(範圍 5、用詞)

引句:「對 Now in Android 釘版提交剝註解字串後算「出現在幾成 kt 檔」」

- spec 全文沒給提交編號。
- 實查 `Android寫法回合結束檢查與改檔前推列_計劃.md` 的 E9:用的是「本機複本(310 支 kt 檔)」,同樣沒有 sha。
- `sweep/triage.py.txt` 只吃語料根目錄參數,64% 基準和 8% 判定都無法逐字重驗。
- 範圍 5 的「增加超過 10 個百分點就停」依賴這個基準。
- 建議補上提交 sha,並把語料檢出步驟寫進 `sweep/`。
- blocking: 否。
severity: minor

**F8 [⚠] 兩處補充**
- 「被問到」的定義略過了平台判斷。`_stack_platform_excluded` 在整批 `.kt` 判成伺服端時,會拿掉 `android_only` 的情境題(`scripts/lumos:39250`)。反查用的假檔 `app/src/main/java/x/X.kt` 沒有 Android import 也沒有建置檔,flavor 判成「判不出」,不會被排除。這剛好和真實伺服端專案的行為不同,但只影響 Android 專案是否被問,屬於定義層面的小缺口。
- 授權。母體檔是 Apache-2.0 的第三方原檔,逐位元組放進 repo,沒提授權聲明。型錄本身零依賴家規之外,這是否需要 NOTICE,我無法判斷。
- blocking: 否。
severity: minor

---

已讀,無 finding 的節:
- 用詞的其他條目(型錄主表列編號、會擋的規則、通電批次欄、停用列與停用字表、段放行、代碼審)。我驗證過 `rules/` 下 148 條規則訊息開頭都是 `[編號]`,`samples/bad/<id>/src/` 結構符合 spec,`test-templates.md` 的 T0 是測試骨架守則。
- 範圍 3(叫不出的壞寫法節)。
- 範圍 6(規則包筆記與型錄說明)。型錄節次順序與插入位置沒問題:`main_rows` 在 `## 情境決策表` 前切斷,新節放在〈接電證據〉後不會被主表解析誤吃。
- 實務隱患的各條。依據來源表的 URL 我都實際打過,四個全數回 200,`KLibSupport.md` 也確實寫「experimental」。
- 驗收條款與預期值表。
- 回退、天花板。
- 審計修正紀錄。

最嚴重 severity 是 major,blocking 共 1 條(F1)。
