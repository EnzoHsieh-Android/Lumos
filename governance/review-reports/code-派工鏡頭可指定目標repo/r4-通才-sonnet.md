severity: minor

## 測試結果

前提:我在 `lens-repo`(含修補的那份程式)跑了三組測試。Backend_improve 工作樹裡沒有修補後的程式(`grep -c _lens_spec_name_ok scripts/lumos` 為 0),原本在那邊啟動的 `-k nodehome` 我已終止,沒有採用。測試時加了 `PYTHONDONTWRITEBYTECODE=1`。

- `python3.14 scripts/test_lumos.py -k nodehome`:721 passed, 0 failed
- `python3.14 scripts/test_lumos.py -k dispatch_lens`:335 passed, 0 failed
- `python3.14 scripts/test_lumos.py -k spec_freeze`:89 passed, 0 failed

## finding

severity: minor
blocking: 否 — 只影響「計劃來源」那行的顯示,不影響讀檔、判定或寫入。
引句:「_LENS_SPEC_PATH_SHOW_RE = re.compile(f"[{_LENS_SPEC_NAME_CHARS}]{{1,300}}")」
問題:計劃路徑從原本的「只擋控制類字元的黑名單」,改成和節點名共用同一份白名單。白名單只收 ASCII 字母數字、日韓中文字、`- _ . /`、空白和半形與全形括號。因此計劃檔名只要帶白名單外的標點(例如 `+`、`&`、`,`、全形逗號、全形冒號、`「」`),提交寫法的來源行就從原本印出路徑,退成「(路徑含不收的字元)」。
具體失敗情境:計劃檔名是 `Projects/A+B_計劃.md`,用 `<完整提交編號>:docs/x-knowledge/Projects/A+B_計劃.md` 派設計審。審查員看到「計劃來源:提交 xxxx 的(路徑含不收的字元)」,對不上 spec-freeze 印的那行。內容照讀,只是少了路徑。目前 `lens-repo` 和 `Backend_improve` 兩個圖譜的全部 .md 節點名都過白名單(我逐一掃過,不合的是 0 篇),所以只有往後檔名帶了這類標點才會碰到。
佐證:``scripts/lumos: `49572`(shown_rel 判斷)``、``scripts/lumos: `49185`(白名單)``

## 已讀,無 finding

- **`_nodehome_cat_sizes` 擴充(加 `ValueError`)**:`lens-repo` 內只有 `_spec_commit_present` 一個新呼叫端。輸出對齊(一個輸入一行輸出)、檔名帶空白、目錄型別都處理得對。
  - 候選走 `_spec_commit_cands_norm`,含換行、NUL 的已先濾掉,不會讓整批變 None。
  - NFC 與 NFD 兩種寫法都問,ls-tree 關掉 `core.precomposeunicode`,結果的鍵一律是 NFC。
  - 候選超過 5000 個時只算前面的。節點排在程式檔前面,節點的分類不會被擠掉。
- **`_vault_node_path` 抽出 `_vault_node_check` 後的落點路徑**:`unreadable` 走到 `_nodehome_landing_existing(None)`,印「讀不到」,和原行為一致。`missing` 仍分「要新開」「只在提交裡」「兩邊都沒有」三類。圖譜資料夾有問題時,落點改印更精確的原因,不會誤歸成「要新開」。
- **固定席改走 `_vault_node_path` 篩選與 `_vault_node_read`**:impact 回傳的節點名是相對圖譜資料夾的名字,和舊的 `vault_rel + node + ".md"` 一致,`_read_wt` 的 `rel[len(vault_rel):-3]` 還原正確。
  - 兩個圖譜的現有節點名全過白名單,不會誤刪固定席。
  - 被濾掉的有計數說明,不是靜默丟棄。
  - 每個節點多做一次 lstat 走訪,節點上限 8,成本可忽略。
- **`no_knowledge`**:`found` 和 `slugs` 的過濾條件與原本一致。只剩符號連結時,rc 仍是 3,只是訊息更具體。
- **`_spec_commit_rev_ok`(dispatch-lens 與 spec-freeze 共用)**:判斷邏輯和原本逐字相同,兩邊回傳碼都沒變。
- **`_spec_commit_present` 回傳改成「(dict, capped)」**:`scripts/lumos`、`scripts/hooks/claude/*.py` 內的呼叫端都已同步,只有 `cmd_dispatch_lens_spec` 一個。`cidx.get` 在「沒問到」時回 None,各處都當「不列也不數」處理,不會誤算成「找不到」。
- **你點名的「測試執行器存回環境拿掉手寫那份」**:這部分不在 r4 修補差異裡(修補只動 `scripts/lumos`),我沒有審。

最高等級 minor,blocking 0 條。
