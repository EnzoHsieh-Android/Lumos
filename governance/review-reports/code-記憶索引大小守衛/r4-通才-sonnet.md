severity: clean

已看,無:這輪修正(在 `index_size_note` 呼叫 `_index_bytes(...)` 的地方外面包一層 `try/except OSError: got = None`)對不對、夠不夠都實際驗過:

1. **對照 `main()` 的呼叫順序**確認了 r3 抓到的問題是真的——`size_note = index_size_note(here)` 排在 `sweep(...)`/`cross_check(...)` 之後、`_emit(...)` 之前,而檔案最外層只有一個 `try: ... except Exception: sys.exit(0)`(fail-open)包住整個 `main()`。所以只要 `index_size_note` 往外拋,`_emit` 就不會被呼叫,同一次開場算出來的 `tally.changed`/`crossed` 會被整個吞掉、什麼都不印——跟 r3 描述的症狀吻合。

2. **翻紅釘實跑**:把 worktree 複製到 `/private/tmp/.../exp-r4` 套上這份 patch,先跑一次全綠(9 passed)。接著只拆掉這輪加的攔截(把 `index_size_note` 改回直接呼叫 `_index_bytes(...)` 不包 try/except),重跑同一支測試:第 ⑨ 條照預期翻紅(`拋出:[Errno 5] 模擬讀取錯誤`),其餘 8 條仍綠——證明新加的攔截跟新增的 ⑨ 號斷言是綁在一起的,不是空測試。之後已還原成套 patch 的狀態(`git checkout -- .` 後重新 apply)。

3. **檢查還有沒有別的例外型別或別的路徑會從 `index_size_note` 漏出去**:通讀 `_index_bytes`——`os.lstat`/`os.open`/`os.fstat`/`os.fdopen`/`fh.read`/`os.close` 全部只可能拋 `OSError`(讀取量被 `MAX_BYTES+1`=64KB+1 卡住,不會因為讀太大檔案冒 `MemoryError`);`_pre_reason`/`_opened_reason` 是純邏輯判斷,不做 I/O,不會拋例外。`index_size_note` 本身在拿到 `got` 之後的格式化(`raw.count(b"\n")`、字串組訊息)全部作用在已經驗證過的 `bytes` 上,沒有 decode 動作,不會有 `UnicodeDecodeError`(跟本檔別的地方讀記憶檔要 `.decode("utf-8")` 不同)。目前沒有找到還會漏出去的例外型別或路徑。

4. **測試裡 `_ms.os.fstat = _boom` 會不會汙染同一個行程裡的其他測試**:實測過——`_ms` 是用 `importlib` 在同一個 Python 行程裡直接載入 hook 模組(不是子行程),而 `_ms.os` 跟 `test_lumos.py` 自己 `import os` 拿到的是 `sys.modules['os']` 同一個物件,所以 patch 期間 `os.fstat` 是整個行程共用被換掉的(用一小段腳本驗證過 `ms.os is os` 為 True、patch 期間 `os.fstat is boom` 也為 True)。不過:
   - 換掉到還原之間只夾了一次同步的 `_ms.index_size_note(str(d9))` 呼叫,中間沒有任何 subprocess/thread 會在這個窗口用到 `os.fstat`;
   - `finally: _ms.os.fstat = _orig` 確實會還原(同一段驗證腳本印出 `restored: True`);
   - 跑了 `python3 scripts/test_lumos.py -k memory_sweep`(整組 75 支相關案例,含 ⑨ 前後的其他 memory-sweep 測試)全綠,沒有觀察到污染;
   - 本專案測試跑法是單一行程依序 `for t in tests:` 執行(沒有 threading/ThreadPoolExecutor 跑測試),所以目前安全。這是個偏 fragile 的手法(直接改全域 singleton),但沒有證據顯示現在會出事,不到開 blocking 條目的地步,寫在這裡留記錄。

5. **`_opened_reason(st, pre, max_bytes=None)` 共用讀記憶檔那支判斷**:確認 `max_bytes=None` 只關掉大小那條判斷,換檔/目錄/非一般檔/硬連結判斷仍然生效(對應測試 ⑤⑦ 綠燈),沒有因為新增這個參數而放寬別的檢查。

沒有發現需要另開的 blocker/major/minor 條目。
