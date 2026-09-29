severity: major

## F1 disk 模式(`lumos drift scan` 預設走的路)的 symbol/test 讀檔完全不看預算,`--budget` 對它沒有作用

severity: major
blocking: 是 — `cmd_drift_scan` 的 docstring 承諾「總預算預設 60 秒…用完的條件列成判不了」,但實測預設(無 `--at`)呼叫時,預算用完後仍會繼續做工作目錄的批次讀檔並回傳確定結果,不會降級成「判不了」,違反這個對外承諾的行為。

引句:「self._text[p] = (Path(self.root) / p).read_bytes().decode("utf-8", errors="replace")」

1. `scripts/lumos:25901-25921` 的 `_DriftProbeTree._read`:`self.where == "disk"` 那個分支(`scripts/lumos:25906-25912`)逐檔讀取,讀完才 `return True`,**中間完全沒有檢查 `self.deadline`**;只有非 disk 分支(`scripts/lumos:25913-25914`)才有 `if self.deadline is not None and self._t.monotonic() >= self.deadline: return False`。
2. `cmd_drift_scan` 不帶 `--at` 時走的就是這條路(`sha or "disk"`,`scripts/lumos:26397` 起),而這正是「怎麼用」段落寫的預設呼叫方式(`lumos drift scan`,沒有 `--at`)。
3. 實測(在自己 mktemp 的臨時 repo,`git -C` 操作,腳本見下):建 3000 支追蹤中的 `.py` 檔、一篇筆記帶一行 `REVISIT:[when-symbol:nonexistent_sym][by:2099-12-31] 補測試`(不帶路徑的 symbol 條件,考卷 A7/B4 本身就是這種寫法),直接呼叫真正的 `cmd_drift_scan(env, budget=0.15)`(等同 `lumos drift scan --budget 0.15`):
   ```
   --budget 0.15s given; actual elapsed: 0.169s; rc=0   (overshoot 1.1x)
   --budget 0.15s given; actual elapsed: 0.202s; rc=0   (overshoot 1.3x)
   --budget 0.15s given; actual elapsed: 0.166s; rc=0   (overshoot 1.1x)
   ```
   三次重跑輸出的 `"unknown": []`、`"problems": []`——不是「超過預算,判不了」,是靜默超時後給出確定答案(該條件真的判成不成立)。更極端的情況(`scripts/lumos` 之外還有更多檔案、或磁碟較慢)超時倍數只會更大,因為 `_read` 的 disk 分支沒有任何時間上限,會把整個語料(`corpus()` 篩出的全部程式檔與測試檔)逐檔讀完才停。
4. 對照:同樣的函式,git 模式(帶 `--at` 或 check 用的 tip/base 樹)有檢查(`scripts/lumos:25913-25914`),批次讀取(`_nodehome_cat_blobs`)也有 `timeout=` 落地;只有 disk 分支漏掉,不是設計上「跑到一半不中斷、最多多花一次呼叫時間」的既有取捨(那個取捨在 `_drift_check_core` 的文件裡講的是 git 呼叫,disk 分支甚至不是 git 呼叫,沒有 20 秒或 timeout 的天花板保護,純粹是 Python 檔案 I/O,理論上可以無上限地跑下去)。
5. 重現腳本(已跑過,可重跑;只碰自己 mktemp 出來的臨時目錄):`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/cy2/repro4.py`(N=3000、BUDGET=0.15);更直接的單元級重現在同目錄 `repro2.py`(deadline 設成已經過去的時間點,`_drift_probe_tree(root, "disk", deadline)` 照樣建出樹、`_drift_probe_one` 讀完 3000 支檔案回傳確定的 `False`,而不是 `None`)。

## F2 帶路徑的 symbol/test 條件每支檔各開一次 `git cat-file --batch`,不是這支檔在同一次讀的一部分——這正是這份程式自己警告過的反模式

severity: major
blocking: 是 — 這份程式的 `_nodehome_cat_blobs` docstring 自己寫明「成本在開 git 行程本身」並舉了「200 支衝突檔、每支三次讀取就是 600 個行程,實測 13.5 秒;用批次讀取一個行程讀完」當理由;`_DriftProbeTree.one()` 對「帶路徑」的條件卻逐一開行程,量出的行程數與耗時隨圖譜裡出現的相異檔案數線性成長,會拖慢每一次 `drift check`(推送閘,擋人)與 `drift scan`。

引句:「if not self._read([path]):」

