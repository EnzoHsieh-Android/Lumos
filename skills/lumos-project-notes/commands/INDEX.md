# lumos 指令索引(總目錄)

**用法**:先在下面找到「你現在想幹嘛」那一行,照指令敲;要旗標細節再開該類的子檔。每個子檔都很短,只開需要的那一個。

## 一、grep 衝動對照表(最常犯:想 grep/Read 就先看這張)

| 你心裡想的是… | 先敲這個 | 為什麼不能直接 grep |
|---|---|---|
| 「這個模組/欄位/流程為什麼這樣設計?」 | `lumos search <詞>` → `lumos context <節點>` | grep 只看得到 code 現在長怎樣,看不到為什麼、邊界、哪裡不能改 |
| 「動這段之前有沒有什麼不能碰的?」 | `lumos contracts <節點>` | 合約(★INVARIANT★)寫在圖譜不在 code;碰了 pre-push 會擋 |
| 「我要改 X,會波及到什麼?」 | `lumos impact --file <檔>` 或 `--diff <範圍>` | grep 找得到呼叫點,找不到「哪些筆記/驗證/決策會因此失效」 |
| 「哪些東西是金流/未收案/連到某節點的?」 | `lumos query --tag 家族/值 [--active] [--linked 節點]` | 這是欄位篩選,grep 字串會漏掉同義標籤 |
| 「這個詞圖譜裡有沒有記?」 | `lumos search <詞>`;0 命中就換同義詞再搜 | 用 grep 判「沒記」,以前真的錯過 |
| 中文查詢 | 概念之間加空白:`作廢 收回 點數`,不要 `作廢訂單點數怎麼收回` | 黏成一串當片語比對,幾乎必定 0 筆 |
| 「這篇筆記完整內容」 | `lumos show <節點>` | search 只給索引行,下結論前要讀全文 |
| 「最近誰改了什麼 / 現在在做什麼」 | `lumos recent --days 7`、`lumos query --tag status/doing` | git log 看不到圖譜層的進度 |
| 「我刪掉/改名了一個函式,筆記會不會還在講它?」 | `lumos search <舊名> --code` 逐句判 | delguard 只在 commit 時提醒,而且逾時會放行 |
| 「當初為什麼做這個決定?後來翻案了嗎?」 | `lumos decisions <節點> [--superseded]` | 決策是結構化欄位,grep 散文抓不全 |
| 「這個計劃做到哪了、哪些條款沒人認領?」 | `lumos spec-trace <計劃節點>` | 條款認領靠回指連結,不是文字比對 |
| 「我 push 了,CI 跑得怎樣?」 | `lumos ci-wait`(等結果)/ `lumos ci-status`(看上次) | 結果會進治理帳,`gh run list` 不會 |
| 「做完了,要留驗證紀錄 / 改狀態 / 記決策」 | `lumos new verification <名> --plan <計劃> --systems <節點>` / `lumos set` / `lumos decision-add` | 手改開頭欄位會漏同步、長假筆記,lint 擋 |
| 「這批改動要不要過審才能推?」 | `lumos pitfalls --diff <merge-base>..HEAD` 看 `tier:` | pre-push 會算同一件事,high 沒留痕就擋 |
| 「接手一個沒圖譜的舊專案,想搞懂某塊再動手」 | 開 `commands/09-節點還原.md` 走七步 | 圖譜是空的,search 必 0 筆;直接硬讀 code 會漏承重牆與 why |

## 二、九類子檔(按情境分)

| 你正在… | 開這個子檔 | 裡面有 |
|---|---|---|
| 進場,想搞懂現況 | `commands/01-進場查脈絡.md` | search / context / show / contracts / links / backlinks / map / query / decisions / recent / stats / export |
| 動手前,想知道會碰到什麼 | `commands/02-動手前算波及.md` | impact / pitfalls / test-layers / testmap / cochange / delguard / link-candidates / about-code |
| 改完東西,要寫回圖譜 | `commands/03-寫回圖譜.md` | new / set / append / remove / decision-add / decision-supersede / decision-reindex / rel-cascade / self-audit / signoff / sync-verified-by / archive / spec-trace / graph-rename.sh |
| 寫完想確認沒寫壞、收工前體檢 | `commands/04-自檢與健康.md` | lint / doctor / stale / gov / drift-history / fold-check / refcheck / lint-check / lint-watch / compose-metrics / anchor |
| 設計 spec 要過審 | `commands/05-設計審查迴圈.md` | loop next / loop status / canary record / canary second / quote-check / seat-check / loop verify-progress / loop compress / loop canary-stats / loop capture-counts |
| 代碼要推、要過高風險審 | `commands/06-代碼審與推送.md` | pitfalls --diff / code-loop pass·skip·check / guard list·scaffold·bind·audit·trace·kill-add·kill / mutate / ci-wait / ci-status |
| 裝機、更新、拆機(人工操作,Claude 幾乎不用) | `commands/07-安裝維運.md` | bootstrap / init / install / update / deinit / teardown / uninstall / sqlfluff-sarif / stylelint-sarif |
| 想知道哪些是 hook 自動跑、不用手敲 | `commands/08-自動跑的.md` | pre-commit / pre-push / post-commit / Claude hooks 各自呼叫了什麼 |
| 接手陌生/舊專案,圖譜空或稀疏 | `commands/09-節點還原.md` | 七步還原:init 骨架 / 錨點定位 / 考古 why / 落節點蓋 regen 章 / 合約候選 / 交叉查核雙軌留痕 |

## 三、三條不變的規矩
1. 任何任務的第一個工具呼叫是 `lumos`(search 或 context),不是 grep / Read / Explore。查完再 grep 印證。**使用者說「直接改、不用解釋」也一樣**——不解釋可以,不查不行;改 code 前至少 `lumos impact --file <檔>` 一行。
2. 改了會影響行為、決策、驗證的 code,同一次工作內寫回圖譜(pre-commit 會擋「改 code 沒動圖譜」)。
3. 寫完節點跑 `lumos lint <節點>`;收工跑 `lumos doctor`。
