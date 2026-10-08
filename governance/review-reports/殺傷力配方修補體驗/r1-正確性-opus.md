severity: major

# 設計審第 1 輪:正確性-opus

鏡頭:照 spec 字面實作會不會做出錯的行為。對照 repo:scratchpad/negguard(HEAD 5f8c84ff),實驗在自己的 --shared clone 裡跑(/opt/homebrew/bin/python3 3.14.6),腳本在 fx-r1-work-正確性-opus/exp.py。

## 逐節核對

- 白話/依據:已讀,無 finding。核對了「kill-rm 印的範本把舊的 `--new` 原樣抄過去」——`_kill_add_template` 目前確實是 `"--new", val("new", "'<壞法>'")`(scripts/lumos:13496)。
- PRIOR-ART / RETIRE-IF:RETIRE-IF 的前提「guard kill 結果行已附短身分,夠用」有洞,併在 F2。
- 範圍:已讀,無 finding。核對了「`--json` 輸出內容(`recipe_id` 欄本來就有)都不改」——`recipe_id` 在蓋章迴圈用 `_kill_recipe_key` 算(scripts/lumos:13926),寫 kill-log 時欄位是逐一列舉的(不會把旁路欄帶進 kill-log,背書計算讀 kill-log 的 `recipe_id`,也不受影響)。
- 做法・範本:F1。其他欄位(`--test` `--platform` `--note` `--covers`)照 spec 字面只動 `--new` 那一格,照舊,無 finding。
- 做法・kill-rm 不帶 --id:F3、F4。回傳碼與順序已核對:現行 `cmd_guard_kill_rm` 先驗 id 再找筆記(scripts/lumos:13518),列出分支要在驗 id 之前分流,spec 寫的「開頭先分流」對;`_kill_read_recipes` 本身就把 `load_raw_for_edit` 的例外收成「frontmatter 解析失敗」,所以「整欄解析不了照既有擋下回 2」用它一支就涵蓋,沒有漏回傳碼。
- 做法・guard kill 人讀輸出:F2、F6。9 個 `results.append` 點(平台不在 config、worktree add 失敗、test 名不合法、baseline 非綠、路徑逃逸、開檔失敗、命中次數不對、revert 失敗、正常判定)手上都還有原配方 `r`,而且 `cmd_guard_kill` 沒有原地改 `r`(結果都是 `{**r, …}` 淺複製、`covers` 是重新指定不是改 list),所以「用原配方算」在每個點都做得到;revert 失敗後同組其餘配方根本沒有結果行(`break`),那幾條拿不到身分是既有行為。
- 條款:S3 的「格式壞的配方也一樣」過度宣稱,見 F2。
- 回退:已讀,無 finding。核對了「筆記與配方都沒被這次改動自動改過」——列出分支唯讀、guard kill 只多印一欄,無寫入。
- 實務隱患:F5。

## F1 範本的 `--new` 改成待填字樣後,忘了填的人會把字樣原封寫進配方,guard kill 判成強殺、回 0
severity: major
blocking: 是
引句:「`_kill_add_template` 的 `--new` 一律印 `'<照新原文改寫的壞法>'`(現在是把舊壞法原樣抄進去)」
file: `scripts/lumos:13325`
1. kill-add 對 `--new` 只檢查「跟 `--old` 不一樣」(scripts/lumos:13325),不檢查是不是範本字樣;寫入後的提醒 `_kill_add_warn` 只驗原文(old),不看 new。
2. `--old` 那格的待填字樣如果忘了填,原文在程式裡找不到,guard kill 會判 drifted、回 2,人會發現。`--new` 不一樣:old 填對、new 忘了填時,guard kill 會把程式碼換成 `<照新原文改寫的壞法>` 這串字。幾乎任何語言都會因此語法錯誤或編譯失敗,測試必紅。
3. 實驗(exp.py 情境 A):照範本只填好 `--old 'LIMIT = 5'`,`--new` 留範本字樣 `<照新原文改寫的壞法>`。kill-add 回 0、標準錯誤沒有任何提醒;提交後 `guard kill` 印出 `✓ killed    上限恆為5 [TestLimitFive]` 和「✓ 全部 killed(1 配方)——綁定測試咬得住」,回 0。測試在函式裡匯入被測模組(pytest 常見寫法;lumos 自己的測試也是在函式裡跑 lumos),語法錯誤的追蹤訊息會帶出測試名,歸因成立,所以是強殺,不是弱證據。
4. 結果:一條「只是把程式弄到編譯不過」的假壞法拿到最強的背書,掩蓋綁定測試其實接不接得住真正的壞法。這次改動以前,忘了改 `--new` 的人至少拿到一條有語意的舊壞法;改動以後,忘了填等於自動造假證據。spec 的「已排除:守衛面」也沒看到這一點。
5. 建議:同一份計劃補一道機械擋——kill-add 遇到 `--new`(或 `--old`)等於範本的待填字樣就擋下回 2(或至少 guard kill 對這種配方判 error),並在 S1 加一條反向條款綁測試。

