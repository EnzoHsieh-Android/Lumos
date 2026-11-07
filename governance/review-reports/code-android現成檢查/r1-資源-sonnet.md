severity: minor

審查範圍:程式、CI、設定與三支測試都逐 hunk 讀完。我另外造了大輸入實測,附在下面。

**F1**
severity: minor
blocking: 否
引句:「with open(root / rp, "rb") as fh:」
file: `scripts/lumos`(diff 內 `_android_build_texts`,現檔約 38995 行)。
- 它對 os.walk 的 `filenames` 逐個 open,沒有先確認是一般檔案。同一份 diff 的 `_ci_config_texts` 讀 workflow 時有用 `p.is_file()`,這裡沒有,兩處不一致。
- 重現:在 repo 根目錄放 `mkfifo build.gradle`(具名管道),跑 `lumos lint-check --repo . --json`。open 會無限期阻塞,10 秒後仍在跑,Ctrl-C 以外無出口。
- 影響:`lint-check` 和健檢(doctor)都會卡住。
- 現實中很少見,但修法只要一行(`os.path.isfile` 或 `stat.S_ISREG`)。

**F2**
severity: minor
blocking: 否
引句:「for dirpath, dirnames, filenames in _os.walk(root, followlinks=False):」
file: `scripts/lumos`(diff 內 `_android_build_texts`)。
- 深度上限在進入子目錄前就剪枝(`dirnames[:] = []`),所以 node_modules、build、`.gradle`、隱藏資料夾和符號連結迴圈都不會被進入。符號連結迴圈有造過,沒問題。
- 但「前 200 支」的上限只在整棵樹走完、排序之後才套用,走訪本身不會提早停。
- 實測:500×100 共 5 萬個空資料夾(深度 2)加兩個指回上層的符號連結,`_android_build_texts` 單次 1.86 秒。
- `lint-check` 整體 4.23 秒,最大常駐記憶體 520MB。這次還包含 50MB 的 CI 檔,大部分記憶體來自它,見 F3。
- 每次健檢和每次 lint-check 都會付一次這個成本。
- 目前還不到卡死的程度,所以只標 minor。若要省,可在走訪時對候選數設上限或限制單層目錄數。

**F3**
severity: minor
blocking: 否
引句:「out.append(p.read_text(encoding="utf-8", errors="replace"))」
file: `scripts/lumos`(diff 內 `_ci_config_texts`)。
- CI 設定檔整檔讀入,沒有大小上限,`_android_ci_has_lint_task` 又對它做 `splitlines`。
- 實測 50MB 的 ci.yml(約 52 萬行):`_android_ci_has_lint_task` 1.14 秒,T4 的 `_detekt_ci_has_typed_task` 0.41 秒,讀檔 0.01 秒(快取後)。
- `lint-check` 最大常駐記憶體 520MB,基底(空專案)是 365MB,多約 155MB。
- 建置檔每支只讀前 1MB,上限有守住。200 支 1MB 中文建置檔(共 298MB)實測 1.15 秒、502MB,比基底多約 140MB。
- 長行的正規式沒有災難性回溯:10 萬字元的單行 `build.gradle` 和 100 萬空白的單行都在秒內完成。
- 真實 CI 檔不會到 50MB,所以只是「可以更省」。

**資源面其他逐條結論**
- 子程序:新增的非測試程式碼沒有開任何子程序。
- 測試暫存:測試裡的 `mkdtemp` 和 `_lng_repo` 沒有各自清理,但整個測試跑道把 `tempfile.tempdir` 指到單輪根目錄,收尾時整個刪掉(`scripts/test_lumos.py:48703`)。
- detekt 子程序:測試用 `sp.run(..., timeout=300)` 起 detekt。`/opt/homebrew/.../detekt` 這支啟動腳本是 `exec java`,逾時時 kill 的就是 java 本身,不會留孤兒。
- 測試耗時:`t_lint_android_ci_advice` 實跑 34.8 秒,通過;`-k lint_android_ci_advice` 共 38 項全過。每次 `fresh()` 都起一次 `lint-check` 子程序,是耗時的主因,屬可更省。

**manifest(1 條)**
- 項目:`scripts/lumos:38995` 的 `\bopen\s*\(`,問「檔案 handle 有沒有 with/確定 close?」。
- 判定:誤報。該處是 `with open(root / rp, "rb") as fh:`,有 with 保證關閉。
- 但同一行帶出 F1 的真問題:open 前沒檢查是不是一般檔案,所以管道會阻塞。這與 handle 有沒有關無關。

**圖譜鏡頭**
- 派工詞附的 `LUMOS-IMPACT` 範圍在本專案算不出來,所以我改讀指定的三篇。我沒有逐篇細讀,只能給推論,不敢說已查證。
- `Systems/lint-declaration-health.md`:新增的提醒只讀檔、不進 `problems`、不改退出碼,diff 與測試都守住退出碼 0,不破壞宣告健康的合約。
- `Systems/hook逾時預算.md`:`_lint_android_ci_advisories` 只在 doctor 和 lint-check 呼叫,不在 hook 路徑上。這個判斷是我 grep 呼叫點得到的,對 hook 預算的影響不大。
- `Systems/bound-tests-gate.md`:diff 改了 `scripts/test_lumos.py` 與 `scripts/lumos`,屬於程式變更,推送閘會依改動分級,圖譜本身不受影響。

**總結:** max severity = minor,blocking 條數 = 0。
