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
2. **參考道(reference lane)**:被 1 降的節點★不進自由席★——加 `lane: "soft-guard"`、`pinned: False`,
   ★不過門檻、不佔名額、不進 free 排序★,附加在 free(與 rescued)之後輸出;hook 顯示獨立小節
   「守衛面參考(軟標記樞紐,未被本次改動直接證實相關):」上限 3 條(顯示層截斷,JSON 全量)。
   ★為什麼不是降自由席★(r1 的血):自由席有動態門檻+名額,實測(s1f3 帶真 query 重驗)被降的會被**整個砍出輸出**,
   不是「排後面」——這正是前案記過的「降級≠保留」舊坑;參考道=結構性保留。
   ★為什麼不是 about 豁免★:翻前案已鎖決策(乙選項擱置理由)+ `t_impact_about_hit` 兩條測試機械擋 +
   巨檔門檻(scripts/lumos 被 56 篇標記>8)讓豁免在震央必死——三票否決,v1 作廢。
   ★為什麼不擴 rescued★(arch ⚠ 的回答):rescued 解的是「direct 被門檻砍」的缺口補席;本案是「整類降級後的保留」,
   語意不同;但實作**共用同一種輸出位置**(free 之後、pinned False、豁免門檻名額),是同一家族的第二個成員,不是第二種做法。
3. **結構保證(這是 v2 的核心賣點)**:free 集合與排序**完全不動** → P@8/nDCG 逐 byte 不變(v1 的「應零影響」是錯的,s2f11/s3f5);
   被降節點仍在輸出 → must_in_out 結構性不退,棘輪只當覆核;固定席噪音 -43/96(held,live 口徑)是**確定值**不是估計——
   降誰是決定論的,不需要帶 query 重算(v1 反事實的口徑錯誤 s1f3 在 v2 不再承重)。
4. **總開關**:`LUMOS_IMPACT_HARD_PIN`,★預設 0(上線即死碼)★(s2f9:預設問號沒法審)——
   照 `LUMOS_IMPACT_BASENAME_MATCH` 轉正流程:train 網格、held 驗一次、gate 全過才轉預設 1;0=舊制逃生。
   參考道整段包在 knob=1 分支內(s2f13:單開關回滾逐 byte)。
5. **goldset 標籤本案凍結**(Codex f4):不補標、不改答案——改了 rev 就換、棘輪重立基線,守衛蒸發。
   E06/E08/E12 那 3 條(加 s1f2 抓的另外 12 處)的「必看但 about 不含」證據★不是 about 漏標★(Codex f1:
   anchor-integrity 的 about 只標 pre-push 是**對的**,它「影響」全部 hook 是另一個語意)——
   整批記進 [[Projects/固定席扇出降權_計劃]] 的 impacts_code 後案當語料,本案不動欄位。

## 落地驗收(照症狀指令)

- 固定席噪音:held 82→預期 ~39(考卷口徑;live 96→53)、train 15→~8;★落地時 pin_noise 進閘「不准變多」★。
- P@8/nDCG:**逐 byte 相同**(測試釘)。must_in_out:不變(測試釘:被降節點仍在 JSON results)。
- out_top3_must held 0.083→應升(觀測)。
- ★eval/hook top 口徑錯位(s2f12,PPR 案舊坑)★:參考道不受 `--top` 截斷(同 rescued 慣例)→ 錯位不影響本案;
  但 per-split 棘輪(Codex f4:現行只比全體)列工具清單,本案順手修。

## 工具清單(草)

| # | 項目 | 錨 |
|---|---|---|
| 1 | indirect 保送條件加 contract 值過濾(knob=1 時) | `if contract and hop <= min(` |
| 2 | 參考道:降級節點 append 到 rescued 之後,`lane`/`pinned:False`,JSON 全量、人讀/hook 顯示上限 3 | `final = pins + free + rescued` |
| 3 | hook 顯示新小節(文案不得沿用「必看——帶著不能破壞的合約」,s3f4) | `build_ranked_context` |
| 4 | eval:pin_noise 口徑=真固定席(參考道不算噪音也不算固定席);P@8 母體不含 lane | `eval_edit` |
| 5 | per-split must 棘輪(held 單獨不退;換 rev 重立基線要印警告) | `must_ratchet` |
| 6 | 測試:①knob=0 逐 byte ②P@8 母體不含 lane ③被降者仍在 results ④事故/INVARIANT indirect 不受影響 ⑤翻紅釘:拿掉參考道→must_in_out 掉 | test_lumos |
| 7 | 文件同步:retrieval-ranking、skill 02/reference 的固定席描述(s3f7) | — |

## 已試已殺(留痕,勿復活)

- **扇出二元砍除**(2026-08-23):提到 ≥N 支檔的筆記直接踢出固定席——P@8 +5 格但必看 26→23,棘輪擋下。
  教訓:砍「量大」砍不準;本案改砍「軟合約搭便車」,且有 about 豁免與棘輪雙保險。重試扇出須過同款考卷。

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

## 下一步

r2:五席審 v2(delta=主案 v2/落地驗收/工具清單/尺/PRIOR-ART/隱患)。過了才動手。
