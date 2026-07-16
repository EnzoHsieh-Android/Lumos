---
type: project
status: doing
created: 2026-07-16
updated: 2026-07-16
tags:
  - type/project
  - status/doing
related:
  - "[[Systems/design-loop]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Systems/canary-audit]]"
  - "[[Systems/finding-refute]]"
summary: |-
  FLAG:DECISION
  KEY:問題=design-loop 常態跑滿 3 輪 cap 靠人裁,收斂慢。真因兩個結構病:①非定態目標——每輪折入改寫 spec,下輪審的是新文件,新 findings 一半在審上輪補丁,capture-recapture 的封閉族群/獨立捕獲前提偏弱(Codex 診斷);②「你一定找得到」framing 保證每輪必交 minor→G2 發現枯竭永不成立
  KEY:文獻定調——self-refinement 普遍 3 輪 plateau(SELF-REFINE/IMPROVE),cap=3 已是效率前緣;解不在加輪數/換停止規則,在「讓 r1 起點更高+後續輪只審 delta」
  KEY:藥方五條(划算排序):①R2/R3 嚴格 delta-scoped(物理只餵 diff+受影響合約+前輪爭議,留一席便宜全局哨兵)②gate 改 risk-cluster 三態帳(resolved/accepted-minor/disputed-major;停止=canary∧無disputed-major∧高風險claim雙finder覆蓋∧無新cluster;capture-recapture 降 advisory)③pre-flight cascade(機械checklist→小模型→panel)④辯方按共識路由(一致+有證據直折,低共識才開庭)⑤fold 迷你核對
  KEY:不做——SPRT(分布每輪變,不可用)/group sequential(收益極小)/Bayesian 停止(posterior 由 prior 主導,需先累 10+ loops 歷史回放校準,順序不可倒)
  DECISION:②動 loop status gate 語意=改守衛的守衛,高風險面——本計劃進實作前必過 design-loop(用舊 loop 審新 loop);①③④⑤純 skill 編排文字,trivial 級可先行
  DEP:[[Systems/design-loop]]｜[[Systems/loop-convergence-recording]]
---
# design-loop提效_計劃

> **狀態**：三路調研（web 文獻 ×3 + Codex 跨家族研究席）收斂的提效方案，尚未實作。緣起：使用者觀察「跑滿久才能收斂」（2026-07-16）。

## 問題（實測數據）

fromscratch-m1 三輪 9→6→3、T3 三輪 12→6→5——常態跑滿 cap 靠人裁實質收斂。拆 findings 性質：r1 大宗是清單型缺陷（未定義詞/矛盾/touchpoint 漏），r2/r3 一大半在審上一輪折入的補丁。

**兩個結構病**：
1. **非定態目標**（Codex 診斷，比「折入品質」更根本）：折入這個動作本身持續改寫受審對象——下輪的「新發現」可能只是新文字引入的；capture-recapture 的封閉族群＋獨立捕獲兩前提在此偏弱，殘餘估計不可當硬閘。
2. **minor 永續供應**：「你一定找得到」framing（防放水的必要之惡）保證每輪必交 minor → G2 發現枯竭結構上永不成立 → 人裁成為事實出口（T3/fromscratch 皆如此）。

## PRIOR-ART（2026-07-16 真搜：web×3 + Codex 席）

- **Self-refinement 文獻**（SELF-REFINE arXiv:2303.17651 / IMPROVE arXiv:2502.18530）：迭代精煉普遍 1-2 輪最大收益、3 輪 plateau——**cap=3 已是效率前緣**，實測 9→6→3 完全吻合。解在輸入品質與 delta 化，非輪數與停止規則。
- **軟體審查經典**（Wohlin/Runeson capture-recapture 十年總結 jss04；El Emam DPM）：估計器該用在「要不要開下一輪」的**事前決策**；experience-based 校正因子（誤差 10.5%→7%）＝歷史回放校準路線。DPM（發現速率曲線）需時間戳，選配。
- **LLM cascade/routing**（ICML 2025 dekoninck25a；ICLR 2024 uncertainty routing）：便宜先掃、不確定才升級是正統；成敗核心在 quality estimator 非層數；**路由用可觀測訊號**（席間重疊/severity 分歧/證據座標缺失/辯方翻案史），不用模型口頭 confidence。
- **Debate 負面證據**（EACL 2026 findings.268）：拉長互辯出現 problem drift/無進展——背書現行「禁互辯＋獨立席」設計，並主張更早截斷。
- **統計停止規則裁決**（Codex）：SPRT 不可用（資料生成分布每輪變）；group sequential 形式可做收益極小；Bayesian 最適配但小樣本下 posterior 由 prior 主導——**先累語料後校準，順序不可倒**。
- 裁定＝**borrow-design**：借 inspection 的事前決策思想 + cascade 架構 + cluster 化記帳，全部原生實作於 skill/loop status。

