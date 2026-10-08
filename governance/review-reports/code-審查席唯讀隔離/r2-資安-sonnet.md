severity: major

### F1 絕對路徑的 git 讓 push 擋不到
severity: major
blocking: 是 — 設計宣稱要擋 git 配 push,而 `/usr/bin/git push` 這種直白寫法實作沒擋到
- 誰、入口:被誘導的審查席,用 Bash 工具。
- 送進來:`/usr/bin/git push origin HEAD`、`/opt/homebrew/bin/git push`、`/usr/bin/git send-email x.patch`。
- 拿到:把分支推出去,或用 send-email 外寄。
- 原因:`words.has('git')` 比的是整份 `toks` 的字面詞,不是前面算出的「路徑最後一段」。切詞不切斜線,所以 `/usr/bin/git` 這個詞不等於 `git`,`push` 那半條規則根本不啟動。
- 對照:r1 之前以非字母數字切詞,這種寫法會被擋,所以這是修 e2 時新開的洞。
- 現有測試若只測 `git push` 與 `gh`,不會紅。
引句:「  if (words.has('git')) for (const w of GIT_PUSH_WORDS) if (words.has(w)) return `指令裡同時有「git」與「${w}」`」
佐證 ``file: `mods/claude/lumos-guard/hooks/register.ts:133` ``

### F2 以 `$HOME/` 或相對路徑呼叫 gh、claude、git 放行
severity: major
blocking: 是 — 設計宣稱要擋 gh 與另開 claude,而最常見的安裝位置寫法沒擋到
- 誰、入口:審查席的 Bash。
- 送進來:`$HOME/.local/bin/claude -p "..."`(claude 常見安裝處)、`cd /opt/homebrew && bin/gh pr create`、`node_modules/.bin/gh`、`$HOME/bin/git push`。
- 拿到:另開 claude 子程序、開 PR。
- 原因:`$` 是切詞符,`$HOME/.local/bin/claude` 切成 `home/.local/bin/claude`。這個詞不以 `/`、`./`、`../`、`~/` 開頭,最後一段的判斷不適用,整個詞不等於 `claude`。
- 相對路徑 `bin/gh` 同理。
- 這是 r1 e2 把斜線拿掉切詞的副作用。「明確的執行路徑」的前綴白名單沒涵蓋 `$VAR/` 開頭與無前綴的相對路徑。
- 修法方向:取每個詞最後一個 `/` 之後的段來比,整詞與路徑一視同仁。誤擋只剩 `cat /x/claude` 這類寫法,符合寧可誤擋的決策。
引句:「    const last = /^(\/|\.\.?\/|~\/)/.test(t) ? t.slice(t.lastIndexOf('/') + 1) : t」
佐證 ``file: `mods/claude/lumos-guard/hooks/register.ts:130` ``

### F3 對照表存回時整份覆寫,熱重載後其他席會從狀態裡消失
severity: minor
blocking: 否 — 縱深防禦,要先碰上熱重載才會發生,且只在重載之後的第一次登記才會覆寫
- 誰、入口:外掛熱重載(例如審查期間重跑 `lumos install --force`)之後,編排者派出新審查席。
- 流程:`lookup` 每次只把被查的那一個 id 從 `$.state` 併進記憶體,`save` 卻把記憶體整份寫回 `$.state`。重載後尚未被查過的舊席會被這次寫入抹掉。
- 拿到:那一席下一次的工具呼叫,記憶體與 `$.state` 都查不到,被當主會談放行,白名單與 Bash 粗擋失效。
- 這與 r1 p2 修復宣稱要守住的場景相同,所以算修補本身的缺口。
- 推論:需要重載與新登記兩個條件湊在一起。
- 另一個小處:`end` 之後只清記憶體裡登記過的 id,重載後載回的 id 不在 `bySession`,永遠留在 `$.state`。這不是洞,只是累積。
引句:「    try { await io.saveSeats(Object.fromEntries(seats)) } catch { /* 存不進去:這場仍在記憶體裡擋 */ }」
佐證 ``file: `mods/claude/lumos-guard/hooks/register.ts:232` ``

