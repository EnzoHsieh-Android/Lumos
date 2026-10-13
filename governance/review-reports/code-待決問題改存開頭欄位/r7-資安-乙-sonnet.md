severity: clean

已看,無可利用的洞,各類結論如下:

1. 命令與暫存
   - 子程序只有 `subprocess.run(["git","show","HEAD:scripts/lumos"], cwd=repo)`,用的是參數陣列,沒有 shell,也沒有拼接使用者輸入。
   - 取出的是被測 repo 自己的 HEAD 版本。它和 CI 本來就要執行的程式同一信任等級,沒有多出新的信任面。
   - 舊版檔案寫進 `mkvault()` 的暫存目錄,不在 repo 內,也不在 `~/.cache`。
   - `tempfile.mkdtemp(prefix="qfmr6-wb-")` 用的是預設的 0700 目錄。這個目錄沒有被清掉,但只是衛生問題,沒有利用路徑。
   - 符號連結和壞連結都建在自己的暫存根目錄裡。測試對它們只做「被擋下」的斷言,沒有寫入。
   - 被換掉的全域狀態(`Path.read_bytes`、`_excl_lock_try`、`builtins.open`、`sys.argv`)都放在 `try/finally` 裡還原。
2. 筆記:新增的圖譜筆記是純說明文字,沒有叫代理執行指令或外傳資料的指示。我掃過零寬、方向控制(bidi)和 BOM 字元,只有合法的 emoji 組字序列(ZWJ、FE0F)和 `\u00ad` 軟連字號,都出現在測試的合法值清單裡,不是藏匿字元。
3. 密鑰與個資:已看,無。
4. 執行邊界:`rglob` 只讀 `repo/docs` 底下的 `.md` 檔,是 repo 內路徑,沒有讀 repo 外的檔,也沒有寫使用者全域設定。
5. 其他與新依賴:新增的 import 都是標準函式庫(`importlib`、`ast`、`contextlib`、`io`),沒有新依賴。

整體已看過,這份 patch 沒有可利用的資安問題。
