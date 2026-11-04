# 變異測試在業界與 AI 生成測試中的用法：全文研讀報告

整理日期：2026-11-02。下載檔與抽出的純文字都在 `scratchpad/papers/mutation/`（未刪，交編排者處理）。

## 讀取狀態總表

| # | 文獻 | 讀到的版本 | 全文？ |
|---|---|---|---|
| 1 | Practical Mutation Testing at Scale（Google） | arXiv 2102.11378v2（2021-02-26）全文；另下載 IEEE TSE 已接受稿（DOI 10.1109/TSE.2021.3107634，正式刊於 TSE 48(10), 2022）比對關鍵段落 | 是（兩版） |
| 2 | Does mutation testing improve testing practices?（Google） | arXiv 2103.07189v1 全文。**出處更正：是 ICSE 2021 Technical Track（pp. 910–921），不是 ICSE 2023** | 是 |
| 3 | TestGen-LLM（Meta） | arXiv 2402.09171v1（FSE 2024 Industry）全文 | 是 |
| 4 | ACH（Meta） | arXiv 2501.12862v1（FSE Companion 2025）全文 | 是 |
| 5 | Test vs Mutant / AdverTest | arXiv 2602.08146v3（2026-08-31，ISSTA 2026 / PACMSE 3(ISSTA)）全文 | 是 |
| 6 | MutGen | arXiv 2506.02954v8（2026-04-15）全文 | 是 |
| 7a | Mutant-Kraken（ICSTW 2024, pp. 227–236） | **只讀到摘要**（IEEE 付費牆，找不到公開 PDF）＋工具 README | 否 |
| 7b | pitest issue #579 | 頁面全部留言（WebFetch 摘要＋短引文） | 是 |
| 7c | Beam PR #365 | `gh` 取 PR 原文與完整 diff，另抓合併後第一次排程執行的 CI 日誌 | 是 |
| 7d | arcmutate | 官網首頁、Kotlin／Android 文件、授權條款、外掛版本紀錄 | 是 |

讀的過程中發現的出處差異（交給下游時別抄錯）：
- 第 2 篇是 **ICSE 2021**，不是 2023。
- 第 1 篇的 arXiv v2 寫「500,000,000 tests」，TSE 版改成「150,000,000」。其他關鍵數字（7 倍檔案數、每行一個、15%→80%→89%、中位數 820/77/7）兩版相同。
- Google 每次審查的上限在兩篇寫法不同：TSE 寫「at most 7 times the number of total files in a changelist」，ICSE 寫「no more than seven mutants are reported per file」。
- TestGen-LLM 的摘要寫 11.5%，正文寫「approximately 10%」（196/1,979 = 9.9%）。

---

## 1. Practical Mutation Testing at Scale: A view from Google（Petrović、Ivanković、Fraser、Just）

**版本**：arXiv v2 全文＋TSE 接受稿比對。

**實驗設計**
- 規模：776,740 份待審改動、產生 16,935,148 個變異、其中 2,110,489 個被顯示給人看、66,798 個收到開發者回饋。使用者超過 24,000 名開發者、1,000 多個專案。
- 語言：服務支援 10 種，**包含 Java 與 Kotlin**。不過分析排除了 Kotlin：「SQL, Common Lisp, and Kotlin are excluded from our analyses because of insufficient data」（表 3；Kotlin 只有 42,209 個變異，占 0.2%）。Java 有 2,894,772 個（17.1%）。**論文裡沒有任何 Kotlin 或 Android 的結論。**
- 量了什麼：產生的變異數（RQ1）、變異存活率（RQ2）、開發者判定有用的比例（RQ3）、依程式上下文挑變異算子的效果（RQ4）。

**Google 怎麼挑給人看的變異**
1. **只變異改到、而且有測試覆蓋的行**：「Mutation testing is done incrementally, mutating only changed code during code review, rather than the entire code base」（摘要）。「An AST node is eligible for mutation if it is covered by at least one test and if it is not arid」（§2）。沒覆蓋的行交給覆蓋率回報，不另外產生變異。
2. **每行最多一個變異**：TSE 版 §2.2 寫「The Mutation Testing Service generates at most one mutant per line, for scalability reasons and based on the insight that the vast majority of mutants for a given line share the same fate」。如果那一個變異被測試抓到，這一行就不再補產生（§4）。
3. **每次審查有總量上限**：「We limit the number of reported mutants to at most 7 times the number of total files in the changelist, to ensure that the cognitive overhead of understanding the reported mutants is not too high, which might cause developers to stop using mutation testing. 7 is a result of heuristics collected over the years of running the system.」（§2.3）
4. **只用五種算子**：AOR、LCR、ROR、UOI、SBR（表 1）。**被拿掉的算子是 ABS**：「the ABS (Absolute value insertion) mutation operator was reported to predominantly create unproductive mutants, mostly because it acted on time-and-count related expressions that are positive and nonsensical if negated, and is therefore not used. Note that this is due to the style and features of our codebase, and may not hold in general.」（§2.2）SBR 刻意不刪 return、continue、break，也不刪變數宣告（第 2 篇 §IV-C）。
5. **「乾枯節點」（arid node，作者對不值得變異的程式碼位置的稱呼）在產生變異之前就壓掉**：「There are more than a hundred rules for arid node detection in our system.」（§3.1）另有超過 200 個函式家族的模糊名稱規則。這些規則依回饋分成四類（表 2）：會編譯失敗（1 條）、等價（13 條）、能殺但沒價值（16 條，「Very common」）、重複（2 條）。
6. **最有效的壓制規則**：「The highest mutant productivity gains came from the three heuristics implemented in the early days: suppression of mutations in logging statements, time-related operations (e.g., setting deadlines, timeouts, exponential backoff specifications etc.), and finally configuration flags.」靠這三條，有用比例大約從 15% 升到 80%，之後陸續補規則到 89%（§3.2.5）。
7. **規則不必完全正確**：「we have had much more important improvements of perceived mutant usefulness from unsound heuristics.」（§3.2.5）
8. 附錄 A 的壓制類別：日誌、記憶體容量（如 `ArrayList(64)`）、監控計數、時間與逾時、追蹤與 assert、管線組裝（Beam/TensorFlow）、**分支條件有覆蓋但分支本體沒跑到**（交給覆蓋率處理）、浮點相等、程式旗標、低階系統呼叫、flush/close、灰度開關、快取查找、無限大、對數值不敏感的參數（zip、比較器、split limit）、集合長度與 0 比較、**equals/hashCode/toString 這類樣板方法**、提早 return、`==`/`===` 互換、min/max 夾值、**Java 依賴注入模組（Guice/Dagger）**、Python main/版本檢查等。附錄開頭的但書：「these heuristics are specifically tailored for the environment of the developers who provided the feedback, and a different context will require deriving new, appropriate heuristics.」

