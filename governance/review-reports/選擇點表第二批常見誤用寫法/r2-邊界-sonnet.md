severity: major

邊界與可執行性鏡頭,r2 版。我拿真實 Kotlin 邊界寫法打計劃,並對 `scripts/lumos`、`check.py`、`ast-grep 0.51.2` 逐項實測。共 9 條 finding:1 條 major(blocking),8 條 minor(non-blocking)。

**固定席(規格閘、kotlin規則包)**
- 「規格閘」節點沒有合約行。它的 20 行 KEY 管的是條款判定、門規則與推送前查簽。計劃只在它的選擇點段補「依列號」口徑說明,不碰那些機制。判不影響。
- 「kotlin規則包」節點沒有 KEY 或合約行,現有 WHY 與 PITFALL 沒被計劃翻案。其中有一條 PITFALL 講「二元運算換不同層級運算子要用 `_choice_top_prec` 加括號」。這份計劃的 b1 正好打到那個函式。判不影響節點宣稱,但要補一條 PITFALL。

---

### b1(major,blocking: 是)
severity: major
判準:不改,實作者照做會做出會當掉的壞系統。範圍 3 的 `_CHOICE_OP_RE` 一改,第一版 LCR 列就會崩。

**spec 段落**:範圍 3 第一點與〈用詞〉「`?:` 的錨點」。

引句:「`_CHOICE_OP_RE` 最前面加 `?:`。」

**問題**
- `_CHOICE_OP_RE` 還有第二個消費者:`_choice_top_prec`。
- `_choice_top_prec` 用 `finditer` 掃運算元,再查表 `_CHOICE_PREC[m.group(0)]`。`_CHOICE_PREC` 沒有 `?:`,所以會 `KeyError`。
- 該函式的 docstring 明寫「有表外的運算子(?:、..、as…)回 0(一律加括號)」。計劃的改法把這個不變式弄壞了。
- 計劃只談 `_choice_anchor` 這一個消費者。

**具體輸入與錯誤輸出**
- 輸入:`val ok = flag ?: false && ready`。`&&` 的 A 是 `flag ?: false`。elvis 優先序高於 `&&`,所以不加括號就是這樣解析。
- 當 LCR 挑中候選 `$A || $B`,`_choice_swap_edits` 會對運算元呼叫 `_choice_top_prec`,然後崩潰。
- 我只動 `_CHOICE_OP_RE` 這一行,其餘照現況,用 12 個不同行指紋實跑 `_choice_file_points`。
  - 現況:12 行都正常,挑到的候選是 `true`、`$B`、`false`、`$A || $B` 等。
  - 改後:其中一行(挑到 `$A || $B` 的那個種子)拋 `KeyError('?:')`,其餘 11 行照舊。
  - 約每 6 個行指紋有 1 個中。

**會有什麼後果**
- 呼叫端 `_choice_compute` 只接 `_ChoiceUnverifiable`,`KeyError` 會直接穿出。
- `choice-points`、`choice-kill`、推送前那一道,碰到任何含 `a ?: b && c` 或 `x ?: false || y` 的改動行都會當掉。這類寫法在 Kotlin 很常見。
- S7 只釘「不含 `?:` 的第一版行」,S1 只測 `?:` 單獨出現,都抓不到。

**最小重現**
```
cd /Users/enzo/harness/lumos-near-miss && python3.14 -c "
import importlib.machinery as M,importlib.util as U,re,sys
sys.argv=['lumos'];l=M.SourceFileLoader('lumos','scripts/lumos');s=U.spec_from_loader('lumos',l);m=U.module_from_spec(s);l.exec_module(m)
print(m._choice_top_prec('flag ?: false'))
m._CHOICE_OP_RE=re.compile(rb'\?:|'+m._CHOICE_OP_RE.pattern)
print(m._choice_top_prec('flag ?: false'))"
```
輸出:先印 `0`,接著 `KeyError: '?:'`。

