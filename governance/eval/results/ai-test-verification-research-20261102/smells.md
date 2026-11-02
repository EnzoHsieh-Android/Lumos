# AI 生成單元測試的壞味道與偵測工具準確度：八篇論文可直接吸收的結論

查證日期 2026-11-02。全文來源：arXiv HTML 轉文字（數學式被濾掉的數字改從 PDF 文字補）。下載檔都在 `papers/smells/`。
標「推論」的是我把結論換算到 Android Kotlin 的部分，標「審讀意見」的是我讀原文後對作者推論的質疑，兩者都不是論文原話。

## 先講結論（白話）

- **偵測工具本身很吵**：同一批測試換一個偵測工具，比例可以差到六十個百分點；人工核對後，「一堆沒說明的斷言」（Assertion Roulette）有四成左右是誤報，某些規則甚至 100% 誤報或 100% 漏報。所以「AI 測試有 X% 壞味道」這類數字只能看相對趨勢。
- **好幾種「壞味道」人寫的測試一樣滿滿都是**：魔術數字在人寫測試裡 100%、Assertion Roulette 98.83%，研究者自己也說魔術數字「可能在情境下無害」。拿這些去擋 AI 測試等於擋所有測試。
- **真正跟「測試沒用」直接相關的**是：沒有斷言、空測試、吞例外讓測試永遠綠、斷言太弱、漏邊界情境。這幾類最值得管，其中前三類可以機械掃。
- **mock 比較多（36% 對 26%）是真的，但「多就是壞」沒有被證明**；同一倉庫內比較差距只有可忽略到小。

---

## 1. arXiv 2410.10628 — On the Diffusion of Test Smells in LLM-Generated Unit Tests（Ouédraogo 等）

**版本與全文**
- 派工寫 v2；最新是 **v3（2026-08-01，已被 TOSEM 接受）**，標題從 v1/v2 的 "Test smells in LLM-Generated Unit Tests" 改成現名。我讀的是 v3 全文。
- 重要差異：v3 新增了**人工核對偵測工具準確度**（Finding 7、表 11–12）和統計檢定；我抓 v2 HTML 核對，v2 裡沒有 "manual oracle"、"precision" 字樣，Finding 只有 15 條（v3 是 19 條）。所以要用 v3。

**實驗設計**
- 語言：**只有 Java／JUnit**（Benchmark 1 的提示要求產 JUnit 4）。沒有 Kotlin、Android。作者明寫只能當 Java 的證據。
- 模型：GPT-3.5、GPT-4、Mistral 7B、Mixtral 8x7B（類別層級）；GPT-3.5、GPT-4、CodeLlama-13B-Instruct（方法層級）。
- 資料：
  - Benchmark 1：Defects4J、SF110、CMD 上 20,505 份類別層級測試，五種提示法（ZSL、FSL、CoT、ToT、GToT）。
  - Benchmark 2：TestBench 的 972 支方法層級測試（108 個函式 × 3 模型 × 3 種上下文）。
  - 對照：EvoSuite 14,469 份；人寫測試 779,585 支，來自 34,635 個 Java 專案（絕大多數是 CAT-LM）。
- 工具：TsDetect v2.2 與 JNose，各 21 種壞味道；另人工抽樣 240 個測試實體核對。

**主要結論與數字**
- Assertion Roulette 最普遍（§4.1）：類別層級 LLM "38–49% ... according to TsDetect, and 50–100% according to JNose"；方法層級 "92.8–99%"。
- 人寫測試同樣滿是 AR（§4.4）："human suites are dominated by Assertion Roulette (AR: 98.83%) and Dependent Test (DpT: 81.22%)"。
- 作者自己把 AR 當底噪（§4.1）："we treat Assertion Roulette as a structural baseline"，並引 Bai 等："its measurable impact on objective code-quality outcomes is limited"。
- LLM 和 EvoSuite 的差別（Finding 2、4、6）：
  - Unknown Test（沒有斷言）在 LLM 最高到 77%，EvoSuite 只有 0–7%。
  - Exception Handling 在 LLM 7–23%，EvoSuite 93%。
  - Lazy Test 在 LLM 7–56%，EvoSuite 77–82%。
- 提示法（Finding 8）：AR 從 "20.94% (GToT) to 54.77% (ZSL)"；但 "prompting mainly redistributes smells rather than eliminating them"。
- 上下文多寡（Finding 9）："more input context alone does not mitigate key smell patterns"。
- 和人寫測試的相似度（Finding 19）：TsDetect 看起來不像（Cosine 0.34），JNose 看起來部分像（Cosine 0.77）；作者強調 "does not by itself demonstrate memorization"。

**偵測工具準確度（表 11、12，人工核對）**

| 層級 | 壞味道 | TsDetect 精確度／召回 | JNose 精確度／召回 |
|---|---|---|---|
| 類別（EvoSuite／LLM） | Assertion Roulette | 0.55／1.00、0.60／1.00 | 0.34／1.00、0.62／1.00 |
| 類別 | Lazy Test | 1.00／0.98、0.91／1.00 | 1.00／1.00、0.94／0.89 |
| 類別 | Magic Number | 1.00／1.00、0.55／1.00 | 1.00／0.61、0.77／0.91 |
| 方法（LLM） | Assertion Roulette | 0.78／0.90 | 0.77／1.00 |
| 方法 | Conditional Logic | 0.73／0.44 | 0.75／1.00 |
| 方法 | Dependent Test | 30 筆全是誤報（精確度 0.00） | 30 筆全判對 |
| 方法 | Magic Number | 24 筆全漏（召回 0.00） | 24 筆全對 |

