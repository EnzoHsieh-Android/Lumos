---
type: project
status: done
created: 2026-07-09
updated: 2026-07-09
tags:
  - type/project
  - status/doing
related:
  - "[[design-loop]]"
  - "[[canary-audit]]"
  - "[[convergence-evidence-gate]]"
  - "[[risk-tiered-review]]"
summary: |-
  FLAG:DECISION
  KEY:把 design-loop/code-loop 從「6 輪同族循序」壓到「≤3 輪:1 輪平行多樣 panel + 條件式精修」,同準確度、砍 token+wall-clock。動機=6 輪跑在文獻有用邊界外(2-3 輪抓絕大部分增益)、且同族循序=相關信號(9 judge 只值 2 票)、framing「你一定找得到」對抗 G2 收斂逼跑滿 cap
  PRIOR-ART:搜過三線文獻(非憑印象):多智能體辯論 2-3 輪報酬遞減(arxiv 2506.00066)/同族 panel 錯誤相關「9 judge 2 票」(2605.29800)/平行廣度常勝循序深度、最優比按難度(2408.03314、2502.20379)/自適應穩定停(2510.12697)。裁定 borrow-design 原生實作,不引依賴
  KEY:收斂判準(2026-07-09交叉查文獻升級)=falsification-存活(辯方零≥major,borrow falsification>voting)∧低分歧(W審計員獨立都≤minor,非「1喊blocker被駁+其餘clean」;borrow Value-of-Variance)∧自適應提交(全體獨立乾淨即K=1,borrow CGES省~69%呼叫);tier映射門檻(high需2一致輪/standard 1輪)
  KEY:核心洞=買獨立廣度而非相關深度——1 輪 3 個「多樣」審計員(canary 型別 a/b/c 各異 + 鏡頭各異 + ≥1 跨家族 qwen)的獨立信號 > 6 輪同族循序;canary per-auditor 平行做(注意力檢查更強非更弱)
  KEY:結構=Round1 平行 panel(覆蓋一次買齊)→ Round2-3 條件式循序精修(只在存活 ≥major 才跑,只重審 delta)→ 收斂判準改 verdict 穩定非輪數;tier=standard 只跑 R1、tier=high 才 R1+≤2 精修(複用 risk-tiered-review)
  KEY:誠實天花板=canary 注意力測試正交於辯論共識,壓縮須保留 per-auditor canary;「2 票」定理反對天真擴 panel→多樣性(型別+鏡頭+家族)是關鍵非數量;本計劃自己該用新規則 dogfood
  DEP:[[design-loop]]
  TEST:待實作;本計劃以「用新 ≤3 輪規則跑自己收斂」為第一驗證
---
# loop 三輪壓縮_計劃

> 把 canary-護的對抗審計 loop(design-loop + code-loop)從 6 輪同族循序壓到 ≤3 輪,同準確度、砍成本與時間。緣起:使用者指出 6 輪太耗;PRIOR-ART 搜證 6 輪跑在有用邊界外。

## 背景:為什麼 6 輪是浪費
- **文獻**:多智能體辯論 2-3 輪抓絕大部分增益、超過 3 輪報酬遞減甚至退化(arxiv 2506.00066)。
- **相關信號**:審計員同族(sonnet/opus)+ 同 framing + 循序 → 「9 judge 只值 2 票」(2605.29800)的相關性,6 輪 ≪ 6 份獨立信號。
- **framing 對抗收斂**:`skills/lumos-design-loop/SKILL.md` 的「你一定找得到至少一個」保證每輪必交 minor,G2 發現枯竭壓不到底,逼跑滿 cap(exec-anchor-gate 空燒、claude-reinject 撞 glue 天花板同根)。

## 方案(borrow-design,零依賴原生;R2 重設計:解 R1 的 B1/B2/B3)

**核心 reframe(解 B1)**:舊 loop 把兩件事混進「輪」——(a) 覆蓋/多樣、(b) 收斂信號。壓縮把它們拆開:
- **覆蓋/多樣 → panel 寬度 W**(平行,一輪買齊)。
- **收斂信號 → panel 內「跨審計員獨立同意」**(輪「內」判定,不是輪「間」findings 遞減)。這就是 G2 序列語意換掉的東西——平行拓樸配 agreement,不配 dwindling 序列。

