# r2 s3 對抗審——既有消費者/回歸面/零擾動承諾

審查對象:`/tmp/閘觸發帳統計-r2.md`(154 行)。角度:既有消費者、回歸面、「不帶 `--stats` 逐字元不變」的承諾是否兌現。不重報 r1 已修項(去重歧義/範圍刀自違/usage 帳誤植/測試對應)。全部發現皆對照 `scripts/lumos` 實碼與 `docs/.*-log.jsonl` 實資料驗證,行號經 `sed -n` 現場核對。

---

## 發現 1(blocker)—— `_KNOWN_GATES` 的「漂移釘」測試方法論本身結構性看不到 6/7 個帳源的 gate 字面值,直接推翻它自稱的「頭號證據」

引句:「掃 `scripts/lumos` 原始碼,所有 `gov_events.append` 的 gate 字面值都在表內」

（同義另一處引句,S1 段一字不差重申同一方法論：「`scripts/lumos` 內所有 `gov_events.append({"gate": ...})` 的字面值都在表內」）

**問題**:規格把「零觸發桶產出前提」的完整性測試(`t_gov_stats_known_gates`)定義成「掃描 `gov_events.append(` 這個字面呼叫模式」。但 `gov_events` 這個變數**只存在於 `run_doctor` 函式內**(`scripts/lumos:453` 起宣告),只覆蓋寫進 `.governance-log.jsonl` 的 7 個 doctor gate(`check-r/check-s/check-e1/check-e2/check-e3/check-k/check-j`,對應 `scripts/lumos:785,789,792,819,825,866,948,989,1030,1303`)。

而規格自己在 S1 開頭宣稱(引句:「母體 = `lumos gov` 既有讀入的帳」,列舉 bypass/rot-queue/governance/canary/kill/signoff/ci 七源)、以及在「不可混為一談」段明講(引句:「故本案統計天然涵蓋它們」,指 canary/signoff/kill)——這六個非 governance-log 來源的 gate 字面值(`L2`、`L3`、`canary`、`kill`、`signoff`、`ci`)**根本不是在 `run_doctor` 裡用 `gov_events.append` 寫出來的**,而是在 `cmd_gov` 自己的 `load(...)` mapper lambda 裡硬寫的字面常數:

- `L2`:`scripts/lumos:2911`(`load(".bypass-log.jsonl", lambda d: {"gate": "L2", ...})`)
- `L3`:`scripts/lumos:2913`
- `canary`:`scripts/lumos:2931`
- `kill`:`scripts/lumos:2925`
- `signoff`:`scripts/lumos:2920`
- `ci`:`scripts/lumos:2944`

這六處**在 `cmd_gov` 函式體內**,與寫著 `gov_events` 變數的 `run_doctor` 完全是兩個函式、兩套字面來源。對 `gov_events.append(` 做字串/AST 掃描,語法上不可能命中這六行——不是「目前湊巧漏了」,是**規格描述的掃描目標與這六個 gate 字面值所在位置無交集**。

另外,即使只看 governance-log 這一源內部,`anchor-approve`(`scripts/lumos:10071`,經 `_append_governance_log(v, [{"gate": "anchor-approve", ...}])` 一個 list 字面量寫入,不是 `.append(` 呼叫鏈)與 `code-loop`(`scripts/lumos:13956`,`_codeloop_gov_log` 內建一個裸 dict 賦值給 `event` 再 `json.dumps` 直寫檔案,連 `.append(` 都沒出現過)這兩個 gate 也不會被同一掃描模式命中。這兩個恰好是文件「三個發現」第 3 點與收斂指標特例處理段落反覆引用、且實帳各有 142/77 筆的核心例子。

**驗證**(全部現場跑過):
```
$ grep -n "gov_events" scripts/lumos
453:    gov_events = []          # 本輪 gate findings → governance-log(--ci 才寫)
785,789,792,819,825,866,948,989,1030,1303: gov_events.append({"gate": ...})
1301:            gov_events.extend(j_gov)
1323:        _append_governance_log(env.vault, gov_events)
```
`gov_events` 這個識別字全檔案只出現在 `run_doctor`(453-1323)範圍內,`cmd_gov`(2883 起)完全不含這個變數名。而 `cmd_gov` 內部所有 `"gate": "..."` 字面值(L2/L3/canary/kill/signoff/ci,共六個)都在 mapper lambda 裡,經 `grep -n '"gate":\s*"[a-z0-9_-]*"' scripts/lumos` 確認位置如上。

