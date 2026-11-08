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

> 白話:型錄每列的「通電批次」欄會寫「批四(CI 範本:Android Lint)」,意思是消費專案照範本接上 Android Lint 或 compose-rules 後,CI 會擋這列的壞寫法。這個標記原本靠型錄自檢讀「現成規則」欄的字面判(段裡有規則碼、而且不含「待查」「相關」這類註記就算接上)。2026-11-08 代碼審三輪加一次事後審查,四次都抓到「標了會擋、那條檢查其實擋不到」的列:r1 是註記寫「相關」一類卻照算、r2 是 STATE-5 那條檢查只管呼叫位置、r3 是 ARCH-17 註記寫「只管」卻一個壞例都擋不到、事後審查是 PERF-1 的「需 `@WorkerThread` 標註」被反引號隔開躲過排除字;接著全表核對又找到兩種漏法(檢查預設關卻沒列進預設關清單、檢查等級是 Hint 不會讓建置失敗)。字面判斷已經同類被打穿四次,這份計劃換形狀:宣稱會擋的列要在一張證據表裡附「擋得到哪個壞例、官方頁原文、網址」,自檢只認證據表,字面判錯的代價從「悄悄多宣稱」變成「被擋下來要補證據」。

PRIOR-ART: 世界怎麼確定一條 lint 檢查管什麼——Android Lint 自己用測試樣本定義每條檢查會報什麼(https://googlesamples.github.io/android-custom-lint-rules/api-guide.html 〈Testing〉),檢查頁附說明、範例與實作原始碼連結;最可靠的是拿壞例真跑檢查,這要 Android Gradle 外掛與專案骨架,工具鏈測試環境沒有(回頭條件見文末)。退而求其次:每列附一條人工(代理)讀官方頁或原始碼得出的證據、帶網址與日期,讓判斷可被覆核;自檢只驗證據存在且與型錄一致,不驗證據本身對不對。排除:繼續補排除字表(四次被打穿,見〈依據來源〉的代碼審卷證)。
RETIRE-IF: 有消費專案接上 CI 範本、能拿每列壞例真跑 Android Lint 之後,改成以真跑結果當證據,這張手寫證據表撤掉;或證據表連續兩次全表覆核都 0 列翻案,降成只在新增列時要求證據。

## 用詞

- **型錄**:`skills/kotlin-idioms/checks-catalog.md`,一列一種 Kotlin/Android 寫法;**現成規則欄**是第 6 欄(登記哪些現成檢查管這列),**情境欄**是第 8 欄,**通電批次欄**是第 10 欄。
- **批一**:型錄自己的 ast-grep 規則包已上線會擋;**批四**:消費專案照 linter 目錄範本接上 Android Lint(CI)或 detekt 外掛 compose-rules(推送前)之後才擋。
- **排除字表**:型錄自檢的 `_B4_SKIP`(待查、預設關、相近、opt-in、間接、相關、需標註),段裡含其中一個字就不算接電。
- **擋得到**:那條檢查的官方說明、範例,或檢查器原始碼與它的測試,顯示它會報壞寫法欄(第 3 欄)裡至少一個例子,而且預設開啟、等級是 warning 以上(範本開 `warningsAsErrors`,warning 以上才讓建置失敗;Hint 與預設關不算)。
- **漏網帳**:`docs/.escape-log.jsonl`,放行之後才被抓到的缺陷紀錄(`lumos loop escape --list` 看)。
- **接電段**:現成規則欄以「;」「、」切段後,型錄自檢 `batch4_expected_tags` 判成接上 Android Lint 或 compose-rules 的段(規則見 [[Systems/kotlin規則包]])。
- **宣稱接電的列**:通電批次欄寫了「批四(CI 範本:Android Lint)」或「批四(推送前:detekt 外掛 compose-rules)」的列。
- **自帶證據的列**:情境欄寫「形狀:由 Android Lint <檢查 id> 判」的列(2026-11-08 共 39 列,全部是 Android Lint 那種;compose-rules 的列沒有這種寫法,全部要附證據)——這列的壞寫法本身就是用那條檢查定義的。自檢另驗情境欄寫的檢查 id 也出現在現成規則欄。
- **證據表**:`skills/kotlin-idioms/checks-catalog-wiring.tsv`(新增),每列一筆:型錄列編號、檢查、擋得到的壞例、官方頁或原始碼逐字一句、網址、查證日期。

## 範圍

1. **證據表**:2026-11-08 對全型錄 168 列宣稱接電的列,扣掉自帶證據的 39 列,剩 129 列逐列核對(六包代理讀官方頁、判不出的 10 列再派一席讀檢查器原始碼);判定擋得到的 117 列寫進證據表。
2. **型錄改動**:判定擋不到的 9 列(API-9、API-23、UI-11、UI-49、UI-95、ARCH-28、DATA-32、PERF-1、PERF-36)與預設關或等級是 Hint 的 3 列(UI-64、UI-80、TEST-25),共 12 列,那段補「(相關:…)」註記、退回只標批一;檢查預設關或預設等級是 Hint 的,那段補「(預設關:…)」註記。各列理由逐字附官方頁一句。
3. **型錄自檢**(`configs/ast-grep/kotlin-android/check.py`):宣稱接電的列,要不是自帶證據的列、就要在證據表有一筆;證據表的每一筆要對得到一列宣稱接電的列(不能留過期的證據);每筆的網址要是 https 開頭、日期是 YYYY-MM-DD、壞例與原文欄不空;自帶證據的列,情境欄寫的檢查 id 要出現在現成規則欄。原本的字面判斷照留(它算出「該不該標」),證據表是外面多一道看門。型錄自檢跑在測試總檔裡(`t_kt_catalog_*` 這組;CI 全套跑、推送前的關鍵字子集碰到型錄或 check.py 時跑),推送前掛鉤沒有另外呼叫 `check.py --catalog-only`;錯誤訊息寫要補哪一列、補到證據表。
4. **型錄〈輸入與口徑〉**:補一句宣稱接電要附證據、證據表在哪。
5. 不做:不拿壞例真跑 Android Lint(環境沒有);不改字面判斷的排除字表。

## 實務隱患

- 證據本身可能判錯(代理讀官方頁也會誤判):已排除靠工具驗證據對錯——自檢驗不了;用 RETIRE-IF 的真跑當最終解,並在〈天花板〉照實寫。
- 證據表與型錄分兩支檔會漂:自檢雙向比對(型錄有證據沒有、證據有型錄沒有都報)。
- 新增型錄列的人不知道要補證據:自檢錯誤訊息直接寫要補哪一列、補到哪支檔。
- 併發寫入不考慮:工具鏈單人、AI 依序操作。
- 已排除:金流:只改型錄與型錄自檢,不碰付款。
- 已排除:對外送出:不寄信、不呼叫外部服務,自檢只讀本機檔。
- 已排除:不可逆:全部是 repo 內的文字檔,退回提交即還原。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| lint 檢查管什麼由它的說明、範例與測試樣本定義 | Android Lint API 指南〈Testing〉與各檢查頁 | https://googlesamples.github.io/android-custom-lint-rules/api-guide.html |
| 型錄登記的 Android Lint、androidx、資安包檢查 | 官方檢查索引 | https://googlesamples.github.io/android-custom-lint-rules/checks/index.md.html |
| 型錄登記的 compose-rules 檢查 | compose-rules 規則頁 | https://mrmans0n.github.io/compose-rules/rules/ |
| 型錄登記的 Slack compose-lints 檢查 | Slack 規則頁 | https://slackhq.github.io/compose-lints/rules/ |
| warningsAsErrors 只讓 warning 以上擋建置 | AGP Lint DSL 說明 | https://developer.android.com/reference/tools/gradle-api/8.7/com/android/build/api/dsl/Lint |

字面判斷四次被打穿的紀錄:代碼審卷證 `governance/review-reports/code-型錄批一列也寫批四/`(r1 到 r3 各一條 major)與漏網帳(事後審查抓到 PERF-1、測試守不住口徑句)。全表核對的代理原始回報存卷證 `governance/review-reports/code-型錄接電要附證據/sweep/`(新增)。

## 驗收條款

- [S1] 當真型錄跑型錄自檢時,問題數 應 是 0,每列宣稱接電的列 應 是自帶證據的列或在證據表有一筆,證據表每筆 應 對得到一列宣稱接電的列 [test:t_kt_catalog_batch4_evidence]
- [S2] 當在型錄複本拿掉證據表的一筆、或替一列沒有證據的批一列加上接電段與批四標籤、或證據表多一筆型錄判成沒接電的列、或一筆網址不是 https 開頭時,型錄自檢 應 各報一個指名那一列的問題 [test:t_kt_catalog_batch4_evidence]
- [S3] 當讀真型錄時,核對判定擋不到的列 應 只標批一、那段 應 帶「相關」或「預設關」註記 [test:t_kt_catalog_batch4_evidence]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 真型錄與真證據表 | 型錄自檢 0 個問題 | 本計劃範圍 3 |
| S2 | 證據表刪掉 UI-24 那筆 | 報 UI-24 宣稱接電沒有證據 | 本計劃範圍 3 |
| S2 | 範圍 2 改完之後的型錄,UI-49 那段拿掉「相關」註記、通電批次改成「批一、批四(CI 範本:Android Lint)」 | 報 UI-49 宣稱接電沒有證據 | 本計劃範圍 3 |
| S2 | 證據表多一筆 TEST-23 | 報 TEST-23 的證據對不到宣稱接電的列 | 本計劃範圍 3 |
| S2 | 證據表 UI-24 那筆網址改成 http:// 開頭 | 報 UI-24 證據網址不合格 | 本計劃範圍 3 |
| S3 | 真型錄的 API-9、API-23、UI-11、UI-49、UI-95、ARCH-28、DATA-32、PERF-1、PERF-36 | 只標批一、原本接電那段帶「相關」 | 全表核對:官方頁或檢查器原始碼顯示這幾條檢查擋不到該列任何壞例 |
| S3 | 真型錄的 UI-64、UI-80、TEST-25 | 只標批一、原本接電那段帶「預設關」 | 官方頁或原始碼:ModifierNodeInspectableProperties 預設等級 Hint、ComposableLambdaParameterNaming 與 ExpensiveAssertion 預設關 |

## 回退

退回本計劃的提交:證據表、型錄註記與通電批次改動、型錄自檢的證據比對與新測試、〈輸入與口徑〉那一句、Systems/kotlin規則包 那幾行。卷證留著。

## 天花板

- 自檢只驗證據存在、跟型錄一致、格式對,驗不了證據本身對不對;證據是代理讀官方頁或原始碼得出的,讀錯就會錯。

REVISIT:2027-02-08 有消費專案接上 CI 範本之後,拿證據表每列的壞例真跑一次 Android Lint,沒命中的列退回只標批一、證據表那筆刪掉(真跑之前證據靠讀官方頁判)

## 審計修正紀錄
