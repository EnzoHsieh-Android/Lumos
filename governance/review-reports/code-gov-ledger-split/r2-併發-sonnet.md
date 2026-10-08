severity: major

## F1 本機帳讀取端仍跟捷徑,指向 /dev/zero 或 FIFO 時讀取程序無界吃記憶體或永久卡住
severity: major
blocking: 是
引句:「raw, _start = _gov_tail_bytes(p)」
file: `scripts/lumos:3809`(_gov_tail_bytes:先 stat 取 size,再 open、seek、fh.read() 無上限)
失敗場景:寫入器已加 is_symlink 擋,但讀取端(_gov_ledger_rows_by_time、_gov_metric_events,走 doctor 度量段與統計段)沒擋。有人把 docs/.governance-local.jsonl 以 git add -f 提交成指向 /dev/zero 的捷徑,別人 clone 後跑 doctor 或統計:st_size 為 0 → start=0 → fh.read() 讀不到 EOF,記憶體一路長到被殺。指向 FIFO 則 open 永久阻塞。
最小重現(已實跑):在臨時目錄 docs/ 下 ln -s /dev/zero .governance-local.jsonl,在 ulimit -v 600000 下 exec 抽出的 _gov_tail_bytes,結果 MemoryError。
與分流前比:版控帳讀取本來就同樣會被打(既有);但本機帳是這批新增的讀取面,且作者對寫入端已用 is_symlink 處理同一威脅模型,讀取端漏掉,保護只做一半。
修法方向:讀取前 is_file() 且非 is_symlink,fh.read(cap) 加上限。

## F2 .gitignore 讀整份再替換:讀與替換之間使用者的編輯會被覆蓋
severity: minor
blocking: 否
引句:「_write_lf(gi, (raw + chunk).decode("utf-8"))」
file: `scripts/lumos:17727`(_write_lf 的 os.replace 無鎖、無版本比對)
失敗場景:程序 A 在 _ensure_docs_gitignore 讀 raw(舊內容),使用者在編輯器存檔加了一行,程序 A 隨後 os.replace,使用者那行消失。改前的 open("ab") 追加只是接在尾端,不會丟編輯。窗口是毫秒級,只在缺行時才進入寫入路徑(之後每次都「已有」而直接 return),實際觸發極窄。兩個程序同時補:兩邊算出同一份內容,替換結果一致;os.replace 為原子,中途讀者只會讀到舊或新整份,不會讀到半份。

## F3 kill 時 docs/ 殘留未追蹤暫存檔,而且沒有被忽略規則涵蓋
severity: minor
blocking: 否
引句:「.gitignore 是捷徑時換掉的是捷徑本身,不會寫到它指的地方」
file: `scripts/lumos:17739`(暫存名 `.gitignore.<pid>-<hex>.tmp-wlf`,建於 docs/ 同層)
失敗場景:SIGKILL 落在 os.open 與 os.replace 之間(except BaseException 清理不會執行),docs/ 留下 .gitignore.1234-ab12cd34.tmp-wlf;_ensure_docs_gitignore 補的只有兩本帳的檔名,不含 *.tmp-wlf,所以 git status 看得到、git add -A 會把它提交。新路徑在每次 init/update 發現缺行時才走,頻率低。程式其他處(31110、31487 行)已知這種殘檔,但沒人清。

## F4 合讀把兩本帳的檔尾全部物件化,與註解宣稱的「不留整份清單」不符
severity: minor
blocking: 否
引句:「rows.extend(_drift_jsonl_iter(raw))」
file: `scripts/lumos:1351`、呼叫點 `scripts/lumos:2989`
失敗場景:兩本各到 24MB 上限(本機帳正是例行高頻寫入),rows.extend 把約 48MB JSON 全轉成 dict 後再 sorted,尖峰記憶體是原文數倍(估計數百 MB);_drift_jsonl_iter 的 docstring 專為避免這件事而寫,這裡反而收集成清單。比改前讀無上限整檔已好,但檔尾被截時 _start 被丟棄,統計類讀者對超過 24MB 的本機帳會靜默少算,沒有任何提示。⚠ 少算是否影響判定我沒追到各統計讀者的用途。

## 已走過沒問題的範圍
- 兩個程序同時跑 _ensure_docs_gitignore:同一舊內容算出同一新內容,os.replace 原子,結果一致,不會補兩份。
- 暫存檔名含 pid 加隨機,多程序不互搶;例外路徑會 unlink。
- is_symlink 檢查與 open("a") 之間的 TOCTOU:能換捷徑的人已能寫 repo,分流前版控帳連檢查都沒有,沒有變差,也不是新的提權面。
- 讀檔尾時另一程序正在 append:半行為 JSON 解析失敗只跳那一行;截斷在多位元組字元中間靠 errors=replace 處理;檔尾頭一行被丟棄的邏輯正確。
- _gov_ts 與排序鍵的例外(OverflowError、OSError、ValueError)接得完整;深層巢狀壞行 RecursionError 已接。
- 圖譜鏡頭:本次未見 hook 附上的固定席筆記,無逐條可答。

總結:合讀與替換寫入的併發時序大致站得住,但本機帳讀取端沒擋捷徑到 /dev/zero 會吃光記憶體,需修。
