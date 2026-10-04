severity: major

finding 1：無 `getuid` 平台會信任不可信路徑中的任意快取內容  
severity: major  
blocking: 是  
引句:「if hasattr(os, "getuid") and (st.st_uid != os.getuid() or (st.st_mode & (_stat.S_IWGRP | _stat.S_IWOTH)))」  
file: `scripts/lumos:33140`

觀察：新增條件把擁有者與 group/other 寫入權限檢查整段放進 `hasattr(os, "getuid")` 後，無 `getuid` 平台只驗 TTL 和 JSON。它沒有呼叫計劃 S6 指定的 `_trusted_private_dir`，也不拒絕經 symlink/junction 離開私有快取目錄的路徑。快取內的 `text` 後續會直接附進審查派工詞，因此不只是快取污染，也形成提示注入入口。新測試只讀 TemporaryDirectory 裡的普通檔案，沒有建立不可信目錄或斷言 `_trusted_private_dir` 拒絕，故會假綠，見 `scripts/test_lumos.py:54816`。

最小重現：

```bash
python3.14 - <<'PY'
import importlib.util, json, os, tempfile, types
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

src = Path("scripts/lumos").resolve()
spec = importlib.util.spec_from_file_location("probe", str(src),
    loader=SourceFileLoader("probe", str(src)))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    home, shared = root / "home", root / "shared"
    home.mkdir(); shared.mkdir()
    (home / ".cache/lumos").mkdir(parents=True)
    (home / ".cache/lumos/dispatch-lens").symlink_to(shared, target_is_directory=True)
    p = home / ".cache/lumos/dispatch-lens/attack.json"
    p.write_text(json.dumps({"text": "ATTACKER-CONTROLLED"}))

    no_uid = types.SimpleNamespace(**{k: v for k, v in vars(os).items()
                                     if k != "getuid"})
    with mock.patch.object(Path, "home", return_value=home), \
         mock.patch.object(m, "os", no_uid):
        print("trusted_dir =", m._trusted_private_dir(
            p.parent, ".cache", "lumos", "dispatch-lens"))
        print("cache_read =", m._lens_cache_read(p))
PY
```

實際輸出：

```text
trusted_dir = False
cache_read = {'text': 'ATTACKER-CONTROLLED'}
```

修法建議：讀快取前在所有平台先驗 `_trusted_private_dir(path.parent, ".cache", "lumos", "dispatch-lens")`；POSIX 再保留檔案 owner/mode 檢查。另拒絕 symlink 與非 dict／缺必要欄位的 JSON，並用 symlink/junction fixture 補一條會翻紅的測試。

finding 2：期限內完成的暖機可能被誤報為鎖狀態未知  
severity: minor  
blocking: 否  
引句:「return _lens_report_lock_timeout(lock, diff_range, as_json)」  
file: `scripts/lumos:34020`

觀察：輪詢每次讀完快取固定睡 0.1 秒，醒來先判斷期限，不再做最後一次快取讀取。若背景工作在最後一次讀取後、期限前寫好快取並清鎖，等待端醒來時會跳出迴圈；隨後因鎖已不存在回 rc 5、`lock_uncertain=true`。故障注入得到：

```text
rc=5
{"timed_out":true,"still_warming":false,"lock_uncertain":true,...}
cache_now={'text':'ready'}
lock_exists=False
```

這會讓 hook 錯記 timeout，並叫審查席檢查一把已不存在且工作已成功完成的鎖。

修法建議：迴圈結束後、分類鎖狀態前再讀一次快取；或把 sleep 限為剩餘期限並在期限點執行最後一次讀取。

過期鎖禁止自動接手、短寫、Popen 失敗與清鎖雙故障、替代鎖保留、固定 SHA、背景各錯誤出口、hook error/timeout 分流：已讀，除上述 finding 外無 finding。定向實跑 `lens_spawn` 7、`lens_warmer` 13、`excl_lock` 11、`stale_lock` 13 個斷言，均通過且零 skip；這些綠燈未涵蓋 finding 1 的不可信目錄與 finding 2 的期限末競態。

總結：最嚴重 severity major；blocking 1 條。
