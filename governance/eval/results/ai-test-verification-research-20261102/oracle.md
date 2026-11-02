# AI 生成測試的「預期答案」問題：六篇論文全文讀後報告

讀取日期：2026-11-02。下載檔與轉出的文字在 `scratchpad/papers/oracle/`（PDF、`.raw.txt`、`.html`），引文都能對照查。
對照的標準檔：`skills/lumos-project-notes/commands/test-quality-standard.md`（下文簡稱「標準」，引用時附行號）。

**一句話總結**：六篇裡有五篇用 Java（JUnit 4 為主），一篇用 Python。**沒有任何一篇用 Kotlin 或 Android。**三篇大樣本研究的結論方向一致：AI 看得到實作時，會把實作現在的行為（包括錯的行為）寫成預期值。光叫它「小心程式可能有錯」沒有用；要把實作從它的視野裡拿掉、改給需求說明，才有效。

---

## 1. arXiv 2610.11835 "On the Risks of using LLM-Generated Tests for Regression Testing"

**版本與讀取**：v1（2026-10-08，目前唯一版本），PDF 20 頁全文都讀了。作者 Charoosaei、Richter、Papadakis（盧森堡大學）。

**實驗設計**
- 資料：SciPy、Qiskit、pandas 三個專案共 145 個已合併的 PR（50 + 50 + 45）。在 PR 改到的函式（以及同一類別的其他方法）上植入 60,780 個變異。只保留「專案現有測試抓不到、但 LLM 能寫出測試抓到」的變異，當作「有錯但仍被合併」的 PR（§3.2，表 2）。
- 語言與框架：**只有 Python／pytest**。沒有 Java、Kotlin，也沒有 Android。
- 模型：Claude Haiku 4.5（claude-haiku-4-5-20251001）。模型看得到舊碼、含錯的新碼和差異，看不到正確版本。它最多依執行結果修 6 輪，直到測試在含錯版本上通過、而且覆蓋到改動的行（§3.3、§4.3）。
- 量測：每支測試分別在含錯版和正確版上跑，分成四類（§3.1）：
  - Fault-Revealing（FR，抓到錯）：錯版紅、正確版綠
  - Fault-Enforcing（FE，把錯寫成預期）：錯版綠、正確版紅
  - Weak（弱）：兩版都綠
  - Invalid（無效）：兩版都紅

  另外追蹤 FE 測試在之後的 PR 裡能活多久（RQ2），以及很多錯堆在同一份程式碼時的情形（RQ3）。

**主要結論（附原文數字）**
- 表 3：FE 佔 16.9%／8.4%／16.9%（SciPy／Qiskit／pandas），FR 只佔 2.6%／2.4%／4.8%。每個專案的 FE 區間下界都高於 FR 區間上界，倍數 3.5–6.5×（§5.1.1）。
- 原文："In 99.8% of comparable fault-enforcing pairs the accepted behavior did not exist before the pull request."（RQ1 Answer）也就是說，被寫成預期值的錯，幾乎都是這次 PR 新加的行為。
- §5.1.3：寫成預期的錯裡，例外最多。原文："Exception expectations dominate with 37–57% of enforcing tests expect an exception (e.g., pytest.raises), against 3–9% of fault-revealing tests"。把例外類斷言濾掉之後，FE 仍是 FR 的 4.0×、4.3×、2.6×。
- 表 4、表 5（RQ2）：FE 一路活到研究期間最後一個 PR 的比例是 85.5%／82.8%／90.9%。原文："In SciPy and Qiskit, no fault-enforcing test ever starts to detect its fault, over up to 49 later pull requests."
- 開發者自己寫的測試後來抓到這些錯的比例只有 36.3%／6.1%／7.6%（§5.2.3）。
- RQ3：錯在同一份程式碼裡累積時，到最後仍有 83%–92% 被 FE 測試鎖住。專案測試確定抓到 14%–30%，最多也只有 34%–57%。
- 弱測試佔 41%–70%。原文："Coverage-guidance is a weak criterion"（§6.3）。
- 原文關鍵句："A passing generated test is not evidence of correctness. Its expected values come from the code, so reviewers should check them against the specification or the PR description and not against the output of the current code."（§6.3 For developers）

**作者建議的做法**
- §6.3 給工具開發者：預期值改從規格、文件或 PR 說明推出來。原文："intervention has to act on where the expectation comes from"。
- 同一節：新測試失敗時，當作程式可能有錯來回報，不要自動修測試或丟掉。原文："tool builders could treat a failing test as a possible fault in the code, as developers do, and report it instead of repairing or discarding it."
- §6.1：成因有兩個——預期答案問題，以及「只收在現有程式上通過的測試」這條收件規則。原文："An accepted test needs to pass on C_fault and hence can only be weak or fault-enforcing"。
- 建議用跨多個 PR 的長期資料來評估生成測試的價值。

