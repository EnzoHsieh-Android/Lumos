severity: major

## F1 讀側忽略落盤的 loop_kind，舊逃逸會隨後來的審查改類
severity: major
blocking: yes
引句:「return [d for d in rows if not _escape_is_withdraw(d) and d.get("token") not in gone」
file: `scripts/lumos:7591` `_escape_rows_for` 原樣回傳舊列，沒有依 [S1] 補推 `loop_kind`；`scripts/lumos:9933` 又忽略新列已落盤的 `loop_kind`，改用目前的審查帳重算。原本以 `loop_kind=plan` 寫入的低風險計劃逃逸，只要日後同編號加入審查帳並收斂，就會被改算成設計審漏網，污染歷史統計。
重現步驟:
1. 實跑：
   `python3 -B -c 'p="scripts/lumos"; ns={"__name__":"lumos_review","__file__":p}; exec(compile(open(p,encoding="utf-8").read(),p,"exec"),ns); raw={"loop":"甲","token":"ESC-A","sha":"old-sha","loop_kind":"plan"}; print("persisted_kind=",raw["loop_kind"]); print("bucket_after_review=",ns["_escape_row_bucket"](raw,"甲",{"甲"},{"甲"},{"old-sha":{"甲"}})); ns["_escape_raw_rows"]=lambda env:[{"loop":"甲","token":"ESC-OLD","sha":"s"}]; print("old_row_read=",ns["_escape_rows_for"](object()))'`
2. 實際輸出：`persisted_kind= plan`，但 `bucket_after_review= counted`；舊列輸出也完全沒有 `loop_kind`。
3. 依 [S1]，已落盤的 `plan` 不應被後來的帳況改類；舊列讀出時則應用同一判法補推種類。

## F2 同一 defect_ref 只因 sha 不同便逃過歸因不明判定
severity: major
blocking: yes
引句:「return str(r.get("sha") or "").strip() or str(r.get("defect_ref") or "").strip()」
file: `scripts/lumos:9879` 每列只挑一個佐證鍵，且 `sha` 永遠遮蔽 `defect_ref`。兩個迴圈明確指向同一 Issue／缺陷報告，但各自帶不同修復提交時，程式會把它們當成兩份獨立佐證，兩個迴圈都進漏網分子；這違反 [S8]/[S20] 要求的共同佐證歸因不明，會灌高各類逃逸率。
重現步驟:
1. 實跑：
   `python3 -B -c 'p="scripts/lumos"; ns={"__name__":"lumos_review","__file__":p}; exec(compile(open(p,encoding="utf-8").read(),p,"exec"),ns); rows=[{"loop":"甲","sha":"commit-A","defect_ref":"Issues/同一缺陷"},{"loop":"乙","sha":"commit-B","defect_ref":"Issues/同一缺陷"}]; ev=ns["_escape_shared_evidence"](rows,{"甲","乙"}); print("shared_evidence=",ev); [print(r["loop"],ns["_escape_row_bucket"](r,r["loop"],{"甲","乙"},{"甲","乙"},ev)) for r in rows]'`
2. 實際輸出：`shared_evidence={'commit-A': {'甲'}, 'commit-B': {'乙'}}`，甲、乙皆為 `counted`。
3. 預期共同的 `Issues/同一缺陷` 應把兩列都歸入 `unattributed`，不進任何類別分子。

測試執行註記:指定的三組測試均已實跑嘗試，但唯讀沙箱沒有任何可寫暫存目錄，測試框架在收集前以 `FileNotFoundError: No usable temporary directory` 退出；上面兩項因此改用同一份原碼記憶體載入並直接執行反例，全程未寫檔。

已看,無:撤回紀錄的基本驗證與重複撤回阻擋、撤回後自動記帳不復活、符號連結帳本阻擋、以迴圈為分子分母、下一站分類、`code-` 前綴與 NFC 計劃查找，未找到另一項可實跑成立的 blocker/major。
