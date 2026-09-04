---
name: lumos-code-loop
description: 分支終審前執行代碼對抗審計 loop——pitfalls --diff 命中 tier high 時觸發、派乾淨 reviewer 驗醒著、辯方殺假陽性、證據閘收斂才放行 finishing。對齊「收斂=終審綠燈」。觸發詞:分支終審、code review 對抗、pitfalls diff 命中 tier high、代碼審計 loop、終審前對抗審。
---

# lumos-code-loop:代碼對抗審計 loop 參考層(分支終審前的硬閘)

## 目錄

1. 何時用 / 何時跳
2. 每一輪的現行步驟
3. 席位紀律與抑噪
4. panel 模式與收斂判準
5. mutation 與 capture-recapture
6. 真跑優先與 UI 層驗收
7. code-loop 與 design-loop 的差異
8. 參考(需要才讀)
9. 歷史與停用(舊頭版全文;只供回放舊帳判讀,不是現行規則)
   (「一眼看懂」併在 1 底下;「護欄」併在 3 底下;兩版「平行 panel 模式」併在 4 底下)

## 何時用 / 何時跳

- **觸發**:分支終審前跑 `lumos pitfalls --diff <merge-base>..HEAD`。
  - `tier: standard`(manifest 無命中)→ 現行單 reviewer 終審,**不走本 skill**。
  - `tier: high`(manifest 命中任一 pattern)→ 本 skill。★K 看模式:循序=2、平行 panel=1(tier=high 實務走 panel)。原本這裡只寫 K=2,對走 panel 的人是錯的——2026-08-03 修★
- **trivial 可跳**:改 typo / 純文檔 / 一行無邏輯 diff → 跳 loop,**但寫一句為什麼跳**(commit message)。
- **loop id** = `code-<topic>`(例:`code-payment-retry`、`code-worker-refactor`)。


> (⚠ 上方為舊版、下方為 2026-08-22 搬入的現行版;兩版並存只為保留原文,**照下方做,勿照上方執行**)

### 一眼看懂

- **何時**:分支終審前跑 `lumos pitfalls --diff <merge-base>..HEAD` → `tier: high` 才走本 skill;`standard` 走單 reviewer(★2026-08-18 起循序 loop 可正常錨定 `--tier standard`(cap 3),守衛誤擋已修——首筆 record 就帶 --tier★;★原本這裡寫「(K=2)」是★講反的★:tier=high 實務上走平行 panel,而 panel 是 **K=1**;K=2 是循序模式的數字。2026-08-03 修★);trivial 可跳(commit 註明)。進場可先 `lumos testmap affected --diff <merge-base>..HEAD` 拿建議測試清單(advisory,需先 `testmap build` 過)。
- **gate/守衛類 code 建議 feature branch**(2026-07-22 prepush範圍修法):pre-push 對 branch 與 main-direct **現已同軌**檢查(讀 stdin 推送範圍逐 ref 判,非 merge-base)——此為縱深建議非機械強制。
- **loop id** = `code-<topic>`（例 `code-payment-retry`）。
- **一輪 = 7 步(循序)** 或 **平行 panel(≤3 輪,見下)**:

## 每一輪的現行步驟

### 步驟總覽(2026-08-22 搬入版)

  1. 產 diff 文字檔 → 複製工作副本
  2. ~~植 bug canary hunk~~ ⛔ 已停用(見頁頂)
  3. ~~三道防污染自檢~~ ⛔ 隨植入停用(無植入即無污染面)
  4. 派乾淨 reviewer + 抑噪紀律 + impact 鏡頭
  5. 判讀:辯方殺假陽性 → 存活 max severity
  6. 記錄 `canary record none`(disposal 版模板:carrier 帶 --findings-set/--folded-set/--accepted-set,
     `loop next` 已泛型吐 `disposal_cmd`——★只換閘不換記帳式,disposal 恆卡「無處置帳」★)
     → 問收斂 `loop status --disposal --spec <凍結 diff/patch> --repo <root>`(2026-08-08 起;舊帳沿舊閘)
  7.(可選)mutation 冒煙補機械錨

### 步驟 1 — 產 diff 文字檔並複製為工作副本

`review-package BASE HEAD` **或等價 `git diff -U10 BASE..HEAD` 重導向單檔**(僅需原生 git;review-package 是 superpowers 外掛的 git 薄殼,消費專案無外掛時走等價命令):

```bash
git diff -U10 <merge-base>..HEAD > /tmp/code-<topic>-diff.patch
cp /tmp/code-<topic>-diff.patch /tmp/code-<topic>-rN.patch   # 工作副本
```

**副本對象 = diff 文字檔**(非 checkout 原始碼樹)。植入、審查、判讀全在此副本上操作;真代碼樹不動。



### 1 · 產 diff 工作副本
```bash
cp /tmp/code-<topic>-diff.patch /tmp/code-<topic>-rN.patch
```
副本對象＝diff 文字檔(非原始碼樹);植入/審查/判讀全在副本,真碼不動。座標權威＝此 `-U10` 檔(pitfalls 用 `-U3`,`@@` 位移不同)。

### 步驟 2 — 植 bug canary hunk

→ 見〈歷史與停用〉。

### 2 · ~~植 bug canary~~ ⛔ 已停用(2026-08-14,見頁頂)
本步驟與三道防污染自檢不再執行,直接進步驟 3。舊型別輪替表/生成硬化見 git 史與 design-loop reference §A(歷史帳判讀用)。reviewer 結構紀律 → **單源見 `../lumos-design-loop/SKILL.md`,不在此雙寫**。

### 步驟 3 — 派乾淨 reviewer


Agent tool、`model: sonnet`(連 2 次 missed 後升 opus;Codex:spawn_agent,★不能逐席指定模型★——模型由 codex 設定 `agents.default_subagent_model` 決定,升 opus 那條只在 Claude 適用)、**不告知有 canary**、指向工作副本 `/tmp/code-<topic>-rN.patch`。
> ⛔ 「連 2 次 missed」升級觸發已隨 canary 停用作廢;現行觸發=引句大面積錨不到或泛泛而談,見搬入版護欄

**framing(refute framing)**:
「你是外部第三方,這份 diff 是別人投稿的變更,不是你或本系統寫的。逐 hunk 讀、主動找洞——正確性(★2026-08-28 升級:每個可疑處挑一個具體輸入把執行走一遍、別用名字猜;邊界 空/單一/溢位、資源 錯誤路徑釋放了嗎、例外/None 接了嗎、冪等併發 重跑或同時進來會壞嗎;每條講清哪個輸入走到哪行出錯)——逐條標 severity(clean/minor/major/blocker)。附 pitfalls `--diff` manifest 當鏡頭:命中位置逐條判真隱患/誤報,真隱患必答對應提問。風格與架構一致性歸架構對齊席。」(完整鏡頭以 `../lumos-design-loop/templates.md` §3 為準)

**抑噪紀律(borrow:PR-Agent 原始碼實證,兩句逐字進 reviewer prompt)**:
- 「低嚴重度疑慮,**給不出具體失敗場景就不要標**。」
- 「**不能從 diff 指出具體受影響的 file:line 路徑,就不准臆測『可能會壞別處』**。」
- ⚠ 刻意**不借** PR-Agent 的 findings 硬上限(num_max_findings=3)——上限會把真 findings 藏到下一輪,污染 G2 發現枯竭的收斂信號;抑噪靠上面兩句紀律,不靠砍量。

