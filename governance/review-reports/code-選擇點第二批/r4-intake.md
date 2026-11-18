# r4 收貨紀錄

第四輪代碼審(tier high,上限三輪跑滿後人裁加開的一輪,cap-decision extra-round 與跑滿回顧在第三輪帳本提交):正確性、邊界、通才、資源、合約與圖譜、架構對齊、資安,全 sonnet。材料凍在 `r4-snapshot.patch`(範圍 `6857e3d60..59c410383`),另附修補鏡頭 `r4-repair.patch`(修前 87093835 → 修後 59c41038)、`r4-repair-binding.json`、`r4-behavior-cases.md`。派工詞改成只放標記行(LUMOS-SEAT、LUMOS-IMPACT、角色卡與架構目標標記)加一句「先讀完 scratchpad 裡自己那份完整派工詞照做」,完整派工詞由 mk_b2_seats_r4.py 產生、內容同第三輪格式;七席都照完整派工詞的格式交回。

## 收貨

- 七席全部交回才一次寫進卷證;報告從逐字稿取最後一則訊息存檔。
- report-normalize:七份都已是正規化格式。refcheck:全對。seat-check:派工單材料欄沿用第三輪格式,工具判 vacuous 豁免。
- quote-check:正確性、邊界、通才、合約全數錨定;資源、架構對齊、資安是 clean 沒有引句。
- 圖譜鏡頭:七席的掛鉤都附了 `LUMOS-LENS:這次沒附固定席節點`(五席註明鏡頭計算超時),派工詞附了備份輸出位置。正確性、通才、合約、資安讀了備份逐條判固定席;邊界、資源、架構對齊照實寫沒讀備份、固定席未判定。
- 席位臨時目錄:資安、架構對齊、邊界自己刪了;其餘收貨後由編排者刪(刪前 lsof)。

## 重現表(編排者自己跑,不照抄席位)

| finding | 指令 | 輸出 | 判 |
|---|---|---|---|
| g1 c3 b1 | `kp.choice_tables` 合成型錄 `已撤列號:C-40`,表列寫 `C-040`、`C-４０`(rules_dir=False);再用真規則目錄複本,表列與規則 id 都寫 `C-040` 或 `C-４０`、指向新規則檔 | 合成型錄兩種都回 `[]`;真規則目錄兩種也都回 0 個問題(只改表列不改規則 id 時才會被「規則 id 要等於列號」擋,這是架構對齊席的反例,只擋住一半) | HIT |
| c1 | 編排者 scratchpad 的 r4_mutsweep.py:api.yml 的 C-34 到 C-37 每一行(子句鍵)刪掉、行內 `{kind: …}` 與 `matches`/`regex`/`stopBy` 每個選項拿掉,各跑一次 `choice_sample_problems` | 修後原樣 132 項變異 47 項照綠;C-34 的 `value-pos` 與第 4 個 `all` 的 `nthChild`(最後一個陳述)、when 那支的 `matches: value-direct` 都在照綠清單裡 | HIT |
| c2 | 同上 | C-36 `literal-arg` 拿掉 `{kind: interpolated_expression}` 照綠;C-37 那份同(由 C-36 與 C-37 literal-arg 一字不差的比對守) | HIT |
| k1 | 讀計劃〈範圍〉2 C-34 那段 | 只寫 if/when 分支,沒有 try/catch;型錄與 api.yml 已收 try、catch | HIT |
| (編排者擴掃) | 同 c1 的掃描 | 照綠清單另有:註解排除(`line_comment`、`multiline_comment`)、四條規則各自比對方法名的 `regex`(let、combine、LaunchedEffect、remember)、C-35 的 `inside: {kind: call_expression}`;nul.yml 掃 8 項照綠 1 項 | HIT |

## 分組

1. **規則子句沒有樣本守住,第三輪只掃了固定行號的一部分**(c1 major、c2 major,另編排者擴掃):第三輪的逐條拿掉掃描只挑了 C-34 `value-used` 選項行與 literal-arg 清單,沒掃行內選項、`value-pos`、方法名比對與註解排除;樣本核對只看有標記的行,拿掉方法名比對後的誤命中落在沒標記的行上,照綠。C-34 這一組連四輪都出現(r1 c1、r2 g1、r3 c1、r4 c1)。
2. **撤號列號只收緊了撤號那一側**(g1 major、c3 minor、b1 minor):第三輪 b1 把撤號那行改成只認 `C-[1-9][0-9]*`,表列號還是 `C-\d+`,表列與規則 id 一起寫成 `C-040` 或全形數字就繞過。同一族連兩輪(r3 b1、r4 g1)。
3. **計劃措辭**(k1):型錄第三輪補了 try,計劃範圍 2 沒跟。

