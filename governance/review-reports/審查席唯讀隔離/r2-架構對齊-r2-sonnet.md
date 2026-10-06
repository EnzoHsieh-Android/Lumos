severity: minor

白話:這版把上一輪的五點大半改回既有做法了,沒有新的 major。剩下三條是「方向對、細節還沒對齊」的 minor,都不擋。

上一輪五點驗收:
- pickMain 逐字比對:已整段拿掉(審計修正紀錄寫「不再需要 repo 範圍判定,pickMain 與漂移守衛整段拿掉」)。已改。
- 標記解析另寫一份:改成跟 dispatch-lens-hook 同形的整行規則 `^LUMOS-SEAT:\s*(\S+)$`。file: `scripts/hooks/claude/dispatch-lens-hook.py:25` 的 `MARKER_RE = ^LUMOS-IMPACT:\s*(\S+)\s*$`。差別是 hook 逐行找、本案只認第一行,理由有寫(內文貼的範例不誤認),屬刻意差異。已改。
- 擋下理由三段式:對得上。file: `scripts/lumos:7930`、`scripts/lumos:10497`、`scripts/hooks/pre-push:167` 都是「擋下:」或「為什麼在意:」加獨立指令行。已改。
- 測試綁法:`[manual:claude plugin test … 的 S1 測試全綠]` 加 TS 測試標題以條款編號開頭,跟事件帳一致。file: `mods/claude/lumos-ledger/hooks/ledger.test.ts:98` 的標題以 `S13 …` 開頭,事件帳計劃 S13 也是 manual 綁此檔。已改,新增的 TS 測試綁法沒有第二種做法。
- 安裝多外掛:細節大幅補寫,但仍有 F3。

### F1 席報告暫存處是另一個位置,既有「報告存 repo 外」慣例沒被取代
severity: minor
blocking: 否 — 結構對,只是同一件事將有兩個存放位置的說法,不影響守衛行為
引句:「編排者收到席報告時先存這裡,全部交回才搬進卷證資料夾(把使用者記憶「報告存 repo 外」那條做法定成固定位置,讓外掛找得到要保護的地方)」
佐證:既有慣例寫的是 `$CLAUDE_JOB_DIR/tmp`,不是 `<暫存區>/lumos-seat-staging/<迴圈編號>/`。file: `/Users/enzo/.claude/projects/-Users-enzo-harness-lumos-toolchain/memory/seat-reports-outside-repo-while-running.md:9`。repo 內現有的收貨句只說「先存檔放著」、沒有位置。file: `skills/lumos-design-loop/SKILL.md:27`、`skills/lumos-code-loop/SKILL.md:35`。本案範圍第 5 點已要改這兩份手冊和 reference 的句子,位置本身算升格成規則,方向對。缺的是兩件事:①沒寫舊記憶那條要改成指向新位置、或標作廢(否則記憶與圖譜各說一個位置);②`$CLAUDE_JOB_DIR` 若不在暫存區底下,新舊位置會落在不同處。⚠ `$CLAUDE_JOB_DIR` 實際落點我沒驗。

### F2 Bash 斷詞要用 TS 自寫第二份,既有跨語言重複規則的對齊做法沒被沿用
severity: minor
blocking: 否 — 外掛是 TS、repo 內唯一的斷詞在 Python,無法直呼;但沒說明自寫的理由,也沒對齊守衛
引句:「把整串指令做 shell 斷詞(引號、跳脫照 shell 規則),`sh -c`、`bash -c`、`zsh -c` 的字串參數遞迴斷詞」
佐證:repo 內 shell 斷詞的既有做法是 Python 的 `shlex.split`,切鏈用 regex 且註明「Quote-aware 不嚴格」。file: `scripts/hooks/claude/check-graph-sync.py:434-444`。TS 與 Python 各寫一份規則時,既有做法是用共用案例檔對齊。file: `scripts/test_lumos.py:70211`(`rules-fixture.ts` 對齊 TS 與 Python 兩份規則),事件帳外掛已有這個檔。本案 S3 只寫「S3 測試全綠」,沒有案例檔,也沒寫「為什麼不能沿用 `shlex`、新寫的斷詞跟它差在哪」。建議在計劃寫一句:語言邊界所以自寫,並指出差別(本案要遞迴 `-c`、命令位置判斷,舊的只切 `&& || ; |`)。⚠ `shlex` 與 TS 斷詞的語意差(例如 `$(`、反引號、換行)是否要用案例檔釘,判不準。

### F3 安裝流程:新增「marketplace update」步驟不在既有同步模式裡,且部分既有名詞與條款沒說怎麼改
severity: minor
blocking: 否 — 結構是對的(清單、逐支、回傳取最差),只是引入一個既有流程沒有、也沒驗證的步驟
引句:「已登記市集的既有使用者先跑一次 `claude plugin marketplace update lumos-toolchain` 再裝(資料夾型市集是否需要這步沒驗證,跑了無害)」
佐證:既有流程對市集只有「不存在就加、本機路徑不同就先移除再加、已裝外掛就不再裝」,另一支同時跑時以最終狀態為準。file: `scripts/lumos:21999-22014`(`_ledger_ensure_market`、`_ledger_ensure_plugin`、`_ledger_wait`)。事件帳計劃 S6 條款寫死了這個行為,條款文字是「使用者範圍已裝外掛就不再安裝」。file: `docs/lumos-toolchain-knowledge/Projects/Lumos事件帳_計劃.md:127`。本案 S9 新綁 `t_install_registers_guard_plugin` 而不是改既有 `t_install_registers_ledger_plugin` / `t_teardown_removes_ledger_plugin`,沒說兩組測試誰涵蓋哪個行為,也沒說 `_ledger_*` 的十幾個名稱與 `_ledger_fail_hint` 提示文字(「事件帳暫時停寫」)怎麼通用化。這幾點寫齊才算沿用既有做法。「沒驗證、跑了無害」這種話,也缺回頭條件。

沒有問題、不列為 F 的項目:
- 分層與依賴方向:外掛只走 `tool.call` 攔截點、核心可注入、寫檔路徑不碰 repo,跟事件帳外掛同層同形。事件帳目前只觀察 `deny`。file: `mods/claude/lumos-ledger/hooks/register.ts:71-72`、`:324`,並沒有自己擋人,所以 guard 是第一支會 deny 的外掛,S10 已改成只禁改寫輸入而不是禁 deny,與事件帳 S9 的禁令分開,對。
- 落點:新開 `Systems/lumos-guard`,市集檔與安裝流程家仍指到既有兩篇,符合「每支檔有家」。
- 錯誤處理:fail-open、`finally` 清單,跟事件帳「外掛出錯不影響會談」同方向。

不對齊共 3 條,其中 major 0 條
總結:最嚴重 minor,blocking 0 條