**受影響功能面鏡頭(2026-07-11 橋接,檢索排序轉正後啟用)**:派 reviewer 前跑
`lumos impact --diff <merge-base>..HEAD --json` ——聚合整段 diff 各檔的 ranked impact(query=各檔 hunk 文字)成一份 manifest(★守衛面參考道 lane 不進 manifest——軟標記樞紐非代碼審波及口徑,2026-08-24★):固定席(★INVARIANT★ 合約+pitfall_when 事故)全保、非固定取跨檔最高分 top-8。★2026-08-29 改:固定席**逐條貼進每一席的派工詞**(不是給 manifest 路徑讓它自己讀——給路徑那條經兩輪設計審否決,見 [[Projects/impact鏡頭機械化_計劃]])★,要它「逐條判此 diff 會不會破壞該節點宣稱的行為/合約;固定席必答」。**定位=advisory 人判**(機械保證只涵蓋合約/事故類固定席,其餘經排序無保底——保底與噪音都靠 reviewer 兜,故當鏡頭不當自動閘)。註:單檔版 ranked 已於 2026-07-11 過 §6 轉正接上 PreToolUse hook;--diff 聚合版仍維持審計鏡頭定位。

> manifest 現含兩種來源的 claim(`source` 欄區分):regex claim(`source:"pitfalls-builtin"`,讀 `question` 對應提問)與 lint claim(`source:"lint:<driver>"`,來自專案 `.lumos/lint.json` 宣告的社群 linter SARIF,讀 `message`——linter 已是具體診斷、無 question 欄)。reviewer 鏡頭對 lint claim 讀 `message`、對 regex claim 仍讀 `question`。

第一次 missed 起加碼 framing:「逐 hunk 讀,你一定找得到至少一個植入的 bug;沒找到就是你沒讀仔細。」

---


### 3 · 派乾淨 reviewer
Agent tool、`model: sonnet`(升級條件單源見 design-loop 護欄:引句大面積錨不到/通用回應 → 升 opus;Codex:spawn_agent 不能逐席指定模型,升級靠改 `agents.default_subagent_model`)、指向工作副本。

**refute framing**(★完整鏡頭以 `../lumos-design-loop/templates.md` §3 為準;2026-08-28 升級=正確性鏡頭從名詞清單改成帶例子的問句+「挑具體輸入走一遍別用名字猜」,借 Meta 半形式推理免費半截★):「你是外部第三方審別人投稿的 diff。逐 hunk 找洞——正確性(邊界:空/單一/溢位;資源:錯誤路徑釋放了嗎;例外/None 接了嗎;冪等併發:重跑/同時進來會壞嗎;每條講清哪個輸入走到哪行出錯)、逐條標 severity(clean/minor/major/blocker)。附 pitfalls manifest 當鏡頭,命中位置逐條判真隱患/誤報。風格與架構一致性歸架構對齊席。」

**抑噪紀律(逐字進 prompt)**:
- 「低嚴重度疑慮,給不出具體失敗場景就不要標。」
- 「不能指出具體受影響 file:line,就不准臆測『可能會壞別處』。」
- （不設 findings 硬上限——會藏真 finding、污染 G2 收斂信號。）

**席位立場+輸出格式(2026-08-29 A+C,`../lumos-design-loop/templates.md` §7.7)**:多席 panel 每席在鏡頭外加「立場+預設姿態」(措辭自己改寫別逐字貼);敘述每條 ≤3 句、不准模稜兩可(結構欄位不計);★預設姿態不放寬證據要求,抑噪紀律照舊★;單席通才不套立場。

**圖譜鏡頭(★2026-08-29 改:每席都附、貼內容不給路徑★)**:派前跑 `lumos impact --diff <range>`,把**固定席**(帶硬合約或出過事故的節點)**逐條貼進每一席的派工詞**——不是給 manifest 路徑讓它自己讀(給路徑那條 2026-08-29 兩輪設計審否掉了,見 [[Projects/impact鏡頭機械化_計劃]])。派工詞寫「逐條判此 diff 破不破壞節點合約;固定席必答」(advisory 人判)。完整格式見 `../lumos-design-loop/templates.md` §3 鏡頭 3,含兩個填寫雷:①來源是 `governance/review-reports/**` 凍結快照 patch 的節點要剔掉(審計證物,裡面故意埋 bug)②「還有 N 篇」的 N 會少報。

**test-layers 鏡頭(有宣告才附)**:派前跑 `lumos test-layers --diff <range> --json`,`hits` 非空 → 附給 reviewer:「diff 碰到 <棧> 且專案宣告 <層> 測試(<cmd>)——判斷此改動需不需要補/跑該層;需要而缺 → 列 finding(severity 依風險自判)」。無宣告檔則略過此鏡頭。

第一次 missed 起加碼:「你一定找得到至少一個植入 bug;沒找到就是沒讀仔細。」

### 收貨三道

**收貨三道(2026-08-08,plan:[[Projects/驗證層去模型化_計劃]] S2a;前置=派工當下落
`rN-dispatch.json`(`{round,seat,lens,materials,auditor}`,與席報告同目錄同 commit))**:
①`lumos quote-check <席報告> --spec <該席工作副本>`(carrier 報告供 disposal gate 錨定條;其餘席 advisory)
②`lumos refcheck <席報告> --repo <root>`(finding 引的 file:line 機械驗存在/範圍——引了不實指涉當場現形)
③`lumos seat-check <席報告> --dispatch <rN-dispatch.json> --ledger <out-of-scope.jsonl>`(有講沒做對帳,觀測恆 rc0)
> ⛔ `lumos mutate` 已退場(2026-08-26 建了沒人跑批次裁定:2026-08-08 裁死消費者後治理帳 0 次使用;指令與測試已拆,復活=有真消費者立案從 git 史撿回,詳 [[Projects/建了沒人跑批次裁定_計劃]])。

### 步驟 4 — 判讀 + 辯方


**① canary 判讀**
caught = reviewer 清楚且正確點出那個植入 bug 的「性質」(如「邊界 off-by-one」「鎖未釋放」);光 token 出現、或泛泛說「這段有問題」不算。

**② 真 finding 取 max severity**
排掉 canary 及其溯源影子後,剩餘 findings 的 max severity(`clean` / `minor` / `major` / `blocker`)。
剝「審計員誤判」要克制:只有能指出該 finding 客觀錯在哪(被真 diff 的 file:line 反證)才剝;判不準就保留(寧可高估),剝除理由記入審計紀錄。

**③ 辯方 refute(對 ② 標為 ≥major 的每條 finding)**
派 1 個獨立 Codex 辯方(`codex exec --sandbox read-only`,乾淨脈絡、不傳 reviewer 報告結論;2026-07-18 S5,不可用退 opus 註記偏離。詳見下方「辯方(對每條 ≥major)」),framing:「預設這條 finding 假/嚴重度高估,構造反駁證據。必須附 file:line(grep/Read 真代碼),光說『沒問題』不算;拿不出反證則維持原 severity。」辯方**明確三選一**(2026-08-27,[[Systems/finding-refute]]):**agree**(同意是真的→維持)/ **evidence**(拿反證降到 minor/clean+file:line)/ **concern**(拿不出反證只存疑→維持)。★只有 evidence 會降,照舊必附 file:line;concern 不能單獨殺 finding。★被駁倒(evidence)→ 降級、不折、審計紀錄標「辯方反證:<file:line>」。三態填進 `canary record --refute-verdict <id>=agree|evidence|concern`——**純記帳不改判閘**(去向仍由 folded/accepted 定),供日後偵測 2026-08-22「三分類先不做」的重啟條件。
- **辯方工具加 `git log`/`git show`**——commit 考古常是決定性反證(發版狀態、先例、時序)。完整派工模板見 `../lumos-design-loop/templates.md` §3-4(2026-07-07 Landmark 實戰)。
- **辯方順產 fix(實戰調參)**:辯方降級時若附「最小修法建議」,直接轉入 fix 佇列(nice-to-have 轉修,不折 finding、不佔 severity)——別浪費辯方查證時看到的低垂果實。

**④ 該輪 severity = 辯方裁決後存活 findings 的最高**



