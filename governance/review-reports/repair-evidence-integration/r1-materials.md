完整材料：/tmp/lumos-future-repair-regression-research/AGENTS.md
# AGENTS.md（Codex 等外部 agent 的入口指路檔）

<!-- LUMOS:GRAPH-DISCIPLINE:START v1.2 — 自動注入/更新,勿手改本區塊;改範本 scripts/templates/graph-discipline.md -->
## 程式碼為主，知識圖譜補脈絡（必讀）

**程式碼是「實作現在長怎樣」的最終依據（不是所有現況：部署設定、feature flag、資料庫值、生產行為都不在裡面）；`docs/lumos-toolchain-knowledge/` 補的是程式碼產生不出的脈絡**：當初為什麼這樣決定、程式看不到的限制、踩過的坑、哪些方案被否決、未來什麼條件才能改。讀者主要是下一個 session 的 AI（偶爾是人），寫的時候以「沒有脈絡的人讀得懂」為準。

### 怎麼用（順序照這個走）

1. **先讀程式碼**：自己讀懂現況、得出改法，照程式實際的行為寫。
2. **動手改之前，系統會把相關筆記推到你眼前**（這支檔的家、出過的事故、合約）；也可以自己查：

| 你心裡想的是… | 敲這個 |
|---|---|
| 「改這支檔會牽連什麼？這一帶出過什麼事？」 | `lumos impact --file <檔>` 或 `--diff <範圍>` |
| 「當初為什麼這樣決定？翻案了嗎？」 | `lumos decisions <節點> [--superseded]` |
| 「動這段之前有什麼不能碰的？」 | `lumos contracts <節點>` |
| 「有沒有程式看不出的規則或事故？」 | `lumos search "詞 詞"`（**中文概念之間加空白**：`lumos search "作廢 收回 點數"`，黏成一串幾乎必定 0 筆） |
| 「這篇全文」 | `lumos context <節點> --brief` → 要全文再 `lumos show` |
| 「這批改動要不要過審才能推？」 | `lumos pitfalls --diff <merge-base>..HEAD` |
| 「我 push 了，CI 怎樣？」 | `lumos ci-wait` / `lumos ci-status`（不要 `gh run list`：結果要進治理帳） |
| 「上一個 session 做到一半斷了」 | `lumos handoff <計劃節點>`（唯讀） |
| 「做完了，要留紀錄 / 改狀態 / 記決策」 | `lumos new verification … --plan … --systems …` / `lumos set` / `lumos decision-add` |

   **同一篇筆記內部也會新舊打架**：摘要裡帶日期的 `KEY:` / `FACT:` 行通常比正文段落新，doctor 驗不出這種內部矛盾。衝突又影響決策時，照下一條的辦法去程式碼裁，再回頭修那篇筆記。

   **查不到不等於沒有**：0 筆先看「逐詞覆蓋」裡標 ★ 的那個詞是不是 0，換同義詞再查，換三次還不到再問人。**要說「沒有／缺／不存在／沒人做過」之前，如果那句話會決定要不要動手做東西——先派一個乾淨 agent 用「原始問題」去對一次，不要把你的結論丟給它**（丟結論它會順著你講）。判斷錯本來就要重查一次，這一步只是提前付；**只有這個場合要派，其他查詢照常**。

3. **筆記跟程式對不上時，先看這件事程式碼答不答得了，再看那句話放在哪裡**：
   - **程式碼答不了的，程式碼就不是依據**：部署設定、feature flag、資料庫實際值、生產觀測、法規與人工核可這類限制，原始碼裡沒有。這時候**不准用「以程式碼為準」把矛盾裁掉**，要去跑一次、查一次，或問人。
   - **有結構、有出處的才能挑戰程式碼**：`decisions:` 欄位裡的決策紀錄、★INVARIANT★ 這類合約行、Issues、Verification，以及**同時寫齊 `[since:]` `[retire:]` `[confirmed:]` 且最近半年確認過、沒被標 `[status:superseded]` 的 `RULE:` 行**（前三者是決策紀錄與合約行沒有的弱點補償：那兩種有獨立審計與綁定測試把關，`RULE:` 沒有，所以改用「有人在近期確認過還成立」頂上）。程式違反它們才算程式的問題——照它修，並在結果裡指出是哪一筆。欄位不齊、過期、或沒人確認過的 `RULE:` 沒有這個效力，只是線索。
   - **其他都是線索**：摘要裡的 `KEY:` / `FACT:` / `FLOW:` / `DEP:` 與正文段落。就算寫得像規則、附了日期，也不能拿來推翻程式；對不上時**以程式碼為準**，照程式行為寫，並立一篇 Issue 記下那句筆記錯在哪。
   - 判不出來：兩邊都不改，在結果裡明講哪裡對不上。
4. **交結果前**，把筆記補到的東西寫進結果：多改了哪裡、確認過哪條規則、發現哪句筆記錯了。

（依據：2026-09-18~21 受控實驗——圖譜裡刻意寫錯的「現況描述」會讓較弱的模型照抄，在句子旁標明「以程式碼為準」可以收回；而程式碼推不出來的規則，有筆記的組才守得住。單源見 `Projects/Lumos定位_程式碼為主脈絡為輔_計劃`。）

### 寫筆記時：先分「程式碼推不推得出來」

摘要行用前綴分類，**判準是程式碼推不推得出來，不是重不重要**；一行一類（混在一起就拆成兩行），過程紀錄（哪天做了什麼、第幾輪折了什麼）不寫進筆記，留在 git 與審查卷證。寫法一律 `<前綴>:<核心一句> [鍵:值] …`，欄位寫在句子前後都行；必有的格子缺了 lint 與提交時的提醒會唸（目前只提醒；提交時擋另外開，開了會改寫這一句）：

| 前綴 | 核心一句 | 必有鍵 | 常用選填 |
|---|---|---|---|
| `WHY:` | 決定（否決過什麼） | `[出處:]` `[因:]` | `[不選:]` `[代價:]` `[test:]` `[applies:]` |
| `RULE:` | 程式看不到的限制 | `[依據:人\|外部\|審計\|法規\|相容]` `[since:日期]` `[retire:機器式]`；`[retire:人裁]` 另必有 `[until:]` | `[confirmed:日期]` `[test:]` `[applies:]` `[until:日期]` |
| `PITFALL:` | 症狀 | `[出處:]` `[根因:]`；`[test:]`、`[repro:]`、`[防回歸:]` 三選一 | `[觸發:]` `[修法:]` `[影響:]` `[同族:]` |
| `FACT:` `FLOW:` `DEP:` | 程式碼答不了的現況 | `[來源:部署\|資料庫\|生產\|外部\|人工]` `[confirmed:日期]` | `[recheck:週期]` `[查:]` `[applies:]` |
| `SEE:` | 不寫句子 | 至少一個 `[[連結]]`（只放連結的 DEP/FLOW 改寫成這個） | — |
| 作廢時 | — | `[status:superseded]` 另必有 `[被取代:]` | — |

例：`PITFALL:分派入口收到空清單會靜默成功 [出處:2026-09-30 事故] [根因:呼叫端沒判空] [test:t_dispatch_empty_list]`

- **RULE 的效力**：同時寫齊 `[since:]` `[retire:]` `[confirmed:]` 且最近半年確認過、沒被標 `[status:superseded]`，才有挑戰程式碼的效力（見上面第 3 條）。`[retire:]` 只收機器式：`when-file:路徑`、`when-symbol:路徑::名稱`、`when-test:路徑::名稱`、`when-status:節點=值`、`when-gone:路徑[::字串]`、`度量 …`、`人裁`。
- **現況描述**：**程式碼查得到的一律不寫**；只標「以程式碼為準」加查詢不再算數。沒帶來源的 FACT/FLOW/DEP、新寫的程式行號引用，提交時會被擋（行號改寫成「哪支檔的哪個函式」、寫測試名，或釘版本 `路徑@<提交編號>:行號`；誤擋用 `LUMOS_SKIP_NOTE_SHAPE=1` 單次跳過、會留帳，但推上主線時 CI 照樣會擋，要改寫或把專案設成 warn）。
- 鍵的意思、撤除條件與作廢的寫法細節在 lumos-project-notes skill。`KEY:` 新寫只用於合約行（`KEY:★INVARIANT★` 等）；舊筆記的 KEY 不用追改。

### 鐵則

1. **同一次工作內寫回**：改了會影響行為 / 決策 / 驗證的 code，當次就把脈絡寫回圖譜（pre-commit 擋「改 code 沒動圖譜」）。設計、spec、計劃一律寫成 `Projects/<主題>_計劃` 筆記。
2. **開頭欄位用指令改**（`lumos set` / `append` / `decision-add`），別手改；多個連結一行一項；不確定是不是合約就不要標。重建筆記（regen）與決策四欄的寫法在 skill。
3. **寫完一篇 `lumos lint <節點>`，收工 `lumos doctor`**；push 前 pre-push 會再擋一次。改完程式先跑跟改動相關的測試子集，全套留給推送前的閘（全套跑在對話裡會超時、也讓人等）；子集怎麼跑看專案自己的說明。
4. **承認風險要附回頭看的條件**：寫「沒機械守衛 / 只提醒不擋 / 單次量測 / 還沒有 X」這種會過期的話，把那一句本身搬成獨立一行回頭條件、原行刪掉那一句；寫不出來就是該處理不該承認。帶日期的寫 `REVISIT:YYYY-MM-DD 一句要做什麼`（doctor 到期會唸），綁事件的寫 `REVISIT:[when-file:路徑][by:YYYY-MM-DD] 一句要做什麼`（事件發生那次推送會被點名、預設擋下；寫法見 lumos-project-notes skill）——純散文的回頭條件沒人會回頭。
5. **每支檔有家**（2026-09-11，提交前擋新違規）：每支程式檔要有一篇管它的 Systems 節點（about_code 列了它），新開用 `lumos new system <名> --code <檔> --responsibility "<負責什麼、不負責什麼>"`；節點只准用反引號寫自己家的檔，別人的檔寫成那支檔的家的 `[[連結]]`；改了程式要寫說明就寫進改到那支檔的家，而且改到的每支檔都得先有家；計劃寫 `lands_in`（現況落在哪幾篇或新開哪一篇）。舊帳看 `lumos doctor` 的 S8–S10。

6. **記憶只回答「去哪裡查」，不回答「是什麼」**（兩層模式：圖譜是真相層，記憶是衍生層）：任何敘述式斷言**要嘛指到圖譜節點、要嘛帶一條宣告式檢查（`verify:`，開場唯讀重驗）；兩者都沒有就不得拿來做決定**。記憶留方法與經驗（怎麼做事、踩過什麼坑）；事實與狀態不准留在記憶裡——程式碼答得了的去查程式碼，答不了的（決策、限制、事故）才寫進圖譜——**記憶會自動塞進視野、圖譜要主動查，所以錯的那份先被讀到**（2026-09-14 實測 76 篇裡三篇在說謊）。經驗要升格成規則得進圖譜過閘，不准在記憶裡默默變成政策。

### 給人看的回報用白話
先一句人話或比喻，再往下講；術語和 file:line 能不用就不用，非用不可就當場一句解釋。

### 設計與排查
設計動筆前先問世界（最小解在哪一層、世界解過沒；預設借用既有設計，真沒輪子才自建，零依賴家規下幾乎不採用新依賴），一行 `PRIOR-ART:` 記進計劃筆記；同時寫一行 `RETIRE-IF:`——**看到什麼就該把這條機制／規則撤掉**（例：連續 N 週零觸發、誤報多過真報、維護成本大於省下的工時）。寫不出撤除條件，就是還沒想清楚該不該建。能寫成規則的走測試先行；探索性的先做最小實驗——講不出一道會對症狀翻紅的指令之前，不准開始建理論（見 `[[Systems/診斷迴圈先行]]`）。

### 提交與推送
一個功能一個提交，說明用白話：
- 格式 `<類型>: <一句白話>`（要標範圍就 `<類型>(<範圍>): …`），類型只用 feat / fix / docs / refactor / test / perf / chore；專案的第一個提交固定寫 `chore: 建立專案骨架`。
- 標題寫這次改了什麼、使用者看得到的差別；不寫內部代號（第幾輪、幾席、F3、決策編號、提交編號）；內文用白話條列，一條一件事，只寫讀 log 的人需要知道的差別。
- 程式、圖譜筆記、審查卷證放同一個提交；做到一半的本機提交，推之前壓成一個（同一個工作目錄有別的會談時只加自己的檔，不用 `git add -A`）。
- 過代碼審的功能多一個帳本提交：留痕綁版本，通過後只准再提交帳本（訊息固定 `chore(lumos): 記錄代碼審通過`）；凍結判定併進功能提交，步驟見 lumos-code-loop。

### 遇到這些情境就調用對應 skill

| 你正在做的事 | 調用 |
|---|---|
| 理解既有系統、排查、對外支援、查 DB、寫筆記、巡檢、綁合約測試（含 ★INVARIANT★ / ★IRREVERSIBLE★ / ★CHECKPOINT★ 與 [test:] [audit:] [kill:] [rollback:] [guard:] 的寫法、`lumos spec-trace`、`lumos signoff`） | **`lumos-project-notes`** |
| 跨專案共用的業務規則（升格核心、`core_refs`、偏離） | **`lumos-core-knowledge`** |
| 設計 spec 寫完:先 `lumos spec-gate <計劃>`(判門+條款句式、綁定、回退節、跑紅綠):風險低過了直接實作不派審;風險高再進實作前的審查迴圈 | **`lumos-design-loop`** |
| 分支要推之前，`pitfalls` 出 `tier: high` 的代碼審 | **`lumos-code-loop`** |

