severity: minor

## 已驗主張與證據

我在 `/tmp/lumos-seat-work/code-新寫句子寫法提醒/正確性r2-sonnet/` 下各 clone 一份修前版(`b`,83067c94)和修後版(`a`,9231d216)做對照。

**① 原問題的修復效果**
- 我把修後版的測試檔複製到修前版,跑 `python3.14 scripts/test_lumos.py -k note_wording`,結果是 23 過 6 紅。
- 紅的是 t_note_wording_paren_any_depth 的兩條斷言、t_note_wording_def_shapes 的三條斷言,以及 count_quiet 新增的 O/P/Q 案例。
- 修後版同一組測試是 29 過 0 紅。這三組新增案例對修前版會翻紅,對修後版全綠。
- 修前版對「同檔有真定義加另一支檔字串裡的假定義」會判成兩處定義而不提醒,修後版會印出 `[count:src/k.py::KINDS=3]`。這是我自己補的案例,不在作者的測試裡。
- 最外層才認的括號,在 50000 層巢狀下修前版沒命中,修後版命中,位置正確。

**② 修補處的鄰近路徑**
- `_count_rewrite` 的正規式:我用 `rf"(?<![{E}])3(?![{E}])"` 和舊寫法逐字比對,兩者完全相同。drift fix 相關的 `-k count` 共 267 過 0 紅,drift fix 的行為不變。
- `_ns_wd_paren_groups` 改成每個右括號配最近的未配左括號:
  - 多群同行(`(更正:甲)(更正:第 2 項)`)能逐群看,第一個含位置字眼的就回報。
  - 「外層不是更正括號、內層是」和「外層是、內層含位置字眼」兩種都正確。
  - 雜散的右括號和沒收尾的左括號都不影響後面的群。
  - `(說明 (更正:第 3 項` 兩個都沒收尾,不提醒,屬合理。
  - 舊行補括號的 `cut` 判斷對巢狀群仍成立。
  - 5 萬層巢狀只多花 0.3 秒。
- `_ns_wd_in_string`:
  - CRLF:多行字串的行號和 `count("\n")` 一致。
  - 夾雜 `\r`、`\x0b`、`\x1c`、` ` 的字串:不會讓行號錯位。
  - 反斜線續行字串:有算進 span。
  - 巢狀 f-string:判定正確。
  - 檔案帶 BOM:仍能正常提醒。
  - tokenize 失敗(語法錯、混用 tab、未收尾字串、括號超過 200 層)時整支檔當不可信,該檔的定義不算。drift scan 的 `_count_eval` 對整支檔 `ast.parse`,同樣會判不了,兩邊一致。
  - 無效跳脫序列不會漏出 SyntaxWarning。
- 效能:
  - 用本 repo 的全部 .py 加 `scripts/lumos`,點名 1224 個不同名稱,耗時約 2.7 秒、峰值約 17 MB。
  - 50 個名稱的上限只限 `_count_eval` 的次數,不限 `_ns_wd_in_string` 的次數。我造了一支含 10 萬個多行字串的檔,點名 3000 個名稱,花了 14.6 秒(名稱數乘 span 數)。這是刻意造的極端輸入,真實 repo 量級沒問題,所以我沒列成 finding。
- 小行為差異:ASCII 冒號、斜線、減號緊貼數字(`` `KINDS`:3 種 ``)現在不提醒,修前會。這是共用 `_COUNT_NUM_EDGE` 的預期結果,測試 Q 也明文釘住,所以我沒列成 finding。

**③ 本案特定鏡頭(只提醒不擋)**
- `_ns_wording_collected` 在 try 之外,但它只做 `box.get`、對 `(路徑, 行號, …)` 元組 `sorted`、印 warns,我找不到會丟例外的輸入。
- 同層的 `_ns_tag_hints_collected` 也沒包 try,寫法一致。
- 判定本體和讀設定丟例外時,只印一句「沒跑完」、rc 不變,否定現況句與前綴提醒照常出,這由 t_note_wording_isolated 覆蓋,且該測試過了。
- 這個測試沒有直接對 `_ns_wording_collected` 注入例外。
- `--diff` 模式 `wbox` 為 None 時 emit 直接返回,行為和修前一致。
- 帳本的 check=wording 事件和其他 hinted 事件共用結構,沒有消費端會因多一種 check 值而壞。