### 4 · 判讀 + 辯方
- ~~canary 判定~~ **⛔ 已停用(見頁頂)**——「reviewer 有沒有真的讀」由收貨三道的 quote-check 引句錨定把關。
- **max severity**:存活 max。剝「誤判」要克制——只有能用真 diff file:line 反證才剝,判不準保留。
- **辯方(對每條 ≥major;預設 Codex,2026-07-18 S5)**:派 1 個 **Codex 辯方**(`codex exec --sandbox read-only`,乾淨脈絡)——判決單點最怕同門盲點,外家反證價值最高;Codex 不可用退 opus 並於留痕註記偏離。framing=「預設此 finding 假,構造反駁證據、必附 file:line(grep/Read 真碼),拿不出則維持」。可加 `git log`/`git show`(commit 考古常決定性)。辯方降級若順手附最小修法 → 轉 fix 佇列。
- **該輪 severity** ＝ 辯方裁決後存活 max。

### 修與翻紅釘

**⑤ 存活真 finding 修進真代碼**
fix commit(含必要的新測試)。測試收口分兩級:
- 隱患屬業務合約級 → 另寫圖譜 ★INVARIANT★ 並 `[test:]` 綁定(Check T 掃圖譜合約綁定才接住)。
- 非合約級的實作測試進套件靠回歸守,不經 Check T、不硬掛圖譜。


- **修進真碼**:fix commit + 必要新測試。**修 bug 標配「還原翻紅釘」**——把 bug 還原回去、綁定測試必須翻紅的回歸測試(存在且全綠的測試可能什麼都沒驗;「存在」騙得過、「翻紅」騙不過)。
  - ★**翻紅釘必須配一條「現場成立」前置斷言**★——證明**被測那條路真的被執行到**。翻紅釘對「現場走不到被測分支」這一型★完全瞎★:布置錯的現場下,把修法還原回去,測試照樣全綠(2026-08-01 實例:要驗 `rmdir` 的例外處理,現場卻布置成「父目錄非空」→ `rmdir()` 根本不會被呼叫)。前置斷言失敗 ＝ 這條測試根本沒在測它宣稱要測的東西,**比主斷言失敗更該優先修**。寫法:
    ```python
    check("★前置★ 現場成立:rmdir 這一步真的拋了例外(輸出有『順帶清理』字樣)", "順帶清理空目錄" in out, out)
    ```
  - **寫測試/審測試前對照 [[Systems/測試假綠形態]] 八型清單**(恆真斷言/斷言太鬆/驗寫法不驗行為/現場走不到被測分支/fixture 無鑑別力/根本沒去驗/白名單過寬/依賴環境巧合)。⚠ **對照過清單 ≠ 測試夠格**——清單是提示器不是偵測器,且★一定有第九型★。
  - 業務合約級隱患 → 另寫圖譜 ★INVARIANT★ 綁 `[test:]`;非合約級測試進套件靠回歸守。

### 步驟 5 — 記錄
> ⛔ `canary record caught|missed` 的 kind 隨植入協議 2026-08-14 停用;現行一律 `canary record none … --findings-set/--folded-set/--accepted-set --report --snapshot --scope-lines`,語法見下方「5 · 記錄」。

```bash
lumos canary record caught|missed \
  --loop code-<topic> \
  --severity <辯方裁決後存活 max> \
  --findings <存活折入數> \
  --auditor <模型>
```

- `--severity` = ④ 辯方重算後的存活 max(非 reviewer 原評)。
- `--findings` = ④ 辯方裁決後存活並折入的真 finding 條數(canary 不計;missed 輪不折記 0)。
- **missed → 該輪判決不採信、findings 全不折**,直接下一輪(N+1、自動換 canary 類型、framing 加碼)。
- **連 2 missed → 升 opus**(canary-log 最近 2 筆都 missed;中間一筆 caught 即重置)。

---


### 5 · 記錄
```bash
lumos canary record none --loop code-<topic> \
  --severity <辯方後存活 max> --findings <存活折入數> --auditor <模型> \
  --scope-lines <這輪 diff 幾行> \
  --report <席報告路徑> --snapshot <工作副本路徑>
```

**留痕慣例(2026-08-05 借 design-loop T3;原:報告躺 scratchpad,session 一清就蒸發,帳上 note
指向不存在的東西——T8 三輪實錄)**:席報告落 `governance/review-reports/<loop-id>/<round>-<席>.md`、
工作副本(=審查快照)存 `<round>-s<席>-snapshot.md` 或共用一份;record 帶
`--report`/`--snapshot` 讓 sha 落帳可重算。code-loop record 不帶 findings_set,不會誤觸 T6 定錨。



**翻紅釘證據制(S3)**:blocker/major 折入採信=必附「先紅後綠」——一條當下翻紅的測試(或可執行重現指令+輸出),
修完轉綠才記 folded,處置帳 note 記測試名/紅綠 rc;捏造的 bug 寫不出會紅的測試。文件精度 minor 豁免;
「真但沙盒不可重現」→ accepted 明文理由。★誠實定位:v1=證據形式紀律+note 留痕,採信仍編排者;
結構化欄位+讀側重跑=v2★。
派工模板本就要求逐字引句(§3 錨定紀律),收貨端機械化:錨不到的條目=弱證據,判讀時要求補引句或降權;報告一旦過錨定,
capture-recapture 的 finder 串也有了可信座標來源。

★**可疑席的 findings 不得直接丟——先過機械 repro triage(2026-08-05 正式化;停用制下觸發改為
「quote-check 大面積錨不到/通用回應」的席)**★:逐條試以真碼/真跑證實(repro 腳本/grep 實查/
測試重現);證實的走通道 a(執行證據)折入,record note 記「機械證實,非席信用」;repro 不出的才丟
並記 triage 結果。實證:2026-08-04 T8 終審 r1 + 2026-08-14 Landmark code-crossclaim r4,
可疑席各交出真 major 靠 repro 撈回——直接丟=結構性誤殺,「撈」是硬步驟不是裁量。

> **`--scope-lines` 為什麼要填**:外部實測指出**東西越多越抓不到**是最主導的因素(arXiv 2606.15689:抓得到合成缺陷**不可靠地預測**抓得到真實缺陷,且 **diff 大小是主導混淆變數**)。本專案十輪 code-loop 的 diff 從 332 到 2770 行,**在帳上長得一模一樣**——不填就永遠答不出「小 diff 上的 caught 是不是灌水」。**不進 gate、純 telemetry**;`wc -l <patch>` 即可。

### 步驟 6 — 問收斂
> ⛔ 本步驟裡的 `--need 2 --gate`(K-streak)已於 2026-08-08 被處置閘取代:現行問 `lumos loop status code-<topic> --disposal --spec <凍結 patch> --repo <repo根>`(見〈panel 模式與收斂判準〉開頭「現行收斂閘=處置閘」)。舊指令只供舊帳回放。

```bash
lumos loop status code-<topic> --need 2 --gate --repo <repo根>
```

無 `--spec`(code-loop 無 spec 對象,G1 引用座標對代碼無意義):
- G1 印 `[gate] G1 refcheck: skipped(無 spec 對象)`、**不計 fail**。
- K-streak(★**循序模式**:連 2 輪 caught 且無 blocker/major;★**panel 模式只看最後一輪(K=1)**★) ∧ G2 發現枯竭 → exit 0(GATE PASS)→ 進 finishing。
> ⛔ 此判準已被處置閘取代,見〈panel 模式與收斂判準〉開頭;K 值討論只供舊帳回放
- exit 1 → 逐錨明細指出斷在哪 → 回步驟 1。

---


### 6 · 問收斂
```bash
```
無 `--spec`(代碼無引用座標):G1 印 `skipped` 不計 fail。K-streak ∧ G2 枯竭 → exit 0(PASS)→ finishing;exit 1 → 回步驟 1。

**誠實天花板(收斂後務必向人提醒)**


