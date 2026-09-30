# r2 收貨紀錄(併發與效能表態要合約背書)

第二輪不做首輪前掃(只有首輪要求)。派工前機械排乾:refcheck 反引號路徑 6 條全在;prose-lint 掃到一處「之類」已改。

## 收貨三道(六席)

- report-normalize:六份皆已正規化。
- quote-check(對 r2-snapshot.md):邊界 14、整合 27、資源併發 16、簡化 12 全數錨定;正確性 1 條、架構對齊 1 條錨不到,見下表重現。
- refcheck:六份引的 file:line 全部存在。
- seat-check:六份皆「unreported r2.md」——報告逐字引用但沒寫出路徑字串,字串比對假陽性;正確性、架構對齊各 1 條 out_of_scope,即上述兩條錨不到的引句。只觀測不擋。

## 編排者重現

| 席位 id | 重現 | 結果 |
|---|---|---|
| C7 | 引句「…帶過來的值。」與快照「…帶過來的值)。」只差句尾標點;原句存在於〈寫表態時算背書〉 | HIT 採信 |
| AR4 | 引句「`contract_evidence` 為 `off` 或看不懂時」快照裡沒有這句,席位自註非原文 | MISS 不採信 |
| C1 Q1 Q5 Q8 AR5 G9 | 讀 `_codeloop_record_valid`:只比 rec_sha 與 marker_sha;kill-log 在簿記清單;背書計算原設計不看 commit | HIT 採信 |
| E1 C2 Q4 G1 AR3 | `cmd_guard_kill_add` 去重鍵 invariant/file/old;kill-log 寫入欄位無 old | HIT 採信 |
| E2 C5 G9 | kill-add 同鍵直接擋並要求手動拿掉舊的 | HIT 採信 |
| E3 Q3 | `_one` 例外被接成擋下;寫表態那段沒有 try | HIT 採信 |
| G4 | kill 整套跑時 detail 標弱證據但 verdict 仍 killed;kill-log 丟掉 detail | HIT 採信 |
| Q2 | kill 在迴圈外一次 open("a") 批次寫 | HIT 採信 |
| F3 Q7 G5 | kill-log commit 為迴圈外單一變數;gov 去重鍵含 commit | HIT 採信 |

refuted-set:AR4(引句錨不到且席位自註非原文;所指開關本輪已移除)。

## 折入後鏡像核對

派 haiku 核對鏡像段;它回報多處「舊說法殘留」,編排者對現檔 grep 逐項驗證為假(疑似讀成 r2-snapshot):`off / warn` 0 次、`evidence: "contract"` 0 次、「六個位置」0 次、「同一 node、同一 invariant、同一 file」0 次、「檔案順序最後一筆」0 次、「commit 改成」0 次;`contract_evidence` 只剩測試名;配方身分(invariant、file、old)、weak 定義、先提交再跑破壞測試、RETIRE-IF 分母皆在正文。編排者自行核對 summary 五行 WHY/RULE/REVISIT 與正文一致。此核對結果不採信。
