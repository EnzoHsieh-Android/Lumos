severity: minor

我對照了 `scripts/test_lumos.py` 既有的 `patch.object`、`patch.dict` 用法和家筆記摘要行寫法。我也跑了 `python3.14 scripts/test_lumos.py --serial -k fanout_spawn_mask`,3 項斷言都過。

## ① 分層與依賴方向

**零 finding。** 新測試 `t_runner_fanout_spawn_mask` 直接呼叫 `_fanout_spawn`,只換掉 `subprocess.Popen`。依賴方向跟既有的 `t_runner_default_fanout_spawn_error` 一致,沒有新增跨層呼叫,也沒有在被測程式裡加測試專用開關。

引句:「with _mock.patch.object(_sp, "Popen", show_mask):」

對照:`scripts/test_lumos.py:31061`,同檔 `scripts/test_lumos.py:15143` 也用 `mock.patch.object(_subp, "check_output", ...)` 換標準庫函式。

## ② 命名與錯誤處理

**零 finding。** 三項都對得上既有做法:
- **命名:** `t_runner_fanout_spawn_mask`、暫存資料夾前綴 `gctl-fanmask-`,跟同組的 `gctl-fansig-` 一致。
- **清理:** 清理用既有輔助 `_fan_reap`、`_fan_wait_gone`(`scripts/test_lumos.py:30887` 附近),再接 `wait(timeout=5)` 和 `rmtree`,跟同組其他測試的收尾寫法相同。
- **平台缺口:** 缺 `pthread_sigmask` 時丟 `_SrcOnly`,跟同組缺 `SIGHUP`、`setpgid` 時的做法一致。

引句:「raise _SrcOnly("沒有 pthread_sigmask 的平台,開片不擋訊號,這段沒驗到")」

對照:`scripts/test_lumos.py:30978` 附近的 `raise _SrcOnly("沒有 SIGHUP 的平台,這段沒驗到")`。

家筆記的新摘要行也對得上規則:
- 都有 `[出處:]` `[因:]` `[test:]`,沒有過程紀錄。
- 新拆出的 `gctl-run-` 那行是獨立一類,符合「一行一類」。
- 計劃 S8 條款的 `[test:]` 也補上了新測試。

引句:「WHY:開片時擋住的訊號遮罩在子程序開頭還原 [出處:[[Projects/測試總檔預設切片_計劃]] 做法 2]」

## ③ 第二種做法

### 1. 修改自己所在模組的全域名稱,用了檔內沒有先例的寫法
severity: minor
blocking: 否
引句:「_mock.patch.object(sys.modules[__name__], "_fanout_kill", spy)」
對照:`scripts/test_lumos.py:30952` 和 `scripts/test_lumos.py:31024`。整份檔案搜 `sys.modules[` 只有這兩處,沒有別處用這個寫法。

說明:
- **修改被測模組的既有寫法:** 其他測試改被測模組的函式,都是 `patch.object(m, "名稱", …)`,`m` 是匯入的 lumos 模組(例如 `scripts/test_lumos.py:15145`、`:16012`)。
- **修改本檔自己全域的既有寫法:** 這一輪修前是 `globals()["_fanout_kill"] = spy`。
- **為什麼歸為第二種做法:** 新寫法是 `patch.object` 加 `sys.modules[__name__]`,檔內沒有先例。
- **為什麼只列 minor:** 它用的仍是 `unittest.mock`,而且 `patch.object` 本身已經是檔內主流,結構是對的。
- **可行的收法:** 兩處共用的寫法可以收成一個輔助,或在檔內統一用這個寫法。

另外,`_sp.Popen = x` 手動換再還原的舊寫法,在這份檔案裡還有 `scripts/test_lumos.py:114092`、`:118472`、`:120116`。這次改成 `patch.object` 讓切片相關測試少了一種寫法,方向對,不列為 finding。

不對齊共 1 條,其中 major 0 條

總結:全份最高 minor