**什麼叫不具生產力的變異（unproductive mutant）**
「developers at Google initially classified 85% of reported mutants as unproductive. An unproductive mutant is either trivially equivalent to the original program or it is detectable, but adding a test for it would not improve the test suite」（§1）。例子是集合初始容量。作者特別警告，為這類變異補測試反而有害：「these tests, if written and added, would even have a negative impact because their change-detector nature (specifically testing the current implementation rather than the specification) violates testing best practices and causes brittle tests and false alarms.」

**開發者回饋怎麼收**
- 變異以「發現」（finding）的形式出現在審查工具 Critique，**不強制處理**：「Unlike human-generated comments, findings do not need to be resolved by the author before submission, unless a human reviewer marks them as mandatory.」（§2.4）
- 一鍵回饋：「If an automated changelist analyzer finding (e.g., a surviving mutant) is not perceived as useful, developers can report that with a single click on the finding. If any of the reviewers consider a finding to be important, they can indicate that to the changelist author with a single click.」也就是「Please fix」和「Not useful」兩個連結。
- 回饋轉成規則的方式是人工：「This process is manual: if we decide a certain mutation is not productive and that the whole class of mutants should not be created, the rule is added to the expert function.」
- 為什麼不給「變異分數」：「we were also unable to find a good way to surface it to the developers in an actionable way, as it is neither concrete nor actionable, and it does not guide testing.」（§2）

**主要結果**
- RQ1：每份改動產生的變異中位數「820 for traditional mutagenesis, 77 for 1-per-line selection, and only 7 for arid-1-per-line selection」（表 5）。
- RQ2：所有產生的變異有 87.5% 被既有測試抓到。各算子存活率在 9.5%（UOI）到 16.3%（LCR）之間。
- RQ3：有回饋的變異裡「82% of all surfaced mutants with feedback were labeled as productive」，上線期間由 80% 升到 89%。依語言看，Java 87.2%、Python 70.6%。「ROR, LCR, and SBR mutants show similar productivity, whereas AOR and UOI mutants show noticeably lower productivity.」（ROR 84.1%、UOI 74.5%）
- RQ4：「Context-based selection improves the probability that a generated mutant survives by more than 40% and the probability that a generated mutant is productive by almost 50%.」

**作者建議與限制**：作者建議用覆蓋率驅動寫測試、用變異驅動改進測試（「we use coverage to drive test case implementation, and mutatns for their subsequent improvement」，附錄 A.1.7）。限制方面，資料只來自 Google 的程式風格；壓制規則需要依環境重新累積；依上下文挑算子的做法需要百萬筆歷史資料。

**已經回答、不必重做的**：在工業規模下，「只變異改到且有覆蓋的行、每行一個、壓掉日誌／時間／旗標、每份審查有上限、以不強制的審查意見呈現」能把有用比例做到約 9 成。這套做法不必再驗證，要做的是換成我們的壓制清單。

---

## 2. Does mutation testing improve testing practices?（Petrović 等，ICSE 2021）

**版本**：arXiv 2103.07189v1 全文。正式出處是 ICSE 2021（Technical Track），不是 2023。

**實驗設計**
- 長期干預研究。實驗組是 2014 年起的 14,730,562 個變異（662,584 次改動、446,604 個檔案），對照組是只開覆蓋率的 8,788,791 次改動（3,398,085 個檔案）。
- 語言：C++ 49%、Java 33.4%、Python 12%、Go 5.7%（表 I，故障耦合資料集）。**沒有 Kotlin 或 Android 的分項。**
- 量了什麼：測試改動量（以 test hunk 計）對曝光次數的關係；變異存活率對曝光次數的關係；與 1,502 個高優先度真實錯誤的耦合；同一行多個變異的命運是否一致。

**主要結果**
- 呈現方式：「To avoid cognitive overload, no more than seven mutants are reported per file in a changelist.」「The mutation system does not offer manual invocations or project-level analyses—only the change-based approach.」
- RQ1：曝光次數與測試改動量的等級相關 rs = 0.9（p < .001），覆蓋率組是 rs = −0.24。審查期間加的 test hunk 中位數，變異組 1、覆蓋率組 0。
- RQ2：曝光次數與存活率 rs = −0.50；審查者要求修的比例 rs = −.34。「RQ2: As exposure to mutation testing increases, developers tend to write stronger tests in response to mutants.」
- RQ3：「Mutants are coupled with 70% of high-priority bugs, for which mutation testing would have reported a live, fault-coupled mutant on the bug-introducing change.」（1,043/1,502）。沒耦合到的錯誤抽 50 個看：算子太弱 14、缺算子 13、根本沒有對應算子 23。後者的結論是「mutation testing is effective in guiding testing to assess whether an algorithm is correctly implemented but not whether the correct algorithm is implemented.」
- RQ4：「Mutants are heavily redundant. In more than 90% of cases, either all mutants in a line are killed, or none are.」
- 為變異寫的測試是不是只為了殺變異的最小測試？作者的看法：「Code reviews are a safety net and minimal, change-detector tests would not pass code review.」「we count on code authors to push back on introducing tests to kill unproductive mutants, and we count on reviewers to push back on low quality tests, specifically written to kill mutants.」

