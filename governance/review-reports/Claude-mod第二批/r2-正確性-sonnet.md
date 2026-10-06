severity: major

## 總覽

已讀全文,逐項對現況實查。第 1 項(壓縮附加段)與會談編號 BASE 配對的邏輯在字面上站得住,但第 3 項有數個照字面實作會出錯的點。牽連節點:派工尾端沒有 hook 附上的牽連節點,不適用。

### F1 抽取函式吃不到報告裡的 file: 引用,而且沒有「file: 前綴」概念
severity: major
blocking: 是 — 照字面實作,S7 在常見輸入下會零判定或誤判,檢查名存實亡

1. spec 說抽取沿用 refcheck 的抽取函式,又說只核對 file: 形式引用。
引句:「`file:` 引用的抽取沿用 refcheck 的抽取函式。」
2. 該函式 `_node_code_ref_tokens` 只看反引號片段(INLINE_CODE_RE 取所有行內程式碼),完全不認 `file:` 前綴:報告裡任何一處反引號路徑(例如反例敘述、被引用的待審文字)都會被抽成引用,與 S7「只核對 file: 引用」互相矛盾。
3. 該函式會丟掉兩類本席與審查員常寫的引用:(a)絕對路徑——`token.split("/")[0]` 是空字串,不在 top_dirs,直接 continue;本次派工自己給的路徑就是絕對路徑;(b)不含 `/` 的 `register.ts:12`——進 bare 集合或 singles,不進 full。所以「路徑換相對 repo 根」那一條作用在抽取之後,而絕對路徑在抽取階段已被丟掉,換算規則對報告引用永遠用不上。
4. top_dirs 要 repo_root(`_refcheck_scan` 的做法:`repo_root.iterdir()`);`cmd_seat_check(report, dispatch, ledger, as_json)` 沒有 repo 參數也沒有 `--repo`,spec 沒說 repo 根從哪來(報告在 /tmp/lumos-seat-work/ 下,不能以報告位置推)。
file: `scripts/lumos:24439-24500`
file: `scripts/lumos:23490`

### F2 去前綴沒寫邊界,本機實測會把兄弟 worktree 切壞
severity: major
blocking: 是 — 字串前綴比對在這台機器的實際 worktree 清單上就會產生錯誤相對路徑

1. spec 規則:
引句:「絕對路徑去掉這個 repo 任一工作目錄(`git worktree list`)的前綴」
2. `git worktree list` 這台機器同時有 `/Users/enzo/harness/lumos-toolchain`(main)與 `/Users/enzo/harness/lumos-toolchain-mod-batch2` 等多個。實跑 `'/Users/enzo/harness/lumos-toolchain-mod-batch2/scripts/lumos'.startswith('/Users/enzo/harness/lumos-toolchain')` 為 True,剩下 `-mod-batch2/scripts/lumos`;沒寫「必須在 `/` 邊界」與「取最長前綴」就錯。
3. 另有巢狀 worktree `/Users/enzo/harness/lumos-toolchain/.claude/worktrees/<名>`:先剝 main 前綴會得到 `.claude/worktrees/<名>/scripts/lumos`,同樣對不上。
4. 即使剝對,審查員在主 checkout 讀 `/Users/enzo/harness/lumos-toolchain/scripts/lumos`(另一個分支的內容),被正規化成與待審 worktree 的 `scripts/lumos` 相同而判「讀過」;spec 沒有交代是否接受這種跨 worktree 放行(內容不同卻算讀過)。
file: `scripts/lumos:22539`(對照用:既有程式沒有現成的去前綴函式可重用)

### F3 席位標記的組成輸入對不上真實派工單形狀
severity: major
blocking: 是 — 標記組不出來或組錯,結果是靜默的「找不到那一席」,檢查看似通過

