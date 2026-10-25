severity: major

(依格式退回只改 F1、F2、F3 的引句。F5 的引句同樣跨了多行,我順手也改成單行,內容、判定、歸因都沒動。)

## F1 逾時路徑進入 TERM 寬限後再收到中斷,TERM 免疫的子程序變孤兒
severity: major
blocking: 是

引句:「signal_group(p, signal.SIGTERM)」

- file: `scripts/templates/android-e2e-run.sh:79-88`(`kill_group`)與 `:90-117`(`run` 的 `except subprocess.TimeoutExpired: kill_group(p)`)。
- 失敗場景:flow 跑過 `LUMOS_E2E_LONG_TIMEOUT`,逾時路徑呼叫 `kill_group`,先送 TERM 再 `p.wait(GRACE)`。這條路徑不像中斷路徑,訊號沒先設成忽略。等待期間腳本再收到 TERM,`on_term` 在 `except TimeoutExpired` 區塊裡丟出 `Terminated`。
- 同層的 `except BaseException: kill_group(p)` 接不到在 except 區塊裡丟出的例外。`finally` 把 p 從 `GROUPS` 移掉,主程式收尾的 `for p in GROUPS: kill_group` 就看不到它。p 已收過 TERM 卻沒收到 KILL,不理 TERM 的子程序從此存活。
- 修前只有 KILL 一步,這個窗口幾乎不存在。修補把窗口開成 GRACE(預設 60 秒)。
- 重現:`python3.14 exp1.py <repo>`,檔在 `/tmp/lumos-seat-work/code-android-e2e-batch1/單審-sonnet/exp1.py`。假 maestro 忽略 TERM 並睡 40 秒,`LONG_TIMEOUT=3`、`GRACE=30`,第 5 秒對腳本送 TERM。
- 歸因:有證據的修復回歸。
  - 修前 533a083e:腳本 rc 2,子程序已死。
  - 修後 73f36793:腳本 rc 2,子程序仍活著。
- 修法方向:`kill_group` 開頭先把訊號設成忽略(或改在 `finally` 裡收),或把 p 留在 `GROUPS` 到真正收完。

## F2 TERM 後只看領頭程序,同組不理 TERM 的成員不再被 KILL
severity: minor
blocking: 否

引句:「signal_group(p, signal.SIGKILL)」

- file: `scripts/templates/android-e2e-run.sh:87`。
- 失敗場景:領頭程序收到 TERM 後在寬限內退出,KILL 就不送。同組裡把 TERM 設成忽略的成員(例如 nohup 出來的 helper)不會被清掉。修前整組一律 KILL。
- 這個行為不是 docstring 承諾的,但「整組收掉」的合約變弱了。
- 重現:`exp2.py`,領頭程序加一個忽略 TERM 的同組子程序,送 TERM 給腳本。
- 歸因:有證據的修復回歸。
  - 修前:同組成員已死。
  - 修後:同組成員仍活著。
- 嚴重度降為 minor:需要同組成員刻意忽略 TERM,Maestro 與收集腳本的實際行為我沒驗到(未判定)。

## F3 `say()` 吞掉輸出錯誤後,結束時 stderr 緩衝區 flush 失敗,rc 變 120
severity: minor
blocking: 否

引句:「print(msg, file=sys.stderr, flush=True)」

- file: `scripts/templates/android-e2e-run.sh:36-41`(`say`)。
- 失敗場景:HUP 時 stderr 管線已斷,`print(flush=True)` 丟 EPIPE,`except (OSError, ValueError): pass` 吞掉。資料仍留在 TextIOWrapper 緩衝區,直譯器結束時 flush 失敗,exit code 變 120。檔頭合約寫 rc 只有 0、1、2,中斷路徑也預期回 2。
- 同一個機制讓「judge 判了 pass、紀錄也寫了、只是 stderr 斷了」的跑法回 120。新增的 HUP 測試只驗 `steps.json` 與紀錄,沒驗 rc,所以抓不到。
- 重現:`exp3.py`,flow 睡著時關掉 stderr 讀端再送 HUP。
- 歸因:未判定。
  - 修前 rc 120(`steps.interrupted` 為 False,更糟)。
  - 修後 rc 120,但 `interrupted` 為 True。
  - 修補解決了原問題(steps.json 與 judge),rc 120 是原本就有的缺口,修補沒補完。
- 這裡沒有把失敗當成功,是失敗或通過被誤標成 120,方向偏安全。`say` 的 except 裡可以順手把 `sys.stderr` 換成 devnull。

## F4 `_e2e_load_json` 加了清洗後,讀改寫紀錄時有損改寫既有的 waivers
severity: major
blocking: 是

引句:「    return _macrobench_stab_scrub(raw), None」

