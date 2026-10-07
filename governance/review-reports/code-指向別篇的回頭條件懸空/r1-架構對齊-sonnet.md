severity: major

我有看到「lumos 自動附加」段,列了 8 篇固定席筆記(都是 lumos-cli-read、lumos-cli-lifecycle 這類 Systems 家節點),另有 13 篇只列名。

## 三問

1. 分層與依賴方向:對齊。
   - 新碼放在 `_doctor_replacement_lines` 之後、`_METRIC_CMP` 之前(`/tmp/code-a3/lumos_r1.py:4065-4125`)。
   - 呼叫方向是 `run_doctor` → `_doctor_revisit_ref_lines` → `_revisit_ref_dates`、`_revisit_ref_hits` → `_search_visible_lines`、`_revisit_split`、`_probe_parse`、`_inline_hidden`、`env.resolve`。
   - 這跟 S17、S19、S20 一樣:只讀 `env`,不跨層呼叫。
   - 治理帳不寫、不計入問題數、用 `warn_soft` 兩段文字、輸出行包 `_esc_clean(..., _DOCTOR_LINE_MAX)`,都跟鄰居一致(S17 在 `:4048-4061`,S19 在 `:4234-4258`)。
   - S21 排在 S20 之後、S8 之前,沿用 S16–S20 的位置紀律。

2. 命名與錯誤處理:大體對齊,有兩處小偏差。
   - 命名:`_doctor_revisit_ref_lines` 跟 `_doctor_replacement_lines`、`_doctor_fact_recheck_lines`、`_doctor_test_ref_lines` 同一型。
   - 錯誤處理:S21 沒包 try。S17 和 S19 也沒包,只有 S18 和 S20 包了,所以鄰居本身不一致,不算偏差。
   - 偏差一:筆記迭代沒排序(A4)。
   - 偏差二:解析連結時沒走 `link_target`(A2)。

3. 第二種做法:有。
   - `_revisit_ref_dates` 是第二份讀回頭條件行的實作(A1)。
   - 連結正規式和日期正規式也各多了一份(A2、A3)。
   - 切句用 `split("。")` 是 `scripts/lumos` 裡第一次出現,沒有既有切句函式可比,不列。

## A1 `_revisit_ref_dates` 是 `_revisit_lines` 之外的第二份回頭條件讀法
severity: major
blocking: 是
引句:「for _no, raw, _pr in _search_visible_lines(text.split("\n"), False):」
佐證:file: `/tmp/code-a3/lumos_r1.py:35296`(`_revisit_lines` 的同一條流水線:可見行 → `_strip_inline_markup` → `_revisit_split` → `_probe_parse`)
佐證:file: `/tmp/code-a3/lumos_r1.py:35218`(`_revisit_closed` 才是「判結案」的唯一處)
佐證:file: `/tmp/code-a3/lumos_r1.py:35496`(`_probe_lines` 也自成一份,但它的用途是只取條件式)
- `_revisit_lines` 的 docstring 寫明它是 E5 與 `lumos set` 結案列出「共用這一支」,而且「不另加參數」。
- 新函式整段複製同一條流水線,只差一點:不跳過已結案的行。
- `_revisit_ref_dates` 自己的 docstring也承認這點(「同 `_revisit_lines` 的可見行與行內程式碼剝法,只是不跳過已結案」)。
- 正解是在 `_revisit_lines` 加一個不排除結案的路徑,或把迴圈抽成共用函式。現在這樣是三份同形迴圈。
失敗場景:
- 日後有人改 `_revisit_lines` 的可見行規則或「bad」種類的處理(例如表格行、開頭欄位的處理),S21 不會跟著變。
- 接手的人以為 S21 跟 E5 看的是同一批回頭條件行。
- 結果是 doctor 一邊說「那篇有這條」、另一邊說「沒有」。

## A2 連結正規式另寫一份,且解析時沒走 `link_target`
severity: minor
blocking: 否
引句:「_RREF_LINK = r"\[\[([^\[\]|#\n]+)(?:[|#][^\[\]\n]*)?\]\]"」
佐證:file: `/tmp/code-a3/lumos_r1.py:415`(`WIKILINK_RE`)
佐證:file: `/tmp/code-a3/lumos_r1.py:4025-4030`(S17 的 `_slot_replacement_dead`:`WIKILINK_RE.search` 加 `env.resolve(link_target(ref))`)
- 專案已有 `WIKILINK_RE`,連結正規式本來就有多份,例如 `:7376`、`:25006`、`:45958`,所以鄰居本身不一致。
- 新碼挑了最像 S17 的路線,卻漏了 `link_target`:新碼是 `trel = env.resolve(tgt)`,S17 是 `env.resolve(link_target(ref))`。
- `link_target` 負責去引號、`.md` 後綴和 nfc 正規化。
- 新正規式內文已排除 `|` 與 `#`,所以別名和標題不受影響。引號與 nfc 沒處理到。
- ⚠ 新碼加正規式的理由(回溯成平方)是實測過的。「該不該改 `WIKILINK_RE`」是鄰居本身的分歧,交編排者。
失敗場景:
- 筆記裡寫 `[[Systems/X.md]]` 沒問題,`resolve` 會去掉 `.md`。
- 但目標含全形引號,或 Unicode 組合形不同時,`resolve` 回 None。
- S21 就靜默不列,跟 S17 對同一種寫法的行為不同。

## A3 日期正規式新增一份獨立常數
severity: minor
blocking: 否
引句:「_RREF_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")」
佐證:file: `/tmp/code-a3/lumos_r1.py:416`(`DATE_PREFIX_RE`)
佐證:file: `/tmp/code-a3/lumos_r1.py:18912`(`DATE_RE`)
佐證:file: `/tmp/code-a3/lumos_r1.py:35190`(`_REVISIT_ANY_RE` 內嵌同一形狀)
- `DATE_RE` 與 `DATE_PREFIX_RE` 都是錨定版,新碼要的是不錨定的搜尋版。
- 專案裡這個形狀有十幾處各自內嵌,沒有共用常數,所以鄰居本身就不一致。
- ⚠ 交編排者。
失敗場景:
- 低風險。日期形狀不會改,漂移的可能性小。
- 只是 `_RREF_DATE_RE` 與 `_RREF_AFTER_DATE_RE` 在同一區塊裡把同一個形狀寫了兩次。

## A4 掃描筆記的迭代沒排序
severity: minor
blocking: 否
引句:「    for rel in env.notes:
        text = env_text(env, rel)」
佐證:file: `/tmp/code-a3/lumos_r1.py:32483`(S20 用 `for rel in sorted(env.notes)`)
佐證:file: `/tmp/code-a3/lumos_r1.py:4006`(`_slot_summary_entries`,S17 與 S19 的底層,也是 `sorted(env.notes)`)
- S17、S19、S20 的迭代順序都是排序的,S21 不是。
- 專案裡也有未排序的迭代(`:4117` 之外還有 `:18309`、`:18320`、`:12450`),但同層的 S16–S20 全部排序。
- S21 這段的列出順序跟 `warn_soft` 的「預設只列前 3 條」有關。
失敗場景:
- 同一份圖譜,在不同機器或不同載入順序下,被截斷後看到的前 3 條不同。
- 接手的人比對兩次 doctor 輸出會對不上。

不對齊共 4 條,其中重大 1 條
總結:新增的 S21 在放哪一層、誰呼叫誰、輸出和記帳寫法上都跟 S16 到 S20 一樣,但「讀回頭條件行」另寫了一份,跟現有的 `_revisit_lines` 平行,以後兩邊容易改岔。
