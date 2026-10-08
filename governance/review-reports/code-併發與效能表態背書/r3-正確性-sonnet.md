severity: minor

我只讀了上一輪之後的修正差異(`/tmp/cpe/code-r3-delta.patch`),再對照 repo 裡相關的函式,沒有跑測試。三件修正都沒找到會讓算出的背書出錯的洞。唯一的發現是一條文字不一致,是修正自己帶出來的。

- **新舊互讀:** 舊格式的 kill-log 行和殘行,會被 `_drift_jsonl_parse` 照常略過。
- **寫一半:** 讀 kill-log 改用 `_drift_jsonl_rows`,行為跟原本自己寫的那支一致。
- **時間:** 判不了的 git 逾時改用剩餘預算,逾時後 `_nodehome_cat_blobs_capped` 回 None,會正確變成「判不了」。
- **be-api-compat:** 新增的兩個參數 `timeout` 和 `unknown` 都有預設值。`_codeloop_record_valid` 的回傳仍是二元組,pass/skip/表態這些既有呼叫端行為不變,只有失敗訊息文字可能不同。
- **be-authz:** 這份修正不新增端點,也不碰授權,不適用。

**R3C1**
severity: minor
blocking: 否(只影響訊息文字,判定本身正確)
file:line:`scripts/lumos:38103` 附近的 `_codeloop_record_valid_ex`。這輪把「提交找不到」拆成兩種,只有淺 clone 才算判不了,完整歷史裡找不到就是確定無效,但兩種情況共用同一句原因文字。完整歷史裡的 sha 找不到時,回傳 `(False, why, False)`,`why` 仍寫「判不了是不是祖先——先確認那個提交還在」。
失敗場景:kill-log 裡有一筆 sha 不在完整 clone 裡的紀錄,同題沒有其他有效紀錄。`_backing_valid_rows` 會把第一筆無效原因放進整題的 `reason`:「沒有在這一版程式上跑過的破壞測試(記錄 sha … 判不了是不是祖先 …)」。句子前半說確定無效,括號裡說判不了,自相矛盾。使用者也可能因此白跑去「確認提交還在」。
引句:「                           "判不了是不是祖先——先確認那個提交還在,不在就照重來的步驟重記"), _shallow)」
佐證行:file: `scripts/lumos:38744`(`_backing_valid_rows` 把 `first_invalid` 放進 reason)

最高嚴重度:minor,blocking 0 條
