---
type: system
status: doing
created: 2026-10-05
updated: 2026-10-06
responsibility: 負責 Lumos 事件帳:Claude Code 的 lumos-ledger 外掛把回合、工具呼叫、子代理寫成的結構化事件帳,它的格式、寫在哪、怎麼讀(lumos events)、怎麼清(--prune)、enforcement 的 claude-event-ledger 那一列怎麼判;不負責外掛怎麼裝(lumos-cli-lifecycle)、也不負責讀它的消費端(收工檢查、接手視圖各自的節點)
aliases: []
about_code:
  - scripts/lumos
  - mods/claude/lumos-ledger/hooks/register.ts
  - mods/claude/lumos-ledger/hooks/ledger.test.ts
  - mods/claude/lumos-ledger/hooks/hooks.json
  - mods/claude/lumos-ledger/.claude-plugin/plugin.json
  - .claude-plugin/marketplace.json
  - mods/claude/lumos-ledger/hooks/rules-fixture.ts
  - mods/claude/lumos-ledger/hooks/seat-fixture.ts
tags:
  - type/system
  - status/doing
  - scope/platform
summary: |-
  WHY:[2026-10-05 Projects/Lumos事件帳_計劃]判斷「AI 這一輪做了什麼」原本只能事後解析逐字稿;逐字稿官方明說不是穩定介面(Codex 收工檢查只認兩版逐字稿,本機升到 0.160.0 後靜默失效),有些情境逐字稿根本不落地。Claude Code 的 mod 能在行程內看到結構化的回合、工具呼叫、子代理,所以改成由 lumos-ledger 外掛寫 Lumos 自己的事件帳,讀取端只讀它
  WHY:[2026-10-05 設計審 r1 架構席]事件種類欄位叫 ev 不叫 kind:同資料夾的 hook-events.jsonl 用 kind 表示結果(ok/timeout/error),同名異義會讓讀兩本帳的人猜錯。兩本帳互不取代:那本記「lumos 的 hook 自己有沒有跑」,這本記「AI 做了什麼」;在 worktree 裡,hook 事件帳寫會談所在的 worktree,事件帳寫主 checkout(worktree 會被刪)
  WHY:[2026-10-05 設計審 r2 架構席]清理(lumos events --prune)放讀取端、要人或排程跑,不像 _note_audit_work_dir 在寫入端自動清——寫入端是 mod,mod 的檔案介面沒有刪除功能
  RULE:[since:2026-10-05][retire:開場提醒改成不只點名 inactive/degraded,或 enforcement_summary 的分母規則改變][confirmed:2026-10-05]enforcement 的 claude-event-ledger 那一列只准 active/stale/unknown 三值,而且除了解主 checkout 的那一次 git rev-parse(限 3 秒,卡住就退回原根)之外不呼叫外部指令(尤其不叫 claude);事件帳上層是連結時判 unknown、連結的會談資料夾不算寫入——開場提醒只點名 inactive、degraded,用錯會讓沒裝外掛、只用 Codex 的人每次開場都被唸;叫 claude plugin list 每次約 0.9 秒(2026-10-05 設計審前掃席本機實測)並讓測試依機器而變;enforcement 每次開場都跑,git 卡住不能拖垮整份(代碼審 r2) [test:t_enforcement_ledger_row] [test:t_enforcement_ledger_row_git_hang] [test:t_enforcement_ledger_row_symlinks]
  FACT:[來源:外部][2026-10-05 Claude Code 2.1.289 隔離設定目錄實測]claude plugin marketplace list --json 每筆是 name、source(本機資料夾為 directory)、path;claude plugin list --json 每筆有 id、enabled、readFromFolder——readFromFolder 證實資料夾型市集直接讀來源資料夾本身、不讀安裝拷貝。外掛安裝與移除照這兩個格式判斷
  PITFALL:[2026-10-05 設計審 r2 正確性席與接手席獨立抓到]外掛移除若掛在 _teardown_global_claude,測試會綠但真的 lumos uninstall 與 lumos teardown 都不會移除——那支只是給測試用的相容包裝,沒有任何指令呼叫它;現在掛在 cmd_uninstall 開頭的探針拒絕之後,測試用子行程跑真指令 [test:t_teardown_removes_ledger_plugin]
  PITFALL:[2026-10-05 代碼審 r1 正確性席與邊界席獨立抓到]claude 的列表指令吐 null 或物件時,迭代它會丟 TypeError,把整個 lumos install 與 uninstall 帶倒(uninstall 停在半拆)。現在 _claude_json 只收「物件組成的清單」,其他一律當失敗 [test:t_ledger_plugin_bad_json_and_races]
  PITFALL:[2026-10-06 mod 段實作]外掛測試第一版跟程式一起寫、沒先看紅,改壞驗證時九個關鍵機制有四個拿掉照樣綠(假時鐘不動加隨機字串遞增遮住了塊名遞增、事件全在寫檔前送完測不到「寫到一半有新事件」、先寫再看緩衝看不出不累積、一行死碼);補了遞減隨機字串、可暫停的假寫檔、不寫直接看緩衝三種測法 [重現指令:claude plugin test mods/claude/lumos-ledger]
  PITFALL:[2026-10-05 實作]enforcement 加一列會同時動到兩支釘數字的既有測試(總列數 23→24、unknown 列數 11→12);設計審只列到第一支 [test:t_enforcement_never_raises_on_missing] [test:t_enforcement_summary_excludes_unknown]
  PITFALL:子代理再派子代理時,spawn 事件的 agent 欄記成空的 [出處:2026-10-06 審查席唯讀隔離設計審 r1 前掃] [根因:用了 e.agentId,引擎給發起方的欄位叫 parentAgentId] [repro:claude plugin test mods/claude/lumos-ledger 的 S12 測試;代碼審 r1 起交給 record 的整組參數由 spawnEvent 給齊,接線那行沒有欄位可選錯]
  RULE:[since:2026-10-05][retire:事件帳不再由可被強制提交進 repo 的檔案提供,或改成只出 JSON 不出文字][confirmed:2026-10-05]印到終端的事件帳內容一律過 _esc_clean 加 _PATH_SPECIAL_CATS(控制、格式含雙向覆寫與零寬、行段分隔、孤立代理),--json 一律 ASCII 跳脫,不另寫第三套消毒——塊檔可能被人強制提交,雙向覆寫能把工具名顯示成別的樣子,孤立代理字元印到 UTF-8 終端會直接丟編碼錯誤。讀進來時就把關:巢狀超過 32 層或單行超過 64KB 算壞行、塊檔超過 16MB 略過並計數——約 7 萬到 11 萬層的巢狀讀得進來、印的時候才爆(代碼審 r3),只擋解析端會漏掉這段;每個欄位各自清理截斷,狀態標記接在最後 [test:t_events_reader_hostile_lines] [test:t_events_r3_hostile_output]
  RULE:[since:2026-10-05][retire:清理改由寫入端自己做,或事件帳搬出 repo][confirmed:2026-10-05]lumos events --prune 只收 1 到 36500 的半形整數(下限 1 同時就是「最近 24 小時動過的會談不刪」的唯一保護,開放 --days 0 會刪到正在寫的會談);事件帳路徑從 repo 根往下每層都不能是連結(讀取也過這道,不然會讀到 repo 外);在 worktree 裡跑時那個 worktree 必須真的登記在主 checkout 的 .git/worktrees 裡(gitdir 是相對路徑時照 gitdir 檔所在目錄解讀,壞項目略過不連累別的)——.git 檔可以被改成指到別的 repo,不驗就會刪到別人的事件帳 [test:t_events_prune_hardening] [test:t_events_prune_edge_cases] [test:t_events_r3_path_trust]
  TEST:t_events_reader_merges_chunks、t_events_reader_no_ledger、t_events_reader_from_worktree、t_events_reader_edge_lines、t_events_reader_hostile_lines、t_events_session_name_and_repo_validation、t_events_prune_only_old_sessions、t_events_prune_edge_cases、t_events_prune_hardening、t_enforcement_ledger_row、t_enforcement_ledger_row_git_hang、t_runner_isolates_claude_plugin、t_install_registers_ledger_plugin、t_teardown_removes_ledger_plugin、t_ledger_plugin_bad_json_and_races、t_ledger_plugin_messages_and_bootstrap、t_ledger_plugin_teardown_scope_and_messages、t_ledger_plugin_files_valid、t_ledger_rules_match_reader、t_events_r3_hostile_output、t_events_r3_path_trust、t_events_r3_honest_messages、t_enforcement_ledger_row_symlinks(python3.14 scripts/test_lumos.py -k events / -k ledger / -k runner_isolates)
