severity: major

審查範圍:/Users/enzo/orca/workspaces/lumos-toolchain/e2e-gate,HEAD 即 ce46398a。我用 test_lumos 的 `_e2eg_*` 夾具在臨時 repo 實跑邊界輸入,探針與暫存放在 `/tmp/lumos-seat-work/code-e2e-gate/邊界-sonnet/`,由編排者收貨後刪。沒讀 r1-* 檔。

## Findings

**1. 開場掛鉤、doctor、`waive --list`、`--ack` 讀紀錄的規則不一致,深層巢狀的紀錄會讓 lumos 崩潰或兩邊說法不同**
severity: major
blocking: 是
引句:「rec, err = _e2e_load_json(path, scrub=False) if path is not None else (None, "太大")」
file: `scripts/lumos:41796`(`_e2e_ai_pending_all`)、`scripts/lumos:40777`(`_e2e_load_json`)、`scripts/hooks/claude/lumos-entry-hook.py` 的 `_e2e_ai_line`

- 失敗場景 A,崩潰:`.lumos/e2e-records/<64 碼>.json` 內容是 20 萬個 `[`,大小遠低於 2MB。`_e2e_load_json` 只接 `(OSError, TypeError, ValueError)`,`RecursionError` 沒接住,也沒先過 `_events_depth_ok` 的深度檢查。
  - `_e2e_ai_pending_all`、`_e2e_records_all`、`_e2e_waive_list` 全部崩潰。
  - 真跑 `lumos android-e2e waive --list` 和 `waive --ack --all` 都印出 `RecursionError: Stack overflow` 的 traceback。
  - doctor 的 AE 段呼叫同一支 `_e2e_ai_pending_all`,同樣會崩。我沒真跑 doctor,因為臨時 repo 缺知識圖譜,doctor 一開始就停。
  - 開場掛鉤的複本有接 `RecursionError`,只跳過那一份。
  - 修補後的說明寫「一份讀不懂只跳過那一份」,與實作不符。
- 失敗場景 B,兩邊算出不同數字:一份合格紀錄帶一個 30 層的額外欄位,另有一筆未看過的 AI 放行。
  - lumos 端 `_e2e_load_json` 因「巢狀太深」回錯誤,算 0 筆。
  - 掛鉤沒有深度檢查,算 1 筆,並叫人跑 `waive --ack --all`。
  - 那條指令找不到可標的紀錄,通知清不掉。
  - 實測:`lumos side pending: []`,`hook line: 有 1 筆…`。
- 重現:`/tmp/lumos-seat-work/code-e2e-gate/邊界-sonnet/s/probe5.py`(兩種場景都在裡面)。
- 測試為何照綠:`t_android_e2e_ai_count_copies_agree` 的樣本有衝突標記、`[]`、指紋對不上、太大、`/dev/zero` 捷徑,但沒有巢狀太深或遞迴爆掉的樣本。
- 歸因:有證據的原有漏查。修前 `_e2e_records_all` 走同一支 `_e2e_load_json`,同案同樣崩潰、同樣兩邊不一致。修補新增 `_e2e_record_files` 與複本,卻沒補這一角,所以這是沒修到,不是修補造成的回歸。
- 兩版查證:
  - 修前(0aecbf90)`_e2e_load_json` 的 except 清單相同。
  - 修後(ce46398a)同上。
  - 我只在修後跑過 probe5,修前以讀碼確認。

**2. 紀錄份數上限(500)與「最新的優先」沒有測試守住,超過上限時也不提示被截掉**
severity: major
blocking: 是
引句:「return [(fp, path) for _m, fp, path in rows[:E2E_RECORD_SCAN_MAX]]」
file: `scripts/lumos:41758`(`_e2e_record_files`)

- 失敗場景:有人把 `[:E2E_RECORD_SCAN_MAX]` 拿掉,或把排序改成舊的在前,測試全綠。
- 當場翻紅嘗試(沒翻紅):我在 `/tmp/lumos-seat-work/code-e2e-gate/邊界-sonnet/mut/` 的複本做這兩處改壞,跑 `-k android_e2e_ai_count_copies_agree`、`-k android_e2e_ai`、`-k android_e2e_waive`,結果 5、15、14 支全綠。
- 原因:`copies_agree` 只放 7 份紀錄、只比常數相等,沒有 501 份以上的情境。
- 實作面的洞:新 clone 時所有檔的修改時間幾乎相同,排序退化成「時間倒序、指紋正序」,超過 500 份時哪些被丟掉不透明。
  - 被丟掉的紀錄裡若有 AI 放行,doctor、掛鉤、`--ack` 都不會提。
  - 輸出沒有「另有 N 份沒讀」的一行。
  - 這道通知是補償 AI 放行便宜的唯一機制。
- 歸因:有證據的修復回歸。lumos 端的 500 上限是這輪才加的,修前掛鉤是按檔名排序取前 500,兩邊都沒測試。
- 兩版查證:
  - 修前 `_e2e_records_all` 沒有上限。
  - 修後有上限,但上面的改壞測試不紅。

**3. `app_dirs` 重疊時永遠誤擋,訊息還說「不存在」**
severity: minor
blocking: 否
引句:「gone = [d for d in dirs[0] if d not in seen_app]」
file: `scripts/lumos:40632`(`_e2e_fingerprint`)