**後果**:若照規格字面實作,`_KNOWN_GATES` 若真的用「掃 `gov_events.append`」這條漂移釘去產生/校驗,最多只能覆蓋 governance-log 一源的 7 個 doctor gate,**完全看不到 canary/kill/signoff/L2/L3/ci 六個 gate**,也看不到 anchor-approve/code-loop 兩個。這六~八個字面值若不靠人工另外補全,`--stats` 的「逐 gate 輸出」與「零觸發桶」要嘛整段看不到這些 gate(比零觸發更糟——連「這道閘存在」都不出現在報表),要嘛(若換一種寫法讓輸出改用「data 中出現過的 gate 集合」保底)則完全繞過了 `_KNOWN_GATES` 存在的理由——r1 blocker①「零觸發桶產不出來,因為沒有 gate 全集」在這六個 gate 上會**原樣復發**,只是換了個外觀:一道從今天起真的不再觸發的 `canary`,不會被歸進「零觸發」桶,只會從報表上悄悄消失,比「顯示零觸發但措辭自曝限制」更難察覺、更貼近「有守衛但實際沒有」——恰是這份文件自己在 Growth test 第 2 問(line 45)點名要防的那類問題。

**修法建議**(供實作參考,不代審計裁決):`_KNOWN_GATES` 的漂移釘測試必須同時掃描 `cmd_gov` 內六個 mapper lambda 的 `"gate": "<字面>"` 賦值,以及 `_append_governance_log(...)` / 任何直寫 `.governance-log.jsonl` 的字面 dict(如 `_codeloop_gov_log`)——不能只認 `gov_events.append(` 這一種呼叫形狀。

---

## 發現 2(major)—— 位置參數 `node` + `--stats` 併用時,四個「結構上不記節點」的來源會被結構性、非語意性地判成「零觸發」,規格的自曝限制句沒有覆蓋這個情境

引句:「以下統計僅為該節點視角」

**問題**:`cmd_gov` 對 `node` 過濾的實際執行點是 `ded = [r for r in ded if q in r["nodes"]]`(`scripts/lumos:2960`),發生在**任何下游統計計算之前**,規格 S1(line 99)也準確引用了這行。但四個來源的 mapper 硬寫 `"nodes": []`(不是「這次剛好沒有節點資料」,是**該來源的欄位設計就是空**):`L2`(`scripts/lumos:2912`)、`canary`(`scripts/lumos:2931-2932`)、`ci`(`scripts/lumos:2944-2945`)、`code-loop`(`scripts/lumos:13956`,`"nodes": []`)。

一旦帶了 `node` 位置參數,`q in r["nodes"]` 對這四源永遠是 `False`(空集合不可能包含任何東西),於是這四個 gate 在 `ded`(node 過濾後)裡**恆為零筆**——不管全域上它們觸發得多頻繁(canary 全史 451 筆、code-loop 77 筆、L2 61 筆)。若「零觸發桶」的判定基準是「node 過濾後的窗口」(規格全文沒有明講「零觸發桶只在無 node 時算」——「與既有旗標的互動」段只交代了要印縮限警示,沒有交代分類桶在 node 模式下要不要照跑、跑的話語意是什麼),則**任何**帶 node 查詢的 `--stats` 呼叫都會把 canary/code-loop/ci/L2 這四道閘全部歸進零觸發桶,而這其實是「這個來源結構上不記節點」的產物,跟「這道閘沒有守到東西/沒有被觸發」是兩件完全不同的事。

規格的零觸發桶自曝限制句(S1「分類桶」段)寫的是:「窗口內零筆——可能從未觸發,也可能是有效嚇阻或守的情境還沒發生;零觸發不等於無價值」——這句話的敘事前提是「全域窗口內真的零筆」,並不涵蓋「這個來源的欄位設計就不記節點,所以任何 node 過濾都必然清零」這個結構性成因。measure 誤讀的風險是:使用者對某節點跑 `lumos gov <node> --stats`,看到 canary/ci/code-loop 都在零觸發桶,可能誤以為「這節點從沒被審計/CI 碰過」,但真相只是這三源從不記節點,對**任何**節點查詢都會如此——這正是規格自己在「風險類逐類答」段落已經處理過一次的同類問題(anchor-approve 假收斂 0.8 因為量錯量),但這次是同一類「結構偽陽性」換了個角度(零觸發桶而非收斂桶)重新出現,且沒被 r1 三席任何一席點名。

**測試覆蓋確認缺口**:測試策略 #8(`t_gov_stats_node_filter`)描述是「帶位置參數 node + `--stats` → 首行印縮限警示;不帶則無此行」——只釘了警示文字的有無,沒有一案釘「node 過濾後,canary/ci/code-loop/L2 這類 nodes 恆空的來源在零觸發桶裡的措辭/是否該被排除出該桶」。

---

## 發現 3(minor)—— `t_gov_stats_rc`「不帶時輸出與改動前逐字元相同」在本репо沒有可比對的基準產物,字面上不可執行

