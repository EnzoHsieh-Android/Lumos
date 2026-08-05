# Code Review Report — r3 s1 (code-dloop-redesign)

審查對象：`/private/tmp/claude-501/.../scratchpad/codeloop/code-dloop-redesign-r3-s1.patch`
repo：`/Users/enzo/harness/lumos-toolchain`（HEAD=`ba3ae1f`，working tree 有未 commit 變更）

## 重要前置：diff 檔與真實 repo 有一處不符（務必先讀）

在深入審查前，我用 `git diff HEAD -- <三個改動檔>` 產出真實 diff，逐行（`comm -13`/`comm -23`）比對兩份 diff 的 `+`/`-` 內容行，發現**除一處外完全一致**。這唯一的不符點：

診斷過程：
1. `git diff HEAD -- scripts/lumos` 中完全找不到任何含 `startswith` 的 hunk。
2. 直接 `Read scripts/lumos:3428-3441`（`cmd_loop_verify_progress` 函式內、`--settle` 分支）確認現行程式碼是：
   ```python
   status = e.get("status")
   if status == "llm-ok" and not is_caught_round(e.get("verified_in_round")):
   ```
   （逐字比對，非 `.startswith("llm")` 版本）
3. `grep -rn "startswith(\"llm\")\|dsp_llm_fam" scripts/` 全 repo 零命中。

**結論**：patch 檔裡這個 hunk（`cmd_loop_verify_progress` 的 `llm-ok`/`llm-retry` 家族化）**目前不在 repo 的工作樹裡**——既未 commit、工作樹也沒有。除此之外，patch 檔與 `git diff HEAD` 逐行完全吻合（含 `_vault_repo_root`、round-less `__seq` 分組、留痕全席重驗、badlines 行號、quote 巢狀修正、校準帳 run_id 讀回、四支新測試等，全部驗證存在於真實檔案且對應行為與 patch 描述一致，並實際跑過全部 5 支相關測試皆綠燈）。

這代表：**若這個 hunk 曾經套用又被撤回（或這份 patch 檔是舊快照/另一份工作樹產物），現行程式碼是安全的**；但若審查標準是「這份 patch 檔」，其內容本身藏了一個 None 上呼叫方法的洞，詳見 Finding 1（標記為「不可在現行 repo 重現」，供留痕，不計入需要修的 bug）。

---

## Findings

### Finding 1（patch 檔內容 vs 現行 repo：分歧點，內容本身若套用會是真洞，但現行 repo 未含此改動）

- **file**: `scripts/lumos`（patch 內對應 `cmd_loop_verify_progress`；現行 repo 該函式在 3436-3437 行是舊版比較，並無此行）
- **severity**: 若套用 → major（未捕例外傳播，指令直接 crash）；現況 → N/A（現行 repo 沒有這段程式碼，故不構成現行 bug）
- 引句：「if status.startswith("llm") and not is_caught_round(e.get("verified_in_round")):」

**問題本身（假設性）**：`cmd_loop_verify_progress` 的 `--settle` 分支讀外部使用者提供的清單 JSON 檔，對每個 entry 只驗證 `data["entries"]` 是非空 list（見現行 3424-3428 行），**不像** `_loop_status_settle`（真正的 gate 路徑）那樣強制每條 entry 必須有 `id/kind/status/spec_sha` 四鍵齊全且 `status` 落在合法集合。所以 `status = e.get("status")` 完全可能是 `None`（entry 缺 `status` 鍵，或 JSON 裡寫 `"status": null`）。

舊版 `status == "llm-ok"` 對 `None` 是安全的（比較恆 False，不 raise）。patch 版 `status.startswith("llm")` 對 `None` 會直接 `AttributeError: 'NoneType' object has no attribute 'startswith'`，未被任何 `try/except` 接住，導致 `lumos loop verify-progress <id> --settle <檔>` 對這類清單檔直接 traceback crash（而非優雅的 rc2 或忽略）。

**驗證**：我用「現行（未套用此 hunk）」的程式碼實際跑了一次 `entries=[{"id":"e1"}]`（無 `status` 鍵）的 `--settle` 檔案：
```
rc= 0
settle={'total': 1, 'unsettled': 0, 'settled': 1}
```
確認現行程式碼優雅處理、不 crash。若把該行改回 patch 檔的 `.startswith` 版本，此輸入會直接炸掉（可用同一個 repro 腳本驗證，換掉那一行即翻紅）。

**建議**（若這個 hunk 之後要重新套用）：`if status and status.startswith("llm") and ...`，或維持 `in ("llm-ok", "llm-retry")` 集合寫法，避免對 `None` 呼叫方法。

---

### Finding 2（現行 repo 真實存在、已用實測確認）：`--disposal` 模式的 `--repo` 旗標被靜默忽略

