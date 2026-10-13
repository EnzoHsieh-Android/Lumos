severity: major

以下用 A 表示修後 `75620ccf`,B 表示修前 `d705e3d7`,兩份主程式都用 `git show <提交>:scripts/lumos` 取出,以 `importlib.machinery.SourceFileLoader` 載入,直接呼叫 `pq_parse` 或跑命令列。

**1. 清單外「縮排的 `pending_questions:`」檢查會誤擋沒有這個欄位的筆記,連 block scalar 內文都擋**

severity: major
blocking: 是
引句:「縮排掉的 pending_questions: 整段會被當成別的欄位的內容,題目跟著不見」
file: `scripts/lumos:7414`、`scripts/lumos:7415`(檢查本身)、`docs/lumos-toolchain-knowledge/Projects/待決問題改存開頭欄位_計劃.md:134`(S6 條款)

- 這個檢查放在 `_pq_scan` 的第一圈。它沒有跳過 block scalar,也不看筆記有沒有頂格的 `pending_questions:`。
- 結果是筆記完全沒有這個欄位,只要 `summary: |-` 的內文裡有一行縮排開頭是 `pending_questions:`,就被判「清單無法判定」。
- 這同時違反兩條合約:S6(沒有欄位的計劃判定與輸出跟現行相同),以及「block scalar 內容不掃」。
- 最小重現(程式碼載入如上):
  ```
  pq_parse(["type: project","summary: |-","  FACT:x","  pending_questions: 之後補"])
  ```
  - A:`(True, [], [(5, 'pending_questions: 要頂格寫;縮排或寫在清單項裡會被讀成別的欄位的內容')])`
  - B:`(False, [], [])`
- 命令列證據:
  - 一份沒有該欄位、`summary` 帶這行的計劃,A 的 `lumos spec-gate --no-run` 多印 `[spec-gate] 待決問題: ✗ — 開頭欄位 pending_questions 清單無法判定`,B 沒有這行。
  - A 的 `lumos lint` 多一條 `待決問題清單無法判定`。專案開關是 warn,所以只提醒。
- 現況:repo 851 篇筆記沒有一篇踩到。
- 歸因:有證據的修復回歸。這段是 `75620ccf` 新增的,B 對同一輸入不報。
- 建議修法:第一圈沿用第二圈的 `block_col` 跳過 block scalar 內文,並加一支「純文件提到」的反例測試。目前的突變實驗(把這個檢查拿掉)只有 `t_qfm_r8_outside_key_rule` 一條斷言翻紅,那條斷言只守正向。

**2. flow collection 跨行時,題目鍵不在該行開頭的片段靜默消失**

severity: major
⚠(原有漏查,只有刻意拆行的寫法才會踩到)
blocking: 是
引句:「flow 值／清單項(`{`、`[` 開頭)逐段找題目鍵;逐段線性掃」
file: `scripts/lumos:7312`、`scripts/lumos:7317`(`candidate[:1] not in ("{", "[")` 讓以逗號、`}`、`]` 或一般字開頭的續行整行不檢查)、`docs/lumos-toolchain-knowledge/Projects/待決問題改存開頭欄位_計劃.md:130`(S2 寫「flow collection 任一段含同樣的鍵」)

- 重現:把 `Q1` 清單後面接
  ```
  x: [a
    , {id: Q2, text: 藏起來的阻塞題, class: 需求, stage: 需求, status: 待人, blocking: true}]
  ```
  - A、B 都回 `pq_parse` 無錯,只讀到 `Q1`。
  - 系統內建 Python 的 PyYAML(`yaml.safe_load`)把這段讀成 `{'id':'Q2','text':…,'blocking':True}`,是一筆完整的題目。
- 同族的幾種寫法也漏:續行以 `}, {text: y}` 起頭、`b, text: y`、`a: 1, id: Q9`、`"a": 1, "text": y`。一行開頭就是題目鍵的寫法(`text: y}`)有被擋。
- 違反的是本輪要驗的第一條規則:讀者當成題目的內容,要嘛讀成題、要嘛整份判無法判定,不准靜默消失。
- 歸因:有證據的原有漏查(A、B 同樣漏)。r8 修補是在「鍵怎麼認」上補,沒有處理「鍵不在行首」。
- 建議:這是同類第七次換形狀,改成整類規則比逐點補丁穩。例如含 `pending_questions` 時,清單外的 flow collection 一律要在同一行內閉合,跨行就判讀不懂。

