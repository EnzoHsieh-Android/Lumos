severity: major

我把凍結快照逐節讀完、對照程式碼查證。有 4 條 major(都擋)、9 條 minor,最嚴重是 major。

## F1
severity: major
blocking: 是——白名單是這份 spec 對「被打開的專案不可信」的唯一防線,而這個包含判準繞得過去,實作者照字面做就是破洞。
- 段落:〈用詞〉「自動執行白名單」。
- 問題:`--config` 的值只寫「要落在安裝目錄裡」,沒說要不要正規化(`..`、符號連結)。禁字清單(`;|&` 反引號 `$<>>*?~` 換行)不含 `..`。
- 繞法:`--config $HOME/harness/lumos-toolchain/../<專案自己的路徑>/sgconfig.yml`,字串前綴對得上,實際指到專案自己的設定檔。
- 後果:該設定檔可宣告自訂語言並載入原生程式庫,回合結束就會執行。S3 的反例清單沒有 `..`,測不到。
- 引句:「而且它的值(展開 `$HOME` 後)要落在 lumos 工具鏈自己的安裝目錄裡」
- 佐證:file: `scripts/lumos:32947` 安裝目錄有 `$LUMOS_HOME` 與 `~/harness/lumos-toolchain` 兩個來源,spec 沒指定用哪個基準、也沒指定 realpath 比對。

## F2
severity: major
blocking: 是——正例與規則自相矛盾,實作者照 S3 寫會放行不該放行的,照規則寫又過不了 S3;實際出貨的範本還沒被任何條款覆蓋。
- 段落:〈用詞〉白名單與 S3。
- 引句:「整條命令除了開頭的 `$HOME` 之外不得含」
- 引句:「沒給 `--config` 或 `--config` 指向專案自己的檔 應 不通過」
- 引句:「ast-grep scan --config x.yml --format sarif」(S3 的「應 通過」正例)
- 矛盾一:`x.yml` 是相對路徑,解析後落在專案,依上面那條規則應不通過,卻被列為正例。
- 矛盾二:`$HOME` 在 `--config` 的值裡,不在命令開頭,「開頭的 `$HOME`」到底指哪裡不明。
- 風險:實作者把它收緊成「命令開頭」,真實範本會全數被拒,功能靜默變成永遠 rc3。
- 佐證:file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:158` 消費專案的實際範本是 `ast-grep scan --config $HOME/harness/lumos-toolchain/configs/ast-grep/kotlin-android/sgconfig.yml --format sarif {LINT_FILES} > {LINT_SARIF_OUT}`,S3 沒有用它當正例。

## F3
severity: major
blocking: 是——手動驗收 S7 照字面不可能通過,而且整個設計會漏掉最常見的短會談。
- 段落:〈用詞〉「這一回合碰過的檔」、範圍 3、S4、S7。
- 引句:「這一次不檢查、只寫時間戳,下一次才開始」
- 引句:「在一回合裡寫進一處規則包會抓的壞寫法並收工時」
- 引句:「在暫存區實驗專案複本用 claude -p 實跑一次」
- 矛盾:`claude -p` 每次呼叫都是新會談,收工就是「第一次收工」,依範圍 3 不檢查、只寫時間戳,所以 S7 不可能擋下。S4 又明寫「第一次收工應不檢查」。
- 同一原因的影響:單回合的會談(`-p`、無人看顧的自動選題 loop)永遠不被這道檢查碰到。這與使用者原話「code review 的 loop 中就檢查乾淨」的用途衝突。
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:985-1003` 既有 `main()` 只有 Stop 一個入口,沒有回合開頭事件可記時間戳;spec 也沒說明為何不改在回合開頭記。

