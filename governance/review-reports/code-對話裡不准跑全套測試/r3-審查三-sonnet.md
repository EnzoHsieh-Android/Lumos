severity: minor

## 發現

### 1. 守衛測試用字串比對,拿掉 `_trusted_private_dir` 呼叫仍然全綠
severity: minor
blocking: 否

引句:「bool(mm) and ("_trusted_private_dir" in mm.group(0) or "_lens_arm_dir_ok" in mm.group(0)),」

- 新函式 `_home_cache_append_line` 的 docstring 寫了「(_mkdir_trusted_under_home、_trusted_private_dir)」。這個測試只看函式區段文字裡有沒有這個字串,docstring 就讓它過了。
- 重現:我在 `/tmp/lumos-seat-work/code-對話裡不准跑全套測試/審查三-sonnet/m` 用修後版 741e4c578 的複本,刪掉函式內的 `if not _trusted_private_dir(d, *segments): return False`。
  - `-k private_dir_trust_shared` 結果是 20 passed、0 failed,「_home_cache_append_line 有走共用的信任檢查」仍是 ✓。
  - `-k drift_m1` 是 252 passed,`-k runner_chat` 是 21 passed,都沒紅。
- 行為上差在「已存在、群組可寫(例如 0770)的最後一層目錄」。`_mkdir_private_layer` 遇到已存在的目錄直接回 True,只有 `_trusted_private_dir` 會擋。這個案例沒有任何測試覆蓋。
- 歸因:未判定。舊版同一支測試用同樣的字串比對,但舊 `_drift_m1_ledger_miss` 的 docstring 沒有這個字串。把檢查搬進有 docstring 的新函式後,這個漏洞才第一次對這一處有效,偏向有證據的修復回歸。我沒有跑舊版的對照,所以標未判定。
- 建議:補一支真跑的案例,預先建好 0770 的 `~/.cache/lumos/full-suite-guard`,斷言回 False、檔案沒被寫。

## 核對

**① 修補宣稱的行為證據**
- 守衛測試改盯共用函式,並驗兩個呼叫端:
  - 兩條 `check` 在修後版確實 ✓。`_drift_m1_ledger_miss` 那條比對的是 `_home_cache_append_line(`,`_chat_guard_log` 那條比對的是 `._home_cache_append_line(`。
  - 兩處的 docstring 都沒有誤命中,但比對只認字串。呼叫端改成呼叫別的函式,只要文字裡還留著這個名字就不會紅。
- 快取目錄是連結時照擋、不寫到別處:新 S3 子程序案例在 `-k runner_chat` 21 passed 內通過。
  - 擋住它的是 `_mkdir_trusted_under_home` 逐層檢查,不需要 `_trusted_private_dir`。
  - 所以刪掉 `_trusted_private_dir` 呼叫後這個案例仍會過(見發現 1)。
- 新函式改用 `_regular_own_fd`:程式碼確認 `scripts/lumos:69255` 已呼叫它,`scripts/lumos:1657` 的 `_regular_own_fd` 帶 O_NOFOLLOW 與 O_NONBLOCK,並在開檔後判一般檔與擁有者。

**② 相鄰路徑**
- mode 與 umask:`mode=0o600` 傳給 `os.open`,跟舊寫法一樣只在建新檔時生效。umask 的效果跟舊版相同,只會再收緊。
- 既有 drift_m1 測試(短寫、FIFO、別人的檔):修後版 `-k drift_m1` 252 passed。邏輯上也等價。
  - FIFO:沒有讀端時 `ENXIO` 回 None;有讀端時 `S_ISREG` 不成立,fd 被關閉後回 None。
  - 別人的檔:`st_uid` 不符回 None。
  - 短寫:`os.write(fd, data) == len(data)` 判斷,拋 `OSError` 時回 False。
- segments 含 `..` 或絕對路徑:`_mkdir_trusted_under_home` 對 `..`、`.`、含 `/`、反斜線、絕對路徑的段都回 False,所以函式不寫。`filename` 參數沒有同樣的檢查,`d / "/abs"` 會重置路徑。舊版也是這樣,兩個呼叫端都是字面常數,不算 finding。

**③ 新發現兩版各跑的結果**
- 發現 1 只在修後版跑了變異。舊版 c1d22e04 沒跑,因為舊守衛盯的是 `_drift_m1_ledger_miss`,那條路徑的行為不同,對照沒有意義。

**未驗範圍**:沒有跑全套,只跑 `-k` 子集。沒有對舊版逐項做行為對照。pre-push 閘的 `-k` 抓名邏輯不在這次修補差異內,沒看。

我已刪除自己建的 `/tmp/lumos-seat-work/code-對話裡不准跑全套測試/審查三-sonnet/m`。
