# code-情境決策點窮舉 r2 收貨紀錄

## 派工與收貨

- 七席(正確性、資源、邊界、合約、通才、架構對齊、資安),sonnet。全部讀同一份修補審閱版 `r2-repair-review.patch`(1428 行、10 支檔;修前 8cd6d3c5e → 修後 594f97e95,剔掉第一輪卷證與帳本,見 `r2-repair-binding.json` 的 archive_only),另附待驗案例 `r2-behavior-cases.md`;合約席多給型錄與計劃全文。記帳的凍結材料是整條分支 `r2-snapshot.patch`(54391 行),各席快照填審閱版。
- 圖譜鏡頭:派工前暖過快取(一次 88 秒,超過掛鉤 45 秒上限),但七席都回報掛鉤沒附上固定席節點;資源、合約兩席讀了編排者事先存的備援檔 `/tmp/lumos-seat-work/code-情境決策點窮舉/lens-r2.txt`,正確性、通才沒讀。備援檔只有「沒附固定席節點」的參考段,沒有可逐條答的合約節點。
- report-normalize:邊界席第 3 行「…沒有 major。」被判成總結句藏更高等級;續談請該席自己改寫那一行(內容不變、等級字樣換成中文),編排者照它的原文替換那一行,其餘未動。其他六席已是正規化格式。
- quote-check(對 `r2-repair-review.patch`):正確性、資源、邊界、合約、通才全數錨定;架構對齊 3 句錨 2 句;資安席乾淨、沒有引句。
- 正確性席交回後另回一則:背景跑的 `-k kt_situation` 145 過、`-k kotlin_rulepack` 118 過(本機沒有 ast-grep,只跑靜態那半),不改它的發現。

## 機械重現

