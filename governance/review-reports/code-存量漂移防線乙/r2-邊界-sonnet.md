severity: blocker

## F1 深巢狀 Python 檔讓 ast.parse 丟出未接的 MemoryError,整支 drift scan/check 當掉
severity: blocker
blocking: 是 — 一支語法合法但巢狀很深的 .py 檔(或惡意構造的檔)就能讓 `lumos drift scan`、`lumos drift check`(推送閘)整支炸掉,不是優雅降級成「判不了」,而是印出未接例外的 traceback、rc1。
引句:「except (SyntaxError, ValueError):」

1. `_drift_py_names`(scripts/lumos:25827)用 `ast.parse(txt)` 解析程式檔,只接住 `(SyntaxError, ValueError)`(scripts/lumos:25834)就回 None 走正則備援。
2. 但 CPython 的 PEG parser 對「巢狀很深、沒有明確括號深度上限」的寫法(例如一長串一元運算子 `-` 疊起來)不是丟 SyntaxError,而是丟 `MemoryError: Parser stack overflowed - Python source too complex to parse`,不在被接住的例外清單裡。
3. `_defines`(scripts/lumos:25933→25940)在字面比對命中後才呼叫 `_drift_py_names(txt)`,所以只要條件標記指到的那支檔「文字裡出現過那個名字」(哪怕只是註解),就會觸發解析、進而觸發這個例外。
4. 重現(在自己 mktemp 的臨時 repo,git -C):建一支 `src/gen.py`,內容是 `# cmd_new appears here as a comment token\n` + `'-'*200000` + `1\n`;圖譜裡一篇筆記寫 `REVISIT:[when-symbol:src/gen.py::cmd_new][by:2099-12-31] test`;提交後跑 `python3 scripts/lumos drift scan`(cwd=臨時 repo),實測:
   ```
   rc= 1
   File "…/scripts/lumos", line 25940, in _defines
       self._py[p] = _drift_py_names(txt)
   File "…/scripts/lumos", line 25833, in _drift_py_names
       tree = _ast.parse(txt)
   MemoryError: Parser stack overflowed - Python source too complex to parse
   ```
   同一條路徑也會讓 `drift check`(推送閘)當掉,不是「擋下」或「警告」,是直接把整個推送檢查程序炸掉。
5. NUL 位元組與 Python 2 語法都有驗過:`_drift_py_names` 對 `\x00` 觸發的是 `ValueError`(已接住,回 None、退回正則)、對 `print "x"` 這種 py2 語法觸發 `SyntaxError`(已接住),這兩種都正常退回正則備援,已看,無 finding;只有 MemoryError 這條路沒接住。

## F2 帶 BOM 的 #! 語料在「不帶路徑」的 symbol/test 搜尋裡被靜默排除,永遠判假且沒有任何診斷
severity: major
blocking: 是 — 一支合法、有 `#!` 的沒副檔名腳本,只因開頭多了 UTF-8 BOM,就會從「不帶路徑」的語料集合裡整支消失;沒帶路徑的 `[when-symbol:名稱]` 條件因此永遠判 False,而且 scan 的「回頭條件的問題」清單完全不會列出它(不算判不了、不算寫錯),使用者拿不到任何線索。
引句:「_nodehome_code_kind(p) == "ext" or self._text[p].startswith("#!"))]」

1. `corpus(test)`(scripts/lumos:25923–25931)判斷一支沒副檔名的檔算不算「程式檔語料」,靠 `self._text[p].startswith("#!")`(scripts/lumos:25930)。
2. 但讀檔內容時(scripts/lumos:25909 與 25920)一律用 `decode("utf-8", errors="replace")`,不是 `utf-8-sig`,所以檔案開頭若帶 UTF-8 BOM(`EF BB BF`),解碼後字串會多一個 `﻿` 字元,`"﻿#!/usr/bin/env python3...".startswith("#!")` 恆為 False——這支檔就被 `corpus(False)`/`corpus(True)` 整批排除,即使它明明是合法的 shebang 腳本。
3. 重現(in-proc,無需 subprocess):建一支 `scripts/runner`(無副檔名),內容是 `b'\xef\xbb\xbf' + b'#!/usr/bin/env python3\ndef cmd_bomtest():\n    pass\n'`,提交後:
   ```python
   tr = m._drift_probe_tree(str(root), head)
   tr.corpus(False)                 # -> []  (該檔完全不在語料裡)
   m._drift_probe_one(tr, tenv, 'symbol', 'cmd_bomtest')            # -> False(實際存在!)
   m._drift_probe_one(tr, tenv, 'symbol', 'scripts/runner::cmd_bomtest')  # -> True(帶路徑就對)
   ```
   同一支函式,不帶路徑判 False、帶路徑判 True——純粹因為 BOM 把它擠出了不帶路徑的語料集合。
