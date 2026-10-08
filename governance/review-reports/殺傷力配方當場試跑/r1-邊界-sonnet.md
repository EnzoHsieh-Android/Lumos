severity: major

# r1 邊界-sonnet(邊界與輸入)

實驗都在我自己的 clone(`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/tr-r1-work-邊界-sonnet/`)跑,沒動被審 repo。

## F1 設定檔讀不了或平台根找不到時,「survived 清單照樣算」與「排除不是 ok 的配方」互相打架,字面實作會讓清單變空
severity: major
blocking: 是
引句:「設定檔讀不了時這段照樣算(它不靠設定檔判對不對得上)」
file: `scripts/lumos:14008`(`_kill_recipe_judge`:`ctx["cfg_err"]` 有值就直接回 status="cfg",平台根找不到回 "noroot")
file: `scripts/lumos:14213`(`_kill_p2_one` 回的就是這個 status;P2 現行只有 ok 與 cfg 不印)
1. 快照〈③〉規定:survived 清單要跳過「`_kill_p2_one` 判出來不是 ok 的」配方完整身分。
2. 但 `_kill_p2_one` 在設定檔壞掉時對每一條都回 `cfg`、平台根找不到時回 `noroot`,兩者都「不是 ok」。字面實作下,這兩種情況的配方全被排除,survived 清單必空。
3. 同一節又寫「設定檔讀不了、平台找不到時也直接加這句」(行尾附註)和「設定檔讀不了時這段照樣算」。這兩句只有在 cfg、noroot 的配方「沒被排除」時才成立,跟排除規則矛盾。
4. 重現(實測):`.lumos/config.json` 寫成 `{bad` 後,`_kill_recipe_judge(_kill_check_ctx(root), 合法配方)["status"]` 印出 `cfg`。
5. 另外 `noroot` 是整個平台聚成一條「它底下 N 條配方沒驗」,不是逐條,也要說清楚排除與否。
6. 要寫清楚的是:排除集合只收「原文對不上而且已逐條列出」的狀態(hits、missing、undecodable、path、malformed、noplat 逐條那幾種),不收 cfg、noroot。S3 沒有任何一條測 cfg 或 noroot 情境,這個洞測試不會紅。

## F2 `--try` 剛寫完筆記必然是弱證據,但 rc 與印出文字只看判定、不看 weak,會對使用者說「咬得住」
severity: major
blocking: 是
引句:「有強證據的 killed 回 0;任一 survived 或全部只拿到弱判定(killed_unattributed、timed_out_weak)回 1」
file: `scripts/lumos:14871`(`node_dirty` 用 `git status --porcelain -- 筆記` 判,kill-add 剛寫完筆記一定是髒的)
file: `scripts/lumos:15030`(收尾 `res["weak"] = bool(... or node_dirty ...)`,但 rc 與尾行「✓ 全部 killed … 咬得住」只看 verdict)
file: `scripts/lumos:41034`(`_backing_judge_groups`:`verdict == "killed" and r["weak"] is not True` 才算強證據,所以這次試跑的結果合約背書不會採信)
1. 輸入:`kill-add … --try`。寫完筆記未提交,`node_dirty` 必為 true,kill-log 這一行 `weak=true`。
2. 判定是 killed(紅燈歸因到綁定測試)時,`cmd_guard_kill` 回 0 並印「✓ 全部 killed(1 配方)——綁定測試咬得住」。
3. 快照寫的「強證據」按〈名詞〉是 `weak` 欄(整套一起跑、flaky、筆記未提交、修改時間沒錯開),但 rc 規則括號卻拿 verdict 的弱判定當定義。兩個定義不同,S2 的「有強證據殺得掉回 0」在 `--try` 這條路永遠測不到(筆記必髒),照字面寫測試的人只能 mock 或先提交。
4. 後果:使用者看到 rc 0 與「咬得住」就以為驗過,提交後合約背書仍是「沒有強證據」,到表態時才發現,要再跑一次整套。〈範圍〉只講了會印未提交警告,沒講「killed 但 weak 時要提醒提交後重跑」。
5. 判不準處標 ⚠ 交編排者:要不要把 killed+weak 的 rc 改成非 0,是設計裁量;但最少要定義「強證據」用哪一個、並為 killed 而 weak=true 的情況另印一句。

