severity: blocker

## F1 加了第六個回傳值,漏改一個解構點,表態閘的 test: 證據驗證會直接炸掉

severity: blocker
blocking: yes

引句:
「return pdata, split, default, methods_for, hay_for, loose_for」

`_platform_test_index` 這批從回 5 個值改回 6 個值(多了 `loose_for`)。patch 把 10 個呼叫點裡的 7 個解構點都改成六元解構(`scripts/lumos:1299` `:5567` `:5837` `:6192` `:10505` `:15094` `:27880`),但有一個下游函式沒跟著改:

`_dispositions_check_test`(`scripts/lumos:28736`)收到的 `pidx` 是 `_platform_test_index` 的完整回傳值(在 `scripts/lumos:28846` 直接 `pidx = _platform_test_index(Path(repo_root))`,原封不動存成一個變數,不在呼叫點解構),但函式內部第一行固定解構成五個:

`scripts/lumos:28740`:`pdata, split, default, methods_for, _hay = pidx`

這行沒被這份 patch 動到(整份 patch 裡找不到 `_dispositions_check_test` 或 `pidx` 字樣),但它假設的仍是舊的五元組。`_platform_test_index` 現在回六元組,這裡就會炸 `ValueError: too many values to unpack (expected 5, got 6)`。

**怎麼重現**(不需要造新情境,repo 既有測試已經在紅):
```
cd /Users/enzo/harness/lumos-toolchain
python3 scripts/test_lumos.py -k disposition
```
結果 `97 passed, 3 failed`,兩支既有(非這批新增)的測試翻紅:
- `t_codeloop_check_dispositions_gate` 的斷言⑨(`樹裡只有治理帳提到那個名字(測試檔未提交)→ 仍 BLOCKED`)
- `t_codeloop_dispositions_r1_folds`(1 條斷言)

失敗輸出裡直接印出:
```
"problems": ["kt-coroutines 無法驗證(內部錯誤 ValueError:too many values to unpack (expected 5, got 6))——擋下不放行,修好再跑"]
```
字面跟我用最小重現腳本(直接呼叫 `_platform_test_index()` 再餵進 `_dispositions_check_test()`)拿到的錯誤一模一樣。

**為什麼是 bug 不是風格**:`_dispositions_verdict`(`scripts/lumos:28796`)是表態閘(code-loop tier=high 推送前核對「架構對齊/棧特定」問題的表態)的核心判定路徑——任何一題 status=`satisfied` 或 `tension` 且 `chosen=suggested`、evidence 開頭是 `test:` 的,都會走到這條路。外層雖然有 `except Exception` 接住(`scripts/lumos:28901`),不會讓整個 CLI 崩潰,但接住之後照樣印「無法驗證(內部錯誤)」並把 `out["blocked"]` 設 True——等於**任何用 test: 當證據的表態,從此以後一律判「驗不了、擋下」**,不管那支測試是真是假。這條路徑一旦上線,現有靠 test: 證據放行的表態全部會被擋,而且訊息看起來像「工具壞了」而不是「你答錯了」,會誤導人去重表態而不是去修工具。這正是本輪攻擊方向③指定要查的「六個解構點是不是都改對了」——結果是沒有,而且不是理論上的邊界情況,是 repo 自己的舊測試已經在紅。

## F2 「把名字套回原本樣式試比對」這個篩法,對縮排本身是判準的自訂正則會整批篩空,悄悄讓修好的功能失效

severity: major
blocking: no

引句:
「return {n for n in names if mre.match(f"def {n}(")}」

`_py_declared_methods` 用語法剖析收集到所有函式名之後,篩「長得像測試」的辦法是把每個名字套進固定樣式 `def {n}(`(永遠沒有縮排、永遠是 `def` 不是 `async def`、永遠沒有裝飾器或類別標頭)再拿去跟這個 profile 的 `method_re` 比對。內建的九個棧裡,`.py` 這格用的 `PYTHON_TEST_RE = re.compile(r"(?m)^def ((?:t|test)_[A-Za-z0-9_]+)\s*\(")`,本身就不含縮排字面,所以重建字串能對上——這是這批要修的正確案例。

但攻擊方向明講「使用者自訂樣式」也要查:`.lumos/config.json` 的 `test.method_regex`(`load_test_profile`,`scripts/lumos:4044`)允許使用者整個換掉這條正則。如果使用者刻意把縮排寫進正則本身——例如很多專案拿 unittest 的 class 慣例,寫 `(?m)^    def (test_[A-Za-z0-9_]+)\s*\(`(錨在 4 個空格,刻意只認類別方法、排除模組層級的同名函式)——這正是本批 loose 掃描宣稱要處理的「類別裡的測試」情境,但重建字串 `def {n}(` 永遠沒有前導空白,`.match()` 對誰都不會過,篩出來永遠是空集合。

我實際帶這條自訂正則跑過:
```
profile["method_re"] = re.compile(r"(?m)^    def (test_[A-Za-z0-9_]+)\s*\(")
lumos_mod._loose_declared_methods(root, profile)   # -> set()
lumos_mod.discover_test_methods(root, profile)     # -> {'test_bar', 'test_bar_extra'}  (真正找得到)
```
放寬掃描回空集合,而同一條正則餵給既有的嚴格掃描(`discover_test_methods`,真正跑測試時用的那份)正確找到兩支方法。

