severity: minor

## F1 `_index_bytes` 內部兩段錯誤處理各自一套,沒有跟同檔任一支既有慣例完全一致
severity: minor
blocking: no
引句:「fd = os.open(str(p), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))」
引句:「except OSError:                 # 讀到一半出錯(r3 major):只放棄這一句,不能連帶吞掉同一次開場的其他發現」

`_index_bytes` 前半(`os.lstat`、`os.open` 兩處)遇到 `OSError` 自己 `except OSError: return None` 吞掉,是就地回 None 的寫法,跟本檔 `node_status`(讀不到回 None,不往外拋)那套慣例一致;但後半(`os.fstat`、`with os.fdopen(...).read(...)`)完全沒包 try/except,讓例外往外拋,改由呼叫端 `index_size_note` 用外層 `except OSError:` 接住。

問題是本檔另一支「跟讀記憶檔同一套防護」的原型 `_read_own_file`,在對應的 lstat/open 兩處是**明確重丟**(`except OSError: raise`、`except OSError as e: ... raise e`),完全不吞,交給呼叫它的 `read_memories` 在迴圈裡逐檔接;`_index_bytes` 卻在同樣兩個位置改成吞掉不丟。也就是說 `_index_bytes` 對 lstat/open 抄的是「就地吞」慣例(像 `node_status`),對 fstat/read 抄的是「往外丟」慣例(像 `_read_own_file`),同一支函式內部混了兩套本來分屬不同呼叫模式(單值 vs 多檔迴圈)的既有寫法,而且註解說「跟讀記憶檔同一套防護」,但實際上跟 `_read_own_file` 在 lstat/open 這段的行為(重丟)是相反的。不影響結果正確性(測試⑨有驗到最終仍回 None),純粹是同一函式內兩段錯誤處理沒有統一抄同一支既有慣例,之後有人要照這支函式「範例」複製錯誤處理寫法時容易學錯半套。

已看,無:測試新增的 `import os` 重複匯入(原本模組層級應該已有 `os`,但這裡是 `ctx_for` 用的局部匯入,跟本檔其它測試函式內按需 `import os as _os` 的做法一致,不算問題)。`_opened_reason` 新增 `max_bytes=MAX_BYTES` 參數並在索引路徑傳 `max_bytes=None` 繞過單檔大小上限,是刻意的行為分歧(索引要真實大小、記憶檔讀取要截斷保護),有註解交代、也有測試⑥/⑦專門驗證,不是寫法不一致。`index_size_note` 外層 `except OSError:` 接住 `_index_bytes` 拋出的例外、只放棄這一句不往外炸,寫法跟 `read_memories` 迴圈裡「一支壞檔不准炸掉整輪」的既有精神一致。`_INDEX_MAX_BYTES = 25 * 1024` 改成跟 `MAX_BYTES = 64 * 1024` 同樣用 `* 1024` 寫法、KB 顯示改成 `/ 1024`,是跟緊鄰的 `MAX_BYTES` 定義及既有 `size // 1024` 顯示慣例對齊,不是另起一套。測試裡 `_ms.os.fstat = _boom` / 用 try/finally 還原,跟本檔既有 `lm.os.write = lambda...` / `finally: lm.os.write = _real_write` 的 monkeypatch 慣例(scripts/test_lumos.py 約 3110–3120 行)寫法一致。用 `importlib.util.spec_from_file_location` 直接載入 `.py` hook 檔案再 `exec_module` 的做法,跟本檔多處(如載入 `scenario_probe.py` 的測試)既有慣例一致,`.py` 副檔名不需要額外傳 `SourceFileLoader`。`ctx_for(index_text, link=False)` 新增符號連結分支、`os.symlink`/`os.link` 的用法跟本測試檔其他地方(如硬化 CX1 段落)的 symlink/hardlink 造測資手法一致。
