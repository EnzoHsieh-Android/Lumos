severity: major

我只讀了材料和 `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos`,沒有跑會寫檔的指令。

**Finding 1**
severity: major
blocking: 是 — 專案已有一套「逐檔去行號、雜湊 hunk 內容」的 diff 正規化,設計卻在 `scripts/lumos` 內另寫第二套同用途的做法,而且沒有說明為什麼不用既有那套。
引句:「切成逐檔,每檔去掉 `index` 行、把 `@@ -a,b +c,d @@` 的數字換成固定字樣,其餘每一行(含空白、含上下文行、含檔頭的路徑)原樣雜湊。」
對照:
- `scripts/lumos: `scripts/lumos:25875`(`_patch_file_changes`)。
- 它的規則:吃 `git diff` 文字,逐檔切出 `{檔名: sha256}`。
- 它的規則:不算行號,但算 `@@` 後的段落標頭和上下文行。
- 它的規則:去掉文字檔的 `index` 行。
- 它的規則:對二進位、mode、rename 另有處理。
- 它的規則:引號路徑用 `_git_unquote_path`(`scripts/lumos:25851`)解開。
- 它的 docstring 寫明這是 rebase 後仍視為「同一版改動」的指紋。
- 計劃 PRIOR-ART 只比了 `git patch-id`,沒提這支。

判定理由:
- 兩套正規化會各自演化,例如二進位、改名、引號路徑、段落標頭要不要算。
- 設計沒有交代這些差異,最後會出現「資安席指紋認得、回頭重讀指紋不認得」的歧義。
- 該做的是讓每檔改動指紋直接呼叫或抽出 `_patch_file_changes` 的核心,並在 PRIOR-ART 說明差異(例如空白一律保留)。
- 要自寫就得寫出不重用的理由。

**Finding 2**
severity: minor
blocking: 否 — 只是組 diff 參數的第三套,不影響行為。
引句:「再加 `--literal-pathspecs --no-renames --diff-algorithm=myers --inter-hunk-context=0 -U3`」
對照:
- `scripts/lumos: `scripts/lumos:32109`(`_ns_diff`)已把 `--inter-hunk-context=0 --diff-algorithm=myers` 等釘死成筆記閘的共用 diff。
- `scripts/lumos: `scripts/lumos:36005`(`_NOTE_REREAD_DIFF_ARGS`)與 `scripts/lumos:36216` 是給判定者的組法。

判定理由:同一檔案內已有兩組「釘本機 diff 設定」的參數。計劃沿用後者再自加,是第三組,要是 `_NOTE_REREAD_DIFF_ARGS` 日後改了,指紋參數可能漏跟。建議把釘死的參數集中一處,或明講為何不用 `_ns_diff`。

**Finding 3**
severity: minor
blocking: 否 — 分岔點沿用 `_codeloop_default_base`,方向是對的,但有兩個未交代的地方。
引句:「現有唯一的呼叫點(代碼審判定在沒給範圍時)傳 HEAD,行為不變;引用它的測試一起檢查。」
對照:
- `scripts/lumos: `scripts/lumos:50959`(`_codeloop_default_base`)讀目前簽出的分支來決定遠端。
- 唯一的程式呼叫點在 `scripts/lumos:51024`。
- `scripts/test_lumos.py:37263` 起有多個直接以單參數呼叫它的測試。
- `scripts/lumos:47181` 的 `_lens_push_base` docstring 與 Issue `Issues/推送前其他閘的範圍在合過主線時會多算` 記載了主線判法收斂的路。

判定理由:
- (a) 改成 `for-each-ref --points-at <頂端>`,在「恰好一條但不是目前簽出」時,選到的遠端會跟現況不同(現況永遠看簽出分支),「行為不變」只在零條或多條退回時成立。最好寫成預設參數,並補一支針對這種分支形狀的測試。
- (b) 同一個 check 指令裡,候選用 `_lens_push_base` / `_push_range_start`,指紋用 `_push_mainlines` 這一套。計劃有回應舊否決理由,但沒有把這個新呼叫點登記進該 Issue 的收斂清單。若日後收斂改用 `_push_range_start`,這個使用者會被漏掉。

判定理由補充:`_mainline_ref`(`scripts/lumos:47409`)是第四套,計劃不碰它,不扣分。

**Finding 4**
severity: minor
blocking: 否 — 快取位置本身對齊,只是逾時語意有出入。
引句:「組 diff 那次 git 逾時(`_lens_git` 預設 20 秒)」
對照:
- `scripts/lumos: `scripts/lumos:36061`(`_note_reread_scan`)用 `deadline` 與 `_NoteRereadStop` 控制整體預算。
- `_ns_git`(`scripts/lumos:32100`)把逾時和 git 失敗一律吞成 `None`。

判定理由:
- 逐檔快取放進 scan dict 並讓 check 與 prepare 共用,和現有慣例一致,沒問題。
- 但計劃把單次 git 逾時直接退回 `v1`,現有路徑在逾時時走 `_note_reread_fail(deadline, …)` 並丟 `_NoteRereadStop`。
- 實作時要說清楚「新指紋這次 git 逾時」是退回 `v1`,還是算入整體 deadline 後中止,別讓兩條路徑各自吞錯。

不對齊共 4 條,其中 major 1 條(Finding 1:自寫第二套 diff 正規化,沒重用 `_patch_file_changes`)。