1. **pattern 掃描是提示器不是偵測器**:N+1/race 多數形態 regex 抓不到;買到的是「reviewer 注意力被導到高風險位置」,漏網靠 reviewer 本身 + canary 紀律 + 測試。單行掃描能力邊界:「迴圈體內/交易語境/續行 timeout」等跨行語境單行不可判,實作以單行 + 小行窗啟發為限;做不到的形態誠實不掃、不硬湊。
2. **bug canary 的校準與污染殘餘**:「認真審抓得到、不一眼看穿」靠植入者自律(同 design-loop 校準鐵則);溯源排除規則由編排者人工判,判錯方向偏「多排」,殘餘=真 finding 被誤排的假陰性,下一輪重挖兜底。
3. **mutation 冒煙的誠實邊界**:3-5 個手植變異是抽樣不是覆蓋;活變異=測試缺口的存在證明,死光≠測試充分;flaky 測試會汙染訊號。
4. **code-loop 收斂少一道 G1**:gate 對代碼只剩 K-streak ∧ G2,「引用座標」類機械錨無對應物;衍生的機械錨(如 mutation 全滅)留 v2 評估是否進 gate。

---


**誠實天花板**(收斂後必向人講):
> 回報遵 CLAUDE.md「對人回報用白話」規則(mutation 之類術語首次出現給一句人話,如 mutation=故意改壞代碼看測試接不接得住)。
1. pattern 掃描是提示器非偵測器(N+1/race 多形態 regex 抓不到);漏網靠 reviewer + 測試。
2. 收斂只證「這批 reviewer 挖不出新的」,不證乾淨;findings 存廢仍由編排者判,無外部 oracle。
3. mutation 3-5 個是抽樣非覆蓋;死光≠測試充分;flaky 污染訊號。
4. code-loop 少一道 G1(代碼無引用座標);衍生機械錨(mutation 全滅)留 v2。

### 留痕與 CI 判讀


`lumos loop status` exit 0 → 向人回報收斂 + 上述天花板 → **必須先記 code-loop pass 留痕** → 再交 **finishing-a-development-branch** 進合併流程。

**強制步驟（不可跳）：**
```bash
lumos impact --diff <merge-base>..HEAD --sync-check   # 落成核對:受影響功能的節點動了沒?未同步清單逐條判(漏了就補,不用就心裡有數)
lumos code-loop pass --note "<收斂理由 / loop-id，例:code-<topic> 收斂 N 輪 caught 無 blocker>"
```

> **為什麼**：pre-push hook 已升級為 **blocking**——tier=high 分支若無有效的 `pass`（或 `skip`）留痕，`git push` 會被硬擋（rc1）。`loop status` exit 0 只代表審計收斂，留痕要另外寫一次才閉環。`skip` 是假陽性逃生閥（繞行也留痕），正常收斂後用 `pass`。

> 設計全文見 `docs/design/2026-07-04-pitfalls-code-loop.md` ### ③ `lumos-code-loop`。



**收斂後(強制,不可跳)**:
```bash
lumos impact --diff <merge-base>..HEAD --sync-check   # 落成核對:受影響節點動了沒
lumos code-loop pass --note "<收斂理由/loop-id>"       # pre-push blocking:無 pass/skip 留痕 → push 硬擋
```
- **push 後拉回 CI 結論（僅當專案 `.lumos/config.json` 宣告 `ci` 區塊時；未宣告＝此條不存在）**：`lumos ci-wait` → 綠且 `verdict=green` 才收工；**rc1（紅）＝當輪修**（讀它印的失敗步驟＋log 尾段 → 修 → 推 → 再等，上限 2 次，仍紅則寫 Issue 攤給人）；rc0 但 verdict 是 `timeout`/`no-run`/`unavailable`/`undetermined` **不算綠**（分別是：還沒跑完要手動查／此 sha 沒觸發任何 workflow／環境缺 gh／跑完了但結論既非成功也非失敗——`cancelled`·`action_required`·`stale`，要人判）。**紅燈不過夜**：修不完也要在收尾報告明講「main 上有紅燈未解」，不得靜默收工。⚠ **這是觀測不是強制**：`ci-wait` 擋不了 push、也擋不了 merge，工具缺席／config 壞損一律 fail-open rc0；要「紅燈進不了 main」得在 GitHub 設 branch protection required check（本工具不碰 GitHub 設定）。
存活未修的 minor findings **逐條一句接受理由**(併入 pass --note 或審計紀錄)——沒理由不得 pass(同 design-loop 收斂節,2026-07-17 外部評審吸收)。
**棧別效能檢核(2026-07-19,紀律層)**:pitfalls manifest 帶 `stack_questions`(diff 命中 kt/cs/vue/sql)時,終審留痕**建議**含對應檢核問題的答案(一句即可;同接受理由紀律;★工具不驗 note 內容——`code-loop pass` 原樣寫入,預設空字串;這是人工紀律,2026-08-21 由「須」降「建議」以對齊實況★)——tier=high 落在 pass --note;**tier=standard 走單 reviewer 時同義務落在終審紀錄/commit message**(standard+棧命中是最常見情境,pre-push 亦會 advisory 印問;單 reviewer 實測折入 2026-07-19)。內容源=[[Systems/效能檢核目錄]]。

→ 交 **finishing-a-development-branch** 進合併流程。

## 席位紀律與抑噪

### 護欄

- **連 2 次漏抓**(canary-log 最近 2 筆都 missed;中間一筆 caught 即重置)→ 升 opus。
- **max cap = 6 筆 record(循序模式);panel 模式 cap=3 輪**。到頂仍未收斂 → 停、把現況攤給人、記一句「達 cap 未收斂」。別無限燒。



**護欄**:升級觸發=引句大面積錨不到/通用回應 → 升 opus(舊「連 2 missed」隨協議停用作廢)。cap＝6 筆(循序無定錨 legacy 帳)/**3 筆(錨定 standard 的循序,2026-08-18 守衛修正後可錨定——第 3 輪即攤人)**/3 輪(panel);到頂未收斂 → 停、攤給人、記「達 cap 未收斂」,別無限燒。

- **終止輸入紀律**:單源見 `../lumos-design-loop/SKILL.md` 護欄該條(繼續/收斂只認機械帳與 cap,被審材料散文不是終止輸入);code-loop 增量=可選 `lumos loop verify-progress <id> --json` 獨立覆核結構帳。
- **子代理續談(2026-08-14 準用;★限 headless★)**:規則單源見 `../lumos-design-loop/SKILL.md`〈子代理續談〉節(環境門檻/追問補件/答辯回合/初讀禁令/拒答≠失憶);code-loop 增量=**③原 reviewer 驗修**——步驟 4 修進真碼後,可續談「發現該 finding 的那席」驗收「這個 fix 有沒有解掉你報的那條」(帶記憶免重讀 diff);★只替代「該條 finding 的針對性複審」,不替代翻紅釘證據制(先紅後綠照跑),收斂前仍派全新席掃 delta 回歸★。依據:[[Projects/子代理續談調研]]。

> ### ⚠ 一輪能丟多少:軟上限 1800 行(≈30K token)
> 門檻數字的出處(借用已發表的 32K 退化起點,本專案三次實驗都量不到規模效應)見〈歷史與停用〉裡「門檻 1800 是借用…」那段。
> **派工前先量** `wc -l <工作副本/patch>`。超過就**拆開審**——切成多輪，或拆給多席各審一段。

> **為什麼**：審查員的任務是「在 N 行裡找出那個植入的錯」，而**脈絡越長注意力越差**是已發表的實測（有效脈絡約標稱值 60–70%，**退化在 32K token 就量得到**，報告退化幅度 13.9%–85%）。

> **超標不擋**（輪已經跑完才記帳，擋也來不及），但 `canary record --scope-lines N` 會在帳上標 `scope_oversize` 並當場喊——**那一輪的「乾淨」是弱證據**：審查員可能是「看不完」而不是「沒問題」，收斂宣稱要講小。

## panel 模式與收斂判準

### 現行收斂閘=處置閘(2026-08-08 切換;這段是現行依據,歷史段另有原位留存)

> ★**2026-08-08 閘切換(取代 2026-08-04 分流註記)**★:本 skill 收斂改走**處置閘**(`loop status --disposal`,
> 與 design-loop 同制)——原「刻意分流/不得改本檔」警語與 A 案防浮動條款經 **Enzo 具名推翻**
> (signoff 留痕見 [[Projects/驗證層去模型化_計劃]];理由=canary 閘可信度被非平穩性論證動搖,條款自我引用)。
> canary 同步降**觀測**(當輪煙霧偵測器:miss 不作廢該席 findings,只記帳;判讀=漏送分題強警報/漏難題弱訊號)。
> **A 案(K=2+抽查)機制碼與 `t_panel_k2_and_probe` 保留不刪**(舊帳重放消費);舊 loop 帳不回溯。