## F4
severity: major
blocking: 是——鉤子與 `lint-new` 之間沒有機讀介面,指令一崩潰就會誤擋模型。
- 段落:範圍 1、範圍 3、〈用詞〉「告警身分(指紋)」。
- 引句:「最多印 20 條、其餘印條數」
- 引句:「只在 `lint-new` 回 rc1 時擋」
- 引句:「這次工作樹檢查新增告警的指紋多重集合(同一指紋出現幾次也算),排序後取雜湊」
- 缺口一:`lint-new` 只列了 `--diff`、`--worktree`、`--only-stdin`、`--budget`,沒有 `--json` 或固定的機讀行。鉤子是獨立檔、不能 import lumos,只能解析人讀文字。
- 缺口二:批次雜湊要全部指紋,可是輸出只印前 20 條,超過 20 條時 S4「同一指紋多出一處應算新的一批」測不到。
- 缺口三:rc1 同時是「擋」和 Python 未捕捉例外的結束碼。
- 缺口三的後果:`lint-new` 裡任何例外會讓鉤子用空清單回 `decision: block`,模型被攔下卻看不到任何告警。
- 佐證:file: `scripts/lumos:74530-74540` 的 `_cli()` 只接 `WriteBlocked`,其餘例外是 traceback、結束碼 1。
- 佐證:file: `scripts/lumos:72262` 推送前掛鉤就是為了這個原因另外用 `LUMOS-BLOCKS:` 當「唯一機讀通道」。

## F5
severity: minor
blocking: 否——只是理由那句寫錯,實際行為與〈天花板〉1 一致。
- 段落:範圍 3 最後一條。
- 引句:「所以續做那輪改的檔,下一次收工會被查」
- 引句:「續做那輪新加的告警,等代碼審通過前或推送前閘」
- 問題:擋下後的續做會再觸發一次 Stop(帶 `stop_hook_active`),那次不檢查,卻先寫入時間戳 T2。續做時改的檔 mtime 早於 T2,下一個使用者回合讀到 T2 就不算「碰過」。
- 結論:被修的檔永遠不會被複查,與〈天花板〉1 自相矛盾。
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:889-899` `stop_block_decision` 遇到 `stop_hook_active` 直接 False。

## F6
severity: minor
blocking: 否——只影響既有「改 code 沒動圖譜」那道在大逐字稿下的預算,且該道 fail-open。
- 段落:範圍 3「時間」。
- 引句:「55 × 0.7 − 12 = 26.5 秒,不少於它實測需要的 25 秒」
- 問題:這個算式只扣了 lint 的 12 秒。把 `_BUDGET_START` 提早到 `main()` 開頭之後,它還要扣掉鉤子啟動、`emit_queue_patrol` 和整份逐字稿的讀取剖析。
- 現況:逐字稿讀取發生在第一個 `_inner_budget` 之前,所以現在沒被算進去。〈天花板〉的 REVISIT 也自承逐字稿是 406MB、常駐約 4GB。
- 後果:大逐字稿加上 lint 跑到上限時,既有那道只剩約 26.5 − X 秒,低於 25 秒,`_impact_missing` 逾時就靜默回 `[]`。
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:211`(整檔 `read_text`)、`:327`(第一次 `_inner_budget`)、`:732-734`(惰性記時)。

## F7
severity: minor
blocking: 否——前例描述不實,且若直接抄既有解析迴圈,少數狀態會錯位。
- 段落:PRIOR-ART ②、範圍 2 改動清單。
- 引句:「沿用既有 `_handoff_files` 那一族的 `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all` 解法」
- 引句:「`R` 照它給的舊路徑當基準」
- 問題一:全 repo 沒有任何 `--no-optional-locks`,這是新增而不是沿用。
- 問題二:`_handoff_files` 的解析是內嵌迴圈,只判 `xy[0] in "RC"`,不是可重用函式。
- 實測:用 `git add -N` 加上 `mv`,`status -z` 吐出 ` R b/Foo.kt|a/Foo.kt|`(R 在第二格)。照既有迴圈會把舊路徑當成獨立條目,前三個字元被吃掉,基準配錯。
- 佐證:file: `scripts/lumos:72868`、`scripts/lumos:72877`。

