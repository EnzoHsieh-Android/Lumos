---
type: project
status: doing
created: 2026-07-28
updated: 2026-07-28
tags:
  - type/project
  - status/doing
related:
  - "[[Projects/檢索優化_計劃]]"
  - "[[Projects/節點靜態先驗_調研]]"
  - "[[Projects/中心性重驗排程_計劃]]"
summary: |-
  KEY:[r1 樞紐重定向]目標面=**edit(impact hook 推薦)**非 related——r1 light 審出考卷實況:goldset 無 related 人工分卷,唯一 related 自動評測以 cochange 當金標=treatment 洩入 oracle 必自我確證(循環);edit 卷=人工標註+train/held 切分俱在,且 PPR 種子導向天然合 edit 面(diff 命中節點=種子)。PPR(personalization 種子向量,對稱化圖)+cochange 邊權(僅加權既有邊);**轉正閘=edit 卷 A/B:train 網格、held 確認、容忍帶內退步即殺+刪碼(A3 前例)**。源=2026-07-28 閉環盤點②
  KEY:v1 範圍刀[r1 反轉]——只動 edit/hook 面推薦;search 與 related 面不動(related 的人工分卷不存在,建卷=另立計劃的標註工程);不新增持久化快取
  DECISION:[2026-07-28]light 進場→r1 即 ratchet(blocker×2)——「引 ③ 為證」被審計員正確指為反向背書(③ 也是 light 炸升);連兩案實證:演算法密集 spec 直接走 standard,light 先驗值該加「演算法密集」硬否決訊號(回饋 design-loop skill 待辦)
---
# 檢索 PPR＋cochange 邊權計劃

> 緣起：2026-07-28 閉環盤點——R 融合現有 BFS-decay（hop 距離衰減）分量；GraphRAG 生態共識（HippoRAG 系）是 PPR 傳播。cochange 共改帳現只用於 commit 提醒，未進任何排序。

PRIOR-ART: ① 最小解層級——[[Projects/中心性重驗排程_計劃]] 已落 `_graph_pagerank(env, personalization=None)`，本計劃啟用參數位；cochange 挖掘複用 `_cochange_transactions`。② 世界解——HippoRAG/fast-graphrag 以 PPR 做檢索傳播（2026 共識）；**在地反證必答**：A3（in-degree 加分）goldset 雙面被殺——PPR 與 in-degree 的差異＝**種子導向**（從 seed 傳播的個人化分數，非全域權威度），這正是 A3 死因（全域樞紐≠對此 seed 相關）所不涵蓋的軸；但此差異是假設，**考卷裁決，輸即殺**。③ 裁定=borrow-design。

## 規格（[S] 條款）

- [S1] **PPR 啟用**：`_graph_pagerank(env, personalization={seed: 1.0})`——teleport 改種子向量（dangling 質量回種子）；**傳播圖對稱化**（r1 折入：本 vault 連結大宗=新筆記→舊節點，有向 PPR 會漏掉 in-link-only 真相關者；HippoRAG 慣例同）。種子必須在節點集內（moc 不在圖中,moc 種子=空結果,呼叫端自濾——r1 canary 矛盾修正）。純函式小圖可測。
- [S2] **cochange 邊權**：以 `_cochange_mine`（r1 勘誤：conf 出自 mine 非 transactions）挖 vault 檔共改，conf **有向**（conf(a,b)=s/freq[a]）——邊 a↔b（對稱化後）取 `w = 1 + max(conf(a,b), conf(b,a))`；沿挖掘層 support≥2 硬底線（不吃 display 層 cfg 閘）；repo 路徑→節點 rel 映射沿 eval 的 vault 前綴切法；僅加權既有 wikilink 邊。git 缺席/空史＝全邊權 1 degrade。
- [S3] **融合與消融（edit 面）**：hook/impact 推薦排序新增 P 分量——種子=diff 命中節點集，PPR 分數取 **候選集內** Hazen 分位（r1 折入：全圖母體會把候選壓進窄帶失鑑別）。消融變體：(a) baseline 現行、(b) P 疊加（w_P 網格,融合層與權重歸一明定於實作）。**edit 卷 A/B**：`--split train` 網格選權重 → `--split held` 確認（r1 勘誤：分卷名=train|held 非 test）→ P@8 **超出既有容忍帶（±0.02,沿 eval 現行 gate 慣例）的退步即殺**（r1 折入：零容忍殺閘在 ±1pp 活語料漂移下=雜訊定生死）；贏才轉正並記 `retrieval-eval-history.jsonl`。

## 邊界（明確不做）

- 不動 search 排序（BM25F/A1 先驗）；不動 related 面（無人工分卷可考——建卷＝另立標註計劃，本計劃不含）。
- 不新增持久化快取（cochange 現挖現用；慢於 2s 再議 v2）。
- 不因 cochange 新增圖上邊（只加權既有邊）。
- 消融輸＝整個 P 分量與 cochange 邊權刪碼（不留關閉的旗標殘骸）。

## 實務隱患

- **self-governance（弱）**：排序 advisory，考卷機械裁決——比人判閘更不依賴自覺；最壞=考卷輸、刪碼、零殘留。
- **payment/prod-irreversible（不適用）**：純讀、git 可逆。

## 測試策略（[S] 對應）

- [S1]：`t_ppr_personalized`——小圖 seed 傳播：seed 鄰居 > 兩跳 > 無關孤島；對稱化生效（in-link-only 鄰居拿高分）；personalization=None 行為與 ③ 既有斷言不變（迴歸；None 時維持有向＝③ 語意不動）。
- [S2]：`t_cochange_edge_weights`——假 git 歷史（temp repo 兩檔共改 3 次）：共改邊權 > 未共改邊權；git 缺席 degrade 全 1。
- [S3]：考卷跑分——train/test 兩分卷結果記入 Verification（含 baseline 對照數字）；輸出入 `retrieval-eval-history.jsonl`。
- **實驗場（Landmark）**：edit 雙庫卷（toolchain＋Landmark 各 20 題人工標註）即實驗場——oracle=人工標註**與 cochange 無關,無循環**（r1 折入:related 自動評測=cochange 金標,考自己出的題,不可用）。

## 審計修正紀錄

- r1 light 單席（2026-07-28，canary=「moc 種子照傳」跨檔矛盾 caught）：**blocker×2**＝①轉正閘引用不存在的 related 考卷、唯一替代=cochange 循環評分→**樞紐重定向 edit 面**（人工卷+train/held 俱在,種子導向天然合）；②canary 即 moc 矛盾→種子域規則明定。**major×4**＝有向 PPR 漏 in-link 真相關→對稱化；cochange 介面勘誤（mine/有向 conf/閾值/路徑映射）；Hazen 母體→候選集；零容忍殺閘→沿 eval 容忍帶。**minor 批**＝cochange 已是 related 金標的既有角色補記、split 名 train|held、light 進場引 ③ 為證係反向背書（承認：本輪自己就 ratchet 了）。**light ratchet：升 standard（-std panel）**。

## 誠實邊界

- PPR 對 A3 死因的差異論證是假設，唯一裁判＝考卷；「種子導向」在幾百節點小圖上與 hop-decay 可能高度相關（B 分量已是距離衰減）——(b)(c) 兩變體都可能輸，輸了就是答案。
- cochange conf 反映的是「編輯行為相關」非「語意相關」，雜訊面靠只加權既有邊緩解；殘餘偏差考卷裁。