**作者承認的限制**
- 錯是人工變異，不是真實的錯。抓錯率（FR）可能偏樂觀，因為保留下來的變異都是 LLM 抓得到的（§7.1）。
- 只有三個 Python 科學計算專案。
- 只用 Haiku 4.5 一個模型。作者推測更強的模型可能讓問題更嚴重："the stronger capabilities of larger models to follow instructions might amplify our results"。
- 分類看的是執行結果，不是斷言的意圖（§7.3）。
- 各專案的點估計不精準（SciPy FE 的區間是 8.4–26.2%），作者只主張方向和範圍（§7.4）。

**這篇已經回答、我們不必重做**：「AI 依現有程式寫回歸測試、修到綠才收」這套流程，在 Python 上會把錯寫成預期值；寫成預期的比例是抓到錯的 3.5–6.5 倍；這些測試合併後幾乎不會自己被發現。

**對標準的意義**
- **支持**標準第 7 行：「固定字面值也要有來源：从程式目前輸出貼出的 88 並不因為是字面值就獨立。」這篇量化了「從程式目前輸出抄預期值」的代價。
- **支持**第 12 行：「它只能證明對所選錯誤敏感，不能證明 expected 正確」。FE 測試在正確版會紅，所以它照樣對變動敏感。故障證明可能把它判成「抓得到」，但它的預期值是錯的。第 151 行「預期值照抄實作算法(故障證明照樣判抓到)」就是同一件事。
- **支持**第 149 行「涵蓋率只拿來找漏」：41–70% 的生成測試覆蓋到改動卻分不出對錯。
- **補強（標準沒寫）**：標準沒規定「新測試在現行程式上紅了該怎麼辦」。第 14 行「測試在修復版本來就紅時，先處理基準」講的是修 bug 的基準，不是這件事。這篇的機制顯示，「修到綠」本身就會把抓錯的測試變成鎖錯的測試。
- **補強（時機）**：FE 測試合併後 83–91% 一直存活，開發者測試在兩個專案裡只抓到 6–8%。要擋只能在合併前擋，這支持標準把需求答案放在「開發時」先固定。
- 補充：標準第 187 行自承「這是合成機制實驗，沒有模型呼叫」。這篇正好補上「真模型、真 PR 歷史」的證據，但只限 Python。

---

## 2. arXiv 2410.21136 "Can we find bugs using LLM-generated oracles?"（Konstantinou、Degiovanni、Papadakis）

**版本與讀取**：讀的是 v2（2026-10-05），PDF 26 頁全文。v1 是 2024-10-28 送出，根據第 1 篇參考文獻 [18]，v1 的標題是 "Do LLMs Generate Test Oracles that Capture the Actual or the Expected Program Behaviour?"。**我沒讀 v1**，以下全依 v2。v2 的標題跟任務給的一致。

**實驗設計**
- 資料：
  - TOGA／TOGLL 的資料（原 25 個 Java 專案，刪掉 1 個剩 24 個；EvoSuite 產生的測試前段加正確斷言）。用 μBERT 做出錯版程式，用 GPT 做出錯的斷言（§3.4）。
  - Gitbug-Java：開發者寫的測試，取 1000 個測試前段給 RQ2。作者說這份資料沒進過 GPT-3.5 的訓練資料。
  - 每個情境、每種提示最多 1000 筆。
- 語言與框架：**Java，JUnit 4／Java 8**（生成提示這樣寫）。**沒有 Kotlin 或 Android。**
- 模型：GPT-3.5-turbo、GPT-4o-mini、DeepSeek V3、Codestral，溫度 0.1。§5.3 另用 GPT-5-mini（推理模型）重做 RQ1。
- 量測：
  - RQ1 分類：程式對／錯 × 斷言對／錯，四種情境各自算準確率。
  - RQ2：把測試名和變數名匿名化後，準確率變多少。
  - RQ3 生成：在**正確程式**上產斷言，看能不能編譯、能不能通過。
  - RQ4：用 PIT 算變異分數，跟 EvoSuite 比。
  - 三種提示：MUT+TP、Docstring+MUT+TP、CUT+Docstring+MUT+TP（MUT 是被測方法，TP 是測試前段，CUT 是整個被測類別）。

**主要結論（附原文數字）**
- Finding 1（§4.1，表 1）原文："LLMs' test oracle classification accuracy considerably drops in the presence of buggy code, suggesting that its predictions are derived towards the actual implementation rather than the desired one."
- 表 1，第三種提示下，斷言本身正確、只是程式從對換成錯，準確率的變化：
  - DeepSeek V3：55.17% → 39.02%
  - GPT-3.5：44.31% → 37.18%
  - GPT-4o-mini：60.33% → 46.58%
  - Codestral：80.55% → 72.02%
