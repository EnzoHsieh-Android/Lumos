severity: minor

審查範圍:修補差異(`e3ea2c16` 到 `ab35a0f8`)我逐 hunk 讀完,也讀了整支 `scripts/templates/android-receipt-rerun.sh` 和 SQL 範本。我在 `/tmp/lumos-seat-work/` 的複本上做了行為重現和破壞實驗,做完已用字面路徑刪除。在 `android-ui-kind` 工作樹裡我只讀檔與跑測試。

在工作樹上跑 `-k android_ui_attribution`、`-k license_headers`、`-k vendored`、`-k android`,全綠。

沒有 blocker 或 major。主修補有效:UTF-8 模式、BOM、工具執行不了回 2 與暫存檔清理都有紅綠證據。找到一個修補自己引入的小回歸,和兩個上輪沒人看的角落。

## 1. 拿掉 reconfigure 後,PYTHONIOENCODING 設成非 UTF-8 時輸出會崩
severity: minor
blocking: 否
引句:「exec env PYTHONUTF8=1 python3 - "$HERE" "$PROJECT_ROOT"」
file: `scripts/templates/android-receipt-rerun.sh:11`(崩在 `:77` 的 print)
歸因:有證據的修復回歸
- **被刪掉的守衛**:`sys.stdout.reconfigure(encoding='utf-8', errors='replace')` 不管環境怎麼設都生效。
- **為什麼 UTF-8 模式沒完整取代**:Python 文件明寫 `PYTHONIOENCODING` 優先於 UTF-8 模式。環境若有 `PYTHONIOENCODING=ascii` 或 `latin-1`,標準輸出照那個編碼。
- **結果**:比對完全相符的收據會 Traceback 並回 1,和「比對不符」同碼。
- **重現**(兩版都用同一組收據):`queries.sql` 寫 `expect=甲:compose_ns=5`,假分析工具印 `"甲","5","x"` 那一列。
  - 命令:`PYTHONIOENCODING=ascii LC_ALL=C TP=./zh.sh sh <腳本>`
  - 修前(`git show e3ea2c16:scripts/templates/android-receipt-rerun.sh`):印 `OK  Q1 甲:compose_ns=5`,rc=0。
  - 修後:`UnicodeEncodeError: 'ascii' codec can't encode character '\u7532'`,rc=1。
  - `PYTHONIOENCODING=latin-1` 也一樣。
- **範圍**:要有人刻意把這個變數設成非 UTF-8 才會發生;失敗方向是安全的(非零)。
- **修法**:env 那行加 `PYTHONIOENCODING=utf-8`,測試的 `env_c` 加一組 `PYTHONIOENCODING=ascii`。

## 2. 收據寫歪(標頭或 expect 格式錯)回 1 並 Traceback,不是文件寫的 2
severity: minor
blocking: 否
引句:「qs[qid] = (dict(x.split('=', 1) for x in head.split()), sql)」
file: `scripts/templates/android-receipt-rerun.sh:20`(同類還有 `:72` 的 `k, v = p.split('=')`、`:15` 與 `:17` 的檔案讀取)
歸因:有證據的原有漏查。修前修後這幾行完全相同,但這輪才把「2 = 收據本身寫錯或環境沒準備好」寫進 `skills/lumos-android-evidence/reference.md`。
重現,修前修後都一樣:
- 標頭多一個沒有 `=` 的詞,例如 `-- [Q1] trace=t foo expect=…`:`ValueError: dictionary update sequence element #1`,rc=1。
- `expect=f1:compose_ns`(沒有 `=`)或 `expect=f1`:`ValueError: not enough values to unpack`,rc=1。
- 缺 `manifest.json`:`FileNotFoundError`,rc=1。
- `queries.sql` 是 UTF-16(PowerShell `>` 預設會寫成這樣):`UnicodeDecodeError`,rc=1。

後果:呼叫端無法分辨「收據寫錯」和「量測比對不符」。同一輪新增的 rc=2 語意因此只對一部分寫錯情形成立。