### 平行 panel 模式(≤3 輪壓縮,2026-07-09;取代 6 輪循序,機械核心與 design-loop 共用)
機械原語 loop-agnostic,**code-loop 直接可用**(同 `lumos loop status`/`canary record`);差別只在 panel 跑的是 **diff 文字檔**、canary 是 **bug hunk**、**無 G1**(code-loop 本就 skip 引用座標)。設計見 [[loop三輪壓縮_計劃]]。

- **一輪 = 平行派 W 個多樣 reviewer**(W=`difficulty.params(tier)['panel_width']`,standard=3/high=5),各讀一份 diff 工作副本:
  - **bug canary 型別跨 slot 輪替** `[(slot) mod 4]`=邊界off-by-one / 資源未釋放 / None例外路徑 / 冪等併發(code-loop 的四型,非 design-loop 的 a/b/c/d);canary hunk 仍落**真改動集之外**、走三道防污染(步驟 2.5)。
  - **鏡頭各異**:bug/邊界 / 資源與例外 / 冪等併發 /(W>3)migration 正確性、測試種子清理。
  - **跨家族(2026-07-18 S5,取代舊「qwen 只否決」)**:tier=high 雙 Codex 角色——1 席帶餌正式 finder 佔 W(受注意力檢查,計入重疊帳)+1 席無餌否決席不佔 W(外掛;findings 與帶餌席同池進辯方,存活 ≥major 依帳模式落閘:M2=記 disputed-major cluster 記錄/舊帳=計存活 max);standard=1 席無餌否決。fail 分級:standard fail-open 退同門+註記/high fail-closed(第三家族替補→延期→外家缺席不得收斂攤人)。qwen 轉列第三家族替補。
- **spec-conformance slot(2026-07-10,調研裁定③)**:tier=high 且該分支有收斂 spec(計劃節點)→ panel **追加**一個對答案審查員(不帶 canary、不佔 W 配額,地位同 Codex 無餌否決位):輸入=收斂 spec+diff,鏡頭=**逐條款對照**「說好的做了嗎/縮水/多做/未實作」四類;縮水與未實作視同 finding 進辯方流程。無 spec 的分支跳過並記一句。派工模板見 templates.md §7.5。
- **判讀/記錄/收斂**:同 design-loop panel(步驟 4 辯方 + 步驟 5 記錄)——一輪 W 筆共享 round-id:
  `lumos canary record caught|missed --loop code-<topic> --round <rid> --auditor <鏡頭>-<模型> --severity <s> [--capture-counts "2,2,1"]`。
- **問收斂**(★2026-08-25 甲裁([[Projects/probe輪退場_計劃]] d3):多席 code-loop 亦走處置閘(彙總記帳),panel 僅供 2026-08-25 前定錨的舊迴圈回放,本段僅回放判讀用★):現行=彙總記帳問 `--disposal`;舊迴圈回放:`lumos loop status code-<topic> --gate --panel --repo <root>` → 兩條合取(輪有效[記帳席≥2,none 制] ∧ 存活max≤minor[caught+none];capture-recapture 殘餘=advisory 不進合取,2026-08-14 降級);**G1 本就對代碼 skip**,panel 模式不影響。一乾淨輪即收斂;存活≥major→fix→下一輪只重審 delta hunk,cap=3。
- **混用守衛**:`--panel` 要求本 loop 記錄全帶 round(partial-mix→rc2)。


### 異質 finder → capture_counts 的機械算法(別手數重疊)
一輪跑完,把每個 finder 找到的 finding-key(正規化成 `file:line` 或 `section:nature`)收齊,機械算重疊:
```
lumos loop capture-counts \
  --finder "app.py:12,svc.py:40"   # LLM reviewer A
  --finder "app.py:12,util.py:9"   # LLM reviewer B
  --finder "app.py:12"             # SARIF linter(pitfalls --diff 命中)
  --finder "svc.py:40"             # 測試失敗 / mutation 存活
# → capture_counts=… + 殘餘估計 + 可直接貼的 `canary record … --capture-counts <串>`
```
- 重疊計數(同洞被幾個 finder 中)是 capture-recapture 核心輸入,**人手數易錯 → 該機械化**。
- **linter 免手貼:`--from-pitfalls <range>` 一鍵收割**——`loop capture-counts --finder "<LLM A>" --finder "<LLM B>" --from-pitfalls main..HEAD --repo <root>` 會自己跑 `pitfalls --diff`、按 source 分組(每個 linter driver / pitfalls 內建各一個確定性 finder)、把命中的 `file:line` 併進來一起算重疊。手動 `--finder` 留給 LLM reviewer,確定性 finder 自動來。
- 拿到 `--capture-counts` 串 → `canary record caught --loop code-<topic> --round rN --capture-counts <串> …`;`loop status code-<topic> --gate --panel` 把它印成殘餘 advisory 觀測(不進合取);canary-stats 重疊分布段也吃它。


### 端到端一輪(照抄改參數)
```bash
# 0. 定 topic / tier / diff range
TOPIC=code-fix-billing; RANGE=main..HEAD; RID=r1
# 1. 平行派 W 個乾淨 LLM reviewer(Agent tool;Codex:spawn_agent,W=panel_width;各讀 diff 工作副本、含輪替 bug canary)
#    → 收各 reviewer 的 findings,正規化成 file:line
# 2. 算重疊(LLM 手動 --finder + linter/regex 自動 --from-pitfalls)
lumos loop capture-counts \
  --finder "billing.py:88,billing.py:120" \  # reviewer A
  --finder "billing.py:88,tax.py:12" \       # reviewer B(billing.py:88 與 A 重疊)
  --from-pitfalls "$RANGE" --repo .          # linter/regex 確定性 finder 自動收割
#    → 印 capture_counts=… 與可貼的 `--capture-counts <串>`
# 3. 記這一輪(W 筆共享同一 --round;此處示意 caught 輪)
lumos canary record caught --loop "code-$TOPIC" --round "$RID" \
  --auditor bug-sonnet --severity minor --capture-counts "2,1,1"
# 4. 問收斂
lumos loop status "code-$TOPIC" --disposal --spec "$PATCH" --repo .   # 2026-08-25 起;舊迴圈回放才用 --gate --panel。rc0=PASS → 進 finishing;rc1→修 delta 再下一輪(cap=3)
# 5. 收斂後記留痕才能 push
lumos code-loop pass --note "panel 收斂:輪有效∧無存活 major(殘餘 obs X.XX advisory)"
```


- **收斂**——★K 取決於你跑哪個模式,別記成同一個數★(2026-08-03 修:本行原本只寫「連 2 輪」,與下方 panel 節的「一乾淨輪即收斂」自相矛盾;**code 實作的是 panel 節那個**——`_loop_status_panel` 只取 `next(reversed(groups.items()))`,也就是★只看最後一輪★):
  - **循序模式**(`--need 2`,無 `--panel`):**連 2 輪**記帳乾淨(kind=none/caught 皆計)且無 blocker/major ∧ 發現枯竭
  - **panel 模式**(`--gate --panel`;★2026-08-25 甲裁([[Projects/probe輪退場_計劃]] d3):多席 code-loop 亦走處置閘(彙總記帳),panel 僅供 2026-08-25 前定錨的舊迴圈回放,本段僅回放判讀用★——tier=high 現行也改多席彙總+--disposal):回放判讀:2026-08-06 起的舊 loop=K=2+收斂後抽查判定(A案,見[[Projects/panel收斂判準改革_計劃]];抽查判定印行 2026-08-25 起降純觀測,probe-* 加開義務退場——三配套從未實作,詳 [[Issues/probe輪三參數只在散文]]);更早舊 loop 沿 K=1
  - 收斂後 → 記 `code-loop pass` 留痕 → finishing。
  - ⚠ **panel 是風險最高的路徑,判準卻最鬆**。外部案例研究(arXiv 2605.12280 §3.5)明確建議「two consecutive clean passes」當複現判準,理由是「stopping rule is a known source of **premature-termination risk on stochastic LLM auditors**」。★本專案尚未改 panel 的 K★——那動到收斂判準、屬守衛面,要另走 design-loop;此處只先把矛盾講白,不偷偷改判準。