**下游影響**:`_spec_gate_declared` 對空集合會回 `None`(`if not methods: return None`,`scripts/lumos:225` 附近),`_spec_gate_verdict` 對 `declared=None` 一律當「非 1」處理,結果是照舊印「測試名要唯一」——也就是說,對這類自訂正則的專案,這整批修的「參數化測試不誤判撞名」完全沒有生效,行為退回到 patch 之前(仍然會誤擋),而且沒有任何訊息提示使用者「你的自訂正則不支援放寬掃描」。不算 blocker 是因為它沒有往危險方向偏(不會把真撞名誤判成參數化、不會放過假綠),只是讓這批修的效果對一整類真實可能存在的自訂設定悄悄失效。跟本輪重點攻擊方向①(「篩法在使用者自訂樣式下會不會篩錯」)直接對上。

## F3 `discover_test_methods` 抽出共用產生器後,迴圈內文縮排多留了一層,跟同函式其餘程式碼的縮排慣例不一致

severity: minor
blocking: no

引句:
「if strip in ("c-style", "c-style+strings"):」

原本這段程式碼巢狀四層(`for dp,dirs,files` → `for f in files` → `if Path(f).suffix.lower() in exts:` → 內文),縮排到 16 格是合理的。這批把外兩層走檔邏輯抽進 `_walk_test_files` 產生器後,`discover_test_methods` 只剩一層 `for txt in _walk_test_files(...):`(`scripts/lumos:4353` 與 `:4424` 各有一份,這裡指 `discover_test_methods` 那份 `:4424`),照該檔其餘程式碢的縮排慣例(每層 4 格)迴圈內文應該是 8 格,但這段還留著沒往回縮,現在檔案裡是 12 格(比同一函式其他行,例如上面的 `methods = set()`、下面的 `return methods` 都只 4 格,多縮了整整一層)。純屬複製貼上舊程式碼時忘了調整縮排,不影響語意(Python 只要求同一區塊內縮排一致,這裡確實一致,能跑),但看得出這次「共用產生器」的抽法沒有像檔案其他抽函式重構(例如同批新增的 `_walk_test_files` 自己、或既有的 `_lens_py_defs`)一樣把縮排整理乾淨,純粹是這次審查鏡頭要求核對的「抽法跟本檔其他抽法一不一樣」——答案是格式上不一樣(多一層縮排的雜訊),但不影響正確性,列 minor。

---

## 鏡頭內其餘三項核對結果(沒發現額外問題)

- **語法剖析這個做法在本檔有沒有先例**:有。`_lens_py_defs`(`scripts/lumos:26558`)在這批之前就用 `import ast as _ast`、`ast.parse` + `try/except (SyntaxError, ValueError): return None` 的同一套寫法(還註明「沿 slim-gen/slim-scan 先例」)。這次 `_py_declared_methods`(`scripts/lumos:4340`)整體風格一致,唯一差異是它 `import ast`(不加別名)而先例 `import ast as _ast`(加別名)——都是函式內區域 import,不會造成命名衝突,純風格差異,不影響行為,沒有另外列成一條。

- **六個解構點是不是都改對了**:七個解構點(`:1299` `:5567` `:5837` `:6192` `:10505` `:15094` `:27880`)全部正確改成六元。另外兩個把回傳值整包存成變數、用索引取值的呼叫點(`:27407` `_bidx`、`:27604` 同名變數,傳進 `_lens_render_listed` 用 `bidx[1..4]` 取值)不受影響,索引沒有超界。**只有 F1 那個漏掉**——這正是這條鏡頭要抓的東西,也是本輪最大的發現。

- **共用產生器的抽法有沒有改變原本篩選語意**(副檔名、檔名錨、內容必含):比對 patch 移除的舊 `os.walk` 區塊與新增的 `_walk_test_files`(`scripts/lumos:4387` 附近),三道篩選(`suffix in exts`→改寫成 `not in: continue`、`fname_globs` fnmatch 檔名錨、`file_must_match` 的 `must.search`)順序與條件完全對應,只是把「符合就往下做」改寫成「不符合就 continue」,語意等價,沒有漏檢或多檢。已用 `python3 scripts/test_lumos.py -k spec_gate` 跑過(99 passed, 0 failed)確認沒有連帶弄壞既有 spec-gate 行為。

## 已驗過的路徑

- 全 10 個 `_platform_test_index(` 呼叫點逐一核對解構/索引正確性(F1 發現漏一個)。
- `_walk_test_files` 與原 `discover_test_methods` 內建 os.walk 邏輯逐行比對篩選語意。
- `_py_declared_methods` / `_loose_declared_methods` 對內建 python profile(`PYTHON_TEST_RE`)行為正確;對自訂 class-縮排正則的行為實測會退化(F2)。
- `python3 scripts/test_lumos.py -k spec_gate`:99 passed, 0 failed。
- `python3 scripts/test_lumos.py -k disposition`:97 passed, **3 failed**(F1,兩支既有測試翻紅,非這批新增的兩支新測試)。
- `python3 scripts/test_lumos.py -k stack_questions`:25 passed, 0 failed(不含 test: 證據路徑,沒踩到 F1)。
- 新增的兩支測試(`t_spec_gate_collision_inside_class_still_weak`、`t_spec_gate_docstring_example_is_not_a_declaration`)語意檢查過,fixture 改動(新增 `t_nested`/`TestGroup`/`t_doc`)沒有破壞既有 fixture 使用者的假設,除了 F1 之外沒有連帶翻紅。
