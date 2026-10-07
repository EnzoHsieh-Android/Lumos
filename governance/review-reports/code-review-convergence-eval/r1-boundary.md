severity: major

自動鏡頭未附上；已實跑 `python3 scripts/lumos impact --diff ce4c30f9..HEAD`，結果為 high、固定席 18 篇加 top 4。完整讀過凍結 patch、計劃、risk/disposition，repo 未改檔或做 git mutation。

### F1：非連續輪次被誤報為已知

severity: major

blocking: 是

引句:「分輪與漏斗沿用既有讀法的語意；回顧狀態另外查既有retro-stats」

file: `governance/eval/review_convergence.py:119`

file: `scripts/lumos:14069`

`build_cohort()` 只去重 round 名稱，沒有沿用既有讀側對 `r1 → r2 → r1` 非連續重現的拒絕語意；它會輸出 `round_count=2`、成本總量已知。損壞帳因此被包裝成可比較資料，違反 S1。

最小重現（已實跑）：

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=governance/eval python3.14 - <<'PY'
import review_convergence as ev
rows = [
    {"loop":"code-x","round":"r1","tokens":1},
    {"loop":"code-x","round":"r2","tokens":1},
    {"loop":"code-x","round":"r1","tokens":1},
]
x = ev.build_cohort(rows)["loops"][0]
assert x["round_count"] is None, x
PY
```

實際翻紅：`round_count` 為 `2`，`tokens.total` 為 `3`。

### F2：非法成本 scalar 仍被算作有效試行

severity: major

blocking: 是

引句:「rounds：正整數；tokens/wall_seconds：非負有限值，缺資料填 null。」

file: `governance/eval/review_convergence.py:313`

file: `governance/eval/review_convergence.py:343`

`validate_outcome()` 沒驗 `tokens`／`wall_seconds`。`true`、負數、字串、陣列、物件及超界整數都會被接受為有效 receipt；之後只被靜默降成成本未知，仍進入 `valid_trials`、配對及品質差計算，且沒有保留無效原因，違反 S3。

最小重現（已實跑）：

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=governance/eval python3.14 - <<'PY'
import hashlib, json, tempfile
from pathlib import Path
import review_convergence as ev
from test_review_convergence import manifest, receipt

with tempfile.TemporaryDirectory(dir="/tmp/lumos-seat-work/code-review-convergence-eval/邊界-sol") as td:
    root = Path(td); m = manifest(); r = receipt(root, m, "baseline", 1)
    p = root / r["receipt"]["path"]
    d = json.loads(p.read_text()); d["tokens"] = True
    raw = json.dumps(d).encode(); p.write_bytes(raw)
    r["receipt"]["sha256"] = hashlib.sha256(raw).hexdigest()
    out = ev.compare(m, [r], root)
    assert out["invalid_records"] and out["valid_trials"] == 0, out
PY
```

實際翻紅：`valid_trials=1`、`invalid_records=[]`。

### F3：NUL receipt 路徑讓整批 compare traceback

severity: major

blocking: 是

引句:「試行應列未判定並保留原因；產品驗收失敗仍是有效負例」

file: `governance/eval/review_convergence.py:259`

file: `governance/eval/review_convergence.py:287`

file: `governance/eval/review_convergence.py:300`

路徑只驗絕對路徑與 `..`。含 NUL 的 JSON 字串進入 `Path.is_symlink()` 後拋出 `ValueError`，不在 `check_trial()` 的 `DataError` 捕捉範圍內；一筆壞索引會中止整批比較，其他有效試行也拿不到結果。

最小重現（已實跑）：

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=governance/eval python3.14 - <<'PY'
from pathlib import Path
import review_convergence as ev
from test_review_convergence import manifest

