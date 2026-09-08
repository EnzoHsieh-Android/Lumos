severity: blocker

### f1 表態閘 satisfied 證據的行號範圍未驗證,IndexError 被吞成靜默放行

severity: blocker
blocking: 是
file: `scripts/lumos:15032`
引句:「return "ok", (file_lines[lo - 1] if lo == hi else file_lines[lo - 1] + "\n…\n" + file_lines[hi - 1])」

`_disp_split_path_line`(scripts/lumos:21148)只用 `\d+(-\d+)?` 驗行號格式,不驗 lo≤hi、也不驗 lo 本身有沒有超出檔案行數;evidence 給 `sample.txt:10-5`(檔案只有 5 行)能通過 `_disp_validate` 寫入表態檔與治理帳。check 時 `_validate_repo_ref` 的 at_sha 分支(scripts/lumos:15023-15032)只檢查 `hi > len(file_lines)`,lo=10 沒被擋下,於是 `file_lines[lo-1]` 丟出未接的 `IndexError`;這個例外被 `_codeloop_guard_verdict` 外層 `except Exception` 吞掉、轉成 `_gate_failopen`(dv["blocked"]=False),導致**整份表態核對(含其他真正未答或答錯的題)被靜默放行**,推送者的終端機只會看到「✅ code-loop check: OK」,唯一痕跡是治理帳裡一筆不會被主動檢視的 fail-open 記錄。

已用真實 git repo 重現(見下):
```
$ python3 -c '
import importlib.util, sys
from importlib.machinery import SourceFileLoader
from pathlib import Path
loader = SourceFileLoader("m", "scripts/lumos")
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("m", loader))
loader.exec_module(m)
print(m._validate_repo_ref(Path("<git repo>"), "sample.txt", "10-5", at_sha="<HEAD sha>"))
'
Traceback (most recent call last):
  ...
  File "scripts/lumos", line 15032, in _validate_repo_ref
    return "ok", (file_lines[lo - 1] if lo == hi else file_lines[lo - 1] + "\n…\n" + file_lines[hi - 1])
IndexError: list index out of range
```
另外 `"5-0"`(lo=5 在檔案 5 行內,hi=0)不會崩潰但會回 `('ok', 'line5\n…\nline5')`——`file_lines[hi-1]` 在 hi=0 時是 `file_lines[-1]`,Python 負索引悄悄繞回最後一行,把一個語意不合法的行號範圍判成「ok」。這兩個輸入都應該在 `_disp_split_path_line` 或 `_validate_repo_ref` 被擋成 `line_out_of_range`/格式錯誤,而不是崩潰或誤判為合法。

### f2 pre-push 新增的 --bound-tests-advisory 讓 code-loop check 對紅色合約測試不再擋,牴觸 bound-tests-gate 的 ★INVARIANT★ 且圖譜未同步

severity: major
blocking: 是
file: `scripts/lumos:21514`
引句:「if bt["status"] == "red" and not bound_advisory:」

`docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:18` 的 ★INVARIANT★ 寫「code-loop check 對 impact 固定席上合約綁的測試逐支真跑,任一紅...→ blocked=True rc1」,沒有任何例外條件;這份 diff 讓 pre-push 對每個分支 push 一律呼叫 `code-loop check`,低風險推送額外帶 `--bound-tests-advisory`(scripts/hooks/pre-push 新增的 `_ba=(); [[ "$_tier_high" -eq 0 ]] && _ba=(--bound-tests-advisory)`),使同一支 `code-loop check` 在 `bt["status"]=="red"` 時直接跳過 blocked=True,回傳「可以推」。以下 stub 一個必紅的 `_bound_tests_check` 直接呼叫兩次 `_codeloop_guard_verdict` 得到的實測差異:
```
bound_advisory=False -> True  模擬:合約測試真的紅了
bound_advisory=True  -> False tier=standard(非 high)
```
這份 diff 沒有同步改寫 bound-tests-gate.md 的 ★INVARIANT★ 行加註「除非帶 --bound-tests-advisory」,圖譜對 code-loop check 行為的斷言與程式碼現狀不一致(CLAUDE.md 鐵則1 要求同一次工作內寫回)。

### f3 --branch 空字串被靜默吞掉、退回目前 checkout 分支

severity: minor
blocking: 否
file: `scripts/lumos:21763`
引句:「return _cmd_codeloop_dispositions(repo_root, marker_branch or branch, head_sha, ts, disp_file)」