- 失敗場景:`app_dirs: ["app", "app/src/main"]`(父在前、子在後)。每支檔只被第一個包住它的項目認走,`app/src/main` 永遠進不了 `seen_app`。
- 結果:被推送那端算指紋回 `app_dirs 的 app/src/main 在 db76f8ef 的檔案樹裡不存在`,每次推送都擋。
  - 對照:反過來寫 `["app/src/main", "app"]` 就正常。
  - `macrobench --check-config` 卻回 0「合格」。
  - judge 與 waive 要先算指紋,也都過不了,這個專案只剩環境變數出口。
- 重現:`/tmp/lumos-seat-work/code-e2e-gate/邊界-sonnet/s/probe4.py`。
- 歸因:有證據的原有漏查。`seen_app` 那段不在修補差異裡,修前同樣。
- 兩版查證:修前(讀碼)`gone` 的算法相同;修後(實跑)結果如上。

**4. `waive --commit` 沒驗格式與長度,沒給時存成 `null`,與文件寫的「沒給就是 HEAD」不符**
severity: minor
blocking: 否
引句:「"commit": commit or head}」
file: `scripts/lumos:41880`(`_e2e_waive_cmd`)

- 失敗場景 A,長度:`--commit` 給 20 萬個字元,整串寫進紀錄(`commit` 欄 200000 字元)和治理帳(帳檔變 200293 位元組)。`--note` 也只有下限沒有上限。
- 失敗場景 B,預設值:帶了完整指紋、沒帶 `--commit` 時,`_e2e_waive_target` 回的 `head` 是 `None`,於是 `commit` 存成 `null`。我實跑了第二、三次放行,最後一筆 `commit` 是 `None`。
  - 計劃與 README 這輪新寫的欄位說明是「沒給就是 HEAD」,只有不帶指紋時才成立。
- 重現:`/tmp/lumos-seat-work/code-e2e-gate/邊界-sonnet/s/probe3.py`。
- 歸因:有證據的修復回歸。`commit` 欄是這輪新增,修前沒有這個欄位。
- 兩版查證:修前沒有欄位;修後如上。

## 逐項邊界走查(實跑結果)

這些都符合「判不清就擋」或正確放行,沒有新發現:

- 只刪檔:被擋,要 `login.ok`。
- 改名:拆成刪加,加的那端對不到功能,要整套。
- 中文與空白檔名:要整套,原因寫「對不到任何功能」。
- 一支檔同屬兩個功能:兩端設定相同時要 `login.ok` 和 `other.x`。
- `shared_paths` 與功能重疊:`shared_paths` 贏,要整套。
- 只改單元測試目錄:不要求。
- 只改設定:`weaken` 與整段刪 e2e 都被擋。修前 `if fp == fp_base:` 會放過,這條修補有效。
- 完全沒改動:不要求。
- 推的是主線本身:
  - 沒有 remote 時走「新 repo」,不要求。
  - 有 origin/main 時要求紀錄。
- detached HEAD、tag、`--at-sha` 縮寫:判定正常。`--at-sha` 不存在回 2。
- `LUMOS_TTY_TIMEOUT` 為 `-1`、`nan`、`inf`、`abc`:用預設 30 秒。寫 `0` 時 select 立刻回,視同沒人答,記成 AI 放行,與修前一致。
- 記錄目錄是捷徑、檔是捷徑或 FIFO:`lstat` 後跳過。
- 單份超過 2MB:在 `_e2e_records_all` 變成「讀不懂」,在 `_e2e_ai_pending_all` 被跳過。

## 圖譜鏡頭與 pitfalls

- 固定席節點:這次派工附的是「鏡頭計算超時、沒附固定席節點」,我也沒補算。「這次新增的殘留」逐條必答這項無法回答,標為 ⚠ 未判定。
- pitfalls manifest:lint 類是舊告警不判,併發類(例如 TOCTOU 把 FIFO 換進去)判範圍外,沒有新增項。

## 三問

1. **原問題修復的行為證據**:
   - 「只改設定放行」已修:我實跑 `weaken` 和 `drop e2e`,都是 `blocked`。
   - 兩個出口:有測試,我沒另外實跑。
   - `LUMOS_TTY_TIMEOUT`:`_confirm_tty_timeout` 實測成立。
   - `/dev/zero` 捷徑:`lstat` 跳過實測成立。
   - 「讀不懂只跳過那一份」只修了一半,見 Finding 1。
2. **修補處的正常、錯誤與相鄰路徑是否仍成立**:
   - 推送判定路徑成立,極端輸入都走到擋下或正確放行。
   - 記錄讀取路徑不成立:lumos 端與掛鉤的複本在深度與遞迴上不同規則(Finding 1);上限與排序沒測試(Finding 2)。
3. **同一案例修前與修後**:
   - 20 萬層巢狀紀錄:修前 `_e2e_records_all` 崩潰,修後 `_e2e_ai_pending_all` 仍崩潰;掛鉤修前就能跳過。
   - 30 層巢狀紀錄:修前與修後都是 lumos 算 0、掛鉤算 1。
   - `app_dirs` 重疊:修前與修後都誤擋。
   - 沒給 `--commit`:修前沒有欄位,修後存成 `null`。

最高等級:major;擋實作的 2 條(Finding 1、2),另有 2 條 minor 不擋。

主要檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/e2e-gate/scripts/lumos`
- `/Users/enzo/orca/workspaces/lumos-toolchain/e2e-gate/scripts/hooks/claude/lumos-entry-hook.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/e2e-gate/scripts/test_lumos.py`
