severity: major

審查範圍:第二版計劃。我讀了快照與 r1-intake.md,並對照 `scripts/lumos`、`scripts/hooks/pre-push`、`configs/ast-grep/kotlin-android/check.py`。第一輪的修法大致站得住:
- 插入點改為排在 `_spec_gate_clause_part` 之前,不看門也不看條款。
- 日期讀不到當今天,與測試總檔設 9999-12-31 的做法接得上。
- 型錄 324 這個數字,我用 `check.py` 重算,兩種口徑都是 324,對得上。

以下是新問題。

### F1 出處第②種(repo 路徑)借 `_refcheck_scan` 判存在,它的抽取規則會誤擋合法路徑,也可能放過不存在的路徑
引句:「用 refcheck 現成的 `_refcheck_scan` 判存在」
- `_refcheck_scan` 先經 `_node_code_ref_tokens` 抽取,只認「含 `/` 而且第一段是頂層目錄」的反引號詞。
  - 根目錄的檔案:出處寫 `` `README.md` `` 或 `` `CLAUDE.md` `` → 預期放行,字面實作會得到零個 claim 而擋下。路徑 `scripts/lumos:37496` 有 `/` 的過濾,`scripts/lumos:37484` 把不含 `/` 的詞丟掉。
  - 點開頭目錄:出處寫 `` `.github/workflows/ci.yml` `` → 預期放行,`scripts/lumos:37575` 的 `top_dirs` 排除點開頭目錄,同樣擋下。
- `_refcheck_scan` 回傳的狀態不只 ok 與 missing,還有 `planned`、`ignored`、`line_out_of_range`。計劃沒寫哪些算存在。
  - 出處寫 `` `scripts/不存在.py`(新增) `` 會被標 `planned`。實作者若用「不是 missing」判存在,就放過。這是一個一行就能繞過的洞。
  - `` `scripts/lumos:99999` `` 是 `line_out_of_range`,計劃沒說算不算。
- 「解析後要在 repo 根底下」這句有人保證:`_validate_repo_ref` 對 `..` 與絕對路徑直接回 missing。計劃應寫成「只認 status == ok」,並補上根目錄檔案與點目錄的處理,否則 S1「存在的 repo 路徑 應 放行」的字面承諾做不到。
severity: major
blocking: 是

### F2 推送前重查沒說「範圍碰到的新計劃」怎麼挑,接上既有的挑選函式會誤擋無關的推送
引句:「對這次範圍碰到的每一份新計劃」
- 既有的 `_spec_gate_push_candidates` 在 `scripts/lumos:15776`,`_spec_gate_push_scan` 的要簽預期值表那一圈在 `scripts/lumos:16498` 之後,篩選條件是 `_live`(doing,或範圍碰到的 done)。計劃寫「同一個出口」,實作者多半會直接接在那個迴圈上。接上去有三個後果:
  1. 候選不只是「被碰到的計劃」,還含「lands_in 或連結指向被碰到的 Systems 節點、或被改程式檔的家」的 doing 計劃。例:別的並行會談的新 doing 計劃沒有〈依據來源〉,我只改 `scripts/lumos` → 預期只查自己碰到的計劃,實際推送被那份別人的計劃擋下。
  2. 新的 todo 計劃被碰到(例:設計審折入後推功能分支)→ 不是 live,不會被查。範圍 3 的健檢卻把 todo 列為健檢對象,兩處範圍不一致。若改成自己另寫迴圈,就會查所有狀態,與「同一個出口」互相矛盾。
  3. 〈用詞〉只替健檢定義了「計劃」(`_計劃.md` 加 `type: project`),規格閘與推送前的「新計劃」沒有這個限定。`Projects/` 底下有非計劃的 `_調研.md` 之類(6 份)。例:修改一份 created 在生效日後、status 為 done 的 `Projects/X_調研.md` → `_live` 為真,被當成「缺依據來源的新計劃」擋下。
- S3 沒有對應的失敗例,上面這些都驗不到。
severity: major
blocking: 是

