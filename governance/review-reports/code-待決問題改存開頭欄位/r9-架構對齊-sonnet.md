severity: minor

我先把 `75620ccf` 的 `scripts/lumos` 抽到臨時目錄對照,下面的行號都指這個版本。patch 的 +/- 分段也讀過。另外用修後版本實跑了一次精簡版產生器,產物裡 `_cli`、`WriteBlocked`、`_write_refusal_reason` 都在,`--help` 正常。

**第 1 問,分層與依賴方向:對齊。**
- **`WriteBlocked` 與 `_write_refusal_reason`**:兩者現在在 `scripts/lumos:20442` 與 `:20451`,緊鄰寫入原語 `load_raw_for_edit`(`:20475`)、`_write_lf`(`:20504`)、`atomic_write_verify`(`:20532`)。用的人有 `atomic_write_verify`(`:20537`)、`_signoff_append`(`:9180`)和 drift fix 載入(`:39934`)。
- **沒人接的擋下**:由命令列入口 `_cli()`(`:53757`)接,與 `scripts/slim-gen.py` 的主函式錨點沒有衝突。
- **訊息清洗**:在 `WriteBlocked.__init__` 清一次,不再靠接住處清,位置合理。
- **待決問題區**:清單外鍵名規則(`_pq_questionish_key`、`_pq_line_mapping`)與 Unicode 判斷(`_PQ_EMOJI_RANGES`、`_pq_bad_char`)都留在那一區,沒有跨層直呼。

**第 2 問,命名與錯誤處理:統一。**
- 各分派段不再 `except WriteBlocked: raise`。`WriteBlocked` 繼承 `ValueError` 與 `RuntimeError`,所以原本接這兩種錯誤的段落(`loop escape`、`set/append/remove`、`new`、`rel-cascade`、`decision-*`、`question-*`、`self-audit`、`updated-sync`)照舊接成「擋下」。`guard` 段接 `RuntimeError` 與 `OSError`,也照舊。
- 沒被任何段接到的,才由最外層 `_cli()` 接,這是統一,不是第二種做法。
- `_write_refusal_reason` 的 docstring 已明寫「筆記與簽核帳共用(其他帳檔各有自己的守衛,不在此列)」,不再宣稱唯一。
- 專案裡仍有別處自己查符號連結或硬連結,都是帳檔守衛,範圍不同:
  - `_escape_log_guard`(`:10342`)
  - `_drift_ledger_path_problem` 同族(`:39646`)
  - `.gitignore` 補寫(`:24401`、`:24426`)
- 這些不算新的不對齊。

**第 3 問,第二種做法:上一輪點名的四項收掉了。**
- 三層接法:改成「分派段照鄰居寫法接,加最外層 `_cli()`」。裝飾器 `_write_blocked_boundary` 與 `_call_with_write_blocked_boundary` 已整組刪除,全 repo 無殘留引用。
- `WriteBlocked` 離寫入原語遠:已搬到原語旁。
- 寫入拒絕函式宣稱唯一:已改成限定範圍的說法。
- anchor 偵測三份:現在只剩 `_pq_skip_markers` 一份,`_pq_structure_marker_problem`、`_pq_flow_questionish`、`_pq_questionish_key`、`_pq_line_mapping` 都共用它。`_pq_structural_value_problem`、`_pq_mapping_parts` 已刪。
- `_cli()` 與其他腳本的入口寫法:`slim-scan.py`、`slim-gen.py`、`usage_scan.py` 等都是 `sys.exit(main())`,只有 `lumos` 多了 `_cli()` 包一層。理由寫在 docstring(精簡版產生器靠 `main` 這個名字),測試也已改成呼叫 `lm._cli()`。這是單一包裝,不是第二種接法,不列為不對齊。
- `_pq_yaml_unescape` 與 `_yaml_quote`、`strip_quotes`:不重複。這兩個是「寫入時挑引號」和「只剝頭尾引號、不解跳脫」,專案裡沒有任何解 YAML 跳脫的函式。`_pq_yaml_unescape` 只服務辨認鍵名,是新能力,不是又一份。

不對齊兩條,都只是命名與重複,結構對。

severity: minor
blocking: 否
引句:「fd = os.open(log, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o666)」
這是新寫的簽核帳追加 `_signoff_append`,自己用原始檔案描述子加 `O_APPEND|O_NOFOLLOW`、`os.write` 迴圈寫滿。`_ledger_append`(`scripts/lumos:21809`)已有同一套「`os.open` 加 `O_APPEND` 加 `O_NOFOLLOW`,再 `os.write` 驗滿寫」,`_drift_ledger_append` 一族也各有一份。差別只在這支多了截回與刪除新建檔的還原,所以不是機械重複。但它沒有說明為什麼不擴充既有追加函式,也沒指到那一份。專案現在有三套各自的「帳追加」原語。

severity: minor
blocking: 否
引句:「_PQ_EAST_ASIAN_RANGES = ((0x1100, 0x11FF), (0x2E80, 0x9FFF), (0xA960, 0xA97F), (0xAC00, 0xD7FF), (0xF900, 0xFAFF),」
這是新寫的 `_PQ_EAST_ASIAN_RANGES` 與 `_pq_is_east_asian`,為了不放行漢字、假名、韓文之間的軟連字號。專案已有「CJK 判斷單一真相」`_RANK_CJK_RE`(`scripts/lumos:4732`)和 `_el_is_cjk`(`:13484`,註解明寫「與 _rank_tokenize 同源(單一真相)」)。`:5086` 還有一段內聯的漢字、假名、韓文範圍判斷。新範圍表涵蓋更廣(含韓文音節、半形全形區),語意不完全相同,但沒有說明為何不共用或擴充既有那份,於是又多一份東亞字碼位清單。

不對齊共 2 條,其中擋合併的 0 條

臨時檔放在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r9-架構對齊-sonnet/`(抽出的 `x.TgQn/l.py`、`sg.py`、`slim_out.py`、`lumos_src`),依派工單留給編排者收貨後刪。
