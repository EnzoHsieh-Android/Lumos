severity: major

## F1 舊版 updater 不會配送新增的共用直譯器檔

severity: major  
blocking: 是 — 不改，既有使用者第一次更新後會拿到引用不存在檔案的新掛鉤，下一次提交與推送都被擋住。  
引句:「新共用檔要登記三張名單:工具自裝檔精確名單(`t_vendored_file_list_matches_what_install_ships`)、錨點清單 `ANCHOR_FILES` 與 `governance/anchor-baseline.json`」  
file: `scripts/lumos:17185`  
file: `scripts/lumos:17448`  
file: `scripts/lumos:18077`

1. 現有 updater 在行程啟動時已把舊版 `_VENDORED_TREE_FILES` 載入記憶體；拉到新版原始碼後，仍依舊清單逐檔複製，不會因新版把共用檔加入清單而自動認得它。
2. 同一次更新會複製名稱既存但內容已改成 `source` 共用檔的 pre-commit、pre-push 與安裝腳本，卻漏掉舊清單不知道的新共用檔。spec 又規定共用檔缺失時掛鉤必須擋下，因此第一次升級必然形成半套安裝。
3. 同一個舊行程還會把自己的舊版 `sys.executable` 傳給新版 `merge-claude-settings.py`；在由 Python 3.9 執行更新的既有安裝上，新版 merge 會拒絕，直譯器註冊亦無法於這次更新完成。
4. 升級設計必須納入「舊 manifest 配送新 manifest」的過渡方案，並以真正的上一版 updater 跑端到端升級測試；只在新版原始碼中檢查三張名單一致，抓不到這條遷移斷層。

## F2 LUMOS_PYTHON 指向非符號連結 wrapper 時會無限重跑

severity: major  
blocking: 是 — 不改，合法的直譯器 wrapper 會讓 POSIX 行程無限 exec，Windows 則持續建立並等待子行程。  
引句:「`LUMOS_REEXEC_PYTHON` 等於自己又仍是舊版時應直接報錯;通過檢查後應清掉這個變數,子孫行程被舊版叫起時應照常重跑」

1. 設 `LUMOS_PYTHON=/company/bin/python`，讓該可執行 wrapper 啟動 `/opt/python-3.14/bin/python3.14`；它不是符號連結，但候選驗證會成功並印出真正的 `sys.executable`。
2. 第一次重跑後，新行程是 Python 3.14；然而 spec 仍以 `realpath(LUMOS_PYTHON) != realpath(sys.executable)` 作為重跑條件，所以再次選到相同目標。
3. `LUMOS_REEXEC_PYTHON` 的停止條件還要求「版本仍舊」，因此 3.14 行程不會報重跑失敗，且在通過檢查後清掉 sentinel，迴圈沒有終止狀態。
4. 重跑判斷必須比較候選驗證得到的實際目標，或在第一次解析後把 override 正規化為該目標；sentinel 也必須能攔住「已到同一目標但 override 字串不同」的循環。

## F3 post-commit 在只有 python3.14 指令的機器上仍寫不了跳過帳

severity: major  
blocking: 是 — 不改，支援矩陣明列的環境會悄悄漏寫跳過帳，使後續治理紀錄失真。  
引句:「`post-commit` 的跳過帳應照舊用任何版本寫入」  
file: `scripts/hooks/post-commit:95`

1. post-commit 現況只找 `python3`，找不到再找 `python`；spec 明確不讓它使用新的共用 resolver。
2. 在只有 `python3.14`、沒有 `python3` 與 `python` 別名的 POSIX 環境，pre-commit、pre-push 和安裝器均可依新規找到直譯器，但 post-commit 得到空的 `PY`。
3. 該掛鉤的錯誤處理會以成功碼退出，提交本身看似正常，應寫入的 bypass ledger 卻消失；這不是「任何版本寫入」。
4. post-commit 至少必須加入不設最低版本的可執行搜尋路徑，涵蓋 `python3.14` 與已登記的直譯器，並測只有版本化指令的案例。

## F4 Windows lumos.cmd 仍會優先寫入無法執行的商店替身

severity: major  
blocking: 是 — 不改，安裝器已找到真實 3.14 的機器仍可能產生完全無法啟動 lumos 的全域包裝器。  
引句:「Windows 的 `lumos.cmd` 包裝:PATH 上有 `python3`/`python` 就寫指令名,都沒有而有 `py` 就寫 `py -3`,版本交給第 2 點」  
file: `scripts/lumos:16394`

