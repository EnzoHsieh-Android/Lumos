severity: minor

三問都對照過 `scripts/test_lumos.py` 的鄰居寫法。結構層(分層與依賴方向)沒問題,不一致集中在「取今天日期」的做法。我只讀了 patch 和 `scripts/test_lumos.py`,沒有讀 `python-idioms` skill。第 3 條是 ⚠,下面說明原因。

**問 1,分層與依賴方向:對齊。**
- 兩支測試仍用 `run(v, "gov", ...)` 打 CLI,測試的位置跟鄰居一致。
- patch 沒有新增跨層呼叫,也沒有新依賴。
- 知識圖譜的 PITFALL 行放在 `test-quality-handbook` 節點(該節點的 `about_code` 已列 `scripts/test_lumos.py`),所以筆記的家沒有問題。

**問 2,命名與錯誤處理:有一處不一致。**
- 鄰居的做法是在測試函式內寫 `import datetime`,再用局部變數 `today` 或 `past`。例如 `scripts/test_lumos.py:2984`(`today = datetime.date.today().isoformat()`)和 `scripts/test_lumos.py:7329`(`past = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()`)。
- 新碼取日期的方式見下面第 1、2 條。
- 沒有錯誤處理差異,日期計算本身不會出錯。

**問 3,第二種做法:有。**
- `__import__("datetime")` 內聯匯入在檔內有 1 處是匯入 datetime 的,就是這條新碼。
- 檔內有 77 處 `import datetime`,24 處 `datetime.date.today()`,沒有一處用 `__import__("datetime")`。
- 另一種情況不算同族:檔內也有 `__import__("os")`、`__import__("re")`(例如 `scripts/test_lumos.py:126`),但那是 os 和 re,不是日期。
- 我把嚴重度定為 minor 而不是 major,有兩個考量,第二個是 ⚠:
  - 「模組層級常數」這一點,檔內沒有現成的模組層級日期常數可對照。
  - 內聯 `__import__` 這種寫法並不陌生,所以我判成「寫法跟鄰居不一致、結構對」。如果你把它當成「引入第二種取日期的方式」,可以改判 major。

## 1 模組層級用 __import__("datetime") 取今天日期,鄰居是函式內 import datetime
severity: minor
blocking: 否
引句:「_GOV_D = (__import__("datetime").date.today() - __import__("datetime").timedelta(days=5)).isoformat()」

鄰居慣例是在測試函式內 `import datetime`,再寫 `datetime.date.today()`(`scripts/test_lumos.py:2984`、`scripts/test_lumos.py:7329`、`scripts/test_lumos.py:7453-7456`)。這裡改用內聯 `__import__`,而且在同一行呼叫了兩次。

## 2 日期在模組載入時算死成常數,鄰居在每支測試執行時才算
severity: minor
blocking: 否
引句:「# gov 預設只看近 90 天:測試帳的日期寫死會隨日子過去掉出窗外」

鄰居的「今天」都是在測試函式裡現算(`scripts/test_lumos.py:7453` 的 `today = datetime.date.today()`)。新碼把值放在兩支測試共用的模組層級 `_GOV_D`,載入時就固定了。

- 這跟鄰居不同:鄰居每支測試各自取一次,不共用狀態。
- 檔內沒有其他模組層級的日期常數,我確認過。
- 後果是這個常數跟測試本身分離,跟「相對今天」的鄰居寫法不同形狀,但結構不算錯。
- 把這條放在 ⚠ 的邊緣:不同的是「共用」這件事,不是取日期的 API。

## 3 過濾條件改成 _GOV_D[:5],鄰居沒有用字串切片取年份前綴的寫法
severity: minor
blocking: 否
引句:「body = [l for l in r.stdout.splitlines() if l.startswith(_GOV_D[:5])]」

原本的 `startswith("2026-")` 是寫死的年份前綴。新碼改成從常數切 5 個字元,在跨年時(例如 1 月初,往前 5 天落到上一年)會跟輸出行的年份不符。這是風格層的差異,結構沒變,所以只列 minor。

不對齊共 3 條,其中 major 0 條
