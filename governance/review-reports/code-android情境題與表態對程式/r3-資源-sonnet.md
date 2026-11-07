severity: major

我在 `4bad5ae19`(範圍終點)上用暫存 HOME 和暫存 repo 實測了四個鏡頭。第二個鏡頭有 major,其餘是 minor 或沒問題。

**F1 提醒記帳:筆數沒有上限、不在時間預算內、重推重複記**
引句:「_gate_event_or_warn(repo_root, "code-loop", "warned", r["text"][:120], hard=False,」
severity: major
blocking: 是
- **筆數與耗時**:每條提醒一筆帳。900 條(約等於 300 支 kt 各 3 列證據不符)耗時 17.05 秒,另一次 17.38 秒,約 19ms 一筆,因為每筆都另開 `git rev-parse` 取 HEAD。100 條要 1.92 秒。
- **不在預算內**:`_kt_sit_reminder_lines` 沒有 deadline,17 秒在 `_DISP_BUDGET = 20.0` 之外,和切段、核對的 20 秒是疊加的。
- **帳檔增長**:`("code-loop","warned")` 不在 `_GOV_LOCAL_PAIRS`,所以寫進版控的 `docs/.governance-log.jsonl`。900 筆 = 520,990 位元組。
- **重推重複記**:同一組提醒再推一次又記 900 筆,實測 900 變 1800 行,沒有去重也沒有每次推送的上限。
- **終端輸出**:最多 7 行、約 2.1KB,輸出沒問題。
- **最小重現**:`_kt_sit_reminder_lines(repo, 900 條 reminders)` 呼叫兩次,量時間和 `wc -l docs/.governance-log.jsonl`。
- **建議**:記帳設上限(例如前 6 筆加一筆總數),或改寫本機帳,並納入 deadline。

**F2 `_home_cache_evict`:成本可接受,沒有誤刪**
引句:「_home_cache_evict(_kt_sit_cache_path(key).parent, _KT_SIT_CACHE_TTL)   # 寫之前清掉過期的」
severity: minor
blocking: 否
- **1 萬份過期檔**:一次寫入前清理 0.78 秒,全數刪除。
- **1 萬份未過期檔**:只掃描不刪,0.105 秒。
- **誤刪**:只動指定子目錄,而且只刪一般檔。同層另一個快取子目錄的過期檔、`kt-situation/sub/` 裡的檔都還在。
- **minor 的原因**:24 小時內每個不同範圍或版本各寫一份,沒有檔數上限。清理只認 mtime,新檔不會被清,所以 TTL 內的檔數不受限。

**F3 `_nodehome_cat_blobs_capped`:單支超過上限的處理正確,整批沒有總量上限**
引句:「blobs = _nodehome_cat_blobs_capped(repo_root, specs, _KT_SIT_READ_MAX, timeout=_disp_git_timeout(), deadline=deadline, sizes=sizes)」
severity: minor
blocking: 否
- **單支 4MB 以內**:讀 1 支(4,194,253 位元組)耗時 0.04 秒,RSS 約 48MB。
- **單支超過 4MB**:大小先查,超過就丟 `_KtSitUnverifiable`,不讀進記憶體,耗時 0.02 秒,正常。這會讓整個推送被擋。
- **整批沒有總量上限**:同時讀 29 支各約 4MB(共 121.6MB)耗時 0.28 秒,RSS 約 556MB。呼叫端沒傳 `max_total_bytes`。照比例推算,300 支這種檔約需數 GB。
- **minor 的原因**:要 300 支各 4MB 且都命中預篩才會發生,情境不常見。

**F4 `-k kt_situation` 整組耗時與暫存**
引句:「`python3.14 scripts/test_lumos.py -k kt_situation`」(跑的指令,出自派工詞)
severity: minor
blocking: 否
- **耗時與結果**:116 個全過,牆鐘 2 分 46 秒(user 75 秒、sys 70 秒)。
- **暫存**:跑完 `/tmp` 底下沒有 `gctl-run-*` 殘留。
- **真實家目錄快取**:`~/.cache/lumos/kt-situation/` 從 19 份增加到 23 份,測試寫進了真實家目錄。每份是 `{"segs":[]}` 級的小檔,24 小時後會被清理,沒有累積風險。

我實驗用的臨時目錄 `/tmp/lumos-seat-work/code-android情境題與表態對程式/資源-sonnet/` 已刪。

總結:最嚴重是 F1(提醒記帳 900 條要 17 秒且重推重複記進版控帳),會擋 1 條。
