severity: clean

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/8fcd76cbd3ef92d818ce2fc38fd1b2a986c5e65196c7fa1ed7f23711017b1316.json.warming` 不存在(`ls` 回 No such file),我沒動任何鎖。我讀了 r1-snapshot.patch 裡 `scripts/lumos` 的覆蓋準備物件、Gradle 初始化腳本、續跑快取與 reach 事件顯示,以及測試檔的子程序與暫存用法。實驗與臨時 repo 都沒開,所以沒有暫存要清。

**①提示注入:已看,無。**
- 進到輸出或帳的文字有兩種:reach 的條款字樣與 reach_why。
- 條款字樣印出前都過 `_kill_esc`。reach_why 只取固定字串表(覆蓋接不起來、分析失敗等),不收外來自由文字。
- `_choice_ledger_aux` 對帳上欄位逐欄檢查型別,型別不對的略過。
- 覆蓋分析失敗時,gradle 輸出尾巴不會進 reach 事件。

**②讀寫與執行越界:已看,無。**
- 初始化腳本與分析腳本寫在隔離樹的 scratch。scratch 是 `tempfile.mkdtemp`(0700)建的資料夾,路徑不可預測,寫檔不會被捷徑帶走。
- `--init-script` 與 `-PlumosCovManifest=` 的路徑都經 `_cmd_arg_quote` 包過,值只來自 scratch,不是外來字串,沒有 shell 插值洞。
- `run_cmd` 與模組、任務名本來就是專案設定;`_choice_cov_analyze_cmd` 對模組名用 `re.escape` 比對,再用 `lambda` 替換,不會被當成正規式。
- 刪 AGP 固定位置的 exec:`_choice_cov_exec_path` 先做 `os.path.realpath`,再要求結果落在隔離樹 `c.wt` 底下,捷徑指到樹外就回 None、不做。`os.unlink` 只刪那個已解析的真實路徑。
- 複製 exec 到 `.lumos/note-audit/choice-cov/<at_sha>/`:
  - `at_sha` 先過 `[0-9a-fA-F]{7,64}` 白名單;
  - 目錄走 `_note_audit_safe_dir`,符號連結拒用;
  - 檔名是雜湊,不含外來字串;
  - 寫入走暫存檔再 `os.replace`;
  - 清舊目錄只 `rmtree` 非符號連結的真目錄,`ignore_errors=True`,不跟連結。
- Groovy 分析腳本只讀 class 與 exec,輸出寫到清單指定的 scratch 路徑。清單裡的 `mm.pkg` 來自原始檔 `package` 宣告,正規式 `[\w.]+` 把點換成斜線,組不出 `..` 路徑段。
- `_choice_cov_read` 限檔案大小,讀到的內容只交給 JaCoCo 解析,不會往外輸出。
- 沒有新增下載來源、依賴或密鑰、信箱。測試檔的 `#!{sys.executable}` 假 gradlew 與 `mkdtemp(prefix="gctl-ckc-")` 暫存是測試自己的現場,沒有拼接外來字串執行。

**③非刻意、一步就能繞過的守衛:已看,無。**
- 非刻意環境:覆蓋是否開啟只看 `.lumos/config.json` 的 `coverage` 布林,`_platform_cov_flag` 對非布林丟 ValueError(照「設定錯誤」那條路擋下),不讀 `LUMOS_SKIP_*` 之類環境變數。
- 檔名帶空白或中文:`_choice_cov_exec_path` 與分析指令都走 `_cmd_arg_quote`,不會因空白失效。
- Ctrl-C:`_KillPrep.on_signal` 在第一個訊號就收掉帶標記的程序群組,`after`、`red_rerun`、`_analyze` 都檢查 `interrupted` 後丟 `_KillHalt`,不會把中斷當成覆蓋結果寫進帳。
- 覆蓋接不起來、斷路、分析失敗、時間不夠都落到 unknown 並改跑全部守的測試,沒有「覆蓋壞了反而少跑測試」的路,所以守衛不會被意外走過。
- `.lumos/note-audit/choice-cov/` 底下的 exec 若被外來內容占位或換成連結,屬刻意多步偽造,在系統天花板之外,不報。

總結:最高等級是 clean(三類逐類已看,無可報的發現)
