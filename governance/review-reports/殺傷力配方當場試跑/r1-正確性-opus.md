severity: major

# r1 正確性-opus(鏡頭:正確性與邏輯)

審查對象:凍結快照 `governance/review-reports/殺傷力配方當場試跑/r1-snapshot.md`(逐節讀完 111 行)。
實驗環境:`tr-r1-work-正確性-opus/repo`(`git clone --shared`),用 `scripts/test_lumos.py` 的 `_mk_kill_env` 夾具造 survived 配方、真跑 `guard kill` 寫 kill-log,再照計劃判法逐步手算(腳本 `tr-r1-work-正確性-opus/exp1.py`、`exp2.py`)。

各節總覽:
- 開頭(白話/依據/PRIOR-ART/RETIRE-IF/REVISIT):交叉引用 5 篇都存在;PRIOR-ART 有一處與做法不符(F8)。
- 〈名詞〉:F8、F9。
- 〈範圍〉:已讀,無 finding。
- 〈共用的小整理〉:已讀,無 finding(`_guard_kill_rm_list` 的結尾句與 `t_guard_kill_rm_lists_ids` 釘的字面一致)。
- ①:F6。
- ②:F5、F9。
- ③:F1、F2、F3、F4、F7。
- ④:已讀,無 finding。repo 頂比對查過:`_vault_repo_root` 走 `Path.resolve()`、`_kill_plat_top` 走 `git rev-parse --show-toplevel`,在 `/tmp→/private/tmp` 這種連結下兩邊實測一致;只有手打 `--repo` 而且大小寫跟磁碟不同時兩邊會不一樣(實測 git 回磁碟上的大小寫、`Path.resolve` 照打的),這是邊角,不列。`changed` 是 `--no-renames` 的 repo 頂相對路徑,跟配方 `file` 同一個基準,判法對。
- 條款 S1–S4:各自的缺口寫在 F1、F2、F6、F7、F9 裡。
- 〈回退〉:已讀,無 finding。
- 〈實務隱患〉:逐類核對寫在報告最後。
- 既有合約:`ids`/`results_out` 都不給時判法不動;`--id` 對不到時回 2,屬於早退,不印 JSON,在 `--json` 純度合約明文收窄的範圍外;rc 優先序那段(`if "survived" in verdicts` 之後)不碰。沒找到會破壞 ★INVARIANT★ 的路徑。

## F1 「已列過的不重複」拿「不是 ok」當集合,設定檔讀不了時 survived 清單一定是空的,跟同節「照樣算」矛盾
severity: major
blocking: 是
引句:「`_kill_p2_scan` 多回一個「這次已列出問題的配方完整身分」集合(`_kill_p2_one` 判出來不是 ok 的),survived 清單跳過它們,不重複列。」
佐證:file: `scripts/lumos:14030`(`_kill_recipe_judge` 設定檔讀不了時,每條格式好的配方都回 status `cfg`)
佐證:file: `scripts/lumos:14225`(`noroot` 只併成整個平台一行「N 條沒驗」,不逐條列)
佐證:file: `scripts/lumos:14233`(`ok` 跟 `cfg` 都不進 items,也就是 `cfg` 從來沒被「列出」)
1. 輸入:有一條配方的 kill-log 最後一筆是 survived,然後 `.lumos/config.json` 寫壞(例如 `{bad json`)。
2. 照 ③ 第一條字面實作:`_kill_p2_one` 回 `cfg`,不是 `ok`,所以這條的完整身分進了「已列出問題」集合,survived 清單把它跳過。結果 survived 段沒東西可列。但同節最後一條明寫「設定檔讀不了時這段照樣算(它不靠設定檔判對不對得上)」,兩句照字面不可能同時成立,S3 也沒有設定檔壞掉的格子能抓到。
3. 實測(exp1.py 的 E3):設定檔寫壞之後,`_kill_p2_one(...)` 回 `['cfg']`,`items: []`。這條在 P2 原文段只出現在一句「設定檔讀不了」裡,沒有逐條列出,survived 段卻因為集合把它擋掉了。
4. 同一個洞也出現在 `noroot`(平台根這台機器上找不到,只印一行「它底下 N 條配方沒驗」)和 `error`(判斷丟例外)。這幾種都不是「已列出問題」,卻同樣被跳過。
5. 要改成跟計劃本意一致:集合只收 `_kill_p2_one` 真的加進 `items` 的那幾種(`hits`/`missing`/`undecodable`/`path`/`malformed`/`noplat`/`error`),`cfg` 跟 `noroot` 不算;S3 再加一格「設定檔讀不了時仍列 survived」。

