severity: major

# r1 整合與接手鏡頭(整合-sonnet)

接手者視角:照〈做法〉逐項對 `scripts/lumos` 與 `scripts/test_lumos.py` 查證(repo 根 negguard)。多數項目未實測,依據是讀碼;最小重現寫在各條。

## F1 `--id` 的短身分到底在哪一層解析成完整身分,計劃前後講法對不上
severity: major
blocking: 是
引句:「CLI 由 `--id` 前段解析出來後傳入」
引句:「比對在合約片段過濾之後」
file: `scripts/lumos:14823`(cmd_guard_kill 簽名與讀配方、invariant 過濾在 14831-14841)
file: `scripts/lumos:43367`(dispatch 只傳參數,沒有讀筆記)
1. 〈範圍〉說 `ids` 是「完整身分清單」、由 CLI 解析前段後傳入;〈①〉卻說比對在「合約片段過濾之後」、「沒有配方可跑」判斷之前,且要印整篇配方列表、對到零條或兩條以上回 2。
2. 配方清單與合約片段過濾都在 `cmd_guard_kill` 內部才產生(`_kill_read_recipes(path)` 之後)。dispatch 層(`args.gcmd == "kill"`)手上只有 node 字串,沒有配方,解析不了前段。
3. 要同時滿足兩句,實作者只有兩條路:(a) dispatch 先自己 `env.find` 讀一次配方再解析,但就做不到「合約片段過濾之後」的比對,且 S1「跟合約片段一起給時兩個條件都要符合」的錯誤格式要在兩處重複;(b) 把前段原樣傳進 `cmd_guard_kill` 在內部解析,但那 `ids` 就不是「完整身分清單」,`--try` 傳完整身分時也就沒有「對到兩條」的可能。計劃沒選,接手者得自己猜,選錯會讓 S1「對到兩條不同配方回 2」只在其中一條路徑成立。
4. 最小重現:讀 `cmd_guard_kill` 第一屏,可見 `recipes` 只在函式內有。

## F2 P2 的「已列出問題」集合若照「不是 ok 的」實作,設定檔讀不了時 survived 清單會整個消失
severity: major
blocking: 是
引句:「`_kill_p2_one` 判出來不是 ok 的」
引句:「設定檔讀不了時這段照樣算(它不靠設定檔判對不對得上)」
file: `scripts/lumos:14008-14034`(`_kill_recipe_judge`:cfg_err 時對每條非畸形配方回 status "cfg")
file: `scripts/lumos:14213-14238`(`_kill_p2_one` 回傳 status 字串,不回身分,"cfg"/"noroot" 並不加 items)
1. `_kill_p2_one` 目前回傳的是狀態碼:ok、cfg、noroot、noplat、malformed、hits、missing…、error。
2. 設定檔壞掉時,每條字典型配方都回 "cfg",而且 `items` 只在 malformed/noplat/其他錯誤才加。照字面「不是 ok 的就放進集合」,cfg 與 noroot 的配方全進集合 → survived 清單全被跳過,與「設定檔讀不了時這段照樣算」直接矛盾;noroot(平台根找不到,只在彙總行「它底下 N 條配方沒驗」出現)算不算「已列出」計劃也沒講。
3. 另外 `_kill_p2_one` 不回完整身分,集合要由 `_kill_p2_scan` 自己用 `_kill_recipe_id(str(rel), r)` 算;「回傳形狀要怎麼改」計劃只寫了集合,沒寫誰算身分、cfg 與 noroot 歸哪邊。接手者得自己決定:建議只收「實際加了 items 且是針對該條配方」的(malformed/noplat/hits/missing/undecodable/path/error),cfg 與 noroot 不收。這個決定會改變 S3「原文已經對不上…不應重複列」的判準,需寫進計劃。
4. 最小重現:fixture 把 `.lumos/config.json` 寫壞、kill-log 放一條 survived,P2 會走 cfg_err 分支(`scripts/lumos:2955`)。