## 藥方（划算排序）

1. **R2/R3 嚴格 delta-scoped + 全局哨兵**（Codex「若只能改一件」）：物理上只餵「折入 diff + 被改 claim 的上下游合約 + 前輪爭議」，另留一席便宜模型全文掃防漏。一石三鳥：省 token/消措辭型重複發現/恢復輪間可比性。改 skill 派工規則。
2. **gate 改 risk-cluster 三態帳**：同根因碎片 findings 合併 cluster，狀態 resolved / accepted-minor / disputed-major。停止＝canary caught ∧ 無 disputed-major ∧ 高風險 claim ≥2 獨立 finder 覆蓋 ∧ 本輪無新 cluster。capture-recapture 降 advisory。**解 minor 永續供應**。動 `loop status --panel` gate 語意 + record 欄位。
3. **pre-flight cascade**：panel 前一道機械 checklist（未定義旗標/欄位/檔名、交叉引用、範圍自違、CLI touchpoint、測試策略對應）+ 小模型掃——清單型缺陷排乾，r1 從 v2 水準起跑，一輪收斂（K=1 本就允許）從理論變可能。
4. **辯方按共識路由 + 免辯方條件明文化**：機械證實（可執行證據+編排者自核）免辯方；席間一致+有獨立證據直折；只有低共識 ≥major 開庭。省每輪 opus pass。
5. **fold 迷你核對**：折完派便宜 agent 只看 delta 問「鏡像段跟了嗎/新舊句打架嗎/新詞有定義嗎」——殺 r3 型「補丁沒同步」findings。
6. **（後續,等語料）** 歷史 replay 校準 Bayesian expected-loss 門檻（golden 語料 10+ 份後）；severity 錨句進派工模板（major=照實作會做錯行為;文件精度/測試枚舉=minor 除非漏合約）。

## 里程碑

- **M1（skill 層,trivial 級可先行）**：①③④⑤ + severity 錨句——全是 SKILL.md/templates.md 文字改動,不動 code。✅ **已落地（2026-07-16,SKILL.md 五處:pre-flight 2.7/severity 錨/辯方路由制/fold 迷你核對/delta-scoped+全局哨兵;user-scope symlink 即時生效）**
- **M2（動 gate code,必過 design-loop）**：② risk-cluster 帳——`canary record` 加 cluster 欄位、`loop status --panel` 改停止條件。**改守衛的守衛,高風險面,進實作前本計劃過 design-loop（舊 loop 審新 loop）**。
- 驗收信號：下一個真實 spec 過 loop 的輪數/wall-clock/token 對照本計劃前的基線（fromscratch-m1 ≈3 輪/~2h）。

## M2 詳細規格（v2;r1 折入）

**範圍**：只改「記錄欄位 + panel gate 停止條件」。不動 canary 判定、不動辯方、不動 legacy(非 panel)路徑。

### 記錄層（cmd_canary 的 record 子指令擴一個選配欄）

- `lumos canary record ... --clusters "名=狀態,名=狀態,..."`：該輪存活 findings 經編排者**按根因合併**後的 risk-cluster 清單。狀態白名單三態:`resolved`(已修並核)/`accepted-minor`(小事,接受不改——note 須帶一句理由,紀律非機械)/`disputed-major`(大事,還在吵/未修)。名=kebab 短 slug(編排者命名,跨輪沿用同名=同 cluster)。
- **W-record 歸屬(r1 Codex+B 折入)**:cluster 合併是編排者一次性彙整,**每輪至多一筆記錄帶 `--clusters`**(建議掛該輪最後一筆);「該輪帶 cluster」=輪級判定(任一筆帶即算,同 capture_counts 慣例 scripts/lumos:2318);同輪 >1 筆帶 → 讀側 rc2(防照抄 capture_counts「取第一筆非空」靜默吞衝突)。
- 不帶 `--clusters` = 無-cluster 舊帳(panel 既有三條合取 gate 不變;「legacy」一詞保留給非 panel 循序模式,兩者勿混)。**混用守衛(r1 A+B 折入,執行時機與升級裁定釘死)**:判定在**讀側 `loop status`**(同 round 混用守衛前例 scripts/lumos:2418-2429;record 保持純 append 不讀回歷史——否則破「只改記錄欄位」範圍刀);粒度=輪級;**模式以該 loop 首輪定錨**:首輪無 cluster → 整個 loop 走無-cluster 舊 gate 到底,後續輪帶 clusters → 讀側 rc2 並提示「M2 前開始的 loop 不升級,開新 loop id」;首輪有 → 全輪皆須帶(輪級),半帶 rc2。
- 解析驗證(r1 B 折入,比照 capture_counts 防禦慣例 scripts/lumos:2226):狀態不在白名單 rc2;名含空白/逗號/等號 rc2;同輪同名重複 rc2;**尾逗號空段靜默過濾**;整值空字串=視同未帶;**段缺 `=` → rc2 明確訊息**(嚴禁未捕捉例外崩潰)。

