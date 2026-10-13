severity: major

我在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r6-邊界輸入-sonnet/` 下造了暫存庫,實跑 lumos 指令並直接呼叫函式。舊版取自 `afb9e0da` 的 `scripts/lumos`,存成同目錄的 `lumos_old.py`。

**逐條發現**

1. 切斷檢查寫得太窄,阻塞題躲過去後規格閘放行。

引句:「_PQ_CUT_RE = re.compile(r"""^[ \t]*(?:-[ \t]*)?id:[ \t]*["']?Q[1-9][0-9]{0,5}["']?[ \t]*$""")」

severity: major
blocking: 是

- 佐證:file: `scripts/lumos:6912`、`scripts/lumos:7043`
- 最小重現:
  - 開頭欄位依序是 `pending_questions:`、一題已驗的 Q1、頂格 `reason: x`、`  - id: Q2 # x`、`    text: 阻塞題`、`    blocking: true`、`    status: 待查`、`decisions:`。
  - 跑 `lumos spec-gate Projects/V2 --no-run`,印出 `待決問題: ✓ — 1 題,沒有擋進實作的`。
  - lint 只報 `reason` 是沒見過的鍵,以及 Q1 的測試警告,沒有一條說清單被切斷。
- 同樣漏掉的寫法,把 `# x` 換成下列任一種,規格閘都放行:
  - `id: Q2x`
  - `id: q2`
  - `id: Q２`(全形)
  - `id: Q2;`
  - `id: Q02`
  - `id: Q1000000`
  - `id: Q2\r`(行尾字面反斜線 r)
- 前後對照:
  - 修前:`_PQ_CUT_RE` 是 `^  - id:(?: |$)`,上述情形全部報「這一題寫在清單範圍外」。實跑修前版,`# x`、`Q2x`、`q2`、全形、`Q2;`、`Q02`、`Q1000000`、`Q2\r` 都被擋。
  - 修後:規格閘全部 `✓` 放行。
  - 兩版都漏的:`ID: Q2`、`id : Q2`、`"id": Q2`。
- 歸因:有證據的修復回歸。
- 查證命令:同一份筆記先跑 `python3.14 lumos_old.py --vault <庫> spec-gate Projects/V2 --no-run`,再跑 `python3.14 scripts/lumos --vault <庫> spec-gate Projects/V2 --no-run`。第一條回 `✗ … 清單無法判定`,第二條回 `✓`。
- 修法方向:切斷後只要還有縮排行、或行首像 `- id`(不論大小寫、冒號前空白、值寫什麼),一律擋;不要要求整行完全符合題號形狀。

2. 工具自己的 `summary-line` 可把「新片段」寫成單獨一行 `id: Q3`,之後整份清單讀不懂。

引句:「if _PQ_CUT_RE.match(fm_lines[k2]):」

severity: minor
blocking: 否

- 佐證:file: `scripts/lumos:7043`
- 重現:
  - `lumos summary-line Projects/T "KEY: 第一行" "id: Q3"` 回 rc0,沒有任何提示。
  - 摘要區成了 `  id: Q3`。
  - `lint` 報「待決問題清單無法判定 … 第 23 行頂格的 'decisions' 把清單切斷了」。
  - `spec-gate --no-run` 報 `✗ … 清單無法判定`。
- 這是擋下方向,不會放行阻塞題,但寫入端沒有擋。
- 其他指令都安全:`decision-add`、`question-add`、`append`、`decision-amend`、`decision-supersede`、`signoff` 等工具會把含 `id: Q1`、`- id: Q9` 的內容加引號寫出。每一步之後 lint 和 spec-gate 都正常。
- 前後對照:
  - 修前(`  - id: Q3` 在摘要區):清單可讀,2 題阻塞照常列出。
  - 修後:同一份筆記擋下,理由是「清單被切斷」。
- 歸因:有證據的修復回歸,但需要手動把摘要寫成裸 `id: Q<n>`,實務罕見。
- 查證命令:同發現 1,對象換成 `Projects/T`。

3. `summary-line` 的寫檔失敗沒有轉成擋下訊息,印出堆疊追蹤。

引句:「except (ValueError, RuntimeError) as ex:」

severity: minor
blocking: 否

- 佐證:file: `scripts/lumos:20211`
- 重現:`chmod 555 <庫>/Projects` 後跑 `lumos summary-line Projects/R 甲乙 丙`,印出 `PermissionError: [Errno 13]` 堆疊,rc1。
- 對照:同情境的 `question-add` 回 `擋下:[Errno 13]…`,rc2。
- 修補處註解寫「寫入原語丟的錯轉成擋下訊息、rc2,不印堆疊」,但只接 `ValueError` 和 `RuntimeError`,漏了 `OSError`。
- 歸因:有證據的原有漏查。修前版同樣 rc1 並印堆疊,不是這輪新增的。
- 查證命令:`python3.14 lumos_old.py --vault … summary-line …` 與新版,兩邊都是 `rc=1 PermissionError`。

4. 看不見的字元還有漏網,且整段只含這些字元的值不算空值。

