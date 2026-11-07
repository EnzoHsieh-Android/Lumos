severity: major

先核對上一輪三條。**F1(去註解第三種寫法)**已處理。`_plan_sources_uncomment` 的圍欄判定仍用 `_visible_lines` 的結果,函式說明也補了「為什麼不共用 `_XML_COMMENT_RE`」。它仍是專案裡第三種去註解的寫法,但理由寫明了,不再列。**F2(去重掃帳只看版控帳)**已處理。函式說明寫了為什麼只掃版控帳,並指出綁定測試 `t_psrc_block_event_vc_ledger`。**F3(兩層記憶)**已處理。`_plan_first_days_once` 刪了,改成 `_plan_head` 一層,`head` 一路傳下去。

這一輪新增的路徑判斷把「讀 git 樹」又做了一套,而且不再走既有入口,因此有兩條主要發現。

**① 模組邊界**
- 新程式碼都留在 `_plan_*` 函式群,沒有跨層直呼。
- 健檢、推送前、規格閘都只叫 `_plan_head`、`_plan_sources_problems`、`_plan_sources_is_new`,這一層沒問題。
- 問題在 `_plan_src_path_ok` 不再叫 `_validate_repo_ref`。`_validate_repo_ref` 是「驗 repo 內檔案指涉」的單一入口,三態語意還有表態閘 A3 的對齊紀錄,見 `scripts/lumos:37918`、`scripts/lumos:37937`。這裡只借走消毒那一小段 `_repo_ref_token_unsafe`,存在判斷和行號範圍判斷都自己重寫了。
- 抽出 `_repo_ref_token_unsafe` 本身方向對,`_validate_repo_ref` 和新函式都改用它。

引句:「if _repo_ref_token_unsafe(path) or path.endswith("/") or path != _pp.normpath(path):」

**② 命名與錯誤處理**
- `_plan_cache_put` 的「滿了丟最早」和 `_KT_BUILD_VERDICT_CACHE` 同形(`scripts/lumos:38700`),命名沿用 `_plan_*`,逾時往 stderr 印一行也一致。
- `_plan_tree` 用 `name.decode("utf-8", "replace")` 再轉 NFC。既有的 `_nodehome_list` 用 `os.fsdecode`(`scripts/lumos:45645`),兩處對非 UTF-8 檔名的處理不同(見 F3)。
- `_plan_blob` 讀失敗回 None 但不寫快取,逾時可以重試,沒問題。
- 新的 `_plan_head` 把 `rev-parse` 自己跑一次。專案已有 `_lens_full_sha`(`scripts/lumos:66770`)問 HEAD,`--is-shallow-repository` 也有好幾處(`scripts/lumos:50280`、`scripts/lumos:52579`)。這支改寫前就是直接 `subprocess`,所以只算輕微。

引句:「def _plan_head(rr):」

**③ 第二種做法**
- **樹清單快取:新增了一套。** 專案已有三處列 HEAD 整棵樹,`_nodehome_list` 加 `_drift_list` 的 (repo, sha) 快取(`scripts/lumos:45616`、`scripts/lumos:56208`)、`_kill_tree`(`scripts/lumos:25995`)、`_SecevTree`(`scripts/lumos:9850`)。`_plan_tree` 是第四個。見 F1。
- **符號連結解析:專案裡原本沒有。** 既有程式碼遇到 120000 都是拒絕或標記,見 `scripts/lumos:9972`、`scripts/lumos:26200`。所以 `_plan_tree_resolve` 不算重複寫法,但它建立在 F1 那份自己的清單上。
- **`_plan_sources_uncomment`:** 圍欄判定共用 `_visible_lines`(`scripts/lumos:5360`),行內程式碼的正則是計劃自己的 `_PLAN_SRC_CODE_SPAN_RE`,上一輪已接受。
- **`_plan_head`:** 只管出快取鍵,沒有另起一套版本快取。

F1
severity: major
blocking: 是
`_plan_tree` 另寫了一套「列 HEAD 整棵樹並快取」,和既有的 `_nodehome_list` 加 `_drift_list` 是同一件事。
- 兩者都是 `ls-tree -r -z --full-tree`,都以 (repo, sha) 為鍵快取。`_nodehome_list` 還會順便回每支檔的物件編號和非一般檔的模式(`scripts/lumos:45616`),快取版是 `scripts/lumos:56208`。
- 它的快取上限寫法和說明在 `scripts/lumos:56198` 到 `scripts/lumos:56216`,新的 `_PLAN_TREE_CACHE` 沒有說明為什麼不共用。
- 缺口只有一個:`_nodehome_list` 不回符號連結的物件編號,而 `_plan_tree_resolve` 要用它去讀連結目標。補法是讓它多填一個符號連結物件欄位,或另填一份,不必再寫一套 ls-tree 解碼。
- ⚠ 判不準的地方:這輪席位認為「沒有共用」比「共用要動既有函式簽章」更偏離專案做法,但改簽章的代價要由編排者衡量。我把它標成會擋,理由是專案已有三份 ls-tree 解碼,這是第四份。
引句:「r = subprocess.run(["git", "-C", root, "ls-tree", "-r", "-z", "--full-tree", sha], capture_output=True,」

F2
severity: major
blocking: 是
行號範圍的判斷和「讀一支 blob 數行數」在 `_plan_blob` 與 `_plan_src_path_ok` 裡重寫了一遍,既有的 `_git_tree_text` 加 `_validate_repo_ref` 的 `source_lines` 就是同一個功能。
- `_validate_repo_ref` 的行數算法在 `scripts/lumos:37923` 到 `scripts/lumos:37931`,範圍判斷在 `scripts/lumos:37947` 到 `scripts/lumos:37950`。讀檔用 `_git_tree_text`(`scripts/lumos:71585`)。
- 新的 `_plan_blob` 在注解裡寫「換行算法同 _validate_repo_ref」,代表作者知道是同一個算法,卻複製了一份。注解寫的是「現在一致」,不是「共用」,日後兩邊一改就分岔,而且沒有測試會同時守兩邊。
- 同樣地,`1 <= lo <= hi <= n` 對應 `scripts/lumos:37949` 的 `lo < 1 or hi < lo or lo > len(...)`,是第二份範圍判斷。
- 修法方向:`_plan_src_path_ok` 在樹清單解析出路徑之後,行號範圍交給 `_validate_repo_ref(... at_sha=head 的提交)`,或把 `source_lines` 抽成模組層函式兩邊共用。
引句:「t = r.stdout.decode("utf-8", "ignore").replace("\r\n", "\n").replace("\r", "\n")」

F3
severity: minor
blocking: 否
非 UTF-8 檔名在新舊兩套樹清單裡的解碼不同:`_plan_tree` 用 `decode("utf-8", "replace")` 再轉 NFC,既有的 `_nodehome_list` 用 `os.fsdecode`(`scripts/lumos:45645`)。同一個壞檔名在兩套裡得到的路徑字串不一樣。F1 若改成共用就自動消掉。
引句:「tree[nfc(name.decode("utf-8", "replace"))] = tuple(x.decode("ascii", "replace") for x in f)」

不對齊共 3 條,其中會擋的 2 條
