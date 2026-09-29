severity: major

## F1 get.sh 舊複本加 --pull 仍會被叫「加 --pull 重跑」,走不出去
severity: major
blocking: 是 — 照字面做,使用者照訊息加了 --pull 還是回 2,舊複本的機器永遠裝不上
引句:「`get.sh` clone 或已存在之後 source 共用檔;沒有共用檔(舊的安裝複本、沒帶 `--pull`)就印」
file: `get.sh:33-45`
file: `scripts/lumos:18374`
1. get.sh 自己只做「clone(檔不存在時)」,不做 pull;`--pull` 只是原樣轉給 `bootstrap`,真正的 `git pull` 在 Python 的 `cmd_bootstrap` 裡(`_pull_source_or_abort`)。
2. spec 要 get.sh 在 clone 或已存在之後、跑 `bootstrap` 之前 source 共用檔。舊複本(沒有共用檔)加了 `--pull` 時,source 發生在 pull 之前,檔還是不在。
3. 結果:印「安裝複本太舊,請加 --pull 重跑」回 2;使用者照做,同一個順序再走一次,同一個結果。[S4] 的「get.sh 安裝複本沒有共用檔時叫人加 --pull」條款字面實作就是這個死路。
4. 修法方向(不是建議考慮,是缺的東西):spec 要寫明 get.sh 在 `--pull` 時自己先 pull 再 source,或 source 失敗且有 `--pull` 時改交 bootstrap 由 lumos 開頭那份找。

## F2 LUMOS_PYTHON 指到 shim 或包裝腳本時,重跑條件永遠成立,無限 exec
severity: major
blocking: 是 — pyenv/asdf/mise 這類 shim 是常見寫法,字面實作會讓 lumos 與掛鉤卡在無限重跑
引句:「版本低於 3.14,或 `LUMOS_PYTHON` 有設、而且不是目前這一支(兩者都比 `os.path.realpath`)」
1. 重跑條件的第二支是「LUMOS_PYTHON 的 realpath ≠ 目前 sys.executable 的 realpath」;防無限重跑的那段只認「版本卻還是舊」才算失敗。
2. LUMOS_PYTHON=`~/.pyenv/shims/python3.14`(一支 shell 腳本)時:驗候選印出的 sys.executable 是真檔 `.../versions/3.14.x/bin/python3.14`;重跑後新行程 realpath(sys.executable)=真檔、realpath(LUMOS_PYTHON)=shim 腳本,仍不相等,版本又是新的,所以不算「重跑失敗」,再重跑一次,無限迴圈。
3. 我照 spec 字面寫了 30 行模擬(臨時目錄,shim=`exec /opt/homebrew/bin/python3.14 "$@"`):LUMOS_PYTHON=shim 五次重跑後仍不通過;LUMOS_PYTHON=/opt/homebrew/bin/python3.14 一次通過。
4. 同一個判斷式也決定 git 掛鉤(LUMOS_PYTHON 設了 hooks 也生效,第 2 點寫明「效力一樣」),所以 pre-commit / pre-push 也會卡。缺的是:比對對象該是「驗候選時印出的路徑」而不是原字串的 realpath,或重跑次數上限。

