severity: minor

我用臨時複本(`/tmp/lumos-seat-work/code-推送與CI提速/邊界輸入-sonnet/r`,固定在 0cdfc7cc)實際造輸入跑過。耗時表側(`_load_durations_table`、`_shard_by_duration`)的多數邊界都正確,出問題的是「超大整數」、「`tests` 型別不對」和「片數極大」這幾條。

**耗時表與分片:結果符合預期的情形**
- 空檔:每一份都 rc2 擋下。
- `1e999`(解析成 inf)與 NaN:每一份都 rc2 擋下。
- 有 BOM 的耗時表:正常載入。
- 整數與浮點混用、重複鍵(取最後一筆)、`version` 缺或寫成 99:都接受,三份聯集正確。
- tests 含不存在的測試名:接受。
- 全部是 0:接受,每份各分到 683 支。
- 只有一支:`--shard 1/1` 分到 2049 支。
- `--shard 0/3`:rc2。
- 片數等於測試數(2049/2049):每份 1 支,rc0。
- 片數大於測試數(2050/2050):rc1,印「一支測試都沒分到」。
- `--shard 3/3 --suite docs`:共 89 支,分到 30 支,正常。
- `--shard 3/3 --suite keys` 沒給 `--keys`:rc2,這是既有行為。
- `-k` 搭配分片:先照全表分片、再套 `-k`,所以某片可能一支都選不中而 rc1。主線 `1b83927e` 也是同樣的順序,不是這次引入的,不報。
- docs 子集在 CI 裡也是 `--shard i/4 --suite docs`,所以壞掉的耗時表會讓純文件推送的 CI 變紅,不會漏掉。

**固定席節點**
- 測試假綠形態(★INVARIANT★,前置斷言):`t_test_durations_refresh` 與 `t_runner_shard_by_duration` 有「前置:現場成立」斷言,沒違反。但兩支測試都沒蓋到下面 F1 到 F3 的輸入,測試綠不代表這幾條安全。
- lumos-cli-lifecycle、lumos-cli-read、guard-kill(兩條 INVARIANT)、design-loop:這次只在 `scripts/lumos` 加了一個新子指令和簿記檔清單一項,沒碰 re-inject、search、guard kill、處置閘,判不影響。
- pitfalls-code-loop、loop-convergence-recording、reversibility-governance-ledger(★RISK★):耗時表進了簿記檔清單,所以改它不會讓代碼審留痕失效、也不被 pitfalls 掃描。不過格式錯的表在 CI 分片時會被擋下,不會悄悄放行,風險有被接住。
- 其餘「超出上限只列名」的節點:diff 沒有碰它們各自的主題,判不影響。

**F1:`refresh` 遇到 run 檔的 `tests` 是字串或陣列,整支指令崩潰**
severity: minor
blocking: 否
- 輸入:run 檔內容 `{"tests":"abc"}` 或 `{"tests":[1,2]}`。
- 實際結果:`AttributeError: 'str' object has no attribute 'items'`(陣列則是 `'list'`),指令以 rc1 加 traceback 結束。同一批裡其他好的 run 檔也沒被合進去,run 檔全部留在原地。
- 應該怎樣:跟 JSON 壞掉的檔一樣印「略過讀不懂的」、繼續處理下一份。`isinstance(d, dict)` 只擋了最外層,沒擋 `d["tests"]`。
- 補充:run 檔本身是陣列(`[1]`)時反而正常處理(rc2,印「一支可用的秒數都沒有」)。
引句:「for k, v in (d.get("tests") or {}).items() if isinstance(d, dict) else ():」
- 重現:`.lumos/test-durations-run.json` 寫 `{"tests":"abc"}` 後執行 `lumos test-durations refresh`。

**F2:超大整數(例如 10 的 400 次方)讓 refresh 與測試執行器都崩潰,而且 refresh 還會把它寫進耗時表**
severity: minor
blocking: 否
- 輸入一:run 檔裡 `t_a` 的秒數是 10 的 400 次方。`0 <= v < float("inf")` 比較通過,接著 `float(v)` 丟 `OverflowError`,refresh 以 rc1 加 traceback 結束。
- 輸入二:舊耗時表裡有一筆這種超大整數。refresh 的篩選(`v >= 0 and v == v and v != inf`)放行它,原樣寫回表。
- 輸入二的後續:執行器 `--shard 1/3` 讀到這張表時,`_md.isfinite(v)` 丟 `OverflowError`。它不是 `ValueError`,所以沒被 `except (OSError, ValueError)` 接住,結果是 traceback 加 rc1,不是說明裡寫的「格式不對 rc2」。也就是 refresh 可以寫出一張執行器讀不了的表。
- 應該怎樣:把 `OverflowError` 當成秒數不合法處理(丟掉那筆,或在 `_load_durations_table` 轉成 `ValueError`)。refresh 讀舊表與讀 run 檔都要同一套判斷。
引句:「if isinstance(v, bool) or not isinstance(v, (int, float)) or not _md.isfinite(v) or v < 0:」
- 重現:`printf '{"version":1,"tests":{"t_a":1%0400d}}' 0 > governance/test-durations.json; python3.14 scripts/test_lumos.py --shard 1/3 --list`,輸出 `OverflowError: int too large to convert to float`。

