# 前置掃描 漂移修法補強_計劃 r1

路徑簡寫:程式 = `scripts/lumos`(clone-ns 內)。

## ① 未定義的詞
1. 「REVISIT:2026-11-30 量上面兩個數(修復帳裡 c4 的 reports 欄位空不空、有沒有回報)」→ 修復帳目前沒有 `reports` 欄位;〈做法〉第 2 節寫入時只記 `template_used`,沒說要把找到的卷證目錄記進帳。RETIRE-IF ① 的「查不到」比例因此量不到。要嘛在做法裡加「帳記 reports 與找法(同提交/退回)」,要嘛改量法 → 佐證:`_drift_fix_record` 只帶 `**res["extra"]`(`scripts/lumos:28125` 一帶)、全檔 grep 無 `reports` 帳欄位,只有 c4 證據 dict 的 `reports`(`scripts/lumos:27950`)。
2. 「修復帳記一筆(`template_used` 看有沒有一項等於範本句)」→ `template_used` 是新欄位,計劃沒定義寫在哪(`res["extra"]`?)、範本句「等於」比對是整句相等還是包含、比對前有沒有 strip → 佐證:全檔 grep 無此詞(新詞);`_drift_fix_record` 的欄位來源 `scripts/lumos` 的 `rec = {... **res["extra"]}`。
3. 「`drift fix --kind c4 --values <各項…>`」→ `--values` 是新旗標,〈做法〉沒提要加 argparse(`drf.add_argument`)、`_DRIFT_FIX_OPTS`、`_DRIFT_FIX_ALLOWED["c4"]`(現為 `set()`,會被「不收 --values」擋掉)。屬漏列而非未定義,但實作必動 → 佐證:`scripts/lumos:27678-27680`、`scripts/lumos:37587-37596`。
4. 「〈做法〉第 4 節」引用:〈範圍〉「[[Projects/存量漂移防線_計劃]]〈做法〉第 4 節」→ 本審材沒附該計劃,無法核對章節存在(筆記檔在,節數未驗)。

## ② 壞引用
已掃:三篇 related 與〈不做〉引用的 `Projects/存量漂移改法_計劃`、`存量漂移防線_計劃`、`code側刪除傳播守衛_計劃`、`舊句偵測實驗_計劃` 皆存在;lands_in 三篇 `Systems/存量漂移守衛`、`lumos-cli-write`、`guard-kill` 皆存在;函式 `_plan_first_commit`(5865)、`_nodehome_git`(23621)、`_set_conditions_locked`(15128)、`_vendored_state`(17765)、`_vendored_skip`(17833)、`cmd_delguard_check`(29423)、`_drift_sh`(27630)、`_esc_clean`(9765) 皆存在。
1. 「`_conditions_rewrite(lines, e, key, vals) → (改後行, 錯誤)`」與條款 [test:t_drift_c4_reports_from_first_commit] 等六個測試名 → 目前不存在(屬計劃要新增,非壞引用,僅註記;實作時要在 scripts/test_lumos.py 落)→ 佐證:grep 無。
2. 「c1 訊息的程式在 guard 區段」→ 半對:訊息字串在 drift 區段 `_drift_fix_c1`(`scripts/lumos:27843`),要判斷的 `missing` 來自 guard 區段 `_guard_settle_rewrite`(`scripts/lumos:12134`)。同時 guard settle 也印一句「找不到…(被手改過?)」(`scripts/lumos:12558`),〈範圍〉③只講 c1,沒說 settle 那句要不要一起改(見 ③)。

