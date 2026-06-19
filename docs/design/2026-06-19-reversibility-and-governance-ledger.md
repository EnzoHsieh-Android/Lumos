# 設計:① 可逆性(Check R)+ ③ 可查詢治理事件帳

- 日期:2026-06-19
- 狀態:設計定版(已過 Sonnet 對抗審計,審計發現已吃進本版)
- 動機來源:2026-06-19 AI 治理日報(reversibility + audit-trail 兩軸,點名為 lumos 方法論盲點)
- 審計:見本檔末「審計修正紀錄」

## 0. 動機與範圍

治理日報指出方法論兩個盲點:四道把關只問「有沒有寫、寫得真不真」,不問「**改動能不能安全收回**」(可逆性);治理訊號散在多個 hook,無法「**一次查某節點歷來被哪幾道閘攔過**」(稽核軌跡)。本設計補這兩軸,**一起做**。

**核心原則(貫穿全設計)**:延續既有 `★INVARIANT★→[test:]→[audit:]` 的「標記+行內指針+doctor/lint 強制」慣例;**防治理過頭**——只標已知危險、軟的維持軟、不疊多餘 ceremony;誠實標明工具天花板(證明「有寫」≠ 證明「能用」)。

非目標(v1 明確不做,見 §5)。

## 1. 功能 ①:可逆性(doctor 新增 "Check R")

### 1.1 標記(KEY 行前綴,僅限 Systems 節點)
與 `★INVARIANT★`/`★DEBT★` 同軸不同義,各自成一條 KEY 行:

```
KEY:★IRREVERSIBLE★ 跑 schema 遷移 v3→v4 [rollback:decisions]
KEY:★CHECKPOINT★   部署到 lab2 測試機     [rollback:重新部署上一版 tag]
```
- `★IRREVERSIBLE★`:收不回(上架、prod DB 遷移)。必須帶 `[rollback:]`。
- `★CHECKPOINT★`:改了難救,動手前先存還原點。建議帶 `[rollback:]`(缺=warning)。
- **未標 = 可逆**(git/測試級,放手)。遵循既有「不確定就不標」哲學。
- **僅限 `type: system`**:Verification 無 summary、Issue/decisions 另有歸屬。標在非 Systems → lint 報「標錯節點型別」。

### 1.2 回退路徑 — 兩個分開的機制(審計 R2-BLOCKER-B:勿混為一談)
這是**兩個不同結構上的兩件事**,實作要分清:

**(A) KEY 行行內指針 `[rollback:<ref>]`**(在 summary block 的 KEY 行尾,對偶 `[test:]`):
- 用**獨立 extractor `reversibility_rollback_ref(line) → str|None`**(對偶 `invariant_test_refs`),**自己剝自己的 tag**。
- **不碰** `INV_TAG_RE`/`strip_test_refs`/`extract_contracts`(那些是 ★INVARIANT★ 家族的,維持原狀;避免 R2-MINOR-1 的 guard bind 比對語義被動到)。

**(B) `decisions[].rollback` 欄位**(frontmatter,放實際回退 SQL/補償步驟):
- block scalar 支援:`parse_decisions` 把它當 decision item 的 sub-key 解析(`m_kv` + block-scalar 路徑本來就吃,已驗;只是要確認 `rollback` 不被當未知鍵丟掉)。

**解析/「算數」規則(MAJOR-3 定案 + R3-B2 明訂)**:
- **v1 唯一支援的 ref 形式 = `[rollback:decisions]`**,語義=「本節點 `decisions[]` 有 ≥1 條非空 `rollback` 內容」。判定即 `any(_nonempty(d.get("rollback")) for d in parse_decisions(...))`;`_nonempty` 對 str/block-scalar 都 strip 後非空。
- **其他 ref 值(非字面 `decisions`)一律視為「未解析」**(irreversible→error、checkpoint→warning)。**不**做 decisions 子字串比對(避開 `[test:]` B6 脆弱)。`[[Verification/…]]` 之類的外部 ref target 留待 v2,v1 不支援。
- 不能只是「冒號後有字」——要求 decisions 真有實質回退內容。

