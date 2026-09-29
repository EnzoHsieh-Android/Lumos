# r3 收貨紀錄(code-推送閘接漂移檢查)

凍結材料:dca86f7d..fc25e1e4 的 git diff -U10(不含帳本與卷證目錄),1623 行,不拆;`r3-snapshot.patch`。第 3 輪(上限輪)審第 2 輪修正本身,全新席位、全編制。
8 席:正確性 opus、邊界 sonnet 5.5、併發回滾 sonnet 5.5、合約圖譜 sonnet 5.5、架構對齊 sonnet 5.5、資安 sonnet 5.5、外家 finder 與外家否決 Codex(gpt-5.6-sol xhigh,唯讀沙盒)。派工鏡頭沿用第 1 輪編排者算好的檔。

## 席位收貨

- 8 席全交,等完成通知(Codex 等背景行程結束)、ls 確認後才讀。併發回滾席說凍結 patch 在它的 clone 裡找不到(當時還沒提交),自己用同一範圍重生一份審——quote-check 以凍結 patch 為準,它的引句全數錨定。
- report-normalize:8 份都已是正規化格式。quote-check:6 份全數錨定;邊界、資安兩席 clean、沒有引句(無 finding,不適用)。
- 發現 9 條(機器數):正確性 3、併發回滾 1、合約圖譜 2、架構對齊 1、外家 finder 1、外家否決 1、邊界 0、資安 0;major 1 條(外家否決 F1)。

## 判讀

- 外家否決 F1 與正確性 F3 同一件事:GitHub Actions 的 checkout 不建 origin/HEAD,預設分支不叫 main/master 的專案在 CI 找不到主線。外家否決席附了 actions/checkout 的 issue 連結與純函式重現;編排者判現象成立(本輪測試自己先補了 symbolic ref,沒測到真前置條件)。修法:CI 那步從事件帶的預設分支補上 origin/HEAD。
- 正確性 F1 F2(fork 流程):照順序取第一個候選是第 2 輪修法的殘留形狀;換成所有候選一起算 `merge-base --all`、取離頂端最近的分岔點,不再依賴順序;「就是這次被推的那條」改成遠端加分支完全相同才跳過。

## 機械重現(在審的那一版 fc25e1e4 上;方法:折入後的新測試格,把修法還原就翻紅,先證明舊行為)

| 發現 | 做法 | 結果 |
|---|---|---|
| 外家否決-F1 | 拿掉補 origin/HEAD 那段 | HIT:`t_ci_drift_default_branch_shapes` 6 條紅(測試照 checkout 步驟建工作目錄,先斷言沒有 origin/HEAD) |
| 正確性-F3 | 同外家否決-F1 | HIT:同上 |
| 正確性-F2 | 改回取第一個候選 | HIT:`t_prepush_drift_start_mainline_shapes` ⑤ 紅 |
| 正確性-F1 | 改回只比分支短名 | HIT:同上 ④ 紅 |
| 外家finder-F1 | 拿掉「兩個參數要一起給」 | HIT:`t_drift_check_push_start_edges` ① 兩條紅 |
| 併發回滾-F1 | git 失敗改回當成找不到 | HIT:同上 ② 三條紅 |
| 合約圖譜-F1 | 讀 ci.yml 註解與 commands/08 | HIT;補「128 以上停下」 |
| 合約圖譜-F2 | 讀存量漂移守衛 | HIT;改成精確說法,範本測試改比整段 |
| 架構對齊-F1 | 讀兩套起點函式說明 | HIT;互相指回並指到收斂 Issue |

## 處置

- 9 條全折(folded),accepted 空、refuted 空。修正在 8bcd45a6。
- 實作代理人自報沒釘住的:兩條互不包含的主線、分支同時合了兩條時取哪個分岔點(取歷史最長的);「Actions 不建 origin/HEAD」只在本機照 checkout 步驟模擬、沒在真的 Actions 跑。

## 到頂之後(編排者裁定,2026-09-30,Enzo 睡前授權編排者裁審查到頂)

- 第 3 輪是上限輪、有 major 而且全折。修正差異(74dc5185..8bcd45a6)沒有新席看過,照「修正差異要派新席」的紀律,破例開一小輪驗收(r4):只派 3 席(正確性 opus、外家否決 Codex、資安 sonnet——資安席要涵蓋最後一版),只看這次修正差異;r4 若再有 major,不再修,停下攤給人裁。
