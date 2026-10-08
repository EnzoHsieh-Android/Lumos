severity: major

# 代碼審修正關卡 設計審第 2 輪 — 正確性-opus(鏡頭:正確性與邏輯)

實驗環境:`git clone --shared` 到 `fg-r2-work-正確性-opus/repo`,在 clone 裡造提交,寫了一支照第 4 項字面判法的模擬器(`fg-r2-work-正確性-opus/sim.py`:兩棵 `worktree add --detach 修正後`、紅樹把 `git diff --no-renames --name-status base 修正後` 裡 `_nodehome_is_test` 判否的檔換回 base、跑 `run_cmd` 帶 `{method}`、用真的 `_ran_count("python", 輸出)` 判)。另寫 `bt.py` 在綠樹真呼叫 `_bound_tests_check(綠樹, "base..修正後")`。

先講判對的(核對過、不報):
- 真修正+好測試 `t_fcgood`:綠 rc0/1 支、紅 rc1/1 支 → 過。弱測試 `t_fcweak`(修前修後都過):紅 rc0 → 「修之前就通過」。子字串撞名(紀錄寫 `t_fcdemo`、另有 `t_fcdemo_strip`):紅讀到 2 支 → 不過。修正只改資料檔(`scripts/fcdemo_limits.json`,非測試檔):紅樹換回舊值、測試紅 → 過。四種都判對。
- 本 repo 執行器 `-k` 是 `keyword in t.__name__` 子字串比對,選中 0 支時印到 stderr、回 1、不印「lumos 測試(N 案例)」;`_ran_count` 的第一條樣式讀的是篩選後的支數,不是全套支數——紅要求恰好 1 支在本 repo 讀得對。
- `_bound_tests_check(綠樹, "e0083b3..eba11ef")` 在工作樹路徑當 repo_root 時:找得到圖譜(`_vault_in` 看工作樹的 `docs/*-knowledge`)、讀得到工作樹裡受版控的 `.lumos/config.json`、`_bound_tests_range` 對非空樹起點原樣放行、`cmd_impact_diff` 在工作樹(`.git` 是檔)照常算;實測 `status green ran 59 secs 258.2 calc 17.36`,主 repo 治理帳 sha 前後都是 `d7491d262df5`,綠樹的治理帳從 `d7491d262df5` 變成 `48017fbd0c56`,`~/.cache/lumos/bound-filter` 沒有多出檔(python 有跑過證據樣式,不跑探針)。「寫帳只落在工作樹」對 python 棧成立(其他棧見 F8)。

---

## F1 紅那邊「支數 ≥2 → 不過」把參數化測試當撞名,本 repo 已修過的同一個誤擋又回來了
severity: major
blocking: 是
引句:「支數 ≥2 → 不過:「名字選中 N 支,判不出是不是這一支紅;換一個不會被別支名字包含的名字」(篩選是子字串比對)」
file: `scripts/lumos:38498`
file: `scripts/lumos:6564`
file: `scripts/lumos:6587`
file: `scripts/test_lumos.py:47562`

1. `_ran_count` 讀的是「收集到幾個案例」,不是「選中幾支測試」。pytest 參數化一支測試餵 3 組輸入,紅樹輸出 `3 failed in 0.05s`,實測 `_ran_count("python", ...)` 回 `(3, False)`;綠樹 `3 passed` 也回 3。
2. 照第 4 項字面,紅那邊 3 ≥ 2 → 回 1「名字選中 3 支」。但程式裡只宣告了一支,換名字也沒用——修正關卡對所有參數化的回歸測試永遠不過。修跳脫、邊界值、巢狀這幾類(固定清單裡的 `escaping`、`boundary`、`nesting`)最常見的回歸測試寫法就是參數化餵一串壞輸入。
3. 這正是本 repo 2026-09-22 已經被消費專案打過一次的坑:規格閘原本也只看案例數,rtb 4 支合約測試收集到 5/5/9/25 個案例全被判「測試名要唯一」,後來改成 `_spec_gate_declared` 數「程式裡宣告了幾支名字對得上」、`_spec_gate_verdict` 在 `declared == 1` 時不判撞名(`t_spec_gate_parametrized_is_not_weak` 釘著)。實測同一組輸入 `_spec_gate_verdict(3, False, "red", "", declared=1)` 回 `('red', '')`,判對;修正關卡照字面會判錯。
4. 這份計劃的動機專案就是 rtb(Python),第一個跑修正關卡的消費專案就會撞到。
5. 條款 S4 只寫「名字在紅樹選中 2 支以上時應回 1」,照它寫的測試會把這個誤擋釘成規格。

