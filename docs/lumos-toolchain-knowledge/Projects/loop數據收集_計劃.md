---
type: project
status: doing
created: 2026-07-16
updated: 2026-08-31
tags:
  - type/project
  - status/doing
related:
  - "[[Projects/design-loop提效_計劃]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Systems/canary-audit]]"
  - "[[Systems/autonomous-iteration-loop]]"
summary: |-
  FLAG:DECISION
  KEY:問題=loop 真實跑一次產生的資訊(輪數曲線/canary 型別命中/席位 missed 軸/辯方開庭/逃逸)散落且部分蒸發——判「最佳收斂方式」需要這本帳。實測盤點(2026-07-16):六 repo 共 ~61 loops/17 golden——toolchain 24+11/LandmarkMember 24+5/mOrangePos 11+0/Citrus_KDS 1+1/CompassKiosk 1+0;唯一活流失=自主日報 loop 的 /tmp 工作區事件流(corrosion-gauge 7 輪 K=3 只剩 golden 散文)
  KEY:★混淆★語料橫跨四五代協議(循序→panel 07-09→canary 硬化 07-10→M1 提效 07-16→M2 cluster 帳 07-16)——跨代混池=體溫計加溫度計;但版本更迭同時是 treatment variable(天然準實驗):跨代比較(panel 省輪?M1 辯方歸零?)可做,代內調參(每層 n=10-15)樣本不足
  KEY:replay 校準不受版本污染——golden 凍 spec+已知 findings(近似 ground truth 標籤),重跑審計算接住率與產出協議代無關;17 份遠超 10+ 門檻,隨時可跑 baseline
  KEY:逃逸帳=唯一能校準停止決策的標尺——「收斂好不好」ground truth 是下游抓到多少設計期漏的(實例:fromscratch 收斂後 code review 抓 token 消毒 blocker;M2 收斂後 code-loop 抓 Codex 3 洞);現只在散文,無機械歸因
  KEY:[2026-07-22 日報吸收]逃逸帳方向外部獨立背書——Meta-Engineering Harnesses(arXiv 2605.25665,小團隊獨立做出「合約+角色分工+對抗驗證」幾乎 lumos 翻版)多做一件 lumos 缺的:把失誤歸類回頭校準把關器(付費金流案例=合約沒寫全/驗證邊界有洞被歸類後修 gate)。**吸收=記錄半(失誤分類+攢+看哪類一直漏,補 canary「戰績帳誰抓到」缺的另一半「失誤帳誰一直漏」)值得做、即 escape record/promote([[Projects/全盤外審2026-07_調研]] finding5);自動調參半(自動改 difficulty 關鍵詞/tier 門檻)仍守本節點 DECISION「先累後校準順序不可倒」+risk-tiered 誠實天花板(tier 按類別非難度),應 advisory 浮「X 類一直漏」→人裁改 gate(改 gate=self-governance=high 本就人裁)。天花板:靠漏網被下游抓+回報+歸類,GIGO 同 cluster 分類**
  KEY:★北極星★[2026-07-17 外部評審吸收,見[[Projects/GPT外部評審吸收_計劃]]]——「流程是否讓正常改動變快,而不只讓錯誤改動變困難」:只防錯但人人想繞的流程終被繞過;效率軸(需求→合併時間/每有效 finding 成本/誤擋耗時)與品質軸(逃逸帳)並列,提效工作(M1/三輪壓縮)以此錨定
  KEY:[2026-07-26 同篇再吸收]arXiv 2605.25665 於 07-26 日報再現(標題換說法,日報 dedup 按標題沒擋同 id——**根因已挖到底並修 2026-07-26**:①真兇非比對力、是「發送成功才記帳」——配額死亡期 07-21~23 的調研全沒進去重帳,同篇自然重現;已解耦為產出即記②歷史帳曾雙檔分裂(舊位置孤本存 06-10~19+誤補的 07-24),已併入 reports/ 單一真相源並 git rm 舊檔③加碼機械 id 黑名單注入 prompt(抽 89 id,同篇=同 arXiv id 硬規則),去重不再只靠模型比標題);本次新料=它的實戰報告有「對抗審多抓到、一般測試漏掉的缺陷數」欄——lumos 整套對抗機關(canary/辯方/跨家族)跑一個月無任何數字證明比普通審多接住什麼。**吸收=增量價值帳:lumos gov 的 canary 分帳加「折入缺陷」欄(sum findings by auditor+severity;折入定義=測試綠後仍被對抗層抓到的真缺陷,天生就是『測試漏掉的』);長期趨零=機關裝飾品該砍——這是驗證層對自己的驗證,合 v1 先累帳哲學(只計數不調參)**。自主側 confidence report 加同欄=待辦(autonomous loop 目前 dry-run,落地時一併)
  DECISION:v1 不做統計模型/dashboard/自動調參(代內 n 不足,先累後校準順序不可倒);只做「訊號機械化+歸因」四件:自主 loop 歸檔/逃逸帳/epoch 蓋章/分層 stats
  DEP:[[Systems/loop-convergence-recording]]｜[[Systems/autonomous-iteration-loop]]
