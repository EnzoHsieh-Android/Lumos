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
  KEY:★問題(實測非假想)★——38 個 design loop 用真 gate 指令跑一遍,★過閘 1/38,panel 模式 0/23★——即★用現行判準重跑,37/38 過不了★(注意界線:帳本沒記出場方式,「當年是不是被閘放行的」查不到,不得寫成「機械帳從未背書過」)
  KEY:★根因不是門檻太嚴,是閘在量一件已經決定不追求的事★——d4 定位=「抬 spec 質量、非保 spec 正確」(2026-08-04 使用者再確認:下游有 TDD+E2E 接功能性),但閘要求「估計剩餘缺陷<1」=窮盡=保正確。政策說一輪放行,閘說要證明母體枯竭
  KEY:★原稿的「邊際產出是平的」是錯的(r1 三席獨立指出 survivor bias,編排者縱貫重算證實)★——中位數 10/10/9 是★橫斷面聚合★,每輪樣本組成不同(先收斂的先退場)。同一批 21 個 loop 逐輪追蹤:平均 ★19.7→15.1→12.6★、13/21 下降。★曲線在降,只是降得太慢★:r3 平均仍 12.6 條、83% ≥major,而 cap=3——被迫停下來時離枯竭還很遠。結論(cap 內到不了)不變,理由整段要重寫
  KEY:★閘的五個錨按「有無獨立真相來源」分兩類★——有(canary caught=植入已知錯、G1 refcheck、G3 hash=機械算 sha256)vs 無(存活≤minor=自報評分、capture-recapture=自報條數+封閉母體假設)。★但 r1 查證:G1 在 panel 路徑根本不執行(`if panel: return _loop_status_panel`,_panel_extra_checks 只做 min-seats+G3),所以真 oracle 只有兩個不是三個★
  KEY:★外部背書三條(2026-08-04 網搜)★——①capture-recapture 原始文獻自己說是 decision support 非 hard gate,且 sparse data / 少 inspector 下失準、artifact 輪間被修改即違反封閉母體假設 ②LLM spec-conformance 審查的 systematic overcorrection 實測 FNR 26-88%,★且「要求解釋+提修法」的複雜 prompt 讓誤判率不降反升(GPT-4o 35.9%→87.9%)★——這正是本 loop 的 refute framing+「你一定找得到」 ③處置閘世界解過=GitHub「Require conversation resolution before merging」(OpenSSF 列為最佳實務)
  KEY:★提案形狀=把「評分」換成「處置」★——不問「你找到的嚴不嚴重」,問「你找到的處理了沒」:輪有效(canary 全席抓到)∧ folded+accepted==findings(可機械核對)。嚴重度通膨在這條規則下失效,因為拿掉了可灌水的維度
  KEY:★r1(tier=high 5席 panel)輪無效:1 caught/4 missed★——而根因是★抑噪紀律與 canary 互斥★:派工寫「低嚴重度、給不出失敗場景就不要提」,而 canary 全是未定義旗標/欄位/產物/壞引用=正好那一類。唯一抓到的 slot1 是★違反指示★才報的。推論:`輪有效` 量到的是「違不違反抑噪紀律」不是「醒不醒著」——這條要回寫 skill
  KEY:★共用碼風險(必先解)★——design-loop 與 code-loop ★共用同一段 `_loop_status_panel`★,改判準會同時打到 code-loop,而 code-loop 的定位是「保正確」不是「抬品質」,不得連動放寬
  KEY:★`findings` 是被本案改語意的既有欄,不是照搬(pre-flight r1c 抓到原稿兩處打架)★——現行語意=「存活★折入★的條數」,沿用則 folded+accepted==findings ★恆假★;本案必須重定義為「存活的全部條數(含 accepted)」。連帶:舊帳走定錨不回溯、兩份 skill 的 --findings 說明要改(★code-loop 那份改不改本案未決,最大未解點★)、循序模式的 G2 枯竭錨也吃這個欄位而本案沒評估連動。★已知擋不住:辯方多駁幾條會同時縮小分子分母,恆等式照樣成立而處置帳看起來很乾淨★
  PRIOR-ART:★①原答「不造新機制」是錯的(r1 查證推翻)★——M2 cluster 帳已是幾乎等價的處置帳:`CLUSTER_STATES=(resolved,accepted-minor,disputed-major)`、accepted-minor ★已機械強制內嵌理由★、其閘實測只有兩條(輪無效/disputed-major)★沒有存活≤minor★,且有 golden fixture。原案是在同一函式群造第二套平行實作=d2 否決 C 案時引的「多份實作立刻漂移」。★修正後的①=擴充既有 cluster 帳(如允許 accepted-major:理由)+讓它不再是沒人選的 opt-in★ ②世界解過=GitHub/GitLab conversation-resolution 合併閘(OpenSSF 最佳實務);capture-recapture 原始文獻自陳非 hard gate ③裁定=borrow-design(零依賴)
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

