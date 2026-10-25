severity: major

## F1 擋合併的 CI 檢查在 PR 上根本不跑,合併後的 push 又因範圍為空而放行
severity: major
blocking: 是 此段把「CI 設成合併前必須通過」當作擋合併的唯一機制,但現有 CI 的 code-loop 步驟擋不了合併。
引句:「擋合併靠專案在 GitHub 把 CI 這道檢查設成「合併前必須通過」,lumos 開不了,只能寫進接入說明」
spec 段落:〈實務隱患〉與〈資料怎麼流〉第 3 點。
問題:
- 工具鏈 `ci.yml` 的 code-loop 步驟寫 `if: github.event_name == 'push'`,而 push 只在 `branches: [main]` 觸發。pull_request 事件根本不跑這一步,所以它是合併「之後」的後盾,不是合併前的檢查。
- 要真的擋合併,得另寫 pull_request 版的步驟。spec 沒寫那一步用什麼 sha 與範圍。PR 事件 checkout 的是合併提交,不是分支頂端,而指紋要從「被推送提交」的檔案樹算。主線若也動過 `app_dirs`,合併提交的指紋會跟分支上跑驗收的指紋不同,紀錄對不上而誤擋。
- 推到 main 之後,分支名等於主線,「分岔點到被推送提交」的範圍是空的。squash 之後的 main 提交若動過 `app_dirs`,指紋也可能對不上。
- 消費專案這邊,doctor 與安裝腳本只會貼 note-shape、drift、`--security-only` 這幾種 CI 步驟範本,沒有任何一個貼 `code-loop check`。spec 的〈這次要改到的地方〉沒有「給消費專案貼 CI 步驟範本」這一項。「CI 照現在的行為」只對工具鏈自己的 ci.yml 成立。
- 〈實務隱患〉說「判定回 2 時 CI 步驟是否算紅要在實作時確認」。現在就能確認:ci.yml 是 `exit "$rc"`,非 1 也紅,但消費專案各自的 CI 沒有這個保證。

佐證:
- file: `.github/workflows/ci.yml:6`
- file: `.github/workflows/ci.yml:9`
- file: `.github/workflows/ci.yml:207-221`
- file: `scripts/lumos:43923-43935`
- file: `scripts/lumos:52893-52960`

## F2 「出錯回 2」不是 code-loop check 的既有做法,未捕捉的例外反而會變成擋下
severity: major
blocking: 是 spec 對錯誤路徑的描述與現有程式不符,照做會讓「紀錄檔壞掉」走成擋下或放行兩種意外結果。
引句:「這道自己出錯(例如讀不了紀錄檔)時照 code-loop check 既有的做法回 2」
spec 段落:〈資料怎麼流〉第 3 點「位置」,以及 S11 一帶。
問題:
- `cmd_code_loop` 的 check 路徑只回 0 或 1。檔頭文件寫 `rc: 0=OK / 1=check:blocked / 2=參數錯`。判定內部出錯的既有做法是捕捉例外、呼叫 `_gate_failopen` 記一筆帳、回「不擋」,最後回 0,不是回 2。
- 沒被捕捉的例外會讓 Python 結束碼變 1,pre-push 與 CI 都把 1 當擋下。
- 所以 spec 要寫清楚兩件事:這道自己出錯時要仿 fail-open 並記治理帳,還是要新開 rc 2 通道。後者會改動 `cmd_code_loop` 的回傳碼語意,而 spec 的〈不做〉說不改既有行為。
- spec 也沒寫「算不出主線或分岔點」(新 repo、沒有 main、force-push 後本機找不到起點)時怎麼辦。既有各道都有明確的 fail-open 並記帳。

佐證:
- file: `scripts/lumos:64756-64761`
- file: `scripts/lumos:64187-64190`
- file: `scripts/lumos:64135-64150`
- file: `scripts/lumos:63137-63150`
- file: `scripts/hooks/pre-push:577-579`

