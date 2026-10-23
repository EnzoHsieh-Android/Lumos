severity: major

## 1. SQL 範本的授權標頭用 `--` 開頭,授權守衛測試看不懂,直接紅
severity: major
blocking: 是
引句:「-- SPDX-License-Identifier: MIT」
file: `scripts/test_lumos.py:53797`(`_spdx` 只認 `^#\s*SPDX-License-Identifier`)
file: `scripts/lumos:31931`(新範本進了 `_VENDORED_ALL`,所以被授權守衛掃到)

這份 diff 把 `.sql` 登記進複製清單,但 SQL 的註解符號是 `--`,不是 `#`。授權守衛 `t_license_headers_travel_with_vendored_files` 對清單內每支檔都用 `#` 開頭的正則找 SPDX,所以掃不到。

重現(在 android-ui-kind 工作樹執行):
- `python3.14 scripts/test_lumos.py -k license_headers`
- 輸出:`✗ 授權/KEY2: 每支會被複製進消費專案的檔都帶 SPDX 標示  ['scripts/templates/android-ui-attribution.sql']`,最後 `6 passed, 1 failed`。

這條守衛綁在 `授權與歸屬.md` 的 ★INVARIANT★ 上,也在全套測試裡,推送前的閘會擋下。這份 diff 的新測試(`-k android_ui_attribution`,39 通過)沒覆蓋到它,所以作者的子集驗證看不出來。

修法有兩種。一是讓 `_spdx` 與 `_who` 同時接受 `--`(例如 `^(#|--)\s*...`)。二是把標頭改成守衛認得的形式。選一的話,要確認 `--` 版本仍能被改壞後翻紅,守衛才沒被放寬成假綠。

## 2. 區段名稱為 NULL 時,那段時間和它底下的子樹整段消失
severity: minor
blocking: 否
引句:「JOIN names n ON n.name = s.name」
file: `scripts/templates/android-ui-attribution.sql:62`(`tree` 遞迴項)

我用 sqlite3 造假表:100ms 的幀,底下有一個 NULL 名稱的 50ms 子區段,它底下又有 30ms 的 `Compose:recompose`。

結果是 `compose_ns=0, other_ns=50`,四類加總 50,小於幀長 100。

原因是 `n.name = s.name` 遇到 NULL 恆假,這個區段和它的後代都不進 `tree`。`kids` 卻照樣把它的時長從父區段扣掉,所以那 50ms 沒有任何一類收到。這違反「四類加總等於幀長」(S5)。

空字串名稱沒問題(同樣的測試,compose=30, other=70)。Perfetto 真實 Trace 的 NULL 名稱很罕見,所以我標 minor。
⚠ 沒有真實 Trace 佐證。

## 3. `draw*` 太寬,App 自訂的 draw 開頭區段會被當成畫面管線
severity: minor
blocking: 否
引句:「OR name GLOB 'draw*' THEN 'pipeline'」
file: `scripts/templates/android-ui-attribution.sql:50`

在 `Compose:recompose`(60ms)底下放 App 自己打的 `drawChart`(50ms)。結果是 `compose=10, pipeline=50, other=40`,這 50ms 本該跟著 Compose 祖先。

S2 規定名稱分不出類的區段要跟祖先。這裡 `draw*` 的前綴比對把 App 自訂區段(`drawBitmap`、`draw_chart` 之類)全吸進管線。測試只用了 `draw-VRI[MainActivity]@1` 一個正例,沒有反例。

使用者拿來判斷「該往 Compose 分支還是 L2」的,正是 App 自己的重繪區段,所以會被誤導。可以改成只認 `draw-VRI*` 之類的系統形狀。

## 4. 子區段總長大於父區段時,輸出負數
severity: minor
blocking: 否
引句:「m.dur - COALESCE(k.kid_ns, 0) AS self_ns」
file: `scripts/templates/android-ui-attribution.sql:70`

幀 100ms,底下 `Compose:recompose` 150ms。輸出 `compose_ns=150, other_ns=-50`。

