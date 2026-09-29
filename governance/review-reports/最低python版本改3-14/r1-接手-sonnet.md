severity: major

鏡頭:整合與知識同步。對照的程式碼 repo 是 clone-314(HEAD 4990a90a)。固定席節點沒有附進派工材料,不逐條判;下列 finding 涉及的合約(每支檔有家、錨點、bound-tests-gate、vendored 名單)都已個別核對。

## F1 新的共用檔沒登記進錨點清單與簽名檔,照字面實作會讓 anchor 測試翻紅、推送被擋
severity: major
blocking: 是 — 不改,實作者只登記工具自裝檔名單,新檔進版控後錨點測試與 anchor verify 一起紅,或更糟:一支決定「擋不擋提交」的檔沒人盯
引句:「新共用檔要登記進工具自裝檔的精確名單(跟 `t_vendored_file_list_matches_what_install_ships` 一起改)」
file: `scripts/lumos:18573`
file: `scripts/test_lumos.py:15935`
file: `scripts/test_lumos.py:34840`
1. spec 的收尾清單只列了 `_VENDORED_TREE_FILES` 一張名單。但 `scripts/hooks/` 底下每一支版控檔另外必須列在 `ANCHOR_FILES`:`scripts/test_lumos.py:15935` 斷言 `tracked == listed`(版控裡 scripts/hooks 的檔 == ANCHOR_FILES 裡 scripts/hooks 開頭的檔),少一支就紅。
2. `ANCHOR_FILES` 還必須等於 `governance/anchor-baseline.json` 的鍵集合(`scripts/test_lumos.py:34840` 起那條),所以要重跑 `lumos anchor approve`;那是人核可的動作,計劃沒排,〈做法〉也沒寫「新檔內容改了要重簽」。
3. 這支共用檔是所有 git 掛鉤的判定源(找不到 3.14 就擋提交),被改壞等於全專案提交被誤擋或全放行,比 `_hookevent.py` 更該進錨點。`scripts/lumos:18586` 的註解自己就寫過「漏登記的話 anchor verify 會直接擋推送」。
4. 連帶:`t_vendored_file_list_matches_what_install_ships`(`scripts/test_lumos.py:11554`)只比 `_VENDORED_TREE_FILES` 與 `git ls-files`,不比錨點;所以只照 spec 改,那一支綠、另外兩支紅。

## F2 [S7] 綁的「舊語法解析」若用 ast.parse(feature_version) 實作,擋不到本 repo 最可能的回歸(3.12 的巢狀引號 f-string)
severity: major
blocking: 是 — 條款宣稱「仍能被 3.9 解析」,但測試綁的機制對最可能踩的寫法回綠,舊版啟動時會在版本檢查之前吞語法錯誤,正是 [S7] 要防的事
引句:當 scripts/lumos 被修改,它仍應能被舊語法(3.9)解析,這樣舊版啟動時才跑得到第 2 點的版本檢查
file: `scripts/test_lumos.py:37461`
1. 我用 3.14 實測 `ast.parse(src, feature_version=(3,9))`:`f"{x["a"]}"` 與 `f"{"\n".join([])}"`(PEP 701,3.12 起合法)都被接受,只有 match、`except*`、`def f[T]`、`type X = int` 被拒。真的 3.9 對前兩者是 SyntaxError。
2. 下限改成 3.14 之後,作者日常環境全是 3.14,最容易無意帶進的正是這種 f-string(spec 自己在背景段就說測試總檔已有 3.12 才合法的寫法)。CI 只跑 3.14(做法 6),沒有任何一層會抓到。
3. 〈誠實界線〉只承認「擋不到載入時呼叫新版標準庫」,沒承認「語法面也漏 PEP 701」,承認的範圍比實情小。
4. 修法方向(不是建議收尾句):S7 的測試要在有真舊直譯器時真跑(`/usr/bin/python3` 這類,沒有就明確跳過並留帳),或另掃 f-string 巢狀同引號;只用 feature_version 不能綁住條款。

