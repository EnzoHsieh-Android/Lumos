# 設計:pitfalls lint 整合(pitfalls-lint-adapter)— `--diff` 從 regex 提示器升級為 lint 整合器

- 日期:2026-07-04
- 狀態:draft(design-loop 前)
- 動機來源:`Projects/pitfalls-lint-integration_計劃` 第 ① 塊(地基)。brainstorm(2026-07-04)收斂:pitfalls 不是規則庫、是提問+整合+接線;通則(ruff S113/SIM115)與偏科(compose-rules/detekt/eslint)社群 linter 已有且 AST 級更準,兩者都該讓給 linter(composition over invention);整合共通格式=SARIF。
- loop_id:pitfalls-lint-adapter
- 計劃回指:docs/lumos-toolchain-knowledge/Projects 的 pitfalls-lint-integration_計劃 節點。

## 目標(一句話)

`pitfalls --diff` 新增 lint 整合:偵測 diff 涉及的技術棧 → 跑專案宣告的一組 lint 指令(各輸出 SARIF)→ lumos 解析合併 SARIF、過濾到 diff 觸及行 → 併進既有 manifest 餵 reviewer/code-loop;無宣告則退回現有 regex-only(向後相容)。lumos 只解析 SARIF 一種格式、不內建任何棧的規則。

## 前提與既驗事實(2026-07-04)

- **pitfalls --diff 現況**:`scripts/lumos` 的 `_pitfall_diff_mode(diff_range, repo_root, as_json)` 掃 `git diff -U3 <range>` 新增行、跑 `_PITFALL_DIFF_PATTERNS`(6 條 regex)、`@@` 行號推導、過濾繼承 Check H(skip .md/.txt/.rst+測試檔+註解行)、輸出 manifest `{file,line,class,pattern,question}`+尾行 `tier: high|standard`、rc 恆 0。本塊在此函數內擴充,不改既有 regex 骨架。
- **SARIF 是 OASIS 標準**(2020,v2.1.0):JSON 格式;`runs[].results[]` 每筆有 `ruleId`、`message.text`、`locations[].physicalLocation.artifactLocation.uri`(檔)與 `region.startLine`(行)、`level`(error/warning/note)。ESLint/detekt/Roslyn/Sonar 皆可輸出。lumos 以 stdlib `json` 解析,零依賴。
- **一棧多 linter 並存**:C#(Roslyn+StyleCop+Sonar+Roslynator)、Vue(ESLint+plugins)、Android(Lint+detekt+ktlint)——故指令是「一棧一組(list)」。
- **lumos 語言無關原則**:`_VENDORED_TOOLKIT` 不含任何棧規則;guard 範本亦專案自備(`.lumos/guard-templates/`)——lint 指令同理由專案宣告(`.lumos/lint.json`),lumos 不猜、不內建。
- **repo 解析**:`_anchor_repo_root(repo)` 既有(refcheck/anchor/pitfalls 共用)。

## 方案評比與選擇

| 方案 | 內容 | 判定 |
|---|---|---|
| **A(選)** | 專案宣告 `.lumos/lint.json`(副檔名→一組 lint 指令,各需輸出 SARIF);pitfalls 跑之、解析合併 | **選**:一次配、明確、跨棧統一;lumos 只讀宣告跑指令、只解 SARIF;無宣告退回 regex(向後相容);對齊 guard-templates 專案自備先例 |
| B(否決) | 自動偵測(看到 detekt.yml/.eslintrc 就推指令) | 否決:指令與參數(尤其 SARIF 輸出旗標)猜不準、脆;不同專案同工具配置差異大 |
| C(否決) | 只印「建議手動跑 detekt」不自己跑 | 否決:沒真接上,lint 結果進不了 manifest/code-loop,價值近零 |

## 範圍(組件)

