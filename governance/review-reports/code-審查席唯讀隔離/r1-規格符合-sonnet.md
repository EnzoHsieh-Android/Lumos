severity: minor

審查結果:13 條條款與〈做法〉各點都已實作,沒有未實作的條款。有三處縮水、三處多做,都是 minor。其中三處(F1、F4、F5)是作者已自承的偏離。外掛行為(S1–S8)我只讀了 register.ts 與測試標題,沒有執行測試。

### F1 不跑 marketplace update(作者已自承,spec 允許拿掉)
severity: minor
blocking: 否 — spec 明寫「實測證明不需要就拿掉這步」,Verification 筆記記了實測,條款字面少一句但有出口
引句:「已登記市集的既有使用者先跑一次 `claude plugin marketplace update lumos-toolchain`,非零只印警告、不中止」
- diff 的 `scripts/lumos` `_sync_claude_plugin` 與 `_lumos_plugin_ensure_market` 沒有 update 呼叫。
- 條款 [S9] 仍寫「`marketplace update` 非零只警告」,而 `t_install_registers_guard_plugin` 沒有對應斷言。建議編排者把 [S9] 那一句刪掉,或註明已拿掉。

### F2 ⚠ 測試名沒有跟著改
severity: minor
blocking: 否 — 只是命名,行為與覆蓋都在
引句:「`_ledger_*` 改 `_lumos_plugin_*`,對應測試名跟著改」
- 函式、常數、訊息都已改名:`_lumos_plugin_market`、`_lumos_plugin_wait`、`_lumos_plugin_user`、`_LUMOS_PLUGINS`。
- `t_ledger_plugin_bad_json_and_races`、`t_ledger_plugin_messages_and_bootstrap`、`t_ledger_plugin_teardown_scope_and_messages`、`t_install_registers_ledger_plugin`、`t_teardown_removes_ledger_plugin` 都保留原名。
- 我讀不準「對應測試名」是指這幾支,還是只指以函式名命名的測試,交編排者判。
- `lumos事件帳.md` 的 TEST 行也還列舊名。

### F3 ⚠ Read 的 `..` 路徑沒擋
severity: minor
blocking: 否 — 我不確定 spec 要擋,且 Read 條款的字面案例(暫存處內的檔、經連結、大小寫)都有擋
引句:「`Read` 的 `file_path` 照第 2 點取真實路徑,落在席報告暫存處裡 → 擋」
- `checkTool` 的 Read 分支在 `realOf` 回 null 時(路徑含 `.`、`..`、空段,或不是絕對路徑)不擋,直接放行。
- 照 spec 第 2 點,這類路徑的處理是「擋」。若編排者認定第 3 點要沿用第 2 點的「`..` 段 → 擋」,這條要升為 major。
- 例如 `/tmp/x/../lumos-seat-staging/a` 在 Read 會被放行。

### F4 路徑一律折成小寫(作者已自承)
severity: minor
blocking: 否 — 只讓暫存處擋得更多,工作資料夾多放行的僅是暫存根底下大小寫不同的同名資料夾,作者已寫進 Systems/lumos-guard 的 WHY 行
引句:「const fold = (p: string) => p.normalize('NFC').toLowerCase()」
- diff 的 `register.ts` `fold` 在所有平台折小寫。
- spec 〈做法〉二·2 寫的是「在 macOS 折疊大小寫、統一成 NFC 後比對」。

### F5 事件登記時,繼承子代理的 cwd 預設不同
severity: minor
blocking: 否 — 只影響 Grep、Glob 相對路徑的補全,而且是只有子代理給了 cwd 以外才會出現的差異
引句:「if (parent) seat = { ...parent, cwd: typeof e?.cwd === 'string' ? e.cwd : parent.cwd }」
- 這是 `spawn` 裡繼承發起方標記時的 cwd 預設。
- spec 寫的是「輸入的 `cwd`,沒給就是會談 cwd」,diff 沒給時用發起方的 cwd。

