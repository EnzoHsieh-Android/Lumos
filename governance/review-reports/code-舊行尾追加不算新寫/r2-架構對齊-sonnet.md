severity: major

我查了三個問題,結果如下。

1. 分層與依賴方向:沒有跨層直呼。
   - `_ns_relaxed_seen` 在筆記檢查這一層,借 `_lens_git` 取 git 目錄。`_lens_git` 定義在 `scripts/lumos:39654`,後面的派工鏡頭區塊,是通用 git 包裝,筆記檢查層其他地方也在用。
   - 這只算借用通用工具,不算跨層。
   - `_gate_event_fit` 把「丟 `nodes`」從回呼 `then=` 改成參數 `nodes_cap=`。兩個呼叫端是 `scripts/lumos:29495` 和 `scripts/lumos:34589`,都已一起改完。
   - 比起 `_drift_m1_fit` 原本包的回呼,新形狀更簡單,沒有分層問題。

2. 命名與錯誤處理:只有一處需要報,見 Z2。
   - `_ns_relaxed_seen` 的失敗回傳(`except OSError: return False`)和 `_note_audit_*` 一帶的「失敗就當沒記過」一致。
   - `_note_audit_mark_appended` 新增的配對失敗提醒,格式和 `scripts/lumos:5163` 的「提醒:…」一樣。

3. 第二種做法:`_ns_relaxed_seen` 是第二種,見 Z1。
   - `_note_audit_show_class` 和 `_note_audit_class_for` 不算兩套。前者只是包一層,算類別時直接呼叫後者(`scripts/lumos:29982`),只多印「只判過句尾」那句人話,可以接受。
   - 讀被刪摘要行:`_ns_deleted_summary_lines` 已改走共用的 `_notelines_parse_hunks`,diff 內容不再有第二套解析。它發出 git 指令的旗標還和 `_ns_diff` 不同,見 Z2。

**Z1 同一次推送只記一次,用了專案裡沒有的第二種做法:自己在 git 目錄存記號檔**
severity: major
blocking: 是 — 引入了第二種「同一次推送只做一次」的做法,也引入了第二種寫入共用狀態檔的做法
引句:「mark.write_text("\n".join((seen + [key])[-50:]) + "\n", encoding="utf-8")」
1. 專案既有的做法是把 `attempt_id` 寫進治理帳事件。依據是 `scripts/lumos:1162` 的 `_gate_event_build` 和 `scripts/hooks/pre-push:236`,後者匯出 `LUMOS_PUSH_ATTEMPT`。
   - 同一次推送的事件靠這個欄位串起來,由讀帳的一方分辨,寫帳的一方不去重。
   - `_ns_relaxed_seen` 反過來,在寫入端自己用外部檔案去重,而且檔案放在 git 目錄(`.git/lumos-relaxed-seen`)。
   - 專案裡找不到另一處把狀態寫在 `.git/` 底下。
   - 要的話可以改成讀帳:掃 `.governance-log.jsonl` 裡同一個 `attempt_id`、同一個 `kind=relaxed` 且鍵相同的事件。
2. 專案裡「記在家目錄快取」的既有寫法是 `_home_cache_write`(`scripts/lumos:39755`)。它做了這幾件事:
   - 同目錄 `mkstemp` 建唯一暫存名。
   - `chmod 0600`。
   - `os.replace` 原子替換。
   - 先用 `_mkdir_trusted_under_home` 和 `_trusted_private_dir` 驗目錄。
   - `_write_lf`(`scripts/lumos:17429`)同樣是暫存檔加 `os.replace`。
3. `_ns_relaxed_seen` 用 `Path.read_text` 讀、再 `write_text` 寫回,有這幾個差異:
   - 不是原子寫入,半寫的檔案下一次會被讀成亂 key。
   - 沒設權限。
   - 沒有 `_excl_lock_try`(`scripts/lumos:40462`)那種鎖。
   - 讀改寫之間沒有保護,一次推多條分支如果平行呼叫,兩邊會互相覆蓋。
   - 這個函式存在的原因本來就是「推送前掛鉤逐分支呼叫」,平行場景正是它要擋的情況。
4. 重現指令未能附上,因為不能在 repo 根寫入。可用的單行驗證是:同時啟動兩個程序,各用不同的 key 呼叫 `_ns_relaxed_seen`,最後看記號檔是否只剩其中一個 key。

**Z2 `_ns_deleted_summary_lines` 的 git diff 旗標仍和 `_ns_diff` 不一致**
severity: minor
blocking: 否 — 解析已統一,只剩發 git 指令的旗標還是兩套
引句:「d = _ns_git(repo_root, "diff", "--no-renames", "-U0", "--no-color", "--no-ext-diff", "--no-textconv",」
1. `_ns_diff` 在 `scripts/lumos:27319` 釘了 `--inter-hunk-context=0 --diff-algorithm=myers`。目的是讓本機和 CI 的 diff 結果一致(該處註解寫明)。
2. `_ns_deleted_summary_lines` 在 `scripts/lumos:28548` 自己組了一份旗標,沒有這兩個釘選,也沒走 `_ns_diff`。
3. 解析改成照 `@@` 計數後,`interHunkContext` 造成的行號錯位不會再傷到它。
   - 但 `diff.algorithm` 不同時,刪行的切段和配對仍會不同。
   - 這會影響續行是否接在同一個改動段(`segs`)裡。
4. 它必須用 `--no-renames` 才能算「被刪的行」,所以不能直接換成 `_ns_diff`(`_ns_diff` 帶 `-M`)。
   - 該補的是同兩個釘選旗標,或抽出共用的旗標常數。

**Z3 `_note_audit_mark_appended` 的配對失敗提醒:行內已有同口徑訊息,這處格式只是接近**
severity: minor
blocking: 否 — 只是日誌口徑不同,結構沒有問題
引句:「print(f"提醒:舊行尾補括號的配對這次沒跑成({pairs.error}),補括號的行整行送審", file=sys.stderr)」
1. 同一類失敗在推送路徑是記進放寬帳,見 `scripts/lumos:28794` 的 `relaxed["error"]`,再由 `_ns_relaxed_record` 寫 `git-failed` 或 `error` 事件。
2. 筆記內容審這一側只印 stderr,不落帳。
3. 如果 `pairs.failed` 的情況值得追蹤,應該和放寬帳一樣落帳;不值得就維持現狀。
4. 這點判不準要不要落帳,標 ⚠ 交編排者。

固定席節點(圖譜鏡頭)這次沒附,編排者已說明不用補算,所以不逐條判。

不對齊共 3 條,其中 major 1 條

最高嚴重度 major,blocking 1 條
