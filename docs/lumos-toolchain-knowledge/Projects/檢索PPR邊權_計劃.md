---
type: project
status: doing
created: 2026-07-28
updated: 2026-07-28
signed_off: 2026-07-28
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

PRIOR-ART: ① 最小解層級——[[Projects/中心性重驗排程_計劃]] 已落 `_graph_pagerank(env, personalization=None)`，本計劃啟用參數位；cochange 挖掘複用 `_cochange_mine`。② 世界解——HippoRAG/fast-graphrag 以 PPR 做檢索傳播（2026 共識）；**在地反證必答**：A3（in-degree 加分）goldset 雙面被殺——PPR 與 in-degree 的差異＝**種子導向**（從 seed 傳播的個人化分數，非全域權威度），這正是 A3 死因（全域樞紐≠對此 seed 相關）所不涵蓋的軸；但此差異是假設，**考卷裁決，輸即殺**。③ 裁定=borrow-design。

## 規格（[S] 條款）

- [S1] **PPR 啟用**：`_graph_pagerank(env, personalization={seed: 1.0})`——teleport 改種子向量（dangling 質量回種子——對稱化後僅全孤島節點適用,近乎空轉,附註非關鍵機制）；**對稱化僅於 personalization≠None 時生效**（r2 升條款正文：None=維持有向＝既有語意分毫不動——現役 None 用戶=doctor Check S 與 cmd_stale 風險排序兩處（r2b 勘誤:原點名的 search A1 係幽靈用戶,search 從不呼叫 pagerank;真用戶 cmd_stale 補入迴歸清單）)；有種子時對稱化（r1 折入：vault 連結大宗=新筆記→舊節點，有向 PPR 漏 in-link-only 真相關者）。**落地同步義務**：③ 節點與 helper docstring 的「personalization=None 恆」句同工作內改寫。**種子向量規格（r2 補）**：多種子均攤（k 個種子各 1/k）；域外種子（moc/不存在）由 **helper 濾除後重歸一**（合約 owner=helper,呼叫端免防）；全數被濾或空集＝回空 dict，呼叫端視為「P 分量缺席」退 baseline 行為（不炸不偽裝）。純函式小圖可測。
- [S2] **cochange 邊權**：以 `_cochange_mine`（r1 勘誤：conf 出自 mine 非 transactions）挖 vault 檔共改，conf **有向**（conf(a,b)=s/freq[a]）——邊 a↔b（對稱化後）取 `w = 1 + max(conf(a,b), conf(b,a))`（r2 點名:support=2 且 freq=2 時 conf 頂格 1.0=最噪估計拿最強權重,w∈[1,2] 壓縮+考卷兜底,不另平滑）；沿挖掘層 support≥2 硬底線（不吃 display 層 cfg 閘）；repo 路徑→節點 rel 映射沿 eval 的 vault 前綴切法；僅加權既有 wikilink 邊。git 缺席/空史＝全邊權 1 degrade。
- [S3] **融合與消融（edit 面）**：hook/impact 推薦排序新增 P 分量——種子=**該檔 reverse-lookup 的 direct 節點集**（r2 措辭勘誤:hook/eval 均單檔呼叫,非 --diff 聚合），PPR 分數取 **free 池（動態閾後、名額截斷前）** Hazen 分位（r3 定死母體:閾前/閾後歧義收口）（r2b 修正：direct 種子若無合約本就是 free 池要排序的對象——逐出母體=其 P 無定義、gate 不可執行;種子 P 天然高=direct 排前,合理且與現行 direct 底分（_dbase）偏好一致（r3 歸因勘誤:L 分量本身不偏 direct）;固定席不參與重排故不入母體;moc 型候選不在圖=P 取 sentinel 0（母體外恆墊底,非 Hazen 分位值——不入母體計算,r3 明文）;hop≥2 被 L 底線預濾者不在池=不入母體）。**掛載機制（r2 定,r2b 補 production 側）**：impact `--json` 輸出逐候選 P 欄位（b1/b2 兩組 P=env knob 兩跑（`LUMOS_IMPACT_PPR`=off|flat|cochange,新增,沿 LUMOS_IMPACT_* 前綴使 history 自動記 knobs））,eval 同一 free 集 client-side 重排比較（(a)=現行 fusion 序,(b1)(b2)=P 融合序;融合式=R'=R+w_P·P 線性疊加,r3 明文）;gate 主指標=P@8。**轉正後 production 融合位置=閾後、名額截斷前重排**（P 融合後才截 quota——r3 修:eval --top 50/quota 10 vs hook 預設 top 8 的參數錯位使「截斷後洗牌」上線增益歸零;截斷前重排讓第 9-10 名可被 P 拉進前 8）;**[S4] 增項:A/B 期間 eval 與 production 的 top/quota 參數對齊**（考卷量的=上線跑的,同構才成立）。誠實註記:同集重排=增益上界受 baseline 選集封頂（被 baseline 剪掉的真相關救不回——此為掛載取捨,如實）。消融變體（r2 補歸因臂）：(a) baseline 現行、(b1) P 疊加·邊權全 1（純 PPR 貢獻）、(b2) P 疊加·cochange 邊權——b1/b2 分離使 cochange 貢獻可歸因。**裁決規則（r3 重寫:逐臂裁決,單位收口）**：b1/b2 **各自**對 baseline 過三態（兩庫 held 各自比較）——該臂任一庫退步超 0.02＝該臂死;該臂兩庫皆不劣於 −0.02 且至少一庫勝出 **>+0.02**（嚴格勝=帶外,統一帶寬）＝該臂過閘;其餘＝該臂不過。**轉正選臂**：全臂死＝整包刪;僅 b1 過＝轉正 b1（cochange 刪）;b2 過＝轉正 b2——cochange 名分由 b2−b1（兩庫 held **macro 庫平均**,r3 明文）>+0.02 判:達標=cochange 有功留邊權,未達=轉正 b2 但**如實註記 cochange 貢獻不可歸因（接受債）**。刪碼留墓碑（A3 忠實轉述,r3 三修:A3=雙面網格負增益即刪、墓碑留 code 註解、紀錄數字出自 train 面——不再宣稱「程序範式」,r2/r3 兩度發明程序細節被 canary 級查證拆穿的教訓在案）。**edit 雙庫卷 A/B（r2 遵既有裁定:凡動排序雙庫都要過）**：**[S4] harness 前置（r3 拆兩子項,原「未落地前非釘定跑」與自身前提矛盾——路由沒落地連非釘定都跑不動）**：**S4a repo 路由（硬前置）**＝eval_edit 支援 per-庫 repo（env `LUMOS_EVAL_REPO`,新增;須同時驅動 search 面 VAULT 且改寫 :283 的 LUMOS_EVAL_VAULT 跳釘守衛——否則自家守衛短路釘定;Landmark 卷 snapshot_commit 歸屬其 repo、worktree 於其 repo 建）——未落地=Landmark 腿**封存**、轉正閘暫僅 toolchain 腿並如實記單庫限制;**S4b snapshot 釘定（軟前置）**＝落地前 Landmark 腿為非釘定確認跑（漂移如實記）。**S4c top/quota 對齊**（r3 增,見掛載機制）。兩庫 train 聯集網格選 w_P → 兩庫 held **各自**確認 → P@8 超出 ±0.02 帶的退步即殺（帶寬理由（r2b 再修真）：**小樣本雜訊**——閘掛 held(toolchain 12 題,一翻≈0.010;free 不滿 8 時 P@min(8,n) 一翻可達 0.03=帶吸不住,方向為誤殺、如實警語)——toolchain 卷有 snapshot 釘定可重現；train 樣本薄=過擬合風險如實警語）；贏才轉正並記 `retrieval-eval-history.jsonl`。

