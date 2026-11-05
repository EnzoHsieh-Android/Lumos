severity: minor

沒有會擋的問題。只有兩條 minor,都不會讓目前的規則包或型錄出錯。

## Finding 1
severity: minor
blocking: 否
標題:`_files_block_is_test_only` 只去掉整行註解,行尾註解沒處理
引句:「# 先去掉整行註解:頂格註解(例「# 不掃 src/main」)不算 files 區塊的內容,也不該把區塊截斷」
file:line:`configs/ast-grep/kotlin-android/check.py:36`(修補在 31 行)
失敗場景:規則檔寫成 `  - '**/src/test*/**'   # 不含 src/main`。我實際跑過,回傳 False。這條只掃測試碼的規則會被判成「不是只掃測試碼」。結果是 `check()` 漏掉對 `samples/ancestor-named-test` 的檢查,而且不報任何問題。目前 `rules*/` 底下沒有行尾註解提到 `src/main` 的規則(grep 過),所以現在不會出錯。
歸因:未判定。這是修前就有的缺口,修補只補了整行註解。
證據:修後版本用複本跑上述輸入,得 `False`。修前版本沒另外跑,因為修前連整行註解都不處理。

## Finding 2
severity: minor
blocking: 否
標題:`dt_triggers` 認全形括號,但分隔字元類裡沒有全形逗號
引句:「trig = [t.strip().strip("`") for t in re.split(r"[、,,]", norm) if t.strip()]」
file:line:`configs/ast-grep/kotlin-android/check.py:60`
失敗場景:字元類 `[、,,]` 的第二、三個字元都是 0x2c(我讀位元組確認),全形逗號不在裡面。輸入「(無)，foo」會得到 `(['(無)，foo'], None)`。結果是「(無)」跟其他觸發字並列的檢查不會報,整串被當成一個觸發字。目前型錄裡沒有任何全形逗號(grep 為 0)。
歸因:有證據的原有漏查。修前的 split 字元類一樣,修補沒有碰它。

## 已驗的主張
做法:把 `ba5996e5a` 用 `git archive` 解到臨時目錄。每道新檢查各自改壞一次,跑 `-k kotlin_catalog_rows` 和 `-k kotlin_rulepack_samples` 看是否翻紅。未改壞時兩組分別是 18 和 20 條全過。

**各改壞結果**
| 改壞點 | 翻紅的測試組 |
|---|---|
| 拿掉整行註解去除 | 樣本組 |
| 拿掉「(無)」並列檢查 | 型錄組 |
| 拿掉全形括號正規化 | 型錄組 |
| 缺〈來源縮寫〉節改回直接 return | 型錄組 |
| 拿掉 `got is None` 分支 | 樣本組 |
| 拿掉 `check()` 開頭重設旗標 | 樣本組 |
| 拿掉 `scan` 設逾時旗標 | 樣本組 |
| 拿掉 `loaded_count` 設逾時旗標 | 樣本組 |
| `dt_triggers` 回 `[None]` | 型錄組 |
| 把 `rule_id in review_ids` 條件換成永遠成立 | 樣本組 |

以上都是各自翻紅,逾時兩條路徑的 `<2.5 秒` 斷言也各自守得住。

**`review-fp-` 判斷拿掉 `owner == rule_id`**
- 這個改動行為上等價,不是漏洞。最後只讀 `hits[("good", rid, rid)]`,owner 不等於 rule_id 的命中本來就不會被計。
- 把 `owner == rule_id` 加回去,測試全綠,這證明它沒有行為差異。

**其他路徑**
- 缺〈來源縮寫〉節時,`abbrs` 是空集合,來源欄會多報一堆來源問題。這是噪音,不是錯。
- `got is None` 時訊息不再印「載入 None 條」。
- `_TIMED_OUT` 在每次 `check()` 開頭重設,連跑兩次不會互相污染。

**三問的回答**
- 原問題修復:上表每條都有修後的翻紅證據。
- 修補處相鄰路徑:真型錄 18 條全過、真規則包樣本 20 條全過。
- 新發現的修前結果:Finding 1 沒跑修前,Finding 2 在修前相同。

未驗範圍:ast-grep 的 `--inspect` 輸出格式在其他版本是否變動,我只用了 0.51.1。

我跑變異留下的 10 份 `gctl-run-*` 現場和臨時目錄都已刪掉,只刪自己的,沒碰別的會談的。
