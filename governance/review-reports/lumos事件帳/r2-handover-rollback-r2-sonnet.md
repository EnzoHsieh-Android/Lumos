severity: major

### F1 移除段掛在 `_teardown_global_claude`,但 teardown 與 uninstall 都不經過它
severity: major
blocking: 是 — 照做後 `lumos uninstall` 與 `lumos teardown` 都移除不了外掛,回退第 1 步失效,S7 測試還會假綠。
spec 段落:範圍 5、做法 4 的位置與移除流程、S7、回退第 1 步。
問題:`_teardown_global_claude` 在現行碼只是給測試用的相容包裝,轉呼叫 `_teardown_global_hooks`。`cmd_teardown` 直接呼叫 `_teardown_global_hooks(…, "claude")`,沒走包裝。`cmd_uninstall` 完全不碰全域 hook。spec 說「uninstall、teardown 都會經過它」,兩條指令實際都不會到 `_teardown_claude_plugin()`。只有 `t_teardown_global_claude` 直接呼叫包裝,所以照 spec 寫的 `t_teardown_removes_ledger_plugin` 會綠,但真指令什麼都沒移。
具體情境一:實作者照 spec 把移除段接在包裝裡,S7 綠。使用者跑 `lumos uninstall`,外掛與市集原封不動。回退第 1 步發布後,每台機器照指示跑 `lumos uninstall` 都以為清掉了。第 2 步刪 `mods/` 後只剩失效市集登記,而 lumos 已沒有任何移除程式。
具體情境二:`_teardown_global_hooks` 在 settings.json 解析失敗時先 `return False`。就算接在這支裡,設定檔壞的機器也跳過外掛移除,spec 沒交代。
具體情境三:spec 說「探針模式下照舊被擋」。但 `cmd_teardown` 與 `_teardown_global_hooks` 都沒有 `_refuse_if_probe`(只有 install、uninstall、update、bootstrap、`_sync_global_hooks` 有),探針沙盒裡跑 teardown 會真的呼叫 `claude plugin uninstall`。
引句:「移除在 `_teardown_global_claude` 裡做」
引句:「都在既有探針拒絕之後,探針模式下照舊被擋」
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:17100-17101` `cmd_teardown` 直接呼叫 `_teardown_global_hooks`。
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:18776-18778` `_teardown_global_claude` 只是包裝,scripts/lumos 內沒有任何呼叫者。
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:16969-17015` `cmd_uninstall` 只清 symlink 與 skills。
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/test_lumos.py:9275-9298` 現有測試直接呼叫包裝。
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:18781-18795` 設定檔壞則提前 return False。
修法方向:移除段接在 `cmd_uninstall` 與 `cmd_teardown` 兩處(或 `_teardown_global_hooks` claude 分支,且放在 return False 之前),S7 改成驅動真指令,並補探針擋。

### F2 回退第 1 步叫人跑 `lumos uninstall`,副作用是拆掉整台機器的 lumos;第 2 步清單漏項與 S12 孤兒
severity: minor
blocking: 否 — 都是第一次跑紅燈或讀 `--help` 就能發現的清單問題,手動兩個指令的替代路徑存在。
spec 段落:回退。
問題:`cmd_uninstall` 會刪 `~/.local/bin/lumos` 與 user-scope skills。為了移除一個外掛,要每台機器先拆掉全域 lumos 再重裝,spec 沒說這個代價。另外第 2 步寫「刪 S4–S11 的測試」,但 S12 的 `t_events_reader_from_worktree` 是 r1 折入時新增的,會留下孤兒測試,指令刪掉後它會紅,pre-push 擋住。S13 的 `ledger.test.ts` 在被刪的資料夾裡,算是有處理。第 2 步也沒列 `_events_root`、`HELP_WHEN` 與指令說明字典、argparse 與分派、`commands/INDEX.md` 及子檔、三篇 Systems 家的回寫,這些是「範圍」登記過的東西。
具體情境:照清單回退後 `t_events_reader_from_worktree` 找不到 `events` 指令而紅;argparse 殘留 `events` 子指令指向已刪函式。
引句:「刪 S4–S11 的測試」
引句:「請每台機器跑一次 `lumos uninstall`」
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:16969-17015` `cmd_uninstall` 的移除範圍是全域指令與 skills。

