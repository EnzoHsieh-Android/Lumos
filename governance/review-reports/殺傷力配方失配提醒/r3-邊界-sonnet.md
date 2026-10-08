severity: major

## F1 file 解析到 repo 頂本身(空字串、`.`、`sub/..`)時,小解析器照字面會判 missing,guard kill 實際判 error(逃逸)
severity: major
blocking: 是
引句:「走完還在根內才算解析成功,得到實際路徑」
file: `scripts/lumos:13268`
1. guard kill 的圍欄是 `target.startswith(wt_real + os.sep)`(spec 自己在「guard kill 的實際做法」也寫「加路徑分隔字元開頭」),所以解析結果等於工作樹根本身時不通過,判 error。
2. 實測(貼近 guard kill 兩行邏輯的腳本):`""`、`"."`、`"./"`、`"sub/.."`、`".."` 全部是 `outside(error)`。
3. 小解析器的敘述是「走完還在根內才算解析成功」。`file` 為空或 `.` 時零段走完、停在根上,字面讀法算「在根內」,接著落到「不是一般檔(目錄)→ `missing`」,於是標成 drifted;S5 的對應是 `missing` ↔ drifted、`outside` ↔ error,這一格會對不上。kill-add 提醒文字也會說錯(「會判 drifted」,實際是 error 並走圍欄訊息)。
4. 折法:把「解析結果必須是根的嚴格子路徑(等於根也算 `outside`)」寫進解析器;S5 題目表加「`file` 為空 / `.` / `sub/..`」一格。

## F2 「逐段走 file」沒定義 `.`、空段、不存在的中間段、尾端斜線,照字面逐段 lstat 會跟 guard kill 的 realpath 判得不同
severity: minor
blocking: 否
引句:「一支小解析器,以 repo 頂為根、逐段走 `file`」
file: `scripts/lumos:13267`
1. 實測 guard kill 用的非嚴格 realpath:`a.py/`、`a.py/.`、`./a.py`、`nonexist/../a.py` 全部解析到 `a.py` 並讀到 count=1(會套壞法)。
2. 逐段 lstat 的實作遇到 `a.py/`(普通檔後面還有斜線,ENOTDIR)或 `nonexist/..`(中間段不存在)會判 missing,於是 kill-add 對 guard kill 其實能跑的配方印出「讀不到」假提醒,P2 列出假失配。
3. 為什麼只給 minor:只會多一條假提醒,不擋寫入。要折的話一句話:「`.` 與空段略過;`..` 與不存在的中間段照 realpath 非嚴格語意折回,不因 lstat 失敗判 missing」,並補進 S5 題目表。

## F3 解析器的連結跟隨上限 40 與迴圈都判 outside,guard kill 實測是 drifted(迴圈)與照常讀取(長鏈)
severity: minor
blocking: 否
引句:「跟隨連結超過 40 次 → `outside`(迴圈)」
file: `scripts/lumos:13267`
1. 實測(python 3.14):`loopa -> loopb -> loopa` 的迴圈,guard kill 的 realpath 回傳還在根內,`open` 丟 ELOOP(OSError),判 `drifted`,不是 error。
2. 45 層的連結鏈(非迴圈)realpath 正常解開、讀到 count=1,guard kill 會套壞法;spec 判 outside 是假失配。
3. 這個「模擬」對這兩格不貼,S5 的對應表(`outside` ↔ error)若加上這兩格會紅。折法:迴圈 → 當 `missing`(細節寫迴圈);鏈長上限拿掉或改成只在偵測到重複節點時才停。minor 理由:兩者都只多一條提醒,現實幾乎不會出現。

## F4 判斷函式丟出 OSError 以外的例外時,kill-add 沒有保護,「照舊寫入、回傳碼不變」會破
severity: major
blocking: 是
引句:「並照舊寫入,標準輸出與回傳碼跟沒有這條提醒時相同」
file: `scripts/lumos:12951`
1. 「每一條配方、每一篇筆記的處理各自包在例外保護裡」只寫在 §5(P2)。§3 的 kill-add 只處理了設定檔例外,解析器與讀檔步驟沒有任何例外保護條款;§1 也只把「開檔」的 `OSError` 歸 `missing`,解析器自己的 lstat/readlink 失敗(例如超長路徑 ENAMETOOLONG、`file` 含 NUL 的 ValueError)沒有歸屬。
2. 實測:`file` 含 NUL 時 realpath 丟 `ValueError: lstat: embedded null character in path`;5000 字元的 `file` 丟 `OSError`。kill-add 「只更新 --covers」那條路徑會取既有配方的 `file`(手改過的筆記可能帶 NUL 或超長值),判斷函式未保護就崩潰,現在這條路徑是能正常寫入的,等於退步。
3. 折法:判斷函式整個包 `except Exception`,轉成 `missing`(細節帶例外名稱);S1/S2 補一格「判斷函式內部出錯也照舊寫入」。

## F5 kill-rm(與其前提 kill-add)的寫後自驗沿用現有寫法會在格式壞的元素上崩潰,「格式壞的也移得掉」只在全部移完時成立
severity: major
blocking: 是
引句:「格式壞的配方也移得掉;移除後沒有任何配方對得到的 KEY 行應拿掉 `[kill:recipes]` 標記」
file: `scripts/lumos:13005`
1. 實測(筆記 `kill_recipes: ["junk", {"invariant":"x","file":3,"old":"a"}]`):現有 kill-add 的寫後自驗 `check()` 對每個元素呼叫 `r.get(...)`,遇到字串元素就 `AttributeError`,kill-add 崩潰、筆記沒被寫(rc 1);`lumos guard kill` 同樣在 `r.get("platform")` 崩潰。
2. kill-rm 照 §4「同 kill-add 的寫法」做寫後自驗與「剩下配方是否還對得到 KEY 行」的判斷(後者要讀每個剩下元素的 `invariant`,元素可能不是物件、`invariant` 可能不是字串)。同一篇有兩條以上格式壞的元素時,移掉第一條後剩下的壞元素仍會讓自驗/對得到判斷崩潰,於是 S6 只有「單一壞元素」那種測試案例會過,真實的存量(rtb 多條壞配方)修不動。
3. 另外 kill-add 的新增配方路徑對同篇已有壞元素會崩潰(實測),所以「先 rm 舊的、再 kill-add 新的」要先把該篇所有壞元素清完才行;spec 沒寫這個順序限制。
4. 折法:§4 明寫「自驗與對得到判斷對非物件元素、非字串 invariant 一律略過不崩」;S6 測試加「同篇兩條壞元素、只移一條」;kill-add 的自驗同步容錯(或在 §3 註明此限制)。

最高等級:major;blocking 共 3 條