- 表 7（推理模型 GPT-5-mini）：92.45% → 65.39%。整體下降 18.65–27.06 個百分點。Finding 8 原文："reasoning models are influenced by the actual implementation rather than the expected behaviour."
- §5.4 只用 gpt-4o-mini 測：先摘要再判，或在提示裡明講程式可能有錯，都沒用。原文："we introduced an explicit instruction warning the model that the code might be buggy… they did not alter the fundamental reasoning pattern of the model. In all configurations, the LLM predominantly grounded its classification decisions based on the actual implementation rather than the expected behavior."
- Finding 2：一般模型偏向否決斷言，所以斷言和程式都錯時準確率最高（DeepSeek 約 96%）；Codestral 反過來偏向接受。
- Finding 3（表 2）：測試名和變數名匿名化後，準確率最多掉 15.30（GPT-3.5）、15.40（GPT-4o-mini）、10.20（DeepSeek）、6.60（Codestral）個百分點。
- Finding 5（表 4）：LLM 生成斷言比判斷別人的斷言準。但作者自己說："these results do not imply that generated oracles are inherently more effective at detecting faults."
- 表 3（只做正確程式）：第三種提示下，產出的單一斷言能通過的比例是 62.36%（GPT-3.5）到 76.98%（GPT-4o-mini）。
- 表 6（RQ4）：LLM 斷言的變異分數 18–21%，EvoSuite 17–20%。**我核對時發現數字對不上**：導論寫 "up to 2.96% higher mutation score"，但表 6 最大的差距是 19.92 − 17.56 = 2.36 個百分點；我照表算不出 2.96。
- 結論句原文："LLMs are prone to generate test oracles that capture the actual program implementation rather than the expected one." 導論原文："we conclude that all LLM oracle suggestions need human inspection."

**作者建議的做法**
- 有意義的測試名和變數名，原文："if LLMs are meant to be used to classify/generate the test oracle, will be determinant to generate tests that follow developer-like naming conventions"（§5.5）。
- 提供能描述預期行為的來源，例如文件、系統需求、提交紀錄、bug 報告（§5.6）。§5.6 引用了另一篇研究 [24]（二手，我沒讀）：開發者寫的文件能讓準確率最多 +20%，LLM 生成的文件約 +10%；冗長但沒內容的 Javadoc 沒有幫助。
- 先生成、再用 LLM 過濾錯的斷言（§5.1）。但 LLM 會把「正確但太弱」的斷言也否決掉，作者建議再加一個 LLM 當裁判。

**作者承認的限制**
- 只有 Java 專案，可能不能推廣到其他專案或語言（§6.1）。
- 提示沿用前人的版本。錯的斷言由 GPT 產生，靠「不能通過」來標成錯（§6.2）。
- 用 Gitbug-Java 降低訓練資料洩漏的疑慮（§6.3）。
- 我另外注意到一個限制：RQ3 的生成只在正確程式上做。所以「生成準確率」量的是「能不能重現正確程式的現有行為」，不能直接解讀成「能抓錯」。

**這篇已經回答、我們不必重做**：在 Java 上，LLM 判斷「這個預期值對不對」時會被看到的實作拉走，推理模型也一樣；在提示裡警告「程式可能有錯」並沒有改變這個傾向（後者只在 gpt-4o-mini 上測過）。

**對標準的意義**
- **補強**第 11 行：「**需求判準**：独立案例能否指出程式和測試共同誤解需求？由審查者核對來源與案例」。標準沒說審查者是人還是 AI。這篇顯示，**看得到實作的 AI 審查者**判斷預期值時偏向實作；GPT-5-mini 在錯版程式上的準確率掉了 18–27 個百分點。如果用 AI 審查預期值，就不該給它實作本體，或者它的「通過」只能算弱證據。
- **支持**第 160 行：「不得把 mutation 分數當來源審查」。表 6 的 LLM 變異分數跟 EvoSuite 差不多，但 EvoSuite 的斷言本來就是照實作行為寫的，所以這個分數不代表預期值有獨立來源。
- **支持**第 133 行的命名格式 `被測對象_動作或輸入_預期結果`：測試名帶著預期行為，LLM 判斷時有用（RQ2）。不過這是分類任務的證據，關聯是間接的。

---

## 3. arXiv 2607.22883 "Evaluating and Mitigating the Misguidance Effect of Buggy Code in LLM-Generated Unit Tests"

**版本與讀取**：v1（2026-07-24，唯一版本），PDF 24 頁全文；已接受於 ISSTA 2026（Proc. ACM Softw. Eng. 3, ISSTA113）。正文全部讀了。表格裡逐模型的數字，大部分以正文引述的平均值為準；表 10、11、12 用 HTML 版核對過。

**實驗設計**
- 資料：Defects4J 3.0 的真實錯誤。17 個專案、233 個錯、318 個被測方法；每個都有錯版和修好版（§2.2）。
- 語言與框架：**Java 11、JUnit 4。沒有 Kotlin 或 Android。**
- 模型：11 個（13 種設定），包括 Gemini 2.5 Pro／Flash、Claude 4 Sonnet（有無推理各一）、Grok-4／3、GPT-4.1、o4-mini、DeepSeek-V3／R1、Qwen3-Coder-Plus／Qwen3-Plus。溫度盡量設 0。
- 量測（表 2）：
  - Misguided（被誤導）＝錯版通過、修好版失敗
  - Effective（有效）＝錯版失敗、修好版通過
  - False Positive＝兩版都失敗

  另外還量了：模型給測試的序列分數（模型內部偏好）、多輪修正的效果、人工標註 636 份 docstring（Cohen κ 0.77–0.84），以及在修好版上的編譯失敗率、誤報率和覆蓋率（RQ3）。

