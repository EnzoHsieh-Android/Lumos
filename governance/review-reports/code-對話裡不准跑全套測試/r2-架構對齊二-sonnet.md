severity: minor

我沒有動鎖檔:`/Users/enzo/.cache/lumos/dispatch-lens/540c51c2573a49d60cb8d773562ed8441aa83ab70c847c85db71a17a54f675b2.json.warming` 不存在,`ls` 回「No such file」。審查材料是 r2-snapshot.patch 與 r2-repair.patch,對照的是 `/Users/enzo/orca/workspaces/lumos-toolchain/block-fullsuite` 的 c1d22e04。

**問 1:分層與依賴方向。** 兩處都對齊,只有位置有一條 minor。

- **呼叫方式對齊。** 執行器用 `_load_lumos_inproc()._home_cache_append_line(...)` 呼叫 scripts/lumos,跟測試總檔既有做法同形:
  - `scripts/test_lumos.py:71`、`scripts/test_lumos.py:104`、`scripts/test_lumos.py:49059` 都是這樣呼叫。
  - 載入函式在 `scripts/test_lumos.py:240`,有快取單例。
  - 執行器這端沒有自己另開一條載入路徑,沒有跨層直呼。
- **命名前綴對齊。** `_home_cache_append_line` 跟 `_home_cache_write`(`scripts/lumos:69250`)、`_home_cache_evict` 同一個前綴。
- **位置不在同一處。** 新函式放在 `scripts/lumos:62015`,緊貼原本的 `_drift_m1_ledger_miss`(`scripts/lumos:62044`)。家目錄快取那群函式在 `scripts/lumos:69250`、`scripts/lumos:70044`、`scripts/lumos:70124`,兩邊差約 7000 行。
- **參數形狀不同。** `_home_cache_write(subdir, path, data)` 把 `.cache/lumos` 寫死,新函式接 `segments` 全段,形狀比較像 `_mkdir_trusted_under_home(*rel_segments)`。

1. 新函式的位置與那一群不在一處,而且參數形狀跟同前綴的 `_home_cache_write` 不同。
severity: minor
blocking: 否
引句:「def _home_cache_append_line(segments, filename, line):」
佐證:`scripts/lumos:69250`(`_home_cache_write`)、`scripts/lumos:70124`(`_mkdir_trusted_under_home`)

**問 2:命名與錯誤處理。** 都對齊,沒有 finding。

- **回傳值。** 新函式回 bool、不丟例外,跟 `_home_cache_write`(`scripts/lumos:69250` 一帶,失敗回 False)和原本的 `_drift_m1_ledger_miss` 一致。
- **執行器吞例外的範圍。** 用 `except Exception`,對照 `scripts/test_lumos.py:105`(載入 scripts/lumos 後吞)與 `scripts/test_lumos.py:49060`(載入失敗轉成 ValueError)。三處都是「載入 scripts/lumos 可能丟任何例外」的同一種寬接。程式註解也寫了理由。
- **不是只攔 OSError。** 因為這裡包含載入步驟,範圍跟鄰居一致。
- **回傳值被忽略。** 執行器沒用回傳值,屬於「計數盡力而為」的設計,不算不對齊。

**問 3:第二種做法。** 家目錄附加寫入現在只剩一種,但 scripts/lumos 內仍有一處重複手寫。

- **家目錄快取的附加寫入。** 全檔 `O_APPEND` 與 `open(..., "a")` 掃過,其餘 `open(path,"a")` 都是寫 repo 內的治理帳或 `.kill-log`:
  - `scripts/lumos:1855`
  - `scripts/lumos:1988`
  - `scripts/lumos:27862`
  - `scripts/lumos:60027`
  - `scripts/lumos:72269`
  - `scripts/lumos:73831`
  - 它們不碰 `~/.cache`,所以沒有別處手寫「家目錄快取附加一行」。
- **有一處重複。** `scripts/lumos:1657` 的 `_regular_own_fd` 和 `scripts/lumos:1695` 的 `_local_ledger_append` 已經有「`O_NOFOLLOW`、`O_NONBLOCK`、開了確認是自己的一般檔、單次 `os.write` 核對長度」這一整套:
  - `_regular_own_fd` 的 docstring(`scripts/lumos:1660`)明說這套是照 `_drift_m1_ledger_miss` 那段抽出來共用的。
  - 新抽的 `_home_cache_append_line` 又把 `os.open`、`fstat`、`S_ISREG`、`os.write` 手寫一遍,沒有改呼叫 `_local_ledger_append(path, line)`。
  - 這段重複原本就在 `_drift_m1_ledger_miss` 裡,這次只是搬位置,所以不算新引入。但這次把它升格成「單一來源」,第二份卻留著。我判不準要不要算 major,標 ⚠,先記 minor。

2. 新函式的「開檔、確認是自己的一般檔、核對寫入長度」仍是手寫一份,`_local_ledger_append` 已有同樣的流程。
severity: minor
blocking: 否
引句:「if not _stat.S_ISREG(fst.st_mode) or (hasattr(os, "getuid") and fst.st_uid != os.getuid()):」
佐證:`scripts/lumos:1657`、`scripts/lumos:1695`、`scripts/lumos:1660`
⚠ 判不準:兩套的差別是 `_regular_own_fd` 吞 `ValueError`,而且開檔失敗時回 None 而不是 False。若這是刻意的,要在 docstring 寫明為什麼不共用。

不對齊共 2 條,其中 major 0 條。
