severity: blocker

## F1 `_platform_test_index` 從 5 值改回 6 值,但 `_dispositions_check_test` 那個解構點沒跟著改,已把表態閘的 test: 證據全部打壞

severity: blocker
blocking: yes

作者這輪把 `_platform_test_index` 的回傳從 5 個值(`pdata, split, default, methods_for, hay_for`)改成 6 個值,自己數過「六個解構點全部跟著改」。但除了那六個「當場解構」的呼叫點之外,還有第七個呼叫點是把整條 tuple 原封不動存起來、延後在另一個函式裡才解構——`cmd_dispositions`(表態核對)的 `_one`/`_ev` 閉包裡:

```
pidx = None
...
if pidx is None:
    try:
        pidx = _platform_test_index(Path(repo_root))
    except Exception as e:
        ...
return _dispositions_check_test(repo_root, at_sha, ev, pidx)
```

而 `_dispositions_check_test` 內部仍是舊的 5 值解構,這一行完全不在這份 patch 的改動範圍內,作者沒有意識到「六個解構點」以外還有它:

`路徑:` `scripts/lumos:28740`(`pdata, split, default, methods_for, _hay = pidx`,函式定義在 `scripts/lumos:28736`)

引句:「回 (pdata, split, default, methods_for, hay_for, loose_for)——★六個值★」

這行是 patch 對 `_platform_test_index` 新回傳形狀的宣告(對應到原始差異第 478 行)。這份宣告成立之後,任何地方只要用舊的 5 值解構去接 `_platform_test_index()` 的回傳值,Python 就會丟 `ValueError: too many values to unpack (expected 5, got 6)`。`_dispositions_check_test` 正是這樣的地方。

**重現(已實跑,前後對照)**:
1. `git clone` 本 repo 到 `/tmp`,checkout 到派工單指定的 base commit `6349bde5`,`git apply` 這份凍結 patch。
2. 跑既有測試(不是這份 patch 新增的測試,是本來就在 repo 裡、這份 patch 完全沒有碰的兩支):
   ```
   python3 scripts/test_lumos.py -k codeloop_check_dispositions_gate
   python3 scripts/test_lumos.py -k codeloop_dispositions_r1_folds
   ```
3. 套用 patch 之後:`t_codeloop_check_dispositions_gate` 13 個斷言裡 2 個失敗,`t_codeloop_dispositions_r1_folds` 也多失敗 1 個,錯誤訊息都是:
   ```
   kt-coroutines 無法驗證(內部錯誤 ValueError:too many values to unpack (expected 5, got 6))——擋下不放行,修好再跑
   ```
   失敗的斷言包括「⑤已提交的測試名 → 放行」——也就是說,一個合法、已提交、樹裡真的找得到的 `test:` 證據,現在會被誤判成「無法驗證」而擋下,不是被誤放行,是把好的也一起擋死。
4. 對照組:在同一台機器上,對**沒有套這份 patch** 的乾淨 clone(base `6349bde5`)跑同一支測試,`t_codeloop_check_dispositions_gate` 13 個斷言全過(`13 passed, 0 failed`)。差異只有「有沒有套這份 patch」。

**為什麼是 bug 不是風格**:這不是理論推演,是拿 repo 自己既有的測試在同一個環境跑出「patch 前綠、patch 後紅」的直接證據。`cmd_dispositions`(表態閘/code-loop 表態核對)只要有一題的 evidence 用 `test:` 開頭,現在一定會炸——不管 tier 是 standard 還是 high、不管證據是不是真的合法。這條路徑正是 lumos-code-loop 表態流程的核心之一(README/skill 提到的 `表態閘`),而這批 patch 的宣告完全沒提到會動到表態閘,審查材料裡也看不到任何人對這個交互面驗證過。三個呼叫點裡有兩個(`_bidx`,`scripts/lumos:27407`、`scripts/lumos:27604`)剛好只用位置索引 0~4,6 值 tuple 不影響它們,所以那兩處是安全的——但這不代表作者有意識地檢查過所有消費者,只是那兩處剛好沒事,`_dispositions_check_test` 這處就沒這麼幸運。

## F2 `_py_declared_methods` 用合成字串 `"def {n}("` 回頭比對 `method_re`,使用者若把 python 的 `test.method_regex` 覆寫成要求 `async def` 前綴,這支函式會把所有名字都篩掉、回一個空集合而非偵測到

severity: minor
blocking: no

