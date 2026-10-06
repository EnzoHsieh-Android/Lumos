severity: major

圖譜鏡頭摘要:牽連清單與合約只點到 `lumos-cli-lifecycle` 這一家(合約 ★INVARIANT★ 是 re-inject 保留 sentinel 外內容,綁測試 t_reinject_preserves_outside)。本 diff 的外掛安裝與移除改動沒碰到那條合約,我也沒看到違反。

### F1 席報告暫存處的搜尋防線只擋 Grep/Glob 工具,真實搜尋走 Bash 時直接繞過,而且提示叫人改用的 Grep 工具在這個引擎版本不存在
severity: major
blocking: 是 — 外掛要擋的「偷看別席報告」,用一般的 `grep -r` 或 `cat` 加萬用字元就漏,不需要刻意繞。
引句:「要搜尋文字請改用 Grep 工具;報告內容直接寫在回答裡,不要用指令寫檔。」
引句:「const BASH_STRINGS = ['api.github.com', 'uploads.github.com', 'lumos-seat-staging']」

- **引擎版本沒有 Grep/Glob。** 引擎型別檔列出該版本內建工具輸入表,有 Agent、Bash、Edit、Read、Write、NotebookEdit,沒有 `Grep`、`Glob`、`Task`、`TaskOutput`。我自己這場會談的工具清單也沒有 Grep 和 Glob,搜尋只能走 Bash。
- **對 Bash 只擋逐字字串。** 暫存處只靠 `cmd.includes('lumos-seat-staging')` 擋。
- **測試走不到真實路徑。** `guard.test.ts` 的 S2 全部用假事件 `{ tool: 'Grep' }` 和 `{ tool: 'Glob' }`。這兩個工具在這版引擎不會出現,所以 S2 綠燈沒測到真實的搜尋路徑。
- **重現。** 我把 `bashBlock` 的邏輯逐字搬出來,在 `/tmp/lumos-seat-work/code-審查席唯讀隔離/通才-sonnet/t.mjs` 跑,下面這些指令都回 `null`(放行):
  - `grep -rn . /tmp`
  - `find /tmp -name "r1-*.md" -exec cat {} +`
  - `cat /tmp/lumos-seat-st*/*/*`
  - `ls /tmp`
- **為什麼不算「有心繞」。** 審查員找檔案時很自然就會下 `ls /tmp` 或 `grep -r ... /tmp`,不必刻意繞,別席報告就洩了。設計稿寫的「不防有心繞」不涵蓋這種意外。
- **Grep/Glob 也不確定一定沒有。** 型別檔註解(約第 12383 行)還提到 Grep,別的版本可能有。但不管有沒有,Bash 的 `grep -r`、`find` 都在白名單內,這個漏洞都在。
- file: `mods/claude/lumos-guard/hooks/register.ts`(新檔,擋下提示在 `checkTool` 的 Bash 分支)

### F2 Bash 字樣粗擋會擋掉本 repo 審查最常用的搜尋,而且給的替代方案(Grep 工具)可能不存在
severity: minor
blocking: 否 — 只是誤擋造成審查變慢,不會放出危險動作。
引句:「const BASH_WORDS = new Set(['gh', 'hub', 'glab', 'claude'])」

- **會擋到什麼。** `words` 用 `[^A-Za-z0-9_.-]+` 切詞,只要出現 `claude` 這個詞就擋。`grep -rn claude scripts/lumos`、`git grep -n push -- scripts`、`git log -S push` 都會被擋。
- **為什麼這個 repo 特別受影響。** 這個 repo 的主題正是 Claude 外掛和 push 閘,審查員天天要搜這幾個詞。
- **代價怎麼記的。** 筆記把這寫成「代價」,但沒提到替代的 Grep 工具在這版不存在(見 F1)。實際結果是審查員只能用 Read 一檔檔看。

### F3 派工詞第一行只要以 lumos-seat 開頭(不分大小寫)就被判寫壞並擋下派工,一般任務也會中
severity: minor
blocking: 否 — 只在派工詞第一行恰好以這個詞開頭時誤擋,可改寫派工詞避開。
引句:「const SEAT_LOOSE_RE = /^lumos-seat/i」

- **誤擋例子。** 主會談派一個第一行是「lumos-seat-work 資料夾清理」或「Lumos-seat 外掛 bug 查一下」的普通子代理,會被判成 `bad`,整個派工被擋。
- **為什麼會發生。** 這個 repo 在做 lumos-seat 相關外掛,第一行寫到這個詞很自然。
- **測試沒涵蓋。** S5 只測了刻意寫壞的標記(`lumos-seat: a/r1/b`、`LUMOS-SEATS: a/r1/b`),沒有測這種合法的一般任務。

### F4 「外掛出錯時 Bash 擋、其他放行」只在 checkTool 內層成立,外層 onCall/onSpawn 的錯誤全放行,測試沒走到
severity: minor
blocking: 否 — 我給不出會讓 `$.session.id()` 真的丟錯的具體情境,屬規則與實作不一致、不是已知會觸發的漏洞。
引句:「    return await st.guard.call(await $.session.id(), e)
  } catch {
    return null」

- **規則與實作不一致。** 文件與 S8 說的規則是 Bash 出錯就擋。但 `onCall` 的外層 `catch { return null }` 讓 Bash 照放行。`onSpawn` 的 `catch { return next(e) }` 讓審查席派工不登記就放行。
- **測試沒走到。** S8 測試直接呼叫 `g.call` 的內層。`onCallFailed` 只有掛鉤逾時或丟錯才會觸發,而 `onCall` 已經把所有錯誤吞掉,所以 `onCallFailed` 對丟錯路徑實際走不到,只會被逾時觸發。
- **這支 `.catch` 其實要靠逾時。** 引擎預算是 10 秒,`call` 內等登記最多 5 秒(`$.clock.sleep` 會計時),留的餘裕不大。
- file: `mods/claude/lumos-guard/hooks/register.ts`(`onCall`、`onSpawn`、`onCallFailed`)

### 固定席逐條
- **事件欄位對照型別檔(逐項核對過):**
  - `tool.call` 帶 `tool`,工具參數攤平,`agentId` 在 `AgentLoop` 上。
  - `agent.spawn` 帶 `prompt`、`parentAgentId`、`cwd`,結果帶 `agentId`;`deny` 時沒有 `agentId`。
  - 這些跟程式假設一致。
- **`$.fs.stat` 的 `realPath`:** 懸空連結回 `undefined`、大小寫別名保留原拼法,跟 `fakeReal` 的假設一致。
- **Teammate 路徑沒驗到:** 型別檔說 teammate 的事件也帶 `agentId`,但我看不出 `agent.spawn` 結果對 teammate 是不是一定回 `agentId`。外掛沒擋 Agent 工具的 `name` 參數。若 teammate 的結果沒給 `agentId`,teammate 會不被登記而不受限。型別檔講得不夠清楚,我無法確認,不標等級,請作者實測。
- **假檔案系統其餘偏差:** 沒發現其他會讓結果變向的差異。
- **假 claude 對真 claude 的 `plugin list`:** 假的預設 `scope` 為 `user`,真實輸出有沒有 `scope` 欄位我無法驗證(筆記只列 `id`、`enabled`、`readFromFolder`)。
- **「新增外掛不跑 marketplace update 也裝得上」:** 屬單次實測宣稱,我無法複驗。
- **移除與市集保留邏輯:** 逐 hunk 讀過,一支失敗就保留市集、成功才移除,邏輯自洽。
- **ledger 的 `spawnFields`:** 改讀 `parentAgentId` 與型別檔一致。

總結:最嚴重 major,blocking 1 條
