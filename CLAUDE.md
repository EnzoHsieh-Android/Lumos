# CLAUDE.md
<!-- LUMOS:GRAPH-DISCIPLINE:START — 自動注入/更新,勿手改本區塊;改範本 scripts/templates/graph-discipline.md -->
## 核心原則：知識圖譜即唯一真相來源 — 圖譜先行（必讀，優先級最高）

**`docs/lumos-toolchain-knowledge/` 知識圖譜是本專案系統脈絡的唯一真相來源（single source of truth）。** 程式碼只是「現在長這樣」；圖譜才是「**為什麼這樣設計 / 邊界在哪 / 哪些是不可改的合約（★INVARIANT★）/ 驗證過沒**」——這些 code 讀不出來。

### 🟢 圖譜先行（第一動作，不可跳過）

**動任何既有系統之前，你的第一個工具呼叫必須是 `lumos`，不是 grep / Read / Explore / DB 查詢。**

- ✋ **STOP 自檢**：如果你正要 grep code、派 Explore、或查 DB 去搞懂「為什麼這樣 / 邊界 / 合約 / 欄位或狀態語意」——**停**，先 `lumos`，再下 code/DB 驗證。
- **不分任務類型**：開發、重構、**排查、對外支援、呼叫既有 API、查 DB、對帳**——全部算「進場」。看似純操作的任務，只要動手前需要理解系統，就先讀圖譜。（最常被合理化跳過的破口：把任務歸成「只是查資料 / 跑指令」就略過圖譜。別這樣。）
- **入口動作**（不知道該讀哪個節點時）：① `lumos search <關鍵字>` 定位節點 → ② `lumos context <節點>` 掃脈絡（頭部直接攤出 ⚠ 合約）→ ③ `lumos contracts <節點>` 查硬合約（★INVARIANT★ 改＝breaking）→ 然後才 grep code / 查 DB 驗證細節。
- 「先查圖譜」不是禮貌建議，是**順序規定**：圖譜先給你合約與邊界，code/DB 只拿來印證，不是拿來重新發明「本來就該這樣」。
- **自動輔助（不取代主動查）**：`impact` PreToolUse hook 會在你 Edit/Write/MultiEdit 一支 code **動手前自動注入**「受影響的關聯節點（直接/間接）+ 相關事故（`pitfall_when` 命中）」——看到就順手判：這些節點/事故會不會被你這次改動波及、需不需同步。它是**輔助推播**，不取代你主動 `lumos context`/`contracts` 查合約（hook 只推「碰到的」，合約邊界仍要自己查）。

### 其餘原則

- **唯一真相**：圖譜與其他文件 / 記憶 / 臆測衝突 → 以圖譜為準。
- **實時更新（不可延後）**：影響系統行為 / 決策 / 驗證的 code 變更，**同一次工作內**同步更新圖譜（不是之後補、批次補）。pre-commit gate 硬擋「改 code 沒帶圖譜更新」。
- **退場必寫**：做完用 lumos 把脈絡（決策 / 驗證 / 合約）寫回。
- **設計動筆前先問世界（PRIOR-ART 三問）**：① 最小解在哪一層（既有閘/一行 config/既有機制小修 → 就做那個，別造新機制）② 世界解過沒（真搜 GitHub/文獻，非憑印象）③ 裁定 = borrow-design（預設，借設計教訓原生實作）/ build（真沒輪子）/ adopt（例外須理由——零依賴家規下幾乎恆排除）。答案一行 `PRIOR-ART:` 記進計劃節點。
- **設計 spec 完成 → 進實作前**：先用 `lumos-design-loop` skill 把它過 canary-護的審計 loop 到 `lumos loop status` 收斂（trivial 改動可跳並註明）。
- **計劃/設計也歸圖譜**：任何設計 / spec / 計劃產出（**不論來源——brainstorming、writing-plans、OpenSpec、其他 SDD / spec-driven 工具皆同**）一律寫成 lumos 計劃節點（`Projects/<主題>_計劃`，`type: project`），**不寫 `docs/superpowers/specs/`、`openspec/` 或其他 repo 路徑**；落地的 Verification 以 `plan_refs` 回指（意圖鏈，graph-doctor Check 4 把關）。任何工具內建的 spec 落點一律以此覆寫——「圖譜即真相」涵蓋計劃，不只 code。

### 寫入時的標籤規範（速查，動筆前掃一眼；完整規範見 `lumos-project-notes` skill）

**summary 區塊符號行**（Systems/Issues 的 `summary: |-` 內，每行一個前綴）：

| 前綴 | 用途 | 前綴 | 用途 |
|------|------|------|------|
| `FLOW:` | 核心流程 `a→b→c` | `VERIFY:` | 驗證紀錄 `[[..]]` |
| `KEY:` | 關鍵概念/欄位 | `DECISION:` | 決策簡版指針 |
| `DEP:` | 依賴模組 `[[..]]` | `FLAG:` | 語意標記 `TECHNICAL`/`DECISION`/`ORIGIN` |
| `TEST:` | 測試狀態 | `AUTH:` | 認證方式 |

**合約鏈（最重要，KEY 行前綴 + 行尾指針）**：
```
KEY:★INVARIANT★ <業務合約,改=breaking> [test:測試方法名] [audit:模型/日期]
                 └ 宣稱            └ 可執行證據(verify) └ 無脈絡獨立 agent 審合法性
KEY:★DEBT★ <已知偶然行為,可改不算 breaking>
```
- `★INVARIANT★` 必綁 `[test:]`(否則 doctor 報裸合約)→ 經獨立審計留 `[audit:]`(否則報未審)。**不確定是不是合約就不標**,嚴禁從 code 反推。

