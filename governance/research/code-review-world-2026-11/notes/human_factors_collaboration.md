# AI 時代代碼審查的人因面:人機協作、AI 寫的程式怎麼審(截至 2026-11-01)

標記說明。**[新]**:`世界解重新註解2026-10_總覽_調研` 與十篇分類定稿都沒記過(查法:在 `docs/lumos-toolchain-knowledge/Projects/` 用 arXiv 編號與關鍵字 grep)。**[已知]**:上述筆記已記過。**基線**:2025-11 之前的舊作,只當對照。
證據等級照派工單:【同儕受控】【預印本受控】【觀察性】(括號內註明同儕或預印本)【廠商報告】【意見】;法規與規格文字不是實證,另標【規範文字】。
除非另外註明,數字都是我下載原文 PDF、抽出文字後逐字核對的。無法打開原文的項目會明寫。「研究員自算」表示原文沒有這個數字。

## 哪些經典基線現在還站得住?

### Takeaway
「審查主要找到的是可維護性問題,不是功能缺陷」和「覆蓋率與參與度跟品質有關」都有一手證據,而且 2026 年的 AI 研究沒有推翻。真正過時的是舊基線預設的情境:變更很小、有人讀。200 到 400 行的上限其實只來自廠商對單一團隊的研究,而堆疊 PR(stacked diffs)我找不到任何受控或同儕審查的效果證據。

