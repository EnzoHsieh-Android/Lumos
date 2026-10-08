# 把 KEY 行與散文拆成 WHY／RULE／PITFALL／FACT 的規律調研

先講比喻：KEY 行像一個什麼都往裡塞的抽屜。這 50 條工具鏈 KEY 行裡，只有約一成是單一種東西，近一半要拆成兩三個前綴。我為這些前綴歸納出的線索詞，在 WHY 上最準，在 RULE 和 FACT 上根本測不了。

產物都在 `/tmp/ctxsplit/`：`sample.jsonl`、`labels.jsonl`、`rules.py`、`heldout_pred.json`（前綴猜測，已先凍結）、`sample.py`（抽樣腳本）。repo 沒有被改動。

## 結論

**找得到規律，但只夠當提醒，不夠機械判定。**

- 我寫了一份關鍵字規則，並且在看到後 50 句的人工標之前就把它對後 50 句的預測存檔。
  - 它在這後 50 句猜對 27 句（54%）。
  - 其中 7 句是合約行，一定猜得對。扣掉它們，只剩 20/43（47%）。
  - 前 100 句是我拿來歸納規則的，準度 56/100，不能當成績。
- **容易的**：
  - 合約行（`★INVARIANT★`、`[test:]`、`[audit:]`、`[kill:]`）靠記號就能認，不用看內容。
  - WHY 有明確的決策用語，後 50 句 5 個 WHY 中它命中 2 個，命中的都對。
- **難的**：
  - 純 CODE、MIXED、PITFALL 都很容易猜錯。
  - 抓 CODE 的規則，是看句子有沒有反引號或檔名。這會誤抓 WHY、PITFALL、MIXED，因為它們也常提到程式實體。
  - RULE 和 FACT 在後 50 句各只有 2 句和 0 句，規則在這裡測不出東西。
- **一個意外**：150 句裡純 RULE 只有 5 句、純 FACT 只有 4 句（合計 6%）。這個語料主要是 CODE、WHY 和過程記錄。
- **分類缺口**：另有約 20 句哪個前綴都放不進去，我歸在 OTHER，種類有：
  - 施工步驟
  - 審查處置紀錄
  - 版本沿革
  - 指標
  - 實驗口徑
  - 待辦
  - 開放問題
  - REVISIT 行
- 還有 20 句是 `★INVARIANT★` 合約行。它的內容像 CODE，但它自成一種格式，不該被拆。

## 規則表（線索 → 前綴）

這張表有兩個限制。第一，它是我的主觀判斷。第二，「前 100」是我從這 100 句歸納出來的，所以偏好看。

計分方式：這些規則是各自獨立計算，不是依序比對。人工標是單一前綴時，標對才算對。人工標是 MIXED 時，只要這條規則預測的前綴是被拆出的部分之一，也算對。

| 線索 | → 前綴 | 前 100 命中／對 | 後 50 命中／對 |
|---|---|---|---|
| `★INVARIANT★`、`[test:]`、`[audit:]`、`[kill:]` | 合約行（OTHER，不拆） | 17／13 | 9／7 |
| 刻意沒做、不重寫、YAGNI、理由、所以、取代、否決、不偷渡、裁定、Enzo 裁、改成、避免、故加 | WHY | 22／15 | 4／3 |
| 使用者指示、席指出、翻案、拍板 | WHY（決策出處） | 3／3 | 1／1 |
| 靜默、更糟、誤擋、教訓、反面教材、整支中斷、死結、事故、根因、blocker、缺口、漂 | PITFALL | 23／12 | 6／3 |
| 基線、p50、arXiv、外界、數字加秒、請求 | FACT | 10／5 | 1／0 |
| 必須、不得、不准、禁令、家規、要嘛、開工前 | RULE | 13／5 | 2／0 |
| 反引號、`()`、`.py`、`scripts/`、底線識別字、`[S\d+]`、欄、回傳、新增、擋下、拒收 | CODE | 55／26 | 28／16 |
| `REVISIT` | OTHER（待辦或回頭條件） | 3／1 | 1／0 |

這些規則補不了的幾個結構線索，不是凍結的規則，只是我在 150 句上事後看到的現象，沒有獨立驗證：

- **目錄分布**：
  - `Issues/` 的 16 句沒有一句是純 CODE，其中 6 句是 PITFALL，5 句是 MIXED。
  - `Systems/` 摘要的 KEY 行幾乎都是合約行。
  - `Projects/` 本文的散文句子最多是 CODE 規格（`[S123]` 這類條款編號、「X 時應 Y」）。
- **MIXED 的形狀**：
  - 句子帶著 `r1`、`r2` 這類審查輪次，或「折入」「代碼審」，或括號日期，常是沿革。
  - 沿革通常和 CODE 或 WHY 夾在同一句，不獨立成一句。
- **條件式 RULE**：「條件式開工、攢滿 N 筆才做」這種開工條件更像 `retire`，不是 RULE 本身。

## 易混淆的形狀

