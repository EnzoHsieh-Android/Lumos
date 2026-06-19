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

### 1.2 回退路徑 `[rollback:<ref>]`
- 行內指針掛在標記的 KEY 行尾,對偶 `[test:]`。
- 解析為**節點層級**(只驗指到的節點/decisions 區塊存在,**不**靠 decisions 子字串精確比對 — 避開 `[test:]` 當初要躲的 B6 脆弱)。`ref` 慣例:`decisions`(指本節點 decisions[])或 `[[Verification/…]]`。
- 實際回退 SQL/補償步驟放 **`decisions[]` 新增的 `rollback` 欄位**(支援 block scalar;`parse_decisions` 要能吃這個 key)。

### 1.3 強制(doctor Check R + lint 同步)
| 情況 | 等級 |
|---|---|
| `★IRREVERSIBLE★` 無 `[rollback:]` | **error**(doctor --ci / pre-push 擋,同裸合約) |
| `★CHECKPOINT★` 無 `[rollback:]` | **warning**(文件性,不擋) |
| `[rollback:]` 指針解析不到節點 | **warning**(懸空回退) |
| `★CHECKPOINT★`/`★IRREVERSIBLE★` 出現在非 Systems 節點 | **error**(標錯型別) |

### 1.4 天花板(必須在 skill/Check R 訊息大聲寫明)
`[rollback:]` 存在**只證明「有人寫了補償步驟的文字」,不證明補償可執行、不證明與現行 schema 一致**。同 `[test:]`(只驗方法存在)/`[audit:]`(只驗非套套邏輯)的天花板。硬擋只是「文件契約」,不是「執行保證」——**嚴禁被誤讀成「有 [rollback:] 就安全」**。

## 2. 功能 ③:可查詢治理事件帳(`lumos gov`)

### 2.1 架構:唯讀彙整器(不合併寫入路徑)
**不**把多個 hook 的寫入合併成單一檔(避開 bash+python 多寫者搶檔的 race / schema 不一)。改為:
- 既有來源**維持原樣**:`docs/.bypass-log.jsonl`(L2 繞過,post-commit 寫)、`docs/.rot-queue.jsonl`(L3 rot,verification-rot-check 寫)。
- **新增單一寫者**:`doctor`(python,唯一寫者→無 race)在 `--ci` 跑時把本輪 findings append 到 `docs/.governance-log.jsonl`,事件 schema:`{ts, commit, gate, kind, hard, nodes}`(gate ∈ doctor 的各 Check:check-t/check-r/lint…;kind ∈ blocked|warned;hard bool)。dedup by (commit, node, gate, kind)。
- `lumos gov [<node>] [--since N]`:**唯讀**讀上述三檔,合併呈現「某節點/全 vault 歷來被哪幾道閘攔過」,分硬閘/軟閘、附時間與 commit。

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

**唯一機器源 + 防漂移**:`scripts/lumos` 的常數/regex 為機器唯一源;`INV_TAG_RE`(剝 `[test:]`/`[audit:]` 的)要加 `[rollback:]`。新增一條**漂移偵測測試**:斷言 skill/cheat-sheet 文件提到的標記集合 ⊆ `scripts/lumos` 實際解析的標記(避免文件寫了、機器不認,或反之)。

## 5. 範圍 / YAGNI(v1 明確不做)
- ❌ **commit-time 軟提醒**(原 Q1「混合」的那半):code→節點靠檔名 stem 配對不可靠(migration 檔 stem 配不到 Systems 節點),漏判+誤報,純噪音。可逆性靠 Check R(push 硬擋)+ lint 足夠。
- ❌ **`lumos guard rollback` 指令**:`[rollback:]` 是指針不是驗證的測試,手寫 + lint 檢查即可;且不污染 `guard`(★INVARIANT★ 家族)命名空間。
- ❌ **`rollback_verified` 必填欄位**:再疊一層 ceremony,過頭。只把天花板講白,不加欄位。
- ❌ **合併 bypass-log/rot-queue 寫入路徑**:見 §2.1。

## 6. 受影響的 callsite(BLOCKER-1:必須逐處改,漏一處=靜默失效)
新 KEY 行前綴必須在以下每處被認得(現都寫死只認 `★INVARIANT★`):
- `scripts/lumos`:`INVARIANT_RE`/`DEBT_RE` 旁新增 `CHECKPOINT_RE`/`IRREVERSIBLE_RE`(寫死 regex,非「parallel」口頭)
- `extract_contracts()` — 抽出可逆性標記(可回傳獨立結構,別硬塞進 invariants)
- `run_doctor` — 新增 Check R 區段
- `cmd_lint` — 可逆性檢查 + 標錯型別檢查;`INV_TAG_RE` 加 `[rollback:]`
- `parse_decisions` — 認得 `rollback` 欄位(含 block scalar)
- `cmd_gov`(新)、`gov` subparser + dispatch、`lint` 既有
- 文件四面(§4)
- **不**動 `guard_bind`/`guard_audit`/`guard_list`/`archive 活守衛`(可逆性不進 guard 家族;但要確認它們不會誤吃到新前綴)

## 7. 驗收標準(測試,對齊 test_lumos.py 既有風格)
- Check R:`★IRREVERSIBLE★` 無 `[rollback:]` → doctor --ci rc1 + 報錯;有 → 0 問題。
- `★CHECKPOINT★` 無 `[rollback:]` → warning 不擋(rc0)。
- 懸空 `[rollback:]` → warning。
- 可逆性標記放 Issue/Verification → lint 報標錯型別。
- `parse_decisions` 正確讀 `rollback`(含 block scalar 多行)。
- `lumos gov`:建構含 bypass + rot + governance-log 三來源的 fixture → `gov <node>` 正確合併、分硬軟閘、標明 bypass 的 node 限制。
- lint 單檔版抓上述 Check R 同類錯。
- 漂移偵測測試(§4)。
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