**作者建議與限制**：作者不主張追求更高的耦合率：「If 1% more coupling means 100% more mutants, or worse 100% more unproductive mutants, then this is undesirable」。限制有幾點：只有一家公司；不是隨機對照實驗（作者已排除三個替代解釋）；耦合分析的錯誤中只有 10.8% 當時開著變異測試。

**已經回答、不必重做的**：每行只挑一個變異就夠代表；給人看的存活變異會讓人多寫、寫強測試；這些變異與七成高優先度真實錯誤耦合。這些在 C++/Java/Python/Go 上已有長期證據。

---

## 3. Automated Unit Test Improvement using Large Language Models at Meta（TestGen-LLM，FSE 2024）

**版本**：arXiv v1 全文。

**實驗設計**
- 語言：**Android 的 Kotlin 測試類別**（Instagram、Facebook）。
- 評估模式：Reels 與 Stories 的 86 個 Kotlin 元件（Stories 31、Reels 55），2 個內部模型 × 4 種提示。
- 部署模式：2023-10-29 到 12-29 的三場 test-a-thon，共 1,979 個測試類別。
- 量了什麼：建置、通過、增加覆蓋三道關卡的通過率，以及工程師的接受率。

**過濾條件與重跑次數**（§2）
1. 能建置：「Any code that does not build is immediately discarded」。
2. 第一次執行就要通過：「TestGen-LLM discards any test case that does not pass on first execution.」
3. 連跑五次都要通過：「a test that does not pass on every one of five executions is deemed flaky.」
4. 要增加覆蓋：「Any test that does not improve coverage is also discarded.」初期試行後改成**逐支測試**算覆蓋增量，並另外濾掉跟之前產生過的測試內容完全相同的（「it simply needed to check for syntactic equality of test bodies」，§5）。

**為什麼丟掉第一次就紅的測試**：「Any test that does not pass may reveal a fault. However, it is more likely that the test simply contains an incorrect assertion. We want an entirely automated workflow. Without an automatable test oracle [7], TestGen-LLM cannot automatically determine whether a failing test has found a bug, or whether it merely contains an incorrect test assertion.」作者的結論是：「The effect of this filter is to preserve only tests that can be used for regression testing」。換句話說，它只產生**以現行行為為準**的回歸測試。

**主要結果**
- 評估：「75% of test classes had at least one new test case that builds correctly」、57% 能可靠通過、25% 能增加覆蓋。
- 部署：「196 test classes were successfully improved, while the TestGen-LLM tool was applied to a total of 1,979 test classes」，「73% of TestGen-LLM test improvements were accepted by developers」。
- Facebook 的 280 份改動：144 接受、64 拒絕或放棄、61 沒人審、11 撤回。
- 被拒的理由：測試平凡的 getter、違反「一支測試一個責任」（2 支）、沒有斷言。第一場還有一支因為「TODO」沒寫斷言被退。
- 每次嘗試的成功率：Facebook 0.05、Instagram 0.04（表 3）。溫度 0 被選為預設。
- 時機：「diff time deployment is far more effective, because it maximizes relevance」。

**作者建議與限制**：覆蓋只是權宜代理：「Mutation coverage [23] would likely be the best performing criterion... However, it is challenging to deploy such computationally demanding techniques at the scale we would require [8].」大規模時只有行覆蓋（JaCoCo 的分支覆蓋做不到那個規模）。產生的測試會模仿既有風格，也會模仿已淘汰的寫法。

**已經回答、不必重做的**：在 Android Kotlin 上，「建置→第一次就綠→連跑五次都綠→逐支有增量」這條過濾鏈，能讓 AI 補的測試有約七成被人接受。這條鏈只保證回歸，不保證預期值正確。

---

## 4. Mutation-Guided LLM-based Test Generation at Meta（ACH，FSE Companion 2025）

**版本**：arXiv 2501.12862v1 全文。

**實驗設計**
- 語言：**Android Kotlin**。「ACH was applied to 10,795 Android Kotlin classes in 7 software platforms」。
- 模型：Llama 3.1 70B 一個模型擔任三個代理。
- 部署期間 2024-10-28 到 12-31。另有 Messenger 與 WhatsApp 兩場隱私主題的 test-a-thon，共 191 支測試由人審。
- 量了什麼：變異能否建置、既有測試會不會放過它、等價判斷的準確度、新測試的接受率與隱私相關度、新測試是否增加行覆蓋。

**ACH 怎麼用變異當目標**（圖 1、表 1）
1. 輸入是一段描述關注點的自由文字（例如過去的隱私錯誤）。「Make a fault」代理據此在類別裡植入相似的錯誤，並用註解 `// MUTANT <START>`/`<END>` 標出改了哪裡。
2. 變異必須能建置，而且**既有測試在它上面照樣通過**（代表目前抓不到）。
3. 拿掉與原碼字面相同的變異，再交給 LLM 判斷是否等價。
4. 「Make a test to catch fault」代理拿原類別、變異類別、既有測試，寫出「will fail on the mutant version of the class, but would pass on the correct version」的測試。
5. 接著沿用 TestGen-LLM 的關卡：能建置、在原碼上通過、**在變異上不通過**，才送審查。保證項目寫的是「(2) Valid Regression Tests: The tests pass and do so consistently, so they are non-flaky」、「(3) Hardening: The new tests catch faults that no existing test can catch」。（ACH 正文沒有重述重跑次數，「consistently」是承接 TestGen-LLM 的五次。）
6. 「Once a mutant is found that builds and passes, the workflow terminates for the current class under test.」
7. 審查者只看測試、不看變異：「Our workflow requires only that engineers review test cases, not mutants.」「By construction, such mutants are non-equivalent, so the engineer will never see an equivalent mutant.」

