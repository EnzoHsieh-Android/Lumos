---
type: project
status: doing
created: 2026-08-24
updated: 2026-08-24
summary: |-
  FLAG:DECISION
  KEY:立案(2026-08-24 Enzo「開」)——held 固定席噪音 96 條(live 口徑;考卷 82)佔比過半,out_top3_must held 0.083 被它拖死。逐條分解:58 條=「間接一跳+RISK 類軟合約」樞紐筆記(pitfalls-code-loop 7x/lumos-cli-read 6x/lumos-refcheck 6x…)搭便車
  KEY:★v2(r1 五席打掉 v1 後改)★主案=間接保送只認 INVARIANT/IRREVERSIBLE;被降的 RISK 類 indirect 進**獨立參考道**(不佔固定席、不進自由席計分/門檻/名額、輸出尾端標「守衛面參考」上限 3 條)。★about/治標籤全退出本案★(v1 的豁免=翻前案已鎖決策+兩條測試機械擋+在震央 scripts/lumos 撞巨檔門檻必死;治標籤=把 impacts 語意塞進 about 欄)。參考道使 P@8 逐 byte 不變、must_in_out 結構性不退
  KEY:已試已殺留痕——扇出二元砍除(2026-08-23):P@8 +5 格但必看 26→23 被棘輪擋;勿憑直覺復活,重試須過同款考卷
  KEY:尺=固定席噪音數(主目標,-43/96)+ P@8 逐 byte 不變(結構保證)+ must_in_out 不退(結構保證)+ out_top3_must 應升;★本案凍結 goldset 標籤★(Codex f4:改標籤→換 rev→棘輪重立基線,守衛蒸發);per-split 棘輪與 eval/hook top 口徑錯位(PPR 案舊坑)列工具清單;症狀指令見正文
  DEP:[[Projects/固定席扇出降權_計劃]]｜[[Systems/retrieval-ranking]]
plan_refs: []
related:
  - "[[Projects/固定席扇出降權_計劃]]"
  - "[[Systems/retrieval-ranking]]"
tags:
  - type/project
  - status/doing
---
# 固定席降噪A層_計劃

> 白話:改程式時 hook 會推「必看」筆記,其中一半以上是不相干的——因為有一批 CLI 樞紐筆記
> 掛著「守衛面」這種**軟**標記、又跟每支檔都只隔一跳,每一題都被無條件保送進固定席。
> 修法:保送只認「改了就壞」的硬合約;軟標記的要嘛有語意證據(about 命中)才留,要嘛下去排隊。

## 症狀(會翻紅的指令;2026-08-24 實測)

```
python3 governance/eval/retrieval_eval.py --goldset governance/eval/retrieval-goldset.json --ablation
```
看「固定席裡不相干的筆記」:held **82 條**(live 口徑 96)、train 15;「輸出前 3 名是必看的比率」held **0.083**。
本案成功=held 固定席噪音顯著降、must_in_out 棘輪不退、out_top3_must held 上行。

## 診斷(2026-08-24,live 口徑逐條分解)

| 分解 | 數字 |
|---|---|
| 噪音 96 條按路徑 | incident 15 / direct 23 / **indirect 58(60%)** |
| 按合約 | **RISK·守衛面 56** / INVARIANT 22 / 無(事故)15 / RISK·不可逆 3 |
| 重複犯 | pitfalls-code-loop 7x、lumos-cli-read 6x、lumos-refcheck 6x、anchor-integrity 4x…(CLI 樞紐,圖上跟誰都一跳) |

**根因**:間接保送條件=「有合約且 hop≤1」——★任何類的合約都算★。「RISK·守衛面」是提醒級的軟標記
(掛在幾十篇 Systems 上),不是「改了就壞」的硬承諾;拿它保送=樞紐筆記全票通過。

## 反事實(2026-08-24 離線算,同一批題)

**R1:間接保送只認 INVARIANT/IRREVERSIBLE;RISK 類間接降自由席。**