**建議**
- 錨點用獨立的 regex,不動共用的 `_CHOICE_OP_RE`。
- 或把 `?:` 加進 `_CHOICE_PREC`(層級介於 infix 與比較之間),並讓 `_choice_top_prec` 的字數檢查能容納。
- 不管選哪個,都要補一條先紅的測試:`?:` 夾在 `&&`/`||` 運算元裡,挑到 `||` 候選不崩。這也屬於全域規則「同根因所有相似路徑各寫一支」。

---

### b2(minor,blocking: 否)
severity: minor
判準:不改,實作者可在寫測試時發現,但條款的「不產生」部分會變空殼或與「撤列不紅」互相矛盾。

**spec 段落**:驗收條款〈測試做法〉與 S2、S3、S4。

引句:「S1–S4 用測試裡合成的型錄列與 Kotlin 片段(不讀真型錄,撤列不會讓它們紅)」

**問題**
- S2 的「前一行結尾是註解 應不產生」,S3 的「單獨成陳述、頂層 combine、完整套件名 應不產生」,S4 的「`LaunchedEffect(Unit)`、`"init"`、`LaunchedEffect()`、具名 `block =`、無尾隨 lambda 的 `remember(k)` 應不產生」,全都由 ast-grep 規則檔(`nul.yml`、`api.yml`)決定。
- 合成型錄列加假命中的測試,根本測不到規則排除。
- 現有測試基礎設施:`_choice_tables_ip` 讀真型錄,`_choice_hit` 只造假命中,`_choice_real` 用真規則與真型錄(file: `scripts/test_lumos.py:143348`、`scripts/test_lumos.py:143373`、`scripts/test_lumos.py:143360`)。
- 兩條路都有問題:
  - 若用真 ast-grep,撤列會讓它紅,違反計劃自己的宣稱。
  - 若只用假命中,綁定測試對這些「不產生」條款是空殼。
- 實際守住這些排除的是 S6(樣本 HIT/MISS)。

**建議**:把「不產生」子句改綁 S6,或明說 S3、S4、S2 的規則排除部分靠 S6,另外改寫〈測試做法〉。

---

### b3(minor,blocking: 否)
severity: minor
判準:不改,實作者要自己猜「單獨成陳述」包不包 lambda 最後一個陳述,猜錯會漏掉常見寫法或留下等價壞法。

**spec 段落**:範圍 2 `api.yml` 的 `.let` 條,與 S3。

引句:「`.let`(排除整個呼叫單獨成一個陳述的寫法,例 `x?.let { show(it) }`——回傳值沒人用,換成 `also` 必然等價)」

**問題**
- 我用 ast-grep CST 實測:`list.map { it?.let { g(it) } }` 裡的 `.let`,其 call_expression 的父節點也是 `statements`,跟 `x?.let { show(it) }` 一樣。
- 但 lambda 最後一個陳述、當值用的 if/when/try 區塊最後陳述、單一陳述的函式本體,值都被用到。把它們一律排除,會漏掉 `map { it?.let { … } }` 這種很常見的寫法。
- 一律保留則會讓 `launch { x?.let { … } }` 這種 Unit lambda 的等價壞法存活。
- 第一版 `sbr.yml` 已經有一套 `value-pos`、`nthChild reverse`、`ofRule: code` 的判法(file: `configs/ast-grep/kotlin-choice/rules-choice/sbr.yml:11`)。
- 該檔註解警告:正面寫 `inside: {kind: statements}` 會讓每個命中帶整個外層陳述清單,輸出會爆(1500 條呼叫超過讀取上限)。
- 計劃只說「照 C-18 先例用 `not:`」,沒講「單獨成陳述」要採哪一種定義。S3 樣本也沒列 lambda 最後陳述、單一陳述函式本體這兩種。
- 我實測過用 `not: {inside: {kind: statements}}` 的寫法,1500 個 `.let` 的長函式輸出 1.7MB,沒爆。所以只是定義沒寫清,不是做不出來。

