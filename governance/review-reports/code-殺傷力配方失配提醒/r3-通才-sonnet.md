severity: minor

# 第 3 輪 通才-sonnet:測試是否真的守住第 2 輪的 16 條修正

方法:在 `git clone --shared` 的臨時 clone(d219e935)對 scripts/lumos 做 28 種突變,每次突變前清 __pycache__,跑 `-k kill_recipe`、`-k guard_kill_rm`、`-k doctor_kill_recipe_drift`、`-k guard_kill_add_warns` 四組(基線 122/22/29/29 全綠)。突變腳本與完整輸出在 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/kcc-r3-work-通才-sonnet/`(mut.py、m_a.log、m_b.log)。

翻紅(測試守得住)的突變:ls-files 少 --error-unmatch、還原恆 True、`_kill_fs_fold` 反過來/只量大小寫/只量寫法、`_kill_alias` 對到多個挑一個與恆 None、`_kill_esc` 只認 Cc 與少 Cf/Zl、節點名佔位字拿掉、範本不擋控制字元、還原判斷搬到數原文前、new 檢查搬到數原文前、test 只收字串、NUL 不判、platform 清單不判、四個 git 子程序各自拿掉上限秒數與上限改 100、tree 讀不了不記住、設定檔讀不了只在部分情況回報、設定檔例外訊息不跳脫、`_kill_rel` 與 `_kill_show` 不跳脫。全部至少一組紅。

照綠(測試沒守住)的突變:M1、M16、M21、M22(見下);M18(`_kill_plat_top` 不快取)也照綠但只是多跑 git、結果不變,給不出失敗場景,不標 finding。

新測試 `t_kill_recipe_check_fs_and_git` 的 `subprocess.run` 替換:`real_sp.run = spy` 在 try 內設、finally 還原,全程 spy 只對 `cmd[:1]==["git"]` 記錄後原樣轉呼叫,不會漏還原、不改別的測試行為;`seen.clear()` 的位置也正確。不依賴本機檔案系統:別名格子是注入 `ctx["fold"]`;`t_kill_recipe_check_matches_guard_kill` 的 `ci/ni` 期望值是在 guard kill 用的同一種暫存資料夾量的,Linux(區分大小寫、不分寫法)下會走 `missing` 分支,邏輯上恆綠而不是恆紅;未在 Linux 實跑(本機只有 macOS),此點標未實測。

## F1 還原改用 HEAD 暫存索引這條修正沒有任何測試釘住:突變成工作目錄索引照綠
severity: minor
blocking: 否
引句:「env={**os.environ, "GIT_INDEX_FILE": idx}, timeout=_KILL_GIT_TIMEOUT)」
佐證行:scripts/lumos: `scripts/lumos:13102`(`_kill_restorable`)
1. 突變:`_kill_restorable` 的 `ls-files` 那次呼叫拿掉 `env={**os.environ, "GIT_INDEX_FILE": idx}`(即問工作目錄的索引)。四組測試 122/22/29/29 全綠,翻不紅。
2. 原因:所有對照格的工作目錄索引都等於 HEAD。差異只在「索引與 HEAD 不同」時出現。
3. 最小重現:在對照測試 cells 加一格 `("索引已移除但 HEAD 還有", dict(after=lambda r: _kr_git(r, "rm", "--cached", "-q", "prod.py")), "ok")`。原碼:判斷函式=ok、跟 guard kill 對得上(兩個都過);突變碼:判斷=unrestorable,而 guard kill 實跑 rc1 survived(判斷與實跑對不上,`81 passed, 2 failed`)。
4. 建議:把這一格補進 `t_kill_recipe_check_matches_guard_kill`(r2-intake 說這是「整類換掉」的核心修正,卻無對應突變格;「暫存索引不是工作目錄索引」正是它的存在理由)。

## F2 資料夾層級的大小寫別名(dirs 參數)沒有測試:不蒐集 dirs 照綠
severity: minor
blocking: 否
引句:「        ("大小寫不同、工作目錄另有沒提交的同名變體", dict(recipe_file="PROD.py",」
佐證行:scripts/lumos: `scripts/lumos:13084`(`_kill_alias` 的 `(*modes, *dirs)`)與 `scripts/lumos:13017`(`_kill_tree` 蒐集 dirs)
1. 突變:`_kill_tree` 裡 `for i in range(1, len(parts)): dirs.add(...)` 整段換成 `pass`。四組全綠。
2. 原因:別名格子都只測檔名那一層(PROD.py、café.py);單元格 `_kill_alias(ctx, ("wt",), name, modes, set())` 傳空 dirs。
3. 最小重現(macOS):加格 `("資料夾大小寫不同", dict(recipe_file="SRC/x.py", top_prod=False, files={"src/x.py": "LIMIT = 5\n"}), "unrestorable" if ci else "missing")`。原碼兩項都過;突變碼:判斷=missing、guard kill 實跑 error(revert 失敗),`81 passed, 2 failed`。
4. 在 Linux CI 上這格期望 missing、原碼與突變碼都過,所以只有 macOS/不分大小寫的檔案系統才會翻紅;單元格(注入 fold)補一格含資料夾名的 modes 即可不靠本機特性。

## F3 kill-rm 完整內容的 `_kill_esc` 沒有測試釘住:拿掉照綠(測試字元被 json.dumps 先跳脫了)
severity: minor
blocking: 否
引句:「check("⑥b kill-rm 輸出沒有原始控制字元、範本的 note 是佔位字", r.returncode == 0 and "\r" not in r.stdout and "\x1b" not in r.stdout」
佐證行:scripts/lumos: `scripts/lumos:13667`(`_kill_rm_show` 的 `_kill_esc(json.dumps(...))`)
1. 突變:`print("  " + _kill_esc(json.dumps(r, ensure_ascii=False, sort_keys=True)))` 改成不經 `_kill_esc`。`-k guard_kill_rm` 22 passed 0 failed。
2. 原因:`json.dumps` 會自己把 `\r`、`\x1b` 跳成 `\\r`、`\\u001b`;⑥b 只放這兩種,`_kill_esc` 有沒有都一樣。真正要靠 `_kill_esc` 的是 json 不跳的 C1(`\x9b`)、雙向覆寫 `‮`、行分隔 ` `。
3. 最小重現:把 ⑥b 的 note 改成 `"x\r lumos guard kill-add 假的 \x1b[K\x9b‮"`、斷言改成四個字元都不在 stdout;原碼綠、突變碼紅(`21 passed, 1 failed`,輸出裡看得到原始 `\x9b‮`)。
4. 同類:`_kill_add_warn` 例外訊息的 `_kill_esc(ex)` 拿掉也照綠(⑮ 的例外訊息只有 "boom")。r2 的 s3 修正宣稱「例外訊息都過 `_kill_esc`」,但沒有一格讓例外訊息帶控制字元。

最高等級:minor
