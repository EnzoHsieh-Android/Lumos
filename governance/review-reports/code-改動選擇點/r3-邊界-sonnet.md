severity: minor

## b1 整批掃描遇到被 gitignore 的暫存目錄時靜默掃出零個選擇點
severity: minor
blocking: 否(要把 TMPDIR 設在忽略 `*.kt` 的 git repo 裡才會發生,但發生時閘會靜默放行,所以列出)

輸入:`TMPDIR` 指到一個 git repo,且該 repo 的 `.gitignore` 寫了 `*.kt`。呼叫 `_choice_scan` 掃含中文檔名在內的 4 支檔。

路徑:`_choice_scan` 檔數大於 1 → `_choice_scan_batch` 執行 `ast-grep scan --config … --json=stream src`。

壞在哪:目錄模式的 ast-grep 會套用上層的 `.gitignore`,檔案被整支跳過,rc 仍是 0 而且輸出是空的。`_choice_scan_parse` 先用 `texts` 建出每支檔的空結果,所以回的是「掃完、零個選擇點」,不會走退回逐檔,也不會進 `bad`。推送前那一道就不會要求任何處置。

修前的逐檔模式把檔案路徑明確交給 ast-grep,不受這個影響。

預期與實際:
- 預期:跟修前一樣,中文檔與 ok.kt 各 1 個選擇點。
- 實際(修後):4 支檔全是 0 個選擇點,`bad={}`。
- 對照:不設這個 `TMPDIR` 時,修後版本同樣的 4 支檔會判出 1、0、(error 1)、1。

引句:「整批失敗(逾時、rc 異常、輸出超過讀取上限、剖不了)才★退回按檔分開★各跑一次」
file: `scripts/lumos:77035`(`_choice_scan_batch`)

歸因:有證據的修復回歸。

兩版證據(同一支探針 `/tmp/lumos-seat-work/code-改動選擇點/邊界-sonnet/p/probe3.py`,`TMPDIR` 指向含 `.git` 與 `.gitignore: *.kt` 的目錄):
- 修前 f1be3141:`a/中文.kt 1 0 0`、`d/ok.kt 1 0 0`。
- 修後 8e521300:`a/中文.kt 0 0 0`、`d/ok.kt 0 0 0`、`bad={}`。

這只是掃描時暫存目錄被忽略規則吃掉。整批與逐檔的結果會不一致,卻不會被偵測到。

## 三個問題的回答

### ① 原問題的修復效果(行為證據)

**H3 整批掃描:已修復。** 1400 支檔、各 7 行的輸入,呼叫 `_choice_scan`:

| 版本 | 耗時 | 結果 |
|---|---|---|
| 修前 | 35.4 秒 | 1400 支都判得到 |
| 修後 | 0.4 秒 | 1400 支都判得到,`bad` 為空 |

另驗證了這幾種輸入,修後都正常:
- 中文檔名加註解(多位元組)。
- 空檔。
- 語法錯誤檔(出 1 筆 error)。
- 空 dict(回 `{}`)。
- 單檔(走逐檔)。

`python3.14 scripts/test_lumos.py -k choice_scan`:9 過 0 敗。

**H1 守的測試雜湊:已修復。** 計劃筆記 `docs/plan.md` 排在 `feature/src/test/…` 前面,測試名寫在筆記裡。探針 `p/probe4.py`:

| 版本 | 只改筆記,雜湊不變 | 補強測試內容,雜湊變 |
|---|---|---|
| 修前 | False | False |
| 修後 | True | True |

另測了修後的幾個行為,都正常:
- 測試名是別字的子字串(`short` 對 `shortLong`、兩個互為前綴的中文帶空白反引號名),各自找到所在檔。
- 中文測試檔名可正確收到。
- `HEAD` 與完整 sha 兩種寫法結果相同。

`python3.14 scripts/test_lumos.py -k choice_kill_test_files`:19 過 0 敗。

**H2 選擇點放行進推送前小結:已修復。** 讀碼確認 `_lint_waivers_ai_pending(choice=True)` 與 `ai_pending_choice` 接到小結。lint 與情境段兩條路徑沒動。我沒跑這一組測試的單獨子集。

**H4 文件:已修復。** 計劃第 58 行與 S6、S9、S10 的寫法,和 `_choice_points_unverified` 回 3、choice-kill 回 2 的程式一致。

### ② 修補處的正常、錯誤與相鄰呼叫路徑

- **雜湊成立的路徑:** 正常的測試名與兩平台同名,按 `(平台, 測試名)` 為鍵各自算。測試名在測試路徑裡找不到時記 `?`。`git` 因參數太長而起不來(`OSError`)時,`_lens_git` 會回 None,整批記 `?`,不會崩。
- **3000 項串接:**
  - 輸入:3000 個測試名,散在 30 支測試檔(約 12k 行)。
  - 結果:單次 `git grep` 撞到 20 秒上限,3000 支全記 `?`、`complete=False`。
  - 後果:survived 的行一律重跑,推送端不印「另一組測試」。這是保守方向,不是壞的行為。
  - 對照:修前同一輸入對每個測試名各跑一次 `git grep`,超過 120 秒仍沒跑完,我手動停掉。所以這不算回歸。
  - 取捨:1000 個測試名時 4.1 秒完成,查得完。
- **批次路徑:** 整批輸出超過 64MB 退回逐檔,這個情況是作者自己列為「未覆蓋」的,我沒重驗。
- **整批掃描的相鄰風險:** 即 b1。

### ③ 新發現的同一案例,修前與修後

只有 b1。修前正常,修後靜默零命中,兩版結果見 b1。

## 圖譜鏡頭

固定席沒附,hook 說算不出來,所以沒有逐條判的項目。

我看過改動的檔:`scripts/lumos` 的 `_choice_scan`、`_choice_test_blobs`、`_choice_tests_sha`、`_choice_kill_pick`、`_choice_push_stale_tests`、`_lint_waivers_ai_pending`,以及計劃筆記與規格閘筆記的文字。沒有看到破壞既有合約的跡象。

## 未驗範圍

- 沒驗真 Android 專案的端到端耗時。
- 沒驗 ast-grep 不在 PATH 與回非零的逐一路徑。這部分由 `t_choice_no_ast_grep`、`t_choice_scan_per_file` 負責,我只跑了 `-k choice_scan` 與 `-k choice_kill_test_files` 兩組。
- 沒驗兩平台同名測試在不同根目錄下的實機行為,只讀了 `_choice_plat_prefix`,測試 ③ 有涵蓋。
- 沒驗遠端名帶斜線與生效日。這份修補沒動到這兩處。

暫存已用字面絕對路徑刪除,只留下 `/private/tmp/lumos-seat-work/code-改動選擇點/邊界-sonnet/p/` 底下的五支探針腳本。

最嚴重:minor;blocking 共 0 條
