severity: major

## F1 新來源標記和既有來源指針同名
severity: major
blocking: 是 —— 不改，合法的重建節點會被既有 lint 硬擋，兩道規則無法同時滿足。
引句:「現況類前綴沒寫出程式碼答不了的來源」

1. 輸入：帶 `regen: from-scratch/2026-09-27` 的節點新增摘要行 `FACT: 正式環境旗標已開 [src:部署]`。
2. `note-shape` 會依新規則放行；但既有 Check J 把所有 `[src:值]` 當 repo 檔案指針，會查找名為 `部署` 的路徑。
3. 路徑不存在即成 lint 硬錯；改寫成既有合法的 `[src:scripts/x.py]` 又不在新規則五種值內。`FACT/FLOW/DEP` 在 regen 摘要中沒有合法寫法。

file: `scripts/lumos:4270` — `SRC_REF_RE` 把任意 `[src:…]` 內容解析成路徑。
file: `scripts/lumos:4558` — `check_regen_provenance` 對帶 regen 的摘要生效。
file: `scripts/lumos:4600` — Check J 對每一個 `[src:]` 呼叫 repo 路徑驗證。
file: `scripts/lumos:4605` — 路徑不存在會加入硬錯。
file: `scripts/hooks/pre-commit:103` — 暫存的圖譜筆記在提交前會先跑 `lumos lint`。

## F2 借來的程式檔判定讀錯版本且帶著家用豁免
severity: major
blocking: 是 —— 不改，提交索引中的無副檔名程式及被 home 豁免的正式程式可以繞過行號閘。
引句:「而路徑是 repo 裡的程式檔或測試檔」

1. 輸入：暫存區的 `tools/run` 首行是 shebang，並暫存筆記正文 `排查入口在 tools/run:12`；之後只在工作樹把 `tools/run` 首行改成普通文字，不重新暫存。
2. 提交前照 spec 呼叫 `_is_code_file`，它先讀工作樹現檔，得到「沒有 shebang」並回 false，不會再讀暫存區；該行號引用因而通過，但提交裡的 `tools/run` 實際是程式。
3. 同一 helper 還先套 `node_home.ignore`、`docs/*`、建置目錄等「不要求有家」豁免；這些豁免不代表檔案不是程式，拿來判行號引用會再產生固定漏網。

file: `scripts/lumos:6182` — 函式契約是「需要有家的程式檔」，不是任意 repo 程式檔。
file: `scripts/lumos:6186` — 測試、docs 與建置路徑會在副檔名判定前被排除。
file: `scripts/lumos:6189` — `node_home.ignore` 命中也會直接排除。
file: `scripts/lumos:6198` — 無副檔名檔案優先從工作樹讀取。
file: `scripts/lumos:22184` — 真正的 home check 特別提供 snapshot 模式，避免工作樹與被檢查版本混用。

## F3 新分支範圍漏掉上線點截斷
severity: major
blocking: 是 —— 不改，安裝閘之前的舊筆記會在首次推送時被當成新違規，違反不回頭清舊帳的決策。
引句:「全部已在遠端就不查;最早那個沒有上一個提交」

1. 輸入：消費專案有一條從未推送、建立於安裝 `note-shape` 之前的本機分支，舊提交內已有 `scripts/a.py:10`；今天更新工具並首次推送。
2. spec 的起點是最早未在遠端提交的上一個，因此整段舊本機歷史都進 `note-shape --diff`，舊行被當新增而擋。
3. 被借用的 home gate 並不只算這個起點；它還把起點截到「該閘第一次上線的提交」。本 spec 沒定義自己的上線標記、截斷或對應測試。