## F3 kill-log 讀法 `_backing_kill_rows` 回的行沒有配方的 invariant 與 file,計劃要的欄位拿不到
severity: minor
blocking: 否
引句:「取筆記那條配方的 `invariant`、經 `_kill_show`,不取帳檔那一行的」
file: `scripts/lumos:41079-41143`(`_backing_kill_rows` 回帳檔行;`_backing_note_recipes` 對回筆記配方後只把 `covers` 與 `note` 寫回行,沒帶 invariant、file、platform 欄)
1. 計劃把 `_backing_kill_rows` 當現成零件重用,但回來的行只含帳檔欄位加 covers、note。P2 一行要顯示「筆記那條配方的 invariant」,git 判斷要用配方的 `file`(帳檔行上的 `file` 欄並不存在,kill-log 只寫 invariant/test/platform…),也要平台來找 repo 最上層。
2. 接手者必須改 `_backing_note_recipes`(共用給合約背書,多帶欄位不影響其判斷,但要確認 `t_*backing*` 系列測試不比對整列),或另寫第二套對回邏輯。計劃應明講改哪一支、多帶哪幾欄。
3. 附帶:`_backing_kill_rows` 讀的是 `repo_root/docs/.kill-log.jsonl` 與 `_vault_in(repo_root)`,與 P2 掃描傳入的 `vault` 在多知識庫專案可能不是同一個;計劃沒提。

## F4 現有測試會紅的有一條計劃宣稱「查過沒有」:t_guard_kill_add_warns_drifted_recipe 逐字比 kill-add 的標準輸出
severity: major
blocking: 是
引句:「只更新 covers 的那條路照舊(已查過沒有測試釘這兩行字面)」
file: `scripts/test_lumos.py:60792`(`r.stdout == ok.stdout`,case 函式註明「標準輸出跟對得上時逐字相同」)
file: `scripts/test_lumos.py:60770`(ok 用 `--old "LIMIT = 5"`,各 case 用 `LIMIT = 42` 等不同原文)
1. 不帶 `--try` 的新「下一步:只跑這一條 … --id <短身分>」把配方身分印進標準輸出。短身分由節點、合約、檔、原文算出,各 case 的 `--old` 不同 → 身分不同 → `r.stdout == ok.stdout` 比對失敗。
2. 這條測試比的不是「下一步」字面,而是兩次輸出相等,所以「已查過沒有測試釘字面」的查法漏了。實作者照做會在第一次跑 `-k guard_kill_add` 時看到紅,且計劃〈既有測試〉一節沒列它。
3. 修法二選一(要寫進計劃):把該測試的比對改成「去掉含 `--id` 的那行後相等」,或維持標準輸出不變、把新 hint 印到標準錯誤(後者會讓 `_kr_err_lines` 的「標準錯誤恰好多一行」計數全部失準,更糟)。前者較合理。
4. 未實測,依據是讀碼;可 `python3.14 scripts/test_lumos.py -k guard_kill_add_warns` 驗。

