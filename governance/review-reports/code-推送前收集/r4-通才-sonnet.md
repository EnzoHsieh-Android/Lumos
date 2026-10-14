severity: minor

**審查範圍**:修補差異 `/tmp/code-推送前收集-r4-repair-hook.patch`,對照 `/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect` 裡的完整掛鉤。我在 `/opt/homebrew/bin/python3.14` 上用小腳本實測了換群組的寫法,實驗目錄已不再需要。我沒有跑掛鉤本身或測試套件。

severity: minor
blocking: 否 — 只影響在 Windows(Git Bash)上推這個 repo 時跑全套測試的路徑,macOS 與 Linux 不受影響,CI 也跑在 ubuntu-latest。
引句:「_PP_OWN_PGRP='import os, sys; os.setpgid(0, 0); os.execv(sys.argv[1], sys.argv[1:])'」
問題:掛鉤內嵌的找 Python 那一段明確支援 Windows(`py -3`、`[A-Za-z]:[\\/]*` 路徑、winget 安裝提示)。新的換群組那行 Python 用了 `os.setpgid`,這個函式只有 Unix 才有。Windows 的 `os.execv` 也不是真的取代行程,而是起新行程後讓舊的立刻結束。
具體失敗情境:在 Windows 的 Git Bash 推送,且走到全套或分片測試時,每一片先是 `AttributeError: module 'os' has no attribute 'setpgid'`,離開碼 1,整套被判紅而擋下推送。即使繞過 `setpgid`,`os.execv` 在 Windows 上會讓外層 Python 立刻回 0,掛鉤的 `wait` 就會在測試還沒跑完時判綠。改前是直接執行測試檔,沒有這個問題。我沒有 Windows 環境可以實測,這條是依據 Python 文件。修法可以是 `hasattr(os, "setpgid")` 才換群組、否則直接 `runpy` 跑測試檔,或在 Windows 上退回舊寫法。
佐證:``scripts/hooks/pre-push: `scripts/hooks/pre-push:810` ``(`_PP_OWN_PGRP` 定義)與 ``scripts/hooks/pre-push: `scripts/hooks/pre-push:832` ``(呼叫端)。

**已讀,無 finding 的部分**
- **離開碼與 log**:`setpgid` 後 `execv` 同一個行程,pid 不變。實測離開碼 3 原樣傳到 `wait`,所以 `rc==3`(每片都選中 0 支)與 `rc!=0`(有紅)的判斷沒壞。stdout 與 stderr 的重導向照舊,log 內容不變,測試輸出沒有受影響。
- **`$PY` 是否可 `execv`**:`$PY` 來自 `_lumos_py314`,已驗證是絕對路徑且是 3.14 以上。`execv` 不查 PATH,我也實測了相對名稱會失敗,但這條路徑走不到相對名稱。`LUMOS_PYTHON` 與 PATH 上有舊版 Python 的情況,都由 `lumos python-path` 與版本檢查先擋,不會走到這行。
- **`py -3` 的組合**:`py -3` 只用來叫起 lumos,不會進到 `$PY`,所以不影響這行。
- **`_pp_kill_jobs` 的其他呼叫點**:掛鉤層的 INT/TERM/HUP 陷阱對 `jobs -p` 列出的對象送 TERM,這些是 `( run_group … ) &` 的子殼,它們不是群組組長。`kill -- -pid` 會失敗,接著退回只送給本人,子殼的陷阱再去整組收各片。這個行為與修補前相同,沒有打到別的群組。
- **子殼裡的 `_pp_kill_jobs`**:各片是組長,整組收得到片自己起的子行程。片剛起、還沒換群組的那一瞬,會退回只送給本人,這是修補自己註解承認的窄縫,不是回歸。
- **Ctrl-C**:片離開前景群組後,tty 的 INT 只到掛鉤。非互動 bash 的背景子殼本來就忽略 INT,掛鉤陷阱再轉成 TERM 去收,收得掉。
- **測試檔裡的群組用法**:`scripts/test_lumos.py` 的 `killpg` 與 `getpgid` 用在自己起的子行程上,和分片的群組無關,沒有牽連。

最高等級 minor,blocking 0 條。
