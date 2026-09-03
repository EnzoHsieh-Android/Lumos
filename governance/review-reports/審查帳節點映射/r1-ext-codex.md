# r1 外家否決席報告(Codex,前景)

---

1. `finding-nodes` 的帳形狀無法支撐「被幾席抓到」：現行 disposal 一輪只准一筆帶 `findings_set`，其他席只有報告留痕；但 spec 又要求 `finding-nodes.id ⊆ findings_set`。結果其他席不能合法記自己的 finding→node 映射，單一彙總 carrier 也沒有「哪一席抓到哪條」資訊，無法重算 capture count。若讓每席都帶 `findings_set`，讀側會直接 rc2。  
severity: blocker  
blocking: 是＋現行帳 schema 無法表達演算法所需的逐席 incidence matrix，核心功能不可實作。  
引句:「多席報告的 finding 若帶相同 `finding-nodes`,視為同一相異缺陷」  
file: `scripts/lumos:4153`  
file: `scripts/lumos:11550`

2. `--finding-nodes <id=節點[,節點],…>` 沒有可判定的 CLI 文法，也沒有照抄既有慣例。既有逐 finding 欄位是 `action="append"`，每次只解析一個 `id=value`；本案卻同時用逗號分隔「同 finding 的多節點」和「下一個 finding」。例如 `F1=A,B,F2=C` 必須另創 look-ahead 文法，`F1=,F2=C` 又無法區分明示空值與漏值。空值還與既有 `if finding_kinds:` 的「空即不寫」慣例不同。應改成可重複旗標並採不衝突的多值表示。  
severity: blocker  
blocking: 是＋公開 CLI 的輸入語法尚未形成無歧義合約，無法寫穩定 parser 與相容測試。  
引句:「`--finding-nodes <id=節點[,節點],…>`:每個 finding 對應到哪些節點」  
file: `scripts/lumos:4173`  
file: `scripts/lumos:4194`  
file: `scripts/lumos:17135`

3. 「交集非空」不是等價關係，不能直接當去重鍵；spec 不只漏選寬或嚴，還漏了傳遞性裁定。真實 `bound-tests-gate/r1` 中，s1-F1 與 s2-F3 都指出 `resolve_test_refs` 漏接，可合理分別標 `{check-t-sentinel, lumos-cli-read}` 與 `{check-t-sentinel}`；相等判準會錯拆。另一方面 s1-F6 是不同缺陷，若標 `{lumos-cli-read}`，交集判準會透過第一條形成 A∩B、A∩C，可能把三條連成一群，即使 B∩C 為空。必須先定義 canonical defect key、是否做連通分量、以及 bridge case。  
severity: blocker  
blocking: 是＋核心輸出會因遍歷／聚類策略不同而產生不同 `capture_counts`、D1、D2。  
引句:「自動歸併的判準是「finding-nodes 交集非空」還是「相等」」  
file: `governance/review-reports/bound-tests-gate/r1-s1.md:2`  
file: `governance/review-reports/bound-tests-gate/r1-s1.md:7`  
file: `governance/review-reports/bound-tests-gate/r1-s2.md:4`

4. 把「節點集合相同」當「同一缺陷」本身資訊量不足。同一節點可同時有多個互不相同的缺陷；真實同輪 s2-F1、F2、F3 都可能歸到同一合約測試節點，但分別是零測試假綠、跨平台去重漏跑、平台前綴解析漏接。只用 node set 會將三個 distinct findings 合成一個。既有 capture-counts 的 key 慣例明確是 `file:line` 或 `section:nature`，節點只能作座標，不能取代「瑕疵性質」指紋。  
severity: blocker  
blocking: 是＋歸併鍵會系統性少算相異缺陷，直接污染本案主要產物。  
引句:「finding 若帶相同 `finding-nodes`,視為同一相異缺陷」  
file: `scripts/lumos:4431`  
file: `scripts/lumos:4835`  
file: `governance/review-reports/bound-tests-gate/r1-s2.md:2`