- 原文（Finding 7）："Both tools are reliable for Lazy Test, but they systematically over-report Assertion Roulette and exhibit complementary behaviours for Magic Number Test"。
- AR 的使用建議（§4.1）："AR detections should therefore be interpreted as candidates for inspection rather than as high-confidence findings."
- 兩工具平均差距（Finding 5、18）：LLM 測試上平均差 6.5–8.6 個百分點；人寫測試上 "mean difference 19 percentage points, stdev 24"；MT 在某設定差到 61.11%。
- 哪些不代表問題（§5.4）："some smells like General Fixture or Duplicated Test may indicate critical maintenance risks ..., while others (e.g., Magic Number Test) may be contextually benign"。
- 全部比例要當上限看（§5.4）："should be interpreted as detector-dependent, upper-bound estimates on actual smell incidence"。

**審讀意見**
- **人工核對的樣本小，召回率偏樂觀**：每格只有 20–60 筆，而且只從「至少一個工具報了」的案例抽，兩個工具都漏的案例根本不在樣本裡。
- **Exception Handling 的解讀前後矛盾**：
  - 表 1 把 EH 定義成壞事（"Manual exception logic disrupts automation; use framework support instead"）。
  - Finding 2 和 §5.1 卻把 LLM 的 EH 低解讀成「很少測錯誤路徑」。
  - TsDetect 的 EH 規則只看測試裡有沒有 throw／catch，量不出「有沒有測錯誤路徑」。「LLM 不測錯誤路徑」這句沒有被這個指標支持。
- **Unknown Test 的 77% 沒經人工核對**：它也是兩工具差距最大的項目之一。

**作者建議**
- 把 TsDetect／JNose 接進 CI，關鍵路徑人工檢查。
- 提示裡寫明「反壞味道」準則或給乾淨範例。
- 走「產生→偵測→修補」流程。
- 原文："LLM-generated tests should be treated as draft-quality artifacts that require validation"。

**限制**
- 只有 Java。
- 只涵蓋兩個工具都支援的 21 種壞味道，**明說不含 mock 相關壞味道**："certain mocking-specific patterns"。
- 人工核對只有一小部分。

**已經回答、我們不必重做**：Java 的 LLM 測試裡哪些壞味道多、偵測工具在 AR／LT／MT／CLT／DpT 上各自多準，都已量過；尤其「AR 偵測約四成是誤報、DpT 在方法層級全是誤報、TsDetect 在方法層級完全漏掉魔術數字」這幾點可以直接引用。

---

## 2. arXiv 2305.00418 — Using Large Language Models to Generate JUnit Tests: An Empirical Study（Siddiq 等）

**版本與全文**：v4（2024-03-09），EASE 2024。全文已讀。

**實驗設計**
- 語言：Java、**JUnit 5**。
- 模型：Codex（2K／4K 輸出上限）、GPT-3.5-Turbo、StarCoder；溫度 0。
- 資料：
  - HumanEval Java 版 160 個類別（作者自己補了標準解）。
  - SF110 的 47 個專案、194 個類別、411 個受測方法。
- 工具：JaCoCo 量涵蓋率；TsDetect 量壞味道；對照 EvoSuite 和人工寫的測試。
- 編譯不過的測試，先用 7 條自動修補規則（H1–H7）修過再量。

**主要結論與數字**
- 編譯率（表 1）：
  - HumanEval 原始 37.5–70%，修補後 76.9–100%。
  - SF110 原始只有 2.7–12.7%。
- 正確率（表 2）：HumanEval 52.3–81.3%；SF110 6.9–51.9%。
- SF110 涵蓋率（表 3）："less than 2% for all models"；EvoSuite 是 27.5%／20.2%。
- 壞味道（表 4、5）：
  - Magic Number 在 HumanEval 上**LLM、EvoSuite、人工寫的全部 100%**。
  - Exception Handling 在人工和 EvoSuite 是 100%，LLM 是 0%。
  - AR：LLM 23.8–61.3%，人工 0%。
  - Empty Test：HumanEval 0.8–3.8%；SF110 最高 7.2%（Codex 2K）。
  - Unknown Test：SF110 最高 21.2%。
  - Redundant Print 最高 10.6%；Ignored Test 只有 StarCoder 0.3%。
- 原文："We found that Magic Number Test (MNT) and Lazy Test (LT) are the two most reoccurring test smell types across all the approaches, i.e., in the unit tests generated by the LLMs and Evosuite as well as the ones created manually."
- 結論句："they heavily suffer from test smells like Assertion Roulette and Magic Number Test."

**審讀意見**
- **Magic Number 和 Lazy Test 分不出好壞**：人工寫的測試 MNT 100%、LT 100%，這兩項在這裡沒有任何區辨力。作者沒有明講，但表 4 自己就顯示了。
- **EH 在人工測試裡 100%**：表示 TsDetect 的 EH 規則在正常寫法上也會觸發（例如方法簽名宣告 throws），跟第 1 篇的質疑一致。
- **部分 Empty Test 可能是修補規則造成的**：H7 會從尾端一行行刪掉、補大括號，可能把截斷的測試修成空殼。這是推論，論文沒量。

**作者建議與限制**
- 限制只寫了 "accuracy of these tools"，**沒做偵測工具的人工核對**。
- 建議往「LLM＋SBST 混合」和 TDD 起手稿的方向發展。

**已經回答、我們不必重做**：舊一代模型產 JUnit 5 測試時常見的壞味道種類（AR、Empty Test、Unknown Test、Redundant Print）已量過；「魔術數字與 Lazy Test 連人寫的也 100%」是現成反證，不必再量。

---

## 3. arXiv 2506.14297 — Quality Assessment of Python Tests Generated by Large Language Models（Alves 等）

**版本與全文**：v1（2025-06-17，唯一版本），EASE 2025。全文已讀。