bad = {
    "case_id":"C1", "arm":"baseline", "repeat":1,
    "receipt":{"path":"bad\0name.json", "sha256":"f"*64},
}
out = ev.compare(manifest(), [bad], Path("/tmp"))
assert out["invalid_records"][0]["reason"] == "receipt-path"
PY
```

實際結果：未回傳 `invalid_records`，直接 `ValueError: open: embedded null character in path`，CLI rc=1。

### F4：escaped surrogate 使 manifest 驗證崩潰

severity: minor

blocking: 否

引句:「案例起點、輸入、判準、分組或模型條件不齊／矛盾時，manifest應拒收而不補造值」

file: `governance/eval/review_convergence.py:160`

file: `governance/eval/review_convergence.py:189`

file: `governance/eval/review_convergence.py:239`

`text_field()` 接受 lone surrogate；`split_for()` 對 group 執行 UTF-8 encode 時拋 `UnicodeEncodeError`。實跑含 `"group":"bad\uD800"` 的 manifest 得到 traceback、CLI rc=1，沒有轉成預期的資料錯誤。這只影響已非法 manifest 的錯誤回報，未讓錯誤證據通過，因此列 minor。

### 其餘邊界

空資料、超限檔案、NaN／Infinity、重複 JSON key、非法頂層 scalar、布林 repeat／rounds、跳出根目錄、symlink、重複 slot：已讀,無 finding。

資源釋放：已讀,無 finding。對 FIFO 與超限一般檔各重複 100 次，`/dev/fd` 維持 `4 → 4`；`os.fdopen()` 後的非一般檔、讀取與超限路徑都有關閉 handle。

既有測試：12 個 unittest 全綠；正式 runner 4/4 全綠。上述重現因此是現有測試未覆蓋的缺口。

### Impact 硬合約逐條

- `Systems/測試假綠形態` 1/1，前置現場斷言：已讀,無 finding。
- `Systems/bound-tests-gate` 1/1，綁定測試真跑：已讀,無 finding。
- `Systems/canary-audit` 1/2，落盤 readback：已讀,無 finding。
- `Systems/canary-audit` 2/2，second 僅 telemetry：已讀,無 finding。
- `Systems/guard-kill` 1/2，rc 優先序：已讀,無 finding。
- `Systems/guard-kill` 2/2，JSON stdout 純度：已讀,無 finding。
- `Systems/slim-get-一行安裝` 1/2，PowerShell ASCII／無 BOM：已讀,無 finding。
- `Systems/slim-get-一行安裝` 2/2，不使用 `$Args`：已讀,無 finding。
- `Systems/slim-install-安裝器` 1/7，sentinel 外 byte-equal：已讀,無 finding。
- `Systems/slim-install-安裝器` 2/7，注入冪等：已讀,無 finding。
- `Systems/slim-install-安裝器` 3/7，完整版位元組備份：已讀,無 finding。
- `Systems/slim-install-安裝器` 4/7，安裝 manifest：已讀,無 finding。
- `Systems/slim-install-安裝器` 5/7，三層目標守衛：已讀,無 finding。
- `Systems/slim-install-安裝器` 6/7，Windows 直譯器偵測：已讀,無 finding。
- `Systems/slim-install-安裝器` 7/7，Windows shim 碰撞：已讀,無 finding。
- `Systems/slim-uninstall-一行卸載` 1/6，bin 內容比對：已讀,無 finding。
- `Systems/slim-uninstall-一行卸載` 2/6，各步獨立且例外不中止：已讀,無 finding。
- `Systems/slim-uninstall-一行卸載` 3/6，skill 先備份：已讀,無 finding。
- `Systems/slim-uninstall-一行卸載` 4/6，CLAUDE.md 精確還原：已讀,無 finding。
- `Systems/slim-uninstall-一行卸載` 5/6，Windows shim 獨立移除：已讀,無 finding。
- `Systems/slim-uninstall-一行卸載` 6/6，manifest 清理及保留：已讀,無 finding。
- `Systems/lumos-cli-read` 1/1，superseded 搜尋濾網：已讀,無 finding。
- `Systems/lumos-cli-lifecycle` 1/1，re-inject sentinel 外保留：已讀,無 finding。
- `Systems/design-loop` 1/1，處置閘條款綁定：已讀,無 finding。
- `Systems/節點範圍與索引守衛` 1/9，共用既有解析器：已讀,無 finding。
- `Systems/節點範圍與索引守衛` 2/9，尊重索引範圍：已讀,無 finding。
- `Systems/節點範圍與索引守衛` 3/9，缺索引明示跳過：已讀,無 finding。
- `Systems/節點範圍與索引守衛` 4/9，範圍只按合約數：已讀,無 finding。
- `Systems/節點範圍與索引守衛` 5/9，doctor 段落位置：已讀,無 finding。
- `Systems/節點範圍與索引守衛` 6/9，已知閘名同步：已讀,無 finding。
- `Systems/節點範圍與索引守衛` 7/9，懸空狀態共用常數：已讀,無 finding。
- `Systems/節點範圍與索引守衛` 8/9，bool 門檻拒絕：已讀,無 finding。
- `Systems/節點範圍與索引守衛` 9/9，三道治理落帳：已讀,無 finding。

其餘 impact 節點未登記硬合約：`Systems/lumos-deinit`、`Projects/逃逸自動記_計劃`、`Projects/引用座標依實際換行_計劃`、`Projects/規格落成可驗收條件_計劃`、`Projects/異常派工單回報輸入錯誤_計劃`、`Systems/check-r-guard`、`Systems/cochange-guard`、四篇 top project：已讀,無 finding。

總結：最嚴重 severity major；blocking 3 條。