### F3 「以 cwd 為鍵快取」與「非 repo 就整場丟棄」互相矛盾,r1 邊界 F4 情境二只修一半
severity: minor
blocking: 否 — 損失只限先在非 repo 目錄啟動、之後才進 repo 的會談,事件帳本來就只承諾「有記到的是真的」。
spec 段落:做法 2 寫入的寫的位置。
問題:同一段先說結果以 cwd 為鍵快取、每次寫塊前重新解位置,後面又說確定不在 git repo 時「丟掉這個會談的緩衝、之後不再收」。型別檔有 `CwdChanged`,會談中途換目錄是常態。前者讓換目錄後能恢復,後者讓會談永久停寫,兩句不能同時成立。
具體情境:在家目錄啟動 `claude`,第一個回合寫塊時 git 報 `not a git repository`,會談被標成永不收。之後 cd 進本 repo 做完整件事,事件帳一筆都沒有,`lumos events` 查不到,也沒有 `ledger_error` 提示。
引句:「錯誤輸出含 `not a git repository` → 確定不在 repo 裡」
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:3523-3527` `CwdChanged` 事件。

### F4 `_lumos_src()` 在 bootstrap 子行程與 `--source` 下不等於實際來源,適用範圍的宣稱不成立
severity: minor
blocking: 否 — 預設路徑 `~/harness/lumos-toolchain` 下不受影響,其他佈局只是靜默略過一行或登記到另一份 clone。
spec 段落:做法 4 的適用範圍與來源、決策 d3。
問題:`cmd_bootstrap` 以子行程跑 `install --force`,但它把 `LUMOS_HOME` 寫進環境是在子行程之後(`os.environ["LUMOS_HOME"] = …` 在第 3 步)。用 `--lumos-home <自訂路徑>` 時,子行程的 `_lumos_src()` 回預設路徑。預設路徑不存在就印略過,存在就把另一份舊 clone 登記成市集。`cmd_update` 與 `cmd_teardown` 都有 `--source`,spec 的 `_sync_claude_plugin()` 與 `_teardown_claude_plugin()` 沒有參數,等於忽略它。`cmd_install` 自己用 `__file__` 當來源裝 hook 與 skills,外掛卻用另一個來源,兩者可以分岔。
具體情境:使用者 `bootstrap --lumos-home ~/tools/lumos`,hook 與 skills 來自 `~/tools/lumos`,外掛被略過,沒有任何事件帳,enforcement 顯示 `unknown`,看起來像「沒裝好」。
引句:「所以只要這台機器有 lumos 來源 repo,任何專案跑 `lumos install` 或 `lumos update` 都會確保外掛裝好」
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:18968` 子行程呼叫 `install --force` 時沒有帶 `LUMOS_HOME`。
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:18982` `LUMOS_HOME` 在安裝步驟之後才設。
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:17630-17634` `_lumos_src(source=None)` 吃 `--source`,spec 的新函式沒有參數。

### F5 enforcement 那一列的家 `Systems/hook信任邊界` 查無對應內容,r1 架構 F1 只是把錯家換了一個
severity: minor
blocking: 否 — 屬落點的找不到問題,不影響功能,但下一個人會查無而重蹈 r1 F10 第 2 點。
spec 段落:範圍的落點。
問題:spec 說既有 hook 事件帳「活著沒」的判法住在 `Systems/hook信任邊界`。實查該節點全文沒有 `hook-events`、「活著沒」或 enforcement 判法,只有一條連到 `Projects/enforcement可觀測性_計劃` 的連結。`lumos search` 的命中也在兩篇 Projects 計劃,`enforcement_status` 沒有任何 Systems 家。about_code 雖列了 `scripts/lumos`,但寫進去的內容會和該節點的「注入框」主題無關。
具體情境:實作者依落點把 `claude-event-ledger` 狀態語意與 `stale` 分母規則寫進 `hook信任邊界`,三個月後要改 enforcement 的人去 enforcement 相關計劃查,看不到。
引句:「enforcement 那一列進 `Systems/hook信任邊界`」
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/docs/lumos-toolchain-knowledge/Systems/hook信任邊界.md:28` 全文只有一條連到 enforcement 計劃的連結。
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/docs/lumos-toolchain-knowledge/Systems/記憶過期清掃.md:175` enforcement 列舉清單只被這篇旁帶提到。

