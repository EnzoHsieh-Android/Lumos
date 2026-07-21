---
type: project
status: doing
created: 2026-07-21
updated: 2026-07-21
tags:
  - type/project
  - status/doing
related:
  - "[[Systems/design-loop]]"
  - "[[Systems/risk-tiered-review]]"
  - "[[Systems/convergence-evidence-gate]]"
  - "[[Projects/design-loop提效_計劃]]"
summary: |-
  FLAG:DECISION
  KEY:問題=design-loop 粒度只有兩檔(trivial 完全跳過｜standard 完整 panel),中間是空的——小而不 trivial 的 spec(小 flag/非金流小邏輯)沒輕量檔可走,直接掉進 standard 完整審=過度審(使用者觀察,2026-07-21)
  KEY:方向裁定——只解「小任務被過度審」(降成本方向),不碰「大任務多跑」(那半撞 cap=3 效率前緣/RHB 縱深非解藥,已由 [[Projects/design-loop提效_計劃]] 定調,本計劃不重開)
  KEY:d5 經濟學合規——輕量檔=便宜 spec 便宜審=缺陷分層定價,降成本非精確度軍備競賽,教義站這邊(見 [[Systems/design-loop]] d5);d4 定位合規——抬品質非保正確,light 只誠實定價最便宜的 spec,正確性照歸下游 code-loop+測試+逃逸帳
  KEY:★進場不對稱★——判「是不是 light」是兩個可靠度不同的問句:往上「有無危險訊號」機械可靠(存在性偵測)→硬否決;往下「夠不夠小」機械不可靠(無訊號≠簡單,誠實天花板那半)→只能 advisory。支點=硬否決擋危險、軟提示只買發現性、ratchet 兜誤判
  KEY:硬否決(往上,reliable,零新分類器)——命中任一即 light 不給選強制 standard+:①風險類命中(複用 [[Systems/risk-tiered-review]] RISK_CLASSES)②碰到硬合約(invariant 級,impact/co-change 偵測)③體積超天花板(行數精確,size 軸非難度判斷)
  KEY:軟提示(往下,advisory,唯一新東西)——三訊號全沒響+體積遠低天花板→design-loop 進場跳一句「這條像 light,要用嗎」maker 拍板;維持 advisory 不更強(2026-07-21 使用者裁定)。價值=發現性非準確度:防 maker 忘了 light 存在而什麼都留 standard;提錯有兩層兜(maker 確認+執行期 ratchet 自癒)
  KEY:light 跑什麼(壓縮 loop)——pre-flight cascade(複用 M1 排乾清單型)+1 輪·1 通才審計員·canary 護·K=1(踩 [[Projects/design-loop提效_計劃]] 已埋「r1 通才席」伏筆);收斂=該輪 canary caught 且無存活 ≥major;自癒=1 輪抓到存活 major→自動 ratchet 升 standard 跑完整 panel
  KEY:三檔取代兩檔——light<standard<high;ratchet「只升不降」(risk-tiered-review 現有)延伸三級;忘宣告→預設 standard(fail-safe,永不更少)
  KEY:★meta 自我約束★——加一檔+ratchet 延伸動到 loop status gate 語意=self-governance 風險類=high;按 risk-tiered-review 與 M2 前例,本計劃 code 部分(第1/3步)自己須過完整 design-loop 才實作(舊 loop 審新 loop);軟提示+pre-flight 純 skill 層可先行
  KEY:體積天花板數值——留實作 replay 校準,不預設魔術數(2026-07-21 使用者裁定)
  FLOW:brainstorming產spec→lumos 算進場資格{硬否決三訊號任一命中→強制standard+｜全沒響+體積小→advisory 提示 light}→maker 拍板檔位→[light?]{pre-flight cascade→1 通才席 canary 護 K=1→該輪 caught∧無存活major?收斂放行｜抓到存活major→ratchet 升 standard 走完整 panel}→[standard/high?]現行 loop 不變
  DECISION:方案 A(人工宣告+壓縮 loop+硬 ratchet)+機械建議拆兩方向(硬否決 reliable/軟提示 advisory);拒「機械大部分自動定檔」(踩誠實天花板)
  DEP:[[Systems/risk-tiered-review]](硬否決複用 RISK_CLASSES+ratchet 只升不降)｜[[Systems/design-loop]](壓縮 loop 派工/canary/K=1 原語)｜[[Systems/convergence-evidence-gate]](loop status gate 認第三檔)｜skills/lumos-design-loop(進場提示+派工模板)
  PRIOR-ART:①最小解=既有 risk-tiered-review 三檔化+複用 RISK_CLASSES 偵測器+M1 pre-flight+design-loop提效 已埋通才席,借既有機制小修非造新機制 ②世界解過沒=LLM cascade/routing(ICML2025 dekoninck25a/ICLR2024 uncertainty routing)+self-refine 3輪plateau 已於 [[Projects/design-loop提效_計劃]] 2026-07-16 真搜並吸收,本題同機制家族引用該搜尋(便宜先掃/不確定才升級=正統;路由用可觀測訊號非模型口頭 confidence) ③裁定=borrow-design(借 cascade 事前決策思想+tiering,原生實作於 skill/loop status/risk-tiered-review)
