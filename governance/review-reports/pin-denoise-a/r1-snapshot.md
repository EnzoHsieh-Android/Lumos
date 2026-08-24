---
type: project
status: doing
created: 2026-08-24
updated: 2026-08-24
summary: |-
  FLAG:DECISION
  KEY:立案(2026-08-24 Enzo「開」)——held 固定席噪音 96 條(live 口徑;考卷 82)佔比過半,out_top3_must held 0.083 被它拖死。逐條分解:58 條=「間接一跳+RISK 類軟合約」樞紐筆記(pitfalls-code-loop 7x/lumos-cli-read 6x/lumos-refcheck 6x…)搭便車
  KEY:主案=★間接保送只認硬合約(INVARIANT/IRREVERSIBLE),RISK 類間接降自由席;about_hit 豁免(命中留固定席);同時治 about 漏標★——反事實:held 噪音 -43/96(45%),被誤降的必看 3 條全是 about 漏標受害者(anchor-integrity 守全部 hook 卻只標 pre-push)
  KEY:已試已殺留痕——扇出二元砍除(2026-08-23):P@8 +5 格但必看 26→23 被棘輪擋;勿憑直覺復活,重試須過同款考卷
  KEY:尺=must_in_out 棘輪(硬底線)+ 固定席噪音數(目標降)+ out_top3_must(觀測)+ 硬合約必看 pinned 不退(新合約候選);症狀指令見正文
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

## 主案:硬合約保送 + about 豁免 + 治標籤(三件一起)

1. **間接保送收窄**:`contract in (INVARIANT, IRREVERSIBLE)` 才保送;RISK 類 indirect 降自由席按分數競爭。
   direct 保送不動(23 條 direct 噪音另議,本案不碰——一次一刀,可歸因)。
2. **about_hit 豁免**:被 1 降級的節點若 `about_hit`(語意上真的關於這支檔、stamp 未過期)→ 留固定席。
   ★這是 about_code 第一次接上降噪——當豁免證據,不是入口;召回方向安全(只留人不踢人)★。
3. **治標籤**:E06/E08/E12 那型的 about 漏標,逐篇人核補標(anchor-integrity 補 pre-commit/impact-hook.py、
   design-loop 補 test_autonomous_loop.py…);本案落地前先補,反事實重算應為必看 0 降。
4. 總開關 `LUMOS_IMPACT_HARD_PIN`(預設?——★開關預設值走考卷:train 掃、held 驗一次★),0=舊制逃生。

## 已試已殺(留痕,勿復活)

- **扇出二元砍除**(2026-08-23):提到 ≥N 支檔的筆記直接踢出固定席——P@8 +5 格但必看 26→23,棘輪擋下。
  教訓:砍「量大」砍不準;本案改砍「軟合約搭便車」,且有 about 豁免與棘輪雙保險。重試扇出須過同款考卷。

## 尺(全部既有,零新建)

- **must_in_out 棘輪**:硬底線,掉一個就紅(擋 R1 誤傷)。
- **固定席噪音數**:主要目標,per-split 印;★本案落地時考慮進閘「不准變多」★(同棘輪語意,方向相反)。
- **out_top3_must**:觀測,held 應上行。
- **P@8**:不動(固定席不計分)——本案對它應零影響,變了就是實作寫錯。

## PRIOR-ART

`PRIOR-ART: borrow-design`——合約分級(硬 INVARIANT/IRREVERSIBLE vs 軟 RISK)是圖譜既有語彙,本案只是讓保送邏輯尊重它;
業界同構:alerting 的 page vs ticket 分級(硬約束才叫醒人,軟提醒進佇列)。無新輪子、零新依賴。

## 實務隱患

- **召回風險**(最大):R1 誤傷靠 about 豁免+治標籤+棘輪三層接;若 held 重算仍降必看 → 停手回設計。
- 守衛面:動的是 hook 的機械保證面;走完整 design-loop(前案明文:動 impact 排序 light 硬拒)。
- 回滾:總開關一顆;行為差異=固定席成員變化,測試逐 byte 釘。
- 併發/效能:無新讀盤(合約與 about 都是既有材料)。

## 下一步

design-loop(standard,3 席+架構+外家 Codex)→ 過了才動手;實作連 #3 治標籤一起。
