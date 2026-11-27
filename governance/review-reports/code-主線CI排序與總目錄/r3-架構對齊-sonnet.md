severity: clean

我對照了兩處既有寫法，這份修正沒有引入第二種做法，也沒有跨層直呼。

**1. 測試寫法（`scripts/test_lumos.py`）**
- 這次新增的情境放在 `t_choice_cov_src_pkgs_edges` 同一個函式裡。
  - 它用 `tmp` 底下 `mkdir(parents=True, exist_ok=True)` 加 `write_text` 建樹，跟同函式前面 `jroot` 那段是同一種寫法：`scripts/test_lumos.py:150540` 一帶、`j/src` 的建法。
  - 它沿用函式開頭 `tempfile.mkdtemp` 配外層 `try/finally` 的清理，沒另開暫存根。
- 手寫還原用 `old = m._CHOICE_COV_SRC_MAX` 存值、`try/finally` 還原，跟同函式內三處完全同形。
  - 三處分別是看滿上限的檢查、總檔數上限的檢查、`_cut_at` 輔助函式（`scripts/test_lumos.py:150510` 到 `150556` 一帶）。
- 還原 `_os_mod.walk = real_walk` 也跟 `_cut_at` 的 `finally` 一樣，並重用同函式已有的 `_rev_walk` 和 `real_walk`，沒有另造反轉工具。
- 輸出用 `contextlib.redirect_stderr(io.StringIO())`，也是同函式既有做法。
- `_cut_at` 是寫死掃 `tmp` 的區域輔助函式，新情境掃的是 `froot`，所以展開寫是合理的，不算重複造輪子。
- 新情境直接拿絕對斷言（`{"fa"}`）加順序反轉對照，沒有另立斷言風格。

**2. 圖譜筆記（`docs/lumos-toolchain-knowledge/Systems/規格閘.md`）**
- 這行 PITFALL 仍是一行一件事，有出處、根因、修法、test 四個必有的格子，順序不變。
- 修法欄只在尾端加了一段「;資料夾層與檔案層排序各造一個碰得到的情境(代碼審 r2 正確性)」。附註括號的寫法跟前一段「(代碼審 r1 正確性)」一致，也跟同篇其他 PITFALL 的「(r2 改:…)」附註一致。
- 長度不是問題：同篇現有的 PITFALL 與 WHY 行有 1200 到 1300 字元以上，修改後這行沒有超出同篇慣例，不需要拆行。拆行反而會違反「一行一類」的規則。

**可選的小建議（不列為 finding）**
- 新情境沒有像上面 `★前置★` 那樣獨立證明現場成立，也就是證明 A.kt 與 B.kt 在同資料夾且上限 1 時確實只收到一個。
- 它以 `f_fwd == {"fa"}` 的精確斷言兼任，風險很小。這是測試品質問題，不是架構對齊問題。
