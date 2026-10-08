severity: major

# 設計審 r1 正確性-opus 席:漂移修法補強_計劃

審材:`governance/review-reports/漂移修法補強/r1-snapshot.md`(凍結)。對照程式碼:clone-ns `f43eea4a` 的 `scripts/lumos`。實驗用 /opt/homebrew/bin/python3 以 SourceFileLoader 載入 `scripts/lumos` 直接呼叫函式,以及在 clone-ns 歷史上唯讀跑 git 模擬第 1 節的找法;沒改任何 repo 檔。

## F1 「有交集就只列交集」會把代碼審卷證目錄濾掉,範本句「代碼審見」指到設計審目錄
severity: major
blocking: 是
引句:「找法順序:同提交找到的目錄跟計劃名比對(`_drift_c4_key`)有交集就只列交集」
file: `scripts/lumos:27949`
file: `scripts/lumos:27945`
1. 範本句固定寫成「提交 <sha>;代碼審見 <目錄>」(`_drift_c4_evidence`),所以要找的是**代碼審**的卷證目錄。本 repo 的代碼審目錄慣例是 `code-<短名>`(275 個卷證目錄裡有 140 個是 `code-` 開頭),短名常常跟計劃名不同;設計審目錄才照計劃名取。
2. 實測:把第 1 節的找法照字面套到 clone-ns 全部 206 篇驗證紀錄(第一次加入的提交 → `show -z --name-only --diff-filter=A --format=` → 取 `governance/review-reports/<目錄>/`,再用 `plan_refs` 做 `_drift_c4_key` 子字串比對)。同提交找到目錄、而且跟計劃名有交集的 12 篇裡,有 5 篇的交集丟掉了同提交的目錄,其中 4 篇丟掉的是 `code-` 開頭的代碼審目錄:
   - `2026-09-29_代碼審資料狀態鏡頭`:同提交 `code-資料狀態鏡頭、代碼審資料狀態鏡頭、代碼審資料狀態鏡頭-std、代碼審資料狀態題組` → 交集只剩 `代碼審資料狀態鏡頭、代碼審資料狀態鏡頭-std`(設計審),`code-資料狀態鏡頭` 被濾掉;
   - `2026-09-29_前端卡小實驗`:`code-角色鏡頭` 被濾掉,只留 `代碼審前後端角色鏡頭`;
   - `2026-09-11_代碼審資安席落地`:`code-資安席與多平台指令` 被濾掉;
   - `2026-09-11_推播漏網量測實作`:`code-推播漏網量測` 被濾掉;
   - `2026-09-18_收工點名改問版本控制`:`收工點名改量檔案樹` 被濾掉。
3. 也就是說,同提交找法正是在這些篇裡**找到了**舊的計劃名比對找不到的代碼審目錄,交集規則又把它剔掉;範本句變成「代碼審見 <設計審目錄>」,人照範本貼就寫進一條錯的證據。
4. 修復帳上這幾筆的 `reports_via` 會記成 `same-commit`,RETIRE-IF ① 只量 `none` 的比例,會把「找錯」算成「找到」,REVISIT 那天量不出這個問題。
5. ⚠ 同族:如果驗證紀錄第一次進歷史的是「整批匯入」提交(程式碼已經知道有這種情形,見 `_guard_pass_commit_date` 的「整批匯入或搬過目錄」),同提交會列出當時所有卷證目錄;沒交集時整批列出並記成 `same-commit`。
6. 建議:不要用交集**濾掉**東西,改成**排序**(`code-` 開頭的、跟計劃名比對得上的排前面),全部列出;或者至少把 `code-` 開頭的同提交目錄一律保留。S1 的測試要加一個「同提交有 `code-短名` 加上設計審同名目錄」的案例。