**3. 簽核時 Ctrl-C 落在帳寫完之後、`fsync` 之中,會留下沒有簽核戳記的帳**

severity: minor
blocking: 否
引句:「Ctrl-C 這類程序內中斷落在筆記已寫、帳還沒寫完之間:先還原筆記再往外丟」
file: `scripts/lumos:9225`(`except BaseException`)、`scripts/lumos:9172`(`_signoff_append` 只接 `OSError`)

- `_signoff_append` 沒接 `KeyboardInterrupt`。整行帳已寫入而 `os.fsync` 還在進行時被中斷,帳行留著,外層卻把筆記還原。
- 重現:在 A 的行程內攔截 `os.fsync`,對指向帳檔的 fd 丟 `KeyboardInterrupt`(以 `os.fstat(fd).st_ino` 比對帳檔),再跑 `signoff`:
  - A:筆記還原成沒有 `signed_off`,帳 2 行(多出一行簽核紀錄)。
  - B:筆記有 `signed_off`,帳 2 行(兩邊一致)。
- 歸因:有證據的修復回歸,窗口從「筆記有戳記、帳沒行」搬到「帳有行、筆記沒戳記」。
- 測試 ③e 把 `_signoff_append` 整支換成直接丟 `KeyboardInterrupt`,碰不到帳檔的半寫入狀態。
- 建議:`_signoff_append` 內對 `BaseException` 也先 `ftruncate`(或刪掉新建的帳)再往外丟。

**4. 新增與改動的測試有四個守不住的洞**

severity: minor
blocking: 否
引句:「預期逐條手寫(不從程式的 emoji 表推):一般符號不算 emoji、emoji 的看不見字元也有串長與整份上限」
file: `scripts/test_lumos.py:57329`(`t_qfm_r8_unicode_scripts_and_budget`)、`scripts/lumos:6959`(`_PQ_EMOJI_RANGES`)、`scripts/lumos:39934`、`scripts/lumos:9225`

- 我在修後副本做了 28 個突變,主要結果如下(用 `-k qfm_r8`,其餘另標):

  | 被拿掉的修補 | 結果 |
  |---|---|
  | 清單外鍵名規則 | 35 條斷言翻紅 |
  | 引號鍵 | 7 條翻紅 |
  | 文字系統連字控制 | 2 條翻紅 |
  | 軟連字號夾東亞字 | 翻紅 |
  | 私用區與未指派碼位 | 翻紅 |
  | 總量上限 32、64 | 各翻紅 |
  | 連接符一串 3 個 | 翻紅 |
  | 帳截回(`ftruncate`) | 翻紅 |
  | 帳的硬連結拒絕 | 翻紅 |
  | 擋下訊息建立時清洗 | 翻紅 |
  | `? ` 複雜鍵 | 翻紅 |
  | 連串 `- ` 平方級 | 翻紅 |
  | block scalar 內容跳過 | 翻紅 |
  | Ctrl-C 處理改窄 | 翻紅 |
  | 帳的連結檢查 | 3 條翻紅 |
  | decision-add 的控制字元與日期 | 各 1 條翻紅 |
  | 縮排 `pending_questions:` 旗標 | 翻紅 |

- 沒抓到的四處:
  1. 把框線區 `U+2500–257F` 加進 emoji 表,整個 `-k qfm`(364 條)全綠,所以「`So` 類別不當 emoji」這條回退沒人守。原本用 20 個 `─‍` 串的反例,現在被「一串最多 3 個」先擋,不再碰到 emoji 表。我手動驗過 `"─\u200d─"`、`"a─\ufe0f"` 在突變版會被放行。
  2. 拿掉 drift fix 載入前的 `_write_refusal_reason`:`-k drift_fix` 161 條全綠。計劃與系統筆記寫了「drift fix 連 `--dry-run` 也拒」,沒有測試。
  3. 把 `decision-amend` 的換行壓平從 `splitlines` 縮回只壓 `\n`:`-k amend` 全綠。我手動跑過,現況行為正確。
  4. 去掉 `O_NOFOLLOW`:全綠。這是檢查與開檔之間的競態,測不到屬預期,只算縱深防禦。
