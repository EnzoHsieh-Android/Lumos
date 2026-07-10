---
type: project
status: doing
created: 2026-07-10
updated: 2026-07-10
tags:
  - type/project
  - status/doing
decisions:
  - content: 耦合度量採 ROSE 非對稱 confidence(shared/freq_A),不採 Code Maat 對稱平均
    context: 漏改守衛本質有方向:改A該提醒B,與改B該提醒A是兩條獨立規則;README.en.md 每次都跟著 README.md 改、反向不成立
    alternatives_considered:
      - "Code Maat 對稱 degree = shared/average(revs_A,revs_B):實作同樣簡單,但頻率懸殊對(en-README 5 次 vs README 16 次)耦合度被平均稀釋,漏單向規則"
      - "時間衰減加權耦合(學界 tie-decay 模型):理論更好但複雜度高、小 repo 增益未證,留 v2"
    why_chosen: conf(A⇒B)=P(改B|改A) 正是『漏改機率』語意;Code Maat 的 shared/average(revs) 在 A/B 改動頻率懸殊時被稀釋,會漏掉單向強耦合;ROSE error-prevention 模式有 ~2% 誤報實測背書
    trade_offs: 非對稱規則數量是對稱的兩倍(每對兩方向),挖掘成本 O(pairs×2) 但本 repo 規模無感;confidence 對低頻檔(freq 剛過 support 門檻)波動大,靠 min_support 兜底
    decided: 2026-07-10
    valid: true
  - content: 參數組 min_support=3/min_confidence=0.8/max_changeset=20,v1 無時間衰減
    context: 小 repo(478 commits)警告型場景;假警報成本=信任崩壞;硬砍時間窗會餓死訊號
    alternatives_considered:
      - "ROSE navigation regime(support 1/conf 0.1):覆蓋率高但 precision 29%,警告型會狼來了"
      - "ROSE 原版 error-prevention(support 3/conf 0.9):誤報最低(~2%)但小 repo 觸發過少;conf 0.9 在本 repo 原型只剩個位數規則"
      - "CodeScene 門檻(10 revs/50%):為上萬 commit 大 repo 設計,本 repo 會幾乎無規則"
    why_chosen: support 3 = ROSE error-prevention 原值;conf 0.8 = ROSE 實測過 0.80 過擬合的下限,警告型可比 0.9 略鬆換覆蓋;changeset 上限 20 比 Code Maat/ROSE 的 30 緊,因 docs commit 較小(本 repo p90=3);衰減留 v2
    trade_offs: conf 0.8 比 0.9 誤報略升(換覆蓋);全史無衰減=已修掉的舊耦合會殘留(規則右側存在性過濾部分緩解);門檻寫進 config 可調,但預設值錨定小 repo、大 repo 用戶要自己調高
    decided: 2026-07-10
    valid: true
related:
  - "[[Projects/社群演算法補強_調研]]"
---
# cochange守衛_計劃

## 目標

解 [[Projects/社群演算法補強_調研]] 缺口 c（知識同步散落）：機制同步只改最相關段、漏散落的列舉表/清單，人手動也漏。做一個 **co-change mining 守衛**——從 git 歷史挖「改 A 歷史上總是同改 B」的關聯規則，commit 時警告漏改的夥伴檔。警告型、不擋人。

PRIOR-ART: ① 最小解層級：既有 doctor Check D（discipline-block drift）只護 CLAUDE.md↔template 單一對，無法泛化到任意共改對；沒有一行 config 能解 → 需新機制。② 世界解過：ROSE（Zimmermann TSE 2005，error-prevention 模式 support≥3/conf≥0.9、誤報 ~2%）、Code Maat（對稱 coupling、min-revs 5/min-coupling 30%/max-changeset 30）、CodeScene（10 revs/50%/50 檔）、Herzig & Zeller MSR 2013（15% tangled commits = 大 commit 排除的學理根據）——真搜真驗，見調研節點。③ 裁定 = **borrow-design**：借 ROSE 的非對稱 confidence 設計，python3 stdlib 原生實作（`subprocess` git log + `collections.Counter`），零依賴。

