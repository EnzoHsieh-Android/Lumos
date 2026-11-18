severity: clean

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/170757806b0583f77f6270f87c61e53d00f5d3ae4258a1121b929ce0d3d7f2dc.json.warming` 不存在，沒有東西要刪或判斷。圖譜鏡頭備份 `lens-r4.txt` 沒有讀。派工詞附的「LUMOS-LENS」寫明這次沒有固定席節點，所以固定席逐條判無對象。

## 三問

1. **分層與依賴方向:對齊。**
   - 修補只動三處:`check.py` 的 `_choice_retired`、樣本 `choice-batch2.kt` 和型錄 C-34 一列。
   - `_choice_retired` 仍由 `choice_tables` 呼叫,也還是走既有的 `_CHOICE_RETIRED_RE`,沒有另讀帳本或另讀一次表。
   - 撤號比對仍交給既有的 `_choice_retired_problems`。
   - 引用位置:`configs/ast-grep/kotlin-android/check.py:1540-1541`。
2. **命名與錯誤處理:對齊。**
   - 錯誤訊息沿用同一個回傳格式 `(set(), "…")`,措辭沒變。
   - 樣本新增行沿用既有的 `// HIT C-34` / `// MISS C-34` 標記。
   - 註解引用「代碼審 r3 …」的寫法,跟同檔 `_choice_retired` 的「代碼審 code-選擇點第二批 r1 b2 g1」一致。
3. **第二種做法:沒有。**
   - 新正則 `C-[1-9][0-9]*` 沿用 repo 既有的「只收半形數字」寫法:scripts/lumos 的 `_PQ_ID_RE`、`_EXPECTED_CLAUSE_RE`、`_FINDING_SOURCE_NO_RE` 同一個形狀。
   - 同檔 `check.py:805` 用的是 `[1-9]\d*`,跟它不同,但那是風格偏好,不列。
   - 我另外想到的疑慮是列表的 `_CHOICE_ROW_RE` 仍是 `C-\d+`,會讓撤號守衛有洞。實測它補得住:列號寫成 `C-034` 時,既有檢查會報「規則 id 要等於列號」。所以這不構成漏洞,也不列為 finding。

## 已驗主張(同一輸入,修前與修後)

- **G2 repair 成立。**
  - 輸入:型錄「已撤列號:」那行分別寫成 `C-４０`、`C-040`、`C-４0`。
  - 預期:報「已撤列號那一行要寫…」,不靜默放過。
  - 修前 87093835:三者都沒有「已撤」類問題,靜默放過。
  - 修後 59c41038:三者都報該錯誤。
  - 歸因:有證據的修復。兩版在同一份 `choice_tables` 上跑出差異。
- **G2 preserve 與 G1 兩組:測試通過。**
  - `python3.14 scripts/test_lumos.py -k choice_table_batch2`:修前 13 個通過,修後 16 個通過。
  - `python3.14 scripts/test_lumos.py -k choice_samples_batch2`:修前、修後各 33 個通過。
  - 修後的測試只看到全綠。這不能證明 C-34 子句和 C-36/C-37 字面值清單「各拿掉一個都會翻紅」,那是編排者手動逐條拿掉的掃描,我沒有重跑,**G1 的拿掉翻紅:未判定**。
  - 引用:`r4-behavior-cases.md` 的「未覆蓋」段。

## 未驗範圍

- 沒有重現 `ast-grep` 規則本身(`api.yml`)對新樣本行的命中,也就是 G1 repair 的行為面。
- 沒有確認 `lumos gov` 的 `_choice_*` 統計與渲染在修補前後是否一致。

臨時副本已用字面絕對路徑刪除。

最嚴重:clean;blocking 共 0 條
不對齊共 0 條,其中 major 0 條
