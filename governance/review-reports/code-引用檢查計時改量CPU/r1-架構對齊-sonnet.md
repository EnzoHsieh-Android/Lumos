severity: clean

我讀了 diff 全文,再對照測試總檔和鄰居筆記。沒有找到不一致的地方。

**1. 分層與依賴方向:對齊**
- 改動只在測試函式本身。它沿用原本的 `_rp_repo()` 和 `_rp_refcheck(root, md)`,後者是用 `subprocess` 開子程序跑 `GRAPHCTL refcheck`。依賴方向沒變。對照:`scripts/test_lumos.py:111976`。
- 函式內才 `import resource as _rs`、帶底線別名,和鄰居一樣(例如 `import time as _t`)。對照:`scripts/test_lumos.py:112463`。
- 測試總檔裡已有 `resource.getrusage` 的用法,但只用 `RUSAGE_SELF` 量記憶體(`scripts/test_lumos.py:110178`、`scripts/test_lumos.py:110572`)。這支量的是被測的子程序,所以改用 `RUSAGE_CHILDREN` 有理由,沒有跨層或另開一層。
- 圖譜端把 PITFALL 和 REVISIT 加在 `Systems/lumos-refcheck` 的摘要裡。refcheck 的測試本來就掛在這篇,所以放對了家。

**2. 命名與錯誤處理:對齊**
- 變數 `r0`、`r1`、`dt` 和檢查的訊息格式 `f"{dt:.2f}s"` 都延續原測試。
- 其他量 CPU 的測試也寫明「量的是 CPU 時間」,例如 `scripts/test_lumos.py:68759`、`scripts/test_lumos.py:68771`、`scripts/test_lumos.py:124350`。這份 docstring 同樣把量法和原因(2026-11-08 的 CI 事故)寫進去。
- PITFALL 帶 `[出處:]`、`[根因:]`、`[修法:]`、`[test:]`,符合專案規定的必填鍵。縮排和前後的 WHY 行相同。
- REVISIT 行用 `REVISIT:YYYY-MM-DD 一句要做什麼`,和 `Systems/測試執行器.md:25` 等現有寫法一致。
- 斷言訊息從「4 秒內跑完」改成「子程序 CPU 時間 4 秒內」,把量法寫進訊息,和鄰居「CPU 時間(5 次取最小)」的做法相符。

**3. 第二種做法:沒有另寫一套**
- 專案裡沒有共用的量子程序 CPU 時間 helper。我搜了 `scripts/test_lumos.py`,沒有 `def _cpu*`、`_timed`,也沒有其他 `RUSAGE_CHILDREN` 的用法。
- 現有的 CPU 量法是同程序內的 `time.process_time()`:一種是 `_best`(`scripts/test_lumos.py:124349`,5 次取最小),另一種是手算前後相減(`scripts/test_lumos.py:68767`)。它們量不到子程序,所以這份 diff 沒有和它們重複。
- 這份 diff 沒有重做 5 次取最小,而是保留絕對門檻 4 秒。這是量法取捨,不算另一套 helper。
- 圖譜裡的 `[同族:]` 一句,等於承認測試總檔另有約 120 處牆鐘門檻沒改,並用 REVISIT 排了回頭條件,是明講的現況。我判斷這不構成「第二種做法」。

diff 其餘部分是 `governance/anchor-baseline.json` 的簽核更新,屬流程性檔案,不在這三問範圍內。

不對齊共 0 條,其中 major 0 條

我沒有在 `/tmp/lumos-seat-work/code-引用檢查計時改量CPU/架構對齊-sonnet/` 底下建任何東西。
