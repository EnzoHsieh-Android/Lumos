severity: major

我拿假輸入實跑了被審的 `scripts/lumos`(分支 HEAD 1e47929e)。收集腳本的函式是從 patch 內嵌的 python 抽出來,用假的 `adb`、`trace_processor` 輸出跑的,沒碰裝置。所有實驗都在 `/tmp/lumos-seat-work/code-android-mem-stability/邊界-sonnet/`,結束後暫存的 `w/` 已刪。

官方分級區間的每個邊界我都跑過,都對:
- 3199 跳過,3200 進第一級,4800 進第二級,18431 判得出,18432 跳過。
- 剛好等於上限判過,多 1 KB 判不過。
- category 填 `tv` 會跳過。

數字欄位的各種壞值也都被擋下:0、負數、布林、字串、空清單、NaN、10^400 的超大整數都回 2。`results_dirs` 缺、只有 stability 段、沒有設定檔但給 `--stability`,都照計劃判。

## 條目一:java_growth 在快照解析不出任何類別時判為通過
severity: major
blocking: 是
引句:「        return None, f"trace_processor 算不了快照:{err.strip()[-200:] or rc}"」
`heap_counts` 只在 trace_processor 回傳碼非 0 時才算失敗。

- 輸入:trace_processor 回傳碼 0 但沒有資料列。例如套件名跟快照裡的行程名對不上,`WHERE p.name = '__PROCESS__'` 就一列都選不到。
- 預期:列成「沒判」。
- 實際:我餵空輸出,`heap_counts` 回 `({}, None)`,收集腳本寫出 `heap.status=ok, before={}, after={}`。
- 判定端我實跑 `java_growth`:`threshold_passed` 裡有它,`grown: []`,明明什麼都沒量到卻判通過。
- 同一段迴圈對 `cells[-1].isdigit()` 不成立的列(例如 `3.0`、空值)也是靜默丟掉。
- `instances` 還有「兩份快照都沒有」的防線,`java_growth` 沒有,所以漏的是增長檢查。

## 條目二:App 崩潰後沒被拉起來時,exits 被判成「沒判」而不是「沒達」
severity: major
blocking: 是
引句:「    res["pids"] = src({"values": pids}, None if all(pids) else "有一次讀不到 pid(App 不在了)")」
`pids` 只要有一個 None,整個 pids 來源就標成 failed。`_ms_exits` 又硬性要求 pids 是 ok 才往下判。

- 輸入:N 輪中途 App 崩潰,而且沒被拉起來。`exits.new` 有一筆 `crash`,收集腳本最後的 `pidof` 是 None。
- 預期:`exits` 判不過(有 `crash` 紀錄)。
- 實際:我實跑得到 `threshold_skipped: reason "pids 沒收到(failed):App 不在了"`。崩潰紀錄在手,卻沒有被判。
- 崩潰且沒重啟正是 exits 最該抓的情境。

## 條目三:宣告了 max_block_ms 但阻塞量不到時,frozen 靜默判通過
severity: major
blocking: 是
引句:「    over = "max_block_ms" in t and block is not None and block > t["max_block_ms"]」
`block` 是 -1(量不到)時會變成 `None`,`over` 就是 False。

- 輸入:門檻寫了 `max_block_ms: 100`,結果檔 `max_main_block_ms: -1`、`frames: 10`、`frozen_frames: 0`。
- 預期:人裁的阻塞上限沒量到,應列成「沒判」。
- 實際:`threshold_passed`,記錄裡 `max_main_block_ms: null`。
- 文字輸出印成「主執行緒最長阻塞 None ms」。
- 對照:`native_unreachable`、`peak_vitals` 遇到量不到都會跳過,只有這條放行。