| | 噪音會降 | 必看會降 | 有用會降 |
|---|---|---|---|
| train | 7/20 | **0/10** | 5/11 |
| held | **43/96(45%)** | **★3/5★** | 8/13 |

被誤降的必看 3 條:E06/E12 `anchor-integrity`(守**所有** hook,about_code 卻只標 pre-push)、
E08 `design-loop`(管自主迴圈測試,about 沒標 test_autonomous_loop)——★全是 about 漏標受害者★。

## 主案 v2:硬合約保送 + 參考道(r1 五席折入後版;v1 的 about 豁免/治標籤已整段作廢,見審計紀錄)

1. **間接保送收窄**:indirect 且 `hop ≤ min(depth, LUMOS_IMPACT_PIN_HOP)`(現行預設 1;★範圍隱性綁這顆旋鈕,動它要重跑考卷★,s2f4)的節點,
   `contract in ("INVARIANT", "IRREVERSIBLE")` 才保送固定席;`RISK·*` 類(值域=`_RISK_ENUM` 四值,錨:`def _impact_contract`)不再保送。
   direct 保送不動(direct 噪音 23 條另案;一次一刀可歸因)。
   ★併名陷阱(s2f2)★:`RISK·不可逆`(軟標籤)與 `IRREVERSIBLE`(硬合約)是兩個機制、中文撞名——實作用字串精確比對,文件裡兩者並列時必註明。
