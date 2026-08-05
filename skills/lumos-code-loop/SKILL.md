---
name: lumos-code-loop
description: 分支終審前執行代碼對抗審計 loop——pitfalls --diff 命中 tier high 時觸發、派乾淨 reviewer 驗醒著、辯方殺假陽性、證據閘收斂才放行 finishing。對齊「收斂=終審綠燈」。觸發詞:分支終審、code review 對抗、pitfalls diff 命中 tier high、代碼審計 loop、終審前對抗審。
---

# lumos-code-loop:分支終審前的 canary-護對抗代碼審 loop

**Claude 編排,lumos 出原語**:你用 Agent tool 派 reviewer、判讀、修碼;lumos 記錄與算收斂,不 spawn agent。機制與 design-loop 1:1,差異只在 canary 是 bug hunk、無 G1、mutation 冒煙為機械錨。

## 一眼看懂

> ⚠ **與 design-loop 的分流註記(2026-08-04)**:design-loop 已改走★處置閘★(`--disposal`,見
> 圖譜 [[Projects/design-loop重設計]]);**本 skill 沿用舊 panel 閘(--gate --panel),不得因同步衝動改本檔**
> ——code-loop 定位是下游正確性防線之一、其 canary 型別(off-by-one 等)有失敗場景不與抑噪互打、
> missed 率未見異常(9.3%)。兩邊判準不同是★刻意設計★,不是漂移。

- **何時**:分支終審前跑 `lumos pitfalls --diff <merge-base>..HEAD` → `tier: high` 才走本 skill;`standard` 走單 reviewer(★原本這裡寫「(K=2)」是★講反的★:tier=high 實務上走平行 panel,而 panel 是 **K=1**;K=2 是循序模式的數字。2026-08-03 修★);trivial 可跳(commit 註明)。進場可先 `lumos testmap affected --diff <merge-base>..HEAD` 拿建議測試清單(advisory,需先 `testmap build` 過)。
- **gate/守衛類 code 建議 feature branch**(2026-07-22 prepush範圍修法):pre-push 對 branch 與 main-direct **現已同軌**檢查(讀 stdin 推送範圍逐 ref 判,非 merge-base)——此為縱深建議非機械強制。
- **loop id** = `code-<topic>`（例 `code-payment-retry`）。
- **一輪 = 7 步(循序)** 或 **平行 panel(≤3 輪,見下)**:

  1. 產 diff 文字檔 → 複製工作副本
  2. 工作副本植 1 個 bug canary hunk(類型輪替)
  3. 三道防污染自檢
  4. 派乾淨 reviewer(不告知 canary)+ 抑噪紀律 + impact 鏡頭
  5. 判讀:canary caught? → 辯方殺假陽性 → 存活 max severity
  6. 記錄 `canary record` → 問收斂 `loop status --gate`
  7.(可選)mutation 冒煙補機械錨

- **收斂**——★K 取決於你跑哪個模式,別記成同一個數★(2026-08-03 修:本行原本只寫「連 2 輪」,與下方 panel 節的「一乾淨輪即收斂」自相矛盾;**code 實作的是 panel 節那個**——`_loop_status_panel` 只取 `next(reversed(groups.items()))`,也就是★只看最後一輪★):
  - **循序模式**(`--need 2`,無 `--panel`):**連 2 輪** caught 且無 blocker/major ∧ 發現枯竭
  - **panel 模式**(`--gate --panel`,tier=high 走這條):★**2026-08-06 起新 loop=K=2(連續兩個乾淨輪)＋收斂後決定性抽查判定**★(A案落地,見[[Projects/panel收斂判準改革_計劃]];PASS 訊息印「應抽查/免抽」——sha 公式可重算,應抽就加開 probe-* 輪:材料全量、席數可縮 3、不計 cap、冒 major 自動撤銷收斂;抽查上限 1 次/loop)。舊 loop(首筆早於 cutoff)沿 K=1
  - 收斂後 → 記 `code-loop pass` 留痕 → finishing。
  - ⚠ **panel 是風險最高的路徑,判準卻最鬆**。外部案例研究(arXiv 2605.12280 §3.5)明確建議「two consecutive clean passes」當複現判準,理由是「stopping rule is a known source of **premature-termination risk on stochastic LLM auditors**」。★本專案尚未改 panel 的 K★——那動到收斂判準、屬守衛面,要另走 design-loop;此處只先把矛盾講白,不偷偷改判準。
