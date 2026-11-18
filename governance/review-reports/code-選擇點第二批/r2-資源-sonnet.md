severity: minor

三問都有答案。關鍵發現是修補確實把新規則的輸出壓下來了；殘留的平方成長是 ast-grep 輸出格式本來就有的，不是這次修補造成的。「長度」指單行文字的長度。實驗都在臨時副本做完，已用字面絕對路徑刪除，沒有孤兒程序。我沒有改 repo 裡的檔。

## r1 單行很長且有大量 `?.` 時，輸出仍是平方，會整批算不出來
severity: minor
blocking: 否 ——失敗場景只有人造的單行超長輸入，沒有一般 Kotlin 會走到的路徑，而且走到時是 rc3「沒檢查到」，不是放行錯誤。

輸入是同一行裡 3000 個 `a?.b`（約 27KB 的單行）。走到 `_choice_scan_one` 或 `_choice_scan_batch`，ast-grep 每個命中都帶出整行文字，輸出等於命中數乘以行長。實際結果是 rc=-25（被檔案大小上限 `RLIMIT_FSIZE` 中止），回報「ast-grep 掃描回 -25」，rc3。預期是照常掃完。

這是 ast-grep 輸出格式本來就有的現象，不是新規則造成的：
- 同一個檔，修前（`eebb84593d24`）也是 rc=-25。
- 6.3 萬字元單行 `a0 + a1 + …`（8000 項）在修前和修後的 AOR 規則都產生 1.25GB 輸出。
- 磁碟寫滿的風險已被 `RLIMIT_FSIZE` 擋住：輸出被截在約 64MB 就中止，沒有寫出 GB 級的檔。

引句:「正面寫 inside 時 ast-grep 把整條外層鏈當次要標記塞進每個命中,長鏈與密集檔的輸出變成平方」
file: `scripts/lumos:42892`
歸因：未判定，傾向有證據的原有漏查。兩版都是 rc=-25；修後只在「多行」與「單行 3000 個 `?.()` 的鏈」上變好。

## 逐問回答

**①輸出平方成長**

修補後的實測（含修前對照）：

| 輸入 | 修前 | 修後 |
|---|---|---|
| 1000 層多行 `remember(k) {` 巢狀 | 56MB | 0.84MB |
| 1000 層多行 `x.let {` 巢狀 | 37.6MB | 0.48MB |
| 1000 層多行 `a.combine(` 巢狀 | 30MB | 0.50MB |
| 1000 層 `LaunchedEffect` 巢狀 | 74MB | 0.86MB |
| 1000 個 `?.` 分多行 | 7.8MB | 0.48MB |
| 3000 個 `?.()` 的單行鏈 | rc3 | rc0 |

仍會平方成長的寫法，沒有一個是新規則專有的：
- 一行塞很多命中（見 r1）。
- 在引數裡又嵌引數，例如 `remember(k, g(remember(k, g(…)){…}))`。深度 600 時 C-37 輸出 14.5MB。深度 2000 時估計超過 64MB，單檔直接記「算不出來」。真實程式碼不會有這種深度。
- 右巢狀 `a ?: (b ?: …)`（C-32，沒改）。

檔案本身大時，輸出大致隨檔案大小線性成長，沒有被平方放大：
- 4MB 的人造密集檔，新規則（C-33 到 C-37）單獨掃描約 128MB 輸出、2.6 秒。
- 1MB 的人造密集檔，新規則單獨掃描約 32MB、0.7 秒。

**②引數錨點與撤列號檢查有沒有二次方**

沒有。
- `_choice_anchor` 的引數分支，每個命中只掃自己範圍內的行，碰到第一個改動行就返回。就算 600 層巢狀、每層範圍都包住內層，挑壞法也是 5.4 秒（修前 5.5 秒）。
- 4MB 目錄文字裡的「已撤列號」檢查是線性：4.8MB 文字 0.021 秒；50 萬行都提到「已撤列號」也只要 0.03 秒，錯誤訊息只帶前 3 行。
- 樣本標記的正規式 `_CHOICE_SAMPLE_MARK` 遇到「標記後面接 2 萬個空白再接怪字元」會二次方（1.5 秒）。它不在這次 diff 裡，輸入又是作者自己寫的樣本檔，不算 finding。

**③推送前挑壞法的 15 秒時限**

