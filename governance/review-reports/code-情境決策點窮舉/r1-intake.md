# code-情境決策點窮舉 r1 收貨紀錄

## 派工與收貨

- 七席(正確性、資源、邊界、合約、通才、架構對齊、資安),sonnet。找問題四席與架構對齊看程式包 `r1-code.patch`(1115 行),合約席看資料包 `r1-data.patch`(1204 行),資安席看整份 `r1-snapshot.patch`(8797 行;兩支官方 `.api` 與設計審卷證快速掃過)。整份核心 2319 行超過 1800 行上限,所以拆兩包。
- 圖譜鏡頭:派工詞都有 `LUMOS-IMPACT:` 標記,但這次鏡頭計算超時、沒附固定席節點(資源、通才、合約、邊界、正確性五席都回報這件事);各席改成自行讀 [[Systems/kotlin規則包]] 與 [[Systems/棧別提問表態閘]] 判斷,結論都是「不影響既有合約」。下一輪派工前先暖快取並確認有沒有附上。
- report-normalize:正確性、合約、資安三席最後一行總結含「max severity」字樣被誤認成宣告;經續談請三席各自改寫那一行(內容不變、只換字樣),編排者照它們的原文替換那一行,其餘未動。
- quote-check:六席全數錨定;邊界席 #9 引句「| Job0 | 無決策 | 內部實作類別,App 不直接用 |」錨不到程式包,是因為它在型錄(資料包)裡。資安席乾淨、沒有引句。

## 機械重現