**實驗設計**
- 語言：**Python**。
- 模型：GPT-4o（經 GitHub Copilot）、Amazon Q Developer、Llama 3.3 70B。
- 提示：兩種情境，Code2Code（給程式碼）、Text2Code（只給文字描述）。
- 資料：HumanEval（Python）。**論文沒寫總共產了幾份測試套件**，我找過 164 等字樣都沒有。
- 工具：Pynose、TEMPY；執行錯誤照 Python 例外分類。

**主要結論與數字**
- 執行錯誤共 151 次（表 3）：AssertionError 64.9%、IndentationError 11.3%、SyntaxError 和 KeyError 各 4.6%。
  - AssertionError 在這裡等於「測試的預期值錯了」，因為受測程式是標準解。
- 壞味道偵測共 512 次（表 4、§5.2）：
  - Lack of Cohesion of Test Cases 41.2%、Assertion Roulette 24.2%、Programming Paradigms Blend 15.8%。
  - Non-Functional Statement 和 Unknown Test 各 3.7%、Conditional Test Logic 2.7%、Duplicate Assert 1.4%、Exception Handling 只有一次。
- 512 次偵測裡有 265 次出現在有錯誤的套件中（§5.4）。
- 提示情境（RQ3）："It was not possible to identify a consistent pattern between the three models"。
  - 摘要另說："textual prompts with detailed instructions often yielded tests with fewer errors but a higher incidence of test smells"。

**審讀意見**
- 百分比的分母是「偵測次數」，不是測試套件數，不能讀成「41% 的套件有這個問題」。
- 共現分析只是計數，沒有統計檢定；「strong relationship」的說法偏強。
- 表 2 列了 Magic Number 是可偵測項目，結果表卻沒有它，原因沒交代。
- 兩個工具都沒經人工核對。

**作者建議與限制**
- 建議人工審查、改進提示、整合靜態分析工具。
- 限制自己寫明：
  - "Detecting errors and test smells alone may not be enough to accurately determine the quality of the tests generated."
  - 只有 Python、只有 HumanEval，可能被拿去訓練過。

**已經回答、我們不必重做**：Python 小題目上，AI 測試最常見的失敗是預期值錯（約三分之二），而不是語法；壞味道以「測試案例不內聚」和 AR 為主。對我們的用處僅止於「預期值錯是主要風險」這一點。

---

## 4. Springer EMSE 10.1007/s10664-022-10207-5 — 測試壞味道偵測工具誤判率的人工標註研究

**版本與全文**
- 標題 *Test smells 20 years later: detectability, validity, and reliability*；作者 Annibale Panichella、Sebastiano Panichella、Gordon Fraser、Anand Ashok Sawant、Vincent J. Hellendoorn。
- EMSE 27(7)，2022-09-20，CC-BY 開放取用；是 ICSME 2020 會議版的擴充。
- Springer 網頁擋自動抓取，**改從 ZHAW 機構典藏下載出版版 PDF 讀全文**：https://digitalcollection.zhaw.ch/handle/11475/25672 。

**實驗設計**
- 語言：Java、JUnit 3／4；沒有 Kotlin、Android。
- 樣本：SF110 的 100 個類別（McCabe 複雜度 ≥ 3）。
  - EvoSuite 1.0.7、JTExpert 各產一套，共 200 套。
  - 另加 49 套人寫測試。
- 被評的工具：Grano 等用的舊規則工具（Bavota 2015），以及 tsDetect（用 Spadini 2020 依開發者感受校準過的門檻）。**JNose 不在這篇。**
- 只標六種壞味道：Eager Test、Assertion Roulette、Indirect Testing、Sensitive Equality、Mystery Guest、Resource Optimism。**Magic Number、Lazy Test、Empty Test 沒評。**
- 標註：兩名作者各自二元標註，分歧 10–20%，爭議案由全體作者裁決。
- 粒度：以整套測試為單位，作者承認會高估。

**主要數字**
- 摘要："the older tool's detection strategies misclassified over 70% of test smells, both missing real instances (false negatives) and marking many smell-free tests as smelly (false positives)."
- 人工核對後的盛行率（表 3）：EvoSuite 測試的 Assertion Roulette 實際 17%，Grano 報 74%；Eager Test 實際 21%，Grano 報 57%。
- 誤報率（表 4，EvoSuite 測試）：
  - 舊工具：AR 0.72、Eager 0.53。
  - tsDetect：AR 0.05（精確度 0.67、召回 0.5）、Eager 0.05（精確度 0.73、召回 0.55）。
- 人寫測試（表 7，tsDetect）：AR 精確度 1.00、召回 0.80；Eager 精確度 0.94、召回 0.39；Resource Optimism 精確度 0.33。
- 人寫測試的盛行率（表 6）：Eager 80%、AR 82%。

**研究判定「其實不是問題」的**
- Assertion Roulette 已過時（§5.2）："advances in the JUnit framework have removed the traceability confound entirely… suggest that this smell has become obsolete"。
  - §7.2 推到所有框架："all unit testing frameworks… explicitly indicate which assertion fail and the reason for it, making assertion roulette outdated"。
- Eager Test 是偏好（§1、§4.5）："encode a matter of preference (e.g., 'Eager Test')"。
  - 39 套被判 Eager 的人寫測試裡只有 4 套真的語意不連貫："We thus found no evidence that the Eager Test smell is a useful discriminator."
- Indirect Testing 定義太嚴；Mystery Guest、Resource Optimism 靠字串比對，在產生器輸出上全是誤判。
- 總評（§5.1）："If the objective of test smells is indeed to identify maintainability issues, then they have failed in both definition and implementation."

