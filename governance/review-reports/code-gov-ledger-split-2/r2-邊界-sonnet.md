severity: minor

## F1 唯讀但已齊全的 .gitignore 每次 update 都被誤報「開不了」
severity: minor
blocking: 否
引句:「        fd = _os.open(str(gi), _os.O_RDWR | _os.O_APPEND | nofollow)」
file: `scripts/lumos:21074`
未能重現(本機跑在 root,權限檢查被繞過;行為由 open(2) 對 O_RDWR 的語意推得)。
1. docs/.gitignore 已有 .governance-local.jsonl 與 .usage-local.jsonl 兩行,但檔案是 0444(或檔案屬別人、或 docs 掛在唯讀檔案系統)。
2. 非 root 使用者跑 lumos update,走到 _ensure_docs_gitignore 的 O_RDWR 開檔,得到 PermissionError 或 EROFS。
3. 走進 `_manual(f"開不了(...)")`,印出「沒有自動補…請自己加上」的警告。舊碼用 read_bytes 讀,已齊全時安靜返回。
4. 本輪特地把「硬連結但兩行齊全」改成安靜放過,同一條「不缺就不該吵」沒套到唯讀。缺行才需要寫權,齊全只需要讀。

## F2 檔案物件用 buffering=0,追加遇到短寫(磁碟快滿)不拋錯,卻回報補上了
severity: minor
blocking: 否
引句:「            f.write((b"" if tail == b"\n" else nl) + b"".join(n.encode("utf-8") + nl for n in missing))」
file: `scripts/lumos:21073`
未能重現(未造出磁碟滿環境)。
1. `_os.fdopen(fd, "r+b", buffering=0)` 回的是裸 FileIO,write 只呼叫一次 write(2),回傳實際寫入位元組數,不迴圈補寫。
2. 磁碟剩幾個位元組時,write(2) 回傳比要求少的正數、不是錯誤,這裡沒檢查回傳值。
3. 檔尾可能留下被截斷的半行(例如 `.usage-loc`),函式照樣印「補上 2 行」並回傳 missing。
4. 後果是 .usage-local.jsonl 沒被忽略,日後被 git add 誤進版控。下次 update 會因行不齊再補,但壞半行殘留。測試只模擬了新建路徑的 write 拋 OSError,沒涵蓋追加路徑的短寫。
5. 同一個新建路徑如果截斷落在註解行的多位元組字中間,下次跑會判「不是 UTF-8」而永遠不自動修(機率更低)。

## 已走過沒問題的範圍
- _local_ledger_open:管線無讀者時 O_NONBLOCK 讓 open 回 ENXIO、有讀者時 fstat 非一般檔而關閉;資料夾 EISDIR、捷徑 ELOOP、唯讀 EACCES 都回 None,fd 不漏。fstat 失敗走 except 關 fd。
- _local_ledger_open 在沒有 O_NOFOLLOW 的平台(Windows)會退成跟隨捷徑:舊的 is_symlink 先檢查已被拿掉,Windows 上這道防線消失,但該平台建捷徑需特權,不列。
- _ensure_docs_gitignore:空檔(size 0 → tail 當換行)、只有 BOM(尾位元組非換行 → 先補換行)、單一位元組、CRLF(沿用 \r\n)、無結尾換行、壞捷徑、資料夾、管線(O_RDWR 不卡、fstat 擋)都走得通。
- 硬連結缺行才警告、齊全放過;新建時 O_EXCL 遇競爭落回已存在路徑。BOM 開頭使第一行比對不到只會多補重複行,對 git 無害。
- _gov_metric_events 的 now 過濾:now=None 行為不變;帶時區 now 與 _gov_ts 回傳的帶時區時間可比;帳內沒帶時區的時間當本機時間後可比;全部在未來時回 None(只是不判,不崩)。
- _gate_event、_append_governance_log、_usage_log:None 與 OSError 都被吞,版控帳寫入照舊;cmd_gov 的 GOV_LOG_NAME 常數與原字面值相同(`scripts/lumos:1316`)。
- 圖譜鏡頭:派工時尾端未附固定席筆記(沒有「圖譜沒有釘到節點」備援段之外的條目),無可逐條判的固定席項目。

本輪修補沒有擋路的邊界缺口,只有兩處小瑕疵:唯讀但齊全的 .gitignore 會誤警告,與追加路徑不檢查短寫。
