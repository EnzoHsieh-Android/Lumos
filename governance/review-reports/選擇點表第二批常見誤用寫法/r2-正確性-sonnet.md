severity: major

整份 spec 已逐節讀完,修訂段落(`?:` 錨點、`$A!!` 樣板、引數錨點、依列號統計)特別細查。我用 ast-grep 在臨時目錄實跑過 `?:`、`?.`、`LaunchedEffect`、`remember` 的規則形狀,也把 `_choice_top_prec` 抽出來實跑。臨時目錄已刪。

## c1
severity: major
blocking: 是。照字面在 `_CHOICE_OP_RE` 最前面加 `?:`,第一版 LCR/ROR 換運算子的路徑遇到含 `?:` 的運算元會 KeyError,整道選擇點掃描炸掉。

引句:「運算子正規式 `_CHOICE_OP_RE` 最前面加 `?:`。比對從 `$A` 結尾那一格開始、只看開頭,第一版各列的運算子位置不會變成 `?:`。」

- **spec 段落**:範圍 3「`_CHOICE_OP_RE` 最前面加 `?:`」,以及〈用詞〉「`?:` 的錨點」說「第一版各列的運算子位置不會變成 `?:`」。
- **問題**:spec 只檢查了 `_choice_anchor`,沒看 `_CHOICE_OP_RE` 的其他用戶。`_choice_top_prec` 用 `_CHOICE_OP_RE.finditer` 掃運算元,再查 `_CHOICE_PREC[m.group(0)]`。
  - `_CHOICE_PREC` 沒有 `?:` 這個鍵。
  - 現況下 `?:` 不被正規式匹配,函式走到「有表外運算子回 0(一律加括號)」。加進去後就改成 KeyError。
- **哪些輸入會中**:`val s = a ?: b || c` 在 tree-sitter 裡 `||` 的 `$A` 是 `a ?: b`(已用 ast-grep 驗證)。
  - LCR 把 `||` 換成 `&&` 時層級不同(1 對 2),`_choice_swap_edits` 會對 `$A` 呼叫 `_choice_top_prec`。
  - `x ?: 0 > 3` 的 ROR 換成 `==`(層級 3 對 4)也一樣。
  - 這種寫法在實際程式裡很常見。
- **波及範圍**:`_choice_compute` 只接 `_ChoiceUnverifiable`,KeyError 不會被攔,會一路炸到 choice-points 與推送前那一道。
- **S7 抓不到**:S7 只測「不含 `?:`」的行,而這類行恰好含 `?:`,所以沒有測試守得住。
- **重現**:
  ```
  python3.14 -c "…exec _CHOICE_PREC/_top_level/_top_prec 定義,_CHOICE_OP_RE 加 \?: …; _choice_top_prec('a ?: b')"
  → KeyError('?:')   ('a ?: b + c'、'x?.y ?: 0' 同)
  ```
  樣本檔:`val s = a ?: b || c`,`ast-grep run -p '$A || $B'` 的 `$A` 為 `a ?: b`。
- **佐證**:file: `scripts/lumos:77184`(`_choice_top_prec` 內 `for m in _CHOICE_OP_RE.finditer(...)`)、file: `scripts/lumos:76876`(`_CHOICE_PREC` 無 `?:`)、file: `scripts/lumos:77176`(docstring 明寫 `?:` 屬「表外運算子回 0」)。
- **建議**:`?:` 不要進共用的 `_CHOICE_OP_RE`。另開一支只給 `_choice_anchor` 運算子錨點用的正規式,或在 `_choice_top_prec` 先排除 `?:`。再加一條測試:運算元含 `?:` 的 LCR/ROR 換運算子。

## c2
severity: minor
blocking: 否。實作者看到欄位缺口會補上,不會做出壞系統。

引句:「吃已去重的統計列(`_render_gov_choice` 收到的那份,不重讀帳)」

