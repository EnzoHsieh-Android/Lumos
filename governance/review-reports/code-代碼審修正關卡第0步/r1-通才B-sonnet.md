severity: major

審查範圍:r1-part-b.patch(測試與夾具、手冊、速查、系統筆記、三篇 Issue)。在 `fcc-r1-work-通才B-sonnet/repo`(--shared clone)跑過 `-k fix_check`:82 passed、0 failed,所以正常環境下這批測試是綠的;下面是「把實作改壞、測試仍綠」與環境問題。

## F1 S12 第④條斷言恆真,拿掉「依賴連回主工作目錄的警告」測試照綠
severity: major
blocking: 是
引句:「"可能被樹裡的測試載到" not in r.stdout or "沒提交的改動" in r.stdout」
佐證行:file: `scripts/lumos:12032`(`notes.append("依賴資料夾連回主工作目錄,上面那幾支沒提交的改動可能被樹裡的測試載到")`)
1. 該斷言是「A 不在輸出 或 B 在輸出」。同一個場景(③已經讓主工作目錄設定檔有沒提交改動)輸出一定含「沒提交的改動」(`dirty_paths` 那條 note:「這次驗的是提交裡的版本,工作目錄這幾支沒提交的改動不算」),所以右邊恆真,左邊的警告字樣有沒有印都過。條款 S12 最後一句「主工作目錄有沒提交的改動又連了依賴時應印警告」實際沒被釘住。
2. 最小重現(只改我的 clone):把 `scripts/lumos` 裡 `notes.append("依賴資料夾連回主工作目錄,…可能被樹裡的測試載到")` 換成 `pass`,跑 `/opt/homebrew/bin/python3 scripts/test_lumos.py -k fix_check_tree_setup`,輸出 `5 passed, 0 failed`(全綠)。
3. 修法:斷言改成 `"可能被樹裡的測試載到" in r.stdout`,並補一個 `link_deps: false` 的對照(同樣主工作目錄不乾淨)斷言不印。

## F2 條款說了、測試沒驗到:至少四處拿掉實作測試照綠
severity: major
blocking: 是
引句:「(root / ".maestro").mkdir()」
佐證行:file: `scripts/lumos:12003`(平台根釘不住版本的判斷)、`scripts/lumos:11823`(`_fix_item_repeat` 的 `>= 10`)、`scripts/lumos:12150` 附近(`bt.get("not_run")`)、`scripts/lumos:11790` 附近(`kind not in ("blob100644", "blob100755")`)
逐條對照,我在自己的 clone 各改壞一處、跑對應條款測試,結果全綠:
1. S2「平台根寫成絕對路徑、在 repo 外、是子模組…應印『釘不住版本』」:測試只造了一個「沒進版控的空資料夾平台 mae」。把 `unpinned[name] = "平台根在樹外…"; continue` 改成只 `continue`(樹外平台不再算釘不住),`-k fix_check` 全套 82 passed 0 failed;把 `k != "tree"` 改成 `k not in ("tree","commit")`(子模組當一般資料夾),也 82 passed。絕對路徑、repo 外、子模組、`root` 為 null 四種都沒測。
2. S6「兩欄都寫了(各至少十個字)」:測試的 prior 兩欄都遠超十字,沒有「只寫幾個字」的反例。把 `len(pr[k].strip()) >= 10` 改成 `>= 1`,`-k fix_check_repeat` 4 passed 0 failed。
3. S5「回 green 但有平台沒設 run_cmd 沒跑…應判不過」與「回 no-config 應判不過」:測試 ⑤ 的設定壞(沒有預設平台)在先決條件就回 2,走不到第 5 項的 no-config 分支;沒有任何測試造「平台沒 run_cmd」。把 `if bt.get("not_run"):` 改成 `if False:`,`-k fix_check_bound` 5 passed 0 failed。
4. S1「`at` 的檔是…符號連結」:測試只造資料夾(`tests:x`)。把 `if kind not in ("blob100644", "blob100755"):` 加上 `"link"`,`-k fix_check_record_complete` 14 passed 0 failed。
另外(同類、未逐一改壞):S1 的「迴圈編號含 `/` 或 `..`」只測輪次;S4「同一支測試多組輸入不算撞名」沒有測;S7「沒有 `docs/` 時印『這次結果沒記到帳』」測的是「帳路徑被換成資料夾」,不是沒有 `docs/`,而且「加了欄位型別後 `gov` 讀既有帳筆數不變」沒有任何斷言;S8 要求 `plant-canary`/`gate-pending`/`converged`/`cap-reached` 都印、`head_sha` 不是 40 碼十六進位時也印,測試只走一種 phase、沒造非 40 碼 head_sha(M4 實測:拿掉 `re.fullmatch(r"[0-9a-f]{40}", hs)` 後 `-k fix_check_reminder` 13 passed 0 failed)。
這些條款在計劃裡都綁了 `[test:…]`,綁定的測試卻拿掉實作不會紅,等於合約沒釘。
有抓到的對照(證明我的改法有效、不是沒跑到):S6「沒記個別嚴重度而最高只到 minor 不要求」與「兩組都是 other 不要求」改壞後各自翻紅(`③這輪最高只到 minor → 不要求`、`④兩組都是 other → 不要求` 變 ✗)。

