# 多審查員、對抗驗證與停止規則:自動代碼審查的證據(截至 2026-11-01)

讀法(給報告撰寫者):

- 新舊標記:**[新]**=在 repo 的 `docs/`、`governance/` 全文搜尋不到這個編號;**[已知]**=repo 已有紀錄(標明哪一份);**[已知,細節新]**=編號已知,但這裡補的數字或解讀既有筆記沒寫。
- 證據等級:**[同儕受控]** 已被會議或期刊接受的受控比較或基準;**[預印受控]** 未審的受控比較;**[觀測]** 探勘、個案、基準上的非隨機比較;**[意見]** 廠商自述、部落格、GitHub issue。
- 讀取層級:**原文已核**=我用程式在原文(HTML 或 PDF 抽字)比對過該數字;**全文摘錄**=打開全文,但由抓取工具的摘要模型轉述,數字沒逐字比對;**僅摘要**=只讀 arXiv 摘要頁;**僅搜尋摘錄**=沒打開原文,只看到搜尋引擎的片段,強度要再打折。
- 版本:除另註明外,arXiv 論文查核時都只有 v1。
- 背景:panel K=2 閘已在 2026-08-25 退役,多席 code-loop 改走處置閘;見 repo 的 `docs/lumos-toolchain-knowledge/Systems/convergence-evidence-gate.md` 開頭告示。下文談 K=2 是談這條規則有沒有證據,不代表它是現行閘。

## 多代理與集成審查:加審查員有用嗎,報酬遞減曲線長什麼樣

### Takeaway
受控的 N 席對 1 席曲線在 LLM 代碼審查上仍不存在;最接近的訊號都指向「第二席之後報酬驟降,瓶頸是錯誤相關而不是席數」。人類基線(2 與 4 人一樣、1 人較差)和 Lumos 自家梯度形狀一致,但有效的多樣性來自模型實力與不同的閱讀範圍,不是多掛幾個同模型或人設。

### Cited Findings

**人類基線**