**清單外真正有問題的（§5.3）**
- 沒有斷言：斷言被註解掉，或只呼叫建構子。原文："tests nearly nothing of semantic importance"。
- 斷言過多：有測試接近 80 個斷言。
- 設定失敗：一大堆 mock 設定後丟 NPE，再用 try／fail／catch 把這個例外當成預期結果。

**作者建議與限制**
- 建議：以語意目標重寫壞味道定義；建共用、徹底驗證過的基準；偵測工具要靠人與業界情境驗證。
- 限制：樣本小、只有 Java、SF110 是老專案；沒找原開發者確認。

**已經回答、我們不必重做**：Java／JUnit 上 Assertion Roulette 與 Eager Test 的規則式偵測誤判很高，而且就算判對也幾乎不代表可維護性問題；真正該抓的是「沒有斷言」和「設定失敗卻被當成預期例外」。

---

## 5. arXiv 2609.05978 — VibeCheck: Assessing the Quality of LLM-Generated Unit Tests（Tabassum 等）

**版本與全文**
- v2（2026-09-14），POVC '26 工作坊（與 ASE 2026 同場），工作坊論文篇幅短。全文已讀。
- 完整標題還有後半："A Multi-agent Empirical Study across Heterogeneous Repositories"。

**實驗設計**
- 語言：Python、JavaScript／TypeScript；沒有 Kotlin、Android。
- 資料：15 個學生專案，原始碼不公開。
- 生成者：Kiro、Antigravity、Cursor 三個 IDE 代理，底層都是 Claude Sonnet 4.5；另以單獨的 Claude Sonnet 4.5 當基準。
- 生成方式：零樣本、只能看專案檔案；代理逐檔「產生→跑→看結果」。
- 提示裡有一句 "Avoid unnecessary mocking"。
- 評分：
  - 五項 0–5 分：能不能跑、斷言強度、邏輯與邊界涵蓋、隔離與確定性、可維護性。
  - **評分者也是這幾個代理**，互評、不評自己。**沒有任何人工校準。**
- 另由作者手寫各專案的「應測行為清單」。

**主要結論與數字**
- 失敗類型佔測試檔比例（表 3）：

  | 生成者 | 卡住跑不動 | 可能不穩 | 斷言太弱 | 漏測行為 |
  |---|---|---|---|---|
  | Kiro | 36.0% | 37.8% | 62.4% | 82.9% |
  | Antigravity | 75.5% | 61.9% | 92.3% | 99.4% |
  | Cursor | 45.1% | 48.0% | 93.1% | 98.8% |
  | 基準 | 52.3% | 58.9% | 81.8% | 99.2% |

- 原文（摘要）："Weak assertions and missing edge cases occur more often than blocking failures, showing that runnable tests can still be shallow."
- 可維護性分數最低（表 4）：R5 只有 0.83–1.71（滿分 5），能不能跑（R1）是 3.38–4.41。
- 典型失敗例（§5.3）：`try { await approveItem('missing-id') } catch (e) { expect(e.code).toBe(404) }`。
  - 原文："this test can pass when approveItem does not throw, because no assertion is executed."
- 評分者的信心不能當品質指標（§5.4）：Pearson r = 0.21，95% CI [−0.05, 0.44]，p = 0.11，n = 60。
  - 原文："it is not reliable enough to replace structured rubric-based assessment"。

**審讀意見**
- 評分者和生成者是同一個模型，作者自己也承認一致性 "cannot be interpreted as independent validation of correctness"。
- 表 1 基準是 83 個檔，表 4 卻是 86 個檔，數字對不上。
- 提示叫代理少用 mock，評分提示卻要求 "DB/network/time/random/external services must be mocked or justified"，兩邊標準不一致。

**作者建議與限制**
- 建議：評估要超越「能跑、涵蓋率」，用結構化評分加失敗模式分析。
- 限制（§6）：
  - 每個 IDE 只配一個模型。
  - "no human-annotated validation of rubric scores"。
  - 只有學生專案、只有零樣本。

**已經回答、我們不必重做**：「代理產的測試能跑，但斷言弱、漏邊界才是大宗」以及「try/catch 讓測試在沒丟例外時照樣綠」這個典型失敗模式，已有現成實例；「評分者信心跟品質幾乎無關」也不必再驗。

---

## 6. arXiv 2609.24341 — Evaluating the effectiveness of class-level LLM-generated test suites in Python（Al-Ahmad 等）

**版本與全文**：v1（2026-09-21，唯一版本，未註明發表處）。全文已讀。

**實驗設計**
- 語言：Python。
- 資料：ClassEval 100 個類別。
- 提示：4 種，作者自己的 77 行版本，加三篇文獻的提示；其中最短的 18 行版本出自第 1 篇的作者群。
- 模型：10 種設定，包括 GPT-5.2（不推理／中度推理）、Gemini 3 Flash（低／高）、DeepSeek Chat／Reasoner、Claude Opus 4.6／Sonnet 4.6（各有開不開延伸思考）。
- 工具：pytest、coverage.py、Cosmic Ray（變異測試）、radon（複雜度）。
- 對照：ClassEval 自帶的人寫測試。
- **本篇不量測試壞味道**，原文："We do not quantify test smells; instead, we report assertion density, complexity, and suite size"。

**主要結論與數字**
- 涵蓋率到頂，分不出好壞（§5.3）："median line coverage is 100% in every cell"。
- 跑得起來的比例差很多：每格 7–84 個類別；DeepSeek Chat 只有 17.8%。
- 變異分數（只算跑得起來的那些）：
  - LLM 90.2–96.2%；人寫 88.3%（82 個類別）。
  - 作者說分母不同，"do not establish superiority"。
