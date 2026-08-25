---
type: project
summary: |-
  FLAG:DECISION
  KEY:立案(2026-08-25,自 [[Issues/連鎖佇列開了沒人跟完]] P1)——decision-supersede 自動開的連鎖待辦單沒人跟(3 張裡 2 張零判定空轉 21/14 天,第 3 張=本案編排者自己開了不知道);解=doctor 加一段 warn_soft 軟提醒(零新命令零新機制,借既有帳本讀取),transitions==0 才報、全判定靜默、損毀歸 E2 不重喊
  KEY:本案兼 [[Projects/設計審收斂重定義_計劃]] [S6] 實測載體:新制全套首次用在非自指真案(prose-lint 排乾/blocking 宣告綁定/d5 處置記帳/兩行審計格式)
status: doing
created: 2026-08-25
updated: 2026-08-25
tags:
  - type/project
  - status/doing
---

# 連鎖佇列軟提醒_計劃

> 白話:決策翻案時系統會自動開一張「誰引用了舊決策,去判一下還成不成立」的待辦單,但開完沒有任何東西提醒你——歷來三張,兩張至今零筆判定,第三張是本案編排者自己開的、直到立這個案才發現。解法不造新機制:doctor 收工體檢多印一行軟提醒。

PRIOR-ART:最小解在 doctor 既有 soft-check 層(`warn_soft`,scripts/lumos:486,不擋、只提醒);世界解=撤稿研究:無提醒時撤稿後引用僅 5.4% 承認撤稿(歸檔於 [[Issues/連鎖佇列開了沒人跟完]] PRIOR-ART 節);裁定=**借用**既有 doctor soft-check 形態+既有帳本讀取(`_ledger_read` scripts/lumos:8162、`_rel_cascade_dir` scripts/lumos:8103),零新命令、零新機制。

## 症狀(會翻紅的證據)

`governance/rel-cascade/` 歷來 3 張帳本:前兩張(2026-08-04/2026-08-11)建立後**零筆 confirm/prune**,分別空轉 21/14 天;第三張(2026-08-25)開單人當下不知道有單。翻紅指令:對含零判定帳本的 repo 跑 `lumos doctor`,現行輸出**沒有任何一行**提到連鎖待辦——[T2] 測試釘住「修後有這一行」。Issue 立案=[[Issues/連鎖佇列開了沒人跟完]](P1;2026-08-13 實測 2/2 空轉)。

## 核心裁定

- **d1 落點=doctor 軟提醒,不是 pre-push**:doctor 是收工必跑(鐵則 3),pre-push 已擠;`warn_soft` 形態=印提醒不動 rc。已排除 pre-push advisory:同一行資訊兩處印=第二真相源,先一處實測。
- **d2 判定條件=帳本 transitions 為零筆**(只有 header)。語意=「這張單你從沒看過」,不是「沒做完」——帳本沒有分母(該判幾個鄰居不入帳,`cmd_rel_cascade_list` docstring 明言「不判開放/完成精確分類」,scripts/lumos:8288)。已排除「判到一半棄坑」偵測:那是活動齡問題,`rel-cascade list --stale N` 既有旗標已覆蓋,首版不重做。
- **d3 訊息照工具輸出三段式**:發生什麼(N 張連鎖待辦單自建立後零筆判定,最老 X 天)→為何在意(被翻案決策的引用筆記沒人回頭判,世界對照=94.6% 的撤稿引用不承認撤稿)→指令獨立一行(`lumos rel-cascade list`)。
- **d4 header 損毀帳本跳過不報**:損毀已有補網 E2 兜底(scripts/lumos:8391 註明),本提醒重報=同一事兩處喊。已排除:理由如上。

## 落地件

1. [T1] doctor 內加一段 soft check:掃 `governance/rel-cascade/*.jsonl`,計 transitions==0 的帳本數與最老天數,>0 就 `warn_soft` 一段;目錄不存在→靜默跳過。
2. [T2] 測試 `t_doctor_cascade_reminder`:零判定帳本→輸出含提醒行;有一筆 transition→不計入;header 損毀→跳過不炸;doctor rc 不因此改變。
3. [T3] Issue [[Issues/連鎖佇列開了沒人跟完]] 結案橫幅+本計劃雙向連;Systems 側 KEY 寫回(關係層傳播守衛的筆記)。

## 行為斷言(每條配例)

- 例1:repo 有兩張僅 header 的帳本(建立日 2026-08-04/2026-08-11,今天 2026-08-25)→ doctor 輸出含「2 張連鎖待辦單還沒人看過(最老 21 天)」語意的提醒段+獨立指令行 `lumos rel-cascade list`。
- 例2:某帳本有 1 筆 transition(confirm 或 prune 任一)→ 不列入「沒人看過」計數;三張裡一張有判定→提醒行報 2 不報 3。
- 例3:某帳本 header 行是壞 JSON → 該檔跳過,doctor 不 traceback、提醒行計數不含它。
- 例4:`governance/rel-cascade/` 目錄不存在 → 無提醒行、無錯誤。
- 例5:全部帳本都有判定 → 完全無此段輸出(靜默,不印「0 張」佔版面)。

## 實務隱患

- **併發/效能**:doctor 每跑掃一次目錄,現況 3 檔、每檔數行,量級無虞;帳本 append-only、讀壞行為 `_ledger_read` 既有語意,無鎖問題。
- **誤報面**:「判過一筆即靜音」可能放過「跟到一半棄坑」——已排除(d2,活動齡歸 --stale 既有旗標);若 [T2] 落地後實測有此案例再議,回頭條件=下一次巡檢發現 confirmed>0 但明顯未跟完的帳本。
- **守衛面**:加的是不動 rc 的軟行,整段可 revert;不碰金流/對外/不可逆。
- **提醒疲勞**:doctor 軟提醒已有多段,再加一段的邊際噪音——控制:全判定時完全靜默(例5),不印空狀態。

## 審計修正紀錄

(待 r1)

## 下一步

r1 設計審(standard,本案兼 [[Projects/設計審收斂重定義_計劃]] [S6] 實測載體:prose-lint 排乾入場、blocking 宣告+綁定、d5 處置記帳、兩行審計格式)→過閘→[T1]–[T3] 實作→code-loop→推送。