## F3 新判定要登記的接點只提了排序,漏了種類登記、擋下訊息分派與守衛測試
severity: major
blocking: 否 這些是實作時會當場紅的接點,補寫即可,但現在 spec 完全沒列。
引句:「pre-push 帶 `--keep-going` 時跟其他判定一起列出擋下原因,CI 照現在的行為第一道擋下就停」
spec 段落:〈資料怎麼流〉第 3 點「位置」,以及 S11。
問題:
- 帶 `--keep-going` 時,每道擋下都要有一個字面的 `reason_kind`。`pp_cl_reason` 對照表要加同名一行,否則 pre-push 的彙總只會印通用句。`t_prepush_cl_reason_table_matches_lumos` 會拿這份表跟 lumos 的 reason_kind 雙向比對。
- `_cl_say_block` 沒有對應分支的種類會落入 else,印出「這次高風險改動還不能推」,對 E2E 擋下是錯的訊息。
- `_codeloop_kg_finish` 只把 `bound_tests`、`dispositions`、`lint_new`、`security_evidence` 四個明細鍵搬進合併結果。新判定的明細鍵會被丟掉。
- 新判定的擋下句不能含「tier=high 且」或「受波及合約的測試沒過」。pre-push 用 grep 認這兩串去記逃逸帳,誤含會被記成逃逸。
- ci.yml 的 `::error::` 文案與 pre-push 的「逃生路」那段也沒有 E2E 這一項,要放行時印不出 `waive` 指令。
- 〈這次要改到的地方〉只寫了 `scripts/lumos`。這些接點分散在 pre-push 與 ci.yml,它們各有家節點(例如 `Systems/bound-tests-gate`)。spec 的 lands_in 沒列,違反「改到的每支檔都要有家」。
- pre-push 登記的「9 道閘」不用新增,因為 code-loop 本來就是其中一道,閘數只算一道。這一點 spec 沒說錯。

佐證:
- file: `scripts/hooks/pre-push:135-147`
- file: `scripts/hooks/pre-push:586-617`
- file: `scripts/lumos:64033-64052`
- file: `scripts/lumos:64877-64890`
- file: `scripts/test_lumos.py:78359`

## F4 紀錄檔放在 `.lumos/e2e-records/` 且進版控,會讓代碼審留痕自失效
severity: major
blocking: 否 有繞法(先放行再審),但正是 spec 自己標榜要避免的「重做」。
引句:「寫一份查證紀錄 `.lumos/e2e-records/<指紋>.json`(進版控);同一個指紋再跑一次就覆蓋成新的那份」
spec 段落:〈資料怎麼流〉第 2、4 點與〈回退〉。
問題:
- code-loop 留痕只在「留痕 sha 是被推送 sha 的祖先,而且中間只動簿記檔」時才算有效。簿記名單是 `_BOOKKEEPING_FILES` 加 `_BOOKKEEPING_DIRS`,沒有 `.lumos/e2e-records/`。
- 在 tier=high 的專案,審查通過後再為 E2E 紀錄或 `waive` 補提交,留痕就失效,要整輪重審。這跟 spec 引為動機的「今天代碼審留痕就因此重做過好幾次」同一類問題。
- 要加進名單的話,`_BOOKKEEPING_DIRS` 有多個消費者(pitfalls、impact、`_codeloop_record_valid` 等),spec 沒評估影響。
- 同一個指紋覆蓋寫入會洗掉先前的 `waiver`,spec 沒寫這種情況。

佐證:
- file: `scripts/lumos:37444-37470`
- file: `scripts/lumos:63551-63600`

## F5 紀錄從工作目錄讀還是從被推送提交的檔案樹讀,spec 沒定
severity: major
blocking: 否 屬於實作未定,補一句即可,但選錯會變成本機過、CI 紅。
引句:「找對得上指紋的紀錄:結果是通過、或有人放行 → 這道過;找不到、沒過、或有「沒判到」→ 這道擋」
spec 段落:〈資料怎麼流〉第 3 點。
問題:
- spec 只說指紋從提交樹算,沒說紀錄檔本身從哪讀。
- 讀工作目錄會讓「已存在但沒提交的紀錄」在 pre-push 過關,CI 乾淨 checkout 卻找不到。
- 既有表態閘的先例是「錨點一律對樹驗,未提交的改動不算證據」。
- 紀錄內部的指紋欄位是否要跟檔名比對也沒寫。不比對的話,把舊紀錄改名成新指紋就能過,這正是〈實驗室驗收〉列的「拿舊紀錄充數」情境。

佐證:
- file: `scripts/lumos:64219-64226`
- file: `scripts/lumos:64307-64330`

