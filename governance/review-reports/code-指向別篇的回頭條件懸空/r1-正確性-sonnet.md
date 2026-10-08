severity: minor

我看到「lumos 自動附加」段,列了 9 篇有內容的節點(lumos-cli-read、lumos-cli-lifecycle、測試假綠形態、guard-kill、design-loop、bound-tests-gate、授權與歸屬、loop-convergence-recording 等),另有 12 篇只列名。逐條對照:這份 diff 沒碰 search 的 superseded 濾網、re-inject sentinel、guard kill rc 與 JSON、處置閘第五步、bound-tests 閘、授權白名單。它只在 doctor 主流程加一段軟提醒 S21,另加幾個新函式。這些合約都沒有被破壞。唯一跟這些節點的接觸點是 S21 插在 S8 之前,軟段截斷的測試仍綠。

本案特定鏡頭的結果:
- 在臨時 clone 跑 `doctor`:S21 印「指向別篇的回頭條件都還在」,0 筆。
- 對 rtb 圖譜載入函式:回傳 `[]`。
- 兩邊都沒有誤報。漏報看下面 F1、F2。
- `-k s21_revisit_ref`(21 條)與 `-k soft`(11 條)全綠。

## F1 連結名稱含待辦詞時整條被排除
severity: minor
blocking: 否
引句:「span = raw[a:b + _RREF_TAIL].split("。")[0]」
佐證:file: `scripts/lumos:4069`
失敗場景:`_revisit_ref_hits` 的待辦詞視窗從連結起點 `m.start()` 算起,把連結的目標名稱也掃進去了。目標名稱含 改寫、改成、改指向、拿掉、刪掉、移除、結案 任一詞時,不管句子本身是什麼,都被當成待辦指示而不列。
- 輸入 `見 [[Systems/結案X]] 的 REVISIT 2026-11-08 再量。`,X 只有 `REVISIT:2026-10-20`:回傳 `[]`。把名稱換成 `Systems/X`,同一句就列出。
- 輸入 `回頭條件見 [[Systems/改成X]]。`,X 沒有任何回頭條件行:回傳 `[]`。
- 真圖譜已有實例。`Projects/漂移修法補強_計劃.md` 第 103 行指向 `Issues/刪除守衛在消費專案把工具更新刪掉的名稱當成專案的`,我用探針確認它是因名稱裡的「刪掉」被排除,不是因為待辦指示。
- 這類節點名在本庫很常見(例如「結案連帶掃描」)。
- 後果是漏報,不會誤擋。
查證命令:`python3.14 /tmp/lumos-seat-work/code-指向別篇的回頭條件懸空/正確性-sonnet/t.py /tmp/lumos-seat-work/code-指向別篇的回頭條件懸空/正確性-sonnet/c`,看 A 與 A3 兩行。

## F2 全形冒號的日期讀不到,退化成不帶日期的比對
severity: minor
blocking: 否
引句:「_RREF_AFTER_DATE_RE = re.compile(r"[`*:: \t]*(\d{4}-\d{2}-\d{2})")」
佐證:file: `scripts/lumos:4069`
失敗場景:字元集裡的冒號寫了兩次 ASCII `:`(用 `ascii()` 印出來確認),看起來原本想放半形加全形。
- 輸入 `見 [[Systems/X]] 的 REVISIT：2026-11-08`(全形冒號),X 只有 `REVISIT:2026-10-20`:`after` 沒匹配,日期變 None,改走「X 有任一條回頭條件就不列」,回傳 `[]`。
- 半形冒號的同一句會被列出。
- 後果是漏報。
查證命令:`t.py` 的 N 行。

## F3 同一行有大量行內程式碼加大量引用時,時間成平方
severity: minor
blocking: 否
引句:「return any(a <= i < b for a, b in hidden)」
佐證:file: `scripts/lumos:4069`
失敗場景:`_in_code` 對每個命中都線性掃過整行所有隱藏區段,而且是 `_RREF_TODO_RE` 判斷之前先算。
- 輸入一行 `` `a` [[Systems/X]] REVISIT 2026-11-08 `` 重複 30000 次(約 1.1MB):`_doctor_revisit_ref_lines` 跑 35 秒。
- 對照:同樣大小、沒有行內程式碼的輸入 0.25 秒。
- 其他病態輸入(兩萬個 `[[`、10 萬個反引號、大量「回頭條件」、大量空白)都在 0.3 秒內。
- 真圖譜 761 篇不會遇到,所以只標輕微。
查證命令:`python3.14 /tmp/lumos-seat-work/code-指向別篇的回頭條件懸空/正確性-sonnet/perf.py /tmp/lumos-seat-work/code-指向別篇的回頭條件懸空/正確性-sonnet/c`,看第一行。

## F4 句尾只認「。」,別的標點會把下一句的待辦詞算進來
severity: minor
blocking: 否
引句:「_RREF_TODO_RE = re.compile(r"改寫|改成|改指向|拿掉|刪掉|移除|結案")」
佐證:file: `scripts/lumos:4069`
失敗場景:
- 視窗只在「。」截斷,`;`、`!`、`?`、英文句點都不截。
- 輸入 `見 [[Systems/X]] 的 REVISIT 2026-11-08 再量; 另外把 Y 改成Z`,X 沒有那天:被當待辦而回傳 `[]`,漏報。
- 計劃文件寫明「到句號為止」,所以這算已知的粗略,不算偏離規格。

另外確認沒問題的邊界,不另開 finding:
- 別名 `[[X|別名]]` 與錨點 `[[X#節]]` 都正確解析。
- 日期 2026-13-40 被當成不存在的日期而列出。
- 引用自己這篇,走一般比對。
- 連結在反引號裡、未閉合反引號、圍欄:都不列。
- `_revisit_ref_dates` 認縮排列表與引用記號,不認表格行,也不認反引號裡的 REVISIT,跟 `_revisit_split` 和 E5 口徑一致。
- 目標讀不到或是空檔:走「沒有」。
- 表格裡 `[[X\|別名]]` 的跳脫管線會讓目標解析成 `X\`,結果靜默不列(漏報,只有輕微影響)。

總結: 這段新增的 doctor 提醒在真圖譜與 rtb 都沒有誤報,測試全綠,也沒破壞牽連節點的合約。有四處輕微漏報或極端輸入變慢,最值得先修的是待辦詞視窗把連結名稱算進去,以及全形冒號的日期讀不到。
