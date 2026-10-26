severity: major

## F1 --changed 遇到整個目錄都是新檔時,對不到功能還被說成沒有對應功能
severity: major
blocking: 是
file: `scripts/lumos:_e2e_changed_features`,資料來自 `_e2e_changed_files`。
失敗場景:新增一個還沒追蹤的模組目錄 `feature-cart2/src/main/N.kt`,同時改了 `app/B.kt`。設定是 `app_dirs: [app, feature-cart2]`,功能 cart 的 `paths` 寫 `["feature-cart2/src/main"]`。
- `_dirty_non_bookkeeping(..., untracked=True)` 用 `--untracked-files=normal`,整個沒追蹤的目錄會被收成一筆 `feature-cart2/`。
- `_e2e_under("feature-cart2/", "feature-cart2/src/main")` 判不成立,所以 cart 沒被挑到。
- 這筆被放進 `unmatched`,judge 印出「這些改到的檔沒有對應功能」,但實際上對照表有對應。
我在臨時 clone 實跑的結果:`_e2e_changed_features` 回 `({'app'}, ['feature-cart2/'], '', None)`,cart 被靜默漏跑。
最小重現:git init 後提交 `app/B.kt`,再建立沒追蹤的 `feature-cart2/src/main/N.kt`,呼叫 `_e2e_changed_files`,得到 `['feature-cart2/']`。
修法:用 `--untracked-files=all` 展開成檔案,或在比對時把以 `/` 結尾的項目當成目錄,和 `paths` 雙向比對。
引句:「+        elif any(_e2e_under(f, _e2e_norm(d)) for d in e2e["app_dirs"]):」

## F2 stability_scenarios 的 warmup、cycles 沒有上限
severity: minor
blocking: 否
file: `scripts/lumos:_e2e_scenarios_err`;對照 `scripts/lumos:39468`,`stability` 段有 `MACROBENCH_MAX_CYCLES=10000` 的上限。
失敗場景:`stability_scenarios.x.cycles = 1000000000` 時,`_e2e_scenarios_err` 只擋 `<1`,`--check-config` 照過。
- 收集腳本把它併進 `st`,驅動會一路跑到 `LUMOS_STABILITY_LONG_TIMEOUT`(1800 秒)。
- 最後 `scripts/lumos:39975` 才把結果判成不合格。
- 我實跑 `_e2e_scenarios_err({"x":{"scenario":"s","driver":"d","cycles":10**9}})`,回的是 None。
- 判讀沒有判錯,所以降為 minor。這是 `stability` 段原本就用上限擋掉的那一類問題,新增的這條路徑漏了。
引句:「+        if any(k in v and (not isinstance(v[k], int) or isinstance(v[k], bool) or v[k] < 1) for k in ("warmup", "cycles")):」

## F3 效能測試方法名到跑到一半才驗,regex 對 # 與 $ 的處理也不貼實際用法
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh:accept`;設定端 `scripts/lumos:_e2e_case_err` 只查非空字串。
失敗場景有三個:
- `macrobench: ["Outer$Inner#test"]` 能過 `--check-config`。但建置、安裝、UI、記憶體都跑完後,才在 `die(...)` 擋下,回 2。這時沒有 judge,也沒有 history 那一行,和 S25「每一次都記」不符,steps.json 也沒有 ended。
- `$` 是 Kotlin 巢狀類別的合法寫法,卻被擋。
- 反過來,`#foo` 通過 regex。若 `macrobench_cmd` 是 `sh run-bench.sh {{TEST}}`,sh 會把 `#foo` 當註解,等於不帶參數,可能整批效能測試都被跑。
建議:設定檢查階段就用同一條 regex 驗,並擋開頭是 `#` 的名稱。
引句:「+            if t is not None and not re.fullmatch(r"[A-Za-z0-9_.#]+", t):」

