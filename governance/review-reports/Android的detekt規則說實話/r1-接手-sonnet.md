severity: major

審查對象:`r1-snapshot.md`(以下「spec」)。重點是知識同步清單、給消費專案看的提醒文字、共用設定疊加。以下實測都用本機 detekt 1.23.8,實驗檔已清掉。

## 逐節結論
- 開頭欄位、PRIOR-ART、RETIRE-IF、用詞:已讀,只有 finding 1、7 的問題。
- 判定表:已讀。T3 已實測成立,`--input=`、`-i=`、`--config=` 都回「Was passed main parameter … but no main parameter was defined」。P1 也和程式一致:`scripts/lumos:38889` 沒有 `{LINT_FILES}` 的命令進 `report_only`。
- 判定依據、範圍、不做、回退、天花板:已讀,見 finding 1~8。
- 實測確認成立的 spec 說法:
  - `CoroutineLaunchedInTestWithoutRunTest` 和 `SuspendFunInFinallySection` 寫進設定,detekt 整個拒跑(rc 非零、報「invalid config property」)。
  - 吞取消那條不抓 `try/catch (e: Exception)`,只抓 `runCatching`。
  - `ForbiddenMethodCall` 要放在 `style:` 底下,放 `coroutines:` 底下會整個拒跑。

## findings

**1. 同步清單要把「要型別資訊」套在不需要型別的規則上,和 spec 自己的用詞矛盾**
- 引句:「不用型別資訊就會響的:GlobalCoroutineUsage、ForEachOnRange。」
- 引句:「R6、R9、R10、R11、R12、R13 的機檢欄標」
- 重現:沒給 classpath 跑含 `GlobalScope.launch` 與 `(1..10).forEach` 的檔,`[GlobalCoroutineUsage]` 和 `[ForEachOnRange]` 都響。
- 撞牆處:
  - kotlin-idioms R11 的機檢規則就是 `GlobalCoroutineUsage`(`skills/kotlin-idioms/SKILL.md:98`),照清單會被標成要型別資訊。
  - `Systems/效能檢核目錄.md:61`「協程 scope」那列,照 spec 的「已開,要型別資訊才跑」替換,也會寫錯 GlobalScope 那條。
  - 接手的人會以為不帶 classpath 就抓不到 GlobalScope。
  - 「primitive array」那列(`效能檢核目錄.md:67`)本來沒有「共用 config 已開」字樣,spec 說的「改成」無從替換。那列又是一條要型別(ArrayPrimitive)、一條不要(ForEachOnRange),得拆開寫。
severity: major
- blocking: 是。這會把錯的規則歸屬寫進三份會被當依據的文件。

**2. 知識同步清單漏列這些仍會說假話的地方,S5 的 grep 字串也抓不到**
- 引句:「對清單裡每支檔 grep「已開」與「預設開」」
- 漏列且實查仍有舊說法的位置:
  - `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:122` 寫「三條」「裸跑時這三條全不生效」,補開兩條後數量就不對。
  - `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:128` 寫「接完跑 `lumos lint-check --smoke` 驗宣告真跑得動」。冒煙只驗有 SARIF 產出,規則沒響也綠。spec 的「不做」又明說不做探針。
  - `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:52` 與 `docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md:87`,detekt「跑得動」「本來就跑得起來」。
  - `configs/detekt/android.yml:12-13`,SuspendFunSwallowedCancellation 的行內註解仍寫「catch 泛型例外吞掉 CancellationException」。實測 `try/catch` 不會響,spec 只改設定開頭的用法說明。
  - `docs/lumos-toolchain-knowledge/Projects/Android協程與API協同機械審_調研.md:46` 和 `:57` 仍把 `--jvm-target` 當必要參數,與 spec 用詞「實測不影響」矛盾。
  - 同一檔 `:49` 的「共用設定還沒開的只剩…那條」,spec 落地後就假了。清單只寫「現況表那幾列」。
- grep「已開」「預設開」抓不到「還沒開」「三條」「跑得動」「真跑得動」,所以 S5 驗不出以上漏洞。
severity: major
- blocking: 是。spec 的目的是「文件說實話」,漏列處會繼續說假話。