`_loose_declared_methods` 判斷「要不要豁免」的邏輯,最終要看 `_py_declared_methods` 能不能篩出「長得像測試」的名字。它的篩法不是照抄 `mre.finditer(txt)` 在真原始碼上跑,而是把 AST 拿到的裸名字組成一個假字串 `"def {n}("`,拿它去跟 `method_re` 比對:

引句:「return {n for n in names if mre.match(f"def {n}(")}」

內建的 `PYTHON_TEST_RE = r"(?m)^def ((?:t|test)_[A-Za-z0-9_]+)\s*\("` 剛好只要求字面 `def `,這個合成比對法對內建 profile 沒問題(我用 mutation test 驗證過:把這支函式換回 r2 那版放寬正則,新測試 `t_spec_gate_docstring_example_is_not_a_declaration` 立刻翻紅,行為對得上)。

但 `scripts/lumos:4081-4086` 允許 `test.method_regex` 逐專案覆寫,而 pytest-asyncio 專案常見的合法寫法是把方法正則錨定成要求 `async def` 前綴,例如 `(?m)^async def (test_[A-Za-z0-9_]+)\s*\(`。這種 profile 一樣「錨在行首」「`.py` 在 exts 裡」,所以會被導去 `_py_declared_methods`;但合成比對字串固定寫死 `"def {n}("`(沒有 `async` 前綴),不管 AST 撿到的是 `FunctionDef` 還是 `AsyncFunctionDef` 都一樣,於是永遠比對不上,回傳空集合。

**重現(已實跑)**:對套用 patch 後的檔案,用 `runpy.run_path` 直接載入 `scripts/lumos`,建一個含兩支互為子字串的 async 測試(`test_thing` / `test_thing_extra`)的假 profile(`method_re` 要求 `async def` 前綴),呼叫 `_py_declared_methods(d, profile)`,回傳 `set()`——完全沒撈到那兩支真實存在、真的撞名的測試。

**為什麼值得記但只算 minor**:失效方向是「安全邊」而非「放過假綠」——`_loose_declared_methods` 對空集合的 `_spec_gate_declared` 會回 `None`,而 `_spec_gate_verdict` 把 `declared=None` 當成「不只一支、要唯一」處理,結果是把合法的參數化 async 測試誤判成「測試名要唯一」,也就是**這批 patch 本來要修的那個原始症狀**,但只在使用者自訂 `async def` 型 `method_regex` 這個窄配置下才會發生;預設 profile、以及本 repo 自己的 fixture 都測不到這條路。不會導致假綠或漏放行,只是沒有把「使用者自訂樣式」這個攻擊面完全堵上,建議下一輪把合成比對字串換成「拿該 profile 實際掃過的某一行原始文字」而不是硬寫 `"def {n}("`,或至少對 async 函式合成 `"async def {n}("` 一併試。

## 查證範圍

- 全文讀了凍結 patch(689 行,sha256 對過)。
- 在 `/tmp/code-pm-r3-A/repo` clone 出乾淨副本、checkout 到派工單給的 base commit、`git apply` 這份 patch(全乾淨套用,無 fuzz),語法 `ast.parse` 過關。
- 對第三輪新增的兩支測試各做過一次「回退到被擋掉的舊做法」的翻紅釘驗證:
  - 把 `_loose_declared_methods` 對非放寬的分支硬改回直接呼叫 `discover_test_methods`(=拿掉「刻意放寬」)→ `t_spec_gate_collision_inside_class_still_weak` 翻紅。
  - 把 `_py_declared_methods` 換回 r2 版本的放寬正則(不用 AST)→ `t_spec_gate_docstring_example_is_not_a_declaration` 翻紅。
  兩支新測試都是真的在守著它們聲稱要守的東西,不是空氣測試。
- 跑過 `python3 scripts/test_lumos.py -k spec_gate`(99 passed)、`-k dispositions`(97 passed, 3 failed,即 F1)、`-k codeloop_check_dispositions_gate`(單獨對照 base 13/13 過、patch 後 11/13 過)。
- 檢查了 `_platform_test_index` 全部 10 個呼叫點(`grep -n "_platform_test_index("`),逐一確認每個解構/消費方式在 6 值 tuple 下的行為;找到 F1 那個唯一沒被更新、也真的會炸的消費點。
- 沒有另外派子代理、沒有動 `/Users/enzo/harness/lumos-toolchain` 的任何 git 狀態(全部操作在 `/tmp/code-pm-r3-A` 底下的 clone 進行)。