## 3. 測試抓不住拿掉 errors='replace'
severity: minor
blocking: 否
引句:「r = subprocess.run([tp, trace, '-q', f.name], capture_output=True, text=True, errors='replace')」
file: `scripts/templates/android-receipt-rerun.sh:58`;測試在 `scripts/test_lumos.py` 的 `t_android_ui_attribution_receipt_rerun`
歸因:有證據的原有漏查(`errors='replace'` 從前就在,這輪只拿掉 `encoding='utf-8'`)
- **破壞實驗**:把 `, errors='replace')` 拿掉,`-k android_ui_attribution_receipt_rerun` 仍是 6 passed, 0 failed。
- **真實風險**:Trace 裡的區段名是 App 任意位元組。分析工具輸出含非法 UTF-8 時,沒有這個參數就會 `UnicodeDecodeError`,rc=1。
- **重現**:假工具輸出 `"a\377b"`,有這個參數時 rc=0,沒有時 rc=1 並 Traceback。
- **建議**:測試補一組輸出含 `\xff` 的假分析工具。

## 其餘修補的驗收
這些都沒找到問題。

- **PYTHONUTF8=1 取代 reconfigure(在複本上逐項破壞實驗)**
  - 去掉 `PYTHONUTF8=1`:在 LC_ALL=C 的兩條斷言轉紅。
  - queries 或 manifest 各拿掉一處 `utf-8-sig`:BOM 那條各自紅。
  - 去掉 `finally` 的 `os.unlink`:暫存檔殘留那條紅。
  - 把分析工具執行不了的退出碼改成 1:「回 2」那條紅。
- **子程序解碼**:UTF-8 模式下 `text=True` 的預設編碼就是 UTF-8,`errors='replace'` 保留,正常路徑沒問題(缺口見第 3 條)。
- **重跑腳本的使用者**
  - 這支腳本只被 `t_android_ui_attribution_receipt_rerun`、`t_android_evidence_rerun_refuses_empty` 和 skill 的 `SKILL.md:138` 用;`SKILL.md:138` 寫「回 2 是收據本身寫錯,照它印的原因修」,新增的「找不到分析工具」訊息自帶 `TP=` 提示,不衝突。
  - 分析工具執行不了現在回 2,而它先前只會 Traceback 回 1,所以沒有任何呼叫端原本依賴「執行不了 = 1」。
- **授權守衛**:`f.lower().endswith(".sql")` 只影響註解符號判斷,前置斷言涵蓋 `x.SQL`、`.sql` 寫 `#` 不收、其他檔只認 `#`。
- **複製清單**:`scripts/lumos` 的 `_VENDORED_TREE_FILES` 與 `.sh` 並列登記,`-k vendored` 92 條全綠。
- **SQL 範本**
  - 範本整份貼進 `queries.sql`:`-- -- [Qn]` 那行不會誤配標頭。
  - `NULL` 區段名經 `IS` 能接上。
  - 遞迴 CTE 有 `dur >= 0` 擋住沒收尾區段。
  - `{{NAME}}` 與 `__NAME__` 兩種佔位字的說明,已對照 `scripts/templates/*.md` 屬實。

## pitfalls manifest 逐條判斷
全部誤報,7 條。

- `scripts/templates/android-receipt-rerun.sh:15`、`:17`:`json.load(open(...))` 和 `open(...).read()` 沒有 `with`。這是一次性短命腳本,CPython 在該陳述式結束時立即關檔,判誤報。
- `scripts/templates/android-ui-attribution.sql:31`、`:47`、`:52`、`:68`、`:78`:`SELECT … FROM` 都在同一條遞迴 CTE 內,不在迴圈裡,沒有 N+1,判誤報。

## 圖譜固定席逐條
- `Systems/授權與歸屬.md` 的 ★INVARIANT★(授權檔不進白名單、被複製的檔至少要有 SPDX):新增的 `.sql` 帶 `--` 的 SPDX,守衛測試綠。
- 另外五條固定席合約(`lumos-cli-read.md`、`測試假綠形態.md`、`design-loop.md`、`bound-tests-gate.md`、`guard-kill.md`,各有一條 ★INVARIANT★)與 `lumos-cli-lifecycle.md`、`pitfalls-code-loop.md` 的節點:這次改動沒碰到它們管的行為,無違反。

## 慣例(CLAUDE.md)
沒有能逐字引出規則並指出違反行的項目。

## 三問
1. **修復有沒有效?** 有。macOS 的測試綠,破壞實驗各自轉紅,Linux 容器的修前修後輸出另有 r3 紀錄,我沒重跑。
2. **修補有沒有引入新問題?** 有一個:第 1 條,`PYTHONIOENCODING` 非 UTF-8 時輸出崩潰。只在刻意設了該變數時發生,失敗方向安全。
3. **新發現的案例在修前修後各是什麼?** 第 1 條修前 rc=0、修後 rc=1。第 2、3 條修前修後相同,屬原有漏查。

總結:最高嚴重度 minor
