---
type: project
status: doing
created: 2026-08-04
updated: 2026-08-04
related:
  - "[[Systems/design-loop]]"
  - "[[Systems/convergence-evidence-gate]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Projects/design-loop提效_計劃]]"
  - "[[Projects/loop三輪壓縮_計劃]]"
  - "[[Issues/loop-next吐不可宣告的tier]]"
tags:
  - type/project
  - status/doing
summary: |-
  FLAG:DECISION
  KEY:★問題(實測非假想)★——38 個 design loop 用真 gate 指令跑一遍,★過閘 1/38,panel 模式 0/23★。全部靠人裁/cap 出場,機械帳從未背書過任何一次收斂
  KEY:★根因不是門檻太嚴,是閘在量一件已經決定不追求的事★——d4 定位=「抬 spec 質量、非保 spec 正確」(2026-08-04 使用者再確認:下游有 TDD+E2E 接功能性),但閘要求「估計剩餘缺陷<1」=窮盡=保正確。政策說一輪放行,閘說要證明母體枯竭
  KEY:★決定性數據:邊際產出是平的★——findings 中位數 r1=10 / r2=10 / r3=9,≥major 佔比 94%/96%/83%。真缺陷母體會耗盡(撈一輪少一輪);★平的曲線=按量產出,不是在撈缺陷★。全期 184 筆 caught 記錄裡 clean 只有 1 筆
  KEY:★閘的四個錨按「有無獨立真相來源」分兩類★——有(canary caught=植入已知錯、G1 refcheck=機械查檔案行號、G3 hash=機械算 sha256)vs 無(存活≤minor=審計員自報評分、capture-recapture=審計員自報條數+封閉母體假設)。★後兩條建在剛被證明是產出率的數字上★
  KEY:★外部背書三條(2026-08-04 網搜)★——①capture-recapture 原始文獻自己說是 decision support 非 hard gate,且 sparse data / 少 inspector 下失準、artifact 輪間被修改即違反封閉母體假設 ②LLM spec-conformance 審查的 systematic overcorrection 實測 FNR 26-88%,★且「要求解釋+提修法」的複雜 prompt 讓誤判率不降反升(GPT-4o 35.9%→87.9%)★——這正是本 loop 的 refute framing+「你一定找得到」 ③處置閘世界解過=GitHub「Require conversation resolution before merging」(OpenSSF 列為最佳實務)
  KEY:★提案形狀=把「評分」換成「處置」★——不問「你找到的嚴不嚴重」,問「你找到的處理了沒」:輪有效(canary 全席抓到)∧ folded+accepted==findings(可機械核對)。嚴重度通膨在這條規則下失效,因為拿掉了可灌水的維度
  KEY:★共用碼風險(必先解)★——design-loop 與 code-loop ★共用同一段 `_loop_status_panel`★,改判準會同時打到 code-loop,而 code-loop 的定位是「保正確」不是「抬品質」,不得連動放寬
  PRIOR-ART:①最小解在既有機制層——canary record 加計數欄+gate 換一條合取,不造新機制、不動記錄 schema 以外的東西 ②世界解過=GitHub/GitLab 的 conversation-resolution 合併閘(OpenSSF 最佳實務),同型:不宣稱「找完了」只要求「找到的都有交代」;capture-recapture 停止規則的原始文獻也已自陳非 hard gate ③裁定=borrow-design(沿用既有 canary record 欄位模式與 PR review 處置語意,零依賴)
  DEP:scripts/lumos _loop_status_panel / _loop_status_panel_clusters / _panel_extra_checks / cmd_canary｜skills/lumos-design-loop/SKILL.md｜skills/lumos-code-loop/SKILL.md
decisions:
  - content: blocker 不得以 accepted 出場,只能 folded;major 以下 folded/accepted 皆可
    id: d1
    context: 處置帳把「評分」換成「處置」後,理論上任何 severity 都可以「附一句理由後放行」。但 blocker 的語意是「spec 前提被打掉」——折一折就放行不合理,那不是「抬品質」的合理殘餘,是把已知的根本性問題帶進實作
    why_chosen: 保留唯一一條與 severity 有關的底線,但只綁在最極端那一檔:blocker 的判定爭議遠小於 major/minor 的分界(通膨主要發生在 minor↔major 之間,實測 94% 記 ≥major 但 clean 只有 1 筆),所以拿 blocker 當底線受通膨污染最小
    decided: 2026-08-04
    valid: true
  - content: 共用碼分流採 A 案:gate 加模式旗標(如 --disposal),design-loop 用、code-loop 不用
    id: d2
    context: _loop_status_panel 是 design-loop 與 code-loop 共用的同一段碼。design-loop 定位=抬品質(下游有 TDD+E2E 接),code-loop 定位=保正確(審要進 main 的 diff,下游沒有另一層)。處置判準的放寬絕不可連動到 code-loop
    why_chosen: 與現行 --panel/--light/--settle 完全同型,是這段碼既有的分流慣例,不引入新概念;B 案(看 loop id 前綴 code- 分流)把命名慣例變成語意承載,改個 id 就繞過去,脆;C 案(兩段碼拆開)最乾淨但會複製 hash 鏈與 min-seats 邏輯,而那正是本專案已經吃過虧的「多份實作立刻漂移」
    decided: 2026-08-04
    valid: true
