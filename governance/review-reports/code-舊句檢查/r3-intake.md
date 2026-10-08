# r3 收貨紀錄(code-舊句檢查)

凍結材料:第 2 輪修正 b1e63672..89884251 的 git diff -U10(不含治理帳、錨點、卷證),1298 行,不拆;`r3-snapshot.patch`。第 3 輪(上限輪),全新席位、全編制。
9 席:正確性 opus、邊界、併發回滾、合約圖譜、spec 對照、架構對齊、資安 sonnet 5.5、外家 finder 與外家否決 Codex(gpt-5.6-sol xhigh)。

## 席位收貨

- 9 席全交,等完成通知、ls 確認後才讀;主 repo reflog 沒有新動作。
- report-normalize:9 份都已正規化。quote-check:9 份全數錨定。
- 發現 19 條(機器數):正確性 5、邊界 2、併發回滾 1、合約圖譜 1、spec 對照 2、架構對齊 1、資安 2、外家 finder 3、外家否決 2;major 3 條(正確性 F1、外家否決 F1 F2)。

## 判讀

- 正確性 F1、外家否決 F1(major)與邊界 F2、資安 F1 同一件事:第 2 輪編排者裁定「跳過超長行算判不了」範圍太寬,跟消失名稱無關的超長行也讓 block 擋、而且無法表態;兩週帳還把它當判完。收窄:只有行內以子字串出現消失名稱的超長行才算判不了,其他只計數並印位置,照計劃「讀不出的筆記:沒改到的只印」同一原則。這是編排者上一輪裁定的副作用,本輪修正。
- 外家否決 F2(major)與外家 finder F2、邊界 F1、正確性 F2 同一類:只擋方向控制與零寬字元不夠,tab、換行、ESC、分行字元也會讓照貼指令指錯。改成含 Unicode 類別 Cc、Cf、Zl、Zp 或非 UTF-8 就不印照貼指令。
- 外家 finder F1 與併發回滾 F1 同一件事(Windows 上收權限失敗):席位都未能在真 Windows 重現,編排者讀程式確認收權限失敗會丟例外,採信,折成失敗不當錯。

## 機械重現(在審的那一版 89884251 上;方法:折入後的新測試格,把修法還原就翻紅,先證明現場成立)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性-F1 | 無關的超長行也算判不了 | HIT:`t_drift_m1_review_r3_long_lines_narrowed` ①② 紅 |
| 外家否決-F1 | 同正確性-F1;不印位置 | HIT:同上 紅 |
| 邊界-F2 | 同正確性-F1 | HIT:同上 |
| 資安-F1 | 同正確性-F1 | HIT:同上 |
| 正確性-F4 | 只在判完時印超長行計數 | HIT:同上 ④ 紅 |
| 外家否決-F2 | 判準改回只看方向控制與零寬 | HIT:`t_drift_m1_review_r3_paste_special_chars` 紅(逐類各一例) |
| 外家finder-F2 | 同外家否決-F2 | HIT:同上 |
| 邊界-F1 | 同外家否決-F2 | HIT:同上 |
| 正確性-F2 | 同外家否決-F2 | HIT:同上 |
| 資安-F2 | 剖不動那行路徑不跳脫 | HIT:`t_drift_m1_review_r3_terminal_escapes` 紅 |
| 正確性-F3 | 同資安-F2;工具出錯訊息不跳脫 | HIT:同上 紅 |
| 正確性-F5 | 舊句檢查設成 block 又唸 | HIT:`t_drift_m1_review_r3_doctor_parent_and_block` 紅 |
| 外家finder-F3 | 父層寫壞時不講舊句檢查狀態 | HIT:同上 紅 |
| 外家finder-F1 | 收權限失敗當錯 | HIT:`t_drift_m1_review_r3_chmod_unsupported` 紅 |
| 併發回滾-F1 | 同外家finder-F1 | HIT:同上 |
| 架構對齊-F1 | 不驗寫入長度 | HIT:`t_drift_m1_review_r3_ledger_miss_short_write` 紅 |
| spec對照-F1 | 讀計劃 kind 對照與 RETIRE-IF | HIT;補齊 |
| spec對照-F2 | 讀計劃那條翻紅說法 | HIT;改成實際還原方式 |
| 合約圖譜-F1 | 讀計劃 r1 折入節 | HIT;兩句標已撤回 |

## 處置

- 19 條全折(folded),accepted 空、refuted 空。修正在 73d55192。前幾輪的還原翻紅在新程式上重跑全紅;三組驗收資料重跑仍與參考實作 P4r3 逐筆相同。

## 到頂之後(編排者裁定,2026-09-30;Enzo 當日授權編排者決策,這條線前兩個功能也是同樣做法)

- 第 3 輪是上限輪、有 major 且全折;修正差異(89884251..73d55192)沒有新席看過。照「修正差異要派新席」的紀律,破例開一小輪驗收(r4):3 席(正確性 opus、資安 sonnet、外家否決 Codex),只看這次差異;r4 若再有 major,不再修,停下攤給 Enzo 裁。