verified_by:
  - "[[Verification/2026-07-16_replay校準baseline_v0]]"
decisions:
  - content: M2 切片「席報告引圖譜率」先行:讀側純觀測掛 gov --stats,d8 前後兩桶分層;近親兩案(送審前impact/impact鏡頭機械化)裁死的是派工端機械強制,本切片不閘不碰寫入路徑,不衝突;light 分級(讀側只印字,流程自產工作量 Issue 批評過不成比例)
    id: d1
    decided: 2026-08-30
    valid: true
  - content: M2 切片「席報告引圖譜率」裁定不建常設:std r1 五席 3 blocker(構念效度反轉 31.2%→9.5%=貼進派工詞後不需引路徑/oracle 造不出唯一/算術快照不成立);縮案=一次性內容級盤點(外家反提案)+重開三條件;帳與證據見切片節與 governance/review-reports/graph-usage-stat-std/
    id: d2
    decided: 2026-08-30
    valid: true
  - content: 飛輪量測雙帳落地(Enzo 2026-08-31 裁做):①攔截帳=★圖譜攔截★零工具記號慣例+種子三筆回填 ②逃逸帳=loop escape 原語(M1②,append-only+歸因守衛,7 測+突變驗)——依本計劃 d0 時代明文「M1 皆 append 級單 reviewer」免設計審,過代碼審推線;季度三數字=攔截站位/逃逸數/使用率基線
    id: d3
    decided: 2026-08-31
    valid: true
---
# loop數據收集_計劃

> **狀態**：ideation 收成（2026-07-16，與人共同盤點），尚未 design-loop、尚未實作。緣起：使用者問「每次真實跑 loop 能不能累積數據供後續判斷最佳收斂方式」。

## 盤點（2026-07-16 實查六 repo）

| repo | loops | golden | 備註 |
|---|---|---|---|
| lumos-toolchain | 24 | 11 | 手動線全留存;**自主日報 loop 在 /tmp 工作區,事件流蒸發**（corrosion-gauge 7 輪 K=3 僅剩 golden 散文摘要）|
| LandmarkMember | 24 | 5 | 真業務語料（金流/票券/點數）,留存完整——與 toolchain 自指型 spec 是兩種難度剖面,正是「哪類 spec 用哪種收斂」的對照組 |
| mOrangePos | 11 | 0 | 06-22~06-25 era,早於 golden 慣例——事件流在、golden 缺 |
| Citrus_KDS | 1 | 1 | |
| CompassKiosk | 1 | 0 | |
| **計** | **~61** | **17** | |

## 兩個釘死的方法論前提

1. **協議代次是一等變數**（使用者點出的混淆）：語料橫跨 循序(≤07-09)→panel(07-09)→canary 生成硬化(07-10)→M1 提效(07-16)→M2 cluster 帳(07-16) 四五代。分析**一律分層嚴禁混池**;跨代比較是價值（treatment variable、天然準實驗）,代內調參是陷阱（n=10-15/層）。epoch 表可從 skill 的 git commit 史機械回溯,拿 loop ts 蓋章,不碰散文。
2. **逃逸帳是 ground truth**：收斂決策對不對,由下游（code-loop/實作/prod）抓到的可歸因缺陷裁決,不由 loop 自己的殘餘估計裁決。

## 里程碑

- **M1（堵流失+建標尺）**：①自主 loop 事件流歸檔——收斂/達 cap 時把 /tmp 工作區 canary-log 整檔搬回 repo（零判斷純搬運,同 golden 慣例）②`lumos loop escape` 原語——下游發現可歸因缺陷時記一筆（loop-id/發現階段/嚴重度/描述）,append-only ③epoch 表回溯蓋章（機械,一次性）。
- **M2（讀取器+新欄）**：①跨 repo 分層 `loop stats`（多 vault 來源,按 epoch 分組輸出:輪數曲線/caught-rate by canary 型別/席位 missed 軸/辯方開庭數/逃逸率）②新記錄結構化欄:`--protocol`/`--canary-type`/`--probe`(現埋於 note 散文,regex 撈不可靠)。★2026-08-30 註:canary 協議 08-14 已停用(record none 制),M2 的 canary 型別/caught-rate 各項需按新制重寫再實作,本切片不動它們★。
- **獨立實驗**：replay 校準。✅ **baseline v0 已跑（2026-07-16,[[Verification/2026-07-16_replay校準baseline_v0]]）**——2 spec×2 模型×釘住/未釘 8 席;三結論(haiku 只配機械清單/單席 sonnet 首輪廣度驚人=多輪價值在折入迴歸/洩漏效應分層)+**三鐵則:受試用 git 史前折 v1、repo 釘同期 worktree、prompt 明示提案語意**——三條缺一分數即污染。擴大跑(更多 golden/加 opus)按需。