---
# design-loop 判準重定位（計劃）

> **狀態**：2026-08-04 立案，**尚未進實作**。守衛面改動，依 `lumos-design-loop` 進場硬否決 → 必須跑完整 panel loop 才能實作。

## 一、問題（實測，不是假想）

把 38 個 design loop **用真的 gate 指令**各跑一遍：

```
★過閘 1/38★（唯一過的是 pitfalls-code-loop，8 輪循序的老帳）
★panel 模式 0/23★
```

也就是說：**每一個 design loop 都是靠人裁或 cap 出場的，機械帳從來沒有背書過任何一次收斂。**

這正是本專案一直在防的 honor-system——只是它藏在一個看起來很嚴謹的閘後面。

### 失敗原因分兩堆，而第二堆很關鍵

| 失敗原因 | 殺掉的是哪種 loop |
|---|---|
| 存活 ≥major | severity 從頭到尾平的（`CI回流閉環` maj×9、`檔案測試依賴地圖` 還往上跳） |
| capture-recapture 殘餘 | ★**真的收斂了的那些**★ |

`rel-mainnet` 三輪 blocker→blocker→**minor**、`lumos-show讀取入口-std` major→clean→**minor**
——**severity 真的降下來了**，然後死在殘餘 2.50 / 6.00（門檻 1.0）。

其餘的殘餘值是 39、28、22.5、15、10.5。**不是差一點，是差一個數量級。**

## 二、★決定性數據：邊際產出是平的★

| 輪序 | n | findings 中位數 | ≥major 佔比 |
|---|---|---|---|
| r1 | 34 | **10** | 94% |
| r2 | 27 | **10** | 96% |
| r3 | 24 | 9 | 83% |

全期 184 筆 caught 記錄，**`clean` 只有 1 筆**。

真的缺陷母體會**耗盡**——撈一輪少一輪。**平的曲線代表這不是在撈缺陷，是在按量產出。**

三種可能的解釋，而**三種都指向同一個結論**：

- **(a) severity 通膨**：refute framing ＋「你一定找得到，沒找到就是沒讀仔細」。skill 自己預期「必交 **minor**」，實際 **94% major**。
- **(b) 折入自己生新缺陷**：skill 已記載「r3 型『補丁沒同步』findings 幾乎全是此型」。
- **(c) spec 真的每輪都有 10 個重大問題**：折了 10 條還剩 10 條，不成立。

→ **多跑輪數不會收斂，只會換一批新 findings。**

## 三、根因：閘在量一件已經決定不追求的事

design-loop 的定位（2026-07-18 d4 使用者裁定，**2026-08-04 使用者再確認**）：

> 抬 spec 質量，**非保 spec 正確**——一輪 panel 抓便宜的就放行；正確性歸下游
> code-loop ＋測試＋驗證。（2026-08-04 補述：**下游有 TDD 落地與 E2E 測試檢驗功能性**。）

但閘要求的是「**估計剩餘缺陷 < 1 個**」——那是**窮盡**，是「保正確」的判準。

★**政策說一輪放行，閘說要證明母體枯竭。兩者從一開始就不是同一件事。**★

## 四、把四個錨按「有無獨立真相來源」重新分類

| 錨 | 真相從哪來 | 提案 |
|---|---|---|
| **輪有效（canary caught）** | ★植入的已知錯——真 oracle★ | **留** |
| **G1 refcheck** | 機械查 repo 檔案／行號 | **留** |
| **G3 hash 鏈** | 機械算 sha256 | **留** |
| 存活 ≤ minor | **審計員自報的評分** | **換成處置帳** |
| capture-recapture 殘餘 | **審計員自報的條數** ＋ 封閉母體假設（不成立） | **降 advisory** |

**下面兩條全部建在剛被證明是「產出率」的數字上。**

> **註**：M2 cluster 帳早就把 capture-recapture 降為 advisory，理由寫著「非定態目標下封閉族群前提偏弱，不當硬閘」——**修法已經在了，但做成 opt-in，34 個 panel loop 裡 33 個靜默落回舊帳**。

## 五、★外部背書（2026-08-04 網搜，PRIOR-ART 第②問）★

