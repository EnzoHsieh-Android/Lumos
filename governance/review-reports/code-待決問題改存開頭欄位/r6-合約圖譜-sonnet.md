severity: major

1. 切斷檢查改成只認嚴格題號,題號稍微寫歪的阻塞題改成靜默消失,規格閘放行。
severity: major
blocking: 是
引句:「_PQ_CUT_RE = re.compile(r"""^[ \t]*(?:-[ \t]*)?id:[ \t]*["']?Q[1-9][0-9]{0,5}["']?[ \t]*$""")」
- 佐證 file: `scripts/lumos:6912`、`scripts/lumos:7043`。
- 問題:r4 的規則是 `^  - id:(?: |$)`,切斷處後面任何 `  - id:` 都會擋。r5 改成「`id:` 後面只能接 `Q[1-9]\d{0,5}` 再接行尾」。`Q02`、`q2`、`Ｑ2`、`Q1234567`、`id: 2`、`id: Q2 # 註解`、`id: Q2 補`,以及花括號寫法的題目行都不再命中。
- 計劃〈讀法〉寫的是「`id:` 後面接 Q 加數字都算」,S2 寫的是「題目行怎麼寫歪」都擋。程式比文字窄。`Q01` 正是計劃自己點名的常見手滑。
- 最小重現(上下文是 `reason: x` 這個單行頂格鍵,後面接 `  - id: Q02`,題目標了 `blocking: true`、`stage: 架構`、`status: 待查`):
  - 修後:`python3.14 /tmp/lumos-seat-work/code-待決問題改存開頭欄位/r6-合約圖譜-sonnet/e2e2.py` 印 `Q02 rc 0 ['… ✓ — 1 題,沒有擋進實作的']`,`q2` 也是 rc 0。
  - 修前:`python3.14 …/e2e2.py …/lumos_before` 印 `Q02 rc 1 … 清單無法判定`,`q2` 也是 rc 1。
  - 對照:`Q2` 修前修後都是 rc 1。
- 歸因:有證據的修復回歸。

2. CRLF 文字走 git 取出的內容時,切斷檢查整個失效。
severity: minor
blocking: 否
引句:「if _PQ_CUT_RE.match(fm_lines[k2]):」
- 佐證 file: `scripts/lumos:7043`、`scripts/lumos:7128`。
- 問題:正規式結尾的 `$` 對不上行尾的 `\r`。`_pq_fm_of_text` 保留 `\r`,而 `_pq_scan` 其他地方有 `rstrip`,只有這一處沒有。
- 重現:`python3.14 …/p2.py scripts/lumos` 的 CRLF 那行是 `errs= [] nq= 1`,Q2 消失。換成 `…/lumos_before` 則 errs 有「寫在清單範圍外」。
- 影響範圍:磁碟上的檔走 `read_text`,會把 CRLF 轉成 LF,所以 spec-gate、lint、`--stage` 都不受影響(三者實測修前修後相同)。只有 `_pq_push_remind` 讀 git blob 的路徑受影響,而那條只是提醒。所以標 minor。
- 歸因:有證據的修復回歸。

3. 切斷檢查是逐行比對,整個開頭欄位剩餘部分只要有一行像題號就整份擋。
severity: minor
blocking: 否
引句:「摘要裡的條列不是 Q 加數字,所以工具自己寫的 decisions、lands_in、summary 不會被誤擋」
- 佐證 file: `scripts/lumos:7043`。
- 問題:這個前提沒驗過。`summary: |` 區塊裡寫一行 `  id: Q3`,或別的欄位底下有 `  - id: Q3`,都會被當成被切斷的題目。`…/p1.py` 的 `legit summary mention` 和 `legit lands_in item mention` 修後都是 `errs=True`,修前是 `errs=False`。
- 風險:記載這個格式的筆記很可能在摘要裡舉例,誤擋後整份清單無法判定。
- 歸因:有證據的修復回歸。

4. 放行規則仍留有看不見字元的暗道,而計劃文字說已擋。
severity: minor
blocking: 否
引句:「與連續兩個以上的異體選擇符(一個字元能藏一個位元組,人看不見;代碼審 r5 資安-甲)」
- 佐證 file: `scripts/lumos:6935`、`scripts/lumos:7003`。
- 問題:只擋連續兩個以上的異體選擇符。可見字元後各接一個 U+FE00–FE0F 的寫法,每字元 4 位元,`_pq_bad_char` 回 None。
- 「只有看不見字元才算空值」也只處理整個值全是隱形字。可見字之間夾 U+3164、U+2800、U+17B4 都放行。
- 重現:`python3.14 …/p3.py scripts/lumos` 印 `VS-per-char bad_char: None`、`2800 inside: None`。修前結果相同。
- 歸因:有證據的原有漏查。

