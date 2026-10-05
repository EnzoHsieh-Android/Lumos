severity: major

### F1 有 git 但沒有圖譜的會談,緩衝與寫塊嘗試沒有定義(使用者層外掛下這是最常見情況)
severity: major
blocking: 是 — 外掛裝在使用者層,機器上絕大多數 repo 沒有圖譜,這條路徑的緩衝上限與重試節奏完全沒寫,照字面實作會無上限成長並每筆事件都重跑判定
- spec 段落:做法 2 寫入(順序、寫的位置)
引句:「位置解不出來時緩衝原封不動,不先取再放回。」
- 問題:500 筆上限、丟最舊、補 ledger_error 只掛在「git 暫時失敗」那一支。「git 成功但主 checkout 沒有圖譜」(S2 後半)沒說緩衝怎麼辦:不寫,但緩衝要不要丟、要不要設上限、圖譜判定要不要快取。快取只寫了 git 結果以 cwd 為鍵,圖譜判定沒寫。順序條款又規定「判完圖譜成功才取緩衝」,所以判不過時緩衝原封不動。
- 失敗場景:使用者在一個沒有圖譜的 git repo(例如別的專案)跑一場 3000 次工具呼叫的會談。事件累積過 50 筆後,「緩衝滿 50 筆」對之後每一筆事件都成立,每筆都觸發一次寫塊嘗試,每次都重做 `$.fs.list("docs")` 圖譜判定且判不過,緩衝一路長到 3000 筆以上。若實作者把 500 上限也套上來,則靜默丟事件;若不套,記憶體無上限。兩種都不是 spec 明講的行為。
- 佐證:型別檔 `claude-code.d.ts:3156` `fs.list` 每次都是真的磁碟呼叫;spec 條款 S2 只驗「不寫任何檔」,沒驗緩衝行為。

### F2 寫塊時才取會談編號,/clear 之後排隊中的塊會寫進新會談的資料夾
severity: major
blocking: 是 — r1 邊界 F2 場景 C 只修了 session.end 一支,其餘觸發點仍可把舊會談事件寫進新會談資料夾,讀取端無從發現
- spec 段落:做法 2 寫入
引句:「會談編號在寫塊當下用 `$.session.id()` 取,`session.end` 用事件自己的 `sessionId`。」
- 問題:型別檔中只有 `session.end` 的輸入帶 `sessionId`;`turn.complete`、`tool.call` 的輸入沒有。`$.session.id()` 是 async 呼叫。spec 同時說「狀態全部以會談編號為鍵」與「寫塊當下取編號」,兩者在排隊延遲下不是同一個值:資料夾名到底取緩衝的鍵,還是寫入當下的 `$.session.id()`,沒定。
- 失敗場景:會談 A 的 `turn_end` 觸發寫塊,排在串行佇列後面(前一塊寫入慢,例如網路磁碟或磁碟忙)。這時使用者打 `/clear`,會談換成 B。佇列輪到 A 的那塊時才呼叫 `$.session.id()`,拿到 B,A 的事件寫進 B 的資料夾。同理,事件進來時要先 `await $.session.id()` 才知道放哪個緩衝,/clear 邊界上的遲到事件會進錯緩衝。
- file: `claude-code.d.ts:2694` `id: () => Promise<string>`;`claude-code.d.ts:10519` 只有 `SessionEndInput.sessionId`;`claude-code.d.ts:4268` session.end 說明。

### F3 非 git 的判斷靠比對 git 錯誤文字,語系或其他永久失敗會被當暫時失敗而靜默丟事件
severity: minor
blocking: 否 — 只會漏記與多花行程,不會寫錯位置;但「永久失敗」沒有任何痕跡
- spec 段落:做法 2 寫入(寫的位置)
引句:「錯誤輸出含 `not a git repository` → 確定不在 repo 裡」
- 問題:git 訊息會依語系翻譯。呼叫沒指定 `LC_ALL=C`(`ProcessRunInit` 有 `env` 欄位可設)。另外永久性失敗(`dubious ownership`、在 `.git` 裡面或裸 repo 時 `--show-toplevel` 報「必須在工作樹執行」)也落到「暫時失敗」那支。
- 失敗場景:使用者語系是繁中,git 為翻譯版,在非 git 資料夾開會談。分類成「暫時失敗」,每 5 分鐘重啟一次 git 行程,緩衝長到 500 後一直丟最舊;因為從沒寫成功過,補 `ledger_error` 的條件永遠不成立,沒有任何痕跡。另外:`session.end` 時該 cwd 剛好在 5 分鐘不重試窗口內,最後一塊直接丟掉;`claude -p` 短場次碰上一次暫時失敗,整場零事件。⚠ Apple Git 2.39.2 是否帶翻譯檔未驗,但 Homebrew 版會。
- file: `claude-code.d.ts:3406` `$.process.run` 的 init 含 `env`。

### F4 非 git 判定是整個會談層級的永久丟棄,但快取鍵是 cwd,會談中途換目錄就永遠不記
severity: minor
blocking: 否 — 只漏記
- spec 段落:做法 2 寫入(寫的位置)
引句:「並丟掉這個會談的緩衝、之後不再收」
- 問題:同一段說結果「以 cwd 為鍵快取」,卻在非 git 時以「會談」為單位永久停收。型別檔說 `$.session.cwd()` 會隨 `/cd`、worktree 移動改變。
- 失敗場景:使用者在家目錄開 Claude,第一回合後 `/cd ~/proj`(有圖譜)。第一次寫塊判「非 git」,整個會談永久停收,之後 3 小時在有圖譜的 repo 裡的工作一筆都沒記。
- file: `claude-code.d.ts:2673` `cwd()`、`claude-code.d.ts:2692` 起 `projectRoot` 說明提到 `/cd` 與 worktree 移動。