1. spec:
引句:「席位標記由派工單組成 `<派工單所在資料夾名>/<round>/<seat>`」
2. 現有 `cmd_seat_check` 只讀派工單頂層的 `round`/`seat`(`disp.get("seat")`)。但 repo 自己承認派工單有三種真實形狀(頂層 auditor 的 dict、帶 `seats` 陣列的 dict、頂層 list)。實例:`/private/tmp/code-born-r1-dispatch.json` 與 `/Users/enzo/rtb-mainwt/governance/review-reports/code-task-domain/r2-dispatch.json` 都是 `seats` 陣列形狀,頂層 `seat` 為 None,標記只能組成 `<夾>/r2/None` 或根本組不出;spec 沒說多席單檔時用哪一席(seat-check 只收一份報告,沒有 `--seat` 參數)。
3. 「派工單所在資料夾名」:`/private/tmp/code-born-r1-dispatch.json` 的資料夾名是 `tmp`,標記會是 `tmp/r1/正確性-sonnet`,與派工詞裡寫的不會一致;派工單位置與派工詞標記由誰保證一致,spec 沒寫(`LUMOS-SEAT:` 在 repo 內 grep 零命中,範本尚未存在,spec 第 63 行已承認但沒設一致性測試)。
4. 「外家席一律印外家席不適用」:seat-check 沒有任何欄位能判斷是 Codex 席(spec 沒說用 dispatch 的 `auditor` 還是席名);判不出時,Codex 席會落到「找不到那一席」,印出的原因錯。
5. 「取最後一筆」spawn 時,若最後一筆是被拒的派工(`child` 為 null),spec 沒說要跳過;會用 null 找子代理事件,等同找不到,把先前成功的那一筆蓋掉。
file: `scripts/lumos:23503-23510`
file: `scripts/lumos:11926-11945`

### F4 「讀過」判準:失敗的讀取、子字串比對、事件欄位不足
severity: major
blocking: 否 — 只提醒不擋、spec 已承認偏寬;但下列三點是字面實作的實際洞,不只是寬鬆

1. spec 的 Read 判準只看「有 Read」。事件帳 tool 事件帶 `ok`/`denied`,被拒或失敗的 Read(例如審查席隔離分支就是要擋讀)照樣記路徑;spec 沒要求 `ok` 為真,被拒絕的 Read 會算「讀過」。
file: `mods/claude/lumos-ledger/hooks/register.ts:97-107`
2. Bash 前 500 字「出現該檔路徑」沒寫比對邊界:引用 `scripts/lumos` 時,指令 `git diff -- scripts/lumos-install.sh` 或 `ls scripts/lumos.bak` 都含該子字串,判讀過。
3. Glob 只記 `path`(register.ts 只收 `file_path`、`path`、`notebook_path` 三個鍵),`pattern`、Grep 的 `glob` 參數都沒記;「沒帶路徑算整個 repo 搜過」對 `Glob pattern=**/foo` 與 `Grep glob=*.md` 這類實際窄搜尋也放行。再者沒帶路徑搜尋的根是子代理的 cwd,事件帳沒記 Grep 當時的 cwd,對 repo 外的檔(例如 /tmp 下的凍結快照、plugin 型別檔)「整個 repo」是否算數沒寫。
4. 實務後果:審查員幾乎一定會跑沒帶路徑的 Grep,於是 repo 內任何檔都算「搜尋根目錄讀過」;spec 另印條數,但判準本身使 S7 對 repo 內檔近乎永不列出。
file: `mods/claude/lumos-ledger/hooks/register.ts:97-107`

### F5 RETIRE-IF ③ 的「0 條」分不出健康與壞掉
severity: minor
blocking: 否 — 只影響何時撤掉機制的訊號品質

1. 引句:「收貨紀錄裡 `seat-check --events` 那一行連續一個月都是 0 條——第 3 項撤掉」
2. 「N 條」是列出的沒讀過條數:全部讀過(機制正常)、帳不完整整席不判(S8,條數 0)、抽取全被丟掉(F1 的絕對路徑)三種情況都印 0 條。照這個條件,機制運作良好或完全失效時都會被判撤掉。需要在固定行加「判了幾條、不判原因」才分得出。

