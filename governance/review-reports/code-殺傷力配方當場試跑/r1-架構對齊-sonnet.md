severity: minor

# 架構對齊審查(架構對齊-sonnet席,第 1 輪)

審的是 `r1-code.patch` 裡 `scripts/lumos` 的部分(筆記、文件、測試只看有沒有引入新做法)。對照物是同檔鄰居。路徑相對 repo 根 `negguard`(其 HEAD 已含這份改動,行號以該樹為準)。

## 問 1:分層與依賴方向
單檔 CLI 沒有分檔分層,這裡的「層」指同檔裡的區段。新碼放的位置跟鄰居一致:kill 配方的新函式(`_kill_note_skipped`、`_kill_p2_survived`、`_kill_log_latest`、`_kill_file_changed_since`、`_guard_kill_pick`、`_kill_add_after_lock`、`_kill_add_try`)都接在既有 `_kill_*` 群裡;共用判法抽成 `_kill_norm_prefix` / `_kill_match_prefix` / `_guard_kill_rm_rows`,kill-rm 與 guard kill 兩邊都改成呼叫它們,沒有複製。`cmd_guard_kill` 加選用的 `result_out` 字典交回結果,跟同檔既有做法一致(file: `scripts/lumos:928`、`scripts/lumos:942`、`scripts/lumos:1091` 的 `_loop_status_disposal(..., result_out=out)`)。doctor P2 的第二個提醒照 P2 原有形狀:自己一個 try、warn_soft 只提醒、gov_events 加 `check-p2s` 並登記進 `_KNOWN_GATES`(file: `scripts/lumos:2958`,P2 原段)。讀殺傷力帳本走既有 `_backing_kill_rows`,沒另寫讀帳本的程式(file: `scripts/lumos:41459`)。
唯一要提的是修正關卡:`_fix_recipe_rerun_notes` 是修正關卡區段第一次直呼 `_kill_*` 私有函式,而且是第一處在這個區段裡讀筆記庫(`env.notes`、`env.vault`)。見 F1。

## 問 2:命名與錯誤處理
命名跟鄰居一致:`_kill_` / `_guard_kill_` 前綴、argparse 的 `dest` 用 `gk_` 前綴(`gk_try`、`gk_id`)、`id_prefixes` / `result_out` 是選用參數預設 None。錯誤走標準錯誤、前綴「擋下:」、回傳碼 2,跟 kill-rm 同;列出每條配方的清單在 kill-rm 印標準輸出(唯讀列表)、在 `_guard_kill_pick` 的擋下訊息裡印標準錯誤,方向對。doctor 兩段都用 `warn_soft` 並各包例外兜底,跟 P2 原有段一致。不一致的只有 kill-add 試跑後附加提示沒有照 `_kill_add_warn` 的「⚠ 提醒:」前綴,見 F2。

## 問 3:第二種做法
沒有引入新的讀帳本或跑 git 寫法:
- 單檔 diff 判改過沒:`_kill_file_changed_since` 用 `_lens_git` 加 `--literal-pathspecs diff --no-ext-diff --no-textconv --quiet`,跟 `_lens_git` 既有呼叫同一組旗標(file: `scripts/lumos:31729`)。kill 群自己的 git 呼叫是直接 `subprocess.run` 配 `_KILL_GIT_TIMEOUT`(file: `scripts/lumos:13973`),兩種寫法專案裡原本就並存,新碼選了其中一種,不算新增。`_lens_git` 加 `timeout` 參數預設 20,舊呼叫行為不變。
- 跳過規則:`_kill_note_skipped` 是把 P2 的逐字判斷抽出來、讓 P2、survived 清單、修正關卡共用,屬收斂。P 段本身(`scripts/lumos:2910`)仍有自己一份,是既有狀況,不是這份 diff 造成。
- 「每條配方取最近一筆」`_kill_log_latest` 跟 `_backing_judge_groups` 的取最新寫法不同,見 F3,是 ⚠。

## F1 修正關卡讀的是工作目錄筆記庫,其餘修正關卡驗的是提交裡的版本
severity: minor
blocking: 否
引句:「for r in _kill_read_recipes(env.vault / rel)[0] or []:」
佐證行:file: `scripts/lumos:12028`(同函式自己宣告「這次驗的是提交裡的版本,工作目錄這幾支沒提交的改動不算」)、file: `scripts/lumos:12055`(設定讀的是隔離樹 `tree`,不是工作目錄)
1. 同一個函式裡,平台設定 `pdata` 讀隔離工作樹(提交 head 那份),配方清單卻讀 `env.notes` / `env.vault`(目前工作目錄)。同一個函式內兩邊基準不同:設定是提交裡的、配方是工作目錄的。
2. 其餘修正關卡的驗證都以 head 提交為準,是這個區段的既有做法;新碼是區段裡第一個讀筆記庫的。⚠ 判不準:`changed` 本身就是 base..head 的提交差異,配方是「現在」的版本是否算合理取捨,設計審可能裁過;交編排者看計劃是否寫了這個基準。若要對齊,配方也該從 head 提交的筆記檔讀(`_fix_ls_tree` 一帶已有讀提交的函式)。

## F2 kill-add --try 的附加提示沒有照 kill-add 既有的提醒前綴
severity: minor
blocking: 否
引句:「print(f"這次試跑是弱證據(筆記還沒提交等),合約背書不採信;提交程式與筆記後跑 {again} 留一筆算數的",」
佐證行:file: `scripts/lumos:14224`(`_kill_add_warn` 結尾 `print(f"⚠ 提醒:{msg}", file=sys.stderr)`,同一個指令的標準錯誤提醒一律帶「⚠ 提醒:」)
1. 同一個子命令(kill-add)的非致命提醒,既有寫法是標準錯誤加「⚠ 提醒:」前綴;`_kill_add_try` 新增的三句標準錯誤提示(弱證據、survived、unattributed)沒有前綴,也不是「擋下:」。
2. 結構是對的(印標準錯誤、不改回傳碼),只是日誌風格跟鄰居不一致;使用者在同一次輸出裡會看到有前綴與沒前綴兩種提醒混著出現。

## F3 取「每條配方最近一筆」的規則跟背書那邊的取最新規則不同
severity: minor
blocking: 否
引句:「if r["recipe_id"] not in best or k >= best[r["recipe_id"]][0]:」
佐證行:file: `scripts/lumos:41431`(`_backing_judge_groups`:`latest = max(..., key=lambda r: str(r.get("ts") or ""))`,同 ts 取先出現的;covers 取檔內最後一筆 `groups[rid][-1]`)
1. 專案裡已有兩處「同一份 kill-log 對同一 recipe_id 取代表那筆」:背書的 `max(... key=ts)`(同 ts 取先出現)與檔內最後一筆;新的 `_kill_log_latest` 是第三種(比 ts、同 ts 取較後面)。
2. patch 自己的 docstring 說明了為何跟背書不同(背書判「這版任何一筆有 survived」),語意目的確實不同,所以標 ⚠ 判不準、不判 major。要看的點只有:同 ts 的 tiebreak 方向跟背書相反,是否有意。給不出具體失敗場景(同一台機器 ts 到秒,同 ts 兩筆機率極低),留給編排者決定要不要統一。

不對齊共 3 條,其中 major 0 條
最高等級:minor,blocking 共 0 條