2. **參考道(reference lane)——★r2 折入版:獨立容器+產生階段 cap★**:被 1 降的節點★自始不進 `results` 共用清單★
   (s1/s2 各自實測:`pinned:False` 會被四處既有「非 pinned=free」分流吃回自由席,把門檻拉高、真候選被擠光),
   收進獨立 `lane_items`;★cap 在產生階段★(arch r2:rescued 的限量就在產生端,三處輸出同一份):
   `LUMOS_IMPACT_LANE_N`(預設 3,考卷網格轉正)內排序鍵 `(-score, node)`(同 free tie-break 慣例),
   截斷後這一份=JSON=人讀=hook,★兩個口徑合一★——被 cap 砍掉的必看會真的掉 must_in_out,棘輪重新有效
   (Codex r2 f1:「JSON 綠燈、人看不到」的偷換口徑由此消滅)。
   欄位:`lane: "soft-guard"`、`pinned: False`、保留原 score;`meta["lane"]` 計數、`meta["lane_dropped"]` 被 cap 砍的條數
   (hook 顯示「另有 N 條守衛面參考未列出」,s2f7);`final = pins + free + rescued + lane_items`。
   ★下游分流全站清單(工具清單 #2b,漏一處就重演舊坑)★:
   `scripts/lumos` free 過濾(lane 不在 results 天然不進)、人讀純文字分支(★要加 lane 小節,score 用 .get,s2f3 抓到會 KeyError★)、
   `impact-hook.py` 自己的 free 桶(既有已排除 rescued,要加排除 lane,s2f4)、
   `retrieval_eval.py` `eval_edit` free 分流(★排除 lane,並順手把 rescued 的排除釘成明文——它現在被算進 P@8 母體只是僥倖沒進前 k,s2f5★)、
   `retrieval_eval.py` `_touched_edit`(消融閘的觸及集:lane 視同 pins 無條件納入未標檢查,否則安全網覆蓋縮水,s1f4/s2f2)。
   ★為什麼不是降自由席★(r1 的血):有動態門檻+名額,被降的會被整個砍出輸出——前案「降級≠保留」舊坑;參考道=結構性保留。
   ★為什麼不是 about 豁免★:翻前案已鎖決策+兩條測試機械擋+巨檔門檻讓豁免在震央必死——r1 三票否決,v1 作廢。
   ★為什麼不擴 rescued★(arch r1 ⚠):語意不同(缺口補席 vs 整類降級保留),但實作同家族——獨立容器、產生端限量、
   不過門檻名額、append 輸出、meta 計數,五個維度全照 rescued 慣例,不是第二種做法。
3. **結構保證(r2 誠實化)**:free 集合與排序完全不動 → P@8/nDCG 逐 byte 不變——★前提是 §2 的獨立容器與全站分流清單一處不漏★
   (s1 實測:漏任何一處,不是灌爆 free 就是 lane 消失);測試逐 byte 釘。
   must_in_out:cap 內結構性不退;★被 cap 砍的必看會誠實掉數字、棘輪抓得到★(這是口徑合一的代價與好處)。
   固定席噪音降幅:★「降誰」對 indirect 是決定論,但 incident/indirect 歸類會隨 delta 變(s1f3:同一節點不同改動下可能走事故路徑)——
   43/96 是無 query 口徑的近似,驗收不押絕對值★,以落地後考卷實測+pin_noise 棘輪為準(Codex r2 f3;82-43=39 的減法也不成立,s1f5)。
4. **總開關**:`LUMOS_IMPACT_HARD_PIN`,★預設 0(上線即死碼)★(s2f9:預設問號沒法審)——
   照 `LUMOS_IMPACT_BASENAME_MATCH` 轉正流程:train 網格、held 驗一次、gate 全過才轉預設 1;0=舊制逃生。
   參考道整段包在 knob=1 分支內(s2f13:單開關回滾逐 byte)。
5. **goldset 標籤本案凍結**(Codex f4):不補標、不改答案——改了 rev 就換、棘輪重立基線,守衛蒸發。
   E06/E08/E12 那 3 條(加 s1f2 抓的另外 12 處)的「必看但 about 不含」證據★不是 about 漏標★(Codex f1:
   anchor-integrity 的 about 只標 pre-push 是**對的**,它「影響」全部 hook 是另一個語意)——
   整批記進 [[Projects/固定席扇出降權_計劃]] 的 impacts_code 後案當語料,本案不動欄位。

## 落地驗收(照症狀指令)

- 固定席噪音:★驗收不押絕對值★(近似估計 held -40% 上下)——以 `LUMOS_IMPACT_HARD_PIN=1` 臂的考卷實測為準(Codex r2 f3:預設 0 是死碼,驗收必須明寫在候選臂上跑);
  ★pin_noise 現況只印不閘——工具清單 #4b:進 verdict+gate「不准變多」,knob 轉正時啟用★。
- P@8/nDCG:**逐 byte 相同**(測試釘)。must_in_out:不變(測試釘:被降節點仍在 JSON results)。
- out_top3_must held 0.083→應升(觀測)。
- ★eval/hook top 口徑錯位(r1 s2f12,PPR 案舊坑)★:參考道不受 `--top` 截斷(同 rescued;s2 查證屬實)→ 錯位不影響本案;
  per-split 棘輪列工具清單——★實作落點是 `main()` 呼叫端(現行只比 "all"),`must_ratchet` 函式本身已支援 split(s2 查證)★。
- **效能觀測**(s2 補充):lane JSON 全量會加大 `impact --json` payload(樞紐檔常態 >3 條被 cap 擋住,體積可控),落地時量一次留數字。

## 工具清單(草)

| # | 項目 | 錨 |
|---|---|---|
| 1 | indirect 保送條件加 contract 值過濾(knob=1 時);★被降者收進獨立 `lane_items`,不進 `results`★ | `if contract and hop <= min(` |
| 2 | lane 產生端 cap(`LUMOS_IMPACT_LANE_N` 預設 3,排序 `(-score, node)`)、`meta["lane"]`/`meta["lane_dropped"]`、`final = pins + free + rescued + lane_items` | `final = pins + free + rescued` |
| 2b | ★下游分流全站清單★:人讀純文字分支加 lane 小節(score 用 `.get`;kind 表加 lane)/hook free 桶排除 lane/eval `eval_edit` 排除 lane★並把 rescued 排除釘明文★/`_touched_edit` lane 視同 pins 納入 | 各檔 grep `not x.get("pinned")` |
| 3 | hook 顯示新小節「守衛面參考(軟標記樞紐,未被本次改動直接證實相關)」+「另有 N 條未列出」 | `build_ranked_context` |
| 4 | eval:P@8 母體排除 lane(含 rescued 明文化) | `eval_edit` |
| 4b | pin_noise 進 verdict+gate「不准變多」(knob 轉正時啟用;現況只印,Codex r2 f3) | `must_ratchet` 旁 |
| 5 | per-split must 棘輪(呼叫端 `main()` 改,函式已支援) | `must_ratchet` |
| 6 | 測試:①knob=0 逐 byte ②P@8 母體不含 lane(含 `_touched_edit` 口徑,s2f2)③被降者在 JSON 且 cap 內 ④事故/INVARIANT indirect 不受影響 ⑤翻紅釘:拿掉 lane 容器→must_in_out 掉 ⑥人讀分支不 KeyError ⑦hook 不重複顯示(f4)⑧lane_dropped>0 時警告行 | test_lumos |
| 7 | 文件同步(★v2 重推,s3f1★):`Systems/lumos-cli-read.md:14`(「risk/標節點保送必看」句★落地後變假,行為合約級,連動其綁定測試★)、`skills/lumos-code-loop/reference.md`(--diff manifest 描述)、`Systems/retrieval-ranking.md`;02 檔不用動(v2 無 about 角色) | — |
| 8 | 前案回寫(s3f2):[[Projects/固定席扇出降權_計劃]] 四處「扇出=A 層降噪主角」標「已由 pin-denoise-a v2 取代(硬合約+參考道);扇出已試已殺」 | 前案 summary/258/393/399-404 |
| 9 | impacts_code 證據轉交(s3f3):E06/E08/E12+s1f2 的 12 處「必看但 about 不含」整批記進前案 impacts_code 後案節 | 前案「下一步:影響欄位」 |

## 已試已殺(留痕,勿復活)

- **扇出二元砍除**(2026-08-23):提到 ≥N 支檔的筆記直接踢出固定席——P@8 +5 格但必看 26→23,棘輪擋下。
  教訓:砍「量大」砍不準;本案改砍「軟合約搭便車」,且 v2 參考道=結構性保留(v1 的豁免/棘輪雙保險說法已作廢)。重試扇出須過同款考卷。

## 尺(v2)

- **固定席噪音數**:主目標(held 82→~39);落地時進閘「不准變多」。
- **P@8/nDCG**:逐 byte 不變(結構保證+測試釘;v1「應零影響」的講法錯,s2f11)。
- **must_in_out**:結構性不退(被降者仍在輸出);棘輪當覆核。★棘輪現況只比全體、換 rev 重立基線(Codex f4)——per-split 版列工具清單★。
- **out_top3_must**:觀測,held 應升。
- ★數字口徑統一(s2f1)★:主基準=**考卷口徑**(`--ablation` 輸出的 82/15);live 口徑(96)只用於逐條診斷,兩者差=goldset 未收錄的題外 pins。

## PRIOR-ART

`PRIOR-ART: borrow-design`——★誠實版(arch r1 抓到 v1 誤標)★:合約**值域**(INVARIANT/IRREVERSIBLE/RISK·*)是既有語彙
(`_impact_contract`/`_RISK_ENUM`),但「硬/軟**分級**、且分級決定保送」是**本案新造的規則**,全庫無先例
(「軟」在專案裡既有意涵是 doctor 提醒那條軸,別混用)。借的是業界 alerting 的 page vs ticket 同構
(硬約束叫醒人、軟提醒進佇列);參考道借自家 rescued 第三桶模式(同家族第二成員)。零新依賴。

## 實務隱患

- **召回風險**:v2 結構性歸零(被降者不離開輸出;free 不動)。v1 的三層網逐層有洞(豁免死於巨檔、rescue 只救 direct、
  棘輪不分 split)——s2f10 點名的三個洞是 v1 作廢的直接原因,留痕。
- 守衛面:動的是 hook 的機械保證面;走完整 design-loop(前案明文:動 impact 排序 light 硬拒)。
- 回滾:總開關一顆;行為差異=固定席成員變化,測試逐 byte 釘。
- 併發/效能:無新讀盤(合約與 about 都是既有材料)。

## 審計修正紀錄

### r1(2026-08-24;s1/s2/s3 + arch + Codex,五席)
s1 5(2 blocker)/ s2 13(4 blocker)/ s3 8(1 blocker)/ arch 2 major+1 ⚠ / Codex 4(3 blocker)。
★v1 主案被三個承重點打穿,整段作廢改 v2★:
**A about 豁免**=翻前案已鎖乙選項+`about 不是第四條入口` docstring 與兩條測試機械擋(s2f5/s3f1/s3f2/arch)+巨檔門檻讓豁免在震央 scripts/lumos(56 篇>8)必死(s1f1/s2f6/s3f3/Codex f2)→ about 全退,參考道取代;
**B 治標籤**=把「影響」語意塞進 about 欄、汙染前案三輪審出的定義(Codex f1);範圍也錯(15 處非 3,s1f2)→ 退出本案,證據轉 impacts_code 後案;標籤凍結(Codex f4:改標籤→rev 換→棘輪基線蒸發);
**C「降自由席」與「P@8 零影響」**=降級後過不了動態門檻直接被砍出輸出(s1f3 帶真 query 實證;前案舊坑重踩),且降級改變 P@8 計分母體(s2f11/s3f5)→ 參考道:不進 free、不進計分、結構性保留;
其餘折入:hop 綁 PIN_HOP 明寫(s2f4,引句錨不到但自查屬實)、RISK·不可逆/IRREVERSIBLE 撞名註明(s2f2)、knob 預設 0 死碼上線(s2f9)、單開關包住參考道(s2f13)、eval/hook top 口徑錯位——參考道不受 top(s2f12)、per-split 棘輪列工具清單(Codex f4)、hook 文案(s3f4)、文件散落三處(s3f7)、PRIOR-ART 誤標既有語彙改誠實版(arch major1;s2 判值域既有——兩席各對一半)、口徑統一(s2f1)、restamp 連動(s2f8,隨治標籤退出而 moot)。
arch ⚠(要不要擴 rescued)已在主案 v2 §2 正面回答。放行:無。
★教訓:v1 用一小時寫的主案,三個承重點全是「沒對前案已鎖的決策與機械測試」——立案時 `lumos decisions <前案> `+grep 測試,比反事實跑得快更重要。★

### r2(2026-08-24;s1/s2/s3 + arch + Codex,五席)
s1 5(2 blocker,含 patch 副本實測)/ s2 8(3 blocker,含工具清單逐項可執行表)/ s3 3(2 major)/ arch 2+2⚠(1 major)/ Codex 3(1 blocker)。全折:
**A lane 會被「非 pinned=free」分流吃回自由席**(s1f1 實測灌爆門檻+s2f1 四處分流)→ 獨立容器 lane_items+全站分流清單 #2b;
**B JSON/人看口徑偷換**(Codex f1+s2f3 人讀分支 KeyError+arch cap 層級)→ cap 在產生階段、三處同一份、meta 計數+未列出提示、棘輪重新有效;
**C eval 側**(s1f4/s2f2 `_touched_edit` 消融閘覆蓋縮水;s2f5 rescued 現在其實被算進 P@8 母體只是僥倖)→ #2b/#4 明文;
**D 驗收數字**(Codex f3 死碼臂+s1f3 incident 歸類隨 delta 變+s1f5 減法不成立)→ 不押絕對值、明寫 knob=1 臂;
**E 文件清單 v2 重推**(s3f1:lumos-cli-read「risk 保送必看」句落地後變假+綁定測試恆綠)、**F 前案扇出框架回寫**(s3f2)、**G impacts_code 轉交進清單**(s3f3)、
meta 慣例(arch)、per-split 落點(s2)、pin_noise 拆句(s2f8)、payload 觀測(s2)。放行:無。
arch ⚠×2:lane 字串命名(kind 先例,採納不改)、eval 排除無先例(以 #2b 明文化+rescued 對稱處理回答)。

## 下一步

r3(上限輪):五席審 v3 delta(參考道獨立容器/cap/全站分流清單/工具清單 2b-9/驗收改寫)。過了才動手;沒過攤人裁。