**建議**:明寫「照 `sbr.yml` 的 `value-pos` 判法,值被用到的最後陳述仍命中」,並補樣本。

---

### b4(minor,blocking: 否)
severity: minor
判準:不改,實作者跑現有測試會看到一條紅燈。這是計劃漏列的既有測試修改。

**spec 段落**:範圍 1 最後一點,與〈回退〉第 1 項。

引句:「〈統計〉的選擇點表列數(31 → 37)與括號裡的說明一起改(check.py 會比對列數)。」

**問題**
- file: `scripts/test_lumos.py:143765` 在 `t_choice_table_missing` 裡硬寫 `real.replace("- 選擇點表:31 列", "- 選擇點表:30 列")`,期待 `stats_problems` 報「重數不對」。
- 型錄改成 37 後,這個 `replace` 變成不動作,`stats_problems` 回空清單,那條 check 翻紅。
- 同一支測試的 `len(tables["choice"]) >= 31` 倒是不受影響。
- 計劃沒列這條既有測試要改。依專案規則,改 `test_lumos.py` 還要走簽章流程,應該在計劃裡預告。

---

### b5(minor,blocking: 否)
severity: minor
判準:不改,實作者做不出能跟第一版對得上的量測數字,範圍 7 的關卡會失真。

**spec 段落**:範圍 7 與 S9。

引句:「在兩個真實 Kotlin 專案(匿名寫成甲、乙)各量加入前後:有選擇點的行比例、最大那支檔的挑壞法耗時、隨機抽 10 段 20 行改動的平均壞法數。」

**問題**
- 計劃沒給量測用的指令或腳本。
- 第一版 Verification 的比例是臨時近似:「用節點起始行代替錨點行,不是 `choice-points` 指令的輸出」(file: `docs/lumos-toolchain-knowledge/Verification/2026-11-15_改動選擇點真實Android端到端驗收.md:37`)。
- 新錨點「`?:` 在續行」與「引數範圍內第一個改動行」跟節點起始行不同。拿同一套近似量,「加入前後」不可比。
- 「哪一列讓…多出超過 10 個百分點」要求逐列增量,卻沒說要逐列開關量幾次。
- 「隨機抽 10 段 20 行」沒說種子。
- `choice-points --diff` 要 git 範圍,計劃沒說怎麼造。
- 另外沒有任何一步量輸出體積或記憶體,只量耗時。
  - 實測:單一 21KB、2500 項的 `a0 ?: a1 ?: …` 行,`ast-grep scan --json=stream` 輸出 133MB,超過 `_LINT_SARIF_MAX_BYTES`(64MB,file: `scripts/lumos:43084`),會落到「整支記驗不了」。
  - 巢狀 elvis 的輸出是 O(N²),第一版的 `+`、`&&` 長鏈有同一類問題,所以不是新類別。但新列大幅擴大了命中面。

**建議**:至少寫明量測指令或腳本位置、逐列怎麼切換、種子,並補一個深層鏈的輸出體積檢查。

---

### b6(minor,blocking: 否)
severity: minor
判準:不改,實作者會發現「依列號」統計需要的欄位在統計列上不存在,要自己決定要不要改 mapper。

**spec 段落**:範圍 5 前兩點。

引句:「壞法:以 (檔, 行指紋, 壞法雜湊 new_sha) 為一個,列號取那個壞法事件帶的 `row`;同一個壞法多筆事件(先存活、後被殺掉)取時間最新那筆當終態。」

