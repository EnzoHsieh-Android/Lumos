---
type: system
status: doing
created: 2026-10-06
updated: 2026-10-06
responsibility: 審查席隔離外掛:認出派工詞第一行帶 LUMOS-SEAT 的子代理(與它再派的),對它的工具呼叫套白名單、寫檔只准席位工作資料夾、擋讀席報告暫存處、Bash 粗擋對外動作。不負責:偵測 repo 被改(這版不做)、安裝與移除(lumos-cli-lifecycle)、市集檔(lumos事件帳)、事件紀錄(lumos事件帳)
aliases: []
about_code:
  - mods/claude/lumos-guard/hooks/register.ts
  - mods/claude/lumos-guard/hooks/guard.test.ts
  - mods/claude/lumos-guard/hooks/hooks.json
  - mods/claude/lumos-guard/.claude-plugin/plugin.json
  - mods/claude/lumos-guard/tsconfig.json
  - mods/claude/lumos-guard/types/index.d.ts
  - mods/claude/lumos-guard/hooks/seat-fixture.ts
tags:
  - type/system
  - status/doing
  - scope/agent-dag
summary: |-
  WHY:審查席改用白名單,不用黑名單 [出處:Projects/審查席唯讀隔離_計劃 決策 d4(現行;白名單始於 d2,d2、d3 已被取代)] [因:設計審 r1 四席實測黑名單有多條繞法(大小寫不分的路徑、--git-dir、Monitor 與 Workflow 與 SendMessage)] [不選:先查作業系統沙盒能不能限單一子代理]
  WHY:Bash 只粗擋對外動作字樣,不逐詞解析指令 [出處:Projects/審查席唯讀隔離_計劃 決策 d4(現行;粗擋始於 d3)] [因:設計審 r1、r2 連兩輪在逐詞解析這一類抓到漏擋與誤擋(heredoc、bash -lc、包裝詞、git -C 暫存區照樣能 push)] [代價:指令裡只是提到 push、gh、claude 也會被擋]
  WHY:外掛不跑任何外部指令,不做事後查 repo [出處:Projects/審查席唯讀隔離_計劃 決策 d4] [因:設計審 r3 證實外掛跑 git status 會照 repo 設定執行過濾指令、會改寫索引(編排者臨時目錄重現,卷證 r3-intake)] [代價:審查席用 Bash 改 repo 不擋也不報]
  WHY:路徑一律折成小寫再比,不只 macOS [出處:2026-10-06 實作;代碼審 r1 後已寫回計劃〈做法〉二·2] [因:引擎的 realPath 保留大小寫別名的原拼法;Linux 上多折只會讓暫存處擋得更多、工作資料夾多放行暫存根底下大小寫不同的同名資料夾,不會放出暫存根]
  WHY:席報告收齊前不寫到硬碟,外掛擋讀暫存處只當多一層保護 [出處:Projects/審查席唯讀隔離_計劃 決策 d5] [因:代碼審 r1 通才、邊界兩席實測 Bash 的 grep -r /tmp、cat 加萬用字元都讀得到暫存處] [不選:加強 Bash 粗擋去擋暫存處前綴與暫存根搜尋]
  WHY:讀、寫、搜尋遇到看不懂的路徑一律擋 [出處:代碼審 r1 四席獨立抓到讀檔放行] [因:讀檔原本把看不懂當成不在暫存處,/tmp/./lumos-seat-staging/… 就讀得到]
  WHY:對照表存 $.state [出處:代碼審 r1 併發資源席] [因:模組變數在熱重載時歸零,執行中的審查席會悄悄脫離白名單;$.state 由引擎替會談保管、跨熱重載]
  RULE:外掛原始碼不呼叫 $.process、不改寫輸入或結果、只掛 agent.spawn、tool.call、session.end [依據:審計] [since:2026-10-06] [retire:人裁] [until:2027-04-06] [confirmed:2026-10-06] [test:t_guard_plugin_files_valid]
  PITFALL:掛鉤自己丟錯時引擎直接跳過它,等於放行 [出處:plugin-authoring reference.md 與 claude plugin validate 的 gating hook 警告] [根因:沒掛 .catch 的擋人掛鉤出錯就被略過] [修法:兩個掛鉤都掛 .catch,工具已經跑過就交回原本結果;沒跑過時,子代理(判不出是不是審查席也算)的 Bash 擋、其他放行,主會談一律放行;要 Claude Code 2.1.290 起,之前 .catch 可能被一起卸掉] [test:t_guard_plugin_files_valid]
  PITFALL:原始碼裡的 \uFEFF、\u3000 跳脫被寫成看不見的字元本身,改壞驗證的字串對不上 [出處:2026-10-06 實作] [根因:寫檔工具把跳脫序列轉成實際字元] [修法:改用 trim(),JS 的空白本來就含這兩個字元] [repro:grep -nP "[\x{3000}\x{FEFF}]" mods/claude/lumos-guard/hooks/register.ts 應 0 行]
  TEST:claude plugin test mods/claude/lumos-guard(條款 S1–S8,94 支,含掛鉤接線那組;第一版改壞 25 處、代碼審 r1 修補後再改壞 11 處,全翻紅;r2 到 r5 的修正各自逐條撤回驗過會翻紅);t_install_registers_guard_plugin、t_guard_plugin_files_valid、t_seat_templates_carry_marker
  SEE:[[Projects/審查席唯讀隔離_計劃]] [[Systems/lumos事件帳]] [[Systems/lumos-cli-lifecycle]]
