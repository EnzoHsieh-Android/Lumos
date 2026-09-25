severity: major

## F1 `_index_bytes` 重新刻了一份 `_opened_reason` 已經有的邏輯,沒有共用
severity: major
blocking: no
引句:「if (st.st_dev, st.st_ino) != (pre.st_dev, pre.st_ino) or _pre_reason(st):」

`_read_own_file` 打開檔案之後,是呼叫既有的 `_opened_reason(os.fstat(fd), pre)` 來判斷「打開後看到的代碼是不是換掉了 / 是不是一般檔」——這支函式已經把「比對 dev/ino」跟「檢查是不是一般檔」包在一起了(見 `def _opened_reason(st, pre)`,376行後)。`_index_bytes` 要做一模一樣的事,卻沒有呼叫 `_opened_reason`,而是手動重寫了 dev/ino 比對,然後拿設計給「打開前」用的 `_pre_reason` 去檢查「打開後」的 `st`(`_pre_reason` 這個名字本身就標明是 pre-open 用的,函式命名跟用途在這裡對不上)。這是同一段 TOCTOU 防護邏輯的第二份拷貝:以後 `_opened_reason` 若因新的資安席發現而加一條檢查(這檔案的 changelog 顯示這套防護已經改過 r1/r4/r5/r9/r11 好幾輪),`_index_bytes` 這份不會跟著變,兩邊會悄悄漂移。既然 `_index_bytes` 本身的 docstring 就寫著「★跟讀記憶檔同一套防護★」,更應該直接呼叫 `_opened_reason(st, pre)` 而不是另起一段等價邏輯(超過大小的分支可以在呼叫之後另外處理,不影響能不能重用這段判斷)。

## F2 同一則訊息裡 KB 換算基底不一致,且改動理由的註解跟實際不符
severity: minor
blocking: no
引句:「% (size // 1024, _INDEX_MAX_BYTES // 1000))」

新加的註解寫「KB 跟本檔其他地方一樣按 1024 算」,但同一段程式碼裡,分子(`size`)改成了 `// 1024` / `/ 1024`,分母(`_INDEX_MAX_BYTES`)卻維持原本的 `// 1000` 沒有一起改(421 行與 427 行都是這樣)。結果同一句「有 X KB,遠超過上限 Y KB」裡,X 是以 1024 為底、Y 是以 1000 為底,兩個「KB」實際單位不同(25000 位元組顯示成 25 KB 上限,但同一顆位元組數若當分子會顯示成 24.4 KB)。既有慣例(改動前)是整段都用 1000,`MAX_BYTES` 那邊(689、719 行)才是全部用 1024 的慣例;這次改動變成在同一句話裡混用兩套,既沒有對齊「跟 MAX_BYTES 那邊一樣用 1024」的說法(因為 `_INDEX_MAX_BYTES` 沒有跟著換),也破壞了原本「整段都用 1000」的內部一致性。

---

已看,無:`_pre_reason` 本身在 `_index_bytes` 裡用來做「打開前」判斷(對 `pre` 呼叫)是正確重用,跟 `_read_own_file` 的用法一致;`os.lstat` → `_pre_reason` → `os.open(O_RDONLY|O_NOFOLLOW|O_NONBLOCK)` → 讀 `MAX_BYTES+1` 位元組再檢查是否超界這一整套雙重檢查(fstat 大小先擋一次、讀出來的實際長度再擋一次)完整比照了 `_read_own_file` 的做法,沒有漏掉中途被換檔的防護。`index_size_note` 改成呼叫 `_index_bytes` 後,原本回傳格式(None / 有值)與呼叫端行為維持一致,`why_unknown`、`memory_dir` 等其他函式沒有被牽動。`scripts/test_lumos.py` 裡新增的 ⑤⑥ 兩個案例延用既有 `ctx_for` / `check` 的寫法,只加了 `link` 這個參數維持原有呼叫慣例,跟 `t_memory_sweep_core` 一帶的測試風格(先建臨時目錄、跑 hook、抓 stdout 尾巴比對關鍵字)一致,沒有另起一套測試骨架。訊息文字的「發生什麼→為何在意→現在就瘦身」白話三段式也跟同檔案其他提醒訊息(`head + "。該瘦身了..."` 那段)風格一致。