## F2 「配方指的檔之後改過」只看配方的 file,補強綁定測試(survived 最常見的修法)提交後不加註,S3 還把這種情況釘成「不帶」
severity: minor
blocking: 否
引句:「配方指的檔在那次的版本到現在的 `HEAD` 之間改過,或判不了 → 「(配方指的檔之後改過,先重跑)」」
1. 實測(exp1.py):`_mk_kill_env` 加一條 `--old 'return n <= LIMIT' --new 'return n <= LIMIT if n != 7 else True'`,提交後跑 guard kill,結果 survived(rc 1)。照計劃判法:E1 列出、`配方檔改過=False`。
2. 接著只改 `test_guard.py`,補 `not prod.check(7)` 再提交,不重跑(E2)。照判法:仍然列出 survived,`配方檔改過=False`,所以不加「先重跑」。可是這時候測試已經咬得住,E2c 重跑也確認判 killed。
3. 改 `prod.py` 別處的註解(E2b)反而會加註。結果是:跟殺不殺得掉無關的改動會觸發提示,真正會讓結論翻盤的改動(改測試)不觸發。標題「原文對得上卻殺不掉」在 E2 那個狀態是錯的,行尾也沒有任何提示,看的人可能照行內第二個指令把一條現在殺得掉的配方 kill-rm 掉。
4. S3 末尾「檔沒改過、只有別的檔改過時應不帶」把 E2 這種情況釘成正確行為。配方只有測試方法名、沒有測試檔路徑,要精確判很難。至少要在計劃裡寫明「綁定測試改過不會觸發這句」是已知盲區,不要讓 S3 的「只有別的檔改過時應不帶」看起來像全面保證。

## F3 「檔內順序最後一筆」的理由「跟 _backing_judge_groups 一致」不成立;本 repo 的 kill-log 進版控,合併後檔內順序不等於時間順序
severity: minor
blocking: 否
引句:「每條配方取**檔內順序最後一筆**(跟合約背書 `_backing_judge_groups` 一致,不比 `ts`);最後一筆判定是 survived 的列出來。」
佐證:file: `scripts/lumos:41041`(背書只用 `groups[rid][-1]` 取 covers)
佐證:file: `scripts/lumos:41046`(背書判 survived 用「這組任何一筆」,跟順序無關)
1. `_backing_judge_groups` 的判定(有沒有 survived)跟順序無關,檔內順序只拿來取 covers。P2 要的是「判定看最後一筆」,這兩件事不等價,所以「一致」這個理由站不住。
2. `git ls-files docs/.kill-log.jsonl` 在本 repo 有結果:帳進版控。〈實務隱患〉只寫了「消費專案的 kill-log 不進版控」。本 repo 常有多個會談各自開 worktree、各自追加 kill-log 再 rebase 合併,追加衝突解開後行的先後是合併順序,不是跑的時間。
3. 會出錯的情況:A 工作樹 T1 survived、修測試後 T3 killed,B 工作樹 T2 在舊版程式上 survived。B rebase 到 A 之後,檔內順序變成 survived(T1)、killed(T3)、survived(T2),P2 判「最近一次 survived」,實際上最新一次是 killed。未實測,依據是讀碼加上帳在版控裡。⚠ 這種情況多常見交編排者判斷。
4. 計劃至少要把理由改成實話(選檔內順序是為了不信手寫的 ts),並在〈實務隱患〉補一句「本 repo 帳進版控,合併後順序可能倒」。