## 邊界（明確不做）

- 不動 search 排序（BM25F/A1 先驗）；不動 related 面（無人工分卷可考——建卷＝另立標註計劃，本計劃不含）。
- 不新增持久化快取（cochange 現挖現用；慢於 2s 再議 v2）。
- 不因 cochange 新增圖上邊（只加權既有邊）。
- 消融輸＝整個 P 分量與 cochange 邊權刪碼（不留關閉的旗標殘骸）。

## 實務隱患

- **self-governance（弱）**：排序 advisory，考卷機械裁決——比人判閘更不依賴自覺；最壞=考卷輸、刪碼、零殘留。
- **payment/prod-irreversible（不適用）**：純讀、git 可逆。

## 測試策略（[S] 對應）

- [S1]：`t_ppr_personalized`——小圖 seed 傳播：seed 鄰居 > 兩跳 > 無關孤島；對稱化生效（in-link-only 鄰居拿高分）；personalization=None 行為與 [[Projects/中心性重驗排程_計劃]] 既有斷言不變（迴歸；None=有向,見 [S1] 條款）。
- [S2]：`t_cochange_edge_weights`——假 git 歷史（temp repo 兩檔共改 3 次）：共改邊權 > 未共改邊權；git 缺席 degrade 全 1。
- [S3]：考卷跑分——train|held 兩分卷（r2 傳播勘誤）結果記入 Verification（含 baseline 對照數字）；輸出入 `retrieval-eval-history.jsonl`。
- **實驗場（Landmark）**：edit 雙庫卷（toolchain＋Landmark 各 20 題人工標註）即實驗場——oracle=人工標註**與 cochange 無關,無循環**（r1 折入:related 自動評測=cochange 金標,考自己出的題,不可用）。