### 平行 panel 模式(≤3 輪,取代 6 輪循序)

機械原語 loop-agnostic,直接可用;差別:跑 diff 文字檔、無 G1。

- **★編制數字單源=`lumos loop next` 吐的 roster 欄(`_TIER_ROSTER`,2026-08-18 派工編制資料化)★**——本段散文為解說,與 roster 打架時以 roster 為準;收斂時可跑 `loop status <id> --roster --repo <root>(全史回放;問閘 --disposal 偵測到席位異常會自動轉述當輪。settle 結清模式的席位對帳需手動 --roster——其記錄結構無輪次欄,自動對帳做不到,詳 Issues/settle路徑席位對帳無輪次可對)` 對帳「應派 vs 實派」(advisory 恆不影響 rc;循序 code/standard v1 不涵蓋)。
- **一輪 = 平行 W 個 reviewer**(W＝panel_width:standard 3/high 5),各讀一份工作副本:鏡頭各異(bug/資源例外/冪等併發/…)(~~canary 型別輪替/帶餌無餌之分~~已隨協議停用——全部席同規則,Codex 席照佔 W 或外掛否決)。**跨家族(2026-07-18 S5,取代舊「qwen 只否決」)**——tier=high 雙 Codex 角色:1 席**正式 finder,佔 W 之一**(findings 計入重疊帳)+1 席**否決席,不佔 W**(外掛,同 spec-conformance 慣例)。standard=1 席否決。**否決席落閘路徑**:其 findings 與帶餌席同池進辯方;存活 ≥major——M2 cluster 帳模式必須記為該輪 `<名>=disputed-major` cluster 記錄(severity 欄該模式僅顯示不裁決)/無-cluster 舊帳計入存活 max。**fail 分級**:standard=Codex 不可用退同門+留痕;**tier=high=fail-closed**——第三家族(qwen 有 cross_audit 整合;gemini 候選未驗)替補→延期→皆不可則**不得收斂攤人裁**(人可明示豁免留痕),不分金流與否。qwen 轉列第三家族替補與 finder 輪替候選。
- **spec-conformance slot**(tier=high 且有收斂 spec):追加一個對答案審查員(不佔 W、地位同 qwen),逐條款對照「做了/縮水/多做/未實作」,縮水與未實作進辯方。**含合約候選兌現**(2026-07-29):spec 計劃節點若列「合約候選清單」,逐條驗落地有沒有標 ★INVARIANT★ 綁 [test:]——該綁沒綁=縮水 finding。
- **判讀/辯方/記錄** 同循序(步驟 4-5,含可疑席 repro triage 與留痕/quote-check 慣例),一輪 W 筆共享 `--round <rid>`。
- **收斂**(★2026-08-25 甲裁([[Projects/probe輪退場_計劃]] d3):多席 code-loop 亦走處置閘(彙總記帳),panel 僅供 2026-08-25 前定錨的舊迴圈回放,本段僅回放判讀用★;現行=--disposal+code 迴圈 major 必折[d2]):舊迴圈回放:`loop status --gate --panel` 兩條合取(記帳席≥2 且 0 missed[none 制] ∧ 存活 max≤minor;capture-recapture 殘餘=advisory 觀測不進合取[2026-08-14 降級,鑑別力≈0 見 Projects/收斂閘殘餘估計降級_計劃];--min-seats/G3 帶旗標才啟用;cluster 帳=兩條合取,詳 design-loop SKILL panel 節);★**2026-08-06 起新 loop=最後兩輪各自全過(K=2)+PASS 印抽查判定**★(A案;舊 loop 沿 K=1——gate 依首筆日期自動判,不用記);存活≥major → 只重審 delta,cap=3(K=2 的第二乾淨輪計入 cap;cap 頂未湊滿照攤人)。
- capture_counts 別手數 → `lumos loop capture-counts --finder ... --from-pitfalls <range>`(自動收割 linter/regex 確定性 finder)產串。


**端到端一輪**(照抄改參數):
```bash
TOPIC=fix-billing; RANGE=main..HEAD; RID=r1   # loop id=code-$TOPIC,TOPIC 勿再帶 code- 前綴
# 1. 平行派 W 個乾淨 reviewer → 收 findings 正規化 file:line
# 2. 算重疊(LLM 手動 --finder + 確定性 finder 自動)
lumos loop capture-counts \
  --finder "billing.py:88,billing.py:120" --finder "billing.py:88,tax.py:12" \
  --from-pitfalls "$RANGE" --repo .
# 3. 記這輪(W 筆共享 --round)
lumos canary record none --loop "code-$TOPIC" --round "$RID" \
  --auditor bug-sonnet --severity minor --capture-counts "2,1,1"   # 席名慣例:<鏡頭>-<模型>
# 4. 問收斂(2026-08-25 甲裁後現行;舊迴圈回放才用 --gate --panel)
lumos loop status "code-$TOPIC" --disposal --spec <凍結patch> --repo .
# 5. 收斂後留痕才能 push
```

## mutation 與 capture-recapture

### 步驟 7 — mutation 冒煙(可選機械錨,高風險分支建議)

在隔離 worktree 對 diff 涉及模組機械植少量變異(運算子翻轉 / 邊界 ±1,3-5 個)→ 跑該模組測試 → **活下來的變異 = 測試沒接住的洞**,列為 finding 回步驟 4。
零污染:不經 reviewer、不碰真樹。

**算子速查(borrow:Offutt E-selective / PItest / Kurtz FSE 2016)**:
- 預設植 **ROR(關係算子 `<`↔`<=`↔`==`)+ LCR(邏輯連接子 `and`↔`or`)**——最防禦得住的兩類;計算密集 diff 加 AOR(算術)。**無普適最優集,跟著 diff 的代碼形態選**。
- 同一個比較式(如 `i < 42`)**非冗餘變異只有 3 個:`i <= 42`、恆 `true`、恆 `false`**——植這 3 個以外是浪費名額(PItest subsumption)。

**結果判讀(borrow:Stryker 語意)**:
- **timeout → 記 `skipped(timeout)`,不算 finding 也不算存活**(無限迴圈=CI 事實上會接住;兩派工具語意殊途同歸)。
- 活變異**分兩桶,處置不同**:**Survived**(測試跑到該行但全綠)= 斷言缺口,補斷言;**NoCoverage**(該行根本沒被執行)= 測試整個缺,**更強的 finding、優先補**。判別零成本:變異行改成 `raise` 試跑一次即知有無被執行。

誠實邊界:3-5 個手植變異是抽樣不是覆蓋;活變異=測試缺口的存在證明,死光≠測試充分;flaky 測試會汙染訊號(跑前先確認套件綠)。

---

- **mutation 冒煙(步驟 7)**在 panel 下升格為**一個確定性 finder**(不只可選旁支;不佔 canary 席,參與方式見上三通道):活變異 = 一條 finding 進 capture-recapture 池。


### 7 · mutation 冒煙(可選機械錨,高風險建議)
隔離 worktree 對 diff 模組機械植 3-5 個變異 → 跑該模組測試 → 活變異＝測試沒接住的洞,列 finding 回步驟 4。不經 reviewer、不碰真樹。
- 預設植 **ROR(`<`↔`<=`↔`==`)+ LCR(`and`↔`or`)**;計算密集加 AOR。同一比較式非冗餘變異只 3 個(`<=`、恆 true、恆 false)。
- **timeout → skipped**(不算 finding/存活)。活變異分兩桶:**Survived**(跑到但全綠)＝補斷言;**NoCoverage**(該行沒被執行)＝更強 finding、優先補(變異行改 `raise` 試跑即知)。

