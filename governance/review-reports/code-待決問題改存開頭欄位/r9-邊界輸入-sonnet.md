severity: major

第 9 輪邊界輸入席的結果:2 條會擋合併的問題,4 條小問題。其餘核對項目,凡文中未列為問題的,實測都過。

實測用的程式(`/Users/enzo/orca/workspaces/lumos-toolchain/qo-frontmatter/scripts/lumos`)與 75620ccf 的內容一致,「修前」是 d705e3d7。所有實驗放在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r9-邊界輸入-sonnet/`。

1. 單獨一行的 `?`(複雜鍵)繞過「清單外 `? ` 整個不收」,題目鍵照樣藏得住。
   引句:「if i + 1 < n and text[i] in "-?" and text[i + 1] in " \t":」
   file: `scripts/lumos:7212`
   - 原因:各行先 `rstrip()` 再判斷,`?` 後面沒有空白也沒有下一個字元,條件永遠不成立。YAML 的多行複雜鍵正是這個寫法。
   - 重現:`pq_parse(["x:","  ?","    text","  : y","pending_questions:","  - id: Q1","    text: 甲","    class: x","    stage: 架構","    status: 待查"])`
   - PyYAML 讀出 `{'x': {'text': 'y'}}`,`pq_parse` 回「OK 1q」、沒有任何錯誤。換成 `"te\`+換行+`xt"`、`id`/`: Q2`、`stage`/`: 架構`、`status`/`: 待人`,或把 `?` 放在頂格,結果一樣。
   - 端到端:拿 `question-add` 建好的計劃,在開頭欄位加 `hidden:\n  ?\n    text\n  : 另一題`,`spec-gate --no-run` 印 `待決問題: ✓ — 1 題`、`lint` 沒有任何提醒。對照組 `hidden:\n  text: 另一題` 會被判「清單無法判定」。
   - 模糊測試:隨機組合約 60 萬份,漏網的全是 `?` 這一族。
   - 圖譜說「`? ` 複雜鍵可以跨行藏鍵名,清單外一律判讀不懂」,與程式不符。修法:別依賴行尾後面還有字元,行首 `?` 只要後面是行尾、空白或 tab 就算。
   - 歸因:有證據的原有漏查。修前同樣漏,這輪的修補沒有補到。
   - 修前:`OK 1q`。修後:`OK 1q`。
severity: major
   blocking: 是

2. 簽核寫帳時按 Ctrl-C,筆記被還原但帳上那行還在,兩邊對不上。
   引句:「Ctrl-C 這類程序內中斷落在筆記已寫、帳還沒寫完之間:先還原筆記再往外丟」
   file: `scripts/lumos:9225`(`_signoff_write_locked` 的 `except BaseException`)
   - 原因:這個分支只還原筆記,沒有把帳截回原長度。
   - 重現:在 `os.write` 寫完帳後立刻丟 `KeyboardInterrupt`,執行 `lumos signoff 測試主題 --note 確認過`。結果是退出碼 -2、筆記沒有 `signed_off`、帳上多一行完整的簽核紀錄,帳原本就有的舊內容也在。換成「帳不存在」的情況,帳會被新建並留下那一行。
   - 後果:`guard abandon` 靠簽核帳(`_guard_signoff_refs`)判斷有沒有簽核。帶 `--ref` 時,被中斷的簽核仍會讓棄置檢查通過。
   - ⚠ 真實按 Ctrl-C 要落在 `fsync` 前後的短窗口,我是用注入重現的。
   - 歸因:有證據的修復回歸。
   - 修前(`os.fsync` 在帳上丟 `KeyboardInterrupt`):筆記 `signed_off: True`、帳有那一行,兩邊一致。修後:筆記沒有、帳有那一行。
severity: major
   blocking: 是

3. 縮排為 0 的清單項 `- status: …` 逃過「非頂格 status」規則。
   引句:「if qk and not (qk == "status" and indent == 0):」
   file: `scripts/lumos:7357`
   - 原因:`indent` 只算前導空格,所以 `x:` 底下頂格的 `- status: 待人` 被當成頂格 status 放行。圖譜寫的是「只有頂格 `status` 豁免」。
   - 重現:`["x:","- status: 待人"]` 回 `OK 1q`。
   - 沒有 `text`、`class`、`stage` 的單獨 status 不構成一題,實際影響小。
   - 歸因:有證據的原有漏查。修前 `OK 1q`,修後 `OK 1q`。
severity: minor
   blocking: 否

4. flow 裡只有鍵、沒有冒號的寫法讀不出鍵,例如 `{text}`。
   引句:「flow 值／清單項(`{`、`[` 開頭)逐段找題目鍵」
   file: `scripts/lumos:7312`
   - 原因:逐段呼叫 `_pq_key_at`,沒有冒號就回 None。
   - 重現:`["x: {text}"]` 與 `['x: {"text"}']` 都回 `OK 1q`,PyYAML 讀出鍵 `text`、值為空。
   - 沒有值的鍵不成題,影響小,與第 1 條同屬「鍵名認法」。
   - 歸因:有證據的原有漏查。修前 `OK 1q`,修後 `OK 1q`。
severity: minor
   blocking: 否

5. 一般法文排版的不換行空白會被額度誤擋。
   引句:「limit = min(_PQ_INVISIBLE_MAX, max(_PQ_INVISIBLE_MIN, visible // _PQ_INVISIBLE_VISIBLE_DIVISOR))」
   file: `scripts/lumos:7108`
   - 重現:`«\xa0Oui\xa0»\u202f?` 與 `1\xa02\xa03\xa04` 回「值裡看不見的字元太多」。
   - 原因:NBSP、窄 NBSP 這類 Zs 空白計入「看不見」額度,短句比例不夠。
   - 較長的句子沒事:`Le plafond est de 10\xa0000\xa0€ ?` 回 None。
   - 歸因:有證據的原有漏查。修前與修後訊息相同。
severity: minor
   blocking: 否

6. `--decided` 接受全形與阿拉伯-印度數字。
   引句:「if not DATE_RE.fullmatch(decided):」
   file: `scripts/lumos:21508`
   - 原因:`DATE_RE` 用 `\d`,會比對 Unicode 數字,`fullmatch` 只解決了尾端換行。
   - 重現:`decision-add … --decided "２０２６-10-01"` 與 `"٢٠٢٦-10-01"` 都 rc0,並寫進 `decided: ２０２６-10-01`。`lint` 只給「warn 不擋」。
   - 歸因:有證據的原有漏查。修前與修後都是 rc0。
severity: minor
   blocking: 否

**三問**
- **① 原問題的修復效果,有行為證據的部分:**
  - 鍵名認法:引號鍵、單引號 `''`、雙引號 `\x78`、JSON 風格 `"text":y`、引號與冒號之間有空白、`-<tab>`、兩個空白、全形 `ｔｅｘｔ`、`Id`/`iD`、anchor 與 tag 開頭、flow 巢狀,實跑都判讀不懂。修前漏的有 `-<tab>id`、`"te\x78t"` 和 `"text":y`。
  - 效能:各種病態長行(約 20 萬個 `- `、`&a `、`{`、`"`)都在 0.5 秒內;唯一例外是 140 萬字的 `\u0041` 跳脫鍵,約 1.4 秒,是線性不是平方級。
  - 簽核帳:符號連結、懸空連結、目錄、FIFO、硬連結、唯讀檔,都是退出碼 2、筆記還原、帳不動。注入「先寫 20 位元組再磁碟滿」,既有帳截回原長度、新建帳刪掉,訊息正確。`ftruncate` 本身失敗時,訊息明說「帳可能留有半行」。
  - 擋下訊息:控制字元已在建立時清洗,訊息裡的符號連結目標、檔名都被清洗。
  - Unicode:阿拉伯、波斯、希伯來、泰、天城、孟加拉、僧伽羅、藏、緬、高棉、蒙古、韓、日的正常長句全過;國旗、鍵帽、膚色、四人家庭、親吻、職業 ZWJ、❤️‍🔥、🏳️‍⚧️、較新的 emoji 全過;17 個 ❤️ 現在放行,修前被擋。
  - 注意:Unicode 17 的新 emoji(例如 U+1FAC8)會被拒,因為 Python 內建的是 Unicode 16.0.0。這是設計取捨,訊息也說明了。
  - 真實筆記:855 篇 docs 附加題目後解析,只有 1 篇因為本來就有 `pending_questions` 而報「寫了兩次」;其餘 20 篇複本跑 `question-add` 與 `lint` 都沒問題。
  - 用 lumos 自己的指令(new、question-add、decision-add 含 `text: x`/`stage: 架構`/`id: Q5`/`- id: Q7`、decision-supersede、append lands_in/tags/aliases/related、set、question-set)依序組合,每步後的 `lint` 與 `spec-gate --no-run` 都沒有讓清單變讀不懂。
  - 缺口:第 1 條、第 3 條、第 4 條。
- **② 修補處的相鄰路徑:**
  - 拿掉裝飾器、改由 `_cli()` 接 `WriteBlocked` 後,精簡版產生器(`scripts/slim-gen.py`)仍保留 `_cli` 與 `WriteBlocked`,精簡版 `--help` 正常。
  - `decision-add` 的 ESC、DEL、tab 都拒寫。
  - `decision-amend` 把 `\r\n`、`\x0b`、`\x1c`、U+2028 壓成空白,tab 拒。
  - 錯誤路徑唯一不成立的是第 2 條。
- **③ 同一案例的修前與修後:** 第 1、3、4、5、6 條修前修後結果相同(都是原有漏查或原有行為)。第 2 條修前是「筆記帶 `signed_off` 加帳有一行」,修後變成「筆記沒有 `signed_off` 但帳有一行」。

總結:這輪對 YAML 鍵名、Unicode 容量與簽核回滾的修補大致站得住,但單獨一行的 `?` 複雜鍵仍能藏題目,簽核寫帳時的 Ctrl-C 會讓帳和筆記對不上,這兩條需要處理後才適合合併。

臨時目錄:`/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r9-邊界輸入-sonnet/`(內含 `flow.py`、`sigint.py`、`fz2.py` 等重現腳本;我建的 `before` worktree 已移除,其餘由編排者收貨後刪)。