**主要結果**
- 產生 31,677 個變異，其中 9,095 個（29%）能建置且既有測試放過。判定為非等價的有 4,660 個。最後產生 571 支測試。
- 「Of these 571 tests, 277 would have been discarded had we chosen to focus solely on the line coverage test adequacy criterion」（49%，表 8）。
- 人審 191 支：接受 73%、拒絕 27%；36% 被評為可能或確定與隱私相關。被接受的原因是增加了非平凡程式的覆蓋，或測到棘手的邊角情況；被拒的原因是沒增加覆蓋、只測平凡程式，或用了已淘汰的 API。
- 等價判斷：精確率 0.79、召回率 0.47。拿掉字面相同的變異、再剝掉 LLM 加的註解後，提升到 0.95/0.96。等價變異裡有 61% 只是「誤導註解」，也就是只加了註解、沒改程式。
- 與 TestGen-LLM 比：殺變異的比率 15% 對 2.4%。「targeting mutants can also elevate coverage, but targeting coverage will be inadequate to kill mutants.」
- 審查量：WhatsApp 的工程師主動提出每人審 12 支，因為「large enough for calibration, yet small enough to avoid reviewer overload」（註 4）。

**作者建議與限制**：只能防未來的回歸，抓不到現存錯誤，因為以現行版本當答案：「it cannot detect existing faults residing in the code base. To do this requires us to tackle the well known Oracle problem」。變異和原本關注點的相關度沒有可靠的量法。等價判斷的好成績可能只限 Kotlin/Android/Meta/隱私這個範圍。

**已經回答、不必重做的**：在 Android Kotlin 上，讓 LLM 依「這次關注的需求」植入錯誤、要求新測試「原碼綠、錯版紅」，這條流程在工業規模可行；用覆蓋當過濾會丟掉約一半真正有抓錯能力的測試；LLM 產生的變異只要做「字面相同＋剝註解」兩步前處理，等價問題幾乎就消失了。

---

## 5. Test vs Mutant: Adversarial LLM Agents for Robust Unit Test Generation（AdverTest，ISSTA 2026）

**版本**：arXiv v3（2026-08-31）全文。

**實驗設計**
- **Java**（JUnit 4、Java 8、Mockito）：Defects4J 200 個錯誤＋GrowingBugs 47 個錯誤，共 727 個受測方法。另加 Python 的 SWE-Rebench 12 個問題。**沒有 Kotlin 或 Android。**
- 模型：DeepSeek-v3.2 與 GPT-OSS-120B，溫度 0。最多 5 輪；變異代理每次的配額是 max(2×行數, 50)。
- 量了什麼：真實錯誤檢出率（FDR）、行與分支覆蓋（Cobertura）、API 成本。

**做法**：寫測試的代理和產生變異的代理輪流出手。變異限定改單一行。殺掉的定義是 `Δ = Fail(T, m) \ Fail(T, P)`，也就是要扣掉在原程式上本來就失敗的測試。**和 Meta 相反的是，它保留在原程式上失敗的測試**：「while all tests in T are compilable, they may still include runtime failures (e.g., assertion errors) by design... Such failure-exposing tests are retained」。

**主要結果**
- Defects4J（DeepSeek）的 FDR：AdverTest 66.63%、HITS 61.38%、EvoSuite 44.36%。EvoSuite 覆蓋最高，但檢出率較低。
- 消融（50 個錯誤的子集，表 2）的 FDR：完整版 54、拿掉迭代 26、拿掉存活變異細節 40、**只給覆蓋回饋 34**、**改用規則式 MAJOR 變異 46**。作者說：「surviving-mutant feedback carries information beyond what coverage signals alone provide」。
- 輪數：FDR 從 35.3% 升到 67.6%，同期行覆蓋只從 88.0% 升到 94.8%。
- LLM 變異的品質：90.3% 能編譯、存活率 36.2%、等價率 3.45%。
- 成本：每個方法約 $0.27、484.95 秒。新測試不會馬上回頭對各自的變異再驗：「Prior work [57] has shown that while immediate feedback can increase mutant detection rates, it comes at a substantial cost: up to ×7.29 higher LLM API token usage」。
- Python 版另外加了「有覆蓋、但還沒有任何變異」的行當變異來源（S3），檢出數從 7/12 升到 11/12。

**作者建議與限制**：測試和變異都是在**修好的版本**上產生，有時變異剛好落在修正才加的程式碼上。只涵蓋兩種語言生態；消融只用 50 個錯誤；溫度 0 仍有不確定性。

**已經回答、不必重做的**：在 Java 研究基準上，「把存活變異的具體差異餵回給 LLM、迭代幾輪」比只給覆蓋回饋檢出更多真實錯誤；LLM 產生的變異比規則式變異更有效。

---

## 6. Mutation-Guided Unit Test Generation with a Large Language Model（MutGen）

**版本**：arXiv v8（2026-04-15）全文。

**實驗設計**
- **Java** 的方法層級：HumanEval-Java 104 題、LeetCode-Java 100 題，都是單一類別、單一方法。工具用 PIT 的 DEFAULTS 算子組，模型是 Llama-3.3 70B、溫度 0，重複三次。**沒有 Kotlin 或 Android，也沒有真實專案依賴。**
- 量了什麼：變異分數、行與分支覆蓋（JaCoCo）、各算子殺除率、修復率。

