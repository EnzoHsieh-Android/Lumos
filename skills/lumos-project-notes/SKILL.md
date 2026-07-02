---
name: lumos-project-notes
description: 維護專案知識圖譜（docs/{project}-knowledge/ 或 docs/knowledge/）— 追蹤進行中/待辦工作、系統關聯、Issue、會話交接摘要。當專案工作開始、結束、遇到 issue、或需要掌握現況時觸發。
---

# 專案知識圖譜系統

## 金科玉律

**所有對專案的改動、調研、計畫，都必須同步更新到知識圖譜。**

- 寫完程式碼 → 更新對應模組筆記
- 調研/討論完 → 記錄結論到 Issue 或 Systems 筆記
- 計畫變更 → 更新待辦清單和未決問題
- 查詢專案知識 → 優先從知識圖譜讀取
- 發現衝突 → 向使用者確認後修正

## 命名慣例

**每個專案的圖譜資料夾命名為 `docs/{project-slug}-knowledge/`**（如 `docs/myapp-knowledge/`、`docs/web-knowledge/`），避免 Obsidian CLI 多 vault 同名衝突——CLI 的 `vault=` 參數只吃資料夾 basename，多個專案若都叫 `docs/knowledge/` 會撞名導致 CLI 無法區分。

舊專案若仍使用 `docs/knowledge/` 保持相容，但**新建專案一律加專案前綴**。

`project-slug` 建議用 repo 資料夾 basename 的小寫精簡版（去掉公司前綴、產品後綴），如 `MyApp` → `myapp`、`WebApp` → `web`。

## 第一步：偵測 Vault

> **lumos 不需要 Obsidian。** lumos（scripts/lumos）是零 Obsidian 依賴的純檔案系統工具，`find_vault` 從 cwd 往上自動找 `docs/*-knowledge/`，vault 名稱 = 資料夾 basename。讀取/寫入/巡檢一律用 lumos，**完全不需要在 Obsidian 開啟或註冊 vault**。Obsidian 註冊只在用到 obsidian-only 功能時才需要（見下方步驟 4 與〈操作方式〉的 obsidian 場景表）——**不要把它當設定前置步驟**。

每次觸發此 Skill 時：

### 1. 偵測知識庫是否存在
```bash
# 優先找新慣例 docs/{slug}-knowledge/，找不到再 fallback 到 docs/knowledge/
ls -d docs/*-knowledge/Projects/ 2>/dev/null || ls docs/knowledge/Projects/ 2>/dev/null
```

### 2. 已存在 → 確認 lumos 找得到
```bash
lumos doctor    # 或 lumos stats；跑得動即代表 lumos 已鎖定本專案 vault
```
vault 名稱即資料夾 basename（如 `compasskiosk-knowledge`），lumos 自動解析，無需手動指定。

### 3. 不存在 → 初始化
詢問使用者確認 vault 名稱（預設 `{repo-basename 小寫}-knowledge`），然後一行開好（像 `openspec init`）：
```bash
lumos init                 # vault slug 預設 = repo 資料夾名小寫;--name <slug> 自訂
```
`lumos init` 建好 `docs/<slug>-knowledge/{Projects,Systems,Issues,Verification,MOC}` 5 個資料夾 + `.gitignore`（排除 `.obsidian/workspace*.json`、`.obsidian/hotkeys.json`），**預設並 vendor 工具組 + 裝 pre-commit/pre-push 閘**（改 code 沒更新圖譜會被擋）。既有 vault 會被偵測到（idempotent，不覆蓋）；要在既有 vault 補齊缺的資料夾/hooks 用 `--force`。
- `lumos init --no-hooks`：只建圖譜資料夾、不 vendor 工具/不裝 hooks（輕量，純記筆記的小專案用）。
- `lumos init --name <slug>`：自訂 vault slug。
> 沒有 vendored `lumos` 的舊專案 fallback：`mkdir -p docs/{vault-name}/{Projects,Systems,Issues,Verification,MOC}` 後手建 `.gitignore`。
> ⚠ 分工：**`lumos init` = 專案層**（圖譜 + 該 repo 的 hooks）；**`lumos bootstrap` = 機器層**（clone Lumos / user-scope skills / 全域 lumos），一輩子一次。bootstrap 不建圖譜資料夾，init 不裝機器層工具鏈。新機器第一個專案：先 `bootstrap`（裝機器層）再 `init`（開專案）；機器已設定好則新專案只需 `init`。
建完即可直接寫節點（rich 節點 = Write/Edit 內文 + summary block，scalar/list/decisions 走 lumos）→ `lumos doctor` 驗鐵則。**全程無需任何 Obsidian 步驟。**

### 4.（可選）Obsidian 註冊 — 僅 obsidian-only 功能才需要
**只有**要用這些 lumos 沒有的功能時才需要在 Obsidian 開啟資料夾：權威 metadataCache eval、白名單外 frontmatter 的 `processFrontMatter` 寫入、在 App 開筆記/搜尋視圖給人看、File Recovery 版本比較。做法：Obsidian「開啟資料夾」→ 選 `docs/{vault-name}/`，Obsidian 自動註冊，`obsidian vaults` 應看得到。**不需要這些功能就不用做。**

### 5. 同名 Vault 衝突（僅影響 obsidian CLI）
lumos 以 cwd `find_vault`，**不受同名影響**。只有用 obsidian CLI 時，若 `obsidian vaults` 列出兩個以上同名項目（例如兩個專案都叫 `knowledge`）：
- 用 `obsidian vault="{候選名稱}" eval code="app.vault.adapter.basePath"` 確認指到哪一個
- 名稱重複導致 CLI 無法區分 → 把其中一個資料夾改成 `docs/{slug}-knowledge/` 慣例（純改名，不破壞圖譜內容）

**注意**：用到 obsidian CLI 時，`vault=` 必須是 command 之前第一個參數（官方限制），否則多 vault 同開會打到當下 focused vault。

## 跨專案核心圖譜接點(core-knowledge)

部分業務規則已**升格**到跨專案核心圖譜(`$CORE_KNOWLEDGE_ROOT` = `$CORE_KNOWLEDGE_ROOT`,詳 `lumos-core-knowledge` skill)。專案層的最小閱讀規則:

1. **看到筆記 frontmatter `core_refs:` 或 summary `CORE:` 行** → 該主題權威在核心圖譜,專案筆記殘留描述**不可當權威**(紀律上不留快照,看到疑似快照 = drift 該清)
2. **語意/規則異動** → 改核心節點(不在專案筆記改),走 `lumos-core-knowledge` skill
3. **自足性審計**的 agent 可讀範圍要涵蓋已掛載的核心 repo,否則升格後的規則會被誤判為圖譜缺漏
4. **雙向核對**:專案筆記 `core_refs` ↔ 核心 facet(`projects/{專案}.md`)的 `implements` 要對得上,巡檢時檢查

## 操作方式

### 主要工具：lumos（讀 / 寫 / 巡檢 / 歸檔一律優先）

repo 內的 `scripts/lumos`（python3 標準庫，零 Obsidian 依賴）是**日常操作圖譜的主要工具**。讀取、寫入、巡檢、歸檔一律先用 lumos；Obsidian CLI 只保留給 lumos 沒有的少數場景（見下節）。

