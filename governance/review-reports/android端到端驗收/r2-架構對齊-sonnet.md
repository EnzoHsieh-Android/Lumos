severity: major

## 一、分層與依賴方向:對齊

- 新子命令 `lumos android-e2e` 住在 `scripts/lumos` 單檔,範本腳本住 `scripts/templates/`。這跟 `lumos macrobench` 加收集腳本是同一個分工,lumos 判定、腳本碰裝置。對照 `scripts/lumos:66668`(macrobench 子命令)、`scripts/templates/android-stability-collect.sh:111-113`。
- code-loop check 新增一道判定,排在放行早退之前。接線有 `_cl_say_block`、`_codeloop_kg_finish`、pre-push 的 `pp_cl_reason`、逃生路文字、ci.yml。這跟安全證據判定同形狀,對照 `scripts/lumos:64876-64883`、`scripts/hooks/pre-push:138-146`、`scripts/hooks/pre-push:602`。
- 簿記目錄清單單一源是 `_BOOKKEEPING_DIRS`(`scripts/lumos:37465`)。計劃是往這份清單加一項,沒有另開一套判準,對齊。
- 沒有跨層直呼。judge 和 gate 都只讀提交樹裡的紀錄,不讀工作目錄。

## 二、命名與錯誤處理:有 5 條不對齊(A2 到 A6)

- 對齊的部分有三點。
  - waive 的形狀跟 `lint-waive <指紋> --note` 一致,對照 `scripts/lumos:37748-37773`。
  - 治理帳走 `_gate_event_or_warn(.., "waived", ..)`,閘名要登記進 `_KNOWN_GATES`,對照 `scripts/lumos:1825`。
  - 回傳碼 2 代表設定或參數錯,跟收集腳本的「擋下:」一致。
- 不對齊的部分見下面各條。

## 三、第二種做法:有 1 條(A1)

- 設定放進 `.lumos/macrobench.json` 的 `e2e` 段,跟 `stability` 段同做法。
- 「設定只讀主線版」是借用安全證據閘的既有原則(`scripts/lumos:8752-8783`)。
- 指紋算法跟安全證據逐檔比不同,計劃已在 WHY 寫明理由(r1 已折),我不再重列。
- 剩下一個第二種做法是原子寫入的暫存檔位置,見 A1。

## 四、落點:對齊

- 新開 `Systems/android-e2e-acceptance` 放 gate 細節與範本腳本,`pitfalls-code-loop` 只加一行連結。這跟安全證據閘有自己的家一樣,對照 `Systems/安全證據閘.md` 的 responsibility。`pitfalls-code-loop.md` 已有 290 行,不該再塞細節。
- pre-push 與 ci.yml 的接線寫進 `bound-tests-gate`,合理。它的 about_code 含 `scripts/hooks/pre-push`,而且已有 pre-push 接線的 KEY(`bound-tests-gate.md:34-37`)。
- `--results-dir` 寫進 `macrobenchmark-adapter`,合理。
- 小提醒:`e2e` 段活在 macrobench.json,而 `macrobenchmark-adapter` 的 responsibility 寫「不擋推送」。新家應連回那篇,那篇也宜補一句「`e2e` 段由新家負責」。這條不單獨算不對齊。

## A1 原子寫入的暫存檔位置跟既有原語不同
severity: major
blocking: 是

引句:「寫入一律用既有的原子寫入(先寫暫存檔再換名,暫存檔放在系統暫存目錄,不放進 `.lumos/e2e-records/`)」

- 既有原語 `_write_lf` / `_write_bytes_atomic` 的暫存檔放在目標同目錄:`path.with_name(f"{path.name}.{pid}-{uuid}.tmp-wlf")`,用 O_EXCL 建、`copymode`、`os.replace`,出任何例外都刪暫存檔(`scripts/lumos:28446-28478`)。
- 計劃一句話說「用既有的」,下一句卻指定暫存檔放系統暫存目錄,這是第二種做法。
- 暫存檔放系統暫存目錄,再 `os.replace` 到專案,跨檔案系統會失敗(EXDEV)。macOS 的 `/var/folders` 與外接或另一個磁碟上的專案就是這種情形。
- 要避免暫存檔被 `git add` 掃進去,既有做法是名稱帶 `.tmp-wlf` 後綴,而且例外時一定刪。
- 建議:直接呼叫 `_write_lf`,刪掉「暫存檔放系統暫存目錄」那半句。

## A2 放行紀錄的形狀與併發保護跟 lint-waive 不一致
severity: minor
blocking: 否

引句:「judge 與 waive 都是「讀出整份、合併、整份寫回」」

