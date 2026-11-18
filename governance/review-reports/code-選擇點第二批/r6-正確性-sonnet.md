severity: clean

沒找到 blocker 或 major;零 finding。本輪兩處修補都對得上,各項結果如下。

## 已驗主張與證據

我在臨時副本(`/tmp/lumos-seat-work/code-選擇點第二批/正確性-sonnet/`,實驗完已用字面路徑刪掉)裡驗過。修後是 8333987a,修前是 c261a154。

**V1 樣本標記與規則真實行為一致(含新增 18 行)**
- claim:新樣本每行的 HIT/MISS,跟規則現在的實際行為一致。
- input:`check.py` 的 `choice_sample_problems`,對修後的 `choice-batch2.kt` 用 `ast-grep 0.51.2` 實跑。
- expected:問題清單為空。
- before:修前規則配修前樣本,清單為空。
- after:修後規則配修後樣本,清單為空。
- comparison:一致。

**V2 `api.yml` 字面值判斷修補只改變 `@Suppress("x") 1` 這一種輸入**
- claim:拿掉 `regex: '^[-+]'` 之後,標註加常數不再命中,其他行為不變。
- input:修後樣本配修前規則(`api.yml` 換回 c261a154 版)。
- expected:只有 `LaunchedEffect(@Suppress("x") 1) { load() } // MISS C-36`(`choice-batch2.kt` 第 119 行)翻紅。
- before:修前規則配修後樣本,恰好只有第 119 行報「標 MISS,規則卻有節點從這一行開始」。
- after:修後規則配修後樣本,清單為空。
- comparison:修復有行為證據。其餘新增樣本是釘住既有錨點的行為,在修前規則下本來就綠。

**V3 表列號判法在這輪沒有改動,新增的只是測試**
- claim:`C-0`、`A-0` 報「列號要寫成…」是修前就有的行為。
- input:對 `choice_tables` 餵 `C-0`、`A-0`、`C-1a`、`C- 40`、`c-40`、`C-００`、`C－40`、`C-40a`、`A-1a`、`A- 1`、`a-1`,以及前後帶全形空白的 `C-40`。
- before 與 after:輸出逐項完全相同。
- 結果:
  - `C-0`、`A-0`、`C-００`、`C-0 `:報「列號要寫成…」並跳過那列。
  - 帶全形空白的 `C-40`:`\s` 認得全形空白,列號會被取出,撤號照擋。
  - `C-1a`、`C- 40`、`c-40`、`C－40`、`C-40a`、`A-1a`、`A- 1`、`a-1`:不符合列頭正規式,整列被安靜丟掉,沒有任何問題訊息。
- comparison:作者的 `check.py` 沒動,只補了 `C-0`、`A-0` 的測試。這些被安靜丟掉的列不會造成漏報,因為規則目錄多出來的 id 會被「沒有對應的列」逮到,撤號檢查看的是規則 id 本身。
  - 同列的規則 id:會被「型錄沒有對應的列」報出。
  - 樣本標記:會被報成「表裡沒有這一列」。
  - 撤號那一行:`已撤列號:C-0` 會報「要寫(無)或列號」。
  - 結果是整張表因為有問題而不被採用,沒有靜默繞過,也沒有連鎖誤報。

**V4 差異變異掃描:新樣本確實多殺了一批原本存活的變異**
- input:對 C-34 到 C-37 的規則逐一拿掉每個 key 或清單項,以及正規式的 `^`、`$`、`\s*`、`(\?\.|\.)` 分支;每個變異各跑一次樣本核對,修前樣本與修後樣本各一遍。
- 修前樣本多存活、修後樣本殺掉的 14 個變異,對應作者聲稱補強的子句:
  - C-34:`ofRule`(if 區塊最後一個陳述後接註解)、`try_expression` 那一支、`^` 與 `$`、`\s*`、`call_expression` 那層。
  - C-35:`?.`、`\s*`、完整套件名的兩端錨點。
  - C-36:`Unit` 兩端錨點、`^[-+]` regex、`LaunchedEffect$`。
  - C-37:`remember$`。
- 每條新樣本確實殺了對應子句:
  - `x.letX` 殺 `$`。
  - `x . let` 殺 `\s*`。
  - `run { x.let }` 殺 `kind: call_expression`。
  - `try … finally` 那行殺 try 分支。
  - `a?.combine`、`a . combine`、`a.combineLatest`、跨行的 `kotlinx.coroutines\n.flow.combine`、`my.kotlinx…` 各殺一個正規式選項。
  - `MyLaunchedEffect`、`distanceUnit`、`UnitX`、`-k + 1` 各殺一個錨點。
  - 另有 `myremember`、`remember(distanceUnit)`。
