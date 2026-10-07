severity: clean

我看到的:hook 附的固定席是 `測試假綠形態.md` 的 ★INVARIANT★(還原翻紅釘必須配「現場成立」前置斷言)。這輪修補只動兩處:`scripts/test_lumos.py` 前置斷言造現場的那一行,以及同節點筆記的一句說明。

**1. 分層與依賴方向:對齊。**
- 修補沒有新增依賴或跨層呼叫。
- 這一行只用測試函式內本來就 import 的 `os` 和 `_sp`,跟鄰居一樣是在測試函式內直接造子程序環境。
- 對照:`scripts/test_lumos.py:516`(修補行),`scripts/test_lumos.py:9572`、`scripts/test_lumos.py:8933`(同檔把 `os.environ` 複製出來改成子程序環境)。
- 唯一進入點設 `PYTHON_COLORS` 的寫法跟 `HOME`、`LUMOS_HOME` 的隔離放在同一處,沒有另開位置。

**2. 命名與錯誤處理:對齊。**
- 前置斷言的標記、位置和寫法跟同檔其他守衛一樣:先造現場,再用 `check("…★前置★ 現場成立…", 條件, 失敗時的證據)` 判定。
- 對照:`scripts/test_lumos.py:590`、`scripts/test_lumos.py:635`、`scripts/test_lumos.py:9326`。
- 造現場的環境是 `dict(bare, FORCE_COLOR="3")`,跟同檔 `dict(os.environ, KEY=值)` 是同一種寫法(`scripts/test_lumos.py:614`、`scripts/test_lumos.py:670`、`scripts/test_lumos.py:8460`)。
- 排除兩個變數時用 dict 推導式,同檔排除單一變數時是 `e.pop(...)`(`scripts/test_lumos.py:9572`)。這是兩個以上變數的取捨,仍然是「複製 `os.environ` 再改」,算不上另一種做法,也不影響結果。
- 失敗時也跟鄰居一樣,把 `repr(r0.stderr[-120:])` 放進證據欄,沒有吞例外。

**3. 第二種做法:沒有。**
- 我查了 `scripts/test_lumos.py` 全檔,對 `NO_COLOR`、`PYTHON_COLORS` 的處理只出現在:
  - 這支守衛測試。
  - `main()` 的設定(snapshot patch 第 83、84 行)。
- 其他測試沒有各自再加一套顏色中和,筆記也同步寫成「個別測試不再自帶 NO_COLOR」。
- 修補只把前置斷言的環境排除範圍多放一個 `NO_COLOR`,沒有新機制。
- 最後一條斷言(`r` 那次)繼承主進程已中和的環境,跟「前置斷言用自己造的環境、其餘斷言吃進入點設定」的分工一致。

沒有不對齊的項目,查證命令是 `git show e58b16c9:scripts/test_lumos.py` 後對 `os.environ.items()`、`env=dict(`、`現場成立`、`NO_COLOR`、`PYTHON_COLORS` 逐條 grep。

不對齊共 0 條,其中重大 0 條
總結: 這次修補只是把造現場的環境多排除一個變數,寫法和同檔其他守衛一致,沒有另起一套做法。
