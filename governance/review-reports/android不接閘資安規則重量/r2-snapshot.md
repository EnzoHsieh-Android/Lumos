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
decisions:
  - content: 出處不全列再查:API-14、TEST-31 等 8 列找到官方原文,改寫成只寫原文支持的主張、拿掉出處不全,引用它們的規則照舊在 rules-unwired/(沒量過誤報);API-36、UI-103 查不到、TEST-31 用顯示文字找節點那半跟官方建議相反,三條規則移出規則包;DATA-12 改成人裁列那半照舊
    id: d1
    context: 使用者要求每條納入的檢查都要有憑據,出處不明的不能把關;移掉之前先查明出處,有的就不用刪
    why_chosen: 派兩個沒看過先前結論的代理逐頁打開權威頁面讀,依原文判直接支持、部分支持、找不到、矛盾;部分支持的列刪掉沒出處的半句後,剩下的主張都有原文
    decided: 2026-11-08
    valid: true
---
# Android不接閘資安規則重量_計劃

> 白話:兩件事。①第一、二、三批共 19 條資安規則放在「只登記不擋」的目錄;其中命中數不夠、或沒量過樣本外的 7 條,換一批從沒用過的 GitHub 語料重量,看能不能升成推送前會擋。7 條都沒過升級條件,全部維持只登記;其餘 12 條照原理由不重量。②使用者要求「每條納入規則的檢查都要有憑據」:盤點後只登記那一級有 11 條規則掛在型錄出處不全的列上,逐頁再查出處,8 條找到官方原文、照原文改寫並保留,3 條查不到或跟官方建議相反、移出規則包。

