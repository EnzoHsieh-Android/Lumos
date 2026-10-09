severity: major

## 分層依賴

已讀,無 finding。`lumos` 委派至 sidecar、Semgrep 維持選配，三支 runtime sidecar 共用既有 vendor/deinit 精確白名單。

## 命名與錯誤處理

### a1 部署不完整時，備援入口攔不到實際子命令與遞移缺檔

severity: major  
blocking: 是  
引句:「測試品質工具未完整部署，請更新來源與vendor」  
file: `scripts/lumos:49417`  
file: `scripts/test_quality.py:274`

缺 `test_quality.py` 時只建立沒有子命令的空 parser，故 `test-quality scan` 先被 argparse 判成未知參數，走不到更新提示。若只缺 `test_quality_scan.py` 或 `test_quality_semgrep.py`，`dispatch` 又未捕捉 `ModuleNotFoundError`，直接吐 traceback。這是 CLI、sidecar 與非原子逐檔部署之間的跨層破口。

最小重現：

```sh
mkdir -p /tmp/lumos-seat-work/code-test-quality-native-push/arch/missing-all
cp scripts/lumos /tmp/lumos-seat-work/code-test-quality-native-push/arch/missing-all/
python3 /tmp/lumos-seat-work/code-test-quality-native-push/arch/missing-all/lumos test-quality scan x --json
```

實際 rc 2：「不認得這幾個參數」，沒有 `lumos update` 指路。

```sh
mkdir -p /tmp/lumos-seat-work/code-test-quality-native-push/arch/missing-transitive
cp scripts/lumos scripts/test_quality.py /tmp/lumos-seat-work/code-test-quality-native-push/arch/missing-transitive/
python3 /tmp/lumos-seat-work/code-test-quality-native-push/arch/missing-transitive/lumos test-quality capabilities
```

實際 rc 1，`ModuleNotFoundError: No module named 'test_quality_semgrep'`。應統一回 rc 2 的結構化未部署錯誤。

### a2 白名單數量名稱已與實值漂移

severity: minor  
blocking: 否  
引句:「白名單移除 vendored 工具組:① _VENDORED_TOOLKIT 固定 5 檔」  
file: `scripts/lumos:21967`  
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:29`

白名單現為八檔，但函式說明與 lifecycle 摘要仍寫五檔。移除行為本身正確，名稱與圖譜現況會誤導下次維護者。

## 是否引入第二套功能

### a3 `scan` 的 argparse 契約有兩份實作

severity: major  
blocking: 是  
引句:「scan.add_argument('--implementation', action='append', default=[])」  
file: `scripts/test_quality.py:105`  
file: `scripts/test_quality.py:263`  
file: `scripts/test_quality_scan.py:227`

`test_quality.py` 與 `test_quality_scan.py` 各自宣告 `--semgrep`、`--check-helper`、`--implementation`、`--json`，dispatch 再把已解析的 Namespace 還原成 argv，交給第二個 parser 重解析。新增或修改選項必須改兩處，已形成第二套公共 CLI 契約。應由 scan sidecar 暴露單一 parser 組裝函式或直接接收 Namespace。

最小翻紅重現：

```sh
python3 - <<'PY'
import ast
from pathlib import Path
repo = Path('/tmp/lumos-readme-oct-audit')
owners = {}
for rel in ('scripts/test_quality.py', 'scripts/test_quality_scan.py'):
    tree = ast.parse((repo / rel).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, 'attr', '') == 'add_argument':
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith('--'):
                    owners.setdefault(arg.value, set()).add(rel)
dup = {k: sorted(v) for k, v in owners.items() if len(v) > 1}
print(dup)
raise SystemExit(1 if dup else 0)
PY
```

實際 rc 1，列出上述四個重複旗標。

## 固定席與合約逐條判

- 授權固定席「LICENSE/COPYING/NOTICE 不得進白名單」：已讀,無 finding；端到端保留測試 4/4 通過。
- 授權固定席「所有 vendored 檔帶 SPDX」：已讀,無 finding；授權測試 7/7 通過。
- `test-quality-cli`：沒有登記硬合約；trusted command、no sandbox、not_attested／not_assessed 邊界均明示，已讀,無 finding。
- `lumos-cli-lifecycle` 的 re-inject invariant：本 diff 未觸及，已讀,無 finding。
- lifecycle 的版本戳與髒來源兩項 DEBT：本 diff 未改其行為，已讀,無 finding。
- vendor/deinit 精確清單測試 1/1、清單覆蓋測試 5/5 通過。
- CLI 與 scanner 獨立測試分別 22/22、21/21 通過；未跑全套。

總結:最嚴重 severity major，blocking 2 條