severity: major

我逐 hunk 讀完整份 diff,並在臨時 clone 實跑。clone 上 `-k android_e2e`、`-k macrobench`、`-k vendored` 都全綠(分別 202、202、107 條),所以下面三條 major 都是現有測試沒蓋到的。臨時目錄已用字面絕對路徑刪除。

## F1 中斷時直接 SIGKILL 整組,收集腳本與 toolkit 的收尾不會跑,各自另開 session 的後代還活著
severity: major
blocking: 是

引句:「os.killpg(p.pid, signal.SIGKILL)」

- **路徑:**
  - 範本腳本收到 TERM、HUP、INT 後,走 `run()` 的 `except BaseException: kill_group(p)` 和 `main()` 的 `for p in list(GROUPS): kill_group(p)`,一律 `SIGKILL` 整組,沒有先送 TERM 給收尾時間。
  - `android-stability-collect.sh` 自己會接 TERM,並在 `cleanup()` 停裝置上的 perfetto 錄製、刪原始 logcat、殺它的驅動。
  - 但它的每個子程序都是 `start_new_session=True`,各自成組,殺它那一組碰不到它們。
  - toolkit 的 `visual-check.sh` 靠 `trap ... EXIT` 做 `vb_demo_exit` 和 `rmdir` 鎖,SIGKILL 下 trap 不會跑。
- **實測:**
  - 用假的 `visual-check.sh`,它設了 `trap ... EXIT TERM`,並用 `start_new_session` 放出一個 `sleep 300` 後代。
  - 對範本腳本送 TERM 後,trap 寫的 `cleaned` 標記沒出現,`sleep 300` 還在跑。
  - 實際影響是:Ctrl-C 或 TERM 後,Maestro 驅動可能繼續操作裝置,裝置上的錄製(含使用者資料)不被停掉。鎖已放掉,下一次驗收會在這種狀態下接手。kill -9 範本腳本本身是同一個結果。
- **測試抓不到:**
  - 把 `run()` 的 `kill_group(p)` 和 `main()` 的 `kill_group` 迴圈都刪掉,`t_android_e2e_run_script` 仍是 29 條全綠,假 maestro 變成孤兒繼續睡。
  - 該測試只驗回傳碼、`steps.json` 和鎖,沒有驗子程序是否收乾淨。
- file: `scripts/templates/android-stability-collect.sh:60-70` 每個子程序 `start_new_session`,`:508-520` 的 `cleanup` 靠收到 TERM 才跑。
- 建議:先 `killpg(SIGTERM)` 等數秒再 `SIGKILL`,並補一條會檢查子程序是否收掉的測試。

## F2 關掉終端(HUP)或 stderr 寫不出去時,不呼叫 judge,`steps.json` 也不標中斷
severity: major
blocking: 是

引句:「st.data["interrupted"] = True」

- **路徑:**
  - `except (Terminated, KeyboardInterrupt)` 先設 `interrupted=True`(只改記憶體,還沒存檔)。
  - 下一行 `print(..., file=sys.stderr)` 沒有保護。終端被關後 stderr 寫入會得到 EIO,管線關掉則是 EPIPE。
  - 例外從 except 區塊逸出,`finally` 放掉鎖,之後的 `st.save()` 和 `judge(run_dir)` 都沒執行。
- **S16 明寫:** HUP 中斷要寫出 `steps.json` 並呼叫 judge。
- **重現:**
  - 假 adb 和假 maestro,maestro 睡著。
  - 啟動後關掉 `p.stderr`,再送 SIGHUP。
  - 輸出:`rc 120`,`interrupted on disk: False ended: None`,`e2e-records` 的 history 只有先前的 `['r1']`,沒有這次。
  - 這個重現用 EPIPE 代替 tty 掛斷的 EIO,走的是同一條 `print` 例外路徑。
- 另外:`die(...)` 和 `judge` 的訊息 print 也沒保護。最小修法是先 `st.save()`,再用 try/except 包住所有中斷路徑上的 print。

## F3 門檻檔裡同一個 check 有別的情境或別的裝置的條目時,記憶體塊永遠判成 unjudged
severity: major
blocking: 是

