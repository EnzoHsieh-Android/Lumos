severity: major

先核對上一輪三條,都修好了。F1(第四份 ls-tree)已處理:`_plan_tree` 改走 `_drift_list`/`_drift_oids`,不再自己跑 `ls-tree`。F2(行數與行號範圍算法複製)已處理:抽成 `_repo_ref_source_lines`、`_repo_ref_line_span`,`_validate_repo_ref` 的 git 樹分支和工作樹分支、`_plan_blob`、`_plan_src_path_ok` 都用同一份。F3(非 UTF-8 檔名解碼不一致)已處理:檔名解碼跟 `_nodehome_list` 同一支 `os.fsdecode`。

這輪新問題在讀 blob 這一層。列樹那層對齊了,但單支 blob 的讀取仍是自己的一套。

**① 模組邊界**
- 新程式碼都留在 `_plan_*` 函式群。
- 判路徑不再自己列樹,改呼叫 `_drift_list`/`_drift_oids`。`_drift_list` 的說明寫它是 `_nodehome_list` 的加記憶版,並已被別的模組使用(`scripts/lumos:56232`、`scripts/lumos:56255`),所以 plan 這一族取用通用的列樹快取,不算跨層直呼。
- 抽出 `_repo_ref_token_unsafe`、`_repo_ref_source_lines`、`_repo_ref_line_span` 放在 `_validate_repo_ref` 旁(`scripts/lumos:37934`、`scripts/lumos:37946`)。`_validate_repo_ref` 與 `_plan_src_path_ok` 共用同一個入口邏輯,方向對。
- `_plan_first_days` 加 scope,兩個範圍在同一次 `git log` 裡算,沒有第二個版本問法。`_plan_head` 仍是唯一的問 HEAD 入口。

引句:「_plan_cache_put(_PLAN_TREE_CACHE, _PLAN_TREE_CACHE_MAX, key, frozenset(p for p in lst[1] if p not in lst[0]))」

**② 命名與錯誤處理**
- `_plan_src_miss_reason` 回 `(路徑, 原因)`,命名沿用 `_plan_*`。擋下訊息的格式跟前面一致。
- `_plan_tree` 失敗時往 stderr 印一行,並把失敗也記進快取。`_drift_list` 自己不記失敗,這是 plan 這一層補的,且說明寫了理由。
- `_plan_cache_put` 的「滿了丟最早」跟 `_drift_list` 的「滿了整個清掉」不同,但 plan 一族內部一致,說明也寫了「同 `_DRIFT_LS_CACHE_MAX`」,只算風格差異。
- `_plan_head` 仍自己跑 `rev-parse`。專案已有 `_lens_full_sha`(`scripts/lumos:66796`)。這段程式不是這輪新增的,上一輪也沒列,不重複計。
- 符號連結的目標改用「提交:路徑」讀,見 F2。

引句:「target = _plan_blob(head[0], f"{head[1]}:{cur}", "link") if hops <= _PLAN_LINK_HOPS else None」

**③ 第二種做法**
- **樹清單快取:** 已共用 `_DRIFT_LS_CACHE`,上一輪 F1 修好。plan 這層只多存一份非一般檔路徑集合與失敗記錄,是衍生資料,不是第二套列樹。
- **符號連結解析:** 專案原本沒有,`_plan_tree_resolve` 不算重複寫法。
- **`_plan_sources_uncomment`:** 圍欄判定仍共用 `_visible_lines`(`scripts/lumos:5360`)。註解判讀沒有共用 `_XML_COMMENT_RE`(`scripts/lumos:38706`),函式說明寫了理由,維持上一輪的接受結論。
- **`_plan_head`:** 沒有另起一套。
- **單支 blob 的讀取:新增了一套。** 見 F1。

引句:「_PLAN_BLOB_CACHE = {}   # (repo 根, 物件或「提交:路徑」, "link" 或 "lines") → 符號連結目標或行數:同一支只讀一次」

F1
severity: major
blocking: 是
`_plan_blob` 自己開 `git cat-file blob`,是專案裡讀單支 blob 的另一條路,而且沒有大小上限。
- 專案已有讀「物件編號或 版本:路徑」規格的批次讀取:`_nodehome_cat_blobs`(`scripts/lumos:46110`),以及加了大小上限的 `_nodehome_cat_blobs_capped`(`scripts/lumos:46077`)。後者的說明直接寫「上限放在批次讀取這一層,不另起查法」(`scripts/lumos:46079`)。`_drift_specs`(`scripts/lumos:56276`)組規格的方式就是「編號或 版本:路徑」,跟 `_plan_blob` 的 spec 一模一樣。
- `_plan_blob` 沒有這些:不限大小全讀進記憶體,逾時另走 `_disp_git_timeout`,路徑含換行的處理也跟批次讀取不同。〈依據來源〉的 `:行號` 可以指向任何大檔。
- 修法很小:`_plan_blob` 保留 (repo, spec, kind) 的快取殼,內部改叫 `_nodehome_cat_blobs_capped(root, [spec], 上限)[0]`,讀不到或超過上限回 None。
- ⚠ 上一輪席位看過 `_plan_blob` 沒列;這輪規格從物件編號擴充到「提交:路徑」之後,跟 `_drift_specs` 的重疊才明顯。判準是要不要為一支快取殼多開一條讀取路,交編排者裁。
引句:「r = subprocess.run(["git", "-C", root, "cat-file", "blob", spec], capture_output=True, timeout=_disp_git_timeout())」

F2
severity: minor
blocking: 否
符號連結的目標用「提交:路徑」讀,是既有程式明寫過不用的方式。
- `_drift_cat` 的說明(`scripts/lumos:56268`)寫:樹清單把路徑轉成 NFC,git 裡存的可能是 NFD 或混用,用「版本:路徑」讀會讀不到,所以改用列檔時記下的內容編號。
- 這輪的 `_plan_tree_resolve` 靠 `non-regular` 路徑集合,再用「提交:路徑」去讀連結。程式碼說明坦承 NFD 檔名的連結會讀不到、只會多擋。
- 原因是 `_nodehome_list` 只替一般檔記編號,符號連結沒有。`_nodehome_list` 還有 `modes` 參數(`scripts/lumos:45642`)可以拿到非一般檔的模式,但 `_drift_list` 沒透出,所以 plan 這邊自己用「全部路徑減一般檔」重算一份。
- 結構上沒有岔出第二套列樹,只是退回一個既有說明已點名的弱點。⚠ 要不要補一個欄位讓編號也記連結,交編排者裁。
引句:「target = _plan_blob(head[0], f"{head[1]}:{cur}", "link") if hops <= _PLAN_LINK_HOPS else None」

另外一個不計入條數的提醒:`docs/lumos-toolchain-knowledge/Systems/規格閘.md` 裡「〈依據來源〉出處判路徑改成每個 HEAD 一份樹清單(`_plan_tree`:一次 `git ls-tree`…)」那條 WHY,以及「行中的要後面同一段真有 `-->` 才算」的說法,在這輪之後已過時。patch 只改了前一條首次加入日的 WHY。這屬於筆記與程式不一致,不屬於架構對齊。

不對齊共 2 條,其中會擋的 1 條