### ① `.lumos/lint.json`(專案宣告檔,repo 側、非 vendored)
```json
{
  "kt":  ["<detekt 指令,輸出 SARIF 到 stdout 或指定檔>"],
  "vue": ["<eslint -f @microsoft/sarif ...>"],
  "cs":  ["<dotnet build -p:ErrorLog=<file>.sarif ...>"]
}
```
- key = 副檔名(不含點,如 `kt`/`vue`/`cs`/`py`);value = 該棧的一組指令(list,支援多 linter 並存)。
- 每個指令須產 SARIF;產物落點約定:指令印到 stdout(pitfalls 讀 stdout)**或**寫到指令內指定的臨時 SARIF 檔再由 pitfalls 讀(兩式擇一,見組件 ③ runner 契約)。
- lumos 不驗指令內容、不猜參數——宣告是專案責任(同 guard 範本專案自備)。

### ② 技術棧偵測(哪些 lint 指令要跑)
- 從 diff 新增行涉及的檔案副檔名集合 → 對照 `.lumos/lint.json` 的 key → 命中的棧的指令集合即待跑。
- diff 無觸及任何宣告棧的檔 → 不跑 lint(只 regex)。

### ③ lint runner + SARIF 解析(runner 契約)
- 對每個待跑指令:`subprocess.run(指令, cwd=repo_root)`;**約定指令將 SARIF 寫到 pitfalls 指定的臨時檔**(pitfalls 以 `{LINT_SARIF_OUT}` 佔位符注入路徑到指令字串、指令用它當輸出路徑;無佔位符則讀 stdout)——確定性拿到 SARIF、不猜工具預設落點。
- 解析 SARIF:`json.load` → 走 `runs[].results[]` → 每筆映射 claim `{file, line, source, rule, message}`:
  - `file` = `locations[0].physicalLocation.artifactLocation.uri`(正規化為 repo 相對路徑)
  - `line` = `locations[0].physicalLocation.region.startLine`(缺則 0)
  - `source` = `runs[].tool.driver.name`(工具名,如 detekt/ESLint)
  - `rule` = `ruleId`;`message` = `message.text`(截 120 字)
- 指令失敗(rc≠0 且無 SARIF 產出)/SARIF 解析失敗 → 印警示、跳過該指令、續跑其餘(容錯,不擋)。

### ④ 過濾到 diff 觸及行
- 從 `git diff` 算出「新增行的 (檔, 行號) 集合」(既有 `@@` 推導已算 new_ln,復用)。
- SARIF finding 只保留 `(file, line)` 落在 diff 新增行集合內者(對齊 pitfalls「只提示本次改動風險」,不倒入專案舊 lint 債)。行號比對容差:同檔且行號 ∈ 新增行集合。

### ⑤ 合併 + tier + 輸出
- lint claims 與既有 regex claims **合併**進同一 manifest;每筆帶 `source`(`lint:<tool>` 或 `pitfalls-builtin`)區分。
- manifest schema 擴充為 `{file, line, source, ...}`——regex claim 補 `source: "pitfalls-builtin"`、保留原 `class/pattern/question`;lint claim 用 `source/rule/message`(無 class/question——lint 自帶訊息)。**向後相容**:既有欄位不刪。
- tier:regex 或 lint 任一有 claim → high;皆無 → standard。rc 恆 0。
- `--json`:`{claims:[...], tier, lint_ran: [<跑過的指令摘要>], lint_skipped: [<失敗跳過的>]}`(新增 lint_ran/lint_skipped 供人看有沒有真跑到)。

### ⑥ 無宣告 / 無 lint 的 fallback
- `.lumos/lint.json` 不存在 → 完全走現有 regex-only 路徑,行為與本塊前分毫不變(回歸釘)。
- 有宣告但 diff 未觸及宣告棧 → 只 regex。

## canary 相容性(不可違反)
- 本塊只擴充 `--diff`(代碼層提示),不碰 spec 模式/`--check`/canary 保留地。
- lint 跑真 diff 涉及的真檔,與 code-loop 的 bug canary(工作副本層)不相交。