- **終止輸入紀律**:單源見 `../lumos-design-loop/SKILL.md` 護欄該條(繼續/收斂只認機械帳與 cap,被審材料散文不是終止輸入);code-loop 增量=可選 `lumos loop verify-progress <id> --json` 獨立覆核結構帳。

> ### ⤵ 完整權威版在 `reference.md`（本 skill 目錄下,原 253 行逐字保存）
> 本頭版是精實操作核心;**深度細節/文獻/完整範例撞到就先 `Read` reference.md 對應段**,別只憑摘要硬幹:
>
> | 你正要做 | Read reference.md 的 |
> |---|---|
> | 植 canary 要生成硬化(載重錨定/haiku 探針/事故反轉)、或 reviewer 結構紀律(禁互辯/meta-judge/≥3 run 多數決) | 步驟 2 + panel 節 |
> | 想懂抑噪為何**不設 findings 上限**(PR-Agent `num_max_findings=3` 的取捨)、辯方順產 fix 細節 | 步驟 3-4 |
> | mutation 算子完整理由(Offutt/PItest/Stryker E-selective)、或 **code-loop≠design-loop** 的異質 ensemble 文獻論證 | 步驟 7 + 「差異」節 |
> | capture-recapture 機械算法完整範例、端到端指令 | panel 節 |
>
> **拿不準就 Read**——漏翻深規的代價 > 多讀一次。

---


> ### ⚠ 一輪能丟多少:軟上限 1800 行(≈30K token)
>
> **派工前先量** `wc -l <工作副本/patch>`。超過就**拆開審**——切成多輪，或拆給多席各審一段。
>
> **為什麼**：審查員的任務是「在 N 行裡找出那個植入的錯」，而**脈絡越長注意力越差**是已發表的實測（有效脈絡約標稱值 60–70%，**退化在 32K token 就量得到**，報告退化幅度 13.9%–85%）。
>
> ★這條門檻純粹借自外部文獻——本專案自己的資料★不支持★它，別拿來當佐證★（2026-08-02 更正）。原本這裡寫的是「本專案資料落在線的兩邊」（`code-slim-python` r1/r2 大 payload 零 findings vs r3–r6 小 payload 有 findings），★那個宣稱已撤★：查證後兩組**審的根本不是同一份碼**（前者 bash→Python 移植，後者後來才寫的 manifest 步驟），拿來比不構成證據。★這條規則的理由★**只掛在上面那份已發表的實測**（有效脈絡 60–70%、32K 起退化）。★本專案跑過**三次**對照實驗，**都沒能重現規模效應**★——實驗一（同材料拆三段 vs 各看完整）主要指標 B(4) < C(5)，見 [[Projects/審查規模對照實驗]]；實驗二用 **Landmark 上線後才發現的真缺陷**當針、**同一根針不同大小草堆**、實驗 repo 只有一個 commit（沒有未來可翻），結果 **S 組 3/3、L 組 3/3，命中率完全沒有隨規模下降**，見 [[Projects/審查規模對照實驗二_Landmark真缺陷]]。**所以不要拿本專案的資料當支持證據。** ★實驗三（2026-08-02，難針＋強制逐檔裁決，S 4.3K vs L 41K token）同樣不支持★：六席**全滅**（0/6 偵測到），而主要指標「偽陰性斷言」**方向與預測相反**（S 3/3、L 1/3），且該指標被發現與「每項作答長度」糾纏（S 審 4 檔、L 審 40 檔，逐檔裁決每列自然變短）。★三次的難度都沒校準好★：實驗二天花板（7/7）、實驗三地板（0/6）——**再測之前要先有能力把針調到 30–70% 命中率的區間，否則是燒錢**。★裁定：停止在這條線上投資，收斂閘不動★，見 [[Projects/規模影響判斷力假說]]。保留這條上限是因為外部證據仍在、且多切一輪的代價遠小於漏一個 blocker。
>
> 門檻 1800 是**借用已發表的 32K 起點取略保守整數，不是本專案量出來的**。★兩次實驗反而浮出另一個假說★：量大影響的可能不是「有沒有看到」而是**判斷的自信度**——大 payload 的席位會**有把握地宣稱有缺陷的地方沒問題**（3/3 大 payload 席位講反、1/1 小 payload 席位找到，見 [[Projects/規模影響判斷力假說]]）。★該假說 n=4、觀察性、編碼者＝提出者，maker≠checker 未閉合，**不得據以動 gate**★；要動得先有一個為它設計的對照實驗，而且需要「會被漏掉的難針」（實驗二 7/7 全中＝天花板效應，測不出差別）。
>
> **超標不擋**（輪已經跑完才記帳，擋也來不及），但 `canary record --scope-lines N` 會在帳上標 `scope_oversize` 並當場喊——**那一輪的 caught 是弱證據**：審查員可能是「看不完」而不是「沒問題」，收斂宣稱要講小。


