---
name: lumos-code-loop
description: 分支終審前執行代碼對抗審計 loop——pitfalls --diff 命中 tier high 時觸發、派乾淨 reviewer 驗醒著、辯方殺假陽性、證據閘收斂才放行 finishing。對齊「收斂=終審綠燈」。觸發詞:分支終審、code review 對抗、pitfalls diff 命中 tier high、代碼審計 loop、終審前對抗審。
---

# lumos-code-loop:分支終審前的 canary-護對抗代碼審 loop

**Claude 編排,lumos 出原語**:你用 Agent tool 派 reviewer、判讀、修碼;lumos 記錄與算收斂,不 spawn agent。機制與 design-loop 1:1,差異只在 canary 是 bug hunk、無 G1、mutation 冒煙為機械錨。

## 一眼看懂

- **何時**:分支終審前跑 `lumos pitfalls --diff <merge-base>..HEAD` → `tier: high` 才走本 skill(K=2);`standard` 走單 reviewer;trivial 可跳(commit 註明)。
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

- **收斂** = 連 2 輪 caught 且無 blocker/major ∧ 發現枯竭 → 記 `code-loop pass` 留痕 → finishing。

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
- **修進真碼**:fix commit + 必要新測試。業務合約級隱患 → 另寫圖譜 ★INVARIANT★ 綁 `[test:]`;非合約級測試進套件靠回歸守。

### 5 · 記錄
```bash
lumos canary record caught|missed --loop code-<topic> \
  --severity <辯方後存活 max> --findings <存活折入數> --auditor <模型>
```
missed → 該輪不採信、findings 全不折、下一輪(換 canary 型、framing 加碼)。連 2 missed → 升 opus。

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
- **spec-conformance slot**(tier=high 且有收斂 spec):追加一個對答案審查員(不佔 W、地位同 qwen),逐條款對照「做了/縮水/多做/未實作」,縮水與未實作進辯方。
- **判讀/辯方/記錄** 同循序(步驟 4-5),一輪 W 筆共享 `--round <rid>`。
- **收斂**:`loop status --gate --panel` 四條合取(caught≥2 且 0 missed ∧ 存活 max≤minor ∧ capture-recapture 殘餘<門檻[無 counts＝fail-closed]);一乾淨輪即收斂,存活≥major → 只重審 delta,cap=3。
- capture_counts 別手數 → `lumos loop capture-counts --finder ... --from-pitfalls <range>`(自動收割 linter/regex 確定性 finder)產串。

**端到端一輪**(照抄改參數):
```bash
TOPIC=code-fix-billing; RANGE=main..HEAD; RID=r1
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
> **回報用白話(CLAUDE.md「對人回報用白話」)**:向人講終審結果與天花板時少專有名詞——canary/tier/mutation/fail-open/G1 第一次出現給一句人話(如 mutation=故意改壞代碼看測試接不接得住),或換人話。術語細節留圖譜。目標:人少花一層理解成本。
1. pattern 掃描是提示器非偵測器(N+1/race 多形態 regex 抓不到);漏網靠 reviewer + canary + 測試。
2. bug canary 校準與溯源排除靠植入者自律、人工判,偏多排,殘餘下一輪兜底。
3. mutation 3-5 個是抽樣非覆蓋;死光≠測試充分;flaky 污染訊號。
4. code-loop 少一道 G1(代碼無引用座標);衍生機械錨(mutation 全滅)留 v2。

**收斂後(強制,不可跳)**:
```bash
lumos impact --diff <merge-base>..HEAD --sync-check   # 落成核對:受影響節點動了沒
lumos code-loop pass --note "<收斂理由/loop-id>"       # pre-push blocking:無 pass/skip 留痕 → push 硬擋
```
存活未修的 minor findings **逐條一句接受理由**(併入 pass --note 或審計紀錄)——沒理由不得 pass(同 design-loop 收斂節,2026-07-17 外部評審吸收)。
**棧別效能檢核(2026-07-19,紀律層)**:pitfalls manifest 帶 `stack_questions`(diff 命中 kt/cs/vue/sql)時,終審留痕須含對應檢核問題的答案(一句即可;同接受理由紀律)——tier=high 落在 pass --note;**tier=standard 走單 reviewer 時同義務落在終審紀錄/commit message**(standard+棧命中是最常見情境,pre-push 亦會 advisory 印問;單 reviewer 實測折入 2026-07-19)。內容源=[[Systems/效能檢核目錄]]。
**真跑優先(2026-07-18 S1,紀律層規則非機械閘)**:diff 經 `lumos impact --diff` 命中綁 `[test:]` 的星標合約節點時,pass 前**只跑該綁定測試**(非全套)且須綠,結果記入 pass --note——LLM 判官意見不能替代這一跑(信任階梯:真跑>機械查>LLM 判官>自報)。`[test:]` 存的是測試名非指令,解析順序=①合約節點/專案圖譜記載的完整指令 ②依該棧慣例組指令(`dotnet test --filter`/`python3 scripts/test_lumos.py -k` 等)③歧義/查無 → **不得靜默跳過**:退跑該測試檔/模組級,再不行跑全套,留痕記「解析歧義」——「解析不了所以沒跑」不構成放行理由。機械化留 v2(動 gate code 另立計劃)。
→ 交 **finishing-a-development-branch** 進合併流程。

---

## 參考(需要才讀)

**code-loop ≠ design-loop 換名字**(2026-07-09 文獻;設計見 `[[loop三輪壓縮_計劃]]`):代碼可執行+可靜態分析,最佳解是**異質 ensemble** 非「多個多樣 LLM」——
- 確定性驗證器(linter SARIF/測試/type checker/mutation)**不佔 canary 席、不進輪有效**(跑真碼樹看不到文字副本裡的餌,記席必 missed;2026-07-18 codestage);參與三通道=(a) findings 憑執行證據機械證實折入 (b) 異質 finder 進 capture-recapture 帳(⚠ M2 cluster 帳下 advisory 不進合取,裁決權歸通道 a)(c) 跑真碼沿隔離 worktree 模式。錯誤剖面與 LLM 正交,才買到真獨立訊號、破「9 judge 2 票」。
- 辯方用**可執行 falsification**(跑測試/repro/mutation 確認或殺一條 finding)> 論證反證。

**出處**:抑噪兩句 borrow PR-Agent;mutation 算子 borrow Offutt E-selective / PItest / Kurtz FSE2016;Survived/NoCoverage borrow Stryker;異質 ensemble borrow AutoSafeCoder(arxiv 2511.16708)、Greptile TREX / CodeRabbit。派工模板見 `../lumos-design-loop/templates.md` §3-4/§7.5。設計全文 `docs/design/2026-07-04-pitfalls-code-loop.md`。
