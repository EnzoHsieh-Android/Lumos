severity: major

# 設計審 r3 正確性席(opus):漂移修法補強_計劃

實驗環境:`git clone --shared clone-ns <本席 scratchpad>/exp`(HEAD e99ef775),另在 `<本席 scratchpad>/sx` 建小 repo 驗 git log -S/-G;沒改 repo 任何檔。

## F1 RETIRE-IF ① 用 git log -S 'valid_under' 找不到 c4 修正的提交,只找得到「建立驗證紀錄」的提交
severity: major
blocking: 是
引句:「在工具鏈與 rtb 用 git 找 5 筆 c4 修正的提交(`git log -S 'valid_under' -- <驗證紀錄目錄>`)」
file: `scripts/lumos:15153`
1. `-S` 只挑出「這個字串出現次數有變」的提交。c4 走 `lumos set` 整欄重寫(`_set_conditions_locked`),只換值,`valid_under` 這個鍵還是一個,次數不變,所以 c4 修正的提交不會出現在 -S 的結果裡。
2. 實測(小 repo,四個提交:建 E(清單寫法)→ 用 c4 改 E → 建 F(單行寫法)→ 用 c4 改 F):`git log -S 'valid_under' -- V` 只回 `createF`、`create`,兩個 c4 修正提交都沒找到。換成 `-G 'valid_under'` 也只多找到單行寫法那個(`c4fixF`),清單寫法的改動只動 `  - …` 那幾行,不會被找到。
3. 照字面在 2026-11-30 量:在工具鏈裡驗證紀錄很多,-S 很容易湊滿 5 筆,但全都是建立的提交。那些提交裡 valid_under 寫的是「未提交」,沒有「改寫後引的卷證目錄」→ 判成「5 筆都沒有 → 同提交找法沒用,撤掉」。**撤除條件會把一個還沒被驗到的功能撤掉。**不然就是量的人自己發現不對、當場改量法,這樣 RETIRE-IF 也就不是機械的了。
4. 改法:抓改寫後才會出現的字,例如 `git log -G '代碼審見|review-reports/' -- <驗證紀錄目錄>`;或抓 c4 詞被拿掉的提交(`-G '未提交|還沒提交'` 再用 `-p` 篩出只有 `-` 行的)。改完拿上面那種四提交的 repo 跑一次確認抓得到。

## F2 `_delguard_parse_diff` 新參數叫 `skip`,跟函式裡原本的區域變數 `skip` 撞名,照字面實作每次提交都會丟 TypeError
severity: major
blocking: 是
引句:「`_delguard_parse_diff` 加 `skip` 參數(預設空集合),抽 `-` 行名稱與收 `+` 行回收表兩遍都跳過 `skip` 裡的路徑」
file: `scripts/lumos:29257`
file: `scripts/lumos:29261`
1. 函式第一遍開頭有 `added, cur, skip, in_binary = {}, None, True, False`,每遇到檔頭又重設 `skip = (cur is None) or …`。照 spec 加一個叫 `skip` 的參數,再在兩遍裡寫「`cur in skip` 就跳過」,參數在第一遍開頭就會被蓋成 `True`。
2. 實測:把現有函式照字面改(參數 `skip=frozenset()`,第一遍判定後面接 `or cur in skip`,第二遍排除條件接 `or cur in skip`),拿一段改 `app/x.py` 加上改 `scripts/lumos` 的 diff 跑 → `TypeError: argument of type 'bool' is not a container or iterable`。用預設空集合呼叫也一樣會炸,只要 diff 裡有一支非 .md、不在排除清單的檔。
3. 後果:`cmd_delguard_check` 外層有個大範圍的 except,把錯誤吞掉、降級成 `degraded reason=error`、照樣放行(fail-open)。所以**不論工具鏈還是消費專案,每次改到程式的提交,刪除守衛都等於沒跑**。既有的解析測試(test_lumos.py 約 19605 行起)會整批翻紅,所以會被抓到;但凍結的 spec 已經指定了這個名字。
4. 改法:參數換個名字(例如 `skip_paths`),或先把函式裡的區域變數改名。「兩遍都跳過」這句順便寫成「第一遍在判 skip 那一行、第二遍在 `is_vault or is_excl` 那一行」,免得實作的人自己猜要插在哪。

## F3 RETIRE-IF ② 與 REVISIT ② 量的地方和需要的資料都不對:工具鏈自己的治理帳永遠是 0,帳裡也沒記是哪些檔
severity: minor
blocking: 否
引句:「②`grep 'vendored-skip=' docs/.governance-log.jsonl`」
file: `scripts/lumos:17822`
file: `scripts/lumos:1251`
1. 第 5 節規定:工具鏈本身(`_is_toolchain_repo` 為真)的 skip 是空的,所以工具鏈的 `docs/.governance-log.jsonl` 永遠不會出現 `vendored-skip=`。REVISIT ② 只寫相對路徑的 grep,沒像 ① 那樣講明要去 rtb 量(要發跨會談訊息)。在工具鏈的會談照做,拿到 0 筆,「累計 ≥20」永遠到不了,這條撤除條件等於死的。
2. RETIRE-IF ② 要「抽 5 次被跳過的檔、看同一次提交刪掉的名稱」。可是 note 只記支數,沒記是哪幾支。治理事件的 `commit` 欄是 `_append_governance_log` 在提交前掛鉤那一刻讀的 HEAD,也就是上一個提交,不是被守的那個;那次提交還可能後來被其他掛鉤擋下或改寫。照帳找不回「被跳過的檔、那次提交」。
3. 改法:REVISIT ② 明寫在 rtb 量;note 改記被跳過的路徑(截幾支就好),或寫明用 `commit` 往下找子提交的查法。