## 真跑優先與 UI 層驗收

**UI 層驗收(2026-08-05,MCP 接驗證層;Enzo 靈感立慣例、不綁案)**:diff 命中 UI 棧
(test-layers 宣告 layer 含「UI 驗收」)時,終審驗收=★agent 真開頁面★——用 Playwright MCP
(乾淨瀏覽器)或 claude-in-chrome(需真登入態如 LIFF)逐條執行驗收條款(真點/真填/真看),
證據=截圖+關鍵 console/network 摘要,存 `governance/review-reports/<loop-id>/ui-evidence/`
並由 Verification 節點引用。哲學同 quote-check:證據可重放,不是口頭宣稱「看起來對」。
無法起環境(lab 不在/需登入而無 session)→ 明記「UI 層未驗+原因」,不得靜默跳過。
**真跑優先(2026-07-18 S1,紀律層規則非機械閘)**:diff 經 `lumos impact --diff` 命中綁 `[test:]` 的星標合約節點時,pass 前**只跑該綁定測試**(非全套)且須綠,結果記入 pass --note——LLM 判官意見不能替代這一跑(信任階梯:真跑>機械查>LLM 判官>自報)。`[test:]` 存的是測試名非指令,解析順序=①合約節點/專案圖譜記載的完整指令 ②依該棧慣例組指令(`dotnet test --filter`/`python3 scripts/test_lumos.py -k` 等)③歧義/查無 → **不得靜默跳過**:退跑該測試檔/模組級,再不行跑全套,留痕記「解析歧義」——「解析不了所以沒跑」不構成放行理由。機械化留 v2(動 gate code 另立計劃)。

## code-loop 與 design-loop 的差異

**編排者(Claude 或 Codex)編排,lumos 出原語。** 你(主對話)用 Agent tool(Codex:spawn_agent)派 reviewer、判讀、修代碼;lumos 出 `canary record none`/`loop status` 記錄與算收斂。lumos 不 spawn agent。

design-loop 的對抗紀律(canary 驗醒著 / 辯方殺假陽性 / 證據閘收斂)1:1 搬到代碼終審,差異只在:① canary 是 bug hunk 非散文瑕疵、② G1 對代碼無意義故 skip、③ mutation 冒煙為可選機械錨補充。


### ⚠ code-loop 與 design-loop 的關鍵差異(2026-07-09 交叉查文獻;別全盤沿用)
程式碼有散文沒有的東西——**可執行 + 可靜態分析**。文獻(見 [[loop三輪壓縮_計劃]] 的 code-loop 差異節)證 code review 最佳解是**異質 ensemble**,非「多個多樣 LLM」:
1. **panel 應異質,不只多樣 LLM**(borrow:AutoSafeCoder / Multi-Agent Code Verification via Information Theory,arxiv 2511.16708——submodularity 證異質分析器各加獨立資訊)。**確定性驗證器的參與方式=三通道,不佔 canary 席、不進「輪有效」判定**(它們跑真碼樹,看不到文字 diff 副本裡的誘餌,記席必然 missed;canary 票只驗 LLM 席注意力;2026-07-18 codestage 收斂裁定):
   - (a) 其 findings 憑執行證據依辯方路由「機械證實」直接折入;
   - (b) 以**異質 finder** 進 capture-recapture 重疊帳(`loop capture-counts --finder/--from-pitfalls`);⚠ 兩套帳差異(2026-08-14 起已無):兩套帳的 capture-recapture 均 **advisory 不進合取**(無-cluster 帳 2026-08-14 降級對齊 cluster 帳);裁決權由通道 (a) 承載(機械證實 findings 進 cluster 三態帳);
   - (c) 需跑真碼的(測試套件/type checker)沿 mutation 冒煙的**隔離 worktree** 模式。
   - 具體 finder:專案 `.lumos/lint.json` 宣告的社群 linter(SARIF)/測試套件/type checker/mutation 冒煙(步驟 7)。
   - **為何**:linter/測試/type 的錯誤剖面**與 LLM 正交**(真獨立資訊),直擊「9 judge 2 票」——純 LLM panel(即使多樣)仍相關,摻確定性工具才買到真獨立訊號。
2. **辯方可執行 falsification**(borrow:Greptile TREX / CodeRabbit sandbox「grep 沒東西≠證明有 bug,先跑再信」):design-loop 辯方用 grep/Read 論證;**code-loop 辯方應能跑測試/repro/mutation 確認-或-殺一條 finding**——可執行反證 > 論證反證。lumos 已有種子:mutation 冒煙 + pre-push 測試 gate。
3. **capture-recapture 跨異質 finder**:LLM findings ∪ linter findings ∪ 測試失敗的**重疊**——LLM 與工具都指同一洞 = 更強收斂信號(且 capture-recapture 本就生於軟體檢驗,回娘家)。
4. **canary 型別、defect 分類本就不同**(已做:bug 四型 vs a/b/c/d)——文獻(PBR/defect-type mapping)證 reading technique 該隨 artifact 調;但實證 PBR 增益不穩,**重點在異質驗證器 mix 而非 LLM 鏡頭數**。
> 一句話:code-loop **繼承 panel 機制 + capture-recapture 收斂**(後者本是代碼檢驗的),但**panel 成員換成 LLM + 確定性工具的異質組合、辯方改可執行反證**——不是「design-loop 換 canary 名字」。


## 參考(需要才讀)

**出處**:抑噪兩句 borrow PR-Agent;mutation 算子 borrow Offutt E-selective / PItest / Kurtz FSE2016;Survived/NoCoverage borrow Stryker;異質 ensemble borrow AutoSafeCoder(arxiv 2511.16708)、Greptile TREX / CodeRabbit。派工模板見 `../lumos-design-loop/templates.md` §3-4/§7.5。設計全文 `docs/design/2026-07-04-pitfalls-code-loop.md`。

**code-loop ≠ design-loop 換名字**(2026-07-09 文獻;設計見 `[[loop三輪壓縮_計劃]]`):代碼可執行+可靜態分析,最佳解是**異質 ensemble** 非「多個多樣 LLM」——
- 確定性驗證器(linter SARIF/測試/type checker/mutation)**不佔 reviewer 席、不進輪有效**(2026-07-18 codestage;原因原為「跑真碼樹看不到餌」——植入雖停用,不佔席照舊:它們的產出走機械通道,不是席報告);參與三通道=(a) findings 憑執行證據機械證實折入 (b) 異質 finder 進 capture-recapture 帳(⚠ M2 cluster 帳下 advisory 不進合取,裁決權歸通道 a)(c) 跑真碼沿隔離 worktree 模式。錯誤剖面與 LLM 正交,才買到真獨立訊號、破「9 judge 2 票」。
- 辯方用**可執行 falsification**(跑測試/repro/mutation 確認或殺一條 finding)> 論證反證。

## 歷史與停用(舊頭版全文;只供回放舊帳判讀,不是現行規則)

**Claude 編排,lumos 出原語**:你用 Agent tool 派 reviewer、判讀、修碼;lumos 記錄與算收斂,不 spawn agent。機制與 design-loop 1:1,差異=無 G1、mutation 冒煙為機械錨。


以下整段搬自本檔各處已標「⛔ 已停用/已撤回/某日修正」的純歷史內容,只供回放舊帳判讀,不是現行規則。

> ⛔ **canary 協議已於 2026-08-14 停用**(Enzo 裁;單源=Systems/canary-audit d5 與 SKILL.md 頁頂告示)。本檔 canary 相關段(植入/判定/missed 懲罰)**僅供回放歷史帳判讀**;每輪記帳改 `canary record none`。

# 舊頭版全文(2026-08-22 從 SKILL.md 搬入;含全部歷史註記與修正——頭版只留一頁手冊)

# lumos-code-loop:分支終審前的對抗代碼審 loop

