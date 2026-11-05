severity: major

我只讀 spec、對照程式碼,沒有改任何檔,也沒有建臨時目錄。以下 6 條 finding 都是邊界與失效情境下,照 spec 字面實作會出錯的地方。

**F1:`pf_json` 空(pitfalls 出錯或逾時)時,功能分支從「全套」降成「幾乎什麼都不跑」**
severity: major
blocking: 是(照字面實作會把現行「算不出就多跑」的方向反轉成「算不出就少跑」)
- spec 段落:〈做法〉第 2 點。
引句:「這個 ref 原本判 `full` 時改判 `light`(沿用 `_SUITE_LIGHT`,不新增狀態);關鍵字照現行從 `pf_json` 的 `affected_keys` 取」
- 問題:`pf_json` 是 `pitfalls ... 2>/dev/null || true`,出錯或逾時就是空字串。這時 `_suite_this` 保持預設的 `full`,現行會跑全套。
- 照 spec,這個 ref 會被無條件降成 `light`。此時 `_k` 為空,`_AUTOLOOP_FULL` 讀不到、維持 0。
- 結果是只跑文件子集,加自主迴圈那支的 `-k real_claude_md`。
- 同一條路徑也適用於 `_test_suite_for_range` 回 `full` 且 reason 是「算不出改動清單」或「範圍算不出來」。這兩種的程式碼注解都明寫「fail-safe 是多跑,不是少跑」。
- spec 沒有寫「`pf_json` 空時不降級」,實務隱患那節也沒提。
- 佐證:
  - `scripts/hooks/pre-push:540` 的 `pf_json=...|| true`。
  - `scripts/hooks/pre-push:544` 的 `_suite_this="full"`。
  - `scripts/lumos:61714-61720` 的 `full` 兜底回傳。

**F2:降級繞過現行的 `light_ok` 守衛,測試檔、守衛檔、hook 本身改了也只跑文件子集**
severity: major
blocking: 是
- spec 段落:〈做法〉第 2 點,以及〈現況〉第二點。
引句:「改了測試檔,測試檔簽名基準 `governance/anchor-baseline.json` 就跟著變;它在守衛檔清單 `_DOCS_ONLY_NEVER`,所以幾乎每個功能推送都判成全套。」
- 問題:現行 light 要同時滿足兩個條件,才算降級:
  - `spec-gate` 輸出「改動風險分級:light」。
  - `pf_json` 的 `light_ok` 為真。`light_ok` 是代碼審資安席加的,理由是測試檔、skills、workflow 這種「既不是文件也不是程式」的檔不准少跑全套。
- spec 只說「原本判 full 就改判 light」,沒說這兩個條件還保不保留。
- 照字面實作的結果是改 `test_lumos.py`、`anchor-baseline.json`、`.github/workflows`、`skills/` 時,`_test_suite_for_range` 走 guard 分支回 `code: []`。
- `_affected_test_keys` 見到空清單回 `[]`,所以 `affected_keys` 為空。
- 於是改到測試檔、改到守衛的那次推送,本機什麼測試都不跑。spec 的設計動機正是這類推送,所以這是主場景,不是邊角。
- `_k`、`_AUTOLOOP_FULL` 的讀取目前都寫在 `light_ok` 的 `if` 區塊裡面。spec 沒說降級要放進區塊內還是另寫一份,實作者會被迫自己決定。
- 佐證:
  - `scripts/hooks/pre-push:572-577` 的條件與賦值。
  - `scripts/lumos:61707-61710` 的 `light_ok` 定義。
  - `scripts/lumos:61722-61724` 的 guard 分支。
  - `scripts/lumos:61758-61762` 的 `if not code_files: return []`。

**F3:「功能分支」的判斷寫死 `main`/`master`,與程式碼已有的「主線」概念不一致**
severity: major
blocking: 是(依「照字面實作會漏掉合約」判準)
- spec 段落:〈做法〉第 1 點。
引句:「目的是 `refs/heads/<名>` 而且名字不是 `main` 或 `master` → 這個 ref 算功能分支」
- 逐形狀核對,這幾種只要用完整名字精確比對就正確:
  - `refs/heads/main2`、`refs/heads/feature/main`、`Main`:算功能分支。GitHub 與 `ci.yml` 的 `branches: [main]` 都分大小寫,所以這是對的。
  - 標籤、`refs/for/*`、`refs/pull/*`、`refs/changes/*`:照現行,spec 有寫。
