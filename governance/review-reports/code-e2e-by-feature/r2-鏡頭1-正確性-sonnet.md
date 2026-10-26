severity: major

我拿修前 9e21d491 和修後 787dd51b 各 clone 一份,在臨時目錄跑實驗。實驗用 `_e2e_feat_env` 等測試輔助函式,修前版換上修後的測試檔。測試一律用 `python3.14 scripts/test_lumos.py -k android_e2e`,修後基線是 332 過、0 紅。臨時目錄(28GB)已用字面絕對路徑刪除。鎖檔 `…738bb93b.json.warming` 不存在,不需處理。

## F1 只列效能或略過後無項目可判的情境:終端與總表說「通過」,feature_runs 卻是 unjudged
severity: major
blocking: 是
file: `scripts/lumos:_e2e_judge_partial` 與 `_e2e_evaluate_selected`、`_e2e_history_append`。`_e2e_judge_partial` 的回傳碼只看整體 `runs["result"]`。`_e2e_evaluate_selected` 在沒有任何可判項目時把整體記成 pass。
失敗場景:專案有 `perf.only` 情境,只列 `macrobench: ["Bench#three"]`。跑 `--case perf.only` 或 `--case login.ok --no-perf` 時,可判的 flow、畫面和記憶體項目都是空的。
- 修後:回傳碼 0,終端印「Android 端到端驗收:通過」。本機總表 `history.jsonl` 的 `result` 是 pass,查證紀錄 `history` 那筆也是 pass。
- 但同一次的 `feature_runs["perf.only"]` 是 `unjudged`、`complete:false`,終端「情境 perf.only:沒判完」。三處記同一次結果,互相矛盾。
- 規格 S22 說「有沒過或沒判完時回 1」,S27 說這種情境是 unjudged,所以回傳碼和總表都該跟著走。
- 測試 `t_android_e2e_by_feature` 斷言 `perf.only` 的 `returncode == 0`,等於把錯的行為釘死。
- 附帶:這種情境的 `reason` 固定寫「(效能只提醒)」,即使真正原因是 `--no-memory` 略過了記憶體。

證據(同一案例 perf.only,修前與修後各跑一次,路徑對應 `<clone>/scripts/lumos`):
- 修前:rc 0、總表 `result:"pass"`,`feature_runs` 是 `{"result":"pass","complete":true,"items":[]}`。三處一致,但一個項目都沒判就記成完整通過。
- 修後:rc 0、總表 `"pass"`,`feature_runs` 是 `unjudged/complete:false`。矛盾是修補才出現的。

歸因:有證據的修復回歸。三處矛盾是修後才有;「沒判任何東西卻回 0」兩版都有。
引句:「result = "fail" if "fail" in rs else ("unjudged" if probs or "unjudged" in rs else "pass")」

## F2 效能測試方法名放行 `$`,交給 sh 後被展開,實際跑的是別的測試
severity: major
blocking: 是
file: `scripts/lumos:E2E_BENCH_NAME_RE`,範本腳本 `scripts/templates/android-e2e-run.sh` 裡 `.replace("{{TEST}}", t)` 之後走 `sh -c`
失敗場景:設定 `com.x.Outer$Inner#bench`,`macrobench_cmd` 是 `echo {{TEST}} >> bench.log`。`--check-config` 回 0,`--case login.ok` 回 0。實際執行的指令字串是 `echo com.x.Outer$Inner#bench`,`$Inner` 被 sh 展開成空字串,bench.log 寫的是 `com.x.Outer#bench`。`$1`、`$$`、`$#` 同理。註解寫了「會換進 macrobench_cmd 交給 sh」,卻放行了 sh 的展開字元。

證據(同一案例):
- 修前:舊規則是 `[A-Za-z0-9_.#]+`,不收 `$`。腳本回 2,印「效能測試方法名只收英數字、點、#、底線」,沒跑錯東西。
- 修後:回 0,bench.log 內容是 `'com.x.Outer#bench\n'`。

測試 `t_android_e2e_args_and_names` 的 `Outer$Inner#test` 只驗設定檢查通過,沒驗執行時的值。

歸因:有證據的修復回歸。
引句:「E2E_BENCH_NAME_RE = re.compile(r"[A-Za-z0-9_.$][A-Za-z0-9_.$#]*")」

