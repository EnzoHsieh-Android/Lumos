severity: clean

只做架構對齊,不找 bug。修補只動兩處:整批掃描的忽略規則,和守的測試雜湊的名稱查找。兩處都沿用專案既有做法,沒有新的第二種做法,也沒有跨層直呼。

(以下 file:line 指提交 24ec789 的 `scripts/lumos`;我把那版另存到 scratchpad 讀的。)

## 問 1 分層與依賴方向
- **`_choice_scan_batch` 加 `--no-ignore`**:仍走原本的 `_choice_sg_run`,argv 還是參數清單、不開 shell,設定路徑仍走 `_lint_wt_cfg_inside`。呼叫鏈沒變(`_choice_scan` → `_choice_scan_batch` → `_choice_sg_run`),所以沒繞過共用函式。
- **`--no-ignore` 不在禁帶清單**:`_LINT_WT_BANNED` 只有 `-U`、`--update-all`、`-i`、`--interactive`、`--custom-languages`(`scripts/lumos:41543`)。這一條也不經過 `_lint_wt_*` 的命令驗證,是直接組 argv,所以不抵觸「不帶 -U、-i、--custom-languages」的既有規範。
- **ast-grep 版本佐證**:0.51.2 的 `scan --help` 確認 `--no-ignore <FILE_TYPE>` 可重複傳入,六個值就是 hidden、dot、exclude、global、parent、vcs。
- **`_choice_test_blobs` 的 term 映射**:用 `_dotted_ident`(`scripts/lumos:26421`)判斷後取最後一段。這和 `_classify_test_refs` 附近 `scripts/lumos:73222` 的 `method in mset or (_dotted_ident(method) and method.rsplit(".", 1)[-1] in mset)` 是同一個寫法。雜湊鍵仍是 (平台, 原名),下游 `_choice_tests_sha`、`_choice_kill_pick` 沒受影響。
- **`_choice_push_scan` 的簽章收斂**:`_CHOICE_GUARD_FLOOR` 與 deadline 回傳拿掉,`_choice_guard(..., cache=cache)` 改成只吃同一份快取。我 grep 修後版只剩註解提到它,沒有殘留引用。`_choice_guard` 仍保留 `deadline=None` 參數,另一個呼叫端 `scripts/lumos:78289` 還在用,簽章沒被破壞。

## 問 2 命名與錯誤處理
- **常數命名**:新常數 `_CHOICE_SG_NO_IGNORE` 沿用同區 `_CHOICE_BATCH_SHARE` 的 `_CHOICE_*` 前綴,放在它正下方。
- **錯誤收法**:失敗路徑沒變(`except (_ChoiceUnverifiable, OSError, KeyError): return None` 退回逐檔),rc 0/1 照舊,沒新增 rc 或訊息。
- **帳本寫法**:沒動,沒有新增 `_choice_gate_event` 以外的寫帳方式。
- **圖譜筆記**:兩條 PITFALL 照 `[出處:] [根因:] [修法:] [test:]` 格式寫。〈依據來源〉表新增兩列都有出處格。
- **錨點簽核**:`anchor-baseline.json` 的 note 照前輪格式附使用者原話。

## 問 3 第二種做法
- **名稱剖析**:沒有另寫一套。`類別.方法` 取最後一段重用 `_dotted_ident`,句子名照整串,跟 `_test_in_tree`、`_classify_test_refs` 的語意一致。
- **忽略規則**:專案裡沒有別處處理 ast-grep 的忽略規則(`scripts/lumos` 與 `check.py` 都沒有 `--no-ignore`),所以這裡是第一處,不構成第二套。
- **逐檔路徑**:逐檔點名 `src/<名>` 沒帶 `--no-ignore`。逐檔明點檔案,不受目錄忽略影響,和計劃寫的一致。
- **重疊計數與時限**:沒新增。

## 小結
圖譜鏡頭:尾端沒附固定席,這次沒有可逐條判的固定席節點。

未驗範圍:沒跑測試、沒做修前修後的行為對照。這份是架構對齊審查,所以只對照了鄰居程式碼。另外 `_choice_test_blobs` 對非 dotted 的句子名仍用 raw 字串,不像 `_test_in_tree` 會處理跳脫過的引號。這不是這次修補引入的,是修前就有的行為,不算不對齊。

最嚴重:clean;blocking 共 0 條
不對齊共 0 條,其中 major 0 條