## F4 「同提交」清單的目錄名沒做 NFC,也沒用無損顯示,跟計劃名清單比「兩者」會對不上,遇到非 UTF-8 的名字會當掉
severity: minor
blocking: 否
引句:「`_nodehome_split_z` 拆;只收路徑至少四段」
file: `scripts/lumos:24488`
file: `scripts/lumos:27945`
file: `scripts/lumos:9765`
1. spec 說借的是「每支檔有家」那段寫法,可是那段拆完一律再做 `nfc(x)`(24488 行);spec 只寫 `_nodehome_split_z` 拆(它只做 `os.fsdecode`)。計劃名清單則是磁碟上的 `d.name`,也沒做 NFC。兩邊的正規化方式一不同(HFS+ 或其他 NFD 磁碟 + `core.precomposeunicode`,或檔案系統的寫法跟 git 裡存的不一樣),同一個中文卷證目錄會列兩次,一次標「同提交」、一次標「計劃名」,本來該標「兩者」、排最前面的,被排到後面。
2. `os.fsdecode` 碰到非 UTF-8 的位元組會留下替身字元(lone surrogate)。`_esc_clean` 只換控制字元,替身字元照留;lumos 沒有重設 stdout 的編碼方式,在一般 UTF-8 locale 下 print 會丟 UnicodeEncodeError,整個證據頁中斷。舊的計劃名路徑要名字比對得上才印;新的同提交路徑是**那次提交裡任何一個**卷證目錄都印,碰到的機會比較大。專案裡已經有 `_nodehome_show` 專門處理這件事。
3. 改法:兩個清單都先 NFC 再比、再去重;印之前先過 `_nodehome_show` 再 `_esc_clean`。

## F5 同提交清單沒檢查目錄現在還在不在,改名或刪掉的舊目錄會被列成證據
severity: minor
blocking: 否
引句:「證據頁全部列出、每個標來源(兩者、同提交、計劃名)」
file: `scripts/lumos:27944`
1. 計劃名清單來自磁碟上的 `iterdir`,一定是現在還在的目錄。同提交清單來自那次提交的樹,後來整理卷證時改名或刪掉的目錄也會照列,標成「同提交」。
2. 人從清單挑一個、寫進 valid_under → `lumos set` 不驗路徑 → 筆記裡的證據指向一個不存在的目錄。範本不自動填,所以不會自己寫進去,但這份清單就是讓人挑的。
3. 改法:同提交的目錄在磁碟上不存在時加註「(現在不在了)」,或者直接不列。

## F6 新字樣照字面組出來,「預告句」會重複兩次
severity: minor
blocking: 否
引句:「找不到〈那一種〉的預告句——可能已經是轉正後的說法(不用改),或被手改過(看一下)」
file: `scripts/lumos:12552`
file: `scripts/test_lumos.py:50781`
1. 〈那一種〉在兩處都是從 `_GUARD_PROSE_NAMES` 取的,值是「摘要的 TEST 預告句」「摘要的 WHY 預告句」,本身就帶「預告句」。照字面組出來是「找不到摘要的 TEST 預告句的預告句——…」。
2. 如果實作的人為了避開重複去改 `_GUARD_PROSE_NAMES`(拿掉「預告句」),既有測試 `t_guard_settle_rewrites_planned_prose` ⑥ 斷言的是 `"找不到摘要的 TEST 預告句" in r2.stdout`,會翻紅。spec 沒提這支既有斷言。
3. 改法:字樣寫成「找不到〈那一種〉——可能已經是…」,不要再接「的預告句」。既有斷言還是對得上。

## F7 範本改成不自動填之後,還在講自動填的既有測試與前一份計劃的撤除條件沒列進要改的地方
severity: minor
blocking: 否
引句:「範本句的卷證一律放 `<卷證>` 佔位字(不自動填)」
file: `scripts/test_lumos.py:53489`
1. 既有的 `t_drift_fix_c4_evidence_then_replace` ② 斷言輸出裡有 `提交 {sha12};代碼審見 governance/review-reports/code-done`(自動填的範本)。改完會翻紅。spec 的條款與回退只講「新測試」,沒列這支要改斷言。另外它 ⑤ 拿 `tpl` 直接去 `lumos set`:如果改成從輸出擷取範本,就會被第 2 節擋下。
2. `Projects/存量漂移改法_計劃` 的 RETIRE-IF ③(「c4 在修復帳裡照抄證據範本(`template_used: true`)的不到一半」)在 c4 改走 `lumos set` 那時就量不到了;這份再把範本改成一定帶佔位字、照抄一定被擋,這條從結構上就不可能成立。這份把那篇列在 related,卻沒標它 superseded,也沒拿自己的 RETIRE-IF ① 取代它。到期時會有人去量一條量不到的條件。
3. 改法:「做」或「回退」節列出要改這支既有測試;在前一份計劃的那條 RETIRE-IF 旁邊註明被本計劃的 RETIRE-IF ① 取代。