> **全域安裝**：`python3 scripts/lumos install` 後 `lumos` 上 `~/.local/bin`，任何專案子目錄直接打 `lumos <cmd>`（find_vault 從 cwd 往上找 docs/*-knowledge，或 standalone vault root 如核心 repo）。下表指令前綴 `python3 scripts/lumos` 與全域 `lumos` 等價。

**禁止用 Grep/Glob/Read/Edit/Write 直接操作 `docs/{vault-name}/` 下的 .md 檔案。**
lumos 提供圖譜感知能力（backlinks、links、orphans、contracts、合約測試綁定），是單純讀寫檔案做不到的；直接編輯也繞過寫後自驗與鐵則防護。

**讀取 / 巡檢**：

| 用途 | lumos 指令 |
|---|---|
| **單檔快檢（寫完一個節點立刻自驗標籤/格式，比 doctor 快）** | `python3 scripts/lumos lint <筆記名>` — type/summary/★ 格式/裸合約/未審/ghost trap;node-local 不掃 repo |
| 治理事件帳（某節點歷來被哪幾道閘攔過） | `python3 scripts/lumos gov [<筆記名>] [--since N]` — 唯讀彙整 bypass/rot/governance-log;本機可見性 |
| **設計 spec 進實作前打磨**（canary-護審計 loop 到收斂） | 調用 **`lumos-design-loop`** skill;原語 `lumos canary record --loop/--severity` + `lumos loop status <id> --need 2` |
| 健康巡檢（orphans / unresolved / verified_by 同步 / plan_refs 意圖鏈 / 同名守衛 / 鐵則 lint / ★INVARIANT★→測試綁定 + 獨立合法性審計；Check P 失效檔案認領(節點正文 inline-code 路徑指向已不存在的 repo 檔 → 軟提醒「圖譜指向死碼」)） | `python3 scripts/lumos doctor [--ci]` |
| 讀單篇 decisions | `python3 scripts/lumos decisions <筆記名>` |
| 全 vault 掃被推翻決策 | `python3 scripts/lumos decisions --superseded` |
| 環境變更掃 valid_under / revalidate_when 命中 | `python3 scripts/lumos stale --match "<條件字串>"` |
| **改某流程前查「該重驗哪幾篇」** | `python3 scripts/lumos stale --candidate --match "<關鍵字>"` — 聚焦活躍 Verification 的 `revalidate_when`(未來重驗條件、排 Archive);比純 `--match` 窄(後者含 valid_under 快照 + Archive) |
| status=stale 清單 | `python3 scripts/lumos stale` |
| 最近 N 天修改 | `python3 scripts/lumos recent --days 7` |
| 資料夾統計 | `python3 scripts/lumos stats` |
| 反查連入/連出 | `python3 scripts/lumos backlinks <筆記名>`／`links` |
| 進場掃脈絡（節點 + 鄰居 closet 索引；頭部突顯 ⚠ 合約） | `python3 scripts/lumos context <筆記名> [--brief]` |
| **合約登記簿（動模組前查硬合約）** | `python3 scripts/lumos contracts [筆記名]` — 列 ★INVARIANT★(改=breaking)/★DEBT★(可改);只認 KEY 行前綴標準格式 |
| **全文搜尋** | `python3 scripts/lumos search <詞> [--path Systems] [--regex] [--files-only]` — frontmatter+body,大小寫不敏感 substring |
| **spec 指涉宣稱機械核對(vault-free)** | `lumos refcheck <md檔> [--repo <root>] [--json]` — 抽 inline-code 檔路徑/行號、核對存在性/行號範圍、輸出證據 manifest(含行內容摘錄);design-loop 審計前先跑,存在性查證不靠 LLM。rc:全 ok=0/有 missing 或超界=1/參數錯=2 |
| **錨點完整性(vault-free)** | `lumos anchor verify [--repo] [--json]`/`lumos anchor approve --note "<理由>"` — 測試 runner+把關 hooks 的 sha256 baseline(`governance/anchor-baseline.json`);verify 不符 rc=1(pre-push/自主 loop 入口擋)、approve=改錨點合法路徑(治理帳留痕)。改測試 runner/hooks 後記得 approve |
| 鄰域樹狀展開／畫圖 | `map <筆記名> --depth 2`／`export --folders Systems Projects` |

**寫入**：

| 操作 | 指令 | 說明 |
|---|---|---|
| 改純量 status/updated/created/type | `lumos set <note> <key> <value>` | 行級手術，構造性最小 diff（只改該行，其餘原樣）；日期 bare 不加引號 |
| list 追加 verified_by/plan_refs/related/tags | `lumos append <note> <key> "[[x]]"` | 鐵則1 安全格式、自動 dedup |
| 依模板建檔 | `lumos new <type> <name>` | system/verification/issue/project |
| rename / 移檔（連結改寫） | `scripts/graph-rename.sh <舊> <新>` | 封印 wrapper（notesmd move），含 frontmatter 字串 |
| 滾動歸檔老 Verification | `lumos archive [--days N] [--apply]` | 單遍移檔 + path 式入連結正規化成 basename；dry-run 預設；**活守衛護欄**：仍背書存活守衛(綁定測試在 code)的 Verification 不按年齡歸檔 |
| **巢狀:翻盤決策** | `lumos decision-supersede <note> "<content子字串>" --by "..." [--ended DATE]` | decisions[] 某條 valid:false + superseded_by;surgical 不碰子清單/其他條 |
| **巢狀:新增決策** | `lumos decision-add <note> "<content>" --decided DATE [--context ..] [--why ..]` | append ADR 決策(無 decisions 則建) |

- T1 寫入一律**寫 tmp → 自驗(值正確+無新指紋) → atomic rename**，失敗原檔不動；BOM/CRLF 檔拒寫
- **decisions 翻盤/新增** → `lumos decision-supersede` / `decision-add`（surgical 巢狀;**非 ruamel**——ruamel round-trip 會 reflow、破壞最小 diff）
- **白名單外的 frontmatter 寫入**（`summary` block 改某行、`alternatives_considered` 子清單編輯）→ lumos 目前無對應,走下節 obsidian `processFrontMatter` eval 或手動 Edit

**安裝 / 生命週期**（操作工具鏈本身,不碰圖譜資料;唯一源 = 公開 repo `EnzoHsieh-Android/Lumos`，預設 clone 到 `~/harness/lumos-toolchain`）：

| 操作 | 指令 | 說明 |
|---|---|---|
| 全域安裝 lumos（symlink → `~/.local/bin`） | `python3 scripts/lumos install [--force]` | 裝完任何專案子目錄直接 `lumos <cmd>`,免打 `python3 scripts/lumos`;`--force` 覆寫既有 symlink |
| 移除全域 lumos | `lumos uninstall` | 移除 `~/.local/bin/lumos` symlink（不動 vendored copy） |
| 從唯一源更新本專案 vendored 工具組 | `lumos update [--source <path>] [--no-pull]` | `git pull` Lumos 來源 → 重新 vendor（lumos CLI / hooks / CLAUDE.md 紀律範本）→ 結尾 diff 自癒;**圖譜資料 scaffold-skip 永不動**。`--source` 指定來源（預設 `$LUMOS_HOME` 或 `~/harness/lumos-toolchain`）、`--no-pull` 用現有來源不拉取。**跑完記得 `git commit` 那份 vendored copy**（CI/hook 靠專案內這份） |
| 一鍵裝好一切（新機器 / 新 clone 的專案） | `python3 scripts/lumos bootstrap [--pull] [--lumos-url <url>] [--lumos-home <path>]` | 自動：clone Lumos（若缺）→ 裝 user-scope skills → 全域 lumos → repo git hooks。裝完**重啟 Claude Code session**（L1/L3 hooks 要 session start 載入）。**`--pull`：既有 Lumos clone 也 `git pull` 拉最新**（不加則沿用現有 clone、拿不到 skills 更新——「已設定過的人想拿更新」用這個或直接去 Lumos clone `git pull`）。`--lumos-url`／`--lumos-home` 預設讀 `$LUMOS_URL`／`$LUMOS_HOME` |

> **子命令全覽**：讀取/巡檢 13（`doctor` `context` `contracts` `search` `refcheck` `links` `backlinks` `map` `export` `decisions` `stale` `recent` `stats`）+ 寫入 7（`set` `append` `new` `archive` `decision-add` `decision-supersede` `self-audit`）+ 安裝/生命週期 4（`install` `uninstall` `update` `bootstrap`）+ 其餘（`anchor` `lint` `gov` `canary` `loop` `guard` `sync-verified-by` `init` `deinit` 等）。`lumos --help` 為現行權威。

### Obsidian CLI：僅限 lumos 沒有的場景

Obsidian CLI **不再是日常工具**,只在這幾件 lumos 做不到的事上用（指令帶 `vault="{vault名稱}"`，透過 Bash 執行）：

| 場景 | 為什麼還用 obsidian |
|---|---|
| **權威 frontmatter 解析驗證**（eval metadataCache） | metadataCache 是 Obsidian 引擎產物,lumos lint 只是盡力版指紋;「這篇 Obsidian 到底讀不讀得到」最終判定仍在 Obsidian |
| **白名單外 frontmatter 寫入**（summary block 某行 / 子清單） | lumos T1 只覆蓋純量+list+巢狀 decisions,其餘走 `processFrontMatter` eval |
| 在 App 中開筆記 / 開搜尋視圖（讓使用者接手檢視） | lumos 是 headless CLI,要叫起 GUI 給人看時用 |
| File Recovery 版本比較、模板變數解析 | Obsidian 專屬功能,lumos 無對應 |

> ⚠️ **用到 obsidian 時：`vault=` 必須是 command 之前的第一個參數**（官方限制）。`obsidian vault="X" command ...` ✅；尾部 `vault=` 在多 vault 並行時會靜默打錯 vault。來源：[Obsidian Forum #112217](https://forum.obsidian.md/t/cli-vault-parameter-ignored-all-commands-resolve-to-the-focused-vault/112217)

> repo 沒有 `scripts/lumos` 的舊專案 → 全部 fallback 既有 obsidian eval（本檔下半部「核心操作指南」的 obsidian 指令範例即為此 fallback 與上述 obsidian-only 場景保留）。

### ⛔ 禁用工具：notesmd-cli 的 `frontmatter` 指令

第三方 `notesmd-cli`（原 Yakitrak/obsidian-cli，Go 單檔）**只准用 `move`**（rename 連結改寫含 frontmatter 字串,2026-06-13 驗收通過;即上方 `graph-rename.sh` 封的那層）。**`frontmatter --edit` 嚴禁對真實 vault 使用**：實測會把整篇 frontmatter 鍵序重排成字母序、縮排 2→4、**日期加引號（property 型別 date→text 靜默損傷）**——一碰整篇 diff 不可審,且 pre-commit 污染指紋會擋。frontmatter 寫入合法路徑只有：lumos T1（純量/list/decisions）、obsidian `processFrontMatter` eval（白名單外）。驗收證據：MyApp vault 的 `2026-06-13_Yakitrak三題驗收`。

### 降級模式（lumos 與 obsidian 都不可用時）
以下情況才允許 Read/Edit/Write 直接碰 .md：
- `scripts/lumos` 不存在 **且** Obsidian App 未執行 / vault 未註冊 / CLI 報錯
- lumos 無法精準替換特定內容時（如修改表格某一行），可用 Edit 輔助（這類 body 表格編輯本就不是 lumos T1 範圍）

## 知識庫位置

- **路徑**：`docs/{project-slug}-knowledge/`（專案 repo 內，隨 git 版控）— 新慣例
- **舊路徑**：`docs/knowledge/` — 舊專案維持相容
- **團隊共用**：clone repo 後用 Obsidian 開啟對應資料夾即為獨立 Vault

## 資料夾結構

```
docs/{project-slug}-knowledge/
├── Projects/          # 專案總覽筆記（一個專案一份）
├── Systems/           # 功能模組 / 系統元件筆記
├── Issues/            # 追蹤中的問題
├── Verification/      # 驗證紀錄（每個功能的測試結果）
└── MOC/               # Maps of Content（索引筆記）
```

## 標籤慣例

| 類別 | 標籤 | 用途 |
|------|------|------|
| 狀態 | `status/doing` | 正在進行 |
| 狀態 | `status/todo` | 待辦 |
| 狀態 | `status/done` | 已完成 |
| 狀態 | `status/blocked` | 被阻擋 |
| 類型 | `type/project` | 專案 |
| 類型 | `type/system` | 系統元件 |
| 類型 | `type/issue` | 問題追蹤 |
| 類型 | `type/verification` | 驗證紀錄 |
| 驗證 | `status/pass` | 測試通過 |
| 驗證 | `status/fail` | 測試失敗 |
| 驗證 | `status/stale` | 曾經 pass 但 `valid_under` 條件已變/`valid_until` 已過，需重跑 |
| 優先 | `priority/P0` | 緊急 |
| 優先 | `priority/P1` | 重要 |
| 優先 | `priority/P2` | 一般 |

## Properties（YAML Frontmatter）慣例

```yaml
---
status: doing
type: project
created: 2026-03-26
updated: 2026-03-26
related:
  - "[[系統A]]"
  - "[[系統B]]"
tags:
  - status/doing
  - type/project
summary: |
  FLOW:主要流程A→B→C | AUTH:認證方式
  KEY:關鍵概念1,關鍵概念2
  DEP:[[依賴模組A]][[依賴模組B]]
  TEST:通過數/總數(日期) | VERIFY:[[驗證紀錄]]
  DECISION:[日期]決策內容(valid)
verified_by:
  - "[[Verification/2026-04-07_API審計修復]]"
  - "[[Verification/2026-05-04_點數圈存顯示]]"
decisions:
  - content: "決策描述"
    context: "當時的背景／痛點／約束（為什麼非做不可）"
    alternatives_considered:
      - "選項A：說明 / 為何不選"
      - "選項B：說明 / 為何不選"
    why_chosen: "為什麼選了這個（vs alternatives）"
    trade_offs: "犧牲了什麼（成本／彈性／複雜度／學習曲線）"
    decided: 2026-03-26
    valid: true
---
```

### Frontmatter 鐵則（違反 = 圖譜長 ghost 節點或整篇 frontmatter 報廢）

2026-06-10 MyApp 圖譜健檢實際踩雷總結，四條鐵則：

1. **多個 wikilink 必須是 YAML list，一項一連結**。❌ `verified_by: "[[A]], [[B]]"`（單一字串）→ Obsidian 把整串從第一個 `[[` 貪婪吃到最後一個 `]]` 當成**一個**超長連結 → 圖譜長出亂碼灰色 ghost 節點；在 Obsidian 點到該節點還會**自動建立含 `]], [[` 的垃圾檔案**（檔名中的 `/` 切成巢狀資料夾）。✅ 寫法見上方 `related` / `verified_by` 範例。
2. **block scalar（`summary: |` 等）內的 wikilink 不會被索引**。寫在 summary 裡的 `[[X]]` 只是文字，不產生圖譜連結、不算 backlink——要建立關聯必須同時在內文（如「## 相關模組」）或 list 型 property 放一份，否則目標筆記可能變孤兒。
3. **含 `: `（冒號+空格）的長文必須用 block scalar 或引號**。❌ `- content: 處置 SQL: UPDATE ...`（未引號）→ YAML `mapping values are not allowed` → **整篇 frontmatter 解析失敗**，所有 property 查詢對此筆記隱性失效。✅ `- content: |-` 換行縮排放長文。
4. **同一層級禁止重複鍵**。`decided:` / `valid:` 在同一個 decision item 出現兩次 → Obsidian 的 js-yaml 直接整篇 fail（CLI 的 ruby/libyaml 寬鬆放行，**用 CLI 驗過不代表 Obsidian 讀得到**）。

**巡檢偵測指令**（健康巡檢時跑）：

```bash
# 偵測 frontmatter YAML 解析失敗（鐵則 3；macOS 內建 ruby，注意 libyaml 比 js-yaml 寬鬆，過了不代表 Obsidian 過）
ruby -ryaml -rdate -e 'Dir.glob("docs/{vault-name}/**/*.md").each { |p| t = File.read(p); next unless t.start_with?("---"); parts = t.split(/^---\s*$/, 3); next if parts.length < 3; begin; YAML.safe_load(parts[1], permitted_classes: [Date], aliases: true); rescue => e; puts "#{p} -> #{e.message[0,120]}"; end }; puts "scan done"'

