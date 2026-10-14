severity: clean

我讀了修補差異,也對照了掛鉤原檔與 scripts/lumos 的既有寫法。三個你特別點名的地方,都沒有引入第二種做法或跨層直呼,所以沒有 finding。

**1. 內嵌 Python 換群組,跟掛鉤既有呼叫 Python 的方式一致**
- 掛鉤原本就有同形狀的寫法:`"$PY" -c '…'`,用同一個 `$PY` 跑一行 Python。
  對照:file: `scripts/hooks/pre-push:547`。
- 新寫法同樣用 `"$PY" -c`,沒有另找 `python3` 或其他直譯器。
- 差別只有一個:把程式碼放進變數 `_PP_OWN_PGRP`,因為兩處呼叫都要用。這是同一種做法的複用,不算第二種。
- 在 bash 掛鉤裡做行程群組切換,而不是呼叫 `$GRAPHCTL`,也是合理的:這件事發生在掛鉤自己起背景工作的當下,不是 lumos 的職責。
- 專案其他地方換群組的做法是 Python 的 `start_new_session=True` 加 `os.killpg`。
  對照:file: `scripts/lumos:18247`、file: `scripts/lumos:29328`。
- 掛鉤是 bash,不能用 Popen 參數,所以改用 `os.setpgid` 加 `execv`。語言層不同,「自成群組、整組收」的概念相同。

**2. `_pp_kill_jobs` 仍是收子行程的唯一一套**
- 我 grep 掛鉤,`kill` 只出現在 `_pp_kill_jobs` 裡(306–310 行)。
- 主陷阱(INT、TERM、HUP)和 `run_group` 子殼的 TERM、HUP 陷阱,呼叫的都是這一支。
- 這次只改了它的內部(改成整組送 TERM、失敗再退回送本人),沒有另外長出一套「記 pid 去收」。這也守住了 r2 架構席立的規矩。

**3. 守衛掃描器**
- 這份修補差異和完整掛鉤差異只含 `scripts/hooks/pre-push`,沒有新增掃描器程式碼,所以沒有對照對象。
- 我沒有檢查 `test_lumos.py` 裡的測試與既有 bash 原始碼掃描守衛的寫法是否一致。

**一個不算 finding 的觀察**
- `os.execv(sys.argv[1], …)` 不會去 PATH 找程式。這要求 `$PY` 是可直接執行的路徑。
- `$PY` 來自 lumos 回傳的結果(`LUMOS_PY`,見 `scripts/hooks/pre-push:243` 一帶)。我沒有證實它一定是絕對路徑。
- 若有人把它改成裸指令名,這一行會壞。目前這是行為風險,不是寫法分歧,我就不列。

最高等級 clean,blocking 0 條。
