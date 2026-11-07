severity: clean

審查範圍:`r2-repair.patch` 整份,重點是 `scripts/lumos` 的 `_plan_first_days`、`_plan_src_path_ok`、`_plan_sources_block_event`、`_plan_sources_since`,以及測試檔裡會執行到的程式。

**核對第一輪那條(生效日環境變數殘留)**
- 已修好。修補後 `_plan_sources_since` 在環境變數覆寫生效日時,會往 stderr 印一行「〈依據來源〉生效日被環境變數覆寫為 X(LUMOS_PLAN_SOURCES_SINCE;原本是 …)」。
- 同一個值每個程序只印一次,靠 `_PLAN_SOURCES_SINCE_TOLD` 去重。
- 這樣殘留的環境不會再無聲失效。
- 測試檔裡設定這個變數的地方有 try/finally 還原(`old = _os_mod.environ.get("LUMOS_PLAN_SOURCES_SINCE")` 那段)。

**逐類**
- ①提示注入:已看,無。
  - 出處格原文寫進治理帳的 `cells` 欄位,取前 200 字,經 JSON 逸出。
  - 新加的 `fp` 欄是 sha256 指紋,不含自由文字。
  - 這份 diff 沒有任何把這些欄位印給 AI 的新讀取端。
  - HTML 註解去除只影響判定的文字,沒有進派工詞。
- ②讀寫與執行越界:已看,無。
  - `_plan_first_days` 的 git 呼叫全是 argv 陣列,沒有 `shell=True`,也沒有 shell 插值。
  - 新增的整 repo `git log` 只讀歷史,不碰工作樹檔案。這類 git 子指令不會觸發 `core.fsmonitor` 之類的 hook。
  - `_plan_src_path_ok` 把出處格反引號裡的路徑(外來文字)放在 `--` 之後交給 `ls-tree`,所以以 `-` 開頭的路徑不會被當成選項。
  - 讀符號連結目標用 `_git_tree_text` 讀 HEAD 的 blob,只做字串正規化判斷,沒有跟過去讀 repo 外的檔。
  - 連結指到絕對路徑或跑出 repo 的一律不算出處。
  - `_validate_repo_ref(at_sha="HEAD")` 只查版控樹的存在,不讀檔案內容。
  - `_plan_sources_block_event` 只讀寫 `docs` 下的治理帳,路徑來自 `_docs_ledger_path`,沒有照外來路徑寫檔。
  - 沒有新增下載來源,沒有新增密鑰或信箱。
  - 測試檔裡沒有 `shell=True`、`os.system`,也沒有看起來真能用的憑證。
  - 測試設的 `GIT_AUTHOR_DATE` 等環境變數只作用在自己建的臨時 repo。
- ③非刻意、一步就能繞過的守衛:已看,無新增。
  - 第一輪那條已如上修好。
  - 淺複製或讀不到 git 時,新舊判斷退回只看 `created`;這是上一輪設計決策(d11)已有的設計,也有 stderr 提示,不是新缺口。
  - 逾時往 stderr 印一行,沒有無聲放行。

總結:最嚴重是無(clean),會擋 0 條。
