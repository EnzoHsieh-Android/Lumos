severity: minor

## Finding COR8-01
severity: minor
blocking: 否
引句:「sample = "\u202e\ufeff\U000e0001\u3000\u00a0x"」
file: `scripts/test_lumos.py:43751`
- 具體輸入:測試拿這個樣本比對 `_SPECIAL_CATS` 與 lumos 的 `_kill_esc` 是否一致。樣本只含 Cf(U+202E、U+FEFF、U+E0001)和 Zs(U+3000、U+00A0)。Zl(U+2028)、Zp(U+2029)、Cs(孤立代理)都沒有。
- 走到哪一段:`render_md` 的 `visible()`(`governance/eval/ablation_lumos_first.py:396`)用 `_SPECIAL_CATS`(同檔第 387 行)。
- 壞在哪:`ablation_lumos_first.py` 的註解寫「改由測試核對兩邊寫法一致」,實際上測試只核對到 Cc 與 Cf。把 `_SPECIAL_CATS` 改成只剩 `("Cc","Cf")` 後,這個樣本的比對照樣為 True。同一個改壞版本下,輸入 `a\u2028b\u2029c\ud800` 的報表標題行在 `a` 後面就被 U+2028 截斷。孤立代理沒轉成 `\ud800`,會留到 `_atomic_write_text` 的 `encode("utf-8")` 才炸。整個 `render_md` 測試群也沒有 `u2028`、`u2029`、`ud800` 的案例。
- 重現命令與輸出:我在取出的修後版 `ablation_lumos_first.py` 上,把 `_SPECIAL_CATS` 換成 `frozenset(("Cc","Cf"))`,再用 `render_md` 跑樣本與 `a\u2028b\u2029c\ud800`。
  - 修後原版:樣本比對 True;U+2028/U+2029/代理輸出 `a\\u2028b\\u2029c\\ud800`(repr 顯示的雙反斜線)。
  - 改壞版:樣本比對仍 True;標題行輸出 `# 修法 A ablation 對照(記錄日期 a`。
- 歸因:有證據的修復回歸。修前 67b1dea2 用 `isprintable()` 加 `⟦U+XXXX⟧`,U+2028、U+2029 與代理本來都會被轉成可見序列(雖然沒有測試)。修後類別縮成五類,測試反而沒涵蓋其中三類。我只在修後版做了改壞實驗,所以「測試沒鎖住」有證據,「修前也沒測」靠讀碼判斷。

## Finding COR8-02
severity: minor
blocking: 否
引句:「return f"\\u{ord(ch):04x}" if unicodedata.category(ch) in _SPECIAL_CATS else ch」
file: `governance/eval/ablation_lumos_first.py:396`
- 具體輸入:meta 的 `date` 或 `claude_version` 帶真的 ESC(U+001B),對照 meta 帶字面文字 `\u001b`。
- 走到哪一段:`render_md` → `text()` → `visible()`,之後再做 Markdown 跳脫。
- 壞在哪:兩者產出的報表標題行位元組完全一樣,都是 `\\u001b`。修前 67b1dea2 的真 ESC 是 `⟦U+001B⟧`,字面文字是 `\\u001b`,看得出差別。
  - 這是 `ablation-lumos-first.md` 的 WHY 行(代價欄)明寫接受的取捨,不算沒交代。
  - 同一篇的 r5 PITFALL 仍列「真 ESC 與字面 `\x1b` 呈現成同一個樣子」為已修缺陷,只是被修成不同的 `\x1b` 寫法。
  - 測試 `真控制字元與字面反斜線文字呈現不同` 取的字面樣本是 `\x1b`,不是新寫法 `\u001b`,所以現在不可能翻紅。測試名稱與上方註解宣稱的保證,實際上只對 `\x` 形式成立。
  - 若維持此取捨,測試就該改成明講「`\u` 形式刻意相同」,不要保留一個看起來在守區別的斷言。
- 重現命令與輸出:
  - 修後 e5ce8675:真 ESC 與字面 `\u001b` 的標題行相同(都是 `...記錄日期 \\u001b;...`)。
  - 修前 67b1dea2:真 ESC 是 `⟦U+001B⟧`,字面是 `\\u001b`。
- 歸因:有證據的修復回歸,且筆記與測試都已部分承認。