**主要結論（附原文數字）**
- 表 4：給錯版程式時，平均每個模型產生 137.69 支被誤導的測試（3.84%）；給修好版時只有 16.46 支（0.46%）。有效測試在錯版輸入下平均 104.15 支（2.98%），在修好版輸入下 304.08 支（8.51%），差了將近三倍。
- 原文："buggy input code not only leads to more incorrect tests, but also suppresses the generation of useful, bug-finding ones."（§3.1）
- 強的模型更容易被誤導（§3.1）：錯版輸入下的被誤導數，跟修好版輸入下的有效數高度相關（r = 0.90）。原文："the models most capable of generating correct tests are also the ones most susceptible to being misguided by buggy code."
- 表 3：在錯版上通過的測試裡，約 93.77% 在兩版都通過。所以前人用「在錯版上通過」當作被誤導，算法不對。
- 表 5：序列分數顯示，模型看到錯版程式時，確實比較偏好把錯寫成預期的測試。
- 表 6（RQ2），四種輸入比較：
  - 只給 LLM 從錯版寫出的 docstring（作者的做法）：被誤導 113.00、有效 186.77
  - 只給程式碼：被誤導 137.69、有效 104.15
  - 程式碼和 docstring 都不給：被誤導 64.38、有效 95.38；而且只有 56.69% 的測試在任一版本通過（作者的做法是 81.05%）
  - docstring 和程式碼一起給：被誤導 146.08、有效 121.92

  原文："the buggy implementation should be removed from the behavioral input and replaced with the generated specification."；"adding the LLM-generated specification as context is insufficient."
- 表 8：先分析、再寫 docstring 的進階提示，讓推理模型的被誤導數再少 32.00 支、有效數再多 56.15 支。對照組是「程式碼仍看得到、但要求先分析錯再寫測試」（Advanced Test Prompt），作者做法比它少 99.00 支被誤導、多 111.15 支有效（推理模型）。
- 表 10：測試斷言了兩版都不存在的行為（幻覺），比例從 16.36% 升到 18.15%（進階提示）；基本 docstring 是 16.19%，跟直接給程式碼差不多。
- 圖 7（多輪修正 3 輪）：給錯版程式碼時，被誤導測試累計增加 31.77 支；給 docstring 時增加 18.08 支。有效測試的增加分別是 17.62 和 35.69 支。
- 表 11（人工標註）：每個模型 318 份 docstring 裡，保留原錯的有 15.09%（Gemini 2.5 Pro）和 20.75%（Qwen3-Coder-Plus）；寫出正確行為的有 62.26% 和 47.48%。保留原錯的那 48 份 docstring，佔了 43 個被誤導方法裡的 24 個（Gemini）。
- 表 12（RQ3，在修好版上）：誤報率平均 37.45%（給程式碼）對 39.04%（給 docstring）；編譯失敗率 21.30% 對 20.10%；行覆蓋率 71.49% 對 75.10%。**另外值得注意的是：程式碼正確時，生成的測試也有三成多會失敗**（不論用哪種輸入）。

**作者建議的做法**
- 分兩步：第一步讓 LLM 依程式寫出意圖 docstring，提示裡明講「不要照抄程式，它可能有錯」；第二步只給 docstring（加上類別的其他資訊）去產測試，**實作本體完全拿掉**（§2.5、圖 3）。
- 進階版：寫 docstring 前先分析「邏輯錯」和「該有卻漏掉的防護」（null 檢查、邊界、跳脫字元）。一般模型要它先列出錯和修法，再照「修好後」的行為寫 docstring。
- 多輪修正時，用 docstring 當基礎，不要用程式碼。

**作者承認的限制**
- 只用 Defects4J。在私有或領域專屬的系統裡，LLM 可能缺乏領域知識，編出不存在的意圖。
- 狀態多、依賴多的程式，方法層級的 docstring 會漏掉資訊。
- 標註有主觀性。
- 可能有訓練資料洩漏；作者認為改寫成 docstring 能降低記憶效應。
- 進階提示可能帶入幻覺行為（§6）。
- 未來工作提到要跟**人寫的高品質規格**比較；**本篇沒做這個比較**。

**這篇已經回答、我們不必重做**：在 Java 真實錯誤上，「把實作從提示裡拿掉、換成意圖描述」能減少被誤導的測試、增加抓錯的測試。「實作還在旁邊、只是加說明或要求先分析」效果差很多。這個結論在 11 個主流模型上方向一致。

**對標準的意義**
- **補強**第 5 行標題「開發時：先固定需求答案，再寫測試」。標準規定了順序，但沒規定**固定答案時能不能看實作**。這篇的「docstring 加程式碼一起給」和「程式碼可見、先分析」兩組對照都顯示：只要實作在視野裡，效果就打折扣。建議寫明：產生「輸入→預期」表的那一步，不給實作本體。
- **支持**第 7 行：「不同函式名或不同模型生成不等於獨立」。從錯版寫出的 docstring 有 15–21% 保留了原錯，所以這種 docstring 只能算「自述（declared）」，不能算 `reviewed-independent`（第 175 行）。它能減少錯，但不是獨立來源。
- **支持**第 11 行由審查者核對來源：進階提示會多出約 2 個百分點的幻覺行為，修好版上也有約 37–39% 的誤報。紅了不等於抓到錯，要有人對照來源判斷。
- 多輪修正的數據（被誤導數 +31.77 對 +18.08），**補強**同一個缺口：標準沒管「新測試紅了就改到綠」這件事。

