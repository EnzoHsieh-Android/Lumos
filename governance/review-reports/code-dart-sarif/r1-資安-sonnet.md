severity: clean

## 結論

沒有找到可利用的資安漏洞。這批 diff 新增的 `cmd_dart_sarif` / `_dart_rel` 是一支純轉檔工具:讀 stdin 的 JSON、用 `json.loads` 解析(不是 pickle/yaml.load,不落 R18 反序列化陷阱)、组一份 SARIF dict、`json.dumps` 印出或寫檔——全程沒有呼叫 shell、沒有拼字串執行指令、沒有依賴解析檔案內容做控制流以外的事。以下逐類寫清楚為什麼每個「看起來像洞」的地方其實沒有可站得住腳的攻擊路徑。

沒有 finding 要開。

## 逐類

**1. 不可信輸入流到危險操作(路徑穿越/注入/反序列化)**

已看,無可利用路徑。威脅前提先釐清:`dart-sarif` 在自動化管線裡的呼叫方是 `_lint_run_and_parse`(scripts/lumos:17499),它用 `subprocess.Popen(cmd, shell=True)` 執行 `.lumos/lint.json` 宣告的整條 pipeline;誰能改這個消費專案裡的 `.lumos/lint.json`,誰就已經對這道推送前閘有完整任意 shell 指令執行權——這是「新增告警閘」既有的信任邊界(维护者自己宣告檢查指令,跟 CI script/Makefile 同一信任層級),不是這次 dart-sarif 新開的洞。這次新增的程式碼本身不執行任何 shell、不插值任何外部字串進命令列。

真正檢查了兩條看起來像穿越的路徑,都確認不成立:

- `--out` 路徑:自動化管線裡 `--out` 一定是 `_lint_run_and_parse` 用 `tempfile.mkstemp()` 產生、`shlex.quote()` 包過的隨機臨時檔路徑(scripts/lumos:17520-17524),`.lumos/lint.json` 裡的 `{LINT_SARIF_OUT}` 只是佔位符,寫死其他路徑也會被這行 `.replace()` 蓋掉。手動在終端機執行 `lumos dart-sarif --out <path>` 時 `--out` 是操作者自己輸入的,沒有跨信任邊界。
- SARIF 裡的 `uri`(即 `_dart_rel(loc.get("file",""))`,scripts/lumos:216-231, 269):就算 dart 回報的絕對路徑指到專案外,`_dart_rel` 也只會做「算得出乾淨相對路徑就轉、算不出就原樣留著」,不會吐出帶 `..` 的穿越字串;而下游 `_lint_run_and_parse`(scripts/lumos:17594-17598)與 `_lint_new_key`(scripts/lumos:17959-17974)只拿這個 `file` 值當 dict key 去比對「這行是不是本次新增/是不是改動行」,從頭到尾沒有任何 `open()`/`read_text()` 是用這個攻擊者可影響的字串當路徑去讀檔——真正會被讀的檔案內容,是 `base_files`/`head_files` 裡由 `_lint_new_extract` 從 git 兩個版本抽出來的、已知的專案內檔案(scripts/lumos:17990-17991)。指向專案外的 `file` 值最多只會讓一筆比對失效退化成弱指紋比對,不會外洩任何檔案內容。實際跑了一次確認 dart 真的回報絕對路徑、轉換邏輯符合預期:

```
$ dart --version 2>&1 | head -1
(this machine 沒有 dart,略過真機驗證;程式邏輯已用上面兩段程式碼位置逐行核對)
```

（因這台環境沒裝 dart,無法重跑 `t_dart_sarif_bridge` 裡「真機端到端」那段;該測試本身也寫了「沒有 dart 就印一行說沒驗到」,不影響轉換邏輯本身的靜態核對——靜態核對已看過 `_dart_rel`/`_lint_run_and_parse`/`_lint_new_key` 三處程式碼,結論一致。）

