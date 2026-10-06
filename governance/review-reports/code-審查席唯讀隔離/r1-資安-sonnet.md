severity: major

### F1 Read 路徑「解不出來」時放行,`..`、`//`、`~`、相對路徑能讀席報告暫存處
severity: major
blocking: 是 — 設計宣稱 Read 讀暫存處一律擋(S2),實作對解不出真實路徑的寫法回放行,繞法一個字就能做到。
- 誰:被文件誘導的審查席。
- 入口:`Read` 的 `file_path`。
- 送什麼:`/tmp/x/../lumos-seat-staging/<迴圈>/r1-資安.md`,或 `/tmp//lumos-seat-staging/…`,或 `~` 開頭、相對路徑的寫法。
- 拿到什麼:同輪別席已交回的報告全文,破壞「各自獨立」。
- 原因:`realOf` 對含 `..`、`.`、空段或不以 `/` 開頭的路徑回 `null`。Read 分支只有在 `real !== null && inStaging(real)` 時才擋,`null` 就直接放行。Write 和 Grep/Glob 的 `null` 都是擋,只有 Read 反過來。
- 型別檔 `$.fs.stat` 的說明已明講「守衛要在解不出來時擋,因為 `~`、還不存在的檔,工具仍可能打開」。`/.vol/<dev>/<ino>` 這類寫法也保留自己的拼法,同樣不會被判成暫存處。
- `guard.test.ts` 的 S2 Read 測試只測了正規絕對路徑,沒有 `..` 或 `//` 的案例。

引句:「return real !== null && inStaging(real)」
file: `mods/claude/lumos-guard/hooks/register.ts:170-175`

### F2 Bash 粗擋區分大小寫,macOS 上 `GH`、`Git push`、`CLAUDE`、`LUMOS-SEAT-STAGING` 全放行
severity: major
blocking: 是 — 設計宣稱 Bash 提到 gh、git push、claude、`lumos-seat-staging` 就擋,macOS 預設不分大小寫,改大小寫就不被擋,不需要編碼或組字串。
- 誰:被誘導、被擋一次後換寫法的審查席。
- 入口:`Bash` 的 `command`。
- 送什麼:`GH pr create`、`Git push origin HEAD`、`CLAUDE -p …`、`cat /tmp/LUMOS-SEAT-STAGING/*/*`。
- 拿到什麼:開 PR 或推分支、另開不受管的 claude 子程序、讀別席報告。
- 原因:詞比對用 `words.has(w)`,字串比對用 `cmd.includes(s)`,兩者都區分大小寫。
- 同一個外掛的 Read 路徑已經用 `fold()` 處理大小寫別名,測試也有,只有 Bash 判斷沒做。
- 設計誠實界線只列「變數或編碼組出來的指令」,沒有把大小寫別名列為已承認。

引句:「const words = new Set(cmd.split(/[^A-Za-z0-9_.-]+/).filter(Boolean))」
file: `mods/claude/lumos-guard/hooks/register.ts:115-118`

### F3 外掛原始碼就在審查席能改的 repo 裡,而且是被即時讀取的市集資料夾
severity: minor
blocking: 否 — 縱深防禦。改 repo 本來就在誠實界線內,這裡是「守衛自己的程式碼被改」的後果,設計沒有單獨列出。
- 誰:被誘導的審查席。
- 入口:`Bash`,例如 `sed -i` 改 `mods/claude/lumos-guard/hooks/register.ts`。
- 送什麼:把 `TOOLS_OK` 放寬,或讓 `call` 一律回 `null`。
- 拿到什麼:外掛熱重載或下次載入後,守衛失效,或新程式碼在編排者的程序裡執行。此外 `lumos install` 把來源 repo 登記成使用者範圍市集、直接讀那個資料夾,所以那份檔案會變成使用者全域的執行碼。
- 這條不經過 Write 白名單,Bash 本來就擋不到,所以沒有被任何一條規則攔住。

引句:「資料夾型市集是直接讀那個資料夾本身」
file: `scripts/lumos`(diff 中 `_LUMOS_MARKET` 常數上方的註解)

### F4 `onCall` 外層吞掉所有錯誤,Bash 也變成放行,與 S8「Bash 判斷出錯要擋」不一致(推論)
severity: minor
blocking: 否 — 推論:要引擎的 `$.session.id()` 之類呼叫失敗才觸發,攻擊者無法直接造成。
- 誰:任何審查席。
- 入口:引擎介面暫時失敗(`$.session.id()` 丟錯,或 `createGuard` 初始化丟錯)。
- 送什麼:一個正常的 `Bash` 呼叫,例如 `gh pr create`。
- 拿到什麼:`onCall` 的 `catch` 回 `null`,判斷根本沒跑就放行。
- 原因:只有 `guard.call` 內部的 `checkTool` 例外對 Bash 回擋。`onCall` 這層的例外對 Bash 也回放行,`onCallFailed` 的 Bash 擋規則在這裡不會被走到,因為 `onCall` 已經把例外吃掉了。

引句:「return await st.guard.call(await $.session.id(), e)」
file: `mods/claude/lumos-guard/hooks/register.ts:301-308`

逐類結論:
- 1 不可信輸入流到危險操作:發現 F1、F2。標記解析本身(只認第一行、拒 `..`、子代理一律繼承)已看,無。
- 2 權限:寫檔路徑(取真實路徑、折疊大小寫、懸空連結擋)、工具白名單、`isolation` 與 `subagent_type`、登記時序(5 秒等待、`finally` 釋放)都有照設計擋到,無洞。有洞的是 Read(F1)和 Bash 大小寫(F2)。
- 3 密鑰與個資:擋下訊息只印工具輸入的路徑、被擋的詞、`isolation` 值與錯誤訊息前 100 字,toast 只印代理編號。已看,無。
- 5 執行邊界:安裝只動 `lumos-toolchain` 市集和清單內兩支外掛,使用者範圍。市集不是本機資料夾時不碰,解除安裝只在路徑相同且全部外掛移除成功後才移除市集,範圍沒有放寬。只有 F3 一條縱深防禦。
- 新依賴:無。

總結:最嚴重 major,blocking 2 條