也就是說：**37/38 個 design loop 是靠人裁或 cap 出場的。**

★**這句話要講到剛好，不要多講（pre-flight r1b 抓到原稿寫過頭）**★：

- 原稿寫「**每一個**都靠人裁出場、機械帳**從來沒有**背書過任何一次收斂」——**與自己的 1/38 打架**，
  而且**比數據強**。
- 而且那個「1」也不等於「它當年是被閘放行的」——**我量的是「拿今天的閘去跑歷史帳」，
  不是「它當年怎麼出場」**。帳本沒有記錄出場方式，這件事查不到。
- 站得住的說法只有這句：★**用現行判準重跑，38 個裡有 37 個過不了。**★

這仍然是本專案一直在防的 honor-system——只是它藏在一個看起來很嚴謹的閘後面。

### 失敗原因分兩堆，而第二堆很關鍵

| 失敗原因 | 殺掉的是哪種 loop |
|---|---|
| 存活 ≥major | severity 從頭到尾平的（`CI回流閉環` maj×9、`檔案測試依賴地圖` 還往上跳） |
| capture-recapture 殘餘 | ★**真的收斂了的那些**★ |

`rel-mainnet` 三輪 blocker→blocker→**minor**、`lumos-show讀取入口-std` major→clean→**minor**
——**severity 真的降下來了**，然後死在殘餘 2.50 / 6.00（門檻 1.0）。

其餘的殘餘值是 39、28、22.5、15、10.5。**不是差一點，是差一個數量級。**

## 二、★決定性數據：邊際產出是平的★

| 輪序 | n（有這一輪的 loop 數） | 該輪 findings 中位數 | ≥major 佔比 |
|---|---|---|---|
| r1 | 34 | **10** | 94% |
| r2 | 27 | **10** | 96% |
| r3 | 24 | 9 | 83% |

★**三個單位別混（pre-flight 指出原稿沒交代，補上）**★：

- **`n` 是「有跑到這一輪的 loop 數」，不是輪數**。38 個 loop 裡 34 個有 r1（4 個沒有任何
  caught 輪），27 個跑到 r2，24 個跑到 r3。**遞減是因為 loop 陸續結束，不是樣本流失。**
- **`findings` 的單位是「條」，`184` 的單位是「筆記錄」**。一輪 panel 有 W 席＝W 筆記錄，
  但 findings 是**該輪跨席去重後的條數**，記在該輪其中一筆上。兩者不可相乘比對。
- **`clean` 是 severity 的最低檔**（`clean` / `minor` / `major` / `blocker`），
  語意＝「排掉 canary 與溯源影子後，這一輪沒有存活的真 finding」。

全期 **184 筆** caught 記錄裡，severity 記 **`clean` 的只有 1 筆**。

真的缺陷母體會**耗盡**——撈一輪少一輪。**平的曲線代表這不是在撈缺陷，是在按量產出。**

三種可能的解釋，而**三種都指向同一個結論**：

- **(a) severity 通膨**：refute framing ＋「你一定找得到，沒找到就是沒讀仔細」。skill 自己預期「必交 **minor**」，實際 **94% major**。
- **(b) 折入自己生新缺陷**：skill 已記載「r3 型『補丁沒同步』findings 幾乎全是此型」。
- **(c) spec 真的每輪都有 10 個重大問題**：折了 10 條還剩 10 條，不成立。

→ **多跑輪數不會收斂，只會換一批新 findings。**

## 三、根因：閘在量一件已經決定不追求的事

design-loop 的定位（**[[Systems/design-loop]] 的決策 d4**，2026-07-18 使用者裁定；
2026-08-04 使用者再確認。★注意：那個 `d4` 是該節點的編號，不是本文件的——本文件只有 d1/d2★）：

