severity: clean

# 第 3 輪資安審查(末輪)

範圍:/tmp/code-tail-r3.patch 全部 1452 行(計劃與筆記、scripts/lumos、scripts/test_lumos.py、skill 說明)。沒有 blocking 級發現,也沒有值得標的 minor。

## 沒問題的項目

逐類結果與查證過程如下。

1. 不可信輸入流到危險操作:已看,無。
   - `_ns_append_read_blobs` 與 `_nodehome_cat_sizes` 組出來的 `版本:路徑` 規格,路徑都先過 `"\n" not in b` 的濾除(佐證 `scripts/lumos:27598` 附近的 `_notelines_append_pairs`)。`_nodehome_cat_blobs` 本來也會在規格含換行時整批放棄(`scripts/lumos:26500` 附近)。所以投稿者的檔名塞不進 `git cat-file --batch-check` 的輸入。
   - 起點版本來自推送前掛鉤的 sha,不是投稿者可控的字串。
   - subprocess 一律用參數陣列,沒有 shell 插值。
   - `_ns_deleted_summary_lines` 補上 `--inter-hunk-context=0` 與 `--diff-algorithm=myers`,原有的 `--no-ext-diff --no-textconv` 都還在。它與 `_ns_diff`(`scripts/lumos:27319`)的旗標一致,所以沒有外部差異驅動的新入口。
   - 這一處沒有新增反序列化、eval、模板或路徑寫入。

2. 閘被繞過、放寬被濫用:已看,無。
   - `_ns_append_subtract` 改成只扣 `_NS_FRAG_KEY_RULES`(行號引用、釘版本),其餘整行規則一律照報。這讓放寬變窄,不是變寬。
   - 我試著想「舊行已有某片段的違規,括號再帶同一個片段」:舊違規與新違規進同一個 `pv`,計數只扣一次,第二個照報。所以不能用舊行的債掩護括號裡新寫的同片段。
   - 候選超過總量上限(`cap`)時回空配對表,整行照查,方向是偏嚴。`failed` 在 `cap` 時為假,只影響提醒與記帳,不影響判定。
   - NFC 與 NFD 並存:`_ns_nfc_clash_errs` 以 `_nodehome_list` 的第二個回傳值(逐筆 NFC 化、不去重)計數,再與有新行的筆記路徑交集,方向正確。第一層(`_note_shape_eval`)與第二層(`_note_audit_items`)都接上了。我查證了 `_nodehome_list` 的實作(`scripts/lumos:26155`),`allp` 確實不去重。
   - 申訴:`_note_audit_dispute_for` 讓只判句尾的申訴只換同一個 tail 的列。整行申訴仍換掉每一種範圍,這是原本的信任模型(申訴是人工覆核的出口),本輪沒有放寬。比上一版更窄,沒有新的放行路徑。
   - 申訴檔本身是否真由有權限的人寫:本輪沒改,審查範圍外。

3. 密鑰與個資進 log/帳/錯誤訊息:已看,無。
   - `capped`、`git-failed`、`error` 帳只含 sha、固定字串與例外類別名。
   - `_ns_relaxed_record` 重組後的 `pairs` 只含路徑與行號,不含行原文。
   - 新增的錯誤訊息與 stderr 提醒會印出投稿者控制的檔名。沒有跳脫是既有行為(`_note_shape_report` 一帶全部這樣印),本輪沒有新增這類型態,不另報。

4. 加密與傳輸:已看,無(本輪沒有相關改動)。

5. 執行邊界:已看,無。
   - 放寬帳去重改讀 `docs/.governance-log.jsonl`:只取 `gate`、`kind`、`attempt_id`、`pairs` 四個欄位做集合比對,不執行也不回顯內容。
   - 去重只影響「要不要再記一筆放寬帳」,不影響擋或放的判定。
   - `LUMOS_PUSH_ATTEMPT` 由掛鉤以時間加行程號產生(`scripts/hooks/pre-push:236`)。偽造同編號、預先寫入帳檔的人,需要自己就是能改本機帳檔的推送者,攻擊面沒有增加。
   - 推送者本人預先在本機帳檔寫假事件,只會讓放寬帳少記幾行。這不是外部投稿者能做到的事,也沒有放過任何違規。
   - `_ns_relaxed_recorded` 沒有像 `_drift_load_acks` 那樣拒絕捷徑檔。但讀到的內容只用於集合比對、不回顯,我給不出具體的外洩或執行路徑,所以不標。
   - 若帳檔裡剛好有同編號的畸形 `pairs`(例如元素是巢狀陣列),`tuple(x)` 會在 `got.update` 丟出 TypeError,被外層 `except Exception` 吞掉並印一句「放寬帳這次沒記成」。判定不受影響。要觸發得先能寫入帳檔,屬自傷,不構成攻擊。

6. 行動端:本案無。

7. 新依賴:無(diff 只用標準函式庫 `collections`、`hashlib`)。

8. 測試與文件部分:測試檔只在臨時專案裡造資料。skill 說明與筆記的文字改動沒有放寬 `LUMOS_SKIP_NOTE_SHAPE` 的使用條件,也沒有叫人繞過閘。

## 上輪修法的核對結論

- 「只扣照片段比的規則」收成一條規則,比逐條比規則名更不容易漏。已核對 `v[2] not in _NS_FRAG_KEY_RULES` 在取鍵之前就 `keep`。
- 總量上限新增位元組總和檢查:`_ns_append_read_blobs` 只累加不超過單篇上限的大小,超過單篇上限的篇本來就回 `None` 不讀,所以記憶體上界是 32 MB。這是 DoS 類,依規定不報;我只確認它沒有讓判定偏鬆。
- 放寬帳去重從 git 目錄記號檔改成讀治理帳:拿掉了一個可被投稿者預先放置或污染的檔案路徑(`<git 目錄>/lumos-relaxed-seen`)。比舊做法更小的攻擊面。

最高 severity:clean
