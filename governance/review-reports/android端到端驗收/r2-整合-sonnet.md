severity: major

我讀完整份 spec,並對照 `scripts/lumos`、`pre-push`、`ci.yml`、收集腳本、maestro-visual-toolkit 和 Maestro 2.10.0 查證。以下 F1 到 F14 每條都有查證依據。

## F1 回退節指向不存在的設定檔,而且依 S9 的規則,刪掉 e2e 段的提交會被判定自己擋下
severity: major
blocking: 是(照字面實作,回退動作什麼都不會關掉,真要關還會被自己的閘擋住)

〈回退〉第一條:
引句:「專案刪掉 `.lumos/android-e2e.json`,`code-loop check` 的 Android E2E 判定就不跑」

〈設定〉與 S1 都說設定放在 `.lumos/macrobench.json` 的 `e2e` 段,全文沒有 `.lumos/android-e2e.json` 這個檔。這是改成 macrobench.json 當設定檔時,漏改的舊殘留。

另一個問題是回退路本身走不通。S9 規定:
引句:「當被推送的提交自己刪掉或改弱 `e2e` 段時,判定應照主線版的設定判」

〈實驗室驗收〉也把「同一個提交裡刪掉 e2e 段」列為應該擋。

〈查證紀錄〉說 `e2e` 段本身算進指紋。所以刪段的提交指紋會和主線分岔點不同,而主線版仍有 `e2e` 段,判定就要求紀錄。刪段的提交推不出去,除非補驗收或放行。spec 沒寫明「關掉這道閘本身也要走放行」。

佐證:
- file: `scripts/lumos:39395` 現行 `_macrobench_config` 只認 `.lumos/macrobench.json`,沒有任何 android-e2e.json 的讀取。

## F2 「既有推送範圍的算法」有三套互不相同的做法;而「推到主線時分岔點就是頂端」按任何一套既有算法都不成立
severity: major
blocking: 是(兩個分岔點算法的結果不同,CI 與本機的行為會跟著不同)

引句:「主線分岔點用既有推送範圍的算法;算不出來(沒有主線、淺層 clone)時這道走 fail-open」

引句:「推到主線時分岔點就是頂端,這道不要求;第一版不另外接 CI」

spec 沒指定「既有算法」是哪一套。我查到的有:
- `pre-push` 的 `_brange`,只有新分支首推才換成跟主線的分岔點。
- `_lens_push_base`:起點是真的 sha 時,原樣回傳那個起點,也就是遠端舊的分支頂端,不是主線分岔點。
- `_secev_mainline_pushed`:推的是 main 時,主線 tip 就是推送前的位置。

後果有三個:
1. CI 在 push 事件把 `--diff "$BEFORE..$SHA"` 交給 check。依上述算法,main 的 base 是 BEFORE,不是頂端。所以每次合進 main 的 App 改動,CI 都會要求紀錄。squash 或 merge 之後,樹裡還混了別人的改動,指紋跟分支上驗收時不同,紀錄就失效,CI 紅。這跟「CI 不要求」直接矛盾,S8 到 S12 也沒有 CI 案例的條款或測試。
2. 若 `_lens_push_base` 的起點是「遠端舊分支頂端」:一次用 `--no-verify` 推上去、沒驗收的 App 改動,之後只改文件的推送,兩端指紋相同,判定不要求。這跟 spec 要的「看主線分岔點到頂端的樹差異」不一樣。
3. 主線用 `_secev_mainline_pick`(挑候選、可被 `.lumos/config.json` 的 `security_evidence.mainline` 覆寫)時,算不出會回 `mainline_unknown`,安全證據那道是擋下。spec 卻決定這道 fail-open,要實作者自己拆開處理。