- 模型比提示重要（§5.4）：模型的效果量 η² = 0.0216，提示是 0.0056，相差 3.9 倍。
- **測試越多不代表越能抓錯**（§5.6）：
  - 變異分數跟測試函式數 r = −0.31、跟斷言數 −0.27、跟測試行數 −0.39。
  - 跟行／分支涵蓋率只有 0.11／0.10。
  - 原文："Larger suites do not necessarily detect more faults."
- AI 測試結構比較複雜（圖 10）：每支測試的平均循環複雜度，LLM 2.22–2.98、人寫 1.09。
  - 原文："a uniform structural signature of LLM-generated tests"。

**作者建議**（四條，§6.3）
- 把「跑不跑得起來」當主要結果回報。
- 先選模型與推理設定，再調提示。
- 變異測試要配執行閘。
- 原文："do not equate suite volume with quality"。

**限制**
- 每種設定只產一次、只有一個基準集、只有一種變異工具。
- 跑得起來的子集大小差異大。
- 研究產物 "upon reasonable request"，沒有公開。

**已經回答、我們不必重做**：「涵蓋率對 AI 測試沒有鑑別力、要看變異或故障偵測」「測試數量與斷言數量不能當品質分」「AI 測試的分支邏輯比人寫的多兩三倍」這三點，在 Python 類別層級已有對照實驗。

---

## 7. arXiv 2511.21382 — Large Language Models for Unit Test Generation: Achievements, Challenges, and Opportunities（Chu 等，綜述）

**版本與全文**
- v3（2026-09-27），讀 HTML 全文。
- 標題實際是 "Achievements, Challenges, and Opportunities"，**不是派工寫的 "the Road Ahead"**。
- 作者來自南京大學與華為，預印本，未註明發表處。

**方法**
- 系統性文獻回顧加對映研究，收錄截止日 2026-07-31；最後一次搜尋 2026-08-18，來源六個。
- 篩選：原始 14,785 筆 → 去重 6,536 → 全文 495 → 最後 178 篇。
- 品質門檻：11 項、滿分 22，至少 18 分。

**對品質問題的整理（§6.1.1）**
- 定義："Magic number test denotes unexplained constants in assertions, while assertion roulette involves multiple unexplained assertions in one test method."
- 綜述引的研究：HPC 測試 "magic number test occurred in 100% of generated tests and the human baseline"。
- 同一設定下，TsDetect 和 JNose 量出的 AR 是 "54.77% ... and 75.83%"。
- 結論句："test granularity, detectors, and human baselines matter when interpreting smell counts."
- 斷言（oracle）問題：
  - "Syntax checks and text matching cannot establish oracle correctness"。
  - ChatTester 研究："Assertion errors accounted for 85.5% of failed executions"。
  - 反方向的提醒："failing assertions are not necessarily invalid ... filtering tests that fail on the current implementation can discard tests exposing its defects"。
  - "Tests generated mainly from implementation code may reproduce a defect rather than expose it."
- 修壞味道（§5.3）：UTRefactor 把數字字面值換成具名變數、補斷言訊息，六個 Java 專案的壞味道 "from 2,375 to 265, an 89% reduction"。
- mock 只被當成生成要素提到，沒有當壞味道分析；flaky 沒有專節。

**評估方法建議（§6.1.3、§9）**
- "Assessing test value additionally requires measures suited to the objective, including oracle correctness, mutation or held-out fault detection, maintainability, and cost, with failed generations included."
- 迴圈修補（§9）："These loops can improve executability, but they do not by themselves establish semantic correctness, fault-detection effectiveness, or industrial reliability."
- 預期值要用規格或開發者回饋審查。

**限制（§7）**
- 文獻集中在 Java 和 Python，"Confidence remains moderate"。
- 26.4% 是預印本。

**已經回答、我們不必重做**：178 篇文獻的共識是「能跑、涵蓋率高不代表斷言對、抓得到錯；壞味道數字會隨偵測工具與人寫基準變動」，不必自己再證。

---

## 8. AI 代理在測試提交裡加 mock 比人多（36% 對 26%）的原始出處

**出處與全文**
- arXiv 2602.00409 v1（2026-01-30），"Are Coding Agents Generating Over-Mocked Tests? An Empirical Study"。
- 作者 Andre Hora、Romain Robbes；MSR 2026 Technical Papers。HTML 全文已讀。
- 作者網站的預印本：https://andrehora.github.io/pub/2026-msr-agents-over-mocked-tests.pdf

**實驗設計**
- 語言：**只有 Python、JavaScript、TypeScript**；沒有 Java、Kotlin、Android。
- 資料：2,168 個有代理設定檔的倉庫，2025 年的 1,254,878 個提交。
- 判定方式：
  - 代理提交：看作者或 Co-authored-by 欄；人工抽 500 筆，精確率 100%。
  - mock：看識別名（mock／stub／spy／fake／dummy／monkeypatch、@patch）；人工抽 100 筆，精確率 94%。**召回率沒量。**

**主要結論與數字**
- 確切定義（§3.2.1）：分母是「測試提交」，不是全部提交。
  - "Overall, we detected 11,035 agent test commits (in 729 repositories), of which 3,934 are mock commits, resulting in a mock commit ratio of 36%. By comparison, non-coding agents presented a mock commit ratio of 26% (i.e., 40,966 out of 158,326)."
  - 摘要寫成 "36% of commits made by coding agents add mocks"，比正文少了 "test" 這個字，以正文為準。
- **同一倉庫內比較，差距小很多**（表 10）：
  - 代理活動少的倉庫：27% 對 24%，"negligible (Cliff's delta = 0.002)"。
  - 代理活動多的倉庫：36% 對 28%，"small effect size (Cliff's delta = 0.252)"。
