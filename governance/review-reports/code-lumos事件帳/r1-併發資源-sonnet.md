severity: minor

審查範圍:diff 已套在 /Users/enzo/harness/lumos-toolchain-event-ledger 工作樹,實驗都在 /private/tmp/claude-501/rv2(臨時目錄、假 claude),沒有執行任何 claude plugin 變更類子指令。

### F1 --prune 與外掛同時寫入同一個舊會談:prune 以 traceback 中止,該會談只剩半截歷史
severity: minor
blocking: 否 — 只動可再生的診斷帳、手動指令,且要會談閒置超過 N 天又剛好在刪除瞬間被續用才中招。

hunk:`_events_prune`。
引句:「所以最近 24 小時內動過的會談(正在寫的)天然落在保留範圍,不另設一道判斷;」
問題:24 小時保護只擋最近有動的會談。閒置超過 N 天、此刻被 --resume 續用的會談,資料夾 mtime 仍是舊的,會被選中;`shutil.rmtree(d)` 沒有任何例外處理。
時序→結果:
1. `lumos events --prune --days 1` 把會談 B 的舊塊檔刪光。
2. 外掛此刻寫入新塊檔 9-new.jsonl。
3. rmtree 最後的 rmdir 回 Directory not empty。
4. 例外沒人接,整支 prune 以 traceback 中止,排在後面的會談 C 沒被處理。
5. B 只剩新塊檔,續用前的歷史事件已被刪掉。
重現(/private/tmp/claude-501/rv2/t.py,在 os.rmdir 對 B 呼叫前寫入新塊檔來模擬外掛):
```
EXC OSError [Errno 66] Directory not empty: .../events/B
left ['B', 'C']
B files ['9-new.jsonl']
```
這是用 monkeypatch 決定時序的重現,不是自然競態。
同型缺口:`newest = max([...] + [f.stat() ... for f in d.iterdir()])` 在 iterdir 與 stat 之間若有檔被改名或刪除(寫端若用暫存檔再改名)會拋 FileNotFoundError;讀端 `_events_sessions` 的排序 key 與 `_events_read` 的 read_text 在並行 prune 時也沒接。
file: `scripts/lumos:18788`(prune 本體,行號為套用後工作樹的大致位置)

### F2 外掛同步被中斷或失敗,留下半套狀態:市集已移除、新的沒加上,install 仍回 0 且沒給救援指令
severity: minor
blocking: 否 — 重跑 lumos install 就補得回,但目前沒有任何提示會讓人想到要重跑。

hunk:`_sync_claude_plugin`。
引句:「_claude_do(claude, ["plugin", "marketplace", "remove", _LEDGER_MARKET, "--scope", "user"])」
問題:同名市集指向別的本機路徑時是先 remove 再 add,兩步之間沒有補償。add 逾時(30 秒)、被殺或失敗時,原本能用的外掛一起消失。
時序→結果(c.py,假 claude 的 add 回 1):
1. 市集 lumos-toolchain 登記在 /tmp/oldwt,外掛已裝。
2. remove 成功、add 失敗。
3. 結果:
```
  ⚠ Claude 事件帳外掛 ... 沒裝好:plugin marketplace add:net down
C failed
{"markets": [], "plugins": []}
```
4. 這行只印到 stderr,install 回傳碼不變。
5. 事件帳靜默停寫;enforcement 那列只會變 stale,而 stale 刻意不被開場提醒點名。
6. teardown 失敗時會附兩條手動指令,sync 失敗時沒有,救援路徑不對稱。
⚠ 假 claude 的 remove 我寫成會連帶移除該市集底下的外掛,真 claude 是否如此沒有驗證(只准 --help);就算不連帶,市集消失這一半仍成立。
file: `scripts/lumos:18804`

### F3 兩支 install 同時跑:外掛步驟沒有互斥,兩邊都走到 add 與 install
severity: minor
blocking: 否 — 假環境只能顯示無互斥,真 claude 對同名重複 add、install 是冪等還是報錯沒有驗證,後果判不準。

hunk:`_sync_claude_plugin`,查列表→決定→加或裝不是原子操作。
時序→結果:A、B 以空狀態同時開始(假 claude 的 list 各延遲 0.5 秒),呼叫紀錄顯示兩邊都先 list,再各自 `marketplace add ... --scope user`,再各自 `plugin install`。若真 claude 對同名市集重複 add 回錯,後到的那支會印沒裝好(最終狀態其實是對的,屬誤報);若兩支的 `_lumos_src()` 不同(不同 LUMOS_HOME),會輪流 remove 再 add,最後來源取決於誰最後動手。
⚠ 依賴真 claude 行為。

### F4 lumos events 列表一次讀光最近 10 個會談的全部塊檔,並每個會談各跑一次 git 子行程
severity: minor
blocking: 否 — 只在手動列表時變慢,不在開場 hook 路徑,且需大量塊檔才明顯。

hunk:`_events_sessions` / `_events_read`。
問題:為了算回合數與工具數就 read_text 讀完每個塊檔;每次 `_events_read` 又重新呼叫 `_events_root`,多一次 git 子行程。
實測:單一含 2 萬塊檔(每塊 5 行)的會談,`_events_sessions` 約 1.64 秒;10 個這種會談線性放大。
反駁點:enforcement 新列只掃會談資料夾 mtime、不讀塊檔,3 萬個會談資料夾下整支 enforcement_status 約 0.27 秒(該列約 0.26 秒),遠低於 7 秒預算;唯一外部成本是 `_events_root` 的 git 子行程(逾時上限 3 秒,逾時與 OSError 有接)。開場 hook 路徑沒找到會被拖垮的時序。

### 圖譜鏡頭
- 機械反查三格皆空,沒有固定席筆記需逐條判。
- `_sync_global_hooks` 回傳值不受影響:兩處 `_sync_claude_plugin()` 呼叫都不併進回傳字串,cmd_install 與 `_sync_global_from_project` 的判斷不變。
- `_sync_global_from_project` 在 lumos update 與 init 路徑也會呼叫外掛步驟,每次最多 5 個子行程、單步 30 秒、無總預算(最壞約 150 秒);沒找到任何 hook 會呼叫 install 或 update,所以不在開場路徑。
- 表態記錄 py-eventloop na 與這份 diff 無關。
- 測試隔離(LUMOS_SKIP_CLAUDE_PLUGIN、清掉 CLAUDE_CONFIG_DIR)在這份 diff 內沒有漏洞。

最嚴重 severity:minor;blocking 條數:0。