## ③ 範圍自相矛盾
1. 〈範圍〉「c3 收 `--reason`,寫進補的那一行」vs〈做法〉「有給就接在補的那一行最後(『…,參考 [[X]]:<理由>』)」→ 理由格式只給了「有 --by 且非 pass」的例句;`--by` 沒給、或 status=pass(「由 [[X]] 解決」)時理由接在哪、標點怎麼接沒寫 → 佐證:`_drift_fix_c3` 的 `txt` 三種分支(`scripts/lumos:27907-27925`)。
2. 〈做法〉2「c4 帶 `--values` 時要做乾淨檢查(會寫檔);不帶時照舊不做」vs〈範圍〉「`--dry-run` 只印不寫」→ 現行 `_drift_fix_load` 是「`--dry-run` 或 kind==c4 就不做乾淨檢查」;計劃只講 c4 要改,沒講 `c4 --values --dry-run` 是否做(依既有慣例不做)。條款 S2 也沒寫這格。→ 佐證:`scripts/lumos:27790-27792`。
3. 〈條款〉S3「`lumos set` 整欄改…行為應與拆函式前完全相同」vs〈做法〉2 把「空值、多行、佔位字」檢查移進 `_conditions_rewrite` 回 (行, 錯誤)→ 原本這些檢查是「印到 stderr 並 return 2」;拆後由誰印、印什麼字,計劃沒定。要「完全相同」得保留原訊息字串(測試若比對 stderr 會紅)。→ 佐證:`scripts/lumos:15134-15147`。
4. 〈回退〉「c4 退回只印 `lumos set` 指令」vs〈範圍〉④「證據頁印的指令改成 drift fix 那一條」+〈做法〉「證據頁只印 drift fix 那條」→ 回退後證據頁該印哪條(舊的 set 指令)得靠還原提交,計劃寫成「各自獨立可單獨還原」略過了 `_drift_c4_print` 內容也被改。輕微。
5. 〈誠實界線〉「刪除守衛…清單壞掉時 `_vendored_state` 判不一致,照舊抽」vs〈實務隱患〉「守衛面(只提醒不擋)」→ 一致,無矛盾,僅註記。

## ④ 機械宣稱驗語意

### 語意對得上
- 「`_plan_first_commit`」回第一次進歷史的提交 sha(`git log --diff-filter=A --format=%H -- <路徑>` 取最舊一筆),沒有回 None,`timeout` 參數逾時也回 None;c4 證據現在已用 `timeout=20` 呼叫 → `scripts/lumos:5865-5875`、`27939`。
- 「走 `_nodehome_git`、有逾時」→ 對:它包 `_lens_git(..., binary=True)`,固定 `timeout=20`,逾時/OSError 回 None,rc≠0 也回 None,輸出是位元組 → `scripts/lumos:23621-23627`、`33068-33080`。
- 「`_set_conditions_locked` 可拆出不寫檔的一段」→ 大致對:前半驗證 → `load_raw_for_edit` 讀 → 算 `fm`(整欄換/插入)→ 最後才 `atomic_write_verify`,中間算 `fm` 段不碰檔,純以 `lines, e, key, vals` 為輸入 → `scripts/lumos:15128-15160`。(注意:驗證段在 `load_raw_for_edit` 之前,拆出的函式要不要含驗證見 ③-3。)
- 「`lumos set` 呼叫兩段」→ `cmd_set` 在 `_vault_write_lock` 內經 `_cmd_set_locked` 進 `_set_conditions_locked`,拆函式放這裡不影響鎖 → `scripts/lumos:15078-15086`。
- 「值裡留著 `<整項新內容>` 時擋下」→ 已存在於 `_set_conditions_locked` 開頭(`_SET_COND_SLOT`);拆到 `_conditions_rewrite` 後 drift fix 自動繼承 → `scripts/lumos:14620`、`15134`。
- 「`cmd_delguard_check` 抽名稱的位置」→ 抽名稱不在 `cmd_delguard_check`,在它呼叫的 `_delguard_parse_diff(r.stdout, gr_rel)`(對 `git diff --cached` 逐檔抽 `-` 行 token);`cmd_delguard_check` 只取 `parsed["tokens"]` → `scripts/lumos:29470` 附近、`29222-29300`。「跳過某些檔」的最佳落點是 `_delguard_parse_diff` 的 `_flags`/`excl` 判定(兩遍對稱要一起改)。
- 「c1 訊息『找不到{names},沒改』的來源」→ 對:`_drift_fix_c1` 用 `_guard_pass_rewrite` 回傳的 `missing`(= `_GUARD_PROSE_KINDS` 中沒被改到的種類)組成 → `scripts/lumos:27835-27843`、`12134-12172`。
- 「c2 的 `--reason` 規則(一行、4 到 200 字、擋提示佔位字)」→ 對:`_drift_fix_reason_ok`(`4 <= len <= 200` 且單行)在 `_drift_fix_args_err` 對所有 kind 共同套用(只要 `reason` 非 None);佔位字檢查 `_drift_placeholder_err` 只在 `_drift_fix_c2_args` 裡呼叫 → `scripts/lumos:27689-27738`。
- 「`_drift_sh`」→ 對:只由文字/數字/CJK/`./@%+=:,-` 組成原樣印,其餘 shlex 加引號,`node=True` 時 `-` 開頭補 `./` → `scripts/lumos:27630-27642`。
- 「`_esc_clean`」→ 對:控制字元(含 C1)換空格、超長截斷(預設 200)→ `scripts/lumos:9765-9770`。
- 「`drift fix` 既有流程:乾淨檢查、鎖內寫入、寫後驗證、修復帳、`--dry-run`、形狀擋」→ 順序與 `cmd_drift_fix` 一致;c4 回 `(None, None)` 由呼叫端直接 `return 0`,要改成有 `res` 時往下走 → `scripts/lumos:28157-28190`。