- mock 種類（§3.3）："Coding agents predominantly use the mock type (95%), whereas non-agents employ a wider variety: mock (91%), fake (57%), and spy (51%)."
- 設定檔：home-assistant 的指引寫 "Mock external APIs"，它本身就是代理 mock 提交最多的倉庫之一（61 筆）；browser-use 寫 "Never mock anything"，仍有 5 筆代理 mock 提交。

**作者是否說 mock 多是壞事**
- 只是推測，沒有量品質：
  - "This may reflect an overuse of isolation techniques, potentially leading to tests that are easier to generate automatically, but less effective at validating real interactions"。
  - 並明說 "opens opportunities for future research to assess whether such mocks impact test quality"。

**作者建議與限制**
- 建議：審查代理寫的 mock 合不合理；在 CLAUDE.md 這類設定檔寫進 mock 的使用準則與反模式。
- 限制：靠字樣比對；沒做品質判定；不能直接推到其他語言或代理。

**已經回答、我們不必重做**：在 Python／JS／TS 真實倉庫裡，代理的測試提交比人更常加 mock，而且幾乎只用 mock、少用 fake 和 spy。還沒回答的是這些 mock 有沒有害，以及 Kotlin 的情形。

---

## 全組綜合：Android Kotlin 專案（JUnit4、Truth、Turbine、MockK／Mockito）該怎麼管

證據強弱的判準：
- **強**：有人工核對過偵測準確度，或語意上直接導致「測試永遠綠」。
- **中**：多篇一致，但只有自動偵測。
- **弱**：單篇、只有大模型互評，或人寫測試一樣普遍。

先講一個前提：八篇裡**沒有一篇量 Kotlin**，也沒有 Kotlin 的壞味道偵測工具被驗證過。資料全來自 Java、Python、JS／TS，所以下面換算到 Kotlin 的部分全屬推論。

### 甲、值得機械掃（找出來當候選，由人裁決，不自動判死）

1. **沒有斷言的測試**（含空測試、斷言被註解掉、只建構物件）。證據：強。
   - 依據：
     - EMSE §5.3 人工判定它是真問題。
     - 第 1 篇 Unknown Test 在 LLM 最高 77%，EvoSuite 只有 0–7%（但這個數字隨工具變動）。
     - 第 2 篇 SF110 的 Unknown Test 最高 21.2%、Empty Test 最高 7.2%。
   - 語意：這種測試永遠綠，不需要再判斷它有沒有害。
   - 推論：Kotlin 版要把這些都算成斷言，否則誤報會很多：
     - Truth 的 `assertThat`／`assertWithMessage`／`Expect`、JUnit `assert*`、`assertThrows`、kotlin.test 的 `assertFailsWith`。
     - Turbine 的 `awaitItem`／`awaitError`／`awaitComplete`／`expectNoEvents`，這些自己就會失敗。
     - MockK 的 `verify`／`coVerify`、Mockito 的 `verify`。
     - 專案自訂 helper 要明示，跟標準現有的 `--check-helper` 同一個思路。
2. **例外路徑讓測試在沒丟例外時照樣綠**。證據：中，但語意強。
   - 典型寫法是 `try { call() } catch (e: X) { assertThat(e.code)… }`，try 裡呼叫之後沒有 `fail()`。
   - 依據：VibeCheck §5.3 的實例；EMSE §5.3 的「設定失敗、用 try／fail／catch 把 NPE 當預期例外」。
   - 另一種要一起掃的：在測試裡 catch `AssertionError`／`Throwable` 或空 catch。
   - 建議統一改用 `assertFailsWith`／`assertThrows`。
   - **不要沿用 tsDetect 的 Exception Handling 定義**（有 throw／catch 就報）：它在人寫測試上 100% 觸發（第 2 篇表 4）。
3. **測試裡用 `Thread.sleep`、`println`**。證據：AI 特有的證據弱，但語意明確、文字比對精確度高。
   - 依據：第 2 篇 Redundant Print 最高 10.6%；Sleepy Test 是兩個偵測工具共同支援的項目。
   - 標準已寫明 detekt 抓不到協程以外的 `Thread.sleep`。
4. **`@Ignore` 沒寫理由**。證據：弱，第 2 篇只看到 0.3%，但規則現成、成本近零。
   - 做法：開 Android Lint 的 `IgnoreWithoutReason`，不自建。
5. **自比斷言**（`assertEquals(x, x)`）：標準已有 Semgrep 規則，Truth 寫法尚未涵蓋。

### 乙、只當審查提示

1. **斷言太弱**：唯一的斷言是非空、`isTrue()`、筆數大於零這類。證據：中。
   - VibeCheck 判 62–93% 的測試檔有這問題，但那是大模型互評、沒人工校準。
   - EMSE 認為 assertNull／assertNotNull 自己就說明了失敗原因，所以拿它當 AR 不合理，但「只有它」仍然是弱斷言。
   - 機械只能列候選，判斷要靠人。
2. **漏邊界與錯誤路徑**：VibeCheck 裡最常見的失敗（82.9–99.4% 的測試檔）。標準已經要求，這要靠審查，機器量不出來。
3. **預期值的來源**（這才是「魔術數字」背後真正的問題）。
   - 第 3 篇 AssertionError 佔錯誤 64.9%；綜述引的 ChatTester 研究是 85.5%。兩者都表示 AI 最常錯在預期值。
   - 綜述："Tests generated mainly from implementation code may reproduce a defect rather than expose it."
4. **mock 太多、或測試只驗互動次數**。證據：弱到中。
   - 36% 對 26% 是事實，但同倉庫內效果只有可忽略到小，也沒證明有害。
   - 推論：在 Kotlin 可以把「只有 `verify` 沒有狀態斷言」列成候選。