- **file**: `scripts/lumos`，`cmd_loop_status` 內 disposal 分派處（現行約 3631-3632 行）
- **severity**: minor（不造成寫讀根不一致或誤判 PASS，但使一個文件建議的旗標完全失效，且與同函式另一模式 `--settle` 的行為不一致）
- 引句：「return _loop_status_disposal(rounds, loop_id, spec, n_badlines, _vault_repo_root(env),」

**問題**：本輪新增的 `_vault_repo_root(env)`（向上找 `.git`，找不到才退 `vault.parent`）被用來當 disposal 閘讀側解析 report/snapshot 相對路徑的 root，**完全不理會使用者從 CLI 傳的 `--repo`**（該旗標仍掛在 `ls.add_argument("--repo", dest="gate_repo", ...)` 上，且 `cmd_loop_next` 產的 `disposal_gate` 提示文字明講「`lumos loop status {loop_id} --disposal --spec <計劃節點.md> --repo <root>`」，暗示 `--repo` 是必要/有效參數）。

**實測驗證**（在真實 repo 上跑，非猜測）：對同一筆合法 disposal 記錄，分別帶一個「根本不存在的路徑」當 `--repo` 和完全不帶 `--repo`，兩者輸出逐字元相同：
```
with bogus --repo '/definitely/does/not/exist': rc=1, 輸出以 quote-check ✗ 結尾
without --repo at all:                          rc=1, 輸出逐字相同
```
證實 `--repo` 對 `--disposal` 路徑毫無作用（連格式錯誤都不會被擋，直接靜默吃掉）。

**影響範圍評估（誠實标注非高風险）**：因為 `canary record`（寫側）本身就從未支援 `--repo` 覆寫（`cr = sub.add_parser("canary"...)` 底下的 `add_argument` 清單裡沒有 `--repo`），寫側原本就只能用 `_vault_repo_root(env)` 落帳；讀側現在也用同一函式，所以「寫讀同根」這個本輪要保的不變量本身沒有被破壞——這點是對的。但這代表 `--repo` 對 `--disposal` 是死參數：唯一會咬人的場景是「vault 沒有 `.git` 可循（如非 git 部署 / vault 被搬到與原檔案佈局不同的路徑）且使用者想靠 `--repo` 顯式指定正確 root 來救」——這條路完全不通，且沒有任何錯誤訊息提示「你的 `--repo`被忽略了」，使用者只會看到 quote-check/留痕莫名 FAIL 而摸不著頭緒。

**建議**：要嘛讓 disposal 分派處優先採用顯式 `--repo`（`Path(repo) if repo else _vault_repo_root(env)`，與既有 `_anchor_repo_root(repo)` 的「顯式優先」慣例一致），要嘛把 `disposal_gate` 提示文字與 argparse help 拿掉 `--repo`，避免宣稱一個不存在的能力。

---

## 其餘掃過部分（無新增 finding）

- `round-less` 逐筆 `__seq{len(groups)}` 分組：驗證 key 恆唯一（每次分配都用當下 `len(groups)`，且只在新增群組時遞增），與 round-id 非連續重現守衛（`next(reversed(groups)) != rid_`）交互正確——round-less 記錄插在兩筆同 round-id 之間時會正確判定為「次序被打斷」而 rc2。實測 `t_disposal_gate_r2_panel_hardening` 綠燈確認。
- 判定輪缺留痕欄席 FAIL：迴圈對 `latest` 逐席逐欄檢查、`continue` 只跳過該欄位不跳過整個迴圈，缺欄正確地累積進 `fails`（不再靜默略過）。`n_files`/`ok` 旗標邏輯正確，唯一是 `fails` 清單在多席都缺留痕時會重複塞入多筆 `"留痕"` 字串，`'/'.join(fails)` 輸出會有重複詞（如 `留痕/留痕`）——純顯示層瑣事，不影響判斷正確性，未達回報門檻。
- `_vault_repo_root`：`env.vault.resolve()` 起、含自身在內向上找 `.git`（`.exists()`，含 worktree 的 `.git` file 也算），找不到退 `env.vault.parent.resolve()`。寫側（`cmd_canary` 內 `_pr.relative_to(_vault_repo_root(env))`，`ValueError` 時退絕對路徑）與讀側（`_prov_path` 用同一 root 拼回絕對路徑）用的是**同一函式**，寫讀同根的核心承諾成立（除 Finding 2 提到的 `--repo` 死參數旁支問題）。
- badlines rc2 訊息附行號：`bad_linenos` 於掃描全檔（非僅該 loop）時同步記錄 1-based 行號，訊息組裝 `f"——壞行行號: {bad_linenos}"` 正確、無例外風險。
- 校準帳 run_id 全檔掃描＋半行補換行：`prefix` 判斷邏輯對「空檔」「無此檔」「已以換行結尾」「半行結尾」四種前置狀態都正確處理（空字串走 short-circuit 不誤判）；讀回自驗用 `try/except ValueError: continue` 容錯逐行掃描，`d.get("run_id")`只在 log 檔本身完全由本程式寫入的前提下安全（外部人為寫入非 dict 的合法 JSON 行會使 `.get` 拋 `AttributeError`，但此檔案無此類真實輸入路徑，不構成可回報的具體失敗場景）。
- 新增四支測試（`t_disposal_gate_r1_panel_hardening` / `t_disposal_gate_r2_panel_hardening` / `t_calibration_readback_hardening` / `t_quote_check_nested_quotes_and_min_length`，注意：實際是 4 支不是任務描述的 3 支，`r1_panel_hardening` 亦不在 HEAD、屬本輪新增）：全部直接在 repo 上執行過，5/5 綠燈（含既有 `t_loop_status_disposal_gate`），前置斷言（★前置★ 現場成立）均先過再驗證修法本身，翻紅釘描述與程式碼行為吻合。
- quote 巢狀『』regex 修正與 `_QUOTE_MIN_NORM_LEN=10` 下限：`(?:「([^」]+)」|『([^』]+)』)` 雙分支＋`m.group(1) if ... else m.group(2)` 正確取出對應群組；`too_short` 標記與 `.get("too_short")` 讀取全程用安全存取，無 KeyError 風險。同型巢狀（如「他說「你好」」）仍會在第一個 `」` 截斷，但這不是本輪宣稱要修的範圍（只修『』異型巢狀），非新洞。

## 結論

- Finding 1：patch 檔內容若套用會是 major（None 上呼叫方法、未捕例外傳播），但**現行 repo 未含此段程式碼**，已標記為「不可在現行 repo 重現」，僅供留痕/提醒勿誤套用不安全版本。
- Finding 2：`--repo` 對 `--disposal` 靜默失效，已實測確認，severity=minor。