**① capture-recapture 當停止規則，原始文獻自己就不背書當硬閘**
Wohlin 等的十年回顧與後續評估指出：CR 模型在 **sparse data 下崩潰**、**inspector 數太少時無任何模型夠準且低估幅度可能很大**；且 artifact 在輪間被修改就**違反封閉母體假設**。作者的定位是 **decision support，不是 hard gate**。
→ 我們是 3-5 席、每輪折入改 spec。★兩個前提都踩到。★

**② LLM 做 spec-conformance 審查有系統性過度糾正，而且「更用力地要求它解釋」會讓它更糟**
`Are LLMs Reliable Code Reviewers? Systematic Overcorrection in Requirement Conformance Judgement`（Springer ASE 2026）實測：把**符合規格的**實作誤判為不符的比率（FNR）在 **26%–88%**；錯誤型態前四名是 Logic Error 宣稱 48.2%、**Added Requirements 14.1%**（審查員自己發明規格沒寫的要求）、Boundary Errors 13.2%、Misread Spec 11.7%。
★最打中我們的一句★：**「要求明確解釋與建議修法的複雜 prompt，反直覺地拉高誤判率」**——GPT-4o 在 MBPP 上 FNR 從 35.9%（Direct）飆到 **87.9%**（Full）。
→ 本 loop 的 framing 正是 refute ＋「必須附具體失敗場景」＋「你一定找得到」。**我們的 94% ≥major 有了外部對照。**
→ 該文的緩解法是 **Fix-guided Verification Filter**：把模型提的修法當**可執行證據**去跑，FNR 54.8%→16.3%。**啟示：判定要落在可執行/可機械核對的東西上，不是文字理由。**

**③ 處置閘世界解過**
GitHub branch protection 的 **Require conversation resolution before merging**：每一條 review 意見都必須被標為 resolved 才能合併；**OpenSSF Best Practices 把它列為預設分支應有的設定**。GitLab 有同型功能。
★它們也不宣稱「找完了」，只要求「找到的都有交代」。★ 這正是本提案要的語意。

## 六、提案：把「評分」換成「處置」

> **不問「你找到的東西嚴不嚴重」，問「你找到的東西處理了沒」。**

一輪收斂的條件：

1. **輪有效**——canary 全席抓到（caught ≥2 ∧ missed=0，維持現行 near-perfect）
2. **處置全清**——`folded + accepted == findings`，且每一條 `accepted` 附一句理由
3. **G1 / G3 照舊**

**嚴重度通膨在這條規則下失效**：審計員把什麼都叫 major 也沒關係，反正每一條都得處置。
★你拿掉了它可以灌水的那個維度。★

### 為什麼這不是放水

它換掉的是「證明沒有更多缺陷」（**已經決定不追求**），保留的是：

- **看了**——canary 是真 oracle，全席醒著才算數
- **看到的都處理了**——可機械核對，而且是 GitHub/OpenSSF 的既有語意

### ★裁定（2026-08-04，見 decisions d1）★：blocker 留底線

**`blocker` 不得以 `accepted` 出場，只能 `folded`。** major 以下兩者皆可。

理由：`blocker` 的語意是 spec 前提被打掉，折一折就放行不是「抬品質的合理殘餘」，
是把已知的根本性問題帶進實作。

★**為什麼底線綁在 blocker 而不是 major**★：通膨主要發生在 minor↔major 的分界
（實測 94% 記 ≥major、`clean` 全期只有 1 筆），**blocker 這一檔的判定爭議最小**，
拿它當底線受通膨污染最少。這條規則刻意只保留「唯一一條還跟 severity 有關的判準」。

## 七、★共用碼風險（必須先解，否則本案不得實作）★

`_loop_status_panel` **是 design-loop 與 code-loop 共用的同一段碼**。

而 **code-loop 的定位是「保正確」，不是「抬品質」**——它審的是要進 main 的 diff，下游沒有另一層接。
★**本案的放寬不得連動到 code-loop。**★

### ★裁定（2026-08-04，見 decisions d2）★：採 A 案，gate 加模式旗標

- **★A（採用）★ gate 加一個模式旗標**（如 `--disposal`），design-loop 用、code-loop 不用。
  與現行 `--panel` / `--light` / `--settle` **完全同型**，是這段碼既有的分流慣例，不引入新概念。
- **B. 依 loop id 前綴分流**（`code-` 走舊判準）——**排除**：把命名慣例變成語意承載，
  改個 id 就繞過去。
- **C. 兩段碼拆開**——最乾淨，但會**複製 hash 鏈與 min-seats 邏輯**，而那正是本專案
  已經吃過虧的「多份實作立刻漂移」（2026-08-02 教訓：預檢與主迴圈兩份實作當場就漂）。

### 隨之而來的兩個守衛義務（設計時要一併解，不得漏）

1. **互斥性**：`--disposal` 與 `--panel` / `--light` / `--settle` 的組合語意要釘死，
   非法組合 rc2——比照 `--settle` 既有的互斥檢查。