5. **測試裡有 if／for／when**。
   - 第 1 篇：JNose 召回 1.00、精確度 0.75，TsDetect 召回只有 0.44。
   - 第 6 篇（Python）：AI 測試的循環複雜度是人寫的兩到三倍。
6. **共用的大型 fixture（General Fixture）、一支測試塞好幾個情境**：第 1 篇說可能是維護風險，但沒做人工驗證。

### 丙、不該管（不掃、不扣分）

1. **魔術數字**。
   - 人寫測試 100%（第 2 篇表 4），作者說 "contextually benign"。
   - TsDetect 在 LLM 測試上精確度 0.55，方法層級召回 0（第 1 篇表 11、12）。
   - detekt 的 `MagicNumber` 預設就排除測試路徑，照預設即可。
2. **Assertion Roulette**（斷言沒附訊息）。
   - EMSE 說已過時；人寫測試 98.83%；兩篇的偵測精確度落在 0.22–0.67。
   - 推論：JUnit4／Truth 失敗時會印出實際值、預期值與行號，「不知道哪個斷言壞了」的問題已由框架解決。
3. **Eager Test**：EMSE 說是偏好，沒有區辨力。
4. **Lazy Test**（好幾支測試呼叫同一個方法）。
   - 偵測準（精確度 ≥ 0.91），但定義本身跟「每個單元都要測邊界」相衝。人寫測試 100%（第 2 篇）。
5. **Dependent Test、Mystery Guest、Resource Optimism、Sensitive Equality**。
   - Dependent Test 在方法層級 100% 誤報。
   - Mystery Guest、Resource Optimism 靠字串比對，認不得 mock。
   - Sensitive Equality 有時本來就在測 `toString`。
6. **測試數量、斷言數量、涵蓋率當分數**：跟抓錯能力無關或負相關（第 6 篇 r = −0.27 到 −0.39；涵蓋率 r = 0.11），只拿來找漏。

### 現成工具查核（2026-11-02，查法見下）

| 需求 | detekt | Konsist | Android Lint | Sonar Kotlin |
|---|---|---|---|---|
| 沒有斷言的測試 | **沒有**。PR #2019 未合併關閉，維護者說 "out of scope what detekt can do"；issue #379 要求自訂規則集。`EmptyFunctionBlock`（預設啟用、不排除測試）只抓得到完全空的 `@Test fun x() {}` | **沒有**。官方明說 "there are no pre-defined rules"，只能自寫，常要退到比對文字 | 沒有 | **沒有**。S2699 只有 Java、C# 等語言版，Kotlin 版頁面 404 |
| 吞例外 | **部分**。`EmptyCatchBlock`、`SwallowedException` 預設啟用、不排除測試，但預設 `allowedExceptionNameRegex: '_\|(ignore\|expected).*'` 放過 `catch (expected: X) {}`。推論：照官方範例，`SwallowedException` 只報「捕到後沒用或沒正確轉拋」，catch 裡有用到 `e` 去斷言就不報，所以抓不到 VibeCheck 那種沒寫 `fail()` 的寫法 | 只能自寫 | 沒有 | 沒有 |
| `@Ignore`／`@Disabled` | 沒有專用規則；可以把 `org.junit.Ignore` 設進 `ForbiddenAnnotation`（預設停用、需型別解析） | 只能自寫，例如 `functions().assertFalse { it.hasAnnotationOf(Ignore::class) }` | **有** `IgnoreWithoutReason`：只認 JUnit4 `org.junit.Ignore`，只要求寫理由，會跑在測試原始碼 | 沒有 |
| 其他 | `MagicNumber` 預設排除 `**/test/**`、`**/androidTest/**` 等；`SleepInsteadOfDelay` 只管協程內；`ForbiddenMethodCall`（預設停用）的預設清單含 `println` | — | — | — |

查法共五種：
1. detekt 官方規則頁 9 個規則集，加上 v1.23.8 與 main 兩版的 default-detekt-config.yml（我另外親自核對 1.23.8 的 `MagicNumber` excludes、`EmptyCatchBlock`／`SwallowedException` 的設定與範例）。
2. detekt 第三方市集。
3. detekt GitHub 的 issue／PR 搜尋。
4. Konsist 官方文件與片段頁。
5. Android Lint 檢查索引、AGP Lint DSL，以及 sonar-kotlin repo 的 144 條規則。

