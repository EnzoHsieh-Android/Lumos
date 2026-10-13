severity: major

我對這輪修補的結論:切斷新規則、旗幟形狀、符號連結擋下都對。但找到一個會讓閘放行的洞,和一個修補自己引入的小回歸。

1. 清單範圍結束後,頂格那一行本身不檢查,而且正規式只認 ASCII 空白,所以用不斷行空白或全形空白縮排的阻塞題整題消失,規格閘放行。(正確性;相關題號 be-api-compat 不適用)
severity: major
   blocking: 是
   引句:「for k2 in range(i + 1, len(fm_lines)):」
   佐證 file: `scripts/lumos:7046`(從 i+1 掃,跳過觸發切斷判斷的那一行自己)、`scripts/lumos:6915`(`_PQ_CUT_RE` 用 `[ \t]*`)。
   - 輸入:Q1 照常寫,Q2 的每一行都用兩個 U+00A0 縮排(U+3000、U+200B 加空白也一樣),後面接 `updated:`。這種縮排常見於從網頁或 Word 貼來的文字。
   - 走法:`raw[0]` 不在 `" \t"`,被當頂格行。`_pq_top_key` 回 `"- id"`,範圍就此結束。後面幾行沒有 ASCII 縮排的 `id:`,沒有任何錯誤,Q2 被丟掉。
   - 最小重現:`/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r6-正確性-sonnet/p11.py`。同一份計劃,全 ASCII 縮排時 `lumos spec-gate --no-run` 回 rc1 並列出 Q2;換成不斷行空白縮排時回 rc0,印「1 題,沒有擋進實作的」。
   - 兩版:`p10.py` 在 afb9e0da 和 5498fec8 都得到 `qs=['Q1'] errs=[]`。
   - 歸因:有證據的原有漏查。修前修後行為一樣,但這輪規則自稱「用長什麼樣判」,這個洞沒補到。
   - 補法:把頂格那行自己也納入檢查,正規式改用 `\s`。

2. 切斷檢查改成直接比對原始行,沒有先 `rstrip`。CRLF 的 `id: Q2\r` 因為 `[ \t]*$` 不認 `\r`,不再被抓。
severity: minor
   blocking: 否
   引句:「if _PQ_CUT_RE.match(fm_lines[k2]):」
   佐證 file: `scripts/lumos:7047`。修前是 `nxt = fm_lines[k2].rstrip()` 後再比對。
   - 受影響的是推送前提醒(`_pq_push_remind`):它讀 git blob 的文字,CRLF 原樣保留。
   - 規格閘和 lint 用 `read_text`,換行已被轉成 `\n`,所以仍然擋得住,影響只在提醒。
   - 重現:`p2.py` 的 CRLF 一行,修前 `errs` 有切斷錯誤,修後 `errs=[]`、`qs=['Q1']`。`p4.py` 把 lf 與 crlf 兩份計劃提交後跑推送檢查,只有 lf 那份得到提醒。
   - 歸因:有證據的修復回歸。計劃 S2 也寫了「CRLF 不應讓它讀不懂」。

3. 「看不見的字算空值」沒補全。Khmer 的 U+17B4、U+17B5 和 Mongolian 的 U+180B 到 U+180D、U+180F 單獨出現時,`_strict_scalar` 都當成非空。
severity: minor
   blocking: 否
   引句:「_PQ_INVISIBLE = "\u2800\u3164\u115f\u1160\uffa0\u034f"」
   佐證 file: `scripts/lumos:6908`。
   - `p8.py` 顯示這六個碼位不管有沒有加引號,`_strict_scalar` 都回 `None` 錯誤,也就是通過。
   - `question-add` 因為共用 `_pq_blank`,同樣收這種題目文字。
   - 修前修後行為一樣。歸因:有證據的原有漏查。這輪只補了其中一部分。
   - 另外 ⚠:單一異體選擇符夾在每個可見字之後仍可通過,每字可藏約 4 位元。我沒實測,所以只標未判定。

4. `summary-line` 遇到符號連結時,先印「改前/改後」兩行,再回擋下 rc2。
severity: minor
   blocking: 否
   引句:「if os.path.islink(path):」
   佐證 file: `scripts/lumos:19982`。
   - `p6.py` 顯示 stdout 有「改前:…改後:…」,同時 rc2 且檔案沒動,看起來像改了。
   - 沒有半寫:各指令前後快照比對,庫內庫外兩種連結的 `changed=[]`。
   - 修前沒有這條擋下路徑,所以這是修補新增的畫面不一致。歸因:有證據的修復回歸。

