severity: major

我是整合/知識同步席。以下只讀盤點,沒有跑會寫檔的指令,也沒有建實驗倉庫,所以 hunk 標頭的行為是用本 repo 既有提交的 diff 輸出佐證,不是另造夾具重現。結論先講:核心裁定(認分支自己的改動、算不出退回 `v1`)我沒推翻。但「改了之後哪些東西跟著錯」這一半,計劃只列了兩個函式呼叫點,漏掉使用者看得到的訊息、手冊、測試、版本與 CHANGELOG。另外有一個算法上的洞,會讓 S1 在常見情況落空。

## Finding 1

severity: major
blocking: 是 — 擋推送的閘(`note_reread.gate` 預設 block)印出的說明與手冊,會跟新指紋的行為相反,而且沒有任何測試釘住那幾句。
引句:「`_note_reread_fps` 與 prepare 單篇那個呼叫都改走新函式」

問題:計劃只盤了 `_note_reread_fps` 和 `_note_item` 內的 `_note_reread_contrast_fp` 兩個呼叫點,沒盤「描述指紋內容的句子」。實際會跟著錯的句子有:
- `_note_reread_print_layer1` 擋下時印的那句「對照指紋含這篇 about_code 列的程式在頂端的版本——合併主線帶進別人對同一支程式的改動、筆記改名、about_code 增減都算」。新指紋下,合併主線帶進別人的改動不再算。
- `_note_reread_contrast_fp` 的 docstring:「★不含範圍與 diff★……只要 ls-tree 就能算,作者本機的 diff 設定也不影響它」,與 S5 的整個前提相反。
- 手冊 `06-代碼審與推送.md` 兩處。第一處寫「程式改了(含合併主線帶進別人對同一支程式的改動、rebase、筆記改名、about_code 增減)就要重判」,把 rebase 列為重判原因,正好是本計劃要消除的。第二處是消費專案 CI 那段「候選與指紋跟作者本機看到的不同」。
- 測試的釘法:`t_reread_block_layer1`(`scripts/test_lumos.py:69068`)只釘子字串「程式改了就要重判」,`t_note_audit_reread_skill_section` 沒釘那一句。所以這些句子錯了,測試不會紅,下一個 session 的 AI 會照手冊講。

失敗情境:作者 rebase 後被擋,訊息說「合併主線算改動、要重判」,作者以為指紋對不上就硬重派一次判定者(花錢),或反過來不信這道閘。

佐證:
- file: `scripts/lumos:37048`
- file: `scripts/lumos:36137`
- file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:98`
- file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:104`
- file: `scripts/test_lumos.py:69068`

## Finding 2

severity: major
blocking: 是 — 計劃自己寫明要推翻舊設計,卻沒列「要一起改的說法」,lands_in 只有一篇,取代不了其他篇的現況句與反向的測試翻紅釘。
引句:「刻意不含範圍與 diff。理由寫在它的〈做法〉第 1、2 節」

問題:`lands_in` 只列 `Systems/筆記內容審`。先例 `Projects/舊句兩道轉擋_計劃` 有一整節〈要一起改的說法〉,逐篇列出筆記、手冊、程式、測試與版本。本計劃沒有。實際要動的位置如下。

| 位置 | 內容 |
|---|---|
| `Systems/筆記內容審.md:77` | 「★不含範圍與 diff★:手動 prepare 與推送前 check 的起點算法不同……」 |
| `Systems/筆記內容審.md` 的 CI WHY(`[test:t_reread_block_hook_and_ci_wiring]`) | 提到「候選與指紋跟本機……不同」 |
| `Projects/守檔筆記對照改動_計劃.md:51` | 「★兩邊起點可能不同,但第 2 節的對照指紋不含範圍……」 |
| 同上 `:60` | 「只用 `git ls-tree` 就能算,不用組 diff」 |
| 同上 `:162` | 〈誠實界線〉的盲區說明 |
| 同上 `:273` | 設計審 r1 紀錄「項目指紋改成筆記 blob 加 about_code 每支檔的頂端 blob」 |
| 同上 S6 | 條款 |
| `Projects/舊句兩道轉擋_計劃.md:29` | 「不做:……改對照指紋的組成」 |
| 同上 `:48` | 「對照指紋照舊含筆記路徑與程式 blob……擋下訊息要講這點」 |
| `Systems/pitfalls-code-loop.md` | `_codeloop_default_base` 的 WHY(`[test:t_codeloop_default_base_prefers_newest_mainline]`)與 `:220` 的 REVISIT |
| `scripts/test_lumos.py:67854` | `t_note_audit_reread_check_reminds` 的「翻紅釘:把範圍或 diff 算進去 → ⑧紅」 |

