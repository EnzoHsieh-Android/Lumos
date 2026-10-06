severity: minor

整體判斷:併發與資源這條線沒有 blocker 或 major。5 秒等待加掛鉤預算、啟動中清單的計數、`end()` 清理都站得住,細節在「固定席逐條」。找到 3 條 minor,其中 F1 和 F3 有最小重現,F2 只是從程式和型別檔推導。

### F1 等待者只在「整個會談的啟動中計數歸零」才放行,先登記好的席也被拖到最後一席回來
severity: minor
blocking: 否 — 只多等最多 5 秒,登記完成後結果仍是正確的擋或放,沒有漏擋

引句:「if (p.n <= 0) {」
引句:「new Promise<void>(res => p.waiters.push(res)),」

時序:
1. 席 A 先派,席 B 在 A 回結果之前也派進來,此時 `p.n=2`。
2. A 的子代理已啟動並呼叫工具。A 還沒登記,所以 `call` 進入 `p.waiters.push(res)` 等待。
3. A 的 `spawn` 回來:`seats.set` 已完成,`release` 把 n 降到 1。
4. `release` 只在 `p.n <= 0` 時才喚醒等待者,所以 A 的第一次工具呼叫要等 B 也回來,或撐到 `WAIT_MS` 的 5 秒計時到。
5. 審查席通常同時派 3 到 4 席,各席啟動快慢不一,第一次工具呼叫常會因此多等。

我在 `/tmp/lumos-seat-work/code-審查席唯讀隔離/併發資源-sonnet/t.mts` 用 `createGuard` 加假 io 重現:A 登記後 `pending n=1`,`callA` 仍卡住,時鐘走到 5 秒才放開,放開後 Write 被正確擋下。所以後果是延遲,不是漏放。

修法方向:每次 `seats.set` 之後就喚醒該會談所有等待者,讓它們各自重查 `seats.get(id)`;還沒登記的再回去等,不必等計數歸零。

### F2 外掛熱重載後 seats 歸零,執行中的審查席與它們的孫代理無聲脫離白名單
severity: minor
blocking: 否 — 要在審查進行中重載外掛才發生,而且威脅模型是防誤導、不防有心繞

引句:「const seats = new Map<string, Seat>() // 子代理編號 → 席位」
引句:「const st: State = { guard: null }」

時序:
1. 審查進行中,外掛熱重載。型別檔寫明熱重載會取消舊環境的等待;`.state` 也寫明「survives a hot reload」。
2. `register` 重跑,`st.guard` 變成新的 `createGuard`,`seats`、`bySession`、`pending` 全空。
3. 執行中審查席的下一個 `tool.call`:`seats.get(id)` 為 undefined,`pending.has(session)` 為 false,走到 `if (!seat) return null`,放行。
4. 該席再派孫代理時,`parentAgentId` 不在 `seats` 裡,第一行又不是標記,走 `next(e)`。孫代理也不受限。

誘因:新增的 Python 流程會在使用者機器上逐支裝外掛,`lumos install --force`、更新、卸載都可能在審查期間觸發重載。失敗時沒有任何訊息,連 toast 都沒有。
修法方向:用 `$.state` 或 `$.store` 存 agentId 到席位的對照,JSON 資料即可;或至少在 `register` 重跑時發一則 toast。

引型別檔佐證(file):`/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:3276`

### F3 install 之後新加的「列表確認」第一次查詢沒有被 `_lumos_plugin_wait` 包住,撞到另一支同時在寫就直接判失敗
severity: minor
blocking: 否 — 只影響並行 install 的罕見交錯,重跑就好,且是可預期的 failed 不是損壞

引句:「if not (_lumos_plugin_user(claude, pid) or _lumos_plugin_wait(lambda: _lumos_plugin_user(claude, pid))):」

時序:
1. 兩支 `lumos install` 同時跑,甲剛裝完 `pid`。
2. 甲立刻呼叫 `_lumos_plugin_user`,這時乙正在寫設定檔,`claude plugin list --json` 回非零或 JSON 壞掉。
3. `_claude_json` 丟出 RuntimeError 或 ValueError。這個例外發生在 `or` 的第一個運算元裡,`or` 右邊的 `_lumos_plugin_wait` 根本不會執行。
4. 例外一路傳到 `_sync_claude_plugin` 的 `except`,印「沒裝好」,`worst` 變成 failed。實際上外掛已經裝好了。

這正是 `_lumos_plugin_wait` 要處理的情境。舊程式碼沒有這個「裝完再確認」的步驟,是這次新加的失敗點。

我在 `/tmp/lumos-seat-work/code-審查席唯讀隔離/併發資源-sonnet/` 用 Python 3.14 載入 `scripts/lumos`,假造 `_lumos_plugin_user`(第一次回 False、第二次丟 RuntimeError):
- 輸出:`丟出: RuntimeError ... ['list', 'install', 'list']`
- `wait` 沒有出現在呼叫序列裡。

修法方向:把第一次查詢也放進 try,例外時當成「還沒看到」,交給 `_lumos_plugin_wait`。

### 固定席逐條
- 圖譜牽連與合約:`lumos-guard`、`lumos事件帳` 兩篇都沒有登記合約。與併發資源有關的只有 `lumos-cli-lifecycle` 的 re-inject 合約,而這份 diff 沒碰 re-inject。
- 5 秒等待加掛鉤預算:型別檔寫明預算只計掛鉤自己的時間,`$` 呼叫不計,但 `$.clock` 的等待要計。`call` 只有一次 `io.sleep(5000)`,最多 5 秒,低於 10 秒。`$.session.id()` 和 `$.fs.stat` 都不計入,所以不會誤走 `.catch`。若走到 `.catch`,`onCallFailed` 的分流也正確。
- 殘留計時器:`sleep(WAIT_MS)` 沒傳 signal,等待者先被放行後那個 5 秒計時器仍會留著。我沒有證據說明它會造成問題,所以不列 finding。
- 計數不漏放:`spawn` 的 `finally` 一定會 `release`,`next` 拒絕時也會。`pending` 在 `p.n<=0` 時才刪。在 `spawn` 還沒回、`end()` 又把 `pending` 刪掉的交錯下,晚到的 `release` 會找不到條目就直接返回,不會出錯。
- 會談結束時還有等待者:`end()` 會喚醒所有等待者,不會卡住。
- Map 只增不減:`seats` 與 `bySession` 只在 `session.end` 清,長會談內每席只多一個小物件,幾百筆也只有 KB 級,不會無界長大。`spawn` 回來晚於 `end()` 時會留下少量殘項,量極小。
- Python 總預算:`_lumos_plugin_wait` 的 10 秒預算只防「再開新的一次查詢」,單次查詢最長 30 秒。兩支外掛逐支裝,最壞情況是每支「install 30 秒加查詢 30 秒加重查」,在 claude 卡死時才會到。這個放大是兩支外掛造成的線性增加,在實際用法下不會發生,所以不單獨標。
- subprocess 逾時:`_claude_do` 與 `_claude_json` 都有 `timeout=30`,`TimeoutExpired` 都在各處的 `except` 清單裡。

總結:最嚴重 minor,blocking 0 條
