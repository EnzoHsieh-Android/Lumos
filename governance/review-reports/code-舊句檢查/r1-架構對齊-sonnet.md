severity: major

# 舊句檢查 r1 架構對齊席(sonnet)——審 r1-snapshot-code.patch

## F1 改到的檔清單另手刻了一份 name-status 解析
severity: major
blocking: 是
引句:「+    toks, out = raw.split(b"\0"), []」
佐證行:file: `scripts/lumos:27203`(_drift_probe_changes 的說明:「解析用共用的 _nodehome_name_status(代碼審 r1 架構對齊席:原本手刻第二份)」——同一個坑已被同一席打過一次)
佐證行:file: `scripts/lumos:23926`(_nodehome_name_status 的 codes 參數,說明就寫「存量漂移的候選篩選要知道哪些檔是新增或刪除」)
佐證行:file: `scripts/lumos:27212`(既有做法:`touched, renames, _gone = _nodehome_name_status(raw, codes=codes)`)
最小重現(靜態):`grep -n "_nodehome_name_status\|split(b\"\\\\0\")" scripts/lumos` 在 m1 的 _drift_m1_changes 只看到手刻的 `raw.split(b"\0")` 一份迴圈,沒有呼叫 _nodehome_name_status;既有的 drift 判定(_drift_probe_changes)與 _nodehome_evaluate 系都走共用那支。未能以測試翻紅(行為目前等價,是第二種做法的問題不是輸出錯)。
1. _drift_m1_changes 自己 `raw.split(b"\0")`、每兩個 token 取 (狀態首字, 路徑)、自己 nfc + fsdecode,產出 [(狀態, 路徑)]。
2. 既有共用的 _nodehome_name_status(raw, codes={}) 吃同一種 `-z --name-status` 輸出,已回 {路徑: 狀態字母} 與 NFC 路徑;--no-renames 的輸出只有 A/M/D 兩 token 一組,共用那支的非 R/C 分支就是它,直接能用。
3. 影響:兩份解析日後對 git 輸出邊界(奇數 token、路徑正規化、norm 旗標)各自演化;既有先例就是為了消掉這種第二份而收斂的。改法:改 --no-renames 的呼叫保留,解析交給 _nodehome_name_status(raw, codes=codes),再由 codes 組 [(狀態, 路徑)]。

## 逐項對照(計劃要求沿用的既有函式,判「真沿用」不另列 finding)
- _drift_py_names:加 m1 參數、m1=False 形狀不變,擴充沿用;指派與旗標抽成 _drift_m1_assigns/_drift_m1_flags 掛在同檔同區,命名跟 _drift_ 前綴一致。OK。
- _drift_probe_is_py、_nodehome_code_kind:_drift_m1_code_kind 直接呼叫(patch 內 `if _drift_probe_is_py(p, first_line or ""):`)。OK。
- _notelines_regions、_visible_lines:_drift_m1_scan_note 直接呼叫。OK。
- _drift_tree_env:讀起點與終點圖譜直接用。OK。
- _drift_config:擴成第四個回傳值,兩個呼叫端(scripts/lumos:28531、29391)都改了,沒有第二支讀 config 的函式;gate 與 old_sentence 從同一次解析出。OK。
- _drift_fix_hint / _drift_print_hints:m1 分支加在單一產生處,去重鍵抽 _drift_hint_key;OK。
- _drift_split_acked:m1 另分支(_drift_m1_split_acked)並在入口分流,c2/c3 綁定邏輯不動;m1 不進 _DRIFT_BOUND_KINDS,計劃有寫。OK。
- _gate_event / _gate_event_or_warn:從 _gate_event 抽出 _gate_event_build 並讓 _gate_event 轉呼叫它,事件欄位只有一份,不是複製;m1 的量長度用它。OK。_drift_m1_fit 的 4096 硬編碼跟 _ledger_append 的 4096 是兩處數字(見下註)。
- 快取寫入:_lens_cache_write 改成轉呼叫新的 _home_cache_write(共用一份,不手抄第三份);讀取用既有 _lens_cache_read、目錄用 _mkdir_trusted_under_home/_trusted_private_dir。OK。
- _drift_unknown_hint:抽成 _drift_report_must 與 m1 共用。OK。
- 新常數/函式命名:全部 `_DRIFT_M1_*` / `_drift_m1_*`,放在 drift 推送閘之後、健檢之前,與 c 系判定分開;_DRIFT_SCAN_KINDS 照 _DRIFT_FIX_KINDS 先例。無跨層直呼(判定函式不印不寫帳,印出與記帳在 _drift_m1_report/_drift_m1_ledger)。

## 已核對、計劃明寫刻意不同或不夠格另列的
- _drift_m1_ledger_miss 另寫 O_APPEND|O_CREAT 追加:既有 _ledger_append(`scripts/lumos:15875`)刻意無 O_CREAT 且超過 4KB 拋例外,語意不同;計劃〈與參考實作的刻意差異〉/計劃第 270 行已寫。不列。
- _drift_m1_about 自己切 frontmatter 讀 about_code(只認區塊清單):計劃第 101 行寫明照參考實作 `_about`、不用既有 _home_map_from_notes(第 224 行)。刻意差異,不列。
- _drift_m1_text_defs 的正則跟 _drift_py_def_re(test=False) 同形狀但另寫:檔內註解說明並有 t_drift_m1_unparsable_files 釘一致;沒有具體失敗場景,不列。
- _DRIFT_M1_DEFS_TTL 抄 _FILTER_PROBE_TTL 的值:後者定義在檔案更後面(scripts/lumos:35780),模組層無法前向引用;註解已寫「值同」。不列。

最高等級:major
