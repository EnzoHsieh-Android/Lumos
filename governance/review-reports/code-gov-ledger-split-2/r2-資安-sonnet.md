severity: minor

## 類1 不可信輸入流到危險操作
已看。本機帳與 .gitignore 的路徑都固定在 docs/ 下的常數檔名,不含外部輸入;寫入內容是工具自己組的 JSON 行。帳檔若是捷徑,寫入端用 O_NOFOLLOW 擋掉,指向 repo 外的檔不會被寫。讀取端(cmd_gov 的 load、_gov_ledger_rows_by_time)跟捷徑讀,但只把解析成功的 JSON 物件欄位印在使用者自己的終端機,沒有外送或寫回 repo 的路徑。已看,無可利用的洞。

## 類2 判定繞過
已看。_GOV_LOCAL_PAIRS 不含 code-loop、fix-check、design-loop,CI 與 pre-push 讀的代碼審留痕只來自版控帳(例如 scripts/lumos:42578 起的讀取只開 .governance-log.jsonl),本機帳讀不進去。攻擊者即使強制提交一份偽造的 docs/.governance-local.jsonl,它只進統計與 doctor 的軟提醒(cmd_gov、規格閘最近一次紅綠、度量式撤除條件),這幾處都不放行推送、不擋推送。_BOOKKEEPING_FILES 新增的兩個本機帳是精確路徑比對,代碼檔改動仍會讓留痕失效,不構成遮蔽代碼改動的通道。偽造的度量事件最多讓 doctor 多印或少印一行軟提醒,見 F1(推論)。

## 類3 密鑰與個資
已看。_ensure_docs_gitignore 的 _manual 提示印出的路徑是 docs_dir/.gitignore(repo 內路徑)與兩個固定檔名,不含家目錄檔內容。捷徑情況只印「是捷徑」,沒有解析並印出捷徑目標。本機帳內容是事件與節點名,不含密鑰;帳檔被忽略,不會被寫進 repo。已看,無。

## 類4 加密與傳輸
已看,無。這批改動沒有網路、加密、雜湊驗證相關程式。

## 類5 執行邊界
已看。_local_ledger_open:O_NOFOLLOW 擋捷徑、O_NONBLOCK 讓沒有讀者的管線開檔回 ENXIO、有讀者時開到後 fstat 非一般檔案就關掉回 None,順序正確,沒有「先檢查再開」的競態。_ensure_docs_gitignore:捷徑先擋;新建用 O_EXCL|O_NOFOLLOW;已存在用 O_RDWR|O_APPEND|O_NOFOLLOW 開,管線(Linux 上 O_RDWR 不阻塞)與資料夾(EISDIR)都落到手動提示;硬連結只在缺行時才拒絕。無 subprocess 參數新增。僅存的未覆蓋點是路徑中間目錄(例如 docs 本身)為捷徑,O_NOFOLLOW 只管最後一段,但這是既有行為、本批沒有放大。已看,無。

## 類6 行動端
已看,無。另看新依賴:只多了標準庫 heapq、stat,無第三方依賴。

## F1 偽造本機帳可誤導度量式撤除條件的軟提醒
severity: minor
blocking: 否
引句:「        evs_l, oldest_local = _gov_metric_events(gll, now)」
file: `/home/user/Lumos/scripts/lumos:4004`
標示:推論(沒有拿到放行或擋人的結果,只影響 doctor 軟提醒文字)。
攻擊路徑四件:
1. 誰:惡意 repo 作者。
2. 從哪個入口:提交進 repo 的 docs/.governance-local.jsonl(本機帳被忽略,但作者可強制 git add -f)。
3. 送什麼:大量偽造的 gate/kind 事件,帶符合度量條件的時間。
4. 拿到什麼:受害者在 clone 後跑 lumos doctor,S18 可能誤報「這條限制該撤」或相反壓掉該撤的提醒;只是軟提醒,不影響任何閘的放行或擋推,也不外洩資料。

最後一行總結:這批修補在開檔、補忽略設定與帳檔讀寫三處的邊界都收得住,判定類讀者仍只讀版控帳,沒有找到能繞過代碼審留痕或外洩資料的攻擊路徑,只有一條僅影響軟提醒的推論。
