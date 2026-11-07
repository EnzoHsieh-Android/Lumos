severity: major

審查對象是 `r1-snapshot.md`(規則包語意覆核級命中走盲判),對照 `scripts/lumos` 與筆記逐項查證。

## 固定席逐條判

- `Systems/pitfalls-code-loop`:**會破壞**一條宣稱,見 F1。該節點寫「設定不可以放 `.lumos/lint.json`——那個檔的每個頂層鍵都被當成「副檔名→命令清單」嚴格驗證」。範圍 1 正好把 `review` 放進 `lint.json` 頂層。收工鉤子要秒級、不派代理這條不受影響,因為範圍 2、不做 1、S9 都守住了。
- `Systems/kotlin規則包`:**不影響**行為,但要跟著改。「接上前範本不接」這句是計劃要改的,`check.py:23` 的註解與型錄第 11 行的「通電批次」說明也會過期(見 F9)。`catalog_problems` 規定引用出處不全的列只准 hint 級(`check.py:393`),跟 d1 的 7 條例外一致。
- `Systems/linter精選目錄`:**不影響**既有行為。「提示級規則預設不接、接了就擋」是範圍 8 刻意改寫的,不算破壞。

## F1 `review` 放進 `lint.json`,跟既有決策相反,也沒處理版本不齊

severity: major
blocking: 是(違反既有明文決策,而且消費專案升級或回退會壞)
- 段落:〈範圍〉1、〈回退〉、〈審計修正紀錄〉舊否決比對。
- 引句:「`.lumos/lint.json` 加選填的 `review` 段,值是「副檔名 → 命令清單」」
- 問題:依賴層同樣想用保留鍵,最後改走另一個檔 `lint-deps.json`,理由就是「同一個檔混著兩種語意」。舊否決比對沒查這一條,spec 也沒說為什麼這次可以破例,更沒比較另開檔(例如 `lint-review.json`)的做法。
  - 升級風險:消費專案照範本寫了 `review` 之後,只要另一台機器或 CI 的工具鏈是舊版,`lint-check` 與 doctor [F] 就會報「value 必須是命令列表」。
  - 回退段只說「驗證器要留著認得 review 鍵」,沒處理這種舊版共存。