---

## 4. arXiv 2607.10277 "From Business Requirements to Test Assertions: Evaluating LLM-Generated Oracles on Real Bugs"

**版本與讀取**：v1（2026-07-11，唯一版本），PDF 11 頁全文。表 3 的欄位對齊用 HTML 版核對過。作者自稱是 "pilot proof of concept"（初步可行性研究）。

**實驗設計**
- 資料：Defects4J **Lang 專案的 10 個錯**（Bug 1、3–11）。作者看錯版和修好版的差異，**人工**改寫成業務需求文字；再人工做一個需求參考答案（REQ）當黃金標準（§4.1–4.3）。
- 語言與框架：**Java。沒有 Kotlin 或 Android。**
- 模型：DeepSeek-V3、Gemma-3n-E4B-it、Llama-3-70B-chat、Mistral-7B-Instruct-v0.2、Qwen3-Coder-480B，都透過 Together AI 呼叫。
- 輸入只有需求文字加方法簽名，**不給原始碼、差異或輸入輸出範例**（§3、§4.4）。
- 量測：
  - 用人工做的測試案例，比較 LLM 答案跟 REQ、跟 SUT（實際程式）各自的一致程度，算準確率、精確率、召回率、F1。
  - 用 ChatGPT 5.1 替需求的技術性和模糊度打分，算這兩項跟準確率的 Pearson 相關。

**主要結論（附原文數字）**
- 表 3：多數模型跟 REQ 的一致程度高於跟 SUT 的。例：DeepSeek-V3 跟 REQ 的準確率 0.8892、跟 SUT 0.8590；Llama-3 是 0.8695 對 0.8455。Gemma-3n 例外（0.7064 對 0.7100）。REQ 本身跟 SUT 的準確率是 0.9580。
- 表 2：Bug 3（數字位數判定）F1 只有 0.20–0.55；Bug 1（型別升級）0.40–0.92；Bug 10（空白處理）0.40–0.85。Bug 8 五個模型都是 1.00。
- §5.3：技術性與準確率的 r 在 −0.50 到 +0.24 之間，模糊度在 −0.36 到 +0.03 之間；95% 信賴區間全部跨過 0。
- 原文："LLM-generated oracles are more useful for requirement conformance checking than for regression testing of existing systems."（§6.2）
- 原文："developers should not rely on LLM-generated oracles as a substitute for manually reviewed assertions in safety-critical or numerically intensive code paths, where model accuracy drops significantly."（§6.4）

**作者建議的做法**
- 把「需求符合度檢查」和「回歸測試」當成兩種用途，分開選做法。
- LLM 可以幫忙起草需求導向的預期值，但數值密集或安全關鍵的路徑要有人審過的斷言。

**作者承認的限制**
- 需求和 REQ 都是作者從差異人工推出來的，有主觀性。
- 技術性和模糊度只有單一 LLM 打分，沒有評分者一致性。
- 測試案例是人工做的。
- 不能編譯的輸出直接排除，會影響總結數字（§6.3）。
- 只有 Lang 一個元件、10 個錯，集中在字串和數值工具。
- REQ 只是單一一種人工詮釋。

我另外注意到兩點：
- 論文沒寫清楚 SUT 指的是錯版還是修好版（§4.6 只寫 "the actual implementation in Defects4J"）。如果是修好版，REQ 跟 SUT 本來就應該接近，「LLM 比較貼近 REQ」能推出多少就有限。
- 樣本小，作者自己也稱結果為 "preliminary"。

**這篇已經回答、我們不必重做**：幾乎沒有能直接沿用的定論，作者自己也說是初步研究。能借用的只有一個方向性觀察：只看需求文字時，LLM 在數值型別、位數、空白這類細節規則上最常錯。

**對標準的意義**
- **支持**第 7 行：「expected 用需求例子、人工確認結果或独立可信參考」。光有需求文字，交給 LLM 轉成預期值仍會錯，所以需求要搭配**具體例子**或人工確認。
- **補強**第 107 行「負數、零與邊界值」。這篇顯示，正好是數值和邊界規則最需要人工確認的預期值，不能只靠 AI 從需求推。證據強度低（10 個錯、單一專案）。

---

## 5. "Do LLMs Generate Useful Test Oracles? An Empirical Study with an Unbiased Dataset"（ASE 2025）

**版本與讀取**：Ernst 個人頁面上的 PDF，13 頁全文，PDF 上沒有版本標示。依第 1 篇參考文獻 [28]，正式出版在 ASE 2025 論文集 278–290 頁。作者 Molinelli、Di Grazia、Martin-Lopez、Ernst、Pezzè。圖 5–8 是圖片，數字以正文引述為準。