1. 環境設為 WindowsApps 的 `python.exe` 商店替身在 PATH，另有能執行 Python 3.14 的 `py` launcher。
2. get.ps1 的候選驗證會拒絕商店替身並成功使用 `py -3.14`，但 `_install_windows_shim` 只用 `shutil.which` 判斷名稱存在，仍把 `python` 寫入 lumos.cmd。
3. 使用者之後執行 `lumos` 時先落到商店替身，尚未進入 `scripts/lumos`，第 2 點的版本檢查與重跑機制沒有機會接手。
4. 包裝器必須使用安裝階段已驗證成功的實際啟動方式，而非重新做一次僅檢查名稱存在的選擇；S4 明列的商店替身案例也必須驗證安裝後實際執行 lumos。

## F5 兩支要求舊版友善報錯的入口沒有舊語法守衛

severity: major  
blocking: 是 — 不改，日後合法使用 Python 3.14 語法時，舊版會在執行版本檢查前直接噴 SyntaxError，違反回 2 且不寫入的合約。  
引句:「merge-claude-settings.py 被 3.14 以前的 Python 直接執行時應報錯回 2、不寫設定」  
file: `scripts/merge-claude-settings.py:11`  
file: `scripts/test_lumos.py:15`  
file: `.github/workflows/ci.yml:21`

1. Python 會先解析整份檔案才執行開頭版本檢查；因此只在「少量 import 後」加入檢查，無法抵抗檔案後段出現 3.14 專用語法。
2. S5 對 `merge-claude-settings.py`、S8 對 `test_lumos.py` 都承諾舊版得到乾淨錯誤；但 S7 的 `ruff --target-version py39 --select E9` 只涵蓋 `scripts/lumos`。
3. 專案最低版本升為 3.14 後，維護者依正常語言基線修改上述兩檔即可破壞這兩項合約，而規劃中的 CI 不會攔截。
4. 兩支直接入口都必須加入 3.9 語法編譯或等價的 E9 守衛；另一條可執行方案是把舊版可解析的啟動器與允許 3.14 語法的主體拆開。

## F6 `{python}` 未定義 shell 安全的代入規則

severity: major  
blocking: 是 — 不改，直譯器路徑含空白或 shell 字元時，合約測試與 guard kill 會執行錯誤命令。  
引句:「當合約測試閘或 guard kill 跑專案測試指令,應以執行中的 lumos 那一支直譯器代入 `{python}`」  
file: `scripts/lumos:12411`  
file: `scripts/lumos:12599`  
file: `scripts/lumos:32067`  
file: `scripts/lumos:32116`

1. `_kill_run` 目前以 `shell=True` 執行字串命令；spec 只說把 `sys.executable` 代入 `{python}`，沒有定義平台相應的引用與跳脫。
2. 直譯器位於 `C:\Program Files\Python314\python.exe` 或 POSIX 含空白目錄時，裸代入會把路徑切成多個 token。POSIX 的 `shlex.quote` 也不能直接當成 Windows `cmd.exe` 的規則。
3. 此問題同時落在 guard kill、bound-test filter probe 與正式 bound-tests 三條路徑；其中任一路徑失敗都會把「測試是否真的執行」判錯。
4. spec 必須定義平台別的 shell 引用，或把執行模型改成 argv 且不用 shell；測試需以含空白及 shell 特殊字元的實際直譯器路徑覆蓋三條路徑。

## F7 官方 onboarding 的直接命令仍繞過直譯器搜尋

severity: major  
blocking: 是 — 不改，只有 `python3.14` 的受支援環境會在官方第一個安裝命令就得到 command not found。  
引句:「當安裝入口在只有 python3.14、只有 Windows 的 py 啟動器、或只有商店替身的機器上執行,工具應找到真的 3.14 或印安裝指令回 2」  
file: `ONBOARDING.md:15`  
file: `ONBOARDING.md:72`  
file: `ONBOARDING.md:120`

1. ONBOARDING 仍以 `python3 scripts/lumos bootstrap` 等直接命令作為官方操作路徑；shell 必須先找到 `python3`，`scripts/lumos` 內的新 resolver 才可能執行。
2. 在 S4 明列的「只有 python3.14」環境，這些命令會由 shell 直接報錯，既不自動找到 3.14，也不輸出 spec 規定的安裝指令。
3. 範圍只列 ONBOARDING 的前置需求表，沒有把正文中的可執行命令納入替換，因此照字面完成 spec 仍會留下壞路徑。
4. 官方命令必須改走具備 resolver 的安裝入口或明確使用已解析的命令；驗收需逐條執行 ONBOARDING，而不只比對版本文字。

