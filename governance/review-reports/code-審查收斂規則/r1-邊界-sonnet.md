severity: minor

我在臨時 fixture 上實跑了殘留標記、問答留痕、索引與分級,實驗目錄已刪。決策指標的 `#d0`、`#d012`、帶 `.md`、`[[…]]` 包裝、短名都被擋,理由對得上。`--checker` 缺日期的 `sonnet` 也被擋。`loop escape` 與 `--list`、撤回、`--auto` 互斥,`--list --residual-ref ""` 也會擋。沒有 blocker 或 major。

severity: minor
blocking: 否 — 只會留下一條帶標記的合約和過期的索引,doctor 會報對不上,不會直接放行;但指令回報的訊息是錯的
引句:「raise WriteBlocked(f"殘留索引 {_RESIDUAL_INDEX_REL}:{why}")」
問題:`_cmd_guard_residual_locked` 先用 `atomic_write_verify` 寫好筆記,才呼叫 `_residual_index_write`。索引寫不進去時,例外被當成「擋下」,回 rc 2、訊息說「這次不寫」,但合約行已經多了 `[residual:]`。
具體失敗情境:我把 `governance/residual-index.json` 做成目錄,再跑 `guard residual … --add Projects/a_計劃#d12 --case c1`。輸出是「擋下:…不是一般檔案;這次不寫」,rc 2。`grep -c "residual:" Systems/S.md` 卻是 1,筆記已改。pitfalls 讀的索引沒有這筆,不會升 high。使用者照訊息以為沒寫,不會去跑 `--reindex`。要到下一次 doctor 才看得到「殘留索引對不上」。測試只測了成功路徑和各種預檢失敗,沒有測「筆記寫了、索引寫失敗」。
佐證:``file: `scripts/lumos`(patch 的 `_residual_index_write` 與 `_cmd_guard_residual_locked`)``

severity: minor
blocking: 否 — 同一個決策被算成兩筆,只影響徽章和索引的筆數,分級結果不變
引句:「if ref in have:」
問題:判「已經有了」是逐字比對,但寫入前的檢查(`_pq_decision_state`、`_residual_decision`)不分大小寫。
具體失敗情境:先 `--add Projects/a_計劃#d12`,再 `--add projects/A_計劃#d12` 都回 0。合約行尾因此有兩個指向同一筆決策的標記。派工鏡頭的 `invariant_residual_refs` 取 `set()` 後會顯示「⚠帶殘留 2 筆」,索引的 `residuals` 也有兩個,但實際只有一筆。測試 S5 的「同一筆只算一次」只用完全相同的字串。

severity: minor
blocking: 否 — 「只准問一次」的防線可以繞過,但問答本來就是自報,這條防線靠自覺
引句:「同一條合約、同一個反例只准問一次」
問題:`prev` 只比對 `case` 字串逐字相等。`_RESIDUAL_CASE_RE` 又允許大小寫和 `.`,所以 `c1`、`C1`、`c1.` 都是不同的反例。
具體失敗情境:`c1` 被判 testable 後,用 `--case C1 --verdict untestable` 重問,回 0 並寫進帳。接著 `--add … --case C1` 就能記殘留。我實測 `c1`、`C1`、`c1.` 三筆都 rc 0。另外,`--checker` 的 `\d` 吃全形數字,`x/２０２６-１０-１４` 也過了,日期 `9999-99-99` 也過。測試只驗了一個格式錯的輸入(`sonnet`)。

severity: minor
blocking: 否 — 只是殘留索引的 `test_files` 過期後 doctor 看不到,漏的是升 high 的範圍
引句:「want = {(e["node"], e["fp"]): e for e in _residual_index_entries(env, with_tests=False)}」
問題:doctor 比對索引時刻意不算 `test_files`,只比 `residuals` 和 `about_code`。綁定測試改名、搬到別的檔,或 `[test:]` 改綁,索引的 `test_files` 都會過期。
具體失敗情境:測試搬到 `tests/test_b.py` 後,索引仍列 `tests/test_a.py`,doctor 不報。之後只改 `tests/test_b.py` 的推送不會升 high。測試 S9 的 doctor 部分只改過 `about_code`,沒有 `test_files` 的情境。

已讀,無 finding:
- `about_code` 寫資料夾或萬用字元:`about_code` 本來就被 lint 限定寫到檔案(程式裡有「它是目錄;about_code 要寫到檔案」的訊息),寫 `src/` 會被正規化成 `src`,不會升 high。這是既有規則,不算新 bug。
- 改名與刪除:`--no-renames` 加上起點、頂端兩版索引取聯集,刪檔和改名都會升 high。刪除只要被刪的檔在索引裡就命中。
- 索引檔不存在、壞掉、頂層是 list、`entries` 形狀不對:pitfalls 側回空集合(分級照舊),doctor 側有 `except` 並報「讀不出」。
- 從別的工作目錄(cwd=`/`)跑 `guard residual`:`test_files` 路徑解析正確。
- 合約行已有多個 `[residual:]`:`--remove` 只拿掉第一個符合的,寫後自驗的計數也對。
- 治理帳重構:`_gov_vc_gate_events` 與原 `_retro_gov_events` 的行為一致。

最高等級是 minor,blocking 條數 0。