# 偵測 Obsidian 端解析失敗（鐵則 3+4 都抓得到；對「有 frontmatter 卻讀不到」的筆記交叉確認）
obsidian vault="{vault}" eval code="app.vault.getMarkdownFiles().filter(f => { const c = app.metadataCache.getFileCache(f); return c?.sections?.[0]?.type === 'yaml' && !c.frontmatter; }).map(f => f.path).join('\n') || '全部可解析'"

# 偵測字串型多 wikilink（鐵則 1）與 ghost 垃圾檔案
grep -rln ']], \[\[' docs/{vault-name}/ --include='*.md' | head
find docs/{vault-name} -name '*\]\]*'
```

### summary 欄位（中文結構化摘要）

**所有 Systems 和 Issues 筆記必須有 `summary` 欄位。** 讓 Claude Code 掃一眼 frontmatter 就掌握模組全貌，不需要讀完整篇筆記。

符號規則：

| 符號 | 用途 | 範例 |
|------|------|------|
| `FLOW:` | 核心流程 | `reserve→complete→void` |
| `AUTH:` | 認證方式 | `HMAC-SHA256`, `JWT` |
| `KEY:` | 關鍵概念/欄位 | `transactionId貫穿三階段` |
| `DEP:` | 依賴模組（用 wikilink） | `[[Billing]][[Inventory]]` |
| `TEST:` | 測試狀態 | `12/12通過(2026-04-07)` |
| `VERIFY:` | 驗證紀錄連結 | `[[2026-04-07_API審計修復]]` |
| `DECISION:` | 重大決策（簡版） | `[日期]內容(valid/superseded)` |
| `FLAG:` | 語意標記 | `TECHNICAL`, `DECISION`, `ORIGIN` |
| `→` | 流程方向 | `A→B→C` |
| `｜` | 分隔同類項目 | `A｜B｜C` |
| `,` | 分隔同欄細項 | `a,b,c` |
| `(valid)` | 現行有效 | |
| `(superseded)` | 已被取代 | |
| `★INVARIANT★` | KEY 行前綴：業務合約，改動 = breaking | `KEY:★INVARIANT★ 自動型只派V` |
| `★DEBT★` | KEY 行前綴：已知偶然行為，可改不算 breaking | `KEY:★DEBT★ RetentionDays=7寫死非設定` |

不同筆記類型的重點：
- **Systems**: FLOW + KEY + DEP + TEST（流程、關鍵欄位、依賴、測試）
- **Issues**: FLAG + DECISION + KEY（標記、決策、關鍵發現）
- **Verification**: TEST + VERIFY（測試結果、驗證紀錄）

### ★INVARIANT★ / ★DEBT★ 合約性標記（合約 vs 偶然）

Systems 節點記錄的是「做完的功能描述」（現在是什麼），天生分不出哪些行為是**合約**（改了 = breaking）、哪些是**偶然**（實作副產物，可隨意改）——未來修改者只能猜。解法是 KEY 行的合約性前綴（2026-06-12 Sonnet 對抗審計選定：**不開「需求與邊界」H2 段**——那會是繼 KEY 行 / decisions[] / DECISION: 行之後第四個放不變量的位置，多軌必漂移；收進既有 KEY 行單一位置）：

- `KEY:★INVARIANT★ ...` — 業務合約。改動此行為 = breaking change，動之前必須先翻 decisions[] 確認意圖
- `KEY:★DEBT★ ...` — 已知偶然行為（實作副產物 / 暫定值 / 寫死常數）。可重構，不算 breaking
- **未標 = 未聲明**（合約性未知，動之前自行判斷）。不回溯大掃除；動到節點時若當下脈絡足以判定，順手補標
- **不確定就不標**（寧漏勿錯，同 L3 confidence 0.7 哲學）。**嚴禁從現況 code 反推「應該是合約吧」**——把偶然行為合約化會鎖死重構，比沒標更毒。只有對話中業務語意明確、或 decisions[] 已載明意圖的行為，才配 ★INVARIANT★（例：decisions 標「暫定，待業務確認」的行為 = ★DEBT★，不是 ★INVARIANT★）
- **跨專案級不變量不在這裡標**：屬核心業務規則（引用密度 ≥2 專案）→ 走 lumos-core-knowledge 升格紀律，專案 KEY 行留 `CORE:` 指針，不留快照
- 慣例起源範例：某筆記的 `KEY:★INVARIANT★ 自動型流程只允許 X、不得走 Y`（合約性標記常自發長出，本規範把它 codify 成統一格式）

### ★INVARIANT★ → `[test:]` 綁定（合約即測試，2026-06-14 機制；doctor Check T 強制）

★INVARIANT★ 只是「宣稱」，沒有可執行證據就還停在「形式為真」（讀 code 看得出）而非「驗到真」（真跑會綠）。**每條 ★INVARIANT★ 在行尾加 `[test:方法名]`**，認領一個真實存在的測試方法：

```
KEY:★INVARIANT★ 點數不足 → INSUFFICIENT_POINTS,在扣點/寫 Registration 之前擋下 ... [test:ActivitySignupInsufficientPointsRejected]
```

- **doctor Check T 強制**：`lumos doctor` 把每條 ★INVARIANT★ 對到一個真實 `[Fact]/[Theory]/[SkippableFact]` 方法（`discover_test_methods` 認真方法，**非子字串比對**——綁到散文/工具方法/拼錯 = 偽證據,擋）。裸合約（沒綁）也擋。
- **① 先判平台（綁 [test:] 的第 0 步;單技術棧專案可略過）**：問「這條合約由**哪個平台/repo 的測試**驗?」——
  | 情境 | 綁法 |
  |------|------|
  | 同 repo 單技術棧(多數專案) | 裸 `[test:名]`(現況) |
  | **單一圖譜記錄的系統橫跨多技術棧 / 多 repo**(前端 App 一個 repo、後端 API 另一個 repo,共用同一圖譜) | `.lumos/config.json` 用 `platforms` map(各平台指 profile + root),綁 **`[test:平台:名]`**、`guard bind/scaffold --platform <平台>`。合約講**哪一端的行為就綁那一端的測試**(如後端合約 → `[test:<後端平台名>:…]`),別把它硬綁到另一端的測試(會變偽證據/套套邏輯) |
  | 合約由 **UI E2E** 驗(點擊流程/跨畫面/真機或瀏覽器,非單元) | 該平台 profile 用 **`maestro`**(mobile)/**`playwright`**(web),綁 flow `name:` / `test('id')`(見文末 test_profile 段) |
  - 判不準測試在哪個平台就**別亂綁**——先確認測試真的在哪、config 有沒有該平台(缺就先補 `platforms`)。詳見 [[Systems/test-profile-multiplatform]]。
- **② 三種 guard（在選定平台內,選最能「驗到真」的那種,別寫套套邏輯）**：
  | 類型 | 專案 | 何時用 | gate |
  |------|------|--------|------|
  | 純函式 | `MyApp.Tests` | 載重**公式**(累點/單次上限) | ubuntu 真跑,dev+prod+PR |
  | 行為整合 | `MyApp.IntegrationTests` | **拒絕路徑**零寫入(點數不足/超賣) | lab deploy 真跑(帶 DB secret) |
  | 狀態驗證 | 同上 | 真寫入 → **讀回 DB 斷言落地值**(累點真加對 AccountBalance、Complete↔Void 淨零) | 同上 |
- **誠實鐵則（B3/B4 教訓）**：守衛**不可靜默跳過**。唯一合法 skip = 本機/PR 無 `DB_CONNECTION_STRING`(整段 SkippableFact skip)。其餘「比率過期/種子取不到/schema 變更」一律 `Assert.True(...)` **大聲失敗**——否則守衛悄悄變儀式,綠燈但什麼都沒驗。純規則的套套邏輯測試(讀 code 就看得出對錯)不算數,要驗 service→repo→SQL→DB 真落地。
- **lab2 = 測試庫**：整合/狀態守衛用全新唯一測試會員,`finally` 依 CustNo 全刪,不留痕。不要把 lab2 當正式機綁手綁腳。
- **不重複**:guard 怎麼寫的細節 / lab CI 真機證據,寫進對應 `Verification/2026-06-14_lumos_*.md`,KEY 行只留 `[test:]` 指針。流程已知限制見 [[2026-06-14_lumos_guard審計_已知限制]]。

### ★INVARIANT★ → `[audit:]` 獨立合法性審計（合約即外審，2026-06-18 機制；doctor Check T 強制）

`[test:]` 證的是「程式**有沒有照規則做**」(verification);它證不了「這條**該不該**是不可改的鐵則」「綁的測試**夠不夠格**(會不會是同源套套邏輯)」。這兩個判斷**沒有標準答案**,而 2026 maker/checker 共識(治理日報 6/17)說得很白:**讓提出者自己評必手下留情**。所以:

> **每條 ★INVARIANT★ 一旦綁了 `[test:]`(視為宣告完成),其「合法性」必須由一個*無對話脈絡的獨立 agent* 判過並通過,在行尾留 `[audit:模型/日期]`。** doctor Check T 對「綁了測試卻沒 `[audit:]`」報**未審**(`--ci`/`--strict` 下擋)。

```
KEY:★INVARIANT★ 點數不足 → INSUFFICIENT_POINTS,扣點前擋下 ... [test:InsufficientPointsRejected] [audit:sonnet/2026-06-18]
```

**「乾淨」與「範圍」兩條件(缺一不算第三方驗證)**:

1. **乾淨脈絡**:審計 agent **只拿到圖譜 + 程式**,**不餵你的結論、不餵你的理由、prompt 必須中立(用「試圖反駁」而非「請確認這條合法」**——後者是帶風向,等於自己改自己的考卷)。它若繼承了 maker 的框架,只是換個分身蓋章,不算外人。
2. **範圍必含兩問**:① 「只讀圖譜,這是『不可改的合約』還是『現在剛好這樣實作』被誤標?」② 「構造一個違反這條保證、但綁的測試**仍會過**的情形——構造得出 = 測試同源/套套邏輯,不合格。」② 通常要 agent **實際去看測試碰了什麼**,不能只讀。
   - ⚠ 一個節點**通過第四道自足性審計(讀得懂、還原得出)** ≠ 這兩問被覆核過——是不同的問題,別混為一談。

**天花板(再乾淨也跨不過)**:`[audit:]` 只買到 verification 那一半;它**證不了 validation**——「這條金流規則**現在還符不符合真實業務**」要對著業務現實的人來確認(見下節 `decisions`/最高層鐵則的『上次對業務確認』)。**別讓「乾淨 agent 過了」被誤讀成「業務上也對」**;不可逆動作與業務正確性,該擋的閘仍留給人。

**模型選擇**:預設 `sonnet`(`--model` 可改)。刻意用較弱模型是為了讓它**不腦補補洞**——圖譜真的自我解釋得通、測試真的擋得住,才過得了關;強模型太會「替你圓場」。

**留痕**:`lumos guard audit <node> "<KEY 行子字串>" [--model sonnet] [--date YYYY-MM-DD]`(寫後自驗,重審覆蓋舊日期)。**工具只記留痕,不證明審計真的乾淨**——那靠上面兩條件的誠實自律,同 §「防帶風向鐵則」。

### ★CHECKPOINT★ / ★IRREVERSIBLE★ → `[rollback:]` 可逆性綁定（2026-06-19;doctor Check R）

不可逆動作(上架、prod DB 遷移)動手前要寫好怎麼收回。KEY 行前綴,**僅限 Systems 節點**:
- `KEY:★IRREVERSIBLE★ <宣稱> [rollback:decisions]` — 收不回。**必綁**;`[rollback:decisions]` 需本節點 `decisions[]` 有非空 `rollback` 欄位(實際回退 SQL/補償步驟)。缺=doctor Check R **error**(--ci/pre-push 擋)。
- `KEY:★CHECKPOINT★ <宣稱>` — 改了難救;建議補 `[rollback:decisions]`,缺=warning 不擋。
- 未標 = 可逆(git/測試級,放手)。
- **天花板**:`[rollback:]` 證「你寫下了 undo」,**不證明它跑得動 / 與現行 schema 一致**(同 [test:]/[audit:])。別把「有寫」當「安全」。
- v1 手寫 `[rollback:decisions]`(無專用指令);`lumos lint` / `doctor` Check R 把關。
- 外部不可逆動作(信已送出、prod 遷移下游已消費)事後無逆操作 → 用 `[guard:decisions]`(decisions[] 記非空 `guard`:冪等鍵/核可閘)取代 `[rollback:]`;兩軌任一即過 Check R,`[guard:]` 僅 `★IRREVERSIBLE★` 適用。

### `lumos guard`：對談驅動的守衛 scaffold（2026-06-15)

把「★INVARIANT★ → 寫守衛 → 綁 [test:]」這條手抄苦工交給 lumos 的機械部分,**斷言本體仍由你經對談向人確認後填**。三步:

```bash
lumos guard list [--unbound]        # 列所有 ★INVARIANT★ 綁定狀態(real/dangling/fake/naked);--unbound 只列未綁
lumos guard scaffold --node <Systems/X> --invariant "<KEY行子字串>" \
    --method <測試名> --type pure|behavioral|state --claim "<向人確認過的可測斷言>" \
    [--out <測試專案目錄>] [--template <路徑>] [--class <類別名>]
