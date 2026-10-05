severity: minor

審查方式:diff 全文逐 hunk 讀完。實驗都在 /private/tmp/claude-501/rv2b 與 rv2c(臨時目錄,假 git 與直接載入 scripts/lumos),沒改 repo,沒跑任何會改設定的 claude plugin 子指令(只看了 `claude plugin uninstall --help`)。

### F1 prune 的 rmtree 失敗被接住了,但同一場會談的舊歷史仍已被刪掉一半
severity: minor
blocking: 否 — 只動可再生的診斷帳、只在手動 prune 剛好撞上續用中的舊會談時發生,而且已有回報。

hunk:`_events_prune`。
引句:「寫入端同時在寫:檔案可能剛出現或剛被改名」
問題:r1 F1 的修法是把 rmtree 包進 `except OSError`,traceback 沒了,但 rmtree 是逐檔刪,失敗當下舊塊檔已經刪光。
時序→結果:
1. 會談 B 閒置超過 N 天,mtime 是舊的。
2. prune 通過 newest 檢查,開始 rmtree,先把舊塊檔刪光。
3. 外掛在 rmdir 之前寫入 9-new.jsonl。
4. rmdir 回 ENOTEMPTY,B 被記入 failed,輸出「沒刪掉 1 個(權限或正在寫)」。
5. B 只剩新塊檔,續用前的歷史永久消失,而且訊息沒說明那一場已被刪掉一半。
同型:newest 檢查與 rmtree 之間沒有再驗一次,這段空窗內才寫入的新塊檔,若在 rmtree 掃描之前出現,也會被一起刪掉(同一個根因,沒另外重現)。
重現(rv2c/t.py,用 monkeypatch 在 os.rmdir 前寫入新塊,時序是人為指定的):
```
([], ['B'])
['9-new.jsonl']
```
佐證:file: `scripts/lumos:21890`(`_events_prune` 本體,行號為 diff 套用後的大致位置)

### F2 enforcement 新增的 git 呼叫沒帶逾時,實際上限是 20 秒,不是 r1 報告寫的 3 秒
severity: minor
blocking: 否 — 要 git 在這個子指令上卡住才發生,而且既有的 `git config core.hooksPath` 已有同型 10 秒風險;但新呼叫把天花板往上疊。

hunk:`_events_root`,被 `enforcement_status` 的 ⑪ 列呼叫。
引句:「git-common-dir 是名叫 .git 的資料夾時取上一層;git 失敗、逾時、找不到都退回 root。」
問題:`_events_root` 用預設逾時的 `_lens_git`,預設是 20 秒(file: `scripts/lumos:41812`)。開場 hook 內層預算約 7 秒(file: `scripts/hooks/claude/lumos-entry-hook.py:256`),超時就整支 enforcement 被殺,回 None。
時序→結果:
1. 開場 hook 跑 `lumos enforcement --json`,事件帳所在的檔案系統或 git 卡住。
2. ⑪ 列的 `rev-parse --git-common-dir` 卡 15 秒(假 git:遇到 git-common-dir 就 sleep 15)。
3. 整支 enforcement 共 16.4 秒(`time` 實測),遠超 7 秒預算。
4. hook 那端逾時,所有層(含和事件帳無關的 hook、pre-commit 等)的掉線提醒一起靜默消失。
重現:rv2b 裡以假 git 包 PATH,在空 git repo 跑 `lumos enforcement --json`,total 16.443s。
佐證:這一列的設計宣稱是只看資料夾時間、不呼叫外部指令(`_ledger_note` 上方註解與測試 t_enforcement_ledger_row 的說明),實際多了一次 git 子行程。

### F3 兩支 install 同時跑時,重查只做一次、沒有等待,後到的一支可能誤報「沒裝好」
severity: minor
blocking: 否 — 只影響訊息(install 回傳碼不看這一步),最終狀態由先到的那支完成。⚠ 真 claude 的並行行為沒驗證(只准 --help),此條是由程式結構推出來的。