引句:「不帶時輸出與改動前逐字元相同」

**問題**:全文搜尋確認,本 repo 對 CLI 輸出沒有「快照 diff」型的回歸基礎設施——`governance/golden/` 目錄下的東西是 design-loop spec 快照(`scripts/test_lumos.py:14983-14984` 註解明講「golden/ 是凍結語料…replay 校準用」),不是任何指令 stdout 的凍結副本;既有 gov 相關測試(`t_gov_denoise`/`t_gov_query`/`t_governance_log_write`/`t_gov_adversarial_increment`,`scripts/test_lumos.py:1555,2939,2914,1631` 一帶)全部走「建構固定 fixture → assert 特定子字串/行數存在」,沒有一個是「跑兩次(改動前/改動後)取 diff」的模式。

「改動前」在單一次 TDD 紅燈/綠燈迭代裡沒有明確指涉物——不是某個檔案、不是某個 git ref、也不是某個已存在的 golden fixture。字面上要讓這個測試「真的比較改動前後逐字元」,唯一辦法是實作者在動手前手動跑一次 `lumos gov` 把輸出存成一個新的臨時 golden 檔(規格全文沒交代要不要新建這個檔、放哪裡、要不要進版控),否則這條測試在 CI/未來任何一次重跑時沒有基準可比,只能退化成「靠既有 `t_gov_denoise`/`t_gov_query` 等測試繼續綠燈」這種弱形式的回歸保證——這樣做是合理且可行的,但與規格文字「逐字元相同」字面上要求的強度不對等,屬於敘述比實作能兌現的還強。

---

## 發現 4(minor)—— `--stats` 未提供 `--json`,但本 repo 同類「唯讀彙整/稽核帳」指令幾乎全數支援 `--json`;規格未討論、也未排除未來被腳本消費的可能性

引句:「**八欄**:去重後筆數、原始行數、不同節點數、不同 commit 數、首見日、末見日、收斂指標、分類桶。」

**問題**:`scripts/lumos` 內以 `as_json` 參數支援 `--json` 輸出的指令有四十餘處(`context`/`query`/`spec-trace`/`seat-check`/`anchor-verify`/`lint-check`/`mutate`/`cochange-check`/`delguard-check`…等),是這個 codebase 對「觀測型/唯讀彙整型」子指令的普遍慣例。`gov` 本體目前就沒有 `--json`(現狀,非本規格造成),`--stats` 沿用這個現狀不算破壞既有慣例,也確認過**現在沒有任何 hook/CI/test 以程式方式解析 `lumos gov` 的 stdout**(全 repo 搜尋 `scripts/hooks/`、`.github/`、`scripts/*.py`/`*.sh` 均無命中,僅 `scripts/test_lumos.py` 做子字串斷言)。

但這份設計的核心動機(line 15、line 19)是「給紀律退場這題第一次提供資料」,且 S1 明講統計要served 給人工回顧判讀哪些閘要退場——這正是最典型「今天是人看,明天很可能想餵進另一支腳本/報表」的資料形態(對照 canary 分帳段落已經在做的「per-auditor/per-type 統計」,那段目前也沒有 `--json` 出口)。規格「範圍刀」段沒有明講「不提供 `--json`」是刻意裁定還是遺漏,若日後真有自動化想吃這批統計(例如餵進 `Projects/graph-engineering掃描` 提到的剪枝訊號),屆時得回頭補一輪設計/測試——不是本輪必須擋的問題,但屬於規格未列的隱性技術債,值得在「未決」段一併記一筆。

---

## 審計結論摘要

發現 1 是本輪的核心破口:round 1 的三個 blocker 之一(零觸發桶缺 gate 全集)被規格用「新增 `_KNOWN_GATES` + 掃描 `gov_events.append`」堵上,但這條漂移釘測試描述的掃描目標(`gov_events.append(` 呼叫形狀)在語法位置上覆蓋不到七源裡的六源(僅覆蓋 governance-log 一源的 doctor gate,且 governance-log 內部另兩個字面來源 anchor-approve/code-loop 也漏)。若照文字實作,round 1 已經判定為 blocker 的那個洞會在多數帳源上原樣復發,只是表現形式從「零觸發桶產不出來」變成「這些 gate 直接不出現在報表裡,或漂移偵測形同虛設」——後者更隱蔽、更難事後察覺。發現 2 是同一類「結構性零值」偽裝成「行為性零值」的問題,換了個位置(node 過濾)再出現一次,且沒有測試釘住。發現 3、4 是敘述強度/慣例對齊層級的落差,不影響既有消費者但值得在落地前釐清。

---

**severity 統計:blocker 1 / major 1 / minor 2**