## F2 `--values` 沒擋範本本身的佔位字 `<卷證>`、`<sha>`,照貼範本會把佔位字寫進筆記,還記成 template_used
severity: major
blocking: 是
引句:「`--values` 各項已由 `_conditions_rewrite` 擋空值、多行、佔位字」
file: `scripts/lumos:27949`
file: `scripts/lumos:27619`
file: `scripts/lumos:15134`
1. `_conditions_rewrite` 從 `_set_conditions_locked` 搬過來的佔位字檢查只認 `_SET_COND_SLOT`(`<整項新內容>`)。
2. 範本句在找不到卷證時會長成 `…;代碼審見 <卷證>`,查不到第一次提交時會是 `提交 <sha>;…`。RETIRE-IF 自己也預期 `none`(兩種找法都查不到)會常見。
3. 證據頁要人把 `<整項新內容>` 換成「那一項改寫後的整句」,範本句是參考。人直接把範本句貼進去時,`<卷證>` 會原樣寫進 valid_under;`template_used` 的算法是「去頭尾空白後等於範本句」,所以這筆會記成 true。
4. 工具鏈本來就有專擋這兩個字串的 `_DRIFT_PLACEHOLDER_RE`,它的說明寫明是給「c4 證據頁真的印過、而且會被貼進 --new」的情況用的。`--values` 正是舊 `--new` 的接班路徑,spec 卻沒接上這道檢查;第 4 節把佔位字檢查抽成 c2、c3 共用時,也沒把 c4 算進去。
5. 建議:`--values` 每一項也要過 `_drift_placeholder_err`;S2 的「擋下不寫」要加上 `<卷證>`、`<sha>`,也要有對應的測試案例。

## F3 寫進去之後才驗「c4 消失」,人寫的新值還含「未提交」這類字時,會留下改了、沒記帳、又叫人 checkout 的狀態
severity: major
blocking: 是
引句:「驗證磁碟內容等於算出的內容且 c4 消失 → 修復帳」
file: `scripts/lumos:26376`
file: `scripts/lumos:28105`
file: `scripts/lumos:27776`
1. c4 的判定是把 valid_under 所有項接起來,只要含 `未提交`、`還沒提交`、`uncommitted` 任一個就算(`_drift_state_findings`)。`--values` 是人寫的自由文字,改寫時留下原字的情形很自然,例如「原本在未提交的工作樹上驗、現已提交 abc123」。
2. 照 spec 的流程,這個值會通過空值、多行、佔位字、`_drift_one_line` 的檢查,鎖內也寫入成功;接著 `_drift_fix_verify` 的 `handled=_drift_no_kind("c4")` 為假,於是印出「寫入後內容跟預期不同(或這一筆還沒處理掉)——工具不自動還原…跑 git checkout -- 退回」,回 2,**修復帳不記**。
3. 結果:筆記已經改了、帳上沒這筆,工具還叫人 checkout(這會連同這篇之前用 drift fix 改過、還沒提交的內容一起退掉);這時不管是再修同一篇的其他項,或是改用 c4 重跑,都會先被乾淨檢查擋成「有未提交的改動(不是 drift fix 自己留下的)」。
4. 以前 c1、c2、c3、c5 寫的是工具自己產的固定句子,「寫完 c4 還在」只可能是工具的錯,事後驗證合理。c4 是第一個由人給內容的種類,這一步會因為輸入而失敗,應該在寫入**之前**就擋掉。
5. 建議:算完改後內容之後、在 `--dry-run` 輸出之前,用改後文字跑一次 c4 判定(或至少檢查 `vals` 有沒有這三個字);還在就回 2,講清楚「新值裡還有 X,判定會以為還沒提交」,檔案不動。S2 也要補上這個案例。

## F4 `_conditions_rewrite` 只回傳三道檢查的錯誤,整欄算法裡 `fmt_scalar` 丟出的 ValueError 在 drift fix 路徑上沒人接,會直接噴 traceback
severity: major
blocking: 是
引句:「`_set_conditions_locked` 拆出 `_conditions_rewrite(lines, e, key, vals) → (改後行, 錯誤訊息)`」
file: `scripts/lumos:14693`
file: `scripts/lumos:28172`
file: `scripts/lumos:38098`
1. 「算新開頭欄位那段」會呼叫 `fmt_scalar`;值需要加引號、同時又含單引號和雙引號(或反斜線)時,`_yaml_quote` 會丟 ValueError。實測 `fmt_scalar("valid_under", '代碼審見: "code-x" 與 Enzo\'s 裁定')` → ValueError「同時有單引號、又有雙引號或反斜線…」。
2. `lumos set` 走得通,是因為 main 在 set 那一支有 `except (ValueError, RuntimeError)`,會印「擋下:…」。drift 那一支沒有 try,`cmd_drift_fix` 在 `_DRIFT_FIX_COMPUTE[kind](cx)` 周圍也沒有 try。所以 `drift fix --kind c4 --values <這種值>` 會以未處理例外結束(rc 1,印出 traceback),而不是 spec 說的「有錯回 2」。
3. 這支檔自己的慣例是「寫入例外一律轉成錯誤」(見 `_drift_fix_write` 的說明)。
4. 建議:`_conditions_rewrite` 把 ValueError 也轉成它回傳的錯誤訊息,set 端照「擋下:{訊息}」印(跟現在 main 印的字一樣,S3 不受影響);S2 的測試要加一個兩種引號並存的值。

