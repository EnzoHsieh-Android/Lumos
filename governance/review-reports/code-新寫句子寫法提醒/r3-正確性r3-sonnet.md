severity: minor

我在 `/tmp/lumos-seat-work/code-新寫句子寫法提醒/正確性r3-sonnet/` 下 clone 了修前和修後兩版,用同一支腳本 `exp.py` 對兩版各跑同一組暫存專案。腳本走真的 `note-shape --staged`。修後版的 `python3.14 scripts/test_lumos.py -k note_wording` 是 31 passed、0 failed。

## 三問的已驗結果

**① 原問題的修復效果**

「t-string 裡的假定義被當成真定義」確實修好了。

- 情境:`src/tfake.py` 是 `S = t"""\nTSTR = ("p","q","r") {x}\n"""`,`src/treal.py` 是 `TSTR = ("a","b","c")`,筆記寫「`TSTR` 有三種」。
- 修前:不出提醒。tokenize 沒認出 t-string,假定義和真定義變成兩處,規則放棄。
- 修後:印出 `[count:src/treal.py::TSTR=3]`,沒有 tfake。
- 用 `python3.14 exp.py before|after tf56` 重現。

**② 修補處的相鄰路徑與介面互動**

- **repair(修補原本要修的)**:⑤ 在修後成立,修前不成立。
- **preserve(原本就該保持的)**:⑥ 在修前就成立,修後仍成立。
- 另外跑了 pathfake、docstr、fstr、realfakediff、reassign、twofiles、pathq、multi4、syntaxerr,修前修後行為一致或符合設計。
- 快取鍵 `(path,name)` 存的是各處的成員數、與 n 無關,所以同一名稱配不同 n(multi4 的「三種、四種」)沒有互相污染。
- 50 個名稱上限有觸發,而且只算找得到定義的名稱,這部分沒看出問題。
- 大於 4 MB 的檔改成不提醒:bigfile 和 cjkbig(約 4.5 MB 的 UTF-8)修前會出提醒、修後不出,和計劃寫的設計一致。
- 4 MB 用 UTF-8 位元組量,和 `scripts/lumos:38969` 的舊句檢查同口徑。

**③ 隔離**

- `_ns_wording_collect` 的 `except Exception` 會清空 items、記類別名。
- `_ns_wording_emit` 整段在 try 裡。
- `_ns_wd_toplevel` 的 `_drift_py_names` 自己接住 MemoryError 和 RecursionError。
- 我沒有找到「丟例外會改回傳碼」或影響另外兩組提醒的路徑。
- 語法錯誤的 Python 檔(syntaxerr 例)修前修後都不出提醒、不報錯。

## Findings

### F1 數量提醒可能把標記指到字串裡的假定義
severity: minor
blocking: 否 — 只是提醒,而且 `drift scan` 掛上標記後會再判一次。
引句:「    real = [(p, c) for p, t, c in cands if _ns_wd_toplevel(box, p, t, name)]」
失敗場景:`_ns_wd_toplevel` 只問「這個名稱在這支檔的 ast 裡有沒有模組最上層指派或任何層的類別」。它不問「行首那一處」是不是那個真定義。

- 檔案 `src/d.py` 是 `class O:\n    class PLAIN:\n        pass\nS = """\nPLAIN = ["p","q","r"]\n"""\n`,筆記寫「`PLAIN` 有三種」。
- 行首正則只抓到字串裡那個假的,`_count_eval` 數出 3。
- `cands` 剩那一處,ast 因為巢狀類別 `PLAIN` 判它為真,於是印出 `[count:src/d.py::PLAIN=3]`。
- `nestfn` 的函式內類別、`chainfake` 的 `OTHER = NAME = ("x",)` 這類「ast 看得到名稱、但行首那一處是字串裡的」情況也一樣。
- 修前這三個情境都不出提醒。

重現:`python3.14 exp.py before|after nestedcls`、`nestfn`、`chainfake`(都在 `/tmp/lumos-seat-work/code-新寫句子寫法提醒/正確性r3-sonnet/`)。修前三個都沒有 `[count:`,修後都印出指向 `src/d.py` 或 `src/c.py` 的標記。
歸因:有證據的修復回歸。
佐證行:`scripts/lumos:31383`、`scripts/lumos:31387`、`scripts/lumos:35735`

### F2 同一支檔裡「假定義加真定義」的數量提醒被吞掉
severity: minor
blocking: 否 — 只是漏提醒。
引句:「    return real[0][0] if len(real) == 1 and real[0][1] == n else None」
失敗場景:`src/s.py` 是 `NAME = ("a","b","c")\nF = """\nNAME = ["p","q","r"]\n"""\n`,筆記寫「`NAME` 有三種」。

- 行首正則抓到兩處,同一支檔的 ast 對兩處都回「是真的」,`len(real)==2`,回 None。
- 修前 tokenize 排除字串裡那處,印出 `[count:src/s.py::NAME=3]`;修後不出。
- 這正是修補後的測試 ⑤⑥ 沒涵蓋的相鄰路徑:它們把假的和真的放在不同檔。
- 測試檔本身常在字串夾具裡放頂格定義,這個漏報可能常見。

重現:`python3.14 exp.py before samefile` 和 `python3.14 exp.py after samefile`。
歸因:有證據的修復回歸。
佐證行:`scripts/lumos:31383`、`scripts/lumos:31384`

## 已看但沒標 finding

- `_ns_wd_resolve` 改成對每處定義都呼叫 `_ns_wd_def_count`。我用 60000 個同名行首定義量,時間和修前相同,最大記憶體約 359 MB 對 221 MB。時間上沒有新增的退化。
- 修前同一情境也是二次方增長:300k 個定義修前已經要 123 秒。
- 理論上可以構造最多 50 個名稱各命中不同的 3 MB 檔、各付 ast 整支解析。我沒有拿到具體輸入,不標。

**pitfalls manifest:**我沒有逐條去對 `/tmp/lumos-seat-work/code-新寫句子寫法提醒/manifest.json`,這一鏡頭未驗。

**圖譜鏡頭:**我沒有跑 `lumos impact`。題目提供的機械反查三格皆空,我沒有補查。

總結:共 2 條,最高 minor
