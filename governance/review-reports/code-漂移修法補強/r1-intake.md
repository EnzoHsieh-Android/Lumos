# r1 收貨紀錄(code-漂移修法補強)

凍結材料:9cc20926..b52d6f02 的 git diff -U10(不含治理帳),1302 行,不拆;`r1-snapshot.patch`。
分級:pitfalls --diff 判 high,沒有適用的棧別題。
9 席:正確性 opus、邊界 sonnet 5.5、併發回滾 sonnet 5.5、合約圖譜 sonnet 5.5、spec 對照 sonnet 5.5、架構對齊 sonnet 5.5、資安 sonnet 5.5、外家 finder 與外家否決 Codex(gpt-5.6-sol xhigh,唯讀沙盒)。
偏離:實作在會談外的複製倉庫;派工鏡頭由編排者先跑 dispatch-lens 存檔(`r1-graph-lens.md`)交給各席——9cc20926 不在主線上,鏡頭改用主線分岔點 bb0be7e1 起算(多含兩個只改筆記的提交)。

## 席位收貨

- 9 席全交,等完成通知(Codex 等背景行程結束)、ls 確認後才讀;impl 的 reflog 只有編排者與實作代理人的提交。
- report-normalize:9 份都已是正規化格式。quote-check:8 份全數錨定;併發回滾席 clean、沒有引句(無 finding,不適用)。
- 發現 15 條(機器數):正確性 2、邊界 3、合約圖譜 1、spec 對照 4、架構對齊 1、資安 1、外家 finder 1、外家否決 2、併發回滾 0;major 3 條(外家 finder F1、外家否決 F1 F2)。

## 判讀

- 外家否決 F1(消費專案按檔名跳過,使用者改過的工具檔也被漏看)推翻了設計審 r3 放行的「刪除守衛純路徑判斷」。設計審可以附理由放行 major,代碼審不行;席位附的重現成立(使用者改過的 pre-push 刪名稱 → tokens 空)。裁定:跳過集合改成既有 `_vendored_state` 的原封不動工具檔(指紋對得上安裝清單),清單不在一支都不跳。計劃第 5 節、S5、誠實界線、RETIRE-IF ② 同步改寫。資安 F1(把自己的檔改名成工具檔名)同一條修法加「刪除行照來源路徑判」一起收。
- 外家 finder F1(改名只看目的路徑):修成來源、目的路徑分開記;工具檔改名搬走時來源已不在工作目錄 → 不算原封不動 → 照抽(寧可多掃;席位預期的是跳過,編排者判跳過需要再讀一次舊版指紋,多掃方向安全,理由寫進註解)。
- 外家否決 F2、正確性 F2、邊界 F2(NFC 印出):三席獨立一致,直接折。

## 機械重現(在審的那一版 b52d6f02 上;方法:折入後的新測試格,把修法還原就翻紅,先證明現場成立)

| 發現 | 做法 | 結果 |
|---|---|---|
| 外家否決-F1 | 跳過集合改回整份清單 | HIT:`t_delguard_skips_vendored_toolkit` ③⑥⑦紅 |
| 資安-F1 | 自己的檔改名成工具檔名、刪除行照目的路徑判 | HIT:`t_delguard_vendored_rename_and_count` ③紅 |
| 外家finder-F1 | 刪除行改回照目的路徑、不讀 rename from | HIT:同上 ②③④紅 |
| 外家否決-F2、正確性-F2、邊界-F2 | 改回印 NFC、照 NFC 去重 | HIT:`t_drift_c4_code_review_r1` ③④⑤紅 |
| 正確性-F1、spec對照-F3 | 拿掉去重、門檻改 >=3 / >0、code- 只算同提交 | HIT:同上 ②③紅 |
| spec對照-F2 | c1 改回逐句接說明 | HIT:`t_drift_fix_c1_missing_tail_once` ②紅 |
| spec對照-F4 | 第一遍不跳、只要碰到就記支數 | HIT:`t_delguard_vendored_rename_and_count` ③④⑤紅 |
| 架構對齊-F1 | 正則少認一個佔位字 | HIT:`t_drift_c4_code_review_r1` ⑥紅 |
| 合約圖譜-F1 | 說明改回舊句 | HIT:同上 ⑦紅 |
| spec對照-F1 | 讀計劃與程式 | HIT:計劃句子改成跟程式一致(只在 git 失敗時印) |
| 邊界-F1 | 拿掉變體檢查 / sha 分大小寫 | HIT:`t_set_conditions_blocks_placeholder_variants` ② 紅(另 ③ 釘合法角括號照收) |
| 邊界-F3 | 拿掉 20 個上限 / 上限改 19、21 / 不印指令 | HIT:`t_drift_c4_dirs_capped_at_20` ②③④ 紅 |

## 處置

- 15 條全折(folded),accepted 空、refuted 空。13 條在 b002ca4a;邊界-F1、邊界-F3 編排者原想附理由放行(佔位字變體要人手打錯、證據頁是人主動叫出),但代碼審同輪有 major 時 accepted 必須為空,改折,在 9a261f20(set 擋佔位字的打錯變體;證據頁卷證目錄最多列 20 個並給列完整清單的指令)。
- 另:實作代理人回報從主線分岔點算有 21 條新增告警,全在舊句偵測實驗程式(不在本功能範圍),推送前另外處理。