**問題**
- `_render_gov_choice` 收到的統計列由 `_gov_row` 產生,`ck` 子物件只保留 `file, fp, killing_test, changed, mutant_lines, secs, reasons`,**沒有 `new_sha`**(file: `scripts/lumos:18423`)。
- 頂層欄位有 `row`、`verdict`、`attempt`、`reason`,但沒有 `new_sha`。
- 統計列的 `ts` 是 `d.get("ts","")`,mapper 註解說它是 HEAD commit 時間,不是事件時間(file: `scripts/lumos:18404`)。同一 commit 內兩筆事件的「時間最新」會打平。
- 計劃說「不重讀帳」,卻沒說要擴 mapper(`_gov_row` 與欄位型別表 `_GOV_FIELD_TYPES`),也沒說平手怎麼判(用 `attempt` 或帳的順序)。
- 若實作者在 S8 夾具裡直接帶 `new_sha`,測試會綠,但真帳資料裡沒有這欄,同一行的不同壞法會被併成一個,統計偏低。
- 原因字串對不上實作。計劃寫的是「基準沒綠所以沒跑」,實際常數是「基準不績沒跑」的寫法:
  - file: `scripts/lumos:77862`,字串是「基準不綠沒跑」。
  - 照計劃的字面去比對會排除失敗。

**建議**:把欄位來源(擴哪個 mapper)、平手規則與原因字串的單一來源寫進範圍 5。

---

### b7(minor,blocking: 否)
severity: minor
判準:不改,不影響實作,但「實測持平」是沒有來源的現況斷言,還跟實作的規則數對不上。

**spec 段落**:〈實務隱患〉「挑壞法時限」。

引句:「掃描時限 `_KT_SIT_BUDGET` 照第一版(ast-grep 多兩支規則實測持平)」

**問題**
- 計劃新增 6 條規則(nul.yml 兩條加 api.yml 四條),不是「兩支」。這句是 r1 版 nul.yml 加 compose.yml 的殘影。
- 「實測持平」沒有出處,範圍 7 也沒量掃描時間,只量挑壞法耗時。
- 我的粗略實測:21,002 行的合成檔,加 4 條近似規則,掃描 0.86 秒變 0.92 秒,時間確實接近。但輸出量從 0 變成 45MB,這個壞處沒被講。
- 這句會讓實作者以為已經量過。

**建議**:改成「掃描耗時由範圍 7 一併量」,或附上確切的量測紀錄。

---

### b8(minor,blocking: 否)
severity: minor
判準:不改,實作者要自己補猜,多半能對,但有踩坑與不一致的風險。

**spec 段落**:範圍 2、範圍 6、範圍 1。

**問題**
- **YAML 要加引號**:`pattern: $A ?: $B` 不加引號會被 YAML 當成映射。實測回:
  ```
  error: line 4 column 16: mapping values are not allowed in this context
  ```
  要寫 `pattern: '$A ?: $B'`。計劃沒提。
- **樣本檔名不明**:範圍 2 說 `samples/` 補樣本,範圍 6 卻說 `about_code` 加「新樣本檔」,沒講檔名。`choice_sample_problems` 靠 glob `*.kt`,新檔名其實沒關係,但文件與 S6 要對得上。
- **規則 id 對列號的對應沒寫**:6 條規則怎麼對 C-32 到 C-37,要靠列出順序猜。S8 夾具用「C-32 那一列」卻沒說它是哪一列。
- **HIT 標記的位置會誤導**:`check.py` 的樣本核對只看節點起始行。
  - `?:` 換行寫在續行的樣本,HIT 要標在 A 那一行,不是 `?:` 那一行,否則樣本核對會紅。
  - 這跟 S1 的錨點在 `?:` 那一行是兩回事。
  - 巢狀 `a ?: b ?: c` 的內外兩個節點起始行相同,也要注意。

---

### b9(minor,blocking: 否)
severity: minor
判準:不改,不影響行為,但規則排除的邊界與理由寫得不準,實作者可能漏掉字串樣板。

**spec 段落**:範圍 2 `LaunchedEffect` 條。

引句:「空括號或具名 `block =` 換掉會刪掉 lambda」

