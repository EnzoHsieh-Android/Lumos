severity: clean

資安三類逐類看過,沒有可利用的洞。範圍是 r6-snapshot.patch 的 `scripts/`、`configs/`、`skills/`、`docs/` 改動,加上 r6-repair 的差異。

**①提示注入:已看,無**
- 新增的 `_choice_retired`、`choice_sample_mark_problems` 會把目錄裡的文字回顯到問題清單:型錄「已撤列號」那行(切到 60 字)、樣本檔名、列號。來源都是 repo 內已提交的型錄與樣本,不是外部輸入,屬既有的「外來文字回顯放行」慣例。
- `gov --stats` 的「依列號」小節輸出帳本來的 `row` 與放行標籤,都先過 `_kill_esc`,`row` 另外截成 20 字。沒有未跳脫的自由文字進到給 AI 的輸出。

**②讀寫與執行越界:已看,無**
- 讀檔只有 `_choice_sample_marks`:對 `<規則包>/samples/*.kt` 做 glob 後讀取,路徑固定在 repo 內,只取行尾標記,內容不回顯。
- 新增的 `subprocess.run` 只在測試,執行 `sg scan`,參數是列表(無 shell),`cwd` 與規則檔都在自己的 `tempfile.mkdtemp` 目錄裡。
- 測試的 `shutil.rmtree(root)` 只刪 `_stats_fixture` 自己建的目錄。
- `_choice_anchor_edits` 只在位元組串上組編輯清單。樣板是型錄裡固定的 `$A!!`、`!!.` 與引數樣板,沒有 shell 插值或 eval。
- 此範圍沒有新增下載網址或讀環境變數的程式。
- 沒有密鑰或信箱。改動裡唯一的 `"token"` 是測試用 `os.urandom` 產的帳本欄位。

**③非刻意繞過守衛:已看,無**
- 列號正規式 `[CA]-[1-9][0-9]*`(含修補新增的 `C-0`、`A-0`)用 `fullmatch`,前導零與全形數字照擋。`C-0` 與 `A-0` 在修前就走同一條拒絕路徑;修補只補了測試,`scripts/` 沒動。
- 排序鍵 `_row_key` 限 9 位 ASCII 數字,`C-²` 這類怪列號不會讓排序丟例外。
- 已撤列號那行的認不出情形,一律報問題,不會靜默當成沒有。

**圖譜鏡頭:** lens-r6.txt 我沒讀。這次的程式、規則、測試改動都在選擇點變異測試與型錄檢查裡,沒有碰 hook、安裝腳本、CI 或對外呼叫,我判定不影響資安面。

**回答三問(同一案例證據)**
- ①修復效果:
  - claim:`C-0`、`A-0` 列號被擋。
  - input:選擇點表列號 `C-0`、乾節點表列號 `A-0`。
  - expected:報「列號要寫成…」。
  - before(c261a154):行為證據未判定,我沒有跑修前版本。
  - after(8333987a):`python3.14 scripts/test_lumos.py -k choice_table_batch2` 為 22 passed、0 failed。
  - comparison:只有修後單側證據,不能單憑這點證明回歸或已修。
- ②正常、錯誤與相鄰路徑:
  - claim:C-36、C-37 的 literal-arg 與樣本標記路徑照常。
  - input:新增的 `LaunchedEffect(@Suppress("x") 1)` MISS、`LaunchedEffect(-k + 1)` HIT 等樣本行。
  - expected:各樣本照標記命中或不命中。
  - after:`-k choice_samples_batch2` 為 33 passed、0 failed。
  - before:未判定,沒跑。
  - comparison:只有修後單側證據;上述兩個子集測試也只是從程式面確認沒有立即回歸。
- ③新發現:沒有新發現,所以沒有修前修後對照。

**未驗範圍:** 變異掃描與差異比對由編排者手動跑,我沒重跑;修前版本沒有檢出;`choice-kill` 實際套用變異到專案原始碼的流程不在這次差異內,沒審。

最嚴重:clean;blocking 共 0 條