**主要結果**
- 「some test suites achieve 100% coverage but only 4% mutation score」（摘要）。
- 變異分數：MutGen 89.5% 與 89.1%；EvoSuite 69.5% 與 58.9%；不給變異回饋的純 LLM 77.9% 與 69.9%（表 I）。
- 迭代約到第 4 輪就收斂，所以設上限 4 輪。
- 難殺的算子：VoidMethodCalls 69.2%（HumanEval）、TrueReturns 57.7%（LeetCode）。原因是副作用不反映在輸出上，以及死碼。
- 消融：影響最大的是「拿掉原始碼註解、改用 LLM 摘要」。原因是「comments in the target code can mislead LLMs」。
- 修測試：約 50% 失敗的測試修得好。修不好的抽 50 支看，74% 是預期值錯。

**特別要注意的做法**：它的修復提示直接把失敗測試的預期值改成實際輸出：「If an error follows the pattern: ... expected:error value but was:correct value ... replace the expected value with the correct one.」assertTrue/False 失敗就直接對調。作者自己在效度威脅裡承認：「Oracle Problem. We assume the original code is correct and only address assertion errors that cause Maven build failures. This simplification can lead to incorrect test oracles and false positives.」

**已經回答、不必重做的**：把 PIT 報告裡「哪一行、哪個算子、存活或沒覆蓋」逐條放進提示，比只要求高覆蓋更能讓 LLM 寫出殺變異的測試；覆蓋率接近 100% 時，變異分數仍能差很遠。

---

## 7. Kotlin／Android 工具實況

### 7a. Mutant-Kraken（Morales、Deng、Dehlinger、Chakraborty，ICSTW 2024）

- **只讀到摘要，全文在 IEEE 付費牆後**，沒有找到公開 PDF。
- 摘要原文：「Existing tools, such as PIT and arcmutate, face challenges in effectively supporting Kotlin mutation testing.」它用 Tree-sitter 在原始碼層級變異，有「seven, novel Kotlin-specific mutation operators, addressing features like null checks and functional programming」。評估只做了 3 個開源 Kotlin 專案，摘要只說「feasible, efficient, and effective」，沒給數字。
- 工具現況：README 寫「Mutant Kraken is currently in beta and is not ready for production use.」最新版 v0.1.6（2025-11-06）。算子包括 `!!` 斷言、Elvis 移除／改值、when 分支移除、any/all/none 與 forEach/map/filter 互換等。
- 摘要與 README 都沒提 Android 或協程。

### 7b. pitest issue #579「pitest generates unhelpful mutations when using Kotlin's coroutines」

- 2019-03-01 由 matejdro 開。用 `GlobalScope.launch {}` 的程式碼產生大量「replaced equality check with false」變異，但原始碼裡根本沒有相等比較。環境是 Android 分支的 gradle-pitest-plugin 0.1.9、pitest 1.4.0、`ALL` 算子。
- 留言重點：Kotlin 的位元組碼和原始碼不是一對一；2020 年仍有人回報 continuation/completion 相關的大量錯誤；維護者 hcoles 表示免費的 pitest-kotlin 外掛不支援協程，也沒人維護。
- **2022-03-02 維護者以「Arcmutate 的 Kotlin 外掛已支援協程」結案。** 討論中沒有提到 `avoidCallsTo` 或 `excludedMethods` 這類免費的繞道方法。

### 7c. Beam PR #365「build(android): advisory Kotlin mutation testing with PIT」（2026-10-29 合併）

設定（取自 diff 原文）：
- `pl.droidsonroids.pitest` 0.3.0。PIT 引擎另外釘在 1.30.1，理由是「pinned so a plugin bump cannot move it silently」。
- `targetClasses = dev.beam.android.*`。
- `excludedClasses`：`uniffi.*`；Hilt/Dagger 產生的類別（`hilt_aggregated_deps.*`、`dagger.*`、`*.Hilt_*`、`*_HiltModules*`、`*_HiltComponents*`、`*_ComponentTreeDeps`、`*_GeneratedInjector`、`*_Factory`、`*_MembersInjector`）；`dev.beam.android.core.testing.*`（共用假實作）；`*.BuildConfig`、`*.R`、`*.R$*`、`*.ComposableSingletons*`。
- **刻意保留手寫的 Hilt `@Module` 當變異目標**，理由是「they hold real decisions」。這與 Google 附錄 A.3.2 把依賴注入模組列為不值得變異的做法相反。
- `failWhenNoMutations=false`、`timestampedReports=false`、輸出 HTML 與 XML、`threads` 設成核心數。**沒有** `excludedMethods`、`avoidCallsTo`、`mutators`，也沒有任何 Kotlin 或協程的過濾。
- **只提醒、不擋**：「It never blocks a merge.」工作流的變異步驟 `continue-on-error: true`，沒有 `mutationThreshold`：「A threshold would make an advisory run fail」。
- **不在 PR 上跑，只排程或手動觸發**，理由是「PIT has no free changed-lines mode like `cargo mutants --in-diff`, so a pull-request run would mutate every module on every push」。
- PR 自報的數字：`:core:media` 634 個變異、244 個被殺；`:feature:auth` 364 個；`:core:ffi` 995 個。作者自己列的缺口：「Whether PIT's mutants reach code that only Robolectric-run tests exercise was not established.」

