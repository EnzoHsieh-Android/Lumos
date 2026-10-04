# r1 收貨(code-gov-ledger-split)

8 席(正確性、邊界、整合、併發、回滾 五鏡頭,加架構對齊、資安、對答案)全部 sonnet,收齊才動工作目錄;各席實驗都在 /tmp,沒動 repo。report-normalize 都不用改;quote-check 邊界席 3 句有 2 句錨不到(它的發現與其他席重疊,編排者自己重現),其餘全數錨定。正確性席與架構對齊席各報一條重大,本輪一律折,不放行。外家席照 2026-09-30 裁定預設不派,結論是單家族視角。

## 去重後的發現

| id | 來源席 | 一句話 |
|---|---|---|
| X1 | 正確性 F1、邊界 F2、整合 F1 | 度量撤除條件:本機帳不在時暖機護欄只看版控帳而放行,走本機帳的閘數成 0 筆、誤報該撤 |
| X2 | 架構對齊 F1、正確性 F3、併發 F1、邊界 F1 | 兩本合讀另寫一套 splitlines 解析與時間解析,U+2028/U+0085 整筆丟、深層巢狀壞行拋 RecursionError |
| X3 | 邊界 F3、整合 F2 | 本機帳已被追蹤時 doctor 不提醒 |
| X4 | 正確性 F2、回滾 F2 | 沒有 docs/ 的佈局,doctor 叫人跑 lumos update 卻補不了忽略行 |
| X5 | 回滾 F1 | 〈回退〉只講本 repo 先刪,沒講每個 worktree、每台機器各一份,刪除不可逆 |
| X6 | 併發 F2、架構對齊 F2 | 兩個程序同時補 .gitignore 會補兩份;就地追加是專案第一種寫法 |
| X7 | 併發 F3 | 合讀整本讀,沒有版控帳讀者那樣的檔尾上限 |
| X8 | 併發 F4 | 兩本之間被 kill 的狀態走查(該席自己判不是缺陷) |
| X9 | 資安 F1 | 本機帳或 docs/.gitignore 是被提交進來的捷徑時,工具會跟過去寫到 repo 外 |
| X10 | 資安 F2 | 被強制提交的本機帳裡的偽造事件會被統計讀者採信 |
| X11 | 架構對齊 F3 | 路徑函式叫 local 卻也拿來組版控帳路徑,簽章也沒比照 _ci_log_path |
| X12 | 架構對齊 F4 | 測試輔助 _m1_events 把 dict 轉字串再轉回來 |
| X13 | 對答案 F1 | 〈做法〉7 的 lumos-cli-read 使用紀錄帳檔名沒改 |

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| X1 | t_gov_split_review_r1_fixes ①:版控帳一筆 100 天前、本機帳一筆兩天前的 check-s.warned,刪掉本機帳再問度量段 | HIT:舊程式列出「該撤」 |
| X2 | 同測試 ②:一筆 note 帶 U+2028/U+0085、再加一行 20 萬個左中括號 | HIT:舊程式拋 RecursionError |
| X3 | 同測試 ③:git add -f 本機帳後問 _local_ledger_doctor_msgs | HIT:舊程式回空清單 |
| X4 | 回滾席 /tmp/rbx 實跑:vault 在根目錄下,doctor 提醒跑 update,update 不補 | HIT |
| X5 | 讀〈回退〉原文對照〈天花板〉第 2 點 | HIT:沒提其他 worktree |
| X6 | 併發席兩執行緒 barrier 實測 | HIT:兩行重複加一個空行 |
| X7 | 併發席 30 萬行 76MB 實測 1.3 秒、整本進記憶體 | HIT |
| X8 | 讀 _append_governance_log 先寫版控批再寫本機批 | MISS:中途被 kill 只會少例行觀察,不會重複或誤算,該席自己判非缺陷 |
| X9 | 同測試 ④:本機帳與 docs/.gitignore 換成指向 repo 外的捷徑 | HIT:舊程式寫進捷徑指的檔 |
| X10 | 讀程式:統計讀者讀本機帳,沒有來源驗證 | HIT(只影響軟提醒與統計,判定類讀者不讀本機帳) |
| X11 | 讀 _append_governance_log 與 _gov_ledger_rows_by_time | HIT |
| X12 | 讀 _m1_events | HIT |
| X13 | grep lumos-cli-read 的 usage-log | HIT |

## 處置

全部折入,X8 駁回:
- X1:暖機護欄看「這個閘+種類現在寫進哪一本」,走本機帳的組合看本機帳最舊一筆,本機帳不在或不滿 N 週就不判。
- X2:合讀改走 _gov_tail_bytes + _drift_jsonl_iter;時間解析抽成 _gov_ts,度量段與合讀共用。
- X3:已追蹤時提醒 git rm --cached。
- X4:提醒改講「帳在 docs/ 的跑 update,其他佈局在帳檔同一層的 .gitignore 加檔名」。
- X5:〈回退〉改成先移出 repo(要留就備份),並寫明每個 worktree、每台機器各自處理。
- X6:補行改用 _write_lf 整份原子替換,原內容位元組不改;兩個程序同時補寫的是同一份內容。
- X7:合讀改讀檔尾(24MB 上限,同 doctor 其他讀治理帳的段落)。
- X8:駁回,理由同重現表。
- X9:本機帳是捷徑時兩支寫入器都不寫;.gitignore 原子替換換掉的是捷徑本身。版控帳是捷徑的情形是分流前就有的寫法,本案不動。
- X10:由 X3 的提醒蓋到(被追蹤就叫人移除);判定類讀者不讀本機帳,沒有繞過判定的路徑。
- X11:改名 _docs_ledger_path,說明改成「docs 層帳檔」。
- X12:改成直接過濾 dict。
- X13:lumos-cli-read 的 KEY 行、內容段、正文三處改成 usage-local;第 34 行的舊 FLOW 一改就會被筆記形狀擋判成新寫的現況描述,照留。

另外,跑相關測試時 t_drift_m1_review_r1_non_utf8_and_guard 紅過一次:同一秒寫進兩本的事件合讀後先後不固定,用 [-1] 取最新一筆會拿錯;改成快照差集抓新事件。