### Cited Findings
- **基線 [新]【觀察性(同儕)】** Bacchelli & Bird,Expectations, Outcomes, and Challenges of Modern Code Review(ICSE 2013,Microsoft):觀察 17 位開發者,問卷 165 位經理與 873 位工程師。找缺陷是最主要的動機,實際留言裡缺陷相關只占一小部分,收穫更多在知識傳遞、團隊覺察和替代解法。「code and change understanding is the key aspect of code reviewing」。— [PDF](https://sback.it/publications/icse2013.pdf)
- **基線 [新]【觀察性(同儕)】** Sadowski 等,Modern Code Review: A Case Study at Google(ICSE-SEIP 2018):約 900 萬個變更、25,000 多位作者與審查者(2014-01 到 2016-07)。變更行數中位數 24;整個審查流程的中位延遲不到 4 小時;等第一次回饋,小變更中位不到 1 小時,很大的變更約 5 小時。每人每週審查平均 3.2 小時(中位 2.6);「The majority of changes are small, have one reviewer and no comments other than the authorization to commit」。— [PDF](https://sback.it/publications/icse2018seip.pdf)
- **基線 [新]【觀察性(同儕)】** McIntosh 等,The Impact of Code Review Coverage and Code Review Participation on Software Quality(Qt、VTK、ITK;PDF 頁首是 MSR '14,但實驗室頁面寫 2011,應是筆誤):覆蓋率與參與度都跟品質顯著相關;低覆蓋率估計多至 2 個、低參與度多至 5 個發佈後缺陷。— [PDF](https://rebels.cs.uwaterloo.ca/papers/msr2014_mcintosh.pdf);[摘要頁](https://www.swag.uwaterloo.ca/www/publications/the-impact-of-code-review-coverage-and-code-review-participation-on-software-quality-a-case-study-of-the-qt-vtk-and-itk-projects.html)
- **基線 [新]【觀察性(同儕)】** Beller 等,Modern Code Reviews in Open-Source Projects: Which Problems Do They Fix?(MSR 2014,人工分類 1,400 多個變更):可維護性對功能問題是「similar 75:25 ratio」;7–35% 的審查留言被丟棄;10–22% 的改動不是由明確留言引發。— [PDF](https://azaidman.github.io/publications/bellerMSR2014.pdf)
- **基線 [已知(迴圈工程篇一行帶過)]【廠商報告】** SmartBear 對 Cisco 一個團隊的研究:一次不超過 200–400 行;快過每小時 500 行後缺陷密度顯著下降;約 60 分鐘後表現下滑;「70-90% defect discovery」是廠商頁面的示意例子,沒有附來源。該頁未寫樣本數。— [SmartBear](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/)
- **[新]【觀察性(同儕,ICPC 2026)】** Crupi, Tufano, Bavota,Studying Quality Improvements Recommended via Manual and Automated Code Review(arXiv 2602.11925v1,2026-02-12):人工檢視 240 個 PR 的 739 則人類留言,其中 447 則標為相關。ChatGPT-4 建議的改動是人的「∼2.4× more」,但只抓到人類所提品質問題的 10%;抽 292 則多出來的留言,約 40% 有意義。結論是互補,不能當替代,也不能當省時手段。— [arXiv](https://arxiv.org/abs/2602.11925)
- **[新]【觀察性(預印本)】** 變更變大的新數據:在一家公司導入 AI 後,AI 寫的 PR 與其他 PR 比較,中位 66 行對 41 行(+0.45 log points)。— [He 等,arXiv 2607.01904v2](https://arxiv.org/abs/2607.01904)
- **堆疊 PR:** 這輪查到的多是工具廠商或部落格的宣稱,例如無來源的「40-60%」;[這篇部落格](https://www.softwareseni.com/how-stacked-pull-requests-and-context-engineering-reduce-review-load)自己說中小型公司的實證很薄。我沒有引用任何數字。

### Inferences
- 推論:75:25 這個比例在 AI 時代可能更重要。人花在審查上最常見的產出是可維護性,而 AI 程式的主要負面訊號也正落在這一塊(見第三節)。如果把審查全部交給「找 bug」的 AI,可能少的是這一塊,以及 Bacchelli 說的「理解」本身。
- 推論:200–400 行不是定律,只能當「單次注意力上限」的量級。比較站得住的是另一件事:變更小的時候審得快,Sadowski 的 24 行中位數也是在這種條件下量到的。

### Gaps
- SmartBear 原始研究未打開。搜尋摘要提到「2,500 次審查、320 萬行」,出處是二手網頁,未核對,不要引用。
- Czerwonka 等〈Code Reviews Do Not Find Bugs〉原文打不開(下載回的是 HTML)。「約 15% 留言指向缺陷」只見於[二手部落格](https://entropicthoughts.com/code-reviews-do-find-bugs),未核對。
- 查無 stacked diffs 的受控或同儕審查證據。這只代表我下過的查詢沒找到。
- 查無「AI 程式的 PR 行數上限」實測;舊的 200–400 行是否適用於 AI 程式,沒有直接資料。

## 有 AI 參與時,人會出什麼問題?(自動化偏誤、過度信任、注意力、理解債、技能退化)

### Takeaway
最直接的受控證據仍是 Tufano(ICSE 2025):AI 先給評論,人會把注意力鎖在 AI 指的位置,保留 89% 的發現,卻沒有多抓到高嚴重度問題。2026 年最強的新證據是 He 等的企業縱向研究:審查量翻倍後,多出來的負荷落在「沒留言就核准」,有留言的實質審查從約 39% 掉到約 21%,回退率卻沒有上升。也就是說,治理指標可能看不出人已經不再審了。理解受損有兩個隨機或組間實驗支持,但受試者都是學習情境,不是審查情境。

### Cited Findings
- **基線 [新]【同儕受控(ICSE 2025,樣本小)】** Tufano 等,Deep Learning-based Code Reviews: A Paradigm Shift or a Double-Edged Sword?(arXiv 2411.11401v3,2024-11-29):29 位專業開發者,三種處理:全手動(MCR)、ChatGPT Plus 自動評論起手(ACR)、假想的完美評論起手(CCR)。
  - 平均 89% 的 AI 發現被保留到最終審查。「Reviewers mostly focused on the code locations pointed out」。
  - ACR 找到的植入問題中位 50%,跟全手動一樣,而 AI 評論本身平均就涵蓋 42%,也就是人幾乎沒有再多找。
  - 只有低嚴重度問題多了,高嚴重度沒有。
  - 時間:MCR 平均 42 分鐘(中位 37),ACR 56(42),CCR 57(50)。但多元迴歸顯示沒有任何變數對時間有顯著影響,所以「更慢」不能算成立,只能說「沒有省時」。
  - 信心:3.5、3.7、3.8,差異不顯著。
  - 作者自承每種處理只有 24 個資料點,可能檢定力不足;受測程式是小型 Rosetta 程式。
  - 作者建議:等人交出評論之後才顯示 AI 評論。— [arXiv](https://arxiv.org/abs/2411.11401);[ICSE 2025 議程](https://conf.researchr.org/details/icse-2025/icse-2025-research-track/72/Deep-Learning-based-Code-Reviews-A-Paradigm-Shift-or-a-Double-Edged-Sword-)
- **基線 [新]【預印本受控(產業隨機安全試驗)】** Maddila 等,AI-Assisted Fixes to Code Review Comments at Scale(arXiv 2507.13499v1,2025-07-17,**Meta**,不是搜尋摘要誤寫的 Google)。把 AI 修補同時給作者和審查者看,審查時間變長(TimeInReview 5.5%,p=.029);改成審查者摺疊、只給作者看,就沒有迴歸(0.42%,p=.86)。實驗期 2024-10-17 到 11-21。機制:審查者「feeling a responsibility to check the AI patch」。原文內文與表格有出入:TimeSpent 內文寫 5.5%(p=.029),表格寫 6.7%(p≪.001)。— [arXiv](https://arxiv.org/abs/2507.13499)
- **[新]【觀察性(預印本,交錯雙重差分)】** He, Agarwal, Denisov-Blanch, Azaletskiy, Koyejo, Vasilescu,AI Writes Faster Than Humans Can Review(arXiv 2607.01904v2,2026-10-27):802 位開發者、196,212 個 PR(2024-01 到 2026-04),單一中型公司。
  - PR 量成長 3.1×,審查者只成長 1.5×,每人負荷約 2.0×;AI 寫的 PR 約占 90%。
  - 至少有一次人工審查的 PR 從 89% 掉到 68%;AI 審查從約 19% 升到約 84%。
  - 有人寫留言的實質審查從約 39% 掉到約 21%,沒留言的核准維持在約 50%;中位審查者的留言審查維持每月約 3 次,沒留言的核准約翻倍。
  - AI 寫的 PR 多約 9% 人類留言,從第一次人審到合併多約 20%,總週期多約 22%。
  - 回退比例略降,合併後修補持平。作者解讀為「evidence against an acute quality collapse」,但也說這些代理指標抓不到缺陷、事故與可維護性。「once review becomes lenient or automated, the gate itself has changed」。
  - 機器人約占審查紀錄的 38%。— [arXiv](https://arxiv.org/abs/2607.01904)
- **[新]【觀察性(預印本,灰色文獻理論建構)】** Agarwal, Miller, Kästner, Vasilescu,3100 Opinions on Code Review in an AI World(arXiv 2607.07980v1,2026-07-08):收 38,709 份工程部落格與 Reddit 討論串,分層抽 3,100 份,用 LLM 輔助編碼,得到 26 個構念與 67 條關係(64 條有方向、3 條有爭議)。主張審查是決定代理效果正負的控制點,正負號由團隊決定,不是 AI 決定;列出被低估的人的成本:理解債、所有權與知識傳遞流失、審查者技能退化。**重要反證:** 代理 PR「審得少、合得快、討論少」的趨勢,換同樣合理的分析選擇方向就翻轉。這是意見綜整,不是效果量測。— [arXiv](https://arxiv.org/abs/2607.07980)
- **[新]【觀察性(同儕,MSR 2026)】** Huang 等,More Code, Less Reuse(arXiv 2601.21276v1,2026-01-29;AIDev 資料):代理的改動重用較少、冗餘較高,但審查者對 AI PR 的情緒比對人類 PR 更中性或正面。全文我只讀到摘要段落。— [arXiv](https://arxiv.org/abs/2601.21276)
- **[已知(同篇 16.6% 已記)]【觀察性(預印本)】** Zhong 等,Human-AI Synergy in Agentic Code Review(arXiv 2603.15911v2,2026-10-26):278,790 段審查對話、300 個開源專案。超過 95% 的 AI 留言集中在改進與找缺陷,人類的回饋範圍更廣,包含理解、測試、知識傳遞;人審 AI 程式時來回多 11.8%;AI 建議採用率 16.6%,人類 56.5%;被採用的 AI 建議跟較大的複雜度與程式量增長有關。— [arXiv](https://arxiv.org/abs/2603.15911)
- **[新]【預印本受控(組間,學生)】** Balepur 等,(Im)Paired Programming(arXiv 2607.26375v1,2026-07-29,作者標註「In-progress Preprint」):54 位學生(代理 27、聊天 27)做網站。代理組初始任務較好,但理解顯著較差(p < 0.002,Cohen's d > 0.80);控制初始表現後,擴充任務的優勢反轉。理解分數:全自動接受 0.615(6 人)、逐檔看 0.777(7 人),但這兩組的背景能力也不同(0.603 對 0.714),有混淆。受試者知道自己理解較弱,仍偏好代理。— [arXiv](https://arxiv.org/abs/2607.26375)
- **[已知(總覽第 9 點)]【預印本受控(預註冊隨機實驗)】** Shen & Tamkin,How AI Impacts Skill Formation(arXiv 2601.20245v2,2026-02-01,Anthropic):主研究 n=52。分數差 4.15 分(27 分制),原文寫「17% score difference or 2 grade points」,d=0.738,p=0.010;完成時間沒有顯著加速(p=0.391);六種使用型態裡有三種保有學習。**量的是學新函式庫,不是審查。** 見最後一節對數字的核對。— [arXiv](https://arxiv.org/abs/2601.20245)
- **[新]【預印本受控(受試者內,註冊報告,EMSE 審查中)】** Burelli 等,Using Biometrics to Understand AI-Assisted Coding(arXiv 2606.20598v1,2026-05-19):腦電 θ/α 比與眨眼率的變化「consistent with reduced cognitive engagement」,受試者是學生。作者說 AI 輔助寫程式是認知上不同的活動。— [arXiv](https://arxiv.org/abs/2606.20598)
- **[新]【同儕受控(CHI 2026,只讀到摘要)】** Fan 等,When Help Hurts: Verification Load and Fatigue with AI Coding Assistants(DOI 10.1145/3772318.3791176):60 人做三個 Python 任務。AI 輔助反而讓 NASA-TLX 降 18.2 分、時間 32.1 降到 25.0 分鐘、正確性 OR 1.71;作者的「驗證負荷指數」部分解釋了跨任務的壓力與疲勞上升。這是反向證據:驗證有負荷,但不代表總負荷變高。ACM 全文回 403,摘要來自 [OpenAlex 中繼資料](https://api.openalex.org/works/doi:10.1145/3772318.3791176)。
- **[新]【觀察性質化(同儕,TOSEM 2025)】** Alami, Jensen, Ernst,Accountability in Code Review(arXiv 2502.15963):16 場訪談加焦點團體。可稽責感來自個人標準、專業操守、品質自豪與名聲;引入 LLM 審查會破壞這個過程,因為可稽責是相互的,而人不能向 LLM 負責(這一句來自[議程頁摘要](https://conf.researchr.org/details/chase-2026/chase-2026-journal-first/2/Accountability-in-Code-Review-The-Role-of-Intrinsic-Drivers-and-the-Impact-of-LLMs)與搜尋摘要,全文我只讀開頭)。同作者群的 [arXiv 2512.05309](https://arxiv.org/abs/2512.05309)(20 位工程師)比較同儕與 LLM 審查的情緒與投入,未細讀。
- **[已知(九類之外提過 Storey)]【意見】** Storey,From Technical Debt to Cognitive and Intent Debt(arXiv 2603.22106v4,2026-04-06):理解債是人的、意圖債是沒寫下來的,舉的是學生團隊案例,沒有量測。— [arXiv](https://arxiv.org/abs/2603.22106)
- **[已知]【廠商報告】** Sonar 2026 State of Code(2026-01-08,超過 1,100 位開發者):96% 不完全相信 AI 程式功能正確,只有 48% 說提交前一定檢查;38% 說審 AI 程式比審人的更費力。我只看到新聞稿層級,未核對題目措辭。— [Sonar 新聞稿](https://www.sonarsource.com/company/press-releases/sonar-data-reveals-critical-verification-gap-in-ai-coding/)

### Inferences
- 推論:Tufano 與 He 指向同一個機制。人的注意力被 AI 的輸出或工作量牽著走,結果是「看起來有審」。Tufano 的 89% 保留率與 He 的沉默核准,都是不需要太多認知投入的輸出。
- 推論:高「接受率」本身不是品質證據。Tufano 的 89% 保留沒有換來更多高嚴重度發現,Lumos 的高折入比例也該這樣看。
- 推論:回退率持平有兩種解讀,品質沒事,或者閘變鬆之後量不到了。He 的設計分不開這兩者,所以 Lumos 不該拿「逃逸沒有增加」直接證明審查有效。
- 推論:Alami 的「人不能向 LLM 負責」對單人情境是直接打擊:同儕壓力與名聲這兩個驅動力都不存在了,要靠機制補上,不能靠紀律。

### Gaps
- 查無 2025-11 之後、用真人審查代理 PR 的受控實驗(檢視注意力或缺陷偵測)。Tufano 仍是最接近的,而且用的是 2024 年模型與小程式。Burelli 等量的是寫程式,不是審查。
- 查無代理情境下 Tufano 的複製實驗。
- 技能退化(deskilling):只有灰色文獻與學習實驗,查無追蹤在職審查者技能變化的縱向受控研究。
- 查無直接以眼動或認知負荷量測「審 AI PR」的研究;Tang 等(2024)只在 Burelli 的文獻回顧裡看到,未打開。

## AI 寫的程式品質如何?審查要盯什麼?

### Takeaway
證據真的互相衝突。廠商報告與 Cursor 的雙重差分研究都顯示問題變多,可是兩篇大規模測量說實際差距不大,或沒有短期崩壞。比較一致的只有三點:可維護性(重複、複雜度)變差;通過自動評分的補丁,維護者願意合併的比例明顯較低(常態化後差 24.2 個百分點);安全通過率在模型進步時幾乎沒有動。DORA 2026 不會出刊,任何「DORA 2026 發現」的說法都要懷疑。

### Cited Findings
- **[已知(九類之外,只讀二手)→ 本輪讀原文]【觀察性(有對照的研究筆記,未同儕審查)】** METR,Many SWE-bench-Passing PRs Would Not Be Merged into Main(2026-03-10):4 位維護者審 296 個 AI PR,外加 47 個原始人類補丁(合併率約 68%)。常態化後,自動評分平均比維護者合併決定高 24.2 個百分點(SE 2.7);未常態化 34.9(SE 2.2)。後期模型的拒收主因包含程式品質,GPT-5 在程式品質上「substantially weaker」。限制:沒有 CI、靜態判斷、不能迭代、最新模型只到 Claude Sonnet 4.5;「we do not claim that this represents a fundamental capability limitation」。各模型合併率只在圖表裡,我無法取值。— [METR](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/)
- **[已知(九類之外,並已更正)]【預印本受控,但作者自認不可靠】** METR,We are Changing our Developer Productivity Experiment Design(2026-02-24):57 位開發者、143 個 repo、800 多項任務。原參與者 -18%(CI -38% 到 +9%),新參與者 -4%(CI -15% 到 +9%),區間都跨 0。METR 說這是「an unreliable signal」、「likely a lower-bound」。30% 到 50% 的人因不想不用 AI 而不交某些任務;同時跑多個代理的人時間紀錄不可靠。2025 年基線是 16 人慢 19%(CI +2% 到 +39%)。— [METR](https://metr.org/blog/2026-02-24-uplift-update/)
- **[已知(九類之外;篇名已改)]【觀察性(同儕,MSR 2026;交錯雙重差分)】** He 等,Speed at the Cost of Quality(arXiv 2511.04427v3,2026-01-26,早期版本題名不同):採用 Cursor 的 GitHub 專案對 1,380 個配對對照。第一個月 commits +55.4%、新增行數 +281.3%,之後消退;靜態分析警告 +30.26%(±6.66%)、複雜度 +41.64%(±7.62%)持續,重複行密度 +7.03%(±4.79%)。限制:採用時點用是否提交 Cursor 設定檔當代理。— [arXiv](https://arxiv.org/abs/2511.04427)
- **[新]【觀察性(預印本)】** Mao 等,A Large-Scale Comprehensive Measurement of AI-Generated Code(arXiv 2603.27130v3,2026-07-01):「real-world AI-Human differences on code-level metrics are rather small instead of more pronounced」,跟實驗室結果不同。樣本量我只讀到摘要,未深入。— [arXiv](https://arxiv.org/abs/2603.27130)
- **[新]【廠商報告】** Veracode 2026 GenAI Code Security Report(2026-07-28):約 44% 的生成任務帶入有風險的漏洞;安全通過率平均 56%,第一份報告 55%;語法接近 100% 正確。GPT-5.5 最高 68%。依 CWE:XSS 15%、log injection 12%、SQL injection 83%、加密演算法 87%。測的是獨立生成任務,不是真實 repo。全報告未打開,「11 個新模型、80 項任務」與語言別數字只見於搜尋摘要,未核對。— [Veracode 部落格](https://www.veracode.com/blog/2026-genai-code-security-report-ai-risk);[資訊圖 PDF](https://www.veracode.com/wp-content/uploads/2026-GenAI-Report-Infographic.pdf)
- **[新(CodeRabbit 的工具功能有記,這份報告沒有)]【廠商報告】** CodeRabbit,State of AI vs Human Code Generation(2025-12-17):470 個開源 PR(320 個 AI 共同作者、150 個純人類),每 PR 平均 10.83 對 6.45 個問題,約 1.7×;可讀性超過 3×,邏輯與正確性多 75%。作者身份靠訊號推斷,自承「cannot guarantee」;量測儀器是廠商自家審查工具;頁面只說按每 100 PR 常態化,沒說按行數。— [CodeRabbit](https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report)
- **[已知(九類之外,同樣未複驗)]【廠商報告,原文未打開】** GitClear,The Maintainability Gap(2026):6.23 億筆程式變更;每百萬變更行的區塊重複從 2023 年 40.3 到 2026 年迄今 73.0(+81%);長期更新比例從 1.7% 到 0.46%(-74%)。GitClear 頁面回 403,這些數字只來自[搜尋摘要對其頁面的節錄](https://gitclear.com/the_ai_code_quality_maintainability_gap),這輪仍未能驗證。「2026 年迄今」可能不完整。
- **[已知(九類之外記了放大器與 5,000 份問卷;吞吐與穩定的方向是新補的)]【廠商報告】** DORA 2025(2025-09):近 5,000 人問卷;90% 使用 AI;「a positive relationship」對交付吞吐量,但「a negative relationship with software delivery stability」;30% 對 AI 程式很少或沒有信任。沒有查到百分比。— [Google Cloud 公告](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report)
- **[新]** DORA 在 2026-09-03 於 LinkedIn 宣布不做年度問卷、不出 2026 年報告;Google 未說明原因,前負責人 Nathen Harvey 轉往 AWS。這是 LeadDev 的報導,我沒看到 LinkedIn 原文。— [LeadDev](https://leaddev.com/?p=36788);[DORA 出版品頁](https://dora.dev/publications/)只列到 2025 版。
- **[已知(資料集)/ 新(各篇)]【觀察性(同儕,MSR 2026 挖掘挑戰,AIDev)】**
  - [2601.00753v2](https://arxiv.org/abs/2601.00753)(DOI 10.1145/3793302.3793609):33,707 個代理 PR,28.3% 幾乎立刻合併;代理放棄率原文內部不一致,RQ2 內文寫「overall ghosting rate of 3.8%」,Finding 2 寫「10% ghosting」,引用時要註明;
  - [2601.15195](https://arxiv.org/abs/2601.15195)(33k PR,人工看 600 個):文件、CI、建置類任務合併率最高,效能與修 bug 最差;未合併的改動較大、改更多檔、常過不了 CI;拒收原因包含重複 PR、不想要的功能、代理搞錯方向;
  - [2601.04886v2](https://arxiv.org/abs/2601.04886):23,247 個 PR,1.7% 有嚴重的訊息與程式不一致,最常見是描述宣稱了沒做的改動(45.4%);這些 PR 接受率 28.3% 對 80.0%,合併時間 55.8 對 16.0 小時;
  - [2601.19287v1](https://arxiv.org/abs/2601.19287)(Haider & Zimmermann,3,177 個 PR 的 19,450 則行內留言,未標同儕):除功能外,主要聚焦文件缺口、重構、風格、測試與安全。
- **[新]【觀察性(同儕,EASE 2026)】** Duma 等,These Aren't the Reviews You're Looking For(arXiv 2605.02273v1):全樣本 33,596 個代理 PR 裡 61.38% 沒有審查;但限定在同一批 repo 比較,代理 PR 沒審查 28.92%(9,616 個),人類 PR 34.52%(5,574 個)。有審查的代理 PR 裡,純人類審查 8.08%,人類 PR 是 25.21%。人類留言裡 25.92% 是在指揮代理,人類 PR 上只有 1.63%。沒有留言不等於沒看(可能沉默核准)。— [arXiv](https://arxiv.org/abs/2605.02273)
- **[新]【觀察性(預印本)】** He 等(2607.01904):上一節的數字。代理 PR 花的人審時間更多,但公司靠機器人和自動核准繞過瓶頸,所以估計值偏保守。— [arXiv](https://arxiv.org/abs/2607.01904)

### Inferences
- 推論:「AI 程式比較差」的量值高度依賴資料來源與定義,不要拿單一倍數做決策。Mao 與 He(2607.01904)是最大的兩個反向或中性訊號,CodeRabbit 與 GitClear 則有商業利益。
- 推論:審查該盯的清單裡,證據較扎實的是:重複與重用失敗(2601.21276、He 2511.04427)、宣稱與實作不符(2601.04886)、弱化 CI 或測試(GitHub 實務建議,見下節)、輸出編碼與 log 注入(Veracode 的 CWE 分布)。
- 推論:Duma 的兩組數字說明,「代理 PR 大多沒人審」主要是 repo 組成的效果,不是作者身份的效果。這也是 Agarwal 警告的分析選擇翻轉的實例。

### Gaps
- 沒有一篇研究同時有隨機分派、真實 repo、最新模型和缺陷或事故級結果。
- 查無「審查者花在代理 PR 的實際分鐘數」的直接量測,只有輪數與週期。
- DORA 2025 全報告 PDF 未打開,所以「多少百分比的不穩定」我無法給。2024 年那個 7.2% 的數字只在二手網頁看到,且有文章把 2024、2025 混用。
- METR 2026-05 問卷文章未打開。

## 人該親自檢查什麼?什麼可以交出去?

### Takeaway
「審意圖或規格、別審每一行」目前是實務者的共識,但**沒有任何受控研究證明它比行級審查抓到更多缺陷**。有證據支持的是更窄的幾件事:AI 評論要晚於人的判斷才出現、人的注意力用結構訊號分流、把 AI 噪音藏起來不給審查者。法規與問責仍要求保留具名的人。

### Cited Findings
- **[新]【規範文字/產品事實】** GitHub Copilot code review 2026-09-01 公開預覽可核准 PR:「Copilot can submit an approval that counts toward the repository's required-approvals rule」,預設關閉;可依路徑限制;新提交會撤銷核准。「An approval assessment alone does not count toward merge requirements」。— [GitHub Changelog](https://github.blog/changelog/2026-09-01-copilot-code-review-can-now-approve-pull-requests)
- **[新]【觀察性(同儕,MSR 2026 挖掘挑戰)】** 風險分流:開 PR 當下用結構特徵預測高成本 PR,AUC 0.957;審 20% 可涵蓋 69%。摘要一處寫「69% of the high-effort PRs」,另一處寫「69% of total review effort」,定義要回原文確認。文字特徵幾乎沒有加分。— [arXiv 2601.00753](https://arxiv.org/abs/2601.00753)
- **[新]【觀察性(預印本)】** Pansuriya 等(arXiv 2607.12057v1):接受與否可預測(F1 > 0.95),但審查成本只能部分解釋;結論是「advisory tools rather than automated decision-makers」。— [arXiv](https://arxiv.org/abs/2607.12057)
- **[新]【預印本基準】** c-CRAB,Code Review Agent Benchmark(arXiv 2603.23448v3,2026-04-07,部分作者來自 SonarSource):把人的審查轉成可執行測試當考官;現有審查代理合起來只解決約 40% 的題目,而且關注面與人不同。— [arXiv](https://arxiv.org/abs/2603.23448)
- **[新]【觀察性質化(預印本)】** Huang 等,Professional Software Developers Don't Vibe, They Control(arXiv 2512.14012v2,2026-08-18):13 人實地觀察、99 人問卷(2025-08 到 10)。資深開發者保留設計與實作的主導權;13 位觀察對象都以某種程度控制實作,不把信任完全交出。— [arXiv](https://arxiv.org/abs/2512.14012)
- **[已知]【預印本受控,ICSE 2027 待刊】** Alexopoulos 等,When AI Agrees Too Much(arXiv 2603.18740v5,2026-10-27):在 PR 中繼資料寫「沒問題」就能讓 LLM 漏掉漏洞。GPT-4o-mini 從 240/247(97.2%)掉到 9/247(3.6%);其他模型掉 16 到 60 個百分點;Claude Opus 4.5 只掉 6.9%。— [arXiv](https://arxiv.org/abs/2603.18740)
- **[新]【意見,作者無實證】** Monperrus,The End of Code Review(arXiv 2606.13175v1,2026-06-11):主張審查的每個目標都能由代理達成;人審保留給「high-risk changes, novel architecture choices, and regulated code paths where a named human must bear legal accountability」。這篇是立場文,沒有實驗。c-CRAB 的 40% 是目前最接近的反面實測,但兩者沒有直接對話。— [arXiv](https://arxiv.org/abs/2606.13175)
- **[新]【意見,作者賣審查工具】** Ankit Jain(Aviator 創辦人),How to Kill the Code Review(Latent Space,2026-03-02,編者註明「not there yet」):人審規格與驗收條件,機器過多層確定性閘;驗證條件要來自規格,不是來自實作。引用 Faros 的「PR 多 98%、審查時間多 91%」是廠商資料。— [Latent Space](https://www.latent.space/p/reviews-dead)
- **[新]【意見,廠商】** Semgrep,Daghan Altas(2026-10-09):AI 審每個變更、例行的自動核准、重大的升給人。引用 He 等的研究。— [Semgrep](https://semgrep.dev/blog/2026/end-is-nigh-for-code-review/)
- **[新]【意見,廠商實務】** GitHub 部落格(Andrea Griffiths,2026-05-07):人該看的是:任何弱化 CI 的改動一律擋、先看 CI 再看應用程式、找重複邏輯、端到端追一條關鍵路徑、要求一個在舊行為上會失敗的新測試、LLM 工作流的提示注入與權限、大 PR 先要計劃。— [GitHub Blog](https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/)
- **[新]【意見】** Simon Willison(2025-12-18):「Your job is to deliver code you have proven to work」、「A computer can never be held accountable. That's your job as the human in the loop」。— [Willison](https://simonwillison.net/2025/Dec/18/code-proven-to-work/)
- 設計實證的三條旁證:Tufano 建議把 AI 評論延後到人交出之後;Meta 把 AI 修補摺疊後審查者不再變慢;Facebook 同一個分析放在 diff 時修復率超過 70%、批次約 0%(見噪音節)。

### Inferences
以下是我的綜合判斷,不是某篇研究的結論。依「證據強度」分三層:

| 決定權 | 建議 | 依據 |
|---|---|---|
| 人保留 | 這件事該不該做、規格與驗收條件、不可逆與高風險路徑(登入、付款、資料遷移、發布)、接受風險 | Monperrus、Jain、Willison 都同意(意見);SLSA 與問責研究支持 |
| 機器先擋、人只看結果 | 測試弱化、CI 改動、依賴、重複邏輯、宣稱與實作不符 | 2601.04886、2601.21276、Veracode、GitHub 實務 |
| 可交給 AI 或自動通過 | 小而結構單純的文件、CI、建置類變更 | 2601.15195、2601.00753;但沒有事故級驗證,要留抽查 |

- 推論:AI 審查應拿不到作者寫的「這沒問題」框架(Alexopoulos),而人應該拿到「AI 找了什麼」之前先自己判斷,或者至少不要讓 AI 清單成為唯一入口(Tufano)。
- 推論:規格閘與合約測試這類「人寫條件、機器驗」的做法,是目前實務意見最集中的方向,但它的效果沒有被量過。Lumos 自己若量到,等於在補世界的缺口。

### Gaps
- **最大的缺口:** 查無比較「意圖或規格審查」與「行級審查」缺陷偵測效果的受控研究。
- 查無「人看摘要或審查導覽」是否改善發現率的受控研究。
- 查無自動核准上線後事故率的受控或準實驗證據;只有 GitHub issue 與部落格層級的提議。
- Addy Osmani 的 O'Reilly〈Agentic Code Review〉我找不到原文,只有二手摘要,所以不引用。

## 只有一個人、AI 審 AI 時,什麼方法有用?

### Takeaway
查無直接研究「單人開發者監督代理」的實證;以下都是從機器互審的實驗推過來的。全新會談的第二次審查比同會談再看一次好,但**還沒證明比第一次自審好**,作者已撤回 v1 較強的主張。換模型能多抓到一部分,但混著審查者能力差異,而且方向不對稱,換錯還會變差。真正硬的保證來自可執行的驗證:自審可能「說得頭頭是道卻是錯的」。

### Cited Findings
- **[新]【預印本受控,單一作者,v2 重大修正】** Song,Cross-Context Review(arXiv 2603.12123v2,2026-10-01):30 個成品、150 個植入錯誤,單一模型 Claude Opus 4.6。全新會談審查(CCR)F1 28.6%,勝過同會談的第二次審查(SR2,21.7%;三輪平均 Holm 校正 p=0.004)。但對第一次同會談自審(SR,27.1%;p=0.26)與帶脈絡的子代理(SA,23.8%;p=0.057)都不顯著。作者原話:資料顯示「context separation rescues a second look, not that it beats looking once」;v1 說在所有輪都成立是不準確的。CCR 與 SR2 的審查語言也不同(英文對韓文),比較不乾淨。絕對分數低。— [arXiv](https://arxiv.org/abs/2603.12123)
- **[已知(迴圈工程篇的更正中提過)]【預印本受控,單一作者】** Song,When Does a Second Model Help?(arXiv 2610.01471v2,2026-10-06):900 場審查、30 個成品、150 個植入錯誤、10 種條件、三個審查模型(兩家)。
  - 頂級跨模型與同模型全新會談的 F1 沒有顯著差異,作者強調「does not establish equivalence」;
  - 兩者重疊 Jaccard 41.2%;
  - 同樣兩次呼叫,一次 CCR 加一次跨模型配到 56.7% 的植入錯誤,兩次 CCR 是 42.7%(Holm p=.006),但對兩次頂級跨模型不顯著,所以模型差異與能力差異分不開;
  - 程式成品上 CCR 較好(F1 40.7%),文件上跨模型較好(至多 42.1%);
  - 輕量跨模型模型不比同模型好。
  - 來源狀況:稽核時排除一輪來源可疑的基線(該輪 92% 的發現描述逐字出現在寫檔腳本裡),另排除 14 個失敗呼叫;所有成品來自單一生成者;GPT-5.4 經 Codex CLI 跑時工作目錄沒有紀錄。— [arXiv](https://arxiv.org/abs/2610.01471)
- **[新,但只看到轉述]** 同作者 D-CCR(Song 2026c)據報重複審查輪次會讓誤報增加 62% 且召回沒提升,作者歸因於同模型放大既有的錯誤信心,且那是同會談重複。我沒打開原文,以上只來自 2610.01471 的文獻段落。— [arXiv 2610.01471](https://arxiv.org/abs/2610.01471)
- **[新]【預印本受控(工作坊,Agentic SE @ KDD'26)】** Xiang 等,Cross-Model LLM Code Review(arXiv 2607.21656v1,2026-07-22):116 題 LiveCodeBench,審查者不能跑測試。Claude Opus 4.7 審 Codex GPT-5.5 的草稿,通過率 71.6% 升到 89.7%(p_BH=.001);Codex 自審升到 84.5%(p_BH=.022);反向 Codex 審 Claude,91.4% **降到** 82.8%(p_BH=.046);Claude 自審不變。限制:演算法題,作者稱是探索性、不足以定排名。— [arXiv](https://arxiv.org/abs/2607.21656)
- **[新]【預印本受控(作者任職 AWS)】** Reddy 等,Articulate but Wrong(arXiv 2605.21537v1,2026-05-20):11 個模型、1,980 次現代化呼叫。262 個語意漂移裡,83 個(31.7%)被產生它的同一模型放行;每模型放行率從 0% 到 100%,雙峰分布,而且跟漂移率、能力都不對應;有模型能明確講出 Py2/Py3 差異,然後仍宣告行為不變。難題在不同模型間相關(Pearson r=0.52)。— [arXiv](https://arxiv.org/abs/2605.21537)
- **[新]【預印本基準】** c-CRAB 把人的審查回饋轉成可執行測試當留出考官,是把判斷變成機器可驗的一個具體做法。— [arXiv 2603.23448](https://arxiv.org/abs/2603.23448)
- **[新]【觀察性(同儕,MSR 2026)】** Chowdhury 等,From Industry Claims to Empirical Reality(arXiv 2604.03196v1,DOI 10.1145/3793302.3793614):分析 3,109 個 PR,只有審查代理時合併率 45.20%,只有人時 68.37%。60.2% 被關閉的純代理審查 PR 訊噪比落在 0–30%;13 個審查代理裡 12 個平均訊號低於 60%。屬相關性:難 PR 可能本來就留給代理。樣本裡的純代理關閉 PR 只有 98 個。— [arXiv](https://arxiv.org/abs/2604.03196)
- **[已知]** SLSA 裡單人專案拿不到兩人審查的第四級(見治理節);[arXiv 2409.05014](https://arxiv.org/pdf/2409.05014) 指出很多開源專案只有一位維護者,這一條我只看到搜尋摘要。

### Inferences
- 推論:把 Lumos 的「乾淨席」當成**成本低的合理預設**是對的,但不要當成已被證明更強。最強的說法是「不要在同一會談重看第二次」。
- 推論:外家席的價值更像「偶爾多抓到別的」,而且取決於審查者能力,不是換家族就有效。Xiang 的 −8.6 個百分點提醒:低能力審查者可能把好草稿改壞。這支持「審查者輸出要過辯方或驗證」,不支持自動套用修正。
- 推論:Reddy 的 r=0.52 與雙峰放行率合起來的意思是:不同模型會栽在同樣的題目上,而某模型會不會發現自己的錯很難事先知道。所以單人情境下,最後防線應是行為測試或可執行重現,不是另一個模型的同意。
- 推論(注意力分配):單人的稀缺資源是裁定次數。合理的組合是:結構分流(20% 的高成本變更)、裁定前先自己說一句「我預期它改了什麼」再看 AI 結果(Tufano 的順序)、每件要人裁的事都帶可驗證的證據,不是摘要。這個組合本身沒有被實驗驗證。
- 推論:METR 提到同時跑多個代理時時間紀錄不可靠,單人並行多專案時連「花了多少注意力」都難量,自家量測要改記裁定次數與等待時間,不要記工時。

### Gaps
- **查無針對單人開發者、無人類同儕的審查研究。** 上述全是機器對機器的實驗或多人團隊的觀察,外推到單人是我的推論。
- Song 系列全部出自同一位作者與公司,植入錯誤、單一生成者;查無獨立複現。
- 查無真實 repo 上「全新會談 vs. 同會談 vs. 跨模型」的逃逸缺陷比較。
- 查無「人看多少 AI 審查結果才會開始蓋章」的數量研究。

## 一個人能真正處理多少發現?靜態分析的告警疲勞經驗能套到 LLM 審查嗎?

### Takeaway
靜態分析給了清楚的設計規則:發現要出現在工作流程當下、要可行動、只看改動行、有效誤報低於 10%,否則工具被放生。LLM 審查目前遠遠達不到這個門檻,依定義採納率落在 0.9% 到 72.9%,最常見的被拒理由是「專案脈絡 AI 看不到」。但**沒有研究直接量過人能處理多少條、或 LLM 噪音與人的遺漏率之間的劑量關係**,所以遷移是推論。

### Cited Findings
- **基線 [已知]【觀察性(同儕)】** Sadowski 等,Tricorder(ICSE 2015):有效誤報定義是使用者選擇不處理的報告,從開發者角度定義;審查時「We still enforce a very low effective false positive rate here (< 10%)」,而且預設只顯示改動行;「not-useful rate」達 10% 就留校察看,超過 25% 可能直接關掉。腳註說 10% 門檻與 Coverity 等平台相同。— [PDF](https://www.cs.umd.edu/class/spring2019/cmsc414/papers/tricorder-building-a-program-analysis-ecosystem.pdf)
- **基線 [已知]【觀察性(同儕)】** Sadowski 等,Lessons from Building Static Analysis Tools at Google(CACM 2018):審查檢查要「Produce less than 10% effective false positives」、可理解、可行動;編譯器檢查要求零有效誤報。FindBugs 整合被拿掉,原因之一就是有效誤報讓開發者失去信心。— [PDF](https://6826.csail.mit.edu/2020/papers/google-analysis-cacm.pdf)
- **基線 [已知(評測、技術棧篇提過 Infer 或 diff time)]【觀察性(同儕)】** Distefano 等,Scaling Static Analyses at Facebook(CACM 2019):「diff time deployment saw a 70% fix rate」,批次清單約 0%;同一個分析、同樣的誤報率。機制是免除切換情境。— [PDF](https://6826.csail.mit.edu/2020/papers/facebook-infer-cacm.pdf)
- **基線 [新]** Beller:連人類審查留言也有 7–35% 被丟棄。人的留言也不是全部被採納。— [PDF](https://azaidman.github.io/publications/bellerMSR2014.pdf)
- **[已知]【觀察性(預印本)】** Sun 等,Does AI Code Review Lead to Code Changes?(arXiv 2508.18771v2,2026-04-25,Treude 為作者之一):16 個審查 Action、178 個 repo、超過 22,000 則留言。有效且被處理的比例 0.9%–19.2%,人類 60%;hunk 級 6.5%–19.2%,檔案級 0.9%–4.2%。簡潔、帶程式碼、手動觸發的較有效;「each code change automatically leads to a review comment, regardless of whether a comment is warranted. This leads to low-precision output and reviewer fatigue」(這句是作者判斷,不是量測)。— [arXiv](https://arxiv.org/abs/2508.18771)
- **[新]【觀察性(預印本)】** Cynthia 等,Go Home Copilot, You're Drunk(arXiv 2607.21997v2,2026-07-29):54,713 則代理留言、Python 專案(摘要寫 342 個 repo,內文 341)。解決率 Copilot 72.9%、Cursor 67.2%、Codex 54.8%(RQ3 段落又寫 Codex 53%)。行內建議 OR 1.617,是最強正向預測;有解釋 OR 0.593;長度 OR 0.926。模型 AUC 只有 0.58。470 段未解決討論裡,114 段其實已處理只是沒標記;真正不採納的類別裡最多是「Intentional Design Decision」(112),其次「Incorrect Suggestion」(67)。解決不等於有用。— [arXiv](https://arxiv.org/abs/2607.21997)
- **[已知]** 16.6% 對 56.5%(2603.15911);36.4% 接受、7.3% 討論、56.3% 拒絕(arXiv 2607.03316,既有更正已說分母只算有回覆的留言)。— [arXiv 2603.15911](https://arxiv.org/abs/2603.15911)
- **[新]** Crupi 等:ChatGPT 多出來的留言約 40% 有意義,反過來約 60% 不值得看(研究員自算)。— [arXiv 2602.11925](https://arxiv.org/abs/2602.11925)
- **[新]【廠商報告,只見搜尋摘要】** Qodo 2026 調查(500 位美國開發者):36.4% 說審 AI 程式時間一樣但認知負擔更大。未打開原文。

### Inferences
- 推論:把 Google 的門檻套到 LLM,「被處理」要大於 90%,目前沒有任何工具接近,但定義不同,不能直接比。Tricorder 的分母是開發者點按,LLM 研究的分母各異。**建議 Lumos 引用時永遠帶分母定義。**
- 推論:Facebook 的 70 比 0 最能遷移,因為它講的是位置不是工具。Lumos 的推送前閘已經對上「當下」這個條件;把發現做成批次報告或週報的,大概會是那個 0%。
- 推論:最常見的不解決理由是「AI 看不到專案限制」,所以 Lumos 把合約與事故推給審查席,方向上是對的。這點有間接支持,沒有對照實驗。
- 推論:有上限的容量估計只能給量級。Sadowski 每週約 3 小時、SmartBear 約 60 分鐘;單人一次裁定 10 條以上時,很可能已超過有品質的注意力。這個數字是我的估計,沒有直接研究。
- 推論:採納率高不代表準確,採納率低也可能只是沒有回覆。Lumos 應同時量「人看了多少」和「事後證明為真多少」。

### Gaps
- 查無直接量測「一輪能處理幾條發現」的研究,也查無 LLM 審查的「精確率對人的遺漏率」劑量關係。
- Coverity 原始論文(Bessey 2010)未打開,10% 只透過 Tricorder 腳註轉述。
- 廠商基準(Martian 等)只見廠商轉述,未引用。

## 治理與問責:稽核軌跡、來源、合規有什麼具體要求?

### Takeaway
目前沒有規範直接規定「AI 程式碼審查該怎麼做」。SLSA v1.2 把審查者定義為人,AI 不算 trusted person,所以 AI 審查加單人不可能達到 Source Level 4。歐盟 AI 法第 14 條只適用高風險系統,高風險時程已延到 2027-12-02;一般開發工具是否適用我沒查到權威說法。SOC 2 查無任何可靠的 AI 審查要求。可用的共通原則只有一條:帳本能證明誰做了什麼,但證明不了人有沒有真的審。

### Cited Findings
- **[新]【規範文字】** SLSA v1.2 Source Track(Approved):Level 4「Changes in protected branches MUST be agreed to by two or more trusted persons prior to submission」;trusted person 定義是「A human who is authorized by the organization to propose and approve changes to the source」;trusted robot 是「Automation authorized by the organization to act in explicitly defined contexts」,例子是匯入、遷移機器人與 Dependabot,組織可給永久例外。頁面沒有提到 AI 代理。— [SLSA](https://slsa.dev/spec/v1.2/source-requirements)
- **[新]** SLSA 部落格的 2025-12-18 客座文雖然題名提到 Robots,但全文**沒有談 AI 代理**,不能當 SLSA 對代理的立場。— [SLSA Blog](https://slsa.dev/blog/2025/12/supply-chain-robots-slsa)
- **[已知(只見版本發布與守衛篇提到 SLSA)]** 既有筆記寫版本發布計劃明列不做 SLSA provenance。
- **[新]【規範文字,經法律媒體轉述】** Regulation (EU) 2026/1744(AI Omnibus)2026-07-24 刊登、2026-07-27 生效:Annex III 獨立高風險系統延到 2027-12-02,嵌入產品的高風險系統到 2028-08-02;透明度義務從 2026-08-02 起續行,只有部分機器可讀標記要求對既有系統有四個月寬限。— [NatLawReview](https://natlawreview.com/article/eu-digital-omnibus-ai-enters-force);[Addleshaw Goddard](https://www.addleshawgoddard.com/en/insights/insights-briefings/2026/technology/eu-ai-act-ai-omnibus-formally-adopted/)(2026-07-01 刊出時尚未公布,寬限寫到 2026-12-02)
- **[新]【觀察性文件分析(預印本)】** Manita & Amari,Regulating the Machine Contributor(arXiv 2606.14594v1,2026-06-12):CLA、DCO 等都預設有法律上可負責的人;代理沒有這個地位。作者認為第 14 條只要求監督能力,不要求可展示的理解,業界分析也指出法條「does not define what separates meaningful oversight from rubber-stamping」。某些開源專案要求貢獻者在審查時能回答問題,作者認為這比法條還嚴。第 14 條只適用高風險。— [arXiv](https://arxiv.org/abs/2606.14594)
- **[新]【方法學警告,同儕】** Duma 等(EASE 2026):挖掘研究中的審查數字不能直接當人類監督的指標。He 等:機器人約占審查紀錄 38%,合併率在閘變鬆後意義改變。— [arXiv 2605.02273](https://arxiv.org/abs/2605.02273);[arXiv 2607.01904](https://arxiv.org/abs/2607.01904)
- **[新]【產品事實】** Copilot 的核准可算入 required approvals,預設關閉。— [GitHub Changelog](https://github.blog/changelog/2026-09-01-copilot-code-review-can-now-approve-pull-requests)
- **【意見,未打開】** 有部落格聲稱 2026-08-02 起第 50 條會處罰「證明不了哪段軟體是 AI 寫的」的組織,我查不到任何權威來源支持,應視為不實;第 50 條主要是透明度與內容標記,我沒讀到它涵蓋原始碼的依據。— [來源僅見搜尋結果](https://lablab.ai/ai-hackathons/ibm-bob-hackathon/ctrlcats/pedigree)

### Inferences
- 推論:Copilot 核准可能滿足 GitHub 的必要核准規則,但依 SLSA 定義不算 trusted person,兩者不能混為一談。
- 推論:單人專案若要對外宣稱 Source Level 4,不可行;能誠實宣稱的最多是 Level 3 加上「留痕綁版本」。這類宣稱要避免把 AI 席位說成審查者。這是我對規格文字的解讀,不是法律意見。
- 推論:對 Lumos,留痕應分開「機器判定」與「人裁定」,並帶上人實際看了什麼(例如裁定前的三問回答)。否則稽核軌跡只能證明核准發生過。

### Gaps
- SOC 2:查無 AICPA 或稽核方對 AI 審查、AI 生成程式的權威指引。搜到的都是廠商文案,我不引用。
- 查無權威來源判定 AI 審查工具本身是否屬 AI 法高風險;依條文邏輯很可能不屬於(一般開發工具不在 Annex III 明列類別),但這是推論,需法律專業確認。
- 查無 SLSA 對 AI 代理身份的官方立場。
- 第 50 條最終寬限日的官方公報文字未親自打開。
- 本節不構成法律意見。

## 本輪證據與既有筆記的衝突有哪些?

### Takeaway
沒有發現會推翻總覽大方向的證據,人是瓶頸這點反而被大幅強化。但有五處要修正或降低信心:廠商「刻意不擋」已不成立、換家族的價值不只在判決、乾淨席的效果被說得太滿的風險、Anthropic 分數對不上、以及用野外接受率當對照。

### Cited Findings
- **衝突 1(總覽〈對 Lumos 前提的挑戰〉第 8 點「廠商刻意讓審查結果不擋」):** 部分過時。GitHub Copilot 2026-09-01 起,開啟後可算入 required approvals。不過預設關閉、可限路徑,所以是「廠商開始提供擋或放行的權力」,不是全面改變。— [GitHub Changelog](https://github.blog/changelog/2026-09-01-copilot-code-review-can-now-approve-pull-requests)
- **衝突 2(總覽〈一頁結論〉第 5 點「換模型家族的價值在判決、不在找錯」):** 太絕對。Song 2610.01471 兩次呼叫的召回 56.7% 對 42.7%,Jaccard 41.2%,代表換家族在「找錯」上也有增量。但同一篇也說模型差異與能力差異分不開,所以正確寫法是「兩邊都可能有增量,歸因未定」。迴圈工程篇的更正已點到這點,總覽主句還沒改。— [arXiv 2610.01471](https://arxiv.org/abs/2610.01471)
- **衝突 3(總覽第 9 點「理解測驗 50% 對手寫 67%」):** 無法在論文內文核對。論文文字是 4.15 分差、27 分制、「17% score difference or 2 grade points」;50% 與 67% 沒有出現在抽出的文字裡,可能來自圖表或部落格。另外 4.15/27 約 15.4%,跟原文的 17% 對不上(研究員自算),原因未查。建議改引 d=0.738、p=0.010,並註明受試者是在學新函式庫,不是審查。— [arXiv 2601.20245](https://arxiv.org/abs/2601.20245)
- **衝突 4(跨類優先順序第 12 條、挑戰第 6 點「折入 98.8% 對野外被拒 56.3%」):** 比較基準不穩。不同研究的採納率從 0.9% 到 72.9%,全看分母與定義;而 Tufano 的 89% 保留又沒有帶來更多高嚴重度發現。所以 98.8% 不該只拿野外拒絕率對照,要獨立抽查才有意義(抽查這條建議本身成立)。— [arXiv 2607.21997](https://arxiv.org/abs/2607.21997);[arXiv 2411.11401](https://arxiv.org/abs/2411.11401)
- **需降低信心(迴圈工程篇「Lumos 能貢獻的是每輪換乾淨席」,以及記憶中的乾淨席慣例):** 沒有錯,但外部證據比想像的弱。Song v2 已撤回「CCR 勝過第一次自審」;2610.01471 說 CCR 只比 SR 多 1.5 個百分點 F1,不顯著。可講的是「不要同會談再看一次」。— [arXiv 2603.12123](https://arxiv.org/abs/2603.12123)
- **狀態更新(九類之外):** METR 維護者研究從「只讀二手」更新為已讀原文;24.2 個百分點是常態化後的值,未常態化是 34.9。— [METR](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/)
- **狀態更新:** DORA 2026 年報不會出現;日後引用 DORA 要標 2025 為最後一版。— [LeadDev](https://leaddev.com/?p=36788)
- **搜尋摘要自己的錯(提醒報告撰寫者別引):** 2507.13499 被說成 Google,實為 Meta;McIntosh 被寫成 2011,PDF 是 MSR '14;Tricorder 的 10% 被說查不到,其實原文有;Song 系列被摘要成「全新會談最受一致支持」,比原文強;「大部分代理 PR 沒人審」與 Duma 的同 repo 比較數字不同方向。

### Inferences
- 推論:總覽第 9 點「人變成瓶頸」現在有強得多的量化根據(He 2607.01904)。值得把「實質審查比例」當 Lumos 的人裁健康指標,看人裁時有沒有寫下理由,而不只看有沒有按下同意。
- 推論:委派地圖裡「伺服器端最後防線委派給分支保護」要加一句:必要核准現在可能是機器人,要看核准者身份。

### Gaps
- 我比對的是總覽與十篇定稿的關鍵字,沒有逐條讀完十篇,衝突清單可能不完整。
- 「[新]」只代表上述筆記查不到,不代表別的筆記沒寫過;核對範圍是 `Projects/` 目錄的 grep。
- 查無的結論都只反映這輪的查詢;WebSearch 只回美國結果,也沒有派乾淨 agent 複查。若「查無」要用來決定建不建東西,依專案規則要另派一次。