**實驗設計**
- 資料：135 個能用 Maven 編譯的 Java 專案；從 4,517 個候選專案篩出來，挑 2024-09-01 之後才加入的測試，避開訓練資料。共 13,866 個斷言（每個斷言前面的測試段當輸入）（§III-A）。
- 語言與框架：**Java，JUnit 的 assert\* 系列。沒有 Kotlin 或 Android。**
- 模型：qwen2.5（1.5b、14b、32b）、qwen2.5-coder（1.5b、14b、32b）、phi4-mini、phi4、phi4-reasoning、llama3.3-70b。
- **我發現的不一致**：正文寫 10 個模型，但總查詢數 610,104 = 13,866 × 4 × 11，而且圖 1 寫 "11 LLMs"。
- 提示四種：測試前段加被呼叫的方法，再分別加或不加測試類別、被測類別。
- 量測：
  - 跟開發者原本寫的斷言比，看完全相同或互相包含。
  - RQ4：只在 4 個專案上，用 qwen2.5-32b，以 PIT 量變異分數。生成的斷言要在現有程式上能通過才保留，因為 PIT 要求測試全綠。

**主要結論（附原文數字）**
- RQ1：模型越大越好。從 1.5b 到 32b，「包含」準確率約從 3% 升到 29%（qwen2.5-coder-32b 平均 29.4%）。程式專用模型沒有比一般模型好。phi4-reasoning 超過 75% 的時候根本沒產出斷言。
- RQ2 原文："A prompt containing the test prefix and called methods provides enough information to generate oracles. Additional information like focal class and test class does not significantly improve the generated oracles."
- RQ4：
  - 生成的斷言約 40% 被丟掉，因為不能編譯或失敗。
  - 作者手動確認：8 個失敗的斷言都是錯的；39 個通過的都是對的。
  - 只保留通過的斷言時，變異分數平均比完全沒斷言高 24.8 個百分點；跟原斷言比，平均少 10%。
  - 摘要原文："LLMs generated oracles with average mutation score of 43% — similar to the 45% score of human-designed test oracles."
- 原文："The test cases that fail and that PIT ignores may still be useful to uncover real bugs (for instance, failures due to correct oracles in a faulty program)."（§IV-F）

**作者建議的做法**
- 優先用大模型，不必特地用程式專用模型。
- 重點放在測試前段和被呼叫方法的品質，不必多塞類別內容（§V）。

**作者承認的限制**
- 結果隨參數和溫度變動；只測開源模型。
- 用字串比對驗證，對正確性是低估：語法不同但語意相同的斷言會被算錯。
- 挖掘工具可能漏掉測試或變異。
- 只有 Java／Maven 專案（§VI）。

我另外注意到兩點：
- 變異分析只有 4 個專案、79 個斷言，樣本很小。
- 整篇**完全沒有處理「程式本身有錯」的情境**。「正確性」的代理指標有兩個：跟開發者斷言一樣，或在現有程式上能通過。這兩個指標都把現有程式當成對的。

**這篇已經回答、我們不必重做**：在沒進過訓練資料的 Java 測試上，大模型產的單一斷言約三成跟開發者寫的一致；能通過的斷言把變異分數拉到接近人寫的水準；多塞類別內容沒有幫助。**它沒回答**「預期值對不對、有沒有把錯鎖住」。

**對標準的意義**
- **支持**第 12 行和第 160 行。這篇是最好的反例說明：變異分數跟人寫的接近（43% 對 45%），量的卻是「在現有程式上會通過的斷言」。這正是標準說的「對所選錯誤敏感」，不能證明 expected 正確。
- **間接支持**本報告後面「固定答案時不給實作」的建議：多給程式碼不會讓斷言更準（RQ2），所以拿掉實作在這個維度上沒有明顯代價。這是跨篇推論，論文本身沒測「拿掉實作」。
- 這篇的「能大幅減少人力」（§V-D）**不能**讀成可以免掉來源審查。

---

## 6. arXiv 2501.17461 "AugmenTest: Enhancing Tests with LLM-Driven Oracles"

**版本與讀取**：v1（2025-01-29，唯一版本），PDF 11 頁全文；正式出版在 ICST 2025（第 5 篇參考文獻 [39]）。**表 II 在 PDF 和 HTML 裡都是圖片，逐個變體的 TP／FP／TN／FN 數字讀不到**，以下只用正文數字。表 I 的內容也沒有轉出文字。

**實驗設計**
- 資料：從 Gruber 等人的資料集（418 個專案）挑出 142 個 Java 類別，條件是每個方法的開發者註解至少 30 字元。
- 做法：
  1. 用 Major 對這些類別產生變異。
  2. 用 EvoSuite 1.2 **從變異（錯版）產生測試**。
  3. 只留「錯版通過、原版失敗」的測試，共 203 支（93 支例外斷言、110 支一般斷言）。

  所以資料集裡的原斷言全都是「把錯寫成預期」。任務是：拿掉原斷言，請 LLM 只依文件和註解補一個斷言，**不給方法本體**（§IV）。
