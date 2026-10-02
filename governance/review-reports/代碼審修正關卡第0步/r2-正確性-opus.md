severity: major

# 代碼審修正關卡第0步 設計審第 2 輪:正確性-opus

席名:正確性-opus。鏡頭:正確性與邏輯。實驗都在 `f0-r2-work-正確性-opus/repo`(以 `--shared` clone 出來)裡做;本機其他專案只做唯讀查看。

## F1 測試名白名單在解析之前套在整串上,多平台專案非預設平台的測試永遠記不進修正紀錄
severity: major
blocking: 是
引句:「測試名:去掉前後空白後要過 `_KILL_METHOD_OK_RE` 白名單(含 `]`、空白、shell 字元的直接判不過」
file: `scripts/lumos:13159`
file: `scripts/lumos:38434`
file: `scripts/lumos:4896`

1. 多平台專案要指定非預設平台,唯一的寫法是加平台前綴(`web:t_cart_total`)。`resolve_test_refs` 用冒號切出平台(`scripts/lumos:4896` 那支);如果不加前綴,測試一律歸到 `default_platform`。
2. `_KILL_METHOD_OK_RE` 是 `^[A-Za-z_][A-Za-z0-9_]*$|^[\w .]+$`,不收冒號。推送前那道閘的白名單是在**解析之後**才套到「方法」那一段(`scripts/lumos:38434`)。快照第 86 行卻要求整串測試名先過白名單,也就是在包成 `[test:名]` 之前。
3. 實測(在 clone 裡載入 `scripts/lumos`):`_KILL_METHOD_OK_RE.fullmatch('web:t_cart_total')` 得 `False`;同一串走推送前閘的路徑,`resolve_test_refs('[test:web:t_cart_total]', {backend,web}, 'backend')` 得 `[('web','t_cart_total')]`,方法段過白名單得 `True`。
4. 結果:多平台專案只要修的是非預設平台,修正紀錄寫上帶前綴的測試名,第 1 項就判不過;不帶前綴的話會被歸到預設平台,第 3 項判找不到。兩條路都過不了,好的修正被判不過。S4 的「多平台設定時判法應一樣」只在測試剛好屬於預設平台時才成立。
5. 第 3 項已經寫明要用從 `_bound_tests_for_diff` 抽出來的共用函式,它本來就在解析之後驗白名單。所以第 86 行的「解析前先驗」整條是多出來的。真正需要在解析前擋的只有會讓 `[test:]` 切錯的字元(`]` 會截斷、`,` 會切成兩支)。

## F2 「測試名含空白就判不過」跟白名單本身、跟推送前閘支援的 Kotlin 反引號測試名互相矛盾
severity: major
blocking: 是
引句:「`at` 的檔是資料夾或符號連結或含 `..`、測試名含 `]` 或空白,也應各自回 1 並寫出是哪一組哪一條」
file: `scripts/lumos:13159`
file: `scripts/lumos:5166`

1. 白名單的第二個分支 `^[\w .]+$` 明明收空白。程式旁的註解也寫了「IDENT 或 Kotlin 反引號拆殼後白名單」;Kotlin 的測試掃描會把反引號拿掉,留下帶空白的方法名(`scripts/lumos:5166`)。快照第 86 行說「要過白名單」,括號裡卻又說「含空白的直接判不過」,S1 也照後一種寫。這兩句不可能同時成立。
2. 實測:`_KILL_METHOD_OK_RE.fullmatch('兩項都有就組成 base 加店號參數')` 得 `True`;推送前閘解析出 `[('backend', '兩項都有就組成 base 加店號參數')]`,當成合法測試。
3. 本機真實專案(唯讀查看):`/Users/enzo/mOrangePos` 有 56 支 Kotlin 測試檔用反引號帶空白的名字,`/Users/enzo/AndroidProject/CompassKiosk` 也有,例如 `` fun `兩項都有就組成 base 加店號參數` ``。
4. 照 S1 實作的話,要另加「含空白就擋」的規則。這兩個專案的修正一旦列出這種測試(推送前閘認得、合約也綁得到),第 1 項就判不過,好的修正被判不過。反過來照「過白名單」實作,S1 的「測試名含空白回 1」就驗不到。實作者要嘛違反 S1,要嘛擋掉 Kotlin。
5. 這兩個專案目前沒設 `run_cmd`,所以現在第 4 項本來就會擋;等它們設了指令,上面的情況就會出現。

## F3 依賴資料夾預設不連時,Node 專案的 `npx` 會在樹裡從網路下載並執行沒鎖版本的測試工具;「不連網」的排除不成立
severity: major
blocking: 是
引句:「已排除:對外送出:只在本機跑測試與讀寫帳本,不連網」
file: `scripts/lumos:13988`
file: `/Users/enzo/.nvm/versions/node/v24.16.0/lib/node_modules/npm/docs/content/commands/npm-exec.md:29`

1. 本機兩個 Node 專案的設定(唯讀查看):`/Users/enzo/harness/pos-api` 的 `run_cmd` 是 `npx jest -t {method}`,`/Users/enzo/harness/pos-guest` 是 `npx vitest run -t {method}`。
2. 這一版改成預設不連依賴資料夾,所以樹裡沒有 `node_modules`。npm 11.13.0 官方文件第 29 行寫的是:「When standard input is not a TTY or a CI environment is detected, `--yes` is assumed.」
3. `_kill_run` 用 `Popen(shell=True)` 跑,沒有另外設 stdin(`scripts/lumos:13988`)。在對話的 Bash 或背景執行時,stdin 都不是終端機。所以 `npx jest` 會自動去 npm 下載當下最新版的 jest 並執行。第 5 項的過濾探針(`_bound_tests_filter_probe`)也會跑同一條指令。
4. 後果有兩層:
   - 第一,外連下載並執行沒鎖版本的程式,跟「已排除:對外送出」相反。
   - 第二,結果不可信:下載來的 jest 沒有專案的 ts-jest、babel 這類設定依賴,多半判紅,而輸出說的是「紅」,不是「缺依賴」;純 JS 的測試則可能用一個跟 lockfile 不同的版本判綠。
5. 快照第 107 行說「需要依賴才跑得起來的測試會在第 4、5 項判不過」,這個假設是「缺依賴就乾淨地失敗」,對 `npx` 不成立。`uv run`(`/Users/enzo/crypto-autotrade` 的 `uv run pytest tests -k {method}`)也是同一類:樹裡沒有 `.venv`,它會當場建一份並同步依賴,快取沒中就連到 PyPI。
6. 這是這一版從「預設連」改成「預設不連」帶進來的(guard kill 本來就不連,是既有行為;但修正關卡每輪都會跑,頻率高得多)。實際外連未實測(會打到 npm registry),依據是 npm 官方文件與兩個專案的實際設定。

## F4 本機的 pos-ios 今天就踩到「平台資料夾沒進版控就回 2」:提醒永遠消不掉,跳過紀錄會污染撤除條件的數字
severity: major
blocking: 是
引句:「平台資料夾沒進版控(樹裡沒有)都回 2,說明是哪個平台、為什麼」
file: `scripts/lumos:4852`

1. `/Users/enzo/harness/pos-ios`(唯讀查看)的 `.lumos/config.json` 有進版控,宣告兩個平台:`ios`(root `.`)與 `maestro`(root `.maestro/`,沒有 `run_cmd`)。`git status --porcelain --ignored .maestro` 印的是 `?? .maestro/`,這個資料夾沒進版控。這個專案的審查帳裡已經有 3 筆 `code-` 迴圈的紀錄。
2. 照快照的「樹裡的先決條件」,每次 `fix-check` 都會回 2,即使修正只動 ios、紀錄裡的測試全在 ios 平台,而 maestro 平台根本沒有測試指令、也用不到。理由那句「沒進版控的平台資料夾每支測試都判找不到」只對**那個平台**的測試成立,卻擋掉了整個專案。
3. 回 2 不記帳,`loop next` 每輪都會提醒,唯一能消掉提醒的辦法是 `LUMOS_SKIP_FIX_CHECK`,會被記成 `skipped-env`。RETIRE-IF 寫的是「跳過比例超過三成」就撤掉整案。這種專案的跳過跟「修正關卡值不值得」無關,卻會算進撤除條件。
4. 快照把這種專案的回頭條件寫成「第一個要用修正關卡的多根專案出現時……靠使用者回報」。pos-ios 現在就已經符合,這個條件形同已觸發,卻沒有被處理。
5. 修法方向(讀碼可行):只對這次會用到的平台驗平台根,也就是紀錄裡測試解析出來的平台,加上受波及合約綁定的平台。其他平台的根不存在時印提醒就好,不回 2。⚠ 這是編排者的範圍取捨,交編排者判要不要改。

## F5 連依賴時,要把「平台根」對回主工作目錄的同一位置,但快照只對先決條件與清殘骸規定要取實際路徑;而且這一步排在先決條件之前
severity: minor
blocking: 否
引句:「repo 頂與每個平台根各用 `_lint_link_deps` 把 `node_modules`、`.venv`、`venv` 連回主工作目錄的同一位置」
file: `scripts/lumos:4852`
file: `scripts/lumos:23630`

1. 多平台時 `load_platforms` 給的平台根已經 `.resolve()` 過(`scripts/lumos:4852`),但樹的路徑來自 `tempfile`,沒有取實際路徑。實測:`mkdtemp` 得 `/tmp/lumos-fixcheck-…`,子資料夾 resolve 後是 `/private/tmp/lumos-fixcheck-…/app`,`relative_to(樹)` 丟 `ValueError`;本機 TMPDIR 是 `/var/folders/…`,也一樣。
2. 要找「主工作目錄的同一位置」就得算平台根相對於樹的路徑。快照只在先決條件與清殘骸寫了「先取實際路徑」,這一步沒寫。照字面實作的話,多平台加上 `link_deps: true` 時,在 macOS 上準備階段就會丟例外。
3. 快照把「樹的準備」(含連依賴)排在「樹裡的先決條件」之前。所以平台根寫在 repo 外、又開了 `link_deps` 時,會先走到連結那一步(丟例外,或在主工作目錄底下建連結),到不了本來該印原因的回 2。⚠ 實作者可能自己取實際路徑,所以標 minor。
4. 修法:定義「樹」時就一律用取過實際路徑的 `Path`;連依賴放到先決條件之後再做。

## 已核對、沒有 finding 的重點(派工詞點名的幾項)

- **單平台(平台根就是 repo 頂)**:舊式單一設定時 `load_platforms` 給的 root 就是傳進去的樹本身(`scripts/lumos:4838`)。實測 `Path.is_relative_to` 在兩邊相等時回 `True`,取實際路徑後比對可以正確判過。多平台寫 `root: "."` 時 resolve 出來也等於樹的實際路徑。
- **平台根是符號連結**:連結指向樹裡面,resolve 後還在樹底下,判過;指向主工作目錄(絕對路徑)或 repo 外(相對路徑 `../x`,在樹裡懸空),resolve 後落在樹外,回 2。判法正確。
- **設定檔沒進版控時複製進樹的時機**:①、② 兩步不讀設定;建樹之後「樹的準備」先列設定檔、再列依賴,最後才判先決條件、呼叫 `load_platforms(樹)`。順序沒問題,只是 F5 指出的連依賴那一步排太早。
- **依賴資料夾預設不連時,本 repo 跑不跑得起來**:`{python}` 會換成 lumos 自己用的直譯器(`scripts/lumos:13961`),測試總檔零依賴,而且用 `__file__` 找到樹裡那份 `lumos`。實測:在 clone 開一棵隔離工作樹(沒有 `.venv`、沒有 `node_modules`),跑 `python3 scripts/test_lumos.py -k t_platform_index_consumers_drift_guard`,得 `3 passed, 0 failed`、rc=0,收樹之後 `git worktree list` 沒有殘留。
- **三處規格閘副本抽成一支後,印出來的字面能不能不變**:實際讀了 `_spec_gate_push_one`。它的 `_ran_count((plats.get(pl) or {}).get("profile_name"), …)` 跟另外兩處的 `per_prof(plat)` 等價;三處都只用到 `(編號, 平台, 方法, 紅綠弱, 原因)`,相依回歸另外用 `detail`,也就是 `_run_bound_tests` 回傳的第 5 個值;各自的聚合、印出、跑不起來時的處理都留在呼叫端。所以抽成 `_spec_gate_judge_items` 之後字面可以不變。快照引句:「失敗細節=`_run_bound_tests` 回傳那筆結果裡的細節欄(第 5 個值,不是另外收的輸出尾巴)」,與 `scripts/lumos:6667` 一帶對得上。
- **改名只提醒**:`_drift_m1_code_kind(p, first_line)` 真的存在,而且收首行參數(`scripts/lumos:31030`),快照的寫法可以實作。
- **loop next 認不認得修正紀錄**:修正紀錄放在 `governance/review-reports/`,這個資料夾在 `_BOOKKEEPING_DIRS` 裡(`scripts/lumos:22681`),所以 fix-check 之後才提交紀錄,不會讓事件失效。

## 實務隱患鏡頭(逐類)

- 跳脫與清洗:見 F1、F2,測試名白名單套的時機與內容都有問題。
- 路徑處理:見 F4、F5;先決條件本身(單平台、符號連結)已核對,沒有問題。
- 外連與供應鏈:見 F3。
- 並行與交易邊界:清殘骸只動超過一天的,隔離工作樹讓別的會談改檔不影響結果。沒有 finding。
- 效能與記憶體:這一版沒改耗時估計;F3 的 `uv run` 每次都會在新的樹裡重建環境,另外加時間,不另列。
- 金流、不可逆:快照已排除,核對過沒有反例。

最高等級:major,blocking 共 4 條