**問題**
- 理由有誤。`LaunchedEffect() { … }` 換成 `(Unit)` 不會刪 lambda。空括號被排除只是因為「至少一個引數」這個條件。
- 具名 `block = {…}` 本來就沒有尾隨 lambda,已被「帶尾隨 lambda」排除,重複了。
- 「字面值」未定義邊界。`LaunchedEffect("user_$id")` 是含變數的字串樣板,不是常數。照 `^".*"$` 寫會被誤當字面值排除。
- `LaunchedEffect(key1 = Unit)` 具名常數會繞過「全是字面值」判斷而產生等價壞法。
- 用 ast-grep 實測,`has:` 加 `value_argument` 的 `regex` 做得到,只是要把這些寫進規則。

---

### 逐節結果
- 〈白話〉、〈舊否決比對〉、〈不做〉、〈依據來源〉、〈天花板〉:已讀,無 finding。
- 〈用詞〉:涉及 b1,其餘已讀。我驗證了「單一記號」判定與 `_choice_atomic` 一致,也驗證 `_choice_anchor` 預設分支確實回節點開頭。
- 範圍 1:b4、b8。
- 範圍 2:b2、b3、b8、b9。
- 範圍 3:b1。其餘我實測 `?.` 兩處編輯結果正確:
  - 同行:`a?.b` 變 `a!!.b`。
  - 續行:`repo.user()` 加 `?.name` 變 `repo.user()!!` 加 `.name`。
  - 前一行是註解時,ast-grep 的 CST 裡註解是 `navigation_suffix` 的前一個兄弟,用 `follows` 可表達。
- 範圍 4:已讀,無 finding。我實測 `check.py --catalog-only --sg <ast-grep>` 可執行、rc 0。`(Unit)`、`!!.`、`$A!!` 都能被 `_choice_candidates` 解析。
- 範圍 5:b6。
- 範圍 6:b8。
- 範圍 7:b5。
- 〈實務隱患〉:b7。其餘風險類:
  - 編不過(`$A!!` 對非可空只警告):屬實。專案開 `allWarningsAsErrors` 時會變編不過,但那種專案本來就不會有 `?:` 對非空型別的寫法,影響低。
  - 同名函式:已列。
  - 併發、金流、對外送出:無,理由同計劃(單人工具鏈,只改型錄、規則與產壞法程式,不對外送資料)。
  - 資料與不可逆:帳逐筆追加,拿掉第二批列後新推送不再產第二批壞法,無。
  - 效能與記憶體:見 b5、b7。
- 〈驗收條款〉:b2。
- 〈預期值表〉:S1 到 S4、S7 的預期值我都核對過。
  - `$A!!` 對 `a + b` 等非單一記號的括號行為正確,對 `repo.load()` 不加括號正確。
  - 巢狀 elvis 的內外節點錨點順序正確,左結合解析也確認(外層 A 是 `x ?: y`)。
  - S8 的計數與計劃的口徑自洽,但依賴 b6 的欄位。
- 〈回退〉:已讀。步驟與 `--catalog-only` 的行為對得上,無 finding。

**邊界輸入逐項結果**:以下我都實測過,沒有找到會出錯的輸出。
- 多行鏈式、行首 `?.`、巢狀 elvis、elvis 右邊是 `return` 或 `throw`、泛型、具名引數、尾隨 lambda 加括號引數、`as?`、`fun String?.f()` 的接收者型別。
- 帶 `?.` 的賦值左側、字串樣板內的 `?:`、一行多個候選點。
- 註解內的 `?:` 不會被命中。
- `a?::b` 與 `String?::length` 這兩個可空 callable reference 被 tree-sitter 誤解析成 elvis 加 ERROR。命中範圍跟 ERROR 重疊,會被第一版的 ERROR 守衛略過,所以不是新洞。

最嚴重 severity:major。blocking 共 1 條(b1)。
