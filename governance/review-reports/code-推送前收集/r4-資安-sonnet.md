severity: minor

# 資安席報告(第四輪)

結論:這輪修補本身沒有讓全套測試被繞過的新洞。唯一的發現是環境變數 PYTHONPATH 劫持,這個洞修補前就有,不是這次造成的。

實驗用的是從 patch 抽出的 run_group 與 _pp_kill_jobs、陷阱,配上假測試程式。我沒有跑完整的真掛鉤。實驗環境是 macOS、/bin/bash 3.2、/opt/homebrew/bin/python3.14,實驗目錄已刪。

severity: minor
blocking: 否 — 修補前的舊寫法同樣中招,這輪修補沒有加重;攻擊者要先能控制推送行程的環境變數。
引句:「換到自己的行程群組再 exec 成真正要跑的程式(argv[1:])」
攻擊步驟:
- 輸入:推送時帶 `PYTHONPATH=<含 sitecustomize.py 的目錄>`,內容是 `import os; os._exit(0)`。
- 結果:換群組的那段 Python 一啟動就被 sitecustomize 結束,離開碼是 0,run_group 回 0,測試判綠。
- 實驗證據:`PYTHONPATH=evil bash h.sh` 印出 `group rc=0`。
- 對照:舊寫法 `PYTHONPATH=evil python3.14 fake/test_lumos.py` 也是 `rc=0`。
- 同一個環境變數也會讓其他每個 `$PY scripts/lumos ...` 的閘直接回 0,所以這不是換群組那段獨有的洞。
- 佐證:``file: `scripts/hooks/pre-push:815` ``(`_PP_OWN_PGRP` 本身沒有加固;修的話要整支掛鉤統一處理,不只這一行)

其他重點逐項結果:

- **PATH 劫持**:已讀,無 finding。
  - `$PY` 是 `lumos python-path` 回來並驗過版本的絕對路徑,exec 用的 `sys.argv[1]` 也是它,整段不查 PATH。
  - 實驗:`PATH` 前面放假的 python3.14 與 python3(內容 `exit 0`)後,結果是 `rc=1`,沒有被劫持。
- **PYTHONSTARTUP**:已讀,無 finding。
  - `-c` 模式不讀這個檔。
  - 加上 `PYTHONINSPECT=1`、檔案內容 `os._exit(0)` 也只得到 `rc=1`。
- **目前目錄的 sitecustomize.py 與 os.py**:已讀,無 finding。
  - 實驗:目前目錄放 `sitecustomize.py`(`os._exit(0)`)和 `os.py`(`raise SystemExit(0)`),結果 `rc=1`。
  - 原因是 `-c` 的 sys.path 在 site 載入之後才補上目前目錄。
  - `PYTHONSAFEPATH=1` 結果也是 `rc=1`。
- **sitecustomize 用 `sys.exit(0)`**:已讀,無 finding。site 載入失敗會得到 `Fatal Python error`,離開碼 1,擋下。
- **片被收掉後的離開碼**:已讀,無 finding。
  - 被收掉的片離開碼是 143、137 之類,不會是 3,所以不會被當成「選中 0 支」。
  - 只對子殼送 HUP,得到 `grc=129 krc=129`,兩組都非 0 且不是 3。
  - 只對子殼送 TERM,得到 `grc=143 krc=143`。
  - 掛鉤端的 `_rc` 在這些情形都會被設成 1。
- **訊號打斷時任何路徑回 0**:已讀,無 finding。
  - 對掛鉤送 INT/TERM/HUP,延遲 5–80 毫秒隨機,共 40 次,離開碼只有 130、143、129,沒有 0。
  - 對掛鉤直接送訊號的 40 次,以及每種訊號各一次對假測試 f2 的實驗,都沒有留下 f2 的測試程式或它的 `sleep 37` 孫行程(孫行程驗過;見下方「沒做到的」)。
- **setpgid 或 exec 失敗**:已讀,無 finding。Python 會丟 traceback 離開 1,是擋下,不是放行。
- **kill 的退回路徑**:已讀,無 finding。
  - `kill -- -pid` 對非組長會失敗,轉成只送給 pid 本人。
  - 片剛起、還沒換群組的瞬間,TERM 會直接殺掉那個 python,不會誤送給別的群組。

沒做到的:

- 我沒有跑完整的真掛鉤,只有抽出的片段。假測試程式不是真的 `test_lumos.py`。
- 孤兒行程計數一度出現 1,是我自己的 pgrep 比對到我自己的 shell 命令,不是真孤兒。後續的獨立檢查沒有找到殘留。

最高等級 minor,blocking 0 條。