**3. 健檢印出的現成訊息會和新提醒直接打架**
- 檔案:`scripts/lumos:4137-4140`
- 引句:「推送前的新增告警閘會真的執行它們」
- 重現:消費專案宣告的 detekt 沒有 `{LINT_FILES}`(Citrus_KDS、mOrangePos 的 `.lumos/lint.json` 都是,已讀過)。健檢先印「宣告健康……推送前的新增告警閘會真的執行它們」,緊接著 spec 要印 P1「對這條只記錄、不擋」。同一段輸出前後互相否定。
- spec 只說「既有分支之後」加提醒,沒說要改這句。
severity: major
- blocking: 是。印給消費專案看的字串,spec 該列進同步清單。

**4. 會過期的「推送時不擋」散進至少六處文件,沒有回頭條件**
- 引句:「「共用 config 已開」改成「已開,要型別資訊才跑;推送時不擋」」
- 撞牆處:`Projects/Android的detekt推送前真的擋_計劃.md` 落地後,「推送時不擋」「對這條只記錄」在 `效能檢核目錄`、`linter精選目錄`、`kotlin-idioms`、`調研` 全部變假。那案的 `lands_in` 只有 `Systems/pitfalls-lint-adapter`,不會提醒回來改這些散落處。
- spec 的 RETIRE-IF 只管判定表。S5 只在寫的當下手動 grep 一次。
- 專案規定(CLAUDE.md 鐵則 4)要求這類會過期的話搬成 `REVISIT:[when-file:路徑][by:日期]` 一行,spec 沒做。
severity: major
- blocking: 是。

**5. 共用設定的新增兩段只靠手動驗收,爆了所有消費專案一起拒跑**
- 引句:「[manual:照〈判定依據〉的做法實跑一次,把指令與輸出貼進實作紀錄]」
- 重現:設定裡規則放錯規則集(例如 `coroutines:` 底下放 `ForbiddenMethodCall`),detekt 回「Run failed with 1 invalid config property」,整次不產結果。KDS、mOrangePos 共用同一份設定。
- spec 只在 S4 手動驗一次,沒有任何自動測試檢查這份檔。
- 同一段還有第二個坑:spec 只寫「方法清單只放 collectAsState」,沒寫要用完整名稱。實測:
  - `collectAsState`:0 筆命中,不報錯。
  - `androidx.compose.runtime.collectAsState`:2 筆命中。
  - `androidx.compose.runtime.SnapshotStateKt.collectAsState`:0 筆命中。
- 寫成裸名稱不會報錯也不會響,只有跑 S4 才發現。
severity: major
- blocking: 是。該在 spec 寫死完整名稱與規則集(`style`),並補一條有 detekt 時跑設定驗證的測試(沒裝就跳過)。

**6. 共用設定與消費專案自己的設定疊加:不會拒跑,但清單會被整份蓋掉,文件也沒教怎麼疊**
- 實測:`--config shared.yml,own.yml` 時 `ForbiddenMethodCall.methods` 不合併,後面那份整份取代前面。
  - `shared,own`:只抓 `runBlocking`(own 的清單)。
  - `own,shared`:只剩 shared 的清單,own 的 `runBlocking` 被丟掉,也沒警告。
- 重現:`--config a.yml --config b.yml` 直接拒跑,印「Can only specify option --config once」加用法說明。
- 撞牆處:`skills/kotlin-idioms/SKILL.md:136-147` 的機檢接線,教消費專案在自己的設定裡寫 `ForbiddenMethodCall.methods`(含 `runBlocking`、`collectAsState`)。再加標準接法的 `--config $HOME/.../android.yml`,照做的人不是拒跑就是被靜默蓋掉。
- 目前四個已知消費專案的 `lint.json`(Citrus_KDS、mOrangePos 等)都只有共用設定,現在沒中。
- spec「不碰消費專案」成立,但同步清單沒要求在標準接法樣板與 kotlin-idioms 寫明:自有設定要和共用設定用逗號合併成一個 `--config`,清單類欄位後面蓋前面。
severity: minor
- blocking: 否。現存消費專案不受影響,只是文件缺口,但已實測重現。