lumos guard bind <node> "<KEY行子字串>" <測試名>   # 把 [test:測試名] 綁回 KEY 行(寫後自驗)
lumos guard audit <node> "<KEY行子字串>" [--model sonnet] [--date YYYY-MM-DD]   # 合法性經無脈絡獨立 agent 審計過 → 留痕 [audit:](見上節)
lumos guard trace [<node>]          # 合約→守衛測試→Verification 證據鏈(reverse:改某模組會動到哪些守衛/驗證)
```

**改某模組前查爆炸半徑**:`lumos guard trace Systems/X` 列出該節點每條 ★INVARIANT★ → 綁的測試方法 → 哪篇 Verification 背書(grep 輸出某測試名即反查「這守衛紅了會牽動誰」)。

**補 verified_by 漏寫**(doctor Check 3 的零判斷項自動修):
```bash
lumos sync-verified-by            # dry-run:列 Verification 連到 Systems 但 verified_by 漏列的
lumos sync-verified-by --apply    # 真寫(T1 atomic append,自帶 dedup,冪等)
```
> 只補 verified_by 這一項。orphan 補掛 / plan_refs 斷鏈需**語意判斷**,doctor 只報不自動修(亂補會掛錯節點)。

- **scaffold 產的是預設紅燈 stub**:套技術棧範本(`.lumos/guard-templates/<type>.tmpl`,專案自備、lumos 語言無關不內建),填好 class/method/invariant/claim/TestIds 前綴,**斷言留 `// TODO` + `Assert.Fail(...)`**——逼你填到綠,不准假綠。
- **bind 是 KEY 行外科手術**:把 `[test:]` 寫進 summary block 的 ★INVARIANT★ 行(已綁則 merge 進同一個 `[test:A,B]`),寫 tmp→自驗該 ref 真的 parse 得到→atomic。

**⛔ 防帶風向鐵則(leading the witness)**:這套指令存在的前提是「claim 的真來自**人確認的意圖**,不是 code 反推」。Claude 用它時必須:

1. **先問「這裡什麼必須永遠為真」,再去看 code 怎麼實作**——不可先讀 code 反推出斷言、再包裝成「請確認」讓人蓋章(那是假 validation,繞回 Check T 在打的套套邏輯)。
2. **誠實標記每條斷言的來源**:是「你(人)講的意圖」還是「我從 code 猜的、請你裁示」——後者必須明講、等人確認才寫進 `--claim`。
3. **重大 invariant 的 claim 等同重大決策**:確認時順手把 `decisions[]` 的 context/why 補上(見下節),別只留一句斷言。
4. **殘餘誠實**:人可能確認一條錯的 invariant——這是 validation 的天花板,工具只保證 claim 被攤開+明確確認,不保證人一定對。別吹過頭。

> scaffold/bind 只省「打字」,不省「確認」。doctor Check T + 誠實鐵則(上節)照舊兜底:stub 不填(留 Assert.Fail)= 紅;綁了不存在的方法 = 懸空被擋。
>
> **測試棧 profile(語言可插拔,P5)**:guard/Check T 的「認哪些測試方法」由 `.lumos/config.json` 決定。內建 4 個 profile:**`csharp-xunit`(預設)**、**`kotlin-junit`**(Android 單元)、**`maestro`**(Android E2E,綁 flow `name:` 欄位;`file_must_match=^appId:` 只認真 flow;多字 name NO MATCH)、**`playwright`**(web E2E,綁 `test('id')`/`test.describe('id')`;含空白 title 不可綁)。各 profile 定:掃哪些副檔名、方法 regex、scaffold 副檔名、測試目錄偵測。**無 config = csharp-xunit,完全向後相容**。逃生口:`config.json` 的 `test` 可欄位級覆蓋 `exts`/`scaffold_ext`/`method_regex`。範本仍技術棧專屬、放各專案 `.lumos/guard-templates/`。
> ```json
> // 單平台:Android 專案 .lumos/config.json
> { "test_profile": "kotlin-junit" }
> ```
> **多平台(單一圖譜跨平台綁測試,見 [[Systems/test-profile-multiplatform]])**:圖譜記錄橫跨前後端的系統時,用 `platforms` 多根多 profile map,讓 `[test:平台:方法]` 綁到不同 repo 的測試。`default_platform` 給無前綴裸 ref 的歸屬(多平台缺省即報錯)。`load_platforms`/`resolve_test_refs` 以「config 有無 `platforms` 鍵」為 legacy 信號,舊 `test_profile`/裸 ref 照舊。`guard bind/scaffold --platform` 指定平台(`--method` 維持識別字、平台另帶,bind 寫 `[test:平台:方法]`)。Check T/`classify_invariants`/`cmd_archive` 各 ref 對其平台的 root+profile 判定(跨 repo)。
> ```json
> // 多平台:<圖譜所在 repo>/.lumos/config.json(平台名/profile/root 依專案自訂)
> { "default_platform": "app",
>   "platforms": {
>     "app":     {"profile": "kotlin-junit", "root": "."},          // 前端 App(同 repo)
>     "e2e":     {"profile": "maestro",      "root": "."},          // 同 repo 的 E2E flow
>     "backend": {"profile": "csharp-xunit", "root": "../<後端 repo>"}  // 後端 API(另一 repo)
>   } }
> ```
> 天花板:Check T 只驗測試識別子存在、不驗跑綠(CI 的事);E2E(maestro/playwright)要裝置/瀏覽器(無裝置才 skip);跨 repo 只讀不寫。**撰寫期用 Maestro MCP / Playwright MCP** 把 scaffold 的紅燈 stub 填到綠(開發工具、非合約守門)。
> - **自我供裝(缺就自動裝、別叫使用者手動)**:要用該 MCP 但工具清單裡沒有(deferred 也 ToolSearch 不到)→ 先 `claude mcp list` 確認,沒有就自動配置再用:
>   - Playwright(web):`claude mcp add playwright npx @playwright/mcp@latest`(前置 Node18+;首用 `npx playwright install` 裝瀏覽器)
>   - Maestro(mobile):先裝 CLI `curl -Ls "https://get.maestro.mobile.dev" | bash`,再 `claude mcp add maestro -- maestro mcp`
>   - 裝完**重啟 session** 或重跑 ToolSearch 讓 MCP 工具載入,再繼續填 stub。E2E 仍需模擬器/真機(mobile)或瀏覽器(web)才跑得起來。
>   - 供裝是這條 workflow 的預設動作;唯一該先問人的情況 = 該機器有明確不得自動裝軟體的政策。
> **stub 的紅燈哨兵放在 skip 之前**——未填的整合守衛在無 DB 的 PR CI 也會紅(不被 skip 掩蓋成假綠);填完斷言後刪哨兵行,skip 才恢復「無 DB 才 skip」。

### decisions 欄位（ADR：決策時間有效性 + 為什麼選/為什麼不選）

