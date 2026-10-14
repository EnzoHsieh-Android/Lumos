severity: minor

我沒找到會讓分片漏跑、重跑,或讓壞表被靜默放行的錯誤。只有兩條 minor,都不阻擋推送。以下都在固定版本 aea70018 的複本上實跑。

## 已驗的正向主張

**1. `_read_durations_table` 的各種壞法都回得對。** 直接呼叫的結果如下:

| 輸入 | 結果 |
|---|---|
| UTF-8 BOM | 讀得進 |
| NaN、`1e999` | ValueError |
| 100000 層巢狀 | ValueError,沒有崩潰 |
| 重複的 `tests` 鍵(後者為空) | ValueError |
| `-0.0` | 讀得進 |
| JSON 結尾有 `\x00` | ValueError |
| 非 UTF-8 位元組 | ValueError |
| 兩個 JSON 接在一起 | ValueError |

表路徑不存在時回 `(None, None)`。路徑是資料夾或斷掉的符號連結時,都回 ValueError「不是一般檔」。

**2. 執行器在各路徑的結果一致。** 我用 `--shard 1/4` 跑,表分別是空 `tests`、資料夾、斷掉的符號連結,三種都是擋下並說明。表正常時印出「分法:耗時表 19a95d9d,共 2049 支,這份分到 512 支」。

**3. `_shard_by_duration` 只回傳測試數那麼多份,呼叫端的取片邏輯成立。** 呼叫端用 `_i <= len(_buckets)` 判斷,超出時是空集合,不會越界。空片判定照舊:加 `--suite` 時回 rc0,不加時回 rc1。測試⑥已涵蓋一千萬份在 0.5 秒內算完。

**4. 每片跑完再讀表比對有效。** 開頭沒有表、結尾有表時,會擋下並回 rc2(`t_test_durations_refresh` 內有實跑,用 `t_zzswap_table` 中途寫出表)。表沒換時回 rc0。

**5. run 檔改名後,刷新與 `.gitignore` 仍涵蓋。** 實際用的名字是 `test-durations-run-shard1of4.json`,`.gitignore` 的 `.lumos/test-durations-run*.json` 和刷新的 glob 都涵蓋。

**6. 刷新的行為正確。** 我實跑了幾種情況:
- run 檔內容是 `b:true` 或 `c:"x"` 時,這兩筆不收。
- 取不到檔案資訊的 run 檔略過,不會讓排序崩潰。
- 舊表是資料夾時回 rc2,不覆蓋。

**資料狀態五問:**
- **新舊互讀:** 主線沒有 run 檔,所以沒有舊命名要相容。倘若本機殘留 `1of2` 這類舊名檔,glob 仍會吃進去。
- **寫一半:** 讀到半寫的表會變成 ValueError,再由結尾比對擋下。
- **衍生資料:** 表只影響分得平不平均,不影響會不會漏跑。
- **時間:** 同一支測試取檔案時間最新的那筆,已驗。
- **不可逆:** 刷新遇到讀不懂的舊表不覆蓋;run 檔在讀完之後又被改寫的會保留。

**測試品質:** 新測試有逐條規則的手算期望、聯集等於全部的檢查,以及子行程實跑。拿掉任一條規則,測試就會翻紅,不只是把實作重寫一遍。

**修補鏡頭三問:**
- **原問題的修復效果:** 上面的 3、4、6 是同一案例的行為證據。這輪我只驗修後版本,沒有對修前版本逐案例重跑。
- **相鄰路徑:** 表壞或沒有表、`--suite` 空片、片數大於測試數這些路徑都仍成立。
- **新發現在修前修後的結果:** 見下面兩條 finding,歸因都是未判定。

## Finding 1

severity: minor
blocking: 否

引句:「return _load_lumos_inproc()._read_durations_table(_durations_table_path())」

- **輸入:** 執行器旁邊沒有 `scripts/lumos`,或主程式載入時丟出非 OSError 的例外(語法錯、缺 `_read_durations_table`),再下 `--shard 1/2`。
- **實際行為:** 載入失敗的 FileNotFoundError 是 OSError,會被 `except (OSError, ValueError)` 接住。但 handler 的 f-string 裡又呼叫 `_durations_table_path()`,那裡會再次載入主程式,而且不在 try 裡,於是整支崩潰成 traceback,不是乾淨的 rc2 說明。
- **重現:** 只複製 `scripts/test_lumos.py` 到一個沒有 `lumos` 的目錄,執行 `python3.14 scripts/test_lumos.py --shard 1/2 -k t_runner`。輸出是 `FileNotFoundError: ... /scripts/lumos`,堆疊從 `_load_lumos_inproc` 往上。
- **應該是:** 載入失敗也印「擋下」並回 rc2,錯誤訊息裡的路徑不要再觸發載入。
- 歸因:未判定。修前版本的讀表規則在執行器內,不需載入主程式,所以修前沒有這條路徑;但我沒有對修前版本做同案例實跑。

## Finding 2

severity: minor
blocking: 否

引句:「print(f"✓ 耗時表更新:{_TEST_DURATIONS_REL}(原有 {before} 支 → 現在 {len(table)} 支;這次合進 {got} 筆,讀完刪掉 {len(runs) - kept} 個 run 檔)")」

- **輸入:** `.lumos/` 下有名稱符合 `test-durations-run*.json` 的資料夾(例如 `test-durations-run-d.json/`)。
- **實際行為:** 它被 glob 收進 `runs`,讀取時 IsADirectoryError 被略過。結尾 `unlink()` 刪不掉,但被 `except OSError: pass` 吞掉,而 `len(runs) - kept` 仍把它算成已刪。
- **重現:** 我放了一個正常 run 檔加一個同名樣式的資料夾,輸出「讀完刪掉 2 個 run 檔」,`ls .lumos` 卻還留著該資料夾。
- **應該是:** 實際刪掉幾個就報幾個。
- 歸因:未判定。這條路徑和 glob 邏輯在修前就存在,修補沒有改它。

## 固定席節點

這次沒有附固定席節點,所以沒有逐條判的對象。

## 未驗範圍

- 沒有跑全套測試,也沒有在 CI 上跑。
- 沒有逐案例重跑修前版本 22f6e132。
- 沒有驗消費專案裡 `GRAPHCTL` 是符號連結時,`.resolve()` 之後的表路徑會落在哪個目錄。這和既有的 cache 路徑寫法一致,所以我沒有當成新問題。

最嚴重等級 minor,blocking 共 0 條。

我的臨時目錄在 `/tmp/lumos-seat-work/code-推送與CI提速-r3/正確性-sonnet/`,留給編排者刪除。