佐證:
- file: `scripts/lumos:58578` `_lens_push_base` 的 docstring 自己寫明「推送前掛鉤與 CI 的存量漂移檢查不走這支」,並提到三套範圍收斂路還沒收斂。`scripts/lumos:58594` 起點是 sha 時直接回傳起點。
- file: `scripts/lumos:9943` `_secev_mainline_pushed`:推 main 時主線 tip 取推送前位置。
- file: `.github/workflows/ci.yml:221` `code-loop check --diff "$BEFORE..$SHA" --at-sha "$SHA" --branch "$BRANCH"`。
- file: `scripts/hooks/pre-push:472` 註解寫明 `_range` 與 `_brange` 是刻意不同的兩套。

## F3 judge 用哪份設定選檔、紀錄用哪份指紋沒定義;「e2e 段本身算進指紋」用 `git ls-tree` 做不到
severity: major
blocking: 是(改 `app_dirs` 的那一支分支永遠過不了自己的閘)

〈資料怎麼流〉第 2 步:
引句:對目前 HEAD 提交的檔案樹算指紋

〈設定〉只讀主線版;S9 規定判定照主線版設定判。judge 沒說自己用工作目錄的設定,還是主線版的設定來選 `app_dirs` 與 `exclude`。判定那端重算指紋是用主線版設定選檔。

具體場景:某分支在 `e2e` 段新增 `app_dirs` 一項。judge 用分支設定,指紋含新模組。判定用主線設定重算,指紋不含它。判定去找檔名等於重算值的紀錄,找不到,就擋;使用者重跑 judge,結果一樣。這個死結要等該設定合進主線才解開,而合進主線前的本機推送就是被這道閘擋住的那一步。

另外 〈設定〉寫:
引句:驗收素材:`flows` 的檔、`visual` 對應的 flow 與基準圖、門檻檔、這一段設定本身,都算進指紋

〈查證紀錄〉的算法只取 `git ls-tree` 列出的 mode、物件編號與路徑。「`e2e` 段」是 `macrobench.json` 裡的一段,不是 ls-tree 的項目,所以:
- 整個 `macrobench.json` 當素材:改 `results_dirs`、`stability` 或其他段也會讓指紋全變,跟「只有範圍或標準變了才重驗」的意圖不符。
- 只取 `e2e` 段:spec 沒定義正規化(鍵序、空白)與取段算法。

佐證:
- file: `scripts/lumos:39395` `.lumos/macrobench.json` 同一檔裡有 `results_dirs`、`stability`、`tolerance_pct` 等各段,整檔物件編號會隨任何一段改變。

## F4 只有 e2e 段的 macrobench.json 會讓 `lumos macrobench` 回 2;`--results-dir` 在設定沒有 results_dirs 時也不會生效
severity: major
blocking: 是(KDS 試點照字面做就會撞上)

引句:跟記憶體與穩定性一樣,放進既有的 `.lumos/macrobench.json` 當一段,不另開設定檔

引句:這次只讀這個目錄,不讀 `results_dirs`;基準照舊用專案的

現行 `_macrobench_config` 在沒有 `results_dirs`、也沒有 `stability` 段時,回錯誤「macrobench.json 要有 results_dirs」。

- 試點 Citrus_KDS 是「現在沒有 macrobench 設定、要從零接」,UI 流程優先,`macrobench` 與 `stability` 預設 false。接入後的 macrobench.json 只有 `e2e` 段,`lumos macrobench` 與 `--check-config` 一律回 2。
- 收集腳本的 `load_config` 也會呼叫 `lumos macrobench --check-config`,同樣會被打斷。
- 〈這次要改到的地方〉只列 `--results-dir`,沒列 `_macrobench_config` 的驗證要放寬。
- `_macrobench_mode` 的 `if cfg is None or not cfg["results_dirs"]` 會直接走 `_macrobench_without_results`,不收集任何結果檔。S15 的 `--results-dir` 必須繞過這個判斷。spec 沒寫。

佐證:
- file: `scripts/lumos:39415` `not has_dirs and ("results_dirs" in raw or "stability" not in raw)` 回 `(None, 錯誤)`。
- file: `scripts/lumos:40207` `if cfg is None or not cfg["results_dirs"]:` 走 `_macrobench_without_results`。
- file: `scripts/templates/android-stability-collect.sh:113` 呼叫 `lumos macrobench --check-config`。