`cmd_code_loop` 對 `dispositions` 子命令用 `marker_branch or branch` 決定表態要記在哪個分支名下;若呼叫端傳入 `--branch ""`(例如自動化腳本算錯分支名回空字串),空字串是 falsy 會被 `or` 悄悄吞掉、退回目前 checkout 的分支,而不是報錯或警告。pre-push 自己一律傳非空的 `${_rref#refs/heads/}`,所以正常流程不會踩到,但人工或腳本呼叫 `lumos code-loop dispositions` 時可能在沒有任何提示的情況下把表態寫錯分支(之後 `check` 用另一個分支名去讀就會查無記錄)。

## pitfalls manifest 判定

`scripts/lumos:21218`(`_codeloop_dispositions_gov_log` 裡的 `with open(docs / ".governance-log.jsonl", "a", encoding="utf-8") as f:`)——誤報。regex `\bopen\s*\(` 純文字比對抓到 `open(`,但這個呼叫已經包在 `with` 區塊裡,handle 會被正確關閉,不是真隱患。

## 圖譜鏡頭

- **bound-tests-gate.md**(★INVARIANT★,固定席):被破壞,見 f2。
- **code-loop守衛main-direct盲區.md**(事故,固定席):不影響——此 Issue 修法的核心(pre-push 用推送範圍 `$BEFORE..$SHA`/`--at-sha`/`--branch` 取代 merge-base..HEAD)完全沒被這份 diff 改動,`_range`/`_lsha`/`_rbranch` 三個變數的來源與傳遞方式維持原樣;這份 diff 反而讓「不論 tier 一律呼叫 code-loop check」,涵蓋面比之前(只在 tier=high 才叫)更大,不會重開這個盲區。
- **canary-audit.md**(★INVARIANT★×2,固定席):不影響——diff 完全沒有觸及 `canary record`/`canary second` 相關程式碼(grep 全份 diff 沒有 "canary" 字樣)。
- **design-loop.md**(★INVARIANT★,固定席,處置閘第五步):不影響——那條 INVARIANT 管的是設計審迴圈(loop id 非 code- 開頭)的處置閘要求審材是 `.md` 計劃,這份 diff 沒有動到 `cmd_loop`/處置閘的判定邏輯,只新增 code-loop 底下的 dispositions/recall-miss 兩個新子命令(名字雖然像但不是同一套機制)。
- **guard-kill.md**(★INVARIANT★×2,固定席):不影響——diff 沒有修改 `guard kill` 指令本身的 rc 判定或 `--json` 輸出邏輯;`_bound_tests_check` 內部雖然重用 guard-kill 的 `_kill_run` 執行器,但這份 diff 只在其外層加了 `bound_advisory` 旗標(見 f2,影響的是 code-loop 自己的 blocked 判定,不是 guard kill 本身的 rc 優先序或 JSON 輸出)。
- **lumos-cli-lifecycle.md**(★INVARIANT★,固定席,re-inject sentinel):不影響——diff 未觸及 CLAUDE.md re-inject 相關程式碼。
- **lumos-cli-read.md**(★INVARIANT★,固定席,search 排除規則):不影響——diff 未觸及 `search` 指令。
- **slim-get-一行安裝.md**(★INVARIANT★×2,固定席,.ps1 BOM/`$Args`):不影響——diff 未觸及任何 `.ps1` 安裝腳本。
- 其餘「超出上限,只列名」的節點(pitfalls-code-loop、check-r-guard、cochange-guard、lumos-deinit、reversibility-governance-ledger、core-invariant-baseline、judge-severity-gate、check-t-sentinel、lumos-refcheck、doctor-irreversible-hint、anchor-integrity、測試假綠形態、授權與歸屬、loop-convergence-recording、slim-install/uninstall):抽查了 pitfalls-code-loop.md,其「白名單與 code-loop 留痕失效豁免共用同一組常數」的說法在這份 diff 裡被正確沿用(`_stack_changed_ok` 直接重用 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIR`/`governance/review-reports/` 排除規則,沒有另開一套),沒有違反;其餘因超出附件上限沒有拿到全文,依 diff 實際觸及的指令範圍(code-loop/pitfalls/dispatch-lens/impact hook)判斷都跟這批筆記講的機制(install/uninstall、doctor 的 irreversible 提示、judge-severity、check-r/check-t、cochange、refcheck、reversibility ledger)無直接關聯,但這條是依範圍推斷、沒有逐字核對內容。

最嚴重 severity: blocker,blocking 條數 2
