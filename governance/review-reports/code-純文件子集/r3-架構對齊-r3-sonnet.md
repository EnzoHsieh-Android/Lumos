severity: major

## F1 「沒帶 --suite 的空片照舊擋」迴歸測試沒有測到它宣稱要驗的那個分支

severity: major
blocking: yes

引句:「沒帶 --suite 的空片照舊擋(不是子集就真的是切錯)」

這批(r2 折入)在執行器加了兩套「空片」語意:帶 `--suite` 時空片印訊息回 0(子集配分片本來就常常切到空);沒帶 `--suite`(全套)時空片仍照舊印「擋下:…跑了個寂寞不算通過」回 1。要證明「新語意(rc0)沒有吃掉舊語意(rc1)」,r2 補的迴歸測試是:

```
r = run_r("--shard", "3/2")
check("沒帶 --suite 的空片照舊擋(不是子集就真的是切錯)", r.returncode != 0, f"rc={r.returncode}")
```

file: `scripts/test_lumos.py:44227-44228`

問題:`--shard 3/2` 在真的跑到「這片空不空」的判斷之前,會先被更早的一段旗標範圍檢查擋下:

```
if _n < 1 or not (1 <= _i <= _n):
```

file: `scripts/test_lumos.py:29396`(此段本輪未改,是既有邏輯)

3 > 2,`1 <= _i <= _n` 為假,直接印「擋下:--shard 3/2 不合理(第幾片要在 1 到共幾片之間)」、rc2 離開——**根本沒有執行到「沒帶 --suite 的空片仍要擋」那段程式**(`scripts/test_lumos.py:29407` 的 `if not tests:` 分支)。實測重現:

```
$ python3 scripts/test_lumos.py --shard 3/2
擋下:--shard 3/2 不合理(第幾片要在 1 到共幾片之間)
rc=2
```

而 `check` 斷言只驗 `r.returncode != 0`,rc2 一樣滿足,所以這條測試**現在就是綠的,但綠的原因跟它的名字、跟它想驗的那個分支完全無關**。我另外用真的能讓某片切到 0 支、但旗標本身合法的輸入重現了目標分支,確認底層邏輯目前其實是對的(不是這裡在報一個現存 bug,是在報「證據是假的」):

```
$ python3 scripts/test_lumos.py --shard 1500/2000
擋下:第 1500 片一支測試都沒分到——片數比測試數還多,或切法寫錯了;跑了個寂寞不算通過
這是第 1500 片(共 2000 片),分到 0 支
rc=1
```

為什麼是 bug 不是風格:這正是本席被指名要判的問題本身——「帶 --suite 的空片回 0」跟既有「空片擋」並存算不算兩套語意、有沒有講清楚。答案是:兩套語意的區分在程式碼裡是對的、也各自有清楚的訊息,但**這批用來證明「舊語意沒被新語意吃掉」的證據沒有站住**——測試斷言恰好被另一段既有邏輯(旗標範圍檢查)提早攔截而巧合通過,不是它宣稱驗的那條路。往後如果有人改壞 `scripts/test_lumos.py:29407` 那個 `if not tests:` 分支(例如誤把它併進 `_args.suite` 那個 if、或改壞邊界條件),這條測試不會發現。這正是本專案圖譜自己記的「測試假綠形態」——宣稱測到、其實沒測到。

修法建議(供作者參考,不是本席要做的事):把 `--shard 3/2` 換成一個旗標本身合法、但真的會讓某片分到 0 支的輸入(例如全套 + 遠大於測試總數的片數,像 `--shard <N>/2000`,N 在 1..2000 且不對應任何測試索引),斷言訊息裡出現「跑了個寂寞」或「一支測試都沒分到」字樣,而不是只驗 `rc != 0`。

## F2 cochange-check 的 upto 計算還在用 `_range_base` 要收斂掉的舊語意(資訊性,非本批引入)

severity: minor
blocking: no

引句:「三點範圍要 merge-base(a,b)(代碼審 r1 正確性席:三點範圍拿左端點當起點,刪掉的檔會從錯的版本讀)」

這批把 `_sc_churn`/`_small_change_check`/`_test_suite_for_range`/`_pitfall_tier` 四個呼叫點統一收斂到 `_range_base(rr, diff_range)`(定義於 `scripts/lumos:22303`),理由寫在 patch 裡:三點範圍 `a...b` 若直接切 `..` 拿左端點當起點,語意是錯的,要用 merge-base。

