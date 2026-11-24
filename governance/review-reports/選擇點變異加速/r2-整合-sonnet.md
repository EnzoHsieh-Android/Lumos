severity: major

## 總結

照三個月後接手的人的預設來讀,這份設計的主體跟既有圖譜相容,但有一處會讓實作者自己做決定:新的 `merge_ver` 過期判定到底套在哪些判定上。其餘是條款與預期值表對不上、幾條帳與舊句子的措辭需要同步。

- 舊否決比對所引的句子都找得到,沒有衝突。
  - [[Systems/規格閘]] 的 `[不選:每個壞法一棵工作樹平行跑(論文的做法,本機成本太高)]` 在。
  - [[Systems/guard-kill]] 的 `另抽一支共用的殺傷力函式` 確實三處。
  - [[Projects/改動選擇點都要有需求守住_計劃]]〈用詞〉殺掉判定與〈實務隱患〉那一行也都在。
- 〈落點〉列的既有句子都找得到:
  - 規格閘 choice-kill 那條 WHY(含「強 killed、編不過、逾時就停」)。
  - 改動選擇點〈用詞〉殺掉判定、〈實務隱患〉「同一平台一次呼叫一棵工作樹」與「同一壞法殺掉就停」。
  - 手冊 `06-代碼審與推送.md` 的 choice-kill 列。
  - `lumos-code-loop/SKILL.md` 的 choice-kill 段。
- 推送閘讀治理帳的路徑:
  - 它走 `_gov_rows_at`、`_gov_event_types_ok`、`_choice_ledger_index`、`_choice_disposition`,不走 `_gov_row`(那是 `lumos gov` 專用)。
  - 舊帳沒有 `judged` 與 `merge_ver`,照 single 讀,舊判法不變。
  - 新欄位若型別錯,事件整筆被丟掉,結果是缺紀錄而擋下,不會誤放行。
- 19 條條款 S1 到 S19 與預期值表一一對上,每條都有對應列。`t_choice_guard_kill_new_params` 在 `scripts/test_lumos.py` 已存在。
- 逐節走查:〈白話〉〈實測〉〈用詞〉〈不做〉〈回退〉〈依據來源〉〈人裁紀錄〉已讀,無 finding。
- 風險類(守衛面、資源、效能、回滾、相容)的隱患答案見各 finding 與文末。

## 逐條 finding

### 1. `merge_ver` 過期套在哪些判定上沒講清楚,會改變回報上限的行為
severity: major
blocking: 是

- 段落:〈做法〉6「作廢舊的合併判定」、S12、預期值表 S12。
- 問題:規則寫成「同鍵最新一筆 `judged` 是 merged、而 `merge_ver` 小於目前常數 → 算過期」,沒限定 `killed`。S12 與預期值表也只演練 killed。
- 現行 `_choice_disposition` 的 stale 只出現在 killed 分支。survived 照回報上限只擋抽中的那批,no_result 回「跑不出結果」。
- 例一:版本升了,帳上舊的合併 survived 若照字面一律回 `stale`,每一行都走「過期」的原因桶,繞過「存活只擋抽中的 `改到檔數 × 7`」的上限。一次升版會把大量存活行全擋下,上限形同失效。
- 例二:若只對 killed 做過期,舊版讀法判的 survived 與 no_result 沒被作廢。這跟〈做法〉6 末句「舊的合併判定一次全部要重跑」自相矛盾。
- 另有三個沒定義的邊界:
  - `judged` 是 merged 但缺 `merge_ver` 的帳。`None < 1` 會丟 TypeError,推送閘直接當掉。
  - `merge_ver` 是 bool。`_GOV_FIELD_TYPES` 的 `(int,)` 用 `isinstance`,bool 會過,見 finding 4。
  - 被放行(waived)的行。`waived` 先判,所以優先於過期。這點合理,但文中沒寫。

