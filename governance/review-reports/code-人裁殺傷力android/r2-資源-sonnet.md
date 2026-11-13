severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/47ebf45980d0bdbe5649fdd88d49a06caa7c1a9c79bc3e574bbe39410d0647f9.json.warming` 不存在,沒有東西要處理,也沒刪任何鎖。

## z1 檔頭掃描每行建一個 dict,4MB 空白行的 .kt 檔讓記憶體放大約 250 倍
severity: minor
blocking: 否
引句:「rows.append({"i": i, "code": t, "kind": kind, "clean": depth == 0 and paren == 0})」
file: `scripts/lumos:76254`(`_situation_rule_header_scan`)、`scripts/lumos:76302`(`_situation_rule_imports_problem` 呼叫它)、`scripts/lumos:40111`(`_KT_SIT_READ_MAX` = 4MB)

失敗場景:
1. 輸入是 HEAD 那版 4MB 的 .kt 檔,內容是 `package a` 後面接約 4M 個空行。這剛好卡在讀檔上限內,`_kt_sit_read_many` 放行。
2. 人裁帶 `--import` 時,`_situation_rule_imports_problem` 呼叫 `_situation_rule_header_scan`。空行和註解都會繼續掃,沒有 break,所以每一行都建一個四欄 dict。
3. 修補前的 `_situation_rule_header_rows` 只存 `rows.append(i)`,一個整數。
4. 我實測 `_situation_rule_imports_problem(src, "Foo", ["import x.Foo"])` 的結果:

| 輸入(4MB) | 耗時 | 峰值 RSS |
|---|---|---|
| 空行 | 3.1 秒 | 約 1017MB |
| 每行 `// c` | 0.6 秒 | 約 284MB |
| 開頭 `/* ` 不收尾 | 1.7 秒 | 約 533MB |
| 一堆 `import a.B` | 1.2 秒 | 約 190MB |

5. 結果仍然是對的,只是記憶體不成比例。
6. 這個讀檔上限本來就是為了擋這類輸入,現在上限擋不住記憶體。
7. 補法:`rows` 改成只留 import 和 package 行,或用 `at` 的候選索引,空行和註解不建 dict。

翻紅重現:對上述 `package a\n` 加 `"\n"*(4<<20)` 的字串呼叫 `m._situation_rule_imports_problem`,用 `resource.getrusage` 量 `ru_maxrss`。修補前不到 100MB,現在約 1GB。

## 其餘資源檢查(沒發現問題)
- **fail_excerpt 與遮路徑**:`_kill_run` 回傳前已經過 `_kill_cap`,上限 256KB(`scripts/lumos:27807`),50MB 的 Gradle 輸出到不了 `_kill_mask_paths`。`re.escape(q)` 加上 `(?![\w.\-])` 是字面比對加一個字元的前瞻,沒有回溯爆炸。
- **`_android_build_texts`**:每次人裁最多一次 `max_depth=3` 的掃描(`"test" in tasks` 時)。另外每個 `<模組>:test` 任務一次 `max_depth=0` 的掃描,只列一個資料夾。
- **`_gradle_module_candidate` 往上找**:到平台根為止,條件是 `d.startswith(root + os.sep)`,碰到 `/` 或 repo 外就停。
- **`_detekt_walk_segments`**:`sh -c` 只展開一層(`depth == 0`),不會遞迴爆炸。
- **新的 error 路徑**:`_kill_run_dir` 失敗時,`continue` 在 `with _iw` 區塊內,隔離工作樹由 context manager 收掉。`_kill_run_dir` 本身不開子程序。
- **`top_ctx`**:每次 `cmd_guard_kill` 一個,同一個平台根只跑一次 `git rev-parse`,不隨配方數增加。
- **`--diff` 驗證**:這份修補沒有改它。

## 附:圖譜鏡頭
這次派工沒附固定席節點,我只憑程式碼判斷。唯一碰到的筆記是 `Systems/guard-kill.md` 第 48 行,它寫的是 run_cmd 改在平台根跑,宣稱和程式一致,我沒發現矛盾。它自己標了代價:平台根是子資料夾、run_cmd 原本寫成從 repo 最上層跑的舊設定要改成從平台根寫。這個取捨已寫明,所以不算新問題。

最嚴重 severity:minor,blocking 共 0 條。
