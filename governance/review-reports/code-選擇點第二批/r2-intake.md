# r2 收貨紀錄

第二輪代碼審(tier high):正確性、邊界、通才、資源、合約與圖譜、架構對齊、資安,全 sonnet。材料凍在 `r2-snapshot.patch`(範圍 `6857e3d60..6cc9ad8c5`),另附修補鏡頭 `r2-repair.patch`(修前 eebb8459 → 修後 6cc9ad8c)、`r2-repair-binding.json`、`r2-behavior-cases.md`。

## 收貨

- 第一次派這輪時,資源席在臨時目錄複製多份 repo 做實驗把整台磁碟寫滿(席位目錄 13GB),其他席做不了實驗;那次七席全部作廢、結果不採用,清出空間後重派全新七席。派工詞加一條磁碟上限(每席一份 `git clone --shared`、修前版本在同一份副本裡開工作目錄、少於 20GB 停手、大檔用完即刪)。
- 七席全部交回才一次寫進卷證;報告從逐字稿取最後一則訊息存檔。report-normalize:七份都已是正規化格式。refcheck:合約席引的 `governance/residual-index.json` 不存在(它說明自己沒讀到、只是提到),其餘全對。
- quote-check:正確性、邊界、通才、合約全數錨定;資安與架構對齊是 clean 沒有引句;資源席 r1 的引句是計劃〈實務隱患〉的轉述、錨不到凍結快照,下面重現表機械重現。
- 圖譜鏡頭:派工鏡頭算 85 秒超過掛鉤時限,七席都讀了席位目錄的備份輸出;「這次新增的殘留」段算不出來,各席照實標未判定。資安與架構對齊兩席提到「派工附的鎖檔不存在、沒處理」,是鏡頭逾時說明裡的提醒,兩席都沒有刪任何東西。
- 席位臨時目錄 `/tmp/lumos-seat-work/code-選擇點第二批/` 收貨後已刪(刪前 lsof 確認沒有程序開著)。

## 重現表(編排者自己跑,不照抄席位)

| finding | 指令 | 輸出 | 判 |
|---|---|---|---|
| g1 c1 | 探針檔放 `if (a) { go() } else if (b) { x.let { show(it) } }`、沒大括號的 else-if、`if (a) if (b) x.let`、`for (…) if (…) x.let`、`if (a) when (c) {…}` 五行陳述,修前修後兩版 api.yml 各跑 `ast-grep scan --json=compact` | 兩版五行全命中 C-34(回傳值沒人用,換 also 必然等價) | HIT |
| b1 c2 | 同探針放 `LaunchedEffect(-1.coerceAtLeast(k))`、`LaunchedEffect(-1)`、`LaunchedEffect(-k)` | 修前三行都命中 C-36;修後 `-1.coerceAtLeast(k)` 不命中(key 隨 k 變卻被當常數) | HIT |
| b2 | `python3.14 -c 'int("9"*5000)'`;`_render_gov_choice` 餵 row `C-` 加 5000 個 9 | ValueError Exceeds the limit (4300 digits);新測試在拿掉位數上限時重現同一例外 | HIT |
| k1 | `git grep -n "REVISIT:2027" 6cc9ad8c -- docs/` | 計劃 2027-01-15、驗證筆記 2027-01-17 | HIT |
| r1 | 單行 3000 個 `a<n>?.b` 用修前、修後 nul.yml 掃 | C-33 輸出修前 98.7MB、修後 97.6MB(兩版都超過 64MB 上限落成驗不了) | HIT |

## 分組

1. **C-34 值的位置判法**(g1 major、c1):外層 if/when 自己掛在另一個控制結構分支底下時,沿用的 `value-pos` 判它「父節點不是陳述清單=值」,else-if 鏈、巢狀 if、if 裡的 when 與 try 都被當成值。這一組在 r1(c1)也出現過,這一輪又有 major。
2. **字面值負數判法**(b1、c2):r1 補負數時用文字開頭 `^[-+]\s*[0-9]` 判,`-1.coerceAtLeast(k)` 整段也是前綴運算式,被誤當常數。上一輪修補造成。
3. **依列號排序鍵**(b2):`int()` 的 4300 位上限,原有漏查。
4. **文件**(k1):r1 只改了驗證筆記的回頭看日期,計劃那條沒跟。上一輪修補造成。
5. **單行超長輸出**(r1):ast-grep 每個命中附整行原文,修前就有。

## 先查世界