## F3 `{python}` 代入漏了第三處讀 run_cmd 的碼,而且沒寫要加引號
severity: major
blocking: 是 — 漏的那處是「測試指令分不分得出找不到測試」的守衛,漏了它會判成可信
引句:「`.lumos/config.json` 的 `run_cmd` 改成 `{python} scripts/test_lumos.py -k {method}`,由 lumos 代入自己的 `sys.executable`」
file: `scripts/lumos:12599`
file: `scripts/lumos:32067`
file: `scripts/lumos:32116`
1. 程式裡拿 run_cmd 換 `{method}` 的地方有三處:guard kill(12599)、真跑合約測試(32116,規格閘也走這裡),以及 `_bound_tests_filter_probe`(32067,拿假測試名多跑一次,確認指令的過濾有效)。spec 只點「合約測試閘與 guard kill」。
2. 冒煙測試漏改時,shell 會執行字面 `{python} scripts/test_lumos.py -k ...`,回 127;該函式把「非 0」一律當「指令分得出找不到測試」,快取成可信 14 天。過濾其實壞掉也照樣判可信,守衛空轉,且沒有任何一條 [S] 會紅([S8] 只驗代入,不驗冒煙測試)。
3. spec 沒寫代入要不要 `shlex.quote(sys.executable)`。同一段程式對 `{method}` 已經 quote;路徑含空白(例如 `/Users/John Doe/...`、`C:\Program Files\...`)不 quote 整條指令壞掉。第 4 點對 hook 命令特別寫了引號,第 6 點沒有。
4. 應該抽一支共用代入函式,三處都呼叫,並在 [S8] 加「冒煙測試那支也用它」與「路徑含空白」兩格。

## F4 spec 對 pre-commit「提早放行」現況的描述與腳本不符
severity: major
blocking: 是 — 照字面加「沒有 scripts/lumos 就放行」會關掉不需要 python 的兩道硬擋
引句:「pre-commit 在圖譜不存在、staged 是空的、沒有 `scripts/lumos` 這三種提早放行之後」
file: `scripts/hooks/pre-commit:36-48`
file: `scripts/hooks/pre-commit:209`
1. pre-commit 現況只有兩個提早放行:Gate 0(圖譜不存在)與 staged 為空。沒有「沒有 scripts/lumos 就放行」;缺 scripts/lumos 時只是每個叫 lumos 的 gate 各自判 `-f` 跳過。
2. 純 shell 的 Gate 1(日期欄位引號污染,rc1 擋)與 Gate 2/3(改程式沒動圖譜,檔尾 `exit 1`)在沒有 scripts/lumos 的專案裡今天照樣會擋。[S3] 寫「沒有 scripts/lumos 時應照舊放行」,「照舊」在 pre-commit 是錯的:測試若造一個有圖譜、有 staged 程式、沒有 scripts/lumos 的 fixture,現況回 1 不是放行。
3. 「確定這次會叫 lumos」在 pre-commit 也沒有單一點:第一個呼叫(Gate CC)是 `|| true` 的提醒,Gate H/NS 是 rc1 才擋。spec 要寫明 source 與擋下擺在 Gate CC 之前,還是擺在第一個「非提醒」的 gate 之前;擺前者,純 shell 的 Gate 1、3 也會被「沒 3.14」先擋掉,那是行為變更,要明講。

## F5 `git config lumos.python` 的寫入指令清單與程式結構對不上,[S1] 字面不可實作
severity: major
blocking: 是 — install 沒有「該 repo」,bootstrap 走另一條路,照清單做會漏寫或寫錯 repo
引句:「lumos init、update、install 跑完應把自己的直譯器寫進該 repo 的 `git config lumos.python`」
file: `scripts/lumos:16370`
file: `scripts/lumos:17442`
file: `scripts/lumos:18277`
file: `scripts/lumos:18421`
1. `cmd_install` 是機器層(symlink、`~/.local/bin`、全域 hooks),沒有 repo 參數;寫「跑完寫進該 repo」在 cwd 剛好是工具鏈 checkout 或任意目錄時,會把設定寫進無關的 repo,或在非 git 目錄失敗。
2. 現有唯一設 git 設定的地方是 `_set_hooks_path`(core.hooksPath),三個呼叫點:`_vendor_toolchain`(update 與 init 都經過,17442)、`_install_hooks_py`(18277)、`cmd_bootstrap` 專案層分支(18421)。bootstrap 有自己的接線路徑,spec 沒列。
3. 對稱面也漏:`deinit` 拆閘只 unset core.hooksPath,`lumos.python` 留在使用者 repo 的設定裡;spec 只在〈回退〉講「留著無害」,沒講 deinit 該不該清。
4. 應改成「`_set_hooks_path` 同一處寫」,並把 [S1] 的指令清單改成 init、update、bootstrap;install 從清單拿掉。