連結：
- detekt：[style](https://detekt.dev/docs/rules/style)、[exceptions](https://detekt.dev/docs/rules/exceptions)、[empty-blocks](https://detekt.dev/docs/rules/empty-blocks)、[coroutines](https://detekt.dev/docs/rules/coroutines)、[1.23.8 預設設定](https://github.com/detekt/detekt/blob/v1.23.8/detekt-core/src/main/resources/default-detekt-config.yml)、[PR #2019](https://github.com/detekt/detekt/pull/2019)、[issue #379](https://github.com/detekt/detekt/issues/379)、[市集](https://detekt.dev/marketplace)
- Konsist：[Why no pre-defined rules](https://docs.konsist.lemonappdev.com/advanced/why-there-are-no-pre-defined-rules)、[JUnit 片段](https://docs.konsist.lemonappdev.com/samples/starter-test-snippets/junit-test-snippets)、[When API is not enough](https://docs.konsist.lemonappdev.com/advanced/when-konsit-api-is-not-enough)
- Android Lint：[IgnoreWithoutReason](https://googlesamples.github.io/android-custom-lint-rules/checks/IgnoreWithoutReason.md.html)
- Sonar：[sonar-kotlin](https://github.com/SonarSource/sonar-kotlin)、[Java 版 S2699](https://rules.sonarsource.com/java/tag/tests/RSPEC-2699)

---

## 對照 test-quality-standard.md

檔案：`skills/lumos-project-notes/commands/test-quality-standard.md`

### 一致（論文替標準提供了證據）

- 標準：「expected 用需求例子、人工確認結果或独立可信參考。固定字面值也要有來源」。
  - 論文顯示問題在預期值的來源，不在「是不是字面值」：第 3 篇 AssertionError 64.9%；綜述說照實作產的測試 "may reproduce a defect"；魔術數字在人寫測試裡 100%。
- 標準：「抓錯能力：原缺陷或相關故障是否使目標行為斷言紅」，以及〈Android〉節的「涵蓋率只拿來找漏」。
  - 第 6 篇：涵蓋率到頂（中位數 100%），跟變異分數 r = 0.11。綜述也要求 "mutation or held-out fault detection"。
- 標準：「靜態命中先核對目的，不因形式相似自動刪除」、「零候選與『掃完』不等於品質通過」、「靜態掃描另外跑人工標註的正反例……記錄候選裁決、漏報／誤報／未分析」。
  - 這正是第 1、4 篇做的事，結果是誤判 70% 以上、AR 精確度 0.34–0.62。第 1 篇自己也說 "candidates for inspection rather than as high-confidence findings"。
- 標準：「替身：假實作優先……mock 與 stub 次之，spy 避免，複雜的 mock 不寫」。
  - 第 8 篇：代理 95% 用 mock，比人更少用 fake。兩者方向一致；不過論文沒證明 mock 有害，所以這條仍屬偏好。
- 標準：「每個單元都要有邊界……只有正常路徑不算」。
  - VibeCheck：漏測行為是每個生成者最常見的失敗（82.9–99.4%）。
- 標準：「錯是被『當掉』抓到的……每條需求至少要有一支用斷言抓」。
  - 對應 EMSE 的「設定失敗卻被當成預期例外」。
- 標準：「不用 `Thread.sleep` 或真實時間等結果」。
  - 對應 Sleepy Test；兩個偵測工具都列這一項。
- 共用規範 03 第 3 條：「呼叫次數……不能單獨當成功能正確的證明」。
  - 對應「只驗互動的 mock 測試」這個提示。

### 補強（標準可以加的）

1. **「沒有斷言」與「try／catch 沒 `fail()`」兩條機械候選**。
   - 標準現在對 Kotlin 只寫「規則只有 `assertEquals(x, x)`，Truth 寫法的自比不在內」。
   - 這兩種是論文裡證據最強、語意最清楚的「永遠綠」，而且四個現成工具都沒有規則。
   - 斷言詞彙表要包含 Truth、Turbine、MockK `verify`，並且可設定。
2. **現成工具的盲點寫進「機器抓不到」**。
   - detekt `EmptyCatchBlock`／`SwallowedException` 放過名叫 `expected`／`ignore` 的例外變數。
   - `SwallowedException` 抓不到「catch 裡斷言、try 裡沒 `fail()`」（推論，依官方範例）。
3. **不要拿測試數量、斷言數量當品質證據**（第 6 篇負相關），也不要用涵蓋率排名生成者。
4. **`@Ignore` 開現成的 `IgnoreWithoutReason`**，不自建。
5. **明列不採用的壞味道**：魔術數字（字面值本身）、Assertion Roulette、Eager Test、Lazy Test、Dependent Test。
   - 這樣下一個 session 不會又把 tsDetect／JNose 的清單整份搬進來。

### 衝突

1. **第 1 篇作者建議 "integrate smell detection tools like TsDetect and JNose directly into the CI/CD pipeline"**。
   - 這跟標準的「靜態命中先核對目的」「零候選不等於通過」方向不同。
   - 第 1 篇自己的表 11–12 和 EMSE 的數據都支持標準的保守立場：照單全收會大量誤報，而且某些規則（DpT、方法層級 MT）完全失準。**以標準為準。**
2. **Lazy Test 的定義跟標準相衝**。
   - 「好幾支測試呼叫同一個方法」在標準裡是必要的（「每個單元都要有邊界：負數、零與邊界值；每一種網路錯誤……」），在壞味道清單裡卻是缺點。
   - 這是壞味道清單本身的問題，**以標準為準**。
3. **第 1 篇把 Exception Handling 少解讀成「不測錯誤路徑」**。
   - 這跟它自己的定義矛盾，也不能拿來支持標準的「每一種網路錯誤」。
   - 標準的要求成立，但證據要用 VibeCheck 的漏測行為，不要用 EH 比例。
4. **斷言訊息**。
   - 綜述介紹的 UTRefactor 主張「補斷言訊息、數字換具名變數」，EMSE 說 AR 已過時；標準沒有要求斷言訊息。
   - 這不算衝突，**建議維持不要求**。

---

## 讀取紀錄與未決

- 八篇都讀到全文。
- 第 4 篇從 ZHAW 典藏取得出版版；第 8 篇是 arXiv 2602.00409（Hora、Robbes，MSR 2026）。
- 編號與標題對不上的有兩處：
  - 2410.10628 v3 已改名為 "On the Diffusion of Test Smells in LLM-Generated Unit Tests"，派工寫的 v2 缺人工核對章節。
  - 2511.21382 的標題是 "Achievements, Challenges, and Opportunities"，不是 "the Road Ahead"。
- 第 3 篇沒寫總共產了幾份測試套件。
- 第 5 篇表 1 和表 4 的基準檔數不一致（83 對 86）。
- 第 7、8 篇的原句我抽查過幾處（mock 36%、Cliff's delta、95% mock type、UTRefactor），跟原文一致。
- 暫存目錄 `papers/smells/` 沒刪，交由編排者處理；沒有改任何 repo 檔案。