1. `scripts/lumos:25946-25963` 的 `_DriftProbeTree.one()`:條件帶路徑時走 `if path: … if not self._read([path]): return None`(`scripts/lumos:25953-25958`),每一個不同的 `path` 各自呼叫一次 `self._read([path])`;而 `_read` 對非 disk 情況會呼叫 `_nodehome_cat_blobs(self.root, [...], timeout=left)`(`scripts/lumos:25916`)——一個 path 一個行程。
2. 對照類別自己的文件字串(`scripts/lumos:25892-25894`)講的是「帶路徑的條件只讀那一支檔(併發席:原本一律整批讀全庫)」,這句話只保證「不讀全庫」,沒有保證「多支不同路徑合併成一次讀」;結果是從「整批讀全庫、太多」的舊問題,換成「一支檔一次行程、太多次」的新問題。
3. 實測(自己 mktemp 的臨時 repo,計數 `_nodehome_cat_blobs` 被呼叫的次數):建 60 支不同檔案(`src/f0.py`…`src/f59.py`),一篇筆記寫 60 行 `REVISIT:[when-symbol:src/fN.py::symN][by:2099-12-31] 補測試 N`(60 個不同路徑,各自帶路徑),直接呼叫 `_drift_probe_scan`:
   ```
   N REVISIT lines: 60
   git cat-file --batch invocations: 60
   specs-per-call: [1, 1, 1, ... ]  (60 個 1)
   elapsed seconds: 1.129
   ```
   60 個相異路徑 → 60 次各讀 1 個 spec 的行程呼叫,而不是 1 次讀 60 個 spec 的行程呼叫。跟這份程式自己引用的量測基準(600 支/13.5 秒 ≈ 22.5ms/行程)量級一致(這裡 60 支/1.13 秒 ≈ 18.8ms/行程)。
4. 這不是邊角案例:計劃文件〈做法〉第 6 點自己寫「舊的回頭條件要人補條件:rtb 約 45 條、工具鏈自己也有」,補完之後這些條件多半會各自指到不同檔案(A7、B4 兩題用的就是不帶路徑的 bare name,但 B1/B2/B3 用的是帶路徑寫法各指不同檔),`drift check` 是推送閘,每次 push 都要付這個代價。
5. 重現腳本:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/cy2/repro1.py`。

## F3 `_notelines_range_cand` 在 `keep_other=True` 時,不論這次候選裡有沒有 other 區塊的行都會多開一次全圖譜範圍的 `git diff`

severity: minor
blocking: 否 — 量到的代價很小(本 repo 全歷史範圍也只要 0.02–0.11 秒),而且這條路是第一層(筆記形狀擋)推送/CI 都會走到的必經路徑,不是候選路徑,不會被跳過,但成本本身不足以擋。

引句:「dn = _ns_diff(repo_root, base_where or _EMPTY_TREE_SHA, tip_where, "--", vault_rel)」

1. `scripts/lumos:24012-24029` 的 `_notelines_range_cand`:`if keep_other:`(`scripts/lumos:24022`起)一律呼叫 `_ns_diff(repo_root, base_where or _EMPTY_TREE_SHA, tip_where, "--", vault_rel)`(`scripts/lumos:24024`),範圍是整個 `vault_rel`(例如 `docs/kg-knowledge`),不是只在「這次候選裡真的有 other 區塊的行」時才做。
2. `keep_other=True` 只有一個呼叫端:`_note_shape_eval`(`scripts/lumos:24286-24287`),而這支是第一層筆記形狀擋的核心,推送前掛鉤與 CI 每次都會呼叫——換句話說這個額外 diff 是每次 push 都固定多付的一次 git 呼叫,不是有需要才付。
3. 實測(在本 repo,`git -C` 對本 repo 唯讀操作,沒有改動任何檔案):
   ```
   time git diff -U0 -M --no-color --no-ext-diff --no-textconv --src-prefix=a/ --dst-prefix=b/ ac5c7ccf 123aaf47 -- docs/lumos-toolchain-knowledge
   → 0.021s
   time git diff ... $FIRST_COMMIT HEAD -- docs/lumos-toolchain-knowledge   (全歷史範圍,62119 行輸出)
   → 0.110s
   ```
   目前規模下不算貴,但沒有任何「這次候選裡有沒有 other 區塊行」的前置判斷就先付這筆成本,圖譜規模再大、range 再長時會線性變貴,而且是每次 push 的固定成本,不是「用到才付」。

## 已看,無 finding

- **`_drift_probe_check` / `_drift_probe_prepare` / `_drift_probe_tree`(git 模式)的預算檢查**:逐一讀過 `scripts/lumos:26044-26126`——`_out()` 在每條候選行評估前都查(`scripts/lumos:26073`)、`_drift_probe_prepare` 在建 `benv` 前查(`scripts/lumos:26101-26102`)、`_drift_probe_tree` 進來就查(`scripts/lumos:25969-25970`)、`_DriftProbeTree._read` 的非 disk 分支在真正發 git 呼叫前查(`scripts/lumos:25913-25914`)。`_drift_tree_env`(`scripts/lumos:25570-25592`)本身沒有在函式開頭查 deadline,但目前兩個呼叫端(`_drift_check_core` 一進來就呼叫、`_drift_probe_prepare` 呼叫前有明確的 `if deadline...: return`)都是先查過才呼叫,而它內部第二個 git 呼叫(`_nodehome_cat_blobs`)用 `timeout=max(1, deadline-now)` 夾住,最壞情況跟 `_drift_check_core` 文件字串講的「最壞比預算多一次呼叫的時間」吻合(20 秒非批次呼叫 + 最多再 1 秒),沒有無上限發呼叫的情況——跟 F1(disk 分支完全沒有這層保護、也沒有天花板)不同。
- **`_DRIFT_LS_CACHE` 跨 repo / 跨呼叫拿到錯內容**:鍵是 `(str(root), 完整提交編號)`,提交的樹內容不可變,不會有「同一把鑰匙指到不同內容」的問題;不同 repo 因為 `str(root)` 不同不會撞鍵。
- **`_DRIFT_LS_CACHE` 滿了整批清掉(不是只清最舊一筆)會不會造成重複列樹**:用 `_drift_exam_history` 真實會用到的走法(依序走 14 個相鄰提交、`_drift_check_core` 逐步推進,超過上限 8)實測 `ls-tree` 的呼叫次數:
  ```
  commits walked: 14, cache cap: 8
  total ls-tree git invocations: 14
  ```
  14 支相異的樹只各列一次,沒有因為整批清除而重複列樹——因為這條路徑是嚴格線性走訪,清除發生時「這一步還會再用到」的那筆剛好是清除後立刻補回去的那筆,舊筆到那個時間點也真的不會再用到。這個記憶體設計文件字串只承諾「一次 check 裡只列一次」(`scripts/lumos:25876`),沒有承諾跨 exam 題目、跨非相鄰提交也一定命中,那種存取型態沒有實測,不在這個承諾範圍內,不算違反。重現腳本:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/cy2/repro3.py`。
