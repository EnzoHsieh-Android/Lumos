severity: major

finding: 結果優先分支沒有裁定「啟動失敗且原鎖清除失敗、但快取命中」的結果。照字面實作會回 rc 0，掩蓋仍存在的殘鎖；快取過期後，後續工作會一直拿不到鎖。

severity: major

blocking: yes

引句:「命中就用現有輸出格式回 rc 0，仍不碰替代持有者的鎖」

file: `scripts/lumos:33921`

可執行重現:
```bash
python3.14 - <<'PY'
import contextlib, io, tempfile
from pathlib import Path
from unittest import mock
import scripts.test_lumos as t

m = t._load_lumos_module()
with tempfile.TemporaryDirectory() as d:
    cache = Path(d) / "cache.json"
    lock = Path(str(cache) + ".warming")
    out = io.StringIO()
    real_unlink = Path.unlink

    def fail_lock_cleanup(self, *args, **kwargs):
        if self == lock:
            raise PermissionError("injected cleanup failure")
        return real_unlink(self, *args, **kwargs)

    with mock.patch("subprocess.Popen", side_effect=OSError("spawn failed")), \
         mock.patch.object(Path, "unlink", fail_lock_cleanup), \
         mock.patch.object(m, "_lens_cache_read", return_value={"text": "ready"}), \
         contextlib.redirect_stdout(out):
        rc = m._lens_wait_or_warm(Path(d), cache, "a..b", Path(d), True, .2)

    print(rc, lock.exists(), out.getvalue().strip())
PY
```
現碼輸出為 `0 True {"text": "ready", "cache_hit": true}`。設計需讓 `_lens_spawn_warmer` 同時回傳啟動與清鎖結果，並明訂清鎖失敗時不能被快取命中完全遮掉；至少要留下可被 hook 記為 error 的機械欄位與測試。

severity: minor

finding: S1 只規定 JSON 輸出，沒有規定 `as_json=False` 的人工 CLI 錯誤文字。照字面實作可能回 rc 2 而沒說明。

blocking: no

引句:「應立即回 rc 2 與 JSON `spawn_error=true`、本次 `lock_path`、原 `range`」

file: `scripts/lumos:33954`

建議補非 JSON 驗收：立即回 rc 2、固定說明背景未啟動並附鎖位置、不輸出原始例外；綁人工模式測試。

總結 severity: major，blocking: 1。