引句:「skipped = [r for r in res.get("threshold_skipped", []) if r.get("check") == c]」

- **路徑:**
  - `_e2e_judge_stability` 對每個 check 聚合 passed 和 skipped,沒有按情境或 `device_model` 篩。
  - `_macrobench_stab_skip_reason` 對「情境不符」和「`device_model` 不符」的條目一律放進 `threshold_skipped`(`scripts/lumos:40077`、`:40079`)。
  - 輸入:門檻檔有 `exits` 在 `pkg.Leak#cycle`(本次情境)和 `exits` 在 `pkg.Other#x`。
  - 結果:前者在 `passed`,後者在 `skipped`,走到 `elif skipped or not passed` 就是 unjudged,reason 是「結果檔是情境 …,不是這條的 …」。
- **與設定檢查矛盾:** `_e2e_thresholds_err` 只看本情境有沒有條目,所以 `--check-config` 回 0,判定卻永遠沒判完。
- **影響:** 下一批的推送檢查會把這種專案永遠擋住。一個專案在 `.lumos/macrobench-thresholds.json` 裡寫了多個情境,或同一情境按裝置分條,就會中。
- **重現:** 在 clone 的 `scripts/test_lumos.py` 加了一支測試,用 `_e2e_proj` 和 `_e2e_steps`,構造上述 `threshold_passed` 加 `threshold_skipped`。輸出 `RESULT unjudged [{'check': 'exits', 'result': 'unjudged', 'reason': '結果檔是情境 pkg.Leak#cycle,不是這條的 pkg.Other#x'}]`,斷言「本情境全過卻被判 unjudged」紅。
- 這份輸出形狀是照 `_macrobench_judge_stability` 的程式手工構造,不是真跑 macrobench 得到的。
- 建議:判定只收 `scenario` 等於設定情境的條目,`device_model` 不符的 skipped 不算。

## F4 範本腳本只在回傳碼非 0 時重跑 flow,回傳碼 0 但報告沒案例時不重跑
severity: minor
blocking: 否

引句:「            if rc == 0:」

- 計劃〈一次驗收跑什麼〉寫「沒過再跑一次」,而「沒過」包含回傳碼 0 但報告零案例或有失敗。judge 也照這個判(`t_android_e2e_judge_ui` 的「回傳碼 0 但零案例」)。
- 輸入:Maestro 第一次回 0,但 JUnit 報告零案例。腳本在 `accept()` 的 `for attempt in (1, 2)` 迴圈裡 `break`,不跑第二次。judge 只看到一次嘗試,判 fail(「第 1 次:報告裡沒有任何測試案例」)。
- 跟計劃表和 WHY(不穩定的重跑)不一致,會誤擋。

## 圖譜鏡頭(固定席節點)
- **`pitfalls-code-loop`(RISK):** 簿記目錄清單加 `.lumos/e2e-records/` 是同一個元組。我核對了 `_BOOKKEEPING_DIRS` 的各個消費者,都只是排除路徑前綴。「簿記資料夾底下程式檔不算簿記」那條既有判法不受影響,不破壞合約。
- **`lumos-cli-lifecycle`(re-inject):** 只在 `_VENDORED_TREE_FILES` 加一項,不碰 sentinel 以外的內容,`-k vendored` 全綠。
- **其餘:** `lumos-cli-read` 的 search 排除 superseded、`guard-kill` 的 rc 優先序與 JSON 純度、`design-loop` 處置閘、`bound-tests-gate`、`loop-convergence-recording`、`reversibility-governance-ledger` 在這批 diff 中都沒有對應程式路徑,不受影響。

其餘各項沒找到具體失敗輸入,所以沒標:flow 名在腳本和 judge 的算法一致(含點號目錄、無副檔名、`./` 前綴都對得上);指紋對 `app/src2`、符號連結、子模組、中文檔名正確;steps.json 和紀錄的 schema 新舊互讀會被擋下;`--results-dir` 在沒有設定檔、空目錄、不存在目錄時行為合理。

最高 severity: major,blocking 3 條(F1、F2、F3)。