- file: `scripts/lumos:40554-40560`(`_e2e_load_json`),被 `scripts/lumos:40673`(`_e2e_record_update` 讀既有紀錄)呼叫。
- 失敗場景:`_e2e_load_json` 同時被用來讀 steps.json、判定輸出,以及要整份寫回的 `.lumos/e2e-records/<指紋>.json`。清洗用 `_esc_clean`,把換行、tab、孤立代理字元換成空格。紀錄裡的 `waivers` 是人寫的持久資料。
- 下一次 judge 到同指紋,waiver 的 reason 被悄悄壓扁後寫回。另外,巢狀超過 20 層的紀錄會被判成讀不懂,這次不寫。
- 這批的程式還沒有寫 waivers 的指令,所以目前只在手動編輯或後續批次出現。紀錄 schema 已承諾保存它。
- 重現:`exp4.py`,第一次 judge 後把 waiver reason 改成 `第一行\n第二行\ttab`,提交後第二次 judge,再讀紀錄。
- 歸因:有證據的修復回歸。
  - 修前:`'第一行\n第二行\ttab'` 原樣保留。
  - 修後:`'第一行 第二行 tab'`。
- 修法方向:紀錄的讀取只做限深,清洗只用在 steps 與判定輸出這類只讀來源。

## F5 `applies=False` 沒有套進 notices 迴圈
severity: minor
blocking: 否

引句:「if r.get("check") and r["check"] not in want:」

- file: `scripts/lumos:40591-40594`。
- 失敗場景:別的情境的 `frozen` 條目被標 `applies=False`,但不在 `want` 裡,仍寫出「記憶體 frozen(沒判到):只提醒」。這是把「不適用」說成「沒判到」。只影響 notices 文字,不影響結果。
- 歸因:未判定,只靜態推導,沒跑。修補只套了 `skipped` 那一處,與之相鄰的這一處沒套。

## 三問回答

**① 原問題的修復效果**

| 主張 | 輸入 | 預期 | case_source | 修前 | 修後 | 結論 |
|---|---|---|---|---|---|---|
| HUP 且 stderr 寫不出去時,steps.json 仍標中斷 | 同 `exp3.py` | `interrupted` 為 True | G2、`exp3.py` | False | True | 已修復 |
| 中斷時子程序收到 TERM 並跑完自己的收尾 | 假 maestro 設了 TERM trap | 收尾標記檔存在 | G1 | 未跑修前版本的新測試(測試檔同在修補提交內,不能直接比) | 修後 `-k android_e2e` 229 條全綠 | 已修復(行為證據只有修後測試,修前缺證據) |
| 別的情境或裝置的 skipped 條目標 `applies=False`,記憶體塊不因此判不完 | G3 的 `t_android_e2e_stab_applies_flag`、`t_android_e2e_judge_perf_memory` | 該 check 判 pass | G3 | 修前沒有這欄(欄位是修補新增) | 修後測試綠 | 已修復(限測試輸入) |

- JUnit 改走 `test_quality.junit()` 後,DTD、案例數對不上的情境測試綠。
- 我沒有真實 Maestro 報告可驗(G6 的平板兩份報告),這部分未判定。

**② 修補處的正常、錯誤與相鄰路徑**

- 正常路徑:修後的 `-k android_e2e` 全綠,229 passed, 0 failed。
- 錯誤路徑:
  - 中斷路徑(訊號已設成忽略)正常,TERM 後等 GRACE 再 KILL。
  - 逾時路徑(F1)、同組成員(F2)、rc(F3)、紀錄讀改寫(F4)不成立。
- 相鄰呼叫路徑:
  - `--stability` 輸出多了 `applies` 欄。既有讀取點 `_macrobench_print_thresholds` 只讀 `check`、`reason`,不受影響。
  - skill 與收據我只做了 grep 層級的比對,沒有逐一核對(未判定)。
  - `applies` 判定式與 `_macrobench_stab_skip_reason` 的前兩個條件一致。

**③ 新發現在修前與修後的結果**

見 F1、F2、F3、F4 的歸因欄。F5 沒跑兩版。

## 圖譜鏡頭(固定席)

- `Systems/pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`、`design-loop`:這份 diff 是 android e2e 與 `--stability` 的內部改動,不碰各節點宣稱的行為,判不影響。
- `lumos-cli-read` 的 search 不排除 stale:不影響。
- `guard-kill`、`lumos-cli-lifecycle`、`bound-tests-gate`:不影響。這份 diff 沒碰 guard kill 的 rc 優先序與 JSON 純度,也沒碰 reinject。新增測試是否被 bound-tests 綁定我沒驗(未判定)。
- 另外:`Systems/android-e2e-acceptance` 那條 `WHY:裝置鎖…相反` 寫的是修補理由,與程式一致,我沒發現矛盾。

## 未驗範圍

- 真機。
- 真實 Maestro 報告的 DTD 與案例數。
- 子程序在 GRACE 內被再次 KILL 的完整時序。
- 寬限到期後 KILL 是否把巢狀子程序全數清掉。

證據與重現檔在 `/tmp/lumos-seat-work/code-android-e2e-batch1/單審-sonnet/`:`exp1.py`、`exp2.py`、`exp3.py`、`exp4.py`、`harness.py`。兩個 clone(`r2`、`r2old`)已刪。

總結:max severity 為 major,blocking 2 條(F1、F4)。