- 語言與框架：**Java，JUnit 4.12，EvoSuite。沒有 Kotlin 或 Android。**
- 模型：GPT-4o（API）、量化版 Llama-3-8B-Instruct、量化版 Nous-Hermes-Llama2-13b。
- 提示四種：SP（類別與方法的基本資訊加註解）、EP（再加類別其他方法的註解）、RAG Gen、RAG SP。RAG SP 和 RAG EP 因為成本高沒有跑完。基準是 TOGA（預設版和放寬門檻版）。
- 量測：補上的斷言在原版通過、錯版失敗，就算正確。每支測試重複 10 次（RAG 只跑 5 次），要求 60%／80%／100% 次數一致才算成功。

**主要結論（附原文數字）**
- §IV-C：門檻 60% 時 EP 45.5%、SP 37.3%；80% 時 EP 36.4%、SP 34.5%；100% 時 EP 30%、SP 29.1%。
- 摘要：TOGA 8.2%（100% 門檻）；RAG 18.2%。
- 原文："none of the variants experimented with were able to infer the correct assertion. Hence, the results presented here are only for those test cases involving non-exception assertions"。也就是 93 支例外斷言**全部失敗**，TOGA 也一樣。
- 從上下文推測，成功率的分母是那 110 支一般斷言；論文沒有明寫分母。
- 作者說 EP 比 SP 多了更多資訊、表現較好，但在最嚴格門檻下差距只有 0.9 個百分點，作者自己也寫 "the difference between the EP and SP variants diminishes as the threshold increases"。
- 常常有產出的斷言不能編譯或不能執行（表 II 的 Failures 欄，數字是圖片讀不到）。

**作者建議的做法**
- 從文件和開發者註解推預期值，不看程式碼。
- 用自然語言的豐富內容（EP），不要用結構化 JSON 的 RAG。
- 未來要補上「語意正確性」的保證機制；目前只靠能編譯、能執行來驗收（§V）。

**作者承認的限制**
- 可能有訓練資料洩漏。
- 用的是人工變異，不是真實錯誤。
- 只有 Java。
- 依賴特定模型。
- 評估指標沒涵蓋細微的真實錯誤和可維護性（§IV-E）。

我另外注意到一點：這篇**沒有**設一組「同一個模型、但看得到程式碼」的對照組，所以 30% 不能歸因於「沒看程式碼」；只能說「只靠註解，能把三成被鎖住的一般斷言改回正確」。

**這篇已經回答、我們不必重做**：只靠 Java 方法的開發者註解，GPT-4o 能把約三成（嚴格門檻）到四成五（寬鬆門檻）原本鎖住錯的一般斷言改對；但例外斷言一個都沒改對。

**對標準的意義**
- **支持**第 7 行，以需求或文件當預期值的來源：沒看程式碼的版本也能做出抓錯的斷言。
- **補強**例外類預期值（跟第 1 篇 §5.1.3 合看）：例外斷言是鎖錯測試的大宗（Python 證據），也是只靠文件最難改對的（Java，0/93）。標準第 107 行要求「每一種網路錯誤；壞資料」都要測，第 133 行要求斷言「錯誤理由」。**這些錯誤路徑的預期值，正是 AI 最容易抄錯、也最難從文件推對的地方**，需要明確的來源，例如 API 合約或產品決定。

---

## 全組綜合：AI 幫 Android 專案寫單元測試時，預期值怎麼來、怎麼審

先講適用範圍。六篇都**沒有** Kotlin、協程、Flow、ViewModel 或 Android 框架的資料，最接近的是 Java／JUnit 4 的純邏輯方法（第 2、3、5、6 篇）。下面的建議套到 Android 本機單元測試（`src/test`）時，最適合純邏輯單元，例如工具類別、用例、Repository 的合併與錯誤處理；ViewModel 的狀態與時序屬於外推。

依證據強弱排序：

1. **預期值不能從實作現在的輸出來；AI 寫的測試「在現有程式上通過」不算正確的證據。**（最強。第 1 篇 Python、145 個 PR；第 2 篇 Java、24 個專案加 GPT-5-mini 重做；第 3 篇 Java、真實錯誤、11 個模型；三篇方向一致。）
   - 標準第 7 行已經這樣規定，**不需要改，只需要附上證據**：AI 把錯寫成預期的比例，是抓到錯的 3.5–6.5 倍（第 1 篇表 3）；給錯版程式時，被誤導的測試多了約 8 倍，有效測試少了約 2/3（第 3 篇表 4）。

2. **AI 產生「輸入→預期」表的那一步，不要給它實作本體**，只給需求或意圖、方法簽名、類別結構，之後再另開一步寫測試程式碼。光在提示裡說「程式可能有錯」，或要它先分析錯，都不夠。（強。第 3 篇表 6 與表 8 的對照組：只給 docstring 優於 docstring 加程式碼，也優於程式碼可見時先分析；第 2 篇 §5.4：警告語無效，只測 gpt-4o-mini。）
   - 這是標準目前**最大的缺口**。第 5 行只規定先固定答案，沒規定固定答案時能不能看實作。
   - 實作上可以：派一個看不到 `src/main` 實作本體的子代理產生答案表；或規定答案表要先提交，再讓 AI 讀實作。
   - 注意：第 3 篇的 docstring 是 LLM 從錯版程式寫出來的，有 15–21% 保留原錯。所以人寫或人確認過的需求例子仍然優先，LLM 寫的意圖只算 `declared`（標準第 175 行）。「人寫規格對上 LLM 規格」**沒有任何一篇直接比過**。