---
# design-loop輕量檔_計劃

> **狀態**：設計收斂（brainstorming，2026-07-21），尚未實作。緣起：使用者全盤檢視 lumos 工作流時提「design loop 能否依任務規模決定 loop 程度」，經釐清方向=**小任務被過度審**、痛點=**缺中間輕量檔**。

## 問題

design-loop 的程度粒度目前只有兩檔，**中間是空的**：

```
trivial（typo/一行/純機械）  →  完全跳過 loop
                              ↑ 缺這一格
standard（其他全部）          →  完整 panel loop（風險面沒 high 就是這檔，「行為分毫不變」）
high（四類風險）              →  K=3 / cap≥8 / 關 fail-open
```

一個「不 trivial、但也不重」的小 spec（加個小 flag、改個非金流小邏輯）沒輕量檔可走，直接掉進 `standard` 的完整 panel——這就是「小任務被過度審」的結構根因。**不是旋鈕沒開好，是缺一檔。**

## 方向界定（範圍刀）

- **只解**「小任務被過度審」——降成本方向。
- **不碰**「大/難任務多跑」——那半撞 `cap=3 是效率前緣`（self-refine 文獻）＋ `RHB 縱深非解藥`（難題多揮棒不降單輪放水率），已由 [[Projects/design-loop提效_計劃]] 定調，本計劃不重開，也不與 d5「精確度軍備競賽先過教義裁」相衝（本案是降成本）。

## 設計

### 1. 三檔取代兩檔
`light < standard < high`。ratchet「只升不降」（risk-tiered-review 現有）自然延伸三級。忘了宣告 → 預設 standard（fail-safe，永遠不會更少）。

### 2. 進場：兩個方向、不對稱約束力

判「是不是 light」其實是兩個可靠度天差地別的問句：

| 方向 | 問句 | 機械可靠？ | 約束力 |
|------|------|-----------|--------|
| **往上（踢出 light）** | 有無**危險訊號** | ✅ 可靠（存在性偵測） | **硬否決**（up-only，只加審永遠安全） |
| **往下（放進 light）** | 夠不夠**小/簡單** | ❌ 不可靠（無訊號≠簡單） | **只能 advisory** |

- **硬否決（reliable，零新分類器）**：命中任一 → light 不給選、強制 standard+：
  1. 風險類命中（複用 `risk-tiered-review` 的 RISK_CLASSES）
  2. 碰到硬合約（invariant 級，impact/co-change 偵測）
  3. 體積超天花板（行數精確，屬 size 軸非難度判斷——不可能又大又是「小」檔）