**合併後第一次排程的實況**（我抓的 CI 日誌：run 41295409888，2026-11-01）：
- 變異步驟跑了約 10 分 18 秒，結果是 Gradle `BUILD FAILED in 10m 17s`，但 `Mutants (Android)` 這個工作的結論顯示 **success**。
- 原因是 `:app:pitestDebug` 一開始就停了：「PitHelpError: 10 tests did not pass without mutation when calculating line coverage. Mutation testing requires a green suite.」失敗的是 MainViewModelTest、BeamAppBackStackTest、ContinueWatchingWidgetTest 等測試。日誌裡另有「Method isLoggable in android.util.Log not mocked」。
- 13 個套用的模組只有 4 個開跑、3 個有結果，其他 `feature:*` 都沒跑到。
- 依時間順序推斷，三個有結果的模組是：
  - feature:admin：1,803 個變異、殺掉 9%、1,596 個沒覆蓋
  - core:ffi：576 個、36%，耗時 7 分 41 秒
  - core:media：648 個、52%，耗時 9 分 49 秒
- 也就是說，「只提醒」加上 `continue-on-error`，讓九成模組沒跑這件事在工作狀態上看不出來。

### 7d. arcmutate（PIT 作者 Henry Coles 的商業外掛）

- 官網首頁的定價段：「Base — $8 per user/month」（擴充算子、subsumption 分析等）；「Pro — $12 per user/month: Everything in Base plus Spring framework support, Git integration, incremental analysis」；「Open Source — Free licenses for open-source projects.」首頁也說「ArcMutate lets you work on massive code-bases mutating only modified code since a commit.」
- 授權條款：以購買時登記的使用者數計，期限依授權證書；到期後「Licensor may take actions so that Licensed Software no longer operates.」需要在專案根目錄放 `arcmutate-licence.txt`，或用動態取得授權。
- Kotlin 外掛（`com.arcmutate:pitest-kotlin-plugin:1.5.2`，需 pitest ≥ 1.22.0）：「The kotlin plugin filters out these junk mutations and removes confusing noise from mutant descriptions.」支援的特性列有 Coroutines、Inlined code、Non-null types、Lateinit 等。可用 `+KOTLIN_NO_NULLS`、`-KOTLIN_MULTI_NULL`、`+KOTLIN_EXTRA` 調整過濾強度；inline 產生的變異會標「(inlined)」。
- Android 外掛（`com.arcmutate:android:0.0.13`）：**仍是 beta**。「Instrumented tests are not supported」。Robolectric 要把 `excludeMockableAndroidJar` 設成 `false`；官方 gradle 外掛與 Android 不相容，但有客戶回報用 koral--/gradle-pitest-plugin（即 `pl.droidsonroids.pitest`）可行。0.0.12 與 0.0.13 版開始濾 Compose 產生的雜訊。
- `pl.droidsonroids.pitest` 的 README：「Experimental Gradle plugin for PIT Mutation Testing in Android projects」，「The plugin works only in Android modules.」支援 AGP 8.5.1 以上（含 AGP 9）。從 PIT 1.23.0 起，增量分析（history）移到獨立外掛 `org.pitest:pitest-history-plugin`。README 沒有「只跑改動檔」的功能。

**已經回答、不必重做的**：免費的 PIT 在 Kotlin 協程上會產生雜訊，官方解法是付費的 arcmutate Kotlin 外掛（開源專案免費）；arcmutate 的 Android 支援仍是 beta，也不支援裝置測試；免費的 Gradle 路線沒有「只跑改動行」的模式。

---

## 全組綜合：Android Kotlin 專案、AI 寫單元測試、推送前要有機械證據

依證據強弱排列。標「推論」的部分，原始證據不在 Android 或不在本情境，是我換算過來的。

### A. 強證據（工業規模、長期、多語言含 Java；Kotlin 另有 Meta 的部署）

1. **只變異這次改到、而且有測試跑到的行，不做全量。**
   - 出處：Google TSE §2.1–2.2（中位數 820→7）；ICSE 2021 RQ4（九成以上的行，所有變異命運相同）；Meta TestGen-LLM 也是在改動當下推薦（「diff time deployment is far more effective」）。
   - 換到 Android（推論）：免費的 Gradle 外掛沒有行層級的差異模式（Beam PR 的決策 3），能做的是依 `git diff` 算出改到的類別，把它們當 `targetClasses` 傳給 PIT，做到類別層級。要做到行層級得用 arcmutate Pro 的 Git 整合（$12/人/月，開源免費）。

2. **把存活變異當成審查意見送出，不設分數門檻。**
   - 出處：Google 說分數「neither concrete nor actionable」；Google 的 findings 不強制處理，除非審查者標成必修；Beam 不設 `mutationThreshold`；ICSE 2021 證明這種「意見」就足以讓人寫更強的測試。
   - 機械證據該證什麼（推論）：證「這次的變異執行有效」，也就是基準全綠、改到的類別真的產生了變異、報告是新的。再加上「每個存活變異都有處置」：補測試殺掉，或附理由標成不值得、等價。

3. **每份審查設上限，每行最多一個變異。**
   - 出處：Google 每份改動最多「7 倍檔案數」，ICSE 寫成每檔 7 個；ACH 的審查者自己要求每人 12 支測試。
   - 換到 Android（推論）：PIT 預設會在同一行產生多個變異，送進審查前要先依行去重、再截到上限。

4. **壓制清單先放日誌、時間、設定旗標三類，再依回饋人工補。**
   - 出處：Google §3.2.5 靠這三類把有用比例從 15% 拉到 80%，最後到 89%；附錄 A 有完整類別。
   - Android 對應（推論）：
     - 日誌：`Log.*`、Timber、`println`
     - 時間：`delay()`、`withTimeout`、退避參數、`Duration`
     - 設定：`BuildConfig.*`、遠端開關、灰度比例
     - 樣板：`equals`/`hashCode`/`toString` 與 data class 產生的方法
     - 生成碼：Hilt/Dagger 產生的類別、`R`、`ComposableSingletons`（直接照抄 Beam 的 `excludedClasses`）
   - PIT 的手段是 `excludedClasses`、`excludedMethods`，以及 `avoidCallsTo`（它的定義是「packages and classes which are to be considered outside the scope of mutation」）。
   - 手寫的 Hilt module 要不要排除，Google 和 Beam 的做法相反，交給專案自己裁。