最後一列是翻紅釘:新指紋本來就要把 diff 算進去。這一句沒改的話,日後的 AI 會把它當守衛,「修回」不含 diff。

「不含範圍與 diff」的標法(回答你的問題):
- `[status:superseded]` 加 `[被取代:]` 只用在摘要條目。這些是正文與〈做法〉段落,用不上。
- 本 repo 的先例是原句就地改成帶日期的括號註記,例如 `舊句兩道轉擋_計劃` 的 S7、S9:「(……由 [[…]] 取代)」。建議每句現況句改成現在式的新事實,舊理由留成一行帶日期的歷史:「2026-10-14 前不含 diff,理由是……,由 [[Projects/回頭重讀指紋不因主線前進失效_計劃]]〈做法〉2 取代」。
- 不要只標在一處。回頭重讀本身與舊句檢查(m1)都會對「改了程式、筆記還說舊東西」出手,漏標的那幾篇會被它們點名。
- 舊理由(設計審 r1 四席)是一筆被翻案的決策。若 `守檔筆記對照改動_計劃` 有 `decisions:` 欄,要用 `lumos decision-add` 記翻案;若沒有,就在新計劃〈做法〉2 保留那條理由的原文與否決依據。

建議 lands_in 補:
- `Systems/pitfalls-code-loop`
- `Projects/守檔筆記對照改動_計劃`
- `Projects/舊句兩道轉擋_計劃`
- 手冊 `06-代碼審與推送.md`
- 還要把 `Issues/預設起點與名冊人數收尾小問題` 列為相關(見 Finding 5)。

## Finding 3

severity: major
blocking: 是 — 本計劃的目的(rebase 後不重派)在常見情況會落空:hunk 標頭尾巴的函式名會隨主線改動而變,而計劃只替換標頭裡的數字。
引句:「把 `@@ -a,b +c,d @@` 的數字換成固定字樣」

問題:`git diff` 的 `@@ -a,b +c,d @@` 後面會接「該 hunk 之前最近一行符合函式名規則的文字」。例如本 repo 實際輸出:`@@ -22797,6 +22797,14 @@ def cmd_new(env, ntype, name, ...`。
- 這個檔沒有 `.gitattributes` 的 diff 驅動(`git check-attr diff` 回 unspecified),所以走預設規則:第 0 欄起頭為英文字母、`_` 或 `$` 的行。
- 計劃只換數字,尾巴「原樣雜湊」。主線若改了作者 hunk 所在函式的 `def` 行、簽名,或在作者 hunk 之前、離它超過 3 行處新增第 0 欄的行(模組層常數、`def`),尾巴就變了,逐檔指紋跟著變。
- `scripts/lumos` 約五萬行、被約 49 篇筆記認領,主線每天在改簽名與模組常數。這正是計劃〈緣起〉那個案例。

失敗情境:作者的改動一個字沒變,主線改了同一個函式的簽名(離作者 hunk 超過 3 行),rebase 後 S1 的預期(「認得已對照、不再列出」)落空。方向是多列、不漏判,但直接違反本計劃自己的 RETIRE-IF 第一句。S1 的測試若只在檔案另一頭加一行,測試會綠,實際仍失效。

另有一個同族缺口:S5 列的本機設定漏了 `diff.indentHeuristic`(會改變等價 diff 的滑動位置)、`diff.suppressBlankEmpty`(空白上下文行寫成空字串或單空格)、gitattributes 的 `diff=<driver>`/`xfuncname`。

建議:
- 整個 `@@ … @@` 標頭只取固定字樣,尾巴一併丟掉。
- 釘 `--indent-heuristic` 和 `-c diff.suppressBlankEmpty=false`。`_lens_git` 目前只固定加 `-c core.quotePath=false`,需要多一個帶 `-c` 的入口。
- S1 加一個「主線改作者 hunk 所在函式簽名」的夾具,S5 補上述設定。

佐證:
- file: `scripts/lumos:36216`(現行組 diff 的選項)
- file: `scripts/lumos:32112`(`_ns_diff` 的先例,同樣沒處理標頭尾巴)

## Finding 4

severity: major
blocking: 是 — 計劃把升級成本定義成「一次性」,卻沒有版本號、CHANGELOG、遷移期的雙讀;在預設 block 的閘上,所有進行中分支的所有候選會同時被擋、要重派判定者(花模型錢)。
引句:「升級之後,進行中的分支上已經用舊指紋記的對照紀錄不再算數,要重新 prepare 一次」