## F2 紅樹逾時判「不過」,修無窮迴圈或卡死的正確修正一律過不了
severity: major
blocking: 是
引句:「0 結束 → 不過:「修之前就通過,沒守住這次的問題」;逾時 → 不過。」
file: `scripts/test_lumos.py:31423`
file: `scripts/test_lumos.py:31947`
file: `scripts/lumos:13976`

1. 輸入:base 的 `_fchang(n)` 在 n 為奇數時 `while n != 0: n -= 2` 永不結束;修正改成 `while n > 0`;測試 `t_fchang` 斷言 `_fchang(3) == 1`。
2. 實測(`LUMOS_TEST_TIMEOUT=8`,模擬器照第 4 項跑):`t_fchang: green(rc=0,n=1)→過 | red(rc=TIMEOUT,n=None)→不過:逾時`。修正對、測試對,關卡判不過。
3. 為什麼一定是外層逾時先到:執行器自己的單支逾時 `TEST_TIMEOUT_SEC` 跟外層 `_kill_run` 讀同一個 `LUMOS_TEST_TIMEOUT`(預設都是 180 秒),外層從行程啟動算、內層從那支測試開始算(中間還要載入六萬行的測試檔),外層永遠先砍,內層「TIMEOUT 判紅」那條路走不到。
4. 紅樹卡死正是「修之前會壞」的證據,不是「沒驗到」。固定清單裡有 `perf-memory`、`nesting`,動機段的實例也是「修補造成深層巢狀當機」;這類修正的回歸測試在修之前的典型表現就是卡住。照字面,這類修正每次都要等滿 180 秒、然後被判不過。
5. 綠那邊逾時判不過是對的;紅那邊應該拆開判,不能跟綠共用「逾時=不過」。S4 沒有任何一句涵蓋紅樹逾時。

## F3 紅樹按路徑判測試檔:放在非測試路徑的輔助檔被換回修正前,弱測試照樣過;S4 自己的條款也跟做法互相矛盾
severity: major
blocking: 是
引句:「非測試檔一律換回 `base` 的內容(`base` 沒有的就刪掉);測試檔、輔助檔、測試資料都留修正後的版本」
引句:「紅樹裡非測試的輔助檔(例:不在測試資料夾的共用夾具)應是修正後的版本」
file: `scripts/lumos:24776`

