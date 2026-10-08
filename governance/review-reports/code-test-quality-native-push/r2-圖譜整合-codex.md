severity: major

G1 — i2 要求移除現況中的舊白名單數量／清單，但生命週期正文仍只列五檔，和現行八檔常數矛盾。歷史決策 d3 的「5 檔」屬歷史快照，應保留；錯的是現況正文。

severity: major  
blocking: 是

引句:「KEY:_VENDORED_TOOLKIT 的精確路徑白名單,為 vendor(_vendor_toolchain)與 deinit(_deinit_remove_vendored)共用,避免漂移」

file: `governance/review-reports/code-test-quality-native-push/r1-intake.md:15`  
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:56`  
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:134`  
file: `scripts/lumos:22144`

最小翻紅重現：

```sh
python3 - <<'PY'
import ast
from pathlib import Path
root=Path('/tmp/lumos-readme-oct-audit')
tree=ast.parse((root/'scripts/lumos').read_text())
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id == '_VENDORED_TOOLKIT'
        for t in node.targets
    ):
        current=ast.literal_eval(node.value)
        break
line=(root/'docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md').read_text().splitlines()[133]
missing=[p for p in current if f'`{p}`' not in line]
print(len(current), missing)
assert not missing
PY
```

實際 rc=1；程式為八檔，正文缺 `test_quality.py`、`test_quality_scan.py`、`test_quality_semgrep.py`。這使讀圖譜者可能再次漏掉三個 sidecar。歸因：有證據的原有漏查；修前已矛盾，本輪 i2 處置未完全修好，並非新 runtime 回歸。

G2 — `test_quality_semgrep.py` 已抽出 `backend_findings`，但它自己的家 `test-quality-multilang` 完全未更新，也未連到本輪驗證；說明只寫進通用 scanner 家。從 Semgrep 家出發無法還原這次重構及其驗證資格。

severity: minor  
blocking: 否

引句:「WHY: 來源與安裝入口共用掃描參數，選配適配器延後載入」

file: `scripts/test_quality_semgrep.py:23`  
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-multilang.md:6`  
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-multilang.md:10`  
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-multilang.md:20`  
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-scan.md:41`  
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-scan.md:47`  
file: `docs/lumos-toolchain-knowledge/Verification/測試品質分支推送前修復驗證.md:11`

機械核對：修前到修後 `scripts/test_quality_semgrep.py` 有差異，但 `Systems/test-quality-multilang.md` 無差異；新 Verification 也只有 `plan_refs`，沒有 `system_refs`。歸因：本輪造成的圖譜安家／連結遺漏；未重現 runtime 失敗。

G3 — repair binding 綁定的 patch 不是規定命令產生的完整兩端差異，且缺樹碼、祖先狀態、歸因界線與前輪材料指紋，無法自足支撐完整修補因果判定。

severity: major  
blocking: 是

引句:「第一輪七席報告、独立資安辯方、修前後控制及五棧重放在 governance/review-reports/code-test-quality-native-push。」

file: `governance/review-reports/code-test-quality-native-push/r2-repair-binding.json:2`  
file: `governance/review-reports/code-test-quality-native-push/r2-repair-binding.json:6`  
file: `governance/review-reports/code-test-quality-native-push/r2-repair.patch:1`  
file: `governance/research/review-repair-regressions/implementation/sample-repair-binding.json:2`  
file: `governance/research/review-repair-regressions/retro-attribution/independent-research.md:8`

最小翻紅重現：

```sh
python3 - <<'PY'
import hashlib,json,subprocess
from pathlib import Path
root=Path('/tmp/lumos-readme-oct-audit')
p=root/'governance/review-reports/code-test-quality-native-push'
b=json.loads((p/'r2-repair-binding.json').read_text())
required={'before_commit','after_commit','before_tree','after_tree',
          'patch_sha256','ancestry','attribution_limits'}