> lumos 在 `scripts/lumos`（python3 零依賴）；`lumos-*` skill 唯一來源是 `lumos-toolchain` repo，每台機器裝一次：`git clone <lumos-toolchain> ~/harness/lumos-toolchain && ~/harness/lumos-toolchain/install.sh`。專案自己的技術棧 skill 慣例列在本檔末尾〈架構參考 Skills〉一節；沒有那一節就是還沒有。
<!-- LUMOS:GRAPH-DISCIPLINE:END -->

本 repo 的規矩與現況**單一來源**如下，本檔只指路、不複製內容（防漂移）：

1. **專案規矩**：讀 `CLAUDE.md`（程式碼為主、圖譜補脈絡、零依賴家規、合約鏈、寫入規範）。
2. **系統現況**：讀 `docs/lumos-toolchain-knowledge/MOC/index.md`（知識圖譜索引），再按需讀 `Systems/`（機制）、`Projects/`（計劃與決策）、`Verification/`（驗證紀錄）。筆記跟程式碼衝突時怎麼裁，照上方紀律區塊「怎麼用」第 3 條，這裡不另寫。
3. **CLI**：`python3 scripts/lumos --help`（每個子命令附一句什麼時候用；讀圖譜用 `context`/`search`/`contracts`/`query`）。
4. **看你被派來做什麼**:被派成唯讀審計員/辯方(`codex exec --sandbox read-only`)時,**不要**改 `docs/*-knowledge/` 下的檔,發現問題用報告回覆;被當協作者開在這個 repo 裡時,照 `CLAUDE.md`(與下方紀律區塊)的規矩走——改了會影響行為/決策/驗證的 code,當次就把脈絡寫回圖譜。


完整材料：/tmp/lumos-future-repair-regression-research/CLAUDE.md
# CLAUDE.md
<!-- LUMOS:GRAPH-DISCIPLINE:START v1.2 — 自動注入/更新,勿手改本區塊;改範本 scripts/templates/graph-discipline.md -->
## 程式碼為主，知識圖譜補脈絡（必讀）

**程式碼是「實作現在長怎樣」的最終依據（不是所有現況：部署設定、feature flag、資料庫值、生產行為都不在裡面）；`docs/lumos-toolchain-knowledge/` 補的是程式碼產生不出的脈絡**：當初為什麼這樣決定、程式看不到的限制、踩過的坑、哪些方案被否決、未來什麼條件才能改。讀者主要是下一個 session 的 AI（偶爾是人），寫的時候以「沒有脈絡的人讀得懂」為準。

### 怎麼用（順序照這個走）

1. **先讀程式碼**：自己讀懂現況、得出改法，照程式實際的行為寫。
2. **動手改之前，系統會把相關筆記推到你眼前**（這支檔的家、出過的事故、合約）；也可以自己查：

| 你心裡想的是… | 敲這個 |
|---|---|
| 「改這支檔會牽連什麼？這一帶出過什麼事？」 | `lumos impact --file <檔>` 或 `--diff <範圍>` |
| 「當初為什麼這樣決定？翻案了嗎？」 | `lumos decisions <節點> [--superseded]` |
| 「動這段之前有什麼不能碰的？」 | `lumos contracts <節點>` |
| 「有沒有程式看不出的規則或事故？」 | `lumos search "詞 詞"`（**中文概念之間加空白**：`lumos search "作廢 收回 點數"`，黏成一串幾乎必定 0 筆） |
| 「這篇全文」 | `lumos context <節點> --brief` → 要全文再 `lumos show` |
| 「這批改動要不要過審才能推？」 | `lumos pitfalls --diff <merge-base>..HEAD` |
| 「我 push 了，CI 怎樣？」 | `lumos ci-wait` / `lumos ci-status`（不要 `gh run list`：結果要進治理帳） |
| 「上一個 session 做到一半斷了」 | `lumos handoff <計劃節點>`（唯讀） |
| 「做完了，要留紀錄 / 改狀態 / 記決策」 | `lumos new verification … --plan … --systems …` / `lumos set` / `lumos decision-add` |

   **同一篇筆記內部也會新舊打架**：摘要裡帶日期的 `KEY:` / `FACT:` 行通常比正文段落新，doctor 驗不出這種內部矛盾。衝突又影響決策時，照下一條的辦法去程式碼裁，再回頭修那篇筆記。

   **查不到不等於沒有**：0 筆先看「逐詞覆蓋」裡標 ★ 的那個詞是不是 0，換同義詞再查，換三次還不到再問人。**要說「沒有／缺／不存在／沒人做過」之前，如果那句話會決定要不要動手做東西——先派一個乾淨 agent 用「原始問題」去對一次，不要把你的結論丟給它**（丟結論它會順著你講）。判斷錯本來就要重查一次，這一步只是提前付；**只有這個場合要派，其他查詢照常**。

3. **筆記跟程式對不上時，先看這件事程式碼答不答得了，再看那句話放在哪裡**：
   - **程式碼答不了的，程式碼就不是依據**：部署設定、feature flag、資料庫實際值、生產觀測、法規與人工核可這類限制，原始碼裡沒有。這時候**不准用「以程式碼為準」把矛盾裁掉**，要去跑一次、查一次，或問人。
   - **有結構、有出處的才能挑戰程式碼**：`decisions:` 欄位裡的決策紀錄、★INVARIANT★ 這類合約行、Issues、Verification，以及**同時寫齊 `[since:]` `[retire:]` `[confirmed:]` 且最近半年確認過、沒被標 `[status:superseded]` 的 `RULE:` 行**（前三者是決策紀錄與合約行沒有的弱點補償：那兩種有獨立審計與綁定測試把關，`RULE:` 沒有，所以改用「有人在近期確認過還成立」頂上）。程式違反它們才算程式的問題——照它修，並在結果裡指出是哪一筆。欄位不齊、過期、或沒人確認過的 `RULE:` 沒有這個效力，只是線索。
   - **其他都是線索**：摘要裡的 `KEY:` / `FACT:` / `FLOW:` / `DEP:` 與正文段落。就算寫得像規則、附了日期，也不能拿來推翻程式；對不上時**以程式碼為準**，照程式行為寫，並立一篇 Issue 記下那句筆記錯在哪。
   - 判不出來：兩邊都不改，在結果裡明講哪裡對不上。
4. **交結果前**，把筆記補到的東西寫進結果：多改了哪裡、確認過哪條規則、發現哪句筆記錯了。

（依據：2026-09-18~21 受控實驗——圖譜裡刻意寫錯的「現況描述」會讓較弱的模型照抄，在句子旁標明「以程式碼為準」可以收回；而程式碼推不出來的規則，有筆記的組才守得住。單源見 `Projects/Lumos定位_程式碼為主脈絡為輔_計劃`。）

### 寫筆記時：先分「程式碼推不推得出來」

摘要行用前綴分類，**判準是程式碼推不推得出來，不是重不重要**；一行一類（混在一起就拆成兩行），過程紀錄（哪天做了什麼、第幾輪折了什麼）不寫進筆記，留在 git 與審查卷證。寫法一律 `<前綴>:<核心一句> [鍵:值] …`，欄位寫在句子前後都行；必有的格子缺了 lint 與提交時的提醒會唸（目前只提醒；提交時擋另外開，開了會改寫這一句）：

| 前綴 | 核心一句 | 必有鍵 | 常用選填 |
|---|---|---|---|
| `WHY:` | 決定（否決過什麼） | `[出處:]` `[因:]` | `[不選:]` `[代價:]` `[test:]` `[applies:]` |
| `RULE:` | 程式看不到的限制 | `[依據:人\|外部\|審計\|法規\|相容]` `[since:日期]` `[retire:機器式]`；`[retire:人裁]` 另必有 `[until:]` | `[confirmed:日期]` `[test:]` `[applies:]` `[until:日期]` |
| `PITFALL:` | 症狀 | `[出處:]` `[根因:]`；`[test:]`、`[repro:]`、`[防回歸:]` 三選一 | `[觸發:]` `[修法:]` `[影響:]` `[同族:]` |
| `FACT:` `FLOW:` `DEP:` | 程式碼答不了的現況 | `[來源:部署\|資料庫\|生產\|外部\|人工]` `[confirmed:日期]` | `[recheck:週期]` `[查:]` `[applies:]` |
| `SEE:` | 不寫句子 | 至少一個 `[[連結]]`（只放連結的 DEP/FLOW 改寫成這個） | — |
| 作廢時 | — | `[status:superseded]` 另必有 `[被取代:]` | — |

例：`PITFALL:分派入口收到空清單會靜默成功 [出處:2026-09-30 事故] [根因:呼叫端沒判空] [test:t_dispatch_empty_list]`

- **RULE 的效力**：同時寫齊 `[since:]` `[retire:]` `[confirmed:]` 且最近半年確認過、沒被標 `[status:superseded]`，才有挑戰程式碼的效力（見上面第 3 條）。`[retire:]` 只收機器式：`when-file:路徑`、`when-symbol:路徑::名稱`、`when-test:路徑::名稱`、`when-status:節點=值`、`when-gone:路徑[::字串]`、`度量 …`、`人裁`。
- **現況描述**：**程式碼查得到的一律不寫**；只標「以程式碼為準」加查詢不再算數。沒帶來源的 FACT/FLOW/DEP、新寫的程式行號引用，提交時會被擋（行號改寫成「哪支檔的哪個函式」、寫測試名，或釘版本 `路徑@<提交編號>:行號`；誤擋用 `LUMOS_SKIP_NOTE_SHAPE=1` 單次跳過、會留帳，但推上主線時 CI 照樣會擋，要改寫或把專案設成 warn）。
- 鍵的意思、撤除條件與作廢的寫法細節在 lumos-project-notes skill。`KEY:` 新寫只用於合約行（`KEY:★INVARIANT★` 等）；舊筆記的 KEY 不用追改。

### 鐵則

1. **同一次工作內寫回**：改了會影響行為 / 決策 / 驗證的 code，當次就把脈絡寫回圖譜（pre-commit 擋「改 code 沒動圖譜」）。設計、spec、計劃一律寫成 `Projects/<主題>_計劃` 筆記。
2. **開頭欄位用指令改**（`lumos set` / `append` / `decision-add`），別手改；多個連結一行一項；不確定是不是合約就不要標。重建筆記（regen）與決策四欄的寫法在 skill。
3. **寫完一篇 `lumos lint <節點>`，收工 `lumos doctor`**；push 前 pre-push 會再擋一次。改完程式先跑跟改動相關的測試子集，全套留給推送前的閘（全套跑在對話裡會超時、也讓人等）；子集怎麼跑看專案自己的說明。
4. **承認風險要附回頭看的條件**：寫「沒機械守衛 / 只提醒不擋 / 單次量測 / 還沒有 X」這種會過期的話，把那一句本身搬成獨立一行回頭條件、原行刪掉那一句；寫不出來就是該處理不該承認。帶日期的寫 `REVISIT:YYYY-MM-DD 一句要做什麼`（doctor 到期會唸），綁事件的寫 `REVISIT:[when-file:路徑][by:YYYY-MM-DD] 一句要做什麼`（事件發生那次推送會被點名、預設擋下；寫法見 lumos-project-notes skill）——純散文的回頭條件沒人會回頭。
5. **每支檔有家**（2026-09-11，提交前擋新違規）：每支程式檔要有一篇管它的 Systems 節點（about_code 列了它），新開用 `lumos new system <名> --code <檔> --responsibility "<負責什麼、不負責什麼>"`；節點只准用反引號寫自己家的檔，別人的檔寫成那支檔的家的 `[[連結]]`；改了程式要寫說明就寫進改到那支檔的家，而且改到的每支檔都得先有家；計劃寫 `lands_in`（現況落在哪幾篇或新開哪一篇）。舊帳看 `lumos doctor` 的 S8–S10。

6. **記憶只回答「去哪裡查」，不回答「是什麼」**（兩層模式：圖譜是真相層，記憶是衍生層）：任何敘述式斷言**要嘛指到圖譜節點、要嘛帶一條宣告式檢查（`verify:`，開場唯讀重驗）；兩者都沒有就不得拿來做決定**。記憶留方法與經驗（怎麼做事、踩過什麼坑）；事實與狀態不准留在記憶裡——程式碼答得了的去查程式碼，答不了的（決策、限制、事故）才寫進圖譜——**記憶會自動塞進視野、圖譜要主動查，所以錯的那份先被讀到**（2026-09-14 實測 76 篇裡三篇在說謊）。經驗要升格成規則得進圖譜過閘，不准在記憶裡默默變成政策。

### 給人看的回報用白話
先一句人話或比喻，再往下講；術語和 file:line 能不用就不用，非用不可就當場一句解釋。

### 設計與排查
設計動筆前先問世界（最小解在哪一層、世界解過沒；預設借用既有設計，真沒輪子才自建，零依賴家規下幾乎不採用新依賴），一行 `PRIOR-ART:` 記進計劃筆記；同時寫一行 `RETIRE-IF:`——**看到什麼就該把這條機制／規則撤掉**（例：連續 N 週零觸發、誤報多過真報、維護成本大於省下的工時）。寫不出撤除條件，就是還沒想清楚該不該建。能寫成規則的走測試先行；探索性的先做最小實驗——講不出一道會對症狀翻紅的指令之前，不准開始建理論（見 `[[Systems/診斷迴圈先行]]`）。

### 提交與推送
一個功能一個提交，說明用白話：
- 格式 `<類型>: <一句白話>`（要標範圍就 `<類型>(<範圍>): …`），類型只用 feat / fix / docs / refactor / test / perf / chore；專案的第一個提交固定寫 `chore: 建立專案骨架`。
- 標題寫這次改了什麼、使用者看得到的差別；不寫內部代號（第幾輪、幾席、F3、決策編號、提交編號）；內文用白話條列，一條一件事，只寫讀 log 的人需要知道的差別。
- 程式、圖譜筆記、審查卷證放同一個提交；做到一半的本機提交，推之前壓成一個（同一個工作目錄有別的會談時只加自己的檔，不用 `git add -A`）。
- 過代碼審的功能多一個帳本提交：留痕綁版本，通過後只准再提交帳本（訊息固定 `chore(lumos): 記錄代碼審通過`）；凍結判定併進功能提交，步驟見 lumos-code-loop。

