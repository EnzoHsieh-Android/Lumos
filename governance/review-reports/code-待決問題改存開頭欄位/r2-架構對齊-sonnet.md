severity: major

答案順序:先逐問回答,再列不對齊。對照行號取自修後版本 c0265db0 的 `scripts/lumos`。

**問 1 分層與依賴方向**
- 新碼都放在 `scripts/lumos` 單檔裡、既有的區段內,沒有跨層直呼。
- `_pq_bad_char`、`_pq_top_key` 在待決問題區頂端,被 `_strict_scalar` 和 `_pq_scan` 往下呼叫,方向正常。
- `_pq_platforms` 呼叫 `load_platforms`(`scripts/lumos:5825`)和 `_vault_repo_root`(`scripts/lumos:9893`),被 lint 規則呼叫,方向正常。
- `_pq_git_read_many` 由 `_pq_push_remind` 呼叫,同屬規格閘區。
- `_decision_cmd_locked` 是 dispatcher 層,由 `main()` 呼叫。
- 不一致的是鎖放的層。鄰居是 `cmd_set`(`scripts/lumos:20103`)自己拿鎖,再叫 `_cmd_set_locked`(`scripts/lumos:20218`),dispatcher 只包 try/except。這輪卻把鎖拉到 dispatcher(見下面第 5 條)。

**問 2 命名與錯誤處理**
- `_pq_git_read_many` 失敗回 None、呼叫端印一句「提醒:…跳過」,這跟 `_spec_gate_prepare`(`scripts/lumos:8159`)的「印一句回 None」同形,對齊。
- `_check(_fields)` 不用傳入的 fields、自己重解 new_lines,跟 `cmd_decision_supersede` 的 `_check`(`scripts/lumos:20820`)是同一個掛法,對齊。
- 不對齊的是 `_decision_cmd_locked` 的命名與鎖位置(第 5 條),以及 `_pq_platforms` 讀設定失敗時悄悄退回單平台(第 6 條)。

**問 3 第二種做法**
- 上一輪要收掉的四項:
  - 嚴格讀法掛在 `parse_decisions`:已收掉。`parse_decisions` 恢復成只讀 decisions,`_pq_scan` 獨立,docstring 說明了文法不同。
  - 測試名另一套比法:已收掉。`_pq_test_same` 刪了,改走 `resolve_test_refs`(`scripts/lumos:5910`)。
  - 讀回檢查被架空:已收掉。`lambda _f: True` 換成有內容的 `_check`,走 `atomic_write_verify`(`scripts/lumos:19907`)的標準掛法。
  - 決策存在自己重寫:只收了一半。`_dref_parse` 接回來了,但節點解析又手寫一份(第 3 條)。
- 這輪新引入了三種第二做法:`cat-file --batch` 解析(第 1 條)、`merge-base` 計算(第 2 條)、字元類別判定(第 4 條)。

---

severity: major
blocking: 是
引句:「def _pq_git_read_many(rr, specs):」
這是專案裡第二份 `cat-file --batch` 解析。專案已有共用的 `_nodehome_cat_blobs`(`scripts/lumos:30360`),回傳同順序的 bytes 或 None,git 跑不起來回 None,還處理了 missing、ambiguous、非 blob 和路徑含換行。新碼沒擋路徑含換行,換行會讓輸出錯位而靜默對錯檔。`scripts/lumos:23133` 的註解明講「第四輪架構席:第三輪另寫了一套 cat-file --batch 解析」,被收掉過一次,這輪又寫了一份。對照處:`scripts/lumos:30360`、`scripts/lumos:23133`。