file: `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:33` — d2 明定舊筆記不回頭清。
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:31` — 被借用的閘明載起點早於上線點時要截斷。
file: `scripts/lumos:22864` — `_nodehome_clamp_base` 實作上線點截斷。
file: `scripts/lumos:23291` — `home check --diff` 實際呼叫該截斷。

## F4 釘版本放行沒有排除會移動的 Git ref
severity: major
blocking: 是 —— 不改，行號引用只要加上會移動的 ref 就能放行，仍會隨後續提交漂移。
引句:「指的是某一次提交的那一行,不會漂」

1. 輸入：新增 `WHY: 細節見 scripts/lumos@HEAD:3218`。
2. `HEAD` 在檢查當下能解析成 commit，但下一次提交後指向不同版本；`main`、tag 被重打時也有相同行為。
3. spec 沒定義 `<提交>` 必須是不可變物件 ID、最短長度、必須存在及路徑在該提交內存在；S1 也沒有 symbolic ref、假 SHA、懸空路徑的反例。照現有 commit 驗證 helper 實作，`HEAD` 會被判合法。

file: `scripts/lumos:4537` — 現有 `_git_commit_exists` 的參數雖名為 sha，實際接受任意 Git revision。
file: `scripts/lumos:4541` — 驗證命令是 `git cat-file -e <值>^{commit}`，`HEAD` 與分支名都會通過。

## F5 治理帳仍有多個寫入者繞過新鎖
severity: major
blocking: 是 —— 不改，設計宣稱已消除的交錯壞行仍能由 doctor、anchor、delguard 或 dispositions 與新寫入者共同產生。
引句:「改成兩者寫入時拿同一把治理帳檔案鎖」

1. 併發輸入：行程 A 執行 `note-shape`，經上鎖後的 `_gate_event` 寫帳；行程 B 同時執行 `doctor --ci`，經 `_append_governance_log` 寫同一檔。
2. spec 只點名 `_gate_event` 與 `_codeloop_gov_log` 上鎖；行程 B 不拿該鎖，互斥不成立。
3. code-loop dispositions 還有另一個直接 append 寫入點。回退段宣稱共用鎖會保護舊寫入者，照字面實作後並不成立。

file: `scripts/lumos:951` — `_append_governance_log` 是 doctor、anchor、spec-gate、delguard 等共用寫入器。
file: `scripts/lumos:969` — 該寫入器直接 append，沒有鎖。
file: `scripts/lumos:29614` — dispositions 有獨立治理帳寫入器。
file: `scripts/lumos:29628` — dispositions 同樣直接 append 同一個 `.governance-log.jsonl`。

## F6 鎖逾時的 rc 會被既有 hook 當成放行
severity: major
blocking: 是 —— 不改，鎖競爭時畫面雖印擋下，提交或推送仍會繼續。
引句:「回傳碼照鄰居:0 過、1 擋、2 參數錯」

1. 讓另一行程持有治理帳鎖直到 `note-shape` 逾時。
2. spec 另規定鎖逾時回 2；但它又要求沿用鄰居 rc 協議，而現有 home hook 明確只對 rc1 `exit 1`，其他非零都放行。
3. 因此 rc2 同時被定義成「參數錯」與「執行期鎖逾時」，hook 沒有可依循的阻擋判準。S7 只測 CLI 回 2，沒有測真正經 pre-commit、pre-push 是否仍擋。

file: `scripts/hooks/pre-commit:121` — home hook 註明只有 rc1 擋，其他非零放行。
file: `scripts/hooks/pre-commit:125` — 實作只檢查 `nh_rc == 1`。
file: `scripts/hooks/pre-push:218` — 推送前同樣定義 rc1 擋、其他非零放行。
file: `scripts/hooks/pre-push:237` — 推送前實作也只攔 rc1。
file: `scripts/lumos:871` — `_gate_event` 現有契約還明定寫帳失敗不得改變閘的判定，與逾時 rc2 要求衝突。

## F7 code-loop 鎖失敗前已留下可放行的 marker
severity: major
blocking: 是 —— 不改，命令回報治理帳失敗後，本機仍會把審查視為通過，乾淨 CI 卻判未通過。
引句:「這是第一層自己要寫事件、也是第二層將來要寫通過紀錄的前提」

1. 持有治理帳鎖超過期限，再執行 `lumos code-loop pass`。
2. 現行順序先寫 `governance/code-loop/<branch>.json` marker，才呼叫 `_codeloop_gov_log`；替後者加鎖並在逾時回 2，不會撤回已寫 marker。
3. 隨後本機 `code-loop check` 優先讀 marker 而放行；乾淨 CI 沒有這個被忽略的 marker，也沒有治理帳事件，因而轉紅。spec 沒要求先取鎖、調整寫入順序或失敗時回滾 marker。

file: `scripts/lumos:30325` — pass/skip 進入留痕分支。
file: `scripts/lumos:30327` — marker 先寫。
file: `scripts/lumos:30328` — 治理帳後寫。
file: `scripts/lumos:28678` — check 的留痕讀取入口。
file: `scripts/lumos:28683` — marker 存在時不會退回治理帳。

## F8 開關與跳過事件可以只留在未暫存工作樹
severity: major
blocking: 是 —— 不改，作者能關掉閘後提交、推送，再丟棄設定與帳目，歷史中看不到任何跳過紀錄。
引句:「有開關與跳過且都寫帳」

1. 已提交設定維持 `note_shape.gate=block`；只在工作樹改成 `off`，不暫存，接著暫存違規筆記並提交。
2. 若照宣稱借用的 `lint_new.gate` 形狀，設定從工作樹讀到 off；`_gate_event` 也只把 skipped 事件 append 到工作樹的治理帳。pre-commit 啟動時索引已固定，兩者都不會進這次提交。
3. 推送時保持 off，再把未暫存設定與治理帳丟棄；在未接 CI 的消費專案，遠端同時沒有違規攔截、關閘設定或 skip 帳。RETIRE-IF 的繞過次數也因此量不到。
4. 被借用的 home gate 已有正確先例：提交前讀索引、推送前讀終點提交，未暫存的 off 關不掉它；spec 沒指定 note-shape 採這個必要語意。

file: `scripts/lumos:21095` — `lint_new` 設定入口。
file: `scripts/lumos:21103` — `lint_new.gate` 直接讀工作樹 `.lumos/config.json`。
file: `scripts/lumos:928` — `_gate_event` 直接寫工作樹的治理帳。
file: `scripts/lumos:22184` — node-home 設定提供 snapshot 模式。
file: `scripts/lumos:22187` — 該模式明定未暫存的關閉設定不得影響被檢查版本。

## F9 新分支含自動合併時會重查遠端已有的行
severity: major
blocking: 是 —— 不改，純粹合併遠端既有內容也會被當成本次新寫，造成穩定誤擋。
引句:「改名用 git 的改名偵測認成同一篇,只算真正變動的行」

1. `origin/main` 沒有某行；`origin/topic` 已有一個上線前的 `scripts/a.py:10` 筆記行。從 main 建本機分支並合併 `origin/topic`，產生唯一未在任何遠端的 merge commit M，沒有人工修改該筆記。
2. 新分支算法選 M 為最早未在遠端提交，再取 `M^`；普通 endpoint diff 會把第二個 parent 帶入的既有行列為相對第一個 parent 的新增行，`note-shape` 因而阻擋。
3. 這同時違反「遠端已有就不查」與 d2 舊帳不追。被借用的 home gate 已為自動合併另外實作「合併自己真正新增的行」判定，本 spec 的共用行集合沒有承接，也沒有 merge 測試格。

file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:18` — 指定節點記載自動合併內容被誤判為合併自己寫入的既有事故。
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:27` — 推送前 home 判定逐提交處理，合併只算合併本身多改的內容。
file: `scripts/lumos:22676` — `_nodehome_merge_own_changes` 是現有合併專用判定。
file: `scripts/lumos:22679` — 註解具體說明逐 parent 比較會誤判自動合併內容。

〈前言與拆分依據〉已讀,無 finding。

〈消費專案的 CI〉已讀,無 finding。

〈誠實界線〉已讀,無 finding。

〈指定節點逐篇核對〉

- `Systems/每支檔有家`：F2 破壞提交索引／目標提交快照語意；F3 漏掉上線點截斷；F9 漏掉它已用事故修出的合併判定。
- `Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋`：F1 使 d3 的合法出口在 regen 節點不可用；F3 違反 d2 舊帳不追；F8 使 d5 的機械擋與跳過統計可無痕繞過。
- `Projects/筆記不存程式碼推得出的事_計劃`：F5 不符合該篇宣稱的所有治理帳寫入者共用鎖；F6、F7 使鎖逾時與 code-loop 留痕產生假放行；其第一層移出後仍引用的共用範圍也受 F3、F9 影響。

〈實務隱患〉

- 守衛準確性：有。F1、F3、F9 會擋合法或舊內容；F2、F4 會放過應擋內容。
- Git 拓撲與版本快照：有。F2 混用工作樹與索引，F3 漏上線截斷，F9 漏合併 parent 語意。
- 資源併發：有。F5 只鎖兩個入口，其他同檔寫入者仍繞過；F7 還會留下半套狀態。
- 可用性：有。F1 讓部分 regen 節點沒有合法表示法；F6 的逾時結果在 CLI 與 hook 間相反。
- 審計與可繞過性：有。F5 仍會產生壞帳，F7 產生本機／CI 分歧，F8 讓 off/skip 帳可被丟棄。
- 對外送出：無；本層只讀本機 Git 與檔案，不呼叫外部模型或服務。
- 不可逆：無；筆記內容不由 hook 改寫，治理帳與設定均可由版本控制回退。
- 金流：無；沒有付款、額度扣款或計費路徑。

總結:最嚴重 severity 是 major、blocking 共 9 條。