### 語意對不上
1. 計劃〈PRIOR-ART〉③與〈做法〉5「借既有 `_vendored_state` / `_vendored_skip`(…)」能在提交時(staged)判工具檔跟安裝清單一致
   - 問題:`_vendored_skip(root, diff_range)` 需要一段 diff 範圍(內部 `_diff_range_ends`),pre-commit 的 staged 沒有範圍,不能直接呼叫。`_vendored_state(root, ref=None)` 的 `ref=None` 讀的是工作目錄不是索引;讀 staged 要傳 `ref=""`(組成 `git show :path`)——repo 內筆記形狀擋就是這樣用(`_vendored_state(root, "")[0]`)。另外它跟 `_is_toolchain_repo` 判斷要自己接(`_vendored_skip` 內含、直接呼叫 `_vendored_state` 沒有)。
   - 修改前:「借既有 `_vendored_state` / `_vendored_skip`(推送閘判…那一支),刪除守衛抽被刪名稱時跳過跟安裝清單一致的工具檔」
   - 建議改後:「刪除守衛在提交時用 `_vendored_state(root, "")[0]`(讀索引 `:path` 與 `:.lumos/vendored.json`,同 `_nodehome` 筆記形狀擋那兩處用法),外面先過 `_is_toolchain_repo(root)`(工具鏈本體回空集合);不用 `_vendored_skip`(它要 diff 範圍)。再在 `_delguard_parse_diff` 加一個 `skip` 參數,`_flags` 的 `excl` 判定與第一遍(`+` 行回收表)、第二遍都用同一個 skip」。
   - 佐證:`scripts/lumos:17765-17800`(ref 分支)、`17833-17845`、`24477`、`24609`。
   - 附帶:被刪的工具檔(拆除工具鏈)在索引已不存在,`_vendored_state(root, "")` 的 present 不含它,不會跳;`_vendored_skip` 有處理「起點原封不動、終點已刪」而 staged 版沒有——〈做法〉5 沒交代這格,拆除工具鏈的提交仍會誤報。
