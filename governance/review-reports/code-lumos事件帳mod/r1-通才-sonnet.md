severity: major

審查範圍:凍結 patch 全份(register.ts、ledger.test.ts、hooks.json、plugin.json、marketplace.json、S9 測試、圖譜筆記)。已實測:`claude plugin test mods/claude/lumos-ledger` 12 條全過;`python3.14 scripts/test_lumos.py -k ledger_plugin_files_valid` 15 條全過。兩場 `claude -p`(haiku、`--plugin-dir`,各在自己的臨時 repo)重現 F1、F2。外掛自己的測試與 S9 都綠,但擋不到 F1、F2。

### F1 緩衝以「會談編號+cwd」分桶,依桶建立順序各寫一塊,同一會談事件被寫成錯序、回合框架被打亂
severity: major
blocking: 是 — 讀取端靠「塊檔名排序+塊內行序」框回合,錯序會讓工具事件落在 turn_end 之後,事件帳的核心用途(這一回合做了什麼)失真,且 Bash 的 cd 很常見
引句:「const key = keyOf(session, cwd)」
引句:「for (const [k, b] of bufs) if (b.session === session) enqueue(k)」
- 成因:Claude Code 的 `$.session.cwd()` 會跟著 Bash 的 `cd` 變。每個 cwd 一個緩衝,`flushSession` 依 Map 建立順序逐桶各寫一塊,桶與桶之間沒有全域順序(沒有序號,也不依 ts 合併)。讀取端 `_events_read` 只依檔名排序,不依 ts。
- 重現(臨時 repo 含 docs/demo-knowledge 與 sub/ 子資料夾,載入原樣外掛):Bash 依序執行 `cd sub && pwd`、`cd .. && pwd`、`cd sub && pwd`、`cd .. && pwd`,一個回合。
  - 輸入:上述四次 Bash。
  - 結果:產生 2 塊。第一塊(檔名 ...830)依序是 turn_start(16:52:09)、tool `cd sub`(14.8)、tool `cd sub`(19.3)、turn_end(22.8)。第二塊(檔名 ...849)是 tool `cd ..`(17.1)、tool `cd ..`(21.4)。讀取端照檔名讀會得到「turn_end 之後還有兩筆這回合的工具事件」,實際時間是穿插的。
- ledger.test.ts 沒有任何「同一會談、cwd 中途變動」的案例;「/clear」案例的兩個會談用同一個 cwd。
- 修法方向:緩衝改以會談編號為鍵,cwd 只用來決定寫入位置(或每筆事件帶收到時的位置判定、合併時依到達序);不要讓同會談事件跨桶亂序。
- file: `scripts/lumos:23596`(`_events_read` 只依檔名排序、塊內行序)

### F2 寫入端不檢查事件帳上層是否為符號連結,被提交進 repo 的連結能把事件寫到 repo 外
severity: major
blocking: 是 — 屬「不可逆/寫到不該寫的地方」:陌生 repo 可帶 `governance -> /任意路徑` 的連結,Bash 指令前 500 字會被寫出去;讀取端明確拒絕連結(r2、r3 已修),寫入端與它不對稱
引句:「const dir = `${v.main}/${EVENTS_REL}`」
- 重現:臨時 repo 含 docs/demo-knowledge,並提交 `governance` 為符號連結(git ls-files -s 顯示 120000)指向 repo 外資料夾。
  - 輸入:`claude -p "用 Bash 執行 echo hi"`,載入原樣外掛。
  - 結果:`runtime/events/.gitignore` 與 `runtime/events/<會談>/1791219168882-aa054a7e.jsonl` 全部寫進連結目標(repo 外),repo 內 `git status` 乾淨。讀取端 `_events_path_safe` 對這種路徑回 False,所以這份帳寫了卻永遠讀不到。
- S9 測試只用正規式檢查「`io.write(` 的第一個參數以 `${dir}/` 開頭」,檢查不出 dir 實際解析到哪;`$.fs.stat(path, { resolve: true })` 可取 realPath,外掛沒用。會談資料夾 `${dir}/${b.session}` 若是連結同理。
- file: `scripts/lumos:23715`(`_events_path_safe`,讀取端的逐層連結檢查)