沒有變慢，守衛不會降成提醒。
- 這次修補沒有碰挑壞法的程式，只改了規則檔、check.py 和統計。
- 250KB、3250 行全是改動行：總共 6.7 秒，修前 6.8 秒。
- 500KB、6456 行全是改動行：總共 17.07 秒，修前 17.26 秒。其中掃描約 12.7 秒、挑壞法約 4 秒，後者在 15 秒內。
- 慢的是修前就有的規則，不是新規則：
  - 500KB 的 CPU 耗時被舊規則吃掉；新規則單獨跑 500KB 只要 0.36 秒。
  - 掃描 CPU 對「同一個區塊的陳述數」是平方。一個函式 5000 個陳述約 4.5 秒（修前 4.5 秒），1 萬個約 20 秒，2 萬個超過 80 秒。
  - 這個平方出在 `nthChild reverse ofRule`，C-34 和 sbr.yml 的舊規則共用。
  - 超過時限只會記「驗不了」，不會卡住。

**④`gov --stats` 依列號的記憶體**

12 萬行全是不重複的選擇點事件時，`_gov_choice_counts` 加 `_gov_choice_by_row` 保留約 43MB（`tracemalloc`）、耗時 0.77 秒，`row_mut` 9.6 萬鍵、`row_waive` 2.4 萬鍵。比帳本本身載入的大小小很多。

## 修補鏡頭三問

1. **修復效果的證據：已驗證。**
   - claim：C-33、C-34、C-35、C-36、C-37 改成雙重否定後，巢狀輸入的輸出不再平方。
   - input：上面 r1 之前那張表裡的多行巢狀輸入。
   - expected：線性。
   - before / after：56MB→0.84MB 等，見表。
   - comparison：修前輸出超過 30MB，修後不到 1MB。
2. **修補處的正常、錯誤與相鄰路徑：已驗證。**
   - claim：`.let` 回傳值被用到的、LaunchedEffect 的 key 不是常數的，仍照常命中。
   - 測試：`t_choice_samples_batch2`（25 案）、`t_gov_stats_choice_by_row`（5 案）、`t_choice_table_batch2`（12 案），在修後副本全綠。
   - 沒驗：真實專案的挑壞法穩定性（`t_choice_points_batch2_stable`），我沒跑。
3. **新發現同一案例在修前、修後：**
   - r1：修前 rc=-25，修後 rc=-25，不是回歸。
   - 陳述數平方（C-34 配 sbr）：修前 4.5 秒、20 秒，修後 4.09 秒、19.3 秒，不是回歸，也不是這次新增。

最嚴重：minor；blocking 共 0 條

## 圖譜鏡頭

固定席節點逐條判，全部不影響：
- `Systems/kotlin規則包.md`：牽連 `check.py` 與 `api.yml`。我讀過兩份差異與規則，沒有看到與節點相矛盾的描述，不影響。
- `Systems/bound-tests-gate.md` 的 ★INVARIANT★：只管綁定測試的跑法。這次改動沒有動綁定測試的執行路徑，不影響。
- `Systems/guard-kill.md`、`lumos-cli-lifecycle.md`、`測試假綠形態.md`、`lumos-cli-read.md` 的 ★INVARIANT★：guard kill 的 rc 優先序、re-inject、還原翻紅釘、search 排除，與這次的規則和統計改動無關，不影響。
- `pitfalls-code-loop.md` 與 `loop-convergence-recording.md`（★RISK★）：這次改動沒有碰推送閘的收斂邏輯，不影響。
- 殘留合約（殘留索引與帳內「這次新增的殘留」算不出來）：這是機器附加的提問，我沒有取得殘留的問答列，無法判定，標未判定，不寫「沒有」。

附帶說明：本席沒有碰 `docs/` 筆記，所以沒有動到任何一篇圖譜節點。

相關路徑（已刪除的臨時目錄不再列）：
- `/Users/enzo/harness/lumos-near-miss/configs/ast-grep/kotlin-choice/rules-choice/nul.yml`
- `/Users/enzo/harness/lumos-near-miss/configs/ast-grep/kotlin-choice/rules-choice/api.yml`
- `/Users/enzo/harness/lumos-near-miss/configs/ast-grep/kotlin-android/check.py`
- `/Users/enzo/harness/lumos-near-miss/scripts/lumos`