5. 「可多、可空」與 D1 定義衝突：空集合依公式必然與 expected-nodes 交集為空，因此「尚未映射／不知道歸屬」會被算成「確定是清單外發現」。這會把缺資料冒充 D1 訊號；同時 spec 沒定義 expected-nodes 缺席、空集合、部分席缺欄、不同席 expected-nodes 不一致時 D1/D2 的分母與輸出狀態。這些應 fail-closed 或輸出 unknown，而非計數。  
severity: major  
blocking: 是＋D1/D2 在合法輸入上即可產生語意錯誤，不能作預註冊指標。  
引句:「D1 清單外發現數(finding-nodes ∩ expected-nodes = ∅ 者)」  
file: `governance/eval/seat-coverage/recount.py:25`  
file: `governance/eval/seat-coverage/recount.py:59`

6. 新鍵本身不會污染 G3、replay 或現有 gov 彙整，但 spec 沒把這個邊界釘成測試。G3 只讀 hash 欄與處置集合；gov 的相關彙整顯式挑既有鍵，會忽略未知鍵；replay 則凍結整行原文，因此新增鍵會自然進入新 golden，舊 golden 對 live 帳仍以原始行 hash 比對。真正風險是實作者為消費新鍵而誤改 `_loop_status_disposal` 或 replay engine revision，spec 目前只說「不動閘」，沒有列必須保持不變的 rc／輸出回歸。  
severity: major  
blocking: 否＋現況讀端對未知鍵安全，但落地前應補 G3、replay、gov 三組相容測試。  
引句:「兩欄全部選配、不給即今日行為(相容鐵則)」  
file: `scripts/lumos:4884`  
file: `scripts/lumos:550`  
file: `scripts/lumos:3531`  
file: `governance/autonomous_loop/cross_audit.py:64`

7. canary-audit 的兩條 INVARIANT 在合理實作下可保持，但 spec 沒明文要求沿用共同 readback 原語，也沒測 `second` 不攜帶／不消費新欄。`record` 必須仍經 `_jsonl_append_verified` 才能宣稱成功；`second` 是獨立寫入路徑，不能因 capture-counts 掃帳而被誤認成席資料。尤其自動路徑若只按 loop/round 分組、不排除 `kind=second`，可能把 telemetry 列混入席數。  
severity: major  
blocking: 否＋不是必然破壞，但缺少兩條既有硬合約的回歸設計。  
引句:「寫入端驗證 fail-closed;不動任何閘的判定邏輯」  
file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md:29`  
file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md:31`  
file: `scripts/lumos:4336`  
file: `scripts/lumos:4419`

8. 本案沒有消除「靠人填」，只是把人工作業從一個整數陣列換成更昂貴的逐 finding 分類；而且仍是選配。寫入驗證只能驗 node 存在及 id 存在，不能驗映射正確，也不能防止整個旗標被漏掉。更小且較機械的方案是：記帳時由已強制存在的 `report_path` 解析每條 finding 的 `file:line`，再用既有 impact/backlink 能力產生候選節點；派工端把 expected-nodes 直接寫入模板；只有無 file 證據或多義映射才要求人工 override。真實席報告已普遍帶程式行號，具備這條資料鏈。  
severity: major  
blocking: 是＋提案宣稱「不靠人填」但資料來源仍完全依賴編排者，與已實證失敗模式同構。  
引句:「仍是編排者在記帳時填——這是判斷不是機械」  
file: `scripts/lumos:4259`  
file: `scripts/lumos:4264`  
file: `governance/review-reports/bound-tests-gate/r1-s1.md:2`

9. 目前兩個母案都已停，本案沒有已承諾的在線消費者；`recount.py` 只是離線量測腳本，capture-recapture 也已明文降為 advisory。spec 的回頭條件是「若未開工才判斷是否無人需要」，方向倒置：應先要求至少一個母案重開並承諾讀取新欄，再建 schema；否則正是在製造 canary-audit d5 所淘汰的「無下游消費之 telemetry」。  
severity: major  
blocking: 是＋在沒有消費者的狀態下，基建無法證明效益，且會新增永久 schema 與維護面。  
引句:「回頭判是不是兩份母案都停了所以沒人要這塊基建」  
file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md:76`  
file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md:79`  
file: `governance/eval/seat-coverage/recount.py:5`

最嚴重 severity: blocker、blocking 7 條。
tokens used
75,784