**有重大架構/技術決策的筆記必須有 `decisions` 陣列。** 追蹤「為什麼當初選 A 後來改 B」，讓過期決策不污染 Claude Code 的上下文，並讓「為什麼不選 B」的學習資產保留下來。

> 設計理由：純粹只記「選了什麼、被誰取代」會掉資訊——下次有人想再考慮被推翻的方案時，看不到「當初為什麼放棄、放棄理由現在是否還成立」。`context` / `alternatives_considered` / `why_chosen` / `trade_offs` 是業界 ADR 標準四欄位，**「為什麼選 / 為什麼不選」才是真正的決策智慧，「選了什麼」只是結果。**

```yaml
decisions:
  # 重大決策範例（ADR 完整版）
  - content: "點數保留鎖採用 MSSQL 樂觀鎖（rowversion + 重試）"
    context: "POS 尖峰 300-1200 RPS，需避免重複扣點；既有架構只有 SQL Server，沒 Redis 基礎設施"
    alternatives_considered:
      - "Redis 分散式鎖：低延遲但要新增基礎設施、增加故障容錯複雜度"
      - "資料庫悲觀鎖（SELECT ... FOR UPDATE）：簡單但長交易卡連線池"
      - "MSSQL 樂觀鎖（rowversion + 退避重試）：用既有 DB，無新依賴"
    why_chosen: "POS API 共用連線池場景下，避免長交易最關鍵；樂觀鎖在 1200 RPS 實測通過，無新依賴成本"
    trade_offs: "高衝突場景重試成本高（但本系統實測衝突率 <0.1%）；錯誤處理複雜度↑（要實作退避重試）"
    decided: 2026-03-10
    valid: true

  # 被推翻的決策（保留 ADR 欄位作為學習資產）
  - content: "用 Redis 做保留鎖"
    context: "初期評估時假設需要跨服務分散式鎖；當時只看 throughput 沒看基礎設施成本"
    alternatives_considered:
      - "DB 鎖：當時誤判會卡連線池"
    why_chosen: "（當時）Redis 是業界主流選擇，throughput 數字漂亮"
    trade_offs: "新增基礎設施、運維負擔、故障容錯複雜度"
    decided: 2026-02-20
    valid: false
    superseded_by: "改用 MSSQL 樂觀鎖（見上方）"
    ended: 2026-03-10

  # 小決策範例（不需 ADR 完整版）
  - content: "採用三階段流程（reserve→complete→void）"
    decided: 2026-02-15
    valid: true
```

**規則**：

| 欄位 | 重大決策 | 小決策 |
|------|---------|--------|
| `content` | ✅ 必填 | ✅ 必填 |
| `decided` (日期) | ✅ 必填 | ✅ 必填 |
| `valid` (true/false) | ✅ 必填 | ✅ 必填 |
| `context` | ✅ **必填** | ⭕ 選填 |
| `alternatives_considered` (陣列) | ✅ **必填**（至少 2 項） | ⭕ 選填 |
| `why_chosen` | ✅ **必填** | ⭕ 選填 |
| `trade_offs` | ✅ **必填** | ⭕ 選填 |
| `superseded_by` | 推翻時必填 | 推翻時必填 |
| `ended` (日期) | 推翻時必填 | 推翻時必填 |

**「重大決策」判定**（任一即是）：
- 架構選型（DB / 快取 / 訊息佇列 / 框架）
- 技術方案（鎖機制 / 認證方式 / 序列化格式）
- 流程變更（三階段流程 / 工作流順序 / API 契約版本）
- 安全/合規方案（加密方式 / 授權策略 / 個資處理）

**Claude 的填寫義務**（在更新圖譜時主動完善這些欄位）：

1. **建立新筆記寫第一筆決策時**：判定是否「重大決策」→ 是 → **主動 ASK USER** 取得 `context` / `alternatives_considered` / `why_chosen` / `trade_offs`，**不可省略只填 content+valid**
2. **讀到舊筆記只有 content+valid 但內容是重大決策**：標記為「ADR 不完整」，**主動詢問使用者**是否補上四欄位（不可自行編造，缺資訊就問）
3. **決策被推翻時**：
   - 舊決策**保留** ADR 四欄位（不刪），加 `valid: false` + `superseded_by` + `ended`
   - 新決策**重新填寫**完整 ADR 四欄位（不是繼承舊的）
   - 新決策的 `why_chosen` 必須提到「為什麼舊方案的 trade_off 不再可接受」
4. **`alternatives_considered` 至少 2 項**（含被選中的方案在內共 3 項才合理；只有 1 個選項不算決策）
5. **不可自行編造**：context/alternatives/why_chosen/trade_offs 若無法從對話/code/commit 推得，**問使用者**，不可生成似是而非的內容污染學習資產
6. Claude Code 讀到 `valid: false` 時，理解為**歷史脈絡 + 學習資產**而非現行規格——但下次有人想用同方案時要先檢查「當時放棄的 trade_offs 現在是否還成立」

**self-check 清單**（每次新增重大決策時用）：
- [ ] context 講清楚當時的約束（不是泛泛而談「為了效能」）
- [ ] alternatives 至少 2 項，每項都有「為何不選」理由
- [ ] why_chosen 明確對比 alternatives（不是孤立陳述「因為 X 好」）
- [ ] trade_offs 寫具體犧牲（不是「沒什麼缺點」這種廢話）

### verified_by 欄位（Verification 反向索引）

**所有 Systems 筆記應有 `verified_by` 陣列**，列出**驗證過此模組的 Verification 筆記 wikilink**。改 Systems 時直接看 frontmatter 就知道哪些驗證會受影響，不用每次跑 `backlinks` 反查 + 過濾雜訊。

```yaml
verified_by:
  - "[[Verification/2026-04-07_API審計修復]]"
  - "[[Verification/2026-05-04_點數圈存顯示]]"
  - "[[Verification/2026-05-08_runbook_auto_rollback_e2e]]"
```

**設計理由**：
- Obsidian 內建 `backlinks` 已能反查引用關係，但會混入所有引用者（Issues、Sessions、Projects），需手動過濾 `Verification/` path
- `verified_by` 是**結構化、過濾後的純驗證索引**：Claude `property:read` 一次取出，不需要 eval 過濾
- 改 Systems 時可直接 iterate `verified_by`，逐一檢查並標 `stale`，比 backlinks 後處理更直接

**Claude 的同步義務**（雙向同步，缺一不可）：

1. **建立新 Verification 紀錄時** → **同時**把該 Verification 的 wikilink 加進**所有相關 Systems** 的 `verified_by`（Verification 的「## 相關模組」列了幾個 Systems，就要更新幾個）
2. **廢棄/刪除 Verification 時** → **同時**把對應 wikilink 從相關 Systems 的 `verified_by` 移除
3. **改 Systems 筆記時的優先順序**：
   - 先讀 `verified_by`（一個 property:read 命令）
   - 再對每個 wikilink 比對 `valid_under` 與當前環境
   - 不匹配的標 `status: stale`
   - **不再需要先跑 backlinks 再過濾 Verification path**（除非懷疑 `verified_by` 不同步）
4. **發現 verified_by 與 backlinks 不一致** → 跑同步檢查 eval（見下方），把缺漏補上

**設定指令**：

```bash
# 加入新的 verified_by 條目 → lumos append(鐵則1 安全 YAML list 格式、自動去重)
python3 scripts/lumos append Systems/OrderService verified_by "[[Verification/2026-05-04_點數圈存顯示]]"

# 讀取 → lumos context(節點 frontmatter 一覽)或直接看檔
python3 scripts/lumos context Systems/OrderService --brief
```

> ⚠️ **絕不要用 obsidian `property:set` 塞逗號串接的多個 wikilink**（`value="[[A]], [[B]]" type="list"`）——實測存成**單一字串**而非 YAML list，圖譜長出亂碼 ghost 節點(2026-06-10 踩雷 14 篇)。`lumos append` 天生用安全 list 格式,沒有這個雷;真要走 obsidian 則用 `processFrontMatter` 陣列操作,別用 property:set。

**自動同步檢查** → `lumos doctor`（巡檢用,Check 3「verified_by 雙向同步」直接掃出漏寫的 Systems,不必再寫 eval）：

```bash
python3 scripts/lumos doctor    # 含「所有 Verification 都已掛進對應 Systems 的 verified_by」檢查
```

> 注意：歷史筆記的 `verified_by` 可能殘留字串型值（非 list）;lumos 讀取已內建正規化,obsidian eval fallback 才需自己 `Array.isArray(raw) ? raw.map(String) : ...`。

### plan_refs 欄位（Verification → 計劃的意圖鏈）

**落地或迭代某個計劃節點的 Verification 應有 `plan_refs` 陣列（選填）**，反指它對應的計劃筆記。意圖鏈 = 計劃（動工前的共識）→ 實作 → Verification 回指；有了這條邊，「後續翻盤有沒有回頭對照計劃」就從個人習慣變成 graph-doctor Check 4 可機械檢查的事。

```yaml
plan_refs:
  - "[[服務台豁免作廢_計劃]]"
```

設計理由（2026-06-12 Sonnet 對抗審計收斂，原「plan 物種四件套」提案砍半）：
- **單向指針，不雙寫**：計劃側不設 `fulfilled_by` 鏡像欄位——那會跟 Systems 的 `verified_by` 形成雙軌雙寫，必 drift。要看某計劃落地了哪些驗證，反查 `plan_refs` 即得。
- **不建 plan 物種**：計劃沿用 `type: project` + 檔名 `_計劃` 後綴識別；`proposed/agreed/done/superseded` 四態對單人+AI 流程過重。部分翻盤（計劃 5 條決策翻 1 條）用既有 `decisions[].valid: false` 決策級粒度表達，不整篇標 superseded。
- **不做模板化盤問**：enforcement 只管「鏈的存在與一致」，不管「思考的品質」——形式 section 保證不了思考發生（開發者 2026-06-12 否決）。

**何時寫計劃節點**（opt-in，非義務；2026-06-12 審計收斂的客觀判準）：

1. **需求討論跨超過一個 session → 預設寫**（session 數客觀可判，「大改造」主觀不可判）
2. 動工前需要跨人 / 跨團隊共識（如服務台豁免案的後台分工）
3. 變更跨多個 Systems 節點（計劃沒有單一宿主可住）
4. **任何工具產出「設計 / spec」→ 一律寫計劃節點**（brainstorming、writing-plans、OpenSpec、其他 SDD / spec-driven 框架皆同；既然有正式設計產出，它就該住圖譜，不是散在 repo 檔）

其餘變更**不寫計劃**：節點 `decisions[]` 一條 + Verification 即可——一條 decision 就是微型計劃（superseded 條目自帶意圖凍結語意）。常態工作流維持「對話敲定 → 依當下脈絡開發 → 事後沉澱」，計劃節點是大型變更的 opt-in，不是進場義務。

