severity: major

### F1 [S2]的「已經是候選」判定沒把參考道(lane)算進去,家會跟lane重複出現同一篇
severity: major
blocking: 是 — 不改,實作者最自然的寫法是沿用現有 `_impact_mark_about` 只掃 `results` 的模式,會讓同一篇節點同時以「必推:家」和「守衛面參考」兩種身分出現,直接違反[S2]自己在「合約候選」段宣告的「每篇只出現一次」。
引句:「已經是候選(事故、直接、間接)的,原項加上」
1. `results` 只收 pinned/free 候選;硬合約保送以外的 RISK·* 間接候選(hop≤1)會被分流進獨立容器 `lane_raw`、自始不進 `results`,[S2]描述的「已是候選/新增一項」二分法完全沒提到這個第三個容器。
2. 若家標記邏輯照 `_impact_mark_about` 現有位置實作(只查 `results`),lane 裡的節點會被誤判成「還不是候選」,依[S2]字面新增一筆分數 0、pinned:true 的「家」項,而它同時仍留在 `lane` 輸出裡。
3. 這不是假設情境:實跑本 repo 現況,`scripts/hooks/pre-commit`(3 個家,不觸發[S4]大檔排除)的家 `Systems/delguard.md` 目前就落在 `lane`(score 0.24, RISK·守衛面, hop1, 不在 results),照 [S2] 字面實作會在必推名單與參考道各出現一次。

file: `scripts/lumos:21623` lane_raw「獨立容器…自始不進 results」的設計註解
file: `scripts/lumos:21640` RISK·* 且 hop≤1 的間接候選改寫進 `lane_raw.append`、不進 `results`
file: `scripts/lumos:21657` 現有 `_impact_mark_about(env, results, rel_file)` 只傳 `results`,不含 lane
file: `docs/lumos-toolchain-knowledge/Systems/delguard.md:34` about_code 列了 `scripts/hooks/pre-commit`(即上述實測用的家)

### F2 [S6]只講「計劃模式把家收進固定席」,沒把[S3]的排序規則接進 dispatch-lens spec 模式自己的 `_rank`,家會被排到 cap 之後只列名
severity: major
blocking: 是 — 不改,實作者依原樣把「家」塞進 `pinned` dict、不動 `_rank`,家項會落進 `_rank` 的 else 分支(rank 3)排最後;派審查員時原本最想被看到的「這支檔的家」反而最容易被 cap 砍到只剩篇名。
引句:「計劃模式把家收進固定席,照舊受每檔篇數上限」
1. [S6]對 `--diff` 聚合明講「必推名單照[S3]的順序排(事故、家、其餘照分數)」,但對 spec 模式只說「收進固定席,照舊受每檔篇數上限」,完全沒提排序要不要也照[S3]——這是[S6]三條路徑裡唯一沒有明講排序規則的一條。
2. `cmd_dispatch_lens_spec` 自己的 `_rank(v)` 目前只認 incident(0)/有 contract(1)/direct(2),其餘一律 3;家若沿用既有 `kind` 標記機制加進 `pinned` 卻不改這支函式,會被歸進「3」,排在所有既有固定席之後。
3. `_lens_render_listed` 對超出 `cap`(預設 8)的項目只印篇名、不印合約行與 INVARIANT 小計——這份計劃本身用的鏡頭(r2-lens.txt)目前已有 16 篇進 `pinned`(5 事故+11 超出上限只列名),cap 早已吃緊,家若沒有排序保證,幾乎必然落進「只列名」區。

file: `scripts/lumos:23135` `pinned.setdefault(node, {"kind": _LENS_KIND.get(kind), ...})` 目前只收 direct/incident/indirect 三種 kind
file: `scripts/lumos:23138` `_rank(v)`:incident=0、有 contract=1、direct=2,其餘一律 3(沒有「家」的分支)
file: `governance/review-reports/推筆記認家/r2-lens.txt:18-30` 這次審查自己的鏡頭已列 11 篇「超出上限,只列名」

### F3 [S16]的字串預篩沒交代 hook 收到的檔路徑要先轉成 repo-relative 才能比對,現況 hook 完全沒有這個轉換工具
severity: major
blocking: 是 — 不改,實作者若直接拿 hook 收到的路徑去比對節點原文(about_code 存的是 repo-relative 路徑),而 Claude/Codex 傳給 hook 的路徑在既有程式碼裡明確是絕對路徑,字串預篩會系統性 0 命中,整條[S16]規則等於沒做,而且不會報錯、無從察覺。
引句:「hook 先做字串預篩(Systems 節點原文裡有沒有這個路徑),有才叫 lumos,由家對照表做最終判定」
1. `impact-hook.py` 全檔沒有任何 relpath/repo_root 轉換函式(只有 `_shebang_is_code` 做相反方向的 相對→絕對);現有流程把 hook 收到的 `file_path` 原樣轉送給 `lumos impact --file <path> --repo <repo>`,絕對→相對的轉換只發生在 `cmd_impact` 內部(lumos 子行程裡),不在 hook 這一層。
2. `cmd_impact` 之所以要在自己內部做 `os.path.isabs(rel_file) ...os.path.relpath(...)`,正說明真實呼叫傳進來的路徑本來就常是絕對路徑;[S16]要求的字串預篩卻明講是 hook 自己做、在叫 lumos 之前,這個轉換步驟在 hook 端完全沒有對應機制。
3. 家對照表存的 about_code 是 repo-relative 路徑(如 `scripts/lumos`),對絕對路徑(如 `/Users/xyz/.../scripts/lumos`)做子字串包含測試本身不會斷(相對路徑是絕對路徑的子字串),但若 hook 端另外把路徑做過標準化/截斷處理不一致,或專案不是從 repo 根目錄呼叫,仍可能落空——spec 完全沒交代這一步驟該怎麼做、由誰做。