- **spec 段落**:範圍 5「壞法:以 (檔, 行指紋, 壞法雜湊 new_sha) 為一個…吃已去重的統計列…不重讀帳」,以及「不加它的最小解為什麼不夠」。
- **問題一**:統計列沒有 `new_sha`。
  - 去重列的 mapper 只帶 `verdict, row, attempt, reason, via, run_id`,`ck` 只有 `file, fp, killing_test, changed, mutant_lines, secs, reasons`。
  - 帳上事件有 `new_sha`,但統計列裡沒有。spec 沒寫要擴 mapper,也沒提 `_GOV_FIELD_TYPES` 型別表。「不重讀帳」的前提因此不成立,除非補欄位。
  - 「取時間最新那筆」也有問題:統計列的 `ts` 是 HEAD 提交時間,不是事件時間,同一提交內先存活後殺掉會同秒平手,終態判定要靠排序穩定性。
- **問題二**:放行事件其實已經帶列號。
  - `ck_waive` 本來就有 `row`(`_choice_waive_target` 回傳 `(x["mutant"] or {}).get("row")`),現行 `shape` 計數也用它。
  - spec 說「列號讀不出來」所以要走「接最近一筆存活事件」,這個理由只對壞法數、殺掉率成立,對放行成立一半。
  - 兩種列號來源(放行時當下挑到的壞法與存活事件)可能不同,spec 沒說以哪個為準。
- **佐證**:file: `scripts/lumos:18420-18426`(mapper 欄位)、file: `scripts/lumos:77883`(事件含 `new_sha`)、file: `scripts/lumos:78677`(waive 帶 row)。

## c3
severity: minor
blocking: 否。只會多出等價存活,靠放行承接。

引句:「`remember` 的 value_arguments(只在呼叫帶尾隨 lambda 時命中)」

- **spec 段落**:範圍 2 `remember` 規則「只在呼叫帶尾隨 lambda 時命中」,對照 `LaunchedEffect` 的排除條件。
- **問題**:`remember` 沒有「至少一個引數」或「不全是字面值」的排除,`LaunchedEffect` 有。
  - `remember() { … }`:value_arguments 是 `()`,刪掉後文字變成 `remember { … }`,行為完全等價。
  - `remember(Unit) { … }`、`remember(true) { … }`:全常數的 key 拿掉也等價。
- **實驗**:ast-grep 的 value_arguments + 尾隨 lambda 規則,在我的樣本裡對 `remember() { 3 }`、`remember(Unit) { 3 }` 都會命中,對 `remember(items)`(無 lambda)、`remember(calculation = {…})` 不命中。
- **建議**:`remember` 照 `LaunchedEffect` 補「至少一個引數、且不全是字面值」,並在樣本與 S4 加對應的不命中列。

## c4
severity: minor
blocking: 否。不涉及產生錯的突變,只是等價與編不過的比例被低估。

引句:「`$A ?: $B`→`$A!!` 在 `$A` 不是可空型別時編譯器只警告不報錯(行為不變,等價存活)」

- **spec 段落**:〈實務隱患〉「編不過」。
- **問題**:只提 `$A!!` 在非空型別時「編譯器只警告」。`?.`→`!!.` 在非空接收者上同樣只是警告,但這一列沒列進等價存活的描述。
- **風險**:很多 Android 專案開 `allWarningsAsErrors`。這時 `UNNECESSARY_NOT_NULL_ASSERTION` 會讓這些壞法編不過,落成「跑不出結果」。這會直接拉高 RETIRE-IF「跑不出結果超過一半」的比例。
- **建議**:實務隱患補一句,並在範圍 7 實測時看 `?.`/`?:` 兩列的跑不出結果率。

## c5
severity: minor
blocking: 否。check.py 不驗那一格,不會紅。

引句:「新增第二批六列(列號接 C-32 起),每列欄位與第一版相同,出處欄寫上面 PRIOR-ART 的來源。」

- **spec 段落**:範圍 1「對應決策表(無)」。
- **問題**:現行型錄慣例是「對應決策表」寫 `—`,「型別前提」才寫 `(無)`。證據是 C-19 列的欄位值,以及型錄說明段「對應決策表寫〈情境決策表〉的列號,沒有寫 —」。spec 全程寫「對應決策表(無)」,照字面填會跟第一版 31 列格式不一致。
- **佐證**:file: `skills/kotlin-idioms/checks-catalog.md:1658`;file: `configs/ast-grep/kotlin-android/check.py:1454`(此欄不檢查)。