1. 〈做法〉的規則只有一條:`_nodehome_is_test` 判否就換回 base。輔助檔有沒有留下,全看它的路徑或檔名有沒有被判成測試檔,跟「它是不是輔助檔」無關。實測 `_nodehome_is_test`:`scripts/fcdemo_helpers.py`、根目錄 `conftest.py`、`src/app/testing_utils.py`、`fixtures/expected.json` 都是 False(會被換回 base);`tests/conftest.py`、`tests/data/x.json` 是 True。
2. 會放過的輸入:修正在 `scripts/fcdemo_helpers.py` 新增 `pad()`,紀錄寫的測試 `t_fchelpweak` 只呼叫 `pad("a")`,完全沒碰被修的 `_fcdemo`。實測:`t_fchelpweak: green(rc=0,n=1)→過 | red(rc=1,n=1,skip=False)→紅,過`。紅樹的輔助檔被換回 base、import 失敗、算「真的跑了、真的失敗了」,一支沒驗修正的測試就這樣過了先紅後綠。
3. 反方向會誤擋:被判成測試檔的產品檔(`specs/` 底下、檔名結尾 `_spec`、`_test` 的,例如 `specs/api.py`、`src/latest_spec.py`、`scripts/stress_test.py` 實測都是 True)在紅樹裡留修正後的版本。修正如果改在這種檔,紅樹=綠樹 → 「修之前就通過」→ 誤擋。
4. 條款跟做法矛盾:S4 要求「不在測試資料夾的共用夾具」在紅樹裡是修正後的版本,但照〈做法〉,這種檔判成非測試檔、會被換回 base。照 S4 寫的測試(夾具這次有改)在照〈做法〉寫的實作上一定紅;要讓它綠,就只能讓夾具這次沒改(測試就沒驗到東西),或偷偷改掉〈做法〉。〈跟提案不同〉那句「效果一樣是「只有修正被拿掉」,但測試的輔助檔、資料不會漏」對這類輸入不成立。

## F4 只改測試的修正(發現是「測試沒釘住」)紅樹等於綠樹,一律判「修之前就通過」
severity: major
blocking: 是
引句:「文件、流程類的折入(`finding_kinds` 記 `spec`/`process`)不要求修正紀錄:寫不出先紅後綠的測試」
file: `scripts/lumos:8652`

1. 輸入:發現是「`t_fcweak` 沒釘住 strip 行為」(本 repo 代碼審最常見的一型:翻紅釘、守衛繞得過);修正只在 `scripts/test_lumos.py` 補一條斷言,產品程式沒動。base 是修正前的提交。
2. 實測:`t_fcweak: green(rc=0,n=1)→過 | red(rc=0,n=1)→不過:修之前就通過`。base..修正後只動到測試檔,紅樹沒有東西要換回,紅樹=綠樹,這類修正數學上就不可能過。
3. 逃生口不存在:`finding_kinds` 只有 `code`/`spec`/`process`(`cmd_canary` 寫側只收這三個值),「測試寫弱」是程式缺陷,誠實記帳只能記 `code`,所以要落在某一組;紀錄完整又要求每組至少一條 `fixed` 路徑配測試。唯一能過的辦法是 `LUMOS_SKIP_FIX_CHECK`(會算進跳過比例、影響 RETIRE-IF),或把它謊記成 `process`(污染流程自產工作量那個指標,〈canary record --regression-set〉那節自己說這個欄位不能被弄壞)。
4. 這不是罕見情況:「測試沒釘住」本來就是代碼審的常見發現,而這道關卡第一次被誤擋時,編排者學到的會是「這關不準」。判法要能分辨「修正只動測試」(紅樹該換回的是測試前一版、看新斷言在舊測試下是否不存在),或至少讓這類組有明確的判法與輸出,而不是一律回 1。

## F5 跳過的判法兩邊都錯:綠樹被跳過判過;紅樹失敗輸出裡出現「1 skipped」字樣就判不成紅
severity: major
blocking: 是
引句:「**綠**:0 結束而且讀得到支數 ≥1(讀不出支數的棧改用 `_ran_evidence_check`;這棧也沒有實測過的輸出樣式時,照合約測試閘的做法退回過濾探針)→ 過」
引句:「非 0 結束而且支數恰好 1、沒有被跳過 → 紅,過」
file: `scripts/lumos:38507`
file: `scripts/lumos:6590`