### F3 圖譜判定把符號連結的資料夾當成不是資料夾,與 lumos 的 `_vault_in` 不一致
severity: minor
blocking: 否 — 只影響少見的連結型 docs 佈局,結果是該專案不記帳,不損壞資料
引句:「docs.some(e => e.kind === 'dir' && (e.name === 'knowledge'」
- 型別檔明寫 `$.fs.list` 對符號連結回 `other` 加 `isLink`,Python 的 `Path.is_dir()` 與 `iterdir()` 會跟連結。`docs/foo-knowledge` 是連結時 lumos 認得、外掛判 skip 且 10 分鐘內快取,沒有任何提示。計劃寫「跟 `_vault_in` 同三種」,實際分歧未記。
- file: `scripts/lumos:22379`(`_vault_in`)

### F4 寫塊失敗只記原因,不記丟了幾筆;失敗後若會談先結束,錯誤標記也丟
severity: minor
blocking: 否 — 設計已承認不重試,缺的是可偵測性,不影響其他資料
引句:「b.err = String((e as Error)?.message ?? e).slice(0, 200)」
- 緩衝在寫之前已清空(`b.events = []`),失敗時缺口大小沒有記錄(同檔的超量丟棄有 `dropped` 計數,寫失敗沒有)。連續失敗時 `b.err` 被後一次覆蓋,只剩最後一個原因。`b.err` 掛在緩衝物件上,`session.end` 的 `drop` 之後下一塊不存在,補寫不會發生,讀者看不到任何缺口。
- 修法方向:失敗時把 `events.length` 累進 `b.dropped`,並讓 `ledger_error` 帶筆數。

### F5 回合編號只存在記憶體:熱重載、resume 後從 1 重算,且 `turn` 欄位型別混用
severity: minor
blocking: 否 — 目前讀取端文字輸出不用 `turn`,但欄位對下游消費者(收工檢查等)是歧義的
引句:「const n = (st.turnNo.get(s) ?? 0) + 1」
- 同一會談在熱重載或 `--resume` 新行程後 `turn` 重新從 1 起,同一會談內會有重複編號。另 `turn_end` 的 `turn` 主會談是數字、子代理是 turnId 字串,同欄兩種型別;計劃的欄位表只寫「`turn`」。

### F6 工具事件與 spawn 事件只在 `next(e)` 正常回傳後才記;next 丟錯(中斷)時整筆消失 ⚠
severity: minor
blocking: 否 — 無實測,且只影響被中斷的那一筆
引句:「const r = await next(e)」
- ⚠ `next.signal` 在使用者中斷時會 abort;若 `next(e)` 因此 reject,`onTool` 不會執行,這次呼叫沒有任何事件(`ok` 為 false 的紀錄也沒有)。我沒能在 `claude -p` 重現中斷,判不準。

### F7 熱路徑上等整條共用串行佇列(含 git 3 秒),拖住主迴圈的 hook
severity: minor
blocking: 否 — 有 3 秒逾時上限,每 5 分鐘最多一次;但外掛宣稱「只觀察、不影響本業」,且佇列是全會談共用
引句:「return b.events.length >= FLUSH_AT ? enqueue(key) : undefined」
- `add` 在滿 50 筆時回傳整條佇列的 promise,`record` 與 `onTurnEnd` 都 `await` 它,所以 `tool.call`、`turn.complete` 會等前面任何會談排的寫塊、`git rev-parse`(3 秒)、`$.fs.list`(無逾時)。判定為「暫時失敗」且緩衝已滿 50 後,每一筆事件都再排一個任務。`$.fs.list`、`$.fs.exists`、`$.fs.write` 沒有逾時保護,任一卡住會讓之後所有等佇列的 hook 卡到 10 秒 hook 預算才被放棄。

### F8 塊名只保證單一行程內遞增,重新載入或時鐘倒退後的新塊會排到舊塊之前
severity: minor
blocking: 否 — 計劃第 3 節已承認跨行程同毫秒先後不保證,但沒涵蓋「時鐘倒退」;只影響少見情況
引句:「const ms = Math.max(io.now(), lastMs + 1)」
- `lastMs` 是 createLedger 實例內變數,重新載入歸零。時鐘被往回調(NTP 校正、休眠恢復)後,同會談新塊的檔名小於既有塊,讀取端依檔名排序會把新事件插在舊事件前面。ledger.test.ts 的「重新載入後再寫(時鐘倒退)」只驗「不覆蓋舊塊」,沒驗順序;修法方向:新實例啟動時先讀會談資料夾最大塊名當下限。

總結:最嚴重 major,blocking 2 條