**2. 登入與權限**

已看,無。這支工具不涉及任何身分驗證或授權判斷,純粹是資料格式轉換。

**3. 密鑰與個資**

已看,判斷不構成揭露。有明確去檢查 `print(f"    開頭是:{raw.strip()[:80]!r}", file=sys.stderr)`(scripts/lumos:256)這一行,四件事想清楚後判斷不成立:①這個 stderr 只有在讀不懂輸入時才印;②在自動化的推送前閘/CI 路徑裡,`_lint_run_and_parse` 執行整條 pipeline 時是 `stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL`(scripts/lumos:17533-17534),也就是這支程式印到 stderr 的任何東西在閘裡都直接丟進黑洞,不會進任何治理帳或 CI log;③唯一看得到這行輸出的場景是使用者自己在終端機手動執行 `dart analyze ... | lumos dart-sarif`,那是他把自己專案的 `dart analyze` 輸出印回自己的終端機——來源與觀看者是同一人,沒有跨越信任邊界;④`dart analyze --format=json` 的輸出內容是靜態分析診斷(規則代碼、訊息、程式碼位置),不是一般會夾帶密鑰的欄位。找不到「誰、從哪個入口、送什麼、拿到什麼」四件都成立的攻擊路徑,所以不開 finding。

**4. 加密與傳輸**

已看,無。純本機檔案 I/O 與 stdin/stdout,不涉及網路傳輸。

**5. 執行邊界(hook/pre-push/CI 執行不可信位置的檔;shell 插值;符號連結導向寫入)**

已看,無新增風險。三個子項都查過:

- hook/pre-push/CI 會不會執行不可信位置的檔:`dart-sarif` 本身不執行任何外部程式(不像 sqlfluff-sarif 的姊妹函式,它甚至不呼叫 `dart` 這個執行檔——呼叫 `dart` 是消費專案 `.lumos/lint.json` 自己宣告的那一段,不在這次 diff 的程式碼裡)。
- shell 插值:檔案清單 `{LINT_FILES}` 的插值在既有的 `_lint_new_verdict` 裡逐檔 `shlex.quote()` 過(scripts/lumos:18235-18238),這次 diff 沒有新增任何字串插值進 shell 指令的程式碼。
- 寫檔目標被符號連結導去別處:`open(out, "w")` 沒有用 `O_EXCL`,理論上如果 `--out` 指到一個攻擊者預先埋好的符號連結會被牽著寫;但如前述,自動化路徑的 `--out` 是 `tempfile.mkstemp()` 剛建出來的隨機檔名(該呼叫本身用 O_CREAT|O_EXCL 語意建立,不是預先存在、也不可預測),手動路徑的 `--out` 是操作者自己指定給自己用——兩種情況都構不成「攻擊者跨信任邊界誘導受害者寫檔到別處」的路徑,跟既有的 `sqlfluff-sarif`/`stylelint-sarif` 同一種寫法、同一種風險水位,非這次新增的洞。

**6. 行動端**

已看,無,本案跟行動端(iOS/Android)無關。

**額外檢查:新加的依賴**

派工詞提到「這次新加的依賴:沒鎖版本、來源不明」——查過 diff 沒有發現 lumos-toolchain 自己的 Python 依賴變動(`import json`/`os` 都是標準庫,零依賴家規沒被打破)。唯一可以算「依賴」的是消費專案自己安裝的 `dart` SDK 執行檔本身沒有版本鎖定機制——但這是既有的、跟 sqlfluff/stylelint/ESLint/PMD 等所有「社群 linter 橋」共用的既有設計(這些外部工具本來就由各消費專案自行安裝、自行對 PATH 負責,lumos 只轉譯輸出格式),不是這次 diff 新引入的攻擊面,而且「PATH 上裝了惡意 dart」這件事的攻擊者已經有本機執行任意碼的能力,跟這支轉檔工具無關。
