severity: major
<!-- 來源:codex exec 逐字稿的最終回覆本體(席位唯讀無法寫檔,由編排者原樣切出;完整逐字稿見 job tmp/codex-r1.log)。★第一版切法把逐字稿裡重複印出的同一份報告切了兩次,已改成只留最終那一份;內容一字未改★ -->

1. `visited` 事件可以混入判定狀態，消掉真正的待辦

severity: major
blocking: 是
位置：`scripts/lumos:11917`
引句:「elif o.get("event") in ("transition", "visited"):」

讀取端接受 `visited`，但 `_ledger_fold` 沒有檢查事件種類，只檢查三個粒度欄位是否有值。「visited 沒有鄰居與邊型」只是寫入端慣例，讀取端沒有保證。

記憶體實測：帳本中的 `visited` 若帶有 `neighbor`、`edge_type`、`from_decision_id`，即使沒有 `state`，仍會進入折疊結果。原本有一個鄰居的待判清單因此變成空清單，`visited` 的空單守衛隨之放行。doctor 的 E2 也會把該筆時間當成已判定時間，錯誤抑制提醒。相同事件在舊版會被忽略。

應在折疊入口明確限定 `event == "transition"`；巡過紀錄另供活動時間與「是否看過」判斷使用。

2. 起點筆記已不存在時，把無法展開誤判成空單

severity: major
blocking: 是
位置：`scripts/lumos:12550`
引句:「pending = _rel_cascade_pending(env, header, trans)」

header 檢查只要求 `node` 非空，沒有確認該路徑仍在圖譜。起點被刪除或改名後，指向舊路徑的引用進入 typed index 的 `ghosts`，不會成為 `_typed_hop1` 回傳的鄰居。

實測：header 指向不存在的 `Projects/Root.md`，另一篇筆記仍以 `verified_by` 引用它；索引明確留有這條 ghost 引用，但 `_rel_cascade_pending` 回傳 `[]`。新指令因而可以記下「零個待判鄰居」，消除尚未確認完成的待辦提醒。

應先確認起點可解析；不能展開時應拒絕銷帳，不能當作已確認為空。

3. 全部項目都是空白的條件清單會漏報

severity: major
blocking: 是
位置：`scripts/lumos:4354`
引句:「if not str(n.fields.get(_f) or "").strip():」

例如：

```yaml
revalidate_when:
  - ""
  - "   "
```

實際 parser 會產生 `['', '   ']`。它是非空 list，轉成字串後包含括號與引號，因此通過新檢查。實測 lint 回傳 `0 問題`，但掃描端既有 `_conds` 對相同內容回傳 `[]`，仍然沒有任何可掃描條件。`valid_under` 同樣受影響。

應使用逐項去空白後的結果判空，例如共用 `_conds`。裸空值、`[]`、純空白字串的提醒正常；數字字面值由現有 parser 保留為字串，這次沒有觀察到型別例外。

4. 前提空值測試命中檔名，無法驗出守衛被移除

severity: major
blocking: 是
位置：`scripts/test_lumos.py:42201`
引句:「"前提" in r.stdout or "valid_under" in r.stdout, r.stdout[:300])」

案例名叫 `Verification/前提空的.md`，而 lint 無論有無警告都會印出路徑。因此斷言中的「前提」可以只命中檔名。

用舊版 `cmd_lint` 實測，輸出：

```text
✓ lint Verification/前提空的.md — 0 問題
```

這條斷言仍為真。只移除 `valid_under` 的提醒、保留 `revalidate_when` 提醒時，新增測試無法抓住退化。

應比對警告本身，例如 `valid_under 是空的`。整段提醒還原成舊版時，第二個案例仍會翻紅，但註解宣稱第三個案例也會翻紅不成立。

驗證範圍：以上使用 patch 重建的記憶體版本及舊版函式比對，未修改檔案。兩支新增測試的函式本體未見零斷言成功路徑；未執行會建立暫存檔的完整測試程序。
