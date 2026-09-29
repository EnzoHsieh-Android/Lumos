severity: major

## F1 形狀過濾讓常見 Python 函式永久隱形
severity: major
blocking: 是
引句:「形狀過濾:定義名要 4 個字以上、而且含底線或大小寫混合」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:279`
file: `scripts/lumos:626`

1. `resolve`、`find`、`main`、`read`、`load`、`check` 這類單一小寫字函式即使被刪除，也會在掃筆記前被 `_shape_ok` 排除；家筆記或摘要裡的現況句不會警告、不會記帳。
2. 唯讀 AST 盤點顯示 `scripts/lumos` 的 1185 個函式／類別中有 43 個（3.6%）被此規則排除；連同測試檔則是 3076 個中的 311 個（10.1%）。這不是只排除短暫區域變數。
3. [S1] 的文字仍宣稱處理「定義名」，卻沒有測試上述普通函式名；照字面實作會形成看似涵蓋所有 Python 定義、實際固定漏掉一類名稱的守衛。
4. 兩週帳也量不到這些漏報，因為它們根本不會成為 finding。實作前應取消此過濾，或明確縮小產品承諾並建立獨立 recall 驗收。
5. 隔離 clone 未能重現：唯讀沙盒執行 `mktemp` 回 `Operation not permitted`；上述結論來自凍結演算法與現庫 AST 的唯讀量測。

## F2 歷史字眼會把仍在描述現況的舊句一起豁免
severity: major
blocking: 是
引句:「被放過的句子不記帳,兩週帳量不到漏報」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:263`
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:401`

1. 判定只問名稱所在句子是否含「沒有、刪、撤、不帶」等子字串，不判該字眼是否真的在描述候選名稱的歷史。
2. 例如現況句「沒有參數時呼叫 `old_handler`」或「刪除快取後呼叫 `old_handler`」；`old_handler` 被刪除後，整句分別因「沒有」與「刪除」被跳過。兩句都是真舊句。
3. P3r→P4r 的主要降噪就是把要處理筆數從 73 壓到 16，但正例只有同一份 9 題考卷；目前沒有量過被壓掉的 57 筆中有多少是真舊句。
4. 計劃只準備在 REVISIT 當天關閉過濾抽一個 rtb 大提交，沒有 recall 門檻，也不會涵蓋兩週間其他提交。即使這個抽樣發現大量漏報，現有「準度 ≥60%」仍只量已列出項目的 precision。
5. 實作前應把歷史判定綁到候選名稱的語法關係，或至少將關閉過濾的影子結果一併記帳並設定 recall 門檻。

## F3 治理帳沒有記下產生 finding 的精確版本
severity: major
blocking: 是
引句:「每次 drift check 有跑 `m1` 就記一筆」
file: `scripts/lumos:1179`
file: `scripts/lumos:1194`
file: `scripts/lumos:1214`
file: `scripts/lumos:28294`

1. spec 的事件只保存計數及前 30 筆「路徑、行號、名稱」，沒有 base SHA、tip SHA、ref 或當時原文。
2. `_gate_event` 沒收到 `head_sha` 時會另跑 `git rev-parse HEAD`；現有 drift-check 呼叫也沒有傳被檢查的 tip。多 ref 推送或顯式 `--diff A..B` 時，帳上的 commit 可以是另一個 checkout 的 HEAD。
3. 兩週後行號與原文已可能改動；沒有 tip 就不能還原事件當時的筆記，也無法判斷每筆是真舊句還是誤報。前 30 筆與 2000 字截斷又使高噪音事件無法逐筆抽判。
4. 因此 RETIRE-IF 所需的「每筆真假」沒有可稽核資料來源。事件至少要帶完整 base/tip SHA、ref、原文或可重算 finding 的輸入指紋，才能用來決定轉 block。
5. 功能尚未實作，且唯讀沙盒無法建立指定 shared clone；此項由既有寫帳路徑與凍結資料格式靜態重現。

## F4 校準期會略過最慢的推送，轉 block 後卻專門擋它們
severity: major
blocking: 是
引句:「`m1` 用 drift check 同一個截止時間」
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:23`
file: `scripts/lumos:28260`

1. `m1` 排在既有 c1–c5/probe 之後並共用同一截止時間；前段耗盡預算時，warn 階段只記 incomplete，不產生可判真假的 finding。
2. 圖譜已有新分支首推前段耗到 67 秒、超過 60 秒預算的實測。這類大範圍推送正是舊句數量最多、最需要校準的樣本，卻被系統性排除。
3. RETIRE-IF 只看已列出的準度與單次筆數，沒有完成率門檻；小推送達到 60% 就能轉 block，即使所有大推送都沒跑完。
4. 轉 block 後，同一批從未校準成功的推送會因「時間到」直接回 1，即使實際有零筆舊句。這會把量不到的效能問題轉成使用者誤擋。
5. 實作前應給 `m1` 獨立預算，並要求校準期完成率／最近連續完整執行達標；未完成的輸入族群不得轉 block。

