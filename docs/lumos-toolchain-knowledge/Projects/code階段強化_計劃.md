---
type: project
status: doing
created: 2026-07-18
updated: 2026-07-18
tags:
  - type/project
  - status/doing
related:
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Systems/design-loop]]"
  - "[[Systems/linter精選目錄]]"
summary: |-
  KEY:code 階段三腿補強(呼應 design-loop d4 定位裁定:正確性歸下游,下游要配得上)——正確性/品質兩腿尚可,性能腿近空(pitfalls 只有 regex 提示,從未真量);2026 業界共識=審查從「用讀的」轉「用跑的」(agentic testing/execution-based verification)
  KEY:[S1]真跑優先(紀律層規則,r1 折入後誠實降級)——(a)diff 經 `lumos impact --diff` 命中綁 [test:] 的星標合約節點時,放行前**只跑該綁定測試**(非全套)且須綠;此為紀律層規則非機械閘(同「硬閘是紀律非技術鎖」家規),機械化=動 gate code 記 v2 另立計劃 (b)確定性驗證器(真跑測試/type checker/mutation)**不佔 canary 席不進輪有效**;參與方式=findings 依機械證實路由折入+以異質 finder 進 capture-recapture 帳(既有 `loop capture-counts` 原語);跑真碼樹沿 mutation 隔離 worktree 模式
  KEY:[S2]查詢數斷言(消費端樣式)——「操作 X 最多 N 條查詢」寫成整合測試斷言,N+1 即紅;**落點=LandmarkMember 自己的圖譜節點**(框架特定歸專案圖譜,csharp-idioms 明文不裁框架、不落 Dapper 代碼;r1 blocker 折入),本圖譜只留框架無關原則一句於 linter精選目錄
  KEY:[S3]性質測試席(選配,r1 大修)——開席雙機械錨:tier=high ∧ impact --diff 命中星標合約節點的純函式模組(非編排者自由心證),預設關+開席理由留痕;產出:反例可重現性免爭,**性質合法性必過辯方**(辯方專問「這條性質真是該函式的業務合約嗎」,對文件/圖譜合約/呼叫端查證;高分=進辯方資格非免審,低分丟);金流級另掛 signoff 既有慣例
  KEY:[S4]持續基準測試=不做(non-goal)——拒收理由立足工程成本(穩定硬體壓噪音);誠實缺口:CPU-bound/記憶體退化在 code 階段零覆蓋,S2 只接查詢數這一種訊號(第一根拐杖非補齊);線上分桶告警=消費端建議待辦**非既存安全網**(r1 折入:原文誤植為已存在)
  KEY:[S5]跨家族比重提升(使用者指示 2026-07-18)——①辯方預設 Codex(判決單點最怕同門盲點;不可用退 opus 並註記)②tier=high 開雙 Codex 角色:1 帶餌正式 finder 席(受注意力檢查,計入重疊帳)+1 無餌否決/對答案席(保底外家聲音);standard ≥1 席③關鍵單點 ≥3-run 多數決至少 1 run Codex④真加軸=引入第三家族(qwen/gemini)輪替,記方向不急做
  KEY:範圍刀——S1 改兩份 skill 文字(紀律層);S2 樣式歸消費端圖譜;S3/S5 是編排規格;零新 lumos 原語;全部加在 code/驗證階段,spec 階段零加重(d4 合規)
  DEP:[[Systems/pitfalls-code-loop]]
  DECISION:[2026-07-18]S4 拒收記理由防重提;S3 觸發雙機械錨收窄(r1 折入,原「編排者判純邏輯」防濫開太弱);S3 免辯方路由撤除(r1 四方共指:自評分=自報級信號不得做免辯方級動作)
---
# code階段強化_計劃——正確性/品質/性能三腿補強(鏡頭在 code 階段)

> **緣起**:design-loop d4 裁定「正確性歸下游」後,使用者要求鏡頭轉向 code 階段:搜業界更全面提升正確性/品質/消除 bad performance 的做法。2026-07-18 搜證(來源見文末)。r1 對抗審計(3 帶餌席+Codex 否決席)折入七組修正,見〈審計修正紀錄〉。

