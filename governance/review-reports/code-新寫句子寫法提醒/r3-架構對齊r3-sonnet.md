severity: minor

**1. 分層與依賴方向:對齊。**
- 新碼留在 `_ns_wd_*` 這一組裡。
- `_ns_wd_toplevel` 向下呼叫既有的 `_drift_py_names`(`scripts/lumos:31398`),沒有另造判法。
- 修補把 tokenize 版的 `_ns_wd_in_string` 整支刪掉,改用 drift 那邊同一個 ast 判法。上一輪的第二種做法已經拿掉。
- 呼叫鏈是 `_ns_wd_count_hit`(`scripts/lumos:31473`)呼叫 `_ns_wd_resolve`,再呼叫 `_ns_wd_toplevel`。`_ns_wd_toplevel` 只在數字已對上時才被叫到。這跟鄰居 `_ns_negation_hints` 的層次一致,沒有跨層直呼。
- 前向引用 `_drift_py_names`(定義在 `scripts/lumos:35735`、使用在 31398)是執行期解析,跟同組既有的 `_count_eval` 前向引用一樣。
- 容器 box 沿用 `_ns_tag_hints_prepare` 的字典形狀(`scripts/lumos:31209`),只把 `str_spans` 換成 `top`。
- 修補沒有新引入分層或依賴方向的不一致。

**2. 命名與錯誤處理:大致對齊,有兩處小差異。**
- 命名照 `_ns_wd_*` 前綴。例外處理與記帳沿用 `_ns_wording_prepare` 的做法(回類別名,見 `scripts/lumos:31318`)。
- 差異一是警告處理,見 F1。
- 差異二是解析失敗時的退路,見 F2。
- 其他提醒的印出與記帳路徑沒有改動。

**3. 第二種做法:`_ns_wd_toplevel` 判「是不是模組層定義」這件事沒有第二種做法,警告處理有一點。**
- `_ns_wd_toplevel` 沒有自創解析,直接用 `_drift_py_names`。它取 `got[1] | got[2]`,也就是類別名加模組層指派名。
- 上限用的是既有常數 `_DRIFT_M1_PARSE_MAX_BYTES`(`scripts/lumos:38521`),沒有自訂數字。
- 改寫後的 `_ns_wd_resolve` 是兩段:先用 `_count_eval` 便宜地數出候選,數字對上才用 ast 確認。這是同一個判定拆成兩步,不是兩套判法。
- `warnings.catch_warnings` 是整個 `scripts/lumos` 裡只有這個新功能才有的做法(grep 只有 31396 和 31419 兩處),而且是在新碼自己裡面重複寫兩次。

### F1 關掉 Python 警告的做法只有新碼有,而且兩處各寫一份
severity: minor
blocking: 否 — 結構沒錯,只是專案裡沒有這種慣例。既有的 `_drift_py_names` 呼叫者沒有跟著抑制,同一種無效跳脫警告走 drift 路徑照樣會印到終端,兩邊行為不一樣。
引句:「with warnings.catch_warnings():     # 同 _ns_wd_def_count:無效跳脫的 SyntaxWarning 不准漏到終端」
佐證行 file: `scripts/lumos:31396`(新增)、`scripts/lumos:31419`(`_ns_wd_def_count`)
對照 file: `scripts/lumos:36103`(`_defines` 呼叫 `_drift_py_names` 不抑制)、`scripts/lumos:38974`(`blob_info` 同上)
建議的方向是把抑制收進一個共用的小函式,或收進 `_drift_py_names` / `_count_eval` 本身。⚠ 這算不算「第二種做法」交編排者裁:我判成 minor,因為它沒有取代任何既有的判法,只是多了既有路徑沒做的防護。

### F2 解析不了或太大的檔,退路跟鄰居不同
severity: minor
blocking: 否 — 這只是提醒功能,偏保守(不提醒)是安全的。
引句:「if len(txt.encode("utf-8", errors="replace")) > _DRIFT_M1_PARSE_MAX_BYTES:」
佐證行 file: `scripts/lumos:31393`
對照 file: `scripts/lumos:38969`(用 `len(raw)` 量原始位元組,太大就退到文字抽定義)、`scripts/lumos:36108`(`_defines` 解析回 None 時退到 `_drift_py_def_re` 的正則,不是直接判否)
新碼兩種情況都直接判「不信、不提醒」,而且為了量大小把整支文字重新編碼一次。`box["py"]` 已經存了解碼後的文字,沒留原始位元組,所以只好重編。

總結:不對齊共 2 條,其中 major 0 條