| 發現 | 命令 | 結果 | 判定 |
|---|---|---|---|
| b6(Job0 引句) | `grep -c "Job0 \| 無決策 \| 內部實作類別" r1-data.patch` | 2 | HIT,採信 |
| c1–c6、b1、b2(守衛改壞照綠) | 編排者自己逐道改壞 check.py 跑 `-k bad_snippets_reach`、`-k api_decision_points`(修前) | 席位點名的改壞修前照綠 | HIT |
| b3、c7(// BAD 變體) | 席位的暫存樣本;編排者在新測試 `_reach_route_guards` 用同形樣本重現 | `// BAD-NEXT` 只標一行、字串裡的 `//` 被截、`// BADGE` 被當標記、非 UTF-8 崩 | HIT |
| g3、b5(why 被覆蓋) | 讀 `check()`:`lumos, why = load_lumos()` 之後 SARIF 迴圈 `got, why = …` | 屬實 | HIT |
| a1(圍欄另一份) | 讀 `_fence_body` 自己呼叫 `_fence_regions` 與嚴寬退讓 | 屬實 | HIT |
| s1(重編正規式) | 席位 profile:每個反查單位重編 `_kt_sit_rows_rx` | 屬實;一次 0.3 秒 | HIT,放行 |
| 資源席 408MB 對 60MB | 編排者重量 `/usr/bin/time -l … --catalog-only` | 有主程式編譯快取:0.9 秒、60MB;席位在乾淨複本沒快取:4.7 秒、約 400MB | 兩邊都對,表態改寫成兩種情況 |

## 分組與處置(29 條:折入 27、放行 2)

1. 守衛沒有測試(c1–c6、c8、b1、b2):每道守衛補一個「只有它會擋」的案例——範本三道、規則目錄與訊息編號、起訖行上界、`--sg` 索引接線(規則包複本裡整檔改成規則不報的寫法)、同名兩列、`…` 依序、只有 `…`、`\|` 還原、停用列、jvm 雜湊、錨點與下限各一半、jvm-only 兩道格式。修完逐道改壞跑測試,20 道都紅(命令見下)。
2. `// BAD` 標法(b3、c7):標記整字認(`//BAD`、`// BAD:`、`// BAD-NEXT`;`// BADGE` 不算);單獨一行的標記標下一個語句(含 `.`/`?.` 續行,跳過 `@` 註記);去註解改用 scripts/lumos 的 Kotlin 剝法(字串裡的 `//` 不截);壞例檔讀不了回問題、不崩。
3. 片段只有 `…` 或空白(b4):判不通過。
4. 重複列(g1):〈叫不出的壞寫法〉同一單位兩列要報。
5. 變數覆蓋(g3、b5):`check()` 的 lumos 載入原因改名 `lumos_why`。
6. 架構對齊(a1–a4):`_visible_lines` 補 `keep_fenced`(對齊 scripts/lumos)、`_fence_body` 改用它;`_norm_colon` 刪掉改用既有 `_norm`;決策表證據樣式與〈叫不出〉片段格都改走 `_snippets`;路徑正規化抽成 `_sample_abs`,反查與 `check()` 起訖行索引共用。修補時這支新函式漏了解析符號連結(macOS 暫存目錄 `/var` → `/private/var`),新測試當場抓到、已修。
7. 資料與文件(k1–k7、b6):補判 JVM 專屬 6 個型別與 TickerMode 兩個列舉值(jvm-only.txt 19 行);改正 `isClosed`、`isClosedForReceive/Send`、`CoroutineName`、`currentCoroutineContext`、`emit`、`Job0`、`SupervisorJob0` 的理由;`決策不問 代碼審` 加「同名異義:」出口(`last` 用它,`Default` 照舊指 CO-39——那段片段用的就是 `Dispatchers.Default`);代碼審理由改成寫明「看是不是犯了 <列>「<名稱>」」;規則改由理由改成不誇大;D-4「不適用時」補 `mapLatest`、`transformLatest` 與 `flatMapConcat` 依序做完、例外證據樣式加 `flatMapConcat`、對應樣本改 `bad main` 並補 alt-ok;筆記過期數字改正。
8. 放行:s1(反查每單位重編觸發字正規式;一次 0.3 秒、表放大四倍約 1.3 秒,不影響判定;要省得重寫 scripts/lumos 的切段入口,不值得);g2(規則報大節點時起訖行涵蓋偏寬;現行 5 個「規則」改由的規則都報行級節點,收窄要另定判準,等出現報整個函式的規則再處理)。

## 先查世界

- 守衛的測試覆蓋 PRIOR-ART:變異測試的判讀——條件改壞後測試照綠代表另一條分支沒被走過;`and`/`or` 組成的條件要各補一個「只有一邊成立」的案例才殺得掉(https://cran.r-universe.dev/muttest/doc/interpreting-results.html 、https://yrkan.com/course/module-03-test-design/mutation-testing/ );PIT 的定義「測試失敗=變異被殺、測試通過=變異存活」(https://orbilu.uni.lu/bitstream/10993/24473/1/PIT-Report.pdf )。採用:逐道守衛手動改壞驗紅(不引進變異工具,零依賴);錨點與下限兩半各補一案。
- `// BAD` 標法 PRIOR-ART:Semgrep 規則測試的逐行標註 `ruleid:` 標在被報那一行的上一行(https://semgrep.dev/docs/writing-rules/testing-rules ),跟壞例樣本既有的「單獨一行 `// BAD:`/`// BAD-NEXT` 標下一個語句」同形。採用:兩種標法都認、標記整字比對。
- 其他組(重複列、變數覆蓋、架構對齊、資料與文件)是內部口徑對齊,照既有函式與型錄先例改,沒有另外上網查。

## 改壞驗證命令

`python3.14 <scratchpad>/mutate.py <repo>`(腳本副本 `mutate.py.txt` 在本目錄):20 道守衛各改一處、跑對應測試、還原。修後結果 20 道全紅(「規則:目錄」第一次照綠,原因是測試用的規則訊息編號也對不上、被另一道先擋,改測試後兩道各自紅;「`--sg` 索引接線」第一次紅是因為規則包複本缺主程式而整支測試紅,補複本後重驗仍紅)。