related:
  - "[[Projects/Lumos事件帳_計劃]]"
  - "[[Systems/lumos-cli-lifecycle]]"
  - "[[Systems/lumos-cli-read]]"
verified_by:
  - "[[Verification/2026-10-05_事件帳Python段實作]]"
  - "[[Verification/2026-10-06_事件帳mod段實作]]"
---
# lumos事件帳

> 白話:Claude Code 裝了 lumos-ledger 外掛之後,每場會談做了什麼(回合開始結束、每次工具呼叫成不成功、派了哪些子代理、實際用哪個模型)會寫成一份事件帳,放在主 checkout 的 governance/runtime/events/<會談編號>/ 底下,不進版控。`lumos events` 讀它,`lumos events --prune --days N` 清舊的,`lumos enforcement` 的 claude-event-ledger 那一列看它最近有沒有在寫。設計、條款與兩輪設計審在 [[Projects/Lumos事件帳_計劃]];前提實驗在 [[Verification/2026-10-05_Claude-mod能力實測]]。

## 現況(2026-10-06)

- 讀取端、清理、enforcement 那一列、外掛安裝與移除、測試執行器隔離(Python 段)與寫入端外掛(mod 段)都在。外掛在 `mods/claude/lumos-ledger/`,市集檔在 repo 根的 `.claude-plugin/marketplace.json`;`lumos install` 會用市集檔把外掛裝到使用者範圍。市集檔 2026-10-06 起另列 [[Systems/lumos-context]] 與審查席隔離外掛 [[Systems/lumos-guard]],市集列的外掛要恰好等於安裝端的外掛清單。
- 外掛的寫法:核心邏輯在 `register.ts` 的 `createLedger`(緩衝、塊名、串行寫入、位置判定),讀寫檔與跑 git 由外面注入,所以 `ledger.test.ts` 能用假的讀寫測並行與重新載入;引擎掛鉤只收事件交給核心。
- 會談編號、圖譜判定、主 checkout 判定這三條規則在外掛(TypeScript)與讀取端(Python)各寫一份;兩邊共用 `mods/claude/lumos-ledger/hooks/rules-fixture.ts` 的案例,外掛測試與 `t_ledger_rules_match_reader` 都跑它,一邊改了規則另一邊會紅。外掛環境只能匯入程式模組(不能匯入 JSON),所以案例檔是 `.ts`、內容寫成純 JSON,Python 端切出 `RULES = ` 後面那段用 json.loads 讀。
- 外掛緩衝只以會談為鍵,每筆帶收到時的 cwd;寫的時候照到達順序把連續寫到同一處的合成一塊,寫前逐層確認事件帳路徑沒有符號連結。
- 外掛的驗證器要求引擎介面 `$` 只能傳給檔案頂層宣告的函式;包在註冊函式裡的內部函式收 `$` 會被拒載(`claude plugin validate` 會擋)。
- 外掛裝與移除的流程與狀態用詞(ok / absent / no-source / failed)的細節在 [[Systems/lumos-cli-lifecycle]];`lumos events` 指令的用法在 [[Systems/lumos-cli-read]]。
- 2026-10-07 起多記幾個欄位([[Projects/事件帳補記搜尋與席位_計劃]]):`Grep`、`Glob` 事件的 `pattern`、`glob`(各前 200 字)與 `output_mode`;`Bash` 事件的 `cmd_len`(看得出 `cmd` 有沒有被截);`spawn` 事件的 `cwd` 與 `seat`(派工詞第一個非空行是合格審查席標記時的值,其他內容不記——「不記提示全文」唯一的例外,理由在那篇的決策)。`seat` 的判法跟 [[Systems/lumos-guard]] 同一套,兩支外掛各放一份一模一樣的 `seat-fixture.ts` 案例(這邊是 `hooks/seat-fixture.ts`),`t_ledger_seat_re_matches_guard` 釘住兩份案例與正規式一字不差。
- 外掛自己的測試要在本機跑:`claude plugin test mods/claude/lumos-ledger`(CI 沒有 Claude)。

## 誠實界線

- 只有 Claude Code 會寫;Codex 沒有同等事件。
- 寫入端出錯時引擎會跳過它,那段沒有事件:事件帳只能證明「記到的有發生」,不能證明「沒記到的沒發生」。
- 其餘界線(子模組、slim、永久性 git 失敗、指令文字可能含秘密)見計劃的〈誠實界線〉。

