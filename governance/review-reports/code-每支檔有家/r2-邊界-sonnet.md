severity: minor

### G1 config.json 符號連結防護只擋葉節點,`.lumos` 目錄本身是捷徑檔時仍讀到圖譜外部檔案
severity: minor
blocking: 否 — 唯一呼叫這條非快照讀取路徑的只有 `lumos doctor` 開頭那一行提示(僅供參考),不影響 `home check --staged`/`--diff` 的實際擋下判斷(那兩處都走 from_snapshot=True 讀提交索引)
引句:「捷徑檔不跟過去讀:跟讀快照那條路一樣(git 裡的捷徑檔讀出來是目標路徑字串,解析失敗退預設)——」
- file: `scripts/lumos:17722` `if p.is_symlink():` 只檢查路徑最後一段(`config.json` 本身),不檢查上層目錄(`.lumos`)是不是捷徑
- 實測重現:把 `.lumos` 整個目錄換成指向 repo 外部目錄的捷徑(外部目錄裡放一支真正的 `config.json`,內容 `node_home.gate=off`),呼叫 `_nodehome_config(root)` 回傳 `{'mode': 'off', ..., 'warnings': []}`——完全讀到外部檔案內容且不留警告,跟修法聲稱的「跟讀快照那條路一樣」不擋不一致
- file: `scripts/lumos:980` `_nh_mode = _nodehome_config(_vault_repo_root(env))["mode"]` 是這條非快照讀取路徑唯一的呼叫點,確認影響範圍僅止於 doctor 開頭那行提示,不是真正的擋

### G2 `--code`/`--responsibility` 寫回丟例外時,同一次失敗印兩行提醒(跟同段的 plan_refs/verified_by 回掛不一致)
severity: minor
blocking: 否 — 只是 stderr 訊息重複,不影響 rc 與節點內容(已實測仍是 rc2、之後項目照做完)
引句:「跟下面回掛那兩段同一套:被擋或寫入鎖逾時(丟例外)也要講「筆記建好了」、其餘項目照做完、最後彙總(代碼審 r1 架構席)」
- 實測重現:讓 `cmd_append(..., "about_code", ...)` 對第一支 `--code` 丟 `RuntimeError`,stderr 印出兩行——「提醒:筆記建好了,但 --code src/a.py 沒寫進 about_code: 第一支失敗」與「提醒:筆記建好了,但 --code src/a.py 沒寫進 about_code(上面有原因),照原因補:…」——因為 except 分支把 `_rc` 設成 2 後又掉進後面的 `if _rc != 0:` 區塊再印一次；同一段下面的 plan_refs/verified_by 迴圈(`rc_side |= cmd_append(...)`)例外時只印一行,兩段寫法不一致
- file: `scripts/lumos:12483` `if _rc != 0:` 在 except 分支已經印過訊息、把 `_rc` 設成 2 之後,還會再進這個區塊印第二行

### G3 `--diff ""`(顯式空字串)被當成「兩個旗標都沒給」,訊息講錯原因
severity: minor
blocking: 否 — rc 仍正確是 2,只是訊息文字對不上使用者實際做的事(明明給了 --diff)
引句:「擋下:lumos home check 要帶 --staged 或 --diff <起點>..<終點>」
- 實測重現:`lumos home check --diff "" --repo <root>` → rc=2,印「擋下:lumos home check 要帶 --staged 或 --diff <起點>..<終點>」——跟三個點、缺一端那幾種壞寫法印的「恰好兩個點、兩端都要有」訊息不同,因為 `args.hm_diff` 是空字串時 Python 真值判斷跟「完全沒給 --diff」無法區分,在真正呼叫 `_lens_range_ok` 之前就先被攔下
- file: `scripts/lumos:22771` `if not args.hm_staged and not args.hm_diff:` 用真值判斷,空字串跟 None 同樣視為「沒給」

## 第一輪修法驗收
F3:修到 — `--diff` 改用既有 `_lens_range_ok`(恰好兩個點、不收三個點),對 `HEAD~1...HEAD`、`HEAD~1..HEAD..HEAD`、`..HEAD`、`HEAD~1..` 等壞寫法逐一實測皆 rc2 且不放行,`-k nodehome` 155 項全過
F9:沒修到 — 只擋了「config.json 本身是捷徑檔」這一種,`.lumos` 目錄本身是捷徑檔的變體仍會讀到外部檔案(見 G1);新測試 `t_nodehome_config_disk_read_skips_symlink` 也只覆蓋前者,沒測到目錄層級
F10:修到 — `_lands_in_bad` 先驗寫法、`p.resolve().relative_to(vbase)` 完整解析符號連結鏈,實測連「整個 Systems 資料夾本身是捷徑檔」都正確判成「指到圖譜外面」而不讀,壞掉的捷徑檔與循環捷徑檔也不炸
F12:修到 — S8→S9→S10 之間補上空行,實測涵蓋無 git 專案(不是 git 專案分支)與截斷(＞_SOFT_CAP 非 verbose)兩種情境,空行都正確出現
F13:修到 — 「家太多」提醒已不再叫人查 `lands_in`,測試斷言 `"lands_in" not in out` 通過

總結:最高 severity minor,blocking 共 0 條
