severity: clean

我讀了修補差異和完整快照 patch,在複本上跑了測試和還原翻紅檢查。沒有找到可標為 finding 的洞。以下是已驗主張和未驗範圍。

## Findings

零 finding。

## 已驗主張(同一案例證據)

**C1(修復):`_e2e_print_runs` 的每個外來文字出口都過 `_out_clean`**
- claim:第四輪漏掉的工具問題、截圖與記憶體畫面名、提醒行,現在經同一個 `say()` 清掉控制字元。
- input:`problems=["build 回 1:\x1b[31mBOOM"]`、`notices=["提醒\x1b[0m"]`、visual 項目 `s\x1b[31m`、UI flow `a\x1b[31mb.yaml` 加現場路徑含 ESC。
- expected:輸出不含 `\x1b`,各行文字仍在。
- case_source:`t_android_e2e_judge_evidence`,本席另做還原翻紅。
- before:修前(e98debe1)這幾行直接 `print`。我只讀了修前程式,沒有在修前版本實跑。
- after:修後測試 `-k android_e2e_judge_evidence` 通過 6 項。把 `say(f"  ? {p}")`、`say(f"  ! {n}")`、截圖與記憶體迴圈那行各自改回 `print`,測試各自翻紅(5 過 1 敗)。
- attribution:有證據的修復有效。我沒另外還原 UI 行那一句。
- 未涵蓋:字串分支(`未設定`、`沒跑成` 等)和效能行的值都是固定字串,不是外來文字,改回 `print` 測試不會紅,也沒有實際危害。

**C2(修復):`--last` 方向與數法**
- claim:A、B、C(C 第二次才過)`--last 2` 會列 C;D、E、E(E 重判)`--last 2` 說最近 2 次執行沒有。
- case_source:`t_android_e2e_flaky_history`,修補 hunk 新增的兩條斷言。
- after:`-k android_e2e_flaky` 29 項通過。
- 推演:改成丟最新,A、B 都是 pass,不會有 flaky,第一條紅。改成數行數,E、E 只剩 1 次執行,訊息變「最近 1 次」,第二條紅。
- before:修前沒有這兩條斷言,是缺測試。這條只靠推演,沒有實跑修前版本。

**C3(正常路徑仍成立):外來文字出口**
- claim:judge 印給人看的結果裡,從 steps.json 或總表讀出的外來文字都已過 `_out_clean`。
- 查證:`_e2e_judge_partial` 的 `情境 …`、`(按功能跑:…)` 兩行仍用 `print`,但內容只有 feature、case 名、flow 與畫面名,全來自 config。
- 實跑:config 驗證擋掉控制字元。我把 flow 名稱改成 `.maestro/lo\x1b[31mgin.yaml` 實跑,得到 `擋下:macrobench.json 的 e2e 段:flows 的一項 不能有控制字元…`,走不到那兩行的印出,所以不標 finding。

**C4(只提醒的保證)**
- `_e2e_flaky_notify` 在 `_local_ledger_append` 成功後才呼叫,沒有回傳值。
- 讀不到總表只捕 `OSError`。`_canary_ledger_rows` 只丟 dict、壞行與超深巢狀都跳過,`errors="replace"`,所以我找不到其他丟例外的輸入。
- 它不碰 `runs`、`feature_runs`、回傳碼。
- `t_android_e2e_flaky_notice` 驗了回傳碼和 `feature_runs`,通過。

**C5(`history --flaky` 歸併)**
- 沒有 `run_id` 的舊行:`_e2e_run_key` 回 `("row", n)`,各算一次。
- `run_id` 轉字串比,數字、字串算同一次。
- `--case` 篩選後空項目的重判行不蓋判定。
- 同一 `run_id` 的行不相鄰時,以第一次出現的位置淘汰。
- 逐行讀,`OrderedDict` 容量封頂在 `--last` 次執行,每 flow 的 `od` 封頂 20 筆,所以十萬行總表的記憶體沒有隨行數成長的風險。
- 時間:`_e2e_flaky_notify` 每次判定整本讀一遍,是 O(n)。我沒有實測十萬行的時間。

**C6(範本腳本)**
- `maestro_has_evidence_flags` 只判斷 `--test-output-dir` 和 `--debug-output`,與 S1 一致。
- `crash_log` 在 `since` 為 None 時回 None,不退回讀整個緩衝。
- 閃退紀錄只在 `rc != 0` 才讀,與 S2 一致。
- `steps.json` 的 `evidence` 先存步驟再補欄位,收閃退紀錄出錯不會丟掉步驟。
- `t_android_e2e_crash_log`(8 項)和 `t_android_e2e_evidence_flags`(8 項)通過。

## 已核對但不標的觀察

1. 整套跑的查證紀錄 `rec["runs"]` 會帶 `fail_evidence` 的絕對路徑。實跑確認會帶,測試也斷言了。同一份紀錄裡既有的 `reports` 本來就是絕對路徑,是既有慣例,不歸這次修補。
2. `history --flaky --last N` 數的是所有執行,擋下而項目為空的另一個 `run_id` 也佔名額。S6 沒禁止這樣算,我給不出具體失敗場景,不標。
3. 篩選後 0 筆時印「最近 0 次執行的紀錄裡沒有…」,是措辭問題,不標。

## 圖譜鏡頭

固定席節點判定:
- **guard-kill、lumos-cli-read、design-loop、測試假綠形態、lumos-cli-lifecycle**:這份 diff 沒碰 guard kill 的 rc 優先序、`--json` 純度、search 濾網、設計審處置閘、re-inject sentinel。不影響。
- **loop-convergence-recording、pitfalls-code-loop、reversibility-governance-ledger**:牽連檔 `scripts/lumos` 但沒碰它們的函式。不影響。
- 沒有「帶殘留」徽章,也沒有「這次新增的殘留」段。
- 其餘「超出上限只列名」的節點未逐篇展開,未判定。

## 修補三問

1. **原問題的修復效果**:有行為證據,見 C1、C2。
2. **修補處的正常、錯誤、相鄰路徑**:正常與錯誤路徑成立,見 C3 到 C6。
3. **新發現的修前、修後結果**:沒有新發現。

## 未驗範圍
- `--flatten-debug-output` 在舊 Maestro 是否存在。腳本只問另外兩個旗標,我沒有真 Maestro 可驗,未判定。
- 同一個 run-id 在 run 目錄被手動刪除後重用,會被歸成同一次執行而低估次數。這是規格明訂的「run_id 相同算同一次」,不屬於缺陷。
- 十萬行總表的實測時間與記憶體沒量。
- 我沒有在修前版本 e98debe1 跑任何指令。before 欄一律是讀修補差異推演,沒有實跑對照。

清理:我已刪掉自己還原翻紅留下的三個 gctl 暫存目錄,原 repo 沒動。複本和實驗腳本留在 `/tmp/lumos-seat-work/code-E2E紅燈現場與不穩帳/單審-sonnet/`。

總結:整份最高嚴重度為 clean