**7. 提醒文字的指路與適用範圍**
- 引句:「Android 專案的依賴沒有穩定路徑,目前沒有現成取法」
- 這句假設全部是 Android。但 `.kt` 棧也有非 Android 後端(`scripts/lumos` 的 `kt-springdata`、`kt-springhttp` 題組存在),後端有穩定的依賴取法。T1 不分 Android 與否,會對後端說「沒有現成取法」。
- 提醒會印進沒有本 repo 圖譜的消費專案,spec 沒規定提醒要不要指到可讀得到的出處。消費專案讀得到的是 `skills/kotlin-idioms/SKILL.md`(安裝為使用者層 skill),所以那份得自帶「要型別資訊」的定義與取得方式。
- 目前 spec 只說機檢欄標「要型別資訊」,SKILL.md 的機檢欄說明(`:12`)和「機檢接線」段都沒要求補定義。三個月後在消費專案讀 skill 的人看不懂這四個字。
severity: minor
- blocking: 否。

**8. 天花板少一條:相對路徑的 classpath 在特定位置靜默失效**
- 引句:「classpath 指到不存在或過期的檔、`--input` 指錯目錄、consumer 自己的設定關掉規則,判定表都看不出來。」
- 重現(ForbiddenMethodCall 對 compose 型別):相對路徑項目 `crx/classes.jar` 放在 classpath 第一位時命中 2 筆;放在中間或最後(沒有 `./` 前綴)命中 0 筆,不報錯。改成 `./crx/classes.jar` 或絕對路徑才命中。
- 這和「指到不存在的檔」同一種表現,但檔案其實存在。lint 命令的 cwd 是 repo 根,消費專案很可能寫相對路徑。spec 的 S4 若用相對路徑驗,也會誤判「兩條都不響」。
- severk: 無。判定表仍判成有型別、T1 不出。
severity: minor
- blocking: 否。補進天花板即可。

**9. 核對邊界改寫會把仍未核對的部分一併洗掉**
- 引句:「開頭的核對邊界改成「2026-11-04 用 detekt 1.23.8 核對過協程與效能兩組」」
- 現有的邊界(`skills/kotlin-idioms/SKILL.md:14-15`)講的是整份文件的規則名、預設開關、條數都沒逐條核對,其中包含 R16 的「compose-rules 32 條」、Slack compose-lints,這些 spec 沒核對。整句改掉會讓人以為整份都核對過。
- 該寫成「已核對:協程與效能兩組」,其餘保留「未核對」。同一處的 `REVISIT:2026-10-25` 已逾期,spec 也沒說要換成什麼。
severity: minor
- blocking: 否。

## 圖譜鏡頭(五個節點逐一判斷)
- **`Issues/推送閘對Android的detekt只記錄不擋.md`**:不影響。spec 明說不修這件事,只加提醒與文件,與該節點「先寫進提醒與文件」一致。
- **`Systems/lint-declaration-health.md`**:不影響。合約是 `lint-check` 退出碼 0/1/2(`:24`、`:63-64`),spec 維持退出碼。`--json` 只加 `advisories` 欄,該節點沒有釘 JSON 形狀。F 段位置測試(`t_doctor_lint_declaration`)只釘 `[F]` 在其他段之後,新提醒在 F 段內,不影響。同步時要補本節點的 FLOW 行(`:24`)。
- **`Systems/linter精選目錄.md`**:不影響合約,但有同步缺口,見 finding 2。
- **`Systems/效能檢核目錄.md`**:不影響題目表同步義務(`:29`),因為 spec 只動「lint 可查部分」那欄,沒碰 `_STACK_QUESTION_SPECS` 的題目文字和 id。但替換文字要依 finding 1 改。
- **`Systems/pitfalls-lint-adapter.md`**:不影響合約。spec 不改新增告警檢查,P1 的描述與程式一致。`:87` 的「跑得動」見 finding 2。

## 實務隱患鏡頭
- 金流、對外送出、不可逆:無,spec 已排除,且只印本機輸出、只改設定與文件。
- 資安:無。不讀不寫外部資源,不執行任何新命令;shlex 只拆詞不執行。
- 相容(detekt 版本):無新增風險。新增的兩條規則在 1.23.x 都有,不抬高版本下限(本席未查 1.23 以前的版本)。
- 狀態一致與文件漂移:有,見 finding 2、3、4。
- 共用設定連動所有消費專案:有,見 finding 5、6。
- 效能與記憶體:無。判定函式只做字串拆詞,輸入是單一 JSON 檔裡的命令字串;不跑 linter。

最嚴重 severity: major,blocking 共 5 條(finding 1、2、3、4、5)。