## 固定席逐條判定
- `Systems/codex-harness.md`(家):新增的 PITFALL/WHY 與程式現況一致。三處共用 `_open_char_device`、`_open_history`,暫存檔一建立就用沿用的權限,歷史檔只收單一名字的普通檔與字元裝置。我用 FIFO(有無讀者)、符號連結、硬連結、新歷史檔、100 次撞名、umask 0o277 逐一走過,結果都符合筆記,fd 沒外洩。不影響其合約。
- `Systems/測試假綠形態.md` ★INVARIANT★(前置斷言證明現場成立):這次新增的測試多半帶了前置斷言,例如「現場成立:真的建了暫存檔」、「現場成立:跑的期間換成有人讀的 FIFO」。COR8-01 的比對斷言沒有前置斷言證明樣本涵蓋三個類別,屬同一類假綠。該 INVARIANT 的綁定測試是 slim 反安裝那兩支,沒被改動,所以不算破壞合約。
- `Systems/lumos-cli-lifecycle.md` ★INVARIANT★(re-inject 範圍):只改了終端 PITFALL 的說明文字,沒動 re-inject。`t_confirm_tty_no_ctty_session_survives` 在 e5ce8675 的 `scripts/test_lumos.py` 第 10255 行存在,「下方 PITFALL」指的是第 156 行那條。不影響。
- `Systems/design-loop.md`、`bound-tests-gate.md`、`canary-audit.md`、`lumos-cli-read.md`、`autonomous-iteration-loop.md`:合約都在處置閘、綁定測試、canary、search 排除與自主迭代迴圈,這份審材沒動到。不影響。
- 其餘「超出上限只列名」的節點:沒讀,未判。
- 角色卡:
  - be-api-compat:報表的控制字元寫法從 `⟦U+XXXX⟧` 改成 `\uXXXX`。我搜了 scripts、governance/eval、governance/autonomous_loop 與圖譜筆記,沒有任何程式讀 `⟦`。`--history` 追加的 JSON 格式沒變。但新增兩種舊版接受的輸入現在會被擋:硬連結歷史檔(開跑前就被擋,rc 2),以及 FIFO、socket 型別的歷史檔(舊版開檔後不檢查型別)。這是刻意的行為變更,不是缺陷。
  - be-authz:沒有端點。檔案權限面上,只有「自己擁有且 nlink==1」的檔才沿用權限,暫存檔一建立就不比原檔寬,硬連結一律照 umask。umask 0o277 下 `keep_mode` 先被收窄、再用 `fchmod` 補回 0640,結果正確。

## 修補三問
- ① 原問題的修復效果:
  - 暫存檔權限:我用 umask 0o277 實跑,最終檔 0640、內容正確。「建立時不比 0600 寬」靠讀碼成立(`os.open(..., keep_mode)`,被 umask 收窄只會更嚴),沒有另外在修前做反向實驗。
  - 字元裝置、歷史檔:我實測 `_open_char_device` 與 `_open_history` 對 FIFO 無讀者回 ENXIO(errno 6),有讀者回 EINVAL(22,fd 已關),對符號連結回 62(macOS 的 ELOOP),三者 fd 都沒外洩。`_output_target_problem` 對硬連結歷史檔回報問題,對 `/dev/null` 回 None。
  - 100 次上限:撞名時拋 `FileExistsError`,不空轉。
  - 報表類別:兩個改動對應的測試與我自己的樣本實測一致。
- ② 修補處的正常、錯誤與相鄰呼叫路徑:
  - 新檔照 umask、既有自有檔沿用權限、取代模式的 FIFO 與符號連結仍換成普通檔,都符合讀碼與實測。
  - `_guard_hang` 嵌套時內層還回外層的處理器與鬧鐘;prev 剩不到 1 秒時被補成 1 秒,最多延長 1 秒,可接受。
  - 例外時 `alarm(0)` 與處理器都會還原。
  - `_Hung` 不是 `OSError`,不會被受測碼的 `except OSError` 吞掉。
  - 「借鬧鐘後執行器逾時還在」那條斷言在執行器沒設鬧鐘時恒為真,只在有鬧鐘時才有意義。我只讀碼確認執行器的逾時(`run_with_timeout`)用 `signal.alarm`,沒有另外量測它在子集模式下是否總有鬧鐘。
- ③ 新發現同一案例的修前、修後:
  - COR8-01:修前 67b1dea2 對 U+2028、U+2029、孤立代理轉成 `⟦U+XXXX⟧`;修後轉成 `\uXXXX`,測試對這三類無覆蓋。
  - COR8-02:修前真 ESC 與字面 `\u001b` 不同,修後完全相同。

## 未驗範圍
- 沒跑 `test_lumos.py` 任何測試(目錄有全套在跑),也沒做 pty、新 session 子程序、大量輸出的實測。這幾項只靠讀碼判斷。
- Linux 與 root 沒驗;只在 macOS、非 root 下做過實驗。
- 沒驗 `_guard_hang` 在 prev 鬧鐘剩餘小於 1 秒的實際計時。
- 沒驗 `/dev/tty` 試開在有控制終端時的副作用,以及特殊字元裝置(序列埠、音訊)開了再關是否有硬體副作用。
- `_open_char_device` 的 fstat 或 `set_blocking` 失敗路徑:讀碼上 `except BaseException` 會先 `os.close(fd)` 再重拋,沒用注入實測。
- 「超出上限只列名」的固定席節點沒讀。
- 實驗目錄 `/tmp/lumos-seat-work/code-probe-postreview-dispatch-ledger/正確性8-sonnet/` 已刪除。

總結:最高嚴重度 minor
