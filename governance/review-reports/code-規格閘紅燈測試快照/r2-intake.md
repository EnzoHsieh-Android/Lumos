# r2 收貨紀錄(code-規格閘紅燈測試快照)

## 收貨

- 三席(單reviewer、架構對齊看 r2-repair-review.patch;資安看 r2-snapshot-lumos.patch)報告從逐字稿原樣存檔。三份都已正規化、引句全數錨定(各對自己那一包)。
- 席位重現腳本在 `/tmp/lumos-seat-work/code-規格閘紅燈測試快照/`,報告存檔後整個目錄刪掉。repo 工作樹只多了工具自己記的帳(逃逸帳、殺傷帳、治理帳)。
- 輪內仍有 major,依使用者先前定的規矩停下來問;2026-11-03 Enzo 裁「照修、派最後一輪(推薦)」。

編號:單reviewer F1–F6 記成 C1–C6、架構對齊 A1–A3、資安 S1–S2,共 11 條;major 3 條(C1、C2、S2),其餘 minor。全數折入,沒有放行,沒有重現不到的。

## 歸因(照 §3.1 第 6 步;兩版證據是席位自己跑的,編排者另有修前紅、修後綠見 r2-repro.txt)

| id | 歸因 | 依據 |
|---|---|---|
| C1 | 有證據的修復回歸 | 同一輸入(分支內新增的測試檔改名後改 expected):修前 30ae09fb6 列 `tq/redbase-weakened`,修後 c627b3874 列 `tq/redbase-unmatched … 太大或讀不出`;r1 修補把 `_tg_read` 的 UNREADABLE(那一版沒有這個物件)當成讀不出 |
| C2 | 有證據的修復回歸(新增守衛沒帶測試) | 修前沒有 `_tg_rb_pending`;修後拿掉頂端判斷 106 條照綠 |
| C3 | 有證據的修復回歸(r1 修補的讀回端沒釘測試) | 修後把讀回端改回只看名字 106 條照綠 |
| C4 | 有證據的原有漏查 | 修前補讀完全不算總量,修後只扣了推送內容、沒扣紅燈版自身 |
| C5 | 有證據的原有漏查 | 寫入端讀上一份同檔重切,修前 11.90 秒、修後 12.17 秒 |
| C6 | 有證據的修復回歸(文件沒跟程式) | 計劃兩處 |
| A1 | 有證據的修復回歸(新增的窄解析) | `_tg_rb_pending` 自己解 porcelain |
| A2 | 有證據的修復回歸 | 寫入端複製了 `_tg_start` 的兩段式 |
| A3 | 有證據的原有漏查 | check-ignore 原本就用 subprocess,修補多了一份 |
| S1 | 有證據的原有漏查 | 所有作弊候選共用 `_tg_cand` 的回顯規則 |
| S2 | 有證據的修復回歸(局部) | 「刪掉它」那句是 r1 修補加的;合併時留痕弄丟的曝險原本就有 |

regression_set:C1、C2、C3、C6、A1、A2、S2。

## 根因分組與處置(全部 folded)

| 組 | 根因 | id | 折法 | 先紅的測試 |
|---|---|---|---|---|
| 1 | 補讀把「那一版沒有這支檔」當成「讀不出」 | C1 | `_tg_rb_fill` 只把 TOOLARGE 當讀不出;UNREADABLE 當空檔、照常走搬家查找 | `t_tq_guard_redbase_moved_or_missing`〈分支內新增的測試檔改名後改 expected〉〈先加後刪原因講找不到〉 |
| 2 | 新守衛沒有測試釘住 | C2、C3 | 補「推舊提交時工作目錄的紅燈版不算」「別的平台判綠過的同名測試照存」;兩條現行行為本來就對,用改壞驗證測試咬得住 | `t_tq_guard_redbase_unreadable`〈推的不是頂端〉、`t_spec_gate_redbase_written_on_red`〈別的平台判綠過〉 |
| 3 | 額度與效能:補讀沒扣紅燈版已讀;寫入端讀上一份同檔重切 | C4、C5 | `_tg_rb_load` 回傳讀了幾個位元組,補讀的額度是 consumed 加它;寫入端讀上一份帶快取 | 〈補讀的額度扣掉紅燈版已讀的〉〈寫入端讀 800 支的上一份 3 秒內〉 |
| 4 | 合併時留痕弄丟,孤兒檔訊息叫人刪,刪完零候選 | S2 | 孤兒檔照它的內容比、訊息改成「用 git log -p 找回那一行補回、不要刪」;這條分支提交刪過的紅燈版(`git log --diff-filter=D`)列出來並照刪掉前的內容比;壓過提交後中間的刪除看不到,寫成天花板 | `t_tq_guard_redbase_unreadable`〈孤兒檔照樣比〉〈訊息不叫人刪〉〈分支內被刪的列出來〉〈照刪掉前的內容比〉 |
| 5 | 架構:重複的分岔點兩段式、check-ignore 另起一份 subprocess、窄解析 porcelain | A1、A2、A3 | 抽 `_lens_fork_point` 給 `_tg_start` 與寫入端共用;兩處 check-ignore 改走 `_lens_git`;porcelain 自己解要狀態碼,註明先例 `_handoff_files` | 無(重構;行為由既有測試守) |
| 6 | 文件與回顯 | C6、S1 | 計劃改寫入端分岔點與讀帳觸發條件;資安段寫明測試名等文字在擋下訊息只清控制字元、跟既有候選同一規則 | 無 |

另外:舊斷言「欄位形狀錯、路徑出界只列 unreadable」「孤兒檔救法講刪掉」跟組 4 的新行為衝突(孤兒檔現在照樣比、會多一條改弱;訊息不再叫人刪),改成「至少要有講對原因的 unreadable」「講找回留痕」。修組 4 時發現 git log 預設把中文路徑加引號,刪除偵測對不上路徑,改帶 `core.quotePath=false`。

## 先查世界(r2 修補前,2026-11-03)

- PRIOR-ART: 組 4。git 內建 `merge=union` 適合只追加的紀錄檔(兩邊新增的行都留),但行序不定、可能重複,讀的一方要能去重排序;GitLab 等託管平台的網頁合併不認這個屬性(https://a3nm.net/blog/git_auto_conflicts.html 、https://gitlab.com/gitlab-org/gitlab-foss/-/issues/17325 、https://github.com/SpillwaveSolutions/wiki_ticket_sdd/wiki/ADR-0001-event-log-fold-union-merge)。排除:這次不改治理帳的合併方式(全 repo 的決定,另案);採用:讀紅燈版的一方容忍留痕遺失(孤兒檔照內容比)。
- 組 1、2、3、5、6 是本專案內部的讀法、測試覆蓋、額度與文件問題,以既有程式為準,沒有外部做法要比。

## 改壞驗證

修完把新舊守衛逐一改壞,結果見同目錄 r2-mutation.md。