## F4 沒有挑法時 --no-perf、--no-memory 被靜默忽略
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh`,解析處與 `SELECTIVE`。
失敗場景:`sh android-e2e-run.sh --no-memory` 沒給 `--changed`、`--feature`、`--case`。`FLAGS` 只有 `select()` 會用,而整套跑不呼叫 `select()`,所以記憶體照跑,也寫正式查證紀錄。使用者以為略過了,實際上沒有。
建議:沒有挑法卻帶這兩個旗標時,直接擋下或明確提示。
引句:「+SELECTIVE = bool(PICK["--feature"] or PICK["--case"] or "--changed" in FLAGS)」

## F5 history --last 0 或負數會列出全部或亂切
severity: minor
blocking: 否
file: `scripts/lumos:_e2e_history_cmd`。
失敗場景:`--last 0` 時 `rows[-0:]` 等於 `rows[0:]`,列出全部。`--last -3` 會變成略過前三筆。
引句:「+    for r in rows[-last:]:」

## F6 同一支 flow 在不同情境用不同寫法會跑兩次
severity: minor
blocking: 否
file: `scripts/lumos:_e2e_select`。
失敗場景:`./.maestro/a.yaml` 與 `.maestro/a.yaml` 能通過設定檢查,因為檢查用 `_e2e_norm` 比對。但去重用的是原字串,所以兩個寫法都留下,同一支 flow 被跑兩次,報告檔名也相同。
引句:「+            sel[k] += [x for x in c.get(k, []) if x not in sel[k]]」

## F7 --changed 改到 .maestro 底下的 flow 時挑不到該 flow 所屬的功能
severity: minor
blocking: 否
file: `scripts/lumos:_e2e_changed_features`。
失敗場景:只改 `.maestro/player_open.yaml`(它在 `e2e.flows` 與某情境的 flows 裡),既不在任何 `paths`,也不在 `app_dirs`。
- 單獨改它時,回「對不到任何功能」。
- 若同時改到別的功能的程式,它既不會被挑去驗,也不會列進 `unmatched`,被靜默略過。
- 規格 S23 沒寫這種情形,所以只標 minor,是設計缺口。
引句:「+        elif any(_e2e_under(f, _e2e_norm(d)) for d in e2e["app_dirs"]):」

## 已確認沒問題的輸入
- `--feature=`、`--feature ""`:`SELECTIVE` 為真,select 回「沒挑到任何情境」,不會退成整套跑。
- `--case login`、`--case a.b.c`:`partition` 後找不到,錯誤訊息講得清楚。
- 重複、帶空白、結尾逗號:`strip` 與 `split` 都處理了。
- run-id 位置對調:旗標先被抽掉,所以不影響。
- 記憶體情境名:名字限 `[A-Za-z0-9_-]+`,拼進 `sid` 與路徑不會跳出產物目錄。
- `paths` 含 `..` 或絕對路徑:設定檢查擋下。
- 檔名有空白或中文:`status --porcelain -z` 不會被引號包起來。
- 刪除與改名:`--no-renames` 加 `-z` 處理得了。
- 測試方法名的 shell 注入:regex 擋得住 `$ ; | & 反引號 空白 引號`。

## manifest 判定
內建題只有一條 `open(` 的 handle 題,只對上 `scripts/lumos` 裡 `_e2e_history_append` 的 `with open(p, "a", ...) as fh`。它在 with 區塊裡,離開時會關,判為誤報。diff 裡其他 `open(` 都是舊行。

## 圖譜鏡頭
- 固定席節點都沒有被這次改動的行為牽動:`lumos-cli-read`(search 預設排除 superseded)、`guard-kill`(rc 優先序、JSON 純度)、`lumos-cli-lifecycle`(re-inject)、`測試假綠形態`。
- `bound-tests-gate` 的合約只管 code-loop check 逐支真跑綁定測試,與此無關。
- 風險類節點 `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`:diff 沒動這些路徑。
- 未列出的節點(超出上限只列名)我沒逐篇讀,無法逐條判。
- 該更新的地方:規格〈按功能與使用情境跑〉和條款 S25 寫「被中斷也記一行」。F3 的「die 中途退出就沒有紀錄」與 S25 的落差,值得在計劃筆記或 Issue 裡記一筆。
- 我沒有查證圖譜裡「功能對照表」另有節點寫了與程式不合的說法。

這份 diff 有一個會讓 --changed 靜默漏掉整個新模組的 major(F1),其餘為設定上限、名稱驗證時機、旗標與歷史查詢等 minor。
