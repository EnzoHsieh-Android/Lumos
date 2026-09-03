# r1 架構對齊審(主session鏡頭利用率_計劃)

審材(凍結):`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/26a6b57a-9efc-4073-b845-c27e42a2fbb1/scratchpad/主session鏡頭利用率-r1.md`
只判「跟本 repo 既有做法不一樣」;不找 bug、不評風格。

## 一、分層與依賴方向(hook 直接 append 帳,還是經 lumos 子命令?)

既有做法(逐條核過):

- **七本帳的寫入全在 lumos 這一層**:`_usage_log` file: `scripts/lumos:7382-7392`(唯一寫者,路徑 `env.vault.parent / ".usage-log.jsonl"`,呼叫點只有 `cmd_show` file: `scripts/lumos:7398` 與 context file: `scripts/lumos:7457`);ci 帳 `_ci_log_path` file: `scripts/lumos:14864-14871`;code-loop 事件 `_codeloop_gov_log` file: `scripts/lumos:16773-16784`;governance 帳寫者註明「寫者=doctor --ci + anchor approve」file: `scripts/lumos:723`。也就是說,**每一種留痕都有一支 lumos 子命令當入口**(canary record / code-loop pass / anchor approve / ci-wait)。
- **hook 這一層要圖譜領域的東西,一律 subprocess 呼 lumos,不自己碰 vault**:impact-hook file: `scripts/hooks/claude/impact-hook.py:473-484`(`lumos impact --file … --repo …`),連 vault 找不到都是靠 lumos 的 rc=3 才知道 file: `scripts/hooks/claude/impact-hook.py:490`;Stop hook 同一條路 file: `scripts/hooks/claude/check-graph-sync.py:352-356`(註解明寫「跟 pre-commit/pre-push 同一條路」)。
- **hook 讀帳有先例、寫帳沒有(活的)**:ci-status-hook 只讀 file: `scripts/hooks/claude/ci-status-hook.py:65-78`;emit_queue_patrol 只讀只印 file: `scripts/hooks/claude/check-graph-sync.py:310-345`。唯一「hook 直接 append repo 內帳檔」的先例是 verification-rot-check file: `scripts/hooks/claude/verification-rot-check.py:404-415`,但它 2026-08-21 已被撤除、帳檔從未被建立 file: `scripts/merge-claude-settings.py:93-94`,lumos 端也標「留 loader 只是假名額」file: `scripts/lumos:3651`。

### f1 impact-hook 直接 append usage-log,繞過該帳唯一寫者(跨層直呼)

現況是 hook 不寫帳、要什麼都經 lumos 子命令;本案讓 PreToolUse hook 自己開檔 append 到 lumos 擁有的 `.usage-log.jsonl`,等於這本帳從此有第二個寫者、且 schema 由 hook 端自訂。既有的對齊寫法是加一支子命令(例:`lumos lens push …` / `lumos lens tally …`,同 `lumos canary record` 形態)由 hook subprocess 呼叫,順帶沿用 lumos 既有的 vault 定位與寫入函式。
引句:「每次真的注入時,把 {ts, session_id, file, pinned 節點名} 追加到 `docs/.usage-log.jsonl`」
severity: major
blocking: 是

### f2 治理觀測事件寫進檢索語料帳,偏離「一機制一本帳 + 治理事件帶 kind 進 gov」

`.usage-log.jsonl` 的宣告用途是檢索側語料(「A2 事件帳種子…先累語料不進分數;未來 frecency」file: `scripts/lumos:7382-7385`),而 `lumos gov --stats` 的七源是 bypass / rot-queue / governance / signoff / kill / canary / ci,每源各自一本、各自映射一個 `kind` 欄 file: `scripts/lumos:3648-3685`——usage-log 刻意不在其中。本案把「推了什麼、對帳結果」這種治理觀測事件塞進 usage-log,一是同一本帳從此兩種語意(節點被查閱 vs 節點被推送/回合彙總),二是新事件在 `lumos gov` 全程隱形、也不吃 gov 的去重與時窗。既有對齊做法=新開一本 `docs/.lens-log.jsonl` 並在 `load(...)` 加一源(rot-queue 當年就是這樣拆出來的)。
引句:「三處各加一小段,同帳同慣例」
severity: major
blocking: 是

## 二、命名與錯誤處理

### f3 `cmd` 欄值域今天只有 lumos 子命令名,"pushed"/"lens-tally" 不是命令

實帳 375 列,`cmd` 只有 `context`(169)與 `show`(206)兩個值,寫入點也只在這兩支子命令 file: `scripts/lumos:7398`、`scripts/lumos:7457`——這個欄位的既有語意是「哪支 lumos 命令讀了這篇」。本 repo 表達「事件類別」的欄位慣例是 `kind`,值是過去式動詞(warned/approved/passed/ran/degraded/converged/green,見映射 file: `scripts/lumos:3652-3676`;canary 帳同 file: `docs/.canary-log.jsonl`)。`pushed` 是過去式動詞卻放進 `cmd`,`lens-tally` 則連動詞都不是,兩邊都不合。結構(append-only jsonl、ts 開頭)是對的。
引句:「`cmd: "pushed"`(同一份帳、同一慣例;best-effort 靜默)」
severity: minor
blocking: 否

### f4 lens-tally 那筆沒有 `node`,pushed 那筆一列多節點,破壞 usage-log「一列一節點」的列形