**可逆性(危險動作動手前先寫好怎麼收回,僅 Systems)**:
```
KEY:★IRREVERSIBLE★ <收不回:上架/prod遷移> [rollback:decisions]   # 必綁,否則 doctor Check R 擋
KEY:★CHECKPOINT★   <改了難救:部署測試機>                          # 建議補 [rollback:decisions],缺=提醒不擋
未標 = 可逆(git/測試級,放手)
```
- `[rollback:decisions]` 需本節點 `decisions[]` 有非空 `rollback` 欄位(實際回退 SQL/補償步驟)。**證「有寫下 undo」≠「驗過能跑」**。
- 外部不可逆(信已送出/下游已消費,事後無逆操作)→ 改用 `[guard:decisions]` 記事前守衛(冪等鍵/核可閘);`[guard:]` 僅對 `★IRREVERSIBLE★` 生效,與 `[rollback:]` 兩軌任一合規即放行。
- 綁定/審計走指令(寫後自驗),別手寫:`lumos guard bind <node> "<KEY子字串>" <測試名>` / `lumos guard audit <node> "<KEY子字串>"`.
- `doctor --ci` 的 Check H 會掃 diff、碰 prod/外部 API/寄送時軟提醒「是否漏標 ★IRREVERSIBLE★」(只提醒、不擋)。

**frontmatter 欄位**：`type`(system/verification/issue/project/moc)、`status`(doing/pass/open/done/stale/superseded)、`verified_by`/`plan_refs`/`related`/`tags`(list)、`decisions`(ADR 巢狀)、`valid_under`/`revalidate_when`(重驗條件)、`core_refs`(核心指針,純文字路徑)、`pitfall_when`(事故 Issue 的 pattern-trigger list,`glob:`路徑/`content:`內容-regex → `lumos impact` 進場自動餵該事故;見 lumos-project-notes skill)。
- ⚠ **多個 wikilink 必須是 YAML list,一項一行**(`- "[[A]]"`/`- "[[B]]"`);寫成 `"[[A]], [[B]]"` 單字串會長出 ghost 節點。
- 純量/list/decisions 一律走 `lumos set`/`append`/`decision-add`(安全格式+寫後自驗),別手改 frontmatter。

> 寫完一個節點先跑 `lumos lint <節點>`(單檔快檢:type/summary/★ 格式/裸合約/未審/ghost trap)→ 收尾再 `lumos doctor` 跑全圖;push 前 pre-push 再擋一次(`doctor --ci` + `anchor verify` + tier=high 未過 code-loop 硬擋,詳見下方 skill 表末列)。

### 主動調用 Skill（遇到情境就調用，別憑記憶硬幹）

| 你要做的事 | 必調用 |
|-----------|--------|
| **排查 / 對外支援 / 查 DB / 呼叫既有 API**（動手前要懂為什麼 / 邊界 / 合約）→ **先查圖譜再下 code/DB** | **`lumos-project-notes`**（先 `lumos search`→`context`→`contracts`）|
| 讀圖譜 / 寫筆記 / 巡檢 / 綁合約測試（★INVARIANT★→[test:]）/ 動 `docs/lumos-toolchain-knowledge/` | **`lumos-project-notes`** |
| 跨專案共用業務規則（升格核心 / `core_refs` / 偏離 / 動 `core-knowledge`） | **`lumos-core-knowledge`** |
| **設計 spec 完成 → 進實作前**：把設計過 canary-護的對抗審計 loop 到 `lumos loop status <id> --gate` 收斂才進實作（trivial 改動可跳並註明；spec 高風險建議 `--need 3`）。設計/計劃寫成圖譜計劃節點（`Projects/<主題>_計劃`） | **`lumos-design-loop`** |
| **分支終審前**：`lumos pitfalls --diff <merge-base>..HEAD` 輸出尾行 `tier: high|standard`；`tier: high` → 調用 **`lumos-code-loop`** skill 做對抗代碼審（user-scope skill，每機裝一次；未裝則退回單 reviewer 並提示裝）。專案配 `.lumos/lint.json` 則 `--diff` 自動吃社群 linter（SARIF），命中併進 manifest；無宣告則 regex-only 不變。**pre-push hook 單點把關（blocking）**：tier=high 且無有效 pass/skip 台帳 → rc1 **硬擋 push**；提示三路（跑 `lumos-code-loop` / `lumos code-loop skip --note` / `git push --no-verify`）。（2026-07-06 ADR：撤除每回合 Stop nag——太擾民；push 才是把關時點）。**loop status 收斂後必須 `lumos code-loop pass --note "<理由>"` 記台帳才能 push** | — |

> 圖譜讀寫工具是 **lumos**（`scripts/lumos`，python3 零依賴；細節見 `lumos-project-notes` skill）。`lumos-*` 是 **user-scope skills**（唯一源在 `lumos-toolchain` repo、symlink 進 `~/.claude/skills/`，不在本 repo）——每台機器首次裝一次：`git clone <lumos-toolchain> ~/harness/lumos-toolchain && ~/harness/lumos-toolchain/install.sh`。專案技術棧 skill（如 vue / csharp）見文末〈架構參考 Skills〉。
<!-- LUMOS:GRAPH-DISCIPLINE:END -->