4. 影響:`REVISIT:[when-symbol:cmd_bomtest][by:…]` 這種不帶路徑的條件式回頭條件,若定義只存在於一支帶 BOM 的無副檔名腳本裡,會永遠評估成「還沒成立」,`drift scan`/`check` 都不會提醒,也不會被列進「回頭條件的問題」(因為它不是語法錯、也不是判不了,只是 `_drift_probe_line` 拿到確定的 False)。跟設計文件特別為 `Config::load` 這種死語法做的 `_drift_probe_path_warn` 提醒比,這一種「死條件」完全沒有對應的偵測。
5. CRLF 本身不影響(`"﻿"` 才是問題根源,行尾 `\r` 不影響 `startswith("#!")`),已看,無 finding。

## F3 when-file/when-symbol/when-test 的「不准 .. 段」guard 可被反斜線繞過,正規化後產出真正的 `../…` 值卻不報錯
severity: major
blocking: 是 — 條件標記寫 `..\x.py`(反斜線)能完整通過語法驗證(`_probe_value_err`)、通過第一層筆記形狀擋(`lumos note-shape`)、通過 `drift check`/`drift scan`,不報任何錯誤或警告,但正規化後的值是真正帶 `..` 開頭的路徑,跟程式碼裡「不准 .. 段」這句文件字面矛盾。
引句:「conds.append((k, val if err else _probe_norm_value(k, val)))」

1. `_probe_parse`(scripts/lumos:25762 起)先對**原始**值 `val` 呼叫 `_probe_value_err`(scripts/lumos:25715),只有沒有錯誤時才對它呼叫 `_probe_norm_value` 做正規化(scripts/lumos:25787,這行是本次差異新加的)。
2. `_probe_value_err`→`_probe_bad_path`(scripts/lumos:25746)`return (not p) or p.startswith("/") or ".." in p.split("/")` 只用 `/` 切詞判斷 `..`;反斜線寫的 `..\x.py` 整串只有一個 token(`"..\\x.py"`),不等於字面 `".."`,不會被擋。
3. `_probe_norm_value`(scripts/lumos:25734)接著把值丟進 `_posix_norm`(反斜線轉斜線、collapse `./`、`..`),`..\x.py` → `../x.py`——這時已經跳過驗證、直接寫進 `conds` 裡。
4. In-proc 重現:
   ```python
   pr = m._probe_parse(r'[when-file:..\secret.py][by:2099-12-31] test')
   pr['errs']   # -> []  (完全沒有錯誤!)
   pr['conds']  # -> [('file', '../secret.py')]
   ```
5. 端到端重現(自己 mktemp 的 git repo):圖譜筆記新寫一行 `REVISIT:[when-file:..\secret.py][by:2099-12-31] backslash dotdot bypass`,提交後跑 `lumos note-shape --diff <base>..HEAD`:
   ```
   note-shape rc= 0
   ```
   完全沒有違規訊息——第一層(新寫回頭條件的守門)乾淨放行了一個照理該被擋的「不准 .. 段」寫法。
6. 影響範圍:評估面(`tree.one("file", v)` 等)只是做 `v in self.files` 集合比對,git 追蹤的路徑不可能帶 `..` 段,所以這個值本身永遠評不到真檔案、不會真的讀到 repo 外的內容,不是資安層級的路徑穿越;但它是一個「看起來合法、寫錯了也不會被任何一層擋下或標成問題、永遠死掉」的條件——跟本計劃刻意為 `Config::load` 這種死語法做偵測(`_drift_probe_path_warn`)的用意矛盾,而且直接違反程式自己印出來的錯誤訊息("不准 .. 段")所承諾的保證。

## F4 `_drift_probe_path_warn` 的「像不像檔案路徑」啟發式對沒副檔名的慣例檔名(Makefile 等)誤判,對帶點的假路徑漏判
severity: minor
blocking: 否 — 不影響評估結果(兩種情況條件都正確地永遠評估成 False),只影響 scan「回頭條件的問題」清單的診斷品質,不會造成錯誤放行或漏擋。
引句:「if path in tree.files or "/" in path or "." in path:」