PRIOR-ART: ① 最小解層級——S1 改既有 skill 文字(紀律層)、S2 是消費端圖譜樣式文檔、S3/S5 是既有 panel 的編排規格;零新 lumos 原語。② 世界解過——S1=agentic testing 2026 共識;S2=Rails bullet/prosopite 查詢數斷言路線;S3=Anthropic property-based testing 配方(2026-07,984 報告實測 56%→86%);S5=異質 ensemble 文獻既有方向的比重調整;S4=Bencher 持續基準(拒收)。③ 裁定=borrow-design 全線。

## [S1] 真跑優先(正確性;紀律層規則,改 skill 文字)

**現況**:code-loop 收斂由 LLM 判官數 finding 決定;真跑測試只是實作階段習慣,終審層面無明文地位。

**改動**(兩份 skill 文字;**紀律層規則,非機械閘**——同「硬閘是紀律非技術鎖」家規,誠實聲明):
1. `skills/lumos-code-loop/SKILL.md` 收斂節加規則:**「觸碰合約」的判定依據=`lumos impact --diff` 命中綁 `[test:]` 的 ★INVARIANT★ 節點**(沿用既有 min_score 門檻機制,非檔案級粗判——單檔如 scripts/lumos 綁 6+ 合約,檔案級會誤傷 docstring 小改)。命中時,放行前**只跑該綁定測試**(非全套,成本=單測試一跑)且須綠;跑過與結果**記入 `code-loop pass --note`**(留痕可稽核)。LLM 判官意見不能替代這一跑(信任階梯:真跑 > 機械查 > LLM 判官 > 自報)。**機械化**(code-loop check 讀綁定並驗執行結果)=動 gate code,記 v2 另立計劃,本計劃不做。
2. panel 節明文確定性驗證器的參與方式:**不佔 canary 席、不進「輪有效」判定**(它們跑真碼樹,看不到文字 diff 副本裡的誘餌,記席必然 missed;canary 票只驗 LLM 席注意力)。參與三通道:(a) 其 findings 依辯方路由「機械證實」直接折入 (b) 以**異質 finder** 進 capture-recapture 重疊帳(既有 `lumos loop capture-counts --finder/--from-pitfalls` 原語,零新機制) (c) 需跑真碼的(測試套件/type checker)沿 mutation 冒煙既有的**隔離 worktree** 模式。刪除任何「同權重投票」措辭——收斂判定的數學(三條合取/cluster 帳)不變。

**測試策略**:純 prompt/紀律層無單元測;以下次真實 code-loop 跑一遍驗流程可執行(同 finding-refute 前例)。

## [S2] 查詢數斷言(性能;消費端樣式)

**現況**:性能腿近空——pitfalls 對 N+1 只有單行 regex 提示,從未有機制真的量過查詢行為。

**改動**(r1 blocker 折入:落點改歸消費端):
1. **樣式主體落 LandmarkMember 自己的圖譜**(Systems 節點):「會數查詢的連線包裝」——測試組件裡包 `IDbConnection` 攔 `Execute*/Query*` 計數 + 斷言範例:`載入 50 筆訂單清單 → 查詢數 ≤ 3`。N+1 出現時 3→51 直接紅。查詢數上限以**該專案實測值+緩衝**訂,硬編碼於各測試(顯式可審),不引入新宣告檔。
2. 本圖譜只在 [[Systems/linter精選目錄]] 補一句**框架無關原則**:「操作級性能可翻譯成確定性測試斷言(查詢數/呼叫數上限),優先於監控與基準」——不含任何 Dapper 代碼。
3. **csharp-idioms 不動**——該 skill 三處明文「框架選擇不在此裁,歸專案圖譜」,Dapper 專屬樣式進去會被其審查鏡頭套到所有 C# 專案(含 EF Core 者)產生誤導 finding(r1 s3-blocker)。
4. LandmarkMember 首用掛該專案待辦,非本計劃交付。

**為什麼是斷言不是監控**:把性能翻譯成**確定性測試**=信任階梯最高階;免基準環境、免統計、CI 直接跑。

**測試策略**:首用時以「故意引入 N+1 → 斷言翻紅」負向驗證(同 lint-check 驗收慣例)。

## [S3] 性質測試席(正確性;code-loop 選配席,r1 大修)