- `lint-waive` 的放行是獨立檔 `.lumos/lint-waivers.json`,內容是 `{"waivers":[{key,rule,file,reason,by,ts}]}`(`scripts/lumos:38615-38631`)。
- 它的讀-改-寫包在 `_vault_write_lock` 裡,原因寫得很明白:只做原子換名不夠,兩個工作階段同時放行,後寫的會整份蓋掉先寫的。
- 計劃把 waivers 放在每個指紋的紀錄裡,judge 與 waive 都改同一檔,卻沒寫鎖。這比 lint-waive 更容易互相蓋掉:judge 跑十幾分鐘後才寫,期間人可能已經 waive。
- `by` 欄位的來源也不一樣:lint-waive 取 `USER` 環境變數,計劃取 git user.name。人或 AI 這個區分是新需求,可以不同,但請寫明理由。
- lint-waive 有 `--list`,計劃只有 doctor 通知,沒有 `--list`。
- 計劃沒寫重複放行同一指紋怎麼處理,lint-waive 是回錯誤。
- 建議:讀改寫包鎖,並在計劃裡寫明 `by` 欄位和重複放行的處理方式。

## A3 設定驗證入口與讀法另開了一套
severity: minor
blocking: 否

引句:「跑 `lumos android-e2e check-config`(驗格式)與 `lumos android-e2e check-config --env`」

- 既有慣例是 `lumos macrobench --check-config` 旗標。它驗整份 macrobench.json 與門檻檔(`scripts/lumos:66674`、`40198`)。
- `stability` 段的驗證 `_macrobench_stab_cfg_err` 是被 `_macrobench_config` 呼叫的(`scripts/lumos:39409-39413`)。
- 計劃把 `e2e` 段的驗證放到另一個子命令,同一個檔就有兩個驗證入口。
- `_macrobench_config` 目前要求有 `results_dirs` 或 `stability` 段,否則報「要有 results_dirs」(`scripts/lumos:39415`)。只有 `e2e` 段的專案會被它擋。計劃沒提要改它。
- 「只讀主線版」要從主線樹讀 macrobench.json,而 `_macrobench_config(repo)` 只讀工作目錄。計劃沒說這個讀法借用哪一支,安全證據的 `_secev_config(for_mainline=True)` 是現成的先例(`scripts/lumos:8752`)。
- 建議:`e2e` 段的驗證寫成 `_macrobench_e2e_cfg_err`,掛進 `_macrobench_config`,並明講主線讀法。`--env` 的環境檢查可另放,命名貼近 `--check-config`。

## A4 計劃對收集腳本的描述與實際不符
severity: minor
blocking: 否

引句:「(收集腳本不呼叫 lumos,這點跟它不同)」

- 收集腳本會呼叫 lumos:`load_config()` 用 `sys.executable` 加 `os.path.join(here, "..", "lumos")` 跑 `lumos macrobench --check-config`,失敗就 `die`(`scripts/templates/android-stability-collect.sh:111-115`)。
- 所以這條「跟它不同」的代價不成立。範本腳本呼叫 lumos 應沿用同一套呼叫方式(腳本旁的 lumos 路徑、`-P` 與 `env -u PYTHONPATH`),計劃沒有寫呼叫方式。
- 建議:更正 WHY 的「代價」句,並寫明範本腳本照收集腳本的呼叫法。

## A5 回退段指向不存在的設定檔
severity: minor
blocking: 否

引句:「判定:專案刪掉 `.lumos/android-e2e.json`,`code-loop check` 的 Android E2E 判定就不跑」

- 計劃的設定在 `.lumos/macrobench.json` 的 `e2e` 段,沒有 `.lumos/android-e2e.json`。
- 回退段與設定段互相矛盾。照回退段做,會刪一個不存在的檔。
- 安全證據閘有 `gate_setting` / `mode` 降級路(`scripts/lumos:8752-8777`),本計劃的出口只有 waive 和刪 `e2e` 段,這是刻意差異,但回退文字要對。
- 建議:改成「從主線版刪掉 `e2e` 段(要合進主線才生效)」。

## A6 治理帳事件種類的寫法與既有不一致
severity: minor
blocking: 否

引句:「回頭看治理帳 android-e2e 的 failopen 次數,不為零就補一條「算不出就擋」的路」

- 既有帳的 fail-open 事件種類是 `fail-open`,帶連字號。`scripts/lumos:16230` 篩的是 `kind == "fail-open"`,`scripts/lumos:38858` 也是。
- 計劃寫 `failopen`。照這寫法記帳,doctor 的 fail-open 統計(`scripts/lumos:16230-16249`)會漏算這一道。
- 建議:統一寫 `fail-open`。計劃也應寫明 fail-open 記帳是記在哪個閘名下。

不對齊共 6 條,其中 major 1 條

判不準而交編排者的事項(⚠):無。