verified_by:
  - "[[Verification/2026-10-06_審查席隔離實作]]"
  - "[[Verification/2026-10-07_Claude-Code-2.1.292-mod異動]]"
---
# lumos-guard

白話:設計審、代碼審派出去的審查員是子代理,權限跟編排者一樣大。這支 Claude Code 外掛認出派工詞第一行帶 `LUMOS-SEAT:` 的子代理(和它再派出去的),把它的工具收窄:只准讀取、搜尋、Bash、網路查詢、派一般子代理;寫檔只准它自己的工作資料夾 `<暫存根>/lumos-seat-work/<迴圈>/<席名>/`(暫存根是 /tmp、/var/tmp、$TMPDIR 這幾個,實驗一般放 /tmp 底下);不准碰席報告暫存處 `<暫存根>/lumos-seat-staging/`;Bash 指令提到 `gh`、`git push`、`claude`、GitHub API 這類對外動作就擋。

防的是「被審的文件裡藏了指令,把審查員誘導去改 repo、開 PR、偷看別席報告」,不防一個有心繞的審查員:Bash 仍是完整的 shell,在 repo 裡改檔這版擋不到也不報。設計與三輪設計審的取捨見 [[Projects/審查席唯讀隔離_計劃]]。

外掛裝在 [[Systems/lumos事件帳]] 同一份市集檔裡,由 [[Systems/lumos-cli-lifecycle]] 的安裝與移除流程一起裝上、拿掉。

- 型別檔 `types/index.d.ts` 只為一件事:用 `declare module 'claude-code'` 擴充 `PluginState`,宣告 `$.state` 裡 `lumos-guard/seats` 這個鍵的形狀;型別檔要求 `$.state` 的鍵在 `PluginState` 裡宣告(沒宣告時型別對不上)。其他兩支外掛不用 `$.state`,所以沒有這個檔(代碼審 r3 架構對齊席問到)。
REVISIT:2026-11-06 實測一次 $.state 寫一個沒在 PluginState 宣告的鍵,引擎會不會擋;會擋就在這段寫明,不會就拿掉這句宣告的理由
- 三處跟另兩支外掛寫法不同,都是刻意的(代碼審 r4 架構對齊席):①工具呼叫的接線抽成 `onTool` 並匯出——事件帳外掛的接線只用 Python 釘字串,守不住「接線改成一律放行」,這邊要讓 TS 測試直接打得到;②存回 `$.state` 帶版本、撞版重試加時間上限——另兩支外掛不跨實例共用 `$.state`,沒有這個問題;③派工範本的檢查(`t_seat_templates_carry_marker`)從原始碼抽 `SEAT_RE` 編譯來比——範本那邊不再另抄一份格式。事件帳外掛的 `seat` 欄是另一回事:兩支外掛各寫一份判法,拿同一批案例對(見下一點)。
- `hooks/seat-fixture.ts` 是審查席標記的共用案例:事件帳外掛記 `spawn` 的 `seat` 欄也用同一套判法,兩支外掛各放一份一模一樣的,各自的測試跑同一批([[Systems/lumos事件帳]])。