### 一輪 panel 的結構
一「輪」= 平行派 **W 個多樣審計員**(W 由 tier 定,見下):
- **canary 型別跨 slot 輪替**:W 個 slot 依 `[(slot) mod 4]` 分派 a/b/c/d(型別覆蓋一輪買齊,不攤 4 輪)。**canary 只給同族(Claude)審計員**——它是注意力測試。
- **鏡頭各異**:正確性 / 邊界可執行性 / 整合知識同步 / …(W>3 時加資源與併發、回滾)。
- **≥1 跨家族(qwen)當獨立軸,不帶 canary**:qwen 貢獻 findings + agreement,**不計入 canary 注意力票**——這解掉 R1-B「qwen 無 canary 破 per-auditor-canary」的矛盾:**per-auditor-canary 只約束同族(測注意力);qwen 是獨立性軸(測 agreement)**,兩軸分離。degrade(無 key/API 掛)→ 純 Claude panel,agreement 仍算、只是少一條家族獨立軸。

### 判定(編排者一次做)
1. **注意力票**:逐同族審計員判 canary caught/missed。**missed 者的 findings 剔除**(不作廢整輪;沿用 `canary-audit.md` 的 panel 變體規則)。輪有效 = **≥2 個帶 canary 審計員 caught**(「9 judge 2 票」的獨立票門檻)。
2. **findings 去重**:跨有效審計員報告,依 `(spec 段落, 瑕疵性質)` 合一(編排者判,同今日跨輪去重、只是一次跨 W 份;非全機械=誠實天花板)。
3. **辯方**:對存活 ≥major 派 opus 辯方(`skills/lumos-design-loop/templates.md` §2)。

### 收斂判準(定案:結構信號取代 count/二值;整合 R2 + 散文收斂三機制)
一輪 panel 收斂 = **四條合取**(全建在 framing 汙染不到的結構上;推導與文獻見下「散文收斂」節):
1. **輪有效**:≥2 個帶 canary 同族審計員 caught(注意力閘;<2 → 輪無效,耗 1 cap、重跑)。
2. **falsification-survived**:每條 ≥major(缺陷類)派辯方 → 零存活(非投票;辯方是既有 falsification 協議)。
3. **ODC class-gating**:只有**缺陷類**(blocker/major/實質 minor)進上條與收斂判定;cosmetic/潤飾/enhancement 記錄但**不 gate**(隔離無界散文噪音)。
4. **capture-recapture 殘餘 < 門檻**:從 W 個獨立審計員 findings 的**重疊**估殘餘缺陷(高重疊=枯竭=收斂;低重疊=續跑)。這是取代「G2 findings 序列枯竭」的結構信號——平行 panel 天生提供 capture-recapture 要的獨立檢驗員。門檻按 tier(high 嚴)。
- **有限 done 判準(AC)**:另要求 spec 的驗收場景(AC)齊備、關鍵決策(AC/失敗/rollout/相容)在(完整性不可判定 → 搬到有限外部物,不判「散文完美」)。
- 未達 → fix → 下一輪只重審 delta,新 W-panel(canary 重分派)。cap=3 panel 輪。**G1 引用座標 refcheck 保留**(平行不影響)。
- **agreement/低分歧** = capture-recapture 高重疊的定性面(R2 加的啟發式,此處被 ③④ 形式化取代)。

### tier→寬度(解 B3)
`difficulty.params(tier)` 擴傳 `panel_width`:**standard=3(cap 1-2 輪)、high=5(cap 3 輪、需 2 個確認乾淨輪)**。對上文獻「最優平行/循序比按難度」。此為 `governance/autonomous_loop/difficulty.py` 的真 code 擴充(現只回 {need,maxr})。

### 留痕(解 B2)
`lumos canary record` 加選填欄 `--round <id>`:一輪 panel = W 筆記錄共享 round-id(保留 per-auditor caught/missed 給 gov 可靠度史)。`cmd_loop_status --gate --panel` 按 round-id 分組讀:一組 = 一輪,判「≥2 caught ∧ 存活 max≤minor」。無 round 欄的舊記錄 = legacy 單體輪(向後相容,K-streak∧G2 舊模式不變)。

