severity: major

我在 `--shared` 臨時 clone(HEAD 5076190af)載入 `scripts/lumos`,把怪輸入餵給 `_plan_src_path_ok`、`_plan_sources_uncomment` 與 `_plan_sources_problems`。臨時目錄已刪。

### 第二輪邊界席 F1–F4 核對

- **F1 目錄符號連結:已修。**
  - `alias -> scripts` 時,`alias/lumos` 放行,`alias` 本身擋。
  - 連結指連結(`alias2/lumos`)放行。
  - 連結成環(`loop1`)擋。
  - 指向 repo 外(`../outside`)、絕對路徑(`/etc/passwd`)、`.git`、子模組擋。
  - 連結內容含換行擋。
  - 連結內容含 `..` 但正規化後仍在 repo 內(`scripts/../scripts/lumos`、`sub/../scripts`)放行。
  - 連結內容結尾是 `/` 放行。
- **F2 還沒提交的訊息:已修。**
  - 剛 `git add` 或剛建的檔、整個 repo 還沒有提交的情況,都會帶出「工作目錄有、HEAD 還沒有」的提示。
  - 小瑕疵見 F2。
- **F3 type 寫錯值:規格閘已修。**
  - 規格閘現在會印「type 是 X 不是 project,這次不查」。
  - `_spec_gate_push_sources` 與健檢遇到壞 frontmatter 仍然靜默略過,這是第二輪就記過的現況,沒有新惡化。
- **F4 每個路徑開 git:已修。**
  - 整棵樹用 `ls-tree -r` 只列一次並快取。
  - `:行號` 用 `cat-file` 讀 blob,同一支只讀一次。

其餘輸入結果:
- 路徑:大小寫錯、`.git/HEAD`、`scripts//lumos`、`scripts/./lumos`、結尾 `/`、反斜線、NUL、`C:/x` 都擋。NFD 輸入、檔名含空白、檔名含中文都放行。
- `:行號`:`:0`、`:-1`、超界、`:3-2`、空檔 `:1` 都擋,CRLF 檔行數正確,`:03` 放行。
- HTML 註解:行首縮排 0 到 3 空白是區塊、4 空白與 tab 不算區塊,`<!-->`、`<!--->`、`<!---->`、行中多個 `<!--`、跨行閉合、圍欄內、CRLF、段落遇空白行就停,結果都對。

### F1 `:行號` 寫超長數字會讓規格閘、推送前、健檢整個崩潰
severity: major
blocking: 是
引句:「    lo, hi = int(lo), int(hi or lo)」

| 輸入 | 實際 | 預期 |
|---|---|---|
| 出處格寫 `` `scripts/lumos:99999…(5000 位)` `` | `ValueError: Exceeds the limit (4300 digits)`,從 `_plan_sources_problems` 一路噴出去,沒有任何地方接 | 回 False,走「出處不合格」的擋下訊息 |
| `` `scripts/lumos:2-99999…` ``(範圍的後半超長) | 同上 | 同上 |

- 原因:`_PLAN_SRC_LINENO_RE` 的 `\d+` 不限位數,Python 3.11 起 `int()` 對超過 4300 位的字串直接丟 `ValueError`。
- 原因:這支函式只接 `OSError` 與 `TimeoutExpired`,新寫的 `_plan_src_path_ok` 沒有 try。
- 影響:規格閘、推送前重查、健檢 S22 三處共用這支,一格怪輸入就讓整次指令崩潰,不是擋下。
- 補充:舊版 `_validate_repo_ref` 裡的 `int(line)` 也不接 `ValueError`,所以這不是第三版才有,但前兩輪都沒抓到。
- 建議:數字長度超過一個上限(例如 9 位)就當超界回 False,或把 `int()` 包進 try。

### F2 工作目錄有、但補提交也沒用的路徑,也會被叫去「先提交再跑」
severity: minor
blocking: 否
引句:「            if wp.is_file() or wp.is_symlink():」

- 輸入:未進版控的符號連結 `abslink -> /etc/passwd`,或 `up -> ../../etc`,出處寫 `` `abslink` ``。
- 實際:提示說「工作目錄有、HEAD 還沒有——還沒提交,先提交再跑」。照做之後,`abslink` 與 `up` 仍然被擋,原因是指向 repo 外或絕對路徑。
- 預期:只在提交後確實會過時才講「先提交」。實作上可以只在未版控符號連結的目標也落在 repo 內時才提示。

總結:最嚴重是 `:行號` 寫超長數字會讓 `int()` 丟 `ValueError` 而崩潰,會擋 1 條(F1);另有 1 條 minor。
