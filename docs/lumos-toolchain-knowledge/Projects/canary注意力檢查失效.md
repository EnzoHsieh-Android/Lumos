---
type: project
status: doing
created: 2026-08-04
updated: 2026-08-04
related:
  - "[[Systems/canary-audit]]"
  - "[[Systems/design-loop]]"
  - "[[Projects/design-loop判準重定位]]"
  - "[[Projects/canary生成硬化_計劃]]"
  - "[[Systems/convergence-evidence-gate]]"
tags:
  - type/project
  - status/doing
summary: |-
  FLAG:TECHNICAL
  KEY:★問題:design-loop 的 canary 與它自己的派工模板互斥★——`templates.md:83` 官方抑噪紀律逐字寫「低嚴重度疑慮,給不出具體失敗場景就不要標」,而 design-loop 的四個 canary 型別(壞章節引用/未定義旗標/未定義欄位/未定義產物)★全部是低嚴重度、講不出失敗場景的文件級瑕疵★。審計員越聽話,越會漏抓
  KEY:★三方互打(不只兩方)★——步驟 2.7 pre-flight 的掃描清單「未定義旗標／欄位／檔名、章節交叉引用」★與 canary 四型完全同一組★:pre-flight 先把這一類從真檔掃乾淨、canary 再植一個同類、派工模板再叫審計員別報這一類。三個步驟裡有兩個在打第三個
  KEY:★帳面證據(n=334)★——design-loop missed 率 ★18.5%★(42/227) vs code-loop ★9.3%★(10/107),兩倍。兩份 skill 的抑噪紀律★逐字相同★,差別只在 canary 型別:code-loop 的四型(off-by-one/資源未釋放/None未接/冪等破壞)★全都講得出失敗場景★,不被該紀律過濾
  KEY:★誠實界線:這是相關不是因果★——兩者材料不同(散文 spec vs code diff)、只有 design-loop 有 pre-flight 掃同類、整體 prompt 也不同,三個混淆都沒排除。★配對實驗未做前不得當定論★
  KEY:★2026-08-04 現場實例★——design-loop判準重定位 r1(tier=high 5席)1 caught/4 missed;唯一抓到的那席是★違反抑噪指示★才報的(標 minor、沒給失敗場景)。同一天同一份文件,不含抑噪紀律的 pre-flight 探針 2/5,含紀律的正式席 1/5
  KEY:★推論:`輪有效=caught≥2∧missed=0` 在此配置下量的是「違不違反抑噪紀律」,不是「醒不醒著」★——而那是整個 gate 裡唯一被標成「真 oracle」的錨
  PRIOR-ART:①最小解在既有機制層——改 `lumos-design-loop/templates.md` 的抑噪紀律措辭 ＋/或 canary 型別清單,不動任何碼、不造新機制 ②世界解過=調查方法學的 attention check／instructed manipulation check:公認做法是「covert、與題材同型、嵌進真題裡」而非讓它突出;且 ★單一 check 不足以判定不專心★(Prolific 政策:>5 分鐘的研究須失敗 ≥2 次才可拒絕),★通過一個 check 不預測通過另一個★ ③裁定=borrow-design(借 attention-check 方法學,零依賴)
  DEP:skills/lumos-design-loop/templates.md §1｜skills/lumos-design-loop/SKILL.md 步驟 2/2.7/3｜scripts/lumos _round_valid_m2 / _loop_status_panel
---
# canary 注意力檢查失效（計劃）

> **狀態**：2026-08-04 立案。**尚未進實作**。由 [[Projects/design-loop判準重定位]] r1 逼出，
> 因為它比那份提案更根本——★它污染之後每一輪的判讀★。

## 一、一句話

**我們用來檢查「審計員有沒有認真讀」的那個埋伏，剛好屬於我們叫審計員「不要report」的那一類。**

## 二、三方互打（不是兩方）

`lumos-design-loop` 的三個步驟，兩個在打第三個：

| 步驟 | 做什麼 | 對 canary 的作用 |
|---|---|---|
| **2.7 pre-flight** | 掃「未定義旗標／欄位／檔名、章節交叉引用」並**修掉** | 把 canary 所屬的那一類**從真檔清空** |
| **2 植 canary** | 植 (a) 壞章節引用／(b) 未定義旗標／(c) 未定義欄位／(d) 未定義產物 | ★正是被清空的那一類★ |
| **3 派工模板** | `templates.md:83`「低嚴重度疑慮，**給不出具體失敗場景就不要標**」 | ★叫審計員不要報那一類★ |

