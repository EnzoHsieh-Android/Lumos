severity: major

上輪邊界席兩條都修好了。這輪找到一個新崩潰（F1），另有兩條 minor。實驗都在臨時 repo 用實際函式跑，臨時目錄已刪。

**上輪核對**
- **上輪 F1（超長行號）：已修。** `d/f.txt:` 後接 5000 位數字、`1-` 加 5000 位數字，都回 False 並帶「行號不在檔案範圍內」，不再崩潰。
- **上輪 F2（指向 repo 外的連結被叫先提交）：已修。** 輸入是工作目錄裡指向 `/etc/hosts` 的連結 `wl`，回「提交了也不算」。懸空連結 `../outside` 不給提示。
- **符號連結其他輸入：結果符合預期。**
  - 目錄連結中段 `dl/f.txt` 通過。
  - 連結指連結 `l1`↔`l2`（成環）擋下。
  - 連結指向 `.git` 擋下。
  - 絕對路徑、`..` 跑出 repo、內容含換行的連結擋下。
  - 連結指向子模組 `sm`、`sm/x` 擋下。
  - 自指連結 `self/d/f.txt`、`d/../d/f.txt` 通過。
- **行號與路徑其他輸入：結果符合預期。**
  - 行號 `0`、`4`、`3-1`、`0-2`、`1-` 擋下；負數 `-1` 不符格式，當成找不到的路徑。
  - 空檔 `:1` 擋下，CRLF 檔行數算對。
  - 檔名含空白與中文通過。
  - `D/f.txt` 的大小寫提示正確。
  - 空 repo 回 False，沒有崩潰。

### F1 路徑含 NUL 字元，擋下原因那支直接崩潰
severity: major
blocking: 是

引句:「real = os.path.realpath(wp)」

- 輸入：出處格寫 `` `x\0y` ``，也就是反引號內含 NUL。`_PLAN_SRC_TICK_RE` 是 ``[^`\n]+``，放行 NUL。
- 實際：`_plan_sources_problems` 和 `_plan_source_cell_ok` 都拋 `ValueError('lstat: embedded null character in path')`。路徑解析不到、又帶了 `why` 清單時，會進 `_plan_src_miss_reason`，裡面的 `os.path.realpath` 與 `os.path.exists` 遇 NUL 都會丟錯。`_plan_sources_problems` 每次都傳 `why=[]`，所以必經此路。
- 預期：回 False，不給原因。上一版用 `Path.is_file()`，它會吞掉 `ValueError`，所以這是這輪新改法帶進來的退化。
- 後果：規格閘、推送前、健檢遇到一份含 NUL 的出處格就整個崩，同上輪 F1 的失敗形狀。
- 同族：路徑含孤立 surrogate（`d/\ud800`）會拋 `UnicodeEncodeError`。這個難從正常讀檔流程進來，但同一處。
- 建議：在 `_plan_src_miss_reason` 前段先擋 `"\0" in path`，或把 `realpath` 與 `exists` 包進 `except (OSError, ValueError)`。

### F2 大小寫不同的 `.git` 仍被叫先提交
severity: minor
blocking: 否

引句:「if parts[0] == ".git":」

- 輸入：`` `.GIT/config` ``，在 macOS 這類大小寫不分的檔案系統上。
- 實際：回「工作目錄有、HEAD 還沒有——還沒提交，先提交再跑」。
- 預期：不講，同 `.git/config`。`.git` 判斷區分大小寫，落到後面 `realpath` 時，路徑字串仍是 `.GIT`，沒被當成 `.git` 底下。
- 這是上輪 F2「叫人做提交不了的事」的殘留，在 macOS 上照做會再看到同一句。

### F3 引用區塊與清單裡的 `<!--` 不當 HTML 區塊
severity: minor
blocking: 否

引句:「_PLAN_SRC_HTML_BLOCK_RE = re.compile(r" {0,3}<!--")」

- 輸入：`> <!-- a`、`> | x |`、`> -->`（前綴 `> `），或 `- <!-- a`、`  | x |`、`  -->`（前綴 `- `）。
- 實際：三行原樣留下，隱藏的表被當成看得見的表。
- 預期：照 CommonMark，容器內的 `<!--` 也開第 2 型區塊，渲染後是看不到的。
- 這對應程式註解寫的刻意偏離，所以只標 minor。要改的話，行首判斷可以先剝掉 `>` 與清單標記再比對。
- 縮排 4 格與 tab 開頭視為縮排程式碼、不當註解，與規格一致。

其餘 HTML 註解輸入都符合預期，包括 `<!-->`、`<!--->`、`<!---->`、行中多個 `<!--`、圍欄內外、圍欄沒閉合、CRLF。效能量測也沒問題：20 萬個沒閉合的 `<!--`、20 萬行都在 0.3 秒內跑完。

總結:最嚴重是路徑含 NUL 字元會讓擋下原因判斷崩潰（F1），會擋 1 條。