## 審計修正紀錄

- r3-std panel（2026-07-28,cap=3 終輪,canary=`goldset run-id` 假對帳鍵／ghosts 政策假援引／`--pin-remote` 假旗標:**3 席全 caught**;輪存活 blocker）：**blocker**＝eval(top50/quota10) vs hook(top8) 參數錯位使「閾後純重排」同構斷裂→重排改閾後截斷前+S4c 參數對齊。**major 批**＝裁決單位未定（殺整包 vs 轉正勝臂矛盾格）→逐臂三態重寫+嚴格勝=帶外+macro 聚合+b2 獨勝歸因債如實;[S4] 降級路自相矛盾→拆 S4a 硬前置(封存)/S4b 軟前置/守衛交互與 snapshot 歸屬補;A3 程序三度不符→忠實轉述不再稱範式;母體閾前後歧義→定死截斷前。**minor 批**＝(b) 記號、融合式明文、moc sentinel、_dbase 歸因、PPR knob 命名、macro 明文。**達 cap 攤牌**。
- r2-std panel（2026-07-28，canary=`seed_hits` 欄／`heldout-report.md` 產物／A3「半權重複跑」假程序：s1/s3 caught（s3 以三處紀錄互證拆穿假程序）、**s2 missed（作廢;其獨有 minor 經編排者自核採納）**;輪無效）：**blocker×2**＝①direct 種子本在 free 池、逐出母體=P 無定義→母體改 free 池全體;②Landmark 腿 harness 跑不了（--repo 硬編/釘定跳過）→[S4] harness 前置工作項+未落地前如實非釘定。**major**＝production 融合位置定閾後純重排（考卷同構）;裁決三態全帶寬化（殺/轉正/平局刪+b2−b1 同帶歸因+A3 假程序勘誤）;None 用戶清單修正（search A1 幽靈→cmd_stale 真用戶）。**minor 批**＝dangling 空轉附註、w 正規化明文、邊權 scoping 收口、帶寬算術改 held 數字+free 不滿警語、增益上界誠實註記、L 底線預濾不入池。
- r1-std panel（2026-07-28，3 席全 caught：canary=`--ppr-off` 假旗標／`txn_horizon` 假常數／`grid-sweep.tmp.json` 假產物;輪有效,r1 兩 blocker 經實查確認解除）：**major 批**＝train/test 殘留傳播（3席）→勘誤全文同步;幽靈 (c) 變體+B 分量舊名→消融臂重構 b1/b2（cochange 可歸因）;對稱化條件性升條款正文+③ docstring 同步義務;多種子/空種子規格（均攤/濾後重歸一/空=P 缺席）;Hazen 母體=free 池+掛載=同集重排（迴避名額截斷）+主指標 P@8;轉正閘遵雙庫裁定（兩庫 held 各自過）。**minor 批**＝±0.02 理由修真（小樣本非漂移）、conf 頂格飽和點名、「diff 命中」措辭、③ 寫全稱、PRIOR-ART mine 同步、train 8 題警語。
- r1 light 單席（2026-07-28，canary=「moc 種子照傳」跨檔矛盾 caught）：**blocker×2**＝①轉正閘引用不存在的 related 考卷、唯一替代=cochange 循環評分→**樞紐重定向 edit 面**（人工卷+train/held 俱在,種子導向天然合）；②canary 即 moc 矛盾→種子域規則明定。**major×4**＝有向 PPR 漏 in-link 真相關→對稱化；cochange 介面勘誤（mine/有向 conf/閾值/路徑映射）；Hazen 母體→候選集；零容忍殺閘→沿 eval 容忍帶。**minor 批**＝cochange 已是 related 金標的既有角色補記、split 名 train|held、light 進場引 ③ 為證係反向背書（承認：本輪自己就 ratchet 了）。**light ratchet：升 standard（-std panel）**。

## 誠實邊界

- PPR 對 A3 死因的差異論證是假設，唯一裁判＝考卷；「種子導向」在幾百節點小圖上與既有衰減分量（edit 面的 G）可能高度相關——消融各臂都可能輸，輸了就是答案。
- cochange conf 反映的是「編輯行為相關」非「語意相關」，雜訊面靠只加權既有邊緩解；殘餘偏差考卷裁。
