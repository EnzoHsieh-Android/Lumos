# r2 收貨紀錄

## 收貨三道

- report-normalize:四份都已是正規化格式。
- quote-check:四份全數錨定。
- refcheck:四份 missing 0、out_of_range 0。
- git status:repo 沒被席位動過(只有本會談的 lumos 帳檔)。

## 機械重現(關鍵發現)

| 發現 | 命令 | 結果 | 判定 |
|---|---|---|---|
| c1/b1/g2 | 照 r2 快照的 JVM 補來源規則試抽 1.10.2 `.api`(編排者自寫腳本) | `isActive` → `active`、`getRECOVER_STACK_TRACES` → `rECOVER_STACK_TRACES` 等假名稱 | HIT |
| g1/c5/b2 | 讀 `samples/bad/kt-map-await-deferred/` 壞例檔第 4 行 | 含 `async` 而規則只管 map 配 await;名稱層級背書會讓 `async` 過關 | HIT |
| b4 | 讀型錄 D-13 的對應檢查 STATE-14 壞寫法欄 | 沒有反引號片段,原口徑不產生單位 | HIT |
| c7/b5/g3 | 席位重數(r2 正確性、邊界各自) | 只試 `app/src/test` 口徑 184 個、叫不出 103 個 | HIT(兩席一致),計劃改寫成設計時的數並寫明口徑 |
| 母體過濾 | 編排者試抽:klib 名稱「JVM 清單全文找不到就丟」 | 誤丟 `coroutineContext`、`immediate`、`asCoroutineDispatcher` | 改成只對標了 `// Targets:` 的宣告過濾:427 丟 4(`asCoroutineDispatcher`、`asPromise`、`awaitAnimationFrame`、`promise`),`asCoroutineDispatcher` 是 `@JvmName` 改名造成的誤丟,寫進天花板 2 並要求實作時人工核差集 |
| 升版案例 | `grep -c 'fun .*associate'` 1.10.2 與 1.11.0 的 klib 清單 | 0 對 8 | HIT,S1 案例成立 |

## 分組與處置(37 條全部折入)

1. 母體抽法(g2、c1、c2、b1、b10、g8 授權):JVM 補來源只補頂層函式與類別、不還原讀取函式與成員;klib 名稱只對標了平台的宣告才拿 JVM 清單過濾;排除清單兩邊對齊(`internal`、`debug`、`$`、`-impl`、底線開頭、列舉合成成員、具名伴生物件);寫明 klib 逐行解析步驟與 UTF-8;母體目錄附說明檔與 Apache-2.0 授權聲明。
2. 改由驗證(g1、c4、c5、c6、b2、b6、b7、a6):〈API 決策點〉不再自己背書改由,`決策不問` 指向主表列(該列壞寫法欄要整字出現名稱)或寫代碼審;改由只在片段層級驗——剝註解字串、折空白、整字邊界;範本要片段出現在 `### 壞寫法:<對應檢查>` 小節圍欄內文(編號後接空白或行尾,冒號全形半形都認);`--sg` 用節點起訖行涵蓋片段行、掃描失敗判問題。
3. 歸屬與同步(c3、c8、b3、b11、b12、g4):歸屬項可並列(`D-5、D-6、撞名 D-35`),`無決策` 只能單獨;名稱另記可見寫法(object 與伴生物件成員寫 `外層類別.名稱`)與 `名稱(` 比對形狀,正反向、停用字都拿三種形狀比;歸屬欄格式錯一律報。
4. 反查單位(b4、b5、c7、g3):沒有片段的(情境列, 對應檢查)算一個 `<無片段>` 單位;`TEST-` 試 `src/test` 與 `src/androidTest` 兩個路徑;數字寫明口徑。
5. 接法(a1、a2、a4、a5、a7):路徑篩選抽成 scripts/lumos 的 `_kt_sit_path_ok`,推送端與反查共用(不做清單改寫為「只動這一處、行為不變」);兩張新表各一支讀表函式;簽名收主表列、lumos 載入失敗回 `<api>`;`--sg` 重用既有掃描、`scan()` 多回起訖行;新節放〈統計〉之前。
6. 命名與位置(a3):母體目錄改名 `coroutines-api/`,加 `coroutines_api_dir()`。
7. 量法與撤除條件(g7、b8、b9):Now in Android 釘提交 sha;補字前後量檔數比例、情境段數、(段,列)配對數三個數,配對數增加超過 20% 就停;RETIRE-IF 第一條改用統計段印得出的「作者判適用數」。
8. 措辭與回頭條件(g5、g6、c9、c10):推送前閘在功能分支可能只跑子集,改寫成「推主線與 CI 全套一定跑到」;加 2027-02-12 升版回頭條件;拿掉不可重現的 1.11.0 計數;母體檔會觸發併發型樣寫進實務隱患,不加黑名單。

## 先查世界

- 母體抽法(第二次被打穿)PRIOR-ART:Android Lint 的 API 檢查靠 SDK 隨附的 `api-versions.xml`(平台 API 資料庫)逐一檢查呼叫(https://android.googlesource.com/platform/development/+/8ec5006 );Android 建置後來因資料庫收了不適用的 mainline API 造成誤報,改成過濾掉那批(https://gitlab.e.foundation/e/os/android_build_soong/-/commit/67cf60e7c5bf29db9dec52c575d0250568371a18 )。採用:用官方清單當母體、只收適用平台的名字(klib 的平台標註)、不從編譯後形狀還原名字。
  方向:對 — 用官方 API 清單當窮舉母體是成熟做法(Android Lint 兩個來源);兩輪被打穿的是「從 JVM 編譯形狀還原名字」這個形狀,已換成以 klib 原始碼名稱為主、只用平台標註過濾。
- 改由驗證(第二次被打穿)PRIOR-ART:Semgrep 規則測試以逐行 `ruleid:` 標註要求那一行一定被報(https://semgrep.dev/docs/writing-rules/testing-rules ),ast-grep 規則測試的 valid/invalid 同理(https://ast-grep.github.io/guide/test-rule.html )——驗證單位都是「一段程式」,沒有「名稱層級」背書。採用:改由只在片段層級驗;API 名稱指向主表列,由那一列的片段走同一條驗證。
  方向:對 — 兩個規則測試框架都以單段程式為驗證單位;被打穿的是「名稱層級背書」這個形狀,已拿掉。
- 其他六組是內部口徑對齊(接法、命名、量法、措辭),照既有程式與自檢先例改,沒有另外上網查。

## 折入後鏡像核對

派一個 sonnet 代理只讀改寫前後、四份席報告與本紀錄,回報八條,全部修:PRIOR-ART 還是「只留 JVM 也出現的」舊說法(改成只有標平台又找不到的才丟);klib 排除清單句子斷裂、缺 `debug`、`$`、`-impl`、底線開頭(補齊,跟 JVM 那邊同一組);歸屬格式還寫「冒號」(改成只用頓號與半形空白);「並把 S4 那兩種寫法」指錯條款(改成 S5,並寫明改標決策不問時 S5 怎麼驗);`bad_snippet_reach_problems` 缺規則與掃描索引參數(補 `rules`、`scan_index`);`asCoroutineDispatcher` 會不會被 JVM 補回來沒講(寫明 `@JvmName` 改名補不回原名);「四種歸屬」實際列了五種(統一成五種);`決策不問 代碼審` 沒核主表是否真的沒寫到(補一條核對與 S1 案例)。