## F5 doctor P2 多開一段軟提醒時,現有 P2 測試的取段與事件斷言會一起吃到新段;段內 ok 與 warn 並存的顯示也沒定
severity: minor
blocking: 否
引句:「另開一個軟提醒(不跟「原文對不上」擠同一段」
file: `scripts/lumos:2951-2975`(P2 段結構:`if cfg_err … elif items … elif total: ok(...) else: ok(...)`,整段包在一個 try)
file: `scripts/test_lumos.py:60898`(t_doctor_kill_recipe_drift:`p2()` 取 `[P2]` 到下一個 `\n[` 的全文;⑥斷言 check-p2 事件全是 kind warned)
1. 計劃沒說新軟提醒接在哪個分支之後。現有結構是 elif 鏈:原文都對得上時會先印 `ok("殺傷力配方的原文都對得上")`,再接 survived 的 `warn_soft`,同一段出現綠勾又出現警告;須在計劃決定(建議先 ok 再 warn,或改標題)。
2. survived 計算要自己的 try(計劃有寫「整段包例外保護」),但它在現有外層 try 內,例外類別與訊息格式要與外層 `warn_soft([], "這一段算不出來…")` 區分,否則一行字無法分辨是哪一半壞。
3. 會碰到的既有測試(名字):t_doctor_kill_recipe_drift(`p2()` 取段、⑥ 事件 kind 斷言)、軟提醒計數類(doctor 結論行「還有幾段提醒」依 `_soft["segs"]`,凡 fixture 有 kill-log survived 列的都多一段)。這兩個在沒有 kill-log 的 fixture 下不受影響;S3 的測試 t_doctor_p2_lists_survived 要自己造 `docs/.kill-log.jsonl`。
4. `check-p2` 已在 `_KNOWN_GATES`(`scripts/lumos:7303`),新增 `"gate": "check-p2"` 的 survived 事件不需改名單,`t_gov_stats_gate_drift` 只掃閘名字面值,不會紅。

## F6 survived 事件的 kind 不是 warned,會被治理帳的空轉偵測與同日折疊整個略過
severity: minor
blocking: 否
引句:「kind 用 `survived`(跟原文對不上的 `warned` 分開)」
file: `scripts/lumos:7555`(`_render_gov_nags` 只算 kind=="warned" 且非 hard)
file: `scripts/lumos:7741`(`_is_advisory` 只折 warned)
1. `lumos gov --nags` 的「同一道軟閘對同一篇筆記喊超過 N 天沒人理」只認 warned;survived 事件永遠進不了那條鏈,等於「survived 清單掛了幾週沒人處理」這個計劃最想看見的狀況,工具看不到。
2. 同日同節點重複的 survived 事件不會被折成 ×N,`gov --full` 會逐筆列。
3. 這是計劃的刻意分開,但後果沒寫。接手者要嘛承認(並在 REVISIT 寫何時重驗),要嘛 kind 沿用 warned 再靠 `extra` 分流。判斷交編排者。

## F7 共用列表函式抽出後,guard kill 的重複配方列的註記字面會誤導
severity: minor
blocking: 否
引句:「guard kill 找不到短身分時用同一個逐行格式、印到標準錯誤」
file: `scripts/lumos:14500-14510`(`_guard_kill_rm_list` 的 dup 註記字面「(同一條 ×n,移除會一起移掉)」)
file: `scripts/test_lumos.py:61496`(t_guard_kill_rm_lists_ids ③ 斷言這串字面、④ 斷言結尾「移除:lumos guard kill-rm …」)
1. `_guard_kill_rm_rows` 要回「文字行」且不含結尾句,才能讓 kill-rm 維持結尾「移除」、guard kill 換成結尾「只跑某一條」(S1 的括號要求)。這點計劃有寫。
2. 但 dup 註記是寫死在行裡的「移除會一起移掉」;guard kill 的錯誤列表裡看到它語意不對(那裡是「會一起跑」)。共用函式要多一個參數,或字面改成中性;t_guard_kill_rm_lists_ids ③ 釘著現字面,改的話要同步。

## F8 條款 S1–S4 測試要的夾具,計劃沒說,接手者能照既有夾具拼出來,但有幾個非顯然的條件
severity: minor
blocking: 否
引句:「[S2] 當 `kill-add` 不帶 `--try` 寫入成功時」
file: `scripts/test_lumos.py:20341`(`_mk_kill_env`)、`scripts/test_lumos.py:20167`(`_mk_attr_env`,永遠綠=殺不掉)、`scripts/test_lumos.py:62140-62160`(`_fc_env`:fix-check 夾具)
1. S1:`_mk_kill_env` 後連續 kill-add 兩條不同 old,取各自 `_kill_recipe_id(...)[:12]`;「對到兩條不同配方」需要兩條身分共同前 8 碼,實務上不可能隨機撞出,要用 `ids` 直傳的單元測試(in-proc `_load_lumos_inproc()`),或手寫筆記注入兩條身分前 8 碼相同的配方(難造);計劃沒說用哪種。
2. S2:殺得掉用 `_mk_kill_env`(test_guard 斷言 LIMIT==5)+ `--old "LIMIT = 5" --new "LIMIT = 99"`;survived 用 `_mk_attr_env("print('ok')\n")`;`--try` 的筆記必然未提交,所以 weak=true、輸出一定帶「repo 有未提交變更」警告(計劃有預告)。「只更新 covers 也試跑」要先寫一條再帶 `--covers` 重跑(同 t_guard_kill_add_covers_update 的序列)。環境變數要 `LUMOS_KILL_TIMEOUT_FLOOR`(`_kr_lum` 已設 5)。
3. S3:要手造 `docs/.kill-log.jsonl`,每行至少 test、platform、verdict、head_sha(40 碼十六進位)、weak(布林)、recipe_id(用 `_kill_recipe_id` 的完整身分)、node(`Systems/Limit.md` 這種相對路徑)才不被 `_backing_kill_rows` 濾掉。「配方指的檔在那次之後改過」需要 head_sha 是真實的早期提交(取 `git rev-parse HEAD` 後再改檔提交);「只有別的檔改過」再多一次只動別檔的提交。這些計劃都沒寫。
4. S4:`_fc_env` 的筆記只有 Clamp.md,沒有 kill_recipes;要加一篇帶 `kill_recipes` 的筆記並在 base 提交裡。「別的 repo」需多平台設定(platforms 的 root 指向另一個 git repo),`_fc_env` 現在是單平台 test.run_cmd,要重寫 config。fix-check 的 notes 若在 `--json` 驗,要找 `"notes"` 陣列。

## F9 要同步的文件清單不全
severity: minor
blocking: 否
引句:「指令速查第 06 子檔 guard kill 那列」
file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:23-24`
file: `skills/lumos-project-notes/commands/INDEX.md:36`(列了 `kill-add(--covers)·kill-rm(不帶 --id 列出)·kill`)
file: `skills/lumos-project-notes/reference.md:520,521,584-586`(三行 guard kill-add/kill-rm/kill 用法)
file: `slim/skills/lumos-project-notes/reference.md`(slim 版對應段,是否由安裝腳本產生需確認)
file: `scripts/lumos:41910-41912`(說明字典 kill-add、kill-rm、kill 的一行說明)與 `scripts/lumos:42403-42425`(argparse help)
file: `scripts/test_lumos.py:25183`(②:守衛掃 `cmd_guard_kill` 函式本體的 verdict 字面,並要求 Systems/guard-kill.md 與 reference.md 列齊;新增 results_out 若寫出新的 `verdict` 字面或鍵會被掃到,只要不引入新判定值就不會紅)
1. 計劃只列三處(guard-kill 筆記、代碼審修正關卡筆記、第 06 子檔)。實際上還有 INDEX.md 的指令摘要、reference.md 的三行用法、slim 版 reference、`--help` 說明字典。reference.md 那段的 2000 字範圍被 ② 測試讀去比對 verdict,改它時別動到判定值清單。
2. 不需改:`docs/指令參考.md` 與 `docs/command-reference.md` 只有 `guard kill <節點>` 一行,沒寫旗標;t_ 測試也沒釘這兩份的旗標。
3. 家的檢查:改 `scripts/lumos` 需要它的家(本計劃 lands_in 已列兩篇,但 kill-add、doctor P2 的家是否是 guard-kill 與 doctor 相關節點,接手者要用 `lumos impact --file scripts/lumos` 確認;單檔四萬行大概有多個家)。

## F10 fix-check 提醒的插入點、倉庫比對與 notes 輸出
severity: minor
blocking: 否
引句:「配方平台的 repo 最上層要等於修正關卡的 repo 最上層」
file: `scripts/lumos:11976-12000`(`changed` 在 `_isolated_worktree` 之前算好;notes 初始化在 11971)
file: `scripts/lumos:12150-12165`(最後輸出:非 JSON 時每條 notes 印成「  · 」;JSON 放進 "notes" 陣列)
file: `scripts/lumos:8438`(`_vault_repo_root` 往上找 `.git`)
1. 可行:`changed` 算完就能收集,notes 輸出路徑兩種格式都現成,早退點(帳本找不到、不用跑、紀錄不合法、base/HEAD 轉不出)全在這之前,所以「沒早退才跑到」成立。`_isolated_worktree` 失敗與設定讀不懂的 `return 2` 在其後,計劃的提醒會被丟掉(rc 2 本就不寫事件,可接受,但計劃沒提)。
2. 比對 repo 頂時 `rr` 是 `.resolve()` 過的路徑,`_kill_plat_top` 回 `git rev-parse --show-toplevel` 的結果,兩邊 macOS 上都是 realpath,可直接比;若 `--repo` 給的是子目錄,`rr` 不是 toplevel,`git diff --name-only` 的路徑卻是相對 toplevel,`changed` 與配方 `file` 會對不上(漏報)。計劃沒說拿 `rr` 還是 toplevel 比;建議比 `_kill_plat_top` 的結果與 `git -C rr rev-parse --show-toplevel`。
3. 配方設定要用 `_kill_check_ctx(rr)` 讀主工作目錄的 config,而修正關卡其餘部分用的是樹裡的 config(複製或提交版)。兩份不同時平台根可能不同,計劃沒提。
4. `_kill_p2_skips` 在現有碼不存在(P2 掃描與 Check P 各自內聯同一組條件,見 `scripts/lumos:2907` 與 `14186`);抽出時要保留 P 段與 P2 的細微差別:P2 多一個 `kill_recipes is None` 才 continue,Check P 不看該欄。計劃寫成「三處共用,行為不變」,但 Check P 不屬於那三處。
5. fix-check 現有測試(t_fix_check_*)夾具都沒有 kill_recipes,新增行為對它們無感;S4 的測試 t_fix_check_record_complete 同類夾具 `_fc_env` 可擴充。

## 已讀,無 finding 的節
- 〈名詞〉〈回退〉〈實務隱患〉的「已排除」三條:已讀,無 finding。
- `warn_box` 帶完整身分:可行但不必改形狀。`_guard_kill_add_locked` 已在 14316 附近算 `key`,warn_box 裝的是 recipe dict(含只更新 covers 時的既有那條),鎖外直接 `_kill_recipe_id(str(rel), rec)` 即得同一完整身分(欄位全是字串時走 `_kill_recipe_key`,與鎖內判重同一函式),不用改 `warn_box` 形狀、也不必動 `_kill_add_warn`。若照計劃字面把 `warn_box` 裝成別的形狀,`_kill_add_warn(env, rel, rec)` 與兩條使用它的現有測試要一起改。
- `results_out`:可行。`weak` 與 `recipe_id` 在尾端蓋章迴圈(`scripts/lumos:15025` 一帶)之後才齊,`_rid` 是完整身分;一定要在蓋章之後、第一個 `return` 之前填。run_cmd 缺失的 `return 2`(`scripts/lumos:14879`)發生在蓋章前,此時 results_out 為空;`--try` 必須能容忍空結果並回 2。
- `--json` 純度與 rc 優先序:新增錯誤輸出全走標準錯誤即不動合約;不給 `ids`、`results_out` 時既有路徑不變。
- argparse:`--try` 的 dest 要避開關鍵字(例 `gk_try`),`--id` 用 `action="append"` 加逗號切分;kill-rm 現用 `dest="gkr_id"`,命名可比照。

最高等級:major,blocking 共 3 條
