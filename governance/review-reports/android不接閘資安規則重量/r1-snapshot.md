---
type: project
status: done
created: 2026-11-08
updated: 2026-11-08
tags:
  - type/project
  - status/done
  - scope/stack-knowledge
related:
  - "[[Projects/Android資安靜態檢查補齊第二批_計劃]]"
  - "[[Projects/Android資安與崩潰靜態檢查補齊_計劃]]"
  - "[[Systems/kotlin規則包]]"
lands_in:
  - Systems/kotlin規則包
---
# Android不接閘資安規則重量_計劃

> 白話:第一、二、三批共 19 條資安規則放在「只登記不擋」的目錄。這次把其中命中數不夠、或沒量過樣本外的 7 條,換一批從沒用過的 GitHub 語料重量,看能不能升成推送前會擋。結果 7 條都沒過升級條件,全部維持只登記;其餘 12 條照原理由不重量。

PRIOR-ART: 量法沿用第一、二批(樣本外語料排除已出現過的 repo,升級條件命中 ≥20、誤報 ≤10%,一份樣本外單獨判)與第三批補的兩條:每個 repo 最多抽一處(避免同 repo 多筆不獨立)、範例碼只看路徑與 repo 名兩樣客觀特徵。保留集只用一次的依據同第三批(Dwork 等人,https://ar5iv.labs.arxiv.org/html/1506.02629)。形狀不動:這次只量、不改規則,規則檔與型錄的規則欄都沒改。
RETIRE-IF: Android Lint、compose-rules 或 Google 資安 lint 規則包出了同一種檢查 → 該條自寫規則撤掉、型錄改指現成檢查(同第一、二批)。

## 用詞

- **只登記不擋(不接閘)**:規則放在規則包的 `configs/ast-grep/kotlin-android/rules-unwired/`,推送前不會擋,只在型錄登記;**會擋**是放在 `rules/`,error 等級在推送前擋下新增的告警。**升級**:從 `rules-unwired/` 搬到 `rules/`。
- **樣本外**:規則形狀定案後另撈、排除先前出現過的 repo 的語料;判升級只看這一份,只用一次(**保留集**:定案後只用一次、不拿來調形狀的語料)。**升級條件**:樣本外命中 ≥20、誤報 ≤10%(第一、二批訂的)。
- **判讀代理**:派去逐處打開前後 20 行判真問題(TP)、誤報(FP)、判不準(UNSURE)的子代理;**判不準**不算真問題,誤報率這裡寫成「誤報+判不準」佔判讀數的比例。**抽 40 處**:命中多的每個 repo 最多抽一處、用固定隨機種子(任意選的固定數,讓抽法可重現)抽 40 處;**全判**:命中只有 20 多處時每一處都判,這時同一個 repo 會有多處(本計劃唯一不照「每個 repo 最多抽一處」的地方,〈天花板〉照實寫)。
- **型錄**:`skills/kotlin-idioms/checks-catalog.md`,每列的**實測狀態欄**記規則量過的數字,**通電批次欄**記這列由哪一批接上機械檢查;**型錄自檢**:規則包 `check.py` 對型錄格式與統計的檢查。**卷證**:`governance/review-reports/android不接閘資安規則重量/`,本計劃的實驗證據都在它的 `experiment/`。
- **exported**:AndroidManifest 裡畫面是否對其他 App 開放;沒開放的畫面外部 Intent 進不來。

## 範圍

1. **重量哪幾條**(命中不到 20 或沒量過樣本外,形狀本身誤報不高):kt-insecure-tls-version(API-45,沒另撈樣本外)、kt-loadurl-external(API-49,14 處)、kt-weak-cipher-suite(API-50,6 處)、kt-secretkeyspec-literal-key(DATA-87,3 處)、kt-provider-openfile-traversal(DATA-89,6 處)、kt-db-on-external-files(DATA-93,1 處)、kt-command-exec-nonliteral(ARCH-90,收窄形狀後沒重量)。
2. **不重量的 12 條與理由**:
   - 樣本外命中已夠、誤報超過一成,誤報來自形狀分不出正當用法(外部協定強制、可信來源、範例碼),用同一形狀換語料不會變:kt-webview-debugging-enabled、kt-webview-file-access、kt-zip-slip、kt-static-iv、kt-object-input-stream、kt-xxe-documentbuilder、kt-weak-message-digest、kt-hardcoded-secret-name、kt-rsa-no-oaep、kt-jackson-default-typing。要改善得先改形狀(各批計劃的回頭條件)。
   - kt-weak-key-size 樣本外命中只有 6 處,但 6 處裡誤報 4 處,換語料要降到一成以內得幾乎全是真問題,先不重量;誤報來自測試用假憑證這類形狀分不出的寫法。
   - kt-biometric-no-crypto 樣本外 46 處抽判 40 處誤報 2,數字過條件,但第二批刻意不升:要不要綁加密物件看保護的是什麼(App 鎖畫面不一定要綁),形狀判不了,照原理由不升。
3. **型錄**:7 列的實測狀態欄補這次重量的數字;通電批次不變(仍是「未接」)。
4. **前兩批計劃的回頭條件**:第二批「換一批語料重量第二批 15 條不接閘規則」結案(第二批重量了 5 條、10 條照理由不重量),RETIRE-IF 那句的事實一併更正;第一批「看三條不接閘規則能不能照升級條件升」補註(重量了 2 條、1 條不重量)。

## 實驗

2026-11-08,ast-grep 0.51.1,規則照 repo 現行版本(不改形狀),設定檔 `configs/ast-grep/kotlin-android/sgconfig-unwired.yml`。語料用 GitHub 程式搜尋,每條一到三組查詢(`experiment/queries.tsv`),排除前三批語料出現過的 3796 個 repo(清單在 `experiment/excl-repos.txt`)。命中多的每個 repo 抽一處、種子 20261111、抽 40 處;命中 20 多處的全判。判讀代理乾淨脈絡,照 `experiment/judge-criteria.md` 判。

| 規則 | 新語料檔數 | 命中(repo 數) | 判讀 | 誤報 | 結果 |
|---|---|---|---|---|---|
| kt-insecure-tls-version | 608 | 428(240) | 抽 40 | 11(27.5%) | 不接閘 |
| kt-loadurl-external | 511 | 190(153) | 抽 40 | 8(20%) | 不接閘 |
| kt-command-exec-nonliteral | 290 | 111(72) | 抽 40 | 30,判不準 2(80%) | 不接閘 |
| kt-provider-openfile-traversal | 266 | 21(20) | 全判 21 | 8,判不準 1(43%) | 不接閘 |
| kt-db-on-external-files | 509 | 25(11) | 全判 25 | 4(16%) | 不接閘 |
| kt-secretkeyspec-literal-key | 480 | 14(6) | — | — | 命中仍不到 20,不接閘 |
| kt-weak-cipher-suite | 328 | 8(4) | — | — | 命中仍不到 20,不接閘 |

表頭:新語料檔數=撈到的 Kotlin 檔數;命中=規則在這份語料報的處數,括號是分布在幾個 repo;誤報欄的百分比是「誤報+判不準」除以判讀數。TLS 的 11 處誤報:範例碼 4、只在 Android 5.0 以前走的相容路徑 3、外部設備強制 2、函式庫原始碼複本 1、已防護 1。判讀結果原文在 `experiment/judge-*.md`,抽到哪幾處在 `experiment/sample-*.txt`,語料清單在 `experiment/corpus-*.tsv`。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 保留集只用一次、調過形狀的語料不拿來判 | Dwork 等人〈Generalization in Adaptive Data Analysis and Holdout Reuse〉 | https://ar5iv.labs.arxiv.org/html/1506.02629 |
| 舊版 TLS 是風險 | OWASP MASTG-TEST-0217 | https://mas.owasp.org/MASTG/tests/android/MASVS-NETWORK/MASTG-TEST-0217/ |
| 外部網址進 WebView 要驗 | Android 官方 unsafe URI loading 風險頁(型錄 API-49 的來源) | https://developer.android.com/privacy-and-security/risks/unsafe-uri-loading |
| 升級條件(命中 ≥20、誤報 ≤10%) | 第一、二批計劃的實驗節 | [[Projects/Android資安靜態檢查補齊第二批_計劃]] |

## 實務隱患

- 這批不改規則、不改哪條會擋,消費專案推送前的行為不變。
- 已排除:金流:不碰付款,只改型錄文字與圖譜筆記。
- 已排除:對外送出:不寄信、不呼叫外部服務(語料下載只在實驗階段)。
- 已排除:不可逆:全部是 repo 內的文字檔,退回提交即還原。
- 已排除:守衛面:不改任何規則與會擋的範圍,推送前的行為不變。
- 併發寫入不考慮:工具鏈單人、AI 依序操作。

## 驗收條款

- [S1] 當真型錄跑型錄自檢時,問題數 應 是 0 [test:t_kotlin_catalog_rows_wired]
- [S2] 當讀型錄那 7 列的實測狀態欄時,這次補的命中、判讀、誤報數 應 跟卷證 `experiment/judge-*.md` 的總計與 `experiment/hits-*.json` 的筆數一致 [manual:逐列對照卷證總計與命中檔筆數,設計審與代碼審各核一次]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 真型錄(7 列補了重量數字) | 型錄自檢 0 個問題 | 本計劃範圍 3 |
| S2 | API-45 那列 | 樣本外 428 處抽判 40 處誤報 11 | `experiment/judge-tls.md` 總計、`experiment/hits-kt-insecure-tls-version.json` 428 筆 |

## 回退

退回本計劃的提交:型錄 7 列實測狀態的補句、第二批計劃那條回頭條件、本篇。卷證留著。

## 天花板

- 每條只量了一份樣本外,誤報率是 40 處以內的點估計。
- 資料庫那條真問題有 12 處來自同一個 repo,樣本不獨立。
- 判讀代理看不到 manifest,外部網址那條的真問題都是「未確認 exported」。
- 誤報只量了命中裡的比例,漏報沒量。

REVISIT:2027-05-08 TLS 版本那條試第二版形狀(外層有 Build.VERSION.SDK_INT 小於 21 的判斷就不報),用新語料重量,過升級條件才升
REVISIT:2027-05-08 外部網址進 WebView 那條試第二版形狀(同函式有 scheme 或 host 比對就不報),用新語料重量,過升級條件才升