## F3 S27 的紀錄可信條件和「不蓋掉完整結果」大半沒有測試
severity: major
blocking: 是
file: `scripts/lumos:_e2e_feature_record`(含內部 `_put`)、`_e2e_record_err`、`_e2e_case_results`
失敗場景:我在修後版本的拷貝上各改壞一處,跑完整 `-k android_e2e`,下面每個都是 332 過、0 紅(改壞的程式碼位置和用途):
- M1:拿掉判讀時的 `_e2e_precheck(root)`,判讀時工作目錄髒了也會寫。
- M2:拿掉 `start_head == head`,HEAD 換了也會寫。
- M3:拿掉 `or v["result"] == "unjudged"`,完整的 pass 會被「沒判完」蓋掉。
- M4:拿掉 `feature_runs` 型別檢查。
- M5:拿掉 `old.get("commit") == head`。
- M7:`_e2e_case_results` 拿掉 `probs or`,建置失敗時情境變成 pass。
- 對照組:拿掉 `_dirty_non_bookkeeping` 那行會紅(`by_feature` 1 紅、`changed_pick` 1 紅),所以這套改壞法有效。

現有測試只守「開跑時髒」和「`--no-perf` 不完整」兩條路。
- 判讀時才髒、判讀前 HEAD 換了,我手動跑過,修後行為正確。HEAD 換了印「開跑後 HEAD 換了」,判讀時髒印「工作目錄有沒提交的改動」,兩者都寫 0 份紀錄。只是沒有測試守著。
- 同一版 `login.ok` 先有完整 pass,再被建置失敗的 unjudged 蓋掉,也沒有測試。

歸因:M1、M2 的程式碼在修前就有(原有漏查)。M3 屬於修補新增的「不蓋掉」邏輯,測試只涵蓋一半,兩版對照沒法給出證據,歸因未判定。
引句:「and (not v["complete"] or v["result"] == "unjudged")」

## F4 `--changed` 的分岔點與改名處理,修補後新增的測試沒守住
severity: major
blocking: 是
file: `scripts/lumos:_e2e_changed_files`
失敗場景:兩個改壞(M10、M8)都在 332 個測試全過。修後正常程式在同樣輸入下都對。
- M10:`base = ml or ""`,跳過 merge-base。
  - 場景:主線在分支切出後又前進,別人改了 B.kt,分支只改 A.kt。
  - 修後:`--changed` 回 `['login.ok']`。改壞後回 `['login.ok','other.x']`,把主線上別人的改動算進來。
- M8:拿掉 `--no-renames`。
  - 場景:分支把 login 的 A.kt 搬到 login 的 paths 之外。
  - 修後:挑到 `login.ok`,unmatched 列出新路徑。
  - 改壞後:git 只印新名字,舊路徑不見,回 2「對不到任何功能」。

`t_android_e2e_changed_pick` 的分岔點案例裡主線沒前進,merge-base 剛好等於主線 tip,所以區分不出來。r1 席已指出測試沒守住分岔點,修補後的新測試還是守不住。

歸因:有證據的原有漏查。這兩行修前就在(`scripts/lumos:40810`、`40812`),修補只加了測試,而測試沒覆蓋。
引句:「base = (_nodehome_git(root, "merge-base", ml, head) or b"").decode().strip() if ml else ""」

## F5 `macrobench_cmd` 不是字串、又沒開 macrobench 時,`--check-config` 噴 traceback
severity: minor
blocking: 否
file: `scripts/lumos:_e2e_features_err`
失敗場景:e2e 段只寫 `"macrobench_cmd": 5`。`macrobench --check-config` 的 `_e2e_features_err` 對 int 做 `"{{TEST}}" in cmd`,噴 `TypeError` 並回 1,不是規格 S26 要的 2。`macrobench` 為 true 時會被先擋下,沒開時沒有。同一支檢查也在 judge 讀 HEAD 設定時呼叫(`_e2e_judge_target`),一樣會 traceback。
- 修前:同一個 TypeError。
- 修後:同一個 TypeError。

歸因:有證據的原有漏查。
引句:「return "macrobench_cmd 帶 {{TEST}} 時要有 features 列出效能測試方法" if "{{TEST}}" in cmd else None」

## F6 重判較舊的 run,會把較新的 fail 蓋回舊的 pass
severity: minor
blocking: 否
file: `scripts/lumos:_e2e_feature_record` 的 `_put`。蓋掉保護只看 complete 與 unjudged,不比 `ended`。
失敗場景:`--case login.ok` 先跑 run-A(pass),再跑 run-B(fail),`feature_runs` 變成 fail。接著手動 `judge run-A --no-record`(範本腳本 judge 逾時時訊息建議的做法)。`feature_runs["login.ok"]` 變回 `pass / run-A`,比較新的 run-B 失敗被蓋掉。
- 修前:同樣輸出。
- 修後:同樣輸出。
整套 `runs` 也是「最近一次 judge」的設計,所以屬於原有設計,不是修補造成。

