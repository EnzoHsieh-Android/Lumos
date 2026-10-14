severity: minor

整體結論:沒有第二種做法,也沒有跨層直呼。找到 4 條不對齊,都是命名、錯誤處理或呼叫形狀上的小差異,全部不擋推。

**三問**

**1. 分層與依賴方向:對齊。**
- 執行器 `_durations_table_path` 和 `_load_durations_table` 用 `_load_lumos_inproc()` 讀 `scripts/lumos` 的 `_TEST_DURATIONS_REL` 與 `_read_durations_table`。這跟 `_docs_suite_select` 讀 `_load_lumos_inproc()._DOCS_ONLY_PATHS` 是同一種做法。
  - file: `scripts/test_lumos.py:82-95`(`_docs_suite_select`)
  - file: `scripts/test_lumos.py:39145-39153`(新增的兩支)
- 方向是執行器載入主程式,主程式不反向依賴執行器。
- 測試用 `inspect.getsource` 釘住「只有一份規則」(file: `scripts/test_lumos.py:22029-22032`),跟既有的「別抄第二份」註解一致。
- 資料檔放 `governance/`,常數 `_TEST_DURATIONS_REL` 的寫法對照 `_ANCHOR_BASELINE_REL`(file: `scripts/lumos:26412`)。
- 它也進了 `_BOOKKEEPING_FILES`(file: `scripts/lumos:29377` 附近),這跟 `anchor-baseline.json` 是同一種處理。
- 子指令寫法對照 `push-range`:同樣用 `_note_audit_root(repo)`,同樣是 `--repo` 加 `dest` 前綴,`HELP_WHEN` 也同時有父指令和子指令兩條(對照 `note-audit` 與 `note-audit prepare`)。

**2. 命名與錯誤處理:大致對齊,有 2 條小差異(下面 F1、F2)。**
- 讀函式只丟 `ValueError` 說原因,由呼叫端加「擋下:」前綴並決定 rc。這跟既有的 `擋下:` 用法一致。
  - file: `scripts/lumos:48602`(`_read_durations_table`)
  - file: `scripts/lumos:48652`(refresh 的呼叫端)
  - file: `scripts/test_lumos.py:39635`(執行器的呼叫端)
- 函式內 `import math`、`import hashlib` 是區域匯入,跟 `_quote_norm` 內 `import re` 同風格。

**3. 第二種做法:沒有。**
- 執行器寫 run 檔,沿用 test-cache 的「暫存檔加 `os.replace`」,條件同樣是 `_is_src`,檔名用同樣的 `shard…of…`。
  - file: `scripts/test_lumos.py:39764-39795`(`_cache` 與 `_dur` 並排)
- `lumos test-durations refresh` 寫耗時表用既有的 `_write_lf`(file: `scripts/lumos:21235`)。
- 這兩種原子寫法(執行器自己的暫存檔、主程式的 `_write_lf`)是既有的分工:執行器是獨立行程,不載入主程式的寫入原語。diff 沒有新增第三種。
- `.gitignore` 加了 `.lumos/test-durations-run*.json`,位置緊貼 `test-cache*.json`。

**不對齊的逐條**

F1:兩個呼叫端對同一個 ValueError 的說法不同。
severity: minor
blocking: 否
引句:「擋下:耗時表 {_durations_table_path()} 格式不對({_e})」
- 執行器一律說「格式不對」,refresh 說「讀不懂」(file: `scripts/lumos:48652`)。
- `_read_durations_table` 丟出的原因包含「不是一般檔」和「讀不進來」,這時說「格式不對」不貼切。
- 歸因:未判定。
- 查證:`grep -n '格式不對\|讀不懂' scripts/test_lumos.py scripts/lumos`,只有這兩處各用一種說法。

F2:`test-durations` 的分派沒有檢查子指令。
severity: minor
blocking: 否
引句:「return cmd_test_durations_refresh(repo=args.tdu_repo)」
- 既有的 `note-audit` 逐一比對 `args.nacmd`(file: `scripts/lumos:55351-55359`),`testmap` 比對 `args.tmcmd`(file: `scripts/lumos:55235`)。
- 新的只要 `args.cmd == "test-durations"` 就直接回 refresh(file: `scripts/lumos:55371`)。
- 目前 `required=True` 且只有 refresh 一個子指令,不會出錯。以後加第二個子指令時,這裡會靜默走到 refresh。
- 歸因:新增的原有寫法,不是修補造成。

F3:⚠ 執行器和 refresh 各自推導根目錄。
severity: minor
blocking: 否
引句:「_dur = _cache_dir / (f"test-durations-run-shard{_args.shard.replace('/', 'of')}.json"」
- 執行器的 run 檔位置來自 `Path(GRAPHCTL).resolve().parent.parent / ".lumos"`(file: `scripts/test_lumos.py:39667`)。
- refresh 讀的位置是 `_note_audit_root(repo)`,也就是 git 根或 `--repo` 加 `.lumos`(file: `scripts/lumos:48628` 之後)。
- test-cache 的寫與讀都在執行器內,不會遇到這個分歧。這次是兩個行程各推導一次。
- 一般的來源 repo 兩者相同。GRAPHCTL 是符號連結、或帶 `--repo` 指到別處時,run 檔會對不上。我沒有實際重現,所以標 ⚠。

F4:⚠ run 檔的讀取規則和耗時表不同。
severity: minor
blocking: 否
引句:「tests = json.loads(p.read_bytes())["tests"]」
- 耗時表走共用的 `_read_durations_table`:要求嚴格,整檔不合格就擋。
- run 檔在 refresh 裡另寫一段解析:不合格的略過,逐筆用 `_duration_ok` 過濾(file: `scripts/lumos:48661`)。
- 這是 docstring 明寫的有意設計,秒數合法性判斷也共用 `_duration_ok`。但同一種 `{"version":1,"tests":{…}}` 格式現在有兩種讀取鬆緊度。我判不準算不算「另一份規則」,所以標 ⚠。

**固定席節點**
- `Systems/測試假綠形態.md` 的 INVARIANT(還原翻紅釘要有前置斷言):這次的新測試有 `★前置★` 現場斷言,沒有牴觸。
- `lumos-cli-read`、`lumos-cli-lifecycle`、`guard-kill`、`design-loop` 的 INVARIANT:改動沒碰 search、re-inject、guard kill、處置閘,不影響。
- `pitfalls-code-loop`、`reversibility-governance-ledger`、`loop-convergence-recording`:只是牽連 `scripts/lumos`,新子指令沒有改動它們的流程,不影響。
- 其餘只列名的節點,我沒有逐篇判。

最嚴重等級 minor;blocking 共 0 條。不對齊共 4 條,其中引入第二種做法或跨層直呼的 0 條。

未驗範圍:沒有實際執行任何測試,也沒有重現 F3 的符號連結情境。