| 發現 | 命令 | 結果 | 判定 |
|---|---|---|---|
| a1(引句跨行) | `grep -n "keep_fenced=True 時也留圍欄" r2-repair-review.patch` | 第 392 行起,原文在 392–393 兩行(docstring 換行),quote-check 逐行比對不到 | HIT,採信 |
| c1(證據樣式測試紅) | `python3.14 scripts/test_lumos.py -k kt_catalog_evidence_patterns`(修後提交、修第二輪前) | 9 passed, 2 failed | HIT |
| s1、b2、k4、g2、c4(切行不一致) | 修補後新測試 `c.kt` 的換頁字元與 U+2028 案例;改回 `splitlines()` 跑 `-k bad_snippets_reach` | 改回舊寫法 14 條紅 | HIT |
| c5、g3(字串裡的 // BAD) | 新測試 `val q = "see // BAD"`;改回原始行判標記 | 1 條紅 | HIT |
| c2(@ 註記同一行有程式被跳過) | 新測試 `@Composable fun A(…)`;改回「@ 開頭就跳」 | 1 條紅 | HIT |
| b1、c3、k5、g1(沒關的圍欄丟最後一行) | 新案例(範本小節與 `t_kotlin_template_fence_parity` 的 keep_fenced=True);改回舊寫法 | 兩支各 1 條紅 | HIT |
| b3、a2(片段格尾巴雜字) | 新測試 `` `a` 垃圾 ``;改回只看開頭反引號 | 1 條紅 | HIT |
| k1(D-4 例外樣式收 flatMapConcat) | 讀型錄 D-4 證據樣式與 `_kt_sit_row_verdict` 只核作者宣告的那一段 | 屬實 | HIT |
| k2、k3、k6、k7、k8、a3 | 讀檔對照 | 屬實(k6 見下方分組 7 的裁法) | HIT |

## 分組與處置(23 條:折入 23、放行 0)

1. 測試漏網(c1,major):`t_kt_catalog_evidence_patterns` 在整份型錄數 `| D-n |` 開頭的列(新節〈叫不出的壞寫法〉也有)、又寫死 D-4 舊證據樣式,第一輪就紅到現在。
   - 出處清單:同形寫法搜 `^\|\s*D-\d+`、`startswith("| D-")`——產品碼 check.py 四處都先切到〈情境決策表〉節,不受影響;測試總檔三處,`t_kt_catalog_evidence_patterns` 兩處(數列、改壞用的列索引)改成只在〈情境決策表〉節裡找,另一處(第四批測試)本來就限在節內。D-4 斷言改成驗「跳脫直線已還原、flatMapLatest 與 `?.cancel()` 都比得到」,不再寫死整條樣式。
   - 編排者自己的漏:第一輪收尾回報「相關測試全綠」時跑的子集不含這一支(`-k kotlin_catalog`、`-k evidence_samples` 都沒命中它的名字)。這輪起改型錄後一律加跑 `-k kt_catalog` 整組(310 條)。
2. // BAD 標記判讀(c2、c4、c5、s1、b2、k4、g2、g3):共同根因是同一份壞例檔用兩種切行法、標記判斷又看沒剝字串的原始行。統一規則:原文、去註解(剝字串)、只去註解(保留字串)三份行一律只照 `\n` 切,行數不一致回問題;標記數在原文比在「只去註解」版本多,才表示至少一個標記在註解裡;單獨一行的標記只跳過「整行只有註記」的行。
   - 出處清單:`_bad_lines` 是唯一讀壞例標記的函式(`rg "_BAD_MARK_RE|_bad_lines"` 只有它與兩個呼叫端:`_rule_route_problems`、測試 `_reach_route_guards`);說法出處:函式 docstring、計劃〈範圍〉`規則 <id>` 那條、〈依據來源〉Semgrep 列——三處都改。反向案例:`// BAD-NEXT` 標續行、`@Foo` 整行註記仍跳過(既有案例保留,照綠)。
3. 圍欄本地複本(b1、c3、k5、g1、a1):`_visible_lines(keep_fenced=True)` 把沒關的圍欄最後一行當收尾標記藏掉,跟 scripts/lumos 那份不同。照 CommonMark 改成沒關的圍欄只藏開頭那行。a1(該不該直接改叫 scripts/lumos 那份):本地複本是刻意的(`template_sections` 在不載入 scripts/lumos 的情況也要用),既有 `t_kotlin_template_fence_parity` 就是守這份複本的對照測試;這次把它擴成 keep_fenced 兩條路都比,本地複本再跟主程式分家就會紅。
   - 出處清單:`_visible_lines` 呼叫端 `_fence_body`、`template_sections`、測試三處;docstring 兩處(`_visible_lines`、`_fence_body`)。
4. 片段格(b3、a2):整格恰好是一段反引號才取內文,其餘照整格原文(對不上反查單位就被報),兩種都做 `\|` 還原。出處:`_unreach_table` 是唯一讀這張表片段格的函式;docstring 一處。
5. D-4 例外寫法(k1、k7):例外文字補「順序不重要時 `flatMapMerge` 並行做完」、例外證據樣式加 `\bflatMapMerge\b`;樣本「搜尋框用 flatMapMerge」改 `bad main`、補 flatMapMerge 並行上傳的 alt-ok。取捨(搜尋框誤用 flatMapConcat/flatMapMerge 又答例外時推送前不提醒、只靠盲判)寫成 [[Systems/kotlin規則包]] 一行 WHY。
6. 理由文字(k3、k8):`Default` 理由照實寫「該不該寫死歸 CO-1,指 CO-39 只因片段寫到這個名稱」(歸屬不變,自檢規則要求被搜到的名稱指向片段所在那列);〈叫不出的壞寫法〉82 列套版前半句改成中性的「觸發字比對不到這段片段」,產表腳本副本 `sweep/gen_tables.py.txt` 同步。
7. JVM 專屬型別的成員(k6):編排者先補收了 6 個成員,隨後發現計劃〈天花板〉第 2 條明定「JVM 專屬的類別成員與屬性不收」(設計審過),補收違反設計,已還原;只在 `jvm-only.txt` 檔頭補一行指回那條規則。席位「沒交代」在清單檔頭這一處屬實。
8. 文件數字與排版(k2、a3):驗證紀錄測試數字改成這輪實跑值;`_fence_body` 前後補成兩個空行。

## 修補因果(regression_set 不填)

- 席位歸成「有證據的修復回歸」的:c2(修前修後兩版實跑,修前標到第 2 行、修後第 3 行)、c3/b1/k5/g1(修前讀碼或實跑回兩行、修後一行)、s1/b2/k4/g2(通才席兩版實跑:修前標記還在、修後消失)、b3/a2、k1、k2。
- 依 `r2-repair-binding.json` 的 attribution_limits:修前提交被 amend 成修後提交(非祖先)、修補與架構對齊重構(G6)沒有分開的中間提交;區間混入其他可達變更、沒有隔離證據,修復歸因維持未判定,所以帳上不帶 `--regression-set`。c1、c5/g3、k3、k6、k7、k8 席位自己判為原有漏查。

## 先查世界

- 圍欄 PRIOR-ART:CommonMark/GFM 規格「沒關的圍欄由文件結尾關閉」(https://gfm.docschina.org/Leaf%20blocks/Fenced%20code%20blocks.html ;討論 https://talk.commonmark.org/t/example-126-confusion-autoclosing-fence-blocks/4335 )。採用:沒關的圍欄內文算到檔尾,跟 scripts/lumos 的 `_visible_lines` 一致。
- 切行 PRIOR-ART:Python 議題 12855 記載 `str.splitlines()` 把 `\x0b`、`\x0c`、U+2028 等也當行界,`split("\n")` 不會(https://bugs.python.org/issue12855 )。採用:三份行一律 `split("\n")`,與 ast-grep 以 `\n` 計行一致。排除:改成三份都用 `splitlines()`——去註解函式只保留 `\n`,行數照樣對不上。
- 標記在註解裡 PRIOR-ART:Semgrep 規則測試的 `ruleid:` 標註寫成該語言的註解(https://semgrep.dev/docs/writing-rules/testing-rules );官方文件沒明寫字串裡的不算,這點是推論,所以用測試釘住行為而不是引為依據。
- 測試漏網、片段格、D-4 文字、理由、數字:內部口徑對齊,照既有函式與型錄先例改,沒有另外上網查。
- 方向:乙組(// BAD 標記)連兩輪出現,但這輪該組沒有 major,不觸發方向查核;改法從「逐個補例外」換成「三份行同一切法、標記用次數比對判是否在註解裡」的單一規則。

## 改壞驗證

`python3.14 <scratchpad>/mutate2.py <repo>`(副本 `mutate2.py.txt`):六道修補各改回舊寫法、跑對應測試、還原,六道都紅;原始輸出在 `r2-repro.txt`。第一輪 20 道守衛沒有被這輪改到的不重跑。
