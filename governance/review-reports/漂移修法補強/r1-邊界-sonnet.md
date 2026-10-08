severity: major

審查立場:邊界-sonnet(空的、單一、超大、剛好卡界線、格式怪的輸入)。實驗在 `git clone --shared` 出來的臨時目錄(edge-sonnet、edge-s2、edge-s3)做,repo 本身沒動。

## F1 範本句原樣貼進 --values 時,佔位字 sha 與卷證會被寫進 valid_under
severity: major
blocking: 是
引句:「`--values` 各項已由 `_conditions_rewrite` 擋空值、多行、佔位字,再過 `_drift_one_line` 擋 U+2028 這類分行字元」
file: `scripts/lumos:14620`(`_SET_COND_SLOT` 是 `_conditions_rewrite` 唯一認得的佔位字)
file: `scripts/lumos:27622`(`_drift_placeholder_err` 認得 sha、卷證、為什麼…,只有 c2 的 `--reason` 走它)
file: `scripts/lumos:27940`(`_drift_c4_evidence` 範本句在沒 sha 或沒找到目錄時會印字面的 `<sha>`、`<卷證>`)
1. 輸入:證據頁範本句 `提交 <sha>;代碼審見 <卷證>`(卷證目錄 0 個時一定是這句),整句貼進 `--values`。
2. `_conditions_rewrite` 只擋 `_SET_COND_SLOT`(整項新內容那個字串)。`<sha>`、`<卷證>` 不是它,通過。
3. `_drift_placeholder_err` 就是為了這種「照貼提示」事故存在的(c2 的代碼審 r1 合約圖譜席抓過),spec 明說 c4 不走它,也沒有補等價檢查。
4. 結果:值原樣寫進 valid_under,「c4 消失」判定成立、修復帳記一筆成功。spec 還特地記 `template_used`,等於預期有人原樣貼範本,卻沒擋佔位字。
修法方向:`--values` 各項再過 `_drift_placeholder_err`,或把 c4 範本的佔位字集中定義在 `_conditions_rewrite` 的佔位字檢查裡。

## F2 改寫後的新句仍含「未提交」等字時,筆記已被改寫才報錯,而且之後同一篇卡住
severity: major
blocking: 是
引句:「驗證磁碟內容等於算出的內容且 c4 消失」
file: `scripts/lumos:26376`(c4 判定:valid_under 全部項串起來,只要含未提交、還沒提交、uncommitted 任一個就中)
file: `scripts/lumos:28086`(`_drift_fix_write` 先寫檔,`_drift_fix_verify` 才在寫後判 handled)
file: `scripts/lumos:28157`(`cmd_drift_fix` 寫後驗證失敗不自動還原)
1. 輸入:人把要改的那項改寫成歷史說法,例如「原本未提交,已於 abc123 提交」。這種句子自然會提到未提交,是最常見的改法。或者另一項本來就合法地含「還沒提交」字樣、照抄不動。
2. `_conditions_rewrite` 與 `check=lambda f: _conds(...) == vals` 都只驗欄位讀回來等於輸入,通過,檔案寫入。
3. 寫後 `_drift_state_findings` 仍有 c4(判定看全欄位子字串,不是看行號),`handled` 為假,報「寫入後內容跟預期不同」並且不還原、不記帳。
4. 之後同一篇再跑任何 drift fix:`_drift_fix_clean_err` 因為「未提交改動、又不是修復帳最後一筆的指紋」直接擋,只能 git checkout。
5. spec 手上有 `Env.from_texts` 這種能在記憶體算發現的接縫(`_drift_state_findings` 註解寫了),可在寫入前先算一次;spec 選擇全部放在寫後。
修法方向:寫入前用改後內容算一次 c4,還在就擋下且不寫,訊息講是哪一項還含哪個字。

