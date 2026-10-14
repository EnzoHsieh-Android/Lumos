severity: minor

我在拷貝出來的工作樹實跑 `prepush_interrupt` 子集(清過 `__pycache__`,30 條全綠),並對掛鉤做了三個破壞實驗。原工作樹沒動,實驗目錄已刪。

severity: minor
blocking: 否 — 只是漏網的寫法與少測一個真實情境,現有五處都已包好,不會造成錯誤放行
引句:「re.search(r"[^&0-9]>>? *\"[^\"]*\" 2>/dev/null", ln)」
問題:全檔掃描守衛只認「`> "引號路徑" 2>/dev/null` 同一行、恰好一個空格」。我用同一條正則直接驗過,下面這幾種都抓不到:
- 路徑沒加引號:`>> $_f 2>/dev/null`
- 兩個空格:`"$_f"  2>/dev/null`
- 把 `2>/dev/null` 換行寫在續行 `\` 之後(`impact_once` 原本就是這種多行寫法)

另一個方向會誤擋:行尾註解裡帶這串字,例如 `cmd # a > "x" 2>/dev/null`,現在會被判成沒包組。

失敗情境:日後有人在掛鉤新增 `printf ... >> $_f 2>/dev/null`,守衛照綠,暫存目錄被刪時又漏出「No such file or directory」。另外 `>"$_AUTOLOOP_LOG" 2>&1` 與 `> "$_sdir/…log" 2>&1 &` 這三處開檔失敗的雜訊也不在守衛範圍內。它們不屬於「丟掉 stderr」那一族,只算提醒。
佐證:``scripts/test_lumos.py: `t_prepush_touched_file_write_fails_quietly` 內 loose 那段` ``;``scripts/hooks/pre-push: `735、818、822 行` ``

severity: minor
blocking: 否 — 多餘的陷阱不會讓行為出錯,只是少了一道測試守護
引句:「trap '_pp_kill_jobs; exit 129' HUP」
問題:我把子殼(`run_group`)裡的 HUP 陷阱拿掉,30 條仍全綠。原因是 ⑨ 只對掛鉤本身送 HUP,掛鉤再用 `jobs -p` 對子殼送 TERM,由子殼的 TERM 陷阱收片。子殼的 HUP 陷阱只有在子殼自己直接收到 HUP 時才有用,例如終端機關掉時整個行程群組一起收到 HUP,這個情境沒有測。
- 把子殼的 TERM 陷阱改成只 `exit 143`,⑥⑦⑨ 全紅。
- 拿掉主殼的 HUP 陷阱,⑨ 紅。
- 這三者的測試都真的測到行為,只有子殼的 HUP 沒有。

失敗情境:日後有人把子殼的 HUP 陷阱「清掉」,沒有任何測試會紅。實際風險很低,因為各片本來也會直接收到群組的 HUP。
佐證:``scripts/hooks/pre-push: `run_group` 內 trap 那兩行` ``

已讀,無 finding:
- **pid 判法**:假全套先寫 `SUITE-PID` 再送訊號。如果它沒寫成,`pid is not None` 會讓檢查變紅,不會假綠。孤兒睡 30 秒、測試只等 10 秒,收尾 `finally` 會 SIGKILL 殘留的孤兒。pid 在 10 秒內被重用,理論上會假紅,不會假綠,可忽略。
- **`_alive` 與殭屍行程**:對殭屍行程 `kill(pid, 0)` 仍會成功,但被收掉的片會被 init 回收,實測沒有卡住。
- **reason_kind 守衛 `_cl_reason_kind_sites`**:涵蓋 dict 字面、關鍵字參數與下標指派,承接者只准 `_CodeloopKg.hit` 與 `_codeloop_kg_finish` 各一處。目前 `scripts/lumos` 裡設定 reason_kind 的點都在這個範圍內。已知漏洞是 `setdefault`、`AugAssign` 與用變數當鍵名,現有程式碼沒有這種寫法。
- **S13 的 `guarded`**:`if x: return x` 的判斷方式正確。`if not x:` 與帶額外語句的寫法會誤紅,保守方向,可接受。
- **移除 `summary` 欄位**:確認沒有其他讀取點。

最高等級 minor,blocking 0 條。
