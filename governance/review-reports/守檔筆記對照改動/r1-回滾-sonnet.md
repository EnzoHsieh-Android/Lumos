severity: major

# 回滾-sonnet 設計審第 1 輪報告

## F1 指紋含 diff 全文,但 prepare 與 check 的範圍起點可能不同,提醒可能永遠消不掉
severity: major
blocking: 是
引句:「項目指紋 = (筆記路徑、筆記終點內容雜湊、給的 diff 全文雜湊、範本版本)的 16 個十六進位字雜湊。」
file: `scripts/lumos:26099-26151`
1. 指紋含「給的 diff 全文雜湊」,diff 由範圍起點決定。reread-check 走 `_push_range_start`,帶 `--push-remote`/`--pushed-ref`,上線點標記傳 `note-audit reread-check`。
2. prepare 是人手動敲的。spec 只說手動不帶那兩個參數時照 `_lens_push_base`,沒說 check 印出的 prepare 指令要帶同樣的 `--diff`、`--push-remote`、`--pushed-ref`。
3. 兩支起點函式在「合過主線、新分支首推、沒設 upstream」時會算出不同起點。程式註解 `scripts/lumos:34609-34622` 自己就寫了這件事。起點不同,diff 不同,指紋就不同。
4. `_note_audit_resolve` 的 mark 預設是 `_NOTE_AUDIT_GOLIVE_MARK`,見 `scripts/lumos:26133`。prepare 沒傳 mark 時,將來筆記內容審接線後會被截到另一個上線點,又多一個讓兩邊範圍不同的原因。
5. 後果:候選明明對照過、紀錄也提交了,reread-check 還是找不到同指紋的紀錄,每次推送重複提醒。〈實務隱患〉的「提醒後真的去對照的占比」與 RETIRE-IF 的「作者真的改掉的行數」會被這個假象污染。
6. 建議:spec 明寫 check 印出的 prepare 指令原樣帶 `--diff` 與 push 參數;prepare 也吃 `--push-remote`/`--pushed-ref` 並傳同一個 mark。加一條測試:同一份範本、同一批提交,prepare 與 check 算出的指紋相等,涵蓋合過主線的形狀。

## F2 抽共用函式時「頂端讀不到的丟掉」放進共用函式會改到嚴格模式的語意
severity: minor
blocking: 否
引句:「改名取新路徑、頂端讀不到的丟掉」
file: `scripts/lumos:25825-25872`
1. 現在的 `_notes_status_flipped` 對頂端讀不到的處理分兩種。非嚴格時 `tip_ok(None, None)` 為假,那篇被略過。嚴格時 `blob is None and strict` 回 None,整批算判不了,見 `_note_flipped_one`。
2. 如果「頂端讀不到的丟掉」寫進抽出來的共用函式,那 `_notes_status_flipped` 的嚴格路徑會靜默少掉判不了。今天存量漂移的兩個呼叫都帶 `only=` 從頂端樹篩過,所以碰巧看不出差別。但 S12 只寫「行為不變」,沒釘 strict、`deadline`、`git log` 失敗回 None 這三條。
3. 共用函式還得保留 `None` 的傳遞:git 失敗或逾時回 None,不可回空清單。少了這條,存量漂移那條路會把失敗當「沒碰過筆記」而放行。
4. 建議:共用函式只回 `git log` 撈出的 .md 路徑清單(含 None),過濾「頂端讀不到」留在 reread 呼叫端。S12 測試補 strict + `deadline` + git 失敗三個案例。既有測試 `scripts/test_lumos.py:52449`、`:52526` 用 `f.__globals__` 換掉 `_ns_git`,共用函式必須繼續走同一個模組全域名字。

## F3 推送前掛鉤「回傳值不看」跟同檔慣例(128 以上停下)與舊版 lumos 未知子指令的雜訊沒交代
severity: minor
blocking: 否
引句:「在存量漂移檢查那一段(逐 ref、帶 `--push-remote`、`--pushed-ref` 的那段)之後加一段,參數照它;回傳值不看。」
file: `scripts/hooks/pre-push:468-497`
1. 掛鉤裡既有的寫法是 `dr_rc=$?` 再交給 `pp_stop_if_signaled`:被訊號殺掉(多半是 Ctrl-C)時整支掛鉤停下,不往下跑約 8 分鐘的全套測試。reread 那段照字面「回傳值不看」,使用者在慢的 reread-check 上按 Ctrl-C,掛鉤可能繼續往下跑。
2. 版本偏斜:新掛鉤配舊 lumos 時(全域掛鉤由 `_sync_global_from_project` 同步,別的專案的 `scripts/lumos` 可能較舊,見 `scripts/hooks/pre-push:83`),`note-audit reread-check` 是 argparse 未知子指令,每次推送多印一段 usage 雜訊。不會擋。舊掛鉤配新 lumos 則沒人呼叫,無影響。spec 沒有寫舊版偵測或安靜略過。
3. reread-check 沒有時間預算。掛鉤在它後面才跑全套測試。第一次推送若起點是空樹,`git log --name-only -M` 掃全歷史,再加 `_nodehome_changes`,可能很慢;drift 有 `_DRIFT_BUDGET_SEC=60`,這裡沒有。
4. 建議:掛鉤沿用 `dr_rc` 與 `pp_stop_if_signaled`,只是不因 1 擋;reread-check 加預算,逾時走「這次沒提醒:逾時」回 0。

