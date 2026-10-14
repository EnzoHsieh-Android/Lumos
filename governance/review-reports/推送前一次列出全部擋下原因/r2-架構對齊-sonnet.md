severity: minor

第二輪架構對齊報告:這份設計大方向照既有做法走。收集擋下承襲 pre-commit 的 Gate L,`push-preview` 命名對齊 `push-range`,借用 git 自己的 `--dry-run`。我沒找到跨層直呼,也沒發現會讓專案多出第二種做法的 major。以下五條都是小處,可以在實作時順手收。

severity: minor
blocking: 否 — `loop escape --auto` 已有「掛鉤呼叫一支會記帳的子命令」的先例,方向可行,只是計劃的理由寫得跟程式註解不一致,另漏了一個必要登記。
引句:「專案慣例是「做判定的那一方順便落帳」,掛鉤不直接寫帳;印彙總正是 `push-summary` 這支子命令自己的工作」
對照:
- 慣例原文:`scripts/lumos:1500-1504`,`_gate_event` 的說明寫「沒有任何先例是 hook 呼叫一個專門用來記帳的端點」,並且 2026-09-07 的結論是「工具沒有給外部腳本寫治理帳的入口」。
- 既有的實際先例:`scripts/hooks/pre-push:464`,掛鉤呼叫 `loop escape --auto`,把掛鉤算好的 `--desc` 交進去記帳。
- 閘名名單:`scripts/lumos:9331`,`_KNOWN_GATES`。不在名單上的閘名,`_gate_event_or_warn`(`scripts/lumos:1520-1530`)會警告並拒寫。
判定理由:
- `push-summary` 吃的是掛鉤給的 `--blocks-file`,它自己沒做任何判定。「做判定的那一方記帳」這個說法站不住。
- 較誠實的理由是:掛鉤呼叫帶副作用的子命令已有 `loop escape --auto` 先例,而彙總本來就必須在所有閘之後才能算。
- 計劃沒寫要把 `prepush-summary` 加進 `_KNOWN_GATES`,也沒提 `t_gov_stats_gate_drift` 那條漂移釘。漏了這步,S12 的事件會被靜默拒寫。
- 建議:改引 `loop escape --auto` 當先例,並在實作清單加上「`_KNOWN_GATES` 登記 `prepush-summary`」。

severity: minor
blocking: 否 — 票檔放哪裡是實作細節,只是跟既有慣例不同,沒有第二套機制。
引句:「`push-preview` 在 `git rev-parse --git-common-dir` 底下的 `lumos/` 建一個檔 `push-preview.<隨機值>`」
對照:
- 既有的跨程序暫存檔都放 `~/.cache/lumos/<功能名>/`:`scripts/lumos:47465`(dispatch-lens)、`:41302`(drift-defs)、`:49591`(bound-filter)。
- 掛鉤自己的暫存用 `$_PP_TMP`。
- `scripts/lumos` 對 git 目錄只做唯讀的 `rev-parse --git-dir` / `--git-common-dir`(`:36852`、`:39140`、`:26910`),我沒找到寫進 `.git` 底下的先例。
判定理由:
- 計劃選 git-common-dir 的原因是同 repo 範圍,而且 `core.hooksPath` 讓多個工作樹共用掛鉤。理由合理,但計劃沒交代,也沒說為什麼不沿用 `~/.cache/lumos/push-preview/<repo 鍵>/`。
- 建議補一句取捨,或改走 `~/.cache/lumos/`。

severity: minor
blocking: 否 — S9 會抓到漏網的寫入器,但「兩支」這個數字對不上現況,實作時容易只補這兩支。
引句:「lumos 的兩支治理帳寫入器在分流之前,看到有效的預演票(同一條驗法:環境變數有值、票檔存在且相符)就替事件標上 `preview: true`」
對照:
- 共用分流:`scripts/lumos:1544` 與 `:1657`,兩處都呼叫 `_gov_routes_local`。
- 直接寫版控帳、不經分流的寫入器:`_codeloop_gov_log`(`scripts/lumos:49326`,直接 append `.governance-log.jsonl`)、`_bound_tests_log`(`:49360` 起)。
判定理由:
- 預演時 `code-loop check` 與受波及合約測試正是會呼叫這兩支,事件會寫進版控帳。
- 計劃第 8 點的盤點步驟有留口,但前提寫成「兩支」。
- 統一規則做法:把「有效預演票就不進版控帳」收進一個共用的追加函式或 `_ledger_tail_needs_newline` 之前的同一個守門處,不要逐支補。這也對應 `_gov_routes_local` 的「兩支共用一支判定,不各抄一份」精神。

severity: minor
blocking: 否 — 掛鉤讀工具輸出本來就有兩種慣例,新增第三種不影響正確性,只是通道變多。
引句:「這個模式最後多印一行 `LUMOS-BLOCKS: <reason_kind 以逗號分隔>`,掛鉤讀它」
對照:
- `scripts/hooks/pre-push:440`,掛鉤對 `--json` 輸出 grep 欄位(`"autoloop_full": *true`)。
- `scripts/hooks/pre-push:462-471`,掛鉤對文字輸出 grep 中文句子(「受波及合約的測試沒過」、「tier=high 且」)。
- 以 `LUMOS-` 開頭的前綴(`scripts/hooks/claude/*.py`)是給 Claude 讀的提示,不是給掛鉤讀的機器行。
判定理由:
- 計劃同一點已經讓 `--json` 帶 `blocks` 清單,所以掛鉤要的資料在 `--json` 裡就有。再加一條文字機器行,等於同一份資料兩個通道。
- 若為了同時保留給人看的文字輸出而不改用 `--json`,建議明寫為什麼不沿用 grep 句子的既有做法,並讓 `LUMOS-BLOCKS:` 成為唯一的機讀通道。

severity: minor
blocking: 否 — 兩個方向的版本探測用了不同手法,但各自有理由。
引句:「檔裡要有一行 `# lumos-hook-cap: push-preview`;沒有就回 2」
對照:
- `scripts/hooks/pre-push:500-501` 與 `:529-530`,既有的上線標記註解是給 `git log -S` 找上線提交用的,不是能力探測。
- 同一份計劃第 6 點由掛鉤探測 lumos 時,用的是 `--help` 輸出有沒有 `--keep-going`。
判定理由:
- 掛鉤與 lumos 的版本探測,一邊讀工具的 `--help`,另一邊讀掛鉤檔內的註解,方向不同所以手法不同,可以接受。
- 新標記的名稱和用途跟既有上線標記不同,命名上不會被 `git log -S` 那支誤抓。
- 建議在 `Systems/bound-tests-gate` 寫明兩種標記的分工,以免日後有人把 `lumos-hook-cap` 當成上線標記改動。

不對齊共 5 條,major 0 條。