### 1.3 強制(doctor Check R + lint 同步)
| 情況 | 等級 |
|---|---|
| `★IRREVERSIBLE★` 無 `[rollback:]`,或指針解析不到實質 rollback(§1.2) | **error**(doctor --ci / pre-push 擋,同裸合約) |
| `★CHECKPOINT★` 無 `[rollback:]` | **warning**(文件性,不擋) |
| `★CHECKPOINT★` 有 `[rollback:]` 但解析不到實質 rollback | **warning**(懸空回退) |
| `★CHECKPOINT★`/`★IRREVERSIBLE★` 出現在非 Systems 節點 | **error**(標錯型別) |

型別檢查要防 `type` 為 None/非字串(比照 `cmd_lint` 的 `isinstance(t, str)`,R2-MAJOR-4)。

**warning 不可誤擋(R3-MAJOR-3)**:`run_doctor` 既有 `warn()` 一律 `issues += len(...)` → 任何 warn 在 `--ci` 下會 rc1。CHECKPOINT 類 warning **必須不計 issues**,故新增 `warn_soft()`(印出但不動 `issues`);Check R 只對 error 級(irreversible 缺實質 rollback、標錯型別)呼叫 `warn()`,對 checkpoint/懸空呼叫 `warn_soft()`。

### 1.4 天花板(必須在 skill/Check R 訊息寫明;措辭不可與 §1.3 硬擋矛盾)
硬擋的語義是「**逼你在動不可逆動作前,先寫下 undo 路徑**」——同 `[test:]` 逼你綁一個測試、`[audit:]` 逼你找外人審。它**證明你寫了補償步驟**,**不證明補償跑得動、不證明與現行 schema 一致**(那是 validation,工具到不了)。所以:**「有 [rollback:]」= 你想過並記錄了回退,≠「驗過能用」**。別把「文件存在」當「執行保證」。(R2-MAJOR-3:此措辭與 §1.3 硬擋一致——硬擋的是「有沒有寫下實質 undo」,不是「undo 能不能跑」。)

## 2. 功能 ③:可查詢治理事件帳(`lumos gov`)

### 2.1 架構:唯讀彙整器(不合併寫入路徑)
**不**把多個 hook 的寫入合併成單一檔(避開 bash+python 多寫者搶檔的 race / schema 不一)。改為:
- 既有來源**維持原樣**:`docs/.bypass-log.jsonl`(L2 繞過,post-commit 寫)、`docs/.rot-queue.jsonl`(L3 rot,verification-rot-check 寫)。
- **新增單一寫者**:`doctor`(python,唯一寫者→無 race)**只在 `--ci`** 把本輪 findings append 到 `<vault.parent>/.governance-log.jsonl`;**純 `lumos doctor`(無 --ci)不寫**(R2-MINOR-2)。schema:`{ts, commit, gate, kind, hard, nodes}`(gate ∈ check-t/check-r/lint…;kind ∈ blocked|warned;hard bool)。
- **寫入 plumbing(R3-BLOCKER-1)**:`run_doctor` 目前簽名是 `(env, strict, color, suggest)`,且 `strict` 同時被 `--strict` 和 `--ci` 設(`main` 的 `strict=args.strict or args.ci`)。要**新增獨立參數 `ci: bool`** 傳進來,只在 `ci=True` 寫(`--strict` 不寫)。commit hash:寫入區塊內 `subprocess git rev-parse --short HEAD`(**非 git repo / 取不到 HEAD → 該次跳過寫入,不報錯**)。路徑 `env.vault.parent / ".governance-log.jsonl"`。
- **dedup 在讀時做,不在寫時做**(R2-MAJOR-2):doctor 純 append(不必每次 push 讀全檔);`lumos gov` 顯示時才 dedup,key = `(commit, frozenset(nodes), gate, kind)`(R4-nit:用整條 nodes 集合,非單一 node)。`nodes` **存 bare stem**(R4-nit:寫入時即 stem 化,讀時直接比,免兩端格式不一)。成長控制:gitignore local-only;`gov` 預設 `--since 90`(**單位:天**),governance-log 輪替上限 `2000` 筆(超過截舊,比照 rot-check 的 CACHE_MAX_ENTRIES 量級)。
- `lumos gov [<node>] [--since N]`:**唯讀**。`gov`(無 node)= 三來源全合併、依 `ts` 排序(commit 各源短碼長度不一,不靠 commit join,只時間軸排序)。`gov <node>` = **以 stem/basename 正規化比對**(R3-MAJOR-4:rot-queue 的 `verification` 是 repo 相對 `docs/<vault>/Verification/foo.md`、節點是 vault 相對 `Verification/foo` — 統一取 basename stem 比;governance-log 的 `nodes` 同樣 stem 化比)。bypass 無 node 欄→不進 per-node。**v1 不載 vault graph 做 Systems↔Verification 反查 join**(R2-MAJOR-1)。輸出**明確標示限制**:bypass 無 node、rot-queue 以 Verification 為鍵,故對 Systems 節點的 per-node 視圖是**部分**的。

