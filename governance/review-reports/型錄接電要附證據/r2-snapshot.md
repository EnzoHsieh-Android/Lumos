---
type: project
status: doing
created: 2026-11-08
updated: 2026-11-08
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
  - risk/守衛面
related:
  - "[[Projects/Android現成檢查接上CI與推送前_計劃]]"
  - "[[Systems/kotlin規則包]]"
lands_in:
  - Systems/kotlin規則包
---
# 型錄接電要附證據_計劃

> 白話:型錄每列的「通電批次」欄會寫「批四(CI 範本:Android Lint)」,意思是消費專案照範本接上 Android Lint 或 compose-rules 後,CI 會擋這列的壞寫法。這個標記原本靠型錄自檢讀「現成規則」欄的字面判(段裡有規則碼、而且不含「待查」「相關」這類註記就算接上)。2026-11-08 代碼審三輪加一次事後審查,四次都抓到「標了會擋、那條檢查其實擋不到」的列:r1 是註記寫「相關」一類卻照算、r2 是 STATE-5 那條檢查只管呼叫位置、r3 是 ARCH-17 註記寫「只管」卻一個壞例都擋不到、事後審查是 PERF-1 的「需 `@WorkerThread` 標註」被反引號隔開躲過排除字;接著全表核對又找到三種漏法(檢查預設關、等級是 Hint 不會讓建置失敗、Slack 的檢查在範本裝的版本裡根本沒有)。字面判斷已經同類被打穿四次,這份計劃換形狀:每個「宣稱會擋」都要在型錄〈接電證據〉節有一筆判定,判定附等級、預設開關與出處;等級與預設開關用 lint 自己的元資料機械填,「擋不擋得到這列壞例」用讀官方頁或真跑判;自檢只認判定表,字面判錯的代價從「悄悄多宣稱」變成「被擋下來要補判定」。

