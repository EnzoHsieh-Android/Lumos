### ext-f6
severity: clean
引句:「promote 全部操作(locate/remove/dedup/寫後 expected_check)一律用正規化 tuple 比對,不用逐字」
佐證:file: `governance/review-reports/dref-v4/r3-snapshot.md:140`
說明:已解。promote 的定位、移除、去重及寫後計數全部明定共用 `_dref_same`；expected_check 也分別要求正欄正規化命中恰一份、AI 欄命中零份，落盤只留一份正規形。以正規形已存於 `_ai`、呼叫端傳等價簡寫重試，不能再造成雙欄各留一份並錯誤通過。另試繞批次振盪：相一可冪等重跑，相二完成後禁止再進 add-ai；在明列單次批次且誠實承認無機械擋的邊界內，相序足以關住人剪後重加，週期重跑亦已列為 future 並設重審條件。

### ext-f7
severity: clean
引句:「所有原語的 ref 比對(backlog 集合差/candidates 去重/add-ai 冪等/prune 定位/promote locate·remove·dedup·count·覆蓋掃描)一律走同一支 `_dref_same` 正規化 helper」
佐證:file: `governance/review-reports/dref-v4/r3-snapshot.md:138`
說明:已解。覆蓋掃描已被明列納入同一正規化 helper，口徑不再含糊。再試無 id 決策：規格要求直接複用 E2 判準、排除 related，並把無 id 翻案決策獨立列為更重警訊，提示先 reindex 或明知會被壓掉仍蓋章；它不會被 candidates 的有-id限制漏掉。提醒雖不阻擋 promote，但這是明示的人裁 advisory，未發現新的靜默繞過。

結論:否決解除。
