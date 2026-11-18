severity: minor

## k1 計劃〈範圍〉2 沒寫 `.let` 的 try 值位置,型錄與樣本卻已收
severity: minor
blocking: 否 文件措辭不全,照文件做不會出錯或被擋。

- 輸入:計劃〈範圍〉2 對 `.let`(C-34)的描述,對照型錄 C-34 列與 `samples/choice-batch2.kt`。
- 預期:計劃寫明 try 區塊與 catch 區塊也是值位置,跟型錄和樣本一致。
- 實際:計劃〈範圍〉2 只寫「if/when 分支的最後一個陳述」,以及「外層 if/when 自己又掛在另一個分支底下」一律不收。整份計劃沒有 try 的規則描述。型錄 C-34 列已寫「外層 if/when/try」,規則 `rules-choice/api.yml` 的 `value-used` 也有 `try_expression` 與 `catch_block` 分支。
- 預期值表有 29 列(派工詞寫 28),沒有 r4 新加的 try、catch、when 值、各種數字字面值案例。這些案例只靠樣本檔與 `t_choice_samples_batch2` 守住。
- 三個月後的接手者看計劃,會以為 try 不收。

引句:「`if/when` 本身在確定是值的位置時才算;外層 if/when 自己又掛在另一個分支底下時」
file: `docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md:62`

- 歸因:有證據的原有漏查。r4 修補沒動 api.yml。r4 改動的只有樣本、check.py、型錄一個格子與計劃的兩段文字。
- 修前查證:修前版本的計劃同樣沒有 try,型錄那格只寫「外層 if/when」。修後型錄才補寫 try,計劃沒跟上。

## 已驗主張與證據

以下已修復或正常路徑仍成立的主張,各附 claim、input、expected、before、after、comparison。

| claim | input | expected | before(87093835) | after(59c41038) | comparison |
|---|---|---|---|---|---|
| G2 撤號守衛不再漏擋全形與前導零 | `_choice_retired()` 吃 `已撤列號:C-４０`、`C-040`、`C-４0`、`C-0` | 報「已撤列號那一行要寫…」,回傳空集合 | 四個都回 `({'C-４０'}, None)` 等,當成合法列號,守衛靜默失效 | 四個都回 `(set(), '…這裡是「…」')` | 已修復,兩版同一支腳本跑出差異 |
| G2 preserve:半形多列號照認 | `C-31`、`C-31、C-32, C-33` | 回傳該列號集合 | 照認 | 照認 | 不變 |
| 計劃新增段「括號包住的常數 key 照樣命中」成立 | `LaunchedEffect((1))`、`LaunchedEffect(-(1))`、`remember((1))`,用 ast-grep 跑 kotlin-choice | 命中 C-36 與 C-37,修前修後相同 | 命中 | 命中 | 計劃寫的「修前修後都命中」屬實 |
| 計劃新增段「引數巢狀的輸出平方成長」數字成立 | 生成 `remember(k, …)` 巢狀,各層帶尾隨 lambda,掃描 JSON 輸出大小 | 300 層約 3.8MB、1000 層約 40MB | 未跑 | 300 層 3,685,369 位元組、1000 層 38,894,846 位元組 | 與計劃寫的 3.8MB、40MB 一致,「約 1300 層超上限」是外推,沒實測 |
| G1 樣本守住規則 | `python3.14 scripts/test_lumos.py -k choice_samples_batch2`、`choice_table_batch2`、`choice_points_compose` | 全綠 | 未跑(只驗修後) | 33、16、7 條全過 | 修後正常路徑成立 |
| 型錄自檢 | `check.py --catalog-only --sg /opt/homebrew/bin/ast-grep` | 0 問題 | 未跑 | 型錄問題 0 個 | 成立 |
| 驗證筆記與計劃的 lint | `lumos lint Verification/2026-11-17_選擇點第二批上線前實測`、`lumos lint Projects/選擇點表第二批常見誤用寫法_計劃` | 0 問題 | 未跑 | 兩篇都 0 問題 | 成立 |

## 鏡頭三問與合約判定

- ① 原問題的修復效果:只驗了 G2(撤號守衛)。上表兩版對照腳本顯示修前全部放過、修後全部擋下。G1(樣本守住每個規則子句)只驗了修後測試全綠,沒做逐條拿掉規則子句的變異,屬未判定。
- ② 修補處的相鄰路徑:撤號行的半形單號、多號、頓號與逗號分隔照認。`lumos lint` 對兩篇改動的筆記 0 問題。
- ③ 新發現 k1:修前修後同結果,見上方歸因。
- 計劃〈實務隱患〉與驗證筆記的新句子:括號 key 與巢狀輸出的數字,實測都對得上。
- 驗證筆記 frontmatter 說 C-34 命中變窄、C-36 與 C-37 多收帶號數字後接呼叫的 key。這是 87093835 以前就進了 api.yml 的改動,不是 r4 修補造成,這處措辭合理。
- 計劃範圍 4 沒寫列號格式是「半形數字、不帶前導零」。這個限制只在 `check.py` 的 docstring 與報錯訊息裡。我找不出會因此翻車的具體場景,所以不報。
- 合約與圖譜鏡頭:
  - 改動的兩篇筆記(第二批計劃、上線前實測驗證)沒有 ★INVARIANT★ 行,沒有被破壞。
  - 固定席 bound-tests-gate、guard-kill、lumos-cli-lifecycle、測試假綠形態、lumos-cli-read 的合約都綁在 `scripts/lumos` 與測試總檔。這次文件包只動 `check.py`、樣本、型錄與兩篇筆記。程式包沒碰 `scripts/lumos` 與 `scripts/test_lumos.py`,不影響這些合約。
  - 殘留段「算不出來」(鏡頭時間預算用完)。本範圍沒有殘留問答被換號或改字重問的證據,但這句沒有機械驗證,標 ⚠ 未判定。
- 未驗範圍:沒有逐條拿掉 C-34、C-36、C-37 規則子句做變異,沒有對真實提交重量,沒有查治理帳殘留列。

最嚴重:minor;blocking 共 0 條