> 抬 spec 質量，**非保 spec 正確**——一輪 panel 抓便宜的就放行；正確性歸下游
> code-loop ＋測試＋驗證。（2026-08-04 補述：**下游有 TDD 落地與 E2E 測試檢驗功能性**。）

但閘要求的是「**估計剩餘缺陷 < 1 個**」——那是**窮盡**，是「保正確」的判準。

★**政策說一輪放行，閘說要證明母體枯竭。兩者從一開始就不是同一件事。**★

## 四、把五個錨按「有無獨立真相來源」重新分類

| 錨 | 真相從哪來 | 提案 |
|---|---|---|
| **輪有效（canary caught）** | ★植入的已知錯——真 oracle★ | **留** |
| **G1 refcheck** | 機械查 repo 檔案／行號 | **留** |
| **G3 hash 鏈** | 機械算 sha256 | **留** |
| 存活 ≤ minor | **審計員自報的評分** | **換成處置帳** |
| capture-recapture 殘餘 | **審計員自報的條數** ＋ 封閉母體假設（不成立） | **降 advisory** |

**下面兩條全部建在剛被證明是「產出率」的數字上。**

> **註**：M2 cluster 帳（[[Projects/design-loop提效_計劃]] M2）早就把 capture-recapture 降為 advisory，理由寫著「非定態目標下封閉族群前提偏弱，不當硬閘」——**修法已經在了，但做成 opt-in，34 個 panel loop 裡 33 個靜默落回舊帳**。

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

### ★欄位定義（pre-flight 指出原稿只用不定義，補上）★

| 欄 | 新舊 | 單位 | 語意 | 誰填 |
|---|---|---|---|---|
| `findings` | 既有欄，★**本案改語意**★ | 條 | 辯方裁決後**存活**的真 finding 條數（canary 與溯源影子不計）——**含 `accepted`** | 編排者 |
| `folded` | **新** | 條 | 其中**折入計劃節點**的條數 | 編排者 |
| `accepted` | **新** | 條 | 其中**不折、附理由放行**的條數 | 編排者 |
| `accept_reasons` | **新** | list[str] | 每條 `accepted` 的一句理由 | 編排者 |

**寫側 CLI**：`canary record ... --folded N --accepted N --accept-reason "<一句>"`（`--accept-reason` 可重複）。

#### ★`findings` 是被本案改掉語意的既有欄——不是照搬（pre-flight r1c 抓到原稿兩處打架）★

現行 skill 對 `--findings <M>` 的定義是「辯方裁決後存活**折入**的真 finding 條數」——
**只算折入的**。而本案的恆等式是 `folded + accepted == findings`。

★**若沿用舊語意，這個恆等式恆假**★（`accepted` 那部分從來不在 `findings` 裡）。
所以本案**必須把 `findings` 重新定義為「存活的全部條數（folded ＋ accepted）」**。
原稿在欄位表寫「存活」、在實務隱患段寫「存活折入」，**兩處打架且沒有察覺**——
那正是核心恆等式的分母。

**這是語意變更，不是新增欄位。連帶三件事必須一起處理：**

1. **舊帳的 `findings` 意義不同** → 走**定錨模式**：`--disposal` loop 的首個有效輪定錨，
   舊帳不回溯、不混算（同 M2 cluster 帳前例）。
2. **`lumos-design-loop` / `lumos-code-loop` 兩份 skill 的 `--findings` 說明都要改**
   ——★而 code-loop 不走本案判準，它的 `findings` 語意要不要跟著動，本案未決★。
   **這是本案目前最大的未解點，優先請審計員打。**
3. **G2「發現枯竭」錨也吃 `findings`**（循序模式的收斂條件之一）。語意一改，
   循序模式的枯竭判定跟著變——**本案沒有評估這個連動**。

> ★**分母可被操弄**★：改成「存活全部」之後，「辯方多駁掉幾條」會同時縮小分子與分母，
> 恆等式照樣成立而處置帳看起來很乾淨。**辯方裁決是 honor-system**，這條路徑本案擋不住，
> 只能靠辯方留 file:line 反證的既有紀律。**如實記載，不假裝解決。**