## 誠實天花板
- **canary 注意力測試 vs agreement 收斂,職責分離但非全正交**(修 R1-HH1):同族審計員的 canary 測注意力、agreement 測收斂;兩者透過「輪有效門檻(≥2 caught)」耦合——輪無效(canary 掛太多)則 agreement 不算數。這是設計內的耦合,已明定判定順序(先剔 missed、再算 agreement)。
- **「≥1 跨家族」的獨立信號增益未量化**(修 R1-HH2):2 Claude + 1 qwen 依「9 judge 2 票」曲線仍 <3 獨立票;本設計取「≥2 caught + 家族獨立軸」為工程折衷,**不宣稱等值 K 次獨立**——只宣稱「一輪多樣 panel > 一輪單審計員,且 ≥ 舊 K=2 循序的相關信號」。qwen degrade 時獨立性降,agreement 仍走同族≥2。
- **去重非全機械**:編排者判「同段同性質」,判錯偏「多留」(寧可多跑一輪)。
- 平行 W 審計員讀 W× spec:token 與舊 6 輪循序讀 6× 相比,W=3 省一半、W=5 約平;**wall-clock 大降(平行)**。最好情況(一輪乾淨)~2.5× 省。
- 文獻是 benchmark 準確度,非 canary/辯方構件;移植的是「輪數 vs 廣度」與「收斂點」,非 1:1。

## 知識同步影響(修 R1:補漏列)
落地須改:① `skills/lumos-design-loop/SKILL.md`(每輪流程 → panel 結構 + agreement 收斂)② `skills/lumos-code-loop/SKILL.md`(**非「同構」帶過**:code-loop 工作副本是 diff/patch,canary hunk 落真改動集外,panel 化的 diff 分派另述)③ `skills/lumos-design-loop/templates.md`(**新增平行 panel 派工模板** + W-slot canary 分派;現 §1-2 是單審計員循序語境)④ `governance/autonomous_loop/orchestrator-prompt.md`(步驟 3-8 改平行 + cross_audit 從 §2.5 提前接 panel)⑤ `Systems/design-loop.md`(收斂判準 KEY)⑥ **`Systems/convergence-evidence-gate.md`**(G2 序列 → panel agreement,本改動的核心語意變更)⑦ **`scripts/lumos` `cmd_loop_status`**(新 `--panel` gate 謂詞)⑧ **`governance/autonomous_loop/difficulty.py`**(`params` 加 panel_width)。

## 實務隱患
- **平行並發峰值**:一輪同時 spawn W auditor;W=5 時並發與 rate-limit 壓力,實作限並發或分批。
- **qwen 成本 per-round(修 R1-F10)**:qwen 每 panel 輪一次,standard=1 輪=1 次、high 最多 3 輪=3 次(非 per-spec 一次)。仍 ~$1-3/月級;無 key → degrade 純 Claude(agreement 走同族≥2,不 fail-closed 卡死;但 tier=high 的 fail-open 政策衝突見下)。
- **tier=high fail-open 衝突(修 R1-IH1)**:`risk-tiered-review` high 級關 fail-open(degraded 不放行)。panel 模式 qwen degrade 時,high 級**不自動放行、走 unconverged requeue 留人**(維持既有 fail-closed),不因 panel 化而破例。
- **去重認知負荷**:一次跨 W 份報告去重,比循序逐輪判省次數但單次負荷高;W=5 時編排者可能漏合——偏「多留」兜底。
- **自主 loop 無人攤牌**:panel 一輪不收斂 → unconverged requeue(既有);tier=high 仍走硬證據閘(G1 + agreement 記錄)。
- **canary 型別 d 在 panel(修 R1-HH3)**:W-slot 輪替含 d 型時,d 仍須裸檔名(refcheck 抽取域外,同 orchestrator 既有限制);W≤3 時可只用 a/b/c。

