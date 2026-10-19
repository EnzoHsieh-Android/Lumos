severity: minor

我拿大輸入實測了。這份 diff 沒有會把機器資源用光的 blocker 或 major。有三條 minor,另外問題①的撞名前置查詢沒有新子程序,已確認乾淨。實驗都放在 `/tmp/lumos-seat-work/code-測試名收自由字串/資源-sonnet/`,用 `scripts/lumos` 當模組載入(`web-gaps` 工作樹已套用這份 diff)。

**問題①:子程序和執行緒有沒有沒收掉的**
- 乾淨。`_name_filter_collisions` 是純函式,`discover_test_methods` 只做檔案走訪和正規式,兩者都沒開子程序。
- 撞名檢查放在 `procs = _BtProcs()` 之前。就算 discover 途中遇到 Ctrl-C 或例外,也沒有已經開出去的程序要收。
- 拿不到子程序孤兒的反例,不報。

**問題②:時間預算**
- 新增的撞名前置查詢(整個平台掃一次宣告名)沒有逾時上限。
- 實測 100MB 的 spec 檔案樹(1500 支檔)掃一次要 4 到 10 秒。舊的剝註解法是 1.2 到 3.9 秒,新版約慢 2.5 倍,但仍是線性,不會把正常操作擋下。
- 推送前閘會先建一次測試索引,`_run_bound_tests` 再掃一次,等於同一個平台掃兩遍。只是慢,不是錯。
- 這一點沒有可報的具體失敗場景,不列為 finding。

**問題③:記憶體與二次方工作**

1. 新的剝註解法在長字串字面上吃記憶體,大約每個字元 130 位元組
severity: minor
   - blocking: 否
   - diff 段落:`_JS_STRIP_RE`,在 `_strip_test_comments` 的 `c-style-strings-kept` 分支使用。
   - 問題:`'(?:[^'\\\n]|\\.)*'?` 這種「群組加星號」的寫法,Python 的正規式引擎每走一個字元就在堆上多推一格狀態。測試檔裡有一個大字串(例如內嵌的 base64 fixture),整條字面就會變成堆上的巨大狀態。時間仍是線性,只有記憶體爆。
   - 具體例:`it('x',()=>{});const d='` 後面接 N 個 `A` 再收尾,呼叫 `_strip_test_comments(txt,"c-style-strings-kept")`。

     | 字串長度 | 時間 | 額外記憶體 |
     |---|---|---|
     | 1MB | 0.03 秒 | +130MB |
     | 8MB | 0.26 秒 | +1042MB |
     | 32MB | 1.06 秒 | +4163MB |

   - 對照:同樣 32MB 用舊的 `c-style` 只要 +134MB(就是字串本身)。反引號樣板字串、沒結尾的引號走的也是同一條路。
   - 佐證:改成展開式 `'[^'\\\n]*(?:\\.[^'\\\n]*)*'?`(雙引號和反引號同理),32MB 只要 0.2 秒、+34MB。這個改法我只在 `fix.py` 裡驗過,沒套進 `scripts/lumos`。
   - 引句:「_JS_STRIP_RE = re.compile(r"'(?:[^'\\\n]|\\.)*'?|\"(?:[^\"\\\n]|\\.)*\"?|`(?:[^`\\]|\\.)*`?|//[^\n]*|/\*(?:.*?\*/|.*\Z)", re.S)」

2. 撞名檢查在綁定數乘測試名數上是二次方,而且每次比對都重新配置小寫字串
severity: minor
   - blocking: 否
   - diff 段落:`_name_filter_collisions`。`coll_cache` 只快取了 discover 的結果,沒有快取小寫化後的名稱集合。
   - 具體例:regex 平台、每個名字約 100 字、20000 個宣告。

     | 綁定數 | 耗時 |
     |---|---|
     | 500 | 5.3 秒 |
     | 2000 | 22 秒 |
     | 2000 綁定、100000 宣告 | 118 秒 |

   - 實際的閘跑幾十支綁定,不會痛。
   - 修法:每個平台先把宣告集合小寫化一次,或建一份小寫名稱的列表重用。我沒有跑這個修法。
   - 引句:「low in (o.lower() if name_filter == "regex" else o):」

3. `node-vitest` 的跑過證據正規式在單行長輸出上是二次方
severity: minor
   - blocking: 否
   - diff 段落:`_RAN_EVIDENCE["node-vitest"]` 的 `re`。
   - 問題:`\bTests\s+[^\n]*?\b[1-9]\d*\s+passed` 的 `[^\n]*?` 對每個 `Tests ` 起點都往行尾掃。`_kill_cap` 把輸出截在約 256KB,正規式再對這份輸出做 `re.search`。
   - 具體例:單行 `"Tests 1 "` 重複到 N KB,而且找不到 `passed`。

     | 行長 | 耗時 |
     |---|---|
     | 16KB | 0.25 秒 |
     | 64KB | 3.9 秒 |
     | 256KB | 63 秒 |

   - 同形的舊 jest 正規式 `Tests:.*?[1-9]\d*\s+passed` 本來就有這個毛病(256KB 要 47 秒),這次是沿用,沒有新增一個類別。
   - 觸發條件是測試輸出裡有一整行超過 64KB 又反覆出現 `Tests `,很不自然。我只把它當低機率的退化。
   - 引句:「"re": r"\bTests\s+[^\n]*?\b[1-9]\d*\s+passed",」

**實測後確認沒問題的**
- 時間線性:1MB 的 minified 單行、沒結尾的引號、一整行的 `'`、每行一個沒結尾的 `'`、1MB 的 `/*`、一百萬個 `it('`、`test(` 後接 1MB 空白,這些都在 0.2 秒內跑完。
- 新掃描正規式沒有回溯爆炸。字面主體限 200 字,每個起點最多走 200 步。
- 沒結尾的 `/*` 只吞一次到檔尾。
- `_ns_wd_binding_norm`、`_split_test_ref`、`_test_name_ok` 都是線性。`_clause_hang_lines` 最多印 15 行,`TEST_REF_RE.findall` 只對這 15 行做。
- 每條條款各掃一次整個 repo 的疑慮:`_run_bound_tests` 的 `coll_cache` 以平台為鍵,每個平台只掃一次。

最嚴重 severity:minor,blocking 共 0 條。