**F3:舊耗時表有 BOM 或讀不進來,refresh 會靜默清空整張舊表**
severity: minor
blocking: 否
- 輸入:舊表開頭有 UTF-8 BOM(Windows 編輯器常見)。
- 實際結果:執行器用 `json.loads(bytes)` 會自動吃掉 BOM,所以這張表分片正常。refresh 用 `read_text(encoding="utf-8")` 再 `json.loads(str)`,BOM 讓它丟 `ValueError`,被 `except (OSError, ValueError): pass` 吞掉。結果是舊表的 `t_old` 全部消失,輸出只印「原有 0 支」,沒有警告。
- 讀取權限被拿掉(chmod 000)時也一樣,直接當空表覆蓋。
- 應該怎樣:執行器讀得進的表,refresh 也要讀得進(兩邊用同一個函式或同樣的 bytes 解碼)。舊表存在卻讀不懂時至少該印警告,不要靜默覆蓋。
引句:「old = json.loads(table_path.read_text(encoding="utf-8"))」

**F4:`--shard 1/N` 的 N 很大時,分片分組的耗時隨 N 成比例暴增**
severity: minor
blocking: 否
- 輸入:`--shard 1/100000 --list`。
- 實際結果:20.4 秒、峰值約 494MB。N 為 1000000 時超過 2 分鐘還沒結束(我手動中止)。
- 原因:`_shard_by_duration` 每支測試都對全部 N 個桶做一次 `min(range(n), ...)`,另外還要建 N 個空串列。
- 對照:主線的取模分法對任何 N 都是瞬間完成(`--shard 1/1000000` 只需過濾一次清單)。
- 影響範圍:CI 只用 4 片,實際只會發生在打錯數字時,但這是這次引入的退步,所以仍列出。
- 應該怎樣:N 大於測試數時直接用空桶、或把桶數限制在 `min(n, len(names))`,再用堆積(heap)挑最輕的桶。
引句:「k = min(range(j), key=lambda j: (loads[j], counts[j], j))」
- ⚠ 引句我憑記憶改寫了縮排與變數,patch 裡的原文是:
引句:「k = min(range(n), key=lambda j: (loads[j], counts[j], j))」

**F5:`refresh` 在非 git 目錄加 `--repo` 時照樣寫檔(⚠ 嚴重度低,可能是刻意設計)**
severity: minor
blocking: 否
- 輸入:在 `/tmp` 底下對一個非 git 目錄執行 `test-durations refresh --repo <非 git 目錄>`。
- 實際結果:`_note_audit_root(repo)` 在有給 `--repo` 時不檢查是不是 git,直接寫出 `governance/test-durations.json` 並刪掉 run 檔。
- 說明寫的是「不在 git 專案 → rc2」,實際上只有「沒給 `--repo` 且 cwd 不在 git 裡」才 rc2。
- 這是既有輔助函式的語意,所以是說明文字與行為對不上,不是 bug。
引句:「沒有 run 檔、不在 git 專案 → rc2;寫不進去 → rc1。耗時表在簿記檔清單裡,刷新它不會讓代碼審留痕失效。」

**其餘邊界:行為合理,不報**
- `.lumos/` 不存在:rc2 加提示。
- 耗時表所在目錄唯讀:rc1 加「寫不進耗時表」,run 檔保留。
- 耗時表路徑本身是目錄:rc1,run 檔保留。
- 只有一份 run 檔、或 run 檔與耗時表的測試名完全不重疊:正常合併,舊的名字原樣保留(表只增不減,屬刻意的「沒跑到的保留舊值」)。
- 某份 run 檔壞掉、另一份好:好的那份照合,壞的那份被刪掉,同時印提示。
- 只有壞掉的 run 檔:rc2,檔案保留。

**環境清理**:我在 `/var/folders/.../T/` 下殘留的 `gctl-run-atjoe_lr` 已刪。該目錄下還有 183 個 gctl 暫存是其他人的,沒碰。我的複本與暫存都在席目錄內,由編排者收。

最嚴重等級:minor;blocking 共 0 條(minor 共 5 條:F1 到 F5)。