## F3 值同時含單引號與雙引號或反斜線時,drift fix 路徑會噴 traceback
severity: major
blocking: 是
引句:「錯誤訊息整句原樣回傳;`_set_conditions_locked` 讀檔 → 呼叫它 → 有錯就照原樣印到 stderr、回 2 → 沒錯才 `atomic_write_verify`」
file: `scripts/lumos:14710`(`_yaml_quote` 對同時有單引號與雙引號/反斜線的值丟 ValueError)
file: `scripts/lumos:38103`(`lumos set` 分派外面包 `except (ValueError, RuntimeError)`)
file: `scripts/lumos:38088`(drift 分派沒有 try/except)
1. 輸入:`--values "a: it's \"x\""`(實測 `lumos set` 對這個值回「擋下:…同時有單引號、又有雙引號或反斜線…」rc 2)。
2. spec 只把空值、多行、佔位字三道檢查搬進 `_conditions_rewrite` 回錯誤字串;算新行時的 `fmt_scalar` 拋的 ValueError 沒被納入。`lumos set` 是靠分派外層的 except 接住的,drift fix 的分派沒有那層。
3. 結果:drift fix 帶這種值直接 traceback(檔案沒動,但 S2 說的擋下變成崩潰);`--dry-run` 同樣崩。
修法方向:`_conditions_rewrite` 自己 try `fmt_scalar` 並回錯誤字串,S2 與 S3 兩邊訊息才一致。

## F4 同提交找法在「沒交集」時把 1 到 3 個不相干目錄當成卷證列出,而且不再試計劃名比對
severity: major
blocking: 是
引句:「沒交集就列同提交找到的全部,超過 3 個時標」
file: `scripts/lumos:5865`(`_plan_first_commit` 用 `git log --diff-filter=A -- <路徑>`,沒開 -M/-C)
1. 實驗(edge-s2):計劃檔改名後,`git log --diff-filter=A -- <新路徑>` 回的是改名那個提交(3fdf0dc),不是最早的提交(8aa7b45)。那個提交若順手加了別的計劃的卷證目錄 zz,`git show --diff-filter=A` 就列出 zz。
2. 同樣會發生在:整批匯入、搬目錄、專案骨架提交、驗證紀錄與別的計劃同提交。
3. spec 規則:同提交有目錄但跟計劃名沒交集 → 列全部,只有超過 3 個才標「自己挑」。1 到 3 個不相干目錄被標成 same-commit、放進範本句「代碼審見 …」,而且因為「同提交一個都沒有才退回計劃名比對」,計劃名比對(可能真的找得到)不會跑。
4. 3 與 4 個的分界只反映數量,不反映正確性;此外計劃名比對是子字串(`k in _drift_c4_key(d.name)`),太短的 key 會多命中,「有交集只列交集」沒有對應保護。
修法方向:沒交集時 same-commit 與 name 兩組都列並標來源,或沒交集就一律標「可能不相干」;`_plan_first_commit` 對改名的提示要在 `reports_via` 標出。

## F5 預填指令被 2000 字截斷,--values 讓截斷變成寫入路徑上的風險
severity: major
blocking: 是
引句:「指令改成 `lumos drift fix <節點> <行號> --kind c4 --values …`,要改的那項放 `<整項新內容>`、其他項照抄」
file: `scripts/lumos:27965`(`print(_esc_clean(f"    lumos set ... {args}", 2000))`)
file: `scripts/lumos:9765`(`_esc_clean` 超長時截斷並補 …,且把控制字元換成空格)
1. 實驗(edge-sonnet):valid_under 12 項、每項約 200 字,證據頁最後一行結尾是 `字字…`,引號沒收、被截斷。
2. spec 要把這條 `_esc_clean(…, 2000)` 的指令換成 `--values`,沒提上限。截在引號中間:貼上後 shell 停在續行提示,不會誤寫,但指令整條不可用。截在兩個參數之間:結尾的 … 變成獨立一個參數,`--values` 各項不空、通過,一條內容是 … 的條件被寫進筆記且帳上成功。⚠ 後者落點需要剛好,我沒造出來,前者已實測。
3. 同一支 `_esc_clean` 把項目裡的控制字元(多行區塊的換行)換成空格,印出來的「照抄」內容跟原項目不同。
4. 本 repo 的驗證紀錄 valid_under 常有長句(例:2026-08-24_節點還原SOP落地),不是假想輸入。
修法方向:指令超長就不印可照貼的版本,改列各項與「請自己組指令」;或分行印每個 `--values` 參數。