## 已讀無 finding 的部分
- **預期值表逐列走過(ast-grep 比對 → 錨點 → 編輯)**:
  - S1 的 `f(a + b ?: c)` → `f((a + b)!!)`:ast-grep 的 `$A ?: $B` 確實給出 `$A`=`a + b`,前後是 `(`、`)`,不會多包括號。
  - `x ?: null`、`null ?: x` 被現成的 `_choice_excluded`(A 或 B 任一個 null)擋掉。
  - S1 續行 `?:`:`$A`、`$B` 位移夾住 `\n    ?: ` 後錨點行落在 `?:` 那一行。
  - S2:同一行插入 `!!` 加換 `?.` 為 `.`,在 `_choice_identity` 倒序套用下得 `a!!.b`。`?.` 另起一行時 `!!` 接在前一行結尾。
  - `follows: {any: [line_comment, multiline_comment]}` 的 `not` 在 ast-grep 實測能排除註解前導(行註解與區塊註解都被排除)。區塊註解其實可插 `!!`,多排除一些屬保守,不算錯。
  - S4:`value_arguments` 在 `call_suffix` 內且有 `annotated_lambda` 的規則,實測對 `LaunchedEffect(k)`、多 key、`(Unit)`、`("init")`、`(true)`、`()` 命中,對 `LaunchedEffect(k, block = {…})` 與無 lambda 不命中。
  - `remember<Int>(k) {}`、跨多行 `remember(` 的 value_arguments 範圍正確。
  - `(刪掉)` 走既有 `tpl == "delete"` 分支,`remember(items) {` 刪 `(items)` 後得 `remember { …}`。
  - S3:`combine`/`zip`:Flow 的 `zip` 只有擴充函式、`_choice_also` 只在檔頭有精確 import 時補一行,通配 import 不補,正確。
- **S7**:新增 NUL 類別放在洗牌清單尾端,只含第一版類別的行 `cats` 過濾後的相對順序不變,挑法穩定。S7 排除含 `?:`/`?.` 的行,所以守不到 c1 的路徑(已在 c1 說明)。
- **S8 期望值**:甲殺、乙先存後殺、丙存活、丁跑不出結果,算出 4/2/1/1,放行等價 1、沒接上 1,內部一致。
- **交叉引用**:D-5、D-6、D-32 存在且內容對得上(D-5 combine、D-6 zip、D-32 LaunchedEffect)。C-31 為止共 31 列,加 6 列得 37,與〈統計〉列數一致。`_CHOICE_PICK_BUDGET`(15 秒)、`_KT_SIT_BUDGET`、`CHOICE_CATEGORIES`、`CHOICE_ANCHORS`、`choice_tables`、`--catalog-only` 都存在。

## 固定席節點
- **規格閘**:判「不影響」。這份不動處置鍵 `(檔, 行指紋)`,只加列與新類別。但 c1 若不修,第一版 LCR/ROR 路徑遇含 `?:` 的運算元會讓整道閘 KeyError,屆時會破壞「算不出來就放行、只提醒」的行為(實際是例外而非放行)。修掉 c1 後不影響。
- **kotlin規則包**:判「不影響」。範圍 6 只加 `about_code` 與 WHY 行,不動既有規則的語意。型錄、規則、樣本要一起改齊,spec 已寫在〈回退〉第 1 項。

## 實務隱患逐類
- **編不過與等價**:見 c3、c4。
- **效能**:無新增疑慮。`?.` 命中量大,但挑壞法是每行一次且有 `_CHOICE_PICK_BUDGET`,spec 已用範圍 7 實測門檻處理。
- **安全、金流、外送、不可逆**:無。只改本機型錄、規則與產壞法程式,治理帳沿用既有追加方式。
- **併發**:不審(單人工具鏈)。

最嚴重 severity: major;blocking 共 1 條(c1)。