★**canary 是文件級瑕疵；而文件級瑕疵，恰好是這份 skill 一路在清除與抑制的東西。**★

## 三、帳面證據（`docs/.canary-log.jsonl`，n=334）

| loop 類型 | caught | missed | ★missed 率★ | canary 型別 |
|---|---|---|---|---|
| **design-loop** | 185 | 42 | ★**18.5%**★ | 壞引用／未定義旗標／欄位／產物——**全都沒有失敗場景** |
| **code-loop** | 97 | 10 | **9.3%** | off-by-one／資源未釋放／None 未接／冪等破壞——**全都有失敗場景** |

★**兩份 skill 的抑噪紀律是逐字相同的一句話。**★ 差別只在 canary 型別是否落進那句話的射程。

### 2026-08-04 現場實例

[[Projects/design-loop判準重定位]] r1，`tier=high` 5 席 panel：**1 caught / 4 missed**。

- 唯一抓到的那席，是**違反抑噪指示**才報的——標 `[minor]`、沒給失敗場景。
- 其餘四席（含跨家族 Codex）**照做了**，於是全部 missed。
- 同一天、同一份文件：**不含**抑噪紀律的 pre-flight 探針 **2/5**；**含**紀律的正式席 **1/5**。

## 四、★誠實界線：這是相關，不是因果（先寫死，不得事後淡化）★

上表的兩倍差距**至少有三個混淆沒排除**：

1. **材料不同**——design-loop 審散文 spec，code-loop 審 code diff。
2. **只有 design-loop 有 pre-flight** 事先把同類缺陷掃乾淨（可能讓 canary 更孤立、也可能更難被聯想到）。
3. **整體 prompt 不同**——鏡頭、severity 錨、輪次語境加碼都不一樣。

★**在配對實驗跑完之前，本節點的假說不得被當成定論引用。**★
同日的 2/5 vs 1/5 是**同文件同 canary**的配對觀察，方向一致，但 n=5，**不構成證據**。

## 五、★推論：`輪有效` 這個錨可能量錯了東西★

現行 panel gate 的第一條合取是：

```
輪有效 = caught ≥ 2 ∧ missed = 0    （near-perfect）
```

它被當成「審計員醒著」的代理指標，而且是 [[Projects/design-loop判準重定位]] 第四節裡
**唯一被標成「有獨立真相來源／真 oracle」** 的那一個。

如果本節點的假說成立，它實際量的是 ★**審計員違不違反抑噪紀律**★。

**後果**：一個嚴格遵守派工紀律的高品質審計員，會被判為「不專心」；
而一個到處亂報低嚴重度疑慮的審計員，反而容易 caught。★方向是反的。★

## 六、PRIOR-ART（第②問：世界解過沒）

這題在**調查方法學**裡是成熟領域——「attention check」／「instructed manipulation check」（IMC）。

**① 檢查項應該與真題同型、covert、嵌進去，而不是突出**
公認建議是「embed attention checks with similar measures so that they are less obvious，
by asking questions that match the topic of the survey」，並偏好 covert check，
以降低受試者識破後的反效果。
→ 對照本案：canary **型別**與真材料同型沒問題，問題出在**它落進了被指示抑制的類別**。

**② ★通過一個 check，不預測通過另一個 check★**
文獻明確指出「people who pass one attention check question do not necessarily pass
other attention checks in the same study」。
→ 對照本案：★`caught` 只證「這一次抓到這一個」，推不出「這席這一輪醒著」★——
而 gate 現在正是這樣推的。

**③ ★單一失敗不足以判定不專心（可直接借的硬規則）★**
Prolific（大規模跑這件事的商業平台）的政策：**超過 5 分鐘的研究，受試者必須失敗
至少兩次 check 才可被拒絕**；只有更短的研究才允許單次失敗即拒。
→ 對照本案：我們一席審計動輒 8 分鐘以上，**卻是單次 missed 即整席作廢、整輪無效**。
★比業界通行做法嚴格，而且嚴在一個已知不可靠的訊號上。★

**④ 檢查數量應隨材料長度增加**（20 題以下 1–2 個、20–50 題 2–3 個、50 題以上 3–5 個）。
→ 對照本案：一席一個 canary，材料是 365 行的計劃節點。

**裁定＝borrow-design**：借 attention-check 方法學的三條（同型嵌入／單次不判定／數量隨長度），
不引任何依賴、不動 lumos 的碼結構。

## 七、候選修法（★未裁定，列給審計用★）