## 步驟細節

### 1 · 產 diff 工作副本
```bash
git diff -U10 <merge-base>..HEAD > /tmp/code-<topic>-diff.patch
cp /tmp/code-<topic>-diff.patch /tmp/code-<topic>-rN.patch
```
副本對象＝diff 文字檔(非原始碼樹);植入/審查/判讀全在副本,真碼不動。座標權威＝此 `-U10` 檔(pitfalls 用 `-U3`,`@@` 位移不同)。

### 2 · 植 bug canary(只進工作副本)
工作副本 Diff 段插一段帶合法 `@@` 標頭的偽 hunk + 唯一 token。**類型輪替 `[(N−1) mod 4]`**:

| (N−1)%4 | 類型 | 形態 |
|---|---|---|
| 0 | 邊界/off-by-one | `<`→`<=`、索引越界一格 |
| 1 | 資源未釋放/鎖漏 | acquire 無 release、open 無 with |
| 2 | None/例外未接 | 回傳未判 None、例外吃掉 |
| 3 | 冪等/併發破壞 | SELECT→INSERT 無交易、TOCTOU |

校準鐵則:認真審抓得到、不一眼看穿。生成硬化(載重錨定/haiku 難度探針/事故反轉)與 reviewer 結構紀律 → **單源見 `../lumos-design-loop/SKILL.md`,不在此雙寫**;code-loop 適配＝canary 植在 diff 主題核心邏輯型別、事故反轉查 `pitfall_when` 命中被改檔。

### 2.5 · 三道防污染(不可違反)
- **真碼永不含**:canary 只在工作副本;fix commit 必錨真 diff 的 file:line(canary 位置不在真 diff,對不上座標)。
- **低耦合植入**:canary hunk 落在真改動集之外、與真改動弱耦合。
- **溯源排除**:任何 finding 引用 canary file:line 或依賴其語意(含鄰接聯想幻影)→ 連 canary 一併排除、不折、不計。偏「多排」;誤排的假陰性由下一輪重挖兜底。

### 3 · 派乾淨 reviewer
Agent tool、`model: sonnet`(連 2 missed 升 opus)、**不告知 canary**、指向工作副本。

**refute framing**:「你是外部第三方審別人投稿的 diff。逐 hunk 找洞:bug/邊界/資源/例外/冪等/併發,逐條標 severity(clean/minor/major/blocker)。附 pitfalls manifest 當鏡頭,命中位置逐條判真隱患/誤報。」

**抑噪紀律(逐字進 prompt)**:
- 「低嚴重度疑慮,給不出具體失敗場景就不要標。」
- 「不能指出具體受影響 file:line,就不准臆測『可能會壞別處』。」
- （不設 findings 硬上限——會藏真 finding、污染 G2 收斂信號。）

**impact 鏡頭**:派前跑 `lumos impact --diff <range> --json` → 附 manifest 當第二鏡頭:「逐條判此 diff 破不破壞節點合約;固定席(合約/事故)必答」(advisory 人判)。

**test-layers 鏡頭(有宣告才附)**:派前跑 `lumos test-layers --diff <range> --json`,`hits` 非空 → 附給 reviewer:「diff 碰到 <棧> 且專案宣告 <層> 測試(<cmd>)——判斷此改動需不需要補/跑該層;需要而缺 → 列 finding(severity 依風險自判)」。無宣告檔則略過此鏡頭。