## F5 讀檔提前到檢查之前,「值不合法、檔案又讀不了」時 set 的訊息會變,違反 S3 的「完全相同」
severity: minor
blocking: 否
引句:「`_set_conditions_locked` 讀檔 → 呼叫它 → 有錯就照原樣印到 stderr、回 2」
file: `scripts/lumos:15130`
file: `scripts/lumos:14915`
1. 現在的順序是:先驗值(佔位字 → 空值 → 多行),再 `load_raw_for_edit`。照 spec 改成先讀檔、再在 `_conditions_rewrite` 裡驗值。
2. 例:對一篇 CRLF(或帶 BOM、欄位區塊沒收尾)的筆記跑 `lumos set X valid_under ""`。舊版印「擋下:valid_under 的每一條都不能是空的…」;新版印「擋下:這個檔的換行是 Windows 式(CRLF)…」。兩邊都回 2,但訊息不同。S3 寫的是「行為與錯誤訊息應與拆函式前完全相同」。
3. 建議:三道值檢查改成不需要 lines 的獨立函式,先驗值、再讀檔;要不就把 S3 的範圍收窄成「單一錯誤的輸入」。另外 S3 跟 S2 綁的是同一支測試,這支測試要真的對照改之前的訊息原文(黃金字串),不然測不出「一字不變」。

## F6 check 裡的 `vals` 跟 `_conditions_rewrite` 內部的去空白口徑沒講清楚,值帶頭尾空白時會被誤擋成「讀回來不一樣」
severity: minor
blocking: 否
引句:「`check=lambda f: _conds(f.get("valid_under")) == vals`」
file: `scripts/lumos:15133`
file: `scripts/lumos:14972`
1. 現在的 set 會先做 `vals = [str(v).strip() …]`,寫入用的是去掉空白的值,檢查也是拿去掉空白的值比。spec 在 drift 那端直接用 `vals`,沒說是 `o["values"]` 原樣,還是 `_conditions_rewrite` 正規化之後的版本;`template_used` 那句特地寫「去頭尾空白後」,暗示 `vals` 沒去空白。
2. 例:`--values " 提交 abc;代碼審見 code-x"`。寫進去的是去掉空白後的內容,`_conds` 讀回來也是去掉空白的,跟原樣的 `vals` 不相等 → `atomic_write_verify` 丟出「寫完讀回來檢查,valid_under 的值跟要寫的不一樣」→ 回報「寫不進去,筆記沒動」。一個合法的值被擋下,訊息還會誤導人。
3. 建議:`_conditions_rewrite` 多回傳它正規化後的 `vals`,drift 端的 check、`template_used` 與修復帳都用這一份。

## F7 接線點列得不齊:drift fix 參數表、c3 的允許表、c4 單一提示產生處
severity: minor
blocking: 否
引句:「加進 `_DRIFT_FIX_OPTS`,`_DRIFT_FIX_ALLOWED["c4"] = {"values"}`」
file: `scripts/lumos:38098`
file: `scripts/lumos:27680`
file: `scripts/lumos:27653`
1. `cmd_drift_fix` 收到的 `o` 是 main 在 38095-38098 一個鍵一個鍵組出來的,不是從 `_DRIFT_FIX_OPTS` 自動展開的。只照 spec 列的三處改,`o["values"]` 會永遠是 None:`--values` 被安靜吃掉,走回「只列證據」、回 0。測試要是直接呼叫 `cmd_drift_fix` 傳 dict,就測不出來。
2. 第 4 節沒寫要把 `_DRIFT_FIX_ALLOWED["c3"]` 加上 `"reason"`;不加的話,`_drift_fix_args_err` 會先回「--kind c3 不收 --reason」。
3. `_drift_fix_hint("c4")`(說明裡標了★提示的單一產生處★)現在印的是「列證據、範本與預填好的 lumos set 整欄指令(c4 不自己寫檔)」。改完之後這句會變成錯話,drift check、scan、doctor Z 都從這裡拿提示。spec 的第 2 節與回退節都沒列到它。

