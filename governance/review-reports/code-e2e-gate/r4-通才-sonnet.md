severity: minor

這份修補沒有帶進會擋實作的新問題。我找到 4 條 minor,都不擋實作。

我跑了 `python3.14 scripts/test_lumos.py -k android_e2e`,結果 601 passed、0 failed。鎖檔 `.warming` 在我檢查時不存在,沒有動它。實驗用的臨時目錄已用字面絕對路徑刪掉。

1. 太大的紀錄被算進「沒讀的份數」後,`--ack` 與 doctor 的說明講錯原因,而且怎麼重跑都消不掉
severity: minor
blocking: 否
引句:「print(f"注意:另有 {unread} 份沒讀(讀超過 60 秒),那幾份這次沒標;再跑一次這個指令", file=sys.stderr)」
file: `scripts/lumos:41821`(`_e2e_waive_ack`)、`scripts/lumos:41871`(`_e2e_ai_pending_all`)、`scripts/lumos:4163`(doctor 的 AE 段)
失敗場景:
- 修補在 `_e2e_ai_pending_all` 與掛鉤的 `if path is None:` 裡加了 `unread += 1`,單份超過 2MB 的紀錄現在會算進 unread。
- `--ack` 的提示固定寫「讀超過 60 秒」並叫人「再跑一次」。這份檔永遠不會被讀,重跑沒有用。
- doctor 的說明只列「超過 500 份或讀超過 3 秒」兩種原因,沒有「單份太大」。
- 這份紀錄裡待看的 AI 放行既標不掉,`waive --list` 也只把它列成「紀錄讀不懂」。
重現:建一份 3MB、含一筆未看 AI 放行的紀錄,先把 `_confirm_tty` 換成回傳 True,再呼叫 `_e2e_waive_ack(root, [], True)`。
- 實際輸出:「注意:另有 1 份沒讀(讀超過 60 秒)…」,接著「沒有還沒人看過的 AI 放行。」,回傳碼 0。
- `_e2e_ack_targets` 回的是 `([], 1, None)`。
修補前這份檔被靜默略過,doctor 也不會為它出警告,所以多出來的提醒是這輪新增的。
歸因:有證據的修復回歸。兩版查證:修前沒有 `unread += 1`;修後我實際跑出上面的輸出。

2. 歸屬與範圍的前綴查表,在「功能路徑和改動檔都很深」時仍是平方工作量
severity: minor
blocking: 否
引句:「pre = seg if pre is None else pre + "/" + seg」
file: `scripts/lumos:40667`(`_e2e_prefixes`)
失敗場景:
- 修補把前綴層數限在 `maxd`。如果設定本身就有一條 10000 層的功能 path,`maxd` 就是 10000,每支深檔仍要逐層組出整串字串,再整串雜湊。
- 實測 50 支深一萬層的檔,對一條 10000 層的 path 花 1.8 秒,約每支 36ms。
- `--changed` 若有上千支這種檔,就會花約 36 秒,吃掉 60 秒預算的大半。
- 測試 `t_android_e2e_scope_perf` 只用 `app/src/main` 這種淺 path 配深檔,沒蓋到這種組合。
重現:`feats={"a":{"paths":["app/"+"/".join(["d"]*10000)],"cases":{}}}`,取 50 支深度 10000 以上的檔,呼叫 `_e2e_owners`,量時間。
歸因:有證據的修復回歸,只修了一半。原本的逐層 join 是整檔深度的平方,現在降成設定最深 path 的平方。

