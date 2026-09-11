severity: major

E1 尾端空白被刪除，讓不同檔案繞過資安涵蓋檢查
severity: major
blocking: 是
引句:「p = _git_unquote_path(p.split("\t", 1)[0])」
file: `scripts/lumos:14872`，`s.strip()` 會刪除未加引號路徑中屬於檔名的尾端空白。
資安席只審過 `app/login.py`，後輪換成另一支 `app/login.py ` 時，解析器把兩者合併，整個處置閘實測回傳 PASS；這是不同檔案漏審，不屬於設計接受的同檔後續修改限制。
以下重現僅以記憶體替代檔案讀取，實際執行原有雜湊驗證與完整處置閘，不寫入任何檔案：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -c '
import runpy, hashlib
from pathlib import Path
from unittest.mock import patch

m = runpy.run_path("scripts/lumos", run_name="review_only")
def p(f):
    return f"diff --git a/{f} b/{f}\n--- a/{f}\n+++ b/{f}\t\n@@ -1 +1 @@\n-old\n+new\n"

data = {
    "r1.patch": p("app/login.py"),
    "r2.patch": p("app/login.py "),
    "report.md": "severity: clean\n",
}
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
rows = []
for rid, auditor in [("r1", "資安-sonnet"), ("r2", "正確性-sonnet")]:
    sp = rid + ".patch"
    h = sha(data[sp])
    rows.append(dict(
        round=rid, auditor=auditor, tier="high",
        ts="2026-09-13T10:00:00+08:00", findings=0, severity="clean",
        report_path="report.md", report_sha256=sha(data["report.md"]),
        snapshot_path=sp, snapshot_sha256=h,
        reviewed_sha256=h, result_sha256=h,
    ))
with patch.object(Path, "read_bytes", lambda self: data[str(self)].encode()), \
     patch.object(Path, "read_text", lambda self, **kw: data[str(self)]):
    rc = m["_loop_status_disposal"](
        rows, "code-repro", "r2.patch", readonly=True)
print("rc =", rc)
assert rc == 1, "unreviewed distinct path passed security coverage"
'
```

實際輸出節錄：

```text
[disposal] 資安席: ✓ — r1 資安-sonnet(看過的檔涵蓋最後一版 1 個)
✅ DISPOSAL GATE PASS (code-repro 輪 r2: G3 ∧ 0 發現空輪 ∧ 留痕可重算;引句無可驗不宣稱)
rc = 0
AssertionError: unreviewed distinct path passed security coverage
```

最嚴重 severity 是 major，blocking 共 1 條。