1. `_drift_probe_path_warn`(scripts/lumos:26128)判斷 `when-symbol`/`when-test` 的路徑段「像不像檔案路徑」,規則是:已在 `tree.files` 裡、或含 `/`、或含 `.` 就當作合理路徑不警告;否則警告「不像檔案路徑(型別::方法?)」。
2. `Makefile::build`(還沒建立、也還沒提交進 repo 的合法情境,對應設計文件裡「還沒建的檔(`src/new.py::main`)是正常的等待狀態,不列」的意圖):`path="Makefile"`,不在 `tree.files`(還沒建)、沒有 `/`、沒有 `.` → 被誤判成「不像檔案路徑」而列警告,即便 `Makefile`/`Dockerfile`/`Rakefile`/`Gemfile` 這類慣例檔名本來就沒有副檔名。實測:
   ```python
   m._drift_probe_path_warn('symbol', 'Makefile::build', FakeTree(files=set()))
   # -> 'when-symbol 的路徑 Makefile 不像檔案路徑(寫成 型別::方法 了?…)'
   m._drift_probe_path_warn('symbol', 'src/new.py::main', FakeTree(files=set()))
   # -> None   (同樣還沒建立,但因為有 . 就不警告)
   ```
3. 反過來,`v1.2::x` 這種明顯不是檔案路徑的版本標籤,因為含有 `.`(`v1.2`),被當成「像路徑」放行、不列警告,跟 `Config::load` 屬於同一種永遠死掉的條件,卻沒有得到同等的診斷提醒:
   ```python
   m._drift_probe_path_warn('symbol', 'v1.2::x', FakeTree(files=set()))  # -> None
   ```
4. `a::b::c` 這種多重 `::` 因為 `rsplit("::", 1)` 只切最後一段,`path` 會變成 `"a::b"`,不含 `/` 或 `.` → 照樣被列成「不像檔案路徑」,方向上是對的(這種寫法本來就有問題),已看,無 finding。

## 其它已看過、沒有發現的邊界
- `_probe_norm_value`/`_posix_norm` 對 `./a`、`a/./b`、`a//b`、`a/b/`(尾斜線)、`.`、NFD→NFC、全形字元、路徑中含空白都正確處理,沒有把文法本來不准的值(如 `..` 開頭)正規化出來(F3 例外)。
- `_probe_bad_path` 對正斜線寫的 `..`、`../a`、`a/..`、`a/../b` 都正確擋下(只有反斜線變體繞得過,見 F3)。
- `_drift_disk_list` 對「不是 git 專案」(git 指令失敗→回 None,不當)、「index 加未追蹤、扣掉磁碟上已刪除的檔」(含剛被刪除但未 stage 的檔)行為跟 PITFALL 註解描述一致,已用既有測試 B1 同構驗證過(自己也重跑過邏輯,無異常)。`ls-files -z`/`--others -z` 用 NUL 分隔,路徑內含換行不會被截斷或誤判。
- `_nodehome_list`/`_nodehome_code_kind` 對連結檔(120000)、子模組(160000)本來就用 mode 過濾排除,這是既有行為(不是這份差異新增的),沒有在這份差異裡被動到。
- `_drift_exam_load_probes` 對 `rewrite` 欄位是整數、`null`、list、dict、缺欄位、帶列表記號前綴(`- REVISIT:…`)都能正確處理:非字串一律經 `str()` 轉字面後走 `_revisit_split`,判不出 REVISIT 格式就歸類成「不是條件式回頭條件」被擋(rc None,印出每題原因),沒有任何一種輸入讓它拋例外。
- NUL 位元組、Python 2 語法在 `_drift_py_names` 裡都被 `(SyntaxError, ValueError)` 正確接住、退回逐行正則備援(唯獨深巢狀觸發的 `MemoryError` 沒接住,見 F1)。
- 名字只出現在註解或字串裡:`_defines` 的字面比對是文字層級寬鬆比對(用來當作「值得進一步解析」的快速篩選),真正認定「是不是定義」靠 ast 的 `funcs`/`classes`/`assigns` 三個集合,註解、字串、docstring 裡的字面不會進這三個集合,行為正確。

共 4 條 finding,最高等級 blocker,blocking 3 條(F1、F2、F3)。