## 演算法規格（借 ROSE error-prevention regime）

- **transaction** = 一個非 merge commit 的檔案集合（`git -c core.quotePath=off log --no-merges --pretty=format:%H --name-only`），排除改 >`max_changeset`（預設 20）檔的 commit（tangled/bulk 噪音，Herzig 學理）。
  - **`core.quotePath=off` 必帶**（挖掘與 staged 讀取皆同）：git 預設對中文/non-ASCII 路徑輸出 octal 逃逸帶引號字串，而本守衛的主要目標檔（圖譜 .md）大多中文檔名——不關掉會把主目標全變垃圾 key。`scripts/hooks/pre-commit` 開頭已為同一 gotcha 設 `-c core.quotePath=off`（既有先例）。
- **規則**：`conf(A⇒B) = shared(A,B) / freq(A)`（非對稱條件機率，ROSE §5）；`support = shared(A,B)`（絕對次數，非比例）。
- **告警門檻**（`.lumos/cochange.json` 可覆寫；缺檔/壞 JSON → 用預設值並印一行提示後繼續，fail-open 援引 `impact.json` 先例而非 lint-watch 的 rc2 硬錯——advisory 工具不因 config 手誤擋 commit）：`min_support: 3`、`min_confidence: 0.8`、`max_changeset: 20`。
  - 0.8 依據：ROSE 實測 confidence 過 0.80 後過擬合（precision/feedback 雙降）、0.9 誤報 ~2%；警告型不擋人可取 0.8 換覆蓋。0.8 是**預設值的設計下限建議**；config 覆寫不 clamp（使用者自由），但文件明講調低的過擬合風險。
  - 此參數組直接回應調研節點 §6 的開放題（小 repo 統計支持度）：2026-07-10 原型已在本 repo（478 commits）實測 conf≥0.8/support≥3 挖出 22 條規則、Landmark（1481 commits）247 條，訊號充足。
- **排除清單**（挖掘與 check 皆套用；`.lumos/cochange.json` 的 `exclude` list 可增補，與預設合併）：預設排除治理帳與生成檔——`docs/.governance-log.jsonl`、`docs/.bypass-log.jsonl`、`docs/.canary-log.jsonl`、`docs/.rot-queue.jsonl`、`**/*-lock.json`、`**/*.lock`、`**/node_modules/**`、`**/dist/**`、`**/Migrations/**`、`**/*.g.cs`、`**/*.Designer.cs`。（辯方實測噪音僅本源 repo 1/22、Landmark 4/247，belt-and-suspenders 而非主防線。）
- **檔案存在性過濾**：規則右側 B 已不存在於 repo（被刪/改名）→ 不告警（防殭屍規則）。
- **粒度**：檔案級、**全 repo-relative 路徑為 key**（basename 有歧義：本 repo 有 5 個 SKILL.md）。
- **v1 不做（documented debt）**：
  - 時間衰減加權（軟衰減留 v2；本 repo 全史即可，硬砍時間窗會餓死訊號）、entity 級解析、TF-IDF 高頻檔懲罰（先觀察誤報再說）。
  - **rename-following**：被改名檔的歷史耦合訊號在改名當下重置（`--name-only` 只吐新路徑），與 ROSE/Code Maat 同限；警告型假陰性成本低 + 本 repo 508 commits 僅 1 次 rename 且無規則涉及（2026-07-10 辯方實測），接受為 documented debt。v2 可解析 `--name-status -M` 的 R 行做路徑 canonicalize。
  - shallow clone：`git log` 在 shallow repo 靜默截斷歷史——v1 不偵測（advisory 工具規則變少無害），文件記一句即可。

## CLI 面（vault-free 命令，仿 lint-watch/pitfalls 慣例）

