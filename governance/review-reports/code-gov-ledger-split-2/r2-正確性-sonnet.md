severity: minor

## F1 唯讀 .gitignore 規則已齊也被警告「開不了」(回歸)
severity: minor
blocking: 否
引句:「fd = _os.open(str(gi), _os.O_RDWR | _os.O_APPEND | nofollow)」
file: `/home/user/Lumos/scripts/lumos:21128`(以 delta 中該行為準;舊版是先 stat/read_bytes,缺行才開寫入)
失敗場景:
1. docs/.gitignore 權限 0444(或所屬別人、本程序無寫權),內容已含 .governance-local.jsonl 與 .usage-local.jsonl 兩行。
2. 以非 root 身分跑 lumos init / update,走到 _ensure_docs_gitignore 的「已存在」分支。
3. 新版一律以 O_RDWR|O_APPEND 開檔,EACCES 落到 `except OSError`,回 _manual(「開不了(PermissionError)」),印出警告並要人手動加那兩行。舊版只讀不寫、missing 為空就安靜回 [],不會警告。
4. 實跑:nobody 身分、0444 且兩行齊全的 .gitignore,輸出「⚠ …/.gitignore 開不了(PermissionError),沒有自動補本機帳的忽略規則」,回傳 []。每次 init/update 都重複,且與 doctor 的建議「跑 lumos update 補忽略」互相打架。
影響:只是誤導的提示,不中止、不寫錯檔;嚴重度 minor。修法方向:先試 O_RDONLY 讀判斷缺行,缺行才用 O_WRONLY|O_APPEND 重開(但會失去同一代號的併發保護),或 O_RDWR 失敗時退而用 O_RDONLY 判斷已齊就靜默。

## 已走過沒問題的範圍
- _local_ledger_open:管線無讀者(O_NONBLOCK 得 ENXIO 回 None)、資料夾(EISDIR)、/dev/null(fstat 非一般檔,關檔回 None)、捷徑(O_NOFOLLOW 失敗)實跑皆回 None 不卡住;不存在則建。非一般檔分支與 fdopen 失敗分支都關了檔案代號;唯一瑕疵是 close 自己丟 OSError 時會被第二個 close 重關(要 close 本身失敗才發生,不構成可重現場景,不標)。三個呼叫端(_gate_event、_append_governance_log、_usage_log)對 None 都是回 False/continue/return,與舊約定一致;非本機分支仍用 open(),f 為 None 的判斷對它無害。
- _ensure_docs_gitignore 實跑:空檔(size 0 走 tail=b"\n",寫入正確)、檔尾無換行、CRLF 檔尾無換行(沿用 \r\n)、只缺一行、資料夾(印出開不了)、非 UTF-8(印出提示、檔不動)、管線(O_RDWR 開得起來、fstat 擋下印出不是一般檔案)皆如預期。buffering=0 的 f.read() 是 readall,讀得完整;seek 後 read(1) 再 write,O_APPEND 保證寫到現在檔尾。O_EXCL 撞到同時建檔:fd=None 落到已存在路徑,讀到空檔會追加兩行,之後對方用自己的 offset 0 寫入整份 body 會蓋掉追加的字節,結果仍是完整 body,不會缺行(重複行屬使用者已裁接受)。新建分支寫入失敗(含緩衝在 close 時 flush 失敗)包在 try 內回 []。
- 次要觀察不標:只有 \r 結尾的檔補一個 \r\n 再接 \n 行(混合換行,git 無害);帶 BOM 的首行不等於規則行會再補一份(舊版同樣行為)。
- _gov_metric_events 的 now:_doctor_metric_lines 預設 now 為 aware,測試傳入的 now 全是 tzinfo=utc,_gov_ts 回傳皆為 aware,aware 對 aware 比較不會丟例外;now 的運算上移到兩次呼叫前,_dt 已匯入,版控帳不存在時仍可走。naive now 本來就會在 cutoff 比較處丟,不是新增的洞。只有一筆舊紀錄、其餘為未來時間時回 None,與計劃〈天花板〉聲明一致;事件計數仍包含未來事件是舊有行為。
- cmd_gov 的 load 改用 GOV_LOG_NAME:常數值就是 ".governance-log.jsonl",等價。
- 新舊互讀:判定類讀者只讀版控帳、統計類讀兩本,這份修補差異沒有改動這個分界。
- 圖譜鏡頭:派工尾端未附固定席筆記,不逐條答。此 diff 未動合約行相關的行為(帳檔分流、讀者分界不變),未發現破壞節點宣稱。角色卡未附,略過。

總結:修補大致正確,唯一可重現的問題是唯讀且規則已齊的 .gitignore 會被誤警告,屬提示層面的小回歸。
