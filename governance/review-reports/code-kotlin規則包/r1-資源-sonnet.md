severity: major

資源面整體沒問題,唯一的 major 是測試在有 ast-grep 的機器上會紅,而 CI 一定有 ast-grep。我用 `/Users/enzo/lumos-scratch/android-checks/venv/bin/ast-grep` 實跑量過。

**資源面量測結果**
- `check.py` 完整跑一次(208 條規則、1.9MB 規則包、339KB 型錄):約 0.7 秒。
- 新測試實際耗時:
  - `kotlin_rulepack` 約 2.7 秒。
  - `lint_new_astgrep` 約 2.9 秒。
  - `lint_new_include` 約 19 秒。
  - `kotlin_catalog` 約 2.1 秒。
  - 離單支 180 秒上限都很遠。
- `check.py` 讀型錄是一次讀完,但 339KB 不構成壓力。`_CELL_RE` 只在單行上跑,我沒找到二次方行為。
- 測試建的暫存目錄(`gctl-ktpack-*`、`gctl-lnitp-h-*`、`mkdtemp()`)都落在 `main()` 設的 `gctl-run-*` 根底下。測試全綠時整個根目錄會被清掉,所以這一條沒有問題。
- 我自己跑測試留下的三個 `gctl-run-*` 現場已用字面路徑刪掉。

severity: major
blocking: 是
`scripts/test_lumos.py`(`t_kotlin_rulepack_samples`,diff 第 637 行):「路徑過濾沒錨在 src/ 要報祖先目錄命中」那段改壞用的原字串在真規則檔裡不存在,所以測試丟例外。
引句:「_ktpack_edit(f, "'**/src/test/**'", "'**/test/**'")」
場景:真檔 `configs/ast-grep/kotlin-android/rules/coroutines.yml:362` 寫的是 `files: ['**/src/test*/**', '**/src/androidTest*/**']`。`_ktpack_edit` 的 `assert old in t` 因此失敗。
重現(`LUMOS_AST_GREP` 指到上面的 ast-grep 後):
`python3.14 scripts/test_lumos.py -k kotlin_rulepack`
輸出:
```
✗ t_kotlin_rulepack_samples EXCEPTION: …/coroutines.yml 找不到要改的字:'**/src/test/**'
17 passed, 1 failed
```
CI 一定裝了 ast-grep 0.51.1,所以這支必紅。紅的時候還會把暫存現場(`gctl-run-*`)留在磁碟上。

severity: minor
blocking: 否
`scripts/test_lumos.py`(`t_kotlin_rulepack_samples` 與 `t_lint_new_astgrep_kotlin_two_files`):本機沒裝 ast-grep 時,測試印了略過就直接 return,但沒有走 `_SrcOnly` 跳過通道。
引句:「print("  ⊘ 本機沒裝 ast-grep,略過(CI 會跑)")」
場景:沒裝 ast-grep 的機器跑 `-k kotlin_rulepack`,輸出是「跑完了但一條斷言都沒有(沒驗過≠通過…)」,算紅,並留下 `gctl-run-*` 現場。實測得到 `15 passed, 1 failed`。這和測試自己的說明矛盾,也會拖累推送前的閘,還多留一份暫存。

severity: minor
blocking: 否
`configs/ast-grep/kotlin-android/check.py:239`、`252`:`subprocess.run` 沒有 `timeout`。
引句:「r = subprocess.run([sg, "scan", "--config", str(HERE / cfg), "--json=stream", str(target)],」
場景:ast-grep 卡住(例如樣本目錄被塞進病態大檔或壞符號連結)時,`check.py` 和兩支真跑測試會無限等,直到外層 180 秒殺掉測試,ast-grep 子程序可能變孤兒。現況每次 0.2 秒,所以這是防禦性缺口。建議加 `timeout=60`,並把 `TimeoutExpired` 轉成 `problems`。

severity: minor
blocking: 否
`scripts/test_lumos.py`(`t_lint_new_include_test_paths`):`run()` 被呼叫 4 次,每次都建一份 `gctl-lnitp-h-*`,最後還多一個 `tempfile.mkdtemp()`,全都沒自己清。
引句:「helper = Path(tempfile.mkdtemp(prefix="gctl-lnitp-h-"))」
場景:全綠時靠整個 `gctl-run-*` 根被清掉就沒事。但測試一紅,這些目錄會跟著現場留著,不能單獨清;而且這支測試實測 19 秒,是這批裡最慢的(`sys` 8.7 秒)。影響很小。

總結:`check.py` 本身時間、記憶體都很輕,暫存也由測試根統一清掉;唯一的 major 是 `t_kotlin_rulepack_samples` 的改壞步驟引用了真規則檔裡不存在的字串,CI 上會紅。
