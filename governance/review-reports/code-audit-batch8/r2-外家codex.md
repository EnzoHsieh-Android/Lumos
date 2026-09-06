severity: blocker
- [blocker] 過期鎖沒有被原子接管；300 秒後所有並行呼叫者都會各自派工，且舊 worker 可能刪掉新 worker 的鎖
  引句:「已經有人在算:看它是不是還活著(鎖檔太舊就當它死了,自己接手)」
  位置:governance/review-reports/code-audit-batch8/r2-snapshot.patch:659
  blocking:是
  why:輸入＝預先留下 mtime 超過 300 秒的 `.warming`，再讓兩個呼叫者同時進入。預期＝只有一個呼叫者以 O_EXCL 原子取得新鎖並派工。實際＝兩者的首次 O_EXCL 都遇到既存鎖，皆把 `already` 設為 false；程式既未 unlink 舊鎖、未重新 O_EXCL，也未驗 PID，兩者都走到 Popen。更糟的是任一 worker 完成後無條件 unlink 同一路徑，可能刪掉另一支仍在運算時所依賴的鎖。行程遭 SIGKILL 確實會留下孤兒鎖；300 秒也不是可靠死亡判準，patch 自述 120 commits 已需 137 秒，更大範圍可能合法超過 300 秒。鎖內寫的還是父行程 PID，並非背景 worker PID，無法據此驗活。

- [major] deadline 的 3 秒下限會在剩餘預算不足時重新造成內層大於外層
  引句:「argv = argv + ([\"--deadline\", f\"{max(3.0, _lens_timeout()):.2f}\"] if rng else [])」
  位置:governance/review-reports/code-audit-batch8/r2-snapshot.patch:424
  blocking:否
  why:輸入＝hook 已耗到 `_lens_timeout()` 只剩 1 秒。預期＝內層 deadline 必須小於剩餘外層天花板。實際＝傳給 lumos 的 deadline 被抬成 3 秒，subprocess timeout 又取重新計算的剩餘值加 5 秒；外層可能先殺 hook，使 rc5 與超時說明都來不及產生。40 秒天花板只改善一般案例，沒有維持程式宣稱的結構性保證。

- [major] 真實超時測試在快機器上直接 skip，因而沒有驗證本次新增的核心行為
  引句:「這台算得比 1.5 秒還快 → 測不到超時那條路,誠實跳過而不是假裝驗過」
  位置:governance/review-reports/code-audit-batch8/r2-snapshot.patch:997
  blocking:否
  why:輸入＝HEAD~12 範圍在 1.5 秒內完成。預期＝測試仍應以可控慢點穩定走 rc5、鎖存在、背景寫快取及清鎖等分支。實際＝收到 rc0 就拋 `_SrcOnly`，整組核心斷言全部跳過；條件本身能正確辨認「沒走超時」，但測試品質仍取決於機器速度與 repo 歷史。它也未覆蓋孤兒鎖、過期接管或兩個並行呼叫者。

- [minor] rc5 的非 JSON 模式只輸出空白行，人工呼叫無法由輸出辨識「仍在背景運算」
  引句:「print(_j2.dumps({\"timed_out\": True, \"still_warming\": True, \"range\": diff_range},」
  位置:governance/review-reports/code-audit-batch8/r2-snapshot.patch:697
  blocking:否
  why:輸入＝不帶 `--json`、帶 `--deadline` 並逾時。預期＝與 JSON 模式同樣提供可理解的狀態訊息。實際＝條件運算式在非 JSON 模式選擇空字串，只印換行並回 rc5。hook 使用 JSON，主要自動路徑可運作；但 CLI help 對一般呼叫者也公開了此選項。rc5 雖與其他子命令的命令內回傳值重複，未發現全域衝突；現有 dispatch-lens hook 已辨識 rc5，其他既有呼叫端沒有把 deadline 納入其成功協定。

- [clean] 快取路徑與鎖路徑使用同一個 `cpath` 基底，沒有重犯第一版的 `with_suffix` 配錯
  引句:「鎖檔名要跟快取同基底再加後綴——用 with_suffix 會把 .json 換掉」
  位置:governance/review-reports/code-audit-batch8/r2-snapshot.patch:649
  blocking:否
  why:核對建鎖、父行程輪詢、背景算完清鎖及測試端定位，全部使用 `cpath.with_name(cpath.name + ".warming")`；父行程等待的快取也是同一 `_lens_cache_path(root, base_sha, head_sha)`。

- [clean] 背景行程輸出已丟 DEVNULL，子行程監督也已移回 lumos，第一輪兩項 blocking 的直接原因已消除
  引句:「kw = {\"stdout\": _sp.DEVNULL, \"stderr\": _sp.DEVNULL, \"stdin\": _sp.DEVNULL}」
  位置:governance/review-reports/code-audit-batch8/r2-snapshot.patch:670
  blocking:否
  why:核對 hook 只用 `subprocess.run` 呼叫 lumos 並處理 rc5；Popen、start_new_session、輪詢與鎖均位於 `scripts/lumos`。背景 stdout/stderr/stdin 都不接無人讀取的 PIPE，不會重現輸出塞滿而卡死。

- [clean] `LUMOS_LENS_WARMING` 能阻止背景 lumos 再派背景行程，且不會改變目前所呼叫的 git 等非 lumos 子行程行為
  引句:「背景那支自己不准再派人★:它帶著 LUMOS_LENS_WARMING 進來,直接算、算完寫快取」
  位置:governance/review-reports/code-audit-batch8/r2-snapshot.patch:823
  blocking:否
  why:背景行程取得該環境變數後，dispatch 層把 deadline 清成 None，直接計算並寫與父行程相同的快取。環境確會照常繼承給它啟動的子行程，但凍結快照中只有 lumos 的 dispatch-lens 分派讀取此變數；未發現 git/其他子行程因此改變行為。

- [clean] 關快取分支同時涵蓋命令列與環境變數兩種停用方式，會直接計算而不進入等待快取的路徑
  引句:「if deadline and deadline > 0 and not (no_cache or os.environ.get(\"LUMOS_DISPATCH_LENS_NO_CACHE\")):」
  位置:governance/review-reports/code-audit-batch8/r2-snapshot.patch:749
  blocking:否
  why:核對讀快取、deadline 分流及寫快取三處使用相同的 `no_cache or LUMOS_DISPATCH_LENS_NO_CACHE` 判準；未找到「跳過讀取但仍等待快取」的第三種狀態。

- [clean] `_BUDGET_START` 在單次 hook 行程內能反映累計耗時；不同模組載入實例不共享此狀態
  引句:「如果 _BUDGET_START 是 None: _BUDGET_START = _tm.monotonic()」
  位置:governance/review-reports/code-audit-batch8/r2-snapshot.patch:100
  blocking:否
  why:同一模組實例第二次呼叫會沿用首次時間，符合「整支 hook 已耗」語意；以新 module object 載入則各有自己的全域值，不會跨模組污染。風險只在測試於同一 module instance 多次模擬獨立 hook invocation 時需顯式重設，但現有預算測試多使用 `elapsed` 明確控制，未看到因此假綠或假紅的直接證據。