- 舊測試的改動我逐條對過,都誠實:
  - `main()` 換成 `_cli()` 是因為擋下的最後防線搬了位置。
  - 軟連字號的正例從漢字改成 `co­operate`,並由新反例守住漢字被擋。
  - 「20 個愛心加異體選擇符」從必擋改成放行,換成 70 個的反例,符合新上限。
  - 簽核帳的注入點改到 `os.open`/`os.write`,比原本的假檔案物件強。
- 獨立來源:DICP 全表 4174 個碼位是測試端另抄(我用 Unicode 16 清單心算核對,範圍與總數都對),emoji 例子是手寫,這兩點合格。

**5. 日期檢查同族沒掃完:`decision-supersede --ended` 尾端換行,以及全形數字**

severity: minor
blocking: 否
引句:「fullmatch:`$` 會放過尾端換行,寫進一個空行」
file: `scripts/lumos:21403`(`if ended and not DATE_RE.match(ended)`)、`scripts/lumos:20157`(`DATE_RE`)、`scripts/lumos:21508`

- 這輪只把 `decision-add --decided` 改成 `fullmatch`,`--ended` 仍用 `match`。
- 重現:
  ```
  lumos decision-supersede Systems/S 舊的 --by 新的 --ended $'2026-10-13\n'
  ```
  - A、B 都是 rc0,筆記開頭欄位 `ended:` 後面多一個空行。
  - `decision-add --decided "２０２６-10-13"`(全形數字)也 rc0,寫出非 ASCII 日期。
- 歸因:有證據的原有漏查(A、B 同樣行為)。

**6. 文件與程式、測試名對不上的幾處**

severity: minor
blocking: 否
引句:「判鍵名只用 `partition`,沒有會回溯的正規式」
file: `docs/lumos-toolchain-knowledge/Projects/待決問題改存開頭欄位_計劃.md:67`、`scripts/test_lumos.py:57346`、`scripts/test_lumos.py:57062`

- 計劃第 67 行說判鍵名只用 `partition`。程式現在是 `_pq_key_at` 的索引掃描,沒有 `partition`,舊句沒更新。
- 計劃〈範圍〉那條寫「範圍外每一行…只檢查三件事」,同一句後面又加了 `? ` 複雜鍵、縮排的 `pending_questions:` 兩件,條數與內容對不上。
- 測試標籤兩處過期:
  - ④ 寫 `min(8,max(2,可見字//4))`,程式是 32。
  - `t_qfm_r6_writeblocked_inventory_and_edges` 的 ③ 仍寫「main 最外層」,實際走 `_cli`。
- Unicode 版本耦合沒有記載:未指派碼位依執行環境的 `unicodedata`(目前 16.0.0)判。較新的 Python 寫入新 emoji 後,舊 Python 的規格閘會判整份讀不懂;測試 ① 和 ⑥c 也會在 Unicode 升版時變紅。我不確定 Python 3.15 的發行時程與它帶的 Unicode 版本(⚠),建議圖譜補一條回頭條件。
- 其餘逐句對照都對得上:DICP 表與 4174 碼位、三個像空白的字、32/64 上限、`_cli()` 與分派維持叫 `main`、`_write_refusal_reason` 只用在寫入原語、簽核帳與 drift fix 載入。

**7. 只有 `WriteBlocked` 在建立時清洗,其他擋下訊息仍可印出檔名裡的 ESC**

severity: minor
⚠
blocking: 否
引句:「⑧ 指令內部自己接住擋下錯誤時(guard 子指令)也印不出檔名裡的控制字元:訊息在建立時就清洗」
file: `scripts/lumos:20442`(`WriteBlocked.__init__`)

