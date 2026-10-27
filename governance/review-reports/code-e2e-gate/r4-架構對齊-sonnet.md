severity: minor

審查範圍是修補差異 r4-repair.patch,對照鄰居檔案與函式讀過。除一處的鎖外,沒有跨層直呼。「第二種做法」我判不到 major,但有幾處值得編排者留意(見第 3 問,尾端附一個 ⚠)。鎖檔 `.warming` 在 `~/.cache/lumos/dispatch-lens/` 下不存在,我沒碰任何鎖。

## 1. 分層與依賴方向

- 新碼全落在 `scripts/lumos` 的 e2e 區段(`_e2e_*`)與開場掛鉤對應的複本,沒有往別的層伸手。
- `_e2e_gate_uses` 新加的「上一版有沒有 e2e 段」檢查,直接呼叫 `_nodehome_git`、`_e2e_tree_json`、`_secev_git_left`、`_secev_int`。同函式與同區段原本就是這樣取用,所以不算跨層。
- `_e2e_ai_pending` 改成轉呼叫 `_e2e_ai_pending_one`,收成同一份計數,方向和鄰居一致。
- `_e2e_record_update` 用 `_e2e_record_err` 加 `_e2e_gate_times_err` 判紀錄讀不讀得懂,與 `_e2e_gate_load` 共用同一套,符合 `_vault_write_lock` 一帶「寫入前用讀取端同一把尺」的做法。
- file: `scripts/lumos:41579-41580`、`scripts/lumos:40950-40972`

不對齊 1(分層內、不是跨層):`_e2e_scope_dirs` 和 `_e2e_owner_index` 回傳的元組多了一項,文件字串沒跟上。

severity: minor
blocking: 否
引句:「指紋範圍的三組路徑 → (app_dirs, exclude, 驗收素材);_e2e_scope_hit 與算指紋時給 git 的 pathspec 共用。」
- 現在 `_e2e_scope_dirs` 回四項,第四項是巢狀元組 `(mdirs, fset, fmaxd)`,`_e2e_scope_hit` 用 `apps, excl, _mats, (mdirs, fset, fmaxd)` 解包。
- `_e2e_owner_index` 的文件字串仍寫回三項,實際回四項。
- 鄰居的 `_e2e_scope_dirs`、`_e2e_owner_index` 原本都是平的元組。
- file: `scripts/lumos:40611-40629`、`scripts/lumos:40631-40643`

## 2. 命名與錯誤處理

- 命名一致:`_e2e_` 前綴、`_err` 回傳「錯誤訊息或 None」、擋下回 `(None, 訊息)`,都跟 `_e2e_relpath_err`、`_e2e_cfg_err` 一樣。
- 新旗標 `newer_schema`、`mainline_newer` 照 `removed`、`uncommitted`、`merge_main` 的布林旗標寫法,擋下訊息分支也照原本的 `elif` 串接。
- 治理帳事件沒動,pre-push 仍記固定的 `loop escape --auto` 描述。
- `_e2e_load_json` 的錯誤訊息改成直接印 `{e}`,與 `_macrobench_stab_load` 的寫法一致(`scripts/lumos:39961`)。

不對齊 2:`_e2e_gate_load` 靠子字串判斷錯誤種類,鄰居是用旗標。

severity: minor
blocking: 否
引句:「_e2e_gate_block(f"查證紀錄 {rerr}", bad_record="git" not in rerr, **info)」
- 鄰居用「建構時就決定的旗標」(`removed`、`uncommitted`、`merge_main`)。這裡改成看訊息文字有沒有 "git"。
- 現在 `_e2e_tree_blob` 的錯誤文字剛好不含 "git" 以外的干擾字,所以結果正確,但文字一改就悄悄判錯。
- file: `scripts/lumos:41692`(對照 `scripts/lumos:41380`)

## 3. 第二種做法

- **`_e2e_prefixes` 前綴查表**:這是重用。`_e2e_owner_index` 在 r2 就已經是「按每層前綴查表」,這輪只是抽成共用函式,讓 `_e2e_scope_hit` 也走同一條。不算另起一套。
- **`cap=None` 不設上限**:這是比照。`_read_fd_capped(limit=None)` 與 `_retro_read_bytes(limit=None)` 都用 `None` 代表讀到底。
- **複本測試**:這是比照。新測試掃主程式加 `hooks` 底下所有 `.py`、從整棵樹找同名函式、一支檔放兩份就紅,與 `t_ci_latest_attempts_copies_identical` 的做法一致。
- **`_e2e_gate_out` 出口清理**:見下面不對齊 3。
- **`_e2e_record_update` 的大小上限**:見下面不對齊 4。

不對齊 3:出口清理的位置。

severity: minor
blocking: 否
引句:「★外來文字在這裡統一清★:原因與清單裡的字串(被推送提交的設定值、紀錄的鍵名、檔名)換掉控制字元」
- 重用的是既有的 `_esc_clean`,而且「載入時就清」有先例(`_macrobench_stab_scrub`),所以不是新發明。
- 但專案裡其他閘有兩種出口:安全證據閘在印出時整行過 `_secinv_say`,其他地方在印出處逐欄位過 `_esc_clean`。e2e 閘現在變成「建構結果時清」。
- 同一個 e2e 區段裡,逐點清理沒有拿掉,`_e2e_waive_list` 與 `_e2e_changed_features` 仍各自清一遍,所以同一區段現在有兩個清理位置。
- `_cl_say_e2e_block` 自己仍是裸 `print`,不像 `_cl_say_sec_block` 整行過 `_secinv_say`。
- file: `scripts/lumos:41366-41377`(對照 `scripts/lumos:66416-66422`、`scripts/lumos:41543-41547`、`scripts/lumos:41908`)

不對齊 4:大小上限的檢查方式與鄰居的有界讀不同。

severity: minor
blocking: 否
引句:「if p.stat().st_size > E2E_RECORD_FILE_MAX:   # 掃描與判定都不讀這麼大的紀錄,寫回也不整份讀進來」
- 這是「先 `stat`、再 `read_text` 整份讀」。
- `_read_fd_capped` 的文件字串自稱「有界讀的唯一一份」,先開檔再讀到上限加一就停。
- 同區段的 `_e2e_record_files` 本來就是「`lstat` 加 `read_text`」,所以在 e2e 家族內是一致的。
- 但這裡用的是 `stat`(會跟著捷徑走),`_e2e_record_files` 與掛鉤用的是 `lstat`。
- 路徑安全由前面的 `_repo_path_unsafe` 擋住,實際風險有限。
- file: `scripts/lumos:40960`(對照 `scripts/lumos:1682-1695`、`scripts/lumos:41838-41846`)

⚠ 交編排者:不對齊 3 判 minor 不是 major,理由是 `_esc_clean` 與「載入時清」都有先例。要不要把它升成 major,取決於你把「清理位置」算不算「做法」。我的判斷是不算,因為工具與函式沒換,只是位置換了。

不對齊共 4 條,其中擋實作的 0 條
