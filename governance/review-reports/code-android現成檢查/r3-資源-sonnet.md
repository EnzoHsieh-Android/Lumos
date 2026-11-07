severity: clean

我在 `android-blind-judge` 實量了五個鏡頭,沒有發現會擋的資源問題。數字都是在別的會談同時跑測試、機器負載偏高時量的,偏保守。審查中途我自己寫的壓測腳本寫錯,開出約 620 個程序,已全部殺掉。

**①`_android_build_texts` 與 `_android_lint_config_evidence`(用 `lint-check --repo <臨時目錄> --json`)**
- 基準(只有一支建置檔)約 0.96 秒,峰值記憶體 365 MB。
- 5 萬個資料夾:6.57 秒,峰值 364 MB。函式單獨量,`_android_build_texts` 約 2.2 秒,新增的 `_android_lint_config_evidence` 約 2.3 秒。後者每次再整棵走一遍,所以這個場景的走訪成本變兩倍。真實 Android 專案的 `build`、`.git`、`node_modules` 都在跳過名單,不會碰到這個量。
- 符號連結迴圈 0.96 秒、具名管道當建置檔(含 `gradle/libs.versions.toml`)0.98 秒,都沒卡住。
- 1000 支建置檔 1.20 秒、峰值 365 MB,200 支上限有生效。
- 250 支各約 1.9 MB 的建置檔(實讀 200 支、每支 1 MB 上限):14.9 秒、峰值 389 MB。這是剝註解本身的線性成本,不是這輪新增的。
- 80000 行或 35 萬次 `" #` 的 `libs.versions.toml`:0.84 秒和 0.76 秒。新的 `_ci_strip_comment` 路徑是線性的。

**②`_android_ci_lint_evidence`**
- 50 MB(170 萬行)CI 檔整條 lint-check:10.5 秒、峰值 602 MB。其中 `_android_ci_lint_evidence` 本身約 5.2 秒,其餘是既有的讀檔去註解。
- 一行一百萬字元:`a` 重複、`a:` 重複、`lint:` 重複、`android-` 重複、`lintFix ` 重複的各種形狀都在 0.01 到 0.23 秒內,沒有回溯。
- 把 `a:` 重複次數加到 40 萬,耗時也只到 0.06 秒,隨長度線性增加。
- 40 萬行 `gradle lintKotlin lintFix lintVital`:1.85 秒,線性。
- `_ANDROID_LINT_WORD` 和 `_CI_WORD_SPLIT` 都沒有回溯問題。

**③`_detekt_walk_segments`**
- 2 萬次隨機組合的壞命令(引號不成對、反斜線、巢狀 `sh -c`、NUL、孤立代理字元)沒有丟例外。`None`、數字、列表、字典輸入也都回空。
- `sh -c` 只展開一層(`depth == 0`),所以巢狀很多層不會遞迴放大。
- 超長命令是二次方:單一 10 萬字元長詞要 7.0 秒,10 萬字元的 `;&|` 要 8.0 秒,10 萬個引號不成對的 `x ` 要 13.7 秒。同樣內容放大 10 倍,耗時大約是 40 倍到 160 倍。
- 根因在標準庫 `shlex` 本身:單獨量,10 萬字元要 2.8 秒。`_detekt_split_segments` 在這輪之前就已經用它,這輪沒有新增這個成本,我也沒有為此標 finding。
- 一般長度的命令(1 萬字元)都在 0.2 秒內。

**④doctor 的 20 條上限**
- `_aadv[:20]` 外加一行「… 另 N 條」。我用 20、21、1000、20000 條 kt 命令,都只顯示 21 行。
- 算 2 萬條 A3 花 0.76 秒,上限限住的是輸出行數。
- `lint-check` 指令本身不設上限,但訊息已寫明「lumos lint-check 看全部」,這是設計。

**⑤新增測試**
- `-k lint_android_ci_advice`:全部 91 個通過,`t_lint_android_ci_advice` 72.0 秒(r2 報的是 74 秒,沒變慢)。峰值記憶體 762 MB,測試框架提示「餘裕不足 3 倍」(超時上限 180 秒)。
- 耗時主要來自約 55 次 `lint-check` 子程序,每次約 1 秒。這是 r2 以來的既有狀態,這輪沒有惡化。
- 我把 `TMPDIR` 指到臨時目錄跑,結束後是空的,`gctl-andci-*` 沒有殘留,也沒有卡住的子程序。
- 環境變數 `HOME`、`LUMOS_T_PLUG`、`LUMOS_T_UNSET_X` 有放在 `finally` 裡還原。

圖譜鏡頭:派工詞沒附固定席,範圍也算不出來,我沒讀 `Systems/lint-declaration-health.md`、`Systems/bound-tests-gate.md`,所以不判有沒有破壞它們宣稱的行為。

我的臨時目錄 `/tmp/lumos-seat-work/code-android現成檢查/資源-sonnet` 已用字面絕對路徑刪除。沒有改 repo,也沒有做 git commit、reset、restore、checkout、stash。

總結:最嚴重是沒有 finding(clean),會擋 0 條。
