severity: major

## 1. 分層與依賴方向
不完全對齊。
- 鄰居的方向是「外掛寫事件帳、lumos 只讀」:file: `scripts/lumos:23636`(註解「寫入端是 Claude Code 的 mod……這裡只讀」)。第 5 項把方向反過來(Python hook 寫、TS 外掛讀,中間靠檔案),是新的跨層資料通道,見 F1。
- 第 4 項改 `merge-claude-settings.py` 的 matcher,會碰到 Codex 轉換表:file: `scripts/merge-claude-settings.py:271`(只認 matcher 恰為 `Edit|Write|MultiEdit`),見 F3。
- 第 3 項 `seat-check --events` 讀事件帳走 `_events_root`:file: `scripts/lumos:23641`,方向與 `lumos events` 一致,對齊。
- 外掛安裝:現有只有單一常數 `_LEDGER_PLUGIN`,沒有「外掛清單」:file: `scripts/lumos:21921`;計劃 S9 與落點都寫成已有清單,見 F5。

## 2. 命名與錯誤處理
大致對齊。
- 第 6 項「沿用既有推送 hook 的預算與失敗即放行」,與 file: `scripts/hooks/claude/impact-hook.py:777`(非改檔工具直接放行)同向;對齊。
- 第 3 項「只提醒、不擋、恆放行」與 file: `scripts/lumos:23499`(seat-check 恆 rc0、輸入壞損 rc2)一致;事件帳找不到那一席要說清楚不擋,對齊。
- 新環境變數名 `LUMOS_SESSION_ID` 符合 `LUMOS_*` 命名(file: `scripts/hooks/claude/lumos-entry-hook.py:42` 一類),但它與 `CLAUDE_CODE_SESSION_ID` 並存,見 F4。
- 外掛測試命名 `context.test.ts`、條款綁測試標題、`claude plugin test` 沿用 file: `mods/claude/lumos-ledger/hooks/ledger.test.ts`,對齊。

## 3. 第二種做法
有四處,見 F1 至 F4。

## 4. 落點合不合理
- 新開 `Systems/lumos-context` 管新外掛:合理(事件帳節點 responsibility 寫明只負責事件帳,file: `docs/lumos-toolchain-knowledge/Systems/lumos事件帳.md:6`)。
- `Systems/design-loop.md` 約 47 KB、`lumos-cli-lifecycle.md` 約 31 KB、`記憶過期清掃.md` 約 26 KB,都已大。seat-check 的 `--events` 與第 3 項新抽取塞進 design-loop 超出它「seat-check 是協議內一致性」的射程(file: `scripts/lumos:23500` 的射程註解)。見 F6。
- `記憶過期清掃` responsibility 與本文都寫「不負責改任何檔(2026-09-14 起唯讀)」「原始碼裡沒有任何寫檔呼叫,有測試直接掃原始碼釘住」(file: `docs/lumos-toolchain-knowledge/Systems/記憶過期清掃.md:6`、`:108`);計劃落點列了該篇,但沒說要改 responsibility 與那支掃原始碼的測試,見 F2。

## 發現

### F1 hook 與外掛之間用檔案交換資料(新通道)
severity: major
blocking: 是 — 專案裡沒有「Python hook 寫檔、TS 外掛讀檔」的先例,而這正是題目點名的第二種做法;要嘛指出先例、要嘛改走既有單向(外掛寫、lumos 讀)。⚠ 鄰居也沒有反向先例可對,屬編排者裁量,不是我硬判錯。
引句:「記憶清掃 hook 每次跑完(沒事也寫)把結果(會談編號、哪幾篇記憶檔、什麼原因)寫進 lumos 自己的快取資料夾」
補充:快取資料夾位置計劃沒指定。專案已有 `~/.cache/lumos/` 先例與受信任目錄檢查(file: `scripts/lumos:17939`、`:17942`、`:36754`),計劃沒說沿用它們;hook 腳本與 `scripts/lumos` 是分開複製的檔,hook 端是否能共用那組檢查也沒交代。

