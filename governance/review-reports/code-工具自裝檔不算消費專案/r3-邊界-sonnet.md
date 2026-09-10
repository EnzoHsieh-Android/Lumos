severity: major

### F19 about_code append 不認 Windows 反斜線路徑,合法檔案被拒
severity: major
blocking: 是 — 是本輪新增的路徑驗證邏輯,對一整類合法輸入永遠拒收,且與同一支函式家族的其他成員(`_about_code_norm`/`_is_vendored_path`)行為不一致
引句:「target = (root / v).resolve()」
`_about_code_path` 直接用使用者輸入的 `v` 與 `root` 相除再 `resolve()`,沒有先把反斜線轉成斜線;而同一輪新增的 `_about_code_norm`(`v = strip_quotes(str(value).strip()).replace("\\", "/")`)與既有的 `_is_vendored_path` 都有這一步。
實測:在乾淨 repo 對存在的 `src/a.ts` 執行 `lumos append about_code 'src\a.ts'` 回應「擋下:「src\a.ts」不是這個 repo 裡的檔案(找不到),檔案沒動」rc=2;同一 repo 用 `src/a.ts` 立即成功(rc=0)。file: `scripts/lumos:10904` `_about_code_path` 定義起點,對照 `scripts/lumos:10897` `_about_code_norm` 有做反斜線轉換。

### F20 about_code 大小寫檢查擋得住新增,但比對鍵不折大小寫,舊的錯字大小寫項目造成重複且刪不掉
severity: major
blocking: 是 — 造成 append 靜默寫出重複項、remove 對著存在的項目回報「找不到」給錯誤診斷,直接牴觸本輪 F15/F16/F17 三條要解決的「去重」目標
引句:「斜線統一、去 ./ 與 ..(純字面,不查檔案」
`_about_code_norm` 的比對鍵只正規化斜線與 `./`、`..`,沒有大小寫折疊;若筆記裡已有一筆舊資料(工具導入前手寫,或磁碟大小寫不敏感時被別的工具寫入)是錯字大小寫(如 `SRC/A.TS`),append 正確大小寫版本(`src/a.ts`)不會被判成重複,反而多插一筆造成同檔兩筆並存;之後想用正確大小寫 remove 掉原本那筆錯字大小寫項目,`edit_fm_remove` 用未折疊大小寫的 `link_target` 比對,直接回「沒有 src/a.ts…可能打錯字或早就不在了」——而那一項其實就在清單裡,只是大小寫不同。
實測:對 `about_code: SRC/A.TS` 的筆記 append `src/a.ts`(rc0,成功),結果檔案變成 `- SRC/A.TS` 與 `- src/a.ts` 兩筆;remove `src/a.ts` 只清掉新插的那筆,剩下的 `SRC/A.TS` 再 remove `src/a.ts` 回 rc2「沒有」。file: `scripts/lumos:10959` cmd_append 已經有訊息用的就是這個比對鍵;`scripts/lumos:10973` cmd_remove 同一套邏輯。

## 前兩輪修法驗收
F1:修到 — 改成精確檔名清單 `_VENDORED_ALL` 逐路徑比對,消費專案自己放在 scripts/hooks 的檔照樣被掃到、tier 仍變 high(乾淨 repo 實測驗證,claims 含該檔、tier=high)
F2:修到 — lint 命中在對齊判斷之前先用 `_is_vendored_path` 濾掉,對齊/未對齊兩條路都濾
F3:修到 — 刪除行那條路的 `_stack_changed_ok` 呼叫也帶入 `skip_vendored` 參數
F4:修到 — about_code 不再有 set 專用路徑,`about_code` 不在 `SCALAR_KEYS` 裡,`cmd_set` 一律擋下(讀碼+t_append_about_code_is_one_list_rule ⑧驗證)
F5:修到 — 絕對路徑與 `resolve()` 後跑出 repo 根的路徑都擋(含符號連結指向 repo 外的情形,實測驗證)
F6:修到 — about_code 只剩 append/remove 一套規則,舊的 set 專用分流已整個移除
F7:修到 — 隨 F6 一併移除,不再有 set 端未加引號寫壞欄位區的路徑
F8:修到 — 依 r2 三席既有判定(事故筆記文字類發現,程式碼側無法覆核)
F9:修到 — `_VENDORED_TREE_DIRS` 常數同時給 `_vendor_toolchain` 與 `_deinit_remove_vendored`、測試三處共用
F10:修到 — 舊的 `_set_about_code` 函式已整支移除,改用 `_about_code_path`,原本的命名/順序問題隨方案更換而消失
F11:修到 — `_stack_ext_counts` 對每個 dirpath 只算一次 `relpath`,不逐檔重算
F12:修到 — `_is_toolchain_repo` 判別鍵命中時方向仍是「不跳過」(掃更多而非更少),t_pitfalls_diff_ignores_vendored_toolchain ④ 釘住
F13:修到 — `_list_scalar_value` 判準改成「去引號後的值本身」,整串加引號、逗號前後多空白等繞法都擋下(多組寫法實測驗證)
F14:修到 — 值已存在時 `edit_fm_append`/`cmd_append` 皆提前 return 不改寫格式,訊息改講「已經有」
F15:修出新洞 — 原本「大小寫不敏感磁碟靜默收下錯字大小寫」已擋下,但配套的比對鍵沒做大小寫折疊,衍生出 F20 的重複/刪不掉問題
F16:修到 — `_about_code_norm` 正規化 `./`、`..`,append 前先用它比對既有值
F17:修到 — `cmd_remove` 對 about_code 用同一套 `_about_code_norm` 找回原始寫法再比對、刪得掉
F18:修到 — `t_license_headers_travel_with_vendored_files` 改用 `getattr(m, "_VENDORED_TREE_DIRS", ())`,不再另寫一份目錄清單

風險掃描清單那 1 條(scripts/lumos:17660,`\bopen\s*\(` 命中):誤報——命中位置是 `_stack_changed_ok` 函式 docstring 裡描述「命中 open(...)」的說明文字,不是真的 `open()` 呼叫。

總結:最高 severity major,blocking 共 2 條