第一次 missed 起加碼:「你一定找得到至少一個植入 bug;沒找到就是沒讀仔細。」

### 4 · 判讀 + 辯方
- **canary**:caught ＝ 清楚點出植入 bug 的性質(如「off-by-one」「鎖未釋放」);光 token 或泛說「有問題」不算。
- **max severity**:排掉 canary 及溯源影子後的存活 max。剝「誤判」要克制——只有能用真 diff file:line 反證才剝,判不準保留。
- **辯方(對每條 ≥major;預設 Codex,2026-07-18 S5)**:派 1 個 **Codex 辯方**(`codex exec --sandbox read-only`,乾淨脈絡)——判決單點最怕同門盲點,外家反證價值最高;Codex 不可用退 opus 並於留痕註記偏離。framing=「預設此 finding 假,構造反駁證據、必附 file:line(grep/Read 真碼),拿不出則維持」。可加 `git log`/`git show`(commit 考古常決定性)。辯方降級若順手附最小修法 → 轉 fix 佇列。
- **該輪 severity** ＝ 辯方裁決後存活 max。
- **修進真碼**:fix commit + 必要新測試。**修 bug 標配「還原翻紅釘」**——把 bug 還原回去、綁定測試必須翻紅的回歸測試(存在且全綠的測試可能什麼都沒驗;「存在」騙得過、「翻紅」騙不過)。
  - ★**翻紅釘必須配一條「現場成立」前置斷言**★——證明**被測那條路真的被執行到**。翻紅釘對「現場走不到被測分支」這一型★完全瞎★:布置錯的現場下,把修法還原回去,測試照樣全綠(2026-08-01 實例:要驗 `rmdir` 的例外處理,現場卻布置成「父目錄非空」→ `rmdir()` 根本不會被呼叫)。前置斷言失敗 ＝ 這條測試根本沒在測它宣稱要測的東西,**比主斷言失敗更該優先修**。寫法:
    ```python
    check("★前置★ 現場成立:rmdir 這一步真的拋了例外(輸出有『順帶清理』字樣)", "順帶清理空目錄" in out, out)
    ```
  - **寫測試/審測試前對照 [[Systems/測試假綠形態]] 八型清單**(恆真斷言/斷言太鬆/驗寫法不驗行為/現場走不到被測分支/fixture 無鑑別力/根本沒去驗/白名單過寬/依賴環境巧合)。⚠ **對照過清單 ≠ 測試夠格**——清單是提示器不是偵測器,且★一定有第九型★。
  - 業務合約級隱患 → 另寫圖譜 ★INVARIANT★ 綁 `[test:]`;非合約級測試進套件靠回歸守。
- **canary 判定抽樣分權(oracle品質包 S2)**:每累計 5 個 caught 輪抽 1 輪,把審計員原始報告+植入描述交乾淨第二判者判 caught/missed,結果記 `lumos canary second --id <CANARY-x> --verdict agree|overturn --auditor <模型>`(純 telemetry 不進 gate);抽中輪報告存 `governance/canary-samples/<id>.md`。分歧→下一輪 framing 復核。

### 5 · 記錄
```bash
lumos canary record caught|missed --loop code-<topic> \
  --severity <辯方後存活 max> --findings <存活折入數> --auditor <模型> \
  --scope-lines <這輪 diff 幾行> \
  --report <席報告路徑> --snapshot <工作副本路徑> \
  --canary-type <型別> --probe <pass|recraftN|recraftN-fail>   # D 前置:結構化取代散文 note
```

**留痕慣例(2026-08-05 借 design-loop T3;原:報告躺 scratchpad,session 一清就蒸發,帳上 note
指向不存在的東西——T8 三輪實錄)**:席報告落 `governance/review-reports/<loop-id>/<round>-<席>.md`、
工作副本(=審查快照,含 canary)存 `<round>-s<席>-snapshot.md` 或共用一份;record 帶
`--report`/`--snapshot` 讓 sha 落帳可重算。code-loop record 不帶 findings_set,不會誤觸 T6 定錨。