## F5 擋下原因對照表有三個同步點,spec 只列掛鉤一處;句子的正本在另一篇計劃,不在 lands_in 裡
severity: major
blocking: 是(照 spec 做,兩支現有測試會紅,而要改的節點不在 lands_in)

引句:擋下種類 `android_e2e`,接進 `_cl_say_block`、`_codeloop_kg_finish` 的明細、pre-push 的擋下原因對照表(連同比對兩邊的測試)與逃生路那段文字、ci.yml 的擋下說明

引句:pre-push 的擋下原因對照表與逃生路文字、ci.yml 的擋下說明:寫進它們的家 [[Systems/bound-tests-gate]]。

對照表句子的正本是 `Projects/推送前一次列出全部擋下原因_計劃` 〈做法〉5「對照表五句的正本在這裡」。`t_prepush_cl_reason_sentences_match_plan` 會去讀那一段並逐字比對 `_PPC_KIND_SENTENCES`。加第六種 `android_e2e` 需要同時改:
- `pre-push` 的 `pp_cl_reason`。
- `test_lumos.py` 的 `_PPC_KIND_SENTENCES`。
- 那篇計劃的「五句」。

spec 把「寫進 bound-tests-gate」當落點,會讓句子寫進錯的節點。這篇計劃不在 `lands_in`,也不是 `bound-tests-gate`。改 test_lumos.py 還要簽名(`anchor approve`)。

佐證:
- file: `scripts/test_lumos.py:77620` `_PPC_KIND_SENTENCES` 目前五種。
- file: `scripts/test_lumos.py:78390` `t_prepush_cl_reason_sentences_match_plan`。
- file: `docs/lumos-toolchain-knowledge/Projects/推送前一次列出全部擋下原因_計劃.md:68` 「對照表五句的正本」那段,安全證據閘加第五道時也是改這裡。
- file: `scripts/hooks/pre-push:140` `pp_cl_reason` 五個 case。

## F6 PRIOR-ART 與 §83 對安全證據判定的錯誤描述:它判不清就擋,不走 fail-open
severity: major
blocking: 是(實作者照「同款做法」找不到可抄的東西,安全預設要靠自己決定)

PRIOR-ART:
引句:設定只讀主線版、內部出錯走 fail-open 記帳

§83:
引句:其他沒料到的內部錯誤照 code-loop check 既有做法:接住、記一筆 fail-open 治理帳、這道放行。

安全證據閘剛好相反。`_secev_evaluate` 把逾時與任何例外轉成 `evaluation_timeout` 或 `evaluation_error` 的擋下,算不出主線是 `mainline_unknown` 也擋,不呼叫 `_gate_failopen`。spec 也寫它「跟安全證據判定一樣排在所有放行早退之前」,最像的鄰居是擋下,不是放行。`_gate_failopen` 的用法在 lint-new 等別的道。

結果是 spec 自己的標準不一致:紀錄讀不懂就擋,其他內部錯誤、算不出分岔點就放行。〈實務隱患〉守衛面又寫「漏擋會讓沒驗收的程式推上去」。任何程式例外都會讓這道無聲放行,只留一筆帳,spec 沒說為什麼這裡該比安全證據寬鬆,也沒有對應的 REVISIT 或 [test:]。

佐證:
- file: `docs/lumos-toolchain-knowledge/Systems/安全證據閘.md:34` 「判不清就擋(evaluation_error、evaluation_timeout、mainline_unknown…),不走同族的 `_gate_failopen`」。
- file: `scripts/lumos:10935` `_secev_evaluate` 的 `except Exception` 轉 `evaluation_error` 擋下。
- file: `scripts/lumos:63137` `_gate_failopen` 的呼叫端是 lint-new 等,不是安全證據。

## F7 WHY「收集腳本不呼叫 lumos」不實,範本腳本沒說怎麼找 lumos
severity: minor
blocking: 否(實作時看得出來,不會造成錯誤放行)

引句:(收集腳本不呼叫 lumos,這點跟它不同)