PRIOR-ART: 量法沿用第一、二批(樣本外語料排除已出現過的 repo,升級條件命中 ≥20、誤報 ≤10%,一份樣本外單獨判,誤報比例=誤報÷判讀數、判不準只留在分母)與第三批補的兩條:每個 repo 最多抽一處、範例碼的判法寫死在準則裡。這次另外補兩條、只用在外部網址那條的第二份語料:刻意寫弱的資安教材與掃描器測試語料不進抽樣、同一份程式複製到不同 repo 只抽一處(第二批混合內容重量做過 fork 去重)。保留集只用一次的依據同第三批(Dwork 等人,https://ar5iv.labs.arxiv.org/html/1506.02629)。重量那 7 條不改形狀;出處補查那 2 條規則收窄形狀,是為了讓規則只報有出處的那半。
RETIRE-IF: Android Lint、compose-rules 或 Google 資安 lint 規則包出了同一種檢查 → 該條自寫規則撤掉、型錄改指現成檢查(同第一、二批)。

## 用詞

- **只登記不擋(不接閘)**:規則放在規則包的 `configs/ast-grep/kotlin-android/rules-unwired/`,推送前不會擋,只在型錄登記;**會擋**是放在 `rules/`,error 等級在推送前擋下新增的告警。**升級**:從 `rules-unwired/` 搬到 `rules/`。
- **樣本外**:規則形狀定案後另撈、排除先前出現過的 repo 的語料;判升級只看這一份,只用一次(**保留集**:定案後只用一次、不拿來調形狀的語料)。**升級條件**:樣本外命中 ≥20、誤報 ≤10%(第一、二批訂的)。
- **判讀代理**:派去逐處打開前後 20 行判真問題(TP)、誤報(FP)、判不準(UNSURE)的子代理;**判不準**不算真問題,誤報比例照第一、二批是誤報÷判讀數,判不準只留在分母。**抽 40 處**:命中多的每個 repo 最多抽一處、用固定隨機種子(任意選的固定數,讓抽法可重現;抽法存成 `experiment/sample.py.txt`)抽 40 處;**全判**:命中只有 20 多處時每一處都判,這時同一個 repo 會有多處(本計劃唯一不照「每個 repo 最多抽一處」的地方,〈天花板〉照實寫)。**命中**:ast-grep 報的比對筆數,同一行可能被報多次;另寫去重後的位置數。
- **型錄**:`skills/kotlin-idioms/checks-catalog.md`,每列的**實測狀態欄**記規則量過的數字,**通電批次欄**記這列由哪一批接上機械檢查;**出處不全**:型錄列名稱的標記,這列的標準寫法或壞寫法的錯因找不到權威原文直接支持;**型錄自檢**:規則包 `check.py` 對型錄格式與統計的檢查。**卷證**:`governance/review-reports/android不接閘資安規則重量/`,本計劃的實驗證據都在它的 `experiment/`。
- **exported**:AndroidManifest 裡畫面是否對其他 App 開放;沒開放的畫面外部 Intent 進不來。

## 範圍

1. **重量哪幾條**(命中不到 20 或沒量過樣本外;其中 kt-weak-cipher-suite 樣本內誤報 82%、kt-command-exec-nonliteral 收窄前樣本外誤報 70%,形狀本身誤報已高,重量只是確認命中數補足後結論):kt-insecure-tls-version(API-45,沒另撈樣本外)、kt-loadurl-external(API-49,14 處)、kt-weak-cipher-suite(API-50,6 處)、kt-secretkeyspec-literal-key(DATA-87,3 處)、kt-provider-openfile-traversal(DATA-89,6 處)、kt-db-on-external-files(DATA-93,1 處)、kt-command-exec-nonliteral(ARCH-90,收窄形狀後沒重量)。
2. **不重量的 12 條與理由**:
   - 樣本外命中已夠、誤報超過一成,誤報來自形狀分不出正當用法(外部協定強制、可信來源、範例碼、除錯判法沒認出、值不是秘密等),用同一形狀換語料不會變:kt-webview-debugging-enabled、kt-webview-file-access、kt-zip-slip、kt-static-iv、kt-object-input-stream、kt-xxe-documentbuilder、kt-weak-message-digest、kt-hardcoded-secret-name、kt-rsa-no-oaep、kt-jackson-default-typing。要改善得先改形狀(各批計劃的回頭條件)。
   - kt-weak-key-size 樣本外命中只有 6 處、誤報 4 處(外部協定強制 2、教學練習 2),量不夠,但 6 處裡誤報 4 處,換語料要降到一成以內得幾乎全是真問題,先不重量。
   - kt-biometric-no-crypto 樣本外 46 處抽判 40 處誤報 2,數字過條件,但第二批刻意不升:要不要綁加密物件看保護的是什麼(App 鎖畫面不一定要綁),形狀判不了,照原理由不升。
3. **型錄重量數字**:7 列的實測狀態欄補這次重量的數字;通電批次不變(仍是「未接」)。
4. **前兩批計劃的回頭條件**:第二批「換一批語料重量第二批 15 條不接閘規則」結案(第二批重量了 5 條、10 條照理由不重量),RETIRE-IF 前半段「重量仍沒有一條達到升級條件」註明已成立、交人裁;第一批「看三條不接閘規則能不能照升級條件升」補註(重量了 2 條、1 條不重量)。
5. **出處不全規則補查**(使用者 2026-11-08「每條納入規則的檢查,都必須有憑據、有來源」「移掉之前,先查明出處,有的就不用刪」):會擋、提示、覆核三級共 199 條規則掛的型錄列都有查證網址、沒有出處不全;只登記那一級有 11 條掛在 10 列出處不全的列上。派兩個沒看過先前結論的代理逐頁再查,結果見〈出處補查〉;照結果:
   - 8 列找到原文:拿掉出處不全、只寫原文支持的主張、來源欄補〔查證 2026-11-08:網址〕;通電批次改寫成跟其他不接閘規則同一句。引用它們的規則照舊在 `rules-unwired/`(還沒量過誤報,要升會擋另外量)。規則訊息照原文改寫;kt-async-await-immediately 拿掉「別的 scope 的 async 再 await」兩個樣式(維護者說它跟 withContext 不等價),kt-click-navigate-unguarded 拿掉 View 的 setOnClickListener 兩個樣式(View 的防護寫法官方沒給);兩條的壞例、好例跟著搬。
   - 3 條移出規則包:kt-error-by-message-string(API-36 查不到權威原文)、kt-compose-preview-no-theme(UI-103 官方範例有包主題、但沒說不包是錯的)、kt-compose-test-node-by-literal-text(TEST-31 用顯示文字找節點那半跟官方相反:官方先用文字等語意屬性、testTag 是最後手段)。規則與壞例好例樣本一起刪;`rules-unwired/compose.yml` 只剩這一條,整支刪掉。API-36、UI-103 兩列保留出處不全當參考、不再掛規則。
   - 測試:`t_kotlin_rulepack_unwired_dir` 原本寫死「API-14、TEST-31 標出處不全、引用的三條規則在 rules-unwired/」,改成新的事實;第 ⑥ 道允許「沒有規則掛在出處不全列上」(偵測能力由第 ⑩ 道的假規則守)。統計測試的寫死值照新數改。
   - 圖譜:[[Projects/Android寫法型錄逐列查證_計劃]] 的決策 d1(API-14、TEST-31 標出處不全)標成被本計劃 d1 取代;[[Systems/kotlin規則包]] 不接閘目錄那行改成 27 條並寫明移除的三條。

## 實驗

2026-11-08,ast-grep 0.51.1,規則照 repo 現行版本(不改形狀),設定檔 `configs/ast-grep/kotlin-android/sgconfig-unwired.yml`。語料用 GitHub 程式搜尋,每條一到三組查詢(`experiment/queries.tsv`),排除前三批語料出現過的 3796 個 repo(清單在 `experiment/excl-repos.txt`)。命中多的每個 repo 抽一處、種子 20261111、抽 40 處;命中 20 多處的全判。判讀代理乾淨脈絡,照 `experiment/judge-criteria.md` 判。

| 規則 | 新語料檔數 | 命中(去重位置;repo 數) | 判讀 | 誤報、判不準 | 結果 |
|---|---|---|---|---|---|
| kt-insecure-tls-version | 608 | 428(361;240) | 抽 40 | 11、0(27.5%) | 不接閘 |
| kt-loadurl-external | 511 | 190(190;153) | 抽 40 | 8、0(20%) | 不接閘(第二份語料另判,見下) |
| kt-command-exec-nonliteral | 290 | 111(111;72) | 抽 40 | 30、2(75%) | 不接閘 |
| kt-provider-openfile-traversal | 266 | 21(20;20) | 全判 21 | 8、1(38%) | 不接閘 |
| kt-db-on-external-files | 509 | 25(25;11) | 全判 25 | 4、0(16%) | 不接閘 |
| kt-secretkeyspec-literal-key | 480 | 14(14;6) | — | — | 命中仍不到 20,不接閘 |
| kt-weak-cipher-suite | 328 | 8(8;4) | — | — | 命中仍不到 20,不接閘 |

表頭:新語料檔數=撈到的 Kotlin 檔數;命中=ast-grep 比對筆數,括號是去掉同檔同行重複後的位置數與分布在幾個 repo;誤報比例=誤報÷判讀數(判不準只留分母)。TLS 的 11 處誤報:範例碼 4、只在 Android 5.0 以前走的相容路徑 3、外部設備強制 2、函式庫原始碼複本 1、已防護 1。Provider 的 21 處裡同一處被判了兩次(StickerContentProvider.kt:83),去重後是 20 處、誤報 8(40%)。判讀結果原文在 `experiment/judge-*.md`,抽到哪幾處在 `experiment/sample-*.txt`,語料清單在 `experiment/corpus-*.tsv`,抽法在 `experiment/sample.py.txt`(用它重跑三條抽 40 處的規則,抽到的位置跟 sample 檔一致)。

換算法的敏感度(設計審 r1 指出的獨立性問題,編排者重算,結論都不變):
- 排除刻意寫弱的資安教材與掃描器測試語料、同源複本合併:TLS 23.7%(席位人工把 9 份同源 HttpHelper 合成一處後約 31%)、指令執行 73.7%、Provider 42.1%、資料庫 16%,都仍超過一成。
- 資料庫那條:25 處只有 11 個 repo,每個 repo 算一次是 11 處、誤報 3,獨立命中本來就不到 20;其中 12 處真問題來自同一個 repo(LocalMusicHelper 把 asset 複製到外部目錄再讀寫),判讀代理自己標了有爭議,若改判誤報則是 16/25。4/25 的 Wilson 95% 區間約 6% 到 35%。
- 外部網址那條:8 處誤報裡 3 處只靠 repo 名帶 demo、example 判成範例碼;若 repo 名不算訊號,再排除教材,是 3/37 約 8%,會過條件。但 32 處真問題全是「未確認 exported」。這兩件事讓結論取決於判準,所以不靠這份語料決定,另用凍結的新判準撈第二份語料判。

### 外部網址那條:第二份語料(判準 v2)

- 判準先寫定再撈語料:`experiment/judge-loadurl-v2.md`,雜湊在 `experiment/judge-loadurl-v2.sha.txt`。跟 v1 差在四點:TP 要 manifest 證明畫面對外開放;範例碼只看檔案路徑、repo 名不算;刻意寫弱的資安教材與掃描器測試語料不進抽樣;同源複本只抽一處。
- 語料:4 組查詢 × 3 個檔案大小切片,排除前面所有語料出現過的 6147 個 repo(`experiment/excl-repos-v2.txt`),撈到 1384 支檔;命中 531 處,教材排除 27 處,同源合併後 406 處、366 個 repo;種子 20261112 抽 40 處;每處抓那個 repo 所有 AndroidManifest.xml(40 處都抓到)。
- 結果(`experiment/judge-loadurl-v2.md` 判讀原文在 `experiment/judge-loadurl-v2-result.md`):真問題 5、誤報 31、判不準 4,誤報比例 77.5%。誤報裡 24 處是畫面根本沒對外開放、已防護 2、可信來源 3、測試或範例碼 2。維持不接閘。

### 出處補查

| 型錄列 | 規則 | 查到的原文 | 判定 | 處理 |
|---|---|---|---|---|
| FLOW-14 | kt-asflow-not-cancellable | kotlinx.coroutines 1.9.0 `docs/topics/flow.md` Flow cancellation checks:asFlow 為了效能不做取消檢查,busy loop 要用 cancellable | 直接支持 | 保留 |
| CO-37 | kt-mutex-reentrant | Mutex KDoc:It is non-reentrant… still suspends the invoker | 直接支持(拆內部函式那句是慣用做法,原文只說不可重入) | 保留 |
| TEST-16 | kt-prod-reads-system-clock | Kotlin Clock 文件:It is not recommended to use Clock.System directly in the implementation | 支持規則本身(後果改成「測試寫不成確定的」) | 保留 |
| STATE-9 | kt-whilesubscribed-no-timeout | WhileSubscribed KDoc 預設 0;官方 state-production 範例與 Room codelab 都給 5 秒,codelab 說旋轉會重建畫面、重新收集 | 部分支持(後果照原文改) | 保留 |
| TEST-33 | kt-robolectric-legacy-looper | Robolectric LooperMode.Mode javadoc:LEGACY Deprecated,use PAUSED;paused looper 部落格 | looper 那半直接支持;固定 SDK 那半沒出處、刪掉 | 保留 |
| ARCH-3 | kt-click-navigate-unguarded | dropUnlessResumed KDoc 建議用它包 navigate;NavController 參考頁的 IllegalArgumentException | Compose 那半支持;View 那半沒出處、規則拿掉 View 樣式 | 保留 |
| API-14 | kt-async-await-immediately | IntelliJ 內建檢查 Redundant 'async' call;kotlinx.coroutines 議題 #1493 維護者:usually async{…}.await() is an error | 同 scope 那半支持;別的 scope 那例與維護者說法衝突、規則拿掉那兩個樣式 | 保留 |
| TEST-31 | kt-compose-test-node-by-index | 官方 Compose 測試 codelab:can't use the Node numbers shown in the tree to match them | 索引那半直接支持 | 保留 |
| TEST-31 | kt-compose-test-node-by-literal-text | 同一份 codelab:testTag 是 last resort;官方測試頁的典型範例就用 onNodeWithText | 跟官方相反 | 移除 |
| UI-103 | kt-compose-preview-no-theme | 官方範例有包主題、PreviewWrapper API 可以統一包,但沒有一句說不包是錯的 | 只有寫法示範 | 移除 |
| API-36 | kt-error-by-message-string | 只有 Throwable 參考頁說訊息可能是 null、可以在地化,沒講這個壞寫法 | 找不到 | 移除 |

兩個代理的原文報告在 `experiment/source-recheck-a.md`、`experiment/source-recheck-b.md`。

## 實務隱患

- 這批不改哪條會擋:會擋、提示、覆核三級沒動;只登記那一級少 3 條、2 條收窄形狀,消費專案推送前的行為不變。
- 已排除:金流:不碰付款,只改規則包的不接閘目錄、型錄文字、測試與圖譜筆記。
- 已排除:對外送出:不寄信、不呼叫外部服務(語料下載、manifest 抓取只在實驗階段)。
- 已排除:不可逆:全部是 repo 內的文字檔,退回提交即還原。
- 已排除:守衛面:不改任何會擋的規則與會擋的範圍,推送前的行為不變。
- 併發寫入不考慮:工具鏈單人、AI 依序操作。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 保留集只用一次、調過形狀的語料不拿來判 | Dwork 等人〈Generalization in Adaptive Data Analysis and Holdout Reuse〉 | https://ar5iv.labs.arxiv.org/html/1506.02629 |
| 舊版 TLS 是風險 | OWASP MASTG-TEST-0217 | https://mas.owasp.org/MASTG/tests/android/MASVS-NETWORK/MASTG-TEST-0217/ |
| 外部網址進 WebView 要驗 | Android 官方 unsafe URI loading 風險頁(型錄 API-49 的來源) | https://developer.android.com/privacy-and-security/risks/unsafe-uri-loading |
| 升級條件(命中 ≥20、誤報 ≤10%) | 第一、二批計劃的實驗節 | [[Projects/Android資安靜態檢查補齊第二批_計劃]] |
| Mutex 不可重入 | kotlinx.coroutines Mutex KDoc | https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-mutex/ |
| 實作裡不直接用系統時鐘 | Kotlin 標準庫 Clock 文件 | https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.time/-clock/ |
| 不能用節點編號找 Compose 節點、testTag 是最後手段 | 官方 Compose 測試 codelab | https://developer.android.com/codelabs/jetpack-compose-testing |
| Compose 導航點擊用 dropUnlessResumed 包住 | Lifecycle dropUnlessResumed KDoc | https://developer.android.com/reference/kotlin/androidx/lifecycle/compose/dropUnlessResumed.composable |

## 驗收條款

- [S1] 當真型錄跑型錄自檢時,問題數 應 是 0 [test:t_kotlin_catalog_rows_wired]
- [S2] 當讀型錄那 7 列的實測狀態欄時,這次補的命中、判讀、誤報數 應 跟卷證 `experiment/judge-*.md` 逐列數出的數與 `experiment/hits-*.json` 的筆數一致 [manual:逐列對照卷證判讀原文與命中檔筆數,設計審與代碼審各核一次]
- [S3] 當讀真規則包與型錄時,API-14、TEST-31 應 不標出處不全且有 2026-11-08 的查證網址,引用它們的兩條規則 應 在 rules-unwired/,移除的三條規則 應 不在規則包 [test:t_kotlin_rulepack_unwired_dir]
- [S4] 當跑規則包樣本自測時,收窄形狀的兩條規則 應 報壞例、不報好例(別的 scope 的 async、View 的點擊導航在好例裡) [test:t_kotlin_rulepack_samples]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 真型錄 | 型錄自檢 0 個問題 | 本計劃範圍 3、5 |
| S2 | API-45 那列 | 樣本外 428 處抽判 40 處誤報 11 | `experiment/judge-tls.md`、`experiment/hits-kt-insecure-tls-version.json` 428 筆 |
| S2 | ARCH-90 那列 | 樣本外 111 處抽判 40 處誤報 30、判不準 2 | `experiment/judge-cmd.md` |
| S2 | DATA-89 那列 | 樣本外 21 處全判誤報 8、判不準 1 | `experiment/judge-provider-db.md` |
| S2 | DATA-93 那列 | 樣本外 25 處全判誤報 4 | `experiment/judge-provider-db.md` |
| S2 | API-49 那列 | 第一份 190 處抽 40 處誤報 8;第二份(判準 v2)抽 40 處真問題 5 | `experiment/judge-loadurl.md`、`experiment/judge-loadurl-v2-result.md` |
| S3 | 真規則包 | 不接閘 27 條;kt-async-await-immediately、kt-compose-test-node-by-index 在 rules-unwired/;kt-error-by-message-string、kt-compose-preview-no-theme、kt-compose-test-node-by-literal-text 不存在 | 本計劃範圍 5 |
| S4 | `scope.async(Dispatchers.IO) { api.feed() }.await()` | 不報 | 本計劃範圍 5:維護者說跟 withContext 不等價 |
| S4 | `b.setOnClickListener { findNavController().navigate(R.id.action_x) }` | 不報 | 本計劃範圍 5:View 防護寫法官方沒給 |
| S4 | `coroutineScope { async { api.user() }.await() }` | 報 | IntelliJ Redundant 'async' call |

## 回退

退回本計劃的提交:型錄 7 列實測狀態的補句與 10 列出處補查的改寫、〈統計〉、三條規則與樣本(含 `rules-unwired/compose.yml`)、兩條規則的訊息與形狀與樣本、六條規則訊息、測試兩支的改動、第二批計劃的結案與 RETIRE-IF 補句與 2026-11-22 那條人裁回頭條件、第一批計劃的補註、第三批計劃的 status、逐列查證計劃 d1 的翻案與正文補註、Systems/kotlin規則包 那行、本篇。卷證留著。

## 天花板

- 每條只量了一份樣本外(外部網址那條兩份),誤報比例是 40 處以內的點估計。
- 資料庫那條獨立 repo 只有 11 個,12 處真問題的判法有爭議。
- 第一份語料的判讀看不到 manifest,外部網址以外的規則(Provider 等)也有「對外開不開放決定可不可利用」的情形,沒有逐處查。
- 誤報只量了命中裡的比例,漏報沒量。
- GitHub 程式搜尋每組查詢只回前 1000 筆、排序偏向特定 repo,寫死金鑰與弱加密套件「命中不到 20」受查詢數(各 2 組)限制。
- 出處補查是兩個代理各查一次,沒有第二輪交叉驗。

REVISIT:2027-05-08 每條不接閘規則要再量時,判準照外部網址那條的 v2 寫(範例碼只看路徑、排除教材、同源只抽一處、看得出可不可利用的抓 manifest),並給 Wilson 95% 區間
REVISIT:2027-05-08 資料庫那條換一批語料重量,判準先寫明「App 從 asset 複製到外部目錄的暫存資料庫」算不算真問題,獨立 repo 至少 20 個才判
REVISIT:2027-05-08 外部網址進 WebView 那條試第二版形狀(只報 manifest 裡 exported 或帶 intent-filter 的 Activity 裡的 loadUrl;規則包得先能讀 manifest),做不到就維持不接閘
REVISIT:2027-05-08 量一次漏報:挑兩條不接閘規則,在新語料裡找該報沒報的寫法,逐處判是不是形狀漏的
REVISIT:2027-05-08 寫死金鑰、弱加密套件兩條各加到 6 組查詢、用檔案大小切片撈,命中到 20 處才判
REVISIT:2027-02-08 出處補查保留的 8 列,另派一個代理用原始問題再查一次,跟這次結果不一致的列攤人裁

## 審計修正紀錄

- r1(2026-11-08,四席):21 條/blocking 5/誤報比例改回前兩批口徑(判不準只留分母);補去重位置數與換算法的敏感度;外部網址那條用凍結的 v2 判準另撈第二份語料重判(真問題 5/40);天花板每句配回頭條件、刪掉兩條修法對不上的 REVISIT;同輪加進出處補查(8 條保留、3 條移除)。
- 席報告與收貨紀錄:`governance/review-reports/android不接閘資安規則重量/`(r1-*.md、r1-intake.md)。