**收貨 quote-check(advisory,不進 gate——panel 判準一字不動)**:逐席
`lumos quote-check <席報告> --spec <該席工作副本>`——派工模板本就要求逐字引句(§3 錨定紀律),
這步讓它有機械收貨端:錨不到的條目=弱證據,判讀時要求補引句或降權;報告一旦過錨定,
capture-recapture 的 finder 串也有了可信座標來源。
missed → 該輪判決不採信(canary 硬閘不動)、下一輪(換 canary 型、framing 加碼)。連 2 missed → 升 opus。
★**missed 席 findings 不得直接丟——先過機械 repro triage(2026-08-05 正式化)**★:逐條試以真碼/真跑
證實(repro 腳本/grep 實查/測試重現);證實的走通道 a(執行證據)折入,record note 記「機械證實,
非席信用」;repro 不出的才丟並記 triage 結果。實證:2026-08-04 T8 終審 r1,missed 席交出
「判定輪取錯」與「巢狀引句截斷」兩條真 major,靠 repro 撈回——直接丟=結構性誤殺,
而「撈」以前只是編排者裁量,現在是硬步驟。

> **`--scope-lines` 為什麼要填**:canary 抓到只證該席**醒著**,但外部實測指出**東西越多越抓不到**是最主導的因素(arXiv 2606.15689:抓得到合成缺陷**不可靠地預測**抓得到真實缺陷,且 **diff 大小是主導混淆變數**)。本專案十輪 code-loop 的 diff 從 332 到 2770 行,**在帳上長得一模一樣**——不填就永遠答不出「小 diff 上的 caught 是不是灌水」。**不進 gate、純 telemetry**;`wc -l <patch>` 即可。

### 6 · 問收斂
```bash
lumos loop status code-<topic> --need 2 --gate --repo <repo根>
```
無 `--spec`(代碼無引用座標):G1 印 `skipped` 不計 fail。K-streak ∧ G2 枯竭 → exit 0(PASS)→ finishing;exit 1 → 回步驟 1。

### 7 · mutation 冒煙(可選機械錨,高風險建議)
隔離 worktree 對 diff 模組機械植 3-5 個變異 → 跑該模組測試 → 活變異＝測試沒接住的洞,列 finding 回步驟 4。不經 reviewer、不碰真樹。
- 預設植 **ROR(`<`↔`<=`↔`==`)+ LCR(`and`↔`or`)**;計算密集加 AOR。同一比較式非冗餘變異只 3 個(`<=`、恆 true、恆 false)。
- **timeout → skipped**(不算 finding/存活)。活變異分兩桶:**Survived**(跑到但全綠)＝補斷言;**NoCoverage**(該行沒被執行)＝更強 finding、優先補(變異行改 `raise` 試跑即知)。

---

## 平行 panel 模式(≤3 輪,取代 6 輪循序)

機械原語 loop-agnostic,直接可用;差別:跑 diff 文字檔、canary 是 bug hunk、無 G1。

- **一輪 = 平行 W 個 reviewer**(W＝panel_width:standard 3/high 5),各讀一份工作副本:bug canary 型別跨 slot 輪替、鏡頭各異(bug/資源例外/冪等併發/…)。**跨家族(2026-07-18 S5,取代舊「qwen 只否決」)**——tier=high 雙 Codex 角色:1 席**帶餌正式 finder,佔 W 之一**(與 LLM 席同規則受注意力檢查,findings 計入重疊帳)+1 席**無餌否決席,不佔 W**(外掛,同 spec-conformance 慣例;即使 finder 席漏抓被作廢,外家聲音不斷線)。standard=1 席無餌否決。**否決席落閘路徑**:其 findings 與帶餌席同池進辯方;存活 ≥major——M2 cluster 帳模式必須記為該輪 `<名>=disputed-major` cluster 記錄(severity 欄該模式僅顯示不裁決)/無-cluster 舊帳計入存活 max。**fail 分級**:standard=Codex 不可用退同門+留痕;**tier=high=fail-closed**——第三家族(qwen 有 cross_audit 整合;gemini 候選未驗)替補→延期→皆不可則**不得收斂攤人裁**(人可明示豁免留痕),不分金流與否。qwen 轉列第三家族替補與 finder 輪替候選。
- **spec-conformance slot**(tier=high 且有收斂 spec):追加一個對答案審查員(不佔 W、地位同 qwen),逐條款對照「做了/縮水/多做/未實作」,縮水與未實作進辯方。**含合約候選兌現**(2026-07-29):spec 計劃節點若列「合約候選清單」,逐條驗落地有沒有標 ★INVARIANT★ 綁 [test:]——該綁沒綁=縮水 finding。
- **判讀/辯方/記錄** 同循序(步驟 4-5,含 missed 席 repro triage 與留痕/quote-check 慣例),一輪 W 筆共享 `--round <rid>`。
- **收斂**:`loop status --gate --panel` 三條合取(caught≥2 且 0 missed ∧ 存活 max≤minor ∧ capture-recapture 殘餘<門檻[無 counts＝fail-closed];--min-seats/G3 帶旗標才啟用;cluster 帳=兩條合取,詳 design-loop SKILL panel 節);★**2026-08-06 起新 loop=最後兩輪各自全過(K=2)+PASS 印抽查判定**★(A案;舊 loop 沿 K=1——gate 依首筆日期自動判,不用記);存活≥major → 只重審 delta,cap=3(K=2 的第二乾淨輪計入 cap;cap 頂未湊滿照攤人)。
- capture_counts 別手數 → `lumos loop capture-counts --finder ... --from-pitfalls <range>`(自動收割 linter/regex 確定性 finder)產串。