## F4 整案回退後留下的紀錄檔與「跟著 revert」的簿記豁免會讓舊版或回退後的代碼審留痕失效判斷誤判
severity: minor
blocking: 否
引句:「已提交的紀錄檔留著當歷史(不被任何東西讀)」
file: `scripts/lumos:37150-37162`
1. 「不被任何東西讀」不成立。代碼審留痕有效性在 `scripts/lumos:37161` 用 `git diff --name-only 記錄sha 目標sha`,只要所有檔案都在 `_BOOKKEEPING_FILES` 或 `_BOOKKEEPING_DIRS` 底下就放行。這個判斷會讀到 `governance/reread-verdicts/` 的路徑。
2. 場景一:實作被 revert(豁免項也跟著撤),但主線上仍有已提交的紀錄檔。之後有分支的 pass 留痕與推送頂端之間夾了「只加紀錄檔」的提交,判斷回「之後動了代碼」,高風險推送被擋。
3. 場景二:沒 `lumos update` 的協作者(舊 lumos 沒有這一項豁免)。他的分支上 pass 之後有人提交 reread 紀錄,他那邊的推送被擋。筆記內容審判定檔當初有同樣的形狀。
4. 五個消費者我在 `scripts/lumos` 對過:`:6581`、`:31250`、`:31262`、`:31349`、`:37161`。〈做法〉3 寫的五個成立。`:36203` 附近只列 `_BOOKKEEPING_FILES`,不是消費者,不受影響。`:5749` 的註解還寫「三個消費者」,是舊註解,不影響行為。
5. 建議:回退節改寫成「紀錄檔留著,豁免項一併保留一個版本」或明講會有前述過渡期擋推送,並附 `git revert` 之後的逃生做法(`code-loop pass` 重跑)。

## F5 候選交集沒說要做 NFC 正規化,中文筆記名在 NFD 樹裡會靜默變成空候選
severity: minor
blocking: 否
引句:「改到的程式檔的家 ∩ 這次被改過的筆記」
file: `scripts/lumos:25856-25858`
1. `_notes_status_flipped` 從 `git log --name-only -z` 撈的路徑原樣加進結果,只有 `only` 比對時才用 `nfc(p)`。`_nodehome_homes` 的鍵是 NFC 化過的。
2. 本 repo 的筆記幾乎都是中文檔名。git 樹裡若存 NFD 路徑(沒開 `core.precomposeunicode` 的環境、或 Linux CI 上 clone 的 mac 舊歷史),交集為空,印「這次沒有要對照的家筆記」、rc0,沒有任何錯誤訊息。存量漂移那邊是在呼叫端才 `nfc(...)`,見 `scripts/lumos:26900-26910`。
3. 建議:spec 在候選那句寫明兩邊都先 `nfc`;S1 補一個 NFD 路徑的案例。

## 其他鏡頭
- `_VENDORED_TREE_FILES` 加範本一項:已讀,無 finding。既有逐檔比對測試在 `scripts/test_lumos.py:11565`;`lumos update` 用 `scripts/lumos:18070` 的清單複製。範本必須是進版控的檔,S11 已覆蓋。消費專案在跑到新版 `lumos update` 之前沒有這支範本,沒人呼叫,無影響。
- 上線點標記與筆記內容審將來接線的互相干擾:已讀,只在 F1 第 4 點有問題。`note-audit reread-check` 不含子字串 `note-audit check`,`git log -S` 與 doctor `scripts/lumos:30481` 不會誤觸。`drift check` 上線標記(`scripts/lumos:26612`)不受新增的那段影響。
- 新增 `reread-` 系列子指令的說明表 `HELP_WHEN`(`scripts/lumos:38361`)與分派尾端(`scripts/lumos:39562`,不認得的子指令會落到 `cmd_note_audit_skip`):spec 沒提。argparse 有 choices,所以不會走到;分派的最後一行要顯式判斷 `reread-*`,實作時留意。屬實作細節,不算 finding。

最高等級:major;blocking 共 1 條