severity: major
blocking: 是
引句:「mb = subprocess.run(["git", "-C", str(rr), "merge-base", base, head], capture_output=True, text=True)」
專案已有 `_range_base(rr, diff_range)`(`scripts/lumos:42905`),語意就是「`a..b` 取 a,`a...b` 取 merge-base」。規格閘區的 `scripts/lumos:8392` 已在用它,旁邊註解寫「同檔同算法要收斂成一份」。`_pq_push_remind` 又自己用正規式拆範圍、再算一次 merge-base。失敗時印一句提醒可以由呼叫端在 `_range_base` 回 None 時做。對照處:`scripts/lumos:42905`、`scripts/lumos:8392`。

severity: major
blocking: 是
引句:「hits = [r for r in env.notes if Path(r).stem == lit]」
決策連結的節點解析又手寫了一套:帶路徑就整條比 `.md`,只有短名就逐篇比 stem,撞名回 bad。專案的做法是 `_dref_norm`(`scripts/lumos:21300`)呼叫 `env.resolve`,後者由 `make_resolver`(`scripts/lumos:668`)建成,比 stem 時轉小寫、取第一篇。同一種 `<節點>#dN` 格式,在 decision_refs 和 pending_questions 裡會解成不同的結果,大小寫與撞名的判定都不同。`self_fm` 分支另外自己讀磁碟、自己 `split_frontmatter`,沒走 `_node_decisions`(`scripts/lumos:21319`)。上一輪要收掉的「決策存在自己重寫」只收了一半。⚠ 嚴格化也許有理由,但這樣做會讓同一格式有兩種語意,要嘛收斂進共用解析,要嘛把差異明寫並同步另一邊。

severity: major
blocking: 是
引句:「return next((c for c in v if unicodedata.category(c) in ("Cc", "Zl", "Zp")), None)」
專案的特殊字元類別集合是 `_PATH_SPECIAL_CATS = Cc, Cf, Zl, Zp, Cs`(`scripts/lumos:35187`),旁邊的註解寫「日後補類別要改兩處」,並要求各處共用。`_json_text_escaped`(`scripts/lumos:14003`)和 `_kill_esc`(`scripts/lumos:16517`)都用它。`_pq_bad_char` 自訂了 Cc/Zl/Zp 三類,沒有 Cf(雙向覆寫、零寬),而它的理由是「ESC 印到終端能改畫面」,跟 Cf 的終端風險同族。沒有理由說明為何不用共用組,也沒有像 `scripts/lumos:11698` 那樣寫明「為什麼不用共用組」。可以用 `_PATH_SPECIAL_CATS - {"Cs"}` 找出第一個字元。

severity: minor
blocking: 否
引句:「def _decision_cmd_locked(env, rel, args):」
命名與拿鎖位置跟鄰居相反。鄰居的 `_cmd_set_locked`、`_cmd_append_locked`、`_guard_*_locked` 是在鎖已被拿住時才被呼叫,拿鎖的是外層 `cmd_*`。這支叫 `_locked` 卻自己拿鎖,而且放在 dispatcher 層,不在 `cmd_decision_*` 裡。拿鎖範圍也不齊:同一份開頭欄位上的 `decision-reindex --all`(`main()` 內 `cmd_decision_reindex(env, all_mode=True)`)和 `decision-amend`(`scripts/lumos:41571`)仍沒鎖。⚠ 後兩者是不是這輪該補,要看計劃範圍。對照處:`scripts/lumos:20103`、`scripts/lumos:20218`。

severity: minor
blocking: 否
引句:「def _pq_platforms(env):」
讀平台設定出錯時悄悄退回「單一平台」。鄰居(`_spec_gate_prepare` 在 `scripts/lumos:8159`,`_spec_gate_push_scan` 附近的「平台設定讀不動」)是印一句再略過或放行。`_kill_cfg_load`(`scripts/lumos:16419`)連原因都回給呼叫端。靜默退回單平台時,前綴條款(例如 `kotlin:foo`)會被當成名稱去比,可能對錯綁定。另外 `_nl_rule_pending_questions` 在迴圈裡每一個已驗題都重載一次設定,鄰居是一次載入重複用。

不對齊共 6 條,其中 major 4 條