- 第 1 組:PRIOR-ART: Kotlin 規格把沒有 else 的 if 當陳述、當值時才要求 else(控制流分析章把缺的 else 補成 Unit,https://kotlinlang.org/spec/pdf/sections/control--and-data-flow-analysis.pdf );Detekt 自訂規則判 when 是不是值看的是父節點種類(https://proandroiddev.com/kotlin-when-statement-when-expression-oh-my-or-how-we-created-our-custom-detekt-rule-6f27e80bedaf );就算有型別資訊,Kotlin 編譯器的 `usedAsExpression` 也有判錯的回報(https://slack-chats.kotlinlang.org/t/18902779/hello-i-encountered-a-case-where-usedasexpression-property-f )。採用:只看語法、只收「確定是值」的位置——外層 if/when/try 自己又在分支底下就一律不收,不做遞迴判斷(ast-grep 規則沒有型別,遞迴往外追的判法越補越多)。查詢詞:Kotlin if expression used as expression vs statement detection static analysis else if unused result;detekt isUsedAsExpression。
  方向:對 — 語法近似「不確定就不收」跟 Trivial Compiler Equivalence 排除必然等價壞法同方向;業界判值位置也是看父節點,連編譯器的型別判法都有誤判,不換成型別分析(來源同上兩個網址:Kotlin 規格控制流章、Detekt 自訂規則文)。
- 第 2 組:PRIOR-ART: 同第 1 組的做法,改看結構不看文字——前綴運算式的運算元本身要是數字常數節點(tree-sitter-kotlin 的 integer_literal、real_literal 等),跟本專案規則包其他字面值判法一致;不另查外部。
- 第 3 組:PRIOR-ART: Python 文件寫明 int() 對超過 4300 位的十進位字串丟 ValueError(https://docs.python.org/3/library/stdtypes.html#int-max-str-digits );採用排序前先限位數,列號由型錄產生、九位已綽綽有餘。
- 第 4 組:文件,不需外部依據。
- 第 5 組:計劃〈實務隱患〉已寫明單行上千個 `?.` 會因每個命中附整行原文而平方成長、靠 64MB 上限落成驗不了只提醒,跟第一版長串 `+` 同一類。

## 處置

| id | 去向 | 種類 | 改了哪裡 |
|---|---|---|---|
| g1 c1 | 折 | code | api.yml C-34 加 `value-direct`(value-pos 而且父節點不是控制結構分支),分支與 try 的外層一律要在 value-direct 才算;樣本補 else-if 鏈兩種、巢狀 if、for 裡的 if、if 裡的 when、if 裡的 try 六行 MISS,`val q = if … else if … x.let` 一行 MISS(語法判不完不收),`fun h() = if …` 一行 HIT;計劃範圍 2 同步 |
| b1 c2 | 折 | code | api.yml C-36、C-37 literal-arg 的負數改成「前綴運算式而且最後一個子節點是數字常數」;樣本補 `-1.coerceAtLeast(k)`、`-1.0.coerceAtLeast(k)` HIT、`+2.5` MISS、`-k` HIT;計劃範圍 2 同步 |
| b2 | 折 | code | `_render_gov_choice` 排序鍵限 1 到 9 位 ASCII 數字;`t_gov_stats_choice_by_row` 加 5000 位列號 |
| k1 | 折 | spec | 計劃 REVISIT 改 2027-01-17,跟驗證筆記一致 |
| r1 | 放行 | code | 計劃〈實務隱患〉已寫明這一類靠輸出上限落成驗不了只提醒,修前修後同量級(上表),不是這輪修補造成 |

另補一條席位提到、沒立條的測試缺口:邊界席說拿掉撤號守衛「頂格才認」的條件 `t_choice_table_batch2` 照綠。加了縮排那行的案例,並把四種怪寫法的斷言收緊成「恰好一行」那句看不懂訊息(原本只比「已撤列號」四個字,撤號衝突的訊息也含這四個字,分不出來)。

修完逐一改壞驗證:C-34 換回修前規則(樣本核對報 8 處不符、`t_choice_samples_batch2` 紅)、排序鍵拿掉位數上限(`t_gov_stats_choice_by_row` 5000 位那條紅)、撤號守衛拿掉頂格條件(`t_choice_table_batch2` 縮排那條紅)——全部翻紅。輸出量:1000 層 `x.let {` 巢狀修前修後都是 0.64MB;1000 段 else-if 鏈修前 34.5MB(每段都誤命中)、修後 0;1000 層巢狀 if 兩版都 0。
