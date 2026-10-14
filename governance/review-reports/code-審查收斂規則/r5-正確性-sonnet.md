severity: minor

我讀了修補差異。另外在臨時 repo 實跑了新增問答計數、多重集合比對、鏡頭附段三條路徑。跑完已刪臨時目錄。

severity: minor
blocking: 否 — 只影響審查席有沒有被告知,分級本身仍升 high,而且觸發條件是 git 讀不出治理帳,很少見
引句:「new_rows = dl[1] if dl else Counter()」
問題:`_residual_ask_rows_delta` 回 None 代表起點或頂端的治理帳 git 讀不出,例如淺層 clone 或物件遺失。分級端把這種情況記成 `asks_dropped = -1` 並升 high。鏡頭端卻把 None 當成「沒有新增問答」。這時如果殘留索引也沒有新增,`_lens_residual_new_lines` 回 []。`_lens_residual_section` 對 [] 回 [],審查席拿不到附段,也沒有「算不出來」的說明。函式 docstring 承諾的是「算不出來也回固定說明加必答題(不准靜默放空)」。頂端索引讀不出(`hst` 為 bad 或 unreadable)也走同一條靜默路徑,因為 `new_res` 會被設成空集合。
具體失敗情境:淺層 clone 裡範圍起點的 `docs/.governance-log.jsonl` 讀不出,而這次推送新增了判 untestable 的問答。輸入是範圍 A..B。結果是 pitfalls 印 tier high,理由是「git 讀不出那段差異」。派工鏡頭卻沒有新增殘留段,也沒有必答題,審查席不知道要去查問答列。
佐證:file: `scripts/lumos:48861`(`_lens_residual_new_lines` 內 `dl = _residual_ask_rows_delta(...)` 之後那行)、file: `scripts/lumos:48882`(`_lens_residual_section`)

已讀,無 finding 的部分:
- 新增問答計數的範圍寫法:實跑 `main..br`、`main...br`、`main..HEAD`、單一版本 `main`、`main..` 都得到 `asks_untestable_added: 1`,`br..main` 得到 `asks_dropped: 1`。
- 治理帳過濾方式:`_residual_ask_rows_at` 與 `_gov_vc_gate_events` 都先用 `residual-ask` 字面過濾,所以閘名跳脫寫法兩邊一致被略過,繞不過計數,也進不了 `--add`。
- 起點治理帳不存在、頂端有新增列時,新舊兩套行為差別不影響結論:原本的「起點為空就回 0」捷徑拿掉後,「起點有、頂端沒有」仍是 0,頂端新增列照算。
- 重複的整列用 Counter 相減,各算一筆,正確。
- doctor 多重集合比對:實跑少一筆、順序不同、索引重複、欄位不同、指紋不同五種輸入,訊息都合理。writer 不去重,所以不會產生永久假警報。壞形狀的索引條目會被 try 接住。
- 鏡頭附段觸發條件:新增殘留、reworded、新增判 untestable 的問答、讀不出判定的列,都在 `want` 或 `unread` 裡。內容從頂端版本讀,每個欄位都過 `_plain_label`。實跑只有新增問答的情境,附段與必答題都正確印出,空範圍回 []。快取鍵含 `_LENS_SCHEMA`(已升 4),舊快取會自然失效。
- `_diff_range_ends` 加 no-replace:只影響 `...` 分支的 merge-base。`_vendored_skip` 只用它取起點,影響限於本機有 replace refs 的消費專案,而且是回到真實歷史,不會讓該跳過的工具檔不跳過。
- `_gov_ts`:不是字串、不是 ISO、轉時區出界都回 None,與舊版相比只更嚴。
- `guard audit` 遇到捷徑帳不寫,並印出警告。
- 資料狀態五問(空、單一、多個、壞、舊),已用前述實跑與讀程式涵蓋。

最高等級 minor,blocking 0 條。