missing=sorted(required-b.keys())
full=subprocess.check_output([
  'git','-C',str(root),'-c','core.quotePath=false',
  'diff','--no-ext-diff','--no-textconv','--no-color',
  '--no-renames','--binary','--full-index','-U10',
  b['base'],b['head'],'--'
])
full_sha=hashlib.sha256(full).hexdigest()
bound_sha=hashlib.sha256((root/b['patch']).read_bytes()).hexdigest()
print(missing, full_sha, bound_sha, b['sha256'])
assert not missing and full_sha == bound_sha == b['sha256']
PY
```

實際 rc=1；缺七個必要欄位，規定完整差異 SHA-256 為 `f81467…`，綁定 patch 為 `0dcdc6…`。完整提交差異有 77 條路徑，綁定 patch 只有 18 條，且 binding 未以 `archive_only` 列出其餘材料。歸因：本輪修補卷證製作缺陷；不是產品行為回歸，但令整體回歸歸因維持未判定。

C1 — 五 consumer 副本、stored replay、native execution 三者在圖譜中有正確分界；scanner／Semgrep 重構在已驗範圍內保持行為。

severity: clean  
blocking: 否

引句:「這次沒有重啟Android/iOS裝置，原生執行資格和當時來源hash仍以先前驗證及不可變manifest為準，不覆寫原始報告。」

file: `docs/lumos-toolchain-knowledge/Verification/測試品質分支推送前修復驗證.md:5`  
file: `docs/lumos-toolchain-knowledge/Verification/測試品質分支推送前修復驗證.md:20`  
file: `governance/review-reports/code-test-quality-native-push/r1-consumer-vendor-hashes.json:1`  
file: `governance/review-reports/code-test-quality-native-push/r1-replay-csharp.json:2`  
file: `governance/review-reports/code-test-quality-native-push/r1-replay-android.json:2`  
file: `governance/review-reports/code-test-quality-native-push/r1-replay-ios.json:2`  
file: `governance/review-reports/code-test-quality-native-push/r1-replay-node.json:2`  
file: `governance/review-reports/code-test-quality-native-push/r1-replay-laravel.json:2`

已機械核對 15 個 consumer sidecar hash 均等於本機來源；五份 replay 都是 rc=0、`detected/not_assessed`，且明文標示沒有重跑 native runner。33 個 CLI、21 個 scanner、15 個 handbook 控制通過。另用同一份有效 Semgrep 假報告對修前、修後版本配對，輸出逐位元相同；`backend_findings` 抽函式未重現行為變化。

固定席前八篇逐條判定：

1. `Issues/vendored測試套件在消費端假紅.md`：受 vendor 變更影響；工具檔排除仍成立，歷史數量保留，無額外 finding。
2. `Systems/lumos-cli-lifecycle.md`：re-inject sentinel 外內容保留合約未受破壞；現況白名單另見 G1。
3. `Systems/lumos-deinit.md`：只清已知 vendored bytecode，使用者 cache 與 symlink 外側均保留，無 finding。
4. `Systems/lumos-cli-read.md`：search 排除 superseded、保留 stale 的合約未受影響。
5. `Systems/bound-tests-gate.md`：真跑、懸空與 unfilterable 阻擋合約未受影響。
6. `Systems/guard-kill.md`：rc 優先序與成功 JSON 純度未受影響。
7. `Systems/授權與歸屬.md`：三支 sidecar 均有 SPDX；LICENSE 類檔案未進白名單，無 finding。
8. `Systems/測試假綠形態.md`：取消、worker、writer、deinit 等控制均含到達現場的前置觀測，無 finding。

固定席其餘只列名：

- `Systems/pitfalls-code-loop.md`
- `Systems/design-loop.md`
- `Systems/reversibility-governance-ledger.md`
- `Systems/loop-convergence-recording.md`
- `Systems/doctor-irreversible-hint.md`
- `Systems/lumos-refcheck.md`
- `Systems/check-t-sentinel.md`
- `Systems/check-r-guard.md`
- `Systems/節點範圍與索引守衛.md`
- `Systems/cochange-guard.md`
- `Systems/canary-audit.md`
- `Systems/slim-get-一行安裝.md`
- `Systems/slim-install-安裝器.md`
- `Systems/slim-uninstall-一行卸載.md`
- `Projects/規格落成可驗收條件_計劃.md`
- `Projects/雙向門放行_計劃.md`
- `Projects/引用座標依實際換行_計劃.md`
- `Projects/逃逸自動記_計劃.md`
- `Projects/異常派工單回報輸入錯誤_計劃.md`
- `Systems/judge-severity-gate.md`
- `Systems/core-invariant-baseline.md`

完整讀過 `r2-graph.patch`、`r2-scanner.patch`、`r2-repair-binding.json`、`r1-intake.md`；另核對 `test-quality-cli`、`test-quality-scan`、`test-quality-multilang`、`test-quality-handbook`、`historical-test-quality`、`lumos-cli-lifecycle`、`lumos-deinit`、`retrieval-ranking` 正文及五份 replay/hash 卷證，未讀其他 r2 席報告。

因果三問：

1. 原問題：F1、b1、b2、r1–r4、i1、a3 的控制通過；i2 因 G1 未完整修好。
2. 既有行為：已測 CLI、scanner、handbook、deinit 與 Semgrep 配對案例保持；本輪沒有 Android/iOS native rerun，也沒有 Windows 資格。
3. 回歸歸因：未重現 scanner／Semgrep runtime 回歸；G1 是原有漏查，G2 是本輪圖譜遺漏，G3 使完整修補區間的總體因果仍未判定。

最嚴重 severity：major；blocking 總數：2