引句:「同鍵最新一筆 `judged` 是 merged、而 `merge_ver` 小於目前的 `_CHOICE_MERGE_VER` → 算過期」
引句:「[S12] 當帳上某一行最新一筆是 `judged` merged、`merge_ver` 小於目前常數的 killed 時」
file: `scripts/lumos:78074`(`_choice_disposition` 現況)
file: `scripts/lumos:78786`(`_choice_push_judge` 把 stale 全歸「過期」桶、survived 才走回報上限)

### 2. 「過期」一詞被借去指「判法版本舊」,但〈落點〉沒列要改的既有定義、提示與指標
severity: minor
blocking: 否

- 段落:〈落點〉「上線時同一提交改的既有句子」。
- 現況:
  - [[Projects/改動選擇點都要有需求守住_計劃]]〈用詞〉把「過期」定義成「`killing_test` 已沒有條款綁」。
  - 規格閘的有效處置那條 WHY 同樣寫「殺掉它的測試已沒有條款綁就是過期」。
  - `_CHOICE_PUSH_FIX["過期"]` 的提示是「殺掉它的測試已沒有任何計劃的條款綁著:重新綁回條款…」。
  - `_choice_ledger_status` 的標籤是「過期(殺掉它的測試已沒有條款綁)」。
- 後果:
  - 因版本升級而過期的行,提示會叫人去重綁條款,但條款其實還綁著,指路錯一半。
  - 同一個改動選擇點計劃的 RETIRE-IF ③「推送被擋的筆數裡超過一半是『過期』就把推送那一道降成只提醒」會被升版事件灌水。
  - S22 與 `gov --stats` 的「過期占比」同樣被污染。
- 現況:這些都不在〈落點〉的修改清單裡。
- 例:升一次 `_CHOICE_MERGE_VER`,下一次推送的過期筆數暴增,RETIRE-IF ③ 的分母看起來像「測試沒綁了」。

引句:「上線時同一提交改的既有句子:[[Systems/規格閘]] choice-kill 那條 WHY 的「強 killed、編不過、逾時就停」補上合併模式」
file: `scripts/lumos:78686`、`scripts/lumos:77902`
file: `docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md:93`、`:40`

### 3. 合併列沒說要保留 `weak`,S2 的「跟 `--no-merge` 同樣判定」在弱證據情境會破
severity: minor
blocking: 否

- 段落:〈做法〉2「歸因夠不夠強」、〈做法〉4「合併那一次怎麼判」第 5 點。
- 現況:
  - 現行判定 `_choice_kill_judge` 要求 `killed 而且不帶 weak` 才算決定性殺掉。
  - 「帶弱證據的 survived」也記跑不出結果。
  - `weak` 在 `cmd_guard_kill` 收尾蓋章,來源有四個:整套一起跑、平台 flaky、筆記未提交、`_mtime_unsure`(修改時間沒錯開)。
- 問題:spec 對合併列只寫「記殺掉(強證據)或存活」,沒說 `_mtime_unsure`、`b_unsure`、`flaky` 怎麼帶到合併列。
- 例:壞法寫檔後修改時間沒錯開,單支跑會把 survived 記成弱證據、判跑不出結果。若合併列照字面「記存活」,同一個壞法在合併模式判 survived,`--no-merge` 判 no_result。這與 S2、S10 的「判定相同」矛盾。
- 另外,S16 的「弱證據升級」只該針對 `killed_unattributed`,不該升 `_mtime_unsure` 那種弱。

引句:「成立 → 合併道每支照 2 記殺掉(強證據)或存活(判法 merged)。」
file: `scripts/lumos:28562`、`scripts/lumos:78208`

### 4. 〈做法〉6 對 `_GOV_FIELD_TYPES` 的描述與實際機制不符
severity: minor
blocking: 否