問題:
- 現況是 `LUMOS_VERSION = "v1.3"`,`note_reread.gate` 預設 block。這是 `v1.3` 才轉擋的。
- 推送前掛鉤是否提示消費專案跑 `lumos update`,靠版本號。`CHANGELOG.md` 有守衛盯著版本與標題一致,`t_discipline_block_stamp_matches_version` 要求紀律區塊戳記與版本相等。先例 `v1.3` 就是為了掛鉤行為改變而升版。本計劃行為改變同樣大(所有舊紀錄失效),卻只在〈回退〉寫「消費專案跑 `lumos update` 取回舊版」,沒有提升版本、CHANGELOG、`lumos update` 重注入。
- 失效是不必要的。若 check 同時接受「`v2` 指紋已對照」或「`v1` 指紋已對照」(`v1` 紀錄代表頂端的程式 blob 逐字相同,比 `v2` 嚴格),就沒有懸崖。新指紋只是額外多一個機會被認出。這樣回退(還原提交)時 `v2` 紀錄也不會變成孤兒。這個雙讀對安全方向沒有任何代價。
- 副作用:第二層表態以判定紀錄的指紋為鍵,重 prepare 後點出的規則類條目要重新 `drift ack --kind reread`,計劃只輕輕帶過。

失敗情境:`v1.4` 上線當天,有 N 條進行中的分支各有 M 篇候選,全被擋,每篇都要重派判定者並重新表態;消費專案沒升版就沒被提示、也沒 CHANGELOG 可查。

## Finding 5

severity: minor
blocking: 否 — 不會放行錯的東西,是測試與簽名收尾的遺漏,推送時會被 anchor 或測試擋下而不是靜默。
引句:「現有唯一的呼叫點(代碼審判定在沒給範圍時)傳 HEAD,行為不變;引用它的測試一起檢查。」

問題:
1. 非測試呼叫點確實只有 `_codeloop_guard_verdict` 一處(`scripts/lumos:51024`),這一點屬實。但 `t_codeloop_default_base_prefers_newest_mainline` 有 7 處用單參數呼叫(`scripts/test_lumos.py:37286`–`37309`)。簽名改成必填 `(repo_root, tip)` 會直接 `TypeError`。要嘛 `tip=None` 預設為 HEAD,要嘛全改。
2. 改 `scripts/test_lumos.py` 必須先 `lumos anchor approve`。治理帳 2026-10-13 對同一支測試就有簽名記錄(`docs/.governance-log.jsonl:122021`)。計劃沒提。
3. 「行為不變」不全對。舊版用 `symbolic-ref HEAD` 取簽出的分支。新版對 HEAD 用 `for-each-ref --points-at`:`git rebase` 中 HEAD 是 detached,且剛好只有一條別的本機分支指到同一提交時,舊版沒有遠端、退回 origin,新版改用那條分支的上游遠端。偏邊緣,但計劃寫的是「不變」。
4. `Issues/預設起點與名冊人數收尾小問題` 的第 1、2 條(`--short` 在分支與標籤同名時回 `heads/<名>`、測試沒覆蓋 detached HEAD 與同名)與本次重寫同一段程式。新寫法的「零條或多條退回目前簽出的分支」仍要處理 `--short` 和同名問題。計劃應連結這篇 Issue,說明是併入處理還是各自處理,否則 Issue 的「什麼條件算修好」會被改寫掉而沒人知道。
5. 現有 reread 測試幾乎都落在 `v1` 退回路徑:`_rr_repo` 用 `git init`,無遠端,本機 master 就是頂端,所以分岔點等於頂端。結果是測試全綠,卻沒有一條在跑 `v2`。S1–S7 要有「本機 main 在頂端之前、有遠端」的夾具。`t_note_audit_reread_check_reminds` ⑫ 與 `ctrl_char_paths` 直接呼叫 `_note_reread_contrast_fp(…, about, oids)`(`scripts/test_lumos.py:68044` 與 `:68384`),簽名改了會一起壞。

## Finding 6

severity: minor
blocking: 否 — 方向是多列、不漏判,但 S3 的「必然相同」措辭比實作強。
引句:「零條或多條退回目前簽出的分支」

問題:S3 說「同一個 repo、同一個頂端……算出的對照指紋應相同」。但分岔點除了 refs 與頂端,還吃「目前簽出的是哪條分支」。零條或多條本機分支指到頂端時(例如另開一條 `backup` 分支指到同一提交,很常見),退回簽出分支的上游遠端;多遠端專案(fork 與 origin)在不同簽出狀態下取到不同遠端,候選主線與分岔點跟著不同。另外 git 逾時(`_lens_git` 預設 20 秒,與 `reread-check` 的 30 秒預算各自計時)也是不確定輸入:prepare 時算成 `v2`、check 時逾時退成 `v1`,同一提交前後指紋不同。

建議:S3 改成「單一遠端、頂端剛好一條本機分支時」;並在計劃說明這兩種情形。

## Finding 7

severity: minor
blocking: 否 — 撤除條件量不到,不影響上線行為。
引句:「治理帳 `note-reread` 事件裡同一篇筆記、同一個分支被重列的次數」

