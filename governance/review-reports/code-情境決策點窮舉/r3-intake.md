# code-情境決策點窮舉 r3 收貨紀錄

## 派工與收貨

- 七席(正確性、資源、邊界、合約、通才、架構對齊、資安),sonnet。全部讀修補審閱版 `r3-repair-review.patch`(763 行、9 支檔;修前 594f97e95 → 修後 6d5394398,剔掉卷證與帳本,見 `r3-repair-binding.json`),附待驗案例 `r3-behavior-cases.md`;合約席多給型錄與計劃全文。記帳的凍結材料是整條分支 `r3-snapshot.patch`(排除本迴圈卷證目錄,9166 行),各席快照填審閱版。
- 材料產法改了一處:前兩輪的快照與差異檔會被下一輪整份包進去(整份 15.8 萬行、修補差異 7.5MB),這輪起整份快照與修補差異都用 pathspec 排除本迴圈卷證目錄,被排除的檔逐一列在 binding 的 archive_only。
- 圖譜鏡頭:派工前暖過快取(85 秒),七席仍回報掛鉤沒附上固定席節點;資源、邊界、通才、合約讀了備援檔 `lens-r3.txt`,正確性沒讀。
- report-normalize:七席都已是正規化格式。quote-check(對 `r3-repair-review.patch`):正確性、邊界、合約、通才、架構對齊全數錨定;資源、資安是 clean、沒有引句。
- 席位紀律:資源席自述清自己的席位暫存時用了萬用字元刪除(只在它自己的席目錄內,沒波及別處),違反派工詞的字面絕對路徑規則;記在這裡,不影響它的發現。

## 機械重現

| 發現 | 命令 | 結果 | 判定 |
|---|---|---|---|
| c1、b1、k1、g1(巢狀括號註記) | 新測試 `kt-y/s0.kt`…`s5.kt`(巢狀括號、具名參數帶呼叫、泛型、`@[…]`、參數跨行、兩個註記同一行);把註記判讀改回一層括號的字面正規式跑 `-k bad_snippets_reach` | 6 條紅 | HIT |
| c2、b2、g2(行數對不上那道沒測試) | 席位在副本把那道改成 `if False` 照綠;新測試用假的去註解函式多吐一行 | 改壞後 1 條紅 | HIT |
| c2、b2、a2(非整格不還原 `\|`、還原寫兩份) | 新測試 ``x `a \| b` y``;拿掉還原 | 1 條紅 | HIT |
| b3(範本圍欄沒關外洩到下一組) | 新測試沒關的圍欄後接 `## T3`,片段只在 T3 | 修前判成落在 T2;修後報「沒關的圍欄」,改壞 1 條紅 | HIT |
| k2(WHY 代價只寫一半) | 讀 [[Systems/kotlin規則包]] 那行與型錄 D-4 例外證據樣式 | 屬實 | HIT |
| a1(測試手寫切節) | 讀 `t_kt_catalog_evidence_patterns` 與 check.py `_section` | 屬實 | HIT |

## 分組與處置(11 條:折入 11、放行 0)

1. 註記判讀(c1 major、b1、k1、g1):`_ANNOTATION_ONLY_RE` 只認一層括號,巢狀括號、泛型、`@[…]`、跨行參數的註記行不再被跳過,單獨一行的 // BAD 標到註記行(修前 `startswith("@")` 會跳過)。改成結構讀法:`_annotation_end` 逐字元配對同種括號(可跨行),`@名稱` 後面可接任意層 `<…>`、`(…)`,`@[…]` 整組配對,一行可放幾個註記;括號到檔尾都沒關就不當註記。字面正規式刪掉。
   - 出處清單:註記判讀只在 `_bad_lines` 一處;說法出處:`_bad_lines` docstring、計劃〈範圍〉`規則 <id>` 那條、〈依據來源〉——三處都改。反向案例:`@Composable fun A()`(註記後同一行接程式)仍標到那一行;括號沒關的 `@Foo(` 不當註記。