收集腳本的 `load_config` 用 `$HERE/../lumos` 找 lumos 並執行 `lumos macrobench --check-config`。新範本腳本要呼叫 judge,也要用同一套找法。但 spec 同時說「相容的 lumos」要在跑驗收的機器上,卻沒說範本放在消費專案的 `scripts/templates/` 時,lumos 位置與 python 直譯器怎麼找,而且收集腳本那個前例的 python3 版本檢查(3.11)和 lumos 自己的 3.14 底線不同。

佐證:
- file: `scripts/templates/android-stability-collect.sh:112` `lumos = os.path.join(here, "..", "lumos")`,`:113` 跑 `lumos macrobench --check-config`。
- file: `scripts/lumos:72` `_PY_FLOOR = (3, 14)`,版本不夠會自行找 3.14 重跑。

## F8 放行的終端確認有三種結果,spec 只處理其中兩種;人明確答 n 可能被記成 AI 放行
severity: major
blocking: 是(違反人意志的放行紀錄會讓閘放行)

引句:有人在終端機答 y → 記成人放行(誰取 git 的 user.name,沒設就取登入帳號);沒有互動終端或沒人回答 → 記成 AI 放行。

`_confirm_tty` 回 `True`(答 y)、`False`(答其他)、`None`(非互動或沒人回答)。spec 只列 `True` 與 `None`。答 n 的人屬於哪一邊沒寫。照字面做「不是 True 就是 AI」(常見寫法 `if ans is True: human else: ai`),人明確拒絕反而會產生一筆放行,而且放行只增不刪、閘認任何一筆放行。另外 `--ack` 同樣用終端確認,`False` 與 `None` 時要不要標成看過也沒寫。

次要:`_confirm_tty` 對無人回答的預設等待是 30 秒,沒有控制終端時才立即回 `None`。AI 無人看顧下每次放行或 ack 要等 30 秒,spec 沒提。

佐證:
- file: `scripts/lumos:33560` `_confirm_tty` docstring:「回 True/False/None」,`LUMOS_TTY_TIMEOUT` 預設 30 秒。

## F9 「只有放行的紀錄」沒有 result,跟 S10 的「result 不認得就擋」衝突
severity: major
blocking: 是(AI 在沒跑過驗收時放行的主要路徑會自己擋自己)

引句:放行寫在紀錄的 `waivers` 清單(只增不刪,之後重跑 judge 不會蓋掉);沒有紀錄就新建一份只有放行的紀錄。

引句:紀錄的指紋欄位跟檔名或重算值對不上、JSON 壞掉、schema 比這版新、或 result 不是認得的值時,判定應擋下(回 1),不走 fail-open

引句:最近一次結果是 pass、或有任何一筆放行 → 過

〈查證紀錄〉定義 `runs`(只留最近一次)內含 result。只有放行的紀錄沒有 `runs`,因此沒有 result 欄位。依 S10,「result 不是認得的值」要擋,依 〈怎麼判〉,有放行就過。兩條規則對這種紀錄給出相反答案,而「紀錄格式」與「放行後的判定順序(先查放行還是先驗格式)」都沒定義。S13 只寫「新建」,沒寫新建出來的紀錄 `runs` 與 `result` 長什麼樣。

## F10 AI 放行的「主動通知」落點:S14 只綁 doctor,開場提示的載體與擋不擋都沒寫
severity: major
blocking: 是(WHY 之一的前提「AI 放行要看得到」沒有可實作、可驗證的落點)

引句:`lumos doctor` 與開場的 lumos 提示列出還沒被人看過的 AI 放行

引句:當有還沒被人看過的 AI 放行時,`lumos doctor` 應列出它們;人用 `waive --ack` 確認後不再列

