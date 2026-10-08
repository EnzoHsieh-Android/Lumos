severity: major

席:邊界-sonnet。鏡頭:邊界與輸入。實驗都在 `fg-r1-work-邊界-sonnet/` 自己的 clone 與臨時 git repo 裡跑,沒動 negguard 與主 repo。

## F1 先紅用子字串篩選,一個測試名會選中好幾支,別支的紅可以頂替這支的紅
severity: major
blocking: 是
引句:「非 0 結束,而且 `_ran_count` 讀得到跑了至少一支、沒有全被跳過 → 紅,過」
file: `scripts/test_lumos.py:5267`(t_guard_trace)與 `scripts/test_lumos.py:5632`(t_guard_trace_multiplatform)
file: `scripts/lumos:6564`(_spec_gate_declared)、`scripts/lumos:6584`(_spec_gate_verdict,篩到 n>=2 就判弱證據、要求測試名唯一)
1. 輸入:紀錄 `tests: ["t_parse"]`。`t_parse` 是新寫但沒牙齒的測試(base 就綠);同一支新測試檔還有 `t_parse_edge`,它測新功能,在 base 紅。
2. 走到「先紅後綠 / 紅那邊」:`run_cmd` 是 `-k {method}`,子字串比對,兩支都被選中,結束碼非 0。`_ran_count` 讀到「N 案例」N>=2 ≥ 1,規則只問「至少一支」,判紅、過。沒牙齒的那支被別支的紅蓋掉。
3. 實測(舊提交,`-k t_guard_trace`):輸出 `lumos 測試(2 案例)`,t_guard_trace 與 t_guard_trace_multiplatform 一起被跑。本 repo 測試名互為子字串的有 36 組(`t_loop_status` 同時選中 4 支)。
4. 同一個工具鏈已經有現成的答案:規格閘 `_spec_gate_verdict` 對 n>=2 判弱證據並要求名字唯一。這份設計的紅綠步驟沒有沿用,綠那邊同理(別支綠不代表這支綠;`_ran_evidence_check` 只證明有東西跑過)。

## F2 受波及合約測試吃到「改名看不到舊路徑」的洞,改名型修正會判 no-pins 直接放行
severity: major
blocking: 是
引句:「`_bound_tests_for_diff`(範圍 `base..現在`,兩個端點比對,不要求祖先關係)算出來的測試」
file: `scripts/lumos:36474`(cmd_impact_diff 取檔案清單用 `git diff --name-only`,預設開改名偵測,只吐新路徑)
file: `scripts/lumos:38385`(_bound_tests_for_diff:沒有固定席就回 no-pins)
1. 輸入:修正提交只把 `scripts/lumos` 改名成 `scripts/lumos_cli`(路徑、名稱碰撞這兩類根因的修法常是改名)。
2. 實測(clone 內):改一行時 `lumos impact --diff HEAD~1..HEAD --json` 回 `results 34 / pinned 26`;純改名 commit 後 `git diff --name-only HEAD~1..HEAD` 只印 `scripts/lumos_cli`,同一指令回 `results 0 / pinned 0`。
3. 呼叫 `_bound_tests_for_diff(repo, "HEAD~2..HEAD")` 回 `[] , "no-pins"`。設計在第 5 項寫「算不出來時 `no-pins`…算過並印說明」,所以整項合約測試全綠放行,等於改名過的檔案完全不受合約保護。
4. 這個洞是既有的(推送前閘同樣有),但這份設計把它當成現成可信的來源,而且正好修正關卡面對的根因類別最容易觸發。

## F3 紅那邊把「選中 0 支」也算紅,疊檔漏掉任何一支就靜默通過;疊哪些檔的清單怎麼取也沒規定
severity: major
blocking: 是
引句:「非 0 結束,但讀不出跑了幾支(這棧還讀不出支數、或要測的函式在修之前不存在而匯入就失敗、或選中 0 支)→ 算紅」
引句:「把 `base` 到現在之間改過的測試檔(用 `_nodehome_is_test` 判)換成現在的內容」
file: `scripts/lumos:24776`(_nodehome_is_test)、`scripts/lumos:5143`(discover_test_methods,測試索引另一套判法:profile 的副檔名與 `file_name_match`)
file: `scripts/lumos:36474`(慣例的取檔案清單寫法沒有 -z,中文路徑會被加引號跳脫)
1. 步驟 3 已保證這支測試「現在」存在。所以 base 的工作樹裡選中 0 支,只可能是「定義它的新檔沒被疊過去」。把它算紅,就是把疊檔失敗當成先紅的證據,這一格正是先紅要抓的「這支測試在修之前其實沒有牙齒」。輸出雖然標「看不出跑了幾支」,但規則本身說過。
2. 實測使疊檔漏掉的來源(用現有函式跑):
   - `_nodehome_is_test('conftest.py')`、`.maestro/login.yaml`、`e2e/flows/login.yaml` 都回 False,但 maestro profile 的索引會認 yaml、python 測試依賴 conftest 的 fixture;這些改過的檔不會被疊進 base 的工作樹。
   - 臨時 repo 裡改一支檔名 `測試 檔.py`:`git diff --name-only HEAD~1 HEAD` 印 `"\346\270\254\350\251\246 \346\252\224.py"`(帶引號的八進位跳脫),照字面當路徑就是找不到檔。
   - 改名(相似度 97%):`git diff --name-only` 只印新路徑 `tests/big2.py`;`--no-renames` 才多印舊路徑 `tests/big.py`。不加 `--no-renames` 時 base 工作樹裡舊檔與疊上去的新檔並存,同名測試定義兩份(xcodebuild、dotnet 會因重複定義編譯失敗,那也被算成紅)。
3. 本 repo 自家執行器:`-k` 選中 0 支時印 `✗ -k 'x' 選中 0 個測試` 並回非 0,沒有「N 案例」那行,`_ran_count` 回 None,落在「看不出跑了幾支」的紅。
4. 順帶:pytest 的匯入錯誤輸出實測 `_ran_count("python", …)` 回 `(2, False)`(「1 error」被各類相加讀成 2),所以 pytest 棧上匯入失敗讀成有支數的乾淨紅,不會標「看不出跑了幾支」,跟條款 S4 寫的「匯入就失敗時標看不出跑了幾支」只在自家執行器成立。

## F4 前提「沒提交的改動已被先決條件擋掉」只在開跑那一刻成立;兩個工作樹與第 5 項之間隔著幾分鐘
severity: major
blocking: 是
引句:「先決條件已擋掉沒提交的程式與測試改動,所以跑的就是現在的提交」
file: `scripts/lumos:38606`(_run_bound_tests:`root = pentry.get("root") or repo_root`,在主工作目錄跑,沒有可指定的工作樹或提交)
file: `scripts/lumos:14182`(guard kill 註解:完整 sha 一次取得、再拿它建沙盒,「先取短碼再另外建沙盒,中間有人提交就對不上」)
1. 全域規則寫明同一個 repo 可能同時有別的會談在做事。修正關卡每輪預估 2–10 分鐘(設計自己寫的),先紅、先綠、再第 5 項依序跑。
2. 輸入:開跑 T0 時工作目錄乾淨;T0 之後另一個會談在同一目錄改了 `scripts/lumos`(未提交)或 checkout 了別的分支。
3. 結果:「第二個工作樹直接檢出現在的提交」若在 T1 才取 `HEAD`,檢出的已不是 T0 驗過的提交;第 5 項在 T2 於主工作目錄真跑,吃到別人的未提交改動,判紅或判綠都跟「現在的提交」無關;事件 `commit` 欄(`_gate_event_build` 取當下 HEAD 前 7 碼)記的是 T3 的 HEAD。
4. 設計沒有要求「開頭取一次完整 sha 並全程使用」,也沒有要求第 5 項前再驗一次乾淨(或在第三個工作樹跑)。

## F5 工作樹只含主 repo 的一份 HEAD 檢出;平台根在別的 repo、子模組、未版控的依賴都不在
severity: major
blocking: 是
引句:「指令是平台的 `run_cmd` 帶 `{method}`,每支逾時同合約測試」
file: `scripts/lumos:13262`(_kill_plat_top:guard kill 對每個平台根另問 `rev-parse --show-toplevel`,支援平台根位在別的 repo)
file: `scripts/lumos:14215`(guard kill 先跑 baseline,非綠就 abort;修正關卡沒有對應的「環境本身能不能跑」判斷)
1. 輸入:`platforms.web.root = "web"`,run_cmd 是 `npx jest -t {method}`,node_modules 沒進版控。或平台根是另一個 git repo / 子模組(`_kill_tree` 註解明寫工作樹「還沒提交的新檔、被忽略的檔、子模組裡的檔它都沒有」)。
2. 綠那邊:新檢出的工作樹沒有依賴,每支都非 0 → 每次都「不過」,關卡對這個消費專案永遠回 1。
3. 紅那邊:同一個環境錯誤也是非 0,落在「看不出跑了幾支」被算紅,所以環境壞掉與真的先紅分不開(對照:guard kill 的 baseline 非綠就是 abort)。
4. `base` 是主 repo 的提交,在別的 repo 的平台根裡不存在;設計只開一對工作樹,沒說這種多 repo 佈局怎麼辦。(未實測,依據是讀碼。)