### F2 翻案「唯讀」卻沒帶走守衛測試與兩處自述
severity: minor
blocking: 否 — 結構對(d3 已明寫翻案),但落地時舊測試會直接紅,計劃沒列要改的東西。
引句:「部分翻案記憶清掃 2026-09-14 的「唯讀」設計」
補充:file: `docs/lumos-toolchain-knowledge/Systems/記憶過期清掃.md:108` 寫明有測試掃原始碼確保沒有寫檔呼叫;S8 的 `t_memory_sweep_writes_machine_result` 與它必然衝突。計劃應列出要改該掃原始碼測試(改成只准寫快取路徑)與該篇 responsibility。

### F3 Bash 改檔推播:列舉寫檔形狀,與既有「列舉補不完」決策相反;matcher 改動打壞 Codex 轉換
severity: major
blocking: 是 — 同專案已有明文決策「列舉法原理上補不完,量結果不量過程才免疫」(file: `scripts/hooks/claude/check-graph-sync.py:298-302`),本計劃又列一份 `>`、`tee`、`sed -i`、`cp`/`mv`、heredoc 的形狀清單,是第二種做法;另外 matcher 字串一改,`_codex_entries` 的相等比對(file: `scripts/merge-claude-settings.py:271`)不再命中,Codex 會收到原樣的含 `Bash` matcher,與「Codex 那邊不動」自相矛盾。
引句:「指令裡有寫檔形狀(`>`、`>>`、`tee`、`sed -i`、`cp`/`mv` 的目的端、heredoc 寫檔)時,對目的路徑做同樣的推送」
補充:`impact-hook.py` 的 `EDIT_TOOLS` 閘與 `extract_paths`(file: `scripts/hooks/claude/impact-hook.py:60`、`:84`、`:777`)也要擴,計劃只提了安裝端。

### F4 第二條會談編號環境變數通道
severity: major
blocking: 否 — 計劃給了理由(接續後舊值)、實測先行的備案與 RETIRE-IF ②,屬自覺的第二種做法;但要求 lumos 內所有取編號處都走同一個讀取函式。
引句:「lumos 需要會談編號的地方(目前只有 `handoff` 排除接手者自己那一處)先讀它,沒有才退回 `CLAUDE_CODE_SESSION_ID`」
補充:現況單一讀取點在 file: `scripts/lumos:46262`;hook 端的會談編號走 payload,不走環境變數。備案「`CLAUDE_PID` 小檔」又是一條新的檔案通道,若走到備案,同 F1 的疑慮。

### F5 外掛安裝端沒有「清單」,第二支外掛會複製一份安裝碼或需先重構
severity: minor
blocking: 否 — 結構方向對,但計劃把不存在的東西當現成。
引句:「當 `lumos install` 與 `uninstall` 執行,外掛清單應含 `lumos-context`,各自裝上與移除」
補充:現況是單一常數與單一外掛專用函式組(file: `scripts/lumos:21921-21923`、`:21992`、`:22063`),測試名也是 ledger 專屬(`t_install_registers_ledger_plugin`,見 `lumos-cli-lifecycle.md:160`)。計劃沒說是把常數改成清單(並更新那三支 ledger 測試)還是複製一組;兩者都需寫明,後者即第二套。

### F6 第 3 項新寫 `file:行號` 抽取,既有 refcheck 已有同功能
severity: major
blocking: 是 — 專案已有路徑加行號抽取與核對的單一實作(file: `scripts/lumos:24524-24531` 的 `_refcheck_scan` 與 `_node_code_ref_tokens`,doc 說明 cmd_refcheck 與 loop status 共用),計劃自述「新寫一套抽取」就是第二套路徑抽取,而且 seat-check 自己的引句抽取也是「同 quote-check 單一實作」(file: `scripts/lumos:23497`),慣例是共用。
引句:「抽報告裡 ``file: `路徑:行號` ``(新寫一套抽取;既有的只抽引句)與引句所在檔」
補充:落點上,這段新邏輯加上 `--events` 灌進已 47 KB 的 `Systems/design-loop`,建議改為另開節點或寫進事件帳消費端節點(事件帳 responsibility 明說不負責消費端,file: `docs/lumos-toolchain-knowledge/Systems/lumos事件帳.md:6`)。

總結:最嚴重 major,blocking 3 條