- 段落:〈做法〉6「run 事件」末句。
- 現況:spec 寫「整數用 `type(x) is int` 排除 bool」,但 `_gov_event_types_ok` 是對每個鍵做 `isinstance(d[k], types)`,表裡只有型別元組。`(int,)` 一定放 bool 過。
- 要照 spec 排除 bool,就得改 `_gov_event_types_ok` 本身。那是七本帳共用的函式,spec 沒把它列進落點。
- 不改的話,`merge_ver: true` 會被收下,`True < 1` 為假,不會被判過期。
- 〈做法〉6 另說「列上的 `judged` 一律 single(不傳 merge 時)」。S17 同時要求「輸出跟現在相同」。`--json` 的輸出是把結果列整個印出,只濾掉幾個底線欄位。`judged` 若放進 `results` 列,`cmd_guard_kill --json` 的 stdout 就多一個鍵,S17 與合約 `t_guard_kill_json_purity` 的旁邊測試可能看得出差。放在 `on_row` 交出的字典則不影響。spec 沒指定放哪。

引句:「新欄位照既有慣例登記進 `_GOV_FIELD_TYPES`(整數用 `type(x) is int` 排除 bool)。」
file: `scripts/lumos:18472`、`scripts/lumos:28587`

### 5. 合併基準沒核對 rc,與〈做法〉4 第 5 點的乾淨條件不對稱
severity: minor
blocking: 否

- 段落:〈做法〉3 第 4 步與第 3 步。
- 問題:第 4 步對每支只看「對到恰好一個完整名而且沒失敗」就記綠。乾淨條件裡的「rc 是 0 若且唯若沒有失敗」只出現在壞法那一次與熱基準。
- 例:第一次合併基準 rc 非 0,但結果檔全綠(測試任務之外的後續任務失敗)。這 64 支全記綠、進合併道。之後每個壞法的乾淨判定都以 rc 為 0 為前提,會一律不乾淨而退回逐支,合併白付。
- 另外,第 3 步對「合併基準逾時」印的是「找不到 JUnit 結果檔」。S4 預期值也固定這句,逾時時訊息誤導。

引句:「對到恰好一個完整名而且沒失敗 → 進合併道,基準記綠、耗時記合併這一次」

### 6. 壞法套不上去的路徑與多平台,合併模式沒定義
severity: minor
blocking: 否

- 段落:〈做法〉4、〈用詞〉判法 `single`。
- 現況:現行每條配方各自走 `file 路徑逃逸`、`file 開不了`、`old 命中次數不為 1`(drifted)、`also 套不上`(error)、`revert 失敗`(`break` 整個平台組)。
- 問題:〈做法〉4 只寫「套一次壞法」,沒說這些情況下合併道、逐支道各產生什麼列。
  - 只在〈用詞〉把 drifted 歸 `single`,S11 也只用一個「old 對不到」案例。
  - 「revert 失敗、這一組作廢」只出現在退回逐支那一步。
- 多平台:`cmd_guard_kill` 把配方依平台分組,各自一棵工作樹;`group` 跨平台,現行 `hk.between` 讓同組跨平台略過。
  - spec 假設「同一個 group 連續」,多個 kotlin-junit 平台時一個壞法的列分屬不同平台組。
  - 「所有列都產生後才一次交出」在跨平台怎麼算、平台 A 合併殺掉後平台 B 是否略過,都沒定義。
  - 沒有條款覆蓋多平台。

引句:「`merge`(真:同一個 `group` 連續、而且 file、old、new、also 都相同的配方視為同一個壞法,照 3、4 跑)」
file: `scripts/lumos:28470`、`scripts/lumos:28497`

### 7. S9 的預期輸入字串與〈做法〉4 的樣式對不上,條款無法照字面寫成測試
severity: minor
blocking: 否