3. 「主線的驗收要求比這一版新」的判斷分不出「主線新」和「這一版自己改弱」
severity: minor
blocking: 否
引句:「if _e2e_canon(ml[1]) != _e2e_canon((sel_full or {}).get("e2e")) or _e2e_mem_canon(ml[0]) != _e2e_mem_canon(sel_full):」
file: `scripts/lumos:41723` 附近(`_e2e_gate_full_note`),訊息在 `scripts/lumos:66895` 附近(`_cl_say_e2e_block`)
失敗場景:
- 分支自己把某條 flow 從 `e2e.flows` 拿掉(檔還在),整套紀錄的 `ran` 就少那條,算出 miss。
- 這時 `mainline_newer` 會被設成 True,擋下訊息印出「git merge <主線>」。
- 三方合併會保留分支這邊的刪除,合進去補不回;照這一版的設定重跑也補不到。
- 使用者照指示合了也還是被擋,真正要做的是把設定改回去。
- 計劃自己在 `removed` 那條已承認「三方合併保留這邊的刪除」,這條判斷沒套同樣的區分。
重現:未能實跑,是靠讀碼推出的。條件是分支設定比主線少一條 flow,兩邊設定的 canon 不同,而 `_e2e_runs_missing` 非空。
歸因:有證據的修復回歸。修前沒有這個分支,不會印合併提示。

4. 範圍判斷的設計說明與狀態:docstring 過期,第四項與第三項重複存狀態
severity: minor
blocking: 否
引句:「"""指紋範圍的三組路徑 → (app_dirs, exclude, 驗收素材);_e2e_scope_hit 與算指紋時給 git 的 pathspec 共用。"""」
file: `scripts/lumos:40612`(`_e2e_scope_dirs`)、`scripts/lumos:40625`(`_e2e_scope_hit`)
失敗場景:
- 現在回傳四項,docstring 還寫「三組」。
- `_e2e_scope_hit` 解包時把第三項丟成 `_mats` 不用。
- 第三項的 flows 清單和第四項的 `fset`、驗收素材目錄各存了兩份。
- 之後有人改其中一份,另一份不會跟著動。
- 第三項只剩算指紋的 pathspec 還在用(`dirs[2]`)。
歸因:有證據的修復回歸,只增加維護成本,沒有行為差異。

## 其他檢查

跨檔追蹤的結果:
- 沒有漏改的呼叫者。`_e2e_scope_dirs` 與 `_e2e_owner_index` 的所有呼叫都把回傳值整包傳下去,只有 `dirs[0]`、`dirs[2]` 會取單項,沒有解包三項的地方。
- `_e2e_ack_targets` 只有 `_e2e_waive_ack` 一個呼叫者,已改成三項。
- `_e2e_ai_pending` 的呼叫者在呼叫前已先過 `_e2e_record_err`,所以 `(rec or {}).get` 不會遇到非字典。
- `e2e-coverage` 分支(HEAD `d22636fd`)的 `_e2e_coverage_report` 只把 `dirs` 與 `index` 當不透明物件傳給 `_e2e_scope_hit` 和 `_e2e_owners`。`_e2e_scope_dirs(e2e)[0]` 取第一項,新舊形狀都相容。
- `_e2e_ai_pending_all(_aer)` 用預設參數。我讀了那份 `scripts/lumos`,沒發現會接壞;兩分支同改同一批函式,文字層會有合併衝突,執行層相容。

被刪掉的行為:
- r2 的逐點 `_esc_clean` 沒有被刪(補丁裡沒有任何 `-` 開頭含 `_esc_clean` 的行),出口只是再多清一次。
- `_e2e_record_files` 舊的份數上限,在預設參數下語意不變。
- `bad_record` 不再一律為真,改成 `"git" not in rerr` 的字串比對。這是跟錯誤訊息文字綁死的脆弱寫法,但目前判得對。
- `_e2e_ai_pending` 舊實作改成呼叫 `_e2e_ai_pending_one`,對已通過 `_e2e_record_err` 的紀錄,計數結果等價。

## 三問

派工詞寫了「回答三問」,但沒列出是哪三問。以下是我照上下文推的三問,若不是這三個請告訴我。

1. 修補有沒有帶進新問題?有,四條,都是 minor。
2. `e2e-coverage` 分支接到這一版會不會壞?不會。呼叫處只做不透明傳遞,相容。
3. 被換掉的行為有沒有補回?補回了。逐點清理沒被拿掉,份數上限在預設參數下語意不變。

最高等級 minor,擋實作的 0 條。
