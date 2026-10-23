severity: major

審查範圍:diff 全文逐 hunk 讀完,在提交 f96ffe70 上真跑測試,並用 Python 內建 sqlite3 對 SQL 範本做邊界實驗。trace_processor 這台機器沒有,所以沒直接在 Perfetto 上跑。

## 1. 授權檔頭守衛測試被這次改動弄紅(合約衝突)
severity: major
blocking: 是
引句:「-- SPDX-License-Identifier: MIT」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-ui-kind/scripts/test_lumos.py:53797`
失敗場景:
- 新範本登記進 `_VENDORED_TREE_FILES` 後,`t_license_headers_travel_with_vendored_files` 會拿 `^#\s*SPDX-License-Identifier:\s*MIT\s*$` 掃每一支會被複製的檔。
- `.sql` 的註解只能寫 `--`,SQLite 的 `#` 不是註解,所以掃不到。
- 實跑 `python3.14 scripts/test_lumos.py -k vendored`:`✗ 授權/KEY2: 每支會被複製進消費專案的檔都帶 SPDX 標示 ['scripts/templates/android-ui-attribution.sql']`,`88 passed, 1 failed`。
- 這支測試綁在「授權與歸屬」的 ★INVARIANT★ 上(被複製的檔至少要有 SPDX 註解行)。紅燈會擋推送閘與 CI。
- diff 只跑了 `-k android_ui_attribution` 就說驗收通過,沒跑到這支。
- 最小重現指令:`python3.14 scripts/test_lumos.py -k vendored`。
- 修法要擇一:守衛的 regex 認 `--` 註解,或範本改別的帶檔頭方式。兩條路都得改測試或範本,不能忽略這個紅燈。

## 2. 名稱為 NULL 的子區段整棵被丟掉,四類加總不等於幀長
severity: minor
blocking: 否
引句:「JOIN names n ON n.name = s.name」
file: `scripts/templates/android-ui-attribution.sql:56`(新檔的 `tree` 遞迴步)
失敗場景:
- 輸入:doFrame 10ms,底下一個 `name IS NULL` 的 6ms 區段,它下面有 `measure` 3ms。
- `n.name = s.name` 遇到 NULL 恆為假,這個子區段和它整棵子樹都不進 `tree`。
- 我跑的輸出是 `frame_dur=10`、`other_ns=4`,其餘三類全 0,加總 4 而不是 10。這違反計劃 S5 寫的「四類加總等於幀長」。
- 真實 Perfetto 裡,透過 track_event 寫入且沒給名稱的區段可能是 NULL。skill 建議開 `tracing-perfetto`,所以不算純理論,但我沒有真實 trace 可證明主執行緒上會出現。
- 我沒有補測試,證據只有上面這次實驗輸出。
- 改成 `n.name IS s.name`,或對 `s.name` 用 `COALESCE`,就能讓 NULL 名稱照「分不出類、跟祖先」處理。

## 3. 測試沒釘住最常見的畫面管線區段名「draw」本身
severity: minor
blocking: 否
引句:「OR name GLOB 'draw*' THEN 'pipeline'」
file: `scripts/test_lumos.py`(`t_android_ui_attribution_pipeline` 的 `names`)
失敗場景:
- 測試只用 `draw-VRI[MainActivity]@1`。
- 把 `GLOB 'draw*'` 改成 `GLOB 'draw-*'`,我實測輸入一個純 `draw` 6ms,原版 `pipeline_ns=6`,改壞版變 `other_ns=10`。
- 這個改壞版仍會讓整套測試照綠,因為測試名單裡的 `draw-VRI...` 同時符合兩種寫法。
- 計劃表格和 skill 都把「draw」列為管線,測試卻沒覆蓋它。
- 只算覆蓋不完整,所以標 minor。

## 其餘逐項核對,結論為對或不影響
- **GLOB 大小寫與開頭比對**:`Compose:`、`compose:`、`Recomposer:`、`RV ` 都是區分大小寫的開頭比對。`RVX` 不算,測試有覆蓋。
- **自身時間**:`dur` 減直接子區段 `dur` 總和,實驗與測試都對。
- **沒收尾的區段**:
  - `main` 用 `s.dur >= 0` 擋掉 -1。
  - 已收尾的父區段底下放一個 -1 的子區段,子區段不進 `kids`,時間留給父區段,不會崩。
  - 沒收尾的幀不輸出。
- **函式區段形狀判斷**:`is_fn` 要求「只有一個空白」加上 `(*.kt:數字*)`,鎖競爭長句不會誤算。
- **`top_compose_fn`**:同名加總後排序,同分用名稱字串排序,結果穩定(實驗中 `a.F` 勝出)。
- **效能**:
  - 造 3000 幀、每幀 42 個區段,0.36 秒。
  - 5000 層深的鏈,0.02 秒。
  - 這兩個實驗都在 `parent_id` 有索引的情況下跑,沒有索引的版本沒量。
- **重跑腳本相容性**:
  - 範本檔裡除了結尾,沒有任何一個 ASCII `;` 緊接行尾,所以 `rerun.sh` 的正則 `(.*?;)\s*$` 會停在結尾。
  - 檔頭註解裡的 `-- [Qn]` 不會被 `^--\s*\[(Q\d+)\]` 誤判成標頭。
  - 第一欄是 `'f'||ts` 字串鍵,符合 reference.md。

## manifest 逐條判定
5 條都是 `pitfalls-builtin` 的 N+1 提問,命中範本第 30、46、51、63、72 行,全部誤報:
- 這些是同一個 `WITH RECURSIVE` 查詢裡的子查詢與 CTE,不是迴圈裡反覆呼叫的獨立查詢。
- 呼叫端只對 trace_processor 跑一次。
- `stack_questions_applicable` 裡的「索引支撐 / SARGable」題,在 trace_processor 上由它自己的表處理,範本沒有可調的索引,也標誤報。

## 圖譜鏡頭(固定席)
- `lumos-cli-read`、`測試假綠形態`、`design-loop`、`guard-kill`、`lumos-cli-lifecycle`、`bound-tests-gate`、`pitfalls-code-loop`:不影響。
  - 這次只在 `_VENDORED_TREE_FILES` 加一行,並新增測試和範本。
  - 沒改 search 的預設、guard kill 的 rc 順序、re-inject、閘的判定。
  - 新測試也有「前置:範本檔在」的前置斷言,沒違反還原翻紅釘的要求。
- `授權與歸屬`(★INVARIANT★ 每支被複製的檔要有 SPDX 註解行):這份 diff 會破壞它宣稱的行為,見 finding 1。

## 角色卡
- `be-api-compat`、`be-authz`:沒有端點,也沒有對外 API 欄位改動,不適用。

## 表態記錄
- 表態檔寫的 `py-*` 題對這次改動(SQL 範本加 sqlite3 測試)不相干。
- `py-external satisfied` 指向的 `scripts/scenario_probe.py:1077` 不在這份 diff 裡,我沒有驗證。

## 清理
我在 `/var/folders/.../T/` 留下的兩個 `gctl-run-*` 暫存現場和 `/tmp/lumos-seat-work/code-android-ui-kind/正確性-sonnet/` 實驗目錄,已用字面絕對路徑刪除。刪之前用 `lsof +D` 確認沒有程序開著。

總結:最高嚴重度 major