### F5 跨塊排序靠檔名毫秒加隨機字串,同一毫秒或時鐘倒退時,讀取端依序框回合會錯
severity: minor
blocking: 否 — 只污染回合歸屬;事件本身不丟
- spec 段落:做法 3 讀取與保留
引句:「同一毫秒的兩塊靠事件自己的 `ts` 已足夠判讀,不另保證先後」
- 問題:做法 1 的回合歸屬規則是依事件順序框的(前一筆 `turn_start` 到下一筆 `turn_end`),不是依 `ts`。`ts` 也只有毫秒解析度,同毫秒的事件靠 `ts` 無法定序。塊檔名取「寫入時」的毫秒;串行佇列裡連續兩個小塊的寫入各只要不到 1 毫秒並不罕見(三個子代理同時 `turn_end`)。
- 失敗場景:佇列依序寫 X(含主會談 `turn_end` N)與 Y(含 `turn_start` N+1 與其工具事件),兩者同毫秒,隨機字串讓 Y 排在 X 前。讀取端先看到 `turn_start` N+1 與工具,再看到 `turn_end` N,把 N+1 的框提前關掉或歸錯。另外 Mac 睡眠喚醒、NTP 校時使時鐘倒退時,後寫的塊檔名較小,同樣排錯。
- 佐證:`mods` 端可以在取走緩衝的同步時刻就決定檔名時間並保證嚴格遞增,spec 沒要求。

### F6 `lumos events --prune` 沒定義 `--days` 的邊界值,`--days 0` 會砍掉進行中的會談
severity: minor
blocking: 否 — 只丟事件帳,不影響程式與圖譜;但後果發生時無痕跡
- spec 段落:做法 3 讀取與保留
引句:「刪掉修改時間早於 N 天(預設 30)的會談資料夾,印刪了幾個。」
- 問題:N 為 0、負數、非整數、極大值都沒定義;進行中的會談沒有排除。mod 的 `$.fs.write` 會自動建目錄(型別檔寫明 creating it and its directories),被刪後下一塊悄悄重建資料夾。
- 失敗場景:使用者想清空,下 `lumos events --prune --days 0`。目前正在跑的會談資料夾也被刪,下一個 `turn_end` 重建資料夾,只剩刪除後的塊,前半段歷史無聲消失,`lumos events` 看起來像一場只有半場的會談。S11 只驗「早於 N 天才刪」,沒有邊界案例。
- file: `claude-code.d.ts:3128` 起 `fs.write` 說明「creating it and its directories」。

### 逐項核對(查證無 finding)
- `$.process.run` 回傳 `{ exitCode, stdout, stderr }`、非零碼不 reject、`timeoutMs` 欄位名正確(`claude-code.d.ts:3396-3415`);`$.session.cwd()` 預設即 run 的 cwd,spec 寫法成立。
- `agent.spawn` 的 `next(e)` 結果帶「已啟動的子代理編號」(`claude-code.d.ts:369-381`),`child` 取法成立。
- `claude plugin test` 與 `claude-code/testing` 確實存在(`reference.md:77`、`claude-code.d.ts:14124`),S13 的手段可行。
- `_vault_in` 三種判定與 spec 描述一致(`scripts/lumos:19114-19127`);`_note_audit_work_dir` 寫的內容確實是 `*\n`(`scripts/lumos:25980`)。
- `_events_root` 的 `--git-common-dir` 父層法在 worktree 與子資料夾下成立;子模組、裸 repo 會退回 root,與 mod 端一致。
- 既有測試確實釘 23 列(`scripts/test_lumos.py:31327`)。

### 前輪修復驗收
- r1 F1 工具事件回合歸屬:已修好(只記主會談 turn_start、讀取端框回合)
- r1 F2 緩衝與序號並行:修一半(取走緩衝與唯一檔名已修好;會談編號歸屬仍有缺口,見本輪 F2)
- r1 F3 寫入路徑與頂層判定:修一半(絕對路徑、非 git 與暫時失敗分判、cwd 為鍵快取已修好;分類靠語系文字、會談層級丟棄、無圖譜路徑沒定義,見本輪 F1、F3、F4)
- r1 F4 圖譜判定窄於 `_vault_in`:已修好
- r1 F5 worktree 事件帳:已修好(寫主 checkout、`_events_root`、S12)
- r1 F6 塊序號起點:修出新問題(唯一檔名已修好覆蓋問題;排序規則引入同毫秒與時鐘倒退,見本輪 F5)
- r1 F7 `origin` 取錯主體:已修好(只取主會談、依 `door` 篩)
- r1 F8 `spawn` 欄位:已修好(`child` 與 `agent` 語意已寫)
- r1 F9 市集來源:已修好(`_lumos_src()`、同名不同來源先移除再加)
- r1 F10 保留與掃描成本:修出新問題(mtime 排序與 prune 已加;prune 邊界值未定,見本輪 F6)

最嚴重 severity:major,blocking 共 2 條(F1、F2)。