問題:`_note_reread_ledger_found` 只記 `head_sha`、`layer1_fps`(路徑與指紋)、篇數與來源,沒有分支名,也沒有指紋是 `v1` 還是 `v2`、為何退回。RETIRE-IF 的第一句「作者那支檔的改動前後相同」在 `v2` 下是定義上不成立的條件,因為它只在紀錄沒提交時才重列。真正要量的是「退回 `v1` 的次數、原因」和「同一篇在 `v2` 下因主線改動而重列」,帳裡都沒有。REVISIT 到期那天會數不出來。

建議:帳加欄 `fpv`(`v1`/`v2`)與 `fp_fallback`(原因代碼)。

## Finding 8

severity: minor
blocking: 否 — 盲區方向是「該重讀卻被當成已對照」,但需要特殊檔型才發生。
引句:「切成逐檔,每檔去掉 `index` 行」

問題:
- 二進位檔、gitattributes 設 `-diff` 的檔、子模組只會印 `Binary files … differ` 或 `Subproject commit` 一行。`index` 行(唯一帶 blob 編號的地方)又被去掉,所以不同內容的兩次改動指紋相同。`about_code` 裡的非文字檔(資料檔、範本)會中。
- 逐檔切分靠 `diff --git a/X b/X` 標頭對應回 `about_code` 的鍵。路徑含 ` b/` 的檔,標頭可兩種切法,對錯鍵時會被記成「未改」。

建議:對這類檔改記該檔兩端的 blob 編號;切分改用 `--raw -z` 或 `--numstat -z` 先取路徑清單。

## Finding 9

severity: minor
blocking: 否 — 文件與設計一致性,不影響上線行為。
引句:「主線分岔點借本 repo 既有的手動代碼審預設起點算法(主線候選與推送閘共用),不另寫一份。」

問題:這不是「不另寫一份」。`reread-check` 的候選範圍起點仍走 `_note_audit_start`(`_push_range_start` 或 `_lens_push_base`),指紋再用 `_codeloop_default_base`。同一次推送有兩個起點算法,與 `Issues/推送前其他閘的範圍在合過主線時會多算` 在談的是同一類分歧,而且 `_codeloop_default_base` 刻意不做 `_push_range_start` 的「跳過被推那條分支自己的遠端 ref」。`_push_mainlines`(`scripts/lumos:47251`)與 `_push_range_start`(`:47414`)兩處 docstring 與 `pitfalls-code-loop` 的 WHY 都只寫「手動 code-loop check 用」,現在多一個消費者。那篇 Issue 的收斂路要把這個消費者列進去,`pitfalls-code-loop` 的 REVISIT(2026-11-13)也一樣。

建議:說明為何不直接用 `_push_range_start`(它吃 `--push-remote`/`--pushed-ref`,與 S3 要的「跟推送參數無關」衝突)。這個理由要寫進計劃,不然看起來像漏考慮。

## 呼叫者、測試、合約盤點(給編排者核對)

- 非測試呼叫者:`_codeloop_default_base` 只有 `scripts/lumos:51024`。
- `_note_reread_fps`:`scripts/lumos:36638` 與 `:36891`。
- `_note_reread_contrast_fp`:`scripts/lumos:36124` 與 `:36272`;測試直接呼叫 `scripts/test_lumos.py:68044`、`:68384`。
- 合約行:`Systems/筆記內容審`、`pitfalls-code-loop`、`存量漂移守衛`、`bound-tests-gate` 裡沒有 ★INVARIANT★ 綁在對照指紋上。
- 受影響的綁定測試:`t_reread_block_layer1`(WHY 的 `[test:]`)、`t_codeloop_default_base_prefers_newest_mainline`(WHY 的 `[test:]`)、`t_note_audit_reread_check_reminds`(S6)、`t_note_audit_reread_skill_section`(S14)。
- `_NOTE_REREAD_PROMPT_VERSION`(範本版本)與範本雜湊釘(`t_note_audit_reread_template_pinned`)不受影響。
- 「上線標記」:本計劃不新增掛鉤字串,但改說明時不得出現筆記內容審的上線字串,先例見 `舊句兩道轉擋_計劃`〈要一起改的說法〉。

已讀,無 finding:
- 〈緣起〉與詞彙一行。
- PRIOR-ART(空白不忽略的取捨成立)。
- 〈做法〉3(算不出退回 `v1` 的方向是只多列、不漏判)。
- 〈做法〉4 中「紀錄檔格式與檔名正規式不變、`reread-record` 不重算指紋」一節(核對 `scripts/lumos:36806` 屬實)。
- 〈實務隱患〉的金流、對外送出、不可逆三項排除。

總結:最高等級 major,共 9 條 finding,blocking 4 條(Finding 1、2、3、4)。