- 問題在於 spec 禁止「另寫 lumos 子指令」,又用字串寫死 `main`/`master`。程式碼已有 `_push_mainlines` 與 `_NOTE_REREAD_MAINLINE_NAMES`,而且程式碼的注解特地講過「遠端 HEAD 指到的分支名也算主線」。
- 推到非 `main` 的預設分支(例如 `develop`、`trunk`),以及推到其他遠端的 `main`,本機會跳過全套。
- `ci.yml` 的 `push` 只觸發 `branches: [main]`,所以這些分支的推送連 CI 也沒有。spec 的「全套由 PR 的 CI 跑」在這裡不成立。
- 實作若用 `${_rref##*/}` 取基名,`refs/heads/feature/main` 會被誤判成主線。spec 沒有寫明要比完整名字。
- 佐證:
  - `scripts/lumos:53729-53735` 的 `_NOTE_REREAD_MAINLINE_NAMES`。
  - `scripts/lumos:65263` 的 `_push_mainlines`。
  - `.github/workflows/ci.yml:5-8`。

**F4:「PR 的 CI 全套照跑」的前提是有開 PR,spec 沒處理沒開 PR 或推到別的遠端**
severity: major
blocking: 是
- spec 段落:〈做法〉第 3 點的訊息,以及〈實務隱患〉守衛面。
引句:「推功能分支:本機只跑文件子集與跟改動有關的測試,全套由 PR 的 CI 跑;合併前要 `lumos ci-wait` 綠」
- 問題:`ci.yml` 的觸發是 `push` 只有 `main` 與 tags,加上 `pull_request`。
  - 功能分支推上去、還沒開 PR 之前,沒有任何測試在跑。
  - 推到別的遠端(備份遠端、fork、鏡像)的功能分支,也沒有任何全套。
  - 分支被 `git merge` 後再用 `HEAD:main` 推,是 main 的 ref,本機會跑全套,這條路是安全的。
- 但「推到遠端別的分支、再由遠端工具以非 PR 方式合入」或「PR 針對的目標分支不是 main」(`pull_request` 沒有 `branches` 限制,倒是會觸發 CI),spec 沒有說清楚前提。
- 訊息把「PR 的 CI 會跑」寫成事實,實際是條件式的。
- 佐證:
  - `.github/workflows/ci.yml:4-9`。
  - `.github/workflows/ci.yml:47`。

**F5:關鍵字為空時,訊息與行為對不上**
severity: minor
blocking: 否(措辭與精度)
- spec 段落:〈做法〉第 3 點。
- 問題:降級後如果 `_k` 為空(F1、F2 的路徑,或單純抽不出關鍵字),實際只跑文件子集。
- 第 3 點的訊息仍寫「跟改動有關的測試」。現行掛鉤對這情況有另一句「抽不出函式或檔名當關鍵字,推送前只跑文件子集」,spec 沒說兩句如何並存。
- 另外,第 3 點的訊息放在 ref 迴圈裡印。舊版 `test_lumos.py` 不認得 `--suite` 或 `--graph` 時,掛鉤會退回全套,但訊息已經印出「本機只跑文件子集」。
- 消費專案(沒有 `skills/`)根本不跑測試閘,也會印這句。
- 多個功能分支一起推,這句會重複印。
- 佐證:
  - `scripts/hooks/pre-push:866-877`(探 `--suite` 與 `--graph`)。
  - `scripts/hooks/pre-push:884-891`。

**F6:第 4 點 `run_group` 改法的邊界沒寫**
severity: minor
blocking: 否
- spec 段落:〈做法〉第 4 點、S2。
- 問題:改成「每片都回 3 才算一支都沒選到」,對 `k`(關鍵字)組合理。
- 但同一個 `run_group` 也跑 `s`(文件子集或全套)組,而且 `_grc` 非 0 一律判紅。改成「全 3 才回 3」之後,`s` 組某片 0 支、其他片有測試時會回 0。這個行為變化沒寫,S2 只測關鍵字組。
- 佐證:
  - `scripts/hooks/pre-push:914-947`。
  - `scripts/hooks/pre-push:962`。

**驗收條款 S1–S4**
- S1 只列「功能分支降級、推 main、推標籤、混推」四種。
- 沒有條款覆蓋以下情境,而這些正是 F1、F2、F3 的邊界:
  - `pf_json` 為空。
  - `light_ok` 為假。
  - `main2`、`feature/main`、`Main` 這類名字。
  - 預設分支不是 `main`。
- S3 依賴 `autoloop_full`,但空 `pf_json` 時該值讀不到。

**〈現況〉、〈範圍〉、〈回退〉、〈審計修正紀錄〉:已讀,無 finding。**

- 〈現況〉中 CI 的 PR 事件一律全套,我核對 `ci.yml` 第 83 行與第 90 行,屬實。
- main 無分支保護,我沒有去驗證(這是外部事實,spec 已標 `[來源:外部]`)。

**實務隱患逐類**
- 併發:spec 已列。
- 守衛面:見 F1、F2、F4。
- 版本錯開:spec 說「新掛鉤配舊 lumos」不受影響,但舊 lumos 的 `pitfalls` 若沒有 `light_ok` 或 `affected_keys` 欄位,新掛鉤降級後也是空值,等同 F1。這句「不影響判定」不成立。

總結:最嚴重等級為 major,共 4 條會擋的問題(F1 至 F4),另有 2 條不擋(F5、F6)。