## F8
severity: minor
blocking: 否——只在 lint-new 被強殺後殘留快照時才出現。
- 段落:範圍 2、範圍 3。
- 引句:「路徑一律相對 `git rev-parse --show-toplevel`;`.lumos/` 底下的一律不掃」
- 引句:「快照暫存若因 SIGKILL 殘留,照既有規則一天後清」
- 問題:`.lumos/` 排除只寫在 lint-new 內。鉤子自己算「碰過的檔」(非空、≤50)時沒有這條。
- 殘留情境:快照放在 `.lumos/lintbase-*`,repo 沒有任何 ignore 規則,殘留的 `.kt` 副本會是未追蹤檔。它們的 mtime 晚於時間戳,算進 50 支上限,也會被既有收工點名當程式碼檔列出。spec 把 SIGKILL 當成設計內路徑,殘留機率比現在高。
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:36-44`(EXCLUDE_PATH_CONTAINS 沒有 `.lumos`)。
- 佐證:file: `scripts/lumos:40515`(`tempfile.mkdtemp(prefix="lintbase-", dir=.lumos)`)。
- 佐證:file: `.gitignore`(沒有 `lintbase`)。
- 順帶:`:347` 鉤子既有的 `_git_status_entries` 用不帶 `-z`、不帶 `--no-optional-locks` 的 `git status`。這與 spec 自己「一般 git status 會改寫索引」的前提相反,卻沒說鉤子的清單要不要改。

## F9
severity: minor
blocking: 否——只是白跑,但每回合都跑。
- 段落:範圍 3「條件」。
- 引句:「條件:專案根有 `.lumos/lint.json`」
- 引句:「只跑通過自動執行白名單的命令」
- 問題:條件只看宣告檔存在,不看有沒有白名單命令。
- 具體失敗:本 repo 的 `.lumos/lint.json` 只宣告 `py` 的 ruff,每次改 `.py` 的回合結束都會啟動一次 lumos(約 0.8 秒),必然落到 not-checked(rc3)。
- 連帶:這種空轉會稀釋 RETIRE-IF 的「零擋停」判讀。
- 佐證:file: `.lumos/lint.json:2`。

## F10
severity: minor
blocking: 否——只是文字不一致。
- 段落:S1。
- 引句:「跟改動清單沒有交集 應 判 no-files」
- 問題:S1 這句主詞是 `--only`,範圍 1 與 S1 其他句都叫 `--only-stdin`,`--only` 沒定義。

## F11
severity: minor
blocking: 否——記帳說法與程式不符,不影響判定。
- 段落:範圍 5。
- 引句:「分岔點算不出來或等於 HEAD 時照 check 既有規則放行並記帳」
- 現況:既有規則只有「算不出 merge-base」會 `_gate_failopen` 記帳;`mb == head_sha` 那條直接放行、不記帳。
- 佐證:file: `scripts/lumos:71505`(無記帳)、`scripts/lumos:71509`(有記帳)。

## F12
severity: minor
blocking: 否——是翻案要補紀錄,不是設計壞。
- 段落:〈實務隱患〉擋停迴圈、〈開審前的改寫〉。
- 引句:「一個會談最多擋三次」
- 問題:既有決策寫的是「收工 Stop hook 擋一次兩家一致…同 session 只擋一次,不算重開 nag」。spec 讓同一支鉤子單會談最多擋三次(lint)再加既有一次,卻沒標明這是對該決策的延伸或翻案,「舊否決對照」也沒提。
- 佐證:file: `docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:30`。

## F13
severity: minor
blocking: 否——撤除條件現在量不到。
- 段落:RETIRE-IF。
- 引句:「回合結束檢查連續三個月零擋停,降成只在審查迴圈跑」
- 問題:`lint-new` 不寫治理帳,鉤子擋停也沒登記事件,而 `stop-block/` 標記七天就被清掉。三個月後沒有任何資料能判斷「零擋停」,改檔前推列的「沒有一列被推出」也一樣。
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:787-800`(標記只留七天)。

