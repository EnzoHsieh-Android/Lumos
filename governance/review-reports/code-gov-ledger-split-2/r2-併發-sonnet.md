severity: minor

## F1 補 .gitignore 追加用無緩衝原始寫入,短寫入被當成功
severity: minor
blocking: 否
引句:「f.write((b"" if tail == b"\n" else nl) + b"".join(n.encode("utf-8") + nl for n in missing))」
file: `scripts/lumos:21134`
失敗場景:
1. 檔案代號以 fdopen(fd, "r+b", buffering=0) 開成原始 FileIO,f.write 只呼叫一次 write(2),回傳寫了幾個位元組,代碼不看回傳值。舊版用有緩衝的 "ab",會自己補寫到寫完。
2. 磁碟快滿或有檔案大小配額、剩的空間不夠整段(約 45 位元組)時,write(2) 回短寫入而不丟例外。
3. 走到 `print(f"  ✓ 本機帳的忽略設定補上 {len(missing)} 行 → {gi}")` 並 return missing,回報兩行都補上了。
實測(RLIMIT_FSIZE 限 32 位元組,忽略 SIGXFSZ,對 docs/.gitignore 內容為 "a\n" 呼叫 _ensure_docs_gitignore):印「補上 2 行」、回傳兩行,檔案實際是 'a\n.governance-local.jsonl\n.usage',.usage-local.jsonl 沒被忽略,工作目錄被弄髒,而且訊息說成功。
影響:下次 update 會因缺行再補一次(檔尾非換行會先補換行),只留一行無害的殘缺規則;但這次有說謊的成功訊息,違反本輪「寫入失敗一律回 []、印手動提示」的意圖。
修法方向:改用 os.write 並驗回傳值是否等於長度,或把 chunk 先包成有緩衝的寫入器。

## 已走過沒問題的範圍
- _local_ledger_open:O_NONBLOCK 對一般檔案不生效,不會有 EAGAIN 或部分寫入;寫入走有緩衝文字寫入器,單筆事件行有 _gate_event_fit 的 4096 上限。fstat 失敗、非一般檔案、fdopen 失敗三條路都有關代號;fdopen 成功後由檔案物件擁有代號,三支寫入器都用 with 關閉。管線沒有讀端時 ENXIO 回 None 不卡;有讀端時開到再關,不卡。
- 多個 hook 同時 append 本機帳:O_APPEND 保證每次 write(2) 落在檔尾。_append_governance_log 一次寫多筆、總量超過緩衝 8192 時可能分多次 write(2) 而交錯,但這是版控帳舊有行為(open "a" 同樣),本輪沒有新增。
- _ensure_docs_gitignore:O_RDWR 開管線在 Linux 不阻塞(且帶 O_NONBLOCK),開到後 S_ISREG 擋下;目錄開檔得 EISDIR 走 _manual;捷徑先擋、O_NOFOLLOW 再擋。讀、取檔尾、追加用同一個代號,fstat 取現在的 size,O_APPEND 讓 seek 不影響寫入位置。init/update 沒有任何會無限等待的路徑(新建用 O_EXCL|O_NONBLOCK,FileExistsError 轉走已存在路徑)。重複行已裁不報。
- _gov_metric_events 的 now 比較:_gov_ts 回帶時區時間,doctor 的 now 一律帶時區,現有測試傳入的 now 都帶 UTC,沒有 naive/aware 比較出錯。
- cmd_gov 與 _gov_tail_bytes、doctor 讀本機帳都先 is_file(),不會對管線開檔卡住。
- 圖譜鏡頭:派工尾端沒有附固定席筆記,無條目可逐條答;本輪修補未見與合約衝突之處。

總結:只找到一條短寫入被誤報成功的低嚴重度問題,資源與併發面其餘路徑沒發現會卡住或洩漏代號的時序。