## R2 定案補充(解 R2 blocker + 真 major;glue 細節交 TDD)
- **F1 mode 並存 footgun(blocker)解**:panel 模式**取代**循序,不並存。legacy 單體循序**僅**在 panel 無法跑時 fallback(可用審計員 <2)。`cmd_loop_status`:偵測 log 內有 `round` 欄 → 強制走 panel 謂詞;`--panel` 與帶 `round` 的 log 二者一致才讀,**混用(舊模式讀到 round-tagged log)直接報錯拒讀**,不靜默把 W 筆當 W 輪(殺 footgun)。G2 在 panel 模式**不跑**(agreement 取代),非「並存」。
- **F3 agreement 形式定義(2026-07-09 交叉查文獻升級:從二值門檻→falsification+低分歧+自適應提交)**:收斂判準**不是**「辯方後 max severity ≤ minor」這個二值門檻(會藏分歧:1 個多樣審計員獨立喊 blocker、辯方駁回、其餘 clean → max=clean 判收斂,但「一個獨立鏡頭看到 blocker」本身就是風險信號)。改三條合取:
  - **① falsification-consensus(非投票;borrow 2602.14251「falsification-driven > voting」)**:每條 ≥major 派辯方 → **零條存活**。lumos 辯方本就是 falsification 協議,文獻證它勝過投票聚合(去偏)。
  - **② 低分歧(borrow 2602.07186「Value of Variance」:收斂=降不穩定非表面對齊)**:W 個有效審計員的**獨立** severity 評估要**集中**——即「零 ≥major 存活」必須來自「大家獨立都 ≤minor」,不是「一個喊 blocker 被駁 + 其餘 clean」。分裂 panel(blocker vs clean 並存)= 不穩定 = 不收斂,即使辯方殺光那條 outlier。
  - **③ 自適應提交(borrow CGES 2511.02603 / DASE 2605.04236)**:round-1 panel 若 falsification 後**全體獨立 ≤minor**(高後驗)→ 立即提交(這才是 K=1 的正當理由,非拍板);分裂/碎片證據 → 續 round-2。CGES 實證這類提交把呼叫從 16→4.9(**省 ~69%**)、準確度差 0.06pp——正對成本痛點。
  - tier 映射門檻(borrow 2603.24481「<5% high / <10% routine」):high=需 2 個一致乾淨輪或全體獨立零 finding;standard=1 輪。
  - **agreeableness-bias 防護(borrow 2510.11822「Beyond Consensus」)**:panel 太容易一致是假共識;lumos 已有 canary 注意力閘 + refute-framing(「你一定找得到」)+ 辯方對沖之;**額外**:全 clean 零 minor 的 panel 罕見(refute-framing 保證通常有 minor),異常全 clean 視作輕度可疑、不因它降門檻。
- **F8 qwen 在收斂的角色**:qwen 計入 agreement 的**否決權**(它報 ≥major 且辯方沒駁倒 → 不收斂),但**不計入 canary 注意力票**(輪有效門檻只數同族 caught)。理由:qwen 是獨立性軸,它的反對是信號;但它沒過注意力測試,不能單獨「證明醒著」,故只作否決不作背書。
- **F4 W<2 caught(輪無效)後續**:輪無效 → 不算收斂、**算耗 1 輪 cap**、下一輪全新 W-panel 重跑(不補單槽——補單槽破壞平行獨立性)。cap 耗盡仍無有效輪 → 手動 loop 攤牌人裁、自主 loop unconverged requeue。
- **去重偏多留 vs 卡收斂(r2c-F4)解**:去重**以「同 (段落,性質)」嚴格合一為預設**(不是偏多留);只有「編排者無法判是否同一洞」時才保留兩條。同一洞的多份報告合成一條 finding,辯方對一條裁決,不會殘存重複條卡收斂。(修正 R2 前的「偏多留」措辭——那會系統性阻收斂。)
- **交 TDD(不在設計散文摳)**:`--round` 產生者/唯一性/部分寫入判定、`--panel` 謂詞分組實作、delta 產生法(git diff vs snapshot)、`__PANEL_WIDTH__` 注入佔位符、並發分批門檻——皆實作級,紅綠測試釘死(見 design-loop-completeness-ceiling:glue 留實作真測)。

## 散文收斂:signal-preserving 停機(2026-07-09 交叉查文獻;解「framing 對抗收斂」根本張力)
**問題**:aggressive refute-framing(「你一定找得到」)保證每輪必出 minor → count-based 收斂(G2 findings 枯竭)對散文永遠不觸底;放軟 framing 能收斂卻**弱化審計信號**。**核心洞:framing 汙染「數量」,不汙染「結構」**——停機改讀 framing 汙染不到的三種結構信號,完全不動 framing:

- **① Capture-recapture 估殘餘(主信號;軟體檢驗界 10+ 年研究,生物學起源)**:多個**獨立**檢驗員讀同一文件,從彼此 findings 的**重疊率**統計估「總缺陷母體」→ 減已找到 = **殘餘估計**;殘餘 < 門檻即停(IEEE 852741 / ScienceDirect S0164121203000906)。**為何不干擾信號**:停機不看「這輪有沒有出 minor」(count 被 framing 汙染),看**重疊的統計結構**——高重疊(獨立審計員都找到同一批)= 母體枯竭 = 收斂;低重疊(各找各的)= 母體大 = 續跑。framing 讓他們找更多,capture-recapture 用「找到的東西的結構」不用「數量」。**且它天生要多個獨立檢驗員——正是平行 panel 本體**,是本設計缺的收斂信號的精確形式(比我 R2 加的「低分歧」啟發式更量化,低分歧≈高重疊≈少殘餘,此為其形式化)。誠實天花板:小樣本估計會出極端值(IEEE 7426632),當一個信號不當 oracle。
- **② ODC class-gating:把母體拆成「有界缺陷 vs 無界潤飾」(Chillarege/IBM,ODC)**:findings 按正交 type + severity 分類;**只有缺陷類(blocker/major/實質 minor)gate 收斂,cosmetic/潤飾/enhancement 記錄但不擋**。無界的散文精修噪音關進「trivial/cosmetic」類隔離,不是壓制。這是我已加的「實質收斂 early-exit」的有原則版(ODC 給它真分類法)。
- **③ 完整性移出散文(undecidable)→ 有限外部判準**:CACM/IEEE 證「spec 充分完整性**理論上不可判定**」——這就是散文永不收斂的數學根源(沒有演算法能判「散文完美沒」)。解=**別在散文上量完整性,搬到有限可檢的外部物**:每條驗收場景(AC)映射一個測試,「done」=所有 AC 有測試 + 關鍵決策(AC/失敗處理/資料歸屬/rollout/相容)齊備(spec-review-checklist),非「散文完美」。把不可判定的散文問題換成有限清單(=borrow-list 的 spec-by-example / spec-kit AC)。

**統一原則**:三者都繞開被 framing 汙染的 count——capture-recapture 讀 overlap 結構、ODC 讀 class 結構、AC 讀 coverage 結構。**停機信號建在結構上,framing 一個字都不用改**。lumos 落地:平行 panel 已提供 capture-recapture 要的獨立檢驗員 → 加「重疊估殘餘」當主收斂信號 + ODC 只讓缺陷類 gate + AC 覆蓋當有限 done 判準,三合一即「散文收斂 without 干擾信號」。

## code-loop 差異(2026-07-09 交叉查文獻;code-loop 不全盤沿用 design-loop)
程式碼有散文沒有的東西(可執行+可靜態分析),文獻證 code review 最佳解是**異質 ensemble** 非純 LLM panel:
- **異質 panel**(borrow:AutoSafeCoder / Multi-Agent Code Verification via Info Theory arxiv 2511.16708,submodularity 證異質分析器各加獨立資訊):確定性驗證器(`.lumos/lint.json` SARIF linter / 測試套件 / type checker / mutation 冒煙)當**一等 panel 成員**與 LLM reviewer 並列。錯誤剖面與 LLM 正交=**真獨立票**,直擊「9 judge 2 票」(純 LLM 即使多樣仍相關)。
- **辯方可執行 falsification**(borrow:Greptile TREX / CodeRabbit sandbox「grep 沒東西≠證明 bug,先跑再信」):code-loop 辯方跑測試/repro/mutation 確認-或-殺 finding,可執行反證 > 論證反證。
- **capture-recapture 跨異質 finder**:LLM ∪ linter ∪ 測試失敗的重疊(且 capture-recapture 本生於軟體檢驗,回娘家)。
- 繼承 panel 機制 + capture-recapture 收斂;但 panel 成員換異質、辯方改可執行——非「design-loop 換 canary 名」。落點:`skills/lumos-code-loop/SKILL.md` panel 段(已補)。
- **異質 finder 接線已機械化(2026-07-09 ship)**:`_capture_counts_from_finders`(跨 finder 正規化+數重疊)+ `lumos loop capture-counts --finder ...`(吐 capture_counts + 殘餘 + 可貼的 `canary record --capture-counts` 串)。orchestrator 把 LLM reviewer / `pitfalls --diff` SARIF linter / 測試失敗 / mutation 存活各當一個 `--finder`,機械算重疊(人手數易錯)。t_capture_counts_from_finders + t_loop_capture_counts_cli;859 passed。

