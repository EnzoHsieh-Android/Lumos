severity: major

## F1 `{python}` 佔位符沒涵蓋所有既有 `{method}` 代換點
severity: major
blocking: 是 — 不補齊所有代換點,實作者會讓過濾探針或 guard kill 拿字面 `{python}` 去 shell 執行,做出壞系統
引句:「合約測試閘與 guard kill 用 shell 跑它,原本吃 PATH 上的 `python3`」
file: `scripts/lumos:32067`
1. 既有 `{method}` 沒有單一代換函式,是各處內嵌 `.replace("{method}", …)`:`scripts/lumos:12599`(guard kill)、`scripts/lumos:32067`(過濾探針,快取鍵含 run_cmd 文字,`scripts/lumos:32052`)、`scripts/lumos:32116`(合約測試閘)。
2. spec 第 6 點與 [S8] 只列合約測試閘與 guard kill;探針那處沒列,照字面實作會漏。
3. 樣板 `_SKELETON_RUN_CMD`(`scripts/lumos:17743-17756`)與提示文字(`scripts/lumos:6043-6045`)也寫死 `python3 -m pytest -k {method}`,是否同步 spec 沒說。
4. spec-gate 走 `_run_bound_tests`(`scripts/lumos:32109-32116`),會跟合約測試閘走;要單獨補的是探針與 guard kill。

## F2 CI 首次裝外部套件、git config lumos.python 與 perl alarm 是既有沒有的新做法
severity: minor
blocking: 否 — 既有沒有鄰居做同功能,spec 已寫理由與 REVISIT,不改也不會做出壞系統
引句:「CI 另加一步裝 ruff、以 py39 為目標只檢查語法錯誤」
file: `.github/workflows/ci.yml:14`
1. CI 全檔沒有任何 pip、apt、npm 安裝步驟(`.github/workflows/ci.yml:14-17` 只有 checkout 與 setup-python),ruff 會是第一個第三方安裝;既有 ruff 是「有裝才用」(`.lumos/lint.json:3` 尾端 `|| true`)。spec 已寫「不是工具鏈的依賴」與理由,理由邏輯站得住。
2. `git config lumos.python`:全 repo 無 `lumos.` 前綴 git config,僅有 `core.hooksPath`(`scripts/lumos:18257`);`.lumos/config.json` 進版控、不適合存每機路徑,所以是新增載體而非重複。⚠ 交編排者:系統筆記宜寫明為什麼不放 `.lumos/config.json`。
3. perl alarm:既有腳本沒用 perl 執行(`scripts/lumos:21391` 只是語言表),shell 側也無任何逾時包裝;Python 側逾時是 `subprocess.run(timeout=…)`(`scripts/hooks/claude/_hookevent.py:102`)。spec 已在〈誠實界線〉自承並附 REVISIT。
4. ⚠ 嚴重度錨對「第二種做法」的解讀交編排者確認:我判 minor(沒有鄰居做同功能)。

## F3 pre-commit、pre-push、test_lumos.py 的家沒進落點說明
severity: minor
blocking: 否 — 只影響筆記寫回落點,不改實作行為
引句:「新開一篇系統筆記(暫定 `Systems/python直譯器選擇`,已列進 lands_in)管共用檔與」
1. spec 第 12 點只處理新檔與無家檔;改到 `scripts/hooks/pre-commit`、`scripts/hooks/pre-push` 核心行為([S3])與 `scripts/test_lumos.py`,但 lands_in 四篇看不出它們的家寫哪一篇(pre-commit、pre-push 的家分散在多篇,如 `Systems/筆記內容閘.md`、`Systems/delguard.md`、`Systems/每支檔有家.md`)。
2. `scripts/merge-claude-settings.py` 同時在 `Systems/lumos-cli-lifecycle.md:92-95` 與 `Systems/codex-harness.md:12` 兩篇 about_code,是既有雙家,spec 未引入新問題。

## 逐問交代(以下沿用原文)

架構對齊審查(第 2 版修訂稿)。對照 repo:clone-314。

## 問 1 分層與依賴方向

大體對齊,一處要標註。