## F6 多行區塊的 valid_under 在證據頁被壓成一項,「其他項照抄」對它不成立
severity: minor
blocking: 否
引句:「指令改成 `lumos drift fix <節點> <行號> --kind c4 --values …`,要改的那項放 `<整項新內容>`、其他項照抄」
file: `scripts/lumos:27959`(`items = [... as_list(...valid_under)]`,沒用 `_conds` 拆)
file: `scripts/lumos:13775`(`_conds` 的說明寫了多行區塊存成含換行的單一字串)
1. 實驗:`valid_under: |` 兩行(第一行含未提交、第二行 macOS 全綠)。證據頁只印 `1. 改動未提交,只在工作目錄 macOS 全綠  ← 要改的這項`,兩個條件併成一項、整項被換成佔位字。
2. 人照證據頁做,第二個條件會在不知不覺中被吃掉(帳上 changed 看得到,但寫入當下沒有任何提示)。`_conditions_rewrite` 擋多行值,所以工具自己也無法把原樣的整項送回去。
3. 寫入端(`_set_conditions_locked`)已能處理多行區塊(實驗:摺疊區塊 `>-` 換成兩項清單成功),只有證據頁拆項有問題。
修法方向:證據頁與 hit 判定改用 `_conds` 拆。

## F7 卷證目錄收集對頂層檔、巢狀、控制字元、shell 元字元的行為沒定義
severity: minor
blocking: 否
引句:「收 `governance/review-reports/<目錄>/` 的目錄名,去重、照字母排」
file: `scripts/lumos:23634`(`_nodehome_split_z` 只切 NUL)
1. 實驗:同提交加了 `governance/review-reports/README.md` 與 `.../b/f.md` 與 `.../漂移 修法/sub/f.md`。`git show -z --name-only --diff-filter=A --format=` 輸出正確且中文、空白、換行目錄名都無損。
2. spec 沒說要求「路徑至少三段」。照 `split("/")[2]` 取的實作會把頂層的 README.md 當成目錄名列出。巢狀目錄只算第一層,這點 spec 也沒寫。
3. 目錄名含換行:「目錄名印到終端前過 `_esc_clean`」把換行換成空格,印出來的範本句指到一個不存在的路徑;`template_used` 比對用未消毒版所以永遠不等。
4. 目錄名含 `$(…)` 或反引號:範本句只過 `_esc_clean`,沒有像指令參數那樣走 `_drift_sh`(spec〈實務隱患〉只承諾指令參數走它)。人把範本句貼進雙引號的 `--values` 時會被 shell 展開。⚠ 需要有人能在版控裡加這種名字的目錄。

## F8 check 拿未去空白的 vals 比,帶頭尾空白的合法輸入會被自己的自驗打回
severity: minor
blocking: 否
引句:「check=lambda f: _conds(f.get("valid_under")) == vals」
file: `scripts/lumos:15150`(`_set_conditions_locked` 是先 `vals = [str(v).strip() ...]` 才比)
1. 輸入:`--values "  已提交 abc  " b`(實測 `lumos set` 會去空白後寫入成功)。
2. spec 把去空白搬進 `_conditions_rewrite`,但 `res.check` 用呼叫端手上的原始 vals 比;`_conds` 讀回來是去過空白的,`atomic_write_verify` 判不一致丟「寫完讀回來檢查…不一樣」,一個合法輸入被擋,訊息與真因無關。同一段的 `template_used` 又明說「去頭尾空白後」比,兩處不一致。
修法方向:check 與 template_used 都用 `_conditions_rewrite` 回傳的去空白值。

## F9 S3 說 lumos set 一字不變,但檢查與讀檔的順序被換了
severity: minor
blocking: 否
引句:「`lumos set` 的行為與訊息一字不變」
file: `scripts/lumos:15128`(現況三道值檢查在 `load_raw_for_edit` 之前)
1. 現況:值有問題時,檔案打不開也照樣先印「擋下:值裡還留著…」。spec 的新順序是「讀檔 → 呼叫它 → 有錯」,檔案不存在、CRLF、讀不了時,同一個壞值會改成印讀檔錯誤。
2. 邊界很窄(值與檔同時有問題),但 S3 的綁定測試若用「壞值 + 壞檔」就會紅,spec 沒交代要不要保留舊順序。
修法方向:`_conditions_rewrite` 拆成先驗值(不讀檔)與後算行兩段,或在 S3 註明順序改動。