- 佐證:
  - file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:237`
  - file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md:95`
  - file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md:103`
  - file: `scripts/lumos:41888`
  - file: `scripts/lumos:39607`

## F2 判定紀錄沒存規則代號,S8 的逐條規則統計做不出來

severity: major
blocking: 是(S8 照字面無法實作)
- 段落:〈範圍〉4(結果檔)、〈範圍〉7、S8。
- 引句:「頂層多一個鍵 `rule_hits: [{"seg": <指紋>, "verdict": "real|false|unsure", "reason": "…"}]`」
- 問題:`seg` 是 sha256 前 16 碼,反推不回規則。命中改完就消失,事後也無法重算。範圍 7 要「每條規則列」,但帳裡沒有 `rule`。放行檔的 `rule` 又是選填(`lint-waive` 沒帶 `--rule` 就算不到)。
- 其他沒列的接線:
  - `_gov_row` 是逐欄投影,不認識 `rule_hits` 就帶不出去。
  - `_GOV_FIELD_TYPES` 沒有 `rule_hits`。程式註解寫過,型別錯會讓整個 gov 當掉,所以要補型別白名單。
  - `_kt_bj_validate` 目前只認 `segments`。
- 佐證:
  - file: `scripts/lumos:17511`
  - file: `scripts/lumos:17601`
  - file: `scripts/lumos:74064`
  - file: `scripts/lumos:41232`

## F3 同片段共用判定,加上 AI 誤報放行綁片段,正好打在「要看型別才分得出對錯」的規則上

severity: major
blocking: 是(判成誤報會永久蓋住同檔同片段的真問題)
- 段落:〈範圍〉3、〈範圍〉5 `false`、〈天花板〉1。
- 引句:「同檔同片段的多處共用同一個身分與同一個判定。」
- 問題:這一級的定義是同樣文字在不同型別下對錯不同,spec 自己的例子就是 `.value.add`。
  - 材料只給「檔內最後一處」,判定卻套到所有同片段。
  - `false` 又自動寫成 AI 放行,而放行綁指紋、不綁版本。`kept` 會把之後同檔同片段的新增命中全部濾掉,以後連命中都不會出現。
  - 情境題的段身分是綁整段材料內容,這裡只綁一行片段。判定看的是前後 8 行,前後文一改,判定就過期卻不會失效。
  - `_lint_waivers_add` 對已存在的指紋直接回「已經放行過了」,記帳那一步遇到同指紋已被人放行的情況沒有定義。
- 佐證:
  - file: `scripts/lumos:42219`
  - file: `scripts/lumos:42244`
  - file: `scripts/lumos:42656`
  - file: `scripts/lumos:41279`
  - file: `scripts/lumos:74064`

## F4 準確率與升降建議的資料來源不成立

severity: major
blocking: 是(RETIRE-IF 與 S8 建議都建立在不可靠的數字上)
- 段落:〈用詞〉人複查、〈範圍〉7、〈實務隱患〉、RETIRE-IF。
- 引句:「`real` 判定至少 20 筆、被人放行少於一成 → 建議移到 `rules/`」
- 問題:
  1. 隱患段自己寫了「判 `real` 被擋時,AI 跑 `lint-waive` 也能放行」。AI 放行的不算人放行,所以「被人放行少於一成」在 AI 代放行時恆成立,會不斷建議升擋。
  2. `--verdict overturn` 沒有任何後果,只是統計欄位。放行還在、命中不會重擋。人推翻了盲判,真問題還是被放行著。
  3. `--verdict` 的值是下指令的人帶的參數,而 ack 的確認提示完全不顯示是哪筆命中、判了什麼。AI 下 `--verdict agree`、人只按 y,就能灌高九成這個數字。
  4. 本 repo 已有 62 筆 AI 放行沒人看過,RETIRE-IF「經人複查的準確率」實務上永遠沒資料,撤除條件不會觸發。
  5. `--ack --all --verdict` 的語意沒定義(會不會把非覆核誤報的 AI 放行也標上去)。
- 佐證:
  - file: `scripts/lumos:41192`
  - file: `scripts/lumos:41179`
  - file: `scripts/lumos:41199`

## F5 判定怎麼接進擋停:落點、簽名與提早返回路徑沒定義

severity: major
blocking: 是(S2、S3 照現況接不進去)
- 段落:〈範圍〉2、〈範圍〉5、S2、S3、S9。
- 問題:
  - 判定要從治理帳讀,而且帳是按分支和合併提交那一側的帳讀(`_kt_bj_read(repo_root, branch)`、`_disp_bj_source`)。但 `_lint_new_verdict(repo_root, diff_range, deadline, worktree, since)` 與 `_codeloop_lint_new_step(repo_root, diff_range, tier)` 都沒有分支或版本參數。spec 沒說簽名怎麼改。
  - `lint-new --diff` 的獨立命令(`cmd_lint_new`)沒帶分支,它顯不顯示覆核命中沒說。
  - `code-loop pass` 走 `mech_only` 只跑「表態與新增告警兩道」。覆核擋下是否進去、`pass` 會不會被自己擋,沒提。
  - 覆核段放在「一般段跑完之後」,但 `_lint_new_tools` 在 `cmd_targets` 為空時直接 `no-files` 早退。只宣告了 `review`、沒有一般 `kt` 命令的專案,覆核永遠不跑。
  - `tools_ran` 為 False 時 `_lint_new_verdict` 也早返回,不會走到覆核判定。
  - `mode` 為 `warn` 或 `off` 時,`real` 該擋還是只報,沒說。
  - 命令沒帶 `{LINT_FILES}` 時,一般段會降級成 `report_only`,覆核段沒定義。
  - `_lint_new_sep_split`(路徑含逗號)的處理也沒說覆核段怎麼辦。
- 佐證:
  - file: `scripts/lumos:42592`
  - file: `scripts/lumos:42623`
  - file: `scripts/lumos:42498`
  - file: `scripts/lumos:74556`
  - file: `scripts/lumos:73895`

## F6 `blind-judge` 指令介面不夠寫成程式

severity: major
blocking: 是(執行者得自己發明介面)
- 段落:〈範圍〉4、〈範圍〉5 `unsure`、S5、S6。
- 問題:
  - `--template` 現在所有份數都從情境段算出來。覆核命中份怎麼選(新旗標、還是接在情境份後面)、`--part` 編號怎麼排,都沒說。
  - 指令一開頭就會因為 `_KT_DT_ERR` 或 `_kt_bj_segments` 失敗而 `return 2`。型錄的情境決策表壞掉,或算不出情境段,覆核命中也連帶判不了。
  - `_kt_bj_validate` 要求有非空的 `segments`,也不准有別的頂層鍵。spec 說「可以單獨一份」,但現在做不到。
  - 記帳時要驗 `seg` 對得上被推版本的命中,等於得再跑一次覆核命令。範本、記帳、check 三處各跑一次,預算與逾時沒統一。範本那次跑漏了就印「沒有命中」,check 卻擋,形成「叫你判、卻沒東西可判」的死結。
  - `--unsure` 與既有 `--disagreements` 的互斥關係沒定義。
- 佐證:
  - file: `scripts/lumos:74130`
  - file: `scripts/lumos:74188`
  - file: `scripts/lumos:74064`
  - file: `scripts/lumos:74175`

## F7 「覆核沒跑」的政策跟一般段相反,而且不留帳、對所有專案都印

severity: minor
blocking: 否(是 spec 明講的取捨,不是缺陷;但有具體副作用要補一句)
- 段落:〈範圍〉2、6,〈實務隱患〉時間預算,S7。
- 引句:「所以專案很大時覆核可能常常沒跑」
- 問題:
  - 一般段把「預算不足沒跑到」判成擋,覆核段判成不擋。
  - 一般段工具沒裝會記 fail-open 帳並被統計,覆核段只印一行,不留帳,等於多一條不被數的繞道。
  - 「沒有 review 段就印覆核沒跑:沒宣告」會在非 Kotlin 專案的每次推送都印。
  - doctor 對「宣告了 kt 卻沒有 review 段」提醒,但 kt 宣告可能只有 detekt,沒用規則包,會誤唸。
  - 這幾處承認的風險沒有回頭條件(專案 CLAUDE.md 鐵則 4)。
- 佐證:
  - file: `scripts/lumos:42675`
  - file: `scripts/lumos:42749`
  - file: `scripts/lumos:4195`

## F8 `--smoke` 不會驗 `review` 的命令

severity: minor
blocking: 否(不影響擋停正確性,只是少一層事前驗證)
- 段落:〈範圍〉1、S1。
- 問題:`--smoke`、detekt 提醒與 `config.items()` 迴圈都只處理值是 list 的鍵,`review` 的值是 dict 會被整個跳過。spec 只講「不把 review 當副檔名」,結果是覆核命令永遠沒被冒煙驗過,壞了要到推送時才以「工具不可用」出現。
- 佐證:
  - file: `scripts/lumos:41070`
  - file: `scripts/lumos:40075`

## F9 要跟著改、spec 沒列的手冊與筆記

severity: minor
blocking: 否(文件同步項,不影響行為正確性)
- 段落:frontmatter `lands_in`、〈範圍〉8。
- 問題:下列檔案會跟實作脫節。
  - `skills/lumos-code-loop/SKILL.md:26`:盲判只在「表態裡有 `kt-situation` 時」才提,沒覆核命中的情況。
  - `skills/lumos-project-notes/commands/06-代碼審與推送.md:15`:同上。
  - `skills/lumos-project-notes/commands/test-quality-standard.md:40`:放行與 AI 放行的說明。
  - `skills/kotlin-idioms/checks-catalog.md:11`:「語意覆核級…要等計劃接上」。
  - `check.py:23`:「接上前不擋」註解。
  - `lint-waive`、`code-loop blind-judge` 的 argparse 說明與 `_CMD_HELP`。
  - `Systems/lint-declaration-health`(`lint.json` 格式的家)與 `Systems/棧別提問表態閘`(盲判與帳欄的家)沒列進 `lands_in`。
- 佐證:
  - file: `scripts/lumos:76333`
  - file: `scripts/lumos:77363`
  - file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:61`