`self_ns` 沒有下限,資料錯或時間重疊時,各類會出現負值。skill 拿「哪一類長最多」做分流,負值會讓比較失真。這不是正常 Trace 會有的輸入,所以只列 minor,可以在查詢或 skill 裡寫明。
⚠ 需要有壞資料才會觸發。

## 5. 經查證後不構成問題的邊界
這些我都跑過,結果正常,不列為 finding。

- 沒有任何 doFrame:回傳零列。空結果由既有的 `rerun.sh` 在執行時拒收。
- 行程在 Trace 中途重啟換 pid:兩個同名行程都被收進來,各自的幀正常輸出。
- 沒收尾的幀(dur=-1):被 `main` 的 `dur >= 0` 濾掉。
- 名稱剛好是 `Compose:` 或 `RV `:分別算 Compose 和 XML,符合設計。
- 函式區段帶多個括號,或函式名含空白:因為「整個名稱只有一個空白」,不算 Compose,所以不會誤算。這是設計取捨。
- 同一幀很多同名函式區段:`fn` 用 GROUP BY 加總,結果正確。
- `__PROCESS__` 換成含單引號的名稱:語法錯誤。Android 套件名不含單引號,不構成風險。
- 同一個主執行緒有多條 `thread_track`:SQL 用 `IN` 收,沒問題。
- 測試輔助函式 `_ui_attr`:幀間隔 100ms、不交錯,符合 Perfetto 巢狀的前提;負的 `dur` 只用在 -1 的未收尾幀,有測到。

## manifest 判定(pitfalls-builtin,共 5 條)
5 條全是同一個型樣:`android-ui-attribution.sql` 第 30、46、51、63、72 行的 SELECT,被問「是否在迴圈內、造成 N+1」。

判定:全部誤報。這些 SELECT 是同一支查詢裡 CTE 的子查詢,整份腳本只執行一次。遞迴 CTE 是在資料庫引擎內展開,沒有 App 端的迴圈逐次呼叫。

## 圖譜固定席逐條判定
這份 diff 只動了 `scripts/lumos` 的 `_VENDORED_TREE_FILES` 加一行、`scripts/test_lumos.py` 加測試,其餘是範本、skill 和筆記。

- `授權與歸屬.md`(★INVARIANT★):**受影響**,見第 1 條。「其餘每一支被複製的檔至少要有 SPDX 註解行」這條合約被新範本打破(在守衛眼中)。該節點另一條「授權檔不得進 `_VENDORED_TOOLKIT`」沒有影響,新檔進的是 `_VENDORED_TREE_FILES`。
- `lumos-cli-read.md`(search 排除 superseded):不影響,diff 沒碰 search 路徑。
- `測試假綠形態.md`(還原翻紅釘要配前置斷言):不影響。新測試有「前置:範本檔在 scripts/templates/」斷言,符合要求。
- `design-loop.md`(處置閘第五步):不影響,diff 沒碰處置閘。
- `bound-tests-gate.md`:不影響。新增的 `t_android_ui_attribution_*` 在子集下全綠(39 通過)。
- `guard-kill.md`:不影響。
- `lumos-cli-lifecycle.md`(re-inject 保留 sentinel 外內容):不影響。diff 沒碰 re-inject。
- `pitfalls-code-loop.md`(★RISK★):不影響,只是這次 diff 觸發了其中的 SQL 型樣。

## 表態記錄
py-eventloop、py-parallel、py-memory、py-hotpath 的 na 與這份 diff 一致:新增的是同步的 SQL 範本和測試,沒有 async 或熱迴圈。py-external 指向 `scripts/scenario_probe.py:1077`,不在這份 diff 範圍內,我沒有查驗。

## 暫存清理
我在 `/tmp/lumos-seat-work/code-android-ui-kind/邊界-sonnet/` 的實驗目錄已刪除。授權守衛測試紅時留下的現場 `/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/gctl-run-me7uajfc` 也已刪除,並確認不在了。

總結:最高嚴重度 major