- **ast 解析 `scripts/lumos`(3.6 萬行)的次數與快取**:實測 `ast.parse` 單次約 0.99 秒(`import ast; ast.parse(開啟的全文)`,跑 5 次取平均)。讀過 `_DriftProbeTree._defines`(`scripts/lumos:25933-25944`)與 `_py` 快取(`self._py[p]`,鍵是路徑):同一棵樹裡,不論有幾條條件命中同一支檔案的名稱正則預檢(`re.search`,在真正解析前先擋掉八成不相關的檔案),`_drift_py_names` 對同一支檔案只會呼叫一次,結果被快取重用;tip 樹跟 base 樹是兩個不同的 `_DriftProbeTree` 實例,各自快取,最多各解析一次。沒有找到重複解析同一支檔案的路徑。
- **不帶路徑的 symbol/test 條件讀全部程式檔(含沒副檔名的)**:`corpus()`(`scripts/lumos:25923-25931`)確實會把整個語料(`_drift_probe_code_path` 篩出、含沒副檔名但開頭 `#!` 的檔)一次讀進來,但這是「不知道在哪支檔」這個功能本身要付的代價,而且是**一次批次呼叫**(git 模式下 `_nodehome_cat_blobs` 一次搞定,不是逐檔開行程),跟 F2 的「逐檔開行程」是不同性質;同一棵樹裡 `test=True`/`test=False` 各只會觸發一次(`self._corpus` 快取,`scripts/lumos:25925`),沒看到重複讀。disk 模式下這條路一樣會被 corpus() 呼叫到,但問題本體已經在 F1 報過(disk 分支完全不看預算),不重複計。
- **讀檔失敗、git 失敗、部分批次讀失敗時算判不了還是算不成立**:追過整條鏈——`_drift_probe_tree` 整批 git 失敗回 `None`(`scripts/lumos:25971-25974`),`.one()` 對 `tree is None` 一律回 `None`(判不了,`scripts/lumos:25987`);`_read` 批次呼叫整體失敗(逾時、跑不起來)回 `False`,`corpus()`/路徑分支都回 `None`(判不了);status 條件指到讀不出來的筆記(`_note_unreadable`)明確回 `None`(`scripts/lumos:25984-25985`),不是當成不成立。唯一「per-item 是 None」的情況(`_nodehome_cat_blobs` 對單一 spec 回 `None`,代表這個版本沒有這支檔)在這裡等同「這個路徑在這個版本查無內容」,而 `.one()` 進到 `_read([path])` 前已經先確認 `path in self.files`(來自同一棵樹的 ls-tree),兩者資料來源一致,沒有找到「ls-tree 說有、cat-file 說沒有」這種可以實際做出來的落差,不標。

最嚴重 major,blocking 共 2 條(F1、F2);另有 1 條 minor(F3)不算 blocking。
