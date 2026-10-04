severity: minor

## 問1 分層與依賴方向
結構對齊。_local_ledger_open 放在 `_docs_ledger_path` 旁、被三支寫入器共用(`scripts/lumos:1339`),方向是「寫入器呼叫小工具」,跟鄰居 `_docs_ledger_path` 一樣,沒有跨層直呼。cmd_gov 的 load 已改用 GOV_LOG_NAME(`scripts/lumos:8338`),與上一行本機帳的 GOV_LOCAL_LOG_NAME 對稱,上一輪那條已收掉。_gov_metric_events 加 now 參數、`_doctor_metric_lines` 把 now 提前算(`scripts/lumos:4004` 一帶),呼叫方向沒變。

## 問2 命名與錯誤處理
命名 `_local_ledger_open` 跟 `_gate_event`、`_usage_log` 同樣的底線前綴加動詞風格;函式內 `import os as _os` 與 `_write_lf` 的做法一致(`scripts/lumos:17779`)。例外吞法:開不了回 None、呼叫端當寫不進去,與 `_drift_m1` 寫帳的「OSError 回 False」同路(`scripts/lumos:35947`);_usage_log 外層仍是 except Exception 靜默,沿用原樣。訊息語氣(印「⚠ …沒有自動補…請自己…加上」)跟鄰近 doctor 提示一致。

## 問3 第二種做法
開檔旗標加 fstat 確認一般檔案這個做法,倉內已有一份(`scripts/lumos:35933`,drift-m1 的 ledger-miss 寫入),本輪把它統一到三支寫入器,上一輪指的「兩種追加並存」在本機帳這邊收掉了。剩下兩處與既有鄰居的小差異,見 F1、F2。

## F1 追加寫入用緩衝檔案物件,既有帳本寫入器用單次 os.write
severity: minor
blocking: 否
引句:「return _os.fdopen(fd, "a", encoding="utf-8")」
file: `scripts/lumos:18678`
file: `scripts/lumos:35933`
說明:倉內以 O_APPEND 開檔寫帳的兩個鄰居(`_ledger_append`、drift-m1 的 ledger-miss 寫入)都是轉成 bytes、單次 os.write、並檢查短寫(寫滿才算成功),註解明說這是併發合約。_local_ledger_open 回傳文字模式緩衝檔案物件,`_append_governance_log` 一批多行用多次 write,不檢查短寫,也沒有整行單次寫出的保證。結構上沒有跨層,但本機帳這三支寫入器走的是跟鄰居不同的追加手法;該帳是統計用、容忍度高,所以只列 minor。

## F2 一般檔確認的做法在本檔又多一份,且比既有那份少了 uid 檢查
severity: minor
blocking: 否
引句:「if not _stat.S_ISREG(_os.fstat(fd).st_mode):」
file: `scripts/lumos:35936`
說明:drift-m1 的同一個做法除了 S_ISREG 還比對檔案擁有者 uid(`scripts/lumos:35936`);本輪新增的 _local_ledger_open 只驗 S_ISREG,`_ensure_docs_gitignore` 內又自帶一份 S_ISREG 判斷,等於同一個「開了再 fstat」慣用法現在有三份寫法、嚴謹度不一。本機帳在 repo 的 docs/ 下、不是使用者家目錄的私有快取,不比 uid 有其道理,但倉內沒有一處註明這個差異是刻意的。

不對齊共 2 條,其中重大 0 條