### 逐節判讀

- 標題、依據、先前工作、PRIOR-ART、RETIRE-IF：已讀,無 finding。
- 範圍：F7；其餘列出的程式、掛鉤、安裝器、CI、文件與消費端產物均已逐項核對。
- 做法第 1 點：F1。
- 做法第 2 點：F2。
- 做法第 3 點：F3。
- 做法第 4 點：F5。
- 做法第 5 點：F4、F7。
- 做法第 6 點：F5、F6。
- 做法第 7 點：F5；其餘 CI 版本、compileall、SyntaxWarning 與生成工作流敘述已讀,無 finding。
- 做法第 8 點：F1 涉及舊 updater 過渡；其餘文件版本與更新通知已讀,無 finding。
- 做法第 9 點：已讀,無 finding。
- 做法第 10 點：已讀,無 finding。
- 做法第 11 點：已讀,無 finding。
- 做法第 12 點：已讀,無 finding。
- 做法第 13 點：已讀,無 finding。
- 條款 S1：F1、F2。
- 條款 S2：F2。
- 條款 S3：F3。
- 條款 S4：F4、F7。
- 條款 S5：F5。
- 條款 S6：已讀,無 finding。
- 條款 S7：F5。
- 條款 S8：F5、F6。
- 條款 S9：F1。
- 條款 S10：已讀,無 finding。
- 回退：已讀,無 finding。
- 誠實界線：F7；其餘已讀,無 finding。
- 審計修正紀錄：已讀；F1、F2、F3、F4、F5、F6、F7 均為修訂後仍存在或由補丁銜接產生的缺口。
- 文件中的第 1、2、3、5、6、9 點引用均有目標；`[S1]` 至 `[S10]` 均有且各自只有一份定義，無懸空交叉引用。

### 固定席節點判讀

- `Systems/lumos-cli-lifecycle`：F1 會破壞 updater 一次完成配送的生命週期；既有 sentinel 僅重注入 sentinel 本身的合約不受影響。
- `Systems/bound-tests-gate`：F6 會破壞「綁定測試確實執行」合約；其餘設計不影響紅燈、懸空與不可篩選時阻擋的行為。
- `Systems/codex-harness`：F5 會讓舊 Python 在 merge 註冊入口先 SyntaxError；節點沒有另一項被本設計破壞的合約。
- `Issues/蘋果內建Python3.9跑全套仍紅`：已讀,無 finding；spec 沒有把該問題誤寫成全套失敗的唯一原因。
- `Projects/全repo審視_計劃`：已讀,無 finding；本稿未恢復已否決的全 repo 編譯方案。
- `Projects/存量漂移防線_計劃`：已讀,無 finding；只暫停 Python 漂移檢查且有恢復條件。
- `Systems/測試假綠形態`：F6 會使 bound-tests 的真執行判定失真；其餘測試規劃沒有繞過既有 mutant 前置條件。
- `Systems/筆記內容閘`：已讀,無 finding；zip pitfall 的理由更新不改變內容閘行為。
- `Systems/slim-get-一行安裝`：已讀,無 finding；root get.ps1 的 ASCII-only、無 BOM 合約仍有既存測試守衛。
- `Systems/hook信任邊界`：已讀,無 finding；共用 resolver 被列為錨點的方向符合該節點，問題在 F1 的跨版本配送。

### 實務隱患

- 守衛面誤擋：F1 會因缺共用檔擋住正常提交與推送；F3 會漏記跳過帳；F6 會把路徑解析失敗誤判成測試失敗。
- 對外送出：F1 會把半套工具送入消費端；F4 會送出不可啟動的 lumos.cmd；F7 會發布在支援環境無法執行的官方命令。
- 不可逆：無；規劃內修改均可由回退提交、重裝掛鉤與恢復設定撤回，沒有資料刪除或外部不可撤銷操作。
- 併發：無獨立 finding；resolver 只讀設定並在單一行程內選擇直譯器，spec 沒新增共享可變狀態。F2 是無限重跑的終止性錯誤，不是併發競態。
- 效能：無獨立 finding；候選數量有限且已有逐候選超時。F2 造成的無界行程與時間消耗已作為正確性缺陷報告。

最高 major，blocking 共 7 條。