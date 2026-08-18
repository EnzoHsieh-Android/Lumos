---
type: project
status: done
created: 2026-08-18
updated: 2026-08-18
tags:
  - type/project
  - status/done
summary: |-
  KEY:立案動機(2026-08-18)——語料前進後的第一顆★真紅★:hook P@8 0.6842<0.70,held 未標 0(標註刷新兌現「量到品質非過期」後的真訊號)。症狀紅指令=`python3 governance/eval/retrieval_eval.py --goldset … --split held`(hook_p_gate False,已實跑翻紅)
  KEY:驗屍(逐案解剖,10 held edit 案)——拖分主力三案:E05 0.25(retrieval_eval.py)/E03 0.375(test_lumos.py)/E14 0.375(lint-watch-check.sh);固定席噪音爆炸另計(E02 34 pin 33 噪/E03 25 pin 24 噪;must 35 筆僅 5 筆被 pin 接住)
  KEY:★關鍵反直覺:三臂離線對照無人能救★——fusion 0.6842/bm25 0.6717/graph 0.6717,最爛案三臂同爛(E05:0.25/0.12/0.38)→ 病在候選層非權重層,調權重天花板極低
  KEY:假說(可證偽,H1-H4)——H1 垃圾查詢毒化文字臂:E05/E14 的 delta 文本是 shebang/檔頭,L=1.0 給到 native-windows-support 這種無關節點;H2 hub 檔 direct 氾濫:test_lumos.py 被 20+ 計劃節點 inline 引用,每個都以 direct 基分洗版(標註實證這些=0);H3 真主沉底:E14 正主 lint-version-watch L=0 排最後(s=0.30=裸 direct 基分);H4 固定席連坐過寬(RISK/INVARIANT 廣域安全網在守衛面節點大增後爆炸)——H4 另軌不影響 P@8
  KEY:實驗計畫(train 調參/held 驗證/凍結=考卷×Landmark 雙場同好;參數凍結紀律沿 v1.2)——EXP1 查詢品質閘:delta 文本 shebang/過短→L 臂靜默(離線可模擬);EXP2 hub 降權:direct 基分按「該檔被引用節點數」idf 式衰減(離線可模擬);EXP3 兩者疊加;各以 held P@8+勝負案清單裁決
  KEY:落地路徑誠實——EXP 勝出後的修法動 scripts/lumos impact 排序(演算法密集=design-loop light 硬否決,走完整 loop);本節點先只承載診斷+離線實驗,不動產線 code
  DEP:governance/eval/retrieval_eval.py(診斷原語)｜scripts/lumos(impact 排序,未動)｜scratchpad autopsy-edit-rows.json(解剖存證)
related:
  - "[[Projects/標註刷新_計劃]]"
  - "[[Projects/hook必看召回修復_計劃]]"
  - "[[Systems/retrieval-ranking]]"
---
# 檢索edit面真紅_計劃

> 白話:語料前進後考卷量到了真實的推薦品質——不及格(0.684<0.70)。解剖發現病不在「三種排序訊號怎麼加權」(三種單獨看都一樣爛),而在**進場的候選就是錯的**:改檔案時的「變更文字」有時只是檔頭雜訊,卻被拿去全文比對給了無關節點高分;被幾十個計劃提過一嘴的熱門檔案,每個提過的節點都擠進推薦;真正的正主反而因為文字不像而墊底。

## 症狀紅指令(已實跑翻紅)

```
python3 governance/eval/retrieval_eval.py --goldset governance/eval/retrieval-goldset.json --split held
# → ❌ hook P@top_k ≥0.70(hook_p=0.6842);held unjudged 0/318=非標註債
```

## 驗屍現場(2026-08-18,語料 9fcb761)

| 案 | 檔 | P@8 | 現場 |
|---|---|---|---|
| E05 | retrieval_eval.py | 0.25 | delta=shebang;前五名全 [0] 且 L 0.91-1.00(含 native-windows-support L=1.0);真 [2](標註刷新兩節點)排 6-7;cochange-guard/retrieval-ranking 等相關項全漏 |
| E03 | test_lumos.py | 0.375 | direct 洗版:主動影響幅度偵測/公開精簡版/code側刪除 等實作計畫全因 inline 引用測試檔而 direct 進場,標註全 0 |
| E14 | lint-watch-check.sh | 0.375 | delta=shebang;L=1.0 的無關節點佔位;正主 lint-version-watch L=0、s=0.30 排第八 |

