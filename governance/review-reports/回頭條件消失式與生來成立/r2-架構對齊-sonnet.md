severity: minor

(對照 repo:scratchpad/rw 的 scripts/lumos;以下行號都是該檔。)

## 四問總答

1. 分層與依賴方向:對。判定仍走 `_DriftProbeTree.one`(32344)、`_drift_probe_line`(32388),推送候選仍走 `_drift_probe_cond_candidate`(32430),`_drift_probe_one` 不動,跟既有四個鍵同一條路,沒有跨層直呼。往回查用 `_git_is_shallow`(5549)、`_nodehome_git`(26179)、`_nodehome_cat_blobs_capped`(26527)、`_drift_tree_env`(31639),跟守衛紀錄查轉正日期的先例 `_guard_pass_commit_date`(13620-13640,先判 shallow、再 `_nodehome_git log`、再逐版讀)同一個形狀。「同一條」認條件標記一模一樣,跟 `_drift_probe_old`(32562)的 `tuple(conds) in 標記集合` 一致。
2. 命名與錯誤處理:大體對,有 5 條 minor(見下)。
3. 第二種做法:沒有。spec 已明確不另開拆值函式(`_drift_cond_split` 依鍵切)、不用 `drift exam` 重放、不用 `-S`。往回查的歷史走法在專案裡本來就沒有 drift exam 那種可重用的單筆歷史工具(`_drift_exam_history` 35201 起是對主線每個提交跑 check,用途不同),用 git log 加批次讀跟 `_guard_pass_commit_date` 同型,不算第二種。
4. 落點:`Systems/存量漂移守衛`(responsibility 含 scan、about_code 含 scripts/lumos)放 WHY 合適;`Systems/筆記內容閘` 補反引號那一行也合適(同節點 29、30 行已有同類的 REVISIT 提交時規則 WHY)。不需另開。

**Z1 逾時寫法跟 `_nodehome_git` 的簽名對不上**
severity: minor
blocking: 否 — 結構對(走既有包裝),只是 spec 同時要求兩件現有函式做不到的事,實作時會被迫改共用函式或改直呼別支;不是第二種做法
引句:「走 `_nodehome_git`,`-c` 關掉外部差異與文字轉換的既有旗標,`--` 隔開路徑」「每個 git 呼叫的逾時取「剩餘預算」與既有 20 秒的較小值」
對照 file:`scripts/lumos:26179`(`_nodehome_git(repo_root, *args)` 沒有 timeout 參數,底下 `_lens_git` 預設固定 20 秒,`scripts/lumos:39854`);`scripts/lumos:5549`(`_git_is_shallow(root, timeout=)` 逾時會丟 TimeoutExpired,由呼叫端接,spec 沒講接)。要讓逾時受預算約束,要嘛改 `_nodehome_git` 多收 timeout(動到全庫共用的包裝),要嘛這段改直呼 `_lens_git(..., timeout=)`;spec 兩個都沒選。⚠ 判不準哪個才是專案慣例:`_drift_exam_history`(35201 起)與 `_drift_probe_changes`(32403 起,用 `_ns_git`)都是直呼底層。

**Z2 往回查用的路徑沒走「原樣 git 路徑」的先例**
severity: minor
blocking: 否 — 錯誤處理層級的缺口(NFD 存檔的筆記會查成「找不到」被標判不了),不是結構錯
引句:「這篇筆記改到它的提交清單用 `git log --format=%H <起點> -- <筆記路徑>`」
對照 file:`scripts/lumos:13607-13620`(`_git_paths_nfc`、`_guard_raw_git_path`:把 NFC 路徑換回 git 裡原樣的路徑再傳給 git log,守衛查歷史的先例);`scripts/lumos:32165-32185`(`_drift_cat`/`_drift_oids` 註解說明了 NFC/NFD 混用時用路徑讀會讀不到,專案為此用內容編號讀)。spec 的 `<筆記路徑>` 來自 `tenv.notes`,是 NFC 化後的相對路徑,直接當 `--` 後的路徑,macOS 上 NFD 存的筆記會得到空的提交清單。建議在 spec 寫明沿用 `_guard_raw_git_path` 或承認列入天花板。

**Z3 「帶字串路徑非一般檔」的問題文字放哪一層沒指明**
severity: minor
blocking: 否 — 結構上 spec 說「scan 列成問題」,但沒指到產生問題的那支函式,實作可能掉進通用的「判不了」文字
引句:「判不了,scan 列成問題「when-gone 帶字串時路徑要是一般檔」」
對照 file:`scripts/lumos:32630-32647`(`_drift_probe_row_problems` 專門放「file 指到資料夾」「symbol/test 路徑不像檔案」這類寫法問題,在評估前產生);`scripts/lumos:32758-32762`(`_drift_probe_scan` 裡 `tree.one` 回 None 時固定印「判不了(git 讀不出程式檔或筆記…)」,並用 `_drift_row_unread`(32535-32552)只認 `symbol/test`)。若 `one()` 對資料夾回 None,scan 會印錯原因;`_drift_row_unread` 也要加 `gone`(spec 只在「點名讀不出的檔」提到,沒列這支)。建議 spec 明寫:資料夾那條放 `_drift_probe_row_problems`,`_drift_row_unread` 對 `gone` 取路徑。

**Z4 born 標記的呈現位置跟 `prev_ack` 先例不同、往回查的呼叫點沒指明**
severity: minor
blocking: 否 — 欄位形狀(可省略的物件欄位)跟 `prev_ack` 一致是對的;不一致只在文字呈現與落點未寫
引句:「文字輸出那一行後面加標記;`--json` 的發現多一個欄位 `born`」
對照 file:`scripts/lumos:34940-34950`(`_drift_scan_print`:發現第一行是路徑加原文加「(已表態)」,說明在下一行縮排的 `why`,`prev_ack` 另起一行括號印,且已表態的只印第一行);`scripts/lumos:32760-32770`(`_drift_probe_scan` 沒有 root/sha,拿不到歷史,所以往回查只能做在 `cmd_drift_scan` 34893 起的後處理,spec 沒說放哪、也沒說用 `dict(f, born=…)` 附在發現上)。已表態的也要標,代表標記得放第一行;跟既有「說明放 why/括號行、已表態不印」不同,屬於新增一種呈現,應在 spec 說明為什麼不放 `why`(why 對已表態的不印)。

**Z5 值驗證與正規化目前各自 `rsplit`,spec 的「全部呼叫它」要一併列入改動**
severity: minor
blocking: 否 — 方向正確(收斂成一支,不是第二種做法);只是 spec 沒列出現存兩處重複的拆值要改,`gone` 的值驗證函式也沒命名
引句:「判定、預讀、候選篩選、正規化、值驗證全部呼叫它」
對照 file:`scripts/lumos:31929-31940`(`_probe_norm_value` 自己 `v.rsplit("::", 1)`)、`scripts/lumos:31948-31957`(`_probe_named_err` 自己 `rsplit`);現有 `_drift_cond_split`(32195)只被 32292、32315、32351、32437 四處呼叫。`_probe_named_err` 只給 symbol/test;`gone` 要有自己的驗證(不准反引號、空字串、`]`),spec 只描述規則沒說放進哪支函式(同一族 `_probe_value_err` 31910 的分支)。

不對齊共 5 條,其中 major 0 條