- 依賴方向沒有倒置。Python 這一側原本就用 `sys.executable` 叫子行程:`scripts/lumos:18077`(merge)、`scripts/lumos:18239`、`scripts/lumos:31254`,以及 `scripts/hooks/claude/dispatch-lens-hook.py:239`。spec 第 4 點的「寫 `sys.executable`」與第 6 點的「`{python}` 代入自己的 `sys.executable`」沿用同一個做法,不算新層。
- 「共用檔被 git 掛鉤 source」是新的跨檔依賴。現況 `scripts/hooks/pre-commit:50`、`scripts/hooks/pre-push:70`、`scripts/hooks/post-commit:95` 各自內嵌 `command -v python3 || command -v python`,掛鉤之間沒有 source 關係。全 repo 也沒有任何 `BASH_SOURCE` 定位,`install.sh:5`、`scripts/install-hooks.sh:5` 與 `scripts/install-graph-toolchain.sh:5` 用的是 `dirname "$0"`。spec 已自承「本專案第一個被掛鉤 source 的檔」,並寫了理由:七類候選加驗法加逾時加說明文字,若各抄一份要多五份同步。
  - 判斷:理由站得住。內嵌 `command -v` 一行與內嵌七類候選加逾時加說明,量級差很多;既有的漂移測試模式(`t_windows_interpreter_pick_matches_slim`,`scripts/test_lumos.py:7703`)也是「複製份數越多越難守」的同一個顧慮。
  - 但「整個 hooks 夾被複製所以共用檔會跟著走」我只核了方向,沒逐項驗:掛鉤是複製進消費專案、不是 symlink,消費專案那份的 `BASH_SOURCE` 位置與 `scripts/hooks/` 相對關係要在實作時成立。⚠ 標交編排者。
- 是 Python 單一源加 shell 共用檔加 PowerShell 三份,對 `lumos` 與 `merge-claude-settings.py` 這兩支 Python 檔各再內嵌一份版本檢查。這與既有「Python 檔複製一份、靠測試盯」(`get.ps1` 那份是第三份)一致。無跨層直呼。

## 問 2 命名與錯誤處理

命名與既有一致,兩處 minor。

- 環境變數 `LUMOS_PYTHON`、`LUMOS_REEXEC_PYTHON` 依循既有的 `LUMOS_*` 環境變數前綴(如 `scripts/lumos:963` 的 `LUMOS_PUSH_ATTEMPT`、`scripts/lumos:12538` 的 `LUMOS_KILL_TIMEOUT_FLOOR`)。對齊。
- 錯誤處理:「找不到就擋下並講出口」對齊 `pre-push` 現有的 `逃生:…` 慣例(`scripts/hooks/pre-push:240`、`scripts/hooks/pre-push:251`)。「rc 2、不印追蹤」也符合既有 CLI 的擋下用語(`scripts/lumos:8884` 一類)。
- minor 一:現況兩支掛鉤的「沒 python 就放行」(`scripts/hooks/pre-push:68-70`、`scripts/hooks/pre-push:119`,註解明寫「不為缺環境 brick push,CI 兜底」)是刻意的既有設計。spec 改成擋下,並在〈回退〉與〈實務隱患〉寫了理由,可接受。但文中沒交代:pre-push 開頭註解與 CI 檔頭「缺環境降級放行」(`.github/workflows/ci.yml:2-4`)的脈絡也要同步改字,否則兩處註解與新行為互相矛盾。
- minor 二:spec 說 `merge-claude-settings.py` 自己開頭也加版本檢查。既有該檔 `_PY = shutil.which("python3") or shutil.which("python") or "python3"`(`scripts/merge-claude-settings.py:51`),Codex 分支 POSIX 不加引號(`scripts/merge-claude-settings.py:100-102` 附近)。spec 已點名 POSIX 補引號,對齊。但 spec 沒說 `scripts/merge-claude-settings.py:51` 這行 `_PY` 與第 4 點「改成 `sys.executable`」是同一處還是新增,細節屬實作,不影響對齊。

## 問 3 第二種做法

逐項對照,以下是引入「既有沒有的做法」的地方。