- 修後仍存活的變異,我逐一判過:
  - 父節點種類限定(`kind: call_suffix`、`inside: call_expression`):`value_arguments` 的父節點只可能是 `call_suffix`,而 `has: annotated_lambda` 加 `LaunchedEffect` 首子節點已排除其餘父節點,等價。
  - `literal-arg` 的 `kind: value_argument` 與 `Unit` 的 `kind: simple_identifier`:前者外層已限定,後者文字 `Unit` 只可能是識別字,等價。
  - `stopBy: end`:字串插值節點在樹裡是 `string_literal` 的直接子節點,我試了原始字串、巢狀字串、多行字串,命中結果完全相同,等價。
  - C-37 的 `literal-arg` 各項:測試用位元組比對把它釘成跟 C-36 同一份,等價。
  - C-34 的 `inside` 裡的 `kind:` 項:位置已由外層 `statements`、`control_structure_body` 決定,在我另造的 53 行語料(if/when/try/catch/finally/for/while/巢狀 lambda 各種位置)上,拿掉後命中位置完全一樣,等價。
  - C-35 的 `^` 與 `combine$`:`navigation_suffix` 文字必以 `.` 或 `?.` 開頭,等價;完整套件名的 `$` 因為後綴已限定結尾,等價。

**V5 作者判等價不補的幾類,我沒造出行為不同的輸入**
- `regex: '^[-+]'`:`prefix_expression` 且最後一個具名子節點是數字,只可能是正負號、標註、標籤加常數。`!1`、`++1` 不是合法 Kotlin,所以不是非常數。`LaunchedEffect(-k + 1)` 的樹是二元運算,仍然命中。
- `nthChild reverse` 的兩處:C-36 拿掉會讓 `@Suppress("x") 1`、`lbl@ 1` 被誤判,已被樣本殺掉。`value_argument` 那層拿掉後,只會在具名引數的名字是 `Unit` 時不同,真實的 `LaunchedEffect` 與 `remember` 簽名沒有這種參數,等價。
- 殘留的誤命中(不是回歸):`LaunchedEffect(@Suppress("x") -1)` 是標註加負號常數,仍然命中,屬於可忽略的等價變異雜訊,修前一樣。

**V6 C-34 規則在值位置判斷上沒有意外**
- input:53 行語料,涵蓋 if 條件、when 主體或條件、try/catch/finally 當值或當陳述、巢狀 if/when 在 lambda 最後、單行 lambda、尾隨分號、尾隨 KDoc 或行註解、泛型 `let<…>`、`let(::go)`、屬性存取。
- expected:跟規則文件的語意一致。
- after:一致。`finally` 區塊、for/while/do 內不命中,`return x.let{}` 與運算式本體命中。巢狀的 else-if、if 底下的 when、巢狀 if 不命中,這是設計上的保守,規則內文已寫明。
- comparison:無矛盾。

**測試重跑(修後版本,子集)**

| 測試 | 結果 |
|---|---|
| `-k choice_table_batch2` | 22 項全過 |
| `-k choice_samples_batch2` | 33 項全過 |
| `-k choice_points` | 105 項全過 |

`-k kt_catalog` 與 `-k choice_stats` 在對話逾時被移到背景,輸出沒有取回,這兩項我沒驗到。

## 三問回答

1. **原問題的修復效果有何行為證據**:標註加常數 `@Suppress("x") 1` 不再被當成非常數 key。V2 兩版對照證明:修前規則對那一行報誤命中,修後不報。`C-0`、`A-0` 的擋法是修前就有的,這輪只補了測試(V3),不算修復。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立**:成立。`-1`、`-1L`、`-0x1F`、`+2.5` 不命中,`-1.coerceAtLeast(k)`、`-k + 1` 命中,`null`/`Unit`/字串字面值/字元都維持原判。具名引數、巢狀 `LaunchedEffect`、泛型呼叫、前綴帶空白的寫法我也試過,結果合理。這些都是用修後規則實跑的結果;嚴格的修前對照只做了 V2 那一條,其餘沒有逐項跑修前。
3. **新發現的同一案例在修前、修後各是什麼結果**:沒有新發現,所以沒有需要對照的新案例。

## 圖譜鏡頭(固定席)

- `Systems/kotlin規則包.md`:這輪只改規則、樣本、測試與計劃文字。`check.py` 沒動,型錄與規則 id 的一一對應檢查由 V1 驗證仍成立,不影響。
- `bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle`、`測試假綠形態`、`lumos-cli-read` 的 ★INVARIANT★:這輪沒碰 `scripts/lumos`,測試檔只加兩個斷言變體,不影響綁定測試的存在與判定。
- `pitfalls-code-loop`、`loop-convergence-recording` 的 ★RISK★:`scripts/lumos` 沒動,不影響。
- 文件小不一致(措辭精度,不影響行為):計劃〈範圍 4〉寫「不帶前導零」,但程式還拒絕 `C-0`、`A-0` 這種零號列。照文件做不會出錯,所以只是措辭,不到 minor。

## 未驗範圍

- 沒有逐條重跑第二批六列的錨點、編輯與「依列號」統計,因為這些程式碼在本輪沒有改動。
- `-k kt_catalog` 與 `-k choice_stats` 結果沒有取得。
- 前幾輪席報告依規定沒讀。

最嚴重:clean;blocking 共 0 條
