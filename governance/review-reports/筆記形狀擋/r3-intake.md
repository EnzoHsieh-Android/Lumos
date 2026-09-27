preflight-4: ran

# r3 收貨紀錄(筆記形狀擋,最後一輪)

r2 處置閘 PASS;r2 折入 15 條且新增喚醒檢查、裸文字規則、釘版本拆解,照「修正差異要派新席」開 r3(上限第 3 輪),4 席全新、只審 r2 修正差異(r3-delta.patch)。refcheck 2 處全對、prose-lint 無命中。

## 席位收貨

- 4 席全交;等完成通知、ls 確認在,才讀。獨立性:3 席 Claude 過程紀錄沒開過別席報告或卷證目錄;外家席沒有。
- report-normalize 4 份皆已正規化。quote-check:3 份全錨定;架構對齊席 2 句有 1 句錨不到,該條發現跟邊界席獨立撞同一件事且編排者重現成立,照採。refcheck:外家席 4 處不存在,都是它舉的假想路徑。
- 編排者重現:
  | 發現 | 重現 | 結果 |
  |---|---|---|
  | 捏造提交通過釘版本(正確性 F1) | `_git_tree_has` 只做 `git cat-file -e sha:path`,不看可達性;席位在臨時目錄以 commit-tree 實測 | HIT |
  | 回傳形狀炸既有使用者(邊界 F1、架構 F1) | `_nodehome_refs` 與 `_node_code_ref_tokens_all`、`_home_confirmed` 都用 `for t, _l in full` 兩欄拆 | HIT |
  | 淺層 clone 退回空樹(邊界 F2) | pre-push 新分支算法在找不到上一個提交時退空樹;上線點用 `git log -S` 在淺層歷史搜不到 | HIT(席位在臨時目錄實測) |
  | FLOW/DEP 接進 lint 會噴舊帳(邊界 F3) | `_CONTEXT_MARKER_RULES` 前的註解明記 277 行舊 FLOW/DEP 與 REVISIT 2026-11-21 | HIT |
  | d7 仍把加鎖給第一層(外家 F4) | Issue d7 內容 | HIT(已以 d8 取代) |
- 13 條全折(輪內有 blocker,不得放行);refuted 無。
