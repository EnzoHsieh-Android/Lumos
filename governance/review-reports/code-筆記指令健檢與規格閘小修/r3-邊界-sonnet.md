severity: minor

三個發現都是 minor,沒有 blocking。我把修前(86aa8f40)與修後(342cf099)的 `scripts/lumos` 都載入實跑比對。web-notes 目前 HEAD 的 `scripts/lumos` 與 342cf099 相同,所以用的是同一份程式。

1. 「只要…就」「等到…才」的配對遇到逗號或括號就失效
severity: minor
   blocking: 否
   - 問題:`_ns_neg_cond_paired` 只在否定字眼所在的那一小段裡找「就/才/再/便」,而小段會被逗號和括號切斷(`_NS_NEG_SEG_CUT_RE`)。「只要…,就…」「只要…(…)就…」這兩種最常見的寫法,配對字落在下一段,否定句照樣被當現況句警告。
   - 輸入與結果(修前、修後都一樣):
     - `只要還沒登入,就不能下單` → `[('還沒', 2)]`
     - `只要尚未回應,就重試` → `[('尚未', 2)]`
     - `只要還沒登入(或逾時)就擋` → `[('還沒', 2)]`
     - 無逗號的 `只要還沒登入就不能下單` 修前被警告,修後 `[]`。這是修補真正守住的範圍。
   - 另一個反例:`等到還沒回來,才顯示` 修後仍是 `[('還沒', 2)]`。
   - 歸因:有證據的原有漏查。修補只收斂了無標點那一種寫法,沒有回歸。
   - 影響:這道檢查是 warn/off,不擋提交,所以只是誤報。
   - 引句:「return any(h.startswith(w) and any(c in tail for c in pair) for w, pair in _NS_NEG_COND_PAIRED.items())」

2. `_ref_cmdline_token` 對沒有副檔名的帶空白缺檔,修後會截成存在的前綴而判 ok
severity: minor
   blocking: 否
   - 輸入:`src/app notes`,其中 `src/app` 存在、`src/app notes` 不存在。
     - 修前回傳原字串,會報 missing。
     - 修後回傳 `src/app`,判 ok,缺檔被吞。
   - 原因:第二個詞 `notes` 沒有 `/`、沒有副檔名,就被當成指令參數。
   - 反方向:第二個詞若是限定名,例如指令 `scripts/lumos Env.run`(`run` 全小寫,`_drift_looks_like_ext` 判它像副檔名),會被當路徑整串核對。修前、修後都回傳原字串,結果是報 missing。這是 r2 G1 要修的「指令被誤報缺檔」的同一族,沒修到。
   - 已驗修補有效的輸入(修後都只核第一個詞):`scripts/lumos doctor`、`scripts/lumos v1.2`、`src/a.py 的某函式`、`scripts/lumos e.g.`、`scripts/lumos （含）`、`nonexist --flag`。
   - 已驗仍會整串核對的輸入:`src/app v2.py`、`src/app 中文.md`、`中文 路徑/缺.md`。
   - 歸因:前一半(`src/app notes` 變 ok)是有證據的修復回歸,取捨是作者有意的(docstring 寫明)。後一半(`Env.run`)是原有漏查。
   - 引句:「or (exists(words[0]) and not _ref_word_looks_like_path(words[1]))):」

3. `_dirty_non_bookkeeping` 沿用舊的解析,改名來源路徑的第三個字是空白時會被截掉前三字
severity: minor
   blocking: 否
   - 輸入:`git mv "ab c.py" "xy z.py"`。
   - porcelain `-z` 輸出裡,改名來源 `ab c.py` 沒有狀態前綴,卻被當成有前綴切掉前三字。
   - 實跑結果:列出 `c.py`、`xy z.py`、`old.c` 等,來源路徑印成 `c.py`。
   - 影響:只影響警告裡印出的路徑文字。簿記檔過濾用的是同一個被截斷的字串,理論上也可能漏濾。
   - 歸因:有證據的原有漏查。這段邏輯是從 `cmd_loop_fix_check` 原樣搬出來的,修前版本行為相同。
   - 引句:「paths = [x[3:] if len(x) > 3 and x[2] == " " else x for x in dirty]」

## 已驗無問題

- 兩個新增的修補行為正確:
  - 未追蹤檔:`untracked=True` 能列出未追蹤的新檔和目錄,例如 `新 檔.txt`、`newdir/`。
  - 中文與空白路徑:能正確處理,例如 `中文 檔.md`。
- `_is_git_worktree` 對 git 目錄回 True,對非 git 目錄(`/tmp`)回 False,對 `.git` 目錄內回 False。
- cochange:`--diff ""`、`--diff " "`、`--staged --diff ""` 三種都回 rc2,訊息正確。
- 標點清單(`_ns_neg_clause_break`)的實測結果:
  - 「時」後接 `.`、`'`、`＊` 現在算子句記號,誤報消除。
  - 「前/後」並列詞仍會被警告。
  - 全形冒號、行尾、情態詞都沒退步。
- 同秒 ts 取先列(本機審查帳):`_spec_gate_pick` 先去重再嚴格比,tie 時 `k > bk` 取先列,ts 讀不懂的記為 -inf、不會崩。
- 從程式碼確認(非實跑):
  - 新分支首推、起點不存在、三點範圍沒有共同祖先時,`_range_base` 回 None,`_spec_gate_status_at` 回 None,照「不是 done」的嚴格路徑走。
  - `_excluded_line` 的前置冒號計數與 `_EXCLUDED_RE` 要求至少兩個冒號一致,不會漏判。

## 未驗範圍

- 沒有實跑 `summary-add` / `summary-line` 在 isgit 為 None(git 逾時)時的完整流程,只靠程式閱讀。
- 沒有實跑 doctor S14 的「治理帳讀不到」分支。
- 沒有跑 `--nth` 0、負數、超界,它們不在這輪修補的 hunk 內。

## 三問

- 原問題的修復效果:
  - 「前/後」之外的標點、無標點的「只要…就」、指令加子命令、cochange 空 `--diff`,修前紅、修後綠,有上面的輸入可對照。
  - 帶逗號的「只要…,就」沒修到,見第 1 條。
- 修補處的正常、錯誤與相鄰路徑:只有第 2 條有一個小的相鄰回歸(存在前綴加無副檔名的缺檔詞)。
- 新發現同一案例在修前與修後:
  - 第 1 條:修前、修後相同。
  - 第 2 條:`src/app notes` 修前報 missing、修後判 ok;`Env.run` 修前、修後相同。
  - 第 3 條:修前、修後相同。

最嚴重 severity:minor;blocking 共 0 條。

臨時目錄 `/tmp/lumos-seat-work/code-筆記指令健檢與規格閘小修/邊界-sonnet` 已刪。