5. `t_qfm_r5_folds` 抓不到上面第 1、2 條,也抓不到第 3 條。
severity: minor
   blocking: 否
   引句:「check(f"① 反例:清單外的題目行{nm} → 讀不懂", bool(errs), (errs, [q['id'] for q in qs]))」
   - 我判它是真實測試:`-k qfm_r5` 37 案全過,反例檢查的是 `errs` 非空,拿掉切斷規則會紅。
   - 缺口:反例固定用 `\n` 與 ASCII 空白,沒有 CRLF 的 blob、沒有不斷行空白縮排、旗幟只驗放行與擋下的字串形狀。
   - 歸因:未判定,是測試覆蓋不全。

圖譜鏡頭(四節點)
- `lumos-cli-write.md`:符號連結「不寫、講明」的說法與實測一致,八支指令加 `decision-supersede`、`decision-reindex`、`self-audit`、`guard audit` 都是 rc2 無追蹤。
- `lumos-cli-write.md` 另寫了「守衛讀寫失敗一併回 rc2」,與程式一致。
- `lumos-cli-read.md`、`規格閘.md`、`pitfalls-code-loop.md`:只講「清單讀不懂回 1/2」,沒有跟上這輪的切斷規則細節。
- 計劃 S2 寫「CRLF 不應讓它讀不懂」,CRLF 只在推送前提醒那條路上被切斷規則漏掉(第 2 條)。這只是計劃條款與程式不一致,不是圖譜節點的矛盾。
- 全 repo 沒有符號連結筆記,擋下不會影響現有內容。

角色鏡頭
- be-api-compat:這是命令列工具,沒有對外 API。行為相容上有兩處變化:
  - 符號連結筆記從「能寫」變成 rc2。
  - `summary-line` 拿鎖逾時從追蹤變成 rc2。
  - 兩者都是刻意的,計劃有寫。
- be-authz:不適用。符號連結指到庫外時,過去能繞過鎖的範圍去改庫外檔案,現在擋住了,方向正確。
- 硬連結筆記:原子換名後也會悄悄分成兩份,沒被擋。我沒測,⚠ 未判定。

三問
- ① 原問題修復效果:
  - 阻塞題寫在 `lands_in`、`tags`、`reason`、`summary` 之後,或縮 3 格、tab、`id:Q2`,都被擋。
  - `id: Q２`、`ID: Q2`、`id: q2` 在清單外不被抓,但別的讀者本來也不會當成題。
  - 清單內這些寫法都報錯,沒有漏掉。
  - 854 篇現存筆記跑修前修後兩版,結果零差異,沒有誤擋。
  - 旗幟:`gbeng`、`gbsct`、`gbwls`、`usca` 放行,`gbengx`(6 字)、大寫、數字開頭被擋。
  - 符號連結與鎖逾時如上所述。
- ② 修補處的相鄰路徑:
  - 正常路徑(LF、ASCII 縮排、工具自己寫的決策與摘要)都成立。
  - 錯誤路徑有兩處不成立:CRLF 的 blob(第 2 條)和不斷行空白縮排(第 1 條)。
- ③ 新發現案例的修前修後:

| 案例 | 修前 | 修後 |
|---|---|---|
| 第 1 條不斷行空白縮排 | 靜默丟題 | 靜默丟題(相同) |
| 第 2 條 CRLF | 報切斷 | 不報(回歸) |
| 第 3 條 U+17B4 等 | 通過 | 通過(相同) |
| 第 4 條 summary-line 符號連結 | 照常寫入 | 先印改前改後再 rc2 |

總結:切斷規則對 ASCII 與 LF 的輸入成立,但有一處能讓閘放行的老洞(第 1 條,major、阻塞)和一處修補引入的小回歸(第 2 條),其餘為次要。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/qo-frontmatter/scripts/lumos`
- 實驗腳本在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r6-正確性-sonnet/`(`p2.py`、`p4.py`、`p6.py`、`p8.py`、`p10.py`、`p11.py`)。
