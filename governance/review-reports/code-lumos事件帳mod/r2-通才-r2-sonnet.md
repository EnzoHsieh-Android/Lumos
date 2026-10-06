severity: minor

審查範圍:凍結 patch r2-snapshot.patch 全文,加上讀取端 `_vault_in`/`_events_root`/`_events_path_safe`/`_events_read`、引擎型別檔、實跑結果。
- `claude plugin test` 20 項全過。
- `python3.14 scripts/test_lumos.py -k ledger_rules_match_reader` 全過。
- claude -p 用了 3 場(haiku、自己的臨時目錄):
  - 場 1:governance 是指向 repo 外的懸空連結,沒有任何檔寫到 repo 外。
  - 場 2:events 是懸空連結,同樣沒有寫出去。
  - 場 3:正常 repo,事件帳照寫,內容與順序正確,含 Bash 失敗那筆。
- 實驗repro在 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ad81457d-7225-41ab-9224-1045d74d59f1/scratchpad/pl(repo 本身沒動)。

### F1 判定等待期間緩衝溢位,會 TypeError 並靜默丟事件
severity: minor
blocking: 否 — 要在一次 git 判定(最長 3 秒)期間湧進 450 筆以上事件才觸發,觸發時只丟一筆、會談不受影響,不到會擋合併。
引句:「const v = vs.get(it.cwd)!」
說明:
- `writeSession` 只替「進入時的前 n 筆」查了判定,查完之後才同步 `splice`。
- 等待期間 `add` 若讓緩衝超過 BUF_MAX,`shift()` 會讓前 n 個位置換成沒查過判定的新事件。
- 它們的 `vs.get(...)` 是 undefined,`v.kind` 丟 TypeError,被 queue 的 `.catch(() => {})` 吞掉。
- 事件已被 splice 取走,沒有 ledger_error,`dropped` 也不計。
重現(臨時副本加測試):
- 輸入:`/repo` 一筆,flush 時把第一次 git 卡住;期間再加 BUF_MAX 筆 `/repo/new0`、`/repo/new1` 交替的事件;放行。
- 結果:寫出 0 筆,pending 499、dropped 1。一筆被取走卻沒寫,也沒任何紀錄。
file: `mods/claude/lumos-ledger/hooks/register.ts:writeSession`
修法方向:取走前對沒有判定的 cwd 補查,或「沒有判定就視為 temp」。

### F2 一個判不了的 cwd 會卡住整個會談後面的事件,會談結束時最多丟 500 筆且不留痕
severity: minor
blocking: 否 — 這是作者新增測試明確採用的取捨,觸發需要某個 cwd 的 git 長期失敗,只影響觀測完整度。
引句:「let end = b.items.findIndex((it, i) => i < n && vs.get(it.cwd)?.kind === 'temp')」
說明:
- 舊版以 cwd 為鍵,一個卡住的 cwd 只拖自己;現在以會談為鍵,第一筆 temp 之後的所有事件(包括回到主 repo 的)都排在它後面。
- 例如 Bash `cd` 進一個 dubious ownership 的目錄:該 cwd 永遠 temp(每 5 分鐘重試仍失敗),主 repo 的後續事件全部堵住。
- 堵到緩衝滿 500 才靠丟最舊的解開。
- `session.end` 走 cachedOnly,堵住的事件全部放棄,既不寫也不記 ledger_error,`dropped` 也不增加。
建議:會談結束時放棄的筆數至少記一筆 ledger_error;或讓 temp 的那一筆有逾時後視為 skip。