## M2 切片:席報告引圖譜率——★裁定不建常設指標★(2026-08-30;light r1 一席 1 blocker+4 major→ratchet 升級 std,std r1 五席 3 blocker 全折後縮案)

**這節現在是「為什麼不做」的正式紀錄**(同 [[Projects/impact鏡頭機械化_計劃]] 形態;要重開先讀完本節)。

**原構想**:讀側掃審查席報告數圖譜節點引用,d8 前後兩桶對照,掛 gov --stats。**std r1 五席(機械定義/資料現實/合約/架構/外家否決)判死,三層同時不成立**:

1. **構念效度反轉(外家實測)**:照字面口徑,前桶字串命中 31.2%→後桶 9.5%——**d8 之後圖譜內容直接貼進派工詞,席位不再需要引節點路徑**;字串型指標與真使用可能反相關,量出來的下降恰恰可能是機制生效的證據。
2. **抽取定義造不出唯一 oracle(機械席)**:bash `[[ 條件 ]]` 語法被當 wiki 連結(code-loop 報告貼腳本是常態,兩份 0 引用報告被算成有);lint 測試夾具的假路徑(docs/x-knowledge 開頭)被當真節點;無前綴反引號節點名抓不到;旗艦數字「max 7」照 spec 自己定義重算=**158**(差 22 倍);「排除自引」規則機械上不可觸發,真正的結構性自引(報告必引自己被審節點)反而沒處理;分桶框架與全體混算的示例自相矛盾。
3. **算術與快照語意不成立(資料席)**:423+20=443≠444,兩個獨立錯誤互相抵消才看似對(數字病第八次);帳是活的——本切片自己的審查當場把帳面數字改了(806→807),spec 快照語意未定義;後桶 13-14% 樣本是 d8 落地時刻(2026-08-29 15:40)之前的殘留,含被 d8 取代的舊案自己的審查紀錄——日級分桶對午後落地的機制粒度過粗。

**縮案交付(外家反提案,便宜且直接;✅ 2026-08-30 當日交付=[[Verification/2026-08-30_席報告圖譜使用一次性盤點]])**:後桶樣本才二十來份——**一次性內容級盤點**:逐份判讀「finding 有沒有實質依賴圖譜節點資訊」(判讀規則:引自己被審的節點不算;bash/夾具字串不算;實質=finding 的證據或判斷用到了節點內容)。結果落 Verification 筆記=飛輪第一批真數據;字串口徑的方向性數字(31.2%→9.5%)一併記為構念效度反證。

**重開條件(全部滿足才重議常設)**:①d8 後審查席列 n≥50 ②有人給得出唯一可驗收 oracle(至少解:bash `[[ ]]` 誤判/夾具假路徑/被審節點自引/活帳快照時點/時刻級分桶五類)③一次性盤點顯示內容級使用率有值得追蹤的變化。

**留下的可復用資產**(std r1 抑噪面驗過):分母判準=有 auditor ∧ 有 report_path(kind 枚舉無篩選力);ts 100% 同時區 ISO、字串前綴比較安全;report_path 值域 444/445 在 repo 內(1 筆指外部私有逐字稿,權限 600);缺 auditor 實帳恰 1 筆;真要抽連結必須復用 link_target()/nfc() 與 code-block 排除慣例(_search_visible_lines),不得另寫(架構席)。

## 已知會被機械報表接住的人肉觀察（動機實例）

深鏡頭席三連漏 canary（席位×軸）/資源例外型 canary 天生 haiku 可見（型別難度）/fromscratch 9→6→3 遞減 vs M2 6→9→7 不遞減（spec 類型剖面）/M1 後辯方零開庭（提效量測）——這些全靠人肉看 note 撈出來,本該一行 stats。

## 飛輪量測雙帳(2026-08-31 立,Enzo 裁「做」;回答「良性循環怎麼衡量」)

良性循環的價值多半長成「沒發生的壞事」,量不到;只能量它的兩面影子,一季看一次趨勢、**不當 KPI 追**(一追人就會製造攔截——Goodhart):

