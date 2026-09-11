severity: minor

## 問一:分層與依賴方向

對齊。這輪新增的 `_heredoc_start`、`_drop_comment`、`_SEARCH_VALUE_ABBR`、`_SHELLS`/`_SHELL_C_RE`、`_search_segments` 的巢狀遞迴、`_committable` 的 try/except,全部留在 recount.py 原本那層「私有模組級小函式」——只呼叫同檔已有的 `_strip_quoted`(既有工具函式)或標準庫(`re`/`subprocess`),沒有新的跨層呼叫(例如伸手進 `check-graph-sync.py` 或 `scripts/lumos` 拿新東西)。這跟本檔既有的兩個「借用既有機制、不自造第二套」的錨點一致:`_load_hook_helpers()`(`governance/eval/lens-utilization/recount.py:34`,docstring 明寫「不自造第二套」)與 `repo_paths`/`existed` 的 `subprocess.run` 包 `try/except`、`timeout=10` 慣例(`governance/eval/lens-utilization/recount.py:122`、`:842`)。`_committable` 這次補的 try/except 正是套用同一個慣例到原本沒套的地方,誰呼叫誰的方向沒變。

## 問二:命名與錯誤處理

大致對齊,一條不對齊(命名/回傳形狀):

G1
severity: minor
blocking: 否
引句:「def _heredoc_start(line: str):」
file: `governance/eval/lens-utilization/recount.py:879`
本檔既有慣例是「回 None 或某值」的函式一律標 `-> X | None`(例如 `norm_note`、`vault_slug`,分別在 `governance/eval/lens-utilization/recount.py:139`、`:134`),同一輪新增、緊鄰在旁的 `_drop_comment` 也照做標了 `-> str`(`recount.py:889`)。`_heredoc_start` 回傳形狀同樣是「`(結束標記, bool)` 或 `None`」,卻沒補型別提示,是這輪唯一一處跟鄰居寫法不一致的地方。

錯誤處理本身對齊:`_committable` 的兩段 `try/except Exception` 搭 `timeout=10`,跟 `repo_paths`(`recount.py:124`)、`existed`(`recount.py:841`)已有的「git 叫不動就當非阻斷訊號」寫法同款,只是把 fallback 值換成布林 True/False(函式本身是判斷式,形狀合理)。

## 問三:第二種做法

對齊,沒看到引入第二種做法。

- heredoc 判斷:這輪把獨立的 `_HEREDOC_START_RE` 砍掉,改用既有 `HEREDOC_RE` 加兩個捕捉群組,`_heredoc_start` docstring 自己點名「沿用本檔的 HEREDOC_RE,不另寫一份(r2 架構 E2)」——引句:「沿用本檔的 HEREDOC_RE,不另寫一份」,file: `governance/eval/lens-utilization/recount.py:880`。這是消掉既有的重複,不是新增重複。
- 剝殼層註解(`_drop_comment`)與認巢狀 `bash -c`(`_SHELLS`/`_SHELL_C_RE`):我在 `scripts/hooks/claude/check-graph-sync.py`(`_segment_command`/`_tokens_of`,`scripts/hooks/claude/check-graph-sync.py:290-299`)、`scripts/lumos` 全文、以及 recount.py 其餘段落都沒找到既有的「剝殼層註解」或「認 `-c` 直譯字串」寫法(全域 grep 只命中這輪新加的那幾行),所以這兩個是第一次出現,不是另外寫一套已存在的東西。
- 巢狀 shell 用 `_search_segments` 遞迴呼叫自己,跟 classify_bash 既有的「解掉 `python3 lumos`直譯包裝」(`recount.py:199`,skip-index 就地解)是不同問題(後者是同一段內跳過一個 token,前者要把整個引號字串當新指令重切),遞迴屬必要手法,不是重寫一套已有的「跳過包裝」邏輯。
- 新測試 `t_lens_recount_search_r2`/`t_lens_recount_search_nested_shell` 沿用同檔既有的 `m.subprocess.run = boom` / `real_run` / `finally` 還原慣例(對照 `scripts/test_lumos.py:36556-36567`,同一支測試檔裡緊鄰的既有寫法),沒有另立一套 mock 手法。

不對齊共 1 條,其中 major 0 條,全份最高嚴重度是 minor。
