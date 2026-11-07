severity: clean

第六輪邊界席 F1 已修好。我把 patch 套到 HEAD 66d50accd 的臨時 clone 上實跑,沒有找到新的 major 或 blocker。

**F1 核對(子目錄專案裡,兄弟目錄的刪除檔被點名)**
- 輸入:repo 有 `sub/`(專案根,含 `docs/x-knowledge`)和 `other/`,在 `other/` 刪了 `other/b.py`,`CLAUDE_PROJECT_DIR=repo/sub`。
- 實際:`_git_status_entries` 沒有回傳 `other/b.py`。
- 預期:`other/b.py` 不在專案底下,不該被點名,與實際一致。
- 其他條目的結果,也符合預期:
  - 改名跨界(`other/d.py` 改成 `sub/d2.py`、`sub/c.py` 改成 `other/c2.py`)兩種方向都有留下專案內那一端。
  - 專案內刪掉的無副檔名腳本 `sub/tool` 有被點名。
  - `other/new.py` 沒被點名。
- 專案根路徑換三種寫法,結果都一樣:`/tmp/...`、`/private/tmp/...`、含 `..` 的路徑,另外給符號連結的專案根也一樣。專案根在 repo 根時,全部條目都留下。

**端到端實跑(`check-graph-sync.py` 收工鉤子)**
- 輸入:檔名含反引號、換行、ESC 控制字元、反斜線、250 字元長名,放在 `sub/d/` 底下,另有 `sub/` 內的改名、刪除與新增。
- 實際:鉤子回 `decision: block`,列出 9 個檔,反引號和換行檔名都被消毒成單行。`other/` 的檔一個都沒進清單。
- 預期:只列專案內的檔,與實際一致。
- 這輪沒動標記檔名、訊號、擋停 1500 字邊界、stdin 與回合起點檔,所以這幾項沒有新差異可審。

**shell 掛鉤的 PATH 過濾**
- 空 PATH 會退回 `/usr/bin:/bin`,純相對項也會退回同一個值。PATH 只剩絕對項時照舊。
- 取到相對路徑 python 的守衛是在 `_lumos_any_python_find` 之後判斷,而 `PATH` 先濾過,所以掛鉤裡走不到這條。

**沒標成 finding 的兩項**
- bash 會展開 PATH 裡的 `~/x`,但 path-clean 當成相對項丟掉。固定位置清單已涵蓋 `$HOME/.local/bin`,實際影響很小,所以沒標。
- 專案根的大小寫與 git 回傳的根不同(例如 `/TMP/.../SUB`)時,`_rel_in_project` 會讓清單變空,等於靜默放行。Claude Code 不會送這種路徑,所以沒標。

臨時目錄已刪。

總結:最嚴重是 clean,會擋 0 條。