引句:「_PQ_INVISIBLE = "\u2800\u3164\u115f\u1160\uffa0\u034f"」

severity: minor
blocking: 否

- 佐證:file: `scripts/lumos:6918`、`scripts/lumos:6968`、`scripts/lumos:6955`
- 實跑 `_pq_bad_char` 與 `_pq_blank`,下列字元都沒被擋:
  - U+180B、U+180C、U+180D、U+180F(蒙古文變體選擇符)。`"a\u180b\u180c"` 回 `None`,連續兩個也不擋,因為 `_pq_is_vs` 只涵蓋 FE00–FE0F 與 E0100–E01EF。
  - U+17B4、U+17B5。
  - U+FFFC。
  - U+1D159。
- 單獨一個 U+17B4 或 U+180B 的值,`_pq_blank` 回 `False`,也就是 `text` 可以是「畫面上空白」卻通過。
- 有擋到的:U+180E、E0001、1D173、U+2062 到 U+206F 都擋。
- 通過的 emoji 都是合法的:英格蘭、蘇格蘭、威爾斯、`usca`、`fr75c`、`jp13` 旗幟,兩個旗幟相連,旗幟後接 VS16,ZWJ 家庭 emoji。
- 該擋的有擋到:四字分區碼、數字地區碼、沒收尾的標籤字、非旗幟後面的標籤字。
- 歸因:有證據的原有漏查。修前版對這些字元結果相同(`old_bad=None`)。
- 效能:200 萬個標籤字、100 萬個變體選擇符、2 萬題加 20 萬行尾巴,都在 0.3 秒內。

5. 筆記本身是壞掉的符號連結時,`append`、`set`、`summary-line` 印堆疊。

引句:「raise RuntimeError(f"這篇筆記是符號連結(指到 {_esc_clean(os.readlink(path), 160)}),寫進去會把連結換成一般檔、它指到的那篇不會改;"」

severity: minor
blocking: 否

- 佐證:file: `scripts/lumos:19962`
- 這三個指令在寫檔之前就先讀檔,在讀的那一步炸出 `FileNotFoundError`,rc1。
- 其他指令正常:`question-add`、`decision-add` 和 `question-set` 回 rc2、訊息是 `[Errno 2]`,不是符號連結訊息。
- 歸因:有證據的原有漏查。修前版 `append` 同樣丟 `FileNotFoundError`、rc1,是前置讀檔的缺口,不是這輪的符號連結擋下造成的。
- 符號連結的其餘情況都正確:
  - 庫內連結、庫外連結:`question-add`、`decision-add`、`append`、`set` 都回 rc2,訊息講明「這篇筆記是符號連結」,連結和被指的檔 md5 不變。
  - 資料夾連結:筆記根本不被索引,回「找不到」。
  - 整個 vault 是連結(`vlink`、`rlink`):全部指令照常寫入。

**圖譜鏡頭**

- 我查了 `lumos-cli-read.md`、`lumos-cli-write.md`、`規格閘.md`、`pitfalls-code-loop.md`,範圍在 `切斷`、`像題號`、`符號連結` 這幾個詞。
- 沒有一條筆記宣稱「`_PQ_CUT_RE` 涵蓋大小寫、全形、尾巴」,所以筆記本身沒跟程式矛盾。
- `lumos-cli-write.md` 第 151 行的 WHY 寫「守衛子指令在分派層統一接,讀寫失敗也一併回擋下 rc2」。`summary-line` 不在守衛路徑,筆記沒說它的 `OSError` 要轉擋下,和發現 3 的缺口一致。

**三問**

1. 原問題的修復效果:
   - 標準寫法(`  - id: Q2`、`  -  id: Q2`、Tab 縮排、縮 1 或 3 格、冒號後無空白、單引號沒收尾)都被擋,規格閘報「清單無法判定」。
   - 旗幟:真實旗幟放行,四字分區碼被擋。
   - 符號連結:庫內、庫外都擋,且不改被指的檔。
   - 但整體的行為證據是反向的:切斷偵測比修前版更窄(發現 1),原問題換了形狀,仍會讓阻塞題靜默消失。
2. 修補處的相鄰路徑:
   - 工具自己寫出的 decisions、lands_in、related、tags、signoff 內容全加引號,切斷檢查不誤擋,正常、錯誤路徑都成立。
   - 手寫的邊界寫法(發現 1)和 `summary-line` 的新片段(發現 2)不成立。
   - 鎖逾時回擋下 rc2 的路徑成立,但 `summary-line` 的 `OSError` 路徑不成立(發現 3)。
3. 同一案例的修前、修後:
   - 發現 1(`# x`、`Q2x` 等):修前擋下,修後放行。
   - 發現 2:修前可讀,修後擋下。
   - 發現 3、4、5:修前修後相同。

總結:五條發現裡只有第一條會擋合併,它是這輪修補把偵測範圍縮小造成的回歸,已用前後兩版同輸入重現;其餘四條都不擋合併,也沒有因為重現不了而降級的情形。
