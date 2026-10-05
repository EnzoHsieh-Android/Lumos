severity: minor

# 架構對齊審查(cic-r1,CI 拆三工作)

## 1. 分層與依賴方向
大體對齊。新測試讀 ci.yml 的方式與既有一致:`_need_src(".github/workflows/ci.yml")` 先守門,再用 `Path(GRAPHCTL).resolve().parent.parent / ".github" / "workflows" / "ci.yml"` 取路徑,沒有跨層直呼 scripts/lumos 的私有函式。
引句:「ci = (Path(GRAPHCTL).resolve().parent.parent / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")」
既有碼佐證:file: `scripts/test_lumos.py:54458`(同一路徑寫法)、file: `scripts/test_lumos.py:54941`(`_need_src` 守門 ci.yml)。
模組常數 `_CI_GATE_STEP_FP` 與輔助函式 `_ci_step_fp` 緊貼在使用它的測試之前,與 `_dr_ci_bodies`(file: `scripts/test_lumos.py:54874`)擺在測試前的慣例相同。ci.yml 新註解仍寫出處計劃與日期,與原註解寫法一致(file: `.github/workflows/ci.yml` 原有「2026-10-03 第一個 PR 實際踩到」)。
引句:「# 2026-10-06 拆成三個工作(Projects/CI加速_計劃):全套在 CI 一台機器切 4 片已跑到 32–38.5 分」

## 2. 命名與錯誤處理
severity: minor
blocking: 否 + 命名不一致但結構對;不影響行為,也沒有同名衝突。
`_ci_step_fp` 用了 `_ci_` 前綴,但本檔 `_ci_` 前綴已被另一族佔用(CI 帳/gh 查詢:`_ci_run`、`_mk_ci_env`,file: `scripts/test_lumos.py:25874`、`scripts/test_lumos.py:25903`;scripts/lumos 另有 `_ci_workflow_texts` 等,file: `scripts/lumos:37092`)。讀 ci.yml 內容的測試輔助慣例用主題縮寫前綴(`_dr_ci_bodies`、`_dr_ci_call_lines`,file: `scripts/test_lumos.py:54517`)。讀者會把 `_ci_step_fp` 誤當成 CI 帳那族。
引句:「def _ci_step_fp(block):」

錯誤處理:`m`、`total` 都先判 None 再取值,讀不到時走 `[]`、`-1`,由 check 報紅而非丟例外;與既有 `next(..., "")`、`if mm else ""` 的容錯方向一致(file: `scripts/test_lumos.py:54880`、`scripts/test_lumos.py:54882`),對齊。函式內 `import re as _re`、`import hashlib as _h` 也是本檔常見寫法(file: `scripts/test_lumos.py:16567`)。
引句:「nums = sorted(int(x) for g in _re.findall(r'"([0-9 ]+)"', m.group(1)) for x in g.split()) if m else []」

## 3. 第二種做法
步驟切法:新測試沿用同一條 `re.split(r"\n(?=      - )"`,不是新寫一套,對齊(file: `scripts/test_lumos.py:54460`、`scripts/test_lumos.py:54562`、`scripts/test_lumos.py:54880`)。
引句:「blocks = _re.split(r"\n(?=      - )", gb)」

不對齊一條:「每個工作都有 fetch-depth: 0」這個判斷,scripts/lumos 已有「照工作項目切、只認設定行、不被 run 腳本內字樣騙」的現成實作(`_ci_jobs_calling_without_full_history`、`_ci_has_full_history`);新測試另用「切工作 + 整段 regex `^ +fetch-depth: 0\b`」重寫一次,且 regex 會被 `run: |` 多行腳本裡剛好出現的字樣騙過(lumos 那邊正是為此修過,見該函式 docstring)。切工作的 `(?m)^  (名):\s*$` 也是第二套。⚠ 判不準:lumos 那兩個函式是偵測用、回傳「缺的」而非「每個工作的狀態」,複用要傳 `needle=""`,可能被認為過度耦合;且被審的 ci.yml 是自家檔,誤判風險低。
severity: minor
blocking: 否 + 重複的只是一條判斷、不改行為,且判不準複用成本;但同一件事將有兩份定義,建議測試改用 `_load_lumos_inproc()._ci_has_full_history` 或在報告註明不複用的理由。
引句:「_re.search(r"(?m)^ +fetch-depth: 0\b", b) is not None and _re.search(r"(?m)^    timeout-minutes: \d+", b) is not None」
既有碼佐證:file: `scripts/lumos:37138`(`_ci_has_full_history`)、file: `scripts/lumos:37105`(按工作項目切)。

指紋機制(`_ci_step_fp` 用 sha256 釘步驟指令):本檔沒有同功能輔助函式(既有測試用 `in`/`find` 比對片段),屬新增能力而非第二種做法,不列。

總結:不對齊共 2 條,其中 major 0 條