1. **前綴在形式上標示「現況」，內容其實是 CODE**（描述行為或欄位）。例子：
   - 「召回路徑照樣把作廢節點遞出去」
   - 「`scan_line()` 改回傳 `(token, form, pos)`」
2. **「修法=…」「建議修法=…」看起來像 RULE，其實是待辦或 CODE。** 例子是 #47、#56。
3. **規格條款（`[S123]`）和 `★INVARIANT★` 長得像 RULE，其實是程式行為的條文。** 它們可以靠測試綁定把關，不屬於人工限制。
4. **帶行號的 CODE**。我驗過的 #84 說 `autonomous-loop.sh:L43`，實際在 `governance/autonomous-loop.sh:562`，行號已錯。
5. **「★xxx★」重點標題後面接的長串。** 前半是 WHY 或 PITFALL，後半是 CODE 的實作。例子是 #49、#61、#137。
6. **FACT 看起來像觀測，其實是程式答得了的。** #68「無 Windows CI」：`.github/workflows/ci.yml` 裡根本沒有 windows，grep 就查得到。
7. **FACT 的反例**：#79「對帳自癒排程 22:30 → 23:00」，repo 內 grep 22:30 和 23:00 都沒命中。這句才是正牌的 FACT（部署設定，程式答不了）。
8. **審查沿革和處置紀錄**像 WHY，因為有「裁定」「折入」，但記的是過程，不是為什麼這樣設計。例子是 #80、#126。
9. **外部前例引用**（如 pre-commit framework、GateMem arXiv）長得像事實，要歸 FACT（外部），不是 CODE。

## CODE 與 MIXED 的比例

我的樣本一共 150 句，其中合約行 20 句。比例是各分層分開算，不能直接當成母體比例，也不能把各層加起來平均。每個分層的抽樣誤差約 ±13 到 14 個百分點（n=50 時）。

| 分層 | 樣本數 | 純 CODE | MIXED | 含 CODE 成分（純 CODE＋MIXED 中含 CODE） |
|---|---|---|---|---|
| 工具鏈 KEY 行（去掉 1 句合約行） | 49 | 12% | 47% | 49% |
| rtb KEY（20 條，合約行占大半） | 20 | 5 句 CODE | 少 | 看不出，樣本太小 |
| 本文散文句子（工具鏈＋rtb） | 80 | 45% | 8% | 52% |
| 全部 150 句去合約行 | 130 | 32% | 22% | 51% |

**對拆的工作量**：

- 工具鏈約 2048 條 KEY 行，若比例成立，大約 960 條是要拆的 MIXED，約 250 條是純 CODE（該刪）。
- MIXED 裡拆出的部分：20 條拆兩段、9 條拆三段，其中 CODE 成分最多（24 次），其次 WHY（16 次）和 PITFALL（13 次）。
- 本文散文句子有一半左右是 CODE，但多半在 `Projects/*_計劃` 這種設計當下的規格，宗旨要不要管計劃筆記，得另外裁。

## 前例比較

網搜是子代理做的，我沒有逐頁重讀。它說它實際打開讀過的有：Nygard 原文、MADR、Diátaxis 的 explanation 和 reference 兩頁、Stab & Gurevych 論文全文、Toulmin 和 IBIS 維基頁、一份程式註解研究（Rani 等人）。QOC 原論文、Lee 1997、Burge & Brown 1998 沒有打開，QOC 那一列只靠搜尋摘要。

| 前例 | 怎麼分 | 可借的地方 | 不合的地方 | 網址 |
|---|---|---|---|---|
| IBIS（Kunz & Rittel） | Issue／Position／Argument（pro、con） | 被否決的選項是 Position，理由是 con，對應 WHY；`replaces` 對應 `[status:superseded]`；「理由必須掛在某個選項上」可拿來檢查 WHY 行 | 是討論過程的圖，不是定稿；沒有外部限制、事故、現況這幾類；粒度是節點，不是行 | https://en.wikipedia.org/wiki/Issue-based_information_system |
| ADR（Nygard 2011） | Context／Decision／Status／Consequences | Decision 加理由對應 WHY；Status 的 superseded 對應 `[status:superseded]` | 文件級，不是行級；Context 把限制和現況混在一起；沒有事故；不要求「推得出的不寫」 | https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions |
| MADR | 加了 Decision Drivers、Considered Options、Pros/Cons、Confirmation、More Information | Considered Options 加 Bad 對應 WHY 的否決；Confirmation 對應 `[test:]`；「何時重審」對應 `[retire:]` | 同樣是文件級；Consequences 的 Bad 只勉強算 PITFALL | https://adr.github.io/madr/ |
| Diátaxis | Tutorial／How-to／Reference／Explanation | Explanation 含設計決策、歷史原因、備選方案，大致對應 WHY 加 RULE；「一個類別只有一種語氣」的純度原則 | 分的是讀者需求，不是知識種類；沒有 PITFALL；Reference 要求完整描述，與「推得出的不寫」相反 | https://diataxis.fr/explanation/ |
| QOC | Questions／Options／Criteria | Criteria 這個獨立類別，可對應 WHY 裡的判準 | 只管設計空間，不管事後；只讀了搜尋摘要 | （只看到搜尋結果，沒打開原文） |
| 論證探勘 | Stab & Gurevych：major claim／claim／premise；Toulmin：claim／ground／warrant／backing／qualifier／rebuttal | warrant 加 backing 像 RULE 和它的出處；qualifier 加 rebuttal 像 `[retire:]`；腳註說標的是角色，不是真假 | 分析的是論述文，沒有「事故」和「現況」；premise 分不出理由是選擇還是外部強加 | https://aclanthology.org/D14-1006.pdf、https://en.wikipedia.org/wiki/Toulmin_model_of_argument |
| 程式註解 why 研究（加碼） | 約 23 種註解類型，含 Rationale、Warning、Deprecation | 支持「why 類最缺、最難抽取，值得寫入時就貼標」 | 針對程式註解；全表沒讀完 | https://scg.unibe.ch/archive/papers/Rani21b.pdf |

