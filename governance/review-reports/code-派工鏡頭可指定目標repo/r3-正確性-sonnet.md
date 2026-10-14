severity: minor

我讀了修補差異,並在臨時 repo 實跑了 `spec-freeze` 和 `_spec_commit_present`,其中有 1 條 minor。實驗目錄已刪。

### Finding 1(be-api-compat 不適用,屬資料狀態)

severity: minor
blocking: 否 — 只影響提交裡用 NFD 存檔名的少見情況,後果是少列一個「只在提交裡」的檔,不會寫錯東西或放行錯誤。
引句:「路徑先 NFC(正確性2:計劃內文的 NFD 名在 macOS 存成 NFC 的提交裡比不到)」
問題:`_spec_commit_present` 把所有候選路徑先轉成 NFC,再拿去問 `cat-file --batch-check`。上一輪修的是「計劃寫 NFD、提交存 NFC」。但如果提交本身存的是 NFD(Linux 上的 git,或 macOS 設 `core.precomposeunicode=false`),不管計劃寫 NFD 還是 NFC,git 都查不到。原本用原字串比對,NFD 對 NFD 是會命中的,所以這是修補造成的新退化。
失敗情境:
- 輸入:提交裡有 `scripts/é.py`,檔名是 NFD(`git ls-tree` 看到的名字 `is_normalized("NFC")` 為 False),計劃內文也寫 NFD 的 `scripts/é.py`。
- 結果:我用 NFD 和 NFC 兩種候選各跑一次,`_spec_commit_present` 都回 `set()`。
- 後果:這個檔不會列進「只在提交裡」,也不會算進「兩邊都找不到」的筆數。
- 資料狀態:兩種 Unicode 寫法都存在時,另一種永遠找不到。
- 影響範圍:只有 `NFC(x) != x` 的檔名受影響,純 ASCII 和中文(無組合字元)不受影響。

佐證:``scripts/lumos: `49390 附近的 _spec_commit_present(NFC 轉換與 present.add(NFC(path)))` ``

### 重點逐項

- **沒給 `--out` 時寫到哪、會不會覆寫**(已讀,無 finding):路徑寫法只建一個不掛分支的提交並印出 `LUMOS-SPEC:` 那行。提交寫法連提交都不建,只印同一行。兩種寫法 stderr 都印「沒給 --out:只建提交、印那一行,沒寫快照」,rc 0,沒寫任何檔。
- **`--out` 的各種寫法**(已讀,無 finding):
  - 指到 `docs/x.md`,回 `out_outside_repo`。
  - `governance/review-reports` 本身是符號連結,回 `out_outside_repo`。
  - `--out` 末段是符號連結,回 `out_conflict`,外部目標沒被寫。
  - 已存在且內容不同,回 `out_conflict`,不覆寫;內容相同則視為重建同一份。
- **提交寫法讀不到時的代碼與訊息**(已讀,無 finding):
  - 7 到 10 碼的短編號,回 `spec_rev_missing`。
  - 全零 40 碼,回 `spec_rev_missing`,`--json` 印 `{"freeze_fail": "spec_rev_missing"}`。
  - 提交裡沒有那份計劃,回 `spec_missing`。
  - 代碼都已登記在 `_SPEC_FREEZE_FAIL_CODES`,訊息固定字彙。
- **`cat-file --batch-check` 批次解析**(已讀,無 finding):
  - 我送了 9 個候選,其中有含空白的路徑、符號連結、不存在的檔、目錄、尾端帶空白、含換行、`../`,只回正確的 2 個一般檔。
  - 含空白的路徑沒被切詞,因為預設格式不含 `%(rest)`。
  - 含換行、NUL、`.`、`..`、空段、絕對路徑的候選在送出前就濾掉了。
  - 缺的物件那行是 `missing`,被 `ok_line` 擋掉。
  - 輸出行數和輸入行數一一對得上。
  - 符號連結(120000 也是 blob)由後面的 `ls-tree` 看 mode 排掉。
  - 注意:這條路徑沒走 `_lens_git`,直接用 `subprocess.run`。cat-file 不跑掛鉤,不需要 `core.hooksPath` 設定,所以可以接受。
- **掛鉤照 `spec_source` 判,對舊版 lumos**(已讀,無 finding):舊版沒有 `spec_source`,`isinstance(src, str)` 為假,回空字串,和修補前行為一致。`lens_fail` 或 `spec_source` 是串列或物件時不再丟 `TypeError`。lumos 只在 `_dispatch_lens_fail(..., {"spec_source": ...})` 那一處(`scripts/lumos:49600`)帶 `spec_source`,範圍類失敗不會帶,不會被誤當計劃類。測試裡也有 `hasattr(hm, "_RANGE_ONLY_FAIL_CODES")` 為假的守衛。
- **上一輪 `deadline` 那種順手改**(已讀,無 finding):
  - `_dispositions_verdict` 的 `deadline is not None` 已還原,diff 只有那一行。
  - `_nodehome_landing_sizes` 最後的 `return (out if len(out) > 1 else [])` 是這輪新增的行為變更,但有說明(只剩標題就不印),我走過幾種情況都沒出錯。
  - `_nodehome_landing_missing` 少一個參數,呼叫端只有一處,已同步。
  - `_spec_freeze_lstat` 改用 `_repo_walk_lstat`:缺檔、末段是符號連結或目錄都回 None,語意不變。
- **節點名字元集變嚴格**(已讀,無 finding):`_vault_node_path` 現在套用 `_LENS_SPEC_NODE_NAME_RE`,工作樹寫法也受影響。我掃了 `orca/workspaces` 底下所有圖譜的 Systems 與 Issues 共 3735 個節點名,0 個不合。本 repo 與 Backend_improve 的現有節點名都能通過,所以沒有實際退化。
- **圖譜資料夾本身是符號連結**(已讀,無 finding):`_vault_dir_ok` 逐段 lstat,資料夾本身與上層是符號連結都回 None。
- **資料狀態五問**(已讀,無 finding):
  - 空輸入:候選為空回 `set()`,不跑 git。
  - 重複:用 `seen` 去重。
  - 缺的:回 `missing`,不當成存在。
  - 逾時:回 None,呼叫端印「算到一半」。
  - 編碼:用 surrogateescape 送入,ls-tree 用 `-z`。
- **角色鏡頭題**:`be-api-compat` 看 CLI 介面,`--out` 由必填變選填、舊呼叫端帶 `--out` 照舊可用,JSON 的 `out` 欄位改成可為 null,讀端要容忍。`be-authz` 沒有新增端點,不適用。
- **ruff**:掛鉤檔有 7 條告警(BLE001、I001、PLW1510)。修補前也是 7 條,沒有新增。

最高等級 minor,blocking 0 條。