### F6 安裝流程多出「來源市集檔沒列就略過那支」
severity: minor
blocking: 否 — 屬安裝流程的防呆,不改外掛行為,有測試(「S9 來源沒列的那支略過、不硬裝」)
引句:「`_lumos_plugin_listed(src)`:來源 repo 市集檔列了哪些外掛」
- 這是 `_sync_claude_plugin` 在迴圈前新增的行為。市集檔沒列的那支回 `no-source` 並略過安裝。
- spec 〈三〉只定義了「逐支沒裝就裝」與四個狀態,沒有這個分支。

### 逐條裁定
- [S1] 已實作。`checkTool` 的 Write、Edit、NotebookEdit 分支用 `realOf` 與 `workDir`,`notebook_path` 欄位分開讀。懸空連結、`..`、相對路徑與連結都擋。含 F4 的折小寫差異。
- [S2] 已實作,但有 F3 的 `..` 缺口。Grep、Glob 走 `searchBase` 加 `aboveStaging`/`inStaging` 的祖孫判斷;Grep 只看 `path`;相對 path 含 `..` 擋;卷證資料夾不擋。
- [S3] 已實作。`bashBlock` 以 `[^A-Za-z0-9_.-]+` 切詞,擋 `gh`、`hub`、`glab`、`claude`,`git` 配 push/send-pack/send-email,兩個 GitHub API 字串、`lumos-seat-staging`、超過 1MB;`call()` 的 catch 讓 Bash 出錯時擋。
- [S4] 已實作。`TOOLS_OK` 白名單,Agent/Task 擋 `isolation`(任何非空值)與不在 `AGENT_TYPES_OK` 的 `subagent_type`。
- [S5] 已實作。`parseMarker` 只看第一個非空行,`trim` 涵蓋 BOM 與全形空白;`SEAT_LOOSE_RE` 抓到寫壞的標記就回 `bad` 並擋派工;三段、`.`、`..` 的檢查齊全。
- [S6] 已實作。`spawn` 在 `parentAgentId` 命中時直接繼承,不看派工詞標記;不過見 F5。
- [S7] 已實作。`pending` 以會談為鍵,等整批最多 `WAIT_MS` 5000;逾時 toast 開頭是 `lumos-guard 逾時放行:`;`finally` 呼叫 `release`;`session.end` 清對應表與啟動中清單。
- [S8] 已實作。`call()` 內部出錯時非 Bash 放行、Bash 擋;`onCallFailed` 處理掛鉤層出錯,工具已跑過就交回原結果。
- [S9] 大致實作。`_LUMOS_PLUGINS` 兩支、逐支安裝並以列表確認、取最差回傳、移除時任一支失敗就保留市集、手動指令只列失敗的那幾支加市集。缺 update 的警告句,見 F1。
- [S10] 已實作。`t_guard_plugin_files_valid` 檢查市集恰好列兩支、hooks.json、禁用模式(含 `$.process`)與只掛三個事件。原本 `t_ledger_plugin_files_valid` 的「市集只列一個」改成「lumos-ledger 恰好一次」,「恰好是清單那幾支」的檢查放到新測試裡,位置略移但覆蓋在。
- [S11] 已實作。`templates.md` 新增 §0,§1、§3、§7.6、§7.8 四段派工詞第一行是 `LUMOS-SEAT:`,後接席位工作資料夾說明。
- [S12] 已實作。`spawnFields` 取 `parentAgentId`,測試標題帶 S12。「獨立成一個 fix 提交」我從 patch 看不出,交編排者查提交歷史。
- [S13] 已實作。Verification 筆記記了真機驗收,三件都被擋,repo 內容沒變(以筆記為準,我沒重跑)。
- 〈做法〉一(認席)、二(規則 1–6)、三(安裝流程):已實作,見上列各條。
- 〈範圍〉做 5:已實作。design-loop 與 code-loop 的 SKILL 收貨句指到暫存處;使用者記憶 `seat-reports-outside-repo-while-running.md` 已指向 `lumos-seat-staging`,檔在 repo 外,所以不在 diff 裡。`lumos-code-loop/SKILL.md` 第 33 行仍寫 `git -C <臨時目錄>`,spec 只要求範本改,不算偏離。
- 落點:已實作。新增 `Systems/lumos-guard`,並在 `lumos事件帳` 與 `lumos-cli-lifecycle` 各補一句。

總結:最嚴重 minor,blocking 0 條;縮水+未實作共 3 條(F1、F2、F3)
