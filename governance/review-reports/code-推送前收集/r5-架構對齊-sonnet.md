severity: clean

這份修補沒有引入第二種做法,也沒有跨層直呼,沒有發現需要列為 finding 的問題。我只讀了修補差異和既有掛鉤與 `scripts/lumos`,沒有跑測試,也沒有細看 713 行的完整掛鉤差異。

- **runpy 退路**:正式程式(`scripts/lumos`、`scripts/hooks/*`、`scripts/merge-claude-settings.py`)裡,同一行程跑腳本的唯一寫法就是這支啟動器。`runpy.run_path(..., run_name="__main__")` 是它在 Windows 才走的分支,POSIX 仍走 `os.execv`,沒有兩套並行的 POSIX 做法。
  - 對照:`scripts/test_lumos.py:27508` 的測試墊片也用 `sys.argv = ...; runpy.run_path(..., run_name='__main__')`,寫法一致。
  - `scripts/merge-claude-settings.py:52` 和 `scripts/lumos:267` 的 `os.execv` 是 POSIX 的替換行程,跟 Windows 分支分開,不衝突。
  - 兩處起片(`scripts/hooks/pre-push:854` 與 `:858`)都經過同一支 `_PP_OWN_PGRP`,啟動器沒有複製出第二份。
- **收片函式**:`_pp_kill_jobs` 仍是唯一一套收法。新增的第二發 TERM 在函式內部,沒有另開收片函式。
  - 呼叫端 INT/TERM/HUP 三個陷阱(`scripts/hooks/pre-push:321-325`)與 `run_group` 的 TERM/HUP 陷阱(`scripts/hooks/pre-push:850-851`)都走這支。
  - 第二發的 `sleep 0.2` 是函式裡唯一的 sleep,跟既有的 `jobs -p` 加整組 TERM 寫法同一族。
- **掃描器與前提斷言**:`t_prepush_interrupt_launcher_without_setpgid` 用 `re.search` 從掛鉤原文抽出 `_PP_OWN_PGRP`,再用 `_need_src(...)` 守前提,斷言前先確認抽得到、且每個起片處都經過啟動器。這跟既有的原始碼掃描守衛寫法一致,沒有另立一種做法。

最高等級 clean,blocking 0 條。
