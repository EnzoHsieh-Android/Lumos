severity: minor

只有一條 minor。本輪修補的行為都站得住,我沒找到修補自己引入的回歸。

驗證範圍:
- 在 `/tmp/lumos-seat-work/code-android-ui-kind/通才-sonnet/w`(checkout 46773fe6)跑了 `-k android_ui_attribution`(47 通過、0 失敗)和 `-k license_headers`(8 通過、0 失敗)。
- 對兩個筆記節點跑 `lumos lint`,都是 0 問題。
- 以 2 條不變的 SQL 效能對照,另有 2 次授權守衛破壞實驗,見下。

## 1. 授權守衛的前置斷言把「查詢範本必須存在」寫死,與計劃的撤除條件互相咬住
severity: minor
blocking: 否
引句:「授權/KEY2 前置:複製清單裡有 .sql 範本(照類型認註解符號那條路徑真的有走到)」
file: `scripts/test_lumos.py:53876`(約在該 hunk 的 `any(f.endswith(".sql") for f in targets)` 一行);撤除條件見 `docs/lumos-toolchain-knowledge/Projects/Android介面寫法分流_計劃.md:35` 的 RETIRE-IF
歸因:有證據的修復回歸(這條斷言是本輪新增的,修前 f96ffe70 沒有)
具體失敗場景:
- 計劃的 RETIRE-IF 寫「撤掉這支查詢改指向官方」。
- 一旦照做,`.sql` 從 `_VENDORED_TREE_FILES` 移除,授權測試會紅在「複製清單裡有 .sql 範本」。
- 而此時授權守衛本身沒有任何問題,維護者得去改授權測試才能撤範本。
- 證據:這個前置只是為了證明 `.sql` 分支有走到,卻把「清單裡永遠有 .sql」寫成必要條件。
- 查證命令:`git -C /Users/enzo/orca/workspaces/lumos-toolchain/android-ui-kind show 46773fe6:scripts/test_lumos.py | grep -n "照類型認註解符號那條路徑"`,在修後有、修前(f96ffe70)沒有。
- 較便宜的寫法:前置改成對守衛自己的 helper 單測(假檔名 `x.sql` 帶 `--` 通過、帶 `#` 被判缺),不依賴真實清單內容。
- 因為撤範本那天會自己顯形(紅燈是明示的),所以只降到 minor。

## 其餘角度:都站得住

### 修復效果與相鄰路徑(三問的證據)
- **授權守衛(原問題:`.sql` 範本被判缺標示)**
  - 修後 `-k license_headers` 8 通過。
  - 破壞實驗 A:把範本第 2 行 SPDX 改成 `# SPDX…`,守衛紅,報 `['scripts/templates/android-ui-attribution.sql']`,所以 `.sql` 寫 `#` 不會被誤收。
  - 破壞實驗 B:刪掉範本的 `-- SPDX-License-Identifier` 行,守衛同樣紅。
  - 其他副檔名仍只認 `#`,沒放寬。
  - `scripts/lumos:44925` 只剝 `# SPDX-` 行,用在 note-audit 派工範本,不碰 `.sql`。
- **NULL 名稱**:`JOIN names n ON n.name IS s.name` 的測試 `(None, 6, [("measure", 3)])` 得到 `(0,0,3,7)`;換回 `=` 這個子樹會消失。
- **負自身時間**:`MAX(m.dur - COALESCE(k.kid_ns, 0), 0)` 讓「子區段比幀長」的其他類是 0,不是負的。
- **`draw*` 改成 `= 'draw'` 加 `GLOB 'draw-VRI*'`**:`drawChart` 的測試在 Compose 底下跟祖先算 Compose。
- **重跑腳本的分號截斷**:`scripts/templates/android-receipt-rerun.sh` 的正規式 `(.*?;)\s*$` 取第一個以分號結尾的行。範本全檔只有 91 行 `ORDER BY f.ts;` 一處以分號結尾。假分析工具要求同時看到 `WITH RECURSIVE` 和 `ORDER BY f.ts;`,所以任何截斷在中途的註解分號都會翻紅。
- **範本 header 的 `-- [Qn]` 字樣**:不會被收據的 `^-- \[(Q\d+)\]` 或 `^--\s*\[(Q\d+)\]` 誤抓,測試 `OK  Q1` 證實。
- **效能**:1500 幀、約 12 萬個區段、數百個不同名稱的合成資料,修前 f96ffe70 與修後 46773fe6 都是 0.46 秒、1500 列,`IS` 沒造成退步。

### 被刪掉的行為
- **`draw*` 全吸進管線**:這個行為被收窄。名為 `drawX` 的 App 自訂區段現在跟祖先。真實框架的 `draw`、`draw-VRI[...]` 都保留。我沒有找到會讓框架 `draw*` 子區段(如 `Record View#draw()`)掉出管線的具體案例,因為它們掛在 `draw` 底下仍會繼承 pipeline。
- **授權守衛**:原本全檔案都只認 `#`,現在只有 `.sql` 例外。不存在「原本判缺、現在漏過」的檔案,只有「原本誤判缺、現在放行」的 `.sql`。

### pitfalls-builtin manifest
我只確認了表態記錄裡的 py-* 題:
- `py-eventloop`、`py-parallel`、`py-memory`、`py-hotpath` 標 na,與本 diff 相符,這次的程式是同步的命令列腳本和 sqlite 查詢。
- `py-external satisfied` 指向 `scripts/scenario_probe.py:1077`,不在本 diff,範圍外。
- manifest 內容我沒逐條展開。

### 固定席筆記(逐條會不會被破壞)
- **授權與歸屬**
  - 「其餘每一支被複製的檔至少要有 SPDX 註解行」這條 ★INVARIANT★ 仍成立,「註解行」只是改成依副檔名認符號;破壞實驗 A、B 證明守衛仍會翻紅。
  - 「LICENSE 不得進 `_VENDORED_TOOLKIT`」這條沒動。
  - 另外 `Systems/授權與歸屬.md` 的決定段仍寫「兩行 SPDX 加一行指路」,但 `.sql` 範本沒有指路行(原本就如此,非本輪引入,不報)。
- **lumos-cli-read、測試假綠形態、design-loop、bound-tests-gate、guard-kill、lumos-cli-lifecycle**:本 diff 沒碰 `search`、還原翻紅釘、處置閘、bound-tests、guard kill、re-inject 的程式,不會破壞。
- **pitfalls-code-loop(★RISK★)**:本 diff 沒動對應程式。

### 慣例(CLAUDE.md)
我沒找到能逐字引出規則又指得出違反行的項目。

## 三問
1. **原問題的修復效果**:有行為證據。授權守衛的破壞實驗 A、B 都翻紅,`-k license_headers` 在修後 8 通過;NULL、負值、`drawChart`、分號截斷各有測試,修後全過。
2. **修補處的正常、錯誤與相鄰路徑**:仍成立。這包括「`.sql` 寫 `#`」「其他副檔名」「`names` 的 `IS` 在大資料量下」「收據重跑的多查詢與 header 字樣」。
3. **新發現的同一案例在修前、修後各是什麼結果**:只有第 1 條。修前 f96ffe70 沒有這條 `.sql` 前置斷言,撤範本不會讓授權測試紅;修後 46773fe6 會紅,是修補新增的耦合。

總結:最高嚴重度 minor