### F3 推送前擋下時的訊息標頭、hook 文案與留帳種類都沒定義
引句:「跟它對預期值表簽核的既有做法同一個出口、同一種留帳」
- `_spec_gate_push_bad_head`(`scripts/lumos:16594`)只認帳讀不到與預期值表兩種標頭,其餘一律印「N 份風險低計劃沒過」。依據來源擋下的是新計劃,不論風險高低,標頭會印錯。
- `scripts/hooks/pre-push:604` 在 rc=1 時固定印「風險低計劃的條款測試沒全綠(或留痕過期)」,並以同一句文案呼叫 `pp_record_block`。依據來源擋下時,使用者會被引去補測試。
- 「同一種留帳」若照字面是 `expected-unsigned`,事件就不是 `sources-missing`。S2 只規定規格閘那一邊寫 `sources-missing`,S3 沒有帳的斷言。結果 RETIRE-IF 與 REVISIT 要數的 `spec-gate/sources-missing`,漏掉所有推送前擋下的次數。
severity: minor
blocking: 否

### F4 〈依據來源〉表的欄位判定有三處計劃沒寫
引句:「表頭欄名或欄數不對、沒有任何資料列,都算這一節不合格」
- 依據欄與機制欄不驗。`| 某機制 | | https://a.example.com |`(依據欄空白)→ 預期擋(依據是「一句為什麼這樣定」),字面實作放行。預期值表檢查本來有三格不空的做法,這裡沒沿用。
- 第二列分隔列怎麼處理沒寫。`_expected_table` 有專門驗證,計劃只說重用 `_expected_table_lines` 與 `_expected_split_cells`。實作者若把分隔列當資料列,出處 `---` 不合格,所有計劃都被擋。
- 冒號與引號變體:
  - 引句:「後面接引號且引號內至少 4 個實字」
  - 計劃的日期語法只示範半形冒號,例子是 `使用者 2026-11-06:「…」`。中文輸入常見的 `使用者 2026-11-06：「…」`(全形冒號)預期放行,字面實作會擋。引號種類(「」、"") 也沒寫。
severity: minor
blocking: 否

### F5 健檢要對全部 todo 或 doing 的計劃逐篇判新舊,對現況會明顯拖慢 doctor
引句:「判成新計劃、而且〈依據來源〉不合格的」
- 現在 todo 或 doing 的計劃有 185 篇,全都沒有〈依據來源〉,先查節再判日期省不掉任何一篇。
- `_plan_effective_day` 每篇至少跑 `rev-parse --is-shallow-repository`、`git log --diff-filter=A`、`diff-tree`。我實測單篇 `git log` 約 0.2 秒,185 篇約增加 45 到 60 秒,而 doctor 會在 pre-push 與 `doctor --ci` 都跑。現在 doctor 沒有這種逐篇 git 呼叫(`scripts/lumos:14261` 目前只被 `_expected_requirement` 單篇呼叫)。
- 計劃沒提批次讀(一次 git log 取全部首次進入日期)或快取。
severity: minor
blocking: 否

### F6 低風險計劃沒有審查席可以接住「支持與否」
引句:「設計審與代碼審席位負責」
- 天花板 1 與實務隱患「過度放行」都把「亂貼格式對的網址」交給設計審與代碼審席位。但範圍 1 明確要求風險低計劃也擋,而風險低計劃的規格閘註明「直接實作、不派審」(`scripts/lumos:15632` docstring),代碼審也只在 tier=high 才派。
- 低風險新計劃寫 `| X | 隨便 | https://a.b |` 會過閘,之後沒有任何一道人工或席位會看到它。
- 計劃應在實務隱患或天花板說明這一類由誰補,或寫成已承認的缺口並附回頭條件。
severity: minor
blocking: 否

總結:最嚴重是出處判法借用 `_refcheck_scan` 時漏掉根目錄與點目錄檔案、放過 `(新增)` 的不存在路徑,以及推送前「範圍碰到的新計劃」沒定義挑法而會誤擋別人的 doing 計劃與非計劃筆記,會擋 2 條。
