# r2 收貨紀錄(code-舊句檢查)

凍結材料:第 1 輪修正 0bc9a726..b1e63672 的 git diff -U10(不含治理帳、錨點、卷證),1970 行,拆成 `r2-snapshot-code.patch`(1284 行)與 `r2-snapshot-tests.patch`(686 行);另附重定基底衝突解法 `r2-rebase-rangediff.txt`(195 行,`git range-diff 25f6a459..620a6f73 eb2a00fd..0bc9a726`)。三份合成一份 `r2-snapshot-all.txt`(2165 行)當這輪的凍結紀錄(引句比對與記帳都對它)。
背景:第 1 輪之後主線推了「存量漂移檢查預設改成擋」(Enzo 裁定),這批重定基底到 eb2a00fd,三個提交分開保留。
6 席:正確性 opus、邊界、spec 對照(審 tests)、架構對齊、資安(審完整)sonnet 5.5、外家否決 Codex(gpt-5.6-sol xhigh)。派工詞把「第一個動作先 cd 到自己的臨時目錄、任何 git 都帶 -C」放在操作限制第一條(上一輪資安席在主 repo 誤跑 git)。

## 席位收貨

- 6 席全交;主 repo reflog 沒有新動作。架構對齊席初交少了圖譜鏡頭逐條判定一節,退回原席自己補(只加那一節)。
- report-normalize:6 份都已正規化。quote-check:對 `r2-snapshot-all.txt` 全數錨定(正確性、架構對齊兩席同時引了 code patch 與 range-diff,單對其中一份錨不齊)。
- 發現 12 條(機器數):正確性 3、邊界 1、spec 對照 2、架構對齊 2、資安 3、外家否決 1;major 2 條(spec 對照 F1、架構對齊 F1)。

## 判讀

- 架構對齊 F1(major)、資安 F2、邊界 F1 同一處:第 1 輪為了 umask 002 在 `_trusted_private_dir` 加了只給 m1 用的 `group_ok` 放寬,一支函式兩套判準;同群組的人能改名換快取、放 FIFO 卡住掛鉤。三席獨立一致,折:撤回放寬,umask 問題改成新建目錄一律明給 0700(套到所有鄰居)。
- 資安 F1:超長行不看會被拿來藏舊句,擋模式照既有「判不了算要處理」。
- 正確性 F1 與架構對齊 F2 同一段(doctor 的 old_sentence 提醒接在 gate 那行、用子字串拆):old_sentence 獨立一行、結構化來源。

## 機械重現(在審的那一版 b1e63672 上;方法:折入後的新測試格,把修法還原就翻紅,先證明現場成立)

| 發現 | 做法 | 結果 |
|---|---|---|
| 架構對齊-F1 | 群組可寫又放行 / 新建層不明給 0700 | HIT:`t_drift_m1_review_r2_strict_home_dirs` 紅 |
| 資安-F2 | 同架構對齊-F1 | HIT:同上 |
| 邊界-F1 | 拿掉 O_NONBLOCK | HIT:同上 紅(卡住被 alarm 殺) |
| spec對照-F1 | 入口改回不經兜底 | HIT:`t_drift_m1_review_r2_entry_guard` ①② 紅 |
| spec對照-F2 | 讀計劃帳欄位段 | HIT;統一成六種狀態、補欄位 |
| 正確性-F3 | 拿掉 m1 擋下時那句 | HIT:`t_drift_m1_review_r2_entry_guard` ③④ 紅 |
| 資安-F1 | 超長行不算有東西 / 結論行照舊 | HIT:`t_drift_m1_review_r2_long_lines_count_as_unknown` 紅 |
| 資安-F3 | 印出不跳脫 / 照印指令 | HIT:`t_drift_m1_review_r2_bidi_paths` 紅 |
| 外家否決-F1 | 桶裡不看時間 / 建索引不看時間 | HIT:`t_drift_m1_review_r2_budget_in_loops` 紅 |
| 正確性-F1 | 拿掉 old_sentence 那行 | HIT:`t_drift_m1_review_r2_doctor_old_sentence` 紅 |
| 架構對齊-F2 | 改回子字串拆 | HIT:同上 紅 |
| 正確性-F2 | 讀 commands/08 | HIT;照實際回傳碼改寫 |

## 處置

- 12 條全折(folded),accepted 空、refuted 空。修正在 89884251。前兩輪的還原翻紅在新程式上重跑仍全紅(r1 那條「群組可寫也擋」隨放寬撤回作廢,由本輪三條頂上)。三組驗收資料重跑仍與參考實作逐筆相同。
- 代價(照裁定接受、寫進筆記):別人建的 0775 `~/.cache` 照樣不信,那台機器上舊句檢查不用快取、每次冷跑;umask 修法是共用函式,vault-lock、dispatch-lens、bound-filter 新建的目錄也一起變成只給自己讀寫。