**最值得借的是 MADR**：它把選項、選了哪個、為什麼、代價分成不同欄位，正好是 WHY 內部的結構。其次是 IBIS 的「理由要掛在具體選項上」。**RULE 和 PITFALL 沒有任何前例；「程式碼推得出的不寫」這條宗旨也沒有，是自己的創新。** 它的合理性只能靠自己的實驗，不能引前例背書。

## 建議

1. **寫筆記時的速查表**：最適合。把上面「WHY 用語、PITFALL 用語、合約標記」放進寫筆記的 skill，並加上三個提醒：
   - 一行只裝一種語氣。
   - 修法、待辦、規格條款是 CODE，不是 RULE。
   - 過程沿革和處置紀錄要另放，不要混進 WHY。
2. **提交時的提醒（建議前綴）**：
   - 有些情況可以安全地機械提醒：合約行標記已有、整行只有檔名加函式名卻沒有決策用語、帶行號引用、或 FACT／FLOW／DEP 行不帶來源。
   - 提醒不要擋人，因為 CODE 規則在後 50 句的準度只有 16/28（57%）。
   - 如果要擋，只擋「行號引用」這類本來就機械的形狀。
3. **交給 AI 判定者**：MIXED 的拆分、PITFALL 對 CODE 的判斷、WHY 與沿革的區別，要讀完整句才能判，不適合機械化。這部分也是工作量最大的地方（約 960 條要拆）。AI 判定者必須看得到程式碼，才能驗 CODE。
4. **先補分類**：在做拆分之前，先決定施工步驟、處置紀錄、版本沿革、指標、開放問題這幾種過程記錄要放哪裡。不然會有約 14% 的句子無處可去。
5. **不適合機械化的**：
   - CODE 與 WHY 的邊界（很多 WHY 句裡嵌著程式實體）。
   - RULE 是否真的是程式看不到的限制（要看有沒有人近期確認）。
   - FACT 是否真是程式答不了的（#68 就是程式答得了的）。

## 誠實標示

- **標籤都是我一個人判的**，主觀。信心註記：高 121、中 19、低 10。沒有第二位標註者，沒有算一致性。
- **樣本小**：150 句，其中後 50 句拿來驗。RULE 只有 5 句、FACT 只有 4 句，兩者的準度估計無意義。工具鏈 KEY 行 n=50，誤差約 ±13 到 14 個百分點。
- **樣本單位**：
  - KEY 行是整行。
  - 本文是一句，用 `。` 切，濾掉短句。
  - 本文句子常缺上下文，像 #2、#119，判斷偏低信心。
  - rtb 的 KEY 行幾乎全是合約行（共 24 行，抽了 20 行），所以 rtb 的 CODE、MIXED 比例沒有代表性。
- **抽樣**：固定種子 20261001，分層抽樣（KEY 工具鏈 50、rtb 20；本文工具鏈 50、rtb 30），再洗牌。1 到 100 是歸納用，101 到 150 是驗證用。
- **規則表是我歸納的**，在前 100 句上有偏好。只有後 50 句的預測是在看人工標之前凍結的，所以那 54%（扣掉合約行 47%）才算真實成績。
- **程式驗證**：只 grep 驗了少數幾句（#29、#35、#50、#52、#58、#62、#68、#79、#84），多數 CODE 是我讀句子判的，沒逐句驗。
- **前例**部分的二手來源：IBIS 的關係清單和 QOC 的 Criteria 來自維基頁或搜尋摘要；子代理說網頁抓取工具回的是摘要，不是原文，所以逐字引用經過一層轉述（只有 Stab 論文是用轉出的全文核對過的）。
- **沒驗的**：
  - 規則表換一批抽樣是否穩定，沒測。
  - 拿這些規則去實際改筆記後，下游 AI 的表現有沒有變好，沒測。
  - 「CODE 該不該刪」我只回答了程式推不推得出，沒回答刪了會不會有人需要。