**現況與舊帳**:07-15 圖譜判「自動生成 property 測試 oracle 不可靠」(agent 自己發明錯誤期望→誤報)。Anthropic 2026-07 配方:推導性質(從文件/型別)→寫 PBT→真跑→自我篩選→評分過濾→**高分交人審**,實測 56%→86%。**r1 四方共指**(Codex+s1+s3):反例只證「代碼≠生成的性質」,哪邊錯正是 oracle 問題;自評分=自報級信號(S1 階梯最低級),不得做「免辯方」這個最高信任動作。

**改動**(code-loop 選配席編排規格):
- **觸發(雙機械錨,r1 收窄)**:①tier=high **且** ②`lumos impact --diff` 命中綁 ★INVARIANT★ 合約節點**且**該 diff 觸及的函式為純函式(無 IO;編排者核,但候選集已被②機械收窄)。**預設關**;開席須在收斂留痕記開席理由。防濫開:tier=high 門檻低(任一 regex 命中即成立),故②是主閘。
- **流程**:席位 agent 讀 diff 涉及的純邏輯函式+文件/型別註解 → 推導 2-3 條性質(從文件推導,禁憑空)→ 該棧 PBT 框架寫測試(C#=CsCheck/Kotlin=kotest-property/JS=fast-check/Py=Hypothesis)→ 真跑數百案例(固定 seed,反例可重現)→ 自我篩選(排除測試自己寫錯)→ 自評分(性質來源可靠度/可重現/影響面)。
- **產出(r1 撤免辯方)**:反例的**可重現性**免爭(那是機械事實);性質的**合法性必過辯方**——辯方(依 S5 預設 Codex)專問:「這條性質真是該函式的業務合約嗎?」對文件、圖譜 ★INVARIANT★、呼叫端行為查證。**高分=取得進辯方資格,非免審**;低分直接丟(防噪音)。辯方維持→折入;辯方駁倒→丟棄並記「性質推導誤」。金流級 finding 折入後另掛 `lumos signoff` 既有慣例(對業務的人確認)。
- **成本上限**:單席、跑一次、cap 數百案例;不收斂不重跑(加菜非主菜)。

**測試策略**:編排規格無單元測;首用挑真實高風險 diff 驗端到端,結果記 Verification。

## [S4] 持續基準測試——不做(non-goal,拒收記理由)

拒收理由立足工程成本:需穩定硬體環境壓噪音(change-point 偵測才有意義),重;lumos 自身是 CLI 無熱路徑。**誠實缺口(r1 折入,不得誇大覆蓋)**:S2 只接「查詢數」這一種性能訊號——CPU-bound 演算法退化、記憶體洩漏、快取失效在 code 階段**零覆蓋**;線上響應分桶告警是**消費端建議待辦,目前並不存在**(原文誤植為既存安全網,已更正)。故性能腿定位=「補上第一根拐杖」非「補齊」;S2 用起來後仍有缺口再議 S4(屆時評 Bencher 類自架)。記此防日報/自主 loop 重提。

## [S5] 跨家族比重提升(使用者指示 2026-07-18)

**動機**:r1 實證——Codex 單席貢獻 3 條真 major(同權票落點/紙上硬閘/免辯方缺口),外家視角價值已證。但**兩個 Codex 彼此同門**,純加席邊際遞減;正確加碼=讓外家出現在更多**關鍵角色**,非堆同款席。

**改動**(兩份 loop skill 的 panel/辯方節):
1. **辯方預設 Codex**:低共識 findings 開庭時辯方由 Codex 擔任(乾淨脈絡、不傳審計結論;`codex exec --sandbox read-only`)——判決單點最怕同門盲點,外家反證價值最高。Codex 不可用退 opus 並於留痕註記偏離(fail-open 同跨家族既有慣例)。
2. **雙 Codex 角色(tier=high)**:1 席**帶餌正式 finder**(拿自己的帶餌工作副本,與 LLM 席同規則受注意力檢查,findings 計入重疊帳)+1 席**無餌否決/對答案席**(即使 finder 席漏抓被作廢,外家聲音不斷線)。standard ≥1 席(否決席)。
3. **關鍵單點判決 ≥3-run 多數決**(cap 攤牌前最後裁定/blocker 級爭議):至少 1 run 用 Codex(既有結構紀律的明文落實)。
4. **真加軸=第三家族**:qwen/gemini CLI 可用時輪替進 finder 席;記方向不急做。

**測試策略**:編排規格無單元測;本計劃 r2 復審即首個實戰樣本(辯方若開庭即用 Codex)。

## 實務隱患

- **效能**:S2 計數包裝只存在測試組件,不進 prod 路徑。S3 席跑數百案例有時間成本→雙機械錨+預設關+單席 cap。S5 Codex 席增加外部 CLI 呼叫次數(分鐘級/席),tier=high 才雙席。
- **併發**:無——S1/S3/S5 為編排文字;S2 計數包裝單測試進程內,無共享狀態。
- **冪等**:S3 固定 seed 記反例(可重現最小案例為產出物),避免 flaky 反例進判讀。
- **資源**:S3 席一次性 agent 無常駐;PBT 框架屬消費專案 dev 依賴,不進 lumos(零依賴家規不破)。Codex 呼叫受本機 quota 限制,fail-open 退同門。

## 誠實天花板

- S1 是**紀律層非機械閘**:審計員漏判合約關聯或直接留 pass,pre-push 仍放行——關「忘了」不關「刻意繞」;機械化留 v2。
- S1 觸碰判定依賴 impact --diff 的 min_score 門檻——門檻漏判=該跑沒跑,屬已知漏網面(逃逸帳接)。
- S2 查詢數上限人訂:太鬆抓不到退化、太緊變 flaky;首用實測值+緩衝,調整靠回歸經驗。性能覆蓋僅查詢數一維(見 S4 誠實缺口)。
- S3 即使性質過辯方,辯方對「文件本身過時」也可能雙雙誤判——低分丟棄的假陰性+辯方誤放的假陽性都歸逃逸帳;定位是加菜非兜底。
- S5 兩個 Codex 席彼此同門,邊際遞減誠實聲明;真獨立軸要等第三家族。
- 全計劃不含線上/prod 層性能網(監控告警歸消費端 ops,且目前不存在,見 S4)。

## 審計修正紀錄

- **r1(2026-07-18,3 帶餌席+Codex 否決席;3/3 caught 0 missed,存活 max=blocker)**:
  1. [Codex+s3] S1(b)「同權重投票」無機械落點(確定性驗證器看不到文字 diff 誘餌,記席必 missed;gate 數學無投票語意)→ 改三通道參與(機械證實折入/capture-recapture 異質 finder/隔離 worktree),刪同權重措辭。
  2. [Codex+s2] S1(a)「真跑綠才放行」原文=紙上硬閘+觸碰粒度未定義 → 誠實降級紀律層+指名 impact --diff 為判定依據+只跑綁定測試+留痕;機械化記 v2。
  3. [Codex+s1+s3 四方共指] S3 高分反例免辯方=自報級信號做免辯方級動作,Anthropic 配方「高分交人審」被偷換 → 撤免辯方:性質合法性必過辯方(預設 Codex),金流級另掛 signoff。
  4. [s2] S3 觸發「編排者判純邏輯」防濫開太弱(tier=high 門檻低)→ 雙機械錨(impact 命中合約節點為主閘)+預設關+開席理由留痕。
  5. [s3, blocker] S2 落點撞 csharp-idioms 明文邊界(不裁框架/審查鏡頭會套到所有 C# 專案)→ 樣式主體改歸 LandmarkMember 專案圖譜,idioms 不動,本圖譜只留框架無關原則一句。
  6. [s2] S4 拒收理由引用不存在的「線上分桶告警」+「性能腿補齊」誇大 → 更正為消費端建議待辦+「第一根拐杖」定位+CPU/記憶體缺口誠實記載。
  7. [使用者指示] 新增 S5 跨家族比重提升(辯方預設 Codex/雙 Codex 角色/≥3-run 含 Codex/第三家族方向)。

## 落地順序

S1(改文字)→ S5(改文字,與 S1 同波)→ S2 樣式(歸 LandmarkMember 圖譜,該專案下次動手時)→ S3 規格(寫進 SKILL,首用等真實高風險 diff)→ S4 不做。落地 Verification 以 `plan_refs` 回指本節點。

## 來源(2026-07-18 搜證)

- Anthropic《Finding bugs with Claude and property-based testing》(2026-07)——S3 配方與 56%→86% 實測
- Rails bullet/prosopite 查詢數斷言路線——S2 樣式原型
- Bencher 持續基準測試——S4 評估後拒收
- Tricentis/12thWonder 2026 agentic testing 盤點——S1「用跑的取代用讀的」共識