## F3 ruff 目標版本改 py314 會多出 10 條 B905 與 1 條 RUF007,而現有測試 t_lumos_no_zip_strict_for_py39 禁止寫 zip(strict=),兩邊直接矛盾
severity: major
blocking: 是 — 照字面改 lint.json,新增告警閘要求 zip 加 strict=,而測試禁止 zip(strict=),兩道閘互相擋,推送卡死
引句:`.lumos/lint.json` 的 `--target-version` 改成 `py314`
file: `.lumos/lint.json:3`
file: `scripts/test_lumos.py:50204`
file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:34`
1. 實測同一組 `--select F,B,ASYNC,RUF,DTZ,E7,E9,C901`,py39→py314 只差:B905 +10(`scripts/lumos` 4900、20561、23898、23939、24241、24558、24738、25491、26128 行,`scripts/test_lumos.py:17446`),RUF007 +1(`scripts/lumos:24558`)。
2. `t_lumos_no_zip_strict_for_py39`(`scripts/test_lumos.py:50204`)用正則禁止 `zip(...strict=`,理由是 3.9 沒這參數。3.14 下限後這條測試成了死規則,而且與 B905 直接相反。做法第 8 點只列 `_toml_loads` 與 `t_hooks_python_fallback` 兩處「擋路舊碼」,漏了它。
3. 〈做法〉第 6 點只寫「編譯全部檔」「SyntaxWarning 歸零」兩道會重跑,沒提 ruff 新增的 11 條要清或要放行;新增告警閘吃的是同一份設定。
4. `Systems/筆記內容閘.md:34` 的 PITFALL 寫「專案宣告支援的 Python 3.9 沒有這個參數」,根因段講「ruff 沒設目標版本」,改完後這條要一起改寫;收尾清單(第 9 點)沒列這篇。

## F4 〈實務隱患〉指望 CHANGELOG 通知消費專案,〈做法〉第 7 點卻明說不寫 CHANGELOG;沒有任何通道主動告訴已裝舊版的專案
severity: major
blocking: 是 — 對外送出那條的唯一防法指向不會被做的事,實作者照〈做法〉做就沒有任何升級通知
引句:防法:CHANGELOG 寫升級說明,擋下訊息附三種平台的安裝指令與 `LUMOS_PYTHON` 的用法;不自動安裝任何東西。
file: `CHANGELOG.md:3`
1. 〈做法〉第 7 點:「不寫 CHANGELOG——它自己規定只記發版」,升級注意改放 README。這與〈實務隱患〉互相矛盾;`CHANGELOG.md` 開頭確實規定只記發版、不留未發布區塊。
2. 誰會通知消費專案:已 vendored 的專案裡,掛鉤與 lumos 是被複製進專案並進版控的(`_VENDORED_TREE_FILES`),隊友 `git pull` 就拿到新掛鉤,不需要跑 `lumos update`,第一次收到訊息就是提交被擋。README 只有還沒安裝的人會讀。
3. 需要在 spec 選一條:哪個通道在「擋下之前」告知(例如 update 指令印一段、或發版那一筆的 CHANGELOG 由發版流程帶),並把矛盾的一句改掉。至少擋下訊息本身要能被隊友看懂,這條 spec 有寫。
4. ⚠ 消費專案自己的 CI(`lumos doctor --ci` 這類步驟在他們的 runner 上以預設 python3 跑)也會在下限拉高後回 2;spec 的〈回退〉只講「提交會被擋」,沒講 CI。我無法查證各消費專案的 workflow 內容(來源:外部)。

## F5 候選清單只靠 PATH,不含常見安裝位置;PATH 精簡的啟動環境(排程、GUI git 用戶端)裝了 3.14 也會被判找不到
severity: major
blocking: 是 — 這是〈實務隱患〉自己列的「誤擋(找得到 3.14 卻判找不到)」的主要成因之一,而防法只有「訊息列出候選」,不是減少誤擋
引句:依序試 `$LUMOS_PYTHON`、`python3.14`、`python3.15`、`python3.16`、`python3`、`python`,有 uv 時再試 `uv python find '>=3.14'`
file: `governance/ai-governance-research.sh:7`
file: `governance/ai-governance-research.sh:35`
file: `governance/lint-watch-check.sh:38`
file: `scripts/test_lumos.py:35831`
1. 全部候選都走 PATH 查找,無 `/opt/homebrew/bin`、`/usr/local/bin`、`~/.local/bin`(uv 常放處)、pyenv shims 這類絕對位置的後備。Homebrew 在 Apple Silicon 裝在 `/opt/homebrew/bin`,從 GUI 用戶端或 launchd 啟動的行程 PATH 常沒有它。連這個 repo 的測試 `_toml_loads` 都自己寫了 `/opt/homebrew/bin/python3` 等絕對路徑後備(`scripts/test_lumos.py:35831`),顯示作者本機就遇過。
2. 已存在、spec 範圍外的呼叫者:`governance/ai-governance-research.sh`(PATH 設成 `$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH`,沒有 homebrew)第 35 行 `python3 scripts/lumos --help 2>/dev/null | head -12 || true`、`governance/lint-watch-check.sh:38` 的 `RAW="$(python3 ... lint-watch ...)" || true`:PATH 上第一個 python3 若是 3.9,lumos 改成回 2 並印說明到 stderr,而這兩處都吞掉 stderr 並 `|| true`,結果是空字串、靜默失效。`governance/autonomous-loop.sh:3` 的 PATH 含 `/opt/homebrew/bin` 所以那支不受影響。`wrapper-watchdog.sh`、`daily-governance.sh` 的 launchd 環境 PATH 我查不到(⚠ 來源:部署),需要看實機。
3. 範圍節(第 35 行起)沒有列 `governance/*.sh`;它們一天到晚在跑 `python3 scripts/lumos`。

## F6 第 5 點說安裝入口「照舊」只找 python,但四支殼只試 python3、也完全沒有「找不到」的分支
severity: minor
blocking: 否 — 只是描述不準;實作者會補分支,只是不知道要補的是新增而不是「只改一件事」
引句:`install.sh`、`get.sh`、`get.ps1`、`scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh` 照舊只負責
file: `install.sh:5`
file: `get.sh:45`
file: `scripts/install-hooks.sh:6`
file: `scripts/install-graph-toolchain.sh:17`
1. `install.sh`、`install-hooks.sh`、`install-graph-toolchain.sh` 都是 `exec python3 ...` 一行,`get.sh:45` 是 `python3 "$LUMOS_HOME/scripts/lumos" bootstrap`;沒有 `command -v` 檢查,也不會退 `python`。只有 `get.ps1:34-40` 有 python3/python 兩個候選。
2. 所以 [S4] 要的「連任何 python 都找不到就印安裝指令回 2」是四支殼要新加分支(bash 沒有 python3 會是 127 加 shell 自己的錯誤),不是「照舊、只改一件事」。get.sh 在 `set -euo pipefail` 下,clone 完才死在找不到 python3,該分支要在 clone 之前還是之後也沒說。

## F7 防無限重跑的環境變數會被子行程繼承,巢狀呼叫舊版 python 時直接報錯而不是重新找
severity: minor
blocking: 否 — 只在「3.14 的 lumos 再叫 PATH 上 python3(3.9)跑 lumos」的巢狀情形出現;spec 沒寫變數何時清、綁什麼值
引句:重跑前設一個環境變數,重跑後的程序若還是舊版就直接報錯,不會無限重跑。
1. 重跑後的 3.14 行程把這個變數留在環境裡,它啟動的任何子行程(shell 腳本、`bash governance/*.sh` 裡的 `python3 scripts/lumos`)都會繼承。若那個 `python3` 是 3.9,它看到變數就「直接報錯」,不會像第一層那樣再找 3.14。
2. spec 沒寫變數的值(建議綁重跑用的直譯器路徑或版本,而不是布林旗標)。⚠ 是否真有巢狀呼叫路徑我只查到 shell 腳本那類(`autonomous-loop.sh` 內的 `python3 scripts/lumos ...` 多次),lumos 本身沒有寫死 `"python3"` 去 spawn 自己(它用 `sys.executable`)。

## F8 文件與筆記收尾清單漏了 ONBOARDING 的前置需求表與另一篇寫著 3.9 下限的系統筆記
severity: minor
blocking: 否 — 漏的是文件精度,不改行為;但三個月後這兩處會與現實對不上
引句:README 與 README.en(安裝需求那兩處,加上 README.en 另一處
file: `ONBOARDING.md:38`
file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:34`
file: `docs/lumos-toolchain-knowledge/Verification/2026-07-10_cochange守衛.md:8`
1. `ONBOARDING.md:38` 的前置需求表列 `python3`(「lumos 指令與 hooks…無法運作」)沒寫版本,是使用者實際照著檢查環境的那張表;spec 範圍只改 README 兩份。get.ps1 的錯誤訊息(`get.ps1:40` 「Install Python 3.9+」)spec 有列,對。
2. 圖譜:我掃了 docs 底下寫著 3.8/3.9 下限的筆記。〈做法〉第 9 點涵蓋 Issue、`Systems/測試假綠形態`、`Projects/全repo審視_計劃` F65。沒涵蓋:`Systems/筆記內容閘.md:34`(見 F3)。`Verification/2026-07-10_cochange守衛.md:8`、Windows 真機三篇是歷史驗證紀錄、slim 已排除,可留。
3. 第 9 點的 REVISIT 改寫:`Systems/測試假綠形態` 第 584 行與 `Issues/蘋果內建Python3.9跑全套仍紅.md:45` 各有一條 `REVISIT:2026-10-29`,spec 只講改前者、結案後者;要確認兩條都被撤掉,否則到期 doctor 還會唸。
4. 第 9 點說兩件 3.9 專屬問題「在 3.14 下不存在」;那篇 Issue 自己標了「★這個推測沒驗★」與「為什麼 3.12 以上不會當,都沒查」。結案依據是 3.14 全套 7521 條全綠,這個證據足夠,但結案時要把依據寫成「3.14 跑過全套」而不是「原因已清楚」。

## F9 第 8 點只改一支測試,其餘直接複製單支掛鉤或跑掛鉤的測試沒盤點;共用檔缺席時掛鉤的行為也沒定
severity: major
blocking: 是 — 掛鉤改成 source 同目錄共用檔後,把單支掛鉤複製到暫存目錄跑的測試會找不到共用檔;spec 沒說「找不到共用檔」時擋還是放,實作者只能猜
引句:`t_hooks_python_fallback`(現在只盯 post-commit 與 pre-push 兩支寫 `command -v python3 || command -v python`)改成斷言三支掛鉤都 source 共用檔
file: `scripts/test_lumos.py:36619`
file: `scripts/hooks/pre-push:68`
1. `scripts/test_lumos.py:36619` 是 `shutil.copy2(hook_src, root / "pre-push")`,只複製 pre-push 一支到暫存目錄後 `bash root/pre-push`;測試檔內共有約八十處引用 `scripts/hooks/(pre-commit|pre-push|post-commit)`,有的複製、有的直接以來源路徑跑。共用檔改用 `$(dirname "$0")` 一類找法時,複製情境全會找不到共用檔。
2. 缺席的行為 spec 沒定:fail-closed(擋)會在殘缺安裝的專案每次提交都擋、且訊息不是講 3.14;fail-open 則違反 [S3] 的精神。需要寫進第 1 或第 3 點。
3. 現有斷言「沒 python 時降級放行」的測試(`scripts/hooks/pre-push:68` 那段行為)spec 只點名 `t_hooks_python_fallback`,但改成擋下之後,凡是模擬「PATH 上沒有 python」的掛鉤測試都要反轉;我沒逐一找出,⚠ 需要實作者用 `-k hook` 全跑一次確認。
4. [S3] 綁的 `t_hooks_block_without_python314` 在 CI(只有 3.14)上要模擬「只找得到 3.9」與「完全沒有 python」,只能靠 stub 直譯器與縮 PATH;spec 沒說怎麼造,做不好會變成測不到擋下分支的假綠(見 `Systems/測試假綠形態`)。

## 條款綁定的整體評估(不算 finding)
- [S1]:順序比對與版本下限測試能守住;shell 與 Python 兩份的一致性靠字串解析,可行。
- [S2]、[S3]、[S4]、[S5]:測試須靠 stub 直譯器,可守,但見 F9 第 4 點。[S5] 的「merge-claude-settings.py 被舊版直接執行回 2」本身沒有像 [S7] 那樣的「該檔仍可被舊版解析」守衛(現況 3.9 真解析可過,`/usr/bin/python3` 實測);之後有人改壞它,舊版會在檢查前吐語法錯誤。這與 F2 同型,只是影響面小。
- [S6]:只能字串比對 ci.yml 與 lint.json,守得住「設定值」,守不住「全套真的在 3.14 通過」;但這是設定條款,可接受。
- [S7]:見 F2。

最嚴重等級 major,blocking 共 6 條(F1、F2、F3、F4、F5、F9),其餘 F6、F7、F8 為 minor