**機械核對三條**（都在 `canary record` 寫側就擋，不留到 gate）：

1. `folded + accepted == findings` —— 對不上 rc2
2. `len(accept_reasons) == accepted` —— 條數不符 rc2（**空字串不算一條**）
3. `blocker` 輪 `accepted == 0`（決策 d1）—— 違反 rc2

**記錄 schema**：三欄平鋪在既有 record 上（`folded` / `accepted` / `accept_reasons`），
**不新增巢狀物件**——沿 `capture_counts` / `clusters` 的既有慣例，讀側防禦同型。

> **`rc2`** ＝ lumos 的既有結束碼慣例：`0` 通過／`1` 未收斂／**`2` 真錯誤（參數非法、IO、帳面損壞）**。

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
  已經吃過虧的「多份實作立刻漂移」（2026-08-02 教訓，見 [[Projects/檢索多詞回退_計劃]]：預檢與主迴圈兩份實作當場就漂）。

### 隨之而來的兩個守衛義務（設計時要一併解，不得漏）

1. **互斥性**：`--disposal` 與 `--panel` / `--light` / `--settle` 的組合語意要釘死，
   非法組合 rc2——比照 `--settle` 既有的互斥檢查。
2. ★**code-loop 不得繞進來**★：光靠「code-loop skill 不寫這個旗標」是紀律不是守衛。
   需要一條機械檢查——候選：**`--disposal` 要求該 loop 的判定輪每筆記錄都帶
   `folded`/`accepted`（見第六節欄位定義），而 code-loop 的 `loop next` 記帳模板
   不產生這兩個旗標**，兩邊靠 schema 而非靠自律隔開。
   ⚠ 這條**本身就是本案最該被審計員挑的地方**，不要在 loop 裡輕易放過——
   ★因為「模板不產生」擋不住手動加旗標，這個候選解可能根本不成立★。

## 八、時間成本（先算給人看，不當決策依據）

- **現在**：3 輪 × 3-5 席 ≈ **9-15 次派工**，跑完拿不到綠燈、人裁出場。
- **改後**：1 輪 × 3-5 席 ＋ 一個便宜的 fold 核對 ≈ **降到約三分之一**，而且**第一次會真的亮綠燈**。

## 九、★誠實天花板（先寫死，不得事後淡化）★

1. **末輪折入的內容沒有下一輪覆蓋。** 這是真逃逸——但既有設計**早已把它列為合法逃逸**（「正確性歸下游 code-loop＋測試」），且使用者已確認下游有 TDD＋E2E。**不是新開的洞，是把已存在的洞講清楚。**
2. **處置帳一樣是自報的。** `folded`/`accepted` 由編排者填，lumos 只做算術核對——與 severity 同屬 honor-system。**買到的是「數字必須對得起來」與「每條 accepted 留下一句理由」的摩擦，不是防竄改。**
3. **canary caught 只證該席醒著，不證審得夠廣**（2026-07-30 已入帳的外部實證，見 [[Systems/canary-audit]]：最強單一配置只抓 71.6%、
   六模型並集才 83.3%；arXiv 2606.19749）。本案**沒有改善廣度**，只是不再用假的指標假裝有。
4. **本案沒有處理 severity 通膨本身**，只是讓收斂判準不再依賴它。若日後要真的壓通膨，方向是外部文獻的 Fix-guided Verification Filter（把提出的修法當可執行證據），**那是另一個題目**。

## 十、實務隱患

- **`accepted` 會不會變成應付式填表？** 規則是「每條附理由」，但理由的品質無法機械檢查。**緩解候選**：抽樣交第二判者複核（同 canary 判定抽樣分權模式，純 telemetry 不進 gate）。
- ~~`findings` 的定義要釘死~~ → **已在第六節釘死**（pre-flight r1c）：`findings` ＝存活的
  **全部**條數（含 `accepted`），是**既有欄的語意變更**，連帶 skill 文字／舊帳定錨／G2 枯竭錨
  三件事。被辯方駁倒的**不算**（它沒存活）；★「辯方多駁幾條就同時縮小分子分母」這條操弄路徑
  本案擋不住★，如實記載於第六節。