## F6 空的或只有逗號的測試名解析成零支測試,存在檢查與先紅後綠整段空轉通過
severity: major
blocking: 是
引句:「每支測試名包成 `[test:名]` 交給合約綁定那套解析」
引句:「每條 `fixed` 至少一支測試」
file: `scripts/lumos:4896`(resolve_test_refs)、`scripts/lumos:4463`(TEST_REF_RE:`\[test:\s*([^\]]+)\]`)
1. 實測 `resolve_test_refs("[test:]"…)`:`""`、`" "`、`","` 三種都回 `[]`。
2. 輸入:`"tests": [""]`。第 1 項若數原始陣列長度(有一個元素)就過;第 3 項解析成零支,逐支驗證迴圈跑零次,通過;第 4 項紅綠同樣迴圈零次,通過。整份紀錄沒跑過任何測試卻 `passed`。
3. 同一個包法還有:`"t_a]x"` 解析成 `t_a`(原始字串與解析結果不一致,後面若拿原始字串去跑,篩選字串帶著 `]`,選中 0 支);`"t_a,t_b"` 被拆成兩支;平台前綴未定義時 `resolve_test_refs` 丟 `ValueError`(多平台 `ghost:t_a` 實測),設計沒寫要接住,沒接住的例外會讓指令以 traceback 結束、不寫事件,跟「回 1 或 2」兩個定義的回傳碼都對不上。
4. 設計沒規定要用解析後的清單當唯一真相(驗幾支、跑哪些),也沒規定解析後數量要等於紀錄原本的條數。

## F7 `at` 的解析與驗證邊界沒定
severity: minor
blocking: 否
引句:「檔案要在現在的提交裡,函式名要在那支檔裡整字找得到」
file: `scripts/lumos:20305`(_vault_in 這類以磁碟為準的判法;專案裡沒有現成的「路徑在某提交的樹裡」判斷被指定給這步)
1. 多冒號:`src/lib.rs:Parser::parse`、Swift `Foo.swift:init(a:b:)`。拆法沒規定:從左拆第一個冒號才對,從右拆就變成檔 `src/lib.rs:Parser:` 找不到。沒有冒號的 `at` 也沒說回哪種錯。
2. 「在現在的提交裡」若用磁碟判斷:未追蹤的檔(先決條件明寫不看未追蹤)、macOS 大小寫不分的檔名、`../x` 或絕對路徑都會被認成存在。要用 `git ls-tree`/`cat-file` 對那個完整 sha 才是設計寫的意思。
3. 整字邊界沒定:`valid?`、`$el`、`operator==`、中文函式名用 `\b` 會找不到;`main`、`get`、`run` 這種字在註解或字串裡出現就算找到,而 `fixed` 的檔是否在 `base..現在` 的改動裡也沒要求(沒改過的檔可以標 `fixed`)。
4. `unaffected` 同樣只驗字面,不會因為這些邊界而更嚴。

## F8 passed 事件只綁紀錄內容的 sha256:程式再改、base 填分支名、`--record` 指到別處,提醒與同類檢查各自失準
severity: minor
blocking: 否
引句:「`record_sha256` 等於現在修正紀錄檔的 sha256」
file: `scripts/lumos:1147`(_gate_event_build:`commit` 欄自動帶,但設計比對時不看它)
1. 紀錄不變、程式在 passed 之後又多一個修正提交:`loop next` 找得到同 sha 的 passed,提醒靜默,而驗的是舊提交。「到頂那一輪推之前」這個設計特別強調的場合就是最後一輪、沒有下一輪審查會補看。轉成擋時這個洞變成放行。
2. `base` 設計只要求是存在的提交:我實測短 sha 與分支名都能 `cat-file -e` 與 `git worktree add --detach`;分支名會移動,同一份紀錄 sha256 之後驗出不同結果;短 sha 日後可能變不明確,走到先決條件的 rc 2。
3. `--record` 指到預設位置以外:passed 事件的 sha 是那個檔的內容 sha,提醒比對的卻是預設路徑的檔;預設路徑沒檔就永遠提醒「先寫紀錄」,也永遠消不掉。同類連兩輪那項讀「前一輪的修正紀錄」也只認預設路徑,前一輪用過 `--record` 時靜默略過。
4. 審查帳輪次被隔開出現:`loop next` 會 rc 2 擋(`scripts/lumos:11557`),`fix-check` 設計寫「照帳上輪次出現的順序」找前一輪,沒有同樣的檢查,第一次與最後一次出現哪個算沒定。

