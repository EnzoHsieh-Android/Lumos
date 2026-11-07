# r2 收貨紀錄(android寫法寫完當下自動檢查)

## 收貨

- 第 2 輪,standard。四席(通才、邊界、資源、架構對齊,全 sonnet)審同一份 r2-snapshot.md(139 行,sha256 63d20597…)。
- 四席交回後一次從逐字稿存檔(完成通知會把角括號轉成跳脫字)。四份已是正規化格式。
- quote-check:邊界 24/24、資源 20/20、架構對齊 13/13 全錨;通才 23 句有 2 句錨不到(#11 是把快照原句「續做那一輪」寫成「續做那輪」,#22 不足 10 字),那兩句不採信,所屬 F5、F12 另有錨到的引句與佐證,照採。refcheck 四份全 ok。
- 席位沒有改 repo:收貨時 `git status` 只有本輪卷證與編排者自己的改動;邊界席臨時目錄 /tmp/lumos-seat-work/android寫法寫完當下自動檢查/ 存完報告後已刪。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 二資1 | 資源 F1 | 讀快照範圍 3 末條與天花板 1 | HIT:範圍 3 說續做改的檔下次會被查,天花板 1 說等代碼審或推送前閘 |
| 二通1 | 通才 F1 | `grep -n '_trusted_lumos\|LUMOS_HOME' scripts/hooks/claude/impact-hook.py scripts/lumos` | HIT:安裝目錄有多個來源,白名單沒指定、沒正規化 |
| 二邊4 | 邊界 F4 | 席位在臨時 repo 實跑 `git diff --quiet HEAD`,索引雜湊改變;`diff-index` 不變 | HIT(席位原輸出) |
| 二架1 | 架構 F1 | `grep -n '全庫只有這一支' scripts/lumos` | HIT:`_strip_c_comments` 註明唯一一支 |
| 二通11 | 通才 F11 | 讀 `scripts/lumos` 的 `_codeloop_guard_verdict` 分岔點分支 | HIT:等於 HEAD 直接放行不記帳,算不出才 `_gate_failopen` |
| 二邊12 | 邊界 F12 | `grep -n "'--repo'" scripts/lumos` 對照計劃範圍 1 | HIT:計劃的 `lint-new` 沒有 `--repo` |

refuted: none

## 先查世界

- PRIOR-ART: 拆小——設計審熔斷提示「累計折入超過 20 條就建議拆小」,母計劃第二輪也照這條把第二批拆出來帶走 36 條;本輪 42 條裡 39 條落在回合結束鉤子、工作樹檢查、改檔前推列、白名單,照同一條拆到 Projects/Android寫法回合結束檢查與改檔前推列_計劃,問題依根因分十一組寫進那份的〈待解問題〉,下次動筆前先查世界再改。留下的「代碼審記通過前先跑機械檢查」借 Google Tricorder 送審前先貼靜態分析結果的做法(Sadowski 等 2018,https://cacm.acm.org/research/lessons-from-building-static-analysis-tools-at-google/ )與 GitHub 必過檢查(https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging )。

## 歸因

- 本輪沒有上一輪修補造成的回歸:42 條都是 r1 折入時新寫的機制本身(回合時間戳、白名單、SIGTERM 收尾、推列通道)的洞,或原文就有的描述不實;判過因果,無回歸。

## 逐條去向(42 條全折,0 放行,0 駁回)

| id | 席報告原條 | 去向 |
|---|---|---|
| 二通1–二通9、二通12 | 通才 F1–F9、F12 | 折:整段機制拆到新計劃,依根因寫進〈待解問題〉第 1、2、3、5、6、9、10 組 |
| 二通10 | 通才 F10 | 折:`--only-stdin` 隨工作樹檢查拆走,本份不再出現 |
| 二通11 | 通才 F11 | 折:範圍 2 改寫成「算不出來放行並記帳;等於 HEAD 直接放行不記帳」,S2 加一例 |
| 二通13 | 通才 F13 | 折:pass 被擋時用既有 `_gate_event_or_warn` 寫一筆 `code-loop-pass` 擋下事件,RETIRE-IF 改數這個;拆走那兩個機制的量法寫進新計劃第 11 組 |
| 二邊1–二邊11 | 邊界 F1–F11 | 折:拆到新計劃〈待解問題〉第 1、2、3、6、7、8、9 組 |
| 二邊12 | 邊界 F12 | 折:`lint-new` 加 `--repo`,沒給時照 `code-loop check` 的找法,S1 加一例 |
| 二資1–二資10 | 資源 F1–F10 | 折:拆到新計劃〈待解問題〉第 1、2、4、5、6、7、9 組 |
| 二架1–二架7 | 架構對齊 F1–F7 | 折:拆到新計劃〈待解問題〉第 6、7、10 組;rc3 另有意思那條 ⚠ 在本份範圍 1 寫明 |