### gate 層（loop status --panel 停止條件改造）

該 loop 首輪帶 clusters 時,合取改為**兩條**(r1 折入:原條 3 降 advisory——A 席揭穿其字面版擋 accepted-minor 首現=隱性最少兩輪、自打「解 minor 永續供應」;放寬版(只擋新 disputed-major)又與條 2 冗餘。dryness 本質是人裁訊號,不硬閘):
1. **輪有效**(canary caught 全數,0 missed)——不變。
2. **cluster 帳無 disputed-major**:跨輪 fold(同名 cluster 取物理序最後一筆狀態,同 [[關係層主網_實作計畫]] M3 cascade 帳本 `_ledger_fold` 前例 scripts/lumos:4841,語意平行不共用函式)後,無任何 cluster 終態=disputed-major。**fold 只採 caught 輪的 clusters(r1 C 折入)**——missed 輪即使帶 clusters 一律忽略+status 顯示「missed 輪 cluster 已忽略」警告(對齊「missed 者 findings 剔除」慣例 scripts/lumos:2311;否則睡著席一筆 resolved 可靜默清掉先前 disputed-major)。**取代「存活 max≤minor」**——blocker/major finding 必須屬於某個 disputed-major cluster(未修)或 resolved cluster(已修核);accepted-minor 只准裝 minor(編排者誠實紀律,GIGO 同 anchors)。
- (advisory,不進合取) **新生 cluster 數**:判定輪首次出現的 cluster 名(含各終態)照印——根因級 dryness 訊號,供實質收斂人裁參考,不硬擋(硬擋要嘛冗餘要嘛復活 minor 卡門)。
- (advisory,不進合取) **capture-recapture 降 advisory**:照算照印(仍是有用訊號),**退出合取**——非定態目標下封閉族群/獨立捕獲前提偏弱(Codex 裁決),不再當硬閘;無 counts 不再 fail-closed(cluster 帳接手守門)。
- **accepted-minor 帳永久可查**:`loop status <id>` 輸出 cluster ledger 表(名/終態/首現輪/末更輪)——接受不是消失,是記帳(防合法掃地毯,天花板條的機械兌現)。

### 明確不做（範圍刀）

- 不做 cluster 自動聚類(合併是編排者判斷,GIGO 誠實記);不做高風險 claim 雙 finder 覆蓋條件(需 claim 級標注,v1 砍——capture_counts advisory 已給重疊訊號);不動 legacy 循序模式 gate;不動 G1 refcheck 錨;不做跨 loop cluster 庫。

### 測試策略

