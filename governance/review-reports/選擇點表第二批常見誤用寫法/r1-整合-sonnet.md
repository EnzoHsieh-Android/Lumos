severity: major

先講結論:這份 spec 的選擇點表、規則、產壞法三塊,我對照程式碼查證後沒有結構性漏洞。範圍 5「依列號」統計有兩個口徑沒定義,範圍 6 的文件同步也漏列幾處,這兩塊的洞比較大。事件欄位本身夠用:`choice-kill` 每筆帶 `row`,選擇點放行事件也帶 `row`、`label`、`decl`。

**已讀,無 finding 的節**
- 白話、舊否決比對、用詞、不做、依據來源、回退、天花板:已讀,無 finding。
- 範圍 2 規則與範圍 4 check.py:已讀,無 finding。
  - `_choice_rules_match` 會自動納入新規則檔,因為 `sgconfig.yml` 的 `ruleDirs` 是整個目錄。
  - 新檔的規則 id 要等於列號,spec 也這樣寫。
  - 型錄〈統計〉的「規則包條數:228」只數 `kotlin-android/rules*/*.yml`,不會被 `kotlin-choice` 的新規則影響。
- 範圍 1 型錄:已讀,有 minor 見第 5 條。

1. 範圍 5、S8:「每列的壞法數、殺掉數、存活數、跑不出結果數」沒定義怎麼把事件折成「壞法」。
severity: major
   blocking: 是,spec 沒定口徑,實作者只能自己猜,而 S8 的數字依賴這個口徑。
   - spec 段落:範圍 5、預期值表 S8。
   引句:「帳上 C-32 列 4 個壞法:1 殺掉、2 存活(放行理由各一筆「等價」「不是需求」)、1 跑不出結果」
   - 問題:帳上是一個壞法一個 attempt 一筆。同一個 (檔, 行指紋) 會有多筆:先 survived,補測試或人裁寫回後再來一筆 killed(attempt 2,via situation-rule)。
   - S8 的表假設一個壞法只有一個終態。真實帳上「存活 2」和「殺掉 1」會重複算同一個壞法。
   - spec 沒說要不要去重,去重取哪一筆(最新一筆?`_choice_disposition` 是「只看同鍵最新一筆」),也沒說 `blocked`、`unverified`、基準不綠的 no_result 算不算。
   - `no_result` 的原因「基準不綠沒跑」不是那一列壞法的錯,卻會灌進 RETIRE-IF 的「跑不出結果超過一半」。
   - 查證:
     - file: `scripts/lumos:17931` 現行 `_gov_choice_count_verdict` 用 `ever` 集合和 `attempt == 1 and via == "run"` 分別處理,沒有「依鍵取最新」的做法可沿用。
     - file: `scripts/test_lumos.py:144783` 現有測試夾具就是 `ck("s1","survived")` 加 `ck("s1","killed",attempt=2,via="situation-rule")` 同鍵兩筆。
     - file: `scripts/lumos:77705` `_choice_ledger_index` 以 (檔, fp) 為鍵放 list。
     - file: `scripts/lumos:78377` 另有「照時間排」的去重列 `ded`。新小節必須吃 `ded`(`_render_gov_choice(ded)`),否則同一筆寫兩次會雙計。spec 沒提這一點,而 `Systems/規格閘.md` 已有 PITFALL 記過這個坑。

