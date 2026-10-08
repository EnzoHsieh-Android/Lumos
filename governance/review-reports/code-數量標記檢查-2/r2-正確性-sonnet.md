severity: major

(實驗檔都在 /tmp/count-r2-work:h.py 載入 scripts/lumos,t1/t2 測 _count_rewrite,t3/t4 測 _count_eval,fz.py 是隨機測試。)

## F1 列舉本體裡看不懂的語句被靜默略過,算出錯的數字而不是判不了
severity: major
blocking: 是
引句:「tgt = st.targets[0] if isinstance(st, ast.Assign) and len(st.targets) == 1 else getattr(st, "target", None)」
佐證:`_count_enum` 的 for 迴圈
1. 輸入 `class X(enum.Enum):\n    A = B = 1`:多重指派 targets 長度 2,走 getattr 得 None,被 `continue` 略過,回 (0, None)。實際 `len(list(X))` 是 1。
2. 輸入 `A, B = 1, 2`:tgt 是 Tuple 同樣被略過,回 (0, None);實際 2。
3. 輸入 `A = 1` 後接 `if sys.version_info >= (3, 0):\n        B = 2`:If 語句根本不是 Assign,迴圈不進去,回 1;實際 2。
4. 標籤寫 `=0` 或 `=1` 就會被判成吻合,drift scan 不列;`drift fix` 還會把句子改成這個錯的現值(`_drift_fix_count` 用 `_count_actual` 的結果)。
這與本輪「Python 對成員的特例一律判不了、不自己模擬」的立場矛盾:無法解讀的本體語句應該回判不了,不是不算。
最小重現:/tmp/count-r2-work/t4.py(multi / tuple / ifbody 三列,lumos= 與 real= 不同);`python3.14 t4.py`。

## F2 auto() 與明寫的值重複時別名沒被認出,多算
severity: major
blocking: 是
引句:「if len(set(consts)) != len(consts):」
佐證:同函式,auto() 的值不進 consts
1. 輸入 `class X(enum.IntEnum):\n    A = enum.auto()\n    B = 1`:A 的實際值是 1,B=1 是別名,實際成員數 1;程式 consts 只有 [1],無重複,回 (2, None)。
2. 輸入 `class X(enum.Flag):\n    A = enum.auto()\n    B = 1\n    C = 2`:實際 2,程式回 3。
標籤寫 2(或 3)就被判吻合,正是「列舉別名判不了」(規格 S2)要擋的情形。修法方向:列舉含 auto() 又含明寫的整數常數時一律判不了。
最小重現:/tmp/count-r2-work/t4.py 的 autodup / autoflag。

## F3 定義之後被整個重新綁定的名稱沒被 _count_mutated 認出
severity: major
blocking: 是
引句:「if isinstance(nd, ast.AugAssign) and isinstance(nd.target, ast.Name) and nd.target.id == name:」
佐證:`_count_mutated` 只看增量指派、`_COUNT_MUTATORS` 方法呼叫、下標賦值或刪除;`_count_eval` 的 hits 只收 tree.body 直屬
1. 輸入 `X = (1, 2, 3)\ntry:\n    import nonexistent\nexcept ImportError:\n    X = (1,)`:巢狀區塊裡的 `X = (1,)` 不在 tree.body 直屬,不算第二次定義,也不是 AugAssign/Subscript/Call,回 (3, None);執行時 X 是 1 個成員。
2. 輸入 `X = (1,2,3)\ndef reload():\n    global X\n    X = (1,)\n`:同上,回 3。
3. 輸入 `X = (1,2,3)\nX, Y = (1,), 2`:頂層 Tuple 目標不進 hits,回 3,實際 1。
4. `del X`、`for X in …`、`import … as X`、`def X`、`X.__iadd__([4])`、海象 `(X := …)` 都同樣回 3。
這是上輪 F5「定義後被改過就數不準」的同一類洞,只補了三種形狀。
最小重現:/tmp/count-r2-work/t3.py、t4.py(globalrebind / tryrebind / unpack,lumos= 3、real= 1)。

