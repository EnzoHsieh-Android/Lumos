severity: major

這輪有兩個會擋合併的問題,都是這次修補造成的回歸(修前正常,修後出錯)。本席實驗都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-正確性-sonnet/`,沒有寫檔。

**先說白話:** 規則甲在「引號包住鍵名」的兩種寫法上漏了,題目會被悄悄吃掉。規則丙的簽核回滾,在磁碟寫滿這類「寫到一半失敗」時會把半行殘留在帳檔裡。

**1. 引號鍵後面多一個空白、或 JSON 風格不留空白時,題目整題靜默消失(規則甲)**
severity: major
blocking: 是
歸因:有證據的修復回歸
引句:「if j < 0 or t[j + 1:j + 2] != ":" or t[j + 2:j + 3] not in」
- file: `scripts/lumos:7153`(`_pq_questionish_key` 的引號鍵分支)。
- 這支函式只認「收尾引號緊接冒號,冒號後再接空白或行尾」。以下三種寫法的鍵名都不被當題目鍵,但 YAML 會讀成 text、id:
  - `"text" : x`(引號和冒號之間多空白)
  - `{"id":"Q2","text":"x"}`(JSON 風格,冒號後不留空白)
  - `'id':'Q2'`
- PyYAML 實測:`extra: {"id":"Q2","text":"x"}` 讀成 `{'extra': {'id': 'Q2', 'text': 'x'}}`,`"text" : c` 讀成 `{'text': 'c'}`。
- 最小重現(清單後接一行,`pq_parse` 的錯誤清單為空,整份「讀得懂」):
  ```
  cd /Users/enzo/orca/workspaces/lumos-toolchain/qo-frontmatter && python3.14 -c "
  import importlib.machinery as m,importlib.util as u
  l=m.SourceFileLoader('lm','scripts/lumos');s=u.spec_from_loader('lm',l);x=u.module_from_spec(s);l.exec_module(x)
  Q=['pending_questions:','  - id: Q1','    text: a','    class: 需求','    stage: 需求','    status: 待查']
  for e in ('extra: {\"id\":\"Q2\",\"text\":\"b\"}','\"text\" : c'): print(x.pq_parse(Q+[e])[2])"
  ```
  - 修後(5242975c)兩行都印 `[]`。
  - 修前(ff6565ec)兩行都被拒。查證用 `git show ff6565ec:scripts/lumos` 的副本 `lumos_before.py`,拒絕原因是「flow collection …」與「頂格寫了 … 不是 鍵: 值」。
- 後果:被吃掉的題若標了阻塞,規格閘看不到,會放行。
- 其他寫法我試過都擋得住:`{"id": "Q2", ...}`、`"text": x`、`'stage': 架構`、全形鍵名、重複 `- `。
- `Projects/待決問題改存開頭欄位_計劃.md` 與 `Systems/lumos-cli-read.md` 第 118 行寫「引號包住的題目鍵照樣算」,這兩種寫法是例外,筆記說過頭了。

**2. 簽核寫帳「寫到一半」失敗時,`truncate` 本身會失敗,帳檔留下半行(規則丙)**
severity: major
blocking: 是
歸因:有證據的修復回歸
引句:「fh.truncate(log_pos)」
- file: `scripts/lumos:9145`(`_signoff_write_locked`)。
- `fh` 是緩衝的 `BufferedWriter`,`truncate()` 會先 `flush()`。真實的短寫失敗(EFBIG,和磁碟滿 ENOSPC 同型)時,殘餘緩衝會再寫一次、再失敗,`truncate` 從沒執行。
- 測試 ③ 用的假把手沒有緩衝,所以測不到。
- 重現(`ulimit -f` 同型,帳檔長度設在上限前約 30 位元組):
  ```
  python3.14 /tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-正確性-sonnet/efbig.py after
  python3.14 /tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-正確性-sonnet/efbig.py before
  ```
  - 修後:rc 2,訊息 `簽核帳還原失敗:[Errno 27] File too large;帳可能留有半行`。帳檔從 16354 位元組變成 16384,結尾是沒有換行的 `{"ts": "2026-10-13T08:29:49", `。筆記有還原。
  - 修前:rc 2,帳檔 `unchanged: True`(逐位元不變),且以換行結尾。
- 後果:這個半行不補換行,下一筆簽核會接在它後面,連同合法的下一筆一起壞成一行。
- 訊息有照實說「可能留有半行」,所以誠實,但資料損壞的是帳。
- 建議改用 `os.ftruncate(fh.fileno(), log_pos)` 繞過緩衝,或失敗時先丟棄緩衝再截。

**3. 看不見字元總量上限誤擋真實語文(規則乙)**
severity: minor
blocking: 否
歸因:有證據的修復回歸(⚠ 這是規格自己取捨的門檻,圖譜已有 `REVISIT:2026-11-13` 要量測)
引句:「limit = min(_PQ_INVISIBLE_MAX, max(_PQ_INVISIBLE_MIN, visible」
- file: `scripts/lumos:7078`、`scripts/lumos:6950`。
- 一句約 120 字、含 10 個 ZWNJ 的自然波斯語,修前放行、修後被擋「看不見的字元太多」。
- 17 個 `❤️`(每個帶 VS16,全部可忽略字元合計超過 16)修前放行、修後被擋。
- `a\u200db` 這類拉丁字縫的連字控制被擋,是規格要求,不算誤擋。
- 日文異體字選擇符(如 `葛\U000e0100`)、阿拉伯文標示符 RLM(U+200F)被擋,修前同樣被擋,算規格如此。
- 緊接的兩面旗(英格蘭加蘇格蘭)修前修後都擋,有測試釘住,屬刻意。

**4. 行首重複 `- ` 的處理成了平方級,不分輸入大小都慢(規則甲)**
severity: minor
blocking: 否
歸因:有證據的修復回歸
引句:「while text.startswith("- "):」
- file: `scripts/lumos:7205`。`_pq_questionish_key` 與 `_pq_structure_marker_problem` 有同型的迴圈。
- 清單外一行 `"- " * 160000 + "a: b"`(約 320KB):修後 `pq_parse` 4.08 秒,修前 0.00 秒。
- 次數翻倍時間約乘 5 到 6 倍,1MB 的單行會卡約一分鐘以上。實際筆記不太會遇到,但會卡住提交掛鉤。
- 建議用索引往前走,不要每次切片。

**5. 殘留的看不見通道(規則乙)**
severity: minor
blocking: 否
歸因:有證據的原有漏查(兩版結果相同:修前、修後都放行)
引句:「三個不是 DICP、畫面仍像空白的字」
- file: `scripts/lumos:6931`。
- 私用區(Co)與未指派碼位(Cn)不在 DICP 表,也不在三個像空白的字裡。`a` + 500 個隨機 U+E000 區字元 + `b` 修前修後都放行,且不受任何上限。
- 這些字在多數字型裡畫成空白或方框,每個字可帶約 12 位元。

**6. 測試抓不到幾道載重分支**
severity: minor
blocking: 否
歸因:有證據的修復回歸(測試缺口)
引句:「if qk and not (qk == "status" and indent == 0):」
- file: `scripts/lumos:7272`。
- 我在副本一次拆一道,跑 `t_qfm_r8` 加上相關的 r6、r7 測試。仍全綠的變形:
  - M11:把 status 豁免從「頂格」放寬到「任何縮排」。沒有測試放巢狀 `status:`。
  - M22:拿掉 U+1D159 這個像空白的字。
  - M23:特殊 Zs 不計入額度。
- 其他十八個變形都有紅。
- 缺口不止這些:
  - 測試 ① 只斷言 `bool(errs)`,不看拒絕原因。`- *題目` 這類落在清單範圍內的行,其實是被清單文法擋的,不是被外部規則擋的。
  - 沒有引號鍵加空白、JSON 無空白的案例,所以 finding 1 沒被抓到。
  - 簽核回滾的測試用沒有緩衝的假把手,抓不到 finding 2。
  - 多條預期是手寫的,獨立性本身沒問題。

**7. 筆記與程式不一致、以及兩個邊角(圖譜鏡頭)**
severity: minor
blocking: 否
歸因:有證據的修復回歸(⚠ 第三點是原有)
引句:「return key_col if parts is not None and _pq_unquoted_value(parts[1]) in BLOCK_SCALAR_HEADERS else None」
- file: `scripts/lumos:7262`、`scripts/lumos:9132`。
- 計劃筆記第八輪定案寫「帶註解不算 block scalar」。程式的 `_pq_unquoted_value` 會去掉 ` #註解`,所以 `x: | # hi` 的內容被當 block 跳過。另外三支讀法(`parse_frontmatter` 等)不這樣認。依 CLAUDE.md 以程式碼為準,該筆記這句要立 Issue 或改正。
- 第一次簽核且帳檔不存在時,寫帳失敗會留下一個 0 位元組的 `.signoff-log.jsonl`;修前會刪掉它(已用假把手實證)。幾乎無害,但屬於「逐位元還原」的小缺口。
- 只有「縮排掉了」的 `pending_questions:` 或巢在別的鍵底下,沒有頂格頭,整段不被掃,`present=False` 且無錯誤。修前行為相同,是原有的設計邊界,但與規則甲「不准靜默消失」的措辭有落差。

**三問**
- **① 原問題的修復效果有何行為證據?**
  - 1090 篇真實筆記(`citrus-core`、`rtb`、`crypto`、`Fraser`、`Stockify`、`KDS`、`PetGame`、本 repo 圖譜)各把題加在最前與最後:修前 2+2 篇被擋,修後 1+1 篇。
  - 那 1 篇是本來就有 `pending_questions` 的 `後端工程提問與證據擴充_計劃`,屬正確。
  - 用 `decision-add`(二十種怪內容,含 `stage:`/`text:`/`id: Q9`/`{a: b}`/`&anc`)、`append`、`set`、`summary-line`、`guard bind`、`signoff`、`decision-supersede`、`decision-amend` 逐一寫過,每一步之後 `pq_parse` 都讀得懂。
  - 清單外頂格、雙層清單、引號鍵(正常寫法)、anchor、tag 都擋得住。
  - 但 finding 1 是修補自己新開的洞。
- **② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
  - 符號連結、硬連結、BOM、CRLF 四種筆記跑約三十個寫入指令,全部 rc 2 或 0,沒有 traceback。
  - 最外層只接 `WriteBlocked` 之後,各分派段新增的 `except WriteBlocked: raise` 訊息都正常印出。
  - `decision-add` 的 `\n`、`\r`、`\x1c`、`\u2028`、`\x85` 都以 rc 2 回報,沒有 traceback。
  - 簽核的鎖內讀原稿、筆記還原、符號連結帳拒絕都成立。
  - 唯一不成立的是 finding 2:緩衝寫入失敗時回滾不了。
  - `signoff` 在鎖逾時時(`RuntimeError`)沒有接,仍會 traceback,但這是修前就有的。
- **③ 新發現的同一案例在修前、修後各是什麼結果?**

  | 案例 | 修前 | 修後 |
  |---|---|---|
  | 引號鍵加空白、JSON 無空白(finding 1) | 拒 | 放行 |
  | 簽核寫帳短寫失敗(finding 2) | 帳逐位元不變 | 半行殘留 |
  | 長波斯語、17 個 `❤️`(finding 3) | 放行 | 擋 |
  | 清單外 `"- " * 160000` 加 `a: b`(finding 4) | 0.00 秒 | 4.08 秒 |

  finding 5 兩版相同。

一句話:規則乙和丙的大方向達成,但引號鍵文法漏兩種寫法(題目會悄悄不見)、簽核回滾在真實短寫失敗時留下半行帳,這兩個要先修才能合併。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/qo-frontmatter/scripts/lumos`
- `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-正確性-sonnet/efbig.py`
- `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-正確性-sonnet/cases2.py`
- `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-正確性-sonnet/mutate.py`
