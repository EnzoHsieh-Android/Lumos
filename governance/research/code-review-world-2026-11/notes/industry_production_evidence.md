# AI 輔助與 AI 主導代碼審查的產業生產實證(截至 2026-11-01)

讀法說明:
- 每條都標 **[新]**(既有筆記《世界解重新註解2026-10_迴圈工程_調研》沒有)或 **[已知]**(筆記已有)。系統名在筆記裡、但這組數字或細節沒有的,標 [新] 並註明。
- 證據標記:**生產-自報**(部署方自己量)、**準實驗**(有對照或差分,但非隨機)、**A/B**(隨機線上實驗)、**離線**、**問卷**、**宣稱**(行銷或無方法)。
- 閱讀深度:**PDF 核**=我把原文抽成文字或看了版面,數字逐字核過;**全文摘**=網頁抓取工具讀全文後回傳(其引號是工具轉抄,未逐字複核);**摘要**=只讀論文摘要;**二手**=只看到轉述,原文沒開。
- 網路內容一律當資料處理。

## 問題一:各工程組織的生產部署回報了什麼?

### Takeaway
真正有生產結果的只有少數幾家,而且最強的數字都來自「把低風險改動分流出去」或「整條流程改造」,不是單純加一個審查機器人。Meta RADAR 是唯一公開事故率的部署(回退率 1/3、生產事故率 1/50),但作者自己說不是因果估計,而且那批改動本來就是挑過的低風險。Anthropic 是唯一公開多輪收斂與回退比例的部署,但沒有樣本數也沒有對照組。其餘多半只有留言處理率,定義互不相容。

### Cited Findings