## F6 範本腳本的「四個子目錄」跟既有收集腳本的輸出位置與 run-id 規則對不上
severity: major
blocking: 是 S12 要求 `stability` 子目錄,以現有收集腳本做不到,而 spec 又沒把改收集腳本列進工作範圍。
引句:「原始輸出放 `.lumos/artifacts/android/<run-id>/` 底下的 ui、visual、macrobench、stability 四個子目錄」
spec 段落:〈資料怎麼流〉第 1 點與 S12。
問題:
- 收集腳本把 `stability.json`、`logcat.txt` 與快照直接寫在 `.lumos/artifacts/android/<run-id>/` 根層,沒有 `stability/` 子目錄。
- 它的 run-id 只收英數字、點、底線與連字號,不能含斜線,所以無法靠傳 `e2e-xxx/stability` 繞過。
- 〈這次要改到的地方〉沒有改收集腳本,但 lands_in 卻列了 `Systems/android-stability-collector`,兩邊矛盾。
- `adb_serial` 與 `package` 同時存在於 `.lumos/android-e2e.json` 和 `.lumos/macrobench.json` 的 `stability` 段。收集腳本只認後者的 `adb_serial` 與環境變數 `ANDROID_SERIAL`,spec 沒寫兩處不一致時誰為準,也沒寫 check-config 要不要比對。
- `lumos macrobench` 讀的結果目錄是 `.lumos/macrobench.json` 的 `results_dirs`(固定的 Gradle 產出位置),不會自己去讀 run 目錄的 `macrobench/` 子目錄。結果也沒有按「這一次」分開的機制。Macrobenchmark 沒跑成時,舊結果會被當成這次的。
- spec 沒寫誰呼叫 `lumos macrobench --json`,是範本腳本還是 judge。

佐證:
- file: `scripts/templates/android-stability-collect.sh:374-384`
- file: `scripts/templates/android-stability-collect.sh:528-529`
- file: `scripts/lumos:39563-39590`
- file: `scripts/lumos:39395-39425`

## F7 toolkit 的實際介面跟 spec 的描述有三處落差:門檻是環境變數、裝置序號預先寫死、畫面名帶後綴
severity: minor
blocking: 否 都是接線細節,補寫即可。
引句:「`visual`(選填):截圖比對的畫面名清單,畫面名要對到 maestro-visual-toolkit 的慣例」
spec 段落:〈設定〉的 `visual`、`visual_threshold`、`adb_serial`,以及〈一次驗收跑什麼〉第二列。
問題:
- `visual-check.sh` 的門檻從環境變數 `THRESHOLD` 讀,不是參數。spec 只寫「收到更低的門檻會回 2」,沒寫範本腳本要用環境變數傳。
- 裝置序號在 `install.sh` 安裝時用 `--device` 寫進 `visual-env.sh`。要換機得設環境變數 `MAESTRO_DEVICE`,不會跟著 e2e 的 `adb_serial`。`install.sh` 另要 `--app-id`。
- `visual-env.sh` 把 adb 寫死成 `$ANDROID_HOME/platform-tools/adb`,跟收集腳本的 `ADB` 環境變數是兩套。
- toolkit 範本與 README 的畫面名帶 `_visual` 後綴(flow 的 `name` 與基準圖檔名都是 `<畫面>_visual`)。spec 例子沒寫這個後綴。
- toolkit 範本 flow 的註解明寫不要跟其他 flow 一起被 `maestro test .maestro/` 全跑。Lumos 既有的 maestro 綁定 profile 會掃 `.maestro/` 底下所有 `^appId:` 的 yaml,spec 沒說 `flows` 清單跟 `[test:maestro:<名>]` 綁定怎麼分工,也沒說截圖 flow 會不會被綁定掃到。
- 鎖目錄 `.maestro/.lock-<裝置>` 只在 EXIT trap 清。範本腳本被 SIGKILL 時會留下鎖,之後每個畫面都回 1(環境問題)。
- 回傳碼 0/1/2 與「只有不相符才印相符率」這兩條,spec 寫得對。

佐證:
- file: `/Users/enzo/harness/maestro-visual-toolkit/lib/visual-check.sh:6-30`
- file: `/Users/enzo/harness/maestro-visual-toolkit/lib/visual-env.android.sh.tmpl:3-5`
- file: `/Users/enzo/harness/maestro-visual-toolkit/install.sh:10-45`
- file: `/Users/enzo/harness/maestro-visual-toolkit/templates/flow.yaml.tmpl:1-10`
- file: `scripts/lumos:6146-6153`

## F8 治理帳事件:`--stats` 只按閘名彙總,數不出「放行」,新閘名還要登進 `_KNOWN_GATES`
severity: minor
blocking: 否 影響的是 RETIRE-IF 的可量測性,不影響擋合併本身。
引句:「治理帳記一筆 `android-e2e-waive` 事件;`lumos gov --stats` 會數放行次數(RETIRE-IF 要用)」
spec 段落:〈資料怎麼流〉第 4 點與 RETIRE-IF。
問題:
- 治理帳的事件欄位是 `gate` 加 `kind`,沒有單一事件名。
- `_render_gov_stats` 只依 `gate` 彙總,不分 `kind`。同一閘名下別的 E2E 事件(例如 fail-open)會混進「放行次數」。
- 去重鍵是 commit、nodes、gate、kind、token。同一提交上放行兩次只算一次。
- 全檔掃 `"gate": "…"` 字面值的漂移守衛要求新閘名都在 `_KNOWN_GATES`,spec 沒提。
- RETIRE-IF 的第二個條件「推送前改走略過檢查的次數多過正常通過」找不到計數來源。pre-push 的說明明寫 `--no-verify` 本機不留痕,只有 CI 轉紅可看。