2. 〈做法〉1「`git show --name-only --diff-filter=A <提交>`,走 `_nodehome_git`」列加進來的檔
   - 問題 a:少 `--format=`,輸出開頭會帶提交標頭(hash、作者、訊息),混進目錄名收集;應加 `--format=` 或用 `diff-tree`。實測 `git show --name-only --diff-filter=A --format= <sha>` 才是純檔名。
   - 問題 b:預設 `core.quotePath=true`,中文/NFD 目錄名會被輸出成 `"governance/review-reports/code-\346..."`(實測本 repo 的 e80f0ce1 就是這樣),`_nodehome_git` 不會幫你關;要 `-c core.quotePath=false`(`_plan_first_commit` 有,`_nodehome_git` 呼叫端沒有)或 `-z`(`_nodehome_split_z` 現成)。這個 repo 的卷證目錄幾乎全是中文名,不處理等於找法永遠找不到。
   - 問題 c:合併提交(merge)`git show --name-only` 預設是 combined diff,`--diff-filter=A` 下通常空;只在第一次進歷史的是 merge 時會落到退回路徑,計劃沒講。
   - 問題 d:`_nodehome_git` 是位元組輸出、失敗回 None,不含「路徑不是 UTF-8」的處理以外的解碼;呼叫端要 `os.fsdecode`(`_nodehome_split_z` 已做)。
   - 修改前:「列那個提交加進來的檔(`git show --name-only --diff-filter=A <提交>`,走 `_nodehome_git`、有逾時)」
   - 建議改後:「`_nodehome_git(root, "-c", "core.quotePath=false", "show", "-z", "--name-only", "--diff-filter=A", "--format=", <提交>)`,用 `_nodehome_split_z` 拆;None 視為找不到,退回計劃名比對」。
   - 佐證:`scripts/lumos:23621`、`23636-23640`;實測 `git show --name-only --diff-filter=A --format= e80f0ce1`(主 repo)輸出中文路徑被八進位跳脫。
3. 〈PRIOR-ART〉①與〈誠實界線〉第一條「專案規矩『程式、筆記、審查卷證放同一個提交』」
   - 問題:規矩原文為「程式、圖譜筆記、審查卷證放同一個提交;做到一半的本機提交,推之前壓成一個」,對得上;但同一份 CLAUDE.md 另規定「過代碼審的功能多一個帳本提交」(訊息 `chore(lumos): 記錄代碼審通過`,只准改帳本)。實測該帳本提交只動 `docs/.governance-log.jsonl`,不含 review-reports,所以卷證仍在功能提交;不矛盾。但「驗證紀錄第一次被提交」的提交若是只提交 Verification 的小提交(規矩允許「一個功能一個提交」但驗證紀錄常另存),同提交也不一定含任何卷證目錄。這正是計劃已有的退回路徑。另外該提交若是壓縮後的大提交,會同時收進「別的計劃的卷證目錄」→ 過多命中,〈做法〉1 只去重、沒說怎麼縮小(例如再與 `plan_refs` 比對交集或標明「同提交找到 N 個」)。
   - 修改前:「有就用它;沒有(驗證紀錄跟卷證分開提交、或 shallow)才退回現在的計劃名比對」
   - 建議改後:加一句「同提交找到的目錄若超過 N 個(例 3),證據頁標『同提交,可能含別的計劃的卷證』並仍列出,由人判斷」,或與 `_drift_c4_key` 比對結果取交集優先。
   - 佐證:`/Users/enzo/harness/lumos-toolchain/CLAUDE.md` 提交與推送一節(「程式、圖譜筆記、審查卷證放同一個提交」);`git show --stat 65de176a`(帳本提交只動 governance-log);`git show --stat e80f0ce1`(功能提交含 review-reports 與 replay)。
