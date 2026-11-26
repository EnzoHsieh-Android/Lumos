severity: clean

我看了凍結 patch 全部非卷證的檔和 r2 修補差異,沒有找到能被利用的洞。r2 修補差異共四份,範圍是筆記、`scripts/lumos`、`scripts/test_lumos.py`。

**本輪特別想的兩點**

1. **`_cmd_arg_quote` 的引號有沒有變弱:沒有。**
   - 對照修前 `54715c64:scripts/lumos` 的 `_run_cmd_expand`,新函式的運算式逐字相同:Windows 用 `list2cmdline([x])`,其餘用 `shlex.quote(x)`。`{python}`、`{method}`、`--init-script` 三處行為都跟修前一致,沒有任何一條路徑變弱。
   - 在 Windows 上,測試名的 cmd.exe 特殊字元由既有的 `_WIN_CMD_SPECIAL` 擋掉(file: `scripts/lumos:6505-6569`)。
   - `--init-script` 路徑在 Windows 含這些字元時也會回 None、不帶腳本(file: `scripts/lumos:29054-29060`)。
   - 路徑來自 `tempfile.mkdtemp` 的 scratch,在工作樹之外。檔案內容是固定的 Groovy 常數,不含外來文字。
   - 測試名要靠 `{method}`、`_name_filter_escape` 這條路才會進指令,POSIX 上整串經 `shlex.quote`,打不破 shell。
2. **事件行改字串切,外來測試輸出能不能讓工具越界:不能。**
   - `_choice_merge_event_line` 只做 `rstrip`、`rpartition`、`partition`,沒有 eval、路徑拼接、檔案存取或 shell。
   - 解析結果只進 `_choice_merge_events`:先換成完整名,再跟 `names` 比對;沒對到的丟掉。回傳的名字全來自 `names` 清單,不是外來字串,只用來排逐支執行的順序(file: `scripts/lumos:29313`)。外來輸出若偽造 STARTED、FAILED 行,頂多影響跑的順序,不判任何事,也不輸出到 shell 或 AI 派工詞。

**三類逐類結論**

- **①提示注入:已看,無。** 本輪新增的程式與筆記沒有把外部可控的自由文字送進給 AI 的派工詞、hook 附加段或指令。測試輸出只做名字比對,沒有回顯進提示。卷證(`governance/review-reports/` 底下的 patch、`verdict.json`)是純紀錄,沒有被程式讀進來當指令的管道。
- **②讀寫與執行越界:已看,無。**
  - 寫檔只寫在 mkdtemp 的 scratch 底下,該資料夾是剛建的新目錄。
  - 斷路器修補(`_kill_merge_trip`、`hang_breaker`)只動記憶體計數與 stderr,其中 `plat` 照舊經 `_kill_esc`。
  - 沒有新增下載、環境變數覆蓋、密鑰或信箱(我對凍結 patch 的新增行搜過,沒有命中)。
  - 測試新增行沒有 `subprocess`、`os.system`、`shell=True`、`environ` 這類執行外部命令的寫法。
  - `anchor-baseline.json` 的簽章更新是依使用者對話原話「簽」代簽,屬既有流程。
- **③非刻意一步繞過守衛:已看,無。**
  - 斷路器恢復後 `hang_streak` 歸零,這是消除誤跳開,沒有新增繞過點。
  - 重試上限改為 `min(cap, remaining)`,只會縮短時限,不會放寬。
  - 殘留的 `LUMOS_SKIP_*` 或 `PYTHONPATH` 在本輪改到的路徑上不會讓任何守衛被走過。

最高 clean,blocking 0 條
