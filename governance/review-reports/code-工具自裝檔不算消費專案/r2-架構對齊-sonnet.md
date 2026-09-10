severity: minor

### F1 about_code append 對未正規化的舊式純量路徑不去重,會疊出指向同一檔案的重複項
severity: minor
blocking: 否 — 不崩潰、不遺失資料,只在既有手改/舊資料含未正規化路徑時才疊出重複項,現況圖譜(docs/lumos-toolchain-knowledge)實測零筆命中
引句:「存成正規化的樣子,排序加分用的鍵才對得上」
- file: `scripts/lumos:10878` `_about_code_path` 只把「這次要寫入的新值」正規化(`target.relative_to(root).as_posix()`),不回頭處理欄位裡既有的項。
- file: `scripts/lumos:10675` `edit_fm_append` 的 dedup 比對用 `link_target()` 逐字比對,不做 `posixpath.normpath` 之類的路徑正規化,所以「新寫法」與「舊寫法」會被判成兩個不同項。
- 重現(已在 /tmp 實測,非臆測):建一篇 `about_code: src/../src/a.ts`(未正規化的純量寫法,例如手改或舊資料殘留),對它跑 `lumos append &lt;節點&gt; about_code src/a.ts`——命令回 `✓ append`、rc0,但欄位變成兩項 `src/../src/a.ts` 與 `src/a.ts`,實際指向同一支檔案卻沒被去重。
- 為什麼算新洞而非既有問題延伸:r1 之前的 `_set_about_code` 直接覆寫整欄成一行純量(`fm[a:b+1] = [f"about_code: {v}"]`),不存在「正規化新值 vs 未正規化舊值並存」這個狀態;這個分歧是這一輪新增 `_about_code_path` 正規化後才出現的交互作用。

## 第一輪修法驗收
F1:修到 — 目錄前綴跳過改成精確檔名清單 `_VENDORED_ALL`(`scripts/lumos:13169`),消費專案自己放在 `scripts/hooks`/`scripts/templates` 的檔照掃(`t_pitfalls_diff_ignores_vendored_toolchain` ⑤、`t_doctor_s3_ignores_vendored_toolchain` ②b 綠)
F2:修到 — lint 命中的過濾移到「對齊」判斷之前(`scripts/lumos:17741-17744`),對齊/不對齊兩條路都測(`t_pitfalls_diff_ignores_vendored_toolchain` ⑦ 兩種 aligned 值都綠)
F3:修到 — 三個 `_stack_changed_ok` 呼叫點(含只刪行那條路,`scripts/lumos:17662`)都傳了 `_skip_vendored`,測試 ⑥ 綠
F4:修到 — `_set_about_code` 整支刪掉,`cmd_set` 不再特判 `about_code`,只剩 append/remove 一套規則,測試 ⑧ 綠(`set` 回 rc2)
F5:修到 — `_about_code_path` 先 `resolve()` 再 `relative_to(root)`,絕對路徑/`../` 逃逸都擋,測試 ⑤(四種壞路徑)綠
F6:修到 — 隨 F4 一併解決,同一欄位只剩一套(append/remove)規則,不再有 set 純量／append 清單兩套並存
F7:修到 — 隨 F4 一併解決,寫入改走 `edit_fm_append`→`fmt_list_item`/`strip_quotes` 既有引號處理,測試 ④(含「: 」的路徑)綠
F8:修到 — 事故筆記已改口:docs/lumos-toolchain-knowledge/Issues/健檢技術棧那段撞到多平台設定就整支中斷.md:20 明寫「(波及計算看的是正文路徑,不受影響)」
F9:修到(用「留兩份但機械守」取代原字面「不另記一份」)— 安裝端仍逐目錄複製、跳過清單改成精確檔名的另一份清單,但有 `t_vendored_file_list_matches_what_install_ships` 逐檔比對 `git ls-files`,且我獨立跑 `git ls-files scripts/hooks scripts/templates` 手動核對與清單完全一致;此模式在本 repo 有直接先例(`ANCHOR_FILES` + `scripts/test_lumos.py:12813` `t_anchor_covers_all_auto_running_hooks`)
F10:修到 — 隨 F4 一併解決,`_set_about_code` 整支移除,命名/訊息順序問題連載體都不在了
F11:修到 — `rd = _os.path.relpath(dirpath, _base)` 移到 `for fn in filenames` 迴圈外、每個 dirpath 只算一次(`scripts/lumos` `_stack_ext_counts` 現碼)
F12:修到 — `t_pitfalls_diff_ignores_vendored_toolchain` ④ 明確釘住「工具鏈本體 repo 不得跳過」,方向維持 fail-closed

風險掃描清單:誤報 — `scripts/lumos:17602` 命中的是 `_stack_changed_ok` docstring 裡描述歷史事故的文字「命中 open(...)」,不是真的 `open()` 呼叫,附近沒有任何檔案 I/O 程式碼。

## 對齊三問
1. 分層與依賴方向:精確檔名清單 `_VENDORED_TREE_FILES`(`scripts/lumos:13157`)與安裝端仍逐目錄複製(`_vendor_toolchain` 用 `_VENDORED_TREE_DIRS`,`scripts/lumos:13152/13333`;`_deinit_remove_vendored` 同名常數,`scripts/lumos:13009` 附近)並存,兩份清單靠 `t_vendored_file_list_matches_what_install_ships`(比對 `git ls-files`)守同步。此「精確清單+drift test 對真實 tracked 檔案」的做法本 repo 已有先例:`ANCHOR_FILES` + `scripts/test_lumos.py:12813` `t_anchor_covers_all_auto_running_hooks` 對 `scripts/hooks` 做一模一樣的 `git ls-files` 比對。判定:同一種做法,對齊。
2. 命名與錯誤處理:`_about_code_path`(`scripts/lumos:10878`)回 `(值, 理由)` 二元組,由 `cmd_append`(`scripts/lumos:10904-10908`)就地 `print` + `return 2`——這正是 `cmd_append` 自己開頭 `if key not in LIST_KEYS`(`scripts/lumos:10901-10903`)既有的「就地印訊息早退」寫法,不是另開一套。`_list_key_scalar_to_list` 丟 `ValueError`(delta 內),由 dispatcher 既有的 `except (ValueError, RuntimeError): print(f"擋下:{e}")`(`scripts/lumos:24680-24682`)統一接住,跟 `edit_fm_append`/`edit_fm_remove` 既有的 `raise ValueError` 走同一條路。判定:兩種寫法都各自跟自己所在函式的既有慣例一致,對齊。
3. 第二種做法:`_about_code_path` 算 repo 根直接呼叫既有的 `_vault_repo_root(env)`(`scripts/lumos:5476`,本輪未改),沒有另開一套。`_list_key_scalar_to_list` 只重組 `TOP_KEY_RE`/`fm_structure`/`fmt_list_item`/`strip_quotes` 這些既有原語,其「單一值視為一項清單」的規則明文對齊讀側既有的 `as_list()`(`scripts/lumos:370-375`,本輪未改),不是新發明的第二套「什麼算清單」規則。判定:沒有引入第二種做法。

不對齊共 0 條,其中 major 0 條

總結:最高 severity minor,blocking 共 0 條