## F3 `--id` 指到列表裡「格式壞」那條時,guard kill 會程式崩潰,結束碼是 1(跟 survived 同碼)
severity: major
blocking: 是
引句:「接著用共用逐行格式列出這篇每條配方(印到標準錯誤)」
file: `scripts/lumos:14882`(`cmd_guard_kill`:`r.get("platform")` 在非物件配方上 AttributeError)
file: `scripts/lumos:14842`(合約片段過濾 `r.get("invariant", "")` 同樣崩)
1. 新列表(共用 `_guard_kill_rm_rows`)會把格式壞的配方也列出短身分(現行 `kill-rm` 列表就印「格式壞:…」,實測 `11fc82e313f1  格式壞:"\"just a string\""`),結尾又叫人「只跑某一條」。
2. 使用者照抄那條的短身分 `--id 11fc82e3` → 比對成功(`_kill_recipe_id` 對壞元素也給身分)→ 進入 `groups` 迴圈 → 非 dict 的 `r.get` 崩潰。Python 未捕捉例外的結束碼是 1,等於 survived 的 rc。
3. 重現(現行碼,id 過濾還沒實作,同一行崩潰):筆記 `kill_recipes` 放 `["just a string", {...好的...}]`,`lumos guard kill Systems/zz-edge` 印 `AttributeError: 'str' object has no attribute 'get'`。
4. 快照〈做法①〉只定了零條、非十六進位、多條三種回 2,沒定「對到的是格式壞配方」。另外 id 過濾排在合約片段過濾之後,帶合約片段時壞元素仍先在片段過濾那行崩潰(現行就崩,但新旗標號稱能繞開壞元素,實際只在不帶片段時才繞得開)。
5. 要補:id 比對先於且不依賴 `r.get`;對到格式壞配方時回 2 並說「格式壞,先 kill-rm」。

## F4 P2 的 `git diff` 沒定義 stderr 處理與單次逾時,壞版本/淺 clone 會洗版、20 秒上限可被單次呼叫衝破
severity: minor
blocking: 否
引句:「整段時間上限沿用 `_BACKING_BUDGET`(20 秒),超過的直接加這句」
file: `scripts/lumos:41007`(`_BACKING_BUDGET`)與 `scripts/lumos:40384`(既有 `_codeloop_record_valid_ex` 的 timeout 夾在剩餘預算內)
file: `scripts/lumos:13971`(`_KILL_GIT_TIMEOUT = 10`,單次呼叫上限)
1. 實測:`git diff --quiet <不存在的 40 碼 sha> HEAD -- a.py` 回 128,淺 clone 缺那版本也回 128,stderr 印 `fatal: bad object …`;快照寫「非 0 或出錯都算改過」判得對,但沒說要擋 stderr,`doctor` 輸出會多出這些 fatal 行(每個不同的版本與檔一次)。
2. 預算只在每次呼叫前比時間;若呼叫沿用 10 秒單次逾時,最後一個判斷可能讓整段到 30 秒。既有背書那段是把 timeout 夾到剩餘預算,快照沒寫要照做。
3. 這兩點都只影響提醒的整潔與時間,不影響判斷方向(逾時、出錯本來就走「改過」),所以 minor。

## 已核對、無 finding 的邊界(附實測)
- `--id` 的怪值:大寫、前後空白由 kill-rm 的 `strip().lower()` + `[0-9a-f]{8,64}` 處理;空字串、`a,,b` 的空片段會因為不是 8 碼以上十六進位而回 2,行為合理。同一個給兩次或兩個短身分指到同一條,以完整身分集合比對,不會重跑。前段剛好 8 碼又同時是兩條前段,沿用 kill-rm 的「對到多條不同完整身分擋下」。快照〈名詞〉已寫明比對照 kill-rm,已讀,無 finding。
- kill-log 怪行(實測 `_backing_kill_rows`,306 筆,含一行 5MB、壞 JSON、非物件、64 碼與大寫與以 `-` 開頭的 `head_sha`、`weak` 為字串或 null、`ts` 缺或是整數、同配方 300 筆):0.01 秒讀完;`weak` 非布林、`head_sha` 非小寫 40 或 64 碼十六進位、`recipe_id` 空的都被略過;`ts` 缺或整數的行照收,快照已要求 `ts` 必須是字串才取前 10 字,已讀,無 finding。
- 配方 `file` 是中文、含空白:`git diff --quiet <sha> HEAD -- "中文/檔 案.py"` 實測行為正確;冒號開頭、非 NFC 檔名在 `_kill_path_issue` 就被判成路徑問題,不會走到 diff;`pages/[id].vue` 這類含萬用字元的檔名,git 會先當字面路徑比對,改了時回 1(實測),不會漏報。檔被刪、被改名時 diff 回 1,也算「改過」,方向正確。
- 平台根在別的 repo:kill-log 的 `head_sha` 是平台所在 repo 的 HEAD(`rev-parse HEAD` 在 `proot` 跑),跟 `_kill_plat_top` 同一個 repo,版本不存在時回 128 走「改過」。
- 淺 clone、不存在的版本:都回 128,走「改過」;CI 上 kill-log 不進版控,清單多半空,快照〈本機才有帳〉已寫明。
- 修正關卡 changed 集合很大:`changed` 是 `set`,逐條配方查 O(1),且用 `-z` 讀、`core.quotePath` 不影響;`_fix_git_z` 失敗時回空集合,只是少一句提醒。已讀,無 finding。
- 配方身分不含平台:同一(合約、檔、原文)在兩個平台會同身分(實測 `same id different platform: True`),但 kill-add 判重就擋,只可能手改造成,快照已說明同身分會一起跑,不另提。

最高等級:major,blocking 共 3 條
