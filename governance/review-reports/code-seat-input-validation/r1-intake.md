# 代碼審首輪收貨與處置

兩席全收齊後才修；單家族 standard 正確性與架構對齊。正確性兩條 minor 均折入，架構 clean；沒有阻擋問題。原報告未改寫，不宣稱實際輪數下降。

preflight-1: ran — 真實錯輸入重現、設計反證與凍結另存 seat-input-validation。
preflight-2: ran — source 180 行、graph 233 行，全snapshot 4597行作歷史指紋而分開審實作與圖譜；固定鏡頭有內容節點逐條答。
preflight-3: ran — 每席材料清單含凍結source/graph/snapshot/真圖譜鏡頭；原快取鏡頭零題表態來自365，派工前另留fd255零題收據。角色卡未自動附，不宣稱已附。
preflight-4: ran — 最初相關166全綠，原完整CLI同新三函式66綠94紅，自主145全綠。全套因首輪補測需改來源而停止，部分shard不算通過；版本固定後重跑。

## 重現與處置

- F1 HIT：原三測試無合法surrogateescape路徑。臨時拒絕全部surrogate版本對原三測試全綠，對補測後出現失敗，實際數字及雜湊見r1-F1-control.json。新增可編碼0x80路徑加實際普通材料、普通/-O CLI與真材料錨定；macOS APFS 不准非UTF8名稱，故缺失路徑依舊只觀測，不能假稱此路徑實際建立成功；二進位收貨避免父行程文字解碼製造假錯誤。正式生產函式未改。官方os.fsencode與Ruff閉包綁定依據已查；Ruff網址 https://docs.astral.sh/ruff/rules/function-uses-loop-variable/ 。
- F2 HIT：原計劃歷史段落含待實作現況文字。刪除18行流程史，保留實際設計理由、官方來源與不可混讀的歷史卷證指標；四條驗收與核心裁定沒有變更。前後全文見r1-fold.patch，原報告引句仍以原snapshot錨定。
- 正確性snapshot hash末尾聲明少了幾個字元：保留原報告，權威為r1-materials.json、r1-dispatch.json與實際檔雜湊，不是文字抄錄；兩份完整patch指紋與真正讀取留在原始執行紀錄。
- report-normalize/refcheck/seat-check均rc0，正確性兩引句quote-check rc0；架構clean無引句rc2為N/A。兩席out_of_scope空；unreported只指鏡頭檔名字串未寫入報告，報告已有7節點逐條答，不宣稱工具證明閱讀。
- 席位臨時目錄受唯讀沙箱限制；架構改以記憶體真入口18探針成功，不冒稱CLI子集獨立綠。