### F6 S8「整個會談有寫入錯誤或壞行就不判」範圍過寬
severity: minor
blocking: 否 — 降低可用率,不會誣賴席位

1. 「那個會談的帳有寫入錯誤或壞行」是以整個會談資料夾為單位。`ledger_error` 在丟棄事件、路徑有連結、單次寫入失敗時各會記一筆,編排者會談常常很長,任何一次早期寫入失敗都讓之後所有席都永遠不判。可限縮為該席 spawn 之後的塊,或只看該子代理事件前後。
file: `mods/claude/lumos-ledger/hooks/register.ts:162-188`

### F7 外掛更新與市集新增項目沒有送達路徑 ⚠
severity: major
blocking: 是 — S6 的 seat 欄與 lumos-context 對既有安裝可能完全不生效;⚠ 未實測 claude CLI 行為

1. `_ledger_ensure_plugin` 已裝就直接 return;`_ledger_ensure_market` 在市集路徑相同時什麼都不做;全檔沒有 `plugin update` 或 `marketplace update` 呼叫(grep 零命中)。
2. S6 改的是已存在的 lumos-ledger 的 register.ts;plugin.json 的 version 固定 0.1.0,spec 沒說要升版或怎麼讓既有安裝拿到新程式碼。未升版的外掛 Claude Code 通常沿用快取的安裝副本 ⚠(未實測)。
3. 新增的 lumos-context 要先寫進 `.claude-plugin/marketplace.json`(目前只有 lumos-ledger 一項);spec 的落點清單與 S9 都沒列這支檔,也沒列新外掛需要的 `.claude-plugin/plugin.json`、`hooks/hooks.json`。市集已登記同一路徑的既有使用者,市集快照是否會看到新項目 ⚠(未實測),`plugin install lumos-context@lumos-toolchain` 可能找不到。
4. 失敗模式是靜默的:seat 欄為 null、lumos-context 沒裝,而 S9 只測「install 會裝」,測不到「既有安裝更新」。
file: `scripts/lumos:21990-22050`
file: `.claude-plugin/marketplace.json:4`
file: `mods/claude/lumos-ledger/.claude-plugin/plugin.json:3`

## 逐類實務隱患

- 會談編號 BASE 配對(實查結論):接續(新行程,BASE 隨新行程環境重取,與 Bash 的值相等)、/clear(同行程,BASE 為舊值、Bash 值若也是舊值則相等而採用新的 `$.session.id()`)、巢狀 `claude -p`(子會談官方編號與繼承來的 BASE 不同,退回自己)三種字面上分得開;目前取會談編號處確實只有 `scripts/lumos:46262` 一處(其他 hook 用 payload 的 session_id,不是環境變數)。剩餘風險:BASE 若讀不到會整項退回(spec 步驟 ① 已涵蓋)。
file: `scripts/lumos:46262`
- 事件帳 child 串接(實查):spawn 事件 `child = r.agentId`,子代理的 tool/turn_end 事件以 `e.agentId` 為 `agent` 欄,兩邊同一個 id,可串起來;子代理的 `turn.complete` 帶同一個 agentId(型別檔 AgentSpawnResult 說明)。小提醒:`onSpawn` 用 `e.agentId` 當 spawn 的 agent 欄,但 AgentSpawnInput 的欄位是 `parentAgentId`,巢狀派工的 spawn 會記成 null(對本案審查席不影響)。
file: `mods/claude/lumos-ledger/hooks/register.ts:282-289`
- 併發:spec 已列 `$.env.set` 行程層級;已讀,無新 finding。
- 效能:已讀,無 finding(讀單一會談事件,有 64KB 單行與 16MB 單檔上限)。
- 第 1 項(壓縮附加段、S1-S3):已讀,無 finding(`session.compact` 輸入有 `instructions`、`agentId`,型別吻合)。
- 資安/對外送出:已讀,無 finding。
- 既有決策牽連:無 hook 附上的牽連節點,不適用。

總結:最嚴重 major,blocking 4 條