## 邊界 / 非目標(YAGNI)
- ❌ 不自動偵測 lint 指令(方案 B);不內建任何棧規則。
- ❌ 不做 SARIF 全欄支援:只取 file/line/ruleId/message/level/tool.name,其餘(codeFlows/fixes/relatedLocations)忽略。
- ❌ 不縮/退役既有 regex pattern 表(留計劃後續;本塊只「共存合併」,pattern 表縮是獨立小改)。
- ❌ 不做 lint 結果快取(每次真跑;效能問題留 v2)。
- ❌ 不裝/不管理 linter(專案自己裝;沒裝→容錯跳過)。
- ❌ 不改 spec 模式、`--check`、gate、code-loop skill。

## 誠實天花板
1. **只收 diff 觸及行**:漏「本次改動害他處 lint 壞」(如改了共用函數簽名、他處 call site lint 紅但不在 diff)。換得「不倒入舊債」的聚焦,低風險可接受。
2. **SARIF level 語意各工具不完全一致**:error/warning/note 的界線工具間有差;本塊不依賴 level 分級(命中即進 manifest、tier 只看有無),迴避此不一致;若未來用 level 排序需另議。
3. **要專案先配 `.lumos/lint.json`**:一次性,但 Android/Vue/C# 專案本就該有 lint 配置;未配則本塊等於沒開(退回 regex)——漸進採用,不強迫。
4. **runner 執行 shell 指令**:`.lumos/lint.json` 的指令由專案作者寫、lumos 照跑——等於信任專案宣告檔(同 guard 範本、hooks)。非對抗場景(自己的 repo),威脅模型是配錯非惡意注入。
5. **行號比對容差**:SARIF 報的行 vs diff 新增行,若 linter 報的是「區塊起始行」而該行不在 diff 但區塊跨進 diff,可能漏;本塊只做精確行比對,粗放匹配留 v2。

## 測試策略
沿 `scripts/test_lumos.py` CLI subprocess 風格,git fixture:
1. **無 .lumos/lint.json → regex-only**:現有 t_pitfalls_diff 行為分毫不變(回歸)。
2. **宣告檔解析**:造 `.lumos/lint.json`,副檔名→指令集合正確讀取。
3. **SARIF 解析→claim 映射**:餵一個假 SARIF(含 2 findings)給 runner(用 `echo` 或 `cat` 假指令輸出到 `{LINT_SARIF_OUT}`),驗 claim 的 file/line/source/rule/message 映射正確。
4. **diff 行過濾**:SARIF finding 有的行在 diff 新增行內、有的不在 → 只保留在內的。
5. **lint+regex 合併**:同 diff 既命中 regex 又有 lint finding → manifest 兩者都在、source 欄區分。
6. **技術棧偵測**:diff 只碰 .py、宣告只有 kt → 不跑 lint(lint_ran 空)。
7. **指令失敗容錯**:假指令 rc≠0/無 SARIF → lint_skipped 記錄、rc 仍 0、regex claims 仍在。
8. **回歸**:兩套件全綠。

## 知識同步影響
| 受影響文件 | 需同步什麼 |
|---|---|
| `skills/lumos-project-notes/SKILL.md` | pitfalls 指令表補「--diff 支援 .lumos/lint.json lint 整合(SARIF)」 |
| `skills/lumos-code-loop/SKILL.md` | pitfalls --diff manifest 現含 lint 來源(source 欄),reviewer 鏡頭涵蓋 lint findings |
| `scripts/templates/graph-discipline.md` | 終審前 pitfalls --diff 段補一句「專案配 .lumos/lint.json 則自動吃 linter」 |
| `docs/methodology/圖譜即合約.md` | pitfalls 列補「lint 整合器(SARIF)——吃社群 linter 非自建規則」 |
| `Projects/pitfalls-lint-integration_計劃` | 第 ① 塊 status 更新 done + verified_by 回指本 spec 落地 Verification |

## 審計修正紀錄(design-loop)
(待 design-loop 各輪填入)