> **⚠ 橋接任何 spec/SDD 工具的預設輸出路徑（必讀）**：各家工具都有自己的 spec 落點——`superpowers:brainstorming` → `docs/superpowers/specs/YYYY-MM-DD-*.md`、`writing-plans` 有自己的落點、`OpenSpec` → `openspec/`、其他 SDD / spec-driven 框架亦各有目錄——**在本紀律下一律覆寫成 lumos 計劃節點**（`Projects/<主題>_計劃.md`，`type: project`），**不另存 `docs/superpowers/specs/`、`openspec/` 或任何 repo 路徑**。理由:「圖譜即唯一真相」涵蓋計劃/設計,不只 code;spec 散在 repo 檔 = 圖譜外的第二真相源,必 drift。多數此類工具也明示「user/專案偏好可覆寫預設 spec 路徑」,本紀律即該覆寫。落地的 Verification 用 `plan_refs` 回指該計劃節點。

**Claude 的維護義務**：

1. **寫 Verification 時，工作對應某個計劃節點** → 填 `plan_refs`。**含迭代/翻盤該計劃範圍的後續驗證，不只首輪落地**（意圖鏈斷裂的高發點正是第二輪之後）。
2. **動 Systems 筆記前** → 順手確認 Projects/ 是否有 `status: doing` 的計劃引用該 system（`grep -l "目標System" docs/{vault}/Projects/*_計劃*.md` 即可），有 → 本次 Verification 填 `plan_refs`。
3. **翻盤計劃中某條決策** → 改計劃本體（bump `updated` + 決策註記或 `decisions[].valid: false`），不是只改 Systems。graph-doctor Check 4 靠「計劃 `updated` 早於回指 Verification 的檔名日期」偵測漏做。
4. **計劃改名/歸檔** → `plan_refs` 是 frontmatter 字串，Obsidian 不會自動改寫（body wikilink 才會）→ 主動修各 Verification 的 `plan_refs`，graph-doctor Check 4 會抓斷鏈兜底。

### 讀取 decisions 的方式

decisions 是巢狀物件,**用 lumos 讀**（格式化輸出 valid/superseded,免自己寫 eval 拆 `[object Object]`）：

```bash
# 讀取單篇筆記的決策(格式化:✅/❌ + 日期 + content + superseded_by)
python3 scripts/lumos decisions Systems/OrderService

# 全 vault 掃所有被推翻的決策
python3 scripts/lumos decisions --superseded

# 看 summary / 整篇 frontmatter
python3 scripts/lumos context Systems/OrderService --brief
```

> fallback(無 lumos 的舊專案):obsidian `eval` 讀 `getFileCache(f).frontmatter.decisions` 自己 map,或 `property:read name="summary"`。

### 更新圖譜時的 summary / decisions / verification 維護規則

1. **新增功能/模組** → 建立筆記時同時寫 summary
2. **修改功能** → 更新 summary 中受影響的行（FLOW/KEY/TEST 等）
3. **新增重大決策** → 主動填齊 ADR 四欄位（`context` / `alternatives_considered` / `why_chosen` / `trade_offs`），缺資訊就問使用者不要編造
4. **決策被推翻** → 舊決策保留 ADR 欄位（學習資產）+ 加 `valid: false` + `superseded_by` + `ended`；新決策重新填完整 ADR
5. **測試完成** → 更新 `TEST:` 和 `VERIFY:` 行，同時建立 Verification 紀錄並填 `valid_under` / `revalidate_when`
6. **新增 Verification** → **必須同步**把該 Verification 的 wikilink 加進相關 Systems 的 `verified_by`（雙向同步）
7. **環境/依賴變更** → 主動掃 Verification 看誰的 `valid_under` 命中變更條件 → 標記 `status: stale` 並提示使用者重跑
8. **Systems 筆記改 DEP/KEY 行** → 優先讀 `verified_by` 取出相關 Verification 清單 → 逐一比對 `valid_under` → 命中的標 `stale`（不再先跑 backlinks）
9. **廢棄 Verification** → 從相關 Systems 的 `verified_by` 移除對應 wikilink
10. **Verification 對應某計劃節點（含後續迭代/翻盤）** → 填 `plan_refs` 反指計劃（見 plan_refs 欄位章節）
11. **翻盤計劃決策** → 改計劃本體（bump `updated` + 決策註記），不是只改 Systems

設定 tags 範例：
```bash
obsidian vault="{vault}" property:set path="Projects/xxx.md" name="tags" value="status/doing, type/project" type="list"
```

## 核心操作指南（obsidian CLI fallback 參考）

> ⚠️ **這一節是 obsidian CLI 的指令參考,不是日常路徑。** 日常讀寫巡檢一律用 lumos（見上方〈操作方式〉的 lumos 表）。本節保留給:① 沒有 `scripts/lumos` 的舊專案 fallback;② lumos 沒有的 obsidian-only 功能(在 App 開筆記/搜尋視圖、File Recovery 版本比較、模板變數解析、權威 eval lint、白名單外 frontmatter 寫入)。對照:`create`→`lumos new`、`append`/`property:set`→`lumos append`/`set`、`search`→`lumos search`、`links`/`backlinks`/`orphans`→`lumos links`/`backlinks`/`doctor`。
>
> 以下 `{vault}` 替換為實際 vault 名稱（第一步取得）。

### 1. 建立筆記

**重要**：`create` 的 `name=` / `path=` 參數不要帶 `.md` 副檔名，CLI 會自動加上。帶 `.md` 會報錯。

```bash
obsidian vault="{vault}" create path="Projects/新專案" content="# 新專案\n\n## 概述\n\n## 目前狀態\n\n## 相關系統\n"

# 從模板建立
obsidian vault="{vault}" create name="新功能" template=Systems

# 覆寫既有筆記（慎用）
obsidian vault="{vault}" create path="Projects/xxx" content="..." overwrite

obsidian vault="{vault}" property:set path="Projects/新專案.md" name="status" value="doing" type="text"
obsidian vault="{vault}" property:set path="Projects/新專案.md" name="type" value="project" type="text"
obsidian vault="{vault}" property:set path="Projects/新專案.md" name="created" value="{日期}" type="date"
```

### 2. 追加內容（不覆蓋）

```bash
obsidian vault="{vault}" append path="Projects/xxx.md" content="\n## 進度更新\n- 完成了 X\n"
obsidian vault="{vault}" prepend path="Projects/xxx.md" content="## 最新更新\n- ...\n\n"
```

### 3. 讀取、檢視與 Properties

```bash
obsidian vault="{vault}" read path="Projects/xxx.md"
obsidian vault="{vault}" outline path="Projects/xxx.md"

# 查檔案 metadata（大小、建立/修改時間）
obsidian vault="{vault}" file path="Projects/xxx.md"

# 在 Obsidian App 中開啟筆記（讓使用者檢視）
obsidian vault="{vault}" open path="Projects/xxx.md"

# 字數統計
obsidian vault="{vault}" wordcount path="Projects/xxx.md"

# Properties 操作
obsidian vault="{vault}" property:read path="Projects/xxx.md" name="status"
obsidian vault="{vault}" property:set path="Projects/xxx.md" name="status" value="doing" type="text"
obsidian vault="{vault}" property:remove path="Projects/xxx.md" name="deprecated_field"

# 列出 vault 所有 properties（審計用）
obsidian vault="{vault}" properties counts sort=count
```

### 4. 搜尋與查詢

> **優先用 `lumos search`**(2026-06-13 起,零 Obsidian 依賴):
> `python3 scripts/lumos search "關鍵字" [--path Projects] [--regex] [--files-only]`
> 下方 obsidian search 為 fallback(無 lumos 的專案 / 需要 Obsidian rendered 內容時)。

```bash
obsidian vault="{vault}" search query="關鍵字"
obsidian vault="{vault}" search:context query="blocked" limit=10
obsidian vault="{vault}" search query="status/doing" path="Projects"

# 統計匹配數
obsidian vault="{vault}" search query="TODO" total

# 區分大小寫搜尋
obsidian vault="{vault}" search query="API" case

# 在 Obsidian App 中開啟搜尋視圖（讓使用者接手查看）
obsidian vault="{vault}" search:open query="blocked"

# 標籤
obsidian vault="{vault}" tags counts sort=count
obsidian vault="{vault}" tag name="status/doing" verbose

# 別名
obsidian vault="{vault}" aliases
```

### 5. 知識圖譜關聯

```bash
obsidian vault="{vault}" backlinks path="Systems/xxx.md" counts
obsidian vault="{vault}" links path="Projects/xxx.md"
obsidian vault="{vault}" orphans
obsidian vault="{vault}" deadends
obsidian vault="{vault}" unresolved verbose
```

### 6. 任務管理

```bash
obsidian vault="{vault}" tasks todo
obsidian vault="{vault}" tasks todo verbose
obsidian vault="{vault}" tasks path="Projects/xxx.md" todo verbose
obsidian vault="{vault}" task path="Projects/xxx.md" line=15 done
obsidian vault="{vault}" tasks done
obsidian vault="{vault}" tasks total

# 篩選自定義狀態（如 ? 表示待確認）
obsidian vault="{vault}" tasks 'status=?'

# 日記任務
obsidian vault="{vault}" tasks daily todo
```

### 7. 檔案管理

```bash
obsidian vault="{vault}" move path="Issues/old.md" to="Issues/new.md"
obsidian vault="{vault}" rename path="Issues/typo.md" name="correct-name"
obsidian vault="{vault}" delete path="Issues/resolved.md"
obsidian vault="{vault}" files folder="Issues"
obsidian vault="{vault}" folders
```

### 8. 版本比較

```bash
# 列出筆記的所有版本（File Recovery + Sync）
obsidian vault="{vault}" diff path="Systems/xxx.md"

# 比較最新版本與目前檔案
obsidian vault="{vault}" diff path="Systems/xxx.md" from=1

# 比較兩個版本之間的差異
obsidian vault="{vault}" diff path="Systems/xxx.md" from=2 to=1
```

### 9. 模板

```bash
# 列出可用模板
obsidian vault="{vault}" templates

# 讀取模板內容（含變數解析）
obsidian vault="{vault}" template:read name="Session交接" resolve
```

### 10. 進階查詢（eval）

```bash
# 在 Obsidian 中執行 JavaScript（進階查詢）
obsidian eval code="app.vault.getFiles().length"
obsidian eval code="app.vault.getFiles().filter(f => f.path.startsWith('Issues/')).length"
```

## 實戰範例（lumos 為主；body 編輯走 Edit）

> 分工提醒:**讀取 / 巡檢 / frontmatter 寫入 → lumos**;**body 內容(進度段落、checkbox、表格)→ Edit**(lumos T1 只管 frontmatter);**版本歷史 → git**(圖譜同 repo 版控)。

### 開工前：掌握現況
```bash
# 掃進行中 / 被阻擋的工作(搜 tag)
python3 scripts/lumos search "status/doing"
python3 scripts/lumos search "status/blocked"

# 看最近的交接 / 異動
python3 scripts/lumos recent --days 7

# 快速了解某模組現況(節點+鄰居 closet 索引,頭部突顯 ⚠ 合約 — 比 read+outline 強)
python3 scripts/lumos context Systems/Billing
```