2. 範圍 5、RETIRE-IF:「被回報存活之後的放行裡,理由是等價或不是需求」。放行事件對不回特定一列的存活。
severity: major
   blocking: 是,撤除條件的分母和分子沒有合法的接法。
   - spec 段落:範圍 5、RETIRE-IF。
   引句:「第二批任一列被回報存活之後的放行裡,理由是「等價」或「不是需求」的超過八成」
   - 放行事件的 `row` 是放行當下由 `_choice_waive_target` 現算的 `x["mutant"]["row"]`,不是存活事件記下的那一列。
   - 不唯一(not_unique)的行沒有 mutant,`row` 記成 `""`,依列號無法歸屬。
   - 放行可以發生在從沒有 survived 事件的行上(沒跑、no_result、超過回報上限),這種放行算不算「存活之後」,spec 沒定。
   - spec 自己在〈實務隱患〉承認型錄一改挑中的壞法可能換列(S7 只保護第一版語法)。存活事件記 C-5,放行時重算成 C-33,兩筆的列號就分家。
   - spec 沒寫「用 (檔, 行指紋) 把放行接到最近的 survived 事件、列號取存活那筆」,也沒寫沒接上的放行歸哪裡。
   - 查證:
     - file: `scripts/lumos:78673` `row = (x["mutant"] or {}).get("row") or ""`。
     - file: `scripts/lumos:42532` 放行事件帶 `row`、`decl`。
     - file: `scripts/lumos:17921` 現行放行統計不接 survived,只看 `ck_waive`。
     - file: `scripts/lumos:17903` 現行 `shape` 只在 `isinstance(row, str)` 時計,空字串也被計進去。

3. 範圍 6 與〈範圍〉3:新增的規則檔與樣本檔沒有列進「每支檔有家」,文件裡寫死的列舉也沒列入同步。
severity: major
   blocking: 是,CLAUDE.md 鐵則 5 規定提交時擋新違規,新檔沒有家會被擋;列舉過期則會被下一個接手者當現況。
   - spec 段落:範圍 6。
   引句:「Systems/kotlin規則包 補 WHY 行(第二批來源與不收理由);Systems/規格閘 補選擇點段「依列號」的說明」
   - 範圍 2 新增 `nul.yml`、`compose.yml` 和新樣本,範圍 6 沒要求把它們加進 `Systems/kotlin規則包` 的 `about_code`。該節點現在逐檔列出每個 `kotlin-choice` 規則檔和樣本檔。
   - 過期的句子至少有這幾處,spec 一處都沒點名:
     - `Systems/kotlin規則包.md` 第 95 行寫「照論文表 1 的 AOR、LCR、ROR、UOI、SBR 外加 Kotlin API 兄弟寫法」。加了 NUL 類別就過期。
     - 同檔「改動選擇點的規則(kotlin-choice)」一節逐檔列 `rules-choice/*.yml` 和樣本。
     - `skills/kotlin-idioms/checks-catalog.md` 說明段「照 …… 表 1 的五個運算子,外加 Kotlin API 兄弟寫法」。spec 只改了「四種錨點」那句。
     - `Systems/規格閘.md` 第 79 行描述 gov --stats 選擇點段「依 (列號, 外層宣告) 數」,新小節的口徑要和它對上。
   - 查證:
     - file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:8-32` `about_code` 列表。
     - file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:95` 類別列舉句。
     - file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:145` 規則檔列舉。
     - file: `skills/kotlin-idioms/checks-catalog.md:1656` 說明段。
     - file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:79`。

4. S7 綁的測試 `t_choice_points_batch2_stable` 照 spec 字面寫不出來。
severity: minor
   blocking: 否,補一句「用釘死的預期值」就能解,不改設計。
   - spec 段落:驗收條款 S7、預期值表 S7。
   引句:「第一版既有樣本裡不含 `?:`、`?.`、`let`、`combine`、`LaunchedEffect`、`remember` 的行,加入第二批列前後各跑一次 choice-points」
   - 測試跑的永遠是加入後的型錄,「加入前」要靠釘死的預期值或保留舊型錄副本,spec 沒說用哪個。
   - S7 的穩定性本身站得住:`_choice_pick` 只洗牌「這一行實際有的類別」,NUL 排尾端、沒出現就不動洗牌序。
   - 但 S1–S4、S6、S7 這幾條要真的 ast-grep。本機沒裝時,現有測試是印一行提示就 return,整段空過。相關測試只有 CI 裝了 0.51.1 才算數,spec 沒提醒。
   - 查證:
     - file: `scripts/lumos:77375-77377` `cats` 只含出現的類別。
     - file: `scripts/test_lumos.py:143606-143609` 沒有 ast-grep 時 `return`。

