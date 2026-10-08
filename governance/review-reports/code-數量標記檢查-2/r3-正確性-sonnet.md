severity: major

## F1 改寫標籤時把遮罩用的 NUL 字元寫進筆記
severity: major
blocking: 是
引句:「left = t.group(1).rpartition("=")[0].strip()」
佐證:引句與 `tags = list(_COUNT_TAG_RE.finditer(seen))` 在 _count_rewrite;file: `scripts/lumos:34315`。標籤是在 `seen`(_count_visible 把行內程式碼換成 \0 的版本)上比對的,`t.group(1)` 因此帶 \0;而 `edits` 用它組新標籤再寫回原行。
1. 輸入:一行 `有 5 種類型 [count:src/st.py::KINDS``x``=5]`(標籤內夾雙反引號或單反引號 span)。_count_lines 用 _strip_inline_markup(直接刪掉 span)解析,得名稱 KINDS、n=5,scan 列 count drift。
2. `drift fix --kind count` 走 _drift_fix_count -> _count_rewrite,新標籤 left 含 5 個 \0,寫成 `[count:src/st.py::KINDS\0\0\0\0\0=2]`。
3. 寫前的把關 `[q["n"] for ... in _count_lines(new_line)] != [actual]` 只比數字:\0 不是反引號,名稱變成 `KINDS\0\0\0\0\0` 仍解析出 n=2,把關放行。
4. 結果:rc=0,筆記被寫入 NUL 字元,被刪掉的 `x` 也不見了;下一次 scan 變成「找不到模組最上層的 KINDS\0…」問題。
最小重現:/tmp/count-r3-work/t3.py(用 test_lumos 的 _ct_repo/_df_fix 在暫存專案跑,輸出末行檔尾含 `KINDS\x00\x00\x00\x00\x00=2`);/tmp/count-r3-work/t2.py 直接呼叫 _count_rewrite 同樣得 `\x00`。
(_count_visible 與 _strip_inline_markup 的標籤個數一致已用 20 萬組隨機輸入驗過、0 筆不同,見圖譜判定前的覆蓋段;問題不在個數,在標籤內文取自遮過的字串。)

## F2 定義/類別標頭裡的海象綁定被整個跳過,數出已被換掉的值
severity: major
blocking: 是
引句:「if not isinstance(nd, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):」
佐證:file: `scripts/lumos:33178`(_count_module_nodes)。遇到這四種節點就不 extend 子節點,連「在外層作用域求值」的部分也一起丟:預設參數值、裝飾器、類別基底/關鍵字、參數與回傳註記、lambda 預設值。這些位置的 `X := …` 綁的是模組這一層的 X。
1. `X = (1, 2, 3)` 後接 `def f(a=(X := (1,))): pass` -> _count_eval 回 (3, None),執行後 X 是 `(1,)`。
2. `@(X := (lambda f: f))` 加裝飾 def -> 回 3,執行後 X 是函式。
3. `class C((X := object)): pass` 與 `class C(metaclass=(X := type))` -> 回 3。
4. `f = lambda a=(X := 1): a` -> 回 3。
標籤因此被判成「對得上」或「對不上 N」,卻不是執行時的值,違反「看不懂就判不了」。
最小重現:/tmp/count-r3-work/repro.py(列出 default walrus / decorator walrus / class base walrus,印出 lumos 與 runtime 的 X);/tmp/count-r3-work/t4.py 另有 class kw、lambda default、annotation 變體,皆回 (3, None)。
修法方向:對這四種節點只跳過本體(body),其餘欄位(decorator_list、args.defaults/kw_defaults、bases、keywords、returns、annotations)照走。

## F3 match 的捕捉模式與 except as 綁名稱,不是 Name 節點,漏判
severity: major
blocking: 是
引句:「and isinstance(nd.ctx, (ast.Store, ast.Del))) > own:」
佐證:file: `scripts/lumos:33190`(_count_changed)。名稱寫入只數 `ast.Name` 的 Store/Del;但 `case [X]`、`case 1 as X`、`case [*X]`、`case {**X}` 的名稱存在 MatchAs/MatchStar/MatchMapping 的字串欄位 name/rest,`except E as X` 在 ExceptHandler.name,都不是 Name,也不經 Import/def/class 分支。
1. `X = (1, 2, 3)` 後接 `match (7,):\n    case [X]:\n        pass` -> 回 (3, None),執行後 X == 7。
2. `X = (1, 2, 3)` 後接 `try: raise ValueError / except ValueError as X: pass` -> 回 (3, None),執行後 X 已被刪除(unbound)。
3. 同理 MatchStar、MatchAs、MatchMapping.rest。
最小重現:/tmp/count-r3-work/repro.py(match capture、except as 兩列)。
修法方向:在 ast.walk 那圈加 MatchAs/MatchStar(name)、MatchMapping(rest)、ExceptHandler(name) 的名稱比對(只看模組層,同 own 規則)。

## 圖譜判定
- 家 Systems/存量漂移守衛.md 的新 WHY 行我沒逐字比對(本席專注正確性);WHY 若寫「_count_changed 把所有重新綁定都判不了」,F2、F3 說明這句與程式不一致。
- 測試假綠:t_count_tag_unknown 的 R1–R5 都是 Name 節點形狀,對 F2、F3 沒有翻紅釘;補測試時須先斷言該檔 runtime 確實重綁(前置斷言證明現場成立)。
- t_count_tag_fix 的 ⑨ 只涵蓋標籤外的雙反引號,沒有標籤內夾反引號案例,F1 沒釘。

## 走過但無 finding 的輸入
- _count_visible 對 _strip_inline_markup:隨機 20 萬組(字母表含 ` `` ``` 與標籤片段)標籤個數差 0;雙反引號含單反引號、三反引號、跨標籤、連續兩組 span、未閉合反引號個數都一致。
- 常見寫法仍可數:docstring 後接常數、`__all__ = [...]`、`from typing import Final` 加 `X: Final = (...)`、`X: Final[tuple] = (...)`、`X = Y = (...)`、`Y = X = (...)`、類別本體與函式本體同名區域變數、`X.attr = 1`、`X.copy()`、`len(X)`、`X[0]`、`type A[X] = int` 型別參數。皆回正確數。
- 判不了方向(保守,不算 finding):`X: tuple` 後 `X = (...)`(Name 寫入 2 次 > own 1)、if 區塊內 `for X in`、`with … as X`、模組層 `X += …`、`X.sort()`。
- `import X.sub` 綁 X 但 (a.asname or a.name) 是 `X.sub`,比不到;名稱要剛好是套件名才會中,我給不出常見場景,未列。

總結:最高等級 major