**端到端一輪**(照抄改參數):
```bash
TOPIC=fix-billing; RANGE=main..HEAD; RID=r1   # loop id=code-$TOPIC,TOPIC 勿再帶 code- 前綴
# 1. 平行派 W 個乾淨 reviewer(各含輪替 canary)→ 收 findings 正規化 file:line
# 2. 算重疊(LLM 手動 --finder + 確定性 finder 自動)
lumos loop capture-counts \
  --finder "billing.py:88,billing.py:120" --finder "billing.py:88,tax.py:12" \
  --from-pitfalls "$RANGE" --repo .
# 3. 記這輪(W 筆共享 --round)
lumos canary record caught --loop "code-$TOPIC" --round "$RID" \
  --auditor slot1 --severity minor --capture-counts "2,1,1"
# 4. 問收斂
lumos loop status "code-$TOPIC" --gate --panel --repo .
# 5. 收斂後留痕才能 push
lumos code-loop pass --note "panel 收斂:capture-recapture 殘餘<1、無存活 major"
```

---

## 護欄 · 天花板 · 收斂後

**護欄**:連 2 missed → 升 opus。cap＝6 筆(循序)/3 輪(panel);到頂未收斂 → 停、攤給人、記「達 cap 未收斂」,別無限燒。

**誠實天花板**(收斂後必向人講):
> 回報遵 CLAUDE.md「對人回報用白話」規則(mutation 之類術語首次出現給一句人話,如 mutation=故意改壞代碼看測試接不接得住)。
1. pattern 掃描是提示器非偵測器(N+1/race 多形態 regex 抓不到);漏網靠 reviewer + canary + 測試。
2. bug canary 校準與溯源排除靠植入者自律、人工判,偏多排,殘餘下一輪兜底。
3. mutation 3-5 個是抽樣非覆蓋;死光≠測試充分;flaky 污染訊號。
4. code-loop 少一道 G1(代碼無引用座標);衍生機械錨(mutation 全滅)留 v2。

