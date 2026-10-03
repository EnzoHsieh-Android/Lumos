# code-回頭條件寫法補齊 r1 收貨

審材:r1-snapshot.patch(60a39f02..功能提交,不含卷證與帳本,1010 行)。分級 standard:正確性一席(派工詞帶角色卡標記)加架構對齊一席。兩席引句全錨,全是 minor,共 6 條。

## 依根因分組(全部折)

1. 引號判定(C1):落單的引號(`5"`)讓同一行後面的句中 REVISIT 被當成在引號裡 → 引號要後面真的有收才算(整行先記每種收引號最後出現的位置,仍是一遍掃)。
2. 提早結束(Z1):格式壞損的行直接回傳,同一行的句中 REVISIT 要第二次提交才報 → 壞損照報、繼續看句中。
3. 範圍一致(Z2、Z3):結案文法延到開頭欄位、但日期與條件文法不延;「寫在不評估的地方」的條件式三處各寫一份 → 抽成一支 `_revisit_dead_place`,三處共用;結案文法只在正文與摘要的非表格行查(同鄰居規則;開頭欄位裡寫錯的結案標記本來就不生效)。
4. 用語(C3):Z 段說「N 處」實際數的是行 → 改成「N 行」,計劃 [S5] 同步。
5. 綁定(C2):[S9] 說 E5 提示要提到結案寫法,綁的測試沒驗 → [S9] 加綁 `t_doctor_revisit_reminder`(它逐字驗新提示)。

## 重現表

| id | 怎麼查 | 結果 | 去向 |
|---|---|---|---|
| C1 | `_revisit_misplaced('長 5" 的管子。REVISIT:2026-10-05 x')` 回空清單 | HIT | 折(第 1 組) |
| C2 | 讀 `t_revisit_closed_issue_listing` 沒驗 E5 提示 | HIT | 折(第 5 組) |
| C3 | 讀 `_drift_doctor_lines` 數的是 `_revisit_misplaced_lines` 的行數 | HIT | 折(第 4 組) |
| Z1 | 讀 `_ns_revisit_violations` 的 bad 分支直接 return | HIT | 折(第 2 組) |
| Z2 | 席位實測開頭欄位 `- REVISIT:… [closed:2026-13-45 …]` 報結案寫錯、壞日期不報 | HIT | 折(第 3 組) |
| Z3 | 讀 `_probe_lines`、`_ns_revisit_violations`、`_revisit_misplaced_lines` 三處條件式 | HIT | 折(第 3 組) |
