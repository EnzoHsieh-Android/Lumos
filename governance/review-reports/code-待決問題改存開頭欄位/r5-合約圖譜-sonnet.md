severity: major

**範圍說明**:我在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r5-合約圖譜-sonnet/` 下檢出修前 `d6bb423f` 與修後 `48b327b0` 兩份副本,並做了幾份拆掉一道修補的變體。修後版 `-k t_qfm_` 的 216 條斷言全綠。這些測試綠燈,正是下面第 1、2 條沒被抓到的原因。

## 對照結果

**S1–S7 字面與程式**
- S2、S3 這輪改的文字,大多跟 `_pq_bad_char`、`_pq_blank`、`_pq_scan` 對得上。
- 例外是「只有看不見的字元算空值」。程式只涵蓋空白、零寬連接字、不連接字和軟連字號,見下面第 4 條。
- 「切斷清單」那條字面寫的是「單行值的頂格鍵」,程式只檢查第一個頂格鍵,見下面第 1 條。
- 標籤字「只在旗幟序列放行」的目的是防藏指令,程式沒做到,見下面第 2 條。

**守衛子指令拿鎖逾時都回擋下:成立**
- 我把寫入鎖換成會丟 `RuntimeError` 的版本,跑 bind、audit、abandon、plan 和 `decision-*`、`set`、`append`、`remove`、`question-*`,全部 rc2 加「擋下」。
- 沒有逐一驗證的守衛子指令(kill-add、kill-rm、settle 等)有一半被參數檢查先擋下,但它們都走同一個 `_guard_dispatch`。
- 例外是 `summary-line`,見下面第 6 條。

**不接 ValueError、guard kill 讀非 UTF-8 檔維持 rc1:成立**
- 我把 `main()` 的例外清單改成同時接 `ValueError`,`t_kill_recipe_check_matches_guard_kill` 立刻紅 3 條。這個說明有測試釘住。

**過期句 grep**
- 全 repo 已找不到 `_vault_locked` 和 `_is_commit`,`_pq_cf_ok` 還留在 docstring,見第 3 條。
- 沒找到「格式字元一律」。
- 「另案」還出現在 `scripts/test_lumos.py:56028` 的測試 docstring,見第 3 條。
- 計劃審計紀錄第 169 行的 `_vault_locked` 是歷史紀錄,不算過期。

**〈實作測試品質〉**
- 這輪新斷言多數抓得到真錯:把新測試放到修前程式上跑,13 條紅。
- 我拆掉 `_pq_blank` 的修補,2 條紅。
- 弱點有兩處:
  - 沒有測試涵蓋「第二個頂格鍵」,所以第 1 條抓不到。
  - 沒有測試涵蓋「旗幟包著的暗藏內容」。我拆掉旗幟序列的長度檢查(`len(run) >= 2`)或中途收尾檢查,216 條全綠。
- ④ 兄弟前綴和 ⑥ `--push-check` 兩條,放到修前程式上也綠,代表它們是舊修補的保護,不是這輪修補的證據。

**圖譜鏡頭**
- 三篇改動筆記加 `lumos-cli-read`、`規格閘`、`pitfalls-code-loop` 都讀過。
- `lumos-cli-read` 和 `pitfalls-code-loop` 沒有新的矛盾。
- `規格閘` 對 `--push-check` 的描述與實測一致。
- `lumos-cli-write` 的 WHY 與代價說明是真的。
- `情境出題` 的負責範圍改動沒問題。
- 字元規則(旗幟序列、空值)只寫在計劃筆記,沒有寫進任何一篇 Systems 的家。

## 發現

1. 清單切斷檢查變窄後,後面的阻塞題會被靜默丟掉。
   - 修後 `_pq_scan` 只檢查第一個頂格鍵,而且遇到下一個頂格鍵就停。
   - 對 `decisions:`、`tags:`、`summary: |-` 這類自己有內容的鍵,完全不看。後面再接 `  - id: Q2`,這題就消失。
   - 重現(把測試輔助函式當函式庫載入,對兩份副本各跑一次):
     - `pending_questions:` 後面接 Q1(實作階段),再接 `reason: x`、`source: y` 兩個頂格鍵,最後接 Q2(需求階段,阻塞)。
     - 或 Q1 後面接 `tags:\n  - type/project`,再接同樣的 Q2。
   - 結果:
     - 修前:`spec-gate --no-run` 回 rc1,訊息是「清單無法判定…把清單切斷了」。
     - 修後:rc0,輸出「待決問題: ✓ — 1 題,沒有擋進實作的」。阻塞題被規格閘靜默放行。
     - `lint` 也只剩無關警告。
   - 與字面對不上:`pq_parse` 回報 qs=1、errs=0。S2 字面把「單行值的頂格鍵把清單切斷而後面還有題」列為讀不懂,`source:` 就是單行值,卻沒被判讀不懂。
   - 可行的收法:自有內容的鍵底下只擋 `  - id: Q<數字>`(決策項目是 `d<數字>`,分得開),且不要在第一個頂格鍵就停。
   - 歸因:有證據的修復回歸。
   - 查證命令:`python3.14 probe2.py <副本>` 的 A、C、D、E 案例,修前 errs=1,修後 errs=0;`e2e.py` 的 spec-gate rc 為 1 對 0。
   - 引句:「for k2 in range(i + 1, len(fm_lines) if not owns else i + 1):」
   - 佐證:`scripts/lumos:7032`
severity: major
   - blocking: 是

2. 旗幟序列放行沒擋住暗藏內容,筆記宣稱的收口不成立。
   - `_pq_flag_run_ok` 只要求前面是 U+1F3F4、中間是標籤字、結尾是 U+E007F,不限長度也不限字母。
   - 重現:
     - `lm._pq_bad_char('題目' + '\U0001f3f4' + <把 "ignore all prior instructions" 逐字偏移 0xE0000 的標籤字> + '\U000e007f') is None` 為 True。
     - 10 萬個標籤字也過。
   - 計劃第 17 行和 docstring 都寫「整段放行可藏人看不見的指令」已解決,這個洞還在。
   - 真正的旗幟只有約 5 到 6 個標籤字;限長度並限小寫字母和數字就能收口。
   - 測試只有「沒旗幟開頭」和「沒收尾」兩個反例,沒有「合法包裝裡塞暗藏內容」。
   - 歸因:有證據的原有漏查。修前標籤字整段放行,這輪修補沒有收到口,也沒變壞。
   - 查證命令:同上 Python 單行;`ma`、`mb` 兩份變體 216 條全綠。
   - 引句:「run[-1] == "\U000E007F" and all(ord(x) < 0xE007F for x in run[:-1])」
   - 佐證:`scripts/lumos:6950`
severity: major
   - blocking: 是

3. 過期的句子還在。
   - `_pq_bad_char` 的 docstring 還寫「扣掉 _pq_cf_ok 放行的那幾個」,這個函式已在這輪被刪。
   - 測試 `t_backend_qo_question_section_not_parsed` 的 docstring 還寫「改存開頭欄位另案」,而計劃第 107–108 行已要求改掉這類措辭。
   - 歸因:有證據的修復回歸(`_pq_cf_ok` 那句);另案那句屬原有漏查。
   - 查證命令:`git grep -n -e "_pq_cf_ok" -e "改存開頭欄位.\{0,6\}另案" -- scripts`,命中 `scripts/lumos:6918` 和 `scripts/test_lumos.py:56028`。
   - 引句:「扣掉 _pq_cf_ok 放行的那幾個。讀寫兩端共用這一條」
   - 佐證:`scripts/lumos:6918`
severity: minor
   - blocking: 否

4. 「只有看不見的字元算空值」說得比實作多。
   - `_pq_blank` 只涵蓋空白、零寬連接字、不連接字和軟連字號。
   - U+3164(韓文填充)、U+2800(點字空白)、U+FE0F、單獨的組合附加符號,用 `pq_parse` 實測都讀得懂,算有內容的值。
   - S2、S3 字面寫的是「值只有看不見的字元」。
   - 歸因:有證據的原有漏查。
   - 查證命令:`probe1.py` 的 Hangul filler、braille blank、variation selector、combining 四項輸出 OK。
   - 引句:「return not "".join(ch for ch in v if not ch.isspace() and ch not in _PQ_CF_OK)」
   - 佐證:`scripts/lumos:6955`
severity: minor
   - blocking: 否

5. 符號連結筆記「寫得進」,但連結被換成一般檔案。
   - 修後 `question-add` 和 `set` 都 rc0,但原本指到的外部檔完全沒被更新,筆記路徑變成獨立的新檔。修前是 rc2。
   - 測試只斷言 rc0,沒看寫到哪裡。
   - 這是 `_write_lf` 原本的換名語意,不是這輪新增的。
   - 歸因:有證據的原有漏查(寫入原語行為);測試盲區是這輪新增的。
   - 查證命令:`sym.py` 輸出 `rc 0 still symlink: False ext has Q: False`。
   - 引句:「r.returncode == 0 and "沒拿" not in r.stderr, r.stderr[-300:])」
   - 佐證:`scripts/test_lumos.py:56685`
severity: minor
   - blocking: 否

6. `summary-line` 拿鎖逾時仍丟追蹤。
   - 我模擬鎖逾時,`summary-line` 讓 `RuntimeError` 直接丟出 `main()`,沒有「擋下」。
   - 其餘 set、append、remove、決策各指令、question-*、guard 全部 rc2。
   - S3 寫的是「寫入指令與守衛子指令拿鎖逾時都應回擋下」,`summary-line` 沒被涵蓋。
   - 歸因:有證據的原有漏查(`cmd_summary_line` 這輪沒碰)。
   - 查證命令:`lockbusy.py`,輸出 `summary-line ... rc=None crash=RuntimeError(...)`。
   - 引句:「寫入指令與守衛子指令拿鎖逾時都應回」
   - 佐證:`scripts/lumos:20183`
severity: minor
   - blocking: 否

## 三問

① **原問題的修復效果**:修後版在合法欄位排列上有行為證據。
- 清單後面接 `decisions`、`lands_in`、`tags`、`summary: |-`,修前讀不懂,修後讀得懂。
- 工具流程「加題、記決策、改題」修前被擋,修後 rc0。
- 守衛 plan、abandon 的鎖逾時修前丟追蹤,修後 rc2。
- 一般旗幟 emoji 放行,孤立標籤字被擋。

② **相鄰路徑**:大致仍成立,有兩處例外。
- 寫入指令、`guard kill` 非 UTF-8 的 rc1、`--push-check` 以 `-` 開頭的範圍,都沒變壞。
- 例外一:正常放行的收窄過頭,連「真的被切斷」的反例也放走了,見第 1 條。
- 例外二:旗幟放行仍可夾帶暗藏內容,見第 2 條。

③ **新發現案例的修前、修後**:
- 第 1 條:修前 rc1 擋下,修後 rc0 放行,是回歸。
- 第 2 條:修前、修後都放行,結果相同。
- 第 4 條:修前、修後都當有內容的值,結果相同。
- 第 5 條:修前 rc2,修後 rc0 但連結被換成一般檔案。
- 第 6 條:修前、修後都丟追蹤,結果相同。

總結:這輪修補把誤擋收乾淨了,但同時讓「第二個以後的頂格鍵、自有內容的鍵後面再接阻塞題」靜默放行(第 1 條),旗幟序列的防暗藏內容也沒有真的做到(第 2 條),這兩條會擋合併。
