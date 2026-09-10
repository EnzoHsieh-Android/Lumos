severity: major

**問一(分層與依賴方向):對齊。** 新判別函式 `_is_vendored_path`(file: `scripts/lumos:13133`)與 `_is_toolchain_repo`(file: `scripts/lumos:13142`)緊鄰 `_VENDORED_TOOLKIT`(file: `scripts/lumos:13127`)定義,只讀既有清單不另記一份,呼叫端 `_stack_ext_counts`(file: `scripts/lumos:13630`)、`_pitfall_diff_collect`(file: `scripts/lumos:17578`)都是讀共用清單而非新開一份表,跟 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIR`(file: `scripts/lumos:15982`)「單一源、多消費者」的既有做法同一種。`_is_toolchain_repo` 判別鍵直接沿用 `_self_repo_origin`(file: `scripts/lumos:14162`)已經在用的 `skills/lumos-project-notes/SKILL.md` 探針,連 docstring 都寫明沿用。`_stack_changed_ok` 用新增可選參數 `skip_vendored=False`(file: `scripts/lumos:17558`)擴充既有函式服務兩個消費者,不是另寫一份,符合本檔一貫「共用一支、參數化差異」的做法。三處都是被既有 `cmd_*`/掃描函式呼叫的私有輔助函式,沒有跨層直呼寫入層。

**問二(命名與錯誤處理):部分不對齊,見 F2/F3。** `_set_about_code`(file: `scripts/lumos:10803`)重用 `load_raw_for_edit`/`atomic_write_verify` 的原子寫入與讀回驗證機制,寫入機制本身跟 `cmd_set`/`cmd_append` 一致。但既有「`cmd_*` 委派的私有輔助函式」一律 `_cmd_<name>` 前綴(`_cmd_remove_scalar` file: `scripts/lumos:10936`、`_cmd_codeloop_dispositions`/`_cmd_codeloop_recall_miss`),新函式卻叫 `_set_about_code`,漏了 `cmd_` 中綴。擋下訊息裡「檔案沒動」的位置也不同:`cmd_set`/`cmd_append`/`cmd_remove` 的擋下訊息全把「,檔案沒動。」接在主要理由子句後面再補充引導語(file: `scripts/lumos:10838`、`scripts/lumos:10885`),新訊息卻把它挪到句尾、獨立成句(file: `scripts/lumos:10815`)。至於「`cmd_set` 開頭用 key 特判分流」有沒有先例——`if key == "status"`(file: `scripts/lumos:10847`)是先例,但它是過完 `SCALAR_KEYS` 白名單、走標準 `edit_fm_scalar` 寫完之後才加一段同步 tag 的「後綴動作」;新的 `if key == "about_code"`(file: `scripts/lumos:10835`)卻在函式第一行就短路整個白名單分流,跳去一支平行寫入函式——這個短路模式沒有先例,細節併入 F1。

**問三(第二種做法):不對齊,major。** `about_code` 至今仍留在 `LIST_KEYS`(file: `scripts/lumos:10533`),`cmd_append`/`cmd_remove` 因此照舊把它當清單型欄位處理,兩者都對 kind 做硬性檢查。新的 `_set_about_code` 卻讓 `cmd_set` 把同一欄位當純量直接改寫,還繞過 `edit_fm_scalar` 對 kind 的型別檢查、手動切片覆寫 frontmatter 行(file: `scripts/lumos:10824`)。結果同一欄位活在兩套規則下:`set` 把它當純量寫、`append`/`remove` 仍把它當清單治理——這正是跟 `SCALAR_KEYS`/`LIST_KEYS` 白名單並行的第二條欄位規則,而不是把 `about_code` 正式移出 `LIST_KEYS` 改記一次規則。repo 根算法與「是不是工具鏈本體」判斷沒有引入第二套:`_set_about_code` 用的 `_vault_repo_root`(file: `scripts/lumos:5476`)是既有唯一函式,`_is_toolchain_repo` 沿用 `_self_repo_origin` 的判別鍵。

### F1 about_code 留在 LIST_KEYS 卻被 cmd_set 短路成純量寫,兩套欄位規則並存
severity: major
blocking: 是 — 同一欄位在 set/append/remove 三指令下活在兩套互相衝突的型別規則,是跟 SCALAR_KEYS/LIST_KEYS 並行的第二條欄位規則
引句:「set 只能改這些純量欄位:{sorted(SCALAR_KEYS | {'about_code'})}」
這行只在錯誤訊息裡把 about_code 臨時併進顯示集合,`SCALAR_KEYS` 本身沒有加它,`LIST_KEYS` 也沒拿掉它。`cmd_set` 因為 `if key == "about_code":` 短路整個白名單分流,直接繞到一支平行寫入函式,而 `cmd_append`/`cmd_remove` 對同一個 key 仍走原本的清單型路徑。

### F2 _set_about_code 沒有比照既有 _cmd_ 前綴命名慣例
severity: minor
blocking: 否 — 純命名不一致,函式行為與結構本身沒問題
引句:「def _set_about_code(env, rel, value):」
既有的 cmd_* 委派私有輔助函式(`_cmd_remove_scalar`、`_cmd_codeloop_dispositions`)一律 `_cmd_<name>` 前綴,新函式漏了 `cmd_` 中綴。

### F3 擋下訊息裡「檔案沒動」的位置跟鄰居不同
severity: minor
blocking: 否 — 只是措辭順序不同,擋下語意與 rc=2 仍一致
引句:「"檔案沒動。", file=sys.stderr)」
鄰居的擋下訊息一律「主要理由,檔案沒動。<補充引導>」,檔案沒動緊接在理由後面;這裡改成把它放到整段細節之後單獨成句。

不對齊共 3 條,其中 major 1 條
總結:最高 severity major,blocking 共 1 條
