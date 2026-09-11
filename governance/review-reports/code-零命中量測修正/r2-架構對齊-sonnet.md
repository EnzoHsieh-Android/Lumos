severity: major

**問一(分層與依賴方向):對齊。**
新函式的呼叫關係都是單向、由上層搜尋分析呼叫下層字串前處理,跟本檔既有分層一致。`_shell_lines`(`governance/eval/lens-utilization/recount.py:879`)只被 `_search_segments`(`governance/eval/lens-utilization/recount.py:905`)與 `_search_events`(`governance/eval/lens-utilization/recount.py:992`)呼叫,不越層回頭被 `classify_bash` 或更上層用到,符合它自己 docstring 講的「`_search_segments` 與 `_search_events` 共用同一份前處理」。`_search_counts`(`governance/eval/lens-utilization/recount.py:930`)被改成唯一計數來源,`_search_verdict`(`recount.py:964`)與 `_search_events`(`recount.py:975`)都改成從它讀,而不是像修前那樣兩套各自解析——這正好是把原本違反單一數據源的舊結構收斂回鄰居一致的分層(下層 parser→上層判定),方向正確。`_committable`(`recount.py:1181`)只被同層的 `write_archive`(`recount.py:1200`)呼叫,沒有被更外層(如 `main`)直接繞過去用,層次合理。

**問二(命名與錯誤處理):不對齊 1 條。**
命名上 `_committable` 跟本檔既有的 `_under_repo`、`_claude_in_repo` 這種「不加 `is_` 前綴的形容詞式私有布林函式」同一掛,`write_archive` 回傳型別從 `tuple[Path, Path]` 改成 `tuple[Path, Path | None]` 也延續本檔既有大量 `X | None` 的寫法(`vault_slug`、`norm_note`、`_codex_meta` 等)。但錯誤處理跟鄰居不一致:

E1
severity: minor
blocking: 否
引句:「r = subprocess.run(["git", "-C", str(d), "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)」
file: `governance/eval/lens-utilization/recount.py:1186`
本檔既有兩處呼叫 git 子行程(`repo_paths` `recount.py:122` 與讀 git log 算誕生時間 `recount.py:842`)都包 `try/except Exception` 且帶 `timeout`,失敗就悄悄退回預設值;`_committable` 的兩次 `subprocess.run` 呼叫都沒有 try/except 也沒有 timeout,git 不存在或掛住會讓 `write_archive`(進而 `main`)整支噴掉,跟鄰居「git 失敗當非阻斷性訊號處理」的慣例不一樣。

**問三(第二種做法):不對齊 1 條,另有一處刻意避開第二種做法值得記一筆。**
`_safe_tokens` 用新增的 `flat` 參數(`recount.py:67`)讓搜尋判斷共用同一份切詞,而不是另開一條切詞路徑,docstring 也明講這是為了不再另寫第二套——這條是對齊的,不算違規。但 heredoc 起始的偵測確實開了第二套:

E2
severity: major
blocking: 是
引句:「_HEREDOC_START_RE = re.compile(r"(?<!<)<<(?!<)(-?)\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?")」
file: `governance/eval/lens-utilization/recount.py:53`(既有 `HEREDOC_RE = re.compile(r"(?<!<)<<(?!<)-?\s*['\"]?\w+")`)
本檔已有 `HEREDOC_RE` 判斷 heredoc 起始(`classify_bash` 用它整段 `.search(cmd)` 判斷要不要走啟發式路徑),r2 卻在 `_shell_lines` 又寫了一份幾乎逐字重複的 `_HEREDOC_START_RE`,只差在加了兩個捕捉群組(dash 旗標、分隔詞)。這兩個捕捉群組原本可以直接加回 `HEREDOC_RE` 本身(布林 `.search()` 用法不受影響),卻另開一個同名字義的常數分開維護,正是題目點名的「heredoc 判斷另寫一份而本檔已有 HEREDOC_RE」這種第二種做法。

不對齊共 2 條,其中 major 1 條,全份最高嚴重度是 major。
