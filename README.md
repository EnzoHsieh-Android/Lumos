# Lumos

**繁體中文** · [English](README.en.md)

> **Lumos —— 揭開全 AI 開發的黑箱,照亮通往正確需求的路。**
>
> (路摸思:點亮咒。一邊照「程式碼」——把藏起來的為什麼、決策、硬合約照出來;一邊照「需求」——用繞不過的對話逼出理解,讓人走對路。Lumos 不替你把需求變對,它把路照亮、讓你自己走對。)

「**圖譜即合約**」方法論的**完整工具組唯一源**。把每一次全 AI 迭代織進「已理解的布」:知識圖譜是專案的唯一真相來源(為什麼這樣設計 / 邊界 / 不可改的合約),用 **commit-time 強制力與可執行合約測試**確保它不腐爛。

> **本治理建立在 [Claude Code](https://claude.com/claude-code) 之上。** 整套規範以 Claude Code 為執行的 AI agent 來設計:`skills/` 是 user-scope 的 Claude Code skills(symlink 到 `~/.claude/skills/`)、紀律注入專案的 `CLAUDE.md`、L1/L3 在 Claude Code session start 載入、`[audit:]` 獨立合法性審計用**乾淨的 Claude agent**(maker ≠ checker)。`scripts/lumos` CLI 本身是純 python、哪裡都能跑;但「先讀後動 / 退場寫回 / 獨立審計」這條完整迴圈假設 agent 就是 Claude Code。

---

## 1. Lumos 解決什麼

當 AI 寫了大部分的 code,瓶頸就從「生不生得出 code」變成「**我們還懂不懂這系統、看不看得出某個改動是錯的**」。Code 只告訴你「現在長這樣」,它說不出:

- **為什麼**這樣設計(決策、被否決的方案)。
- **邊界**在哪。
- 哪些行為是**合約**(改了 = breaking)、哪些是**偶然**(可隨意重構)。
- 有沒有**驗證過**、在什麼前提下成立。
- 這個動作**可不可逆**、搞砸了怎麼收回。

Lumos 把這些知識存成一張 Markdown 筆記圖譜(Obsidian 相容,但**不需要 Obsidian app**),用零依賴的 python CLI + git hooks 讓「**不更新圖譜**」比「更新圖譜」更難。

---

## 2. 核心理念:圖譜即合約

- **圖譜是唯一真相。** 圖譜與 code / 記憶 / 臆測衝突 → 以圖譜為準。
- **先讀再動。** 動既有系統前,第一個動作是 `lumos`,不是 `grep` / `Read` / 查 DB。圖譜先給你合約與邊界,code/DB 只拿來印證細節。
- **退場寫回。** 做完把決策 / 驗證 / 合約寫回圖譜。
- **commit-time 強制。** pre-commit 硬擋「改 code 沒更新圖譜」;`lumos doctor` 證明圖譜內部一致、且每條載重宣稱都綁了可執行測試。

---

## 3. 工具組內容

| 類別 | 檔案 | 作用 |
|---|---|---|
| **CLI** | `scripts/lumos`、`scripts/test_lumos.py` | 純 python3 標準庫、零依賴。讀 / 寫(寫後自驗)/ 巡檢(`doctor`)/ 歸檔。 |
| **合約守衛 scaffold** | `lumos guard list/scaffold/bind/audit/trace` | 對談驅動:列未綁的 `★INVARIANT★`、套範本產**預設紅燈**測試 stub、綁 `[test:]`、蓋獨立 `[audit:]`。 |
| **git hooks** | `scripts/hooks/` | pre-commit 硬擋「改 code 沒帶圖譜」;post-commit 留繞過痕跡;pre-push 跑 `lumos doctor --ci`。 |
| **安裝器** | `scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh`、`scripts/merge-claude-settings.py` | 把工具組 vendor 進專案 / 設 hooks / 合併 Claude settings。 |
| **紀律範本** | `scripts/templates/graph-discipline.md` | 「圖譜先行」紀律,注入各專案 `CLAUDE.md`。 |
| **skills** | `skills/lumos-project-notes`、`skills/lumos-core-knowledge` | 寫給 **AI** 的圖譜讀寫規範(user-scope 共用)。 |

---

## 4. 快速上手

### 4a. 已導入 Lumos 的專案
clone 後在裡面跑一個指令——**連 Lumos 都自動幫你 clone**:

```bash
git clone <你的專案> && cd <你的專案>
python3 scripts/lumos bootstrap     # 自動:clone Lumos(若缺)+ user-scope skills + 全域 lumos + repo hooks
```

然後**重啟 Claude Code session**(L1/L3 hooks 在 session start 載入)。

> `bootstrap` 預設**不**拉更新。日後更新:`git -C ~/harness/lumos-toolchain pull`(全 symlink),或 `lumos bootstrap --pull`。

### 4b. 全新專案導入(兩條指令)

**① 每台機器一次**(遠端,連 Lumos 都自動 clone):

```bash
curl -fsSL https://raw.githubusercontent.com/EnzoHsieh-Android/Lumos/main/get.sh | bash
# 然後重啟 Claude Code session
```

`get.sh` 裝「機器層」:clone Lumos + user-scope skills + 全域 `lumos`。(可先 `curl -fsSL <url> -o get.sh` 審閱再跑;傳參用 `… | bash -s -- --pull`。)

**② 每個專案一次**(在你的專案內):

```bash
cd <你的專案> && lumos init       # slug 預設取資料夾名;自訂用 --name <slug>
```

`lumos init` 裝「專案層」:建 `docs/<slug>-knowledge/{Systems,…,MOC}` + `.gitignore`、vendor 工具組、裝 pre-commit/pre-push 閘。既有 vault **絕不覆寫**(`--force` 才補齊缺的;`--no-hooks` 只建圖譜輕量版)。

<details><summary>進階/離線:手動 install-graph-toolchain</summary>

```bash
git clone https://github.com/EnzoHsieh-Android/Lumos ~/harness/lumos-toolchain
cd ~/harness/lumos-toolchain && ./install.sh        # user-scope skills(symlink)
python3 scripts/lumos install                       # (選用)全域 `lumos` 上 PATH
scripts/install-graph-toolchain.sh --target <專案路徑> --slug <名稱>
```
</details>

### 4c. Windows(原生 PowerShell)
前置:Git for Windows(自帶 bash 跑 git hooks)、python on PATH、Claude Code。

```powershell
irm https://raw.githubusercontent.com/EnzoHsieh-Android/Lumos/main/get.ps1 | iex
# 重啟 Claude Code session(L1/L3 在 session start 載入)
# 若 lumos 找不到:把 %USERPROFILE%\.local\bin 加進 PATH
cd <你的專案>; lumos init
```

`get.ps1` 裝「機器層」:clone Lumos(若缺)+ 呼叫 `lumos install` —— 全域 `lumos` 用 `%USERPROFILE%\.local\bin\lumos.cmd` shim、user-scope skills 用目錄 **junction**(`mklink /J`,失敗才退回複製),皆零權限免 admin;個別 Claude hook 的 `.py` 一律**複製**到 `~/.claude/hooks/`。接著 `lumos init` 同 Unix 建專案層(圖譜骨架 + vendor 工具 + git/Claude hooks)。

### 為什麼分兩層裝?
CI 只 checkout 專案 repo、git hook 是 per-repo,所以**工具組必須 vendor 進各專案**;而 **skills 是 user-scope**(一份共用、symlink 到 `~/.claude/skills/`)。對 Lumos clone `git pull` 會即時更新 skills + 全域 CLI;專案裡 vendored 的工具組用 `lumos update` 刷新。

---

## 5. 心智模型:節點與標籤

### 節點型別(frontmatter 的 `type:`)
`system`(模組:流程、合約、依賴)· `verification`(測試/審計紀錄)· `issue`(發現)· `project`(計劃)· `moc`(索引)。

### `summary` 符號行(Systems / Issues)
`summary:` block scalar,每行一個前綴,讓你掃一眼就掌握模組:

| 前綴 | 意義 | 前綴 | 意義 |
|---|---|---|---|
| `FLOW:` | 核心流程 `a→b→c` | `VERIFY:` | 驗證連結 `[[..]]` |
| `KEY:` | 關鍵概念/欄位 | `DECISION:` | 決策指針(簡版) |
| `DEP:` | 依賴模組 `[[..]]` | `FLAG:` | 語意標記(`TECHNICAL`/`ORIGIN`…) |
| `TEST:` | 測試狀態 | `AUTH:` | 認證方式 |

### 三條強制的「鏈」(Lumos 的差異化)

**合約鏈** —— *這是不是規則、有沒有被證明?*
```
KEY:★INVARIANT★ <業務合約;改 = breaking> [test:方法名] [audit:模型/日期]
                 └ 宣稱          └ 可執行證據    └ 無脈絡獨立 agent 的合法性判決
KEY:★DEBT★ <已知偶然行為;可改、不算 breaking>
```
- `★INVARIANT★` **必須**綁 `[test:]`(一個真的存在於 code 的測試方法)——否則 `doctor` 報「裸合約」並擋。
- 然後**必須**帶 `[audit:]` —— 由**無對話脈絡的 agent** 判決「這真的是合約、測試不是套套邏輯」(maker ≠ checker)。缺 = 「未審」,`--ci` 下擋。
- *不確定是不是合約就不標。* 嚴禁從 code 反推「應該是合約吧」。

**可逆性鏈** —— *能不能 undo、怎麼 undo?*(僅 Systems)
```
KEY:★IRREVERSIBLE★ <收不回:prod 遷移 / 上架> [rollback:decisions]
KEY:★CHECKPOINT★   <改了難救:部署測試機>
未標 = 可逆(git/測試級,放手)
```
- `★IRREVERSIBLE★` **必須**帶 `[rollback:decisions]`,且節點 `decisions[]` 要有一條非空 `rollback` 欄位(實際回退 SQL / 補償步驟)——否則 `doctor` 的 **Check R** 擋。
- `★CHECKPOINT★` *建議*帶(缺 = warning,不擋)。
- **天花板**:`[rollback:]` 證明*你寫下了 undo 路徑*,**不**證明它跑得動、或還符合現行 schema——同 `[test:]`/`[audit:]` 的誠實。別把「有回退」當「安全」。

### frontmatter 欄位
`status`(`doing`/`pass`/`open`/`done`/`stale`/`superseded`…)· `verified_by` / `plan_refs` / `related` / `tags`(list)· `decisions[]`(ADR:`content`/`context`/`alternatives_considered`/`why_chosen`/`trade_offs`/`decided`/`valid`/`superseded_by`/`rollback`)· `valid_under` / `revalidate_when`(重驗條件)· `core_refs`(指向跨專案核心圖譜)。

> ⚠ 多個 wikilink 必須是 YAML **list**、一項一行(`- "[[A]]"`)。單字串 `"[[A]], [[B]]"` 會長出 ghost 節點。純量/list/decisions 一律走 `lumos set`/`append`/`decision-add`(安全格式 + 寫後自驗),別手改。

---

## 6. 日常工作流

```
進場 ── lumos search <關鍵字> → lumos context <節點> → lumos contracts <節點>   (動 grep/DB 前先讀圖譜)
動工 ── 改動;新增 INVARIANT 時:guard scaffold → bind → audit
寫回 ── lumos set/append/decision-add 記決策、驗證、合約
自驗 ── lumos lint <節點>        (快、單檔——寫完一個節點馬上跑)
       ── lumos doctor           (全圖健康)
提交 ── pre-commit 擋 code-without-graph;pre-push 跑 doctor --ci 當最後一道閘
```

三層強制力,由快到硬:

| 層 | 指令 | 範圍 |
|---|---|---|
| **lint** | `lumos lint <節點>` | 單檔、不掃 repo——預判 pre-push 會不會擋 |
| **doctor** | `lumos doctor [--ci]` | 全圖:orphan、斷連、`verified_by` 同步、**Check T**(合約→test→audit)、**Check R**(可逆性)、frontmatter lint |
| **pre-push** | 跑 `doctor --ci` | push 前硬擋 |

---

## 7. 指令參考

**讀**
```bash
lumos context <節點> [--brief]    # 節點 + 鄰居壓縮索引(合約突顯在頂部)
lumos contracts [<節點>]          # 合約登記簿:★INVARIANT★(含綁定測試)/ ★DEBT★
lumos search <關鍵字> [--path P]  # 全文搜尋(取代 Obsidian search)
lumos links / backlinks <節點>    # 連出 / 連入
lumos map <節點> [--depth N]      # 鄰域樹
lumos decisions [<節點>] [--superseded]   # ADR 決策 / 掃被推翻的
lumos stale [--match S] [--candidate]     # stale 驗證 / 「改 X 時該重驗哪幾篇」
lumos recent [N] · lumos stats · lumos export --format mermaid|dot|html
```

**寫**(都寫後自驗)
```bash
lumos new system|issue|project|verification <名稱>   # scaffold 節點(印出怎麼填標籤)
lumos set <節點> <欄位> <值>                          # 純量欄位(status/updated/...)
lumos append <節點> verified_by|plan_refs|related|tags "[[X]]"
lumos decision-add <節點> "<內容>" --decided 日期 [--context ..] [--why ..]
lumos decision-supersede <節點> "<子字串>" --by "..." [--ended 日期]
```

**合約與驗證**
```bash
lumos guard list [--unbound]                         # ★INVARIANT★ 綁定狀態(real/dangling/fake/naked)+ 審計狀態
lumos guard scaffold --node S --invariant "<子字串>" --method M --type pure|behavioral|state --claim "..." [--platform P]
lumos guard bind  <節點> "<子字串>" <方法> [--platform P]   # 把 [test:方法] 寫回 KEY 行(多平台:[test:P:方法])
lumos guard audit <節點> "<子字串>" [--model sonnet] [--date 日期]   # 獨立審計後蓋 [audit:]
lumos guard trace [<節點>]                           # 合約 → 守衛測試 → Verification 證據鏈
lumos sync-verified-by [--apply]                     # 補漏寫的 verified_by(doctor Check 3)
```

**治理與巡檢**
```bash
lumos lint <節點>                # 單檔快檢(標籤/格式/合約/可逆性)
lumos doctor [--ci] [--suggest]  # 全圖健康;--ci = strict + 無色(會擋)
lumos gov [<節點>] [--since N]    # 唯讀治理事件帳:某節點被哪幾道閘攔過、硬擋 vs 軟
```

**安裝 / 生命週期**
```bash
lumos install [--force] · lumos uninstall          # 全域 lumos symlink 到 ~/.local/bin
lumos update [--source PATH] [--no-pull]           # 從 Lumos 唯一源刷新本專案 vendored 工具組
lumos bootstrap [--pull]                           # 一鍵全套
lumos archive [--days N] [--apply]                 # 滾動歸檔老的 pass Verification(活守衛受保護)
```

### 卸載

Lumos 是兩層安裝,對應兩個指令:

- **專案層**(本 repo 的 hooks/工具組/CLAUDE.md 注入/圖譜):在專案內跑
  ```bash
  lumos deinit              # 完整逆轉 init:拆閘 + 移工具組 + 剝 CLAUDE.md 區塊 + 刪圖譜(互動確認)
  lumos deinit --keep-graph     # 保留圖譜,只拆其餘
  lumos deinit --dry-run        # 只預演,不改動
  lumos deinit -y               # 跳過互動確認(CI/非互動環境用)
  lumos deinit --source <path>  # 指定 Lumos 來源(自我保護比對用)
  ```
  deinit 不自動 commit、不碰機器共用項;偵測到 standalone vault(圖譜=repo 根)會自動保留圖譜以防誤刪整個 repo。
- **機器層**(全域 `~/.local/bin/lumos`、user-scope skills):`lumos uninstall`。

> 完整卸載 = 在每個專案跑 `lumos deinit`,最後 `lumos uninstall` + 視需要 `rm -rf ~/harness/lumos-toolchain`。

權威清單以 `lumos --help` 為準。

---

## 8. 治理事件帳(`lumos gov`)

治理訊號以前散在各 hook。`lumos gov` 是**唯讀彙整器**,讀三個本機 JSONL:

- `docs/.bypass-log.jsonl` —— L2 pre-commit 繞過(post-commit 寫)
- `docs/.rot-queue.jsonl` —— L3 verification-rot 發現
- `docs/.governance-log.jsonl` —— `doctor --ci` 發現(Check T / Check R),單一寫者

```bash
lumos gov                # 全部 gate 事件的時間軸
lumos gov OrderService   # 這節點被哪幾道閘攔過、硬擋 vs 軟、附日期
```

> 這是**本機開發可見性**工具(三檔皆 gitignore),不是合規物。L2 繞過事件無 node、L3 以 Verification 路徑為鍵,故對 Systems 節點的 per-node 視圖是部分的——輸出會標明。

---

## 9. 更新方式

- **skills + 全域 CLI**(symlink):`git -C ~/harness/lumos-toolchain pull`——即時,免重裝。
- **某專案的 vendored 工具組 + `CLAUDE.md` 紀律區塊**:在該專案跑 `lumos update`(拉 Lumos 源、重 vendor、重注入)。圖譜資料受保護。

---

## 10. 設計原則

- **DRY / YAGNI / TDD**、頻繁提交;CLI 純標準庫、可在 CI 跑。
- **別治理過頭。** 只標載重的;軟的維持軟;不疊沒有對等價值的 ceremony。
- **誠實的天花板。** 工具證的是*形式*(測試存在、回退有寫、乾淨 agent 審過),不是*validation*(規則符不符合今天的業務、回退跑不跑得動)——那留給人。
- **maker ≠ checker。** 沒有標準答案的判斷(這是不是真合約?測試是不是套套邏輯?)交給無脈絡的獨立 agent,不是作者本人。

---

## 邊界與延伸閱讀

Lumos 只放**通用的圖譜工具組**。各專案**自己的東西不進這裡**:業務圖譜內容、app 的發版/部署腳本(如 `release.sh`)、技術棧 skill(vue/csharp 等 project-scope skill)。

- 上手細節:[ONBOARDING.md](ONBOARDING.md)
- 架構全景:[ARCHITECTURE.md](ARCHITECTURE.md)(唯一源→兩種 scope→消費端、生命週期指令、子命令、強制力管線)
- 與 SDD 的差異:[SDD-vs-Lumos.md](SDD-vs-Lumos.md)