- `lumos cochange rules [--all] [--repo <root>] [--json]` — 挖全史規則。**預設套用 config 門檻**（輸出即 check 會告警的規則集，觀察=行為，杜絕「rules 看得到、check 不告警」歧義）；`--all` 列未過濾全量（support≥2 起，調參用）。rc：成功 0（含空規則集）、git 失敗（非 repo/無 commit/git 缺）2。`--json` schema：`{rules:[{lhs,rhs,confidence,support}],commits,files}`（confidence 取 4 位小數）。
- `lumos cochange check [--staged | --diff <A..B>] [--repo <root>] [--json]` — 對「本次變更檔案集」比對規則：改了 A、`conf(A⇒B)≥min_confidence` 且 B 不在本次變更且 B 存在 → 警告。旗標名用 **`--diff`**（同 `pitfalls --diff` 慣例，吃 pre-resolved 兩點 range 如 `main..HEAD`；不另造 `--range`）。變更集讀取：`--staged` = `git -c core.quotePath=off diff --cached --name-only`；zero-commit repo（`git log` 失敗但 staged 可讀）→ 無規則、rc 0。
- **rc 語意（精確條件式，不用「恆」）**：正常執行（不論有無警告）→ rc 0；git/subprocess 本身失敗（非 git repo、git 不存在、log 拋錯）→ rc 2（讓呼叫端知道「警告清單不可信」，pre-commit 側以 `|| true` 隔離）。
- `--json` manifest：`{warnings:[{changed,missing,confidence,support}],checked}`，`checked` = int（本次比對的變更檔數）。
- 每次執行即時挖規則、不做 cache（實測：本 repo 478 commits ≈0.1s、Landmark 1481 commits ≈0.5s；cache 與 commit 數上限留 v2，數萬 commit 的 monorepo 用戶先以 `exclude`/門檻自救）。

## 整合面

- **pre-commit hook 插入點（關鍵——不是「末段追加」）**：現行 `scripts/hooks/pre-commit` 每條路徑都以顯式 `exit` 結束（`:88`、`:92`、`:120` 等），末段是不可達死碼；且主場景 docs-only commit 在 `:88` 就 `exit 0`。**插在 STAGED 取得之後、Gate 1 之前**（約 `:41`），作為獨立 advisory 段：
  ```bash
  # Gate CC(advisory): co-change 漏改警告 —— 恆不影響 rc
  if command -v python3 >/dev/null 2>&1 && [[ -f "$REPO_ROOT/scripts/lumos" ]]; then
    python3 "$REPO_ROOT/scripts/lumos" cochange check --staged 2>/dev/null || true
  else
    echo "pre-commit: 無 python3 或 scripts/lumos,跳過 co-change 警告" >&2
  fi
  ```
  - 用 **vendored 路徑 + python3**（同 pre-push `:21-26` 慣例），不用裸 `lumos`（consumer 多半沒做全域 install，裸命令會靜默失效）。
  - fail-open 但**不靜默**：缺依賴時 echo 一行再跳過（對齊 pre-push 實際行為，spec 原「靜默跳過」描述有誤）。
  - `|| true` 隔離 rc 2，兌現「恆不擋」。
- **anchor 連動（實作 checklist）**：`scripts/hooks/pre-commit` 是 `ANCHOR_FILES` 成員（`scripts/lumos:4325`）——改完 hook 要 `lumos anchor approve --note "pre-commit 加 cochange 警告"`，否則 pre-push 擋。consumer 面免處理（baseline 是 opt-in、無自動建立路徑、錯誤訊息自導修復，2026-07-10 辯方查證）。
- doctor check 不做（v1）：commit 時點才有「本次變更集」語意，doctor 巡檢無 changeset 可比。
- 治理留痕不做（v1）：警告型無 gate 事件。

## 交付同步清單（散落列舉表——本守衛的立意，自己不能漏）