- **K=1 之後，fold 迷你核對變成唯一的後手**。現在它是「可選的便宜 agent」，改後應**升為必要步驟**，否則末輪 fold 殘餘無任何接手。
- **既有 38 個 loop 的舊帳怎麼辦**：新判準需要 `folded`/`accepted` 欄，舊帳沒有。→ 走**定錨模式**（同 M2 cluster 帳前例，[[Projects/design-loop提效_計劃]] M2：首個有效輪定錨），舊帳不回溯、不強制遷移。
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
     （**本節點同日稍早的初稿**寫過「用新判準跑一輪看它自己過不過得了」，**已撤回**，理由如上。）
3. 收斂後 → writing-plans → 實作 → Verification 以 `plan_refs` 回指本節點。

### 派 loop 前必須先確認的一件事

本 repo 目前**明示禁用 Agent tool**（本 session 限制）。design-loop 需要派乾淨審計員，
**派不了就跑不了**。要嘛解除該限制，要嘛把本案掛起等能派工的場次——
★**不得以「先實作、之後補審」繞過**★：守衛面改動的進場硬否決就是為了擋這個。

---

## 審計修正紀錄

### r1 · pre-flight（機械清單掃描，不算 loop findings）

| # | 命中 | 修法 |
|---|---|---|
| 1 | `folded` / `accepted` / `disposal` **只用不定義**——而那是本案的核心 | 第六節新增〈欄位定義〉：四欄語意／單位／誰填、寫側 CLI、**三條機械核對**、schema 平鋪慣例 |
| 2 | 第二節表格的 `n`（34/27/24）與「38 個 loop」對不上，且 `findings` 中位數 × n ≠ 184 | 補「三個單位別混」段：`n`＝有跑到該輪的 loop 數（非輪數）；`findings` 單位是**條**、`184` 單位是**筆記錄**，不可相乘比對 |
| 3 | `clean` / `rc2` 未定義 | 各補一句就地解釋 |
| 4 | 第七節 code-loop 隔離的候選解只寫了「模板不產生該欄」 | 補明**該候選可能不成立**（模板不產生 ≠ 擋得住手動加旗標），並把它標成本案最該被挑的點 |

★**pre-flight 沒有動任何論證或裁定**★——四條全是「定義缺漏」與「單位沒交代」，
屬清單型缺陷。設計層的洞留給 panel。

### r1b · pre-flight 補跑（全文對照組，方法論修正後）

**改用全文餵給便宜模型重掃**（理由與實測見本節最後的〈方法論修正〉小節，
不在此重複）。

| # | 命中 | 修法 |
|---|---|---|
| 1 | ★**自相矛盾**★：一處寫「過閘 **1**/38」，另一處寫「**每一個**都靠人裁出場、機械帳**從來沒有**背書過」 | 改為「37/38」，並補明**界線**：帳本沒記出場方式，「當年是不是被閘放行的」**查不到**；站得住的只有「用現行判準重跑，37/38 過不了」。summary 鏡像行同步 |
| 2 | `M2 cluster 帳` 兩處被當論據與前例引用，但無 wikilink | 補 `[[Projects/design-loop提效_計劃]]` |

★第 1 條是**我把結論寫得比數據強**★——與本案要修的毛病同型（用一個看起來嚴謹的數字，
講一句它撐不住的話）。留在這裡不刪。

### r1c · pre-flight 第三輪（全文探針 ×5，方法論修正後）

**方法**：多次獨立派便宜模型讀**全文**問「有沒有內部不一致或未定義引用」，取交集與獨有。
同模型同問題的重複派工可互為對照，收斂到下表。

| # | 命中 | 幾次獨立抓到 | 修法 |
|---|---|---|---|
| 1 | ★**`findings` 兩處定義打架**★——欄位表寫「存活」、實務隱患寫「存活**折入**」 | 1 | 第六節新增〈`findings` 是被本案改語意的既有欄〉：**沿用舊語意則恆等式恆假**；連帶舊帳定錨／兩份 skill 文字／G2 枯竭錨三件事；並記載「辯方多駁幾條同時縮小分子分母」這條**本案擋不住**的操弄路徑 |
| 2 | `d4` 引用在本文無定義 | **3** | 改指 `[[Systems/design-loop]]` 的 d4，並註明「不是本文件的編號」 |
| 3 | 標題「把**四個**錨重新分類」但表格列**五個** | 1 | 改「五個錨」 |
| 4 | 71.6%/83.3% 外部實證無出處 | 2 | 補 `[[Systems/canary-audit]]` ＋ arXiv 號 |
| 5 | `M2 cluster 帳` 第二處漏 wikilink（第一處已補） | 1 | 補上 |
| 6 | 「2026-08-02 教訓」無出處 | 1 | 補 `[[Projects/檢索多詞回退_計劃]]` |
| 7 | 「原立案時」時序模糊（本文件就是同日立案） | 1 | 改「本節點同日稍早的初稿」 |