## 先查世界

- 第 1 組:PRIOR-ART: Semgrep 規則測試(https://semgrep.dev/docs/writing-rules/testing-rules )每個 `ruleid:` 標注要有命中、沒有標注的行有命中也算失敗——比本 repo 的樣本核對嚴(本 repo 只看有標記的行);變異分析(https://www.fuzzingbook.org/html/MutationAnalysis.html )把存活變異分成「測試不夠」與「等價變異」兩類,等價的不補測試。採用:掃描改成全面(每一行與行內每個選項),存活的逐項分類,不等價的補一行樣本;等價的(父節點種類本來就固定的多餘限定)在下面列出理由不補。不採:把樣本核對改成 Semgrep 那樣「沒標的命中也算失敗」——量過現有樣本 236 個命中有 128 個沒標(多是第一批規則在別的樣本行順帶命中),全面改要重標第一批樣本、會動到釘住行指紋的樣本檔,範圍超出這條分支。查詢詞同第三輪。
  方向:對 — 判法照舊只看語法樹;缺的是掃描涵蓋面,不是判法(同上兩個網址)。
- 第 2 組:PRIOR-ART: 同第三輪 Python `re` 文件 `\d` 收 Unicode 十進位數字(https://docs.python.org/3/library/re.html#regular-expression-syntax );這次照「同族一次掃完」把表列號(選擇點表與乾節點表)也收緊成 `[CA]-[1-9][0-9]*`,規則 id 與樣本標記本來就要等於表列號,表列號收緊後跟著收緊,不另改。
- 第 3 組:文件,不需外部依據。

## 等價存活(補完樣本後重掃仍照綠,判等價不補)

- C-34 第 4 個 `all` 的 `kind: statements`、C-34 與 C-35 的 `kind: navigation_expression`、C-36 與 C-37 外層的 `kind: call_suffix`、`kind: call_expression`、literal-arg 的 `kind: value_argument`、nul.yml C-33 的 `inside: {not: {kind: navigation_expression}}`:限定的節點種類在 Kotlin 語法樹裡本來就固定(navigation_suffix 的父節點一定是 navigation_expression,value_arguments 的父節點一定是 call_suffix,依此類推),拿掉不改命中。
- literal-arg 的 `nthChild: {position: 1, reverse: true}`:value_argument 只有具名引數才有多個具名子節點,名字是識別字、不會是字面值。
- 帶號數字的 `regex: '^[-+]'`:其他前綴運算子(`!`、`++`、`--`)接數字常數編不過;前綴是標註(`@Ann 1`)時拿掉 regex 反而也當常數,仍是常數。
- 字串插值的 `stopBy: end`:插值節點是 string_literal 的直接子節點,往下找一層與找到底結果相同(正確性席也找不到會改變結果的輸入)。
- C-37 literal-arg 區各項:由 C-36 樣本加「C-36 與 C-37 literal-arg 一字不差」比對測試守。

## 處置

| id | 去向 | 種類 | 改了哪裡 |
|---|---|---|---|
| c1 c2 | 折 | code | 樣本 choice-batch2.kt 補 C-34 六行(行尾 line comment 與 block comment 在最後一個陳述之後各一行 HIT、lambda 與 if 區塊非最後一個陳述各一行 MISS、if 底下 when 區塊一行 MISS、`x.also` 一行 MISS)、C-35 兩行 MISS(`a.zip`、沒有呼叫的 `a.combine`)、C-36 四行(`"k${id}"` HIT、`k + 1` HIT——帶號選項整行拿掉時 `k + 1` 會被當常數、`LaunchedEffectCompat` MISS、`run(k)` MISS C-36 C-37)、C-37 兩行(`"k${id}"` HIT、`rememberSaveable` MISS);重掃 api.yml 132 項照綠 31 項,只剩上面列的等價存活(含 C-37 literal-arg 區 22 項) |
| g1 c3 b1 | 折 | code | check.py `choice_tables` 表列號不是 `[CA]-[1-9][0-9]*` 就報「列號要寫成…」;`t_choice_table_batch2` 補表列前導零、全形、全形混半形與乾節點表 `A-01` 四案例(修前紅 4 條、修後 20 passed) |
| k1 | 折 | spec | 計劃〈範圍〉2 C-34 補 try/catch 區塊與外層 try、字串樣板補 `"k${id}"`;〈範圍〉4 補列號只認半形數字不帶前導零 |

修補因果:g1 c3 b1 是第三輪修補只收緊一側,修前修後同結果(三席兩版實跑),記為原有漏查;c1 c2 修前修後同結果(正確性席兩版實跑),原有漏查;k1 原有。無回歸。
