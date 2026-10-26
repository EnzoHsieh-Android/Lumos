severity: minor

整份 diff 逐 hunk 讀完,也讀了 `_e2e_judge_stability`、`_e2e_judge_macrobench`、`_dirty_non_bookkeeping`、`_e2e_print_runs`、`Steps.step` 等被牽連的函式。我沒有找到會損壞資料的缺陷,也沒有會擋推送的發現。範本腳本與 lumos 之間的介面(select 的 JSON、`judge --no-record/--history`、steps.json 的 `selection`/`dirty` 欄)兩邊對得上。F1 到 F6 屬會出錯的行為,但都沒有真機重現,所以都列為輕度。F7 是純清理。

## F1 多個效能測試方法跑完才一次收結果,前面的結果可能被後面蓋掉
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh`(accept 的 macrobench 迴圈,diff 約 963 到 971 行)
失敗場景:`{{TEST}}` 展開成多個方法時,迴圈把每個方法各跑一次 Gradle,迴圈跑完才呼叫一次 `collect_results(cfg, t0, mdir)`。Macrobenchmark 的 `*-benchmarkData.json` 檔名通常每個模組固定,每次 Gradle 執行會覆寫。若是如此,`--feature` 挑到兩個以上的效能方法時,總表與判讀只看得到最後一個方法的數字,前面的被靜默丟掉。修法是每跑完一個方法就收一次,並按方法名分目錄。未能重現,因為沒有真機,所以降為 minor。
引句:「st.step("macrobench", ["sh", "-c", cmd], name=t, env=env)」

## F2 開跑時工作目錄有未提交改動、跑完卻變乾淨,仍會寫成「這一版驗過」的正式紀錄
severity: minor
blocking: 否
file: `scripts/lumos`(`_e2e_feature_record`,diff 約 404 到 438 行)
失敗場景:
- 開發者帶著未提交的修改跑 `--changed`,APK 是用髒樹建的,`steps["dirty"]` 因此記成 True。
- 跑的期間他用 `git checkout -- .` 或 `git stash` 把改動丟掉,HEAD 沒變。
- judge 時 `_e2e_precheck` 通過,`start_head == head`,就把 `feature_runs.<情境> = pass` 以 HEAD 的指紋寫進正式紀錄。
- 但被驗的 APK 並不是 HEAD 那版。
- `Steps.__init__` 特地記了 `dirty`,卻只有 `_e2e_history_append` 在用,`_e2e_feature_record` 沒有查它。
- 修法是 `steps.get("dirty")` 為真時一律不寫查證紀錄。
- 規格〈按功能跑〉寫的是「工作目錄乾淨、HEAD 沒換」,條文本身沒涵蓋「開跑時髒、結束時乾淨」。
引句:「self.data["dirty"] = lumos("android-e2e", "judge", "--repo", root, "--precheck")[0] != 0」

## F3 `--no-perf` 或 `--no-memory` 單獨使用時被靜默忽略,整套照跑還寫整套紀錄
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh`(引數解析,diff 約 762 到 778 行)
失敗場景:
- 使用者跑 `sh android-e2e-run.sh --no-memory`,想整套跑但省掉記憶體。
- 旗標被收進 `FLAGS`,但 `SELECTIVE` 只看 `--feature`、`--case`、`--changed`。
- 結果是記憶體照跑,耗時最長的一段沒省到,而且寫的是整套 `runs`。
- 同樣的旗標交給 `lumos android-e2e select` 卻會回「沒挑到任何情境」,兩邊行為不一致。
- 修法是單獨出現時擋下並說明。
引句:「SELECTIVE = bool(PICK["--feature"] or PICK["--case"] or "--changed" in FLAGS)」

