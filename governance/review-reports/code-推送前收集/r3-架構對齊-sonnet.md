severity: clean

本輪修補沒有引入第二種做法,也沒有跨層直呼,所以沒有 finding。四個指定檢查點的結果如下。

**1. 子殼收子行程的寫法**
- 全檔收子行程的 kill 只剩 `_pp_kill_jobs` 一支,`scripts/hooks/pre-push:303` 定義。INT、TERM、HUP 的 trap(305–309 行)和子殼 `run_group` 的 TERM、HUP trap(814–815 行)都呼叫它。
- 全檔已沒有直接對 pid 清單下 kill 的寫法。
- `_pids` 還留著,只用來 `wait` 收離開碼(`scripts/hooks/pre-push:828`),跟收子行程是兩件事,不算第二套。
- 對照:`scripts/hooks/pre-push:303`(`_pp_kill_jobs`)。

**2. 包組重導向是否全檔一致**
- 「寫檔加 `2>/dev/null`」的站點都已包成 `{ …; } 2>/dev/null`:`pp_record_block` 的 107 行、`pp_touched_file` 的 160 和 170 行、`impact_once` 的 282 行、合併測試 log 的 856 行,另有 700 行本來就是包組。
- 735、818、822 行的 `> log 2>&1` 沒包組,但它們不是要吞掉開檔雜訊,而是把 stderr 併進 log,性質不同,不算漏網。
- 對照:`scripts/hooks/pre-push:107`。

**3. 原因對照表只剩掛鉤一份**
- 對照表現在只有掛鉤的 `pp_cl_reason` 一份,`scripts/lumos` 裡的 `_CODELOOP_BLOCK_KIND_REASONS` 和 `_CODELOOP_BLOCK_KIND_FALLBACK` 已刪。
- 全 repo 搜不到殘留引用,JSON `blocks` 的 `summary` 欄位也沒有讀者(這個欄位是這次修補一起刪掉的)。
- 掛鉤是獨立檔,要能配舊版 lumos 跑,所以不向 lumos 要表。
- 現在掛鉤對照表是正本,`scripts/test_lumos.py:64612` 的 `_PPC_KIND_SENTENCES` 當期望值。這跟專案既有的「獨立檔各留一份,加逐字漂移守衛」慣例同族,例如 `scripts/test_lumos.py:17472` 和 `:17968`。
- 這次還少了 lumos 端那份複本,比既有慣例更單一,沒有走出慣例。
- 對照:`scripts/hooks/pre-push:140`(`pp_cl_reason`)、`scripts/test_lumos.py:64612`。

**4. reason_kind 字面守衛的寫法**
- 守衛 `_cl_reason_kind_sites`(`scripts/test_lumos.py:65217`)用 `ast.parse` 加遞迴走訪原始碼,不是 regex。
- 專案裡 `ast.walk` 掃原始碼當守衛的做法已有先例,例如 `scripts/test_lumos.py:12197`、`:6901`,所以是同一種寫法。
- 例外白名單 `_CL_REASON_KIND_CARRIERS`(`scripts/test_lumos.py:65214`)按「函式名加次數」限制轉手處,這是既有守衛常見的白名單形狀。
- 對照:`scripts/test_lumos.py:12197`(`ast.walk`)。

最高等級 clean,blocking 0 條。