- **軟提示（advisory，唯一新東西）**：三訊號全沒響 + 體積遠低天花板 → design-loop 進場跳一句「這條像 light，要用嗎？」maker 拍板。**維持 advisory 不更強**。
  - **它的價值是發現性、不是準確度**：純靠人記得選 light 的真風險是 maker 嫌麻煩不選、什麼都留 standard、白做。提示讓 maker 在對的時機真的走輕量路。
  - **提錯有兩層兜**：① maker 確認（同 trivial-skip 是 maker 責任）② 執行期 ratchet 自癒（見下）。

### 3. light 跑什麼（壓縮 loop）
- **pre-flight cascade**（複用 M1）排乾清單型缺陷。
- **1 輪 · 1 個通才審計員 · canary 護 · K=1**（踩 `design-loop提效` 已埋的「r1 通才席」伏筆）。
- **收斂**：該輪 canary caught 且無存活 ≥major → 收斂放行。
- **自癒（誤判在這裡被接住）**：該輪一抓到存活 major → **自動 ratchet 升 standard**，跑完整 panel。

### 4. 教義合規（先講在前面）
- **d5 經濟學**：便宜 spec 便宜審 = 缺陷分層定價 = **降成本**，非軍備競賽，教義站這邊。
- **d4 定位**：design-loop 本就「抬品質非保正確、漏網進逃逸帳」；light 只誠實定價最便宜的 spec，正確性照歸下游。
- **誠實天花板**：不靠「相信分類準」，靠硬否決擋危險 + ratchet 自癒 + 軟提示只買發現性。

## 里程碑

- **M0（純 skill 層，可先行）✅ 落地 2026-07-21**：lumos-design-loop SKILL 三處——〈何時用/何時跳〉加 light 檔進場條（硬否決 honor-system 自核 + 預設 fail-safe 走完整 loop）、新增〈light 檔〉專節（pre-flight + 1 通才席 + legacy `--need 1` + 人裁實質收斂 + 向上 ratchet）、templates.md §1 加單席通才用法。純散文/prompt，不動 gate code。
  - **⚠ 開工發現（M0/M1 邊界銳化）**：light 想要的「單席 K=1 乾淨機械 gate」**現有兩 gate 都不支援**——panel gate 要 caught≥2（單通才席湊不到）、legacy G2「發現枯竭」被『你一定找得到』framing 壓不到底。故 M0 的 light 收斂**只能走人裁「實質收斂」出口**（既有機制）拿數據；**乾淨的單席 K=1 機械 gate 確定落在 M1**（gate code 要新增 light tier 的收斂謂詞：pre-flight-drained + 單席 caught + 無存活 major = 收斂，不靠人裁）。這條把 M1 的 scope 從「加 tier 標籤 + ratchet」擴到「還要定義單席收斂謂詞」。
- **M1（動 gate code，必過 design-loop）**：`loop status` 認第三檔 light + ratchet 延伸三級 + 硬否決機械 filter（複用 RISK_CLASSES + ★INVARIANT★ 偵測 + 體積閘）。**self-governance=high，進實作前本計劃過完整 design-loop（舊 loop 審新 loop），同 M2 前例。** ✅ **loop-status 面已由 [[Projects/loop機械脊椎M1包_計劃]] 交付（2026-07-21：`--light` K=1 機械謂詞＋ratchet 永久 FAIL 分因＋hash 強制 fail-closed＋`loop next` phase=escalate；t_m1_* 34 checks＋全套 1302 綠）**——本計劃 M1 剩餘＝進場硬否決機械化（pitfalls 剝自核段，pitfalls/assess 面）。
- **驗收信號**：一批 light 檔 spec 的 wall-clock/token vs standard 基線；下游逃逸率進逃逸帳對照（見天花板）。

## 待實作校準