## F6 「3.9 能解析」的守衛只蓋 scripts/lumos,而 spec 也靠另外三類檔的版本檢查;ruff 沒釘版、沒有正向對照
severity: minor
blocking: 否 — 現在這幾支檔都仍能被 3.9 解析(我用 ruff py39 與 3.9 逐支驗過),是未來才會破的守衛缺口
引句:「當 scripts/lumos 被修改,它仍應能被 3.9 語法解析:ruff 以 py39 為目標檢查語法錯誤」
file: `.github/workflows/ci.yml:23`
1. 第 4、6 點承諾 merge-claude-settings.py 與 scripts/test_lumos.py 被舊版直接執行時印說明回 2([S5]、[S8])。這只在該檔本身能被 3.9 解析時成立(Python 先解析整檔)。CI 新增的 ruff 那一步與 [S7] 都只點 scripts/lumos,這兩支沒有守衛;hooks/claude/*.py 在設定還寫著舊直譯器(〈實務隱患〉效能段自己承認的過渡期)時也跑在 3.9,一樣沒守。
2. [S7] 沒有正向對照:ruff 沒裝或版本改口就綠。我本機 ruff 0.16.7 確實把 `f"{d["a"]}"` 報成 py39 語法錯誤,但 CI 那步「裝 ruff」沒釘版本,spec 也沒要求測試造一行 3.12 才合法的樣本確認 ruff 真的會報。守衛靠一個會漂的外部工具而沒有自證。
3. 補法:守衛檔案清單擴到 [S5][S8] 承諾過的三支;測試附一行必紅樣本;ruff 釘版本。

## F7 doctor 新項沒指定落在哪一塊,編號、計不計 issue、怎麼判版本都沒寫
severity: minor
blocking: 否 — 實作者要自己補決策,補錯的代價是誤擋或重複,可逆
引句:「`lumos doctor` 多一項:Claude/Codex 設定裡註冊的直譯器路徑不存在或版本低於 3.14 時提醒」
file: `scripts/lumos:19652`
file: `scripts/lumos:2049`
1. 「註冊了沒、檔在不在」的判斷已經在 `enforcement_status`(獨立的 `lumos enforcement` 指令,19652),不在 `run_doctor`。spec 說放 doctor,沒說跟 enforcement 的既有列怎麼分工,也沒說要不要改它的 `python` 那列(19838,只印 sys.version)。
2. run_doctor 的段落以字母命名(Check C、D、E1–E5、H、J、K、M、N、R、S、S2、T、U、Y、Z、F),而且已經有兩段都叫 Check N(2663、2839)。spec 沒給新段的代號,實作者容易再撞。
3. 沒寫是軟提醒(不計 issues)還是計 issues:`doctor --ci` 是 pre-push 的硬擋。計 issues 的話,brew 升版讓註冊路徑消失後,該機器所有專案推送都被擋,直到重跑 install,與〈實務隱患〉自己強調的「守衛面誤擋」相反。
4. 版本怎麼判沒寫(執行一次那個路徑,還是看檔名),舊註冊可能是裸 `python3`、也可能帶引號含空白的絕對路徑;讀家目錄的測試也要隔離 HOME。[S10] 沒管這幾件。

## F8 第 10 點的測試盤點法會漏掉大半跑掛鉤的測試;掛鉤搬家位置也沒定
severity: minor
blocking: 否 — 漏掉的會在推送前全套紅燈被抓到,只是盤點步驟給了假安全感
引句:(`-k hook` 全跑一次盤點;已知 `t_hooks_python_fallback` 只盯兩支
file: `scripts/test_lumos.py:36611`
file: `scripts/test_lumos.py:16949`
1. `-k` 比對的是測試函式名。名稱含 hook 的 `t_` 函式只有 41 支;真正讀、複製或直接執行 pre-commit / pre-push 的還有 `t_prepush_*`、`t_precommit_*`、`t_codeloop_guard_prepush`、`t_delguard`、`t_gov_adversarial_increment`、`t_escape_auto_unreviewed_twoway`、`t_nodehome_required_files_definition`(我抽查的 19 支,名稱都不含 hook)。它們有的比對腳本原文(把邏輯搬進共用檔後字串斷言就過期),有的用受限 PATH 跑。
2. 「連共用檔一起複製」沒說放哪。36611 那支把掛鉤複製成 `root/pre-push`(不是 `scripts/hooks/`);第 1 點寫「`${BASH_SOURCE[0]}` 或 checkout 路徑定位」二選一沒定,選 checkout 路徑則這類 fixture 全找不到共用檔而走「共用檔不見」擋下。
3. 盤點應改成:對測試檔用 grep 找「hooks/pre-」「pre-push」「pre-commit」的引用列清單,或直接規定定位法(BASH_SOURCE 同目錄)。

## F9 〈範圍〉說排程腳本都經 lumos 啟動,實際上不是
severity: minor
blocking: 否 — 只影響維護者機器,且失敗是維持現況
引句:它們用 `python3 scripts/lumos` 啟動,經第 2 點的開頭檢查會自己改用 3.14;不另改
file: `governance/autonomous-loop.sh:327`
file: `governance/autonomous-loop.sh:383`
file: `governance/autonomous-loop.sh:428`
1. `governance/autonomous-loop.sh` 直接 `python3 governance/eval/retrieval_eval.py`、`refresh_labels.py`、`python3 scripts/scenario_probe.py`、`replay_weekly.py`、`lens_weekly.py` 和很多 `python3 -c`,不經 lumos。它們繼續吃 PATH 的 python3(cron 上多半是 3.9),不會被第 2 點改成 3.14。
2. 這不是要求改,而是這句話寫的前提錯了:三個月後接手的人讀到「都會自己換 3.14」會以為這些腳本已經在 3.14 上驗過。`replay_weekly.py:83` 只有呼叫 lumos 那一處走重跑。應改成「經 lumos 的走第 2 點;其餘照舊,不受下限約束」。

## F10 slim 被凍結、而生成器從 scripts/lumos 衍生,〈範圍〉的前提陳舊且沒交代生成器
severity: minor
blocking: 否 — ⚠ 我沒法在不改 repo 的前提下真跑生成器,影響程度未實測
引句:精簡版 `slim/**`——它是另一個對外發佈的東西,自己承諾
file: `slim/FROZEN.md:1`
file: `scripts/slim-gen.py:1`
1. `slim/FROZEN.md` 寫明 2026-08-20 起交付庫獨立、本目錄只為測試(約 370 處引用)與歷史而在;spec 說它「是另一個對外發佈的東西」已不成立,但結論(不拉下限)不受影響。
2. `slim-gen.py` 的說明明講「root 集合必須含 module-level 語句」,即 scripts/lumos 開頭新加的模組層版本檢查與 LUMOS_PYTHON 邏輯會被原樣帶進產物。⚠ 產物(測試裡的 `dist/scripts/lumos`)因此也會要求 3.14 並可能被 LUMOS_PYTHON 環境變數影響,跟「精簡版不拉下限」的用意反向;spec 沒說生成器要不要剝掉那段、`t_slim_*` 要不要跟著改。

## F11 消費專案 CI 範例不只一處,spec 與 [S6] 都當成一個
severity: minor
blocking: 否 — 漏補的那幾處只是範例文字,消費專案照範例貼才會踩
引句:lumos 建議給消費專案的 CI 範例(`lumos doctor --ci` 等步驟)補上安裝 3.14 的那一步
file: `scripts/lumos:24295`
file: `scripts/lumos:25882`
file: `scripts/lumos:26293`
1. 程式裡至少三處 doctor 提醒會印「CI 貼這一步」的範例 YAML:note-shape(24295)、drift check(25882)、note-audit check(26293),另有各棧 lint 橋的範例;`lumos doctor --ci` 本身沒有範例產生處。spec 用單數「範例」,[S6] 的測試也是單數。
2. 更缺的是偵測面:消費專案既有 CI 是 `setup-python 3.12` 時,升級後 lumos 在 CI 回 2;doctor 目前有偵測「CI 沒呼叫某步」的機制(同一段),卻沒有「CI 的 Python 低於 3.14」的提醒。spec 只補範例,沒補偵測。

## F12 「同一個版本檢查」在 merge-claude-settings.py 與 test_lumos.py 是否含候選清單沒定
severity: minor
blocking: 否 — 只影響要不要多一份清單與同步測試的覆蓋
引句:它自己開頭也加同一個版本檢查(低於 3.14 就報錯回 2、不寫設定)
1. 第 1 點說清單只有「兩處實作加 PowerShell 一份」,[S1] 的同步測試守三份。第 4、6 點又在 merge-claude-settings.py 與 test_lumos.py 各加「同一個版本檢查」,但 [S2] 規定找不到時要列「找過的候選與各自結果、安裝指令」。這兩支若要印同樣的說明就等於第四、五份清單,同步測試沒涵蓋;若只印「需要 3.14、現在是 X.Y」就與 [S2] 的說明內容不同。要寫明是哪一種。

## F13 收尾清單與條款之間還有幾個沒綁的承諾
severity: minor
blocking: 否 — 都是提醒與紀錄類,漏了不改行為,但三個月後沒人查得到
引句:`lumos update` 在消費專案更新到這一版時印一次升級注意
file: `docs/lumos-toolchain-knowledge/Projects/全repo審視_計劃.md:196`
1. 「印一次」沒說狀態記在哪、怎麼判「更新到這一版」(是比對前後版本戳、還是寫一個已提示記號);也沒有任何 [S] 條款與測試綁它。
2. 第 13 點落地驗收(sha256、加引號路徑)只是人跑一次的步驟,沒有條款也沒有回頭條件,做完就沒有痕跡;若要保留,寫進驗證紀錄。
3. 收尾第 11 點只列 F65 「記一行被翻掉」,但 `Projects/全repo審視_計劃` 196 行的 quick win 12 也寫著「把 Python 版本宣告訂成 ≥3.9」,同樣會過期。
4. 第 1 點的三張登記名單漏提:動到的既有錨點檔(pre-commit、pre-push、test_lumos.py)一樣要 `lumos anchor approve` 重簽,不只新共用檔。

## 已讀無 finding
- 〈回退〉:全部回退、只回退擋下、主線已有後續提交三段與第 3 點放行語意一致(放行是整道不跑,不會出現 lumos 回 2 被 pre-push 當成擋下);合併器以 `_equivalent` 依腳本檔名取代舊註冊,遷移與去重確認不會重複註冊。
- 〈誠實界線〉與〈審計修正紀錄〉:各承認條的回頭條件齊備(REVISIT:2026-12-29 一條);紀錄的 51=43+8 對得上,〈範圍〉〈做法〉〈條款〉之間沒有新的前後矛盾(除上面指出的 F4、F5、F9)。
- 第 12 點每支檔有家:`install.sh`、`get.ps1`、`scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh` 確實在圖譜裡沒有家(匹配到的是 slim/ 底下同名檔);`get.sh` 已在 lumos-cli-lifecycle。另 `scripts/hooks/post-commit` 也沒有家,但 spec 不改它,不在這次要求內。
- 收尾 REVISIT:2026-10-29 兩條在 Issue 與測試假綠形態都存在。

最嚴重 major,blocking 共 5 條(F1–F5),另 minor 8 條