record 解析:三態白名單過/壞狀態 rc2/名含非法字元 rc2/同輪重名 rc2/尾逗號空段靜默過濾/空字串=未帶/段缺 = → rc2 訊息非崩潰/不帶=無-cluster 舊帳不變;W 歸屬:同輪 >1 筆帶 clusters → 讀側 rc2;混用守衛(讀側):首輪無 cluster 後續帶 → rc2 提示開新 loop/首輪有半帶 → rc2;fold:同名跨輪最後狀態勝(disputed→resolved 放行、resolved→disputed 回鎖)/**missed 輪 clusters 忽略+警告**(睡著席 resolved 不得清 disputed-major);gate:fold 後有 disputed-major 擋/無 disputed-major 且 canary 全 caught 放行(**含 r1 單輪帶 accepted-minor 首現=可收斂**,K=1 真可行);advisory:新生 cluster 數照印/無 counts 不再 fail-closed/殘餘照印不進合取;ledger 表:accepted-minor 顯示於 status 輸出;無-cluster loop 走 panel 既有三條合取迴歸不變;非 panel 循序 gate(K-streak∧G1∧G2)不受影響。

## M2 審計修正紀錄

**pre-flight（2026-07-16,M1 新步驟 2.7 首戰）**:panel 前便宜 agent 排乾 4 條清單型——①cmd_canary_record 函式名不存在(實為 cmd_canary 的 record 子指令)②「四條合取」標題與「第4項退出合取」自相矛盾(實為三條)③「四條舊合取」與現碼不符(panel 舊 gate 為三條)④「legacy」一詞雙義(panel 無-cluster vs 非 panel 循序)已消歧。全數修真檔,未耗 panel 席。

**r1（2026-07-16,panel:3 sonnet 異鏡頭+Codex 否決席;M1 新規則首戰輪）**:canary a✗(advisory 高殘餘時回鍋硬條件的矛盾,A 席漏——其 F1/F2 帶行號自核採信)b✗(未定義 ledger 查詢旗標,B 席漏——其 F1/F2/F3 帶行號自核採信)c✓(憑空第四狀態自相矛盾+帳外孤兒,精準)。**caught 1/3=無效輪**;誠實記:兩 missed 席均挖出深層真洞卻漏表面植入——canary 或藏過頭,r2 校準難度+framing 加碼。Codex:核心可建、無結構性障礙,gate 改造點行號級列明。存活 6 條 distinct 全折 v2:
- **條 3 降 advisory(major,A 自核)**:字面版擋 accepted-minor 首現=隱性最少兩輪、自打核心賣點;放寬版與條 2 冗餘 → gate 收兩條合取,新生 cluster 數改 advisory 供人裁。
- **W-record 歸屬(major,Codex+B)**:每輪至多一筆帶/輪級判定/同輪多筆 rc2(防 capture_counts「取第一筆」慣例靜默吞衝突)。
- **混用守衛時機+升級裁定(major,A+B 合併)**:判定在讀側(record 純 append 不讀回,護範圍刀);首輪定錨模式;隱患節裁定折回本體消兩節矛盾。
- **missed 輪 fold 污染(major,C)**:fold 只採 caught 輪,missed 輪 clusters 忽略+警告——否則睡著席可靜默清 disputed-major。
- **解析邊界(major,B)**:尾逗號/空值/缺 = 三態補全,比照 capture_counts 防禦慣例,嚴禁未捕捉例外崩潰。
- **M3 引用消歧(minor,B)**:補 wikilink 與 `_ledger_fold` 行號。

## 實務隱患（M2）

- **self-governance 循環（最重）**：M2 改的是「判定所有 spec 能否進實作」的閘——gate 邏輯錯了會系統性放行壞 spec 或永遠擋好 spec。緩解＝測試逐條對齊合約 + 本 spec 過 design-loop（舊閘審新閘）+ anchor 護測試。
- **編排者誠實依賴加深**：cluster 合併與三態標定全是編排者自報——把 major 標成 accepted-minor 即偽收斂。緩解＝accepted-minor 須帶理由 + ledger 永久可查 + canary 仍驗審計員(但不驗編排者,誠實記:比 capture-counts 的 GIGO 面更大)。
- **混用守衛的邊界**：升級裁定已折回規格本體(首輪定錨,r1)——此處僅留提醒:讀側 rc2 的錯誤訊息必須指路「開新 loop id」,否則使用者會誤以為要改舊紀錄。
- **fold 語意撞名**:cluster fold(最後狀態勝)與 M3 cascade 帳本 fold 同模式但**不同資料源**(canary-log vs rel-cascade jsonl)——實作勿共用函式硬湊,語意平行即可。
- **誤擋逃生口**:gate 兩條合取下唯一硬擋=fold 後 disputed-major(新生 cluster 數僅 advisory 不擋門,r1 已降);誤擋的出口仍是既有「實質收斂人裁」——不新增旗標。

## 天花板（誠實）

- delta-scoped 有漏看風險——全局哨兵是便宜緩解非保證；哨兵本身是弱檢查器。
- risk-cluster 的「同根因合併」是編排者判斷——cluster 切錯（兩個真問題併一個）會漏；GIGO 同 anchors。
- 這些提效都不改變誠實天花板：收斂仍只證「醒著的審計員沒再找到」，非「沒有更深的洞」。
- 提效後 minor 被 accepted 掉不再擋門——**accepted-minor 帳要留著可查**（不是消失,是記帳),否則變成合法掃地毯。