## F4 句子數字的位置判定與可見性判定不一致,fix 會改到看不見的數字
severity: minor
blocking: 否
引句:「shield = [m.span() for m in re.finditer(r"\[[^\]]*\]|`[^`]*`", line)]」
佐證:`_strip_inline_markup`(`file: scripts/lumos:368`)剝雙反引號 span 並丟掉未閉合反引號之後的內容;`_count_rewrite` 的 shield 只認成對單反引號與方括號
1. 輸入行 `[count:a.py::X=5]`5`(標籤之後有未閉合反引號,尾端的 5 看不見):`_count_lines` 抽得一個標籤 n=5;`_count_rewrite` 把反引號後的 5 當句子數字,回 `[count:a.py::X=6]`6`,重抽通過、寫入。實際被改的是看不見的文字。
2. 輸入行 `共 ``5`` 種 [count:a.py::X=5]`(雙反引號內的 5):shield 以單反引號配對,``5`` 不在範圍內,回 `共 ``6`` 種 [count:a.py::X=6]`,而看得見的句子根本沒有數字,應擋下。
3. 隨機測試 fz.py 30 萬行中 2150 行有此現象。
重抽只驗標籤,不驗只動了看得見的文字。

## F5 句子數字與日期、區間裡的數字不分
severity: minor
blocking: 否
引句:「hits = [m for m in re.finditer(rf"(?<![0-9A-Za-z_.]){old}(?![0-9A-Za-z_.])", line) if not inside(m.start(), shield)]」
佐證:lookbehind/lookahead 允許 `-`、`/`、`,`
1. 輸入行 `2026-10-04 起共十種 [count:a.py::X=10]`,old=10:中文數字不是 hit,日期的月份 `10` 前後是 `-` 被當成唯一的句子數字,回 `2026-11-04 起共十種 [count:a.py::X=11]`,標籤重抽通過,日期被悄悄改掉。
2. 輸入行 `共十八種(見 2026-09-18 事故)[count:a.py::X=18]` 同理得 `2026-09-19`。
`[出處:日期]` 在方括號內被 shield 保護,只有正文裡的日期受影響,所以降為 minor。
最小重現:/tmp/count-r2-work/t1.py 的 rewrite 呼叫(本報告實測輸出如上)。

## 沒有發現的項目(走過的輸入)
- 重疊/相鄰:`5[count:…=5]`、`[count:…=5]5`、`共5種[count…]`、新值 0/4/10 位數變化,由後往前套用位置都正確(t1.py)。
- 名稱含 `=` 的路徑 `a=b.py::X=5` 左半正確;`[count: a.py::X =5]`、`=05` 重寫為正規形。
- `5.0`、`-5`(變 -6 但屬語意問題不計)、`5%`、`[[連結5]]`、`(5)`(兩個 hit 擋下)、URL 內 5(擋下)、全形 ５ 不誤改。
- 未閉合反引號在標籤之前:`_count_lines` 看不到標籤,`_drift_fix_count` 在 len(tags)!=1 先擋,兩邊一致。
- IntFlag、Flag 透過 enum.Flag 屬性基底、值 0、負數(UnaryOp 判不了)、True 皆判不了或正確;一般 Enum、集合去重(1/True/1.0)、字典重複鍵、tuple/list 不去重皆維持舊行為。
- `if __name__ == "__main__":` 底下的 `+=`/`.append` 會被抓到;參數同名與別的類別同名變數會被誤判成判不了(偏保守,可接受)。

## 圖譜判定
- Systems/存量漂移守衛.md 新 WHY 行宣稱「定義後被改過、列舉底線名稱、Flag 組合值一律判不了」:F3 顯示「改過」只涵蓋三種形狀,宣稱比程式廣;F1/F2 顯示列舉「別名判不了」對 auto() 與多重指派不成立。
- Systems/測試假綠形態.md 的還原翻紅釘:t_count_tag_unknown 等測試沒有 F1~F3 的案例,現有翻紅釘證明不了這些形狀被擋。

總結:最高等級 major