★**第 1 條是設計層的洞，不是引用衛生**★——它打在本案的核心恆等式的分母上，
而且原稿**兩處自相矛盾卻沒察覺**。便宜模型的全文掃描接住了它。

### ★方法論修正：難度探針的規格在計劃節點上是壞的（要回寫 skill）★

`lumos-design-loop` 規定難度探針只餵「植入點 ±20 行」。**在交叉引用密集的計劃節點上，
這個做法沒有鑑別力**——`d1`／`d2`／`第六節`／`capture_counts`／`clusters` 全部落在片段外，
探針一律當「未定義」，於是 **canary 與真的存在的引用被同等噴出**。

**實測對照**（同模型、同問題、同一天）：

| 餵法 | 結果 |
|---|---|
| 植入點 ±20 行（skill 現行規格） | 每次噴 3–8 條，**其中把真的存在的「第六節」也列為不存在** |
| **完整檔** | 乾淨真檔只噴 2 條，且主動說「第六節欄位定義與機械核對邏輯均自洽」 |

★後果：照字面套用現行規格，探針的輸出無法用來判斷難度——它對「真的懸空」與
「只是被切斷」一視同仁，據此做的任何取捨都是拿噪音當訊號。★
**待本案收斂後回寫 skill**（現在不改——那會動到正在被審的機制）。

---

## r1（tier=high，5 席 panel）：★輪無效，1 caught / 4 missed★

`⛔ PANEL GATE FAIL（輪無效／存活≥major／無 capture_counts）`

| 席 | 鏡頭 | canary 型 | 結果 | 自報 max |
|---|---|---|---|---|
| 1 | 無鏡頭通才 | 未定義旗標 | **caught** | major |
| 2 | 論證與數據 | 未定義欄位 | ❌ missed | blocker |
| 3 | 邊界與失敗路徑 | 未定義產物 | ❌ missed | blocker |
| 4 | 整合與連動 | 壞章節引用 | ❌ missed | blocker |
| 5 | 跨家族（Codex） | 未定義旗標 | ❌ missed | blocker |

依規則：**missed 席 findings 全數剔除、輪無效不採信**。以下記載**不是**折入。

## ★r1 最大的收穫不是 findings，是 canary 機制本身的一個結構性缺陷★

四席漏抓，起初看起來是「審計員不夠醒」。查自己的派工 prompt 之後，答案是相反的：

> 派工紀律（逐字）：「**低嚴重度的疑慮，給不出具體失敗場景就不要提。**」

而 r1 的四個 canary 型別是什麼？**未定義旗標／未定義欄位／未定義產物／壞章節引用**
——全部是**低嚴重度、講不出具體失敗場景的文件級瑕疵**。

★**抑噪紀律精準地過濾掉了 canary 所屬的那一整類。**★

- 唯一抓到的 slot1，是**違反指示**才報的（標 `[minor]`、沒給失敗場景）。
- 其餘四席**照做了**，於是「missed」。

### 推論（要寫進 skill）

`輪有效 = caught≥2 ∧ missed=0` 被當成「審計員醒著」的代理指標。
但在「canary 是文件級瑕疵」＋「prompt 要求抑制文件級 finding」的組合下，
★**它量到的是「審計員違不違反抑噪紀律」，不是「醒不醒著」**★。

**兩者是同一個機制的兩端，而現行 skill 把它們寫在同一份 prompt 裡、沒有察覺衝突。**

三個候選解（未裁定，留給 r2）：

- **A. canary 型別改成有失敗場景的**（例：邏輯矛盾、與既有合約相牴觸的規則）——
  但那會與「真 finding」難以區分，溯源排除會變糊。