問題:
1. 開場提示是獨立檔 `lumos-entry-hook.py`,只在專案有 `docs/*-knowledge` 時才印,而且只靠 `lumos enforcement --json`(各層防護有沒有生效的列)加 3 秒預算。未放行的 AI 放行事件不是「防護沒生效」,沒有現成的承載列。spec 沒指定要加什麼。
2. 沒有 `docs/*-knowledge` 的 Android 專案(KDS 現況不明)開場提示整支不印。
3. S14 只綁 `doctor`,開場提示沒有條款也沒有測試。
4. 沒寫要擋還是只提醒:`doctor --ci` 在 CI 跑,「列出」若算警告會讓 CI 變紅,spec 沒規定只提醒。
5. 資料來源是已提交紀錄的 `waivers`,而 `--ack` 改的是工作目錄的紀錄,要提交才會讓另一台機器或 CI 看見已 ack,spec 沒寫提交步驟。

佐證:
- file: `scripts/hooks/claude/lumos-entry-hook.py:287` 沒有 `docs/*-knowledge` 就 `return 0`。
- file: `scripts/hooks/claude/lumos-entry-hook.py:252` 開場唯一的動態內容來自 `enforcement --json` 的列。

## F11 RETIRE-IF 與 REVISIT 需要的帳沒有人寫,事件名也寫錯
severity: minor
blocking: 否(兩條都是回頭看的條件,不影響這次實作能不能完成)

引句:治理帳 android-e2e 的 waived 對照紀錄裡的 pass

引句:回頭看治理帳 android-e2e 的 failopen 次數,不為零就補一條

〈放行〉只記 `waived` 事件;judge 沒有任何寫治理帳的步驟,所以「waived 對照 pass」沒有 pass 的事件可數,RETIRE-IF 無法判。治理帳 fail-open 事件的種類名是 `fail-open`(有連字號),不是 `failopen`,照字面查會永遠是零。「AI 放行佔一半以上」可以從紀錄的 `waivers` 算,但 spec 沒說這條要掃哪裡。

佐證:
- file: `scripts/lumos:63147` `_gate_event_or_warn(repo_root, gate, "fail-open", why, hard=False)`。
- file: `scripts/lumos:4790` `_SLOT_METRIC_KINDS = ("blocked", "warned", "skipped-env", "hinted", "acked")`,沒有 `waived`,所以這條也無法改成機器式 `[retire:度量 …]`。

## F12 check-config 只驗門檻檔有 check 條目,沒驗情境與裝置對得上;格式通過後這塊永遠 unjudged
severity: minor
blocking: 否(原因會印出來,是可診斷的誤擋,並有放行出口)

引句:門檻檔 `.lumos/macrobench-thresholds.json` 裡每一個都要有寫了 check 的條目,缺一個 check-config 回 2。

門檻條目帶 `scenario`(必要)與可選的 `device_model`。`_macrobench_stab_skip_reason` 在 `stab.scenario` 跟條目的 `scenario` 不同、或裝置型號不同時回「跳過」。S5 與表格規定「在 threshold_skipped → 沒判到 → 擋」。所以門檻檔有條目但情境名跟 `stability.scenario` 不同,check-config 回 0,每次驗收都 unjudged 而擋,要靠放行。S1 沒列這種情形。

佐證:
- file: `scripts/lumos:40058` `_macrobench_stab_skip_reason` 對情境不符與 `device_model` 不符都回跳過原因。

## F13 `check-config --env` 要查裝置,跟「lumos 不碰裝置」的已記決策衝突,而且該道檢查沒有條款
severity: minor
blocking: 否(實作者要在兩條自相矛盾的敘述裡自行選一條)

引句:lumos 自己操作裝置(要重寫裝置控制、逾時、收尾)

引句:驗環境:maestro 在不在、toolkit 腳本與基準圖在不在、裝置有沒有連上而且沒鎖屏

WHY 把「lumos 不碰裝置」當被選擇的分工,並以「要重寫裝置控制、逾時、收尾」為由否決另一個做法。`--env` 要 lumos 查 adb 連線與鎖屏狀態,正是這類程式。〈實務隱患〉還承諾 `--env` 對 settings.gradle 裡未列入 `app_dirs` 的模組印提醒;S1 只綁格式驗證,沒有條款綁 `--env` 或那個提醒,等於無測試。