**A. 改抑噪紀律的措辭（最小改動）**
加一條例外：「**未定義的詞、壞引用、內部不一致——一律要報，不受『具體失敗場景』要求限制**」。
- 成本：改 `templates.md` 一句話。
- 風險：可能重新打開它原本要關的噪音閘（PR-Agent 借來的那條紀律是有理由的）。

**B. canary 檢查與 findings 報告分離**
派工結尾另問一題：「**這份文件裡有沒有未定義的詞或壞引用？（與上面的 findings 分開回答）**」
- 成本：改派工模板。
- 優點：抑噪紀律照舊管 findings，不影響注意力量測。
- ★風險：這使 canary 從 covert 變 overt——違反 PRIOR-ART ①，審計員知道有 trap 會改變行為★。

**C. 一席多 canary（借 Prolific 的「失敗兩次才判」）**
每席植 2 個不同型的 canary，**兩個都漏才算 missed**。
- 成本：植入工作加倍、溯源排除面積加倍。
- 優點：直接對應文獻的可靠性建議（單一 check 不足）。

**D. 改 canary 型別，讓它有失敗場景**
例：植入「與既有 ★INVARIANT★ 相牴觸的規則」而非「未定義的詞」。
- 優點：不再落進抑噪射程。
- ★風險：與真 finding 難以區分，溯源排除會變糊——而溯源排除本來就是靠自律的軟環節★。

**A 與 C 可並行；B 與 PRIOR-ART ① 衝突；D 動到 canary 生成的核心。**

## 八、★決定性實驗（做這個之前不要挑修法）★

**配對設計**：同一份 spec、同一個 canary、同一個模型，兩臂只差一句話。

- **對照臂**：現行派工模板（含抑噪紀律）
- **實驗臂**：同一份模板，**只刪掉抑噪那一句**

各跑 N 席，比 caught 率。**同文件同 canary 消掉「材料不同」這個混淆**；
同模型消掉能力差異；只差一句話消掉 prompt 整體差異。

- **樣本**：至少 10 對（今日的 2/5 vs 1/5 只有 5 對且非嚴格配對，不夠）。
- **成本**：20 席便宜模型。
- ★**前置**：實驗臂會產生更多低價值 findings，**這是預期中的代價，不得拿來當「實驗臂比較差」的證據**★——本實驗只量 caught，不量 findings 品質。

## 九、實務隱患

- **改了抑噪紀律，findings 噪音會回來**。那條紀律 borrow 自 PR-Agent，是有實證理由的
  （見 [[Projects/design-loop判準重定位]] 第五節②：LLM 審查的誤報是真實部署最大抱怨）。
  ★兩害相權的取捨要明寫，不能只顧一頭。★
- **canary 判定本來就是植入者自判**——本節點只處理「審計員為什麼沒報」，
  **不處理「編排者判 caught/missed 判得準不準」**（那是既有的 `canary second` 抽樣分權，另一條線）。
- **改動會同時影響 code-loop**：兩份 skill 共用同一句抑噪紀律。
  ★若只改 design-loop 那份，兩份會漂移★——而 code-loop 的 9.3% 顯示它那邊沒壞，
  **不該連動改**。要明確寫「只改 design-loop 這份，並註明為什麼兩邊不同」。
- **既有 227 筆 design-loop 記錄的 missed 意義可能要重新解讀**。若假說成立，
  過去被判「該席不採信」而丟掉的 findings 裡，可能有真東西。
  ★但不得回溯採信★——那些 findings 沒留全文，無法重判。**只在此記載，不追溯。**

## 十、★誠實天花板★

1. **本節點只是假說。** 帳面兩倍差距有三個混淆沒排除，配對實驗未跑。
2. **就算假說成立，修好之後 canary 仍然只證「這一次抓到這一個」**——
   文獻明講通過一個 check 不預測通過另一個。★注意力檢查的天花板不因本案而抬高。★
3. **與 [[Systems/canary-audit]] 既有的誠實天花板疊加**：canary caught 只證該席醒著、
   不證審得夠廣（2026-07-30 外部實證：最強單一配置 71.6%、六模型並集才 83.3%）。
   **本案不改善廣度。**

## 十一、與 [[Projects/design-loop判準重定位]] 的關係

那份提案把「輪有效（canary caught）」列為**唯一保留的真 oracle**。
★本節點直接打在那個前提上。★

**順序**：本案的配對實驗**應先於**那份提案的 r2——否則 r2 會在一個可能失效的
注意力指標上重跑一遍，得到的還是不能解讀的結果。