## 審計修正紀錄

### R2(2026-07-09,平行 panel dogfood 第 2 輪,重審重設計稿;canary c/a/b 輪替)
- **canary 3/3 caught**(AGREEMENT_QUORUM / §5.3 / --panel-strict 全被點名憑空)——注意力連兩輪平行都守住。
- **severity 降**:R1(3×blocker)→ R2(1 blocker F1 + ~6 major),且性質從「approach 錯」轉為「規格不夠細」——架構已收斂,殘留是 glue。
- 存活真 finding(排 3 canary):F1 mode footgun(blocker)/ agreement 未定義 / qwen 收斂角色 / W<2 後續 / 去重偏多留卡收斂 / delta 機制未定義 / round-id 實作規格——**已於上「R2 定案補充」逐一解或交 TDD**。
- **裁定**:不跑 R3。理由=(1)唯一 blocker(F1)已解為明確設計決策;(2)其餘全 glue 實作細節,續審只會再生「沒指定到位元」的散文 finding(claude-reinject/exec-anchor-gate 同型),TDD 紅綠釘更對;(3)**本實驗雙重成功**:證平行 panel 機制(2 輪 = 舊 6 輪循序覆蓋、canary 6/6、wall-clock ~1/3)+ 再次實證 glue 天花板(壓縮 spec 自己也撞它,正是自食其果的活教材)。**架構收斂,轉 writing-plans + TDD。**

### R1(2026-07-09,新規則 dogfood:平行多樣 panel × 3,sonnet A正確性/B邊界/C整合;無跨家族 qwen——手動 Agent tool 限 Claude,此軸未驗)
- **canary 3/3 caught**(a=§4.2壞引用 / b=--stability-window / c=PANEL_WIDTH_DEFAULT,三審計員各抓各的)——一輪平行完成舊機制需 3 輪循序的注意力覆蓋。
- **存活 blocker(三鏡頭獨立收斂 + 真 code 佐證,非假陽性,不折入即修——需重設計)**:
  - **B1 收斂機制正面衝突(致命)**:本設計「1 輪平行 panel + K=1」與剛落地的 `convergence-evidence-gate` G2 衝突——G2「findings 枯竭」是**序列語意**(單調不增、末輪≤1,`scripts/lumos:1685-1689`);need=1 退化成「findings==0 才收斂」,與本設計「clean/**minor** 即收斂」(minor⇒findings≥1)矛盾,閘永遠 FAIL。**根因**:壓縮不能只改 skill——平行 panel 用**廣度**產生獨立信號,但 G2 的收斂信號建在**深度序列**上;兩者拓樸不合。
  - **B2 canary-record 資料模型**:`cmd_canary` 1輪1筆,裝不下 3-auditor panel;平行 canary missed 無「下一輪」可作廢。
  - **B3 tier 不驅動寬度**:`difficulty.params()` 只回 {need,maxr},無「並行寬度」維度;`PANEL_WIDTH_DEFAULT` 憑空(且是 canary,但真設計確實缺此常數與能力)。
- **major**:去重演算法未定義(影響 G2 計數)/ cross_audit 提前 R1 時 evidence 空退化 + qwen 無 canary 能力破「per-auditor canary」/ 成本 model per-spec vs per-round 差 3× / 知識同步漏列 `convergence-evidence-gate.md` + `templates.md`(平行需新派工模板)+ `scripts/lumos` G2 code 改動。
- **裁定**:R1 severity=blocker,**不收斂**。但**實驗本身成功**——機制(平行 panel、3 canary 一輪全抓、獨立收斂真 blocker)驗證了「廣度取代相關深度」;而它抓到的 B1 是真設計缺陷,證明壓縮的正確 scope 比原設想大。
- **redesign 方向(B1 的解,實驗浮現)**:平行 panel 的收斂信號**不能沿用 G2 的序列枯竭**——改為 **cross-auditor 獨立同意**(adaptive stability / 多樣 panel 都判無 ≥major = 收斂),這才配平行拓樸。故壓縮**必須同時改** `convergence-evidence-gate`(G2 語意)+ `scripts/lumos` cmd_loop_status,非 skill-only。待使用者裁定是否進此擴大 scope。