## F2 S3 的「格式壞的配方也一樣」在 guard kill 上做不到:好幾種格式壞的配方會讓 guard kill 整支崩潰、一行結果都不印
severity: minor
blocking: 否
引句:「該短身分拿去 `kill-rm --id` 應對得到那一條(格式壞的配方也一樣)」
file: `scripts/lumos:13792`
1. 實驗(exp.py 情境 B,每次一條正常配方加一條格式壞的):
   - 不是物件(例 `3`):分組那行 `r.get("platform")`(scripts/lumos:13792)丟 AttributeError,回 1,標準輸出全空,kill-log 0 行。
   - `file` 是數字:`os.path.join(wt, 5)`(scripts/lumos:13859)丟 TypeError,同上全空。spec 自己舉的例子「file 是數字」只有在更早就出結果的路徑(平台不在 config、test 名不合法、baseline 非綠)才會有結果行。
   - `old` 是數字:`src.count(5)`(scripts/lumos:13871)丟 TypeError,全空。
   - `invariant` 是數字:kill-log 寫完後,印人讀行的 `r.get('invariant','')[:30]`(scripts/lumos:13964)丟 TypeError,只印出第一條。
   - 缺 `old`:有結果行(drifted),這是唯一能穩定出結果行的格式壞樣本。
2. 所以「格式壞的配方也一樣」只在「是物件、而且出得了結果行」時成立。照字面實作的人如果拿 `file: 5` 或不是物件的元素寫 S3 的測試,會跑到崩潰;拿缺 old 寫就會綠,但條款宣稱的範圍比實際大。
3. RETIRE-IF 拿「guard kill 結果行已附短身分,夠用」當撤掉列出功能的理由,但上面這幾種配方 guard kill 根本印不出身分;另外缺 run_cmd(回 2、什麼都不印)、revert 失敗後同組其餘配方(沒有結果行)也一樣。這幾種現在由 doctor P2 列(格式壞的算失配),但撤除條件的理由要寫準。
4. 建議:S3 改成「格式壞但 guard kill 出得了結果行的配方(例:缺 old)也一樣」,並明寫「不是物件、欄位型別錯到讓 guard kill 崩潰的,不在本條範圍(guard kill 判法不改)」;RETIRE-IF 的理由補上這些例外。

## F3 列出時人寫欄位不是字串或缺欄位的印法沒定義:照字面「old 前 30 字」可能崩潰,缺欄位會印成像真值的 "None"
severity: minor
blocking: 否
引句:「`<短身分前 12 字元>  平台 <platform 或預設>  檔 <file>  原文 <old 前 30 字>  test <test>`,各欄經 `_kill_show`(會帶引號);不是物件的元素整個印 `_kill_show(json 原樣)`」
file: `scripts/lumos:13056`
1. S2 要求格式壞的配方「也應列出」。是物件但 `old` 是數字(例 `{"old": 5}`)時,照字面先取「前 30 字」再交給 `_kill_show`,`5[:30]` 會丟 TypeError,列出整支崩潰(既有 `t_guard_kill_rm` 的樣本就有 `file: 5` 這種)。
2. 缺欄位時 `_kill_show(r.get("old"))` 會印 `"None"`(`_kill_show` 先 `str()`),看起來像原文真的是 None 這串字,而不是「缺」。
3. 「<platform 或預設>」沒說是印「預設」這兩個字,還是讀設定檔拿 default_platform。後者要讀 config,設定壞時 `load_platforms` 會丟 ValueError(guard kill 會接住回 2,列出分支 spec 沒說要接);前者經 `_kill_show` 後印成 `"預設"`,跟一個真的叫「預設」的平台分不出來。
4. 「不是物件的元素整個印 `_kill_show(json 原樣)`」沒說那一行開頭還要不要有短身分;S2 要求「身分可直接拿去 `--id` 移除」,照字面只印 json 就拿不到身分。
5. 建議:寫明「欄位先 `str()` 再截斷再 `_kill_show`;缺的欄位印 `<缺>`;平台缺時印不加引號的 `(預設)`、不讀設定;不是物件的元素那行開頭照樣是短身分」。