2. ★**code-loop 不得繞進來**★：光靠「code-loop skill 不寫這個旗標」是紀律不是守衛。
   需要一條機械檢查——候選：**帶 `--disposal` 的 loop，其 record 必須帶 disposal 欄；
   而 code-loop 的記帳模板不產生該欄**，兩邊靠 schema 而非靠自律隔開。
   ⚠ 這條**本身就是本案最該被審計員挑的地方**，不要在 loop 裡輕易放過。

## 八、時間成本（先算給人看，不當決策依據）

- **現在**：3 輪 × 3-5 席 ≈ **9-15 次派工**，跑完拿不到綠燈、人裁出場。
- **改後**：1 輪 × 3-5 席 ＋ 一個便宜的 fold 核對 ≈ **降到約三分之一**，而且**第一次會真的亮綠燈**。

## 九、★誠實天花板（先寫死，不得事後淡化）★

1. **末輪折入的內容沒有下一輪覆蓋。** 這是真逃逸——但既有設計**早已把它列為合法逃逸**（「正確性歸下游 code-loop＋測試」），且使用者已確認下游有 TDD＋E2E。**不是新開的洞，是把已存在的洞講清楚。**
2. **處置帳一樣是自報的。** `folded`/`accepted` 由編排者填，lumos 只做算術核對——與 severity 同屬 honor-system。**買到的是「數字必須對得起來」與「每條 accepted 留下一句理由」的摩擦，不是防竄改。**
3. **canary caught 只證該席醒著，不證審得夠廣**（2026-07-30 已入帳的外部實證：最強單一配置只抓 71.6%、六模型並集才 83.3%）。本案**沒有改善廣度**，只是不再用假的指標假裝有。
4. **本案沒有處理 severity 通膨本身**，只是讓收斂判準不再依賴它。若日後要真的壓通膨，方向是外部文獻的 Fix-guided Verification Filter（把提出的修法當可執行證據），**那是另一個題目**。

## 十、實務隱患

- **`accepted` 會不會變成應付式填表？** 規則是「每條附理由」，但理由的品質無法機械檢查。**緩解候選**：抽樣交第二判者複核（同 canary 判定抽樣分權模式，純 telemetry 不進 gate）。
- **`findings` 的定義要釘死**：現在是「辯方裁決後存活折入的真 finding 條數」。改成處置帳後，**被辯方駁倒的算不算進分母**？→ 傾向**不算**（它沒存活），但這會讓「辯方駁掉一堆」成為刷低分母的路徑。**需在 spec 明定並設守衛。**
- **K=1 之後，fold 迷你核對變成唯一的後手**。現在它是「可選的便宜 agent」，改後應**升為必要步驟**，否則末輪 fold 殘餘無任何接手。
- **既有 38 個 loop 的舊帳怎麼辦**：新判準需要 `folded`/`accepted` 欄，舊帳沒有。→ 走**定錨模式**（同 M2 cluster 帳前例：首個有效輪定錨），舊帳不回溯、不強制遷移。
- **本案自己要不要用新判準審**：見下。

## 十一、合約候選清單（收斂時再逐條裁，候選 ≠ 已標）

- `folded + accepted == findings` 的算術恆等式（改了＝收斂判準壞掉）
- `blocker` 不得以 `accepted` 出場（若待決 ① 採此案）
- **code-loop 不得繼承 design-loop 的處置判準**（共用碼分流的正確性）
- 定錨語意：首個有效輪定模式，之後不得切換

## 十二、下一步

1. ~~待人裁~~ **✅ 2026-08-04 已裁**：blocker 留底線（d1）、共用碼採 A 案模式旗標（d2）。
2. **→ 現在這裡**：跑 design-loop 審本節點。
   - **進場資格**：命中硬否決（**守衛面**）→ **不給 light，必須完整 panel**。
   - **tier**：`standard`（3 席）或 `high`（5 席）。傾向 **high**——本案改的是收斂判準本身，
     判錯的爆炸半徑是「之後所有 loop 的放行標準」。
   - ★**用舊判準審**★：本輪仍走現行的 `--gate --panel`。**不得用本案提議的新判準審本案**
     ——那是拿待證命題當前提。新判準的第一次實測留給實作後的下一個 spec。
     （原立案時寫的「用新判準跑一輪看它自己過不過得了」**已撤回**，理由如上。）
3. 收斂後 → writing-plans → 實作 → Verification 以 `plan_refs` 回指本節點。

### 派 loop 前必須先確認的一件事

本 repo 目前**明示禁用 Agent tool**（本 session 限制）。design-loop 需要派乾淨審計員，
**派不了就跑不了**。要嘛解除該限制，要嘛把本案掛起等能派工的場次——
★**不得以「先實作、之後補審」繞過**★：守衛面改動的進場硬否決就是為了擋這個。