**① 攔截帳(防禦面,零工具慣例)**:圖譜舊知識擋下錯誤動作的瞬間。**寫法**:停案/縮案/廢案的裁定文字裡寫統一記號 `★圖譜攔截★站:開案前|首輪|第N輪;源:<節點名>`;週看=
    grep -rn "★圖譜攔截★" docs/*-knowledge governance/review-reports
攔截點越早=循環越順;老攔在第 N 輪=有料但送不到眼前。**種子帳(2026-08-30 一天三筆,回填)**:
| 站 | 案 | 源 |
|---|---|---|
| 開案前 | 席報告引圖譜率(乾淨查證員命中兩前案,免當第三個重造者) | [[Projects/impact鏡頭機械化_計劃]]、[[Projects/送審前impact鏡頭機械化_計劃]] |
| 首輪 | 爆炸半徑供糧(守墓人席拿停案 d2 逐字對上提案 B) | [[Projects/impact鏡頭機械化_計劃]] |
| 第 2 輪(貴,反面教材) | impact 鏡頭機械化 2026-08-29(燒兩輪十席次才被外家攔) | [[Projects/送審前impact鏡頭機械化_計劃]] |

**② 逃逸帳(漏網面,M1② 原語,✅ 2026-08-31 落地)**:迴圈收斂放行後、下游抓到可歸因缺陷→
    lumos loop escape <迴圈編號> --stage <發現階段> --severity <minor|major|blocker> --desc <描述>
append-only 落 `docs/.escape-log.jsonl`(★code-r1 折入:寫入走 canary 家族的落盤自驗原語非裸 append;帳檔進簿記白名單防「自己的帳擋自己推送」死結重演;desc 顯示消毒保住一行一筆的 grep 合約★),不進閘;歸因人工判斷(天花板照舊);`--list` 按迴圈分組讀(與記帳參數互斥硬擋——r1 兩席實測「多帶 --list=靜默吞資料」)。**歸因守衛職責=只防編號打錯(NFC 正規化實存性比對),不驗迴圈收斂狀態**——驗語意=偷渡閘,明文不做(r1 外家 ESC-01 裁)。**讀側現況只有 --list**;「季度三數字」是未來式,gov 聚合另案。**現況 0 筆=還沒人記,不等於零逃逸**——用法要進 code-loop skill 收尾步驟(下游修 bug 時回頭問「這缺陷哪個迴圈放行的」)。

**季度三數字**:攔截次數+站位分佈(越早越好)/逃逸次數(越少越好)/使用率基線變化(方向參考,[[Verification/2026-08-30_席報告圖譜使用一次性盤點]])。

★規劃期假設修正(code-r1 合約席 G-1)★:d0 時代寫「M1 皆 append 級貼近 trivial、單 reviewer 即可」——實際 M1② 的 diff 被 pitfalls 機械判 `tier: high` 走了七席完整編制,r1 折入 20+ 條;「規劃期拍的分級」讓位給「機械判的分級」,d3 引句裡「單 reviewer」以此為準訂正。


## 實務隱患(逐類答;2026-08-30 補,涵蓋 M2 切片)

- **金流(payment)**:計劃正文提及金流只是描述 LandmarkMember 語料當對照組;本計劃與切片不碰任何金流。已排除。
- **正式環境不可逆(prod-irreversible)**:全計劃為讀側統計與 append 帳,無對外送出、無不可逆操作。已排除。
- **治理自指(self-governance)★真隱患★**:引圖譜率會被拿來評「鏡頭有沒有用圖譜」——表面提及會膨脹數字(canary-audit 老教訓);處置=①不進任何閘、不驅動任何自動行為 ②天花板明文「量出現不量讀懂」③若未來有人提議拿它當閘,先讀本節與兩前案停案紀錄。
- **效能**:切片掃歷史報告檔(現存數百檔 read_text);gov --stats 非熱路徑、人工指令。單次量測門檻:>2s 再議快取。
- **併發/回滾**:純讀;輸出級,revert 即回。已排除。

## 天花板（誠實）

- 逃逸歸因是人工判斷（「這個 bug 算不算某 loop 該抓的」）,GIGO 同 cluster 歸併。
- 61 loops 分五代後每層樣本小——v1 產出是**可比較的帳**,不是統計結論;結論等帳厚。
- 收集本身不改善任何 loop——它買的是「下次改 loop 機制時有據可依」,對齊 loop engineering 大方向（機制價值看對自動 loop 有沒有用:自主 loop 要自選收斂策略,前提是有帳可查）。

## 進實作前（紀律）

M1 三件皆機械搬運/append 級,貼近 trivial——實作時單 reviewer 即可,註明;M2 stats 讀取器動分析語意,建議過一輪輕 design-loop。落地 Verification 以 `plan_refs` 回指本節點。
