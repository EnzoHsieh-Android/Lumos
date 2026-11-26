severity: clean

審查範圍:`r2-snapshot.patch` 的 `scripts/lumos` 部分,重點是 r2 新增的四處:exec 讀者看 `org/robolectric/`、`_choice_cov_prune`、`_choice_init_file_write`、`-PlumosCovVariant` 與 `_choice_cov_analyze_cmd`。repo 根的現行程式我也對過。派工詞裡的鎖檔 `…647e0b825a/….json.warming` 不存在,所以沒有鎖要處理,也沒刪任何東西。

**① 提示注入:已看,無**
- 進到給 AI 的文字有三種:`_choice_reach_text` 印的 `reach_clauses`、`reach_why`,以及存活行的印字。前兩者都過 `_kill_esc`(控制字元、雙向覆寫、零寬換成可見的 `\uXXXX`),`reach_why` 另截 40 字。
- 條款字樣來自計劃檔路徑與條款號。路徑裡的惡意字元會被跳脫,不會變成指令或換行。
- `reach_done` 寫進帳的 note 帶檔名,走 JSON 序列化,不是文字拼接。
- 讀端 `_choice_ledger_aux` 對每個欄位檢查型別,`reach` 必須是 clause、none、unknown 三值之一,否則略過。

**② 讀寫與執行越界:已看,無**
- **寫初始化腳本到 scratch**:
  - `scratch` 是 `tempfile.mkdtemp`(權限 0700),腳本檔名是常數,路徑不含外來字串。
  - `_choice_init_file_write` 只是把原本的 `open(..., "w")` 抽出來,沒有新增路徑或權限。
  - 分析輸出 `lumos-cov-out.json` 與清單 `lumos-cov-manifest.json` 也在同一個 0700 資料夾。
- **刪 AGP 固定位置的 exec**:
  - `os.unlink(self.ep)` 的 `ep` 是 `os.path.realpath` 解析後的路徑。`_choice_cov_exec_path` 另外要求它落在隔離工作樹的 `realpath + os.sep` 底下,不在就回 None,不刪。
  - 工作樹裡提交進來的符號連結會被 `realpath` 先解開,指到樹外就被擋。
  - 變體名只能是 `[A-Z][A-Za-z0-9]*`,不能帶路徑分隔字元。
  - 跑測試期間被換掉檔案的情形,測試碼本來就能在同一使用者下做任意事,不是新增的洞。
- **刪快取資料夾**:
  - `_choice_cov_prune` 先過 `_repo_path_unsafe(rr, rel, dirs=True)`,逐層擋符號連結,也擋解析後跑出 repo 根。
  - 只刪 `top.iterdir()` 裡「是資料夾、不是符號連結」的項目,而且只刪最舊、超過保留數的那幾個。
  - `shutil.rmtree` 不跟連結走,符號連結本身不跟、不刪。
  - `cur = top / str(at_sha)` 在 `_choice_cov_prune` 裡沒先驗 at_sha 格式,但只對它做 `os.utime`,不刪。
  - 建快取目錄的 `_choice_cov_dir` 有驗 at_sha 是 7 到 64 碼的十六進位。
- **組 Gradle 指令**:
  - `-PlumosCovVariant=` 的值取自 `shape["task"]` 的 `fullmatch(test([A-Z][A-Za-z0-9]*)UnitTest)`,只含英數字。
  - 初始化腳本路徑與 `-PlumosCovManifest=` 都過 `_cmd_arg_quote`(POSIX 用 `shlex.quote`、Windows 用 `list2cmdline`)。
  - 路徑只由 mkdtemp 的目錄加常數檔名組成,沒有外來字元。
  - 其餘片段來自 `run_cmd`(專案設定,屬信任邊界)。`head`、`tail` 是 `run_cmd` 切開的兩段,原樣接回。
- **Groovy 端**:
  - `compile${v}Kotlin` 只拿來比對任務名,不是執行。
  - 清單裡的 `pkg` 來自 `package\s+([\w.]+)`,轉成斜線後只用來 `new File(root, pkg)` 找類別資料夾,並且只取副檔名為 `.class` 的檔。
  - `pkg` 的字元集只有英數、底線、點,點換成斜線後不會產生 `..` 路徑穿越。
  - exec 檔只交給 JaCoCo 的 `ExecFileLoader` 當資料解析,不會被執行。
- **exec 讀者**:
  - `_choice_cov_exec_classes` 以位元組逐區塊解析,不認得的區塊、被截斷的區塊、版本不對都回 None。
  - 單份讀取上限 `_CHOICE_COV_OUT_MAX` 是 8MB,讀取前先看是不是一般檔。
  - `org/robolectric/` 前綴比對只是字串判斷,沒有路徑或執行語意。
- **密鑰與信箱**:diff 的程式與範本裡沒有新增。

**③ 非刻意、一步就能繞過的守衛:已看,無**
- **Ctrl-C**:`after()` 開頭先看 `interrupted` 就丟 `_KillHalt`;`_analyze` 跑完、`red_rerun` 跑完後也再看一次。中斷不會被記成「沒有條款經過」。
- **覆蓋判成存活的方向**:舊 exec 讀不出來、`ep` 刪不掉、分析失敗、時限不夠,結果都落在 unknown,壞法照跑全部守的測試。這個方向只會多跑,不會把「沒測試守著」誤放成「已殺掉」。
- **Gradle 任務被判為最新而不執行**:`wrap` 在每支測試跑之前刪 `ep`,所以沒有新檔就是「覆蓋資料沒產出」,讀不到上一支測試留下的檔。
- **檔名帶空白、中文或換行**:`ainit` 與 `man` 的檔名是常數,目錄來自 mkdtemp,引號走 `_cmd_arg_quote`。Windows 路徑有 cmd.exe 特殊字元時 `_choice_merge_init_path` 回 None,整條覆蓋路徑關掉。
- **環境變數殘留**:這段程式不新增任何讀 `LUMOS_SKIP_*` 或 `PYTHONPATH` 的點。

總結:最高等級是 clean(三類都已看,沒有可利用的洞)