- 段落:〈做法〉4 第 2 點、S9、預期值表 S9。
- 問題:〈做法〉寫的樣式是 `Process 'Gradle Test Executor <N>' finished with non-zero exit value 137`,並註明「字樣待實作時…實測確認後寫死」。預期值表案例四給的輸入卻是 `Gradle Test Executor 1 finished with non-zero exit value 137`,沒有 `Process '` 與引號。
- 例:照〈做法〉的樣式寫比對,表裡的案例四不命中,測試紅。要先決定樣式才寫得出測試。
- 同類的對不齊:
  - S13 條款寫「不帶 `--only` 時重跑範圍內所有有紀錄而沒放行的行」,預期值表 S13 沒有對應案例。
  - S19 條款的不乾淨只列三項(有失敗、rc、讀不出來),〈做法〉3 第 5 步還含「合併道每支都對到恰好一個完整名」。
  - S15 預期值表「零案例檔 → 退回逐支」沒分是出現在基準(整次不合併)還是壞法那次(只退一個),兩種結果不同。

引句:「輸出含測試行程被收掉的寫法(預期是 `Process 'Gradle Test Executor <N>' finished with non-zero exit value 137` 這類;字樣待實作時在實驗專案實測確認後寫死)」
引句:「案例四:rc 1、輸出含 `Gradle Test Executor 1 finished with non-zero exit value 137`」

### 8. 「殺掉它的測試與 `--no-merge` 相同」與 S16 的升級互相牴觸,S18 抽查與 RETIRE-IF ① 的判準也被拖動
severity: minor
blocking: 否

- 段落:〈做法〉5 第一點與「刻意的差別」、S18、RETIRE-IF ①。
- 問題:〈做法〉5 第一點說合併判定與逐支「是同一支」,同節又規定弱證據(未歸因)會升級。
  - 例:排序 a(未歸因的紅)、b(強殺)。`--no-merge` 判 killed by b,合併判 killed by a。S10 與預期值表的「`--no-merge` 也是 a」只在 a 本身強殺時成立。
- 後果:S18「抽 10 行 `--recheck --no-merge` 判定與殺掉它的測試都相同」與 RETIRE-IF ①「抽查查出一筆合併判定跟逐支不同、而且是讀法的錯」。升級案例按設計就會 `killing_test` 不同,抽查會誤報,必須事先把這類排除。
- 另外,抽查用的 `--recheck --no-merge` 會追加一筆 single 紀錄蓋過原本的合併紀錄,之後 `judged` 的樣本計數(RETIRE-IF ① 的 50 筆、三成)被抽查改寫,spec 沒說。

引句:「這樣排序第一支(可能在逐支道)跟合併道的結果一起比,殺掉它的測試與 `--no-merge` 相同。」
引句:「判成被那支殺掉;完整名有兩個以上時 應 不升級、退回逐支、判定同 `--no-merge`」

## 沒有 finding 的部分

- 舊帳讀法:`_choice_ledger_index` 只要 `file`、`fp`、`verdict` 三個字串欄位;新欄位型別錯時整筆被 `_gov_event_types_ok` 丟掉,走缺紀錄,fail-closed。
- 規格閘 PITFALL「總時限在配方之間停時已有決定性結果的壞法缺列」:合併模式只在壞法之間看 `should_stop`,不會落進同一個洞。
- 固定席各節點的判斷:
  - guard-kill:兩條 ★INVARIANT★(rc 優先序、`--json` 純度)。`merge` 不傳時行為不變,S17 守,不影響。唯一要注意是 finding 4 的 `--json` 鍵。
  - test-quality-cli、`test_quality.junit()`:只被讀、不改,不影響。
  - lumos-cli-lifecycle、bound-tests-gate、lumos-cli-read:與選擇點判定無關,不影響。

## 風險類逐類

- **守衛面**:判錯的方向見 finding 1、3、8。合併只會把歸不到升成殺掉,其餘不乾淨退回逐支。升版過期是 fail-closed。
- **資源**:無新風險。逾時時 Gradle 背景程序的行為 spec 已自承沒驗過。
- **效能**:spec 已量化,待 S18 實測。
- **回滾**:spec 已寫,但 finding 2 的 RETIRE-IF ③ 污染會讓升版這條回收路徑製造雜訊。
- **相容**:舊 lumos 讀新欄位會略過,新舊帳混讀照 single 處理,無新增風險。

發現共 8 條