## F4 「沒帶 --id」跟「--id 給空字串」沒分開,實作寫成 `if not rid` 會把現在擋下的空字串變成列出回 0
severity: minor
blocking: 否
引句:「argparse 的 `--id` 從必填改成選填;`cmd_guard_kill_rm` 開頭先分流——沒帶 `--id` 走唯讀列出」
file: `scripts/lumos:13518`
1. 現在 `--id ''` 會落到 `str(rid or "")` 再過正規式驗證,擋下回 2(scripts/lumos:13518)。
2. 分流如果寫成 `if not rid:`(Python 常見寫法),`--id ""` 會改走列出、回 0、筆記不變。腳本用 `lumos guard kill-rm X --id "$ID"`、而 `$ID` 因為前一步沒抓到變成空字串時,以前會被擋下,之後回 0,腳本以為移除成功。
3. 建議:spec 寫明分流條件是「參數沒出現(None)」,空字串照既有驗證擋下回 2,S2 的測試加一格。

## F5 「worktree 無殘留」那支測試看的是 `git worktree list`,不是 guard kill 的人讀輸出,隱患段的前提寫錯
severity: minor
blocking: 否
引句:「那支要求人讀輸出維持單行(加 id 後仍單行)」
file: `scripts/test_lumos.py:20504`
1. `t_guard_kill` 裡的「worktree 無殘留」是 `git worktree list` 的輸出只有一行(scripts/test_lumos.py:20503-20504),跟 guard kill 的人讀輸出無關。
2. 照這句去檢查的人會以為已經有測試守住「人讀行單行」,其實沒有。真要守住(例:說明欄帶換行時,`id=` 放在說明前面才不會被擠到下一行),要在 S3 自己的測試斷言。
3. 建議:改寫成正確的描述,或刪掉這句。

## F6 「在組結果時用原配方算」要在 9 個 append 點各補一次,S3 的測試走不到其中幾個點;漏一個就印空身分或崩潰
severity: minor
blocking: 否
引句:「所以在組結果時用原配方算 `_kill_recipe_id`,存成底線開頭的旁路欄」
file: `scripts/lumos:13836`
1. `cmd_guard_kill` 有 9 個 `results.append` 點(scripts/lumos:13798、13836、13845、13855、13861、13868、13873、13883、13908)。照字面在「組結果時」補,就是 9 處各加一欄。
2. 其中「worktree add 失敗」(13836)、「revert 失敗」(13883)、「開檔失敗」(13868)在測試裡很難造出來,S3 的測試大概不會走到。漏補的那一處,人讀行用 `r.get(旁路欄, "")` 會印 `id=`(空的,拿不到身分),用 `r[旁路欄]` 會在 kill-log 寫完後丟 KeyError。
3. 建議:spec 改成單點做法——分組前一次把每條配方複製成 `{**r, 旁路欄: _kill_recipe_id(str(rel), r)}`(先算再加欄,不改到原配方的雜湊輸入),9 個 `{**r, …}` 自然都帶上;不是物件的元素在分組那行本來就會崩潰(F2),不受影響。`--json` 前濾掉旁路欄的寫法照 `_logged`;kill-log 是逐欄列舉,不會帶到。

最高等級:major;blocking 共 1 條
