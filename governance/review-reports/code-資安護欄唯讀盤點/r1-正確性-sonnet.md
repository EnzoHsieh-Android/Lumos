severity: major

這次改動的主流程(登記、證據、覆蓋、退出碼、讀取邊界)走得通,但有兩類輸入會讓指令當掉。當掉時印 traceback、退出碼 1,JSON 模式沒有輸出。這違反 CLI 契約(退出 0 或 2、stdout 恆為單一 JSON)。

驗證方式:用 `/tmp/lumos-seat-work/code-資安護欄唯讀盤點/正確性-sonnet/v` 這個臨時圖譜,跑 `python3.14 scripts/lumos --vault … security list`。

**1.「不可雜湊的值」讓 schema 檢查變成 TypeError,而不是記成 invalid_record / inventory_error**

severity: major
blocking: 是

位置在 r1-lumos.patch 的三處(patch 行 559、836、841)。登記塊裡的欄位型別錯了,本來應該列錯誤、退出 2。實際上程式在檢查前就拿它去當 dict 鍵或 set 元素,直接丟例外。

- `_sc_source`:`source.kind` 不是字串,是陣列或物件。
  - 輸入:`{"schema_version":1,"controls":[{"id":"a","source":{"kind":[]}}]}`
  - 預期:一條 invalid_record,退出 2。
  - 實際:`TypeError: cannot use 'list' as a dict key`,退出 1。`kind` 給 `{}` 同樣當掉。
- `_secinv_inventory_problems` 的 assets:資產 `id` 不是字串(例如 `[]`)。
  - `_secinv_inv_items` 發現後記了問題,卻仍執行 `ids.append(it.get("id"))`。接著 `set(...)` 對不可雜湊的值丟 TypeError。
  - 輸入:`"inventory":{…,"assets":[{"id":[],"description":"x"}],"surfaces":[]}`
  - 預期:inventory_error,退出 2。
  - 實際:`TypeError … as a set element`,退出 1。
- surfaces 的 `asset_ids`:元素不可雜湊。
  - `_secinv_str_list` 只記問題、不中止,後面的 `x not in aset` 就拿陣列去查 set。
  - 輸入:`"surfaces":[{"id":"S1","asset_ids":[["x"]],"description":"d"}]`
  - 預期:inventory_error,退出 2。
  - 實際:`TypeError … unhashable type: 'list'`,退出 1。

三處我都實跑重現。這三處都沒有測試。`t_seclist_s02` 只測了壞 JSON、重複鍵、未知版本、多餘欄位這幾種形狀,沒有型別錯的值。拿掉任何防護,測試都照綠。

修法方向:
- 驗型別的函式先確認是字串,再去查表。
- `_secinv_inv_items` 對非字串的 id 要 `continue`。
- `x not in aset` 前先確認 `isinstance(x, str)`。

引句:「"requirement": ("kind", "claim", "decision_ref")}.get(kind)」

**2. `--json` 輸出遇到孤立代理字元(lone surrogate)就當掉,文字模式卻正常**

severity: major
blocking: 是

位置在 `cmd_security_list`。登記塊的 JSON 字串允許 `\ud800` 這種跳脫,`json.loads` 會還原成孤立代理字元。`_secinv_is_text` 只判非空,所以 `scope` 之類的欄位會接受它。輸出時用 `ensure_ascii=False`,`sys.stdout.write` 會編碼失敗。

- 輸入一:一條其他欄位都合格的控制項,加上 `"scope":"\ud800"`,用 `--json` 跑。
  - 預期:單一 JSON 加退出 0 或 2。
  - 實際:`UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800'`,退出 1。
- 輸入二:頂層多一個鍵 `"\ud800":1`。
  - 錯誤訊息 `頂層有未列出的欄位 \ud800` 會帶進 errors,`--json` 一樣當掉。
  - 文字模式因為 `_kill_esc` 會跳脫,同一輸入正常輸出並退出 2。
- 這與契約「文字與 JSON 是同一份資料」相衝,兩個模式的退出碼也不一致(JSON 為 1,文字為 2)。
- 沒有測試覆蓋。`t_seclist_s07` 的控制字元案例沒有放孤立代理字元。
- 修法方向:JSON 輸出改用 `ensure_ascii=True`,或在進報告前把含代理字元的字串跳脫。

引句:「sys.stdout.write(_json.dumps(rep, ensure_ascii=False, indent=1) + "\n")」

**3. 圖譜固定席與「不影響」的核對(不是缺陷)**

severity: minor
blocking: 否

- `_visible_lines` 抽出 `_fence_regions` 後行為不變。我取出 `ec4c6307` 的舊版與新版,用 200000 組隨機行(包含各種圍欄、縮排、tab、帶語言標記的行)、`keep_fenced` 兩種值各比一次,輸出差異為 0。
- `_regular_own_fd` 新增 `dir_fd=None`。不給時走原本的 `os.open(str(path), flags, mode)`,既有呼叫端不受影響。
- 固定席逐條判斷:
  - lumos-cli-read 的 search 不排除 stale 合約:本次未動 search,不影響。
  - design-loop 處置閘第五步:未動。
  - lumos-cli-lifecycle 的 re-inject:未動。
  - guard-kill 的 rc 優先序與 JSON 純度:未動。
  - 測試假綠形態:該合約要求「還原翻紅釘」要配前置斷言。上面兩個缺陷若補測試,要照這條寫。
- 退出碼語意只有 0 和 2。除了第 1、2 條的當機路徑外,我走過的路徑都符合契約:
  - 零登記退出 0,且 `registration_complete=false`。
  - 過期例外只列問題,退出 0。
  - 例外的核可決策作廢,記錯誤,退出 2。
  - 重複 ID 與同來源雙 ID 都記錯誤。
  - 同來源寫成 `Systems/a` 與 `Systems/a.md` 會被合併成同一來源(實測)。
  - 雙關注面(business + security)只列一次。
  - 純業務撤除項留在 excluded_business。
- 對本 repo 真實圖譜(907 篇、11MB)跑 `--json`,約 0.7 秒,0 個錯誤。
- 效能提醒:2000 條控制項在一篇 1.25MB 的筆記裡約 3.7 秒,耗時隨控制項數線性增加,沒有爆量,不另立缺陷。

引句:「區段怎麼切只在 _fence_regions 一處(資安護欄唯讀盤點_計劃:專用登記要讀嚴格結果,不另寫第二套 toggle)。」

最嚴重 severity:major,blocking 共 2 條(第 1、2 條)。

臨時檔留在 `/tmp/lumos-seat-work/code-資安護欄唯讀盤點/正確性-sonnet/`(含 `v/`、`run.sh`、`fz.py`、`old_lumos.py`、`real.json`),請編排者收貨後刪除。
