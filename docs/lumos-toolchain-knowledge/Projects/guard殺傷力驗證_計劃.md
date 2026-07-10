---
type: project
status: doing
created: 2026-07-10
updated: 2026-07-10
tags:
  - type/project
  - status/doing
decisions:
  - content: 壞法人宣告(kill 配方進 decisions)+config 宣告 run_cmd,不做自動變異生成
    context: 零依賴跨語言(C#/Kotlin/E2E/python)工具不內建語言知識;自動生成變異有等價變異不可判定問題(實務 4-39% 誤報)
    why_chosen: 人宣告的壞法保證語意有變(繞開等價變異,pytest-mutagen/ISO 26262 先例);run_cmd 沿 .lumos/lint.json 既有信任模型(專案自己宣告的指令);universalmutator ICSE 2018 實證文字層+外部指令 rc 跨語言可行
    decided: 2026-07-10
    valid: true
  - content: 四態判定(killed/survived/timeout/error)+baseline 前置,error 不得記 killed
    context: 紅燈≠殺傷:本來就紅的測試會假殺、編譯錯的紅是最常見假殺來源
    why_chosen: cargo-mutants baseline 流程+timeout=baseline×5下限20s 整套照搬;PIT/cosmic-ray 的獨立 timeout 類別;survived 才 rc1(稻草人)、環境問題 rc2 分開
    decided: 2026-07-10
    valid: true
related:
  - "[[Projects/社群演算法補強_調研]]"
  - "[[Systems/check-t-sentinel]]"
  - "[[Systems/check-r-guard]]"
  - "[[Systems/test-profile-multiplatform]]"
---
# guard殺傷力驗證_計劃

## 目標

補 ★INVARIANT★→`[test:]` 合約鏈的最後一哩：Check T 只驗「綁的測試存在」、`[audit:]` 靠 agent 讀判「夠不夠格」——都沒有**真的打一拳**。新增 `lumos guard kill`：對綁定的測試，在隔離環境故意弄壞被守護的行為，測試必須翻紅；全綠＝綁定是稻草人（假證據），機械可證。

PRIOR-ART: ① 最小解層級：既有 guard 家族加子命令 + config 加欄位，無新物種。② 世界解過（2026-07-10 專項調查，來源見文末）：pytest-mutagen（人宣告壞法、逐 mutant 期望翻紅——概念完全對口但綁死 python/pytest）、ISO 26262 fault injection（安全領域制度化的「宣告故障+期望防護翻紅」）、StrykerJS command runner / cosmic-ray test-command / universalmutator（「config 宣告任意測試指令、rc 判紅綠、工具不內建語言知識」的跨語言介面，ICSE 2018 實證）、cargo-mutants（baseline 前置 + timeout=baseline×5 下限 20s）、PIT/Stryker（四態判定 killed/survived/timeout/error 與增量失效）。③ 裁定 = **borrow-design**：「宣告式 kill 配方 × command-runner × 圖譜綁定」組合世界無既成品，各構件皆有先例背書；零依賴 stdlib 原生實作。

## 設計裁定（r1 折入後修訂版）

1. **壞法由人宣告，不自動生成；配方存節點級 `kill_recipes` frontmatter 欄位（r1 折入：不進 decisions——decisions 是節點級平面陣列、與個別 KEY 行無映射，「對應 decision」無資料模型可依）**。`kill_recipes` = block scalar 內 JSON array，每條配方自帶歸屬：`{"invariant":"<KEY子字串>","test":"<綁定測試名>","platform":"<平台名,單平台可省>","file":"<相對該平台root>","old":"...","new":"...","note":"業務上壞了什麼"}`。KEY 行尾標 `[kill:recipes]`（存在性標記；lint/doctor 驗 recipe.invariant 真的匹配到某 ★INVARIANT★ 行，防孤兒配方）。`old` 為 **literal 字面替換**（str.replace，非 regex；含換行走 JSON `\n`），唯一命中的權威判定時點=worktree 內套用時（count==1，否則 `drifted`）；kill-add 時對當下工作樹預檢並提示。**配方從業務行為推導、不從實作反轉**（DO-178C 教訓）；一條 INVARIANT 可綁多條配方（N=1 證據力弱）。
   - **同步改動明列（r1 折入,勿再宣稱零改動）**：`INV_TAG_RE` 擴為 `(test|audit|kill)`（否則 `[kill:recipes]` 漏進 strip_test_refs 的乾淨合約文字，污染 Check T 顯示/scaffold stub/guard bind 比對——scripts/lumos:1029/1249；複核 bind :2157、audit :2220 的 sub 邏輯）；`classify_invariants`+`cmd_guard_list` 各加 kill 欄顯示（兩函式、非免費）。
2. **跑測試靠 config 宣告指令**：多平台 → `platforms.<名>.run_cmd`；**legacy 單平台 → config 頂層 `run_cmd`**（r1 折入：legacy 無 platform 物件可掛——本 repo 自己就是 legacy）。`run_cmd` 含 `{method}` 佔位（多平台 ref 取**裸方法名**、剝平台前綴；代入前重驗 IDENT_RE + `shlex.quote`——`[test:]` 可被手改，不可信任；沿 `_lint_run_and_parse` 先例 `scripts/lumos:4642`，**注意先例是唯讀 linter、本功能會寫檔+跑有副作用的測試，信任邊界同為「專案自宣告指令」但爆炸半徑更大，見裁定 3 圍欄**）。無 `{method}` 的 run_cmd 允許但 verdict note 記 `whole-suite`（baseline 語意變成全套綠）。缺 run_cmd → rc 2 明確報。執行一律 `Popen(shell=True, start_new_session=True)` + timeout 到期 `os.killpg`（沿 :4666-4681，殺得掉 dotnet/vstest 孫進程）；cwd=**該配方平台的 worktree 根**。
3. **原始碼層隔離 + baseline 前置（r1 折入：正名——worktree 只隔離檔案，不隔離 DB/埠/外部狀態）**：對**配方 platform 的 repo root** 開 `git worktree add --detach`（跨 repo 時對 Landmark 那類外部 root 開，不是對 vault repo）；worktree 命名唯一（`.lumos-kill-<pid>-<ts>`）+ **try/finally + SIGINT 下 `git worktree remove --force`**（配方會弄髒樹，不 --force 刪不掉）+ 併發：同 root 同時只允許一個 kill（簡單 lockfile）。**未提交變更帶入**（r1 折入：worktree 取 HEAD 會漏掉剛寫好還沒 commit 的守衛測試）——`git diff HEAD` patch apply 進 worktree + untracked 檔（`ls-files --others --exclude-standard`）複製；帶不進的（如 .gitignore 內容物）誠實不管。**路徑圍欄**：配方 `file` resolve 後必須在 worktree 根之下（realpath 檢查，擋 `../` 逃逸——這是 lint 先例沒有的寫檔能力，必須新加的圍欄）。baseline = worktree 內先跑未變異 run_cmd，rc 0 才續（非綠 → `abort`）；timeout 基準 = 該次 baseline 牆鐘 ×5、下限 20s（含建置成本，對編譯語言偏鬆——誠實記不精確）。**hermetic 前置警語**：run_cmd 若有外部副作用（真 DB 寫入），弄壞行為可能把髒資料寫進共用資源——僅建議對自我清理（交易回滾/finally 全刪）的測試跑 kill。
4. **判定與合併（r1 折入：timeout 歸 killed，對齊 PIT/cargo-mutants——變異致掛而測試靠超時抓到=接住）**。per-recipe verdict 六值：`killed`（紅）✓ / `timed_out`（歸 killed 類、註記）✓ / `survived`（綠——含「filter 零命中」情形：綁定測試沒執行到=守不住這條壞法，語意上同稻草人；留痕存 baseline 輸出尾 200 字供人查證）/ `drifted`（old 零命中或多重命中——配方漂移，原名 stale 更名避免與既有 `lumos stale` 語意相撞）/ `abort`（baseline 非綠）/ `error`（套用後 harness 失敗，**不得記 killed**）。**node-level rc**：任一 survived → 1；無 survived 但有 drifted/abort/error → 2（證據缺損非稻草人）；全 killed（含 timed_out）→ 0。留痕 append **docs/.kill-log.jsonl**（r1 折入：跟四個治理帳同層，`lumos gov` 撈得到；欄位含 `commit`——對哪個版本跑的——與 `note`/`flaky_risk`），`--json` 出 manifest。

## CLI 面

- `lumos guard kill-add <node> "<KEY子字串>" --file F --old X --new Y [--test 方法名] [--platform P] [--note "業務上壞了什麼"]` — 寫配方進 `kill_recipes`（T1 寫後自驗：重讀 parse 得回、invariant 匹配到 KEY 行）+ KEY 行尾補 `[kill:recipes]`（merge 不重複）。`--test` 缺省時取該 KEY 行唯一的 `[test:]` ref；多 ref 必須指明。
- `lumos guard kill <node> ["<KEY子字串>"] [--platform P] [--json] [--keep-worktree]` — 跑該節點（或指定合約）的配方。rc 見裁定 4；`--keep-worktree` 保留現場（測試計畫的「無殘留」斷言在不帶此旗標時成立）。
- doctor 不加硬檢（v1）：kill 是主動體檢不是 gate；`guard list` 顯示各 INVARIANT 有無 `[kill:]`（改 classify_invariants + cmd_guard_list）。

## 交付同步清單

- `skills/lumos-project-notes/SKILL.md`：子命令全覽 guard 段 `list/scaffold/bind/audit/trace` → 補 `kill/kill-add`；`lumos guard` 指令區塊補用法。頂層命令計數 **42 不變**（guard 子命令非頂層）。
- guard subparser help 文字補 kill。
- 圖譜：`Systems/check-t-sentinel` 補 kill 機制段、Verification、本計劃 `plan_refs` 回指；related frontmatter 補齊與 body 相關模組一致（四節點）。
- guard-templates 無需動（kill 用配方非範本）。

## 邊界與誠實天花板

- **E2E（maestro/playwright）**：`{method}` 佔位對 maestro **不成立**（maestro 跑 flow 檔路徑、綁的是 name: 欄位，CLI 無法按 name filter）——E2E 平台 run_cmd 由專案自帶正確形狀（多半整檔跑），無裝置時 run_cmd 非綠 → 走 `abort` 路徑（baseline 前置的副作用，明列）。flaky 紅 ≠ 殺傷：E2E verdict 註記 `flaky_risk`（留痕有欄位），v1 不自動重跑。
- **worktree ≠ 環境隔離**：只隔離原始碼；DB/埠/外部資源共用（r1 否決位 M1）。hermetic 警語見裁定 3。
- **冷 build 成本**（r1 否決位 M2）：fresh worktree 無建置快取，C# 大 repo 每配方一次冷 build——比所引 cargo-mutants（重用 target）貴；v1 接受（偶發體檢非 per-commit 閘），build 產物重用留 v2。
- **submodule**：worktree 不自動 init submodule——依賴 submodule 的測試會假紅走 abort；v1 記載不處理。
- **配方等價風險**（dead code → 永遠 survived，人查）；**配方自身稻草人**（audit 順帶審）；kill 證「這個測試接得住這個壞法」，是存在證明不是覆蓋證明。

## 測試計畫（scripts/test_lumos.py，合成 repo + python run_cmd）

- 六態各一：killed / timed_out（sleep 配方,斷言歸 killed 類）/ survived / drifted（old 漂移與多重命中兩例）/ abort（baseline 紅）/ error（壞語法）；無 run_cmd rc2；legacy 頂層 run_cmd 生效。
- 未提交變更帶入：worktree 內看得到主樹未 commit 的新測試檔（B3 迴歸）。
- 路徑圍欄：`file` 含 `../` → 拒絕。
- 清理：**成功與失敗路徑（error/abort/中斷模擬）都無 worktree 殘留**；`--keep-worktree` 有殘留（且測試自行清）。
- `[kill:recipes]` 標記：strip 後乾淨合約文字不含 kill 標（INV_TAG_RE 迴歸）；kill-add 寫後自驗；孤兒配方（invariant 對不到 KEY 行）lint 報。
- {method}：多平台 ref 剝前綴、非識別字拒絕、shlex.quote 進指令。
- rc 合併：混合 verdict 的 node-level rc 斷言。

## 驗收（真機）

- 本 repo（legacy config + python run_cmd）：對一條示範 INVARIANT 走完六態。
- **Landmark（C# xunit，跨 repo platform root）**：挑一條已綁 `[test:]` 且測試 hermetic（lab2 finally 全刪那批）的 ★INVARIANT★，platforms 條目宣告 `run_cmd`（`dotnet test --filter FullyQualifiedName~{method}`），宣告一條業務壞法配方，真跑 kill 至 killed——跨 repo、跨語言、真守衛端到端閉環。**前置**：確認該測試自我清理（否決位 M1 的 hermetic 限縮）。

## 審計修正紀錄

- **r1（2026-07-10，panel W=5：4 canaried opus（新出題程序首跑：載重錨定+haiku 探針 4/4 probe:pass+事故庫無匹配走輪替）+1 否決位 opus；canary 3/4 caught、s4 missed → near-perfect 判準下輪無效、s4 findings 剔除〔其 ghost 連結 HIGH 經編排者覆核為編造——兩 Systems 檔實際存在〕）**：折入有效來源（s1/s2/s3/s5 + s4 與 s1 重合的 INV_TAG_RE 經覆核）——資料模型重設（配方改 kill_recipes frontmatter、自帶 invariant/test/platform 歸屬——原「對應 decision」無映射可依）、run_cmd legacy 棲身處、worktree 帶入未提交變更+跨 repo 開樹規則+路徑圍欄+finally --force 清理+唯一命名+lockfile、timeout 歸 killed（對齊 PIT）、survived 併 no-coverage 語意+baseline 輸出留痕、stale 更名 drifted、留痕改 docs/.kill-log.jsonl+commit/flaky_risk 欄、INV_TAG_RE 擴 kill+兩函式改動明列、{method} 剝前綴+IDENT_RE 重驗+shlex.quote+killpg、E2E maestro 佔位不成立明列、hermetic 警語+驗收限縮（否決位 M1）、冷 build 天花板（M2）、交付同步清單節新增、先例行號 :4613→:4642+唯讀 vs 副作用限定。

## 相關模組

- [[Projects/社群演算法補強_調研]]
- [[Systems/check-t-sentinel]]
- [[Systems/check-r-guard]]
- [[Systems/test-profile-multiplatform]]

## PRIOR-ART 來源

- pytest-mutagen：github.com/timpaquatte/pytest-mutagen（宣告式 mutant、期望翻紅）
- StrykerJS command runner：stryker-mutator.io/docs/stryker-js/configuration
- cosmic-ray：cosmic-ray.readthedocs.io（test-command+timeout→incompetent 三態）
- cargo-mutants：mutants.rs/baseline.html（baseline 前置、timeout 公式）
- universalmutator：github.com/agroce/universalmutator（ICSE 2018，文字層跨語言+外部指令 rc）
- PIT：pitest.org/faq（KILLED/SURVIVED/TIMED_OUT/NO_COVERAGE、targetTests、withHistory）
- ISO 26262 fault injection、DO-178C requirements-based coverage（需求推導壞法、人審把關）