### F6 讀取端回合框法依賴三個沒查證的時序假設
severity: minor
blocking: 否 — 只影響 `lumos events` 的回合歸屬與 `turn_start.origin` 欄位,消費端另案。
spec 段落:做法 1 回合歸屬、做法 3 讀取。
問題:①子代理的工具事件從派出它的那筆 `spawn` 之後起算,但 `spawn` 是等 `next(e)` 回來才記,子代理第一個工具事件可能比 `spawn` 先到。②塊檔同一毫秒的兩塊,spec 說靠 `ts` 判讀,但讀取端只說依檔名排序合併,沒說要依 `ts` 重排,隨機尾碼可能把較晚的塊排在前面。③`turn_start.origin` 取最近一筆 `door` 為 `prompt` 的列,沒驗證 `session.append` 的 prompt 列比 `turn.start` 早到,晚到就取到上一回合的 origin。⚠ 三點都沒實機驗證。
具體情境:兩個並行子代理在同一毫秒各寫一塊,塊檔名隨機尾碼排序顛倒,合併後一個子代理的 `turn_end` 排在它自己的 `tool` 之前,框法把那些工具事件歸到錯的回合。
引句:「同一毫秒的兩塊靠事件自己的 `ts` 已足夠判讀,不另保證先後」
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:12627-12660` 子代理的 turn 沒有 `turn.start`,每次迴圈執行算一個 turn,`tool.call` 不帶 turnId。

### F7 外掛安裝流程的分支判準與清理的不對稱留有缺口
severity: minor
blocking: 否 — spec 在誠實界線已自承 `marketplace list --json` 欄位沒實測,屬實作第一步要量的項目。
spec 段落:做法 4 安裝流程與移除流程。
問題:①「來源不同」要比較路徑,但 JSON 欄位沒實測,也沒定路徑正規化(結尾斜線、符號連結、`~`),一樣的來源可能被判成不同而每次先移除再加,連帶使用者原本裝好的外掛被一併移除再重裝。②同名 `lumos-toolchain` 若是使用者自己用 GitHub 來源加的,會被靜默換成本機路徑,沒有訊息說明。③移除流程只在外掛有列出時才動市集;外掛被人手動移除而市集留著,`lumos uninstall` 不會清它。
具體情境:使用者先手動 `plugin uninstall`,再跑 `lumos uninstall`,市集登記殘留,下次 `lumos install` 又發現「有但來源不同」而走移除再加。
引句:「有但來源不同 → 先 `claude plugin marketplace remove lumos-toolchain --scope user` 再加」
file: `claude plugin marketplace remove --help` 與 `claude plugin list --help` 皆有 `--json`,但輸出欄位沒有量過。

## 前輪修復驗收(r1 本鏡頭)
- r1 F1 子代理沒有 turn_start:已修好(事件表改成只有主會談記 `turn_start`,讀取端用前後框,對得上型別檔 12627-12660)。
- r1 F2 origin 型別與取法:已修好(取 `origin.kind`、用 `door` 為 `prompt` 且 `agentId` 為空篩);順序假設仍未驗,見本輪 F6。
- r1 F3 序號在記憶體會覆蓋:已修好(時間加隨機字串唯一檔名、狀態以會談編號為鍵、先同步取走緩衝與串行佇列)。
- r1 F4 相對路徑與頂層快取:修一半(絕對路徑、主 checkout、cwd 為鍵已修好;「非 repo 整場丟棄」與 cwd 快取互相矛盾,見本輪 F3)。
- r1 F5 session.end 順序:已修好(先寫塊再 `next(e)`,用事件自己的 `sessionId`)。
- r1 F6 enforcement 列數與外部呼叫:已修好(單列、只看檔案系統、23 改 24、S10 測試執行器隔離;現行測試仍釘 23 列於 `test_lumos.py:31327`,與 spec 一致)。
- r1 F7 市集來源撞名與懸空:已修好(d3 改 `_lumos_src()`、同名不同來源先移除再加);bootstrap 與 `--source` 的分岔與判準細節見本輪 F4、F7。
- r1 F8 回退與 uninstall:修出新問題(前置判斷、`--scope user`、確認清單、兩步順序都補了,但移除段掛錯函式、實際不可達,見本輪 F1)。
- r1 F9 新版 mod 判定:已修好(資料夾型市集直接讀來源資料夾,不再要求 `plugin update`,與 reference.md 第 72 行一致)。
- r1 F10 落點與登記漏項:修一半(登記處、slim 界線、三份名單都補了;enforcement 的家改指 `Systems/hook信任邊界` 但該節點查無對應內容,見本輪 F5)。

機械 refcheck 備註:`governance/runtime/` 與 `docs/knowledge/` 屬預期不存在。`git rev-parse --path-format=absolute --show-toplevel --git-common-dir` 在本 worktree 實測輸出兩行,順序與 spec 相符。

總結:最嚴重 major;blocking 共 1 條(F1)。