5. 範圍 1 的新列沒寫「對應決策表」欄的值,範圍 3 對 `_choice_anchor` 的描述與程式不符。
severity: minor
   blocking: 否,不影響行為,只是實作者要自己補或改寫。
   - 範圍 1 說「每列欄位與第一版相同」,但只給了錨點、壞法、型別前提,沒給「對應決策表」。
     - 型錄裡已有可互指的列:`combine` 對 D-5、`zip` 對 D-6、`LaunchedEffect` 對 D-32。
     - 說明段規定重疊成員要用列號互指。
     - check.py 只讀進 `dt` 不驗,漏了不會報錯,只會留下沒互指的列。
   - 範圍 3 寫「`_choice_anchor` 認新錨點「安全呼叫符」(位移取 navigation_suffix 開頭的 `?.`)與「引數」(位移取節點開頭)」。
     - 現行 `_choice_anchor` 對運算子與方法名以外的錨點,一律走預設 `return hit["s"], None`。
     - 兩個新錨點的位移就是節點開頭,現況已經對,不用改這支。
     - 真正要加的是 `_choice_edits` 的三個分支,spec 的範圍 3 第二條已有。這句多餘,但不會害人。
   - 〈統計〉的選擇點表列數會從 31 變成 37,spec 只寫「同步」。型錄現寫「31 列;乾節點規則:14 列(2026-11-14 第一版 ……)」,括號裡的日期說明也要一起改。
   - 查證:
     - file: `scripts/lumos:77118-77131`。
     - file: `skills/kotlin-idioms/checks-catalog.md:1651`。
     - file: `skills/kotlin-idioms/checks-catalog.md:744-745` D-5、D-6。
     - file: `skills/kotlin-idioms/checks-catalog.md:771` D-32。

**已查證、判不受影響**
- 現有 `t_gov_stats_choice_kill` 與 `t_gov_stats_choice_dedup` 只用 `in seg` 子字串比對,新小節放在選擇點段尾端不會讓它們紅。
- `t_choice_table_missing` 的 `len(tables["choice"]) >= 31` 是下限,加列不會紅。
- 現有測試夾具和樣本裡的 `?:`、`?.`、`.let`、`remember`:
  - 測試檔 143400–146000 行內只在 `_choice_atomic` 的斷言字串裡出現,不會產生新命中。
  - 樣本裡只有 `chain.kt:9` 的 `?.filter // HIT C-19` 和 `arid.kt:73` 的頂層 `combine // MISS A-11`。新規則多命中只影響新列自己,不影響 C-19 與 A-11 的標記。
- `_choice_catalog_sha` 只記帳備查,型錄加列不會讓舊處置過期。處置鍵是 (檔, 行指紋),spec 的〈用詞〉說法成立。

**實務隱患鏡頭**
- 編不過、等價存活:spec 已列,RETIRE-IF 承接,但第 1、2 條的統計口徑沒定會讓 RETIRE-IF 算不出。
- 掃描量:`?.`、`?:`、`.let` 是 Kotlin 裡最常見的語法,有選擇點的行比例會比第一版量到的 13–15% 高很多,推送前每行要跑殺傷力。spec 只寫「實作時重量一次」,沒有門檻,量了之後沒有可據以處理的數字。這條不影響設計正確性,所以我沒另立 finding。
- 守衛面、併發、金流、對外送出、不可逆:同意 spec 的排除理由,我沒有發現反例。

**lumos 自動附加節點**
- `Systems/規格閘` 與 `Systems/kotlin規則包`:這份設計不會破壞它們宣稱的行為,因為只加列、加規則,不改鍵與判定;但兩篇裡寫死的列舉會過期,見第 3 條。
- `scripts/lumos`(229 篇牽連):太泛,不逐條列。

最嚴重 severity: major,blocking 共 3 條。