### F3 ⚠ 連結檢查把懸空連結當成「不是連結」,葉節點 .gitignore 也沒檢查
severity: minor
blocking: 否 — 已實測目錄層的懸空連結沒有寫出 repo 外(引擎的 $.fs.write 建目錄時失敗),葉節點只是理論路徑,寫入內容固定為 `*\n`。
引句:「if ((await io.stat(p))?.isLink) return false」
說明:
- 引擎 `$.fs.stat` 對懸空連結會 reject ENOENT,`makeIo.stat` 把 reject 一律轉成 null,所以 pathSafe 把懸空連結當成「不是連結」。
- 讀取端 `_events_path_safe` 用 `is_symlink()`,懸空連結也算連結,兩邊規則不一致。
- rules-fixture 沒有懸空連結案例,守衛抓不到這個差異。
- pathSafe 只走到 `events/<session>`,不含 `.gitignore` 這個葉節點。
- 若 `events/.gitignore` 是懸空連結:`exists` 回 false、`io.write` 順著連結建立目標檔。⚠ 這條我沒實跑驗證。
file: `scripts/lumos:23715`(`_events_path_safe`)
修法方向:改用 `list(parent)` 的 `isLink`(不跟連結),並在 fixture 加懸空連結案例。

### F4 補丁新增的狀態收尾不完整(連結分支吃掉表頭、floors 不清)
severity: minor
blocking: 否 — 只影響除錯訊息與少量記憶體,不改寫任何事件。
引句:「if (!(await pathSafe(s.v.main, session))) continue // 上層是連結:不寫(讀取端也不會讀)」
說明:
- 這個 `continue` 發生在 `b.err`、`b.lost`、`b.dropped` 已清空之後。
  - 先前累積的 ledger_error 表頭與丟失筆數就此消失。
  - 這段事件本身也沒計入 lost。
  - 重現:加 `failWrites:1` 與 governance 連結,結果 writes=0、pending=0,沒有任何痕跡。
- `floors`(`Map`)只增不減,`drop(session)` 沒清它。長跑行程每個會談留一筆。

### 前輪修復驗收
- ① Bash cd 把事件拆成亂序兩塊:已修。
  - 緩衝以會談為鍵、每筆帶自己的 cwd,寫入時照到達順序合段。
  - 實跑場 3 的 turn_start、tool、tool、turn_end 順序正確。
  - 代價是 F2 的隊頭阻塞,與 F1 在溢位時的丟筆。
- ② governance 是符號連結寫到 repo 外:已修(存在的連結)。
  - 單元測試四層都過;實跑場 1、2 的懸空連結也沒寫出 repo 外。
  - 有缺口:F3。TS 端與 Python 的 `is_symlink` 規則不一致,葉節點 .gitignore 沒查。
- ③ 三條規則共用 fixture:已修,且我確認不是形式上的。
  - 兩邊都實跑全過。
  - vault 的連結案例確實讓 TS 的 `stat` 路徑與 Python `is_dir` 一致。
  - 會談編號案例涵蓋 `x\n`、`été`。
  - 主 checkout 案例涵蓋 `/srv/bare.git`。
  - 缺懸空連結案例(F3)。
  - Python 端 `_events_root` 只吃 common-dir、TS 吃 top+common,fixture 的 top 欄位在 Python 端沒有對應檢查,等價性靠 root=top 的巧合成立。⚠ 目前沒造成差異。
- 寫失敗記丟了幾筆:已修。`lost` 累計、第一個原因保留,測試過。連結分支吃掉它是 F4。
- 工具被中斷也記:已修(程式面)。catch 後記 `interrupted` 再 rethrow。
  - ⚠ 引擎被中斷時 `next(e)` 是 throw 還是回傳 isError,我沒實測;回傳 isError 的路徑原本就會記(ok=false)。
- 收事件不等寫入佇列:已修。`add` 回 void,`record` 不再 await;turn.complete 的 flush 用 void。實跑結束前事件照寫完。
- 子代理回合用 turn_id:已修。型別檔 `TurnCompleteFields` 有 `turnId`,讀取端沒有讀 `turn` 欄位的消費者。
- 新實例讀既有塊名當下限:已修。`loadFloor` 加 `floors`,重載測試過,檔名 13 位數與讀取端排序一致。
- 另外確認 t_ledger_plugin_files_valid 對新字串(`const dir = ${s.v.main}...`、pathSafe 那行)的斷言與程式一致,已過。

總結:最嚴重 minor,blocking 0 條