- [已知,細節新][同儕受控] Porter、Siy、Toman、Votta,TSE 23(6),1997:在商業產品上隨機分派,11 名資深開發者、130 次檢查,自變數為每隊 1/2/4 人、1/2 隊、兩場之間是否修復。結論原句:`1sX1p < 1sX2p, but 1sX2p = 1sX4p`;把大隊拆成兩小隊沒有提升效果(`2sX2p = 1sX4p`)。讀取層級:原文已核 — [Porter 1997 PDF](https://userweb.cs.txstate.edu/~rp31/papersSQ/PorterEtAl_TSE.pdf)
- [新][觀測] Votta 1993 工業個案 50 次設計檢查:會議新增發現約 5%,遠低於 Humphrey 宣稱的約 25%;Porter 等的後續受控實驗發現,這點增益還被「準備時發現、開會卻沒回報」的會議損失抵消。讀取層級:僅搜尋摘錄 — [CS-TR-3410](https://drum.lib.umd.edu/bitstream/1903/694/2/CS-TR-3410.pdf)、[NASA 報告](https://ntrs.nasa.gov/citations/19950024821)

**錯誤相關與獨立性**

- [新][預印受控] arXiv 2607.02808(2026-07-02,Pato Nogueira、Pattabiraman、Vieira、Campos):224 題、12 模型、5 語言、3 種提示。3 版與 5 版集成只拿到獨立假設下可達增益的 0.43 與 0.44,單一模型組成時低於 0.3;5 版多數決把平均可靠度從 0.88 提到 0.91;同模型解的 CodeBLEU 0.76、跨模型 0.55;「no model ensemble surpasses the best single model」。範圍是程式生成的 N 版本,不是審查。讀取層級:原文已核 — [arXiv 2607.02808](https://arxiv.org/abs/2607.02808)
- [已知] arXiv 2605.29800(2026-05-28,v1):9 個前沿 LLM、7 個家族,3 個自然語言推論資料集;9 席約等於 2 票獨立資訊,比獨立投票低 8–22 個百分點,既有方法最多補回缺口的 11%。題材不是代碼。讀取層級:僅摘要 — [arXiv 2605.29800](https://arxiv.org/abs/2605.29800)
- [已知,細節新][預印受控] arXiv 2608.06940(2026-08-07):HumanEval+/MBPP+ 上,panel 82.44%、最佳單席 87.16%、純執行訊號 87.60%,只在 16.2% 題上啟用訊號並採多數方替換規則可到 85.62%。+11.2pp 只出現在一票之差的題、其餘恰為零。讀取層級:原文已核 — [arXiv 2608.06940](https://arxiv.org/html/2608.06940)
- [已知][觀測] Kim 等 ICML 2025:350 多個 LLM 的錯誤高度相關,某榜單資料集上兩模型同時答錯時有 60% 答案相同。讀取層級:僅搜尋摘錄 — [arXiv 2506.07962](https://arxiv.org/abs/2506.07962)

**在審查任務上的直接訊號**

- [已知,細節新][預印受控] Adversarial Review,arXiv 2608.18167(2026-08-16):全用 Claude Sonnet 4.5。LiveCodeBench n=105:零發 77%、單審 77%、雙審 75%、MARS 五代理 82%、AR 三代理 87%;SWE-PRBench n=100 F1:單審 0.495、雙審 0.503、MARS 0.501、AR 0.457、AR 加文字約束 0.533。沒有信賴區間;作者自稱單純審查的差距在雜訊內。讀取層級:F1 原文已核,LCB 為全文摘錄 — [arXiv 2608.18167](https://arxiv.org/html/2608.18167)
- [新][同儕受控] Cross-Model LLM Code Review,arXiv 2607.21656(2026-07-22,Agentic SE @ KDD'26):116 題 LiveCodeBench 中難題,審查者不能執行程式、必須輸出最終程式。通過率:Claude 單獨 .914、Codex 單獨 .716;Claude 審 Codex .897(26 修好/5 改壞,p_BH .0010);Codex 自審 .845(p_BH .0222);Claude 自審 .914(3/3,p_BH 1.0);Codex 審 Claude .828(3 修好/13 改壞,p_BH .0456);回歸率 .026–.112;兩種跨模型順序的直接對比不顯著(p_BH .1444)。效應和基線差距混在一起,作者只當描述。讀取層級:原文已核 — [arXiv 2607.21656](https://arxiv.org/html/2607.21656v1)
- [已知][觀測] arXiv 2605.12280v2(MDPI *Software* 2026, 5, 26):合成迷你規格的 5 個種子缺陷,四家廠商共 12 條軌跡,只有聯集全抓;Grok 三次都漏 S2,Claude 三次漏一次 S3。樣本極小。讀取層級:原文已核 — [arXiv 2605.12280](https://arxiv.org/abs/2605.12280)
- [已知][觀測] OpenCodeReview,arXiv 2608.09290(AACR-Bench,200 PR、1,505 條專家驗證留言,LLM 判官比對):同為 Claude-4.6-Opus,SEM-F1 25.10% 對 Claude Code 11.57%;後者召回 28.90% 較高、精確率只有 7.23%。OpenCodeReview 召回僅 11.7–20.0%,而且論文沒做消融,作者多來自 Alibaba。讀取層級:全文摘錄 — [arXiv 2608.09290](https://arxiv.org/html/2608.09290v1)

**專鏡頭與人設**

- [新][觀測] Ericsson,arXiv 2609.15877(2026-09-14):四個專鏡頭(可靠性/可讀性/可維護性/效能)產出 206 條,197 條被判正確(約 96%);7 個 commit、5 位資深開發者,作者評自己的工具。論文明言沒做消融也沒和其他設計比較,召回未量。讀取層級:全文摘錄 — [arXiv 2609.15877](https://arxiv.org/html/2609.15877v1)
- [新][預印受控] MARS(arXiv 2509.20502,推理任務,非代碼審查):保守/激進人設沒有帶來跨任務提升,作者歸因於 LLM 本身的隨機性已提供一定多樣性,激進人設還造成雜訊式過度批評。讀取層級:僅搜尋摘錄 — [arXiv 2509.20502](https://arxiv.org/pdf/2509.20502)
- [意見] Kosli 工程部落格稱拆成安全、測試品質、資料庫等人設後品質明顯變好,沒有對照組。讀取層級:僅搜尋摘錄 — [Kosli](https://www.kosli.com/blog/ai-code-review-with-specialized-llm-personas/)

**現場與廠商**

- [已知,細節新][意見] Anthropic 2026-10-15:數個代理同時找蟲,另一組投票決定每條能否張貼,門檻沒寫;風格、診斷、清理類直接丟掉。讀取層級:全文摘錄 — [Solving code review at Anthropic](https://claude.dev/blog/solving-code-review-at-anthropic/)
- [已知,細節新][意見] Anthropic 2026-03-09:內部有實質留言的 PR 從 16% 升到 54%;工程師標記不正確的發現少於 1%;超過 1,000 行的 PR 84% 有發現、平均 7.5 條,低於 50 行的 31%、平均 0.5 條;每次約 15–25 美元。「少於 1%」是工程師標記率,不是獨立查核。讀取層級:全文摘錄 — [Bringing Code Review to Claude Code](https://claude.com/blog/code-review)
- [已知,細節新][意見] Cursor Bugbot 2026-01-15:v1 用 8 次隨機化 diff 順序的平行掃描加多數決,丟掉只在一次掃描出現的蟲,再過驗證模型;2025 秋改成能呼叫工具、自己決定往哪查的代理,解決率從 52% 升到 70% 以上,每 PR 解決的蟲從約 0.2 升到約 0.5。指標是內部 AI 判定,貼文沒說多數決是否保留。讀取層級:全文摘錄 — [Building a better Bugbot](https://cursor.com/blog/building-bugbot)
- [新][觀測,已獲 MSR 接受] MSR 2026,arXiv 2604.03196:AIDev 3,109 個 PR,僅有審查代理留言的 PR 合併率 45.20%,僅人類 68.37%;13 個審查代理有 12 個平均訊號比低於 60%。讀取層級:僅摘要 — [arXiv 2604.03196](https://arxiv.org/abs/2604.03196)
- [新][觀測] arXiv 2607.13196(207 專案、約 102 萬 PR):代理參與的審查較快,但審查壞味道比例 78–94%,僅人類 69–76%;互捧式審查(Review Buddies)僅人類 16%、LLM 參與 60%、代理參與 53%。相關性研究,未量缺陷。讀取層級:全文摘錄 — [arXiv 2607.13196](https://arxiv.org/html/2607.13196v1)
- [新][觀測] ESEM 2026,arXiv 2608.21311:248,641 個 AI 寫、AI 審的 PR,其中跨產品 45,269、同產品 208,145;四個雙角色審查者有三個在同產品組每 PR 留言多 58–65%,效應量小或可忽略。讀取層級:僅摘要 — [arXiv 2608.21311](https://arxiv.org/abs/2608.21311)

### 與既有主張的衝突

- `Verification/2026-09-03_席間覆蓋率離線量測.md` 的 KEY 寫「2 席輪 74.2% → 3 席 60.8% → 4 席 58.3%」,但表格分層變數是「該輪最多幾席同時抓到同一缺陷」,不是派出的席數。最大重疊只是席數的下限代理,這張表不能直接當席數效應曲線引用。
- 同篇「獨家不是誤報,是真的漏抓」靠「零放行=編排者認可」推得。外部證據動搖這個前提:LLM 判官 TNR 低於 25%([arXiv 2510.11822](https://arxiv.org/abs/2510.11822));同類 LLM 候選在 Refute-or-Promote 被殺掉約 79%([arXiv 2604.19049](https://arxiv.org/abs/2604.19049),領域不同);Meta 工程師確認率 19.5%([arXiv 2601.22832](https://arxiv.org/html/2601.22832))。1.1% 放行率可能反映的是判定端缺乏否決力。詳見下一節的推論。
- `世界解重新註解2026-10_迴圈工程_調研.md` 第 84 行「多模型比同家多席好」要收窄:2607.21656 顯示方向取決於審查者實力,較弱的外家審較強的作者,在可改寫的設定下顯著變差。不過該研究裡審查者輸出的是改寫後的程式,不是發現清單,不能直接套到只提發現的席位。
- `世界解重新註解2026-10_迴圈工程_調研.md` 第 446 行把 Porter 那份 PDF 標成 *Understanding the Sources of Variation in Software Inspections*,該 URL 的 PDF 實際標題是 *An Experiment to Assess the Cost-Benefits of Code Inspections in Large Scale Software Development*。

### Inferences

- 三組不同任務、不同模型的證據形狀一致:從 1 席到 2 席有收益,再往上快速變平(Porter;Lumos 表;2607.02808 的 0.43→0.44 幾乎不動)。「2 到 3 席為主力」是合理的預設,但沒有 LLM 審查的受控實驗直接支持,只能算旁證收斂。
- 找碴的聯集和判定的多數決是兩件事:多數決會丟掉單席發現(Cursor v1 的做法),而 Lumos 帳上 64.6% 是單席發現。相關性研究大多量的是投票,不該拿來否定找碴席的聯集價值;反過來,聯集的「多抓」也沒排除是雜訊。
- 多樣性排序的暫定看法:能換到不同證據的設計(能執行、能拉上下文、不同閱讀範圍)> 實力夠的跨家族模型 > 順序與隨機種子 > 人設。這是綜合判斷,沒有一篇研究把四者放在同一實驗裡比。
- 跨家族席的條件應該是「實力接近或更強」;較弱外家若有改寫權限,風險大於收益。

### Gaps

- 找不到任何隨機指派 N 席審同一批真實 PR、以真實缺陷召回為結果的受控研究。
- 找不到專鏡頭對通才、在代碼審查任務上的消融實驗;Ericsson 明言沒做。
- 2607.02808、2605.29800 量的是生成或判斷,不是找蟲;把數字套到審查是類比。
- 我搜尋到的工具基準都沒公開跨工具重疊與聯集召回。Entelligence 的矩陣只看到表頭。
- Fagan、Basili 的原始論文這輪沒有打開,不在此引用其數字。

## 聚合:多數決、聯集、辯論,以及辯方的誤殺率

### Takeaway
辯論不值得:同質代理互相看答案時常比獨自修正更差,證據量多但幾乎都不在代碼上。LLM 否決在窄範圍告警分類上誤殺只有幾個百分點,自由格式代碼審查的誤殺率則沒有人量過;行為驗證和 LLM 驗證的錯誤型態互補,行為證據適合當單向確認,不適合當否決。

### Cited Findings

**辯論與從眾**

- [新][預印受控] The Cost of Consensus,arXiv 2605.00914(2026-04-29):10 個同質代理、3 輪,模型為 7–8B 開放權重,題材為 GSM-Hard 與 MMLU-Hard。四個資料集×模型組合裡辯論顯著差於自我修正(例:Ministral GSM-Hard 20.7% 對 48.3%),Llama 兩組不顯著;附和率最高 85.5%;對變錯的脆弱度最高 70.0%,其他為 6.9%–21.4%;正確答案在池中出現 53.0%,團隊準確率卻只有 20.7%;token 為自我修正的 2.1–3.4 倍。作者提醒:只測小模型、沒有結構化辯論或人設基線。讀取層級:全文摘錄 — [arXiv 2605.00914](https://arxiv.org/html/2605.00914v1)
- [新][預印受控] Most LLM Conformity Needs No Speaker,arXiv 2607.05545(2026-07-06):6 個開放權重 LLM、7 個資料集,拿掉說話者只留被斷言的答案,仍有 66.5% 原本正確的案例被改壞,單純重問只有 10.3%。讀取層級:僅摘要 — [arXiv 2607.05545](https://arxiv.org/abs/2607.05545)
- [新][預印受控] Not All Flips Are Conformity,arXiv 2606.00820(v2,2026-10-18):5 個 GPT-4o 代理在 MMLU-Pro 分歧題,沒有同儕資訊也有 37% 改答案;控制後 29.3% 採用同儕答案;完整理由讓個體準確率上升,但多數決沒有比自我反思更好,token 多 57%。原句:「convergence is an ambiguous signal of value」。讀取層級:僅摘要 — [arXiv 2606.00820](https://arxiv.org/abs/2606.00820)
- [已知] Talk Isn't Always Cheap、Debate or Vote、Judging with Many Minds 已收在 `世界解重新註解2026-10_迴圈工程_調研.md` 第 115 行,這輪沒有重讀。 — [arXiv 2509.05396](https://arxiv.org/abs/2509.05396)

**否決階段與誤殺(false-kill)**

- [已知,細節新][觀測] Refute-or-Promote,arXiv 2604.19049(2026-04-21,單一作者):31 天、7 個目標,約 171 個候選殺掉約 135 個(約 79%,回溯);前瞻子集 30 個殺 25 個(83%);36+ 成果含 4 個 CVE。論文明言「optimises precision but does not measure recall」,**沒有誤殺率**。n=2 的兩個案例很有代表性:OpenSSL 假漏洞被 10 個專責代理一致確認,一個編譯實測就推翻;lcms2 的真漏洞 CVE-2026-41254 被一致判「DO NOT FILE」,靠人類指示才救回(觸發條件從 174 MB 找到 4.8 KB)。跨家族批評只殺約 5 個(約 3%);沒做消融。讀取層級:全文摘錄,「future work」與 recall 句原文已核 — [arXiv 2604.19049](https://arxiv.org/html/2604.19049v1)
- [新][預印受控] LASAA,arXiv 2607.09979(2026-07-10,CMU SEI):LLM 判靜態分析告警,約 100 例一個套件,地面真值為人工判定且未公開。誤殺(false dismissal)=實際為真卻被否決:Juliet 上 1.0%–4.0%;FormAI 上 0.0%–4.1%;SV-COMP 上 0.0%–2.4%;frontier 模型在 FormAI 為 0.0%,但只跑 5 次。一致性檢查門檻是看過初輪結果才選的;Juliet 有記憶化風險。讀取層級:全文摘錄 — [arXiv 2607.09979](https://arxiv.org/html/2607.09979)
- [新][預印受控] QASecClaw,arXiv 2605.01885(2026-05-03):OWASP Benchmark 2,740 例,FP 560→64(少 88.6%),TP 1,273→1,233(損失 40 條,相對 3.1%),召回 .900→.871;CWE-501 有 48 條 TP 被誤判為良性,比基線差。評估時沒有啟用動態證據路徑,完全靠讀程式碼。讀取層級:全文摘錄 — [arXiv 2605.01885](https://arxiv.org/html/2605.01885v1)
- [新][觀測,會議別未查] LLM4PFA,arXiv 2506.10322:空指標解參考保住 42/45 真 bug。騰訊工業研究(LLMPFA)去掉 94%–98% 假陽性,但摘錄沒有召回數字。讀取層級:僅搜尋摘錄 — [arXiv 2506.10322](https://arxiv.org/pdf/2506.10322)、[DOI 10.1145/3786583.3786910](https://doi.org/10.1145/3786583.3786910)
- [已知,細節新][預印受控] Beyond Consensus,arXiv 2510.11822(v2,2025-12-24):14 個 LLM 判 366 份高中 Python 程式的代碼回饋,TPR 96%、TNR 低於 25%:判官幾乎不說「這則無效」。少數否決有韌性;再用少量人工標註做迴歸校正,最大絕對誤差降到 1.2%,是最佳集成的 2 倍改善。讀取層級:僅摘要 — [arXiv 2510.11822](https://arxiv.org/abs/2510.11822)

**LLM 驗證 vs 行為驗證的正面比較**

- [新][預印受控] 同一篇 LASAA,FormAI 76 條告警(30 真、19 相依、27 假):LLM 合成觸發程式,40 個驅動程式有觸發,有效性檢查擋掉全部 9 個針對假陽性的;20 個有效觸發裡 18 個是真、2 個相依、0 個假。但只確認了 18/30 真陽性(60%),另 8 條只能靠違反前置條件才觸發,4 條完全觸發不了。原文定調:「a valid trigger is therefore strong evidence of a real flaw」,同時「incomplete on the positive side」。讀取層級:原文已核 — [arXiv 2607.09979](https://arxiv.org/html/2607.09979)
- [已知,細節新][預印受控] 2608.06940:一票替換的增益全落在 pivotal 題,摘要原文稱其餘題「exactly zero」;純執行訊號(87.60%)打平最佳單席(87.16%),兩者都明顯高於整個 panel(82.44%)。讀取層級:原文已核 — [arXiv 2608.06940](https://arxiv.org/html/2608.06940)

**結構化異議**

- [已知,細節新][預印受控] 2608.18167:批評者判決分 AGREE / DISAGREE_EVIDENCE / DISAGREE_CONCERN,CONCERN 時審查者必須引用程式確認或反駁。F1 0.457→0.533,但論文沒有給假共識率,也沒有誤殺或召回損失的數字,而且提示是看著同一基準迭代的。讀取層級:原文已核 — [arXiv 2608.18167](https://arxiv.org/html/2608.18167)

### 與既有主張的衝突

- **重要,要修帳**:`docs/methodology/圖譜即合約.md` 第 586 行與 `Projects/收斂機制優化調研2026-08-14.md` 的 2026-09-01 補記都寫 2604.19049「實測單發反駁比互辯省 30–40% 成本、比多席投票 precision 高 40–50%」。這篇 arXiv 只有 v1;全文 HTML 比對不到這兩組數字,摘要也沒有,論文明寫和辯論變體的受控比較「is future work」,成本段只有約 250 美元、每 CVE 約 62 美元。這兩個數字查不到出處,不應再當「路由制 + 禁互辯」的實測背書。支持禁互辯的證據要換成 2605.00914、2606.00820 這類。
- 引 2510.11822 時不要經由 2604.19049 轉述:後者相關工作段寫 minority-veto「beats a 14-LLM ensemble by 2×」,而 2510.11822 摘要的 2× 是迴歸校正對最佳集成的改善,兩者說法不一致,以原論文為準。
- `收斂機制優化調研` 寫「它報告的最大失敗模式=false consensus」「三分類是它的修法」。分類確實來自該論文,但假共識沒有量化,0.533 只比雙審 0.503 高 0.030、沒有信賴區間,而裸 AR 0.457 反而比單審 0.495 差。「從 naive 起點修上來」的判讀是對的,裁定不動也合理。
- `收斂機制優化調研` 判「多樣性崩塌/密集拓撲…結構上不成立,席之間看不到彼此」。對找碴席成立;對辯方不完全成立:2607.05545 顯示不需要說話者,單是看到被斷言的答案就有傷害,而辯方必然讀到席位的斷言。該研究不是代碼題,所以只算疑點。
- 同節寫「換一席帶來的準確率增益」,原論文替換的是**執行測試的第二證據來源**,不是換一個 LLM 判官。把它轉成「只在勢均力敵輪算獨佔貢獻」(決策 d1)時有兩層跳躍:從執行訊號跳到 LLM 席,從多數決跳到聯集式找碴;聯集沒有一票之差這回事。建議把 d1 的依據改標為類比。

### Inferences

- 誤殺率的實務範圍:窄範圍、單一告警的分類任務約 0–4%;開放式審查未知。Lumos 的辯方面對的是開放式發現,不能借用這個數字。
- 1.1% 放行率有兩種互斥解讀:席位真的很準,或者判定端幾乎不否決(LLM 的 TNR 低,加上 major 一律折)。2510.11822 的 TNR 與 Refute-or-Promote 的約 79% 淘汰率支持第二種的可能性,但領域不同,需要自家抽驗才能裁,例如對已折入發現抽樣做觸發實測。
- 行為證據的不對稱用法最符合現有資料:**做得出來就升級、免辯;做不出來不降級、走 LLM 或人工**。把「沒重現」當否決會丟掉約四成真問題(LASAA 的 12/30),而且是在 C 小程式這種容易重現的情境。
- 全體一致不是可靠訊號(OpenSSL 與 lcms2 兩例剛好一正一反,都是一致而錯)。一致否決也值得留申訴路徑;目前只有 n=2 的案例支持。

### Gaps

- 沒有任何研究量「開放式 LLM 代碼審查發現被辯方否決時,有多少其實是真 bug」。這是本題最大的空白,也是 Lumos 帳本的機會。
- 辯論研究幾乎都用 QA 或數學題與小模型;我沒找到在代碼審查上的結構化辯論受控實驗。
- Pebblous 部落格提到的 conformity without verification 預印本(74.6%→36.4%)只有二手來源,找不到原文,不採用。
- Anthropic 投票門檻未公開,無法判斷它算多數決還是少數否決。

## 行為證明:發現要附失敗測試或重現才算數

### Takeaway
行為證明是目前精確率最高的單一訊號,但「失敗的測試」本身不是證明:測試可能把舊行為寫死、和修補共享同一個誤解,或違反前置條件才觸發。可重現比例依題材大約六到八成,而且約三分之二的真實審查關注點(可演化性)根本無法這樣證明。

### Cited Findings

**可重現比例與品質**

- [新][預印受控] CoHarden,arXiv 2607.19843(2026-07-22,Yuhao Tan 等 12 位作者):SWE-bench ∩ SWT-bench Verified 433 例;共生測試 F→P 72.3%,CoHarden 78.9%,R0 高點 83.3%。Cogen 的 166 個未解題有 80 個(48.2%)測試通過 F→P 而修補是錯的;聯合失敗 19.9%,是獨立預測 10.6% 的 1.87 倍;P(修補錯∣測試錯)=71.7%。獨立研究(1,104 組 F→P):只有嚴格測試讓解題數 +8.5,寬鬆測試 +0.0,偏差測試 −3.6。讀取層級:原文已核;部分數字為全文摘錄 — [arXiv 2607.19843](https://arxiv.org/html/2607.19843v1)
- [已知,細節新][預印受控] Meta JiTTest,arXiv 2601.22832(投 FSE 2026 工業軌):22,126 個測試、約 1% 成為弱捕獲(231 個);41 次聯繫工程師,8 個確認為真(19.5%),4 個若上線會造成嚴重失敗;規則與 LLM 評估器把人工審查量降約 70%。diff 感知方法的候選捕獲率是強化測試的 4 倍、巧合失敗的 20 倍。論文內有數字不一致(7/8、9,125/22,126)。作者明說資料點太少,不足以做強科學主張。讀取層級:全文摘錄 — [arXiv 2601.22832](https://arxiv.org/html/2601.22832)
- [新][預印受控] arXiv 2603.23443(2026-03-24):8 個模型、22,374 個程式變體;語意改變後的測試有 23,977 個在改動後程式失敗,其中 23,737 個(超過 99%)在原程式通過並執行到改動區;作者解讀為「殘留對齊」舊行為,沒有判定這些是真 bug 還是誤報。讀取層級:全文摘錄 — [arXiv 2603.23443](https://arxiv.org/html/2603.23443v1)
- [已知,細節新][觀測] Agentic PBT,arXiv 2510.09907(NeurIPS 2025 DL4Code 工作坊):100 個 Python 套件,報告 56% 有效、32% 值得回報;排序後前 21 名 86% 有效、81% 值得回報;回報 5 個、3 個修補合併。讀取層級:僅摘要 — [arXiv 2510.09907](https://arxiv.org/abs/2510.09907)
- [新][同儕受控] PBT-Bench(NeurIPS 2026):40 個 Python 函式庫 100 題,Hypothesis 鷹架讓中等模型提升超過 20 個百分點,最強模型增幅較小。讀取層級:僅搜尋摘錄 — [PBT-Bench](https://neurips.cc/virtual/2026/poster/138920)
- [已知][觀測] AIxCC 決賽:54 個合成漏洞發現、43 個修補,另有 18 個真實漏洞。分母來源不一:DARPA 一處用 63 題(86%/68%),Trail of Bits 與 KAIST 用 70(77%/61%)。讀取層級:僅搜尋摘錄 — [DARPA](https://www.darpa.mil/news/2025/aixcc-results)、[Trail of Bits](https://www.trailofbits.com/documents/AIxCC_Main_Stage_Presentation.pdf)、[SoK arXiv 2602.07666](https://arxiv.org/html/2602.07666v1)

**突變測試**

- [已知][觀測] Meta ACH,arXiv 2501.12862(投 FSE 2025 工業軌):10,795 個 Android Kotlin 類、9,095 個突變、571 個強化測試;工程師接受 73%,其中 36% 判為隱私相關;等價突變偵測精確率 .79、召回 .47,簡單前處理後 .95/.96。讀取層級:僅摘要 — [arXiv 2501.12862](https://arxiv.org/abs/2501.12862)
- [已知,細節新][觀測] Google:ICSE-SEIP 2018 超過 70,000 個 diff、110 萬突變、15 萬可行動發現,有用率從 20% 回饋調整到 80%;ICSE 2023:38% 的突變與 60% 的有產出突變被修掉或補測試;64% 突變所在程式碼在 MR 演進中變動。讀取層級:僅搜尋摘錄 — [Practical Mutation Testing at Scale](https://research.google/pubs/practical-mutation-testing-at-scale-a-view-from-google/)、[ICSE 2023](https://homes.cs.washington.edu/~rjust/publ/mutation_testing_resolution_icse_2023.pdf)
- [新] CoHarden 用 LLM 合成突變修補當寬鬆度訊號:每輪 12 個修補、τ=0.2 接受;涵蓋率受限於 LLM 對「看似合理但錯」的想像。讀取層級:全文摘錄 — [arXiv 2607.19843](https://arxiv.org/html/2607.19843v1)

**會失去什麼**

- [已知,細節新][同儕受控] MCR-Bench,arXiv 2608.27442(ISSTA 2026):2,269 個真實多輪任務的缺陷分類,加總後可演化性 65.38%、功能性 34.62%。讀取層級:全文摘錄,加總我已驗算 — [arXiv 2608.27442](https://arxiv.org/html/2608.27442v1)
- [新][觀測] Ericsson:206 條裡可讀性加可維護性 108 條,約 52.4%(我由表計算)。讀取層級:全文摘錄 — [arXiv 2609.15877](https://arxiv.org/html/2609.15877v1)
- [新][觀測] 蘇黎世 2022:審查改動多屬可演化性問題,多半不是修主要功能缺陷;「至多 75%」的常見說法在我這輪只找到 Wikipedia 鏡像轉述 Mäntylä & Lassenius 2009。讀取層級:僅搜尋摘錄 — [PMC9489594](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9489594/)

### 與既有主張的衝突

- `收斂機制優化調研` 候選④的方向(收斂錨行為訊號)獲支持,但要補一條限制:行為訊號本身會共謀。同一代理同時寫修補與測試時,聯合失敗是獨立預測的 1.87 倍;翻紅釘若由修補者自己寫,會落入這個情境。
- 「紅釘證據」的品質前提沒有被驗過:2603.23443 與 CoHarden 都顯示 F→P 或失敗測試不等於命中真正的缺陷。

### Inferences

- 把行為證明分三級比二元好:(甲)獨立方寫的、在基準版通過而在變更版失敗,且行為差異經意圖核對;(乙)只有失敗;(丙)無法執行。只有甲級能免辯。
- 誰寫測試很關鍵:測試與修補應分開,由不看修補的乾淨席先寫(CoHarden 的 Lax-init 也是先測試後修補)。
- 涵蓋範圍預估(綜合,非單一研究):可演化性發現約佔三分之二且不可行動驗證;剩下的功能問題中,即使在小程式也只有約 60% 能有效觸發。所以強制「沒有重現就不算」大約只留下二到三成的發現類型(34.62% 乘上 60%–83% 的可重現比例,約 21%–29%)。這個估計混了不同母體,只適合當量級。
- Meta 的 8/41 提示:不做評估器的話,行為候選的人工成本很高。值得保留的是評估器加工程師確認的組合。

### Gaps

- 我沒找到「審查留言中可被機械重現的比例」的直接測量;上面的 60% 來自 C 小程式與靜態告警,不是真實 PR。
- 2607.09979 的 FormAI 是 AI 產生的小程式,SWE-bench 是 Python 開源修補;企業多檔服務的重現率未知。
- LLM 突變對照傳統突變、在審查階段的增量價值,我沒找到受控比較。
- CVE-Genie 的 PoC 重現率這輪沒查。

## 停止規則:什麼時候停止審查

### Takeaway
沒有任何受控證據支持 K=2 或其他固定連續乾淨輪數。較強的新訊號是相反方向:無上限的審改循環會自己製造工作,甚至傷害正確程式。業界最具體的做法是低上限(三輪)加改變再審形狀,而不是更精巧的殘餘估計。

### Cited Findings

**古典捕獲再捕獲**

- [已知][觀測] Briand 等 TSE 26(6),2000:估計器傾向低估缺陷數,少於四名檢查員時低估最大;技術報告版建議用允許不同偵測機率的模型加 Jackknife。讀取層級:僅搜尋摘錄(技術報告版) — [Comprehensive Evaluation](https://www.ehealthinformation.ca/web/default/files/wp-files/2001-A-Comprehensive-Evaluation.pdf)、[ISERN-97-22](https://ehealthinformation.ca/web/default/files/wp-files/isern-97-22.pdf)
- [已知] 2026-08-14 帳本測得殘餘估計鑑別力約為零(67% 對 79%,p≈0.25),已降 advisory — `Projects/收斂機制優化調研2026-08-14.md`
- [新][觀測] 主觀估計替代方案:30 名工程師研究中,用檢查員主觀估計做的再檢查決定比「一律不再檢查」更正確。讀取層級:僅搜尋摘錄 — [Subjective estimates](https://www.sciencedirect.com/science/article/abs/pii/S0164121200000327)

**殘餘風險的新估計**

- [新][觀測] arXiv 2607.17061(2026-07-19,stat.AP):單次回報缺陷比例 s/n 是「使用者遇到測試未見缺陷機率」的保守上界,不需要操作剖面或缺陷數假設;用合成母體驗證;使用者面解讀只對遭遇級資料成立。讀取層級:僅摘要 — [arXiv 2607.17061](https://arxiv.org/abs/2607.17061)
- [已知,細節新][觀測] STADS(Böhme,TOSEM 2018):Good-Turing 用 f1/n 估下一個測資發現新物種的機率。ICSE 2026 Lee & Böhme 指 Good-Turing 忽略依賴,新估計器在 FuzzBench 誤差中位數為其五分之一,照 Good-Turing 會多浪費 7 倍時間才決定停止。讀取層級:僅搜尋摘錄 — [arXiv 1803.02130](https://arxiv.org/pdf/1803.02130)、[ICSE 2026](https://conf.researchr.org/details/icse-2026/icse-2026-research-track/138/Dependency-aware-Residual-Risk-Analysis)

**連續乾淨輪與收斂**

- [已知,細節新][觀測] 2605.12280v2:7,152 行規格九輪,每輪 15, 8, 12, 2, 8, 1, 4, 1, 0,共 51 個。作者**自己只用一輪乾淨就停**,理由是額外一輪成本高;建議複現時用兩輪連續乾淨,並說明這條是建議、不是實測結果。Mann–Kendall τ=−0.72、p=0.008,但輪次不獨立且稽核協議隨輪成熟,兩個訊號分不開。Round 6 只有 1 條、round 7 又冒 4 條。作者聲明收斂到零只證明內部一致,不證明正確,且作者與稽核同家族。讀取層級:原文已核 — [arXiv 2605.12280](https://arxiv.org/abs/2605.12280)
- [已知,細節新][意見] Anthropic 2026-10-15:一個 CLI PR 跑超過 50 輪審修才被作者中止;原文「about 59% of it was code that had been there since the reviewer's first pass」,「The reviewer was rarely finding new bugs, it was finding a few more old ones each round」。改動後:一輪審修即過 65%→78%、需 5 輪以上 8.9%→1.5%、平均審查次數 2.08→1.32;三輪後請作者退一步重想。同時追蹤過關輪數與召回,優先序是先抓真 bug、再減輪數。沒有樣本數與期間,表格不拆各項修法效果,召回數字未公開。讀取層級:全文摘錄 — [Solving code review at Anthropic](https://claude.dev/blog/solving-code-review-at-anthropic/)
- [已知,細節新][同儕受控] MCR-Bench(ISSTA 2026):2,269 任務、平均 3.8 輪、κ=0.87;所有模型 F1 隨輪次下滑(GPT-5.2 第 2 輪 .5995→第 6 輪 .5067;Claude Haiku 4.5 .6495→.5313;高輪次樣本少)。假陽性主因:狀態時序錯位 32.5%、過度審查 27.8%;漏報主因:跨輪遺忘 25.1%、長距依賴 23.4%、語意盲點 22.3%、對修補過度樂觀 15.2%、附和 6.5%。最常見狀態錯誤是把已解決判成新缺陷,38.29%。論文未報告後輪是否引入新問題。讀取層級:全文摘錄 — [arXiv 2608.27442](https://arxiv.org/html/2608.27442v1)

**修補誘發與循環**

- [新][預印受控] If It's Not Buggy, Don't Fix It,arXiv 2609.10123(2026-09-09):CodeContests+ 800 份 C++ 提交、無歷史馬可夫迭代、上限 100 輪、僅 Gemini 2.5 Flash-Lite 與 Qwen2.5-7B。正確程式起步、τ=0 時每步傷害率 β:Gemini SRB 0.293、整檔 0.165;Qwen SRB 0.424、整檔 0.099。修復率 α 都小得多:SRB 錯誤起步 0.023 與 0.004,整檔 0.101 與 0.019。原文結論:傷害「at least as large as the improvements」,SRB 明顯更高、整檔兩者相近;常落入同一改動反覆加入又移除的偽修復循環。只有小模型、單檔、靠隱藏測試判定。讀取層級:原文已核 — [arXiv 2609.10123](https://arxiv.org/html/2609.10123v1)
- [已知,細節新][預印受控] CoHarden:Resolved 第 1 輪 61.0%、第 2 輪 67.8%、結束 69.4%,約第 3 輪飽和;測試 F→P 從 83.3% 掉到 78.9%,作者懷疑測試與修補的耦合會跨輪再現。讀取層級:全文摘錄 — [arXiv 2607.19843](https://arxiv.org/html/2607.19843v1)
- [新][預印受控] 2607.21656:一次審查改寫的回歸率 .026–.112,就算是能提高總分的組合(26 修好)也改壞 5 題。讀取層級:原文已核 — [arXiv 2607.21656](https://arxiv.org/html/2607.21656v1)
- [已知,細節新][觀測] 2605.12280 §5.2 串聯編輯:round 5 拿掉 Lane 2 設定導致 changelog 變錯,round 6 才抓到。原文比作傳統審查的回歸引入。讀取層級:原文已核 — [arXiv 2605.12280](https://arxiv.org/abs/2605.12280)
- [已知] Lumos 手填帳:2026-10-02 到 10-09 共 583 條有 185 條(約 32%)被標為上一輪修補造成,未驗證 — `世界解重新註解2026-10_迴圈工程_調研.md` 第 218 行
- [新][觀測] Yin 等 FSE 2011:大型作業系統抽樣的上線後修復至少 14.8%–24.4% 不正確,併發 bug 修復 39% 不正確,27% 不正確修復出自從未碰過該檔的人。讀取層級:僅搜尋摘錄 — [NetApp 摘要](https://netapp.com/atg/publications/publications-incorrect-fixes-20110911)

### 與既有主張的衝突

- `世界解重新註解` 把「約 32% 修補誘發」與第二輪後的發現連結。Anthropic 的 59% 提示另一種機制:後輪發現大多是**第一輪就存在、只是被慢慢挖出的舊碼**,不是修補造成。兩者口徑不同(自家手填對 git blame),不能直接相減,但說明帳上的 32% 需要用 git blame 式機械比對驗證。
- `圖譜 convergence-evidence-gate` 的「K=2」外部依據主要是 2605.12280 的建議,而該研究本身沒有實測 K=2,repo 已註明 N=1。截至這輪,仍沒有更強的新證據,也沒有反證。
- `收斂機制優化調研` 的「不推加輪」獲強化,而且理由更強:不只是邊際遞減,還有傷害面。

### Inferences

- 固定 K 的邏輯前提是每輪像獨立抽樣;2605.12280 明言每輪稽核函數在變,LLM 又是隨機的,而且 2609.10123 顯示正確程式也可能被判有蟲。K 輪乾淨能排除的只是這個審查器看得到的錯,對共同盲點無效。
- 更有用的停止訊號是**發現的性質**而非數量:新發現是否落在舊碼、是否重複、是否由上一輪修補引入、嚴重度是否下降。Anthropic 的 git blame 分析就是這種。
- 上限應分兩類理由:防循環(硬上限)與提醒重想(觸發時改問人或改設計)。三輪是 Anthropic 的現場值,不是最適值證明;Adversarial Review 的五輪上限(見 `收斂機制優化調研`)也只是設計選擇,沒有比較。
- 2609.10123 的最實用啟示是:審修迴圈要給「不改」一個合法出口,而且大改勝過細碎逐條修補(SRB 傷害明顯高於整檔)。這和 Lumos「major 一律折」有張力:逐條必修的流程更接近 SRB 模式。但研究模型很小,不宜直接推到前沿模型。
- f1/n 類上界不需要獨立假設,適合做不進閘的描述性指標;不要拿來重開 2026-08-14 已被實測打掉的預測用途。

### Gaps

- 沒有任何受控實驗比較 K=1、2、3 或固定上限的逃逸缺陷率。
- 2609.10123 沒用前沿模型,也不是「審查者提發現、作者修」的角色分離設定。
- MCR-Bench 沒有報告後輪引入新問題的比率,也沒有 delta 對全量實驗。
- 這輪只確認 panel K=2 退役;循序模式 design-loop 的現行 K 值我沒有在程式碼上核對。
- Wohlin、Eick 原文未開啟;只引用 repo 既有結論,不在此重述數字。Petersson 2004 只看到標題。

## 風險分流:哪些 diff 特徵能預測缺陷,以及按風險分配審查力的證據

### Takeaway
風險模型能把事故集中到一小部分 diff,這點有 Meta 的生產級資料支持;但證據幾乎全在「管制或放行」,不在「分配審查力讓缺陷更少」。Anthropic 2026 年的三級分流是最新實例,仍是自報。

### Cited Findings

- [已知][觀測] Meta DRS,arXiv 2410.06351(v1,2024-10-08):邏輯迴歸基線擋前 5%/10%/50% 風險 diff,分別抓到 18.7%/27.9%/84.6% 的 SEV;生產環境 iCodeLlama-34B 與 iDiffLlama-13B 抓到的倍數為 1.40×、1.52×、1.05×(摘要未標各對應哪個區)。讀取層級:僅摘要 — [arXiv 2410.06351](https://arxiv.org/abs/2410.06351)
- [新][觀測,已獲 AIware 接受] AIware '26,arXiv 2607.02782(Meta,DOI 10.1145/3805760.3814916):用模型注意力標示風險行,前 2 個 hunk 涵蓋 53.85% 的事故成因行,需看 26.28% 的改動行;事故成因 diff 約千分之二;轉引 Abreu 2025「gating just the top 10% of diffs」抓到超過 40% 事故。內部試用回饋 55 則:7 正面、48 負面,作者稱只是除錯訊號。讀取層級:全文摘錄 — [arXiv 2607.02782](https://arxiv.org/html/2607.02782)
- [已知][意見] Meta 2025-08-06:DRS 讓一次重大夥伴活動期間多落地超過 10,000 個變更,生產影響很小;19 個風險工具用例;沒有給模型指標。讀取層級:全文摘錄 — [Meta 工程部落格](https://engineering.fb.com/2025/08/06/developer-tools/diff-risk-score-drs-ai-risk-aware-software-development-meta/)
- [新][觀測] DRS-OSS,arXiv 2511.21964(v3,2026-06-07,工具展示):Llama 3.1 8B 在 ApacheJIT ROC-AUC 0.895;早期版本稱擋前 30% 可阻止最多 86.4% 致缺變更(模擬)。讀取層級:僅摘要與搜尋摘錄 — [arXiv 2511.21964](https://arxiv.org/abs/2511.21964)
- [已知,細節新][意見] Anthropic 2026-10-15 三級:低風險(文件、文案、內部功能、旗標後新增)自動檢查綠燈後免人工;中風險一人;高風險與少數固定路徑兩人。分級器看變更不看作者;只有信任名單作者走輕路徑;代理核准不算人核准。原文承認還沒有隨回滾或事故數收緊的斷路器。回滾比例六到九月下降超過 40%,絕對值與因果未交代。讀取層級:全文摘錄;斷路器句來自 InfoQ 引文 — [Anthropic](https://claude.dev/blog/solving-code-review-at-anthropic/)、[InfoQ](https://www.infoq.com/news/2026/10/anthropic-code-review/)
- [已知,細節新][觀測] DORA 2025:近 5,000 人調查;AI 採用與吞吐量、產品績效正相關,「does continue to have a negative relationship with software delivery stability」;作者解釋為缺乏控制時變更量放大不穩定。部落格未具體談批次大小或審查,完整報告沒打開。讀取層級:全文摘錄(部落格) — [Google Cloud 部落格](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report)
- [已知] Kamei 等 TSE 2013,DOI 10.1109/TSE.2012.70:即時缺陷預測基礎論文,這輪只確認書目,未讀內容。 — [書目](https://posl.ait.kyushu-u.ac.jp/pman3/pman3.cgi?D=322)
- [已知][觀測] 工作量感知的即時預測研究:,簡單無監督模型常勝過監督模型。讀取層級:僅搜尋摘錄 — [Effort-aware JIT](https://www.researchgate.net/publication/310821310_Effort-aware_just-in-time_defect_prediction_simple_unsupervised_models_could_be_better_than_supervised_models)
- [已知] Lumos 帳本:scope_lines 與存活發現相關 −0.42、−0.35,觀測性 — `Projects/收斂機制優化調研2026-08-14.md`

### 與既有主張的衝突

- 不要把 DRS 當「分配審查注意力有效」的證據:DRS 的數字都是管制與放行;2607.02782 的 55 則回饋 48 負面,也沒有衡量下游結果,標示審查注意力這條路還沒被驗證有效。
- 2410.06351 只有摘要的三個倍數不能對應到三個區;別把它寫成「LLM 在前 10% 抓 X%」。Abreu 2025 的「超過 40%」是轉引。

### Inferences

- Lumos 的分級應優先當**路由**(派幾席、走哪條閘),不要假設「多派幾席=風險下降」,這段因果沒有資料。
- 尺寸仍是最便宜的訊號:Anthropic 84%/7.5 對 31%/0.5 與自家相關性同向,但只說明大改動留言多,不等於缺陷多。
- 斷路器(逃逸時自動收緊)是連 Anthropic 都還沒做的空白,Lumos 若有逃逸帳,這裡可以領先。

### Gaps

- 找不到以「按風險分配審查力」為自變數、缺陷逃逸為應變數的受控研究。
- 找不到 2026 年 LLM 對簡單 change-metric 模型的直接比較(CodeFlowLM 只比預訓練模型與定位)。
- 小 repo 的事故樣本量能否訓練或校準這類模型,我沒找到研究;Meta 的基率約千分之二,是在其規模下才有足夠正例。
- Kamei、DORA 全文未讀,不引用其具體係數或數字。

## 修正的再審:只審差異還是全量重審

### Takeaway
沒有受控比較。現場最具體的做法是 Anthropic 的「前幾輪後改只審差異、指出整類 bug、不重複已發表的發現、三輪封頂」,改善了過關輪數,但個別效果無法拆開。全量與差異各有明確的失敗型態,所以合理的形狀是「差異加上受影響範圍」。

### Cited Findings

- [已知,細節新][意見] Anthropic 2026-10-15:改動含「Diff-only re-review after the first few passes」、標示 bug 類別讓作者一次修完、不重複已發表發現;沒說前幾輪是否全量。讀取層級:全文摘錄 — [Anthropic](https://claude.dev/blog/solving-code-review-at-anthropic/)
- [已知,細節新][同儕受控] MCR-Bench 的相關機制:全上下文下,把已解決判成新缺陷是最大狀態錯誤(38.29%)、跨輪遺忘佔漏報 25.1%、對修補過度樂觀 15.2%、長距依賴 23.4%。讀取層級:全文摘錄 — [arXiv 2608.27442](https://arxiv.org/html/2608.27442v1)
- [已知,細節新][觀測] 2605.12280:round 5 的修補在另一份文件造成問題、round 6 才抓到;跨文件缺陷必須同一輪讀到兩邊。讀取層級:原文已核 — [arXiv 2605.12280](https://arxiv.org/abs/2605.12280)
- [已知,細節新][同儕受控] Porter 1997:兩場之間修復沒有提高效果(`2sX2pR` 對 `2sX2pN`),但作者警告「viewed with caution」,該處理組只有 4 與 5 次,2sX2pR 因耗時提早停用,中位間隔 20 天對其他約 10 天。讀取層級:原文已核 — [Porter 1997 PDF](https://userweb.cs.txstate.edu/~rp31/papersSQ/PorterEtAl_TSE.pdf)
- [新][意見] GitHub 專案回報的兩難:pi-rukas #1198 指修後再審看不到修補改了什麼,回歸因而過關;NCodeGroup/code-review #24 指再審持續對未動程式碼挑小毛病,甚至推翻上一輪;QFAI #3956 對行為改動給一次聚焦再審、文字修改不審;atom #16 主張每輪修復後獨立全量再審。讀取層級:僅搜尋摘錄 — [#1198](https://github.com/trail-openers/pi-rukas/issues/1198)、[#24](https://github.com/NCodeGroup/code-review/issues/24)、[#3956](https://github.com/aganesy/QFAI/pull/3956)、[#16](https://github.com/girishmotwani/atom/issues/16)

### 與既有主張的衝突

- `世界解重新註解2026-10_迴圈工程_調研.md` 第 326 行寫「Porter 說修後再審不多找到缺陷」,語氣太強。Porter 只有 4 與 5 次的小格子,作者明確要求謹慎看待,而且那是人類檢查,修補不是 AI 大改。
- `世界解` 第 361 行的更正把 Lumos 的貢獻定為「每輪換乾淨席」。MCR-Bench 的遺忘與時序錯位正是有狀態審查者的毛病,乾淨席可避開;但乾淨席也看不到歷史,Anthropic「不重複」和 2605.12280 的逐輪累積都需要狀態。這是取捨,不是純優勢。

### Inferences

- 建議的形狀:修補的直接差異 + 從圖譜或依賴圖算出的受影響範圍 + 上輪已處置清單(只作去重,不作提示),由乾淨席審。只給差異會漏掉跨檔串聯,只給全量會回到舊碼慢慢挖的循環。
- 「不重複」要以機械去重實作,不要只靠提示;MCR-Bench 顯示模型對缺陷狀態的判斷不可靠(最佳模型 79.69%)。
- 全量重審更適合當稀疏抽查(例如收斂時一次),不適合每輪都跑。
- 這和現有的「修正差異派新席」紀律相容,差別在於明確把受影響範圍納入派工材料。

### Gaps

- 找不到 delta 與全量再審的受控比較,逃逸率更沒有。
- Anthropic 未公開「前幾輪」是幾輪,也未拆開各項改動效果。
- 查不到把受影響範圍(impact)納入再審的評估研究。

## 預防與偵測:規格先行、合約、LLM 輔助形式驗證,到 2026 年有什麼是真的

### Takeaway
LLM 寫證明在有界任務上已很實在,寫對規格仍是瓶頸,所以「證明取代審查」目前只成立於規格已被審好的窄範圍。對一般團隊,輕量的合約與行為規格比完整證明務實;沒有任何資料顯示團隊用證明取代人工審查。

### Cited Findings

- [新][預印受控] VeriContest,arXiv 2605.08553(2026-05-08):946 題 Rust/Verus,十個模型中最強者的自然語言到代碼 92.18%、規格生成 48.31%、證明生成 13.95%、端到端 5.29%。讀取層級:僅摘要 — [arXiv 2605.08553](https://arxiv.org/abs/2605.08553)
- [新][預印受控] Vero,arXiv 2608.13522(2026-08-13):43 個多模組 Lean 4 repo 實例,最強代理配置完整解出 27/43,最難的 repo 一條規格都關不掉;稽核機制讓代理能證明規格不可滿足或參考實作有錯,協助找出編纂錯誤。讀取層級:僅摘要 — [arXiv 2608.13522](https://arxiv.org/abs/2608.13522)
- [已知][預印受控] Vericoding,arXiv 2509.22908:現成 LLM 在 Dafny 約 82%、Verus/Rust 44%、Lean 27%;純 Dafny 驗證一年從 68% 升到 96%。讀取層級:僅搜尋摘錄 — [arXiv 2509.22908](https://arxiv.org/pdf/2509.22908)
- [新][同儕受控] DafnyPro(POPL 2026 Dafny 工作坊,arXiv 2601.05385):DafnyBench 上 Claude Sonnet 3.5 達 86% 正確證明。miniF2F-Dafny:自動化本身約 40.6%,最佳 LLM 55.7%(pass@4),LLM 最適合給高階指引。讀取層級:僅搜尋摘錄 — [DafnyPro](https://popl26.sigplan.org/details/dafny-2026-papers/12/DafnyPro-LLM-Assisted-Automated-Verification-for-Dafny-Programs)、[miniF2F-Dafny](https://popl26.sigplan.org/details/dafny-2026-papers/16/MiniF2F-Dafny-LLM-Guided-Mathematical-Theorem-Proving-via-Auto-Active-Verification)
- [新][意見] de Moura 2026-02-28:Claude 將 zlib 轉成 Lean,定理 `zlib_decompressSingle_compress` 證明壓縮後解壓回原資料,含 `data.size < 1024 * 1024 * 1024` 前置條件;最佳化版本等價證明仍在進行。原文說「Testing and proof are complementary」,且承認 zlib 比資料庫或分散式系統單純。作者是 Lean FRO 首席架構師。讀取層級:全文摘錄 — [de Moura](https://leodemoura.github.io/blog/2026-2-28-when-ai-writes-the-worlds-software-who-verifies-it/)
- [新][觀測] Rust-to-Lean 經驗報告,arXiv 2605.30106:AI 能有效關掉結構性證明義務,複雜不變量仍要人工。讀取層級:僅搜尋摘錄 — [arXiv 2605.30106](https://arxiv.org/html/2605.30106)
- [新][意見] 2026-07 部落格主張形式驗證可消除審查瓶頸;ReversingLabs 則說「complements rather than replaces these controls」。讀取層級:僅搜尋摘錄 — [Wiese](https://georgwiese.github.io/posts/formal-verification-ai/)、[ReversingLabs](https://www.reversinglabs.com/blog/can-lean-improve-security-for-ai-coded-software)
- [新][預印受控] 測試當規格神諭,arXiv 2601.12845:多模型加修復提示解出 TESTDAFNY110 的 98.2%。讀取層級:僅搜尋摘錄 — [arXiv 2601.12845](https://arxiv.org/pdf/2601.12845)

### 與既有主張的衝突

- 未發現直接衝突。若既有筆記把規格生成視為已解決,VeriContest 的 48.31% 與 Vero 最難 repo 為零的結果是反證;本輪沒有逐篇比對 `世界解` 的相關段落。

### Inferences

- 形式驗證把審查的工作移到規格,而不是消滅。審規格的成本應該算進去,這也是 Vero 需要稽核機制的原因。
- 證明可補的是**審查最不擅長**的部分:窄但高後果的不變量(序列化往返、權限判斷、金額)。Lumos 的 ★INVARIANT★ 正好是這種形狀,但它和證明助理之間沒有資料可談效益。
- 零依賴家規下,Lean、Dafny 工具鏈成本高;對應的現實選項是 Hypothesis 式屬性測試加合約綁定測試,然後把高價值不變量留作未來候選。這是判斷,不是研究結論。
- 規格先行作為「審查替代」的直接效益,這輪沒有量化證據,所以不能在報告裡寫成已證實。

### Gaps

- 沒有找到任何 Kani 加 LLM 用於代碼審查的研究或現場報告。
- 沒有找到規格先行、合約或形式驗證與「審查發現量或逃逸率」對照的受控研究。
- 沒有找到企業把證明當作合併條件、取代人工審查的量化案例;AWS Cedar 這類案例這輪沒查。
- 上面的百分比分屬不同基準,彼此不可比較。