三臂離線:fusion 0.6842 / bm25 0.6717 / graph 0.6717——無臂可救,候選層病。

固定席另軌:pin_noise E02=33/34、E03=24/25;must_pinned 全 held 僅 5/35——RISK/INVARIANT 連坐在守衛面節點大增後爆炸(H4,獨立戰場)。

## 假說(可證偽)

- **H1 垃圾查詢毒化文字臂**:delta 文本=shebang/檔頭時,L 高分為偽訊號。證偽法:該類案把 L 臂靜默離線重排,P@8 不升即偽。
- **H2 hub 檔 direct 氾濫**:被 N(大)個節點 inline 引用的檔,單一引用的訊號價值 ~1/N。證偽法:direct 基分乘 idf 式衰減離線重排,E03 類不升即偽。
- **H3 真主沉底**=H1/H2 的合成結果(正主僅裸 direct 基分,被偽高分擠出)。
- **H4 固定席連坐過寬**:另軌,不動 P@8;候選修法=pin 資格加「與該檔 direct 或 hop≤1」的檔案側條件。

## 實驗計畫(EXP,離線模擬,不動產線)

1. EXP1:查詢品質閘——delta 首行為 shebang/長度<門檻 → 該案 L 臂權重 0;離線重排全 held,報 macro P@8+逐案勝負。
2. EXP2:hub 降權——direct 基分 ×(1/log(1+引用節點數));同上報法。
3. EXP3:1+2 疊加;若 macro ≥0.70 且無案倒退>0.1 → 進落地階段。
4. 落地階段(另起):spec 動 scripts/lumos impact 排序 → design-loop(演算法密集=完整 loop)→ TDD → 雙場(考卷+Landmark 實測)同好才凍結。

## 刻意不做

- 調三臂融合權重(離線已證天花板 0.6842,反直覺證據在案)。
- 為過卷改標註(金標剛人裁放行,動標=作弊;考卷誠實界線沿標註刷新)。
- H4 與 P@8 混治(固定席另軌另案)。

## 實務隱患

- **過擬合 held**:實驗在 train 選型、held 只做最終確認一次;逐案勝負清單防「macro 升但個案崩」。
- **雙場紀律**:凍結前 Landmark 真機同驗(調參紀律沿 v1.2:考卷精度×實場條數/延遲雙好)。
- **[self-governance]**:本節點階段純離線觀測,無擋人面。

## EXP 結果(2026-08-18,離線重排)

| 排法 | held macro P@8 | 逐案 |
|---|---|---|
| 基線(現行 fusion) | 0.6842 | E05 0.25/E03 0.38/E14 0.38 拖分 |
| **EXP1 垃圾查詢閘** | **0.7092 ≥0.70** | E05 0.25→0.38、E14 0.38→0.50,**零案倒退** |
| EXP2 hub 降權(粗) | 0.6717 | 整分打折粒度太粗(動不到 direct 基分項),E05 反降——★不足以判 H2 死刑,留待實作層帶真公式重驗★ |
| EXP3=1+2 | 0.7092 | 同 EXP1 |

train 交叉驗:6 案全非垃圾查詢 → EXP1 零觸發零倒退(0.6667 不動)。規則自由度極小(判準=delta 首字元 `#!` 或全文<20 字),非對 held 擬合。

**裁定:H1 確認(垃圾查詢毒化文字臂),EXP1 規則具落地資格**;H2 未定(需真融合公式層面的手術,離線模擬搆不到);H3=H1 合成結果隨之緩解;H4 固定席另軌未動。

## 下一步(等放行)
spec「edit 面查詢品質閘」動 `scripts/lumos` impact 排序(演算法密集=design-loop 完整 loop)→ TDD → 考卷×Landmark 雙場同好才凍結。E03 型(hub direct 洗版)P@8 天花板受候選集限制,列 H2 後續。

## 戰果(2026-08-18,本案收案)

H1 落地([[Projects/edit面查詢品質閘_計劃]],design-loop 一輪收斂+落地後發現收窄判準)後:**held hook P@8 0.6842→0.7467,六閘全綠(gate 總判定 PASS),零案倒退,凍結預設參數**。fusion-vs-graph 與 free-p95 兩顆老紅燈同時治癒——垃圾 L 的位次污染是共同根因,驗證「病在候選層」的診斷。殘留:H2(hub direct 氾濫,E03 0.38 天花板受候選集限制)/H4(固定席噪音,must_pinned 5/35)列後續戰場,事故驅動再啟。