1. `git config lumos.python`(存直譯器):
   - 現況全 repo 沒有任何 `lumos.` 前綴的 git config(`grep lumos\.python` 為 0)。既有的 git config 只有 git 自己的 `core.hooksPath`(`scripts/lumos:18257` 寫入,`scripts/lumos:16760`、`scripts/lumos:17081` 讀取)。
   - 既有的「專案設定」是 `.lumos/config.json`(`.lumos/config.json:1-30`,`test.run_cmd`、`node_home.gate` 等),但它是進版控、跨機共用的,不適合存「這台機器的絕對路徑」。spec 選 git config 有理由(不靠行程環境變數、GUI 用戶端讀得到),且 `core.hooksPath` 確有「每機器要重接」的先例(`scripts/lumos:18415` 註解)。
   - 判斷:這是新增的第二個「每機設定」載體(第一個是環境變數 `LUMOS_*`),不是既有做法,但既有沒有同功能的鄰居可借,不是重複發明。⚠ 交編排者裁:這個新命名空間要不要在系統筆記寫明「為什麼不放 `.lumos/config.json`」。spec 第 12 點的新系統筆記涵蓋「`git config lumos.python`」,可接受。標 minor,不算 major(沒有鄰居已做同功能)。
2. `perl -e 'alarm 5; exec @ARGV'`:
   - 既有腳本沒有用 perl 做任何事(`scripts/lumos` 裡的 perl 只出現在語言表 `scripts/lumos:21391`,不是拿來執行);既有掛鉤也沒有任何逾時包裝(`scripts/hooks/*`、`install.sh`、`get.sh` 對 `timeout`/`alarm` grep 為 0)。Python 側的逾時是 `subprocess.run(timeout=…)`(`scripts/hooks/claude/_hookevent.py:102`)。
   - spec 已在〈誠實界線〉自承沒有 perl 時沒有逾時,並附 REVISIT。
   - 判斷:shell 側逾時是新做法,但 shell 側原本就沒有先例,沒有鄰居可借,屬「新增而非分歧」。minor。
3. CI 裝 ruff:
   - `.github/workflows/ci.yml` 全檔沒有任何 `pip install`/`apt`/`npm`,只有 `actions/checkout` 與 `actions/setup-python`(`.github/workflows/ci.yml:14-17`)。這會是 CI 第一個裝第三方工具的步驟,直接對到「零依賴家規」。
   - 既有處理開發工具的方式:ruff 是「有裝才用」,`.lumos/lint.json` 的指令尾巴 `2>/dev/null || true`,缺就靜默略過。CI 沒有裝它。
   - spec 已寫「ruff 只在 CI 當工具裝,不是工具鏈的依賴」,並附理由(ubuntu 內建 python3 3.12 擋不到 3.12 的 f-string 寫法)。⚠ 這個理由我沒有重跑驗證:setup-python 改 3.14 之後,CI 上 `python` 就是 3.14,而 3.14 對 3.12 的 f-string 寫法是合法的,所以確實沒有現成的工具能擋「3.9 解析不過」。理由在邏輯上站得住。
   - 判斷:這是引入「CI 裝外部套件」這個第二種做法(既有 CI 全靠標準庫)。但既有沒有鄰居做同功能,而且 spec 有一段明寫理由。我依嚴重度錨(major 只給「引入第二種做法或跨層直呼」)判 major?這裡「第二種做法」的本意是「鄰居已有同功能卻另起一套」;鄰居沒有,所以判 minor,並 ⚠ 交編排者確認錨的解讀。