4. 〈做法〉3「在就講『已經是轉正後的說法,不用改』」能靠現有程式判斷「那一種已是轉正後說法」
   - 問題:目前只有 `why-done`(WHY 行尾「(日期 已轉正)」)與 `settle-del`(下一行已是手補的「已轉正」段)被 `_guard_prose_ops` 辨認;`TEST:[日期] 預告已轉正…` 沒有辨認器(算出的 `missing` 只是「沒看到預告句」,不知道是已轉正還是被手改);`whynot` 的轉正後說法是「預告當時…」開頭,`settle` 的是「(日期 已轉正)」,計劃只講 TEST 與 WHY 兩種。四種 `_GUARD_PROSE_KINDS` 裡兩種沒定義「轉正後說法」怎麼辨認。
   - 修改前:「找不到某種預告句時,再看那一種的『轉正後說法』在不在(摘要的 TEST 行已是…、WHY 行尾已有…):在就講…,不在才講…」
   - 建議改後:列全四種各自的轉正後辨認式(TEST:`^\s*TEST:\[\d{4}-\d\d-\d\d\] 預告已轉正`;WHY:沿用 `why-done`;whynot:`^\s*預告當時`;settle:`^\s*\(\d{4}-\d\d-\d\d 已轉正\)` 或 `settle-del` 已判),放進 guard 區段共用函式;`guard settle` 那句「找不到…(被手改過?)」是否一併改要寫進〈範圍〉。
   - 佐證:`scripts/lumos:12115-12132`、`12134-12172`(產出格式)、`27835-27843`、`12556-12558`。
5. 〈做法〉2「c4 帶 `--values` 時要做乾淨檢查」「走 drift fix 原本的乾淨檢查、鎖內寫入、寫後驗證、修復帳」
   - 問題:語意大致成立,但 `res` 要符合 `_drift_fix_write/_verify/_record` 用的鍵:`new`、`key`、`check`、`handled`、`extra`、`texts`、`msg`(`deps` 選填);`check` 要是 `lambda f: _conds(f.get("valid_under")) == vals`(拆函式後仍要傳出這個 lambda,`_conditions_rewrite` 回 `(改後行, 錯誤)` 兩值不夠,得另回 check 或由 drift 端自己組);`handled` 用 `_drift_no_kind("c4")`;`texts` 傳 `[(項, "frontmatter")]`?——`_drift_fix_shape_err` 的 region 參數是 `"body"` 或 `"summary"` 這類區域名,valid_under 屬開頭欄位,計劃寫「形狀擋(自由文字)」但沒說 region 用什麼,`_ns_check_line` 對開頭欄位是否適用未驗。→ 這一格計劃沒寫清,屬「借既有就能做」但差一段接線,不是直接可用。
   - 修改前:「用 `_conditions_rewrite` 算改後內容 → 形狀擋(自由文字)→ …」
   - 建議改後:「`_conditions_rewrite(lines, e, key, vals) → (改後行, 錯誤)`,並在 drift 端以 `lambda f: _conds(f.get('valid_under')) == vals` 當 `check`;形狀擋的 `texts` 指定 region(先確認 `_ns_check_line` 對開頭欄位的行為,不行就只對 `--values` 各項做 `_drift_one_line` 與佔位字檢查,略過形狀擋並在計劃說明)」。
   - 佐證:`scripts/lumos:15150-15158`(check lambda)、`28157-28190`(res 鍵)、`28040-28060`(`_drift_fix_shape_err`)。
6. 〈範圍〉⑤/〈條款〉S6「消費專案提交時…被改過的工具檔照舊抽」
   - 問題:`_vendored_state` 的「原封不動」定義是「檔名在精確清單且內容指紋等於安裝時記下的指紋」;提交時若 `.lumos/vendored.json` 也在同一提交被更新(執行 `lumos update` 後提交),索引的清單與索引的檔會一起變,判成一致——正是要跳過的情形(對)。但若專案只改了工具檔、沒更新清單,判不一致→照抽(對)。不矛盾,僅註記:工具檔在 `_DELGUARD_EXCLUDE_DIRS` / `_DELGUARD_PROSE_DIRS` 目前不排除 `scripts/`,所以確實會誤報(rtb 案例成立)。
   - 佐證:`scripts/lumos:17773-17777`、`29260-29270`。