### 2.2 誠實表述(修正原提案的過度宣稱)
此帳是**本機開發可見性**工具(三檔皆 gitignore、local-only),**不是**法規稽核合規物(團隊間各自的 log 不會收斂、清機即失);**移除**原提案的「歐盟 Art.12 合規」大旗。
已知限制:L2 繞過事件的 `nodes` 常為空(commit→節點映射不可靠),故 `lumos gov <node>` 對 bypass 類事件是部分視圖——`gov` 輸出要標明此限制。

## 3. ① 餵 ③
Check R 的 findings 經 §2.1 的 doctor 寫者進 `governance-log` → 自動出現在 `lumos gov`。不需額外接線。

## 4. 橫切要求:新標籤同步到所有面 + 防漂移
新增的 `★CHECKPOINT★`/`★IRREVERSIBLE★`/`[rollback:]` 必須同步到:
1. `scripts/templates/graph-discipline.md` 速查表
2. `skills/lumos-project-notes/SKILL.md` 寫入規則(新增一節,對齊 `[test:]`/`[audit:]` 既有節)
3. `lumos new` 的 `NEW_HINT`(system 類提示提到可逆性)
4. `lumos lint`(Check R 的單檔版)

**唯一機器源 + 防漂移**:`scripts/lumos` 的 regex/常數為機器唯一源。**漂移偵測測試(具體可寫,R2-MAJOR-5)**:對每個機器強制的 marker 字串(`★CHECKPOINT★`、`★IRREVERSIBLE★`、`[rollback:`)斷言它**同時出現在** `skills/lumos-project-notes/SKILL.md` 與 `scripts/templates/graph-discipline.md`(distinctive Unicode/字串 substring presence)。單向:**碼有強制 → 文件必須提**(防文件落後於碼)。`NEW_HINT["system"]` 草稿補一行,例:`可逆性: 不可逆動作(prod遷移/上架)標 ★IRREVERSIBLE★ + [rollback:decisions];改了難救標 ★CHECKPOINT★`。

## 5. 範圍 / YAGNI(v1 明確不做)
- ❌ **commit-time 軟提醒**(原 Q1「混合」的那半):code→節點靠檔名 stem 配對不可靠(migration 檔 stem 配不到 Systems 節點),漏判+誤報,純噪音。可逆性靠 Check R(push 硬擋)+ lint 足夠。
- ❌ **`[rollback:]` 的寫入指令**(對比 `guard bind` 寫 `[test:]`):`[rollback:]` 是指針不是驗證的測試,**v1 手寫進 KEY 行 + lint 檢查**即可;且不污染 `guard`(★INVARIANT★ 家族)命名空間。R3-MINOR 指出此 write-side 不對稱——明確接受,寫入工具留 v2。
- ❌ **`rollback_verified` 必填欄位**:再疊一層 ceremony,過頭。只把天花板講白,不加欄位。
- ❌ **合併 bypass-log/rot-queue 寫入路徑**:見 §2.1。

