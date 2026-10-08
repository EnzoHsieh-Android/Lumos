severity: major

severity: major

blocking: 是

引句:「當啟動失敗清掉原鎖後另一程序取得同名鎖，`_lens_wait_or_warm` 應保留新鎖」

file: `governance/review-reports/design-背景啟動失敗即時回報/r1-snapshot.md:34`

file: `scripts/lumos:33921`

finding: S4 只測「原鎖已清掉後」才換入替代鎖，漏掉 `Popen` 尚未拋回 `OSError` 時原鎖已被換走的交錯。現碼捕捉例外後直接按路徑 `unlink()`，沒有核對建鎖時的 inode／唯一 token；照快照只新增回傳狀態與事後快取重讀，仍會刪掉替代持有者的鎖。現有 `_excl_lock_try` 已在建鎖失敗清理使用 `(st_dev, st_ino)` 防同類誤刪，見 `scripts/lumos:33853`。

重現:
```bash
python3.14 - <<'PY'
import contextlib, importlib.machinery, importlib.util, io, tempfile
from pathlib import Path
from unittest import mock
p = Path("scripts/lumos").resolve()
loader = importlib.machinery.SourceFileLoader("lumos_review", str(p))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec); loader.exec_module(m)
with tempfile.TemporaryDirectory() as d:
    root = Path(d); cache = root/"cache.json"; lock = root/"cache.json.warming"
    state = {}
    def replace_then_fail(*a, **kw):
        lock.unlink()
        state["acquired"] = m._excl_lock_try(lock, m._LENS_LOCK_STALE_SEC)
        state["before"] = lock.exists()
        raise OSError("sync failure")
    with mock.patch("subprocess.Popen", side_effect=replace_then_fail), \
         contextlib.redirect_stdout(io.StringIO()):
        m._lens_wait_or_warm(root, cache, "a..b", root, True, 0)
    print(state, "after=", lock.exists())
PY
```
輸出為 `{'acquired': True, 'before': True} after= False`，替代持有者的新鎖被失敗端刪除。S4 必須把換入點放在 `Popen` side effect 內，並要求失敗清理只刪建鎖時記住的同一身份。

severity: minor

blocking: 否

引句:「讀不到則回 rc 2，兩者都不按「曾取得」刪新鎖」

file: `governance/review-reports/design-背景啟動失敗即時回報/r1-snapshot.md:34`

finding: cache miss 只能證明「替代持有者尚未寫出快取」，不能證明沒有替代背景工作。固定提示應限定為「本次背景未啟動」，並明示同名鎖可能已由其他工作持有；事件可記本次 spawn error，但不能宣稱整體沒有背景工作。

重現/因果: P1 Popen→OSError → P1 安全清原鎖 → P2 取得同名鎖並開始暖機 → P1 單次重讀在 P2 寫入前回 None → S4 規定 rc 2 → S2 規定輸出「背景未啟動」，與 P2 已運行矛盾。

總結: 最嚴重 severity high；blocking 1 條。