## F14 REVISIT 的條件與其文字不一致
severity: minor
blocking: 否

引句:效能判定統計化第 1、3、4 條都上線後,把毫秒類效能從只提醒改成擋,條款另開

觸發條件是整份「Android效能判定統計化_計劃」status 變成 `done`,不是第 1、3、4 條上線。那份計劃共九條,第 9 條還可能被拿掉;第 1、3、4 條上線後計劃仍可停在 `doing`。後果是回頭條件要等到 2027-06-30 的 `by` 日期才觸發。

佐證:
- file: `docs/lumos-toolchain-knowledge/Projects/Android效能判定統計化_計劃.md:22` 該計劃 REVISIT 另列了第 1、2、3、5 條才是「上線了沒」的檢查。

## 固定席判定:會不會破壞 bound-tests-gate 節點宣稱的行為或合約
不影響,但有一個要實作時注意的點。該節點的 ★INVARIANT★ 說 code-loop check 對受波及合約綁的測試逐支真跑,任一紅、懸空、偽證據、證不出跑過就 `blocked=True` 並回 1;沒 run_cmd 或無固定席或沒綁則不擋,只寫 `gate=bound-tests` 的帳。spec 新增的判定是獨立擋下種類 `android_e2e`,不改 `_bound_tests_check` 的判斷,也不碰 `bt["status"]` 的判定分支,所以那條合約的行為不變。

要注意兩點:
1. spec 把新判定排在安全證據之後、所有放行早退之前。不帶 `--keep-going` 時,e2e 擋下會讓合約測試那道本次不跑,和安全證據擋下時的情形一樣,只要擋下結果不變,合約不受影響。
2. `t_prepush_cl_reason_table_matches_lumos` 是雙向守衛,見 F5。

## 實務隱患逐類
- 金流、對外送出、不可逆:無。spec 只讀驗收輸出與程式檔,紀錄只進專案自己的 git。
- 個資:run 目錄的 junit 與截圖可能含畫面上的使用者資料。收集腳本只對自己的 `ARTIFACTS` 七個檔名做 `check-ignore`。`ui/*.xml`、`visual/*.png` 不在其中,spec 靠 `check-config --env` 檢查產物目錄被忽略,而 `--env` 如 F13 沒有條款。已有 `--env` 一道防線,不另列 finding。
- 併發與資源:`.e2e-lock` 放在 `.lumos/artifacts/android/` 底下,收集腳本的 `prune_old_snapshots` 只處理子目錄、跳過檔案,不衝突。toolkit 鎖用 `mkdir` 目錄鎖,spec 有處理強制中斷殘留。無 finding。
- 外部工具介面:Maestro 2.10.0 的 `maestro test` 認得 `--udid`、`--format`、`--output`、`-e`,PRIOR-ART 的旗標寫法成立。visual-check.sh 的參數與退出碼(0 與 1 與 2)、`MAESTRO_DEVICE` 覆寫、基準圖路徑,都與 spec 一致。

## 逐節已讀
- 檔頭與白話、PRIOR-ART、RETIRE-IF、REVISIT:見 F6、F11、F14。
- WHY 各條:見 F7、F13。
- 〈設定〉:見 F3、F4、F12。
- 〈第一次接入的順序〉:見 F13。
- 〈一次驗收跑什麼〉表:見 F4、F12。
- 〈資料怎麼流〉:見 F2、F3、F8、F9、F10。
- 〈查證紀錄〉:見 F3、F9。
- 〈這次要改到的地方〉:見 F4、F5。
- 〈不做〉:已讀,無 finding。
- 〈實務隱患〉:見 F13 與上方逐類。
- 〈實驗室驗收〉:已讀,無 finding。
- 〈條款〉S1 到 S20:見 F1、F2、F3、F4、F9、F10、F12。S17 到 S20 是 manual 條款,已讀。
- 〈審計修正紀錄〉:已讀,無 finding。
- 〈回退〉:見 F1。

最嚴重 severity:major;blocking 共 9 條(F1、F2、F3、F4、F5、F6、F8、F9、F10)。