**manifest 與圖譜**
- manifest 共 2693 條,沒有任何一條落在 diff 新增行上,沒有要判真隱患或誤報的項目。
- 我另外用 ruff 重跑:RUF001 的全形字元在專案設定的 allowed-confusables 內;B905 指的 `zip(bounds[::2], bounds[1::2])` 兩邊長度必相等,是誤報。
- 固定席的機械反查三格皆空,沒有圖譜合約要答。

**未驗範圍**
- 非 Python 3.14 的行為,專案下限是 3.14。
- 上輪席報告和作者的因果結論,依指示沒讀。
- 修前、修後只有一個提交,測試和產品碼無中間點,所以「歸因」靠兩版對照得出。

## Findings

### F1 多行 t-string(Python 3.14)裡頂格的假定義沒被排除,和 f-string 修補同族
severity: minor
blocking: 否 — 只提醒不擋;失敗模式是少一則提醒,rc 不變。
引句:「elif tok.type == getattr(tokenize, "FSTRING_START", -1):」
失敗場景:`src/k.py` 內容為
```
S = t"""
FOO = ("p","q","r") {x}
"""
FOO = ("a","b","c")
```
筆記寫「`FOO` 有三種」。
- `_NS_WD_DEF_RE` 找到兩個頂格 FOO。
- `_ns_wd_in_string` 只認 STRING 和 FSTRING_START/END。3.14 的 t-string 斷成 TSTRING_START/MIDDLE/END,假定義那行被判成真定義。
- 兩處定義導致 `len(defs) == 1` 不成立,`_ns_wd_resolve` 回 None,本該印出的 `[count:src/k.py::FOO=3]` 不出。
- 實測修後版兩個定義都回 False、resolve 回 None。
- 修前版也是 None,與 f-string 修法留下同樣的缺口。

歸因:有證據的原有漏查(修前、修後都是 None,修補只補了 FSTRING 一族,沒補 TSTRING)。
查證命令:
- `python3.14 -c "import tokenize;print(hasattr(tokenize,'TSTRING_START'))"` 回 True。
- 對上述原文呼叫 `_ns_wd_in_string`(修前 b、修後 a 兩版),結果都是 `[False, False]`。
佐證行:file: `/Users/enzo/lumos-note-nudge/scripts/lumos:31399`

### F2 `_COUNT_NUM_RE` 的位數理由註解被搬到 `_COUNT_NUM_EDGE` 那一行尾端
severity: minor
blocking: 否 — 只影響閱讀,不影響行為。
引句:「_COUNT_NUM_EDGE = r"0-9A-Za-z_./:\-"      # 句子裡的數字前後緊貼這些字就不是獨立數字」
失敗場景:
- 修補把原本掛在 `_COUNT_NUM_RE = re.compile(r"[0-9]{1,9}")` 後面的註解(九位數以內,超長數字轉整數會丟例外,r1 F4)接到 `_COUNT_NUM_EDGE` 新註解尾端,中間只隔一串空白。
- 讀者會以為九位數限制屬於邊界字元集。
- 真正需要這個理由的 `_COUNT_NUM_RE` 變成沒有說明,下次有人想放寬 `{1,9}` 就看不到會丟例外的警告。
- 實測 `sed -n 36513,36514p scripts/lumos`,第 36514 行有 152 個字元,尾端是「# 九位數以內:…」。

歸因:有證據的修復回歸(修前該註解在 `_COUNT_NUM_RE` 同一行,修後被搬走)。
查證命令:`git -C a diff 83067c94 9231d216 -- scripts/lumos | grep -n '九位數以內'`,顯示舊行被刪、新行掛在 EDGE 行尾。
佐證行:file: `/Users/enzo/lumos-note-nudge/scripts/lumos:36513`、file: `/Users/enzo/lumos-note-nudge/scripts/lumos:36514`

總結:共 2 條,最高 minor