## F4 效能測試方法名的字元限制只在跑到一半才檢查,設定檢查時不擋
severity: minor
blocking: 否
file: `scripts/lumos` 的 `_e2e_case_err`(只驗非空字串);`scripts/templates/android-e2e-run.sh` accept(diff 約 965 到 966 行)
失敗場景:
- 對照表寫了含空白或 `$` 的方法名,`macrobench --check-config` 和 `select` 都放行。
- 腳本要等建置、安裝、全部 flow、記憶體都跑完,才在效能那段 `die`。
- `die` 直接 `sys.exit(2)`,不經 Steps 收尾,steps.json 沒有 `ended`,judge 也沒被呼叫。
- 一次長跑白費,而且不留總表。
- 這條規則應搬進 `_e2e_case_err`,與其他格式檢查放在一起。
引句:「die(f"效能測試方法名只收英數字、點、#、底線:{t!r}")」

## F5 整套跑時,judge 寫不進紀錄就整筆不進總表
severity: minor
blocking: 否
file: `scripts/lumos`(`_e2e_judge_cmd`,diff 約 614 到 616 行)
失敗場景:
- 整套跑的 `_e2e_history_append` 排在寫紀錄成功之後。
- 跑的期間 HEAD 換了、跑完工作目錄髒了,或 `_e2e_record_update` 失敗時,都在 `why` 或 `werr` 提前回 2。
- 整場很長的驗收就完全沒進 history.jsonl。
- 範本腳本與 `--history` 的說明寫的是「每次都記」,docstring 也寫「過或沒過都記」。
引句:「_e2e_history_append(root, steps, runs, "full")」

## F6 打錯的旗標會被當成 run-id,於是不帶挑法整套跑
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh`(引數解析,diff 約 775 行)
失敗場景:
- `--chaged` 這類打錯的旗標落進 `rest`,`rest[0]` 成了 run-id。
- run-id 的字元規則允許連字號,所以通過檢查。
- 結果是整套跑、寫整套紀錄,目錄名叫 `--chaged`。
- 這次新增了五個旗標,打錯的機率變高。
- 修法是以 `-` 開頭而不認得的引數一律擋下。
引句:「elif a != "--preflight":」

## F7 `_e2e_judge_partial` 的 docstring 與實際行為相反
severity: minor
blocking: 否
file: `scripts/lumos`(`_e2e_judge_partial`,diff 約 356 到 377 行)
失敗場景:
- docstring 寫「不碰 `.lumos/e2e-records/`」。
- 函式尾端的 `_e2e_feature_record` 在乾淨樹上會寫該目錄(規格 S27 也要求如此)。
- 下一個讀碼者會被誤導,可能把這個寫入當成 bug 拿掉。
- 這是純文件問題,docstring 應改成「髒樹時不碰;乾淨時只寫 `feature_runs`」。
引句:「selection 列的東西,不碰 .lumos/e2e-records/。rc 0=選到的都過;1=有沒過或沒判完;2=設定或 steps.json 讀不懂。"""」

## pitfalls manifest 判定
內建那一題是 `open(` 的 handle 題,本次 diff 新增的只有 `_e2e_history_append` 裡的 `with open(p, "a", encoding="utf-8") as fh:`,在 `with` 裡,有關閉。範本腳本新增的部分沒有新的 `open(`。收集腳本既有的 `json.load(open(...))` 不是這次引入的。判定是誤報、沒有真隱患。ruff 回報的 4489 筆全是既有舊帳,略過。

## 圖譜鏡頭
固定席節點裡,`lumos-cli-read` 的 search 與 superseded、`guard-kill` 的 rc 優先序與 JSON 純度、`lumos-cli-lifecycle` 的 re-inject、`測試假綠形態`、`bound-tests-gate` 的各條 ★INVARIANT★,碰的都是別的函式。這次 diff 只動 android-e2e、macrobench 設定與 argparse 分派,沒有碰到這些合約的程式路徑。

`測試假綠形態` 的「還原翻紅釘要配前置斷言」這條有照做:新測試用了 `★前置★` 風格,並用 `flows_run(fake)` 確認現場真的跑到被測分支。`pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger` 這三個 ★RISK★ 節點,與這次改動沒有可指的牽連。

計劃筆記〈按功能與使用情境跑〉S22 到 S27 與實作大致一致,對不上的只有 F2 與 F7 兩處。

整體沒有 major,最需要處理的是 F2(開跑時髒、結束時乾淨的紀錄語意)和 F1(多個效能方法的結果收集時機),其餘是邊角行為與清理。