## F10 `_guard_prose_settled` 的辨認條件太鬆,可能對「其實被刪掉」講「已轉正,不用改」
severity: minor
blocking: 否
引句:「摘要有 `TEST:[日期] 預告已轉正` 開頭的行」
file: `scripts/lumos:12070`(`_guard_planned_prose` 已用區域判斷行落在摘要還是正文)
file: `scripts/lumos:12093`(`_GUARD_MANUAL_SETTLED_RE` 只驗 4-2-2 位數字,不驗真的是日期)
1. whynot 的辨認條件只寫「預告當時」開頭。正文任何以「預告當時」開頭的句子(例如「預告當時的討論見…」)都算已轉正,把真正被手改掉的 whynot 誤講成「不用改」。改寫出來的句型其實是「預告當時為什麼還不做:」,可以收緊。
2. TEST 與 whynot 都沒說要落在哪個區。TEST 只在摘要、whynot 只在正文才合理;spec 只在 WHY 那一項說沿用既有辨認(既有函式有區域參數)。
3. 日期:`TEST:[今天] 預告已轉正`、`(2026-13-45 已轉正)` 都被算轉正;跟 `_guard_written_settled_dates` 兩邊也可能不一致。部分句子轉正(TEST 轉、WHY 沒轉)本身沒問題,因為判定是逐種類的。
修法方向:whynot 認完整的「預告當時為什麼還不做:」,TEST 與 whynot 限定區域。