4. `{python}` 佔位符:
   - 既有佔位符是 `{method}`(小寫)與 lint 用的 `{LINT_FILES}`、`{LINT_SARIF_OUT}`(`.lumos/lint.json:3`)。`{python}` 風格與 `{method}` 一致。
   - 但 `{method}` 的代換不是一個共用函式,而是散在至少四處的 inline `.replace("{method}", …)`:`scripts/lumos:12599`(guard kill)、`scripts/lumos:32067`(過濾探針)、`scripts/lumos:32116`(合約測試閘)、加上 `scripts/lumos:32050`、`scripts/lumos:32115` 的存在判斷。另有 `scripts/lumos:6043-6045` 的提示文字與 `scripts/lumos:17743-17756` 的 `_SKELETON_RUN_CMD` 樣板(`"python": "python3 -m pytest -k {method}"`)。
   - spec 第 6 點與 [S8] 只說「合約測試閘與 guard kill」。漏列:`_bound_tests_filter_probe`(`scripts/lumos:32067`)也代換 `{method}`,而且它的快取鍵含 run_cmd 文字(`scripts/lumos:32052`);不在同一處補 `{python}`,探針會拿字面 `{python}` 去 shell 執行。這是「照字面實作漏掉平行路徑」,屬於對齊層面的分歧風險(新佔位符沒有走既有的單一代換點,因為既有本來就沒有單一代換點)。
   - 判斷:major。spec 引入了新佔位符,卻沒有指定所有既有 `{method}` 代換點同步加,而既有做法是「每個代換點各自內嵌」,漏一處就會出現同一支 run_cmd 在不同閘裡行為分歧。這算「同功能的既有鄰居(四處 `{method}` 代換)沒被涵蓋」。
   - 既有 spec-gate 走的是 `_run_bound_tests`(`scripts/lumos:32109-32116`),同一個函式,所以 spec-gate 會跟著合約測試閘走;真正要單獨補的是探針與 guard kill 兩處。

## 問 4 落點(lands_in 四篇)

- `Systems/lumos-cli-lifecycle`:合理。它已管 `get.sh`、`scripts/lumos`、`scripts/merge-claude-settings.py`(`about_code`,`Systems/lumos-cli-lifecycle.md:92-95`),spec 也把 `install.sh` 等四支無家檔交給它。
- `Systems/bound-tests-gate`:合理。它的 `about_code` 有 `.github/workflows/ci.yml`、`scripts/hooks/pre-push`、`scripts/lumos`(`Systems/bound-tests-gate.md:42-45`),`{python}` 與 S8 落在這裡對。
- `Systems/codex-harness`:合理但偏薄。它的 `about_code` 有 `scripts/merge-claude-settings.py`(`Systems/codex-harness.md:12`),第 4 點註冊直譯器落這裡;但 `scripts/merge-claude-settings.py` 同時被 `lumos-cli-lifecycle` 的 `about_code` 列了,兩篇都管同一支檔。⚠ 這是既有的雙家,spec 不引入新問題。
- `Systems/python直譯器選擇`(新):合理,負責範圍寫得清楚。
- 不對齊:`pre-commit`、`post-commit`、`scripts/test_lumos.py` 的家。`scripts/hooks/pre-commit` 的家是 `Systems/每支檔有家.md`、`Systems/筆記內容閘.md`、`Systems/delguard.md`、`Systems/cochange-guard.md`(多篇);`scripts/hooks/pre-push` 有更多。spec 改到這兩支掛鉤的核心行為(擋或放行)卻不在 lands_in 列它們的家,且 [S3] 是掛鉤行為合約。要動的檔各自需要在改動當次寫回它的家;`lands_in` 只列四篇,讀的人看不出 `pre-commit`/`pre-push` 的家要寫哪一篇。這符合 CLAUDE.md 鐵則 5(「改到的每支檔的家」),spec 第 12 點只處理新檔與無家檔。minor。

## 合計

不對齊共 3 條,其中 major 1 條。

- major 1:`{python}` 沒有涵蓋所有 `{method}` 代換點(`scripts/lumos:32067` 探針、`scripts/lumos:12599` guard kill),既有做法是各處內嵌代換,新佔位符照字面只列兩個消費者。
- minor 2:CI 首次裝外部套件(ruff),`git config lumos.python` 與 perl alarm 是新增而非分歧(合併算一條);`pre-commit`/`pre-push`/`test_lumos.py` 的家沒進落點說明。

不對齊共 3 條,其中 major 1 條。最高等級:major;blocking 1 條(判準:不補 `{python}` 涵蓋所有代換點,實作者會讓過濾探針或 guard kill 拿字面 `{python}` 去執行,做出壞系統)。
