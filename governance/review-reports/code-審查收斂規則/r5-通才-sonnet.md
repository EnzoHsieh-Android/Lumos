severity: minor

已讀並實測,只有一條 minor。

驗證:`-k residual` 339 項、`-k dispatch_lens` 149 項、`-k guard_audit` 18 項、`-k cap_retro` 355 項,全綠。另在 review-converge 實跑 `pitfalls --diff HEAD~3..HEAD`(1.4 秒),沒有殘留的 repo 照常出 light。

**finding**

severity: minor
blocking: 否 — 只會多升 high,不會放行,而且要連續碰到少見條件才觸發
引句:「    if not brows:
-        return 0
     hst, hrows = _residual_ask_rows_at(repo_root, head)」
問題:`_residual_ask_rows_dropped` 改成 `_residual_ask_rows_delta` 時拿掉了 `if not brows: return 0` 的提前返回。起點完全沒有 residual-ask 列的 repo,以前根本不讀頂端帳。現在每次治理帳在改動清單裡,都會讀頂端那份。頂端讀不出就回 None,`asks_dropped` 被設成 -1。理由句會寫「推送範圍刪掉或改掉治理帳裡 residual-ask 的列(git 讀不出那段差異,當成有)」。
失敗情境:起點沒有任何 residual-ask 的 repo(多數消費專案),頂端是工作目錄且治理帳是被追蹤的捷徑或非一般檔。這時 `pitfalls` 會判 high,理由卻是「刪掉問答」,與事實不符,審查席會被誤導。我只從程式推得,沒有實際重現。一般情況(頂端是一般檔或一個提交)不會觸發。
佐證:`scripts/lumos:44636` 附近的 `_residual_ask_rows_delta`,舊版提前返回在 patch 第 609–610 行被刪。

**已讀,無 finding**
- **派工鏡頭快取**:`_LENS_SCHEMA` 升到 4 只讓舊快取 miss。快取鍵含 `base|head|schema|extra`,新增殘留段只依這兩個 sha 的 git 物件,同一個鍵結果固定。
- **段落順序**:固定席、新增殘留段、補選段依序接上。固定席為 0 的備援路徑,殘留段自己帶框,沒有掉到框外。出口照樣過 `_lens_visible`。表態記錄的框外指示句現在落在殘留段之後,措辭「上面」略遠,但不影響功能。
- **鏡頭 JSON 與 hook**:新增的 `residual_new` 欄位,`dispatch-lens-hook.py` 只讀最後一行 JSON 與 `text`,不受影響。
- **鏡頭效能**:治理帳約 20MB,`git show` 加掃描一次約 0.08 秒,鏡頭多讀 3 到 4 次,可忽略。
- **`_diff_range_ends` 加 no-replace**:只影響 `A...B` 的 merge-base 那一次呼叫,`_vendored_skip` 及其他呼叫端(分級、arch、lint-new)的語意不變。
- **`guard audit` 遇到捷徑帳**:只是不寫、改印警告,rc 仍為 0,不影響後續流程。帳檔不存在、docs 不存在時 `_drift_ledger_path_err` 回 None,照常寫。
- **`GOV_LOG_REL` 套到 cap_retro**:字串與原本逐字等價,讀帳、寫帳、錯誤訊息一致,測試全綠。
- **doctor 殘留索引比對**:改成多重集合並讓鍵帶殘留指標,語意是原本比較的超集。
- **`_residual_ev_order` 改走 `_gov_ts`**:行為相同(沒帶時區當本機時間),另補了出界保護。
- **`_pitfall_tier` 拆分**:理由句順序保持原樣,只多插入 reworded 與 untestable 兩種。
- **沒有殘留的 repo**:不升 high,輸出與原本一致。

最高等級 minor,blocking 0 條。