## F9 `--regression-set` 與提醒指令的輸入邊界
severity: minor
blocking: 否
引句:「載體席選填 `--regression-set <id 串|none>`」
引句:「在輸出加一行提醒與要敲的指令」
file: `scripts/lumos:8566`(`_ids` 以逗號切,`""` 與缺值是兩種意思)、`scripts/lumos:8610`(`--refuted-set` 比對 none 用 `.strip().lower()`)
1. `--regression-set None` / `NONE`:跟 `--refuted-set` 不同,設計沒說大小寫;照字面會當 id,而 id 不在發現清單,回 2 但訊息指向 id 而不是 none 寫法。`--regression-set ""`、`none,F1`、重複 `F1,F1` 都沒定。
2. 第一輪帶非空的 `--regression-set F1`:第一輪沒有上一輪,合法寫入後被算進「上一輪修補造成的比例」的分子,而 REVISIT 與 RETIRE-IF 都靠這個比例。
3. 迴圈編號與輪次是自由字串(`scripts/lumos` 的 `_qid = shlex.quote(loop_id)` 註解提到代碼審 r3 資安 G1:編號帶 `;` 會在照抄的指令裡被執行)。提醒行會印出「要敲的指令」,設計沒要求編號與 `--round` 值都要 `shlex.quote`。

## F10 沒有 `docs/` 或 vault 在非標準位置時,事件寫不進去,提醒永遠消不掉;長時間執行被砍時工作樹會殘留
severity: minor
blocking: 否
引句:「跑完逐項驗(過或不過)用 `_gate_event_or_warn` 寫一筆治理帳」
引句:「收法照它:`worktree remove --force`、刪資料夾、`worktree prune`,放在 finally 裡一定收」
file: `scripts/lumos:1202`(_gate_event:`docs/` 不是目錄就回 None,不寫)、`scripts/lumos:7609`(cmd_gov 讀 `env.vault.parent / .governance-log.jsonl`,跟寫者的 `repo_root/docs/` 是兩套定位)
file: `scripts/lumos:14316`(guard kill 同樣的 finally 收法;全檔 grep `signal.signal`/`SIGTERM` 沒有處理器)
1. standalone vault(`_vault_in` 的第二種佈局,審查帳在 repo 根):`docs/` 不存在時 `_gate_event_or_warn` 回 None,fix-check 沒寫事件也不報錯;`loop next` 的提醒因為找不到同 sha 的 passed,每次都印。設計沒說這種佈局要不要靜音。
2. 預估每輪 2–10 分鐘,但每支測試跑兩次、逾時各 180 秒、沒有總時間或總支數上限;紀錄列 12 支慢測試就超過對話裡指令的 10 分鐘上限。被砍時 Python 的 `finally` 在 SIGKILL/預設 SIGTERM 下不會跑,`lumos-fixcheck` 暫存資料夾與已登記的 git 工作樹留下,也沒寫事件;下次沒有清掃殘留的步驟,S4 的「沒有殘留」只在正常結束時成立。

## 其他節
- 修正紀錄 JSON 本身:空 `groups`(有折入時第 1 項會擋)、同一發現在兩組(設計沒禁,不造成放行)、重複組 id(只影響輸出辨識)、`tests` 空陣列(第 1 項擋)。已讀,無 finding。
- 輪次字串不是 `rN`:設計明講不解析數字,沿用帳上字串;載體席必定寫 `folded_set`(`scripts/lumos:8643` 在 `--folded-set` 缺值時寫 `[]`),沒有「欄位不存在」的新帳。已讀,無 finding。
- 第一輪(沒有前一輪):第 2 項條件不成立,不要求 `prior`。已讀,無 finding。
- `base` 等於 HEAD:兩個工作樹內容相同,測試在 base 就通過,回 1 並寫「修之前就通過」;`_bound_tests_for_diff("HEAD..HEAD")` 回 no-pins。方向是擋,可接受。
- 治理帳很大與壞行:`loop next` 逐行預篩 `"fix-check"` 再解析,讀端既有 `_drift_jsonl_parse` 也跳壞行與型別不對的行(`_GOV_FIELD_TYPES`)。已讀,無 finding。

最高等級:major,blocking 共 6 條
