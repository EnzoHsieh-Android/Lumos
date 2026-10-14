severity: major

審查範圍:修補差異 `/tmp/code-推送前收集-r4-repair-hook.patch`,並對照 `/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/scripts/hooks/pre-push` 全檔。換群組那段 Python 的離開碼,我在 macOS 實跑了兩種情況。

## Findings

severity: major
blocking: 是 — 在原生 Windows 的 python(掛鉤明文支援 `C:\` 路徑的 PATH 找法與 `py -3` 備援)上,每片都在起跑的那一刻失敗,所有推送都被擋,而且擋下訊息是錯的。
引句:「os.setpgid(0, 0); os.execv(sys.argv[1], sys.argv[1:])」
問題:`os.setpgid` 在原生 Windows 的 Python 上不存在。沒有任何 `hasattr` 檢查,也沒有退回「不換群組直接跑」的路。修補前這條路是直接 `"$PY" test_lumos.py`,在 Windows 能跑。就算 `setpgid` 過了,Windows 的 `os.execv` 也不是替換行程,而是起新行程後讓父行程結束,離開碼語意也不同。
具體失敗情境:在 Git for Windows 底下推送,`$PY` 是 `C:\...\python.exe`,片一起跑就丟 AttributeError、離開碼 1。`run_group` 把 1 當 `_bad=1`,掛鉤印「擋下:test_lumos.py 有紅」。但 log 裡沒有任何 `✗ ` 行,「紅的是這幾支」是空的,只有 traceback。推送永遠過不去,使用者唯一的出路是 `--no-verify`。
佐證:``file: `scripts/hooks/pre-push:203` `` 與 ``file: `scripts/hooks/pre-push:236-250` `` 明文處理 `[A-Za-z]:[\\/]*` 的 Windows 路徑。換群組的 Python 字串在 ``file: `scripts/hooks/pre-push:807` ``。
建議:包成 `if hasattr(os,'setpgid'): os.setpgid(0,0)`,Windows 上改用 `subprocess` 等價或直接略過。

## 逐項回答重點

- 換群組失敗時的離開碼:`$PY` 經 `_lumos_py314` 驗過,是絕對路徑且可執行,所以 `execv` 找不到檔在 POSIX 實際上不會發生。我造了不存在的路徑實測,離開碼是 1(traceback)。`run_group` 把它當 `_bad`,回 1,掛鉤擋推送,所以是 fail-closed。它的 log 只有 traceback 沒有 `✗ ` 行,這是訊息品質問題,不是漏擋。已讀,無其他 finding。
- 各片離開碼收集:`execv` 保留 pid,所以 `$!` 與 `wait` 拿到的仍是測試程式本身的離開碼。我實測 `sys.exit(3)` 經過換殼後離開碼仍是 3,「每片都選中 0 支」的 rc3 判定照舊正確。被訊號殺掉的片是 128+N,屬 `_bad`。已讀,無 finding。
- 只有子殼收到 HUP,回 1:子殼 `exit 129`,主殼的 `wait` 得到 `_grc` 或 `_krc` 為 129。`_grc` 非 0 就 `_rc=1`,`_krc` 非 0 且非 3 也 `_rc=1`,最後 `exit 1`,一定擋。TERM(143)走同一條。已讀,無 finding。
- 主殼收到 HUP,回 129:主殼 `exit 129` 是非 0,git 一定中止推送。主殼收到 INT 是 130,TERM 是 143,同理。已讀,無 finding。
- 終端機 Ctrl-C 與前景群組:各片在自己的背景群組,終端機的 INT 不會直接送給它們。子殼是非互動 bash 的背景命令,SIGINT 被忽略。路徑是主殼的 INT 陷阱呼叫 `_pp_kill_jobs`,對子殼先試 `kill -- -pid`。子殼不是組長,這步失敗後退回只送它本人 TERM。子殼的 TERM 陷阱再對每個片整組送 TERM。片剛起還沒換群組的空窗,群組還不存在,也退回只送片本人 TERM,此時它還是 Python 啟動中,預設 TERM 會殺掉它。我讀不到洞。已讀,無 finding。
- 資料狀態五問:
  - 暫存 log 目錄:`$_PP_TMP` 由 EXIT 陷阱整個清掉,被殺時各片寫到已刪的檔,無殘留。
  - 離開碼:上面三項已涵蓋。
  - pid 重用:`kill -- -pid` 只在 pgid 等於組長 pid 時成立,組長活著時 pid 不會被重用。窗口極小,不構成 finding。
  - 訊號繼承:`execv` 保留被忽略的訊號,Python 自己本來就忽略 SIGPIPE,與修補前行為一致。
  - 既有狀態:殘留的孤兒群組與修補前一樣,只有掛鉤被 SIGKILL 時才發生。

最高等級 major,blocking 1 條。
