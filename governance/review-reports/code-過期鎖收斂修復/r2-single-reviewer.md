severity: major

finding 1：讀取端拒絕不可信快取目錄後，deadline 路徑仍沿該目錄連結建立 `.warming`，造成外部寫入與永久卡鎖  
severity: major  
blocking: 是  
引句:「只讀私有快取目錄的普通檔；POSIX 加驗 owner/權限，並限制 TTL 與結果形狀。」  
file: `scripts/lumos:33139`  
file: `scripts/lumos:33858`  
file: `scripts/lumos:33860`  
file: `scripts/lumos:33993`  
file: `scripts/lumos:34042`  
因果：新讀取檢查會把連到外部的 `dispatch-lens` 判為不可信並回傳 cache miss；`_lens_wait_or_warm` 接著仍呼叫 `_excl_lock_try`，後者未套用同一信任檢查，會經 symlink 在外部目錄建立鎖。背景端既無法寫入快取，退出時也因目錄不可信而拒絕清鎖；往後相同範圍只會反覆 rc 5，且不再啟動工作。新增測試只直接呼叫 `_lens_cache_read`，未走這條後續寫入路徑。  
file: `scripts/test_lumos.py:54862`  
最小重現（已實跑；末行期望斷言會翻紅）：

```python
import contextlib, importlib.util, io, os, tempfile, types
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

spec = importlib.util.spec_from_file_location(
    "lm", "scripts/lumos", loader=SourceFileLoader("lm", "scripts/lumos"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    home, shared = root / "home", root / "shared"
    (home / ".cache" / "lumos").mkdir(parents=True)
    shared.mkdir()
    cache_dir = home / ".cache" / "lumos" / "dispatch-lens"
    cache_dir.symlink_to(shared, target_is_directory=True)
    cpath = cache_dir / ("a" * 64 + ".json")
    without_uid = types.SimpleNamespace(
        **{k: v for k, v in vars(os).items() if k != "getuid"})

    with mock.patch.object(Path, "home", return_value=home), \
         mock.patch.object(m, "os", without_uid), \
         mock.patch("subprocess.Popen") as spawn, \
         contextlib.redirect_stdout(io.StringIO()):
        rc1 = m._lens_wait_or_warm(root, cpath, "a..b", root, True, 0)
        rc2 = m._lens_wait_or_warm(root, cpath, "a..b", root, True, 0)

    external_lock = shared / (cpath.name + ".warming")
    assert rc1 == 2 and rc2 == 2 and spawn.call_count == 0 and not external_lock.exists()
```

實際結果：`rc1=5`、`rc2=5`、`spawn_count=1`、`external_lock=true`。

JSON 形狀、快取檔 symlink 拒絕：已讀,無 finding。  
期限末最後讀取：已讀,無 finding。  
Popen 失敗、換鎖 inode、快取命中清鎖相鄰路徑：已讀；除 finding 1 外無 finding。  
anchor hash：已讀,無 finding；目前 `scripts/test_lumos.py` SHA256 與 baseline 均為 `bbf4862d7281add86980dd152e13e25139ccb0e419bbe133f14b3a443a74a5cb`。  
圖譜 `Systems/codex-harness` 與 F2 計劃：已讀；finding 1 與「不信、不碰」的既有路徑信任判準衝突。  
驗證：`lens_cache_read` 6 passed、`deadline_final_cache_read` 2 passed、`lens_warmer` 13 passed、`lens_spawn` 7 passed；上述故障注入另行穩定重現。

總結：最嚴重 severity: major；blocking 1 條