### 遇到這些情境就調用對應 skill

| 你正在做的事 | 調用 |
|---|---|
| 理解既有系統、排查、對外支援、查 DB、寫筆記、巡檢、綁合約測試（含 ★INVARIANT★ / ★IRREVERSIBLE★ / ★CHECKPOINT★ 與 [test:] [audit:] [kill:] [rollback:] [guard:] 的寫法、`lumos spec-trace`、`lumos signoff`） | **`lumos-project-notes`** |
| 跨專案共用的業務規則（升格核心、`core_refs`、偏離） | **`lumos-core-knowledge`** |
| 設計 spec 寫完:先 `lumos spec-gate <計劃>`(判門+條款句式、綁定、回退節、跑紅綠):風險低過了直接實作不派審;風險高再進實作前的審查迴圈 | **`lumos-design-loop`** |
| 分支要推之前，`pitfalls` 出 `tier: high` 的代碼審 | **`lumos-code-loop`** |

> lumos 在 `scripts/lumos`（python3 零依賴）；`lumos-*` skill 唯一來源是 `lumos-toolchain` repo，每台機器裝一次：`git clone <lumos-toolchain> ~/harness/lumos-toolchain && ~/harness/lumos-toolchain/install.sh`。專案自己的技術棧 skill 慣例列在本檔末尾〈架構參考 Skills〉一節；沒有那一節就是還沒有。
<!-- LUMOS:GRAPH-DISCIPLINE:END -->

## 本 repo 的測試子集怎麼跑(紀律區塊鐵則三說的「看專案自己的說明」就是這裡)

改完程式先跑跟改動相關的子集,全套(約 8 分鐘、3700+ 案例)留給推送前的閘:

```
python3.14 scripts/test_lumos.py -k <關鍵字>
```

測試要用 Python 3.14 跑(系統內建的 `python3` 若是 3.9,測試總檔跑不起來;[[Projects/最低Python版本改3.14_計劃]])。關鍵字比對測試函式名(例:`-k stop_block`、`-k codex`);對照組 Codex 曾因在對話裡跑全套而超時([[Projects/Codex行為精修_計劃]] 基線)。

推送前的閘會自己看這次改了什麼:只改 README / docs / assets 這類文件就只跑文件子集(`--suite docs`),改到程式但判成 light 的再加跑「原始碼提到改到的函式或檔名」的測試(`--suite keys`),其餘才跑全套;CI 對純文件推送也只跑文件子集。細節在 [[Systems/bound-tests-gate]]。


完整材料：/Users/enzo/.agents/skills/python-idioms/SKILL.md
---
name: python-idioms
description: 寫或審 Python（asyncio 長跑服務、機器人、排程、資料處理腳本）代碼前必讀——通用不變量層的慣例規則：並行等待與有界並行、不阻塞事件迴圈、task 參照與取消、外呼逾時與重試、例外與程序生命週期、金額用 Decimal、時間帶時區、資源釋放、邊界驗證與秘密。每條附壞例→好例與機檢對照（ruff／mypy／bandit）。框架選擇（Django vs FastAPI、SQLAlchemy vs 其他 ORM、pandas vs polars、requests vs httpx）不在此裁——查該專案圖譜。
---

# Python 慣例（通用不變量層）

**這份文件治的病**：AI 寫出「正確但笨、或正確但會在半夜炸」的 Python——`async def` 裡塞了 `time.sleep` 和 `requests.get` 讓整個事件迴圈停擺、`asyncio.create_task` 的回傳值沒存（task 可能半路被回收、例外無聲蒸發）、`requests` 沒給 timeout（對方掛了你永遠卡住）、金額用 `float` 算到差一分錢、`datetime.now()` 不帶時區讓跨時區比對全錯、`except Exception: pass` 把真正的錯吞掉。這些不炸在單元測試上，炸在長跑幾天之後、在網路抖一下的那一刻。

**分層原則**：只寫不隨框架選擇改變的原則。Django 還是 FastAPI、哪個 ORM、pandas 還是 polars——查該專案的知識圖譜與 CLAUDE.md（`lumos search <關鍵字>` 起手）。規則以「可注入」「runtime schema」等能力措辭，不點名框架。

**機檢欄說明**：`ruff:代碼`＝Ruff 規則（⚠ Ruff 預設只開 `E`／`F` 兩族，下面引用的 `ASYNC`／`RUF`／`S`／`DTZ`／`B`／`G`／`T20`／`SIM`／`PERF`／`TRY`／`BLE` 要在 `pyproject.toml` 的 `select` 明確開，沒開等於沒裝，接法見文末接線表）；`mypy`＝型別檢查（`--strict`）；`bandit:代碼`＝Bandit；`自訂`＝可寫 ast-grep 規則；`不可機檢`＝只有本文件與審查鏡頭能守——排最前面。

> **誠實邊界（2026-09-11）**：本文件是官方文件整理，規則代號全部用本機 `ruff 0.16.7` 的 `ruff rule <代號>` 逐條核對過；**尚未在任何真 Python 專案上實跑**。第一個接入的是一個自動交易專案（asyncio 長連線＋pandas 回測），它踩到的坑要回填進來。

---

## 一、async 紀律（本文件存在的理由）

> **審查時機管道**：本文標「⚠ 不可機檢」的效能／適用性條目，其載重問已由 lumos 效能檢核機制在三時機自動推送（動手前 impact hook 注入／push 前 pitfalls advisory／終審 code-loop 鏡頭；內容源＝lumos-toolchain 圖譜 Systems/效能檢核目錄 Python 段，雙向同步義務）——可機檢條目歸 Ruff，勿靠人記。