2. 沒測試守的分支(c2、b2、g2、a2):行數對不上那道用假的去註解函式(多吐一行)觸發;片段格非整格那條路補含 `\|` 的案例。`\|` 還原抽成 `_unpipe` 一支,`_snippets` 與 `_unreach_table` 都叫它(check.py 裡再沒有第二處還原)。
3. 範本圍欄沒關(b3):範本改由的核對先看範本檔寬鬆讀法還有沒有關不上的圍欄,有就直接報問題、不拿外洩的內文背書(沒關的圍欄照 CommonMark 吃到檔尾,後面各組都會被算進去)。席位標 ⚠ 交編排者:該擋還是該容忍——判擋,理由是判不準小節範圍時寧可要人關上圍欄;目前型錄範本改由 0 個,不會擋到現有資料。
4. 文件(k2):[[Systems/kotlin規則包]] 那行 WHY 的代價補 flatMapMerge,不選那格改寫成讀得通的句子(用 `lumos summary-line`)。
5. 測試切節(a1):`t_kt_catalog_evidence_patterns` 兩處切〈情境決策表〉都改走 check.py 的 `_section`,並拿掉同一支測試裡重複的 `_ktpack()`。席位 ⚠ 指出測試總檔其他測試本來就有兩派切法——這輪只改被點名的這一支,其他不在本案範圍。

## 修補因果(regression_set 不填)

- c1/b1/k1/g1:四席都兩版實跑(修前標到函式、修後標到註記行),屬這輪修補造成。但 `r3-repair-binding.json` 的 attribution_limits 寫明修前修後不是祖先關係、修補與排版沒有分開的中間提交,依 §3.1 修復歸因維持未判定,帳上不帶 `--regression-set`。
- c2/b2/g2/a2/a1/k2:修補一併帶進來的缺口,席位判原有漏查或修補不完整;b3 席位判原有漏查。

## 先查世界

- 註記判讀 PRIOR-ART:Error Prone 測試輔助 `DiagnosticTestHelper` 的標註檢查「註解下一行」(https://errorprone.info/api/latest/com/google/errorprone/DiagnosticTestHelper.html ),合併請求 4575 的例子裡標註與方法之間隔著 `@Override`、錯誤報在方法那一行(https://github.com/google/error-prone/pull/4575 );Semgrep 的 `ruleid:` 標下一行(https://semgrep.dev/docs/writing-rules/testing-rules );detekt 測試改走斷言發現的起訖位置(https://detekt.dev/kdoc/detekt-test-assertj/dev.detekt.test.assertj/-finding-assert/has-end-source-location.html )。採用:保留「標記標下一個語句」的形狀;起訖位置那一層本來就由 `--sg` 模式的起訖行涵蓋負責。排除:列舉註記寫法的字面正規式(這輪就是被它打穿)。
- 方向:對 — // BAD 標記這組連三輪出現、這輪有重大,依規則查方向。Semgrep 與 Error Prone 都用「註解標下一行」,detekt 用位置斷言,兩種都已在用(前者 `_bad_lines`、後者 `--sg` 起訖行);要換的是判讀的形狀——註記從字面列舉換成結構配對,不再為新寫法補例外。
- 範本圍欄 PRIOR-ART:CommonMark 沒關的圍欄由文件結尾關閉(同 r2〈先查世界〉的出處),所以外洩是規格行為,不是讀法錯;採用「判不準就報」。
- 其他組(未測分支、文件、測試切節):內部口徑對齊,照既有函式改,沒有另外上網查。

## 改壞驗證

`python3.14 <scratchpad>/mutate3.py <repo>`(副本 `mutate3.py.txt`):六道各改壞、跑 `-k bad_snippets_reach`、還原,六道都紅;原始輸出在 `r3-repro.txt`。