## F8 預填指令用 `as_list` 取各項,區塊寫法的 valid_under 會被併成一項,「其他項照抄」會把兩條前提合成一條
severity: minor
blocking: 否
引句:「要改的那項放 `<整項新內容>`、其他項照抄」
file: `scripts/lumos:27958`
1. 實測 `valid_under: |` 加上兩行(`在未提交的工作樹上跑`、`只測 macOS`):`as_list` 給出一項含 `\n` 的字串,`_conds` 給出兩項。證據頁 ④ 與預填指令都用前者;`_esc_clean` 把換行換成空白,所以第 ④ 段印成一項「在未提交的工作樹上跑 只測 macOS」。這一項含「未提交」,所以整塊被 `<整項新內容>` 取代,「只測 macOS」這條前提在指令裡消失了。人要是只改寫第一句,第二條前提就被 drift fix 刪掉,帳上看起來是一次正常的修復。
2. 同一段輸出經過 `_esc_clean(…, 2000)`,超長時會截斷並接上「…」,照貼會少掉項目,或多出一個「…」項。現在這兩點是 set 指令就有的老問題;這次 spec 把它們接進會寫檔、會記帳的路徑。
3. 建議:證據頁與預填指令改用 `_conds` 展開各項;預填指令不要截斷(參照 `_drift_git_cmd`「★不截斷★」的理由),太長就改講怎麼找。

## F9 刪除守衛的改動沒落在它自己的家節點
severity: minor
blocking: 否
引句:「刪除守衛在消費專案跳過跟安裝清單一致的工具自裝檔」
file: `docs/lumos-toolchain-knowledge/Systems/delguard.md:34`
1. `lands_in` 只列了存量漂移守衛、lumos-cli-write、guard-kill 三篇。刪除守衛的家是 `Systems/delguard`:它的 summary 寫著抽取規則,還有 `t_precommit_whitelist_drift_guard` 釘住的排除清單;正文的「已知殘項」也寫了「vendored 白名單源 repo 反轉語意」,第 5 節正好在處理這一條。
2. 照家規第 5 條,改到的行為要寫回管它的家。只寫進三篇 lands_in 的話,下一個讀 delguard 的人看不到「消費專案跳過工具檔、拆除提交照舊誤報」這條邊界,那條殘項也不會被收掉。
3. 建議:`lands_in` 加上 `Systems/delguard`,並寫明 `skip` 參數跟 `_DELGUARD_*` 排除清單是兩回事,不要併進去:併進去的話,`t_precommit_whitelist_drift_guard` 比對的第三份清單會漂移。

---

## 逐節

- 〈白話〉〈依據〉〈PRIOR-ART〉:①的前提見 F1;②③④與程式碼對得上。③(`_vendored_state(root, "")`)跟筆記形狀擋那兩處的用法一致,我查過 `scripts/lumos:24477` 與 `24609`。
- 〈範圍〉:已讀,無另外的 finding。
- 第 1 節:F1。另外核對過兩點。一是 `git show -z --name-only --diff-filter=A --format=` 的輸出第一筆就是路徑、沒有前導空行(實測 od),`_nodehome_split_z` 拆得乾淨。二是加了 `-z` 之後,quotePath 本來就不會跳脫(實測 `-c core.quotePath=true` 加 `-z` 印出來仍是中文);spec 對 quotePath 的理由不精確,但不會出錯,所以不列 finding。
- 第 2 節:F2、F3、F4、F6、F7、F8。`_drift_fix_load` 對 c4 不做乾淨檢查的條件要改成「沒帶 `--values`」,spec 已經寫到。
- 第 3 節:已讀,無 finding。逐條核對如下:`why-done` 在 `_guard_settle_rewrite` 裡已經當成 `why` 記進 seen,`settle-del` 也已經當成 `settle` 記進 seen,所以 WHY 與 settle-del 這兩種辨認只是多一層保險,不會讓已經改過的句子被認成找不到。TEST(`TEST:[日期] 預告已轉正`)與 whynot(`預告當時` 開頭)的辨認只可能對上 `_guard_settle_rewrite` 自己寫出來的句型,只有在 missing 時才會去問;還沒轉正的預告句會先被 `_guard_prose_ops` 認成 op,不會進 missing,所以不會出現「沒轉正卻被說成已轉正」。實作時,摘要那一行要先去掉縮排再比對。
- 第 4 節:F7 第 2 點。理由的接法(三種寫法最後都接「;理由:」)照字面做沒問題;接完的整行會進 `texts`,再過筆記形狀擋,理由裡寫程式行號的會被擋,這跟 c2 的橫幅行為一致。
- 第 5 節:F9。`_vendored_state(root, "")` 會用 `git show :<路徑>` 讀索引,清單用 `_json_at_ref(root, "", …)`,也是讀索引;提交時「更新工具檔、清單跟著一起 stage」才會跳過,只 stage 其中一個就照舊抽(寧可誤報),跟〈誠實界線〉說的一致。工具鏈 repo 靠 `_is_toolchain_repo` 不跳。這一步本身有 `_lens_git` 的 20 秒逾時,要放進 `cmd_delguard_check` 既有的 try 裡,例外才會落到 fail-open。
- 〈條款〉:S1 見 F1,S2 見 F2、F3、F4、F6,S3 見 F5;S4、S5、S6 已讀,無 finding。
- 〈回退〉〈實務隱患〉〈誠實界線〉〈合約候選〉:已讀。回退節沒列到 `_drift_fix_hint`,見 F7。