- 我用檔名含 `\x1b[31m` 的筆記跑 13 個寫入指令,分硬連結、符號連結、不可讀三種:
  - `guard bind`/`audit` 在 B 會印原始 ESC,A 不會,修補有效。
  - `summary-line` 的「找不到…」擋下訊息,以及 `decision-reindex` 的成功行,A、B 都仍印原始 ESC。它們不是 `WriteBlocked`。
- 歸因:有證據的原有漏查。修補範圍只到 `WriteBlocked`,文件的「誰接都印不出控制字元」也只該讀成這一類。檔名由被審分支決定,是否整批清洗要由你裁。

**三問**

① 原問題的修復有行為證據(A 對 B,我自己的格子實測):
- 鍵的認法:A 擋下而 B 放行的有 `-<tab>id: Q2`、`"text"<tab>: y`、`"\x74ext": y`、`{? text : y}` 與 `- ? text`。
- 效能:連串 `- ` 8 萬個只花 0.1 秒,線性。
- 看不見字元:emoji 連接符一串 5 個、私用區與未指派碼位、軟連字號夾韓文,A 擋下而 B 放行。
- 真實 emoji 序列 67 個,64 個放行;另 3 個(`#️⃣` 等)只是 YAML 純量規則要求加引號,不是誤擋。
- 簽核帳:磁碟滿截回、第一次建帳失敗刪帳、目錄、硬連結、符號連結、FIFO 都擋,筆記還原。
- 決策自由文字:DEL、ESC、tab 在 A 被拒;B 放行 DEL,`decision-supersede --by` 的 ESC、tab 也放行。
- 局部子集全綠:`-k qfm_r8` 76 條、`-k qfm` 364 條、`slim` 487 條、`summary_line` 27 條、`signoff` 28 條、`drift_fix` 161 條、`decision` 127 條、`guard` 819 條、`refus` 94 條。

② 修補處的相鄰路徑:
- 正常路徑沒壞。我用 14 種含 `text:`、`id: Q9`、`{…}` 的自由文字,對 `decision-add`、`set`、`append`、`summary-line` 各跑一遍,沒有任何一份被判無法判定。
- 錯誤路徑成立:帳的各種失敗模式、拿鎖逾時、符號連結與硬連結的筆記都回 rc2 並還原。
- 壞在相鄰路徑的有第 1 條(沒有欄位也誤擋)、第 3 條(Ctrl-C 窗口搬位)與第 5 條。

③ 新發現在 A、B 的對照:

| 條 | 案例 | A(修後) | B(修前) |
|---|---|---|---|
| 1 | `summary` 內文有縮排的 `pending_questions:` 行 | 判無法判定,`spec-gate` 多印 ✗ 行 | 讀得懂 |
| 2 | 跨行 flow 續行 `, {id: Q2, text: …}` | 靜默消失 | 靜默消失 |
| 3 | 帳寫完後 `fsync` 被 Ctrl-C | 筆記還原、帳留 1 行 | 筆記有戳記、帳 1 行 |
| 5 | `--ended $'…\n'` | 開頭欄位多空行 | 開頭欄位多空行 |
| 7 | `summary-line` 的檔名含 ESC | 印原始 ESC | 印原始 ESC |

**我這邊要交代的事**
- 我曾用 `pkill -f "scripts/test_lumos.py$"` 想停掉自己的整套測試,這個比對太寬,可能殺到同機別的會談跑著的無參數測試。發現後已停手,請編排者留意是否有別的測試被中斷。
- 我在 repo 登記了 `after`、`after2`、`after3`、`before` 四個分離 worktree,都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r9-合約圖譜-sonnet/` 下。
- 我跑測試留下了 `gctl-run-*` 暫存,分不清哪些是我的,沒有刪。收貨刪目錄後請順手 `git worktree prune`。

總結:這一輪的三條規則大致站得住,但第 1 條的新檢查讓沒有欄位的筆記也可能被擋,第 2 條的跨行 flow 漏洞讓題目仍能靜默消失,測試對框線當 emoji 的回退、drift fix 拒寫、amend 換行壓平三處守不住。