`_range_base` 在這支診斷過的四個呼叫點確實都已改用(`scripts/lumos:5716`、`5776`、`22263`、`22325`,共 4 個呼叫點,跟 `def` 一起用 `grep -n _range_base scripts/lumos scripts/test_lumos.py` 可數)。但同一支檔裡還有一處做的是完全同一件事(把 diff range 切出一個「歷史起點」去挖掘規則母體),沒有跟著改:

file: `scripts/lumos:21723`

```python
base = diff_range.split("..")[0].strip()
```

這行在 `cmd_cochange_check` 裡,用途是「`--diff A..B` 挖到 A(規則來自變更之前的歷史)」——跟 `_range_base` 要解決的問題是同一個語意類別(給一段 diff range,要拿它的「起點」去讀歷史)。對三點範圍 `main...feature`,`"main...feature".split("..")` 一樣會切成 `["main", ".feature"]`,`[0]` 仍是左端點 `main`,不是 merge-base——跟這批說「三點範圍拿左端點當起點是錯的」那條理由完全對得上。

判為 minor、不擋的理由:這行不在 `beb61e03..HEAD` 這批動到的範圍裡(`git diff beb61e03..HEAD -- scripts/lumos` 對 21723 附近沒有任何 hunk),`cmd_cochange_check` 整支函式這批完全沒碰。按本席只判「這批的折法」的範圍,這不是這批新引入的第二種做法,而是這批建好收斂點之後,還有一個沒被順手拉進來的舊同族——不是這批的錯,但也代表「同檔同算法收斂成一份」目前只做到一半、範圍侷限在小改動閘那四個呼叫點,值得記一筆,由作者或後續票自己決定要不要順手拉齊。

## 三問對照(逐問簡答,細節見上)

1. mktemp 防呆 `|| true` 判空 vs 新的「建不出來就 exit 1」:兩種寫法在改動前就已經並存於同一支檔(`impact_once` 的 `_f` 是靜默 `return 0`,`_AUTOLOOP_LOG`/`_TESTS_LOG` 是 exit 1 附訊息,後者是 2026-09-07 就有的既有紀律,見 `git show beb61e03:scripts/hooks/pre-push` 302-306 行)。這批把 `_PP_TMP` 從「不判空」直接補成跟 `_AUTOLOOP_LOG`/`_TESTS_LOG` 同一套 exit 1 寫法——是收斂到既有紀律,不是引入第三種。`_PP_TMP` 建的是後面一堆路徑的家(`$_PP_TMP/shards` 等),criticality 跟 `_TESTS_LOG` 同級,選這套是對的。判:不對齊(無)。
2. `[[ "$_shards" =~ ^[0-9]+$ ]]` 驗數字先例:`scripts/hooks/` 底下改動前完全沒有任何「驗證是不是數字」的既有寫法(`git grep -n '=~ \^\[0-9\]' beb61e03 -- scripts/hooks/` 零筆)。`pre-commit`/`post-commit` 有 `[[ "$f" =~ $CODE_EXTS_RE ]]` 這種 `=~` 樣式(驗副檔名,不是驗數字),所以「用 `=~` 做字串驗證」這個手法本身在本 repo hooks 有先例,只是題材(數字 vs 副檔名)是新的、且沒有跟別處打架(repo 裡找不到第二套數字驗證寫法)。判:不對齊(無),屬第一次但合理的擴充,非第二套競爭寫法。
3. 見上方 F1:兩套語意本身劃分正確、訊息也分別講清楚,但本輪補的迴歸測試斷言沒有站在它宣稱驗的那個分支上(判 major)。
4. `_range_base` 呼叫點:4 個(`scripts/lumos:5716`、`5776`、`22263`、`22325`),定義在 `scripts/lumos:22303`。`split("..")[0]` 同族:`scripts/lumos:21723`(cochange 挖掘 upto)是同一語意、未收斂,但不在這批改動範圍內,判 minor 資訊性(見 F2);另外 `scripts/lumos:15296`、`16783`、`18611`、`23858`、`25520`、`27231` 也各有 `split("\.\.")` 但用途不同(裁 index 行、單邊裁頭尾等),不是同一族,不計入。
5. `inspect.getsource` 結構釘先例:本檔在改動前就有同款用法,`"_bootstrap_url(" in inspect.getsource(m.cmd_bootstrap)`(見 `git show beb61e03:scripts/test_lumos.py` 第 30363 行),跟這批新增的 `"_range_base(" in _insp.getsource(m._sc_churn)`(`scripts/test_lumos.py:44167`)是同一手法(釘「函式 X 有沒有呼叫函式 Y」)。判:不對齊(無),有先例、合理。

不對齊共 2 條,其中 major 1 條(F1)、minor 1 條(F2)。