hunk:`_sync_claude_plugin` 的 add、install 兩處重試。
引句:「另一支 install 同時跑、先加好了:以最終狀態為準」
問題:r1 F3 的修法是 add 或 install 失敗後立刻再查一次清單。但先到的那支還在寫入中時,清單還看不到它的結果,立刻重查仍是空的,於是重新丟出原錯誤。
時序→結果:A、B 同時跑;A 持有 claude 內部的鎖或正在寫入,B 的 add 回錯;B 立刻 list,A 尚未寫完,看不到市集;B 印 `⚠ Claude 事件帳外掛 ... 沒裝好`;片刻後 A 完成,實際狀態是對的。使用者被誤導去「修好原因後重跑」。
補充:同一函式最壞耗時為 6 次子行程各 30 秒上限,約 180 秒,仍沒有總預算(在 install、update、init 路徑,不在開場 hook;grep 沒找到開場 hook 會呼叫 install)。

### 前輪修復驗收
- r1 併發 F1(prune 與寫入同時):traceback 已修好(rmtree 失敗會被收進 failed 清單,後面的會談繼續處理);殘留的半截歷史見上面 F1。讀端 `_events_read` 的 read_text 與 `_events_prune` 的 stat 迭代已各自接了 OSError;`_events_sessions` 的排序 key 本來就接了。
- r1 併發 F2(先移除再加失敗):`removed_old` 旗標加上了「舊的市集登記已移除、新的沒加上」提示和「重跑 lumos install --force」,但仍只印到 stderr、不附像 teardown 那樣的手動指令。算修好,沒引入新洞。
- r1 併發 F3(兩支 install):加了「失敗後再查一次」的最終狀態判斷,邏輯上對 add 與 install 都成立(重查通過才當成功,未通過才重新丟出原錯誤);限制見 F3。
- r1 併發 F4(列表讀光塊檔、每個會談各一次 git):`_events_read` 現在可接 `base=`,不再每個會談重跑 `_events_root`,git 子行程已降到每次列表一次;但仍是讀完整塊檔,記憶體隨單一會談大小線性增長(只在手動指令,未另列)。r1 報告說 git 逾時上限 3 秒,實測是 20 秒,見 F2。
- 新引入的檢查:`_claude_json` 對 null、物件、數字、非 dict 元素一律丟 RuntimeError;`_sync_claude_plugin` 與 `_teardown_claude_plugin` 都攔下 RuntimeError、ValueError、OSError、TimeoutExpired,`UnicodeDecodeError` 是 ValueError 子類所以也被接住。這幾條時序下沒找到崩潰。
- 測試執行器隔離:`LUMOS_SKIP_CLAUDE_PLUGIN=1` 與清掉 CLAUDE_CONFIG_DIR 在 `_isolate_environment` 內,沒找到繞過口;假家目錄本身也會讓真外掛操作落在假 HOME。

### 圖譜鏡頭(固定席逐條)
- `Issues/code-loop守衛main-direct盲區.md`:不影響。它只牽連審查卷證路徑,本 diff 不動 code-loop 閘或 main-direct 判定。
- `Systems/lumos-cli-read.md`(★INVARIANT★ 針對 search 預設排除 superseded):不影響。本 diff 未動 search 與 supersede 濾網。
- `Systems/每支檔有家.md`、`Systems/筆記內容閘.md`:不影響。沒新增檔,新函式都在已有家的 scripts/lumos 裡(S8 到 S10 的家歸屬需要補寫圖譜,但不是併發問題)。
- `Systems/design-loop.md`(★INVARIANT★ 處置閘第五步)、`Systems/lumos-cli-lifecycle.md`(★INVARIANT★ re-inject 只覆蓋 sentinel 之間):不影響。我讀過的 `cmd_uninstall` 與 `_sync_global_hooks` 新增的是外掛呼叫,沒動注入或 sentinel 區塊。
- `Systems/loop-convergence-recording.md`、`Systems/pitfalls-code-loop.md`:不影響。僅牽連 scripts/lumos 與輪替游標,本 diff 沒碰收斂記帳。
- 其餘「超出上限只列名」諸筆(bound-tests-gate、guard-kill、授權與歸屬、測試假綠形態、lumos-deinit、reversibility-governance-ledger、anchor-integrity、check-r-guard、check-t-sentinel、cochange-guard、lumos-refcheck、slim-install-安裝器 等):這輪沒逐篇打開,只憑名稱與本 diff 範圍判斷。例外只有 lumos-deinit 與 slim-install-安裝器、slim-uninstall-一行卸載:`cmd_uninstall` 現在多了外掛移除,這幾篇如果寫著 uninstall 只拆 symlink 與 skills,會落後一步(⚠ 沒打開驗證)。
- 表態記錄 py-eventloop na:同意,diff 沒有 async 程式。

總結:最嚴重 minor,blocking 0 條