## 逐節結論

- 第 1 節(c4 卷證目錄):F4、F5、F7。git 指令本身實測沒問題:`show -z --name-only --diff-filter=AR --format=` 輸出沒有前導空行,中文路徑用 NUL 分隔、原樣;沒加 `-M` 也不影響,因為不論有沒有偵測改名,新路徑都會落在 A 或 R 裡。四段路徑取第三段、repo 根用 `_vault_repo_root`(找 .git 的那一層),跟 `git show` 給的根目錄相對路徑一致。排序規則與「>3 個」的標註照字面做得出來。證據頁與 `_drift_fix_hint` 的 c4 提示句(「列證據、範本與預填好的 lumos set 整欄指令」)沒有引用自動填;要改的是 `_drift_c4_print` ② 的標題字樣、`_drift_c4_evidence` 的 docstring,以及 F7 那支測試。
- 第 2 節(set 多擋兩個佔位字):已讀,無 finding。查證:圖譜裡所有 valid_under/revalidate_when 的值(掃開頭欄位,帶角括號的 10 項)沒有 `<sha>` 或 `<卷證>`;test_lumos.py 裡也沒有這兩個字串,既有的 c4 測試 ④⑤ 不受影響(④ 仍只含 `<整項新內容>`,⑤ 的值沒有佔位字)。`_set_conditions_locked` 只有 `cmd_set` 在 COND_KEYS 那條路上呼叫,沒有其他自動寫入的路徑會被誤擋。
- 第 3 節(c1 與 settle 訊息):F6。`_guard_settle_missing_say` 有兩個呼叫點(pass 補改與第一次轉正),改這一支就兩處都改到;c1 的 msg 只拿來印,沒有別處解析「沒改」。
- 第 4 節(c3 理由):已讀,無 finding。接線照字面可行:`_drift_fix_args_err` 已經先用 `_drift_fix_reason_ok` 驗長度與單行(`--reason ""` 會被擋);`_DRIFT_PLACEHOLDER_RE` 本來就認 `<sha>`、`<卷證>`、`<為什麼…>`;補上理由的那一行會經過 `texts` 送進 `_drift_fix_shape_err`,帶程式行號的理由在寫檔前就會被擋,跟 c2 一樣。
- 第 5 節(刪除守衛):F2、F3。`_is_toolchain_repo` 認 `skills/lumos-project-notes/SKILL.md`,工具鏈本體與它的 worktree 都是真,消費專案(安裝時不複製 skills/)是假,判定正確。`_VENDORED_ALL` 是精確路徑:消費專案自己放在 `scripts/hooks/` 底下、不同名的檔不會被跳過。要誤跳過,得是消費專案自己的程式剛好放在清單上的確切路徑;但刪除守衛是從工具裝進去的 `scripts/hooks/pre-commit` 呼叫(`core.hooksPath=scripts/hooks`),安裝時 `_vendor_toolchain` 會用來源蓋掉清單上的每一支檔,所以會跑刪除守衛的專案,那個路徑上一定是工具的檔。剩下的就是「消費專案自己改工具檔」,已寫在誠實界線,也有 REVISIT。

## ★INVARIANT★ 逐條
- Systems/guard-kill 第 20 行(guard kill 回傳碼的優先序)、第 21 行(--json 只印一行合法 JSON):不影響,這份只改 guard settle 的提醒字樣,guard kill 的程式碼一行都沒碰。
- Systems/存量漂移守衛、Systems/lumos-cli-write、Systems/delguard:沒有 ★INVARIANT★ 行。delguard 的「永遠回 0、fail-open」寫在 docstring、不是合約行;照 F2 的字面實作不會打破回 0(錯誤被吞),但守衛會整個失效。

## 實務隱患
- 不可逆:沒有。只改輸出、檢查與 note 字樣,revert 就回去。
- 資安:有碰到。目錄名印到終端前過 `_esc_clean`,控制字元擋得住;替身字元擋不住(F4),不過那是當掉,不是注入。
- 效能:有碰到。多兩次 git 查詢,各 20 秒逾時(`_lens_git` 與 `_plan_first_commit` 的逾時參數);`_git_is_shallow` 沒設逾時,這是既有的,本案沒有變差。
- 併發:沒碰到。沒有新增寫入路徑。
- 守衛面:有碰到。F2 照字面做會讓刪除守衛全面降級;F1、F3 會讓撤除條件量錯或永遠量不到。
- 金流、對外送出:不碰(本機命令列工具)。

最高等級:major;blocking 共 2 條