### 改完程式碼後：更新圖譜
```bash
# 更新 updated 日期(frontmatter 純量 → lumos)
python3 scripts/lumos set Systems/Billing updated 2026-03-27

# 追加一條 verified_by(frontmatter list → lumos,自動 dedup)
python3 scripts/lumos append Systems/Billing verified_by "[[Verification/2026-03-27_xxx]]"
```
> body 的進度段落、打勾待辦、串接狀態表格 → 用 **Edit** 精準改(這類 body 編輯不是 lumos T1 範圍;真要叫 GUI 給人看才用 obsidian)。

### 查關聯：更新一份筆記後檢查連帶影響
```bash
# 誰引用了這份(反向連結) / 這份連出去的(正向連結)
python3 scripts/lumos backlinks Issues/會員升等降級機制
python3 scripts/lumos links Issues/會員升等降級機制

# 搜相關關鍵字,確認其他筆記是否也要更新
python3 scripts/lumos search "贈獎"
```

### 追溯變更
```bash
# 圖譜同 repo 版控 → 直接用 git 看歷史 / diff
git log --oneline -- docs/myapp-knowledge/Systems/Billing.md
git diff -- docs/myapp-knowledge/Systems/Billing.md
```
> commit 前的本機版本(還沒進 git)→ obsidian File Recovery(obsidian-only,見上節)。

### 健康巡檢
```bash
# 一次到位:orphans / 破連結 / verified_by 同步 / plan_refs 意圖鏈 / 同名守衛 / 鐵則 lint / 合約測試綁定
python3 scripts/lumos doctor

# 資料夾統計 / 最近異動
python3 scripts/lumos stats
python3 scripts/lumos recent --days 7
```
> lumos doctor 涵蓋了舊 obsidian `orphans`/`unresolved` 等;deadends 等 obsidian-only 巡檢才回頭用 obsidian(見上節)。

## 同步規則（何時更新知識圖譜）

### 程式碼變更後（必做）
更新對應 Systems 筆記：
- 串接狀態（mock → 已串接）
- 新增/修改的檔案、API 端點
- DB 表結構變更
- 待辦完成打勾（`obsidian task ... done`）

### 更新筆記後（必做）
用 backlinks 檢查關聯筆記是否也需要同步更新：
```bash
obsidian vault="{vault}" backlinks path="剛改的筆記.md" counts
# 逐一檢查引用它的筆記，搜尋相關關鍵字確認是否過時
obsidian vault="{vault}" search query="相關關鍵字"
```

### 圖譜更新後：Sonnet agent 自足性審計（必做）

**原理**：圖譜的存在目的是讓「沒有主對話脈絡的下一個 session」能單靠圖譜還原現況。所以驗收方式就是模擬這件事——派一個**乾淨的 Sonnet agent**（沒有主對話上下文）只讀圖譜還原脈絡，主對話比對它的還原結果與自己腦中的現存脈絡：**有出入 = 圖譜當下不健全，需補足缺漏後重審**。

**時機**：每次對圖譜的**實質內容更新**完成後（新增/修改 Systems、Issues、Verification、decisions、summary）。純格式修正（typo、缺欄位補登、連結修復）可豁免，但修完建議至少跑一次健康巡檢。

**做法**：用 Agent tool 派出 subagent，`model: sonnet`，prompt 模板：

```
你是知識圖譜審計員。只允許讀 docs/{vault-name}/ 下的筆記（唯讀；優先用 obsidian CLI，
帶 leading vault="{vault-name}"，查詢指令見 search/backlinks/property:read/eval），
禁止讀程式碼、git log、其他文件——模擬「只有圖譜」的新 session。

請基於圖譜還原以下脈絡，據實回答，圖譜裡找不到的就明說「圖譜未記載」不要腦補：
1. {本次更新涉及的模組} 的現況：核心流程、關鍵欄位、現行有效的決策
2. 最近一次對 {模組} 的變更做了什麼、為什麼做、驗證狀態如何
3. 有哪些進行中(doing)/被阻擋(blocked)的工作與未決問題
4. 哪些決策已被推翻、被什麼取代

輸出：條列還原結果 + 末尾列出你覺得圖譜記載模糊或互相矛盾的地方。
```

**判定與處置**（主對話執行）：

| Agent 還原結果 vs 主對話脈絡 | 判定 | 處置 |
|---|---|---|
| 一致，無模糊點 | ✅ 圖譜自足 | 記錄審計 PASS（commit message 或 Verification 註記）|
| 缺漏（主對話知道但 agent 還原不出來）| ❌ 圖譜不健全 | 把缺的脈絡補進對應筆記（summary/decisions/內文）→ **重派 agent 直到一致** |
| 誤讀（agent 還原出與現實相反的結論）| ❌ 圖譜誤導 | 通常是過時決策沒標 superseded、summary 沒更新、或 frontmatter 解析失敗讓 property 隱性消失 → 修正後重審 |
| agent 自己回報「模糊/矛盾」| ⚠️ 視同缺漏 | 逐條釐清補寫 |

**注意**：
- 審計 agent 與主對話相同，優先用 obsidian CLI 查詢（圖譜感知能力：backlinks/property:read/eval）；CLI 不可用時才降級 Read/Grep（唯讀豁免）
- 主對話**不可把自己的脈絡餵給 agent**（污染測試），prompt 只給「審哪些模組」的範圍
- 比對時注意 agent 還原不出來的東西，到底是「圖譜缺漏」還是「本來就不該進圖譜」（如一次性對話細節）——後者不用補

**留痕（2026-06-23）**：審過且補到一致後，`lumos self-audit <node> [--model sonnet] [--date YYYY-MM-DD]` 蓋 `self_audit: <model>/<date>` 戳記到該節點 frontmatter（純量、走 T1 寫入）。語意：「這整篇被無脈絡乾淨 agent 還原審過」——**節點級**戳記，有別於 ★INVARIANT★ 軸的行級 `[audit:]`（驗單條合約合法性），兩軸獨立。**工具只記留痕，不證明審計真乾淨**（同 guard audit 的 maker/checker 誠實前提）。
- **doctor Check S（軟提醒、不擋）**：`type=system` 節點**無 `self_audit`** → 列「從未跑 L4」；`self_audit` 日期 **< `updated`** → 列「節點更新後未重審（過期）」。用 `warn_soft`、不計 issues、`doctor --ci` 仍 exit 0，是摩擦地板不是 gate（真實性機器驗不了）。
- `[H]` 漏標可逆性提醒（`doctor --ci` 才跑）:掃 diff 碰 prod/外部 API/寄送 → 軟提醒「是否漏標 ★IRREVERSIBLE★」。只提醒、不擋。

### 變體 B：圖譜×程式碼交叉審計（無主對話脈絡時用，以 code 為真值）

標準自足性審計需要「主對話脈絡」當比對基準。**沒有脈絡時**（定期巡檢、接手陌生專案、審很久沒動的大節點），改用程式碼當真值，兩階段、每節點各派一個乾淨 Sonnet agent：

**階段一（還原）**：agent **只讀單篇 Systems 筆記**（禁讀 code/其他筆記/git log），萃取 12~15 條「可被程式碼驗證的具體主張」：
- 挑載重最高的：流程順序、方法/類別名、欄位語意、invariant、邊界規則
- 必須可證偽（「設計良好」這種不算）；筆記有提檔案/方法名就照抄
- 只取 `valid: true`（或 partial 的「仍有效」部分）的決策，被推翻的不要
- 輸出：`C1. [主張] | 預期驗證點: [檔案/方法]`

**階段二（實證）**：另一個 agent **只讀程式碼（嚴格禁讀 docs/——那是被審計對象）**，逐條判定：
- ✅ 一致（附 file:line 證據）／❌ 不一致（說明 code 實際）／❓ 找不到（說明搜過哪裡）
- 多節點時兩階段都可並行（一節點一 agent）

**判定與處置**（主對話執行）：❌ = 圖譜腐爛 → 修筆記（過時決策標 superseded、錯誤描述更正並註明「YYYY-MM-DD 程式碼實證」）→ 建 Verification 紀錄審計結果 → 相關 Systems 的 `verified_by` 雙向同步。**修正一律以 code 為準**——除非 code 本身是 bug（那就開 Issue，不改筆記遷就）。

**實戰教訓（2026-06-10 四大節點首跑，60 主張 85% 一致）**：
1. 最高頻腐爛型態 = 「**決策在別篇筆記被推翻、本篇沒跟上**」——hooks 抓不到（改 code 時只同步了主筆記），交叉審計是目前唯一掃得出它的機制
2. **計數/清單型主張最會漂**（「共 5 處」「6 個檔案」「1 筆」）——寫筆記時這類數字要附截至日期或乾脆不寫死
3. 有筆記**引用了 codebase 不存在的方法名**（從未實證過就寫進去）——升格任何主張前先 grep 一次
4. 同篇筆記可能 KEY 行已更新、decisions 卻沒標 superseded——**自相矛盾**型,審計時兩處都要看

### 對抗設計審計的 canary（test-the-tester，2026-06-19）

派乾淨 agent 對抗審計一份 **spec/設計稿**(挑毛病、找 blocker)時,**順手驗證審計員這輪有沒有認真讀**——放水審計員回報的「沒問題」是最危險的假乾淨。做法:

1. **植一個 canary**:在審計用的**工作副本**裡塞一個刻意、已知、**純加性**的瑕疵(只允許不牽動其他段落的型:**指向不存在章節的交叉引用**、或**約束引用未定義的詞**)。**禁用「與某段矛盾的需求」**那類非局部 canary(會污染審計員對被矛盾那段的真實意見)。給它一個唯一 token 當定位記號。**提交的文件永遠不含 canary。**
2. **正常跑審計,不告訴 agent 有 canary**(講了就作弊)。
3. **判定**:唯一算數的是 agent **清楚且正確描述了那個瑕疵**(光是 token 出現不算)。
   - **抓到** → 這輪是醒的;只信它對**同類、同段**的真實 findings(不是全面合格證)。移除 canary、依真實 findings 改。`lumos canary record caught --auditor <模型>`。
   - **沒抓到** → 放水。**這輪判決作廢**,換不同 canary 重跑。`lumos canary record missed --auditor <模型>`。連 2 次 missed 就升級模型/把文件切小(升級前 `lumos gov --since 7` 看 missed 史)。
4. **panel 變體**:一輪派 N 個審計員時,每個各給自己的 canary;漏抓自己 canary 的剔出投票。

**收斂留痕(2026-06-19;讓多輪審計能機械終止)**:把每輪記成一筆帶 loop 的 canary——`lumos canary record caught|missed --loop <設計slug> --severity clean|minor|major|blocker --auditor <模型>`(`severity`=忠實轉錄審計員的最嚴重 finding)。`lumos loop status <slug> --need 2` 從紀錄**算收斂**:連 2 輪 caught 且 severity∈{clean,minor} → exit 0(綠燈進實作);否則 exit 1。missed/缺 severity/blocker/major 都讓它不收斂(逼修了再審)。`gov` 看得到整段輪歷史。