### F4 出錯時 seatish 只看記憶體,`$.state` 讀不到就放行
severity: minor
blocking: 否 — 縱深防禦,推論,需要外掛自己先出錯
- 誰、入口:審查席的 Bash,恰好撞上 `onCall` 內部出錯,例如 `$.session.id()` 丟錯。
- 前提:熱重載後 `st.guard` 已建立,但該席尚未被 `lookup` 載入記憶體。
- 結果:`seatish` 回 `false`,錯誤路徑不擋 Bash。
- `call` 內部的 `lookup` 在 `$.state` 讀失敗時回 `undefined`,走「不是審查席」放行。這與 r1 g4 要修的「出錯就放行」同形,只是縮小了範圍。
- 建議:`lookup` 讀失敗時,若該 agentId 非主會談,回傳「不確定」,Bash 照擋。
引句:「    seatish(id: unknown): boolean {」
佐證 ``file: `mods/claude/lumos-guard/hooks/register.ts:312` ``

### F5 `$.state` 的值能被別的外掛攔截並改寫
severity: minor
blocking: 否 — 縱深防禦,推論,攻擊者要先有另一支已安裝的外掛
- 型別檔說明:`state.set` 與 `state.get` 是可被掛鉤的事件,其他外掛可 hook `state.set` 改 `e.value`。
- 誰、入口:使用者已裝的另一支外掛,或審查席用 Bash 寫進去的外掛(後者屬 Bash 誠實界線)。
- 送進來:改寫 `lumos-guard.seats`,清空或把 `cwd` 改掉。
- 拿到:`lookup` 讀回的席位沒有通過檢查,而且 `lookup` 沒驗證讀回來的物件形狀。
- 因為記憶體優先,只有重載後才吃到這份被改過的資料。
- 建議:讀回後驗證形狀。
- 我沒看到審查席能直接寫 `$.state`。
引句:「    loadSeats: async () => (await $.state.get({ plugin: 'lumos-guard', key: 'seats' })).value ?? {},」
佐證 ``file: `mods/claude/lumos-guard/hooks/register.ts:328` ``

### F6 失敗訊息的手動指令附註解,照抄會直接執行移除
severity: minor
blocking: 否 — 縱深防禦,誤導風險很低,而且動到的只在「判不出市集來源」的分支
- 誰、入口:使用者。外掛移除失敗,且市集查詢也失敗(`ours is None`)。
- 內容:指令印成 `claude plugin marketplace remove lumos --scope user    # 先用 … 確認 …再刪`,要求人先確認。
- 問題:整行貼進 shell 時,`#` 後面的註解不會阻止前面的指令執行。照抄的人會在沒確認的情況下,移除一個可能不是我們的同名市集。
- 修法方向:把確認寫成獨立一行(`claude plugin marketplace list`),移除指令放在其後、獨立一行。
引句:「            todo.append(f"{market_cmd}    # 先用 claude plugin marketplace list 確認它的來源是 lumos 的資料夾再刪")」
佐證 ``file: `scripts/lumos:22082-22091` ``(以 delta 的 `@@ -22066` 區塊為準)

### 逐類
1. 不可信輸入流到危險操作:有發現,見 F1、F2。大小寫已修。`gh`、`hub`、`glab`、`claude` 的整詞與 `/`、`./`、`../`、`~/` 開頭的路徑已擋。沒擋到的是 `git` 的路徑寫法、`$VAR/` 開頭與無前綴相對路徑。寫壞標記的判準(`SEAT_LOOSE_RE`)只會多擋,不會放行。路徑上限(4096 字、256 段)正確擋下,沒有新放行。
2. 權限:`seatish` 的弱點見 F3、F4。審查席拿不到別人的 agentId,也無法讓 `agentId` 變成非字串。`$.state` 被竄改見 F5。
3. 密鑰與個資:擋下訊息新印出的路徑片段是審查席自己送進來的 `file_path`,最多 200 字,印回給它自己。例外訊息最多 100 字。沒有不該印的內容。
5. 執行邊界:安裝與移除只動 `lumos` 市集,而且先確認來源是本機資料夾且路徑相同。`_lumos_plugin_listed` 對 null、數字、BOM 的處理沒有動到別人的外掛。手動指令誤導見 F6。
新依賴:無。

### 前輪修復驗收
- r1 s1(Read 路徑含 `.`、`//`、`..` 或相對路徑讀得到暫存處):已修。`realOf` 拒收空段、`.`、`..`,Read 在 `real === null` 時直接擋。
- r1 s2(Bash 粗擋分大小寫):已修大小寫,但連帶打開 F1、F2,所以整體算部分。
- r1 s3(外掛原始碼在審查席改得到的位置):已寫進誠實界線並綁 REVISIT,不是程式修法。對這條已看,無新發現。
- r1 s4(onCall 外層吞錯、Bash 也放行):部分。改成 `seatish` 判斷,但 F3、F4 的情境還是會放行。

總結:最嚴重 major,blocking 2 條
