# r3 收貨紀錄(末輪)

## 收貨三道

- quote-check:四份全數錨定。
- 席位暫存目錄:三席的 `/tmp/lumos-seat-work/情境決策點窮舉與壞寫法要叫得出/<席>/` 報告存進卷證後已刪(字面絕對路徑)。
- git status:repo 沒被席位動過。

## 機械重現

| 發現 | 命令 | 結果 | 判定 |
|---|---|---|---|
| IO(三席) | `grep -n "final val kotlinx.coroutines/IO " core-1.10.2.klib.api` | 第 1057 行,簽名註解 `kotlinx.coroutines/IO\|@kotlinx.coroutines.Dispatchers{}IO[0]`,是頂層擴充屬性 | HIT |
| 列舉值與伴生物件 | 同檔 grep `enum entry LAZY`、`final val Lazily`、`const val UNLIMITED` | 簽名註解是 `CoroutineStart.LAZY`、`SharingStarted.Companion.Lazily`、`Channel.Factory.UNLIMITED` | 改用簽名註解取名稱、外層、接收者 |
| fun interface | 同檔第 82 行 `abstract fun interface kotlinx.coroutines.flow/SharingStarted { // kotlinx.coroutines.flow/SharingStarted\|null[0]` | 宣告部分有 `fun`、`interface` 兩個宣告字;簽名註解直接給出名稱 | HIT |
| `// BAD` 標註 | `grep -rl '// BAD' samples/bad` | 233 支壞例檔有 199 支、536 行 | 改由規則改比對 `// BAD` 行 |
| TEST- 路徑(兩席) | 席位實跑 `_PITFALL_DIFF_TEST_PAT` | `src/test` 一律不出段、`androidTest` 會出 | HIT |

## 先查世界(跑滿上限的方向查證;使用者 2026-11-12 問「上網查了嗎」後補查)

- 名稱來源:kotlin-metadata-jvm 能從編譯後類別讀出原始碼名稱(https://kotlinlang.org/docs/metadata-jvm.html ),但要 JVM 執行環境、維護者說讀不到 `@JvmName` 這類註記(https://discuss.kotlinlang.org/t/announcing-kotlinx-metadata-jvm-library-for-reading-modifying-metadata-of-kotlin-jvm-class-files/7980 );零依賴家規下不採用。klib 文字清單沒有公開文法規格,權威是產生它的程式(https://pigweed.googlesource.com/third_party/github/JetBrains/kotlin/+/67ac90ce0868ee0c9cd08d72460f16efecded549/compiler/util-klib-abi/ ),格式一行是「宣告部分 // 簽名部分」。採用:只讀簽名部分,宣告部分的形狀(泛型、`fun interface`)整個不碰;解析靠真清單的固定測試釘住。
  方向:對 — 用官方 API 清單當母體(Android Lint 的 api-versions.xml 先例,r2 已引)不變;r3 改的是讀清單的哪一半。
- 改由驗證:Semgrep 以逐行 `ruleid:` 標註要求那一行被報(https://semgrep.dev/docs/writing-rules/testing-rules ),PMD 7.12 起驗違規的起訖行(https://docs.pmd-code.org/pmd-doc-7.17.0/pmd_userdocs_extending_testing.html )。採用:片段要落在壞例樣本既有的 `// BAD` 標註行、`--sg` 驗起訖行涵蓋那一行;單一識別字片段不准用範本背書。
  方向:對 — 兩個規則測試框架都以「標註過的那一行」為驗證單位。

## 分組與處置(35 條全部折入;使用者裁「折入後進實作」)

1. 可見寫法(g1、c1、b2、c8):只讀 klib 簽名註解;可見寫法兩種——類別鏈(去伴生物件段)與擴充屬性的接收者;列舉值有可見寫法;反向同步只比簡名與 `簡名(`(解 c5 的 `NonCancellable` 成員雜訊)。
2. TEST- 路徑(c2、b1):`TEST-` 只用 `src/test` 路徑、一律進表(寧可多列)。
3. JVM 補來源(g3、c3、b3):改成手列 `jvm-only.txt`,自檢核對右欄字串存在。
4. klib 解析(c4、b4、c9、b11 的 427):不解析宣告部分;總數實作時實測寫進統計。
5. 改由驗證(g2、b5、g8、b8、b10、c7):規則要片段在 `// BAD` 行、`…` 切段依序比、`--sg` 驗起訖行涵蓋;範本拿掉 T0 限制、改成要有那個對應檢查的壞寫法小節(同編號取聯集),單一識別字不准用範本;`<無片段>` 只准代碼審;`決策不問 <主表列>` 只看片段不看散文、主表列要是情境列的對應檢查。
6. 接法(a1–a5、g4、b6、b9、c10、g6):`_kt_sit_path_ok(rel, skip=frozenset())`,兩處內聯都改呼叫;參數名照鄰居 `text, rows`、`lumos=None` 自己載入;新增 `scan_ranges()` 不改 `scan()`;`scan_index` 用 `SCAN_FAILED` 哨兵分開沒掃與掃壞;`BAD_HEADING_RE` 與 `_fence_body` 照既有讀法;測試篩選要看得見反查問題;`lands_in` 補棧別提問表態閘。
7. 其他(c6 反向每列覆蓋、g7 D-4 證據樣式、b7 TEST-29 例子、b11 量法排除測試檔與頓號空白):逐條改。

## 跑滿上限

三輪 standard 上限到頂,r3 仍有 major。攤人裁(選項:折入後進實作/加開第四輪/拆成兩份)。使用者先問「上網查了嗎」,補查上節後再問,裁「折入後進實作」。記 cap-decision accept-risk,並寫跑滿回顧。