## 條目四:category 填清單或物件時 lumos 噴 traceback,不是回 2
severity: minor
blocking: 否
引句:「    if st.get("category", "app") not in MACROBENCH_VITALS_FG:」
- 輸入:`stability.category` 寫 `[]` 或 `{}`。
- 預期:`擋下:… category 只能是 app 或 game`,回 2。
- 實際:`--check-config` 回 1,噴 `TypeError: cannot use 'list' as a dict key`。
- 收集腳本的 `load_config` 把整串 traceback 當錯誤訊息印出來。
- 計劃要求設定驗不過回 2,這裡回 1。
- 同一個函式裡 `None`、`"x"` 都正常回 2,只有不可雜湊的值漏掉。

## 條目五:門檻條目寫錯欄位名會靜默用最嚴的預設
severity: minor
blocking: 否
引句:「    for name, (required, kind, desc) in fields.items():」
驗證只逐一檢查「已知欄位」,多餘的欄位不報。

- 輸入:`{"check":"native_unreachable","max_byte":999}`(少了 s)。
- 預期:報未知欄位。
- 實際:`--check-config` 回 0。判定時 `max_bytes` 取預設 0,任何增量都判不過。
- `java_growth` 的 `min_pre_cycle`、`frozen` 的 `max_block` 同理,寫錯了就是用預設值。

## 條目六:手改過的結果檔欄位型別不對時,判定函式噴 traceback
severity: minor
blocking: 否
引句:「    new = [e for e in s.get("new", []) if isinstance(e, dict)]」
- 輸入:`exits.new` 為 `null`,或 `pids.values` 為 `[[1],[2]]`。
- 預期:列成「沒判」,或回 2 並印擋下。
- 實際:兩種都噴 `TypeError`,回 1。
- 收集腳本不會寫出這種結果檔,所以只有手改或外來結果檔才觸發。

## 條目七:run-id 可以是 `..` 或 `.`,max_record_s 沒有上限也沒有下限換算
severity: minor
blocking: 否
引句:「    if not re.fullmatch(r"[A-Za-z0-9._-]+", run_id):」
- run-id:`..` 和 `.` 都符合這條規則。`..` 會讓 `run_dir` 變成 `.lumos/artifacts`,`stability.json` 寫到上一層。`.` 會寫進 `android/` 本身。
- max_record_s:`1e300` 能通過驗證,換成毫秒後是超大數字,perfetto 開不起來,`cycle_trace` 變成 failed。`0.0004` 通過驗證,換成毫秒變成 `duration_ms: 0`。
- 預期:驗證擋掉,或收集腳本把它們夾進合理範圍。

## 條目八:有 mapping 時,宣告類別沒有實例的情況會被誤判成「類別名拼錯」
severity: minor
blocking: 否
引句:「            name = mapping.get(base, base) + arr」
`java.lang.Class<a.b>` 這種類別物件名,只套用整個字串的 mapping 查詢,不會把角括號裡的混淆名還原。

- 輸入:release 版有 mapping,門檻 `instances` 宣告 `com.Real`,快照裡只剩 `java.lang.Class<a.b>`(實例全釋放)。
- 預期:判通過,數量 0。
- 實際:`declared_classes` 存的是 `java.lang.Class<com.Real>`,對不上,判定落到「兩份快照都沒有…類別名拼錯或被混淆?」並跳過。
- 結果偏保守,不會誤報通過。

## 逐項確認後沒有問題的地方
- `unreachable` 的正規式吃得下 `allocation` 與 `allocations`,`0 bytes in 0 unreachable allocations` 解析成 0。
- 逗號類別名 `java.util.Map<K,V>`、陣列 `x[][]` 加 mapping、`[NULL]` 類別名都能正確累加。
- `parse_exit_info`:`description` 含 `state=` 時只截到 `state=` 前,reason 不是數字時 `classify` 回 `other`,套件名前綴不同(`a.bc` 對 `a.b`)不會誤收。
- `results_dirs: []` 搭配 stability 段仍回 2。計劃寫的是「可以不填」,實作是「不寫這個鍵才行」,語意有落差,但跟原本要求非空的行為一致,我沒列成 finding。

最嚴重 severity: major,blocking 共 3 條。