1. 綠樹跳過也判過:測試 `t_fcgskip` 先碰新函式 `_fcnew`,再 `raise _SrcOnly("需要外部工具,這台沒有")`。實測 `green(rc=0,n=1,skip=True)→過 | red(rc=1,n=1,skip=False)→紅,過`:一條斷言都沒跑過的測試通過整項。隔離工作樹本來就比主目錄少東西(被忽略的檔、沒連的依賴),環境不足就跳過的測試在綠樹最容易跳過。本 repo 規格閘的判法 `_spec_gate_verdict` 已經把「n == 1 且被跳過」判成弱證據,這裡的綠沒有沿用。
2. 紅樹被誤判成跳過:`_ran_count` 的跳過偵測是對整段輸出跑 `skipped\s*=\s*[1-9]|\b[1-9]\d*\s+skipped\b`,失敗的測試印出的說明也算進去。好測試 `t_fcskiptext` 的失敗說明裡帶子執行器的摘要「0 passed, 1 skipped」(本 repo 測合約測試閘、規格閘、執行器跳過基準線的測試,失敗時都會印子程序的 stdout 尾巴)。實測 `red(rc=1,n=1,skip=True)`。照第 4 項字面,這不符合「沒有被跳過 → 紅」,其他分支也都不收「非 0、1 支、被跳過」這個組合,判法沒定義。實作照「不是紅就不過」就會誤擋一個正確的修正。
3. S4 兩種情況都沒釘。

## F6 依賴資料夾連回主工作目錄,紅樹會載到主目錄裡修正後的程式,正確修正被判「修之前就通過」
severity: major
blocking: 是
引句:「兩棵樹在平台根都把依賴資料夾連回主工作目錄(`_lint_link_deps`:`node_modules`、`.venv`、`venv`;那些不進版控,隔離工作樹裡沒有會整個跑不起來)」
file: `scripts/lumos:23630`
file: `scripts/lumos:23590`

1. `_lint_link_deps` 是給新增告警閘用的:靜態檢查只要「載得動外掛」,不在乎套件從哪裡載入。先紅後綠要的剛好相反:紅樹必須載到「換回 base 的那份程式」。
2. 會打破它的輸入:Python 專案用 src 版面加可編輯安裝(hatchling、uv、舊式 `pip install -e` 都會在 `.venv` 的 site-packages 放一個 `.pth`,寫著主目錄 `src/` 的絕對路徑)。最小重現(`fg-r2-work-正確性-opus/pyproj`):base `f(s)` 回 `s`,修正改成 `s.strip()`;紅樹把 `src/mypkg/__init__.py` 換回 base、`.venv` 連回主目錄,在紅樹執行:
   ```
   $ cat src/mypkg/__init__.py      → def f(s): return s        (紅樹確實是修正前)
   $ .venv/bin/python -c "import mypkg;print(mypkg.__file__)"
   imported from .../pyproj/src/mypkg/__init__.py                 (載到的是主目錄=修正後)
   $ .venv/bin/python -m unittest -k test_strip
   Ran 1 test ... OK
   ```
   紅樹的測試通過 → 「修之前就通過」→ 回 1。所有用 src 版面加可編輯安裝的 Python 消費專案,每一組都會這樣被擋。
3. Node 的同一型:npm/pnpm workspaces 的 `node_modules/@scope/pkg` 是指向 `../../packages/pkg` 的相對連結;`node_modules` 整個連回主目錄後,`require("@scope/pkg")` 解析到的是主目錄的 `packages/pkg`(修正後)。monorepo 裡修正落在 workspace 套件時,紅樹一樣載到修正後的程式。
4. 失敗方向是擋,而且輸出會叫人「換測試」,人查不出真正原因。〈實務隱患〉的「隔離工作樹缺東西」只講到缺東西會讓綠不過,沒講多出來的連結會讓紅失真。

## F7 `loop next` 把「事件之後只改了 `governance/`」當成仍然通過,但本 repo 的 `governance/` 底下就有程式與它的測試
severity: major
blocking: 是
引句:「事件的 `head_sha` 跟現在的 `HEAD` 之間沒有 `docs/` 與 `governance/` 以外的檔案改動(那個提交已經不存在也算有改動)」
file: `governance/autonomous_loop/gap_select.py:1`
file: `scripts/test_autonomous_loop.py:5`