## F3 夾具不清掉環境變數,繼承到 LUMOS_SKIP_BOUND_TESTS 時整批 fix-check 測試變紅
severity: minor
blocking: 否
引句:「e = dict(os.environ)」
佐證行:file: `.github/workflows/ci.yml:111`(CI 在 code-loop gate 那一步設了 `LUMOS_SKIP_BOUND_TESTS: "1"`,測試步驟沒設,所以 CI 目前不受影響);file: `scripts/test_lumos.py:8968`(同檔既有夾具都有 `e.pop("LUMOS_SKIP_BOUND_TESTS", None)`)
1. `_fc_lum` 照單全收呼叫端環境。我在 clone 跑 `LUMOS_SKIP_BOUND_TESTS=1 /opt/homebrew/bin/python3 scripts/test_lumos.py -k fix_check`,t_fix_check_bad_input、bound_tests_green、gov_event、listed_tests_green、tree_setup、loop_next_fix_check_reminder 共 6 支變紅(第 5 項在跳過時判不過,所有「過」的斷言都落空)。`LUMOS_SKIP_FIX_CHECK=1` 同理會讓本檔其他 fix-check 測試被短路。
2. 失敗方向是紅不是假綠,且 CI 測試步驟不設這個變數,所以只在開發者 shell 或將來有人把它提到 job 層時才出事。同檔既有夾具已經有清掉它的慣例,這裡漏了。修法:`_fc_lum` 開頭 `e.pop("LUMOS_SKIP_BOUND_TESTS", None); e.pop("LUMOS_SKIP_FIX_CHECK", None)`。
3. 其餘環境面我查過沒問題:git 只用 `git init -q` 加 `config user.*`,不依賴預設分支名;沒有寫死 macOS 路徑(`/private/...` 只出現在實作的 realpath 與註解);測試指令用 `python3`、`pwd`,Linux 可用;S11 ⑧ 用 `TMPDIR` 與 `utime`,跨平台。

## F4 手冊、速查、系統筆記、Issue 與主程式對照:未發現不一致
severity: minor
blocking: 否
引句:「回 no-config 判不過;有程式檔改名只印提醒、不因此判不過」
佐證行:file: `scripts/lumos:11640`(`_fix_dispatch_base` 讀派工單頂層 `base_commit`,與手冊「頂層加 base_commit」一致)、file: `scripts/lumos:11866`(`_fix_check_status` 與筆記「同一輪、紀錄指紋相同、之後只動簿記檔」一致)、file: `scripts/lumos:39634`(`_ran_count` 與 Issue「出現 `1 skipped` 字樣就判有跳過」一致)
1. 手冊的退出碼(0/1/2)、`LUMOS_SKIP_FIX_CHECK` 記 `skipped-env`、`--record-template` 骨架與 `--regression-set` 第 2 輪起帶,都跟 `cmd_loop_fix_check`、`_fix_check_template`、`cmd_canary` 的行為對得上。
2. 一個小處:筆記 S5 條款文字寫「`no-config` 判不過」,但實作裡設定壞(沒有預設平台)會先在第 0 層讀設定就回 2(測試 ⑤ 也是這樣釘),`no-config` 在第 5 項只剩罕見路徑;不算矛盾,只是條款字面與可達路徑有落差,併入 F2 第 3 點處理即可。這條不要求動作,記錄用。

最高等級:major,blocking 共 2 條