- **體積天花板數值**：留 replay 校準（spec 改動行數 / 動檔數的門檻），不預設魔術數。**先驗暫用值（2026-07-21 外審吸收，見 [[全盤外審2026-07_調研]] finding 10）**：預估實作改動 ≲50 行且孤立（SDD 生態經驗共識「<50 行孤立改動可跳 spec」）——是生態經驗值非實證門檻，replay 數據到位即取代。
- **通才席 vs 窄鏡頭席的首輪 capture**：`design-loop提效` 第六改已在等這個數據（n=2 方向性證據）；light 的單通才席正好是它的天然實驗場——可合併觀察。

## M1 實作前置發現（light 首戰 2026-07-21 回饋，樣本=lumos-show spec）

- **關鍵字誤報**：`lumos show` spec 自核段引用風險類名稱（「不碰金流/對外送出…」），`pitfalls --check` 關鍵字偵測命中全四類——**M1 機械化硬否決必須先剝「light 資格自核」段再掃**（同 `risk-tiered-review` assess_spec 的黑名單剝除前例），否則每份寫了自核的 light spec 都被誤踢 standard（fail-safe 方向但摩擦拉滿，light 形同虛設）。
- **probe 窗對小 spec 失準**：haiku 難度探針的「±20 行局部片段」在 ~60 行 spec 上≈半份全文，body 內任何植入近乎全域可見——同窗重植×2 皆被抓；改**植入拓撲**（矛盾跨 frontmatter summary ↔ body，兩端相距 40+ 行）才 probe pass。M1 收斂謂詞設計時：light 小 spec 的 canary 難度紀律應改「跨鏡像段植入」為預設型，probe 窗協議註明對 <100 行 spec 的失準（偏離字面協議一次，理由已記 r1 note）。
- **ratchet 首戰即觸發（n=1 數據點）**：「~40 行唯讀指令」的 spec 單通才席挖出 4 條 major（全機械證實：派發組 fallback 陷阱/命名陷阱/簽章抄錯/gate 同步漏列）→ 升 standard。方向解讀：light 的省在「小而真乾淨」的 spec；「小但接既有 8000 行單檔」的 spec 陷阱密度不隨行數縮——**「孤立」判準比「行數」判準更載重**，M1 體積閘設計時併記。升級率統計起點 1/1。
- **light 首戰全程收束（2026-07-21，loop 完整跑到落地）**：ratchet 後 std panel 3 輪（有效/無效/有效）＋Codex 否決席 3 次介入，實質收斂人裁 → TDD 落地（11 checks＋全套 1268 綠）。M1 可再吃三筆數據：①**canary 植入位置決定性**——sonnet 對「受審物內」canary 4/4 caught、對「編排者 briefing 內」0/2（r2 全輪作廢）；delta 輪 canary 應植 diff hunk 本體，寫進 M1 派工紀律。②**護欄升級實效**——r2 連 2 missed 觸發升 opus，r3 opus 2/2 完美抓（附反先例＋工作包落差三重證據）——升級鏈條真的接得住。③**capture-recapture 殘餘對 singleton minor findings 無資訊量**——末輪 4 條 singleton 全文件精度級，殘餘估計 6.0 卡門到 cap，人裁成為事實出口——M1 的單席 light 收斂謂詞不應含 capture 殘餘條件。

## 天花板（誠實）

- light 用深度換速度是**設計本意**——小 spec 裡藏的細微 bug 可能溜過單通才席；靠 ratchet + 下游 code-loop/測試 + 逃逸帳兜。
- 軟提示 + 宣告都依賴 maker 誠實（可能橡皮圖章）——同 trivial-skip / anchors 的 GIGO 天花板。
- **調價回路**：light 檔 spec 的下游逃逸率該進 `逃逸帳`（d5 已定位「逃逸帳=調價器」）——若 light 檔逃逸率偏高 = 收緊訊號（縮體積天花板 / light 也要 2 席 / 移除某類進 light）。
- 硬否決只和現有 RISK_CLASSES 一樣可靠——不引入新的漏偵風險，但也**不比它更強**（它漏的它也漏）。