佐證:
- file: `scripts/lumos:16058-16100`
- file: `scripts/lumos:15996`
- file: `scripts/test_lumos.py:9640`
- file: `scripts/hooks/pre-push:602`

## F9 spec 內部對「工具沒跑成」與「毫秒類只提醒」兩條規則互相矛盾
severity: minor
blocking: 否 是語意不一致,實作前補一句即可。
引句:「當任一塊的工具沒跑成(找不到 maestro、裝置斷線、輸出檔不在)時,judge 應把那一塊記成失敗、result 不得是 pass」
spec 段落:S6 對照〈一次驗收跑什麼〉第三列與 S5。
問題:
- S6 寫「任一塊」,毫秒類效能沒跑成(Macrobenchmark 沒出結果)也包含在內。第三列與 S5 又說毫秒類「只提醒」。
- 記憶體那塊沒跑成時,收集腳本沒產出 `stability.json`,`lumos macrobench --stability` 會回 2(結果檔不存在)。這算「失敗」還是「沒判到」,跟 `result` 的 fail 與 unjudged 定義重疊。
- spec 沒寫 judge 怎麼處理 `lumos macrobench` 的 rc 2(設定或門檻檔壞掉)。
- 效能那塊的 `baseline_missing`、`failed`、`low_iterations` 等鍵,spec 的 notices 沒提。沒有基準時 `regressions` 恆為空,看起來像沒退步。

佐證:
- file: `scripts/lumos:40205-40245`
- file: `scripts/lumos:39886-39900`

## F10 紀錄的指紋是提交樹,但實機測的 APK 可能來自未提交的工作目錄
severity: minor
blocking: 否 設計缺口,不是跟既有機制的接點錯誤。
引句:「指紋從被推送的那個提交的檔案樹算(`git ls-tree` 取 `app_dirs` 底下的檔與內容),不看工作目錄」
spec 段落:〈資料怎麼流〉第 3 點與 S2。
問題:
- 常見流程是先建置、跑驗收,再提交。judge 當下的 HEAD 還是上一個提交,紀錄會綁到錯的指紋。
- 工作目錄有未提交的 `app_dirs` 改動時,APK 與被綁定的提交樹內容不同。
- 紀錄雖然記了 APK 的 sha256,卻沒有任何東西拿它跟原始碼對照。
- spec 沒寫 `judge` 在 `app_dirs` 有未提交改動時要拒絕或警告。
- spec 沒寫 Macrobenchmark(Gradle 連線測試)會不會換掉裝置上安裝的 App。收集腳本量的是哪一份 APK,與「裝置上實際安裝那份的 sha256」是在哪個時間點取的,也沒寫。

佐證:
- file: `scripts/templates/android-stability-collect.sh:466`
- file: `skills/lumos-android-evidence/SKILL.md:32`

## 已核對且判不影響的項目
- `pre-push` 的中斷就停清單(9 道閘):新判定掛在既有 `code-loop check` 那道,閘數只算一道,不用新增清單項,也不用新增 `中斷就停` 行。已讀,無 finding。
- `--at-sha`、`--branch`、`--diff` 的傳遞:現有路徑都把被推送 sha 傳進 `_codeloop_guard_verdict`,新判定可直接用 `marker_sha`。唯一缺口是「分岔點」的算法,見 F2。
- skill 的 reference.md Maestro 範例:`reference.md:165-180` 確實有一份沒實測的 `repeat` 範例,spec 的說法正確。
- Lumos 既有 maestro 綁定:profile 綁的是 flow 的 `name:`,跟 spec 的 `flows` 路徑清單機制不同,不衝突。分工沒寫清楚的部分見 F7。
- `lumos macrobench --json` 的輸出鍵 `regressions`、`threshold_failures`、`threshold_passed`、`threshold_skipped`、`stability_unjudged`,以及記憶體類 check 的名稱,spec 引用正確。回傳碼 0(含退步)、2(壞檔)也對。記憶體類與毫秒類共用同一組清單,靠紀錄內有沒有 `check` 欄位區分,spec 只說「check 列在 failures」,可再寫明。
- `lands_in`:`Systems/pitfalls-code-loop` 的 about_code 是 `scripts/lumos`,可作新判定的家。`macrobenchmark-adapter` 與 `android-stability-collector` 在本工作目錄都存在。這兩篇列入 lands_in 但本計劃沒動它們管的檔,見 F6。

總結:最嚴重為 major,blocking 共 2 條
