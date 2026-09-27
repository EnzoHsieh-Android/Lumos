preflight-4: ran

# r2 收貨紀錄(筆記形狀擋)

r1 處置閘 PASS,但 r1 折入 35 條(新增上線點截斷、合併處理、快照讀設定、抽取器擴充、來源標記改名),照「全折後修正差異要派新席」開 r2,5 席全新、只審修正差異(r2-delta.patch)與銜接處。首輪前掃四類清單已在 r1 跑過;本輪 refcheck 2 處全對、prose-lint 無命中。

## 席位收貨

- 5 席全交;等完成通知、ls 確認在,才讀。獨立性:4 席 Claude 過程紀錄沒開過別席報告或卷證目錄;外家席過程紀錄裡的卷證字樣只來自計劃原文。
- report-normalize 5 份皆已正規化。quote-check:4 份全錨定;邊界席 3 句有 1 句錨不到,該條發現另有錨定引句,且編排者重現成立(下表),照採。refcheck:外家、接手、正確性共 5 處不存在,都是審查員舉的假想路徑或把兩個行號寫在一起。
- 編排者重現:
  | 發現 | 重現 | 結果 |
  |---|---|---|
  | 抽取器先刪圍欄(邊界 F1) | `_node_code_ref_tokens` 抽取前呼叫 `_strip_fences_text`,後者不留圍欄內容 | HIT |
  | 合併函式只回真假(邊界 F2、外家 F4) | `_nodehome_merge_wrote_new_lines` 回 any(...) | HIT |
  | 上線點標記寫死(邊界 F3、架構 F1) | `_NODEHOME_GOLIVE_MARK` 是模組常數、`_nodehome_golive` 無參數 | HIT |
  | 釘版本被 refcheck 判不存在(正確性 F1、接手 F1) | 正確性席實跑 `_refcheck_scan` 回 missing;`_validate_repo_ref` 已有 at_sha 參數 | HIT |
  | lint 只掃 summary(接手 F3、架構 F2) | `context_marker_warnings(summ)` 唯一呼叫點 | HIT |
- 15 條全折(輪內有 blocker,不得放行);refuted 無。
