# r1 收貨紀錄(code-舊句檢查)

凍結材料:25f6a459..620a6f73 的 git diff -U10(不含治理帳),2978 行,超過 1800 行,拆成 `r1-snapshot-code.patch`(1773 行:scripts/lumos 與筆記、說明頁)與 `r1-snapshot-tests.patch`(1178 行:scripts/test_lumos.py)分給不同席;完整一份 `r1-snapshot.patch` 留作凍結紀錄。
分級:pitfalls --diff 判 high;沒有適用的棧別題。
9 席:正確性 opus、邊界、併發回滾、合約圖譜、spec 對照(審 tests 那份)、架構對齊、資安(審完整一份)sonnet 5.5、外家 finder 與外家否決 Codex(gpt-5.6-sol xhigh,唯讀沙盒)。
偏離:實作在會談外的複製倉庫;派工鏡頭由編排者先跑 dispatch-lens 存檔(`r1-graph-lens.md`)。

## 席位收貨

- 9 席全交,等完成通知、ls 確認後才讀。邊界席初交少了圖譜鏡頭逐條判定一節,退回原席自己補(只加那一節)。
- 資安席自報:一條指令 cwd 沒對,在主 repo(不是被審的複製)跑了 `git add -A`,提交被 pre-commit 擋下後 `git reset -q` 還原。編排者唯讀核對:主 repo 工作樹沒變、當時沒有暫存的東西;但 pre-commit 在主 repo 治理帳追加了 3 行(08:55,其中一筆 nodehome blocked),Enzo 裁定刪掉,已刪。被審的複製 reflog 只有實作者的提交。
- report-normalize:9 份都已正規化。quote-check:9 份全數錨定(spec 對照對 tests 那份、資安對完整一份、其餘對 code 那份)。
- 發現 21 條(機器數):正確性 1、邊界 2、併發回滾 3、合約圖譜 2、spec 對照 6、外家 finder 2、外家否決 2、架構對齊 1、資安 2;major 8 條(正確性 F1、外家 finder F1、外家否決 F1 F2、架構對齊 F1、spec 對照 F1 F2、資安 F1)。

## 判讀

- 外家 finder F1 與外家否決 F1 同一件事(沒副檔名的 Python 腳本失去 shebang 或換格式時,舊定義整批漏查),兩家獨立一致,直接折。
- 外家否決 F2、外家 finder F2、邊界 F2、資安 F2 同一類(候選名稱與表態名稱正規化不同、有些名稱照貼提示也表態不掉):改成候選與 `--name` 共用一支正規化,過不了的不列、計數。
- 資安 F1 與邊界 F1 同一類(名稱比對沒有時間上限、長行時間平方成長):每行看截止時間、單行長度上限、只拿可能命中的名稱比對。
- 正確性 F1(非 UTF-8 檔名讓寫帳當掉、連 warn 都擋):路徑與名稱照既有轉義寫帳;m1 整段兜底成新狀態 `error`,warn 回 0。
- 架構對齊 F1 席位自標「靜態證據、輸出等價」:編排者讀 `_drift_probe_changes` 說明確認「手刻第二份解析」是先前架構席收斂掉的形狀,採信,改用共用 `_nodehome_name_status`。

## 機械重現(在審的那一版 620a6f73 上;方法:折入後的新測試格,把修法還原就翻紅,先證明現場成立)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性-F1 | 路徑不轉義 / 拿掉兜底 | HIT:`t_drift_m1_review_r1_non_utf8_and_guard` 紅(用 git 底層指令造非 UTF-8 檔名) |
| 資安-F1 | 拿掉單行上限 / 逐行候選漏一類 / 切句終點偏一格 | HIT:`t_drift_m1_review_r1_scan_budget` 紅(3 萬名稱加超長行) |
| 邊界-F1 | 同資安-F1 | HIT:同上 |
| 外家否決-F1 | 只看終點版判 Python | HIT:`t_drift_m1_review_r1_shebang_either_side` 紅 |
| 外家finder-F1 | 同外家否決-F1 | HIT:同上 |
| 外家否決-F2 | 候選端改回只擋控制字元 | HIT:`t_drift_m1_review_r1_name_canon` 紅(照貼提示表態後那一行不再列) |
| 外家finder-F2 | 同外家否決-F2 | HIT:同上 |
| 邊界-F2 | 同外家否決-F2 | HIT:同上 |
| 資安-F2 | 同外家否決-F2 | HIT:同上 |
| 架構對齊-F1 | 改回手刻解析 | HIT:`t_drift_m1_review_r1_shared_parsers` 紅 |
| spec對照-F1 | 家只看終點樹 | HIT:`t_drift_m1_layers_and_mode` ⑧ 紅 |
| spec對照-F2 | 不明傳終點 | HIT:`t_drift_m1_events_and_budget` ⑨ 紅 |
| spec對照-F3 | 只列出層表態、名稱排序去重各改回 | HIT:`t_drift_m1_ack_binds_name` ⑧ 紅 |
| spec對照-F4 | 十項沒測到的行為各改回一次 | HIT:`t_drift_m1_review_r1_spec_gaps`、`t_drift_m1_review_r1_shebang_either_side` 紅 |
| spec對照-F5 | 範圍宣告字與含子節三種改回 | HIT:`t_drift_m1_history_filters` ⑩ 紅 |
| spec對照-F6 | 同 spec對照-F4 | HIT:同上 |
| 併發回滾-F1 | 群組可寫也擋 | HIT:`t_drift_m1_review_r1_ledger_kinds_and_umask` 紅 |
| 併發回滾-F2 | 沒有起點改回記 skipped | HIT:同上 紅 |
| 併發回滾-F3 | gov 去重鍵不帶 check | HIT:同上 紅 |
| 合約圖譜-F1 | 說明改回去 | HIT:`t_drift_m1_review_r1_spec_gaps` ⑧ 紅 |
| 合約圖譜-F2 | 讀存量漂移守衛那句 | HIT;照改完的 gov 行為重寫 |

## 處置

- 21 條全折(folded),accepted 空、refuted 空。修正在 314b2347。三組驗收資料重跑仍與參考實作 P4r3 逐筆相同(9 題 487/97、rtb 182 提交 91/20、工具鏈 300 提交 1/0)。
- 實作者自報沒釘住:快取檔不是自己的(要換使用者身分才造得出);`drift fix --keep` 只測到名稱為 None。