1. 本 repo 受版控的 `governance/` 底下有一整包程式:`governance/autonomous_loop/*.py`(`gap_select.py`、`backlog.py`、`run_ledger.py` 等)、`governance/autonomous-loop.sh`、`governance/daily-governance.sh`、`governance/eval/*.py`。`scripts/test_autonomous_loop.py` 直接 `from autonomous_loop import backlog, gap_select, ...`,`test_lumos.py` 也有測試去跑 `governance/eval/lens-utilization/recount.py`。
2. 會放過的輸入:某個代碼審迴圈審的是自主迭代 loop,第 r2 輪修正後 `fix-check` 在提交 Y 通過;編排者接著又改 `governance/autonomous_loop/gap_select.py` 並提交成 Z。`Y..Z` 只動到 `governance/` → 照字面仍然算通過、`loop next` 不提醒。「修補之後又改了程式卻沒人驗」正是這道關卡要抓的情況;到上限那條路更糟,因為〈做法〉自己說「推之前跑一次修正關卡是唯一的機械檢查」。
3. 先決條件同一個洞:`governance/` 底下沒提交的程式改動被放行,兩棵樹跑的是提交版,修正其實還在工作目錄裡。失敗方向雖然是擋,但印的是「`fixed` 的檔沒改過」或綠不過這類誤導訊息,而不是「先提交修正」。
4. 排除 `governance/` 原本是為了修正紀錄與帳本。只要排除那幾個確定的路徑(這一輪的 `<輪>-fix.json`、帳本檔),或沿用 r1 版的「判程式檔」那一層,就不會把程式一起排掉。S8 只釘了「只改 `docs/`」,`governance/` 的豁免沒有任何測試。

## F8 第 5 項在綠樹跑時,`TMPDIR` 沒有傳進去,過濾探針快取也永遠對不到
severity: minor
blocking: 否
引句:「它寫的治理帳事件落在綠樹裡、跟著刪掉,不進主 repo 的帳」
file: `scripts/lumos:38641`
file: `scripts/lumos:38571`

1. 第 4 項說跑測試時 `TMPDIR` 指到修正關卡自己的暫存資料夾,`_kill_run` 也加了帶環境變數的參數;但 `_bound_tests_check` → `_run_bound_tests` 呼叫 `_kill_run(cmd, root, timeout, keep_re=...)` 時沒有這個參數,〈做法〉也沒說要一路傳下去。第 5 項紅的合約測試照樣把 `gctl-test-*` 暫存現場留在系統暫存資料夾。
2. `_bound_tests_filter_probe` 的快取鍵含 `realpath(root)`,而 root 是每次新開的暫存工作樹。kotlin-junit、java-junit、dart、node-vitest、playwright、maestro 這六種沒有跑過證據樣式的棧(實測 `_RAN_EVIDENCE` 只有 csharp-xunit、node-jest、python、swift-xctest),每次修正關卡都會多跑一次探針(Gradle 這種就是一次完整建置),還在 `~/.cache/lumos/bound-filter/` 留下一個以後永遠用不到的快取檔。「副作用只落在工作樹」對這六棧不成立。

## F9 總時間上限打斷不了第 5 項,也打斷不了正在跑的那一支;S11 釘不到
severity: minor
blocking: 否
引句:「`.lumos/config.json` 的 `fix_check.max_minutes`(預設 20)用完,還沒跑的測試與項目不跑、這項判不過」
file: `scripts/lumos:38725`

1. 第 5 項是一次 `_bound_tests_check` 呼叫,裡面自己逐支跑完。本 repo 改到 `scripts/lumos` 的修正實測要跑 59 支、258 秒,最壞情況是 59 × 180 秒。只要第 5 項在預算用完前一秒開始,就會整段跑完才停。單支測試的逾時也還是固定 180 秒,不會縮成剩下的預算。
2. 「總時間」實際上是「開始下一支之前檢查一下」,上限能超出多少沒有界線。S11 只寫「停止還沒跑的測試」,照它寫的測試釘不到這兩種超時。