### R1. 互不依賴的等待必須並行 ⚠ 不可機檢，頭號條款
```python
# ✗ 笨（延遲相加）
balance = await client.balance()
positions = await client.positions()

# ✓ 一起飛（3.11+ 優先用 TaskGroup：一個失敗會取消其他，例外不會被吞）
async with asyncio.TaskGroup() as tg:
    b = tg.create_task(client.balance())
    p = tg.create_task(client.positions())
balance, positions = b.result(), p.result()
# 個別失敗不連坐、要每個結果 → asyncio.gather(..., return_exceptions=True)
```
- 判斷順序：先確認無資料依賴，再確認無共享資源（同一個 DB transaction／同一條連線的查詢**不准**平行），才並行。
- 依據：[Python docs — asyncio.TaskGroup](https://docs.python.org/3/library/asyncio-task.html#task-groups)

### R2. `gather` 不是佇列、不是限流器 ⚠ 不可機檢，生產最常炸
```python
# ✗ 一千個代號同時打 API：吃到對方速率限制被封、或打爆自己的連線池
await asyncio.gather(*(fetch(sym) for sym in symbols))

# ✓ 有界並行
sem = asyncio.Semaphore(10)   # 上限依對方的速率限制算，寫成常數並註明依據
async def bounded(sym):
    async with sem:
        return await fetch(sym)
await asyncio.gather(*(bounded(s) for s in symbols))
```
- 集合大小不是你控制的（來自 DB／外部輸入／交易所清單）就一律有界。

### R3. `create_task` 的回傳值要存起來，例外要有人接
```python
# ✗ 事件迴圈只留弱參照：task 可能跑到一半被回收；裡面的例外沒人看見
asyncio.create_task(heartbeat())

# ✓ 存強參照，完成時移除並檢查例外
background = set()
t = asyncio.create_task(heartbeat())
background.add(t)
t.add_done_callback(background.discard)
# 更好：放進 TaskGroup，生命週期跟著作用域走
```
- 機檢：`ruff:RUF006`（asyncio-dangling-task）。
- 依據：[Python docs — asyncio.create_task「Important」段](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task)

### R4. `async def` 裡禁同步阻塞；CPU 重活離開事件迴圈
- `time.sleep`、`requests.*`、`urllib.request.urlopen`、同步 `open()` 讀大檔、`subprocess.run`、大 JSON 解析、大迴圈——任一個在 coroutine 裡＝所有 task 一起停（行情漏收、心跳逾時、WebSocket 被伺服器斷線）。
- 換法：`asyncio.sleep`、非同步 client（能力措辭：支援 async 的 HTTP client）、`asyncio.to_thread(同步函式)`；CPU 重活用 `ProcessPoolExecutor`（標準 CPython 有 GIL，執行緒不會讓 CPU 重活變快）。
- 「`while True:` + `sleep` 輪詢」優先改成等事件、佇列或交易所推播。
- 機檢：`ruff:ASYNC251`（time.sleep）、`ruff:ASYNC210`（阻塞 HTTP）、`ruff:ASYNC230`（阻塞 open）、`ruff:ASYNC220`（同步建子程序）、`ruff:ASYNC110`（忙等迴圈）。

### R5. 每個外呼都有逾時；重試有退避、有上限 ⚠ 部分不可機檢
```python
# ✗ requests 預設不逾時：對方不回，你就永遠卡在這行
r = requests.get(url)

# ✓ 同步：明確 timeout（連線, 讀取）
r = requests.get(url, timeout=(3.05, 10))
# ✓ 非同步：整段加上限（3.11+）
async with asyncio.timeout(10):
    data = await client.get(url)
```
- 重試：指數退避＋上限＋只重試「可安全重做」的操作；不可逆操作（下單、付款、寄信）的重試規則見 R17。
- 連線／session／client 在程序生命週期建一次重用，不要每次請求新建。
- 機檢：`ruff:S113`（requests 無 timeout）、`ruff:ASYNC109`（async 函式自帶 timeout 參數，改用 `asyncio.timeout`）。
- 依據：[Requests docs — Timeouts](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)、[Python docs — asyncio.timeout](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout)

### R6. 不准吞例外；不准吞取消
```python
# ✗ 什麼錯都當沒發生
try:
    place_order(o)
except:            # 連 KeyboardInterrupt、CancelledError 都吞
    pass

# ✓ 只接你知道怎麼處理的，其他往上丟
try:
    place_order(o)
except OrderRejected as e:
    log.warning("order rejected: %s", e.reason)
```
- `asyncio.CancelledError` 是 `BaseException`（3.8 起），`except Exception` 接不到它——這是對的；但裸 `except:` 或 `except BaseException:` 會把取消吞掉，關閉流程就卡住。真的要接取消做清理，清理完**重新 raise**。
- 機檢：`ruff:E722`（裸 except）、`ruff:BLE001`（接太寬）、`ruff:S110`（try-except-pass）。

---

## 二、錯誤與程序生命週期

### R7. 例外要保留原因；邊界才轉換
```python
# ✗ 原始例外斷掉，stack 看不到真兇
except KeyError:
    raise ConfigError("missing key")

# ✓
except KeyError as e:
    raise ConfigError("missing key") from e
```
- 在 `except` 裡記錄錯誤用 `log.exception(...)`（自動帶 stack），不用 `log.error(...)`。
- 機檢：`ruff:B904`（except 內 raise 沒 from）、`ruff:TRY400`（except 內用 error 而非 exception）。

### R8. 長跑程序要有優雅關閉 ⚠ 不可機檢
- 收到 `SIGTERM`／`SIGINT` → 停止接新工作 → 取消背景 task 並等它們收尾 → 關連線／session → 退出。沒這條，每次重啟都可能留下半途的狀態（掛單沒記錄、檔案寫一半）。
- 能力措辭：`loop.add_signal_handler`（Unix）或框架提供的 lifespan 掛鉤；重啟交給外部 supervisor（systemd、launchd、容器平台）。
- library 碼不准 `sys.exit()`，只有入口檔可以。

### R9. 日誌用 logging 不用 print；log 參數用延遲格式化（`log.info("%s", x)`，不用 f-string）
- 機檢：`ruff:T201`（print）、`ruff:G004`（logging 用 f-string）。

---

## 三、資料與數值

### R10. 金額、價格、數量用 `Decimal`，不用 `float`；`Decimal` 從字串建 ⚠ 部分不可機檢
```python
# ✗ 二進位浮點：0.1 + 0.2 != 0.3；累加與比較會漂
total = 0.1 + 0.2
qty = Decimal(0.1)                 # 已經是錯的值：Decimal('0.1000000000000000055511151231257827…')

# ✓
from decimal import Decimal, ROUND_DOWN
qty = Decimal("0.1")
qty = (raw_qty / step).to_integral_value(rounding=ROUND_DOWN) * step   # 對齊外部系統給的精度規則
```
- 外部系統（交易所、金流）回的數字用字串接進 `Decimal`，捨入方向寫明（`ROUND_DOWN`／`ROUND_HALF_UP`）且只在一處做。
- 統計與回測的大量運算用 float／numpy 可以，**要送出去的那個數字**（下單量、價格、金額）在邊界轉成 `Decimal` 並對齊精度。
- 機檢：`ruff:RUF032`（Decimal 用 float 常數建）；「金額用了 float」本身不可機檢。
- 依據：[Python docs — decimal](https://docs.python.org/3/library/decimal.html)

### R11. 時間一律帶時區（存 UTC，顯示才轉）；量時間間隔用單調時鐘
```python
# ✗ naive datetime：跟帶時區的比會直接炸，或默默用錯時區
now = datetime.now()
now = datetime.utcnow()            # 3.12 起棄用，而且回的還是 naive

# ✓
now = datetime.now(timezone.utc)
t0 = time.monotonic()              # 算逾時、間隔用這個；系統時間被校時會跳
```
- 機檢：`ruff:DTZ005`（now 不帶 tz）、`ruff:DTZ003`（utcnow）。

### R12. 不准可變預設參數（含類別層可變屬性）；閉包別抓迴圈變數
- 機檢：`ruff:B006`（可變預設參數）、`ruff:RUF012`（類別層可變預設）、`ruff:B023`（閉包抓迴圈變數）。

---

## 四、資源與記憶體

### R13. 檔案、連線、鎖一律用 `with`／`async with` 管
- 例外路徑也要釋放；session／client／連線池在程序層建一次（見 R5），不要在函式裡建了不關。
- 機檢：`ruff:SIM115`（open 沒用 context manager）。

### R14. 大資料逐塊處理；長活集合有上限 ⚠ 不可機檢
- 大檔逐行或分塊讀（`for line in f`、`read_csv(chunksize=…)`）、大查詢用 cursor 分批，不用 `read()`／`fetchall()` 整包進記憶體。
- 模組層的 dict／list 當快取＝沒有上限的洩漏；要快取就用有上限的（`lru_cache(maxsize=N)`，不是 `maxsize=None`）或有 TTL 的實作。
- pandas 熱路徑不用 `iterrows`／`apply(axis=1)`／迴圈裡 `concat`，改向量化或先收成 list 最後一次建（效能題 `py-hotpath` 會在審查時問）。

---

## 五、邊界、型別與安全

### R15. 外部輸入在邊界驗證後才進領域層；型別檢查開 strict
```python
# ✗ 把外部 JSON 直接當領域物件用
price = msg["p"]                       # KeyError、型別是字串還是數字都不知道

# ✓ runtime schema 驗證（能力措辭；pydantic／attrs＋cattrs／自寫都行）→ 得到窄型別
tick = Tick.model_validate(msg)        # 驗證失敗在邊界就擋下
```
- 型別：新專案 `mypy --strict`；公開函式都要有型別註記，`Any` 要有理由。
- 機檢：`mypy --strict`（`disallow_any_generics`、`disallow_untyped_defs`…）。

### R16. 秘密不進 log、不進錯誤訊息、不進 repo
- API key／secret 從環境變數或秘密管理讀；`.env` 進 `.gitignore`；log 物件序列化前遮罩；錯誤對外只給錯誤碼。
- 機檢：`ruff:S105`（寫死的密碼字串）、`bandit`；`自訂`（log 呼叫帶 `secret`／`api_key` 欄位）。

### R17. 不可逆的外部動作（下單、付款、寄信、刪資料）要冪等或有守衛 ⚠ 不可機檢
- 重試機制（R5）、斷線重連、程序重啟都保證同一動作會再來一次：用冪等 key（例如自己產生的 client order id）、去重表、或送出前「查一下是不是已經做過」，擇一並寫進節點的 `[guard:]`。
- 對應圖譜 ★IRREVERSIBLE★ 合約的 rollback／guard 要求。

### R18. 不反序列化不信任的資料；不用 shell 拼指令
- `pickle.load` 不信任的來源＝任意程式碼執行；子程序用參數列表，不用 `shell=True` 拼字串。
- 機檢：`ruff:S301`（pickle）、`ruff:S602`（shell=True）。

---

## 接線表（裝了不等於開了）

| 規則 | 工具 | 前提 | 動作 |
|---|---|---|---|
| R3–R6、R9–R13、R16、R18 | Ruff | `select` 要明確開下面這些族 | 見下方設定 |
| R15 型別 | mypy | `--strict` | CI 當閘；★沒有 SARIF 輸出★（只有 `--output json`），不登進 `.lumos/lint.json` |
| R16、R18 資安 | Bandit | 裝 `bandit[sarif]` | `bandit -r src -f sarif -o {LINT_SARIF_OUT}` 可登進 `.lumos/lint.json` |
| 依賴漏洞 | pip-audit | — | CI 報表；無 SARIF（只有 json／cyclonedx） |
| 全部 Ruff 告警 | SARIF 進審查 | Ruff 內建 | `.lumos/lint.json`：`{"py": ["ruff check --output-format sarif -o {LINT_SARIF_OUT} src"]}`，接好跑 `lumos lint-check --smoke` |

```toml
# pyproject.toml
[tool.ruff.lint]
select = ["E", "F", "B", "ASYNC", "RUF", "S", "DTZ", "G", "T20", "SIM", "PERF", "TRY", "BLE"]
# 中文註解與說明文字的全形標點不是混淆字元——沒這行，RUF001/002/003 會把每個「：（）」都報成錯
# (2026-09-11 首個接入專案第一次跑 ruff 就踩到)
allowed-confusables = ["：", "，", "（", "）", "；", "！", "？", "～", "｜"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]    # 測試裡用 assert 是正常的

[tool.mypy]
strict = true
```

**依據總表**：[Python docs — Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html)、[Python docs — Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html)、[Python docs — decimal](https://docs.python.org/3/library/decimal.html)、[Requests — Timeouts](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)、[Ruff rules](https://docs.astral.sh/ruff/rules/)、[mypy — strict](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict)、[Bandit](https://bandit.readthedocs.io/)。


完整材料：/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md
---
type: project
status: doing
created: 2026-10-07
updated: 2026-10-07
tags:
  - type/project
  - status/doing
  - risk/guards
lands_in:
  - Systems/每輪修補差異派工
  - Systems/每支檔有家
  - Systems/測試假綠形態
related:
  - "[[Projects/修復與重構分段驗證_計劃]]"
  - "[[Projects/同類提醒與根因歸因分開_計劃]]"
  - "[[Projects/根因修復與行為保留配對_計劃]]"
  - "[[Projects/跑滿回顧沿用修補因果證據_計劃]]"
---
# 修補驗證與來源留存整合_計劃

本案把既有修補／保留、分段修復、根因歸因與跑滿回顧指引一起交付。原先逐項小範圍人工驗證，不足以代表含CLI與測試裁判變更的整批低風險。本次整合按高風險審設計與代碼；不修改既有審查上限或閘，歷史通過只證原先範圍。

落點 Systems/每輪修補差異派工、Systems/每支檔有家、Systems/測試假綠形態。分兩個功能提交：先CLI輸入與測試路由修正及其脈絡，再審查流程來源及研究脈絡；兩個提交各有完整有效的相依筆記，不借錯誤about_code避開寫回檢查。審查帳與最後版本重新綁定。

PRIOR-ART: Git官方write-tree把完整可合併索引寫成不可變樹，沿用現有Git reader而不自建快照引擎；Git bundle官方允許增量封存，須明記前置提交並實驗驗證可還原。來源 https://git-scm.com/docs/git-write-tree 與 https://git-scm.com/docs/git-bundle ，2026-10-07實讀。
RETIRE-IF: home檢查入口已由正式設計統一接受固定樹且不再直接讀活動索引時，移除本入口重複捕獲；来源留存要求仍保留，直到正式版本庫已提供同等可取回與驗證的固定版本證據。

## 範圍

1. 索引模式先用write-tree捕獲固定樹。可捕獲時，改動清單、設定、圖譜與分類讀同一樹；測試route不再從會動的索引借證。結尾若索引讀不到或版本不同，撤回額外測試路由證據。捕獲失敗不借額外證據，保留原正式程式檢查退路，不修改安家集合、每提交規則或fail-open政策。
2. 新增同一fixture控制：穩定非法、索引非法途中換合法再還原、索引合法途中換非法再還原，普通及最佳化各驗。先確認真實index注入及還原，再獨立驗結果與借證，避免前置條件冒用預期結果。既有worktree競態fixture改指實際讀的固定樹，仍斷言注入確實執行。
3. 共用範本的留來源指引要求在squash/rebase前保存仍可取回的兩端完整來源，選既有受保護ref或bundle/archive；增量bundle明記前置commit與取回入口，核對指紋；bundle須實際還原commit/tree及必要blob，普通來源壓縮包只能核對tree/blob，提交血緣需另有可取回的完整commit入口。不把patch、版本字串或bundle verify單獨當完整來源已還原，不要求每輪產巨大完整歷史封存。
4. 1800行包括派工、操作規則與慣例指引，以及必讀差異及附錄。本輪既有超額席保留報告但不作受控行數試驗成功樣本；下次先核算後拆席，不追改舊結果。
5. 新發現但主線已存在的缺陷，以真實原報告、版本函式雜湊與重現寫Issue。既有缺陷仍然是缺陷，不算本批新增，也不記為上輪修補造成。未判定不變成none。

## 驗收條款

- [S1] 當暫存區途中改动又還原時，home檢查應只用捕獲的固定樹採信測試路由；非法來源仍拒收，合法來源仍通過。 [test:t_nodehome_optional_test_index_aba]
- [S2] 當索引持續變動、工作樹變動或每提交改動不同時，home檢查應維持撤回與版本隔離、逐提交核對的原行為。 [test:t_nodehome_optional_test_index_changed] [test:t_nodehome_optional_test_snapshot_race] [test:t_nodehome_optional_test_home_writeback]
- [S3] 當整理提交使舊版本不再在交付分支上時，範本應要求仍可取得完整來源，增量封存須記前置來源並冷還原核對。 [manual:核對完整與增量bundle的實驗收據及模板]
- [S4] 當派工材料含操作規則及附錄時，範本應計入1800行總量；超額席留證並把未驗範圍列未判定。 [manual:核對code-convergence-input-guards的r3-dispatch.json與原報告閱讀帳，入口見固定材料入口]
- [S5] 當判讀新發現時，交付紀錄應區分主線既有缺陷、本批新增缺陷與有因果證據的修補回歸；主線既有缺陷仍有Issue入口。 [manual:核對固定材料入口的主線與審材版本、同一案例及函式比較收據]

## 實務隱患

已排除:金流:本地審查與Git讀取不處理交易。
對外送出:提交main與CI依使用者2026-10-07授权；不開PR或寄消息。
已排除:不可逆:不刪歷史帳，不強制推送，來源先留存。
守衛面:誤借測試證據會誤放路由，按高風險review及紅綠控制；保留現有正式程式fallback。
併發:write-tree擷取完整索引，讀取期間其他程序改index不會改已存樹；結尾版本不同只撤回额外證據，不宣稱鎖住所有外部程序。
資源:每次staged最多捕獲及核對兩個樹，不建長駐快取。可能寫入Git物件，不改工作樹或索引的內容；Git原有清理負責不可達物件。
相容:Windows暫排除。source取得不代表行為測試通過；原始碼封存未包含外部部署或DB。

## 回退

還原本次cmd_home_check固定樹修改，移除新ABA測試及fixture適配，保留先前功能與所有真實紅綠紀錄；來源留存指引可獨立還原，不刪既有封存。撤回修復會恢復ABA缺口，須明記Issue不能假稱已安全。

REVISIT:2026-10-20 由每輪修補差異派工計劃的真實試行入口核對材料總量、來源可用性與新增缺陷歸因，按實際樣本數寫未判定，不以合成fixture宣稱收斂輪數下降。

## 固定材料入口

本案版本與交付觀測：修後審材為95735eff7f3e17c930d43eecde5dd9d7c4fe9eff，主線起點為c4f2b0cf479ccdff5823524c0b6954113819496b；r3-dispatch.json、r3-file-index.txt及原報告在governance/review-reports/code-convergence-input-guards/。所有18席收齊後才開始改交付來源。最終版本需另綁，不沿用957的結果當新碼全套通過。

來源留存實驗位於本次卷證的來源封存收據；整合時複製增量bundle及其前置/還原收據，而非超過100MB的完整歷史bundle。archive只指保存全部被驗版本tracked原始檔的完整壓縮包，須逐檔還原比對blob/mode並重建Git tree核對；不包含Git提交血緣，不把patch或只收幾支檔當完整archive。增量bundle需前置c4f2b0cf完整物件閉包；未取得前置時verify應拒收。

函式比較收據：governance/review-reports/code-convergence-input-guards/r3-validation/main-inherited-retro-case.json、main-inherited-test-functions.json。增量來源封存與實際冷還原收據為同目錄reviewed-957-incremental.bundle及reviewed-957-incremental-cold.json；完整bundle與來源壓縮包只保留試驗收據，不提交巨大原件，不把它們當交付可取回入口。


完整材料：/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修復與重構分段驗證_計劃.md
---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
self_audit: gpt-6.1-sol/2026-10-06
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/每輪修補差異派工
verified_by:
  - "[[Verification/2026-10-06_修復與重構分段驗證]]"
related:
  - "[[Projects/修補驗證與來源留存整合_計劃]]"
---
# 修復與重構分段驗證_計劃

白話：先確認修補本身保住既有行為，再看搬函式或改結構後是否仍保住；出問題時能縮小是哪一段帶進來。

WHY:先驗可獨立的修補，把非必要重構另段驗證 [出處:2026-10-06 使用者繼續授權] [因:同區間混入無關改動會讓退化原因難以定位]
PRIOR-ART: 借用Google保持改動聚焦、重構與修錯分開的實務 https://google.github.io/eng-practices/review/developer/small-cls.html ；沿用已有固定版本與repair/preserve案例，不建立新執行器。
RETIRE-IF: 十個有混合修補的修訂輪中，中間驗證點均未幫助定位原因且成本高於節省時間，撤回獨立段要求，保留可比證據與不可分離的明示理由。
REVISIT:2026-10-20 沿用每輪修補差異派工計劃觀察入口核對定位用途與成本；不足十輪保留未判定，關閉前補30天內下一個日期。

## 範圍

只在既有共用範本加入分段準則，手冊與速查指向它，不改CLI或資料格式。編排者按根因識別哪些是直接修補、必要配套及非必要清理／重構；作者分類只是待核對說明，新席從完整改動獨立核對，不能以分類排除檔案。

可獨立時先保留「僅修補＋必要測試」的完整可執行固定版本，用已有配對證據驗原問題與保留行為；非必要重構另存完整可執行固定版本，再跑受影響的相同保留案例。需要先做必要重構才能修時，先記重構前後保留行為結果，再在修復版本驗原問題。編譯或載入失敗不是有效行為驗證。

每個驗證點記實際完整版本、涵蓋根因組、變更目的與固定案例證據指標；兩段各自可比才說哪段引入退化，不把順序本身當因果證明。測試、設定或依賴跟著變時沿用現有未判定與歸因界線。拆不開就留不可分離的原因及需合看路徑，按完整改動審；不拼混合版本，不為分段製造不能運作的半成品。

本機可暫存中間提交供驗證，但推送前仍按現有一功能一提交規範整理，最後可一起PR；不為此增加PR或審查輪。壓提交或換基底後重新固定派工版本並按現有規則重驗留痕，歷史中間證據只回答原版本，不能挪為新版本通過。

## 條款

- [S1] 當修補混入可獨立的非必要重構時，範本應引導完整可執行的分段驗證點與配對案例證據，並保留完整改動供新席核對 [manual:核對三份技能來源及三版本退化定位例子]
- [S2] 當必要配套無法拆開或中間版不能載入時，範本應要求明示不可分離與未判定，不將半成品測試失敗當回歸 [manual:核對必要重構先行與不可分離兩條分支]
- [S3] 當中間本機提交在整理版本後被改寫時，範本應保留原規則的重新固定與留痕要求，不以舊證據替代新版本 [manual:核對指路與新版本判讀界線]

## 實務隱患

已排除:金流:只編輯本機派工文字，不處理交易
已排除:對外送出:不推送發布，不增加PR
已排除:不可逆:文字可獨立還原，不動正式資料
已排除:守衛面:不改CLI、資料格式、閘判定或輪數

## 回退

只移除本次新增分段說明與兩處指路，保留原有修補差異、配對選例及兩版證據。以本功能提交的三份技能來源差異定位，不還原其他功能內容；驗證紀錄仍留其受控範圍。

## 接手

來源完成後維持doing等待試行；安裝與觀察入口見 [[Projects/每輪修補差異派工_計劃]] 。本次無全域安裝，受控例子只驗證判讀方法，不證實收斂成效。

## 本次整合風險

2026-10-07 本機逐項人工小實驗僅證原先範圍；整批交付包含CLI、測試裁判與跨方案脈絡，改按 [[Projects/修補驗證與來源留存整合_計劃]] 高風險設計及代碼審核對。不是改掉原實驗結果，也不靠改風險標籤宣稱已審過；待實際處置閘收據。


完整材料：/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/同類提醒與根因歸因分開_計劃.md
---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-07
self_audit: gpt-5.6-sol/2026-10-07
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
related:
  - "[[Systems/代碼審修正關卡]]"
  - "[[Projects/修補驗證與來源留存整合_計劃]]"
verified_by:
  - "[[Verification/2026-10-06_同類提醒與根因歸因驗證]]"
  - "[[Verification/2026-10-07_主線回顧與修補鏡頭整合驗證]]"
  - "[[Verification/2026-10-07_同類提醒實輪修復紀錄試用]]"
lands_in:
  - Systems/每輪修補差異派工
---
# 同類提醒與根因歸因分開_計劃

白話：都被叫做「邊界問題」，不代表這次與上次壞在同一個原因；要求回顧修法仍保留，因果另外用案例判。

WHY:保留粗分類的回顧提醒，同時避免為填欄位而編造前次修補失敗 [出處:2026-10-06 使用者繼續授權與category-root-attribution受控helper查證]
PRIOR-ART: 借用MITRE對粗分類與具體根因的區分 https://cwe.mitre.org/documents/cwe_usage/guidance.html ；這是對一般代碼審的推論，不採用CWE分類或安全計分。沿用既有prior與同一案例證據，不另建根因識別器。
RETIRE-IF: 十個觸發同類提醒的實際修訂輪中，本說明均未改變根因或因果判讀且填寫成本高於省下重查時間，撤回額外關係說明，保留原同類提醒與兩版歸因規則。
REVISIT:2026-10-20 沿每輪修補差異派工的試行入口核對十輪同類提醒、關係證據與成本；不足十輪維持未判定，關閉前另接30天內日期。

## 做法與範圍

只修改既有共用範本並讓手冊與速查指向它；固定分類、prior兩欄與字數檢查、CLI、處置與輪數都保持原規則。

粗分類相同是回顧觸發，不是同根因或修補因果。編排者在既有intake逐條記前後finding/group ID與版本、具體症狀、觸發輸入、受影響需求、實際失效機制及證據指標。ID／位置相同不證同根因，改名或換ID也不證不同。沒有可核對機制與案例，就記關係未判定；不同根因的判定也要證據。所有證據沿既有§3.1第6步，避免複製一套格式。

既有repeat提示要求prior時照填。why_failed說已核對的前次涵蓋／未涵蓋與證據界線，不硬寫「上次修錯」；關係未判定可明寫缺什麼證據。new_approach說此輪具體補法、待驗與保留案例，不只寫「再測一次」。誠實且具體的兩欄仍各至少十個字；文字過檢查不證關係成立或修補有效。

前次根因殘留／重現與修補造成退化分開：前次修補沒有解決的問題不自動列regression_set，僅因類別相同不列。綠轉紅但混合區間不能歸因仍維持原未判定；有隔離證據才按現有歸因規則列入。分類差異或關係未判定也不降嚴重度或丟發現。新席仍獨立看固定完整版本、需求與症狀，不讀上輪席結論。

## 條款

- [S1] 當同類提醒觸發時，範本應分清分類、根因關係與修補因果，仍要求原prior兩欄 [manual:核對範本與七項實際helper對照]
- [S2] 當身份或位置相同／不同或證據不足時，範本應要求案例機制證據或未判定，不讓欄位字串通過充作語意查證 [manual:核對相同身份及不同身份兩例與prior相容例]
- [S3] 當前次問題殘留或新發現原因未判定時，範本應維持既有歸因、severity及完整審查規則，不只靠repeat列regression_set [manual:核對第6步與收貨原規則及兩處指路]

## 實務隱患

已排除:金流:只補人工判讀文字
已排除:對外送出:無發布或推送
已排除:不可逆:文字可單獨還原
已排除:守衛面:不更動既有CLI、欄位檢查、處置或輪數

## 回退

只撤本功能新增的同類／根因判讀段與兩處指路，保留既有配對、版本與歸因流程；驗證保留受控範圍，不改歷史卷證。

## 接手

來源完成後保持doing，沿 [[Projects/每輪修補差異派工_計劃]] 的安裝與實輪試行入口觀察，不用合成案例充當實際收斂成效。

## 方案與代價

背景：既有同類回顧提示有必要，但欄名why_failed可能誘導無證據的失敗解釋。可選方案：①保留原文字，依每次編排者自行分辨，成本最低但易誤讀；②新增根因識別與因果自動判定，需更多版本與語意判準且可能製造誤判；③本案只補人工解釋與案例證據指路，保留機械要求。選③因為既有證據格式已可用，不必改門檻。代價是每次需少量人工核對，未知仍可能留存，沿既定入口量測再決定是否保留。這是本案選擇的脈絡，不翻案或補寫Systems既有d1的歷史欄位。

結案入口：累積至少十個實際觸發輪後，在本計劃記錄逐輪證據與成本、依RETIRE-IF作保留／撤除決定並完成相應來源處置，才將本計劃done；這只結束本機制試行，不等同證明輪數下降。Systems承接多項補強，各計劃觀察均收尾才結案，不以本案十輪替其他功能結案。

## 實輪紀錄試用（2026-10-07）

VERIFY:既有code-convergence-input-guards的R2修復紀錄按本案原則補prior：concurrency依R1工作樹案例與R2索引撤回案例說明涵蓋界線；boundary依R1測試家／分組案例與R2解析器OSError案例說明，不從粗分類編造修補因果。另將waiver定位指向既有理由中的_nodehome_evaluate文字，符合原定位規則，沒有更改放行內容。卷證見governance/research/review-repair-regressions/real-r2-record/metadata-receipt.json。這次是既有修復紀錄試用，不計為新審查輪或收斂成效。
REVISIT:2026-10-20 核對本次R2完整fix-check與後續新席回報，將實際通過／失敗與缺證分開記；若測試失敗先修對應原因，不從prior字串通過宣告修補有效。

## 本次整合風險

2026-10-07 本機逐項人工小實驗僅證原先範圍；整批交付包含CLI、測試裁判與跨方案脈絡，改按 [[Projects/修補驗證與來源留存整合_計劃]] 高風險設計及代碼審核對。不是改掉原實驗結果，也不靠改風險標籤宣稱已審過；待實際處置閘收據。


完整材料：/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/根因修復與行為保留配對_計劃.md
---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
self_audit: gpt-6.1-sol/2026-10-06
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/每輪修補差異派工
related:
  - "[[Projects/每輪修補差異派工_計劃]]"
  - "[[Projects/修補驗證與來源留存整合_計劃]]"
verified_by:
  - "[[Verification/2026-10-06_根因修復與保留配對驗證]]"
---
# 根因修復與行為保留配對_計劃

白話：修負數問題前，也先挑零、正常正數、上限與相鄰呼叫者中會受修補影響的既有行為；修完分開確認「修好了」與「保住了」。

WHY:沿用既有根因組與兩版證據，先改善人工選例 [出處:2026-10-06 使用者同意先做修復與保留案例] [因:只驗原問題會漏掉修補造成的相鄰退化]
PRIOR-ART: 借用SWE-bench修復與保留既有測試分開判定的觀念 https://www.swebench.com/SWE-bench/api/harness/ ，並借用Google對邊界、有效斷言及必要測試的審查要求 https://google.github.io/eng-practices/review/reviewer/looking-for.html 。最小落點是現有技能來源與人工證據，不引入其執行框架。
RETIRE-IF: 既有同一案例紀錄已能直接還原所有根因組的修復／保留角色與選例依據，且連續十個有程式修補的修訂輪沒有額外辨別出遺漏時，撤去重複配對清單，僅保留原紀錄指標；不是撤掉保留行為驗證。
REVISIT:2026-10-20 依每輪修補差異派工計劃的觀察入口核對實際使用與成本；不足十輪須記未判定，關閉本行前寫下30天內下一個日期。

## 範圍

只改三份已有家的技能來源：詳細做法放共用範本§3.1，代碼審手冊的「修與釘」接上修前選例，速查僅指路。CLI與修正紀錄格式、測試自動選擇、處置閘與輪數保持原樣。

對每個程式修復根因組，編排者在動手修前留一組repair與preserve候選；群組沿用既有修正紀錄的group ID，能共用案例但逐組保留覆蓋理由。修完填兩版結果，分開判修復效果與保留行為。找不到基底或不能執行時留未判定，不能用修後綠替代修前保留證據。

配對紀錄可放rN-behavior-cases.json或既有intake的表格；必要資訊是根因組ID、finding IDs、角色、待驗行為與合約／需求或已確認產品行為的出處、固定兩版案例證據指標、選例依據及未覆蓋範圍。修前正常的preserve標籤需有可核對的修前成功證據；僅推測正常者標候選／未判定。修前先選案例，不要求在所有專案新增自動修前執行機制。

選preserve候選需看固定版本的改到函式、直接呼叫者與受影響合約，考慮正常、邊界、錯誤與相鄰呼叫行為，只挑與修補相關且能指出行為來源的案例。每組至少列一項保留候選；無適用行為則記具體原因交新席核對，不捏造測試。純文字修正用可重放的使用場景與既有同一案例規則，不硬套產品測試。案例數與未覆蓋範圍明寫，不表示全覆蓋。

保留案例修前失敗不是修補回歸；修前未跑或不穩定就未判定。題目變動、共同比較區間的因果與嚴重度判讀沿用現有§3.1，不重複建立另一種格式。下一輪新席獨立核對案例來源與覆蓋是否足夠，可以補案例；編排者不把上輪報告或作者因果結論送給新席。必讀材料仍計入原1800行總量。

## 條款

- [S1] 當每個程式修復根因組準備動手修時，手冊應引導先選repair與preserve候選並沿用既有群組與兩版證據，保留選例依據與未覆蓋範圍 [manual:核對三份技能來源接向同一詳細定義]
- [S2] 當原問題修後通過但相鄰保留行為退化時，配對判讀應分開報修復效果與保留結果；修前失敗或未驗不得報修復回歸 [manual:重放負數修好但上限或呼叫者退化的三版本受控案例]
- [S3] 當配對材料供新席核對時，範本應保留獨立選例與擴充權限、未判定、既有材料上限與閘結果 [manual:核對未驗與不適用案例不假裝通過且不取代完整改動]

## 實務隱患

已排除:金流:只改本機派工文字與受控小實驗，不處理交易
已排除:對外送出:不推送或發布，不寄送消息
已排除:不可逆:文字可獨立還原，受控案例不動正式資料
已排除:守衛面:不改CLI或既有判定結果、輪數與自動執行

## 回退

以git diff核對本功能三份技能來源的新增文字，僅移除該段與指路，保留原有同一案例規則與其他變更；計劃與驗證保留實際試行範圍，後續可記停止使用，不追改舊結果。

## 交付邊界與接手

來源實作完成後本計劃維持doing，等待實際試行；小實驗與手冊核對通過不能宣稱收斂輪數改善。例子與重放入口在governance/research/review-repair-regressions/repair-preserve-pairs/；技能安裝及觀察入口沿用 [[Projects/每輪修補差異派工_計劃]] 的〈接手與觀察入口〉，本次不執行全域安裝。

## 本次整合風險

2026-10-07 本機逐項人工小實驗僅證原先範圍；整批交付包含CLI、測試裁判與跨方案脈絡，改按 [[Projects/修補驗證與來源留存整合_計劃]] 高風險設計及代碼審核對。不是改掉原實驗結果，也不靠改風險標籤宣稱已審過；待實際處置閘收據。


完整材料：/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/跑滿回顧沿用修補因果證據_計劃.md
---
type: project
status: doing
created: 2026-10-07
updated: 2026-10-07
self_audit: gpt-5.6-sol/2026-10-07
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/每輪修補差異派工
related:
  - "[[Systems/loop-retro]]"
  - "[[Projects/修補驗證與來源留存整合_計劃]]"
verified_by:
  - "[[Verification/2026-10-07_跑滿回顧因果證據銜接驗證]]"
---
# 跑滿回顧沿用修補因果證據_計劃

白話：回顧不能只把「修完才被發現」改寫成「修補造成」；沿用已有兩版查證，缺證據就保留不知道。

WHY:把日後逐項修補證據接到跑滿回顧，避免未知原因被彙整成確定的修補回歸 [出處:2026-10-07 使用者持續授權與retro-attribution乾淨調研／受控helper]
PRIOR-ART: 借用Google SRE無責回顧對根因與預防措施的查核 https://sre.google/sre-book/postmortem-culture/ ；以本repo既有§3.1兩版案例和§9回顧骨架銜接，不重建因果計算或改歸族機器。
RETIRE-IF: 十份實際代碼審跑滿回顧中，補充指路未避免任何無證據的修補歸因，且準備時間高於省下的重查，簡化本段為短指路，保留原兩版判讀與未知不灌成零。
REVISIT:2026-10-21 沿現有loop retro-stats與對應回顧／派工／intake核對實用、錯誤分類與成本；不足十份維持未判定，關閉前接30天內日期。

## 做法

本案只補共用範本§9並讓手冊與速查指向它。保留八種family、原evidence只收帳上現存席報告的形狀、note原字數、起草者／補完者及人裁觸發、處置與輪數。不修CLI，不改歷史已記回顧，不指控既有分類已錯。

代碼審產品缺陷列fix-induced前，起草者獨立核對既有intake指向的§3.1同一案例、兩版可比與修補因果證據；只有報告的結論、修後新出現、同類或位置／ID關係都不夠。若可比區間混入其他變更而未隔離、只有修後失敗、載入／執行未完成，就保留未判定。

編排者依已有資料逐項列所需原始案例／binding／輸出，不預填因果結論；派工材料只添原已存在的證據，安全非敏感必要部分沿§3.1規則。起草者只讀列定材料與原始觀察，不把報告或作者結論當判準。證據不可得就不造材料、不重跑產品、不拼版本。

若沒有證據支撐其他原有family，就用現有other，note至少十字，寫attribution-undetermined、finding IDs及具體缺件；evidence仍是原報告路徑，不挪成原始輸出路徑。其餘可支撐的family照原定義，同族可為相同根因或相同類疏漏，但同族不證修補因果，根因未知明寫。why_cap與avoid不能從未知斷言修補致因或保證少一輪；可寫已知瓶頸與需補的證據，原字數與changes欄仍照填。

混合族逐項留finding／輪次與觀察指標，可在note敘明有證據部分與未知部分或拆項，不把一項成立擴成全族成立。觀察、歸族與可測量原因分開；other未知不挪為零回歸、不與regression_set互相代填，也不改severity或處置。流程與設計缺陷用相應固定文字／卷證核對，不能硬套產品執行紅綠。本段不證形式檢查變成語意判定，不額外啟動審查輪。

## 條款

- [S1] 當代碼審產品缺陷回顧列修補引入時，範本應指向既有同案例兩版證據、列必要原始材料，且未知不被結論或分類取代 [manual:核對§9與四項實際checker helper對照]
- [S2] 當原因未知、混合或屬非產品缺陷時，範本應沿原八類與note／evidence保持相容、限定逐項結論，且不改severity／處置／regression_set [manual:核對unknown／有證據部分／設計文字三種回顧情境及兩處指路]

## 實務隱患

已排除:金流:本機派工文字與合成helper
已排除:對外送出:不發布、不呼叫服務
已排除:不可逆:可單獨還原的文字
已排除:守衛面:不改CLI、骨架、閘、分類值或輪數

## 回退與收尾

按本功能差異移除§9新增因果／材料說明與兩處指路，保留原回顧與§3.1。來源完成仍doing；十份真實回顧完成證據／成本核對與保留／簡化決定，兌現來源處置並立驗證後才done，受控fixture不算樣本。Systems觀察集合承接本計劃，不代表現有主線已部署此補充。

## 本次整合風險

2026-10-07 本機逐項人工小實驗僅證原先範圍；整批交付包含CLI、測試裁判與跨方案脈絡，改按 [[Projects/修補驗證與來源留存整合_計劃]] 高風險設計及代碼審核對。不是改掉原實驗結果，也不靠改風險標籤宣稱已審過；待實際處置閘收據。


當前957尚未修固定樹：_nodehome_list
def _nodehome_list(repo_root, where, oids=None):
    """where='index' / 提交 sha / None(空)。回 (一般檔 {路徑: 模式}, 所有路徑) 或 None(git 失敗)。
    模式從索引或提交樹讀——連結檔(120000)與子模組(160000)不算一般檔 [S40]。
    oids 給一個 dict 時順便填 {NFC 路徑: 內容編號}(一般檔才填):要讀內容的呼叫端拿編號讀,不必管 git 裡存的檔名寫法。"""
    if where is None:
        return {}, []
    raw = _nodehome_git(repo_root, "ls-files", "-s", "-z") if where == "index" else \
        _nodehome_git(repo_root, "ls-tree", "-r", "-z", "--full-tree", where)
    if raw is None:
        return None
    files, allp = {}, []
    for ent in raw.split(b"\0"):
        if not ent or b"\t" not in ent:
            continue
        meta, p = ent.split(b"\t", 1)
        parts = meta.split()
        if where == "index":
            if len(parts) != 3 or parts[2] != b"0":      # 合併中的衝突階段不算
                continue
            mode = parts[0]
        else:
            if len(parts) != 3:
                continue
            mode = parts[0]
        path = nfc(os.fsdecode(p))
        allp.append(path)
        if mode in (b"100644", b"100755"):
            files[path] = mode.decode()
            if oids is not None:
                oids[path] = (parts[1] if where == "index" else parts[2]).decode()
    return files, allp


當前957尚未修固定樹：_nodehome_reader
def _nodehome_reader(repo_root, where, from_git=False):
    """回 read(path)->bytes|None。讀的是 where 那個版本:跟磁碟一樣的直接讀磁碟,不一樣的用 git show 讀
    ([S38]:提交前只讀提交索引——同一個工作目錄另一個會談寫到一半、還沒加進索引的東西讀不到)。"""
    if where is None:
        return lambda p: None
    disk_ok_all = False
    differ = None
    if from_git:
        pass                                                # 新借用的測試證據只讀版本,不信先前的磁碟相等判定
    elif where == "index":
        differ = _nodehome_changed_vs_disk(repo_root, "index")
    else:
        head = _lens_full_sha(repo_root, "HEAD")
        if head and head == where:
            differ = _nodehome_changed_vs_disk(repo_root, where)
    root = Path(repo_root)
    spec = "" if where == "index" else where

    def read(p):
        if differ is not None and p not in differ:
            fp = root / p
            try:
                if fp.is_file() and not fp.is_symlink():
                    return fp.read_bytes()
            except OSError:
                pass
        r = _lens_git(repo_root, "show", f"{spec}:{p}", binary=True)
        if r is None or r.returncode != 0:
            return None
        return r.stdout
    return read


當前957尚未修固定樹：_nodehome_changes
def _nodehome_changes(repo_root, base, tip):
    """[(狀態字母, 舊路徑, 新路徑)];改名的新路徑算新增 [S31]。base=None 且 tip='index' → 看暫存區。
    ★只帶 -M、沒帶 -C★:複製出來的檔 git 標成 A,照樣算新增(使用者設了 diff.renames=copies 也一樣,-M 蓋過它);
    下面認 C 那半只是防呆,這條呼叫實際收不到 C(代碼審 r1 正確性席)。"""
    if tip == "index":
        args = ["diff", "--cached", "--name-status", "-z", "-M"]
        if base is None:
            args.append(_EMPTY_TREE_SHA)
    else:
        args = ["diff", "--name-status", "-z", "-M", base or _EMPTY_TREE_SHA, tip]
    raw = _nodehome_git(repo_root, *args)
    if raw is None:
        return None
    toks = _nodehome_split_z(raw)
    out, i = [], 0
    while i < len(toks):
        st = toks[i]
        code = st[:1]
        if code in ("R", "C") and i + 2 < len(toks):
            out.append((code, nfc(toks[i + 1]), nfc(toks[i + 2])))
            i += 3
        elif i + 1 < len(toks):
            p = nfc(toks[i + 1])
            out.append((code, p if code != "A" else None, p if code != "D" else None))
            i += 2
        else:
            break
    return out


當前957尚未修固定樹：cmd_home_check
def cmd_home_check(repo=None, staged=False, diff_range=None):
    """lumos home check --staged | --diff A..B [S24]:有新違規 rc1,沒有 rc0;沒有圖譜/合併中/開關 off 說一句跳過、rc0。
    git 跑不起來=fail-open(說一句、rc0):這道閘只擋「確定是新違規」的,不因為環境壞了擋人。
    ★設定、工具自裝檔、圖譜位置都從被檢查的那個版本讀★(提交前=提交索引、推送前=終點那個提交),不讀工作目錄。"""
    root = Path(repo).resolve() if repo else None
    if root is None:
        r = _lens_git(".", "rev-parse", "--show-toplevel")
        if r is None or r.returncode != 0:
            print("擋下:這裡不是 git 專案,用 --repo 指定", file=sys.stderr)
            return 2
        root = Path(r.stdout.strip())
    if staged:
        mh = _lens_git(root, "rev-parse", "-q", "--verify", "MERGE_HEAD")
        if mh is not None and mh.returncode == 0:
            print("每支檔有家:合併提交跳過(推送前會把合併的結果整段查一次)", file=sys.stderr)
            return 0
        head = _lens_full_sha(root, "HEAD")
        base_where, tip_where, mode_word = head, "index", "這次提交"
        index_before = _nodehome_git(root, "ls-files", "-s", "-z")
        changes = _nodehome_changes(root, head, "index")
    else:
        # 寫法用派工鏡頭那支判法:恰好兩個點、兩端都有、不收三個點——原本只切第一個「..」,
        # 三個點的寫法變成「起點 到 .終點」、找不到就放行,同一條違規完全沒擋(代碼審 r1 邊界席)
        rg = _lens_range_ok(diff_range)
        if rg is None:
            print("擋下:--diff 要給 <起點>..<終點>——恰好兩個點、兩端都要有(三個點的寫法這裡不收:"
                  "先用 git merge-base 算出起點再給)", file=sys.stderr)
            return 2
        a, b = rg
        tip = _lens_full_sha(root, b)
        if tip is None:
            if _ZERO_SHA_RE.fullmatch(b):
                print("每支檔有家:範圍終點是全 0(刪除分支),沒有要查的東西", file=sys.stderr)
                return 0
            # 推送前與 CI 的終點一定找得到,找不到就是範圍寫錯;三道檢查一致當參數錯(筆記內容審代碼審 r2 兩席)
            print(f"擋下:範圍 {diff_range} 的終點在本機找不到——範圍寫錯了?", file=sys.stderr)
            return 2
        base, why = _lens_push_base(root, a, tip)
        if why:
            print(f"每支檔有家:{why}", file=sys.stderr)
        if base is None:
            _gate_event_or_warn(root, "nodehome-check", "skipped", why)
            return 0
        base = _nodehome_clamp_base(root, base, tip)
        base_where = None if base == _EMPTY_TREE_SHA else base
        tip_where, mode_word = tip, "這次推送"
        changes = _nodehome_changes(root, base_where, tip)
    if changes is None:
        print("每支檔有家:git 算不出這次的改動,跳過(fail-open)", file=sys.stderr)
        return 0
    lst = _nodehome_list(root, tip_where)
    if lst is None:
        print("每支檔有家:git 讀不到檔案清單,跳過(fail-open)", file=sys.stderr)
        return 0
    # 圖譜位置:被檢查的那個版本裡的 docs/*-knowledge(推送一個不是目前 checkout 的分支,工作目錄那份可能不一樣)
    vaults = sorted({_vault_slug_of(p) for p in lst[1]} - {None})
    wv = _vault_in(root)
    wv_rel = wv.resolve().relative_to(root.resolve()).as_posix() if wv is not None else None
    if wv_rel and wv_rel.startswith("docs/") and wv_rel.split("/", 1)[1] in vaults:
        vault_rel = wv_rel
    elif vaults:
        vault_rel = "docs/" + vaults[0]
    else:
        print("每支檔有家:這個專案沒有圖譜,跳過")
        return 0
    reader = _nodehome_reader(root, tip_where)
    cfg = _nodehome_config(root, reader(".lumos/config.json"), from_snapshot=True)
    for w in cfg["warnings"]:
        print(f"提醒:{w}", file=sys.stderr)
    if cfg["mode"] == "off":
        print("每支檔有家:這個專案把這道檢查關掉了(node_home.gate=off),跳過", file=sys.stderr)
        return 0
    N = _nodehome_side(root, tip_where, vault_rel)
    changed_paths = {p for _c, o, n in changes for p in (o, n) if p}
    B = _nodehome_side(root, base_where, vault_rel, share=N, changed=changed_paths)
    if B is None or N is None:
        print("每支檔有家:git 讀不到檔案清單,跳過(fail-open)", file=sys.stderr)
        return 0
    skip = frozenset() if _is_toolchain_repo(root) else _vendored_state(root, "" if staged else tip_where)[0]
    _tj = []

    def tag_judge():
        """測試名判定,第一次真的需要(某篇只差測試綁定)才建——建索引要掃測試檔。"""
        if not _tj:
            _tj.append(_nodehome_tag_judge(root, None if staged else tip_where))
        return _tj[0]
    groups = None if staged else _nodehome_mark_note_content(root, _nodehome_commit_groups(root, base_where, tip_where), vault_rel,
                                                                 tag_judge=tag_judge, route_cfg=cfg, route_skip=skip)
    staged_route_tests = set()
    if staged:
        candidates = set()
        for side in (N, B):
            for note in side.notes.values():
                for value in note["about"]:
                    key = _nodehome_key(value)
                    if key in changed_paths:
                        candidates.add(key)
        for side in (N, B):
            staged_route_tests.update(_nodehome_route_tests(
                root, side.files, side.all_paths, candidates, side.where, cfg, skip,
                reader=_nodehome_reader(root, side.where, from_git=True)))
        if staged_route_tests and (index_before is None or _nodehome_git(root, "ls-files", "-s", "-z") != index_before):
            staged_route_tests.clear()                     # 觀察到索引變動時撤回借用證據,不改既有正式程式退路
            print("提醒:暫存區在檢查期間變動或讀不到,額外測試寫回證據不採信;請重新檢查。", file=sys.stderr)
    res = _nodehome_evaluate(root, B, N, changes, cfg, skip, vault_rel, groups=groups, tag_judge=tag_judge,
                             staged_route_tests=staged_route_tests)
    homesN, _own = _nodehome_homes(root, N)
    lines = _nodehome_render(res, homesN, N, cfg, mode_word)
    blocked = bool(res["blocks"])
    if blocked and cfg["mode"] == "warn":
        lines = [l.replace("擋下:", "提醒(node_home.gate=warn,不擋):", 1) for l in lines]
    for l in lines:
        print(l, file=sys.stderr)
    # 治理帳:nodes 只放程式檔路徑(統計語意表這麼宣告);沒有程式檔的違規(負責範圍)把節點另放 notes
    files, notes_ = set(), set()
    for kind, it in res["blocks"]:
        if kind in ("new-homeless", "write-back-homeless"):
            files.add(it)
        elif kind == "home-removed":
            files.add(it[0])
        elif kind in ("foreign", "foreign-awakened"):
            files.add(it[1]); notes_.add(it[0])
        elif kind == "route":
            files.update(it[1]); notes_.add(it[0])
        else:
            notes_.add(it[0])
    kind = "blocked" if blocked and cfg["mode"] == "on" else ("warned" if blocked else "passed")
    extra = {}
    if res["pairs"]:
        extra["pairs"] = [list(x) for x in res["pairs"][:100]]
    if notes_:
        extra["notes"] = sorted(notes_)[:50]
    _gate_event_or_warn(root, "nodehome-check", kind,
                        f"{mode_word}:新違規 {len(res['blocks'])} 條" + ("(warn 模式不擋)" if blocked and cfg["mode"] == "warn" else ""),
                        hard=(kind == "blocked"), nodes=sorted(files)[:50], extra=extra or None)
    return 1 if kind == "blocked" else 0


現行共用範本§3.1：
 修訂輪的修補鏡頭（編排者準備，僅供 code-loop）

上一輪有程式、測試或流程修補時，準備下列材料，並把本節末尾的提問段放進每席派工詞。首次審查不放。這是人工準備與判讀流程，CLI 沒有新增強制檢查。

0. **修前選例，修後配對**：在動手修每個程式根因組之前，編排者沿用既有修正紀錄的group ID與finding IDs，先列 `repair`（原問題）及 `preserve`（須維持的既有行為）候選。可存 `rN-behavior-cases.json` 或既有intake表格，逐組記角色、待驗行為與合約／需求或已確認產品行為的出處、選例依據、兩版案例證據指標及未覆蓋範圍；兩版證據的唯一格式沿用本節第6步。案例可跨組共用，仍逐組說明涵蓋理由，不改修正紀錄的CLI欄位。
   - **同類提醒與根因關係分開**：既有fix-check按前輪category與本輪major以上觸發prior，不代表同根因或修補因果。編排者在intake逐條連前後finding／group ID、固定版本、症狀／觸發輸入、受影響需求、失效機制與第6步證據；ID或位置相同不證同根因，改名或換ID不證不同。根因相同／不同都要可核對案例與機制，不足就關係未判定，不靠粗分類下結論。
   - 提示要prior時仍填原兩欄且各至少十字：why_failed寫前次實際涵蓋／未涵蓋與證據界線，關係未知就具體寫缺什麼，不編造前次修錯；new_approach寫本輪具體補法與待驗／保留案例。文字過檢查不證關係或修法有效。前次問題殘留／再現不自動等於修補造成退化；regression_set仍按第6步與本節收貨規則填，不因同類就列入。類別不同或關係未判定也不降severity、不丟發現，新席照原規則獨立查證完整改動。
   - 保留候選從固定版本的修補函式、直接呼叫者與受影響合約選：考慮正常、邊界、錯誤與相鄰呼叫路徑，只挑能指出行為來源且與修補相關的案例。每組至少留一項保留候選；無適用者留具體原因供新席核對，不捏造測試，也不表示已驗無回歸。純文字修正沿用可重放使用場景，不硬套產品測試。
   - `preserve`確認為修前正常，須有可核對的固定修前版本成功證據；修前已失敗、未跑、不能載入或不穩定者，保留候選／未判定與原因，不能說修補回歸。修後分開記「原問題修復結果」與「各保留案例結果」，不可只因repair通過就把整組記成功。不新增自動修前執行機制，也不把 `unaffected` 的人工理由當保留成功證據；列在既有fixed路徑tests中的測試仍照原制驗修後綠。
   - **分開驗修補與重構**：區分直接修補、必要配套與非必要清理／重構；可獨立時先保存僅修補與必要測試的完整可執行固定版本，驗repair及preserve，再保存重構版驗受影響的相同preserve。必要重構先行時先驗重構前後保留行為，再驗修補；拆不開則記原因與合看路徑，不拼混合版本，不以不能載入的半成品當回歸。每個點留完整提交、涵蓋組與本節第6步證據指標；順序不是因果證明，測試／設定／環境變更沿用未判定規則。
   - 中間點可用暫時本機提交；推前仍按一功能一提交整理，最後可一起PR，不因此增加輪數。壓提交或換基底後按原規則重新固定派工版本與留痕，歷史中間結果不可挪成新版本通過。新席從完整改動核對作者分類，不以分類排除檔案。
   - **高風險保留案例驗抓錯能力**：同根因反覆修補、共用邊界被改或懷疑保留斷言只報綠時，挑一項有需求／合約或已確認行為來源的相關小錯誤，記觸發與選擇理由；不每輪遍歷全程式。執行前查核實際端點斷線／替身、測試身分與可重置夾具，記非敏感證據；worktree只隔離檔案，不隔離資料庫／服務。無法安全隔離就不執行、記未判定。只在隔離副本套錯誤，錯誤版不作產品提交。
   - 沿第6步固定完整產品與測試來源、輸入／預期／環境、實際載入證據及原文→改文指紋；固定可控亂數、時間、順序，每次重置等同夾具狀態，預先安排原版綠→錯誤版目標行為斷言紅→還原原版綠，還原後驗載入／快取，任一步不成立就未判定，不反覆重跑洗綠。語法、載入／收集失敗、超時、未跑、不穩定或無關紅燈不算有效偵測。等價／無效錯誤或未到達路徑記不適用／未判定；相關錯誤仍綠只證此案例未偵測此錯誤，不指控產品已壞或全套無效。補案例／斷言後用同一錯誤再驗上述對照，保留原結果。
   - 有真實既有合約／配方才沿既有 `guard kill` 入口；逐筆核對版本、配方ID、測試來源、狀態、weak與真正斷言，總rc或killed標記不能代替。weak=true一律不算本次有效偵測，記原因、排除弱因後固定重驗；未提交筆記的試跑仍非正式背書。真正失敗內容取既有runner原始報告／必要完整節錄，記來源與逐筆綁定；只有截斷摘要、原始報告取不到就未判定。已有人工probe另按第6步記實際版本與錯誤，不挪為原配方執行或合約背書，不反推新合約、不新建執行器。命令與輸出只保留必要非敏感內容，保存前遮罩秘密／個資並記範圍；不能安全保留可核對證據就未判定。這只回答所驗版本與小錯誤，未證無其他回歸，不改既有閘或輪數。
   - 新席取得待驗行為、案例與來源，不讀上輪席報告或作者因果結論；獨立核對選例是否足夠，可補案例。編排者的配對不限制新席範圍，材料仍計入原1800行總量，完整改動與上下文不被案例清單取代。

1. **固定兩端**：起點取上一輪派工單的 `base_commit`；終點取修補已提交後的完整提交碼。上一輪已跑 fix-check 時，用它 JSON 結果的 `base`、`head` 核對這兩端，並保留結果檔。但派工單與修正紀錄可能共用錯誤起點，兩者一致不是獨立證明；另核對上一輪凍結快照的生成範圍／版本留痕，確認起點是那一輪實際被審的提交，必要時以固定範圍重生審材核對內容。只對上檔名、快照SHA或兩份相同base不算完成。缺少可核對的版本來源時，binding 記 `before_provenance: undetermined`、保留原因與所比較的兩個實際提交，不稱已確認修前版本、不據此歸因修復回歸。派工單不完整、多份互相矛盾、結果沒有這兩欄或起點不同時，先釐清；不能猜 `HEAD~1`、改用最新分支名稱或把材料不可得當空差異。fix-check 的未執行項也一併保留，不把前置失敗說成測試已跑。
2. **產生兩版差異**：用已核對的兩個固定提交，執行 `git -c core.quotePath=false diff --no-ext-diff --no-textconv --no-color --no-renames --binary --full-index -U10 "<修前完整提交碼>" "<修後完整提交碼>" --`，stdout 存到下一輪的 `rN-repair.patch`。檢查命令成功才使用材料；不要以 merge-base 取代修前版本，也不要按作者的修正紀錄挑檔。這份差異含兩版之間全部已提交變動，不是自動判出的「只有修復」。
3. **留來源**：建立 `rN-repair-binding.json`，記 `before_commit`、`after_commit`、兩端 `git rev-parse "<提交碼>^{tree}"` 的樹碼、`patch_sha256`、上一輪派工單與 fix-check 結果檔的位置及 SHA-256（沒跑則記未執行）、`ancestry`（`git merge-base --is-ancestor` 的 rc0/rc1；其他退出碼是查詢失敗）、`attribution_limits`。指紋用讀檔 bytes 計算；派下一輪時再核對一次，版本與材料不符就重做。另在 intake 保留本輪 fixed/unaffected 路徑的說明，不能讓它代替完整差異。
4. **說清歸因界線**：非祖先版本、換基底、合併其他工作或無法分離的測試／設定變更，都列在 `attribution_limits`。祖先關係成立也不表示中間只有修復；空差異只表示兩棵樹沒有內容差異，不能宣稱無回歸。這一階段不自動拼裝混合版本或推論原因。
5. **供應上下文**：原始完整分支改動與完整兩版差異仍可讀。先核對完整改檔清單；產品碼、技能來源、測試、設定與決策變更都要在實際閱讀材料中。純歷史卷證、產生的測試log或二進位封存可歸檔不重讀，但要在 binding 逐檔列 `archive_only` 及理由；不能只按目錄前綴排除，更不能把卷證目錄中的可執行檔當紀錄。若另產 `rN-repair-review.patch`，其路徑、指紋與涵蓋檔也列在 binding，並保留原差異供查核。將實際必讀修補差異、完整改動、必要的固定版本完整函式／呼叫者、受影響合約、測試與設定變更列入派工單 `materials`。正文上下文用 `git show "<固定提交碼>:<檔案>"` 查，工作目錄只供找線索。沿用既有固定圖譜鏡頭；不把上一輪席報告或作者的因果結論供給新席。每席必讀材料總量（完整改動、修補差異與附錄合計）超過 1800 行就拆範圍或分席，不能只計新差異，也不能把同一批全部材料原樣丟給每席卻說已拆分。資安席對最後完整快照的覆蓋規則仍照原制。


6. **核對同一案例**：收貨時，每條 finding，以及三問中「原問題已修復／正常路徑仍成立」的每個行為主張，都用下列同一份證據紀錄；零 finding 也不能省略正向主張的依據。可引用同一個原始紀錄，無需複製內容。這是審查員獨立查證後的輸出，不是編排者預先提供的答案。
   - `claim`：finding ID 或具體被驗的行為；`input`、`expected` 及合約／需求出處。兩版題目、夾具或預期不同，先說明差異，不以各自綠燈判已修好或無退化。
   - `case_source`：實際測試、probe及夾具的固定版本或內容指紋；必要的版本適配記適配內容與界線。指紋相同只證內容相同；仍須確認斷言與輸入真的等價。
   - `before`／`after`：各記實際命令、工作目錄、實際載入產品版本的查核方式與結果、相關環境前提、退出碼、實際執行／跳過狀態與行為觀測，連到原始輸出。命令中寫了版本、路徑或測試名稱不等於實際載入已核對；語言／工具無法證明載入來源時保留未判定。環境紀錄只留相關非秘密資訊，不抄整份環境變數。
   - `comparison`／`attribution`：先判是否能比較，再判能否歸因。題目不同、未執行、收集失敗、缺檔、超時、環境不可比或不穩定結果都不能當產品行為失敗；寫未判定與原因，不反覆重跑直到變綠。即使有可比的綠→紅，若區間混入其他可達變更且原因未由既有中間提交或其他可核對的隔離證據釐清，只說區間出現退化，修復歸因維持未判定、不列 regression_set。不新增回退執行器，不自動回植測試或拼混合版本。

修訂輪派工詞追加段（把 `{}` 換成真實材料與版本）：

```text
修補鏡頭：修前 {before_commit} → 修後 {after_commit}。
修補差異：{rN-repair.patch}；來源：{rN-repair-binding.json}；完整改動入口：{完整快照}。
這份差異可能含其他工作，歸因界線請先讀 binding，不能把每個新發現都算修復造成。
配對案例入口：{behavior-cases紀錄或intake的案例來源段}；案例只是待驗範圍，不是作者判定已修好或因果成立的證據。獨立核對repair與preserve選例，必要時補案例，分開報兩種結果；缺修前證據或無適用者留未判定與原因。
除了本席原有鏡頭，核對：①原問題的修復效果有何行為證據？②修補處的正常、錯誤與相鄰呼叫路徑是否仍成立？③新發現的同一案例在修前、修後各是什麼結果？
不要讀上輪席報告或作者的因果結論；從固定版本、合約與症狀獨立查證。
每條 finding 除既有 severity、引句與失敗場景外，另寫「歸因：有證據的修復回歸／有證據的原有漏查／未判定」，附兩版查證命令與結果；沒跑、不能載入、跳過、環境不同或不穩定就說明未判定。
只見修後失敗不能證明回歸；只見測試通過不能證明問題解決。重大發現不因原因未判定而降級或丟掉。
最後回答上述三問；每條finding及「已修復／正常路徑仍成立」的正向主張，都附§3.1第6步的同一案例證據。零finding仍須留已驗主張的證據與未驗範圍；證據不足回答未判定，不寫整體無回歸保證。
```

收貨沿用既有格式與證據閘，歸因文字不改 severity、finding-kind 或處置欄位。編排者在 intake 對每條歸因留兩版證據與未判定原因；`--regression-set` 只列已支持由上一輪修補造成的 finding ID。只有本輪已報 findings 全數完成歸因，且沒有 finding 有證據屬修復回歸時才填 `none`；`none` 不表示未發現區域沒有回歸；存在未判定時保留其 ID 與原因、可不填此選填欄，不能把缺欄統計成零。三問中的未判定行為另外保留在intake，不因finding歸因填了none就抹掉。誤報仍由原有重現與辯方流程判讀，沒有兩版證據不等於誤報。流程文件與測試的修補也可審，但不可硬套產品執行結果作因果證明。

## 4. Code-loop 辯方（**預設 Codex**，不可用退 opus 註記；2026-07-18 S5）

同模板 2（含路由制：低共識才開庭），把「設計 spec 的審計 finding」換成「代碼分支的審計 finding」、
查證工具加 `git log/git show`（commit 考古常是決定性反證：發版狀態、先例、時序）。
可要求「若維持，附最小修法建議」——本次 migration 自癒段就是辯方降級時附帶的
nice-to-have 轉化成的 fix。

## 5. SDD implementer 派工（模型分級：計畫含完整代碼→haiku；多檔整合/寫測試→sonnet）

```
你是實作者。專案：{repo 根}（{技術棧}）。本任務是「{功能名}」{M} 個任務中的
第 {N} 個：{一句話}。

**先讀需求檔（唯一需求來源，程式碼一字不差照用）**：{task-N-brief.md 路徑}

前置任務已完成的介面（你可直接用）：{exact 簽名/屬性清單，只列本任務會碰的}
{前面任務踩過的坑，一句話傳承：如「種子必須綁店否則 guard 測試假綠」}

補充脈絡與慣例：
1. TDD：先寫測試跑紅 → 實作 → 綠。{測試指令、環境變數、harness 模式指引}
2. {環境細節：PATH、連線字串來源}
3. **commit 慣例（pre-commit gate 硬擋 code 無圖譜 commit）**：把計劃節點
   {路徑} 的 Task {N} checkbox 勾成 [x] 同 commit 進。message 照 brief。
   不要 --no-verify。{branch} 直接 commit。

完成後完整報告寫 {task-N-report.md 路徑}（測試紅→綠輸出、build、commit hash、
{任務特定證據}），回覆只回：狀態（DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED）、
commit hash、一行測試摘要、concerns。開工前不清楚先問。
```

## 6. SDD task reviewer（sonnet；⚠ 機械任務可由編排者自審跳過此派工——見下方調參）

```
你是 task reviewer。兩個必答判定：**spec 合規**（brief 全做到、無多餘）與
**任務品質**（Approved / 需修）。

讀三個檔：
1. 需求 brief：{task-N-brief.md}
2. 實作者報告：{task-N-report.md}
3. diff 全文：{review-package 產出的 .diff 路徑}

本任務綁定的專案約束（來自 spec，逐字抄）：{值碼合約/邊界語意/不可動的呼叫等
binding constraints，3-6 條}

檢查點：{任務特定的驗證焦點，含「實作者自陳的偏離/假綠修正要獨立推演成立與否」、
「diff 無無關變更」「計劃節點 checkbox 只動本 task」}。有疑慮可 Read 實際檔案深挖。

輸出：spec 合規 ✅/❌ 逐項、問題標 Critical/Important/Minor、任務品質判定、
⚠ 無法驗證項（列出，由編排者裁決）。
```

---

## 編排者判讀規則（prompt 之外、skill 正文用）

- **剝除克制**：只有能指出 finding 客觀錯在哪（被 spec/code file:line 反證）才剝；
  判不準保留（寧可高估）。辯方只買 code 層假陽性，業務層留人。
- **severity 錨（2026-07-16 M1，與 SKILL.md 判讀 ② 同句）：major=照 spec 字面實作會做出**錯的行為**或漏掉合約;文件精度/測試枚舉完整性/措辭=minor,除非漏的是合約級。**難判搖擺場換問法重問一次**(「這條 finding 若實作照做,具體錯在哪個行為?」),兩問等級不一致=取高並記 unstable(Sage 2026-07-27)。
- style-bias 錨（2026-07-21，外審吸收）**：severity 按**後果**判（照 spec 實作會發生什麼），
  不按 finding 寫得多詳細/多有說服力判——2026 實證 judge 最大偏誤是 style（0.76-0.92），
  position 反而極小；一條寫得漂亮的 minor 仍是 minor，一條寫得潦草的 major 仍是 major。
- **blocking↔severity 綁定（2026-08-25 [S3],[[Projects/設計審收斂重定義_計劃]]）**：blocking:否 ↔ minor;blocking:是 ↔ major/blocker——席報告兩欄矛盾=整份退回該席重判(編排者人工核,無機械擋;矛盾率在實測輪抽驗)。**兩層不互改**：blocking 是審查員層宣告,accepted 是編排者處置層裁量——被放行的 major 仍標 blocking:是+附 accept-reason,不回頭改席報告;cluster 三態帳無 accepted-major 態,散文處置不用 cluster 帳。
- **carrier 選席 SOP（2026-08-25 d1）**：記帳前對候選席報告跑 quote-check,選全錨席當 carrier——carrier=記帳載體、非證據總集（機制兜底=d5 記帳型態:各席一筆帶 report+sha,僅 carrier 帶三個 set）。
- **rN-intake.md 收貨紀錄（2026-08-25 d1;新增於收貨三道之外,非取代）**：編排者對佐證通道與錨不到引句的機械重現留痕檔,落 `governance/review-reports/<迴圈>/rN-intake.md`。每條格式=重現命令+輸出摘錄+**HIT/MISS 結論**;判準=命令必須能重現該席宣稱的那個結果,只證存在的查詢不算;**MISS=該條佐證不採信,其支撐的 finding 退回該席補證或降級**。此步為編排者人工判讀+機械留痕,非全機械。前掃語意類修正也逐條記這裡,**必含「修改前原句→修改後」對照**,派工詞告知席位可覆核推翻。★宣告行(2026-08-30 intake守衛 d1)★:首輪前掃第四類跑完,intake 檔**頂格獨立一行** `preflight-4: ran`(值域只有 ran;零命中也寫——跑了沒挖到東西仍是跑了;同檔多行=格式壞視同無;別把示例留在檔裡——parse 會剝 fenced 圍欄,但圍欄外的照抄殘留=偽宣告)。處置閘會印 intake 觀測行(advisory 不擋),doctor [I] 段滾動窗計出現率;記帳可帶選配 `--intake <rN-intake.md>`(存 sha,處置閘全輪重驗,竄改同罪)。
- **輪 severity = 辯方裁決後存活 findings 的 max**；findings 數 = 存活折入條數。

---

## 7.5 spec-conformance slot 派工(code-loop panel 追加位,2026-07-10)

```
你是對答案審查員。你唯一的工作:拿「收斂設計 spec」逐條對照「實作 diff」,判每條規格:
  已實作 / 縮水(做了但比 spec 少) / 多做(diff 有 spec 沒有的行為變更) / 未實作。
不找 bug(別的審查員管),只管合規。

收斂 spec:{計劃節點路徑}
Diff 檔(git diff -U10):{工作副本路徑}
repo:{repo 根}(可 Read/Grep 查證 diff 上下文)

紀律:
- 逐條款過,每條給裁定+diff 佐證(hunk 位置);spec 若有 [SN] 條款標記,輸出用 [SN] 編號。
- 「縮水/未實作」必須引 spec 原文;「多做」必須指出 diff 中無 spec 對應的行為變更(純重構/測試不算)。
- 判不準的標 ⚠ 交編排者。

輸出:四類清單(可為空)+ 最後一行「縮水+未實作共 N 條」。
```

## 7.6 架構對齊席派工(code-loop 與 design-loop 皆派;2026-08-22,Enzo:自動開發不得產出跟既有不一樣或不入流的寫法)

```
你是架構對齊審查員。你唯一的工作:判這份 diff(或設計)有沒有「跟這個專案既有的做法不一樣」。
不找 bug(別的審查員管),不評風格好壞——只管「一不一致」。

被審材料:{工作副本路徑}
同層最相似的既有檔(對照用,這些代表專案現在的寫法):{鄰居檔清單,pitfalls --diff 會吐}
這個技術棧的慣例 skill:{kotlin-idioms / csharp-idioms / vue-idioms / swift-idioms / node-idioms / python-idioms / java-idioms / dart-idioms,依副檔名;.ts/.js 看 package.json 分前後端}
圖譜裡相關功能筆記(DEP/FLOW 寫了模組邊界):{代碼迴圈:原樣留一行 `LUMOS-IMPACT: {base}..HEAD`,hook 會附固定席(見 §3 鏡頭 3);設計迴圈:留一行 `LUMOS-SPEC: <計劃.md>`,hook 從計劃提到的檔與直接連結的節點算(2026-09-05 起;之前手貼實測 209 份只有 14 份貼)}

三問(設計審多第四問),逐問答、每問附對照的 file:line:
1. 分層與依賴方向:新碼放的層、它呼叫誰、誰呼叫它,跟鄰居檔一樣嗎?有沒有跨層直呼(例:UI 直接打 DB、Service 直接 new 另一個 Service)?
2. 命名與錯誤處理:命名慣例、例外/錯誤回傳方式、日誌方式,跟鄰居檔一樣嗎?
3. 第二種做法:這份 diff 有沒有引入專案裡原本沒有的做法(新的 DI 方式、新的狀態管理、另一套 HTTP client、自創的工具函式而鄰居已有同功能)?
4. (設計審才問)落點合不合理:計劃的 lands_in 列了現況要寫進哪幾篇——該寫進既有那篇,還是另開一篇?派工詞尾端的「落點現況」列了每篇掛幾份計劃、幾行 KEY、管幾支檔;一篇已經很大、或要塞進的東西超出它的負責範圍,就該另開(每支檔有家,2026-09-11)。

跟棧別檢核題撞到時(2026-09-09 起,Projects/兩席相反時端出張力_計劃):派工單附的表態記錄裡若有 `status=tension` 的題,
那是作者已經看見兩邊——既有寫法 X(existing)、隱患 Y(hazard)、建議 Z(suggestion)、這次選了哪邊(chosen)。
你的工作是查這四欄真假:existing 指的檔真的那樣寫嗎(開檔對照)、hazard 在這份 diff 裡真的成立嗎、suggestion 在這專案可行嗎、
chosen 跟 diff 實際做的一致嗎——查到假的才報 finding;不重裁誰贏,不因「跟既有不一致」單獨再開一條。
若你自己發現「跟既有不一樣」、而該處對應的檢核題答了 satisfied,把發現寫成張力形狀:既有 X/隱患 Y/這次 Z/不一致 N 檔,
severity 照本席錨(最多 minor,除非引入第二種做法或跨層直呼)。

嚴重度錨(只有這一種判 major):
- major = 引入了「第二種做法」,或跨層直呼——之後每個接手的人要在兩套之間猜。
- minor = 命名/錯誤處理/日誌跟鄰居不一致,但結構對。
- 純風格偏好(空行、註解語氣)不列。

輸出:三問(設計審四問)各一段(對齊 / 不對齊 + 對照 file:line),最後「不對齊共 N 條,其中 major M 條」。
判不準(鄰居檔本身就不一致、專案沒有既有做法可對)標 ⚠ 交編排者,不硬判。
```

## 7.7 席位立場與輸出格式(2026-08-29,Enzo 裁 A+C;單源=[[Projects/席位人格化_計劃]] d1)

**為什麼**:對抗式審查的增益取決於三條件——(a) 席位之間夠不一樣 (b) 批評扣在事實上 (c) 裁判獎勵可查證。(b)(c) 本專案早有(逐字引句+refcheck 行號機驗+拿不出反證不准降級),**(a) 原本只做到「換鏡頭文字」**。本節補 (a) 的措辭層。★只取差異化,**不取互相攻擊到共識**★(諂媚從眾 85.5%／oracle gap 32.3pp／第三輪 23.9% 收在一致錯誤;席間維持乾淨脈絡、禁互辯)。