- **B. 抑噪紀律加一條例外**：「**未定義的詞／壞引用／內部不一致，一律要報，不受失敗場景要求限制**」。
- **C. canary 檢查獨立於 findings 報告**：另問一題「這份文件裡有沒有未定義的詞或壞引用？」
  ——與抑噪 prompt 分離。

> **對照證據**：pre-flight 階段用**不含抑噪紀律**的便宜模型跑全文，
> 5 個 canary 抓到 2 個（40%）；正式席**含抑噪紀律**，5 個抓到 1 個（20%）。
> 樣本極小、不足以定論，但方向與上述推論一致。

## ★編排者機械查證後必須立即更正的事實錯誤（非折入，是「本文寫了假話」）★

輪無效 ⇒ findings 不折。但以下四條**由編排者自己下指令查證為真**，
留著等於讓本節點繼續散布錯誤宣稱：

| # | 本文原本寫的 | 查證指令與結果 | 影響 |
|---|---|---|---|
| 1 | PRIOR-ART「最小解在既有機制層——**不造新機制**」 | `grep CLUSTER_STATES` → `("resolved", "accepted-minor", "disputed-major")`；`accepted-minor` **已機械強制內嵌理由**；cluster 閘實測只有兩條（輪無效／disputed-major），**沒有存活≤minor** | ★**地基錯誤**★：提案的「處置帳」已上線、有閘、有 golden fixture。原案是在同一函式群造第二套平行實作——正是 d2 否決 C 案時引的「多份實作立刻漂移」 |
| 2 | 「**G1 / G3 照舊**」，且 G1 列為三個真 oracle 錨之一 | `cmd_loop_status`：`if panel: return _loop_status_panel(...)` 直接 return；`_panel_extra_checks` 只做 min-seats ＋ G3 | ★G1 在 panel 路徑**從來沒有執行過**★。三個保留錨其實只有兩個 |
| 3 | summary「閘的**四個**錨」 | body 第四節已於 r1c 改成「五個錨」，**summary 鏡像行沒跟** | ★本文親手示範了它要防的「補丁沒同步」★，而 r1c 紀錄還寫著「已改」 |
| 4 | 「邊際產出是**平的**」 | 縱貫重算（r1/r2/r3 皆有的同一批 21 個 loop）：平均 **19.7 → 15.1 → 12.6**，13/21 下降 | ★曲線不是平的，是在降★。結論（cap 內到不了枯竭）不變，**理由要整段重寫** |

**第 1 條使本案的形狀必須改變**：不是「新增三個欄位」，而是
**「擴充既有 cluster 帳（例如允許 `accepted-major:理由`）＋讓它不再是沒人選的 opt-in」**。

## r2 之前要處理的設計層問題（來自 missed 席，★不折、僅列冊★）

多席重複指出、且指得出具體位置的（**待 r2 由醒著的席重新提出才折**）：

- **survivor bias**：三席獨立指出（含 Codex）。已由編排者驗證為真（見上表 #4）。
- **`--disposal` 是 opt-in**，而本文自己剛用「33/35 靜默落回舊帳」證明 opt-in 沒人記得帶。
- **d1 粒度**：`blocker 不得 accepted` 是逐條規則，但 schema 只有輪級聚合整數。
- **寫側擋不住 blocker**：blocker 可能記在別席，寫入當下看不到整輪 max severity。
- **負數繞過**：`findings=0, folded=-1, accepted=1` 滿足恆等式且不觸犯 blocker 條。
- **`cmd_loop_next` 不在 DEP**：它才是 skill 實際呼叫的入口，不改它則新判準在正常流程上不生效。
- **light 模式的欄位互證**也讀 `findings`，是第四個沒被列出的消費者。
- **fold 迷你核對**被本文稱為「唯一後手」，卻沒進收斂條件、也沒進合約候選清單。

## r1 的流程失誤（自我記載）

★**Codex 席第一次派工空跑 61 分鐘**★：`codex exec` 的 prompt 要走 stdin，
編排者當成位置參數傳 → 它印 `Reading additional input from stdin...` 後**無限等待**，
不報錯、不逾時。若沒去查，帳上會記成「跨家族席無回應 → 退同門」，
而真相是**指令根本沒跑起來**。

★fail-closed 擋得住「調不到外家」，擋不住「以為調到了但其實卡住」。★
→ 候選守衛：派工後檢查輸出檔非空且含結束標記，否則視為未派成。