#### Meta(最完整的一組)
- [新] **RADAR 規模與結果**(系統已在筆記,數字沒有;生產-自報;PDF 核):已審 535,290 個 diff、落地 331,720 個,單日達 25K;目前核准率 60.31%(L7)、Verification 通過率 26.31%;回退率是非 RADAR 的 1/3、生產事故(PI)率 1/50,兩者 Fisher 精確檢定都顯著;相較人審,「median time to close」低 "over 330%"、「median diff review wall time」低 35%;把 DRS 門檻從 p25 放寬到 p50 後核准率到 60.31%。第 4 節明寫 "this is not a causal estimate";內部效度節說 diff 不是隨機分派,差分法「we do not provide the full model specification」。「低 330%」數學上不可能是降幅,應是倍率寫法,原文如此。原始回退與事故件數未公開。一篇第三方解說把比值寫成 1/13,是 PDF 文字層把分數 ⅓ 抽成「13」造成的誤讀,我看過版面確認是 1/3。— [arXiv 2605.30208v1,2026-05-28](https://arxiv.org/abs/2605.30208)
- [新] **RADAR 分層門檻**(PDF 核):人寫的 diff 預設 DRS P5(只有最低風險 5% 合格),未列白名單的機器來源 P20,白名單 runbook P50;排除開源碼、SOX 範圍、需額外審查的碼,加作者資格、封鎖片語與封鎖路徑。人寫 diff 分兩步:Verification 通過可先上線、之後補審;Approval 再通過才免人審。機器 diff 有每 runbook 每日 10–2000 上限,核准後還有可設定的延遲,人可在此期間否決。— [arXiv 2605.30208v1](https://arxiv.org/abs/2605.30208)
- [新] **RACER 代碼修改代理**(PDF 核):約 3,000 diff/週,59% 不需人修改就落地;在沙盒產生改動、跑驗證、依 build/test/靜態分析錯誤重試。— [arXiv 2605.30208v1 第 2.2 節](https://arxiv.org/abs/2605.30208)
- [新] **ARCTIC 意圖與偏移檢查**(準實驗,非隨機;全文摘):作者署名 Meta(頁首另見 Concordia University),2026 春季漸進上線,超過 100 萬次 API 請求;看到偏移分數的作者比沒看到的多降 −5.76 分(n=94 對 99,單尾 Welch p=0.026,Cohen's d=−0.28,Mann-Whitney p=0.063);意圖預測核可 90.2%(n=112);自審落地累計 0 件歸因缺陷,**但自審 diff 回退率 0.33%,基線 0.17%**,且未給分母。離線:Spotlight 較基線 AI 審查員品質估計好 2.4 倍、token 少 5 倍,首次回應 55.4 秒對 335.9 秒。作者聲明資料依法不能公開。— [arXiv 2607.29516 v2,2026-08-14](https://arxiv.org/html/2607.29516v2)
- [新] **MetaMateCR(依審查留言自動產修補)**(線上實驗,論文稱 experiment,隨機方式未逐字核;全文摘;FSE 2026 工業軌):ActionableToApplied 定義為「可行動留言中,作者接受並併入的比例」。GPT-4o 10.71%/10.53%,SmallLSFT 16.13%,LargeLSFT 19.75%;ShownToApplied 分別 19.90%/21.27%、27.55%、28.74%;離線完全一致率 59.22%、63.11%、67.96%。**安全試驗:讓審查者看到 AI 修補時,TimeInReview +5.5%(p=.029)、TimeSpent +6.7%(p≪.001);改成審查者端摺疊後回歸消失。** 論文內部有小不一致(18.90% vs 19.90%)。試驗樣本只寫「10's of thousands of engineers」。— [arXiv 2507.13499v1,2025-07-17](https://arxiv.org/html/2507.13499v1);[FSE 2026 議程](https://conf.researchr.org/details/fse-2026/fse-2026-industry-papers/16/AI-Assisted-Fixes-to-Code-Review-Comments-at-Scale)
- [新] **JiTTest 即時抓錯測試**(生產-自報;摘要):22,126 個測試;改動感知方法的候選比強化測試多 4 倍、比巧合失敗多 20 倍;規則加 LLM 評估器減少人工審量 70%;41 個候選報給工程師,8 個確認為真(研究員自算 19.5%),其中 4 個若漏掉會造成嚴重失敗。— [arXiv 2601.22832v1,2026-01-30](https://arxiv.org/abs/2601.22832v1)
- [新] **TestGen-LLM 基線**(生產-自報;摘要;FSE 2024):75% 建置成功、57% 穩定通過、25% 提高覆蓋率;73% 建議被工程師接受進生產(後者來自 test-a-thon,不是全部生成)。— [arXiv 2402.09171](https://arxiv.org/abs/2402.09171)
- [已知] **Diff Risk Score**:官方文只有定性結果,加 2024 年一次凍結期間落地 "10,000+" 改動與 19 個用例。— [Meta Engineering,2025-08-06](https://engineering.fb.com/2025/08/06/developer-tools/diff-risk-score-drs-ai-risk-aware-software-development-meta/)
- [新] **DRS 捕獲數字的正確讀法**(摘要):2024 論文裡,邏輯迴歸基線擋前 5% 抓 18.7% SEV、前 10% 抓 27.9%、前 50% 抓 84.6%;LLM 模型的倍率是 1.40x、1.52x、1.05x(摘要未對應到各模型各區)。RADAR 論文另舉例「flagging 10% of diffs while catching 60% of PI-causing changes」(例示語氣,非量測報告)。— [arXiv 2410.06351](https://arxiv.org/abs/2410.06351);[arXiv 2605.30208v1 第 2.3 節](https://arxiv.org/abs/2605.30208)

#### Anthropic
- [新] **Claude Code 團隊內部流程**(生產-自報;全文摘,關鍵句逐字請工具抄出):Claude 寫約 90% 的 Claude Code;6 到 9 月合併 PR 增加一倍以上,"the share that had to be reverted fell by more than 40 percent"。收斂改造前後:一輪審修就過 65%→78%,需 5 輪以上 8.9%→1.5%,平均過關審查次數 2.08→1.32。**未給樣本數,回退怎麼算也沒寫,沒有對照組。** 也有反例:一個 CLI PR 一夜跑了 50 輪以上才被作者叫停。— [How the Claude Code team does code review,2026-10-15](https://claude.dev/blog/solving-code-review-at-anthropic/)
- [新] **該流程的閘**(同上,逐字):"A PR can't merge while any finding from the bug review or the security review is still open. You either fix it or close the thread with a short reason";"Every finding has to be answered";"An agent's approval never counts as a person's";低風險(文件、文案、內部功能、flag 後的新增)"None required once automated review and security checks are green";風險級由分類器看改動決定,第二個分類器再問這次要不要人;CI 工作流檔案永遠要人。自承缺口:"We don't yet have circuit breakers that tighten approval when those numbers move"。— [同上](https://claude.dev/blog/solving-code-review-at-anthropic/)
- [已知] **託管版 Code Review**:有實質意見的 PR 16%→54%;>1000 行 84% 有發現、平均 7.5 條;<50 行 31%、平均 0.5 條;被標錯 <1%;約 20 分鐘;$15–25。— [claude.com/blog/code-review,2026-03-09](https://claude.com/blog/code-review)
- [新] **託管版現況**(官方文件,2026-11-01 讀):四階段 Find/Verify/Rank/Post;"without building or running your code";review "never approves or blocks";現行成本頁已不寫固定金額,改說依等級、大小、候選量而定;新增 Quick/Standard/Deep 三級;預設每次 push 都審,成本乘以 push 數;分析頁的回饋指標是「因開發者處理而自動解決的留言數」。GA 日期 2026-10-15 為二手。— [文件](https://code.claude.com/docs/en/code-review);[成本](https://code.claude.com/docs/en/code-review-costs.md);[Unite.AI(二手)](https://www.unite.ai/?p=486769)

#### Microsoft
- [新] **內部 PR 審查助手**(宣稱級自報;全文摘):"over 90% of PRs across the company impacting more than 600K pull requests per month";"5000 repositories onboarded" 觀察到 "10 – 20% median PR completion time improvements",來源只寫 "Per early experiments and data science studies",無方法、基線、時間窗;無留言接受率。文中未描述技術架構。— [Engineering@Microsoft,2025-07-14](https://devblogs.microsoft.com/engineering-at-microsoft/enhancing-code-quality-at-scale-with-ai-powered-code-reviews/)
- [新] **CLI 代理推廣**(準實驗;全文摘;不是審查研究):合成對照 +24.0% PR/人/日(95% CI +14.5%~+33.7%);作者明說未量審查時間、回退、PR 大小、品質。— [arXiv 2607.01418v1,2026-07-01](https://arxiv.org/html/2607.01418v1)

#### ByteDance
- [已知] **BitsAI-CR**:精確率 75.0%。— [arXiv 2501.15134](https://arxiv.org/abs/2501.15134)
- [新] 摘要另報 Outdated Rate 26.7%(Go)、周活 12,000+(摘要);2025-11 之後未找到 ByteDance 新的審查生產論文。— [arXiv 2501.15134](https://arxiv.org/abs/2501.15134)

#### Atlassian
- [新] **RovoDev 數字**(系統已在筆記,數字沒有;生產-自報,觀察性;全文摘):2024-06 到 2025-06 共約 12 個月;超過 1,900 個 repo(§4.1 寫超過 2,000);54,000+ 則、約 2.1 則/PR、5,500+ 工程師。CRR(留言行在下一次提交被改且問題解決)38.70%,人類 44.45%(只量 2025-07-10 到 15 一週)。有留言的 PR 中位週期 14.35 小時,無留言 20.73 小時,−31%(摘要 30.8%;43,633 對 42,981 個 PR);每 PR 人類留言 2.87 對 4.45,−35.6%;另有 77 週中斷時間序列。— [arXiv 2601.01129v2](https://arxiv.org/html/2601.01129v2)
- [已知] RovoDev 消融:拿掉 LLM 事實判官影響很小。— [同上](https://arxiv.org/html/2601.01129v2)

#### Google
- [已知] AutoCommenter 有用率 54%→66%。— [arXiv 2405.13565](https://arxiv.org/html/2405.13565)
- [新] **該數字的細節**(全文摘):分母是「有回饋的留言」;54%→66% 是抑制 17 條 URL 後對歷史資料重算,評分員口徑 60%→74%;目標 80%,作者稱抑制後超過 80%;330 條規則 URL,前 85 條占 90% 留言;全域門檻 0.98 後改每 URL 門檻;濾掉未改動行後 6%→1.3% 的變更檔有留言;2023-07 約半數開發者 A/B,2023-10 GA。未公開絕對量。— [同上](https://arxiv.org/html/2405.13565)
- [新] **ML 建議編輯**(生產-自報;全文摘;基線):離線在 50% 精確率下處理 52% 留言;線上約 50% 相關留言有高信心建議;被預覽的建議有 40–50% 套用;預覽率 20%→40%;「hundreds of thousands of hours」是預估不是量測;12 週 A/B 當時僅為計畫。— [Google Research,2023-05-23](https://research.google/blog/resolving-code-review-comments-with-ml/)
- [新] 後續「約 7.5% 審查留言由助手處理」(二手:只見搜尋摘要,原文沒開)。— 見 [arXiv 2507.13499](https://arxiv.org/pdf/2507.13499)
- [新] 75% 新碼由 AI 生成且經工程師核可(2026-04,Pichai;二手)。— 引用見 [arXiv 2607.13196v1](https://arxiv.org/abs/2607.13196)

#### Uber
- [已知] uReview 有用率 75%、已處理 65%。— [uber.com/blog/ureview,2025-08-12](https://www.uber.com/blog/ureview/)
- [新] **2026 演講數字**(二手:StartupHub 轉述 AI Engineer 演講,未開影片):約 25,000 則/週;約 10% 留言有明確回饋;約 4% PR 有負面回饋;整體處理率 67%,高嚴重度約 75%;成本比樸素基線 −60%;「accuracy +70%」未定義;首次審查時間由 2024 約 3 小時升到 2026 約 9 小時。— [StartupHub,2026-08-28](https://www.startuphub.ai/ai-news/artificial-intelligence/2026/uber-s-ureview-rebuilds-automated-code-review)
- [新] 涵蓋約 90%、約 65,000 diff/週、中位延遲 4 分鐘;「約 1,500 小時/週」方法未揭露(二手整理)。— [Port 整理](https://software-factories.port.io/uber)
- [新] 約 11% PR 由代理開出(二手搜尋摘要,未核原文)。— [Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/how-uber-uses-ai-for-development)

#### Tencent
- [新] **《腾讯2025研发大数据报告》**(自報;二手:報告原文沒找到):評審環節 AI 參與度 94%;28% 代碼缺陷由 AI 直接發現並被工程師採納;有效問題檢出量 +44%;50% 新增代碼由 AI 輔助生成。定義全部未知。— [新浪財經,2025-10-24](https://finance.sina.com.cn/stock/t/2025-10-24/doc-infuyzvh8294319.shtml);[新浪科技](https://finance.sina.com.cn/tech/it/2025-10-24/doc-infuyrfq6957124.shtml)
- [新] 靜態分析誤報研究:433 則告警,LLM 結合靜態分析減誤報 94–98%(二手摘要)。— [Emergent Mind 轉載](https://www.emergentmind.com/papers/2601.18844)

#### Ericsson
- [新] **多代理審查原型**(工業評估,非線上部署;全文摘;PROFES 2026):Kiro CLI 編排四個鏡頭代理(可讀性、可維護、可靠、效能),加 GitLab 與 Code Knowledge Graph 兩個 MCP;7 個提交、4 個專案、5 位資深開發者;206 條裡 197 條正確(96%),重要性 Minor 31%、Medium 36%、High 33%。**只有 Python、作者評自己的提交、沒量接受率、延遲、成本,也沒消融。** — [arXiv 2609.15877v1,2026-09-14](https://arxiv.org/abs/2609.15877v1)

#### Mozilla
- [新] **patch 時 AI 審查僅有入口**:`moz-phab` 有 `submit.ai_review`(預設 False)與 `--ai`;未說明用什麼模型,也查不到成效數字。— [mozilla-conduit/review](https://github.com/mozilla-conduit/review)
- [新] **Firefox 程式稽核管線**(生產-自報;全文摘;這是程式稽核,不是 PR 審查):271 個 Claude Mythos Preview 找到的 bug 在 Firefox 150 修掉(180 sec-high、80 sec-moderate、11 sec-low);2026-04 修 423 個資安 bug,2025 每月約 20–30;自建 harness 產生並執行可重現測試案例,重現不了就丟棄;早期 GPT-4、Sonnet 3.5 誤報太多。patch 時掃描仍是計畫。— [Mozilla Hacks,2026-05](https://hacks.mozilla.org/2026/05/behind-the-scenes-hardening-firefox/)
- [已知] RevMate(Mozilla+Ubisoft)採用率 7–8%(本次未複驗)。

#### 商用工具
- [新] **GitHub Copilot code review**(自報;全文摘):6,000 萬次;"more than one in five code reviews on GitHub";量較上線 10X;71% 審查有可行動回饋、29% 不留言;約 5.1 則/審查;改代理架構帶來 "initial 8.1% increase in positive feedback";12,000+ 組織每 PR 自動跑。回饋指標是讚/倒讚,加上「合併前有無修掉」。— [GitHub Blog,2026-03-05](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/)
- [已知] Copilot 多模型合成 A/B 與 ReviewBench。— [GitHub Blog,2026-10-05](https://github.blog/ai-and-ml/github-copilot/reviewbench-an-open-benchmark-for-ai-code-review/)
- [新] **Cursor Bugbot**(自報;全文摘):LLM 判官判「合併時是否已處理」,只算公開 repo:Bugbot 78.13%(50,310 PR)、Greptile 63.49%(11,419)、CodeRabbit 48.96%(33,487)、Copilot 46.69%(24,336)、Codex 45.07%(19,384)、Gemini Code Assist 30.93%(21,031);上線時 52%。學習規則:110,000+ repo、44,000+ 規則,依信號升降級。廠商自己跑自己排第一。— [cursor.com/blog/bugbot-learning,2026-04-08](https://cursor.com/blog/bugbot-learning)
- [新] **Greptile v4**(自報 A/B;全文摘):「過去一個月」跨「many customers」、「hundreds of thousands of PRs」,未給分組或顯著性;處理率 30%→43%(LLM 判);每 PR 已處理 0.92→1.60、正面回覆 0.31→0.52、按讚 0.05→0.08。— [Greptile,2026-03-05](https://www.greptile.com/blog/greptile-v4)
- [已知] CodeRabbit 野外研究 36.4/7.3/56.3。— [arXiv 2607.03316](https://arxiv.org/abs/2607.03316)
- [新] **CodeRabbit AI vs 人寫**(廠商報告;全文摘):470 個開源 PR(320 AI、150 人),AI PR 約 1.7 倍問題(10.83 對 6.45);作者身分靠推斷,自承無法保證。— [CodeRabbit,2025-12-17](https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report)
- [新] **Graphite Diamond**:Cursor 2025-12-19 宣布收購;Diamond 名稱已廢止併入 Graphite Agent;計畫併入 Bugbot;沒找到 Graphite 自己的生產接受率。— [TechCrunch](https://techcrunch.com/2025/12/19/cursor-continues-acquisition-spree-with-graphite-deal);[Graphite](https://graphite.com/blog/series-b-diamond-launch)
- [新] **Qodo**:Martian 離線 64.3% F1 第 1 是研究預覽版 "Qodo Extended",**生產版 Qodo Standard 只有 47.9%、第 4**;沒找到生產接受率。— [Qodo,2026-03-15](https://www.qodo.ai/blog/qodo-ranked-1-ai-code-review-tool-in-martians-code-review-benchmark/)
- [新] **Sourcegraph Amp/Cody**:Amp 2025-12-18 改為獨立審查代理(Gemini 3 Pro,加預掃與檔案排序),**無任何量測**;Amp 2025-12-02 分拆、Cody 轉企業限定(後者二手)。— [Amp](https://ampcode.com/news/agentic-code-review);[aicodereview.cc(二手)](https://aicodereview.cc/tool/sourcegraph-cody)

#### 與既有筆記的矛盾或需修正(彙整)
- **矛盾 1,硬閘**:筆記第 6 條、挑戰 11、機制表寫「產品界的 check 都中性不擋」「硬擋推送沒有外部背書」「世界刻意不做硬閘」。託管產品確實不擋,但 Anthropic 自己內部是 "A PR can't merge while any finding … is still open" 且 "Every finding has to be answered"。這是最接近 Lumos 處置閘的外部做法。「可重算的帳」這點目前仍查無對應。— [來源](https://claude.dev/blog/solving-code-review-at-anthropic/)
- **矛盾 2,投票**:筆記第 5 條與總結寫「多席取聯集不投票」「放棄多數決」。Anthropic 內部是 "a separate group votes on each finding, and it only gets posted if enough of them agree",投票從找錯端移到驗證端,不是消失。— [來源](https://claude.dev/blog/solving-code-review-at-anthropic/)
- **過期 3**:第 5 條 Bugbot「52%→70% 以上」已過期,2026-04-08 是 78.13%。— [來源](https://cursor.com/blog/bugbot-learning)
- **需補 4**:第 20 條「擋前 5% 也只抓到 18.7%」是 2024 邏輯迴歸基線,不是現行 LLM 版本的上限;見上面 DRS 條。
- **需修 5**:「Martian 三家判官」實際是 Opus 4.5、GPT-5.2、Sonnet 4.5,三個模型只有兩家。— [來源](https://github.com/withmartian/code-review-benchmark)
- **確認 6**:2603.15911 的 16.6% 在 v1、v2 都成立(PDF 核);2026-10-15 Anthropic 數據「自報、無樣本數」也成立。

### Inferences
- 有生產結果的部署,共同點是「先決定這個改動值不值得人看」,而不是「把留言變多」。RADAR、Anthropic 都把分級放在審查之前。
- RADAR 的 1/50 不能解讀成自動審查比人安全。它比的是「挑過的最低風險」對「其餘全部」,DRS 本身就在預測事故,這個差距大部分應該來自選擇。
- ARCTIC 的 0.33% 對 0.17% 是目前少數公開的「放寬審查後回退變高」訊號,而且出自同一批作者群,值得跟 RADAR 的 1/3 並列看。
- RovoDev 的「有留言的 PR 週期較短」可能是反向因果:留言與 PR 大小、類型相關,未見配對。

### Gaps
- Google 2024 之後沒找到任何量化的 AI 審查生產論文;Microsoft 未找到同儕審查的 PR 審查器論文;Tencent 報告原文未找到,定義不明。
- Graphite、Qodo、Amp 查無公開生產接受率。
- Uber 2026 數字只有演講轉述,未能開原始影片。
- ByteDance、Tencent 2026 年審查生產論文未找到(不代表不存在,只做了兩次中英搜尋)。

## 問題二:哪些架構模式正在收斂?

### Takeaway
「平行找、獨立驗、再濾」已是共識。2026 年真正新增的是三件事:審查前的風險分流、多輪收斂控制、把事故做成每日評測。沙盒實跑確認仍然分裂:資安與測試生成在跑,主流 PR 審查產品仍只讀不跑。

### Cited Findings
- [已知] **找與驗分離**:BitsAI-CR 二元驗證器、RovoDev 雙判官、Anthropic 驗證步驟。— 見筆記第 6、12、13 條。
- [新] **驗證端用投票**:Anthropic 內部以獨立一組代理對每條投票,再丟掉純風格類。— [Anthropic](https://claude.dev/blog/solving-code-review-at-anthropic/)
- [新] **風險分流進入主流**:Meta 三層 DRS 門檻;Anthropic 低/中/高風險對應 0/1/2 人;Faros 也建議依風險切分。— [RADAR](https://arxiv.org/abs/2605.30208);[Anthropic](https://claude.dev/blog/solving-code-review-at-anthropic/);[Faros](https://pages.faros.ai/hubfs/AI_Engineering_Report_2026_The_Acceleration_Whiplash_Faros.pdf)
- [新] **多輪收斂控制**:三輪後 "the reviewer asks the author to step back and reconsider the approach";"Diff-only re-review after the first few passes";"No repeats of findings already posted";標記整類 bug 而非單行。— [Anthropic](https://claude.dev/blog/solving-code-review-at-anthropic/)
- [新] **事故轉評測**:"Any incidents are now an eval",工程師確認過的歷史事故 PR,每天回放。— [Anthropic](https://claude.dev/blog/solving-code-review-at-anthropic/)
- [新] **沙盒實跑確認分裂**:Mozilla 跑可重現測試案例;RACER 沙盒加驗證;Meta 抓錯測試跑在 CI;Ultrareview 用雲端沙盒;但託管 Code Review 明寫不建置不執行。— [Mozilla](https://hacks.mozilla.org/2026/05/behind-the-scenes-hardening-firefox/);[RADAR](https://arxiv.org/abs/2605.30208);[JiTTest](https://arxiv.org/abs/2601.22832v1);[Claude 文件](https://code.claude.com/docs/en/code-review)
- [新] **信心門檻下放到每條規則**:AutoCommenter 從全域 0.98 改每 URL 門檻,每語言門檻無效。— [arXiv 2405.13565](https://arxiv.org/html/2405.13565)
- [新] **Repo 脈絡檢索**:Copilot 改代理式檢索,正面回饋 +8.1%(無對照細節);Ericsson 用代碼知識圖譜 MCP;Uber 連知識庫與歷史 PR。— [GitHub](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/);[Ericsson](https://arxiv.org/abs/2609.15877v1);[StartupHub](https://www.startuphub.ai/ai-news/artificial-intelligence/2026/uber-s-ureview-rebuilds-automated-code-review)
- [新] **去重與貼文後處理**:Anthropic 排名前去重;Uber 評分、分類、過濾、去重;Mozilla 對已知問題去重。— 同上各來源
- [新] **回饋學習自動化**:Bugbot 候選規則升降級;Copilot 跨審查記憶;Anthropic 依作者反應分類留言(修、拒、有意為之、忽略)。— [Cursor](https://cursor.com/blog/bugbot-learning);[GitHub](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/);[Anthropic](https://claude.dev/blog/solving-code-review-at-anthropic/)
- [新] **留言呈現位置會改變成效**:MetaMateCR 只把修補從審查者端摺疊,就消除了 5.5% 的審查變慢。— [arXiv 2507.13499v1](https://arxiv.org/html/2507.13499v1)
- [新] **責任邊界明文化**:Anthropic「代理的核准不算人」;Meta RADAR 把作者資格與排除範圍寫進資格規則。— [Anthropic](https://claude.dev/blog/solving-code-review-at-anthropic/);[RADAR](https://arxiv.org/abs/2605.30208)

### Inferences
- 架構收斂的方向是「更多確定性閘包住 LLM」。RADAR 五層裡只有一層是 LLM 審查,其餘是規則與模型分數。
- 把重審範圍縮到差分,Anthropic 與 Qwen(筆記第 9 條)同向;Lumos 修完重審整份的做法,已有兩家外部做法方向相反,Anthropic 還附了多輪收斂的自報數字。

### Gaps
- 沒有任何部署公開「驗證步驟本身的開關消融」的生產數據;RovoDev 的消融只對齊人類留言位置,不算線上。
- 「三輪上限」與「只審差分」各自貢獻多少,Anthropic 沒拆開。

## 問題三:接受率與精確率的實際數字與定義

### Takeaway
這些數字幾乎不能互比。「精確率」「接受率」「解決率」的分母從「有明確回饋的留言」到「全部建議」都有,判定者從人到 LLM 都有。同一工具在不同口徑下差很多:Copilot 在 Cursor 的解決率表是 46.69%,在 Martian 線上是 62.6% F1。

### Cited Findings

| 組織或工具 | 數字 | 分子/分母 | 判定者 | 不相容之處 |
|---|---|---|---|---|
| Google AutoCommenter [已知] | 54%→66% | 正面/**有回饋的留言** | 開發者 | 自願回饋,有選擇偏誤 |
| Uber [已知] | 有用 75%、處理 65% | 有用:明確回饋;處理:重跑判定 | 開發者與自動 | 2026 轉述僅約 10% 留言有回饋 |
| Atlassian CRR [新] | 38.70%(人 44.45%) | 下一提交改了留言行且解決 | 自動 | 唯一有人類對照,但只量一週 |
| Bugbot [新] | 78.13% | 合併時已處理/留言 | **LLM** | 只公開 repo,廠商自跑 |
| Greptile [新] | 43% | 已處理/留言 | **LLM** | 樣本未揭露 |
| CodeRabbit 野外 [已知] | 接受 36.4% | 接受/**有人回覆的留言** | GPT-5.1 標註 | 沒回覆的不算 |
| 2603.15911 [已知] | AI 16.6%、人 56.5% | 採用/全部 suggestion 區塊 | 文字相似度 | 只算 suggestion 區塊 |
| Claude Code Review [已知] | 被標錯 <1% | 被標錯/發現 | 工程師 | 不是精確率:沒標不代表對 |
| Meta MetaMateCR [新] | 19.75% | 套用/可行動留言 | 系統紀錄 | 量修補不是找錯 |
| BitsAI-CR [已知] | 75.0% | 人工抽樣精確率 | 人 | 僅約 10% 抽樣 |
| Ericsson [新] | 96% | 正確/206 條 | 作者本人 | 7 個提交 |
| Tencent [新] | 28% | 未定義 | 未知 | 無法比較 |
| Martian [已知] | F1 約 57–66% | 配對到開發者後續修改 | LLM | recall 分母是「開發者修掉的」,不是全部缺陷 |

- [新] Martian 線上 recall 的分母是開發者後來修掉的問題,不是所有存在的缺陷(repo 定義:Real fixes the bot caught / total fixes made;搜尋摘要另引一句 Martian 原話,但我沒開到該頁,不當逐字引用)。— [方法 repo](https://github.com/withmartian/code-review-benchmark)
- [新] 2607.21997:五個代理在 342 個 Python repo 的 54,791 則留言,未解決主因是建議錯誤與刻意設計;Copilot 占已解決留言 72.9%(這是占比不是解決率)。搜尋摘要另寫 54,713 則、約 60–70% 未解決,**摘要頁未證實**,引用時要注意。— [arXiv 2607.21997,v2 2026-07-29](https://arxiv.org/abs/2607.21997)
- [新] 2603.15911 v2 未採用原因(N=383):錯誤 28.7%、改用別的修法 24.0%、不需要 16.4%、宣稱修了但無提交 11.2%、開發者偏好 10.2%(PDF 核)。— [arXiv 2603.15911,v2 2026-10-26](https://arxiv.org/abs/2603.15911)
- [新] 重要缺陷的處理率高於平均:Uber 高嚴重度約 75% 對整體 67%(二手)。— [StartupHub](https://www.startuphub.ai/ai-news/artificial-intelligence/2026/uber-s-ureview-rebuilds-automated-code-review)

### Inferences
- LLM 判定的「處理率」與真實精確率之間的差距無人公開校準。Bugbot、Greptile、ReviewBench 都用它,等於同一把尺的共同偏誤。
- 「被拒」也不等於錯:上面 N=383 的樣本裡 24.0% 是改用別的修法。

### Gaps
- 沒有任何一家公開「同一批留言,LLM 判定 vs 人工判定」的一致度數據。
- 沒有部署同時公開召回與精確;Anthropic 明確沒有召回。

## 問題四:AI 審查真的降低生產缺陷或事故嗎?有無負面發現?

### Takeaway
沒有。截至 2026-11-01,我找不到任何受控或差分研究證明 AI 審查工具本身降低生產缺陷或事故。正面數字都是挑過的樣本或前後比較;最嚴謹的大樣本研究只確認了審查是瓶頸、AI 審查工具沒解掉它。負面證據是具體的:審查變慢、回退變高、品質沒跟著效率上升。

### Cited Findings

**正面訊號(都不是因果)**
- [新] Anthropic 回退占比降逾 40%:同期還改了流程、分級、收斂,且無對照。— [來源](https://claude.dev/blog/solving-code-review-at-anthropic/)
- [新] Meta RADAR 回退 1/3、PI 1/50:"not a causal estimate"。— [arXiv 2605.30208v1](https://arxiv.org/abs/2605.30208)
- [新] Meta JiTTest:4 個若漏掉會造成嚴重失敗的真實抓錯,是少數有具體攔截案例的。— [arXiv 2601.22832v1](https://arxiv.org/abs/2601.22832v1)
- [新] RovoDev 週期 −31%:觀察性。— [arXiv 2601.01129v2](https://arxiv.org/html/2601.01129v2)
- [新] Microsoft 10–20%:無方法。— [來源](https://devblogs.microsoft.com/engineering-at-microsoft/enhancing-code-quality-at-scale-with-ai-powered-code-reviews/)

**負面或中性**
- [新] **Chen & Stratton(最嚴謹的公司層級研究;錯開差分;PDF 核;工作論文,未同儕審查)**:655 家、720,542 人、4.45 億事件(2021-01 到 2026-08)。採用代理後審查時間 +56.1%(β=1.99,基線 3.56 天)、等待 +59.9%、主動審查 +58.5%、每 PR 留言 +38.6%;被正式要求修改 +38.5% 但邊際不顯著。"This bottleneck is not eliminated by adoption of AI tools in the review process"。**Jira bug 回報無顯著變化**(代理 β=−0.062,s.e.=0.150)。資料由分析平台 Jellyfish 提供。**此論文沒有估 AI 審查工具本身的效果**,只描述採用率。— [Chen & Stratton,版本日 2026-11-01](https://fion.ac/jellyfish.pdf)
- [新] **版本漂移警告**:二手報導仍引舊版的 718 家、3 億事件、+49%(3.45/7.03 天)、「要求修改幾乎翻倍」;最新版已改,上面才是現值。— [二手例](https://letsdatascience.com/news/harvard-study-finds-ai-coding-agents-raise-code-volume-not-o-ea78729b)
- [新] **2607.13196**:207 個 GitHub 專案、102 萬 PR,三個時代比較:代理參與的模式在漸進採用與快速代理採用下決策較快,"these efficiency gains do not translate into better review quality";快速 LLM 採用組 review smell 上升(LLM 時代 +8.0 點、代理時代 +4.4 點)(PDF 核)。— [arXiv 2607.13196v1,2026-07-14](https://arxiv.org/abs/2607.13196)
- [新] **2603.15911**:採用的 AI 建議帶來明顯更大的複雜度與程式量增加;人審 AI 碼多 11.8% 回合;v2 把 v1 的「produce」改成「are associated with」,因果語氣降級(PDF 核)。— [arXiv 2603.15911](https://arxiv.org/abs/2603.15911)
- [新] MetaMateCR 審查變慢 5.5%、ARCTIC 自審回退 0.33% 對 0.17%。— 見問題一
- [新] **Faros 2026**(相關,非因果;遙測;PDF 核):22,000 開發者、4,000+ 團隊,低→高採用季度比:PR 事故比 +242.7%、月事故 +57.9%、每人 bug +54%、每 PR bug +28.7%。方法為 Spearman 相關,每公司標準化,報告自己提醒與 2025 版是獨立橫斷面。Faros 賣工程治理平台。— [Faros,2026-03 分析](https://pages.faros.ai/hubfs/AI_Engineering_Report_2026_The_Acceleration_Whiplash_Faros.pdf)
- [新] **直接衝突**:Faros 說 bug 與事故大增、PR 大小 +51.3%;Chen & Stratton 用差分得 bug 無顯著變化、PR 大小無顯著變化(代理 β=−221.8,s.e.=239.0)。後者有對照設計,前者沒有。— 上述兩來源
- [新] 2608.06640:352 萬次 AI 生成 C++ 改動(2025-04 到 2026-04):介面耦合負擔與複製配置開銷較多,審查工作量較高、運算 +5–8%;針對性回饋讓目標靜態告警 −11.1%(摘要)。— [arXiv 2608.06640](https://arxiv.org/abs/2608.06640)
- [新] 2609.29172:15 天單案例,修補的提交量灌爆 CI 與審查注意力,靠按目錄分批與限制每改動檔數恢復。— [arXiv 2609.29172 v2](https://arxiv.org/abs/2609.29172)
- [新] Amazon 2026-03 事件:FT 報導引內部備忘錄稱有 "Gen-AI assisted changes" 相關事故趨勢並要求資深簽核;**Amazon 否認範圍,稱只有一件涉及 AI 工具**。雙方說法衝突,只能當爭議案例(二手)。— [the-decoder](https://the-decoder.com/amazon-makes-senior-engineers-the-human-filter-for-ai-generated-code-after-a-series-of-outages/);[Slashdot](https://tech.slashdot.org/story/26/03/10/212214/)
- [已知] Beko 已解決 73.8% 但關閉時間變長(本次未複驗)。
- [新] 「83% 確認過的生產故障沒有 AI 審查工具標到」來自賣競品的 PlayerZero,僅見搜尋摘要,未驗證。— [PlayerZero](https://playerzero.ai/resources/ai-code-review)

### Inferences
- 最接近的因果設計(Chen & Stratton)只回答「寫碼代理對審查的衝擊」。要回答「審查工具的效果」,理論上可用同一份 Jellyfish 資料做審查工具採用的錯開差分;論文已偵測 CodeRabbit、Greptile、Copilot Reviewer、Bugbot、Graphite、Bito 的採用時間,只是沒拿來估這件事。
- Faros 與 Chen & Stratton 的衝突,方法差異足以解釋。在這點上應優先採信差分結果,但 Jira bug 回報量本身也是弱指標。
- 目前所有產業證據都支持「審查的效率收益」多於「審查的品質收益」。

### Gaps
- 未找到任何針對 AI 審查工具採用的差分或隨機研究;搜尋了兩次,結果都是代理寫碼研究。
- 逃逸缺陷率(審查過卻出事)沒有任何部署公開。
- Beko、RevMate 原文本次未重開。

## 問題五:商用工具有哪些獨立基準?誰出資?

### Takeaway
真正不賣審查工具的只有 Martian 與學術基準,而 Martian 本身有創投與 Accenture 投資、賣模型路由,網站也沒揭露資金。其餘基準都是廠商自辦,而且主辦方幾乎都排第一。排名的時效以月計。

### Cited Findings

| 基準 | 主辦/資金 | 資料 | 指標 | 注意 |
|---|---|---|---|---|
| Martian Code Review Bench [已知,細節新] | Martian;種子 $9M(NEA 領投,Prosus、Carya、General Catalyst),2024 Accenture Ventures 投資;賣 LLM 路由,不賣審查工具 | 離線 50 PR、173 條標準答案;線上持續抽樣 | P/R/F1 | 頁面未揭露資金或利益衝突 |
| GitHub ReviewBench [已知] | GitHub(賣 Copilot) | 219 PR、187 repo | 見筆記 | 自家第一 |
| Greptile benchmark [新] | Greptile;頁面未明言主辦 | 2025-07,5 repo 各 10 個 bug | 抓到率,**不計誤報** | 自家 82% |
| Macroscope [新] | Macroscope(賣競品) | 118 真實 bug、8 語言;2025-08-25 到 09-14 | 偵測率 | 自家 48.3% 第一;Greptile 只評 72 題 |
| Cursor 解決率表 [新] | Cursor | 公開 repo,見問題一 | LLM 判解決率 | 自家第一 |
| Qodo 植入基準 [已知] | Qodo | 植入缺陷 | 離線 | 見筆記 |
| Augment 基準 [已知] | Augment | — | — | 見筆記 |
| MCR-Bench [已知] | 學術(ISSTA 2026) | 2,269 多輪任務 | 見筆記更正 | 無廠商 |

- [新] Martian 資金:— [Maginative](https://www.maginative.com/article/martian-emerges-from-stealth-with-9m-seed-funding-to-bring-model-router-tech-to-enterprises);[Accenture,2024-09-17](https://newsroom.accenture.com/news/2024/accenture-invests-in-martian-to-bring-dynamic-routing-of-large-language-queries-and-more-effective-ai-systems-to-clients)。目錄站有資金數字互相矛盾,以新聞稿為準。
- [新] Martian 方法:判官 Opus 4.5、GPT-5.2、Sonnet 4.5,前五名三者一致;線上以開發者後續修改為真值,LLM 三步判定,判官模型未具名。— [repo](https://github.com/withmartian/code-review-benchmark)
- [新] **資料重疊疑慮**:Martian 離線集的五個 repo(Sentry、Grafana、Cal.com、Discourse、Keycloak)與數量,跟 Greptile 自辦基準完全相同(5 repo、50 件)。未查到官方說明是否沿用。— [Martian](https://github.com/withmartian/code-review-benchmark);[Greptile](https://www.greptile.com/benchmarks)
- [新] **排名漂移**(線上 F1):2026-07-30 Greptile 60.8%(P 76.2%、R 50.6%)、Codex Connector 59.4%、Cubic 58.7%、Devin 58.6%、CodeRabbit 57.5%;cubic 自家表 cubic 65.7%、Copilot 62.6%、CodeRabbit 60.2%、Bugbot 57.0%;第三方 2026-10-05 快照 Cubic 65.5%、Greptile 62.3%、CodeRabbit 61.0%,14 個工具差約 17 點。各工具評分 PR 數 678–2,434,小差距多半是雜訊。— [Greptile](https://www.greptile.com/content-library/greptile-martian-code-review-benchmark);[cubic](https://www.cubic.dev/blog/cubic-is-the-best-ai-code-reviewer-on-martian-s-benchmark);[aicodereviews.io(作者不具名)](https://www.aicodereviews.io/blog/martians-code-review-bench-the-1-claim-rots-in-months/)
- [新] 離線快照(2026-06-03):GitLab Duo 48.3% F1、第 5/20,cubic 61.8%;$0.25/審查。頁面在 gitlab.io 子網域,未確認是否 GitLab 官方。— [Duo Review Bench](https://duo-review-bench-6f7260.gitlab.io/)
- [新] **主辦方效應**:Greptile 在自家基準 82%(41/50),在 Macroscope 基準 23.6%(17/72);Graphite 6% 與 18.3%。Greptile 頁面的 Copilot 54% 與自家逐 repo 加總 52% 不符。— [Greptile](https://www.greptile.com/benchmarks);[Macroscope](https://macroscope.com/best-ai-code-review-tool)

### Inferences
- 目前最可用的是 Martian 線上榜,但它量的是「開發者後來改了什麼」,對「修了但 AI 沒提」「AI 提了真 bug 但沒人修」都無感。
- 引用任何排名都要帶快照日期與模式(離線/線上)。沒帶的一律不可用。

### Gaps
- 無法直接讀到 Martian 線上榜(網頁主體是動態載入),排名數字全部經廠商或第三方轉述。
- 2606.15689「Bigger Isn't Always Better」與 Medium 上的基準比較文未讀到(後者 403)。
- Claude Code Review 是否列入 Martian 榜,本次無法確認。

## 問題六:AI 寫的程式變多後,審查行為怎麼變?

### Takeaway
審查量與人力的缺口已是多個獨立資料源的共同結論,但「AI 參與審查的比例」的數字差很大,因為有的算 repo、有的算 PR、有的算留言。公司內部的極端案例(Anthropic、Meta)已走到「低風險不需人」,業界平均則還有 7 成以上的留言來自人。

### Cited Findings

**AI 參與審查的比例(口徑不同,不可直接比)**
- [新] 79.1% 公司用過 AI 審查工具(2026-07),但只有 23.3% 審查留言由 AI 產生、10.8% PR 有 AI 留言(PDF 核)。— [Chen & Stratton](https://fion.ac/jellyfish.pdf)
- [新] 25% PR 由 AI 代理審查(前一資料集 0),<1% PR 由代理獨立開出(定義是無人發起)(PDF 核)。— [Faros 2026](https://pages.faros.ai/hubfs/AI_Engineering_Report_2026_The_Acceleration_Whiplash_Faros.pdf)
- [新] Copilot 占 GitHub 審查 "more than one in five"。— [GitHub](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/)
- [新] 單一公司:Microsoft 90%+、Uber 約 90%、Tencent 94%(定義不明)。— 見問題一
- [新] 2607.13196:207 專案中漸進 46%、快速 LLM 22%、快速代理 32%;快速代理組代理參與 76% PR。— [arXiv 2607.13196v1](https://arxiv.org/abs/2607.13196)

**AI 寫碼比例**
- [新] Anthropic:Claude Code 約 90%;monorepo 每日落地約 2,500(5 月)→ 30,000+(9 月)。— [來源](https://claude.dev/blog/solving-code-review-at-anthropic/)
- [新] Meta:每 diff 行數 +105.9%、每人 diff +51%,80%+ 歸因代理,24 小時內審完比例下降(PDF 核)。— [arXiv 2605.30208v1](https://arxiv.org/abs/2605.30208)
- [新] Faros 60% AI 生成程式被接受(前 20%),但這是其遙測口徑。— [Faros](https://pages.faros.ai/hubfs/AI_Engineering_Report_2026_The_Acceleration_Whiplash_Faros.pdf)

**瓶頸數據**
- [新] Faros(相關,PDF 核):首次審查中位等待 +156.6%、審查時間平均 +199.6%、中位 +441.5%、PR 大小 +51.3%、**「PR 不經審查就合併」+31.3%**。注意這是相對增幅,不是「31% 的 PR 沒審」。審查留言 +25% 含 AI 留言,報告自承無法分開。報告本身結論是 "This is an authoring problem, not a review problem"。— [Faros](https://pages.faros.ai/hubfs/AI_Engineering_Report_2026_The_Acceleration_Whiplash_Faros.pdf)
- [新] **Faros 2025 的 91% 與 2026 的 441.5% 常被混用**:91% 只見二手轉述(我沒開 2025 版);2026 版明言兩份是獨立橫斷面、只可看方向。— [二手例](https://baeseokjae.github.io/posts/ai-coding-pr-review-bottleneck-2026/);[Faros 2026](https://pages.faros.ai/hubfs/AI_Engineering_Report_2026_The_Acceleration_Whiplash_Faros.pdf)
- [新] LinearB(8.1M+ PR、4,800 團隊):AI PR 等審 4.6 倍、接手後審 2 倍快;30 天內合併 32.7% 對 84.4%(廠商自有頁面,完整報告未開;5.3x 僅見第三方)。— [LinearB](https://linearb.io/library/ai-in-software-development);[報告頁](https://linearb.io/resources/engineering-benchmarks-report)
- [新] Uber 首審時間 3 小時→9 小時(二手)。— [StartupHub](https://www.startuphub.ai/ai-news/artificial-intelligence/2026/uber-s-ureview-rebuilds-automated-code-review)

**AI 審 AI**
- [新] 2608.21311(ESEM 2026):248,641 個 AI 歸因 PR 收到 AI 歸因審查;跨產品 45,269、同產品 208,145;跨產品約占代理 PR 1.6%,2025-Q1 到 Q3 增長超過兩個數量級;三分之二雙角色工具的同產品留言多 58–65%(效應小);中位延遲跨產品 1.2 分對同產品 4.7 分(時間戳不全);CodeRabbit 對 Claude Code PR 35.0% 標重構,對 Copilot PR 10.5%。— [arXiv 2608.21311](https://arxiv.org/abs/2608.21311)

**問卷**
- [新] DORA 2025(約 5,000 人;PDF 核):90% 使用 AI;30% 對 AI 碼幾乎不信任;吞吐提升但 "it still increases delivery instability";建議用 AI 改善審查是散文建議,無量測。— [DORA 2025](https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf)
- [新] DORA ROI 報告:頁面 2026-04-22 更新,全文要到 Google Cloud 下載,我沒開到;「verification tax」與 J 曲線都是二手;Kodus 文確認該文的審查主張是作者自己的,不是 DORA 的。**LeadDev 稱 DORA 2026-09-03 宣布不做 2026 年度報告**(單一二手,未核)。— [DORA](https://dora.dev/ai/roi/report/);[Kodus](https://kodus.io/en/dora-accelerate-state-of-devops/);[LeadDev](https://leaddev.com/?p=36788)
- [新] Stack Overflow 2026:48% 在容易驗證時才信任 AI;66% 用編碼助手或代理;PR 審查僅稱 "meaningful AI adoption" 沒給百分比;官方頁未見總樣本。6.6%(重要決策)來自二手。— [官方](https://survey.stackoverflow.co/2026/ai);[IT Brief](https://itbrief.co.uk/story/stack-overflow-survey-shows-developers-trust-ai-with-caveats)
- [新] Sonar 2026-01:38% 開發者認為審 AI 碼比審同事的費力(二手)。— [flowverify 轉述](https://www.flowverify.co/blog/ai-code-review-bottleneck-2026-data)

### Inferences
- 10.8%(有 AI 留言的 PR)與 Copilot 的 "one in five" 並不矛盾:前者是 Jellyfish 客戶,後者是全 GitHub 的審查事件,母體不同。
- 「審查是瓶頸」三個方法不同的來源一致(差分、遙測、公司內報);「瓶頸來自品質還是來自量」則未定:Chen & Stratton 兩者都有,Faros 偏品質。
- AI 審查留言並未替代人類審查的工作量,反而可能增加要看的留言數;Faros 的 +25% 無法拆開,這點只是推測。

### Gaps
- 沒有全行業「AI 開出 PR 的比例」共同口徑:<1%(Faros)、10.8%(Chen,是有 AI 留言的 PR,不是開 PR)、11%(Uber 二手)定義全不同。
- Stack Overflow 2026 的 PR 審查使用率、DORA 2025 的「用 AI 做 code review」百分比(圖表抽不出配對)未取得。
- DORA ROI 報告全文未讀。