- `skills/lumos-project-notes/SKILL.md:141`「41 個頂層命令」→ **42**、分類全覽字串補 `cochange`、vault-free 命令表補一列。
- CLAUDE.md 若動速查表則同步（目前速查未逐列 vault-free 命令，預期免改，確認即可）。
- 圖譜：新增 `Systems/cochange-guard` 節點 + Verification + 本計劃 `plan_refs` 回指。
- `lumos anchor approve`（見整合面）。

## 測試計畫（scripts/test_lumos.py）

- 規則計算單元測：合成 git 歷史（tmp repo 真 git init + commit）驗 conf/support 數字、merge 排除、大 commit 排除、min 門檻過濾、排除清單生效。
- check 模式：staged 檔命中規則但缺夥伴 → 警告；夥伴同在 staged → 不警告；規則右側檔已刪 → 不警告；**docs-only staged 變更能觸發**（防 blocker 迴歸）；中文檔名 staged → key 正常非 octal 逃逸。
- `--diff <A..B>` 模式：range 內變更檔缺夥伴 → 警告（至少一個 happy path 測試，不留零覆蓋 CLI 面）。
- rules：預設輸出全部 conf≥0.8（0.778 的對**不出現**——rules/check 一致性）；`--all` 才出現。
- config 覆寫：`.lumos/cochange.json` 改門檻生效；壞 JSON → 印提示、用預設、rc 0（fail-open）。
- rc 語意：正常 rc 0、zero-commit repo check --staged rc 0、非 git 目錄 rc 2。

## 驗收（真機）

- 本 repo 跑 `cochange rules`：應含高於門檻的已知真耦合對——README.en.md⇒README.md（conf 1.0）、`scripts/test_lumos.py`⇒`scripts/lumos`（conf 0.82，103/126）。注意方向：`scripts/lumos`⇒`scripts/test_lumos.py` 是 0.795 **低於 0.8 不出現**（rules 預設套門檻）；graph-discipline⇒SKILL.md（0.778）同理只在 `--all` 可見。數字隨 commit 漂移，驗收以「對存在且方向正確」為準、不鎖死小數。
- **方向性驗收（修正版）**：造「改 `README.en.md`、不改 `README.md`」的 staged 變更 → `check --staged` **應警告**（conf(en⇒主)=1.0 ≥0.8）；反向「改 `README.md` 不改 en」→ **不警告**（conf(主⇒en)=0.375 <0.8）。兩向都測，驗非對稱設計落地。
- **consumer 真機驗收（Landmark）**：在 `/Users/enzo/backend/LandmarkMember`（1481 非 merge commits、C#+Vue、含 docs/landmark-knowledge 大圖譜）跑 `cochange rules`——驗規則品質（2026-07-10 原型：247 條、生成檔噪音 1.6%）、挖掘延遲（~0.5s）、interface⇄impl 與圖譜節點↔code 共改對浮現。2026-07-10 使用者指定此驗收場。

## 審計修正紀錄

- **r1（2026-07-10，panel W=3：sonnet×2 帶 canary + opus 否決位；canary 2/2 caught）**：折入 2 blocker（pre-commit 末段死碼→改插入點至 Gate 1 前；驗收方向矛盾→改例子方向並兩向測）+ 6 major（rules 門檻語意統一、rc 條件式改寫、vendored 路徑取代裸 lumos、quotePath=off、--range→--diff、交付同步清單新增）+ 辯方降級 4 條為 minor 折入（rename documented debt、anchor checklist、排除清單 belt-and-suspenders、開放題意圖鏈補注）+ 若干 minor（checked 型別、rules json schema、fail-open echo、shallow clone 注記、路徑 key 全稱）。辯方反證留檔：rename「活風險」實為內容替換（e710ad4 全 M 零 R）、噪音實測 1/22 與 4/247、anchor baseline opt-in（scripts/lumos:4360 無 baseline rc 0）。

## 相關模組

- [[Projects/社群演算法補強_調研]]
- [[Systems/pitfalls-code-loop]]
- [[Systems/lumos-cli-lifecycle]]
