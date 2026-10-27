severity: minor

審查範圍:r4-repair.patch 的程式 hunk(`scripts/lumos`、`scripts/hooks/claude/lumos-entry-hook.py`)逐段讀完。r4-snapshot.patch 只當上下文。本席的實驗目錄已用字面絕對路徑刪除。固定席節點沒有附,我也沒有自己補算。

1. `waive --list` 把全部紀錄一次讀進記憶體,而且沒有時間上限,修補之後不再有份數上限
severity: minor
blocking: 否
- 引句:「for fp, path in _e2e_record_files(root, cap=None)[0]:   # waive --list 用:讀全部」
- file: `scripts/lumos:41874` 附近的 `_e2e_records_all`,以及呼叫它的 `_e2e_waive_list`(`scripts/lumos:41896`)。
- 失敗場景:`_e2e_records_all` 把每份解析完的紀錄都放進 `out` 清單,`_e2e_waive_list` 等全部讀完才開始印。記憶體跟著份數線性長,沒有任何上限。
- 量測:我用 Python 3.14 造了單份 1.9MB 的紀錄,直接呼叫 `_e2e_waive_list`。

| 份數 | 耗時 | 最大記憶體 |
|---|---|---|
| 100 | 11.7 秒 | 1.2GB |
| 250 | 29.9 秒 | 3.0GB |

  - 每份約 0.12 秒、12MB,線性成長。外推 3000 份要約 6 分鐘、約 36GB,5000 份要約 60GB,機器會先換頁或被殺掉。
  - 修補前上限是 500 份,約 6GB。
- 重現:`_e2e_records_all` 的 `out.append((fp, ...))` 改成邊讀邊印、不保留,同一批輸入的記憶體就是常數。
- 歸因:有證據的修復回歸。「保留整份清單」本來就有,但本輪拿掉份數上限才讓它沒有上限。修前版 `bf9dac49` 最多 500 份,修後版 `de8a99bc` 不限。

2. `_e2e_scope_hit` 與 `_e2e_shared_paths_err` 的 CPU 工作沒有時間檢查
severity: minor
blocking: 否
- 引句:「out = [x for x in sp if not any(_e2e_under(_e2e_norm(x), a) for a in apps)]」
- file: `scripts/lumos:40510` 附近的 `_e2e_shared_paths_err`。
- 失敗場景:
  - `shared_paths` 乘上 `app_dirs` 是二次方。`app_dirs` 一般只有幾個模組,所以只有設定異常大時才會出現。
  - 同一類問題還有 `_e2e_scope_hit` 裡 `next(d for d in apps if ...)` 對 ls-tree 每個檔逐個比。60 秒預算只在 git 呼叫處檢查,純 CPU 迴圈不檢查,所以慢的時候不會被預算擋下。
- 量測:本席沒有針對這條造大輸入實驗,所以不升級。
- 歸因:`shared_paths` 那段是未判定(新增的檢查,但我沒量過)。`_e2e_scope_hit` 那段是有證據的原有漏查,因為逐檔比對在修補前就存在。

3. 主線設定不同時多算兩次指紋,吃同一個 60 秒預算
severity: minor
blocking: 否
- 引句:「mh, e2e2 = (None, None) if e1 else _e2e_fingerprint(root, sha, ml[1], ml[0], allow_missing=True, deadline=deadline)」(實際原文是 `mh, e2 = (None, None) if e1 else ...`,引句以 patch 為準。)
- file: `scripts/lumos`,`_e2e_gate_fps` 內,`fp == fp_base and same_cfg and pushed[1] and isinstance(ml[1], dict)` 那個分支。
- 失敗場景:只改文件、且主線在分岔後改過 e2e 設定的分支,本來兩次 ls-tree 就能放行,現在要四次,共用同一個 `deadline`。大 repo 或慢機器上,原本放行的推送會變成逾時擋下。
- 量測:本席沒有量一次 ls-tree 的耗時,所以不升級。
- 歸因:有證據的修復回歸。這個分支是本輪新加的,但實際耗時未量。

三問:
1. 哪個子程序在逾時、Ctrl-C、例外時沒被收掉?
   - 本輪修補沒有新增子程序。
   - `_e2e_gate_uses` 多了一次 `rev-parse`,走 `_nodehome_git`,帶 `timeout=_secev_git_left(deadline)`。
   - `_nodehome_git` 逾時時會不會殺子程序,我沒有讀它的實作,不下結論。
2. 哪個時間預算會在大輸入或慢機器上擋下或放行正常操作?
   - `--list` 沒有時間上限,量測見第 1 條。
   - `--ack` 的 60 秒:我讓 `_e2e_ai_pending_all` 帶 `cap=None` 讀 100 份 700KB 紀錄,預算 0.4 秒內第一輪就全部標完(目標 100 份、沒讀到 0 份)。每份讀取約 20 毫秒,60 秒大約能讀 3000 份 2MB 紀錄。
   - 我只在紙上推到一個可能的卡住情形:標過的檔 mtime 變新、重跑時排最前面,又吃掉預算。這條我沒有重現,也沒有證據,所以不列為 finding。
   - 另一個小問題:超過 2MB 的紀錄現在算進「沒讀到」,但訊息寫成「讀超過 60 秒…再跑一次」。這種情況重跑永遠一樣,這句話是誤導。
   - 主線設定不同時多算的兩次指紋,見第 3 條。
   - 開場掛鉤的 `min(_E2E_RECORD_SCAN_SEC, _inner_budget())` 方向正確,`_inner_budget` 有下限 1 秒,不會出現負值。
3. 哪段把大檔一次讀進記憶體,或做二次方工作?
   - `_e2e_records_all` 保留全部解析結果(第 1 條)。
   - `_e2e_record_update` 先 `stat` 大小再讀,這條修補有效。
   - `_e2e_prefixes` 只切前 `maxd` 段,避免二次方,方向正確。
   - 前綴字串用 `pre + "/" + seg` 累加,對只有設定路徑極深的情況每檔約 `maxd` 平方的複製量。我只估算,沒有量測,不列 finding。
   - `_e2e_record_err` 新加的型別檢查對 items 是線性,沒有二次方。
   - `_e2e_gate_out` 的 `clean` 對清單是線性,沒有二次方。

總結:最高等級 minor,擋實作的 0 條。