**天花板**:canary 抓得到「審計員根本沒讀/只吐通用回應」,**抓不到「讀了但複雜權衡判錯」**;判定「有沒有抓到」「severity 多嚴重」都由植入者自己做、無外部檢查——canary/收斂是**降低放水機率的摩擦 + 可觀測地板**,不是閉合驗證或 oracle。設計全文見 `docs/design/2026-06-19-canary-audit.md`、`…-convergence-recording.md`。

### 發現 Issue 時
```bash
obsidian vault="{vault}" create path="Issues/ISSUE-名稱" content="# ISSUE: 名稱\n\n## 現象\n\n## 相關系統\n- [[Systems/相關系統]]\n\n## 解決方案\n\n## 狀態\n- [ ] 分析原因\n- [ ] 實作修正\n- [ ] 驗證\n"
obsidian vault="{vault}" property:set path="Issues/ISSUE-名稱.md" name="status" value="doing" type="text"
obsidian vault="{vault}" property:set path="Issues/ISSUE-名稱.md" name="type" value="issue" type="text"
obsidian vault="{vault}" property:set path="Issues/ISSUE-名稱.md" name="priority" value="P1" type="text"
```

### 里程碑完成時
```bash
obsidian vault="{vault}" property:set path="Projects/xxx.md" name="status" value="done" type="text"
obsidian vault="{vault}" property:set path="Projects/xxx.md" name="updated" value="{日期}" type="date"
obsidian vault="{vault}" property:set path="Issues/相關issue.md" name="status" value="done" type="text"
```

### 測試前：查既有驗證紀錄（必做）

要測試某個功能前，**優先順序**：

1. **先讀對應 Systems 筆記的 `verified_by`**（最快，O(1) frontmatter 讀取）：
   ```bash
   obsidian vault="{vault}" property:read path="Systems/相關系統.md" name="verified_by"
   ```
2. **若 Systems 無 `verified_by` 或不確定完整性，再 fallback search**：
   ```bash
   obsidian vault="{vault}" search query="功能關鍵字" path="Verification"
   ```
3. **同步檢查**：跑「verified_by 自動同步檢查 eval」確認 Systems 的 verified_by 是否完整（見上方）

判斷準則：
- **有，`status: pass` 且 `valid_under` 條件仍成立** → 照著紀錄的測試項目跑，更新 `date` / `commit`
- **有，`status: stale` 或 `valid_under` 條件已變** → **必須重跑全部測試**，跑完後改回 `pass` + 更新 `valid_under`
- **有，`valid_until` 已過期** → 同上，必須重跑
- **沒有** → 寫新測試，跑完後建立驗證紀錄並更新對應 Systems 的 `verified_by`

**Claude 必做的有效性檢查**（讀到 Verification 時自動跑）：
1. 比對 `valid_under` 每一條跟當前環境（commit hash / DB schema 版本 / 依賴版本 / 預估 RPS）
2. 任一條不匹配 → **主動提示使用者**「此驗證的 `valid_under` 條件已變（具體哪條），建議改 status: stale 並重跑」
3. 不可以「假裝沒看到」直接拿舊驗證當保證

### 功能完成後：寫驗證紀錄（必做）

每完成一個功能並測試通過後，在 `Verification/` 建立驗證紀錄。**`valid_under` 與 `revalidate_when` 是必填欄位**（讓未來的人/AI 知道這份驗證在什麼條件下還算數）：

```bash
obsidian vault="{vault}" create path="Verification/{日期}_{功能名稱}" content="---\ntype: verification\nstatus: pass\nfeature: {功能描述}\ncommit: {commit hash}\ndate: {日期}\nvalid_under:\n  - \"DB schema v1.0.20（Member 表結構未變）\"\n  - \"並發 ≤ 1000 RPS\"\n  - \"三竹 SMS API v2\"\n  - \"Android 14 + 三星 One UI 6.0（若涉及行動端）\"\nrevalidate_when:\n  - \"Member 表結構變更（加欄位/改型別）\"\n  - \"RPS 超過 1200（30 櫃位尖峰再 2x）\"\n  - \"三竹 API 改版\"\n  - \"Android 16 GA\"\ntags:\n  - type/verification\n  - status/pass\n---\n# 驗證：{功能名稱}\n\n## 變更範圍\n- ...\n\n## 測試項目\n\n### 1. {測試場景}\n| 步驟 | 預期 | 結果 |\n|------|------|------|\n| ... | ... | ✅/❌ |\n\n## 測試方式\n{如何測試：API 呼叫、瀏覽器、腳本等}\n\n## 相關模組\n- [[Systems/xxx]]"
```

**命名規則**：`{日期}_{功能簡稱}`，如 `2026-04-01_點數圈存顯示`

**Frontmatter 欄位**：

| 欄位 | 必填 | 說明 |
|------|------|------|
| `type` | ✅ | 固定 `verification` |
| `status` | ✅ | `pass` / `fail` / `stale`（見下方規則） |
| `feature` | ✅ | 功能簡述 |
| `commit` | ✅ | 驗證當時的 commit hash |
| `date` | ✅ | 驗證日期 |
| `valid_under` | ✅ **必填** | 列出驗證**有效的環境條件**（list）—— 平台版本、規模、依賴版本、DB schema、外部 API 版本 |
| `revalidate_when` | ✅ **必填** | 列出**需要重驗的觸發條件**（list）—— 人類可讀，AI/人遇到該條件時應提示重跑 |
| `valid_until` | ⭕ 選填 | 只有絕對失效日才填（廠商合約到期、SDK EOL）；無就留空靠 `revalidate_when` 觸發 |

**status 規則**：
- `pass`：全部測試通過 + `valid_under` 條件仍成立
- `fail`：有失敗項目（需記錄失敗原因和後續處理）
- `stale`：曾經 pass，但 `valid_under` 條件已變或 `valid_until` 已過 → **下次有人依賴此功能前必須重跑驗證**，等同警告：「別把這份結論當現行依據」

**紀錄內容**：
- 變更範圍（改了哪些檔案/API）
- 測試項目表格（步驟 → 預期 → 實際結果）
- 測試方式（Python 腳本、curl、瀏覽器、DB 查詢等）
- 關聯模組（wikilink）

**Claude 主動填寫義務**：
- 寫 `valid_under` 不可只填「現在好用」這種廢話；要具體版本/規模/schema 數字
- `revalidate_when` 從 `valid_under` 反推：每條 `valid_under` 對應一條「當條件 X 改變時」的 `revalidate_when`
- 若使用者沒提供具體環境條件（版本/RPS/schema 版本）→ **主動詢問**，不可自行假設
- **建立 Verification 後同步更新 Systems**：Verification 的「## 相關模組」列了幾個 Systems wikilink，就要更新幾個 Systems 的 `verified_by` 欄位（追加，不是覆蓋），雙向同步缺一不可

> 進場提示(2026-06-29 起):`lumos context` 讀節點時會在最上方自動顯示 `valid_under` 條件(>90 天未更新加紅標),並由 `lumos doctor` Check V 量全圖過期率——失效條件從「寫入時標記」變「進場主動提示」,不需 AI 自己去 `lumos stale` 查。

### Verification 健康檢查（巡檢時必做）

開工前、commit 圖譜更新前、重大環境變動後，用 lumos 掃 Verification：

```bash
# status: stale 的驗證(需重跑)
python3 scripts/lumos stale

# 環境變動後:掃 valid_under / revalidate_when 命中某條件的驗證(改了 .NET 8 → 比對哪些要重驗)
python3 scripts/lumos stale --match ".NET 8"

# Systems 改動後查 verified_by + 反向連結
python3 scripts/lumos context Systems/{剛改的系統} --brief
python3 scripts/lumos backlinks Systems/{剛改的系統}

# verified_by 雙向同步漏寫 → doctor Check 3 一次掃全 vault
python3 scripts/lumos doctor
```

> `valid_until` 過期掃描 lumos 暫無對應(valid_until 用得少;多數用 valid_under 條件式),需要時走 obsidian eval fallback。

**掃出 stale / 過期 → Claude 必做**：
1. 列給使用者看：哪些 Verification 過期 / stale
2. 詢問：「這些要現在重跑、還是先標起來之後處理？」
3. 重跑通過後：更新 `date` / `commit` / `valid_under` / status 改 `pass`
4. 暫不處理：至少確保 status 已是 `stale`，不要保留 `pass` 假象

## MOC（Maps of Content）維護

MOC 是索引筆記，彙整某個主題下的所有相關筆記。
當某個領域的筆記超過 5 份時，建立或更新 MOC。

## 注意事項

1. **create 不帶 .md**：`name=` / `path=` 參數不帶副檔名，CLI 自動加 `.md`
2. **其他命令帶 .md**：`property:set`、`read`、`append`、`backlinks` 等用完整路徑含 `.md`
3. **file= vs path=**：`file=` 用 wikilink 解析（不需完整路徑），`path=` 要完整路徑
4. **內容換行**：用 `\n` 表示換行，`\t` 表示 tab。**Mermaid 區塊內換行用 `<br/>` 不是 `\n`**
5. **Wikilink**：筆記間互連用 `[[筆記名]]` 或 `[[資料夾/筆記名]]`
6. **不要覆寫**：優先用 `append` / Edit，除非明確要重建
7. **更新 updated**：每次修改筆記後，更新 `updated` property
8. **中文檔名**：可直接使用
9. **隨 git 版控**：所有變更被 git 追蹤，commit 時一起提交
10. **衝突處理**：知識圖譜 vs Memory vs Session 有出入時，向使用者確認
11. **vault 動態取得**：不要硬寫 vault 名稱，每次用 `obsidian vaults` 確認
12. **複製輸出**：任何命令加 `--copy` 可複製結果到剪貼簿
13. **Obsidian 必須執行中**：CLI 需要連接正在運行的 Obsidian App
14. **Verification 豁免**：Verification 筆記不需要 `summary` 和 `updated` 欄位（有 `feature` + `date` 已足夠），**但 `valid_under` + `revalidate_when` 是必填**
15. **避免假 Tag**：內文中的 `#` 會被 Obsidian 解析為 tag，顏色值用 backtick 包裹（如 `` `#FFF3E0` ``），編號用 `1~3` 不要用 `#1-3`
16. **ADR 不可編造**：`decisions` 的 `context` / `alternatives_considered` / `why_chosen` / `trade_offs` 若無法從對話/code/commit 推得，**問使用者**，不可生成似是而非的內容污染學習資產
17. **Verification 巡檢時機**：開工前、commit 圖譜更新前、重大環境/依賴/schema 變更後，跑健康檢查 eval 指令掃 `status: stale` 和過期 `valid_until`
18. **verified_by 雙向同步**：新增/廢棄 Verification 時，**必須同步**更新對應 Systems 的 `verified_by`；改 Systems 時優先讀 `verified_by` 而非跑 backlinks（backlinks 含 Issues/Sessions 雜訊）
