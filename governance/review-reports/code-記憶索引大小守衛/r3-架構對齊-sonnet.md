severity: clean

已看,無:這次改動(`_index_bytes`、`index_size_note` 改寫、`_opened_reason` 加 `max_bytes` 參數、`t_memory_sweep_index_size` 補測試)在寫法上跟本檔既有慣例一致,沒發現另起一套的地方:
- `_index_bytes` 組裝流程(先 `os.lstat` 拿 `pre`、過 `_pre_reason`、`O_NOFOLLOW|O_NONBLOCK` 開檔、`fstat` 過 `_opened_reason`、`os.fdopen(fd, "rb", closefd=False)` 讀、`finally: os.close(fd)`)跟 `_read_own_file`(656 行)是同一套防護骨架,且明確重用 `_pre_reason`/`_opened_reason` 兩支共用判斷,不是重寫一份平行邏輯;docstring 也照本檔既有寫法標出「翻紅釘」與代碼審輪次來源。
- 給 `_opened_reason` 加 `max_bytes=MAX_BYTES` 參數、`None` 表示不管大小,這個「加可選參數、預設值等同舊行為」的做法跟本檔其他函式(如 `_outer_budget(default=10.0)`、`_claims_near(body, stem, paras=None)`)的參數風格一致。
- `_index_bytes` 在 `_pre_reason`/`_opened_reason` 之前(378 行)、被依賴的兩支定義在後面(695/708 行)這種「前面用、後面定義」的順序,本檔本來就有(例如 633 行 `read_memories` 呼叫 656 行才定義的 `_read_own_file`),不是這次新引入的不一致。
- `_INDEX_MAX_BYTES = 25 * 1024` 改成跟 `MAX_BYTES = 64 * 1024` 同樣「以 1024 為底」的寫法,且改動旁補了原因註解,訊息組裝(`%d KB`、「發生什麼——★怎麼做★」的三段式)延續 `index_size_note` 原本的白話風格,沒有換一套用詞。
- 測試新增的 ⑤–⑧ 沿用同一支 `t_memory_sweep_index_size` 裡既有的 `check()` + 圈碼編號 + 翻紅釘寫法,`ctx_for` 加 `link` 參數也是「既有 helper 加可選參數」而非另開一支 helper;函式內 `import os`(不加底線別名)在本檔其他測試(如 440、10062 行)也有前例,跟旁邊 `t_memory_sweep_core` 用 `_os` 別名的差異屬於本檔既有的兩種並存寫法,不是這次新造成的不一致。