## F10 推送閘判斷出處不全、讀型錄的失敗行為沒定義

severity: minor
blocking: 否(邊界情境,現有慣例可直接照抄)
- 段落:〈範圍〉4「讀型錄主表」、S3。
- 問題:spec 只說範本材料用 `main_rows` 讀型錄,但 S3「出處不全只提醒」是在擋停那一刻判的,同樣要讀。找不到工具鏈或型錄讀不到時,是擋、放行還是提醒沒寫。
- 佐證:既有情境題對「型錄讀不到」有明確做法(判無法驗證擋下),可照抄:file: `scripts/lumos:38312`

## F11 閾值敘述自相矛盾

severity: minor
blocking: 否(筆誤級,但驗收會對不上)
- 段落:〈範圍〉7。
- 引句:「七成、八成是本案自己的數字,上線後照 REVISIT 回頭校準」
- 問題:同一段實際用的門檻是一成、20 筆、九成、八成,全文沒有七成。

## 風險類逐類答覆

- **守衛面**:有隱患,見 F3、F4、F5。
- **金流、對外送出**:無。只讀本機檔、跑本機 ast-grep、不連網。
- **不可逆**:大致同意 spec 的說法,退提交即回原狀。但已寫的 AI 放行會永久靜默同片段(F3),這一點 spec 沒算進去。
- **材料含作者可控文字**:盲判材料帶命中行前後 8 行程式碼,註解可以對代理下指示。這是系統天花板(刻意偽造),跟既有情境題盲判同一條,不另標 finding。
- **併發**:放行檔與治理帳都有鎖、只追加,現有機制足夠,無新增隱患。

## 逐節

- 前言、用詞、PRIOR-ART、依據來源、回退(升級共存之外)、預期值表:已讀,除上述各條外無 finding。
- 引用核對:`check.py` 的 `main_rows` 存在;rules-review 共 12 條、rules-hints 共 50 條;出處不全的規則在提示級共 7 個型錄列。
- 「一條規則只對一列」成立,但反過來有多條規則共用同一列(STATE-7 有 3 條、ARCH-50 與 DATA-30 各 2 條)。範本材料四欄對這幾條會重複,不構成 finding。

最嚴重 severity:major;blocking 共 6 條(F1、F2、F3、F4、F5、F6)。