3. **新寫的測試在現行程式上紅了，先對照需求來源判斷是程式錯還是測試錯；不准直接把 expected 改成程式目前的輸出。**（強偏中。第 1 篇 §3.3、§6.1、§6.3 的機制：「只收綠的」這條規則讓測試只剩弱或鎖錯兩種；第 3 篇圖 7：用程式碼當輸入多輪修正時，被誤導數 +31.77，用 docstring 是 +18.08。）
   - 標準目前沒有這條。建議加在〈開發時〉節：判定為程式錯時，這支測試就是 bug 的證據，修程式、不修測試；判定為測試錯時，要寫出依據哪個來源。

4. **審查預期值要在合併前做；合併之後幾乎不會有人再發現。**（中。第 1 篇 RQ2、RQ3：鎖錯測試 83–91% 活到最後，開發者測試只抓到 6–36%。）
   - 這支持標準把需求判準放在「開發時」和審查時，不靠事後掃描。

5. **用 AI 審查預期值時，不要給審查者實作本體；給了的話，它說「通過」只能算弱證據。**（中。第 2 篇表 1、表 7：程式從對換成錯，GPT-5-mini 判斷正確斷言的準確率從 92.45% 掉到 65.39%。）
   - 建議補在標準第 11 行「由審查者核對來源與案例」旁：審查者如果是 AI，只給需求來源和測試，不給實作。

6. **錯誤路徑和例外類預期值（`assertThrows`、`assertFailsWith`、`Result.failure`、錯誤狀態）要特別查來源。**（中，跨語言拼湊。第 1 篇 §5.1.3 Python：鎖錯測試有 37–57% 是例外預期；第 6 篇 Java：只靠文件，例外斷言 0/93 改對。）
   - 標準第 107 行要求的網路錯誤、壞資料、儲存空間滿，會讓 AI 寫出大量例外類測試。每一支都要有「這個輸入就該丟這個錯／進這個狀態」的來源，例如 API 合約或產品決定。

7. **故障證明和變異分數只證「對變動敏感」，不證預期值對。**（中。第 1 篇：鎖錯測試照樣對變動敏感；第 5 篇：變異分數 43% 對 45%，但只量在現有程式上通過的斷言；第 2 篇表 6。）
   - 標準第 12、151、160 行已經寫了，**不必改**，可以附上這些證據。

8. **LLM 從程式推出的意圖、規格或 docstring 不是獨立來源；照它寫的測試紅了也要有人判斷。**（中偏弱。第 3 篇表 11：15–21% 保留原錯；表 10：進階提示讓幻覺斷言從 16.36% 升到 18.15%；表 12：程式正確時誤報率仍有 37–39%。）
   - 這支持標準第 7 行「不同模型生成不等於獨立」。

9. **數值型別、位數、空白、邊界這類細節規則，預期值要有人工確認的具體例子。**（弱。第 4 篇只有 10 個錯、單一專案，作者自稱初步；表 2：Bug 3 的 F1 只有 0.20–0.55。）
   - 對應標準第 107 行的「負數、零與邊界值」。

10. **測試名寫出預期行為**，例如標準第 133 行的 `被測對象_動作或輸入_預期結果`。（弱。第 2 篇 RQ2：匿名化後判斷準確率最多掉 15.4 個百分點；但這是分類任務，不是生成任務。）

11. **不要用「多塞程式碼給 AI」來解決預期值問題。**（弱、參考。第 5 篇 RQ2：多給類別內容沒有提升；第 6 篇：RAG 反而比較差，EP 比 SP 在嚴格門檻下只高 0.9 個百分點。）

另外一點：**換更強的模型不會自動解決。**第 3 篇發現越強的模型越容易被誤導（r = 0.90）；第 2 篇的推理模型 GPT-5-mini 同樣會被實作拉走；第 1 篇作者也推測更強的模型可能讓問題更嚴重。

**這組論文還沒回答、我們真的需要時才要自己量的**：
- Kotlin、協程、Flow、ViewModel 狀態下的被誤導比例。
- 人寫的需求例子對上 LLM 寫的意圖，哪個效果好。
- 在像 Claude Code 這樣能讀檔、能跑測試的代理流程中，「答案表先行、不給實作」的實際效果。最接近的是第 1 篇：Haiku 4.5 搭 6 輪依執行結果修正。

第 1 篇也引用了同一團隊的另一篇（arXiv 2607.05139，「先寫程式再寫測試」的風險研究），稱「從錯的程式產生測試，抓錯率從 25% 降到約 14%」。**這篇我沒讀，只是二手轉述。**
