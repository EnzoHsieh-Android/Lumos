severity: minor

審查範圍是 `r2-repair.patch` 對 `scripts/lumos` 的改動(修前 a95e650 到修後 c4ed34e)。能當場翻紅的 major 沒找到。同一個修補裡的測試改動只讀了 diff,沒有逐 hunk 比對。

## 對應修補鏡頭的三問

### 問 1:原問題的修復效果
- **claim:** `_KillMerge.off` 與 `plats` 兩份記帳改成單一來源,run 事件的 `merge_off` 由 `plats` 算出。
- **證據(讀碼):**
  - 先在 repo 全文搜 `.plats`、`mg.off`、`_KillMerge(`、`"條件不合"`、`"基準"`,`scripts/lumos` 內沒有讀舊 `plats` 文字或 `mg.off` 的殘留。
  - `_choice_kill_report` 的新推導式 `{q: why for q,(on,why) in plats.items() if not on and why != "斷路器"}` 與寫入處對得上。
  - `_kill_merge_off` 每次都寫 `mg.plats[plat]=(False, why)`。
  - 斷路器那處寫 `(False,"斷路器")` 並設 `tripped`,被排除。
  - `quiet=True` 只用在基準不乾淨與中斷兩處,這兩處本來就不該重複印。
- **before / after:** 修前 `mg.off` 與 `plats` 各存一份,`_kill_merge_iter` 還會用 `"條件不合"` 或 `"基準"` 覆蓋 `plats`,現在不再覆蓋。
- **test 狀態:** 本席跑 `python3.14 scripts/test_lumos.py -k t_choice_kill_merge`,結果 203 passed、0 failed。這只表示修補後這批測試是綠的,沒有修前對照,不代表問題已解決。`t_choice_kill_merge_failed_first` 跑了 72 秒,離逾時上限 180 秒只剩 2 倍餘裕,測試輸出標了「⚠ 餘裕不足 3 倍」。
- **新增案例:** 修補新增的 r1 c1 案例(中斷時 `merge_off == {"kotlin-junit": "中斷"}` 且不印「這次不合併(中斷)」)只讀了 diff。

### 問 2:修補處的正常、錯誤與相鄰呼叫路徑是否仍成立
- **`n_mutants` 拿掉:** 唯一的建構處(`scripts/lumos:79077`)與測試端建構處都已改成不傳,沒有漏改的呼叫者。
- **`_single` 改 `_ran_solo`:**
  - `cmd_guard_kill` 的 `--json` 過濾清單同步改了。
  - `on_row` 與 `_choice_kill_report` 端同步改了。
  - 逐筆記帳的 `_kill_log_rows` 是明列欄位,不會帶出底線鍵。
  - 所以 `--json` 純度這條 ★INVARIANT★ 在讀碼層面仍成立。
- **新增的「合併道不足 2 支」判斷:**
  - 它在時限門之前,所以單一測試的平台不會再被提示去調大 `--max-seconds`。
  - 副作用:只綁 1 支測試的平台現在每次都印 `⚠ …這次不合併(合併道不足 2 支)` 並記 `merge_off`,屬計劃內行為,不是錯。
- **`merge_need` 改成全部支數:** `c.merge_need` 現在是 `(len(uniq), avg*len(uniq)*K)`。時限提示的 X 會把已量基準的秒數算兩次(已花 + 全部估計),建議值偏保守,不會偏低,不構成錯誤。

### 問 3:新發現案例的修前修後
沒有新發現的案例需要比對。下面兩條都是 minor,沒做修前修後實跑。

## Finding

severity: minor
blocking: 否(沒有行為出錯,只是 `merge_off` 靠字串約定,屬維護風險)
- 位置:`scripts/lumos:79111` 與 `scripts/lumos:29094`。
- 描述:`merge_off` 的推導式用 `why != "斷路器"` 排除斷路器,字串散在兩處,中間沒有常數或測試連結。
- 失敗情境:有人把斷路器的原因字串改名時,`merge_off` 會多出斷路器,而且測試不一定抓得到。
- 歸因:未判定。這是修補新引入的結構,但還沒有人去改它。
引句:「merge_off={q: why for q, (on, why) in (getattr(mg, "plats", None) or {}).items() if not on and why != "斷路器"})」

severity: minor
blocking: 否(只影響文件,不影響行為)
- 位置:`scripts/lumos:28340` 附近 `cmd_guard_kill` 的 docstring。
- 描述:`on_row` 的欄位清單沒列新加的 `ran_solo`。
- 歸因:修補新增的文件漏補。
引句:「"fail_excerpt": str(res.get("fail_excerpt") or ""), "ran_solo": bool(res.get("_ran_solo"))})」

## 圖譜鏡頭
這次沒有附固定席節點(鏡頭計算超時),派工詞說不用自己補算,所以沒逐條判。我只對照讀了 `Systems/guard-kill` 兩條 ★INVARIANT★ 的程式端:rc 優先序沒被動到,`--json` 過濾清單與鍵改名同步。

## 未驗範圍
- 沒對修前版本實跑。
- 沒做變異檢驗(例如把 `quiet` 拿掉看哪支測試紅)。
- 沒對 `len(uniq)<2` 的邊界(測試名重複)做實驗。

總結:最高嚴重度 minor,blocking 0 條。