> ## ⛔ canary 協議已停用(2026-08-14,Enzo 裁;單源=圖譜 Systems/canary-audit d5 + `../lumos-design-loop/SKILL.md` 頁頂告示)
>
> 植入/判定/漏抓懲罰停止;每輪記帳改 `lumos canary record none ...`(純處置帳載體,severity/findings/disposal 欄照記);panel 輪有效=記帳席 ≥2 且零 missed。下文殘留的 canary 步驟=歷史帳判讀用,不再執行。

### 步驟 2 — 植 bug canary hunk(只進工作副本)

在 `/tmp/code-<topic>-rN.patch` 的 Diff 段插入一段帶合法 `@@` 標頭的偽 hunk + 唯一 token 註解。

**類型輪替 `[(N−1) mod 4]`**:

| N 值 | (N−1) mod 4 | 類型 | 典型形態 |
|------|------------|------|----------|
| N=1 | 0 (a) | 邊界 / off-by-one | `< N` 改 `<= N`、索引越界一格 |
| N=2 | 1 (b) | 資源未釋放 / 鎖漏 | `lock.acquire()` 無對應 `release`、`open()` 無 `with` |
| N=3 | 2 (c) | None / 例外路徑未接 | 呼叫回傳值未判 None、例外吃掉不上報 |
| N=4 | 3 (d) | 冪等 / 併發破壞 | `SELECT` 後 `INSERT` 無交易包裹、TOCTOU |

canary 要「認真審就抓得到、但不一眼看穿」——太細=不公平、太明顯=訊號弱(校準鐵則,同 design-loop)。
**生成硬化三條(載重錨定/haiku 難度探針/事故反轉)與 reviewer 結構紀律(禁互辯/meta-judge/≥3 run 多數決)同 design-loop SKILL——單源在該檔對應節,code-loop 適配:載重錨定=bug canary 植在 diff 主題的核心邏輯型別、事故反轉查 pitfall_when 命中被改檔。不在此雙寫(防散落漂移)。


### 步驟 2.5 — 三道防污染(不可違反)

**① 真代碼永不含**
canary 只存在於 package 工作副本(`/tmp/…-rN.patch`)。折入真 finding 時每個 fix commit 必須錨到**真 diff 的 file:line**(canary hunk 的位置不在真 diff,想折也對不上座標)。

**② 低耦合植入**
canary hunk 的 file:line 必須落在**真改動集之外**(合成新 hunk 於未被真 diff 觸及的檔/函數),且與真改動弱耦合,縮小衍生推理波及面。
載體明定:reviewer 讀的是 diff 文字檔(`git diff -U10` 產)的工作副本;植入 = 在其 Diff 段插入帶合法 `@@` 標頭的偽 hunk + token 註解。
座標權威 = package 的 `-U10` 檔(pitfalls `--diff` 預設 `-U3`,兩者 `@@` 位移不同;pillar 判定為檔級,行級引用以 package 檔為準)。

**③ 溯源排除**
判讀時,任何 finding 的推理鏈引用 canary hunk 的 file:line、或依賴其語意(含間接聯想幻影:未顯式引用 canary file:line、僅因鄰接 canary 而聯想到真碼風險者)→ **連同 canary 一併排除、不折、不計 findings**。排本體也排影子。
排除方向偏「多排」(寧可少折不污染);殘餘=真 finding 被誤排的假陰性,由下一輪重挖兜底。折入端另有機械錨兜底:fix 必錨真 diff 座標 + 辯方 file:line 反證。

---

**① canary 判讀**

> (此處 5 行與〈現行收斂閘=處置閘(2026-08-08 切換;這段是現行依據,歷史段另有原位留存)〉完全相同,已去重;正本在那裡。)

> ### ⤵ 完整權威版在 `reference.md`（本 skill 目錄下,原 253 行逐字保存）
> 本頭版是精實操作核心;**深度細節/文獻/完整範例撞到就先 `Read` reference.md 對應段**,別只憑摘要硬幹:
>
> | 你正要做 | Read reference.md 的 |
> |---|---|
> | reviewer 結構紀律(禁互辯/meta-judge/≥3 run 多數決);~~植 canary 生成硬化~~(歷史帳判讀用) | 步驟 2 + panel 節 |
> | 想懂抑噪為何**不設 findings 上限**(PR-Agent `num_max_findings=3` 的取捨)、辯方順產 fix 細節 | 步驟 3-4 |
> | mutation 算子完整理由(Offutt/PItest/Stryker E-selective)、或 **code-loop≠design-loop** 的異質 ensemble 文獻論證 | 步驟 7 + 「差異」節 |
> | capture-recapture 機械算法完整範例、端到端指令 | panel 節 |
>
> **拿不準就 Read**——漏翻深規的代價 > 多讀一次。

> ★這條門檻純粹借自外部文獻——本專案自己的資料★不支持★它，別拿來當佐證★（2026-08-02 更正）。原本這裡寫的是「本專案資料落在線的兩邊」（`code-slim-python` r1/r2 大 payload 零 findings vs r3–r6 小 payload 有 findings），★那個宣稱已撤★：查證後兩組**審的根本不是同一份碼**（前者 bash→Python 移植，後者後來才寫的 manifest 步驟），拿來比不構成證據。★這條規則的理由★**只掛在上面那份已發表的實測**（有效脈絡 60–70%、32K 起退化）。★本專案跑過**三次**對照實驗，**都沒能重現規模效應**★——實驗一（同材料拆三段 vs 各看完整）主要指標 B(4) < C(5)，見 [[Projects/審查規模對照實驗]]；實驗二用 **Landmark 上線後才發現的真缺陷**當針、**同一根針不同大小草堆**、實驗 repo 只有一個 commit（沒有未來可翻），結果 **S 組 3/3、L 組 3/3，命中率完全沒有隨規模下降**，見 [[Projects/審查規模對照實驗二_Landmark真缺陷]]。**所以不要拿本專案的資料當支持證據。** ★實驗三（2026-08-02，難針＋強制逐檔裁決，S 4.3K vs L 41K token）同樣不支持★：六席**全滅**（0/6 偵測到），而主要指標「偽陰性斷言」**方向與預測相反**（S 3/3、L 1/3），且該指標被發現與「每項作答長度」糾纏（S 審 4 檔、L 審 40 檔，逐檔裁決每列自然變短）。★三次的難度都沒校準好★：實驗二天花板（7/7）、實驗三地板（0/6）——**再測之前要先有能力把針調到 30–70% 命中率的區間，否則是燒錢**。★裁定：停止在這條線上投資，收斂閘不動★，見 [[Projects/規模影響判斷力假說]]。保留這條上限是因為外部證據仍在、且多切一輪的代價遠小於漏一個 blocker。

> (此段支撐現行〈席位紀律與抑噪〉的 1800 行軟上限,規則仍生效,以下只是數字出處與實驗考古。)
> 門檻 1800 是**借用已發表的 32K 起點取略保守整數，不是本專案量出來的**。★兩次實驗反而浮出另一個假說★：量大影響的可能不是「有沒有看到」而是**判斷的自信度**——大 payload 的席位會**有把握地宣稱有缺陷的地方沒問題**（3/3 大 payload 席位講反、1/1 小 payload 席位找到，見 [[Projects/規模影響判斷力假說]]）。★該假說 n=4、觀察性、編碼者＝提出者，maker≠checker 未閉合，**不得據以動 gate**★；要動得先有一個為它設計的對照實驗，而且需要「會被漏掉的難針」（實驗二 7/7 全中＝天花板效應，測不出差別）。

### 步驟細節

- ~~canary 判定抽樣分權~~ **⛔ 已停用**(隨協議停用;`canary second` 封存)。

~~missed 懲罰~~ ⛔ 已停用(無植入即無漏抓;歷史帳回放照舊制判讀)。

### 舊章節標題(原文逐字保留,內容已併入前面各章)

### 每一輪 N(照做,步驟 1-7)

### 誠實天花板(收斂後務必向人提醒)

### 收斂後

### 護欄 · 天花板 · 收斂後

---