## F4 列出的短身分沒指定從哪裡算;帳上的 recipe_id 跟 --id/kill-rm 用的身分在配方缺 invariant 時不同,照帳上那份印會給出用不了的指令
severity: minor
blocking: 否
引句:「一行寫:筆記、短身分、合約前段(取筆記那條配方的 `invariant`、經 `_kill_show`,不取帳檔那一行的)」
佐證:file: `scripts/lumos:15028`(kill-log 的 recipe_id 用 `_kill_recipe_key`)
佐證:file: `scripts/lumos:14877`(guard kill 的 id= 跟 kill-rm 都用 `_kill_recipe_id`;欄位不是字串時改用 malformed 雜湊)
佐證:file: `scripts/lumos:41119`(`_backing_note_recipes` 用 `_kill_recipe_key` 對回筆記)
1. 實測(exp2.py):kill-add 一條會 survived 的配方,手改筆記拿掉 `invariant` 欄,提交後跑 guard kill → survived。`_backing_kill_rows` 照樣收這一行(recipe_id 前段 `0537548cc29a`),P2 的 `_kill_p2_one` 判 `ok`(原文判法不看 invariant),所以它會出現在 survived 清單。
2. 同一條配方的 `_kill_recipe_id` 是 `8c425245663c`。拿帳上那份跑 `lumos guard kill-rm Systems/Limit --id 0537548cc29a` 實測 rc 2:「配方裡沒有身分以 0537548cc29a 開頭的」。
3. ③ 的分組天然是按帳上的 `recipe_id`,計劃對合約前段特地寫了「取筆記那條」,對短身分卻沒寫。照分組鍵印,兩個貼上就能跑的指令都會失敗。要明寫短身分取 `_kill_recipe_id(節點, 筆記那條配方)`,跟〈名詞〉的定義一致。觸發條件是手改造成的格式不全配方,所以標 minor。

## F5 `--try` 寫入成功但試跑判 drifted/abort/error 時回 2,跟寫入失敗同一個碼;drifted 提示的「再試」照做會被判重擋下,abort 沒有提示
severity: minor
blocking: 否
引句:「寫入成功時用 guard kill 的回傳碼——有強證據的 killed 回 0;任一 survived 或全部只拿到弱判定(killed_unattributed、timed_out_weak)回 1;drifted、abort、error 回 2。」
佐證:file: `scripts/lumos:14351`(同一條配方已存在時 kill-add 擋下 rc 2)
1. kill-add 原本 rc 2 一律是「擋下、沒寫進去」。加了 `--try` 以後,rc 2 也可能是「已寫進筆記、只是試跑 drifted」。看回傳碼的人或代理分不出這兩種。
2. ② 寫 drifted 時另印「先提交程式再試」。照字面「再試」就是再跑一次同一行 `kill-add … --try`,結果撞到判重,rc 2「同一條合約、同檔、同一個舊字串的突變配方已經有了」。正確的下一步是 `lumos guard kill <節點> --id <短身分>`,提示要直接印這行。
3. `abort`(baseline 不綠)在 `--try` 裡很常見:剛 `guard bind` 的新測試還沒提交,HEAD 的工作樹裡沒有它。計劃替 survived、全弱、drifted 都配了提示,abort 沒有,使用者只看到 rc 2 跟「baseline 非綠」。

## F6 ① 的前段解析位置自相矛盾(CLI 先解析,還是過濾後才比對),跟合約片段一起給時錯誤訊息與歧義判定會因實作而異,S1 釘不住
severity: minor
blocking: 否
引句:「比對在合約片段過濾之後、「沒有配方可跑」判斷之前;兩個條件都要符合。」
佐證:file: `scripts/lumos:14841`(合約片段過濾在 `cmd_guard_kill` 裡面)
佐證:file: `scripts/lumos:14844`(過濾後清單是空的就印「沒有任何突變配方可跑」)
1. 同節第三條又寫 `ids` 是「CLI 由 `--id` 前段解析出來後傳入」的完整身分。如果 CLI 在呼叫 `cmd_guard_kill` 之前就解析前段,那是對整篇配方解析,發生在函式裡的合約片段過濾之前,跟第一句矛盾。
2. 可觀察的差別有兩個。(a) 給的短身分存在,但被合約片段濾掉:CLI 先解析的做法會走到「沒有任何突變配方可跑」,過濾後才比對的做法會走「對不到 + 列出每條 + 只跑某一條」。(b) 某個前段在整篇裡對到兩條不同配方,但濾完只剩一條:前一種擋下 rc 2,後一種照跑。
3. S1 只寫「兩個條件都要符合」,沒說這兩種情況的回傳與訊息,兩種實作都會綠。要定一種:建議在函式裡、合約片段過濾之後解析,`ids` 參數改收前段;或者把 (a)、(b) 寫進 S1。