## F11 c3 理由:沒說要不要去頭尾空白,也沒驗理由裡的雙括號連結
severity: minor
blocking: 否
引句:「`--kind c3` 收選填的 `--reason`(規則同 c2:一行、4 到 200 字、擋提示佔位字」
file: `scripts/lumos:27697`(`_drift_fix_reason_ok` 用 `len(r.strip())` 算長度)
file: `scripts/lumos:27874`(c2 的橫幅寫入時 `.strip().rstrip("。")`,c3 現行字串組合沒有)
1. 長度規則 4 與 200 的兩端已被既有函式處理(以去空白後計)。但 spec 的補行寫法是「接理由」,沒說要不要 strip;`--reason "  abcd  "` 通過長度檢查,原樣接在行尾,行內留下前後空白。
2. `--by` 會過 `_drift_fix_by` 驗連結存在;理由裡的 `[[壞連結]]` 不驗,直接寫進正文。⚠ 我沒實跑寫入後 lint 會不會報,屬於程式讀得出、未實測。
3. 理由含分號、冒號沒有問題(接在行尾,不被任何解析吃掉)。
修法方向:c3 與 c2 一樣 `.strip()`(要不要去句號自行決定),並寫明理由裡的連結不驗。

## F12 argparse 與分派字典的接線沒列全,漏接時是靜默變成「只印證據」
severity: minor
blocking: 否
引句:「新增 `--values`(argparse `nargs="+"`,加進 `_DRIFT_FIX_OPTS`」
file: `scripts/lumos:38095`(drift fix 分派把選項手抄成一個固定字典傳給 `cmd_drift_fix`,沒有 values 鍵)
1. spec 列了 argparse、`_DRIFT_FIX_OPTS`、`_DRIFT_FIX_ALLOWED`,沒列分派處那個字典。漏接時 `o.get("values")` 恆為 None,帶了 `--values` 的指令等同不帶,rc 0 印證據頁,沒有任何錯誤——使用者以為寫了。
2. 另外 `_drift_fix_load` 現在對 c4 一律跳過乾淨檢查(`kind != "c4"`);spec 要改成「c4 且沒帶 --values」,也沒點名這一行。
3. `nargs="+"` 的值以 `-` 開頭且不含空白(例如 `-3`、`--foo`)會被 argparse 當選項,報用法錯而不是進到 `_conditions_rewrite`。這在條件句上罕見,列為附帶。
修法方向:把分派字典與 `_drift_fix_load` 的條件列進做法第 2 節,並在 S2 綁一條「帶 --values 一定寫檔」的測試。

## F13 lands_in 漏了刪除守衛自己的家
severity: minor
blocking: 否
引句:「③工具自己的檔:借既有 `_vendored_state`(讀索引時傳 `ref=""`,同筆記形狀擋的用法)與 `_is_toolchain_repo`,刪除守衛抽被刪名稱時跳過跟安裝清單一致的工具檔」
file: `docs/lumos-toolchain-knowledge/Systems/delguard.md`(about_code 列 scripts/lumos 與 scripts/hooks/pre-commit,摘要有「排除域與 pre-commit 對齊」與 t_delguard 的描述)
1. 這份計劃的 lands_in 是存量漂移守衛、lumos-cli-write、guard-kill,沒有 Systems/delguard;五條裡第五條動的是 delguard 的抽取行為,家是 delguard。鐵則 5(改了程式要寫進改到那支檔的家)會在提交時提醒,但計劃沒寫等於實作者不知道要補。
2. delguard 的摘要寫了「排除域漂移由 t_precommit_whitelist_drift_guard 釘第三份清單」;新增的工具檔跳過是第四種降噪來源,沒有對應的漂移守衛,spec 也沒說靠什麼確保安裝清單(`_VENDORED_ALL`)與 delguard 用的是同一份(這點靠直接呼叫 `_vendored_state`,已經是共用一份,所以只是文件缺口,不是機制缺口)。

## 已讀但無 finding 的項目
- 卷證目錄 4 個時標示:實驗 edge-s2 顯示 `-z --name-only --diff-filter=A --format=` 輸出是乾淨的 NUL 分隔,沒有提交標頭,中文、空白、換行的目錄名無損。
- 合併提交:實測 `git log --diff-filter=A`(沒開 -m)不會回合併提交本身,回的是側枝上加檔的那個提交,所以「第一次進歷史是合併提交」在正常歷史裡不會發生,只是對走 evil merge 的情形退到 name;不出錯。
- shallow:`_git_is_shallow` 先擋,sha 為 None,符合 spec 的退回計劃名比對。實測 depth 1 的 clone 上 `_plan_first_commit` 會回 tip commit,所以先擋 shallow 是必要的,spec 有做。
- `_delguard_parse_diff` 的 skip:清單檔不存在時 `_json_at_ref` 回 None,`_vendored_state` 回空集合,一支都不跳,符合「寧可誤報」。清單只列部分檔或某檔指紋不符時,是逐檔判定,沒問題。工具檔被部分改動(跟清單不一致)照舊抽,符合 S6。
- `_vendored_state(root, "")`:`f"{ref}:{p}"` 變 `:scripts/lumos`,git 解成索引內容,實作上可行;git 跑不起來時 data 為 None、不算原封不動。
- valid_under 各種現況(單行、清單、摺疊區塊 `>-`、單項/兩項):`_set_conditions_locked` 的 a..b 整段換掉,實測正確;valid_under 原本不存在:c4 判定要有值才成立,所以 `--values` 走不到插入分支,不會出錯。
- 值含冒號、引號、井號、方括號、全形空白、控制字元 ESC、超長 300 字:`fmt_scalar` 與 `_conds` 讀寫來回一致(34 種值批次驗過,唯一不一致是 F3 的雙重引號類與 F8 的頭尾空白)。
- c3 理由 4 與 200 字的邊界:既有 `_drift_fix_reason_ok` 已處理。

## 合約逐條判定(★INVARIANT★)
- Systems/guard-kill 兩條:rc 優先序(t_guard_kill_rc_precedence)、`--json` stdout 恰一行 JSON(t_guard_kill_json_purity)。這份設計只動 c4 證據與寫入、c1 與 guard settle 的「找不到」訊息、c3 理由、delguard 抽取,沒碰 guard kill 的執行路徑與 stdout 契約。不影響。
- Systems/lumos-cli-write:沒有 ★INVARIANT★ 行。有一條 KEY 說所有 frontmatter 變動經 `atomic_write_verify`;c4 的 `--values` 仍走它(經 `_drift_fix_write`),沒破壞。這條 KEY 只是線索,判斷依據是程式碼。
- Systems/存量漂移守衛:沒有 ★INVARIANT★;有兩條 RULE(預設 warn、開關讀推送頂端提交)。這份設計不改閘與開關,不影響。
- Systems/delguard(不在 lands_in,但被第五條動):沒有 ★INVARIANT★,不影響;見 F13。

## 實務隱患
- 不可逆:碰到。F2 的寫後驗證失敗與 F5 的截斷是這一類;其他情況乾淨檢查保證 git 退得回來。
- 金流:無,本機命令列工具。
- 對外送出:無,不寄信、不打外部服務。
- 守衛面:碰到。F10 的「不用改」誤判、F4 的不相干目錄當證據,都是守衛的文字誤導。
- 資安:碰到。F1、F7(目錄名進範本句沒走 `_drift_sh`)。
- 效能:F5 所在的證據頁很短;`git show` 有逾時。無其他隱患。
- 併發:c4 走既有鎖與指紋。無新增隱患。

最高等級:major;blocking 共 5 條