PRIOR-ART: ①世界怎麼確定一條 lint 檢查管什麼:Android Lint 用測試樣本定義每條檢查會報什麼(https://googlesamples.github.io/android-custom-lint-rules/api-guide.html 〈Testing〉),最可靠的是拿壞例真跑。2026-11-08 先導實驗證明本機能離線真跑(AGP 8.13.2、Gradle 8.13 都在快取,23 列全部編得過、報告齊全;卷證 `governance/review-reports/型錄接電要附證據/sweep/pilot.md`(新增))。②等級與預設開關:lint 的檢查物件自帶 defaultSeverity 與 isEnabledByDefault,先導用同版 lint-api 載入各套件的檢查清單機械讀出(本機這批套件 608 條);沒載入的套件讀官方檢查頁固定格式的 Severity 與「disabled by default」欄(https://googlesamples.github.io/android-custom-lint-rules/usage/flags.md.html 的 `--show` 印的就是這兩項)。③粒度:lint baseline 以「issue id + 位置」為單位記錄(https://googlesamples.github.io/android-custom-lint-rules/usage/baselines.md.html),判定表照樣以「列 + 標籤 + 檢查 id」為單位。④放哪:照型錄既有〈待查證〉節的做法,在同一份檔裡加一節、雙向比對(check.py 的 `_pending_table` 與 `pending_problems`)。排除:繼續補排除字表(四次被打穿)、另開 TSV(設計審 r1 架構對齊席:第二種做法)。
RETIRE-IF: 範本裝的 lint 版本能在 CI 裡跑一次壞例樣本之後,判定表的「擋得到」改成以 CI 真跑為準、這張手寫判定撤掉;或判定表連續兩次全表重驗都 0 列翻案,降成只在新增列時要求判定。

## 用詞

- **型錄**:`skills/kotlin-idioms/checks-catalog.md`,一列一種 Kotlin/Android 寫法;**現成規則欄**是第 6 欄(登記哪些現成檢查管這列),**壞寫法欄**是第 3 欄,**通電批次欄**是第 10 欄。
- **批一**:型錄自己的 ast-grep 規則包已上線會擋;**批四**:消費專案照 linter 目錄範本接上 Android Lint(CI)或 detekt 外掛 compose-rules(推送前)之後才擋。兩個**標籤**:「CI 範本:Android Lint」「推送前:detekt 外掛 compose-rules」。
- **候選**:型錄自檢 `batch4_expected_tags` 從現成規則欄抽出的(標籤,規則碼)——只看結構(前綴加規則碼、不在 `B4_DEFAULT_OFF`、段裡不含排除字表 `_B4_SKIP` 的字);排除字只會讓候選變少(少宣稱),不會讓沒判定的宣稱成立。
- **判定**:〈接電證據〉節的一列:型錄列編號、標籤、檢查 id、判定(擋得到/擋不到)、等級、預設、出處。
- **擋得到**:那條檢查會報壞寫法欄裡至少一個例子(真跑報出,或官方說明、範例、檢查器原始碼與測試顯示會報),而且**等級是 Warning、Error 或 Fatal**、**預設開**(範本開 `warningsAsErrors`,warning 以上才讓建置失敗;Hint 與預設關不算)。compose-rules 是 detekt 規則,沒有 lint 等級,等級欄寫「detekt」,預設以 compose-rules 預設設定為準。
- **等級與預設的來源**:Android Lint 內建與本機快取裡有的 androidx、Slack 套件,用 lint-api 31.13.2 載入檢查清單讀(版本照範本支援的最舊那一段:[[Systems/linter精選目錄]] 的對照寫 AGP 8.7.1 到 9.2.0 裝 Slack compose-lints 1.4.2,讀 1.4.2);其他套件讀官方檢查頁的 Severity 與預設欄。清單裡讀不到的檢查 id 判「擋不到」,理由寫「範本版本沒有這條」。
- **漏網帳**:`docs/.escape-log.jsonl`,放行之後才被抓到的缺陷紀錄(`lumos loop escape --list` 看)。

## 範圍

1. **〈接電證據〉節**:型錄新增一節表格,欄位「列 | 標籤 | 檢查 | 判定 | 等級 | 預設 | 出處」;出處用型錄既有的〔查證 日期:網址〕或〔真跑 日期:樣本檔〕寫法。每個候選(列,標籤)至少一列判定;同一(列,標籤)有多個候選檢查時,判成擋得到的寫一列就夠,全部擋不到才要每個候選各一列。
2. **資料**:168 列宣稱接電的列與候選逐一判定——等級與預設照〈用詞〉的來源機械填;擋不擋得到沿用 2026-11-08 全表核對(六包讀官方頁、10 列讀原始碼、23 列真跑先導)。真跑先導另隨機抽 30 筆「讀頁判擋得到」的判定真跑一次,量讀頁判定的準確率,不一致的以真跑為準改判定、寫進〈天花板〉。
3. **型錄自檢**(`configs/ast-grep/kotlin-android/check.py`,接進 `catalog_problems`,型錄側一律用 `main_rows` 與 `_cells`):
   - 每列該寫的批四標籤 = 該列有一筆「擋得到、等級 Warning/Error/Fatal 或 detekt、預設開」判定的標籤;通電批次欄寫的要一字不差(取代原本只看候選的比對)。
   - 每個候選(列,標籤)要有判定;沒有就報「要補判定」並指名列與標籤。
   - 每筆判定的檢查 id 要是該列該標籤的候選規則碼(整詞);列編號要在主表;同一(列,標籤,檢查)不准兩筆;判定、等級、預設欄只收固定值;出處要符合既有〔查證〕的格式(重用 `_VERIFIED_RE`)或〔真跑 日期:樣本檔〕且樣本檔存在。
   - 自帶證據的豁免不做(39 列一樣要判定)。
4. **型錄資料改動**:判定後沒有任何標籤擋得到的列,通電批次改成只標批一;註記照讀頁或真跑結果補一句(不再靠註記字決定)。UI-100 壞例補 `@Preview`;UI-11 實測欄那句實跑紀錄改成真跑結果。
5. **真跑樣本**:先導的樣本檔搬進 `configs/ast-grep/kotlin-android/samples/lint-wiring/`(新增),一列一支,檔名帶列編號,給判定表的〔真跑〕出處引用。
6. **型錄〈輸入與口徑〉**:改寫成「批四以〈接電證據〉節為準」,寫明擋得到的定義與等級、預設的來源。
7. 不做:不在 CI 真跑 Android Lint(CI 沒有 Android 建置環境);不改排除字表。

## 實務隱患

- 讀頁判定本身可能錯:用範圍 2 的真跑抽樣量準確率,〈天花板〉照實寫抽樣結果。
- 判定表與主表會漂:自檢雙向比對(候選沒判定、判定對不到候選都報)。
- 範本裝的 lint 版本之後升級,等級、預設與有沒有這條會變:判定表記讀取的版本,回頭條件綁版本(見文末)。
- 新增型錄列的人不知道要補判定:錯誤訊息寫要在〈接電證據〉節補哪一列哪個標籤。
- 併發寫入不考慮:工具鏈單人、AI 依序操作。
- 已排除:金流:只改型錄與型錄自檢,不碰付款。
- 已排除:對外送出:不寄信、不呼叫外部服務,自檢只讀本機檔。
- 已排除:不可逆:全部是 repo 內的文字檔,退回提交即還原。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| lint 檢查管什麼由它的說明、範例與測試樣本定義 | Android Lint API 指南〈Testing〉與各檢查頁 | https://googlesamples.github.io/android-custom-lint-rules/api-guide.html |
| 等級與預設開關是檢查自帶的元資料,`--show` 印得出 | lint 命令列旗標說明 | https://googlesamples.github.io/android-custom-lint-rules/usage/flags.md.html |
| 判定以 issue id 為單位記錄 | lint baseline 說明 | https://googlesamples.github.io/android-custom-lint-rules/usage/baselines.md.html |
| warningsAsErrors 只讓 warning 以上擋建置 | AGP Lint DSL 說明 | https://developer.android.com/reference/tools/gradle-api/8.7/com/android/build/api/dsl/Lint |
| Slack compose-lints 各檢查的加入版本 | Slack compose-lints CHANGELOG | https://raw.githubusercontent.com/slackhq/compose-lints/main/CHANGELOG.md |
| compose-rules 預設關的規則 | compose-rules 規則頁 | https://mrmans0n.github.io/compose-rules/rules/ |

字面判斷四次被打穿的紀錄:代碼審卷證 `governance/review-reports/code-型錄批一列也寫批四/`(r1 到 r3 各一條 major)與漏網帳。全表核對與真跑先導的原始回報:卷證 `governance/review-reports/型錄接電要附證據/sweep/`。

## 驗收條款

- [S1] 當真型錄跑型錄自檢時,問題數 應 是 0,每個候選(列,標籤) 應 有判定,每列通電批次的批四標籤 應 恰好等於判定擋得到的標籤 [test:t_kt_catalog_batch4_evidence]
- [S2] 當在型錄複本拿掉一筆判定、把一筆判定的檢查 id 改成該列沒有的、把一筆擋得到的等級改成 Hint、把預設改成關、或讓同一(列,標籤,檢查)出現兩筆時,型錄自檢 應 各報一個指名那一列的問題 [test:t_kt_catalog_batch4_evidence]
- [S3] 當讀真型錄時,判定沒有任何標籤擋得到的列 應 只標批一 [test:t_kt_catalog_batch4_evidence]
- [S4] 當讀〈接電證據〉節時,出處是〔真跑〕的每筆 應 指到存在的樣本檔 [test:t_kt_catalog_batch4_evidence]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 真型錄 | 型錄自檢 0 個問題 | 本計劃範圍 3 |
| S2 | 型錄複本刪掉 UI-24 的判定 | 報 UI-24 的 CI 範本:Android Lint 要補判定 | 本計劃範圍 3 |
| S2 | 型錄複本 UI-24 判定的檢查改成 NewApi | 報 UI-24 判定的檢查不是候選 | 本計劃範圍 3 |
| S2 | 型錄複本 UI-24 判定的等級改成 Hint | 報 UI-24 通電批次與判定不一致(判定沒有擋得到的標籤) | 〈用詞〉擋得到:Hint 不算 |
| S2 | 型錄複本 UI-24 判定的預設改成關 | 報 UI-24 通電批次與判定不一致 | 〈用詞〉擋得到:預設關不算 |
| S2 | 型錄複本 UI-24 的判定重複一筆 | 報 UI-24 判定重複 | 本計劃範圍 3 |
| S3 | 真型錄的 API-9、API-23、UI-11、UI-49、UI-95、ARCH-28、DATA-32、PERF-1、PERF-36、UI-64、UI-80、TEST-25、UI-96、UI-92、UI-43、UI-44、UI-45、UI-46 | 只標批一 | 全表核對與真跑先導:擋不到、Hint、預設關或範本版本沒有這條 |
| S4 | 型錄複本把一筆〔真跑〕出處的樣本檔名改成不存在的 | 報那一列的樣本檔不存在 | 本計劃範圍 3 |

## 回退

退回本計劃的提交:〈接電證據〉節、型錄通電批次與註記改動、真跑樣本目錄、型錄自檢的判定比對與新測試、〈輸入與口徑〉那一句、Systems/kotlin規則包 那幾行。卷證留著。

## 天花板

- 「擋不擋得到這列壞例」大部分是讀官方頁判的,讀錯就會錯;範圍 2 的真跑抽樣量出準確率後寫在這裡。
- 等級與預設照範本最低支援的版本讀;消費專案裝更新的版本時,可能多擋(新版加的檢查),判定表不會反映。
- 自檢在 CI 只驗判定表跟型錄一致與格式,不重跑 lint。

REVISIT:2027-05-08 看 [[Systems/linter精選目錄]] 有沒有改 Android Lint、Slack compose-lints 或 compose-rules 的版本對照,有就用新版重讀等級與預設、重跑〔真跑〕樣本,判定照新版改
REVISIT:2027-02-08 有消費專案接上 CI 範本之後,拿〈接電證據〉節每筆「擋得到」的壞例在那個專案真跑一次,沒報的改判擋不到

## 審計修正紀錄

- r1(2026-11-08,4 席):22 條/blocking 13/證據要跟標籤綁、帶等級與預設、放回型錄裡、取消自帶證據豁免、退回不再靠註記字;另查到本機能離線真跑,改成真跑優先。卷證 `governance/review-reports/型錄接電要附證據/`。