## 各節狀態
- 〈用詞〉:有 F1、F2、F4、F5(時間戳段)。
- 範圍 1:有 F4,其餘已讀。
- 範圍 2:有 F7、F8。
- 範圍 3:有 F3、F5、F6、F8、F9。
- 範圍 4:已讀,無 finding。我核對了 `extract_delta_text` 已有 2MB 上限、`_ttl_lazy_cleanup`、`cmd_impact` 找不到圖譜時的提早返回、決策表 D-1 到 D-32 與停用字檢查(`check.py:94-189`),都與 spec 描述相符。
- 範圍 5:有 F11。
- 範圍 6:已讀,無 finding。手冊在 `skills/lumos-code-loop/SKILL.md` 有對應的「派審查員」步驟。
- 〈開審前的改寫〉:已讀,無 finding。
- 〈實務隱患〉:有 F12。
- 驗收條款:有 F2、F3、F10。
- 〈回退〉:已讀,無 finding。
- 〈天花板〉:有 F5(與範圍 3 矛盾)。
- 〈審計修正紀錄〉:已讀,無 finding。
- 交叉引用:前言與正文的 `[[…]]` 目標都存在,例外是 `Systems/回合結束寫法檢查`,它是要新開的節點。`lumos rejections`、`_handoff_files`、`HOOK_BUDGET`、`_BUDGET_START`、`stop-block/`、`stop-printed/`、`keep_going` 都已核對存在。

## 實務隱患逐類
- 併發:
  - 多會談共用工作目錄已在 spec 內承認。
  - 快照目錄名是隨機的,同時跑 `lint-new` 不會撞。
  - 鉤子自己的 `git status` 沒有 `--no-optional-locks`(見 F8),會與別的會談的 `git commit` 搶索引鎖。這是既有行為,範圍 2 沒處理。
- 效能熱路徑:
  - Stop 每回合最多多 13 秒,外加 lumos 啟動約 0.8 秒(見 F6、F9)。
  - 改檔前鉤子每次 `.kt` 編輯多讀一次型錄表。單次最大 2MB 內容的剝註解是線性的,不構成問題。
  - `code-loop pass` 從幾乎瞬間變成可能跑 pitfalls、表態和最多 300 秒預算的新增告警,spec 沒提這個延遲,但看不出會弄壞既有呼叫端。
- 資源釋放:SIGTERM 與快照清理的設計成立,殘留見 F8。
- 回滾:〈回退〉完整,與程式一致。
- 會不會擋錯人:
  - 共用工作目錄時,別人改的檔會被算進來,spec 已承認。
  - F4 的崩潰誤擋是新增的誤擋路徑。
  - F3 反過來是漏擋短會談。

## 節點固定席
- `Systems/lumos-cli-lifecycle` 的 ★INVARIANT★:不影響。本案只改 `HOOK_BUDGET` 數值與鉤子行為,不碰 re-inject 的 sentinel 區間;`merge-claude-settings.py` 的 `_equivalent` 遷移會取代舊註冊而不重複新增。
- `Systems/canary-audit`、`Systems/design-loop`、`Systems/lumos-cli-read`:不影響。本案沒碰 canary 記帳、處置閘第五步和 search 濾網。
- `Systems/pitfalls-code-loop`(★RISK★):大致不影響,但有一處要留意。
  - 本案在 `code-loop pass` 加機械檢查,而該節點記著「閘放在 pass 不放 check,因為 check 不知道分支對應哪個迴圈」,以及不選「pass 內重跑處置閘」。
  - 這裡加的是新增告警與表態,不依賴迴圈編號,沒有碰到那條否決。
  - 但 spec 的舊否決對照沒有提到這條。

最嚴重的 severity 是 major,blocking 共 4 條(F1、F2、F3、F4)。
