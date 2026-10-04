severity: minor

## F1 唯讀的 docs/.gitignore 已有兩行時,補忽略規則每次都誤報「開不了」並叫人手動加
severity: minor
blocking: 否
引句:「+        fd = _os.open(str(gi), _os.O_RDWR | _os.O_APPEND | nofollow)」
file: `scripts/lumos:21123`
失敗場景(已在臨時目錄實跑,用 setpriv 拿掉 root 的 dac_override 模擬非 root):
1. 消費專案的 docs/.gitignore 權限 444(或唯讀掛載、root 擁有的簽出),內容已經有 `.governance-local.jsonl` 與 `.usage-local.jsonl` 兩行。
2. 跑 lumos update 或 init,經 `_init_additive_setup` 呼叫 `_ensure_docs_gitignore`。
3. 修補後一開始就以 O_RDWR 開檔,唯讀檔直接 PermissionError,走到 `_manual("開不了(PermissionError)")`,印出「沒有自動補本機帳的忽略規則;請自己在…加上」兩行,回傳 []。實測輸出正是這段。
4. 修補前的路徑是 read_bytes 讀、比對後「沒缺行」就靜默回 [];現在連已經齊全的情況都先要求可寫,等於把先前的靜默放行改成誤報。
5. 照提示手動加,行早就在;doctor 的提醒又叫人「跑一次 lumos update」,跑了仍印同一段,每次 update 都吵,而且這條提示的補救動作無效(循環)。
修法方向:缺行才需要寫入;先以 O_RDONLY 開(同樣 O_NOFOLLOW|O_NONBLOCK)讀比對,真缺行再以可寫方式開同一檔;或 O_RDWR 失敗時退回 O_RDONLY 讀,齊全就靜默。docstring「不動的情況:…寫不進去」的措辭也應限縮為「缺行且寫不進去」。

## 已走過沒問題的範圍
- 呼叫點:grep 確認 `_local_ledger_writable` 在 scripts/、docs/ 已無殘留;`_local_ledger_open` 只有 `_gate_event`、`_append_governance_log`、`_usage_log` 與新測試使用;`_gov_metric_events` 兩個呼叫端(版控帳、本機帳)都已傳 now;scripts/hooks/、其他 scripts/*.py、*.sh 沒有引用這些函式或本機帳檔名。
- `_doctor_metric_lines` 把 now 的取值移到讀帳之前,所有測試傳入的 now 都帶 UTC 時區,與 `_gov_ts` 回傳的帶時區時間比較不會 TypeError;生產路徑 now 也是帶時區。
- `_local_ledger_open`:管線以 O_NONBLOCK 開寫會 ENXIO 回 None、捷徑 ELOOP 回 None、資料夾 EISDIR 回 None、特殊檔 fstat 擋掉;fdopen 失敗會關檔;docs 目錄不存在時 O_CREAT 失敗回 None,與舊行為一致。
- `_ensure_docs_gitignore`:捷徑先擋、新建 EEXIST 競態落到已存在分支、O_RDWR 開管線在 Linux 不會卡住且被 S_ISREG 擋下、硬連結只在缺行時警告、檔尾以同一個 fd 現看,邏輯自洽;重複行取捨使用者已裁,不審。
- cmd_gov 的 load 改常數 GOV_LOG_NAME 後,Systems/reversibility-governance-ledger.md 的 `count=7` 與正則實測匹配 7 行(bypass、GOV_LOG_NAME、GOV_LOCAL_LOG_NAME、signoff、kill、canary、CI_LOG_NAME),數量標記沒漂。
- 計劃〈回退〉(整段還原與帳檔取聯集)、〈天花板〉第 5 點(只有一筆舊紀錄不判)、〈實作紀錄〉最後一條,與程式現況對得上;〈做法〉6 開頭仍寫「暖機只看版控帳」,但同段括號已註明現況,且 `_doctor_metric_lines` 程式為準,不構成撞牆。
- doctor 新增措辭「工具來源 repo 自己看根目錄的 .gitignore,update 不會補」與 `_ensure_docs_gitignore` 只動 docs/.gitignore 一致。
- 圖譜鏡頭:派工訊息尾端沒有附 LUMOS-IMPACT 固定席筆記或備援段,沒有可逐條回答的固定席項目;已自行核對 Systems/reversibility-governance-ledger.md 與計劃兩篇,系統節點內 PITFALL 一行寫「第二早」而未提「不晚於 now」,屬程式碼可查到的細節,以程式為準,不立項。

只有一條小問題:唯讀但內容已齊全的 .gitignore 會被誤報,其餘修補與呼叫點、筆記同步都對得上。