## F7 `git diff --quiet <head_sha> HEAD -- <file>` 沒加 `:(literal)`,路徑含 `[ ]` 等萬用字元時,別的檔改過也會加註,違反 S3
severity: minor
blocking: 否
引句:「用配方平台的 repo 最上層(`_kill_plat_top`)跑 `git diff --quiet <head_sha> HEAD -- <file>`;非 0 或出錯都算改過。」
佐證:file: `scripts/lumos:14982`(guard kill 還原時用的是 `":(literal)" + 路徑`,已有前例)
1. 實測(`tr-r1-work-正確性-opus/pathspec`):repo 裡有 `app/[id]/page.tsx` 跟 `app/i/page.tsx`,只改後者後提交。`git diff --quiet <舊> HEAD -- "app/[id]/page.tsx"` 回 1,被當成改過;加 `:(literal)` 回 0。
2. Next.js 動態路由(`[slug]`、`[id]`)是消費專案常見的路徑。照計劃字面實作,會在 S3 寫明「只有別的檔改過時應不帶」的情況下加註。要改成 `-- :(literal)<file>`。

## F8 〈名詞〉說 guard kill 用 `_kill_plat_top` 找 repo 頂,與程式不符;PRIOR-ART 還列著前掃後已經不用的 `_codeloop_record_valid_ex`
severity: minor
blocking: 否
引句:「配方的 `file`,路徑相對配方平台所在 repo 的最上層(guard kill 用 `_kill_plat_top` 找那一層)。」
佐證:file: `scripts/lumos:14919`(guard kill 是用 `_isolated_worktree` 對平台根建工作樹,以工作樹根為基準)
佐證:file: `scripts/lumos:13915`(`_kill_plat_top` 是 P2/kill-add 提醒「模擬」guard kill 用的,guard kill 本身沒呼叫)
1. 實作者照〈名詞〉去 guard kill 裡找 `_kill_plat_top` 找不到。正確說法是:「guard kill 以平台根所在 repo 的工作樹根為基準;P2 用 `_kill_plat_top` 模擬同一層」。
2. PRIOR-ART 還寫著「之後只動簿記檔」判法 `_codeloop_record_valid_ex`;前掃第 2 條已經把「之後改過」從 `_codeloop_record_valid_ex` 改成 `git diff --quiet`,PRIOR-ART 沒跟著改。

## F9 「強證據」一詞跟〈名詞〉的「證據弱=weak 欄」打架;`--try` 下 weak 一定是 true,S2 的「有強證據殺得掉」照名詞定義永遠成立不了
severity: minor
blocking: 否
引句:「**證據弱**:kill-log 每行的 `weak` 欄(整套一起跑、flaky 平台、筆記有未提交改動、修改時間沒錯開會設 true),跟判定是兩回事。」
佐證:file: `scripts/lumos:14871`(`node_dirty`:筆記有未提交改動)
佐證:file: `scripts/lumos:15030`(`weak` 包含 `node_dirty`)
1. 計劃自己在〈預先講清楚的現象〉寫了 `--try` 那次 `weak` 一定是 true。照〈名詞〉,「強證據」就是 weak 為 false,那 `--try` 永遠拿不到強證據,S2 第二格「帶 `--try` 而新配方有強證據殺得掉時應印出判定並回 0」沒有輸入能造出來。
2. 回傳碼那句的「強證據的 killed」其實指的是判定為 `killed`(不是 unattributed/timeout),跟 weak 欄無關。實作者照名詞寫成「killed 而且 weak 為 false 才回 0」,`--try` 就永遠回不了 0。要把 ② 跟 S2 的「強證據」改成「判定是 killed」。

## 實務隱患(逐類)
- 併發:`--try` 在鎖外呼叫 guard kill,鎖只包寫入,沒有新的持鎖時間問題。CLI 解析前段跟函式裡重讀筆記之間會有空檔,別的會談在這段時間 kill-rm 掉那條時會落到「沒有配方可跑」rc 2,不會誤跑別條,無害。
- 時間與效能:P2 只對 survived 的最後一筆做 git diff,每個(版本、檔)一次,加上 20 秒上限,不會拖垮 doctor。
- 回傳碼與輸出純度:F5;`--json` 純度沒動到(見總覽)。
- 身分一致性:F4。
- 路徑解析:F7;repo 頂比對見總覽 ④。
- 帳本可信度與順序:F3;`_backing_kill_rows` 的型別擋、完整 sha 擋、對回筆記都沿用,照計劃寫的實作沒問題。
- 金流、對外送出:無,只讀本機帳與 git,不連網。
- 不可逆:無;`--try` 只追加 kill-log、不改筆記以外的檔,revert 回得去。

最高等級:major,blocking 共 1 條
