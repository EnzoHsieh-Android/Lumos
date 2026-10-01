preflight-4: ran

# 設計審第 1 輪前置掃描收貨:殺傷力配方修補體驗

前掃報告原樣存 r1-preflight.md。①②③與存在類命中直接修真檔;④語意類命中修真檔並逐條留痕如下(修改前 → 後)。本計劃沒有「核心裁定」節,沒有要升級交席位審的。

| # | 類 | 命中 | 修改前 → 後 |
|---|---|---|---|
| p1 | ④語意(硬傷) | guard kill 結果裡既有的 recipe_id 是 `_kill_recipe_key` 算的,配方格式壞時跟 kill-rm 用的 `_kill_recipe_id` 不同,而且結果是 `{**原配方, …}`、事後還原不出原配方 | 「行尾加 id(同一支 `_kill_recipe_id`)」→「建結果時用原配方算 `_kill_recipe_id`,存成底線開頭旁路欄、`--json` 前濾掉;放在 [<test>] 之後、說明之前」;S3 補「格式壞的配方也一樣」「各筆結果的欄位跟改動前相同」 |
| p2 | ④語意(不精確) | `t_guard_kill_rm` 沒有斷言比對舊壞法 | 「斷言要改」→「不用改,S1 是新增反向斷言」 |
| p3 | ④語意 | `--id` 是 argparse required、驗證順序在找筆記之前、列出要不要拿鎖沒寫 | 〈做法〉補:argparse 改選填、開頭分流、列出走唯讀不拿鎖、各錯誤回傳碼 |
| p4 | ④語意 | 不是物件的元素沒有平台/檔/原文可印 | 補「整個印 `_kill_show(json 原樣)`」 |
| p5 | ①未定義 | P2、S7 字面、原文開頭、完整內容、健康檢查 | P2 首次出現加說明;S7 改寫成三句說明字面;原文開頭寫明前 30 字;完整內容寫明是哪一行;健康檢查改 doctor P2 段 |
| p6 | ③軟矛盾 | 「只做 2、3」與實際三項、RETIRE-IF「第二條」編號含混 | 改用功能名 |
| p7 | ②漏列 | 要同步的文件沒列 | 〈實務隱患〉補 guard-kill、skill 06、HELP_WHEN 與 argparse help |

# 設計審第 1 輪席位收貨

4 席全收齊後才動計劃。四道機械檢查:4 份都已是正規化格式;quote-check 全錨;refcheck 全數對得上;seat-check 派工單材料為空(vacuous)。兩欄全部一致。repo 根 reflog 無異動(席位都在自己的 clone)。

finding 編號:c=正確性-opus、h=接手-sonnet、b=邊界-sonnet、a=架構對齊-sonnet。

| 編號 | 席 F | 等級 | 重現 | 處置 |
|---|---|---|---|---|
| c1 | 正確性 F1 | major | HIT(席位實跑:`--new` 留待填字樣 → kill-add rc0、guard kill 判強殺回 0);多席獨立一致(h2、b6) | 折:kill-add 擋待填字樣,新條款 S4 |
| c2 | 正確性 F2 | minor | HIT(同 b1、h1) | 折:S3 縮成有印出結果行的;另開 Issue |
| c3 | 正確性 F3 | minor | HIT | 折:列出格式逐欄定義 |
| c4 | 正確性 F4 | minor | HIT | 折:以 is None 分流,空字串照舊擋 |
| c5 | 正確性 F5 | minor | HIT | 折:更正 worktree 測試前提,S3 測試斷言一行一條 |
| c6 | 正確性 F6 | minor | HIT | 折:分組前一次算好短身分 |
| h1 | 接手 F1 | major | HIT(席位實測 file 數字、非物件、invariant 數字都崩潰) | 折:同 c2 |
| h2 | 接手 F2 | major | HIT | 折:同 c1 |
| h3 | 接手 F3 | major | HIT(讀規格:缺欄與截字順序未定) | 折:同 c3 |
| h4 | 接手 F4 | minor | HIT | 折:S1 只對範本那一行斷言 |
| h5 | 接手 F5 | minor | HIT | 折:同 c6、c5 |
| h6 | 接手 F6 | minor | HIT | 折:節點寫法用 _kill_node_arg;is None;重複合一行;RETIRE-IF 寫明來源 |
| b1 | 邊界 F1 | major | HIT(席位實測四種崩潰) | 折:同 c2 |
| b2 | 邊界 F2 | minor | HIT | 折:同 c4 |
| b3 | 邊界 F3 | minor | HIT | 折:同 c3 |
| b4 | 邊界 F4 | minor | HIT | 折:重複配方合成一行並註明會一起移除 |
| b5 | 邊界 F5 | minor | HIT(席位實測 test 名夾換行偽造 id) | 折:id 放在人寫欄位前面 |
| b6 | 邊界 F6 | minor | HIT | 折:同 c1;S1 只對範本那一行 |
| a1 | 架構對齊 F1 | minor | HIT | 折:PRIOR-ART 記不另開 kill-list 的取捨 |
| a2 | 架構對齊 F2 | minor | HIT | 折:--json 濾掉所有底線開頭欄、分組前算好 |

重現不到而沒折的:無(refuted-set none)。放行的:無。