file: `scripts/hooks/claude/impact-hook.py:120` `_shebang_is_code` 是唯一的路徑轉換工具,方向是相對→絕對,不是預篩要的絕對→相對
file: `scripts/lumos:21518` `rel_file = str(file)` 起、內部才做 `os.path.isabs(...)` 轉相對路徑,證明真實輸入常是絕對路徑
file: `scripts/hooks/claude/impact-hook.py:794` `_impact_for_file` 把 `file_path` 原樣送進 `lumos impact --file`,沒有先轉相對路徑

## 逐節讀完的其餘部分

- **為什麼(這批的來源)**:已核對舊計劃 `Projects/固定席扇出降權_計劃.md` d4「丙(第四條保送)需先把 about 漏標率壓到零,無新證據不重提」與其 r1/r2 被打穿的機制(有欄但不含目標檔→降自由席,把 2/9、3/5 的必看主動踢出固定席)——本案[S2]「只加不降」結構上不可能重現「降級傷害」這個機制,改寫後的依據站得住;殘餘風險(家填錯、單次量測)已用[S14][S15]加 REVISIT 承接,不算未處理。無 finding。
- **名詞**:「家」「家對照表」「必推名單」「大檔」定義已用 `_nodehome_homes` 實跑核對(scripts/lumos 31 個家,與舊 `_impact_about_counts` 算出的 65 個確實不同),與名詞段文字一致。無 finding。
- **核心裁定甲 [S1][S3][S4][S5][S7][S8][S9][S10][S14][S15]**:[S1] 現有 `_nodehome_homes` 確實只吃 `_NodehomeSide`(git 快照)、推筆記走 `env.notes`(工作目錄圖譜),兩套資料結構不同,抽出純函式的前提屬實。[S3] 三層排序(事故>家>其餘)、[S7][S8][S9] 旋鈕開關互斥(旋鈕關時家整段不跑、about-hit 整段不跑)彼此邏輯自洽,無矛盾。[S4] 邊界值 8 目前圖譜裡沒有檔案卡在 7/8 交界,不影響現況。[S10] 沿用既有 `--ablation`(擋未標新候選)機制已存在,不是向壁虛造。[S9] 提到的 `about-code restamp/revert/migrate-stamp` 三個子指令均已存在。無新 finding(家與 lane、家與 dispatch-lens 排序的落差見 F1/F2)。
- **核心裁定乙 [S11][S12][S13][S17]**:已用 `scripts/lumos:4368`(lint 認任何非空 regen)、`scripts/hooks/pre-commit`(暫存節點逐篇 lint)核對過「掛進每支檔有家新違規、不動 Check J」的落地路徑與 r1-intake 的機械重現一致。`node_home.gate` 開關已存在。無 finding。
- **範圍外 / 落點**:已讀,落點三篇([[Systems/retrieval-ranking]]/[[Systems/每支檔有家]]/[[Systems/節點還原]])均存在。無 finding。
- **實務隱患**:六類(噪音、寫錯的家、評測尺量不到、效能、舊專案、兩家一致)逐條已自陳並附機制或 REVISIT,查無牴觸既有事實;「回滾」段見固定席逐條判。無 finding。
- **驗收怎麼跑**:已逐一核對 19 個 `[test:]` 標籤與 14 個 `-k` 關鍵字(含改寫用的 `impact_about_hit`),全部子字串可對到;`t_impact_about_hit` 確實存在(scripts/test_lumos.py:889)且斷言⑨就在其中。無 finding。
- **回頭條件 / 合約候選**:四條 REVISIT 都有日期與可執行的重驗動作;合約候選四條與 F1/F2 揭露的落差有關,收斂時建議一併複核。無 finding(獨立於 F1/F2 之外沒有新問題)。
- **審計修正紀錄**:與 r1-intake.md 的 G1–G18 逐條對照過,去重分組與處置描述一致,machine-reproduced 表格全 HIT。無 finding。

## 固定席逐條判

- `Systems/retrieval-ranking`:會被本案直接改動——這正是落點段指名要更新的節點,現有 KEY 行是描述現況的敘述,沒有鎖死排序公式的 ★INVARIANT★/★IRREVERSIBLE★ 合約行,[S18]也已把它相關的驗證紀錄排進要標 stale 的清單,屬於預期中的落點而非破壞。
- `Systems/每支檔有家`:不影響——about_code 定義、比對鍵(`_nodehome_key`)、三個既有進入點(提交前/推送前/健檢)本身不變;[S1]只是把既有算法抽出給推筆記多一個讀法共用,沒有改「每支檔有家」自己判定用的輸入輸出。
- `Systems/節點還原`:不影響——`about_code: []`,是主題型節點;[S11][S12][S13]明文允許這種「不管檔」的節點只要寫負責範圍就放行,不會反過來要求這篇自己補 about_code。
- `Issues/canary-record未落盤事件`、`code-loop守衛main-direct盲區`、`hook卸載殘留註冊`、`init-force-slug誤用basename`、`vendored測試套件在消費端假紅`:全部不影響——它們出現在鏡頭裡是因為 `pitfall_when` 的 `content:` 觸發詞剛好命中計劃提到的 `governance/eval/retrieval-goldset.json`(內嵌歷史程式碼片段的已知偽觸發模式);五篇 `type: issue`,依「家」定義(`_nodehome_homes` 只認 `type == "system"`)永遠不可能被判定成任何檔的家,[S3]「事故同時是家的算事故」這條在這五篇身上結構性不會發生(但在同時掛 `pitfall_when` 的 Systems 節點上是可能的且已用本 repo 現況驗證過,不影響判準本身)。

總結:最高 severity major,blocking 共 3 條