## 資料狀態

- 新舊互讀:修復帳在工具裡只有 `_drift_fix_last_sha` 在讀(`scripts/lumos:27755`),它只看 path、seq、after_sha256;舊資料列沒有 `reports`、`reports_via` 不影響它。clone-ns 裡沒有 `governance/drift-fixes.jsonl`,也就沒有舊的 c4 資料列。REVISIT 量數字時要把「沒有這個欄位」的列排除,不要算成 `none`。
- 寫一半:筆記寫了、帳沒記的情況,沿用既有的 `_drift_fix_record` 訊息;c4 多出一條「值本身讓驗證失敗」的路,見 F3。
- 同一篇連修:c1 → c4 靠修復帳指紋放行,沒問題。c4 → c4 重來時,第一次寫入之後 c4 已經消失,`_drift_current_finding` 會擋;這時只剩 `lumos set` 可用,但 set 不記帳,之後同一篇的 drift fix 會被乾淨檢查擋到提交為止。這是 spec〈誠實界線〉接受的取捨,不列 finding。

## 實務隱患

- 不可逆:不碰。寫入前的乾淨檢查保證 git 退得回來;F3 的情形也退得回來,只是訊息誤導。
- 金流:不碰(本機命令列工具)。
- 對外送出:不碰(只有本機 git 唯讀查詢)。
- 資安:碰到。從 git 歷史來的卷證目錄名只會印在證據頁(過 `_esc_clean`)與範本句,不會進照貼的指令,預填指令裡各項走 `_drift_sh`。刪除守衛的 skip 只認精確清單與內容指紋,消費專案把自己的程式取成工具檔名也躲不掉。沒有新的隱患。
- 守衛面:碰到。見 F9;skip 只跳「內容跟清單一致」的檔,方向是寧可誤報,正確。
- 效能:碰到。多一次 `git show` 加上 17 次 `git show :path`(刪除守衛),都有 20 秒逾時;刪除守衛要放進既有的截止時間與 try 裡(見第 5 節)。
- 併發:碰到。c4 寫入沿用鎖內比對位元組的做法,沒有新的寫入路徑。

## ★INVARIANT★ 逐條

- `Systems/guard-kill` 第 20 行(guard kill rc 優先序)、第 21 行(`--json` 成功時 stdout 恰一行 JSON):這份 spec 只改 guard settle 與 c1 的「找不到」訊息文字,不碰 `guard kill` 的 rc 與輸出,不受影響。
- `Systems/lumos-cli-write`、`Systems/存量漂移守衛`:grep 不到 ★INVARIANT★ 行,沒有可以判的合約行。S3 的「set 訊息一字不變」是這份 spec 自己的條款,見 F5。
- `Systems/delguard`(不在 lands_in):沒有 ★INVARIANT★。它的 KEY「advisory 恆 rc0」:skip 只影響抽取,不影響 rc;前提是 `_vendored_state` 要放在既有的 try 之內。

最高等級:major;blocking 共 4 條