歸因:有證據的原有漏查。
引句:「fr[fc] = dict(v, run_id=steps.get("run_id"), ended=ended, commit=head)」

## F7 history 按情境篩選時,別的情境的失敗會算在被篩的情境頭上
severity: minor
blocking: 否
file: `scripts/lumos:_e2e_history_cmd`、`_e2e_history_append`。總表的 `items` 是整次跑的平鋪清單,沒帶情境。
失敗場景:`--case login.ok,other.x` 跑,other.x 沒過。`history --case login.ok` 印出「沒過 login.ok、other.x 沒過或沒判完:ui .maestro/other.yaml」,看起來像 login.ok 沒過。
- 修前:同樣輸出。
- 修後:同樣輸出。
規格〈檢測紀錄〉寫的是「每個情境每一項的結果(含這次沒跑)」,實作沒有。

另外 M14(`startswith(feature + ".")` 改成 `startswith(feature)`)在 332 過 0 紅下存活。`history --feature log` 會誤列 `login.*`,測試沒有前綴碰撞的案例。

歸因:有證據的原有漏查。
引句:「if feature and not any(str(c).startswith(feature + ".") for c in cs):」

## 三問
1. **原問題的修復效果有何行為證據?**
   - 已驗修復(修前與修後各跑同一案例):
     - 乾淨樹按情境寫 `feature_runs`、整套不蓋掉(`t_android_e2e_by_feature`)。
     - 開跑時髒不寫:修後 0 份紀錄,有訊息。
     - 判讀時 HEAD 換了不寫、判讀時變髒不寫:修後都是 0 份紀錄,印出原因。
     - `--no-perf` 標 `complete:false`、`--changed` 的新目錄逐檔、`$`/空白名稱等已有的測試。
   - 未達成或有疑義:F1(空項目情境的整體回傳碼)、F2(`$`)。
   - 沒有測試守住的行為(F3、F4)我在修後版本上逐一實測,正常程式都正確,只是改壞抓不到。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - 成立:
     - 整套 judge 的「拒寫髒樹、HEAD 換了回 2」優先序(錯誤優先序 err > serr > cerr > ferr)與重構前一致,既有測試全綠。
     - `judge` 沒帶 `--no-record` 又讀到 `selection` 時回 2。
     - 新舊互讀:無 `feature_runs` 的舊紀錄可正常讀;舊 steps.json(沒 `name`)被新判讀處理;沒有 `features` 的舊設定照舊合格。
     - 錯誤路徑上寫總表用的是 fd 版 `_local_ledger_append` 與 `_ledger_tail_needs_newline`,有 finally 關檔。
   - 不成立:F1、F2。
3. **新發現同一案例修前修後各是什麼?** 已隨各條列出。F1、F2 是修後才出現的回歸。F3、F4 修前沒有保護、修後新增的測試也沒補上。F5、F6、F7 兩版輸出相同。

未驗範圍:
- 真機與真實 Gradle 的 Macrobenchmark 實際輸出路徑(只用假工具)。
- 收集腳本在真裝置上以 `<run-id>.<情境>` 為 run-id 的行為(只測假收集腳本與設定讀取)。
- 多進程併發寫同一份紀錄(範圍外)。
- F3 的改壞法只在修後版本驗證,修前版本沒有對應測試,故沒做修前對照。

## pitfalls manifest
- 內建題:「scripts/lumos 寫總表那段的 open(」判為誤報。
  - 這份差異新增的行裡沒有 `open(`。
  - 總表寫入走 `_local_ledger_append`,用 `os.open` 加 `finally: os.close`。
  - 補換行的 `_ledger_tail_needs_newline` 同樣有 `finally` 關檔。
- 併發類題目(鎖、交易)在這個 repo 判範圍外,一律標誤報。

## 圖譜鏡頭與角色卡
- 這次沒有附固定席節點,不逐條答。
- 規格 S22–S28 與實作對照,衝突只有 F1(S22 的回傳碼、S25 的總表)。S27 的 `feature_runs` 行為正確。
- `be-api-compat`:
  - 這是本機 CLI 與 JSON 檔,沒有 HTTP 介面。
  - 新增的 `steps.json` 欄位(`selection`、`dirty`、step 的 `name`)和 `feature_runs` 都被新舊判讀容忍。
  - 新版範本腳本對舊版 lumos 會被未知參數擋成 rc 2,不會把部分結果當整套寫入。
- `be-authz`:沒有新增或改動需要授權的端點,不適用。

這次改動有 4 條會做出錯行為或測試抓不住的問題(F1 到 F4),另有 3 條較輕的問題。