## 6. 受影響的 callsite(R1-BLOCKER-1 + R2-BLOCKER-A:走平行路,別動既有合約管線)
**核心決定:可逆性走自己的平行函式,完全不碰 `extract_contracts` 管線。** 這樣 `extract_contracts` 的 7 個 callsite(doctor Check T、`cmd_contracts`、`cmd_guard_list`、`cmd_guard_bind`、`cmd_guard_audit`、`cmd_guard_trace`、`_html_model`)**全部維持原狀、只認 ★INVARIANT★/★DEBT★**,零靜默失效風險。

新增(`scripts/lumos`):
- `CHECKPOINT_RE` / `IRREVERSIBLE_RE`(寫死 regex,對齊 `INVARIANT_RE` 形狀)
- `reversibility_rollback_ref(line) → str|None`(獨立 extractor,自剝 `[rollback:]`)
- `extract_reversibility(note) → [(marker, text, rollback_ref), …]`(平行於 `extract_contracts`,供 Check R + lint)
- `run_doctor`:**簽名加 `ci: bool`**(與 `strict` 分開);新增 `warn_soft()` 閉包(印但不計 `issues`);新增獨立 **Check R 區段**(不混進 Check T,error 用 `warn()`、checkpoint/懸空用 `warn_soft()`);`if ci:` 區塊內 `git rev-parse --short HEAD` 後 append governance-log(取不到則跳過)。`main` dispatch 傳 `ci=args.ci`
- `cmd_lint`:可逆性檢查 + 標錯型別檢查(用上面獨立 extractor,**不動** `INV_TAG_RE`/`strip_test_refs`)
- `parse_decisions`:確認吃 `rollback` sub-key(含 block scalar;只是確認不被當未知鍵丟)
- `cmd_gov`(新)+ `gov` subparser + dispatch
- 文件四面(§4)+ `NEW_HINT["system"]` 補一行

明確不動:`extract_contracts`、`INV_TAG_RE`、`strip_test_refs`、`invariant_test_refs`、guard 家族、archive 活守衛。
v1 不做(YAGNI):`cmd_contracts`/`_html_model` 顯示可逆性標記(Check R + lint 已涵蓋強制;要在登記簿/視圖呈現留待之後)。

## 7. 驗收標準(測試,對齊 test_lumos.py 既有風格)
- Check R:`★IRREVERSIBLE★` 無 `[rollback:]` → doctor --ci rc1 + 報錯;`[rollback:]` 指到的 decisions 無非空 rollback 內容 → **仍 error**(R2-MAJOR-3 resolve-to-substance);指到有實質 rollback → 0 問題。
- `★CHECKPOINT★` 無 `[rollback:]` → warning 不擋(rc0);有指針但無實質 → 懸空 warning。
- 可逆性標記放 Issue/Verification → lint 報標錯型別;節點 `type` 缺失/非字串 → Check R 不崩、不誤報(R2-MAJOR-4)。
- `parse_decisions` 讀 `rollback`(含 block scalar):**走 Check R 整合測**間接驗(test harness 是 subprocess-only、不 import)——irreversible + `[rollback:decisions]` + decisions 有非空 rollback block scalar → rc0;rollback 空 → rc1。
- `lumos gov`:用 `root/docs/<slug>` **全專案結構**(比照 `t_archive_live_guard_protected`,非 bare `mkvault`)建 bypass + rot + governance-log 三來源 fixture → `gov`/`gov <node>` 正確合併、stem 比對、分硬軟閘、標明 bypass node 限制。
- `★CHECKPOINT★` 只 warn 的回歸:確認 `doctor --ci` 對「只有 checkpoint 缺 rollback」仍 **rc0**(驗 `warn_soft` 不誤計 issues)。
- lint 單檔版抓上述 Check R 同類錯。
- 漂移偵測測試(§4):skills/ 不存在時**優雅跳過**(vendored 部署)。
- 既有 130 測試全綠(回歸)。