## F10 Python 這次讀不出支數時,「這棧讀不出支數 → 算紅」會把一次都沒跑到的測試判成紅
severity: minor
blocking: 否
引句:「這棧讀不出支數 → 非 0 結束就算紅,但輸出標「讀不出跑了幾支」讓人自己判斷」
file: `scripts/lumos:38498`

1. 條款的意思是整個棧讀不出支數,但實作只拿得到 `_ran_count` 這一次的回傳值。pytest 一支都沒選到時輸出 `4 deselected in 0.01s`、回 5,實測 `_ran_count` 回 `(None, False)`,跟「這棧讀不出」分不開。
2. 輸入:pytest 設了 `python_files = check_*.py`,新測試寫在 `check_x.py`。這支檔 `_nodehome_is_test` 判否,在紅樹裡被刪掉,紅樹選到 0 支、回非 0、`_ran_count` 讀不到支數 → 照字面判紅、過。可是那支測試在修之前一次都沒跑到。條款裡「工具明說選中 0 支 → 不過」那條路,要求實作自己認得 pytest 的 `deselected`/`no tests ran`,但〈做法〉只寫了用 `_ran_count` 讀。

---

## 各節核對

- 名詞:已讀,無 finding(「測試檔/非測試檔」的定義本身沒錯,問題在第 4 項怎麼用它,見 F3)。
- 範圍:已讀,無 finding。
- 修正紀錄:已讀,無 finding。`at` 在第一個冒號切開、`fixed` 檔要有改動,兩條都驗得到。
- fix-check 先決條件:見 F7 第 3 點,其餘無 finding。
- 第 1、2、3 項:無 finding。`--finding-severity` 寫側要求給全集(`scripts/lumos:8669` 那段),所以「沒記的那條」只會是整欄沒給。帳上 315 筆代碼審載體席只有 66 筆帶這欄,退回「這一輪各席最高」是常走的路;它只會往嚴的方向錯(某組其實都是 minor,卻被同輪另一條 major 拖著要寫 `prior`),不會放水。315 筆載體席全都帶 `round`,這個前提成立。
- 第 4 項:見 F1–F6、F10。
- 第 5 項:實測在工作樹裡可以用(見開頭),另見 F8。
- 第 6 項:見 F9。
- 記帳與跳過:已讀,無 finding(`token` 已經在 `_GOV_FIELD_TYPES` 裡,型別是 str)。
- 中斷與殘骸、共用隔離工作樹:已讀,無 finding。
- `loop next` 提醒:見 F7。`finding_kinds` 免紀錄的判法本身沒錯;F4 講的是它沒涵蓋到的那一類。
- `canary record --regression-set`、第 2 步、上線、跟提案不同、回退:已讀,無 finding。
- 條款:S4 見 F1、F2、F3、F5;S8 見 F7;S11 見 F9。S1–S3、S5–S7、S9、S10、S12–S16 照寫出來的測試釘得住它們說的行為,無 finding。

## 實務隱患鏡頭

- **判對與判錯(本鏡頭主項)**:見 F1–F7、F10。
- **時間**:實測第 5 項 258 秒、算波及 17 秒,跟〈實務隱患〉估的「約 4 分鐘」相符。見 F2(紅樹卡死要等滿 180 秒)、F9。
- **並行與殘骸**:實測兩棵樹都是 `--detach` 的獨立工作樹,主 repo 的治理帳沒動;無 finding。
- **檔案系統副作用**:見 F8。
- **金流、對外送出**:無。只在本機跑測試、讀寫帳本。
- **不可逆**:無。工作樹跑完就收,帳本只追加。

最高等級:major,blocking 共 7 條