**收斂後(強制,不可跳)**:
```bash
lumos impact --diff <merge-base>..HEAD --sync-check   # 落成核對:受影響節點動了沒
lumos code-loop pass --note "<收斂理由/loop-id>"       # pre-push blocking:無 pass/skip 留痕 → push 硬擋
```
- **push 後拉回 CI 結論（僅當專案 `.lumos/config.json` 宣告 `ci` 區塊時；未宣告＝此條不存在）**：`lumos ci-wait` → 綠且 `verdict=green` 才收工；**rc1（紅）＝當輪修**（讀它印的失敗步驟＋log 尾段 → 修 → 推 → 再等，上限 2 次，仍紅則寫 Issue 攤給人）；rc0 但 verdict 是 `timeout`/`no-run`/`unavailable`/`undetermined` **不算綠**（分別是：還沒跑完要手動查／此 sha 沒觸發任何 workflow／環境缺 gh／跑完了但結論既非成功也非失敗——`cancelled`·`action_required`·`stale`，要人判）。**紅燈不過夜**：修不完也要在收尾報告明講「main 上有紅燈未解」，不得靜默收工。⚠ **這是觀測不是強制**：`ci-wait` 擋不了 push、也擋不了 merge，工具缺席／config 壞損一律 fail-open rc0；要「紅燈進不了 main」得在 GitHub 設 branch protection required check（本工具不碰 GitHub 設定）。
存活未修的 minor findings **逐條一句接受理由**(併入 pass --note 或審計紀錄)——沒理由不得 pass(同 design-loop 收斂節,2026-07-17 外部評審吸收)。
**棧別效能檢核(2026-07-19,紀律層)**:pitfalls manifest 帶 `stack_questions`(diff 命中 kt/cs/vue/sql)時,終審留痕須含對應檢核問題的答案(一句即可;同接受理由紀律)——tier=high 落在 pass --note;**tier=standard 走單 reviewer 時同義務落在終審紀錄/commit message**(standard+棧命中是最常見情境,pre-push 亦會 advisory 印問;單 reviewer 實測折入 2026-07-19)。內容源=[[Systems/效能檢核目錄]]。
**UI 層驗收(2026-08-05,MCP 接驗證層;Enzo 靈感立慣例、不綁案)**:diff 命中 UI 棧
(test-layers 宣告 layer 含「UI 驗收」)時,終審驗收=★agent 真開頁面★——用 Playwright MCP
(乾淨瀏覽器)或 claude-in-chrome(需真登入態如 LIFF)逐條執行驗收條款(真點/真填/真看),
證據=截圖+關鍵 console/network 摘要,存 `governance/review-reports/<loop-id>/ui-evidence/`
並由 Verification 節點引用。哲學同 quote-check:證據可重放,不是口頭宣稱「看起來對」。
無法起環境(lab 不在/需登入而無 session)→ 明記「UI 層未驗+原因」,不得靜默跳過。
**真跑優先(2026-07-18 S1,紀律層規則非機械閘)**:diff 經 `lumos impact --diff` 命中綁 `[test:]` 的星標合約節點時,pass 前**只跑該綁定測試**(非全套)且須綠,結果記入 pass --note——LLM 判官意見不能替代這一跑(信任階梯:真跑>機械查>LLM 判官>自報)。`[test:]` 存的是測試名非指令,解析順序=①合約節點/專案圖譜記載的完整指令 ②依該棧慣例組指令(`dotnet test --filter`/`python3 scripts/test_lumos.py -k` 等)③歧義/查無 → **不得靜默跳過**:退跑該測試檔/模組級,再不行跑全套,留痕記「解析歧義」——「解析不了所以沒跑」不構成放行理由。機械化留 v2(動 gate code 另立計劃)。
→ 交 **finishing-a-development-branch** 進合併流程。

---

## 參考(需要才讀)

**code-loop ≠ design-loop 換名字**(2026-07-09 文獻;設計見 `[[loop三輪壓縮_計劃]]`):代碼可執行+可靜態分析,最佳解是**異質 ensemble** 非「多個多樣 LLM」——
- 確定性驗證器(linter SARIF/測試/type checker/mutation)**不佔 canary 席、不進輪有效**(跑真碼樹看不到文字副本裡的餌,記席必 missed;2026-07-18 codestage);參與三通道=(a) findings 憑執行證據機械證實折入 (b) 異質 finder 進 capture-recapture 帳(⚠ M2 cluster 帳下 advisory 不進合取,裁決權歸通道 a)(c) 跑真碼沿隔離 worktree 模式。錯誤剖面與 LLM 正交,才買到真獨立訊號、破「9 judge 2 票」。
- 辯方用**可執行 falsification**(跑測試/repro/mutation 確認或殺一條 finding)> 論證反證。

**出處**:抑噪兩句 borrow PR-Agent;mutation 算子 borrow Offutt E-selective / PItest / Kurtz FSE2016;Survived/NoCoverage borrow Stryker;異質 ensemble borrow AutoSafeCoder(arxiv 2511.16708)、Greptile TREX / CodeRabbit。派工模板見 `../lumos-design-loop/templates.md` §3-4/§7.5。設計全文 `docs/design/2026-07-04-pitfalls-code-loop.md`。