既有列形固定 `{ts, node, cmd}`,`node` 必有且是單一相對路徑 file: `scripts/lumos:7389-7390`;本案的 pushed 列多了 `session_id`/`file` 且節點是複數,tally 列則只有 `{pushed, touched}` 完全沒有 `node`。任何按 node 聚合的讀者(frecency 是這本帳的既定下游)都要多寫分支才不會被無 node 的列絆到。
引句:「並追加一筆 `cmd: "lens-tally"` {pushed, touched}」
severity: minor
blocking: 否

### f5 ⚠ 把既有 TTL 標記的位置寫成「家目錄」,實際慣例是系統 tmpdir

`_ttl_marker_path` 是 `tempfile.gettempdir() / lumos-impact-<session_id> / <sha1[:16]>` file: `scripts/hooks/claude/impact-hook.py:104-107`,惰性清理也掃 tmpdir file: `scripts/hooks/claude/impact-hook.py:114`。設計把它記成家目錄——本身是描述錯誤,但本案正是靠「同慣例」立論,照設計文字落地會多開一個 hook 狀態位置。標 ⚠ 因為這只影響文字,不影響第一段要寫的帳。
引句:「鍵是 session+檔,存在家目錄」
severity: minor
blocking: 否

**fail-open 部分對齊,不列為不對齊**:設計寫的 best-effort 靜默,與 `_usage_log` 的 `except Exception: pass` file: `scripts/lumos:7391-7392`、rot-queue 的 `except OSError: pass` file: `scripts/hooks/claude/verification-rot-check.py:414-415`、ci-status-hook 的頂層 `sys.exit(0)` file: `scripts/hooks/claude/ci-status-hook.py:97-99` 一致;Stop hook「只印不擋」也與 check-graph-sync 全程 stderr 軟提醒一致 file: `scripts/hooks/claude/check-graph-sync.py:1-13`。

### f6 帳檔怎麼定位沒裁,現有三種定位法而 impact-hook 一種都沒有

既有三種:lumos 用 `env.vault.parent` file: `scripts/lumos:7387`;rot 系 hook 用 `find_graph_root()` 再 `.parent` file: `scripts/hooks/claude/check-graph-sync.py:72`、`scripts/hooks/claude/verification-rot-check.py:405`;ci-status-hook 用 `git rev-parse --show-toplevel` + glob `docs/*-knowledge` 找同層帳 file: `scripts/hooks/claude/ci-status-hook.py:25-44`。impact-hook 今天完全不知道 vault 在哪(只有 `repo`,vault 解析全丟給 lumos file: `scripts/hooks/claude/impact-hook.py:466-490`),要寫帳就得新增定位邏輯;設計只寫了檔案路徑字面,沒說沿用哪一種,實作時很容易長出第四種。結構其他部分對。
引句:「每次 commit 帶著走;append-only 行級合併,多機合併不衝突」
severity: minor
blocking: 否

## 三、第二種做法(自創對帳邏輯 vs 沿用既有函式;兩週後腳本放哪)

沿用面是對的:設計明寫 Bash 路徑走既有 `extract_bash_file_paths` file: `scripts/hooks/claude/check-graph-sync.py:218`,這與 impact-hook / check-graph-sync 之間「同源清單、同一條路」的慣例一致(CODE_EXTS 註解 file: `scripts/hooks/claude/impact-hook.py:26`)。以下兩條是沒對齊的。

### f7 ⚠「Edit 之前碰過」的順序判定,既有 collect_turn_actions 給不出來——會逼出第二支逐字稿解析

`collect_turn_actions` 回傳 `(file_paths, bash_commands)` 兩個扁平 list,沒有先後、沒有時間戳,也不區分是哪一次 Edit 之前 file: `scripts/hooks/claude/check-graph-sync.py:107-146`;它今天的下游只需要「這回合有沒有動過 code」,不需要順序。本案的判準是「那次 Edit 之前碰過」,靠「多收 Read 的 file_path」是判不出來的,實作只剩兩條路:改共用函式的回傳形態(會動到 Stop hook 現有四層閘的輸入),或另寫一支帶順序的逐字稿解析(第二種做法)。設計沒有裁,也沒說要改共用函式的介面。標 ⚠ 是因為若最後選「不要求順序、整回合有碰就算」,這條就自動消失——但那等於改了審材裡的定義。
引句:「`collect_turn_actions` 多收 Read 的 file_path;收工時把本回合 pushed 事件對上」
severity: major
blocking: 是

### f8 兩週後的重算腳本沒指定位置與形態,既有慣例是 governance/eval/<主題>/recount.py

既有唯一同型先例:`governance/eval/seat-coverage/recount.py`——唯讀、零副作用、帳檔路徑吃 argv 帶預設、結果直接印、開頭標「什麼時候用/資料源/唯讀零配額」file: `governance/eval/seat-coverage/recount.py:1-14`,並由對應 Verification 的 `revalidate_when` 指名重跑 file: `docs/lumos-toolchain-knowledge/Verification/2026-09-03_席間覆蓋率離線量測.md:6`、file: `docs/lumos-toolchain-knowledge/Verification/2026-09-03_席間覆蓋率離線量測.md:19`。設計只說「一支唯讀腳本」,沒說放 `governance/eval/<主題>/recount.py`、也沒說 REVISIT 那條要指向它;唯讀這點與慣例一致,位置與掛勾方式沒對齊。
引句:「一支唯讀腳本讀使用帳算總命中率與分佈」
severity: minor
blocking: 否

---

不對齊共 8 條,其中 major 3 條。