## 審計修正紀錄(Sonnet 對抗審計,2026-06-19)
- BLOCKER-1 callsite 列舉 → §6。
- BLOCKER-2 [rollback:] 改節點層級解析 + parse_decisions 認 rollback → §1.2。
- BLOCKER-3 ③ 改唯讀彙整器、不合併寫入 → §2.1。
- MAJOR-4 切掉 commit-time 軟提醒 → §5。
- MAJOR-5 唯一機器源 + 漂移偵測測試 → §4。
- MAJOR-6 可逆性標記僅限 Systems → §1.1。
- MAJOR-7 天花板講白、不加 rollback_verified → §1.4 / §5。
- MINOR-9 移除 Art.12 合規宣稱,降為本機可見性 → §2.2。
- 駁回:審計建議的 `rollback_verified` 必填欄位(過頭)。

### 第二輪(re-audit 修正版,fresh agent)
- R2-BLOCKER-A:可逆性走平行函式 `extract_reversibility`,**不碰** `extract_contracts` 7 個 callsite → §6 重寫。
- R2-BLOCKER-B:KEY 行 `[rollback:]`(獨立 extractor)與 `decisions[].rollback`(欄位)是兩個機制,分清 → §1.2。
- R2-MAJOR-1:`gov <node>` v1 只直接匹配、不載 vault graph join;標明 rot-queue/bypass 限制 → §2.1。
- R2-MAJOR-2:dedup 改讀時做、doctor 純 append 只在 --ci 寫、加 --since/輪替 → §2.1。
- R2-MAJOR-3:irreversible 硬擋 + 要求 `[rollback:]` 解析到**實質** rollback;§1.4 措辭改成不與硬擋矛盾 → §1.2/§1.3/§1.4。
- R2-MAJOR-4:Check R 型別檢查防 None/非字串 → §1.3。
- R2-MAJOR-5:漂移測試給出具體規則(marker 字串須出現在兩份文件)→ §4。
- R2-MINOR:doctor 非 --ci 不寫、NEW_HINT 草稿、不動 INV_TAG_RE(故 guard bind 比對語義不受影響)→ §2.1/§4/§6。
- 第二輪結論:第一輪架構修正 sound、無回歸;本輪修的是新設計引入的縫隙。

### 第三輪(re-audit,fresh agent)— 全為 plumbing 層,無架構問題
- R3-BLOCKER-1:`run_doctor` 寫 governance-log 需 commit hash + 與 git 互動;加 `ci:bool` 參數、只在 ci 寫、寫前 `git rev-parse`(取不到跳過)→ §2.1/§6。
- R3-BLOCKER-2:`[rollback:]` 解析明訂 v1 唯一形式 `[rollback:decisions]`、其餘視為未解析 → §1.2。
- R3-MAJOR-3:CHECKPOINT warning 不可走會計 issues 的 `warn()` → 新增 `warn_soft()` → §1.3/§6。
- R3-MAJOR-4:`gov <node>` 改 stem/basename 正規化比對(rot-queue 路徑格式不同)→ §2.1。
- R3-MINOR:parse_decisions 測走 Check R 整合測;gov 測用全專案結構;drift 測 skills 缺則跳過;`[rollback:]` v1 無寫入指令(手寫)→ §5/§7。
- 第三輪結論:收斂中——已無架構級問題,剩的是實作 plumbing,已全部寫進 spec。

### 第四輪(收斂確認,fresh agent)— ✅ CONVERGED
- 三輪修正逐一**對著 code 驗證屬實**(ci 參數 plumbing、warn_soft 保 rc0、parse_decisions 吃 rollback、env.vault.parent=docs/)。
- 無 blocker、無 major。3 個 trivial nit 已即時補:dedup key 用 `frozenset(nodes)`、`nodes` 存 bare stem、`--since` 單位=天 + 輪替上限 2000。
- 第四輪結論:**implementable as-is**,審計通過,迴圈結束。