5. 這輪新增的斷言有三處抓不到對應的破壞。
severity: minor
blocking: 否
引句:「lm._pq_bad_char("題\U000e0100\U000e0101") is not None)」
- 方法:我在副本(`/tmp/lumos-seat-work/…/m`)逐一拆掉修補,跑 `-k t_qfm_r5_folds`。
- 拆 `0xE0100 <= ord(c) <= 0xE01EF` 這一道:全綠。測資是兩個連續異體選擇符,被「連續」那條代打。單一 U+E0100 沒有斷言。
- 從 `_pq_blank` 拿掉 `_pq_is_vs`:全綠。沒有「值只有異體選擇符」的案例。
- 把守衛分派的 `except (RuntimeError, OSError)` 改成只接 `RuntimeError`:`-k t_qfm` 全過(253 條),`-k t_guard` 只剩一條與此無關的環境路徑錯誤(副本在 /tmp 底下,找不到檔)。所以「守衛讀寫失敗也回擋下」沒有測試釘住。這條行為本身是舊的,但計劃寫入篇這輪把它寫進了 WHY。
- 其餘拆除都翻紅:符號連結檢查 islink、旗幟形狀、連續異體選擇符、填充字、檔名清洗、summary-line 的 try、切斷檢查的四種變體(關掉、退回 r4、拿掉引號、拿掉 dash、縮排寫死)。
- 歸因:未判定(測試是新加的,沒有修前版本可比)。

6. 過期句與記載不全。
severity: minor
blocking: 否
引句:「check("③ 筆記是指到庫外的符號連結:不誤判成沒拿鎖(r5 起改成講明是符號連結、擋下,見 t_qfm_r5_folds ④)",」
- 佐證 file: `scripts/test_lumos.py:56644` 是 `t_qfm_r4_folds` 的 docstring,這輪沒改,仍寫「只有單行值的頂格鍵後面又出現題目才算切斷;旗幟標籤字只在旗幟序列裡放行,…筆記是符號連結也寫得進」。三句都已過期。
- 符號連結擋下對所有走 `atomic_write_verify` 的入口生效,包括 `set`、`append`、決策指令。這會改變原本「對連結筆記照寫」的行為。`Systems/lumos-cli-write.md` 的總表(約 114 行)和計劃 S3 只講 question-add/set,沒提這個範圍。
- 其他你要我 grep 的句子:「_pq_cf_ok」已經沒有殘留。「另案」在待決問題相關檔案裡沒有過期用法。「照樣寫得進」只剩上面那一處的 docstring。計劃第 168 行 r4 審計紀錄寫「符號連結筆記照樣寫」是歷史紀錄,可留。
- 歸因:有證據的修復回歸(文件沒跟上)。

**t_qfm_r4_folds 的兩處改法:**
- ③ 從「寫得進」改成只斷言「不含沒拿」,是誠實的反轉。嚴格的行為由 r5 ④ 接手:rc 2、講明符號連結、連結與目標都不變,庫內庫外兩種都測。
- ② 從「合法長旗幟放行」改成「兩萬個標籤字照擋且 1 秒內」。計時仍在,但新的 `fullmatch` 本身是定長比對,舊的平方級路徑已不存在。所以計時只是補充,沒有丟掉原本要守的東西。

**圖譜鏡頭(固定席):**
- `lumos lint` 對計劃和 `Systems/lumos-cli-write.md` 都是 0 問題。
- `Systems/lumos-cli-read.md` 第 232 行的 `_pq_scan` 文法描述沒提切斷規則。這不算錯,但看不出 r5 的改法。
- `Systems/規格閘.md` 和 `Systems/pitfalls-code-loop.md` 沒有與這輪衝突的句子。規格閘那篇也沒提推送前提醒檔名會清洗,屬遺漏,不算過期。
- S1、S4–S7 與程式、測試一致。S2 和讀法的「像題號」兩處對不上程式(見第 1 條)。S3 的符號連結、summary-line 逾時有測試釘住,字面成立。

**三問:**
1. 原問題的行為證據。
   - 通過的部分:阻塞題寫在 lands_in、兩個單行鍵之後、空值鍵、空 decisions、summary 區塊之後,或題目行用 text 開頭、縮 3 格、`id:Q2`、加引號,都能擋。修後與 r5 自己的測試實測為 `t_qfm_r` 系列 111 條全過。
   - 通過的部分:大寫、過長、夾空白的旗幟標籤字,和補充區異體選擇符都擋。
   - 例外:題號寫歪就繞過(第 1 條)。
2. 修補處的相鄰路徑。
   - 正常路徑仍成立:decisions 帶註解、摘要條列寫 id、清單後接三個欄位都讀得懂,gbeng、gbsct、gbwls、usca 與單一 FE0F 放行。
   - 錯誤路徑:符號連結擋下,summary-line 逾時回 rc 2。
   - 相鄰路徑出問題:CRLF 的 git blob(第 2 條)和摘要裡的 `id: Q<n>`(第 3 條)。
3. 新發現的同一案例,修前修後各是什麼結果。
   - 第 1 條:修前 spec-gate rc 1,修後 rc 0。
   - 第 2 條:修前報錯,修後靜默。
   - 第 3 條:修前讀得懂,修後擋。
   - 第 4 條:修前修後一樣放行。

這輪修補在驗收上有一個會擋合併的問題:第 1 條把阻塞題的靜默放行重新打開,其餘五條都是 minor。