## F5 提示中的名稱只做終端消毒，不能安全貼進 shell
severity: major
blocking: 是
引句:「名稱與路徑先過 `_esc_clean`」
file: `scripts/lumos:9765`
file: `scripts/lumos:27630`
file: `scripts/lumos:27642`

1. `_esc_clean` 只替換控制字元及截長，不會 shell quoting；空白、分號、`$()`、反引號仍原樣保留。
2. `m1` 名稱集合包含被刪或改名的 Python 舊路徑。合法檔名可含上述字元；若提示直接產生 `--name src/x;...py`，使用者照貼就會切參數或執行額外命令。
3. 現有 `_drift_sh` 的註解明載同型事故，且 `_drift_fix_hint` 已用它處理節點路徑。spec 卻只要求新名稱經 `_esc_clean`，漏掉相同的 shell 邊界。
4. 實作條款應要求每個 `--name` 先經 `_drift_sh` 或等價的參數引用，`_esc_clean` 只能用於顯示，不能當 shell 安全措施。
5. 功能尚未實作，且唯讀沙盒無法建立 clone；未能動態重現，靜態資料流已可確定不安全。

## F6 剖不動時的文字退路漏認合法的帶型別指派
severity: major
blocking: 是
引句:「終點版有剖不動的檔時,候選名稱再用文字比一次」
file: `scripts/lumos:26809`
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:200`

1. 正常 AST 路徑把 `name: Type = value` 視為定義；spec 的文字退路只找 `名 =`，不會命中冒號介於名稱與等號之間的合法 `AnnAssign`。
2. 具體輸入：A 檔刪除 `old_name`；終點另一支 Python 檔仍有 `old_name: Callable = handler`，但該檔因別處語法錯誤剖不動。文字退路找不到 `old_name =`，遂把名稱判成全 repo 消失。
3. 若家筆記或摘要提到 `old_name`，block 模式會誤擋使用者。反方向上，註解或字串裡出現 `def old_name` 又會被當成仍存在而漏報。
4. [S1] 只寫「文字比對仍找得到」，沒有釘住正常 AST 與 fallback 的定義形狀等價。應重用既有定義正則／tokenizer，並用 AnnAssign、註解、字串、async def、類別層指派逐項驗收。
5. 功能尚未實作，且唯讀沙盒無法建立 clone；未能動態重現，兩條判定分支的語法差異可由現碼直接確認。

## 已讀、無 finding 的部分

- 核心 A：判定另開函式、不進 `_drift_check_core`，可避免改動既有 exam/history 噪音基準。
- 核心 B：兩個開關的控制流已能表達 `gate=off` 與 `old_sentence` 獨立行為。
- 核心 C：一行一筆帶名稱集合、表態需完整涵蓋集合，語意一致。
- 核心 D：warn/block 的回傳語意本身清楚；問題是轉 block 的校準閘，見 F4。
- 核心 E：三類消失判準已分開；剖不動 fallback 的定義形狀仍有 F6。
- 核心 F：P4r2 字眼與參考實作一致；判法本身的 recall 洞見 F2。
- 回退：程式、設定、種類與快取都有可撤路徑；治理帳與表態保留不會改變舊版判定。
- 合約候選、審計修正紀錄：已讀，無新增 finding。

## 合約核對

- `Systems/存量漂移守衛` 沒有正式 ★INVARIANT★；兩條 RULE 已核對。頂端設定讀法不受影響；逾時 fail-closed 的新誤擋落在 F4。
- `Systems/guard-kill` 的兩條合約（rc 優先序、JSON stdout 純度）不受影響：本設計不進 guard-kill 執行路徑。
- `Systems/lumos-cli-write` 目前沒有登記正式合約。
- `Systems/canary-audit`、`Systems/design-loop`、`Systems/lumos-cli-lifecycle`、`Systems/lumos-cli-read` 的合約均不受影響：沒有改其記帳、處置閘、注入或搜尋路徑。
- slim install/uninstall 的 13 條合約不受影響：本案不觸及安裝與卸載程式。
- `Systems/節點範圍與索引守衛` 的九條合約逐項核對：既有抽取重用、索引範圍、缺索引出聲、合約數門檻、doctor 段落順序、閘名登記、懸空單源、bool 防呆、治理帳接線均未被 m1 修改；spec 也明定 doctor 排除 m1。

## 實務隱患逐類判定

- 不可逆：無；程式變更可由 git 回退，快取可刪，治理帳為追加紀錄。
- 金流：無；不處理金額、付款或帳務。
- 對外送出：無；不呼叫外部服務。
- 守衛面：有；F1、F2 造成假陰性，F3 讓校準不可稽核，F4 造成 block 假陽性，F6 使 fallback 判定不等價。
- 效能：有；F4 的共享截止時間直接改變 warn/block 結果。
- 併發：無 blocking finding；快取最後寫入者覆蓋只會少命中快取，正確性仍可重算。
- 資安：有；F5 的可照貼提示缺 shell quoting。
- Python 通用慣例：快取有 20000 筆上限、檔案寫入有原子替換、沒有 async／外呼／秘密／金額路徑；除 F5、F6 外無新增 finding。

最高等級:major;blocking 共 6 條