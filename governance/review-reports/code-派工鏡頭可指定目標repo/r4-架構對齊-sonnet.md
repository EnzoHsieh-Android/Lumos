severity: minor

審查範圍:修補差異主審,對照 `scripts/lumos` 現況(`lens-repo`,只讀)。`scripts/hooks/claude/dispatch-lens-hook.py` 裡沒有這幾個名字,也沒有另存一份字元集或節點讀取。

你點名的四件事,我的結論:

1. **讀節點是不是唯一一套**:是。`_vault_node_read` 先過 `_vault_node_check` 才讀,落點、計劃連結、固定席三處都走它。`_read_wt` 也改走它,不再自己寫 `root / rel`。
   - 計劃連結那條(約 49641 行)只問在不在,走 `_vault_node_path`,它是 `_vault_node_check` 的薄包裝,還是同一套檢查。
   - 設計審區段裡其餘的 `root / ...` 都不是讀節點:`scripts/lumos:49607` 是找程式檔,`scripts/lumos:50040` 是 spec-freeze 讀計劃本身。
2. **`_spec_commit_present` 還留不留自寫的 git 呼叫**:`cat-file` 已改走既有的 `_nodehome_cat_sizes`。剩下的 `ls-tree` 走既有的 `_lens_git`,用來看 mode,`cat-file` 分不出符號連結,patch 註解有講明。沒有自寫的 `subprocess.run`。
3. **字元集是不是變兩份**:不是。`_LENS_SPEC_NAME_CHARS` 一份,`_LENS_SPEC_NODE_NAME_RE`(80 字)與 `_LENS_SPEC_PATH_SHOW_RE`(300 字)都從它組出來,只差長度上限。舊的另一組黑名單常數已刪掉。
4. **`_spec_commit_rev_ok` 的共用**:有共用。dispatch-lens(`scripts/lumos:49281`)與 spec-freeze(`scripts/lumos:49984`)都呼叫它,原本兩處各寫一份的 40/64 碼加 `_lens_full_sha` 比對已收斂。

只有下面一條 minor。

severity: minor
blocking: 否 — 只是把專案已有的類別檢查再抄一次,沒有引入第二種做法的行為差異,也沒有跨層直呼。
引句:「return bool(pattern.fullmatch(text)) and not any(_ud.category(ch) in _LENS_SPEC_PATH_BAD_CATS for ch in text)」
對照:`scripts/lumos:36215`(`_path_special_chars` 是專案共用的類別檢查);`scripts/lumos:7132`(同一個「共用組加 Co、Cn」組合已在 `_pq` 驗證裡內聯寫過)
判定理由:`_lens_spec_charset_ok` 自己用 `unicodedata.category` 迴圈比對 `_PATH_SPECIAL_CATS | {"Co","Cn"}`,而專案已有 `_path_special_chars` 做同樣的事。它先用 `_PATH_SPECIAL_CATS` 組出常數,算是有沿用共用類別,所以不到 major。白名單本來就不含 Cc、Cf、Zl、Zp、Cs,實際只剩 Co、Cn 在擋白名單範圍內未指派的碼位,可以改成 `not _path_special_chars(text) and not any(category in ("Co","Cn"))`,或把 Co、Cn 補進共用常數的說明。

附帶一點,不列為 finding:`_read_wt` 用 `rel[len(vault_rel):-len(".md")]` 把完整路徑切回節點名,再交給 `_vault_node_read`。這是組路徑與拆路徑對稱的小繞路,行為正確。

最高等級 minor,blocking 0 條。