5. **AI 寫的測試，先過「能建置、原碼上連跑 N 次全綠、對目標錯誤會紅」，才算有證據。**
   - 出處：TestGen-LLM 第一次就紅直接丟、要連跑 5 次全綠；ACH 要求在原碼上綠、在變異上紅。兩者都是 Android Kotlin 的工業部署。
   - 但這只證明測試對錯誤敏感、而且穩定，**不證預期值正確**：兩篇都明說以現行版本當答案（ACH：「cannot detect existing faults」）。

6. **不要用覆蓋增量當唯一的接受條件。**
   - 出處：ACH 有 49% 殺變異的測試完全沒增加行覆蓋；MutGen 有覆蓋率 100% 但變異分數只有 4% 的例子；AdverTest 只給覆蓋回饋時 FDR 34，給變異回饋時 54。

### B. 中等證據（研究基準，Java／Python，非 Android）

7. **AI 補測試時，把存活變異的具體差異（哪一行、改成什麼）放進提示，迭代 3 到 4 輪就停。**
   - 出處：MutGen 第 4 輪收斂；AdverTest 的消融。
   - 換到 Android（推論）：直接拿 PIT 的 `mutations.xml` 當提示材料，不必自建變異引擎。

8. **讓 AI 依「本次需求」自己植入錯誤，可以取代或補充規則式變異。**
   - 出處：ACH（Kotlin，工業規模）；AdverTest 用 MAJOR 規則式變異時 FDR 46，用 LLM 變異時 54。
   - 等價判斷的前處理只要兩步：字面相同直接丟、剝掉植入時加的註解後再比（ACH 從 0.79/0.47 提升到 0.95/0.96）。

9. **不准讓 AI 把失敗測試的預期值改成程式實際輸出。**
   - 出處：MutGen 的修復提示就是這麼做，作者承認會產生錯的預期值；未修好的失敗有 74% 是預期值錯。這是反面教材。

### C. Kotlin／Android 工具面（工具文件、issue 與實跑日誌）

10. **協程雜訊怎麼壓：**
    - 免費 PIT 沒有官方的協程過濾（#579 是以「改用 arcmutate」結案）。
    - 選項一：買 arcmutate Base（$8/人/月，開源免費），加 Kotlin 外掛。若有 Robolectric 測試，再加 Android 外掛（beta）。
    - 選項二（推論、未驗證）：只用免費 PIT 時，把變異範圍限縮在本次改到的類別，再加上面的壓制清單。協程狀態機產生的雜訊要靠審查者標成「不值得」。這條路需要先實測雜訊比例，再決定要不要買。
    - Mutant-Kraken 自稱不適合正式使用，不考慮。

11. **工具：** `pl.droidsonroids.pitest`＋另外釘死的 PIT 引擎版本。
    - 這個外掛只能用在 Android 模組，純 JVM 模組要用上游的 `info.solidsoft.pitest`（Beam 決策 7、README）。
    - 裝置測試不在 PIT 的範圍內（arcmutate 文件）。

12. **「只提醒」要防止靜默失效。**
    - Beam 第一次排程，PIT 因基準有 10 支紅（「Mutation testing requires a green suite」），13 個模組只有 3 個出結果，工作狀態卻顯示 success。
    - 推論：推送前的證據要檢查「每個目標模組都有新的 `mutations.xml`，而且變異數大於 0」，不能只看退出碼或工作是否成功。基準紅就判 invalid，而不是判「沒有存活變異」。

13. **時間預算：**
    - Beam 在 CI 上 3 個模組約 10 分鐘；單一模組 1 到 10 分鐘，`core:media` 約 650 個變異跑了 9 分 49 秒。
    - 推論：全量放在推送前跑不完，只跑改到的類別才放得進推送前的時間。

---

## 對照 `test-quality-standard.md`

### 跟證據一致、可以保留的

- 〈開發時〉：「修 bug 與關鍵守衛沿共用規範提供實跑紅綠證據。其他測試按風險選取有代表性的故障，不要求每支測試、每輪審查跑全套 mutation。」→ 與 Google 只變異改動行、每行一個、ICSE 的冗餘結論一致。
- 〈開發時〉：「**抓錯能力**：…它只能證明對所選錯誤敏感，不能證明 expected 正確、所有錯誤均被覆蓋。」→ 與 TestGen-LLM 和 ACH 自承「只做回歸、不解決答案從哪來」一致；MutGen 的修復步驟正好是反例。
- 〈開發時〉：「測試在修復版本來就紅時，先處理基準，不能把故障結果算檢出。」→ 與 PIT 的硬規則「Mutation testing requires a green suite」，以及 AdverTest 扣掉原版就失敗的測試（`Fail(T,m) \ Fail(T,P)`）一致。
- 〈工具接入〉：「使用各專案既有 runner，选配成熟 mutation 工具。Lumos 不自建通用多語言解析器或 mutation engine」→ 與 Mutant-Kraken 仍是 beta 一致。ACH 證明「由 AI 依需求植入錯誤」不需要自建引擎，可以把它當作「故障挑本次需求」的做法。
- 表格 Android 列：「純JVM評估PIT；平台故障用既有runner」「Kotlin/Java、JUnit、AGP、Robolectric、裝置分開，JVM不等於Android」→ 與 arcmutate 說「Instrumented tests are not supported」、Robolectric 需要特別處理，以及 Beam 自列的 Robolectric 缺口一致。
- 〈共用證據格式〉：「等價變體獨立裁決，未決保留，不用100% mutation當硬目標。」→ 與 Google 不給分數、MutGen 承認等價變異擋住 100% 一致。
- 〈適配器資格考卷〉第 2 條：「重抄算法：展示故障可翻紅但仍沒有獨立來源；不得把 mutation 分數當來源審查。」→ 與 MutGen「把預期值改成實際輸出」的教訓一致。
- 〈Android 驗收標準〉不算過：「重試到過才綠」→ 與 TestGen-LLM「五次都要過」同方向。

