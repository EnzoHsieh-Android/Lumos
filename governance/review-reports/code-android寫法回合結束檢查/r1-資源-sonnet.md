severity: major

審查範圍是 `scripts/lumos` 的工作樹模式與兩個鉤子(`stop-lint-hook.py`、`_hookshared.py`)。我在 `/tmp` 底下用 `git clone --shared` 複製出 41f1b9abc,造了一個有 3000 支 `.kt` 的專案,用假的 `ast-grep` 實跑。完成後已刪除我自己的臨時目錄(`/private/tmp/lumos-seat-work/code-android寫法回合結束檢查/資源-sonnet`)。沒有動 repo,沒有留下 gctl-run-*。

**F1 刪掉大量已追蹤的大檔,會把它們整份從 HEAD 讀進記憶體,哪怕這些檔根本不是程式碼**

`_lint_wt_pairs` 把 `deleted` 全部丟給 `_lint_wt_blobs`,用 `git cat-file --batch` 一次讀回。但 `deleted` 只在「新增檔配對同名刪除檔」時才用得到,而且 50 支上限的判斷在讀完之後才做。
- 實測:HEAD 追蹤 200 個 5MB 的 `assets/*.bin`(共 1GB),整個資料夾刪掉後跑 `lint-new --worktree`。
- 結果:耗時 8.99 秒,最大常駐記憶體 3,984,146,432 位元組(約 4GB),最後只回 `no-files`,什麼都沒檢查。
- 對照:同一個專案只改 3000 支 `.kt` 是 1.9 秒。
- 影響:記憶體約為被刪資料量的 4 倍。刪 3GB 的 `jniLibs` 或 vendor 資產,就會超過鉤子內層 21 秒而被收掉,也有被系統因記憶體不足收掉的風險。
- 重跑:每回合都重做,因為沒有任何快取,直到使用者提交為止。

引句:「blobs = _lint_wt_blobs(repo_root, [p for _x, _y, p, _o in touched] + list(renames.values()) + deleted)」
file: `scripts/lumos:40304`(複本裡的行號;材料是 `r1-snapshot-甲.patch` 的 + 行)
severity: major
blocking: 是

**F2 回合中新增檔名含空白的檔案,`_lint_wt_blobs` 會例外崩潰,整回合的寫法檢查靜默失效**

HEAD 裡不存在的路徑,`cat-file --batch` 輸出的是 `HEAD:My File.kt missing`,切詞後剛好是三個詞。程式把它當成「樹或其他物件」,執行 `int(b'missing')`。
- 實測:新增 `src/My File.kt` 後跑,出 Python traceback:`ValueError: invalid literal for int() with base 10: b'missing'`,exit code 1。
- 鉤子端:exit code 1 但沒有 JSON,鉤子直接 `return 0`,沒有任何提示。
- 影響:那一回合改的其他 `.kt` 也全部不檢查,而且看不出來。這不是資源問題,但它是這段新程式的崩潰路徑,屬於作者沒看到的 bug。

引句:「elif len(head) == 3:              # 樹或其他物件:跳過內容」
file: `scripts/lumos:40272`
severity: minor
blocking: 否

**F3 50 支上限在讀 HEAD 內容之後才判斷,有大量未追蹤的程式檔時前置成本跟著檔數線性長**

`ents` 全部列出後,每一筆都做 stat,再把所有 `touched` 路徑丟給 `cat-file --batch`,最後才判斷 `len(pairs) > _LINT_WT_MAX_FILES`。
- 實測:未被 ignore 的 `build/` 底下放 10 萬個副檔名被判成程式檔的未追蹤檔,總耗時 13.8 秒;其中 `cat-file --batch` 對 10 萬個 missing 路徑單獨就要 10.4 秒。最後只回「超過 50 支」,什麼都沒檢查。
- 規模:約每萬支 1 秒,要到十萬支以上才逼近預算,所以只列 minor。
- 重跑:每回合重跑一次。

引句:「if len(pairs) > _LINT_WT_MAX_FILES:」
file: `scripts/lumos:40335`
severity: minor
blocking: 否

**F4 lint-new 收到 SIGINT(或在工具執行中丟出未捕捉例外)時,已開出的工具程序群組不會被收掉**

只有 SIGTERM 有處理器。SIGINT 讓 `lint-new` 直接結束,`finally` 只做「從登記檔拿掉」,不殺群組。
- 實測:假 `ast-grep` 睡 300 秒,對 `lint-new` 送 SIGINT。`lint-new` 結束,`lintbase-*` 快照目錄由 `finally` 刪掉,但 `sleep 300` 的群組變成孤兒,繼續跑。`--pgid-file` 的登記也在 `finally` 被清空,鉤子之後想收也找不到這個群組。
- 範圍:鉤子只送 SIGTERM 和 SIGKILL,這條路徑只會在手動 Ctrl-C 或例外時走到。
- 已確認沒問題的路徑:鉤子逾時被 SIGTERM、工具自己逾時、鉤子 SIGTERM 時 `lint-new` 還在跑工具,這三條都收乾淨了,沒有孤兒程序,`.lumos/lintbase-*` 也被刪掉。

引句:「_lint_wt_unregister(proc)      # 工作樹模式:工具結束就從登記(含鉤子的登記檔)拿掉;其他模式是空動作」
file: `scripts/lumos:41015`
severity: minor
blocking: 否

總結:最嚴重是 F1(刪除大量已追蹤大檔時記憶體約 4GB、耗時 9 秒且每回合重跑),會擋 1 條;另有 F2、F3、F4 三條 minor 不擋。
