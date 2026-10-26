severity: minor

派工詞要我檢查的鎖檔 `…/93aaa64b….json.warming` 不存在(cat 回「No such file」),所以沒有需要處理的鎖。

## F1 效能方法與記憶體情境逐個跑,每個都有一小時上限,卻沒有整體預算
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh` 的 `accept()`,即 `for i, t in enumerate(tests)` 與 `for scn in stab_to_run(cfg)` 兩個迴圈。每個 `st.step(...)` 預設 `timeout=T_LONG`(3600 秒)。
失敗場景:`features` 裡列了 10 個效能方法,`macrobench_cmd` 在裝置掉線時卡住。每個方法各自等滿 3600 秒,迴圈不會因為前一個逾時就停,總共約 10 小時,期間一直握著裝置鎖。以前整條指令只跑一次,最多 1 小時。記憶體情境同理:整套跑是 1+S 次收集,每次最多 3600 秒。
歸因:未判定(不確定是不是回歸)。這個迴圈在修前(787dd51b)已經存在,修補只改了方法名的正則。我只讀了程式,沒有跑假裝置來量實際耗時。
引句:「            st.step("macrobench", ["sh", "-c", cmd], name=t, env=env)」
兩版查證:`git show <版本>:scripts/templates/android-e2e-run.sh | grep -n 'for i, t in enumerate(tests)'`。修前 481 行有,修後 484 行有。

## F2 每個記憶體情境另開的目錄裡,cycle.pftrace 與 logcat 不會被清
severity: minor
blocking: 否
file: `scripts/templates/android-stability-collect.sh` 的 `prune_old_snapshots`(`heap-.*\.pftrace` 那一行,約 148 行)。
失敗場景:整套跑會產生 1+S 個 `<run-id>` 與 `<run-id>.<情境>` 目錄,每個都有 `cycle.pftrace`(錄製最長 600 秒)和 `logcat.txt`。清理只刪 7 天前的 `heap-*.pftrace`,其餘永遠留著。新加的按功能跑鼓勵開發中頻繁重跑,這些檔案線性累積。
實測:我在 `e2e-1` 與 `e2e-1.mem` 兩個目錄各放一份 30 天前的 `cycle.pftrace` 和 `heap-after.pftrace`,把腳本的 `prune_old_snapshots` 原樣抽出來跑。兩個目錄的 `heap-after.pftrace` 都被刪了(說明清理有掃到情境目錄),`cycle.pftrace` 兩份都還在。
歸因:有證據的原有漏查。清理規則在修前修後相同,實測用的是修後版本(我另外對修前版本做了 grep,同一行同一個正則)。情境目錄讓累積量乘上 1+S,屬於新功能放大。
引句:「        sid = run_id if scn is None else f"{run_id}.{scn}"」

## 三問的答覆
- **①原問題的修復效果**:本席鏡頭只核對了與資源有關的修補。
  - 效能方法名拿掉 `$`:兩版 `grep` 都看得到,修後正則是 `[A-Za-z0-9_.][A-Za-z0-9_.#]*`。
  - `--changed` 改成 `diff HEAD` 加 `ls-files --others`,任何一個 git 讀不到就回錯誤,不當成沒改動。我只讀了程式,沒跑。
  - 其他修補我沒有逐項跑到。測試子集(`-k android_e2e`)也沒跑。
- **②修補處的正常、錯誤與相鄰路徑**:
  - 子程序都走 `run()`:每個自成程序群組,逾時或中斷時整組先 TERM 再 KILL,不會變孤兒。這是讀程式的結論。
  - `Steps` 的建構在 `try` 裡,鎖由 `finally` 放掉。`select()` 與 `preflight` 在拿鎖之前,中斷時 `run()` 會收掉子程序。
  - `judge` 在收尾階段用 `subprocess.run(timeout=600)`,逾時會殺子程序,回 2。
- **③同一案例修前修後**:F1、F2 兩條的修前修後行為相同(上面各附 grep 命令與結果),所以沒有修補造成的資源回歸。

## 其他已驗項目(新程式與修補都同樣成立)
- **總表寫入**:`_e2e_history_append` 用 `_local_ledger_append`,單次 `os.write` 加 `finally os.close`。帳尾沒換行會先補。`_ledger_tail_needs_newline` 也在 `finally` 關檔。沒有留下開著的 handle,也沒有寫一半的行。
- **總表讀取**:我造了 50000 行、231MB 的 `history.jsonl`,跑 `lumos android-e2e history --last 20`。實測 3.5 秒,最大常駐記憶體 339MB,跟只有 5 行時的 338MB 一樣。證明是逐行讀、只留最後 N 筆,不隨檔案長大。載入的是 e2e-docs 工作樹,HEAD 為 4b056532。
- **重複操作**:同一效能方法列在多個情境時,`_e2e_sel_add` 與 `tests_to_run` 都會去重,只跑一次。每次開跑多叫的 lumos 子程序是固定幾次(check-config、select、precheck 最多兩次、各情境的判讀、judge),各約 0.6 秒,相對於真機驗收可忽略。
- **`--changed` 的成本**:`_secev_mainline` 只叫本機 git,不碰網路。
- **新查證紀錄不影響下一次髒樹判斷**:`.lumos/e2e-records/` 在 `_BOOKKEEPING_DIRS` 裡。
- **未驗範圍**:真機整輪、`_vault_write_lock` 的逾時行為(併發類題目,範圍外)。

## pitfalls manifest
「scripts/lumos 寫總表那段的 open( —— 檔案 handle 有沒有 with/確定 close?」判為誤報。
- 寫總表那段(`_e2e_history_append`)根本沒有 `open(`,走的是 `os.open` 加 `finally: os.close`。
- 讀的那段用 `with Path(path).open("rb")`。
- 範本腳本新增的部分沒有裸 `open(`。

## 圖譜鏡頭
這次派工沒附固定席節點(`LUMOS-LENS` 寫明鎖狀態未知),屬於備援段,不逐條答。我也沒有自行查圖譜,因此沒有確認這份差異是否牴觸任何合約。

這份差異在資源面沒有 handle 洩漏、孤兒程序或總表膨脹問題,只有逐個逾時無整體預算、情境目錄的 `cycle.pftrace` 不清理兩條小問題。

臨時目錄 `/tmp/lumos-seat-work/code-e2e-by-feature/鏡頭2-資源-sonnet` 已用字面絕對路徑刪除。