### 建議修改的

1. **「故障證明挑本次需求」那條的社群附註，事實要更正、內容要補。** 原句：「社群：變異測試(Pitest 的 Android 外掛、arcmutate 的 Kotlin 外掛)可以補，但有人回報協程程式碼會產生大量雜訊，不當必要條件。」
   - 「有人回報」不精確。#579 已在 2022-03-02 由 PIT 維護者以「arcmutate Kotlin 外掛已支援協程」結案。更準確的寫法是：免費 PIT 在協程上有雜訊、沒有官方過濾；arcmutate Kotlin 外掛會濾（付費 $8/人/月起，開源免費）；arcmutate 的 Android 外掛仍是 beta，不支援裝置測試。
   - 「Pitest 的 Android 外掛」容易誤會。`pl.droidsonroids.pitest` 是社群維護的 Gradle 外掛分支，README 自稱「Experimental」、只能用在 Android 模組；arcmutate 另有一個 Android 外掛，用途是讓 Robolectric 測試能參與變異。兩者應該分開寫。
   - 「不當必要條件」可以保留，證據支持（Google 的 findings 不強制、Beam 只提醒）。但要補上用的時候怎麼用：只變異本次改到的類別；同一行只送一個存活變異、每份審查有上限；先壓掉日誌、時間、旗標、生成碼；存活變異當審查意見逐條處置，不設分數門檻。
2. **補一條「變異執行本身的有效性」。** 依據 Beam 的實跑：基準紅、模組沒產生報告、變異數為 0，都要判 invalid 或未驗，不能因為退出碼 0 或工作成功就當作跑過。這可以併進〈什麼證據才算過〉的「不算過的證據」。
3. **〈工具接入〉表格 Android 列可以補兩點：**
   - PIT 引擎版本要和 Gradle 外掛分開釘（Beam 的理由是怕外掛升級時偷偷換掉引擎版本）。
   - 純 JVM 模組要用上游外掛，不用 Android 分支。
4. **〈開發時〉可以補一句 AI 補測試的關卡**：AI 產生的測試要在原碼上連跑多次全綠（Meta 用 5 次），而且在本次所選故障上要紅；第一次就紅的不直接收，要先查是預期值錯還是真的抓到錯，不能讓 AI 把預期值改成實際輸出。現行標準有「重試到過才綠」不算過，但沒有要求多跑幾次確認不是偶然綠。
5. **要不要把「AI 依需求自植故障」寫成選配做法**（給標準作者裁）：ACH 是目前唯一在 Android Kotlin 工業規模驗過的變異導向 AI 測試流程，和標準的「故障挑本次需求」同一個方向，可以寫成選配。若寫進去，等價判斷的前處理只要「字面相同就丟、剝註解後再比」兩步。

---

## 來源

- [arXiv 2102.11378 Practical Mutation Testing at Scale](https://arxiv.org/abs/2102.11378)；[TSE 接受稿 PDF](https://homes.cs.washington.edu/~rjust/publ/practical_mutation_testing_tse_2021.pdf)；[IEEE Xplore 9524503](https://ieeexplore.ieee.org/document/9524503)
- [arXiv 2103.07189 Does mutation testing improve testing practices?](https://arxiv.org/abs/2103.07189v1)；[ICSE 2021 議程頁](https://2021.icse-conferences.org/details/icse-2021-papers/70/Does-mutation-testing-improve-testing-practices-)
- [arXiv 2402.09171 TestGen-LLM](https://arxiv.org/abs/2402.09171)
- [arXiv 2501.12862 ACH](https://arxiv.org/abs/2501.12862)
- [arXiv 2602.08146 AdverTest](https://arxiv.org/abs/2602.08146)
- [arXiv 2506.02954 MutGen](https://arxiv.org/abs/2506.02954)
- [Mutant-Kraken（ICST 2024 Mutation workshop 摘要頁）](https://conf.researchr.org/details/icst-2024/mutation-2024-papers/2/Mutant-Kraken-A-Mutation-Testing-Tool-for-Kotlin)；[工具 repo](https://github.com/JosueMolinaMorales/kode-kraken)
- [pitest issue #579](https://github.com/hcoles/pitest/issues/579)
- [Beam PR #365](https://github.com/justin13888/Beam/pull/365)；排程執行 run 41295409888（`gh run view` 取得）
- [arcmutate 首頁（含定價）](https://www.arcmutate.com/)、[Kotlin 文件](https://docs.arcmutate.com/docs/kotlin.html)、[Android 文件](https://docs.arcmutate.com/docs/android.html)、[授權條款](https://docs.arcmutate.com/licence.html)、[Android 外掛版本紀錄](https://docs.arcmutate.com/docs/releases/android-plugin.html)、[Kotlin 外掛版本紀錄](https://docs.arcmutate.com/docs/releases/kotlin-plugin.html)
- [pl.droidsonroids gradle-pitest-plugin](https://github.com/koral--/gradle-pitest-plugin)；[PIT Maven 參數說明](https://pitest.org/quickstart/maven/)
