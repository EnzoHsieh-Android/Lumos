severity: major

我把這份快照逐節讀完,並對照程式碼逐項查證,共 12 條。其中 5 條是會讓實作者做錯決定或違反自家驗收條款的 blocking major,其餘 7 條是 minor。另外跑了兩組 git 實驗(在 `/tmp/lumos-seat-work/android寫法寫完當下自動檢查/邊界-sonnet/t1`,未動 repo 內任何檔),證實第 3 條與第 6 條。

## F1 第一次收工不檢查,讓單輪會談與 S7 手動驗收都無法成立
severity: major
blocking: 是——這個設計讓一個會談裡通常最大的第一輪工作永遠不被檢查,而且 S7 自己的驗收步驟照規格跑不過。
- 位置:〈用詞〉「這一回合碰過的檔」、範圍 3、〈驗收條款〉S4 與 S7。
引句:「沒有回合時間戳(會談第一次收工、檔被七天清理掉、會談編號是空的)→ 這一次不檢查、只寫時間戳,下一次才開始」
引句:「在暫存區實驗專案複本用 claude -p 實跑一次,記下擋下訊息、續做結果與耗時」
- 問題:`claude -p` 是無頭的單輪執行,整個會談只有一次 Stop。規格規定第一次 Stop 只寫時間戳、不檢查,所以 S7 要求的「被回合結束檢查擋下」不可能發生。一般互動會談的第一個任務多半也是整個會談最大的一批改動,同樣完全不被查。規格只在天花板 3 把它當限制列出,沒有處理它跟 S7 的矛盾,也沒評估其他做法。
- 佐證:
  - file: `scripts/merge-claude-settings.py:166` 已有 `SessionStart` 註冊(`lumos-entry-hook.py`),會談一開始就能寫回合起點時間戳,規格沒有評估這條路。
  - file: `scripts/hooks/claude/check-graph-sync.py:985-1000` 現有 `main()` 沒有任何「回合起點」概念可借用。

## F2 `stop_hook_active` 那一次也寫入時間戳,與「續做改的檔下一次會被查」自相矛盾
severity: major
blocking: 是——照字面實作會做出與自己宣稱相反的行為,且 S4 沒有測這一段。
- 位置:範圍 3 末條與〈天花板〉1。
引句:「這道一開始(任何提早離開之前,含 `stop_hook_active` 那一次)先讀出上一個時間戳,接著立刻寫入這一次的時刻」
引句:「所以續做那一輪改的檔,下一次收工會被查」
引句:「同一回合先寫後提交的、續做那輪新加的告警,等代碼審通過前或推送前閘」
- 問題:
  - 推演:Stop#1 讀 T0、寫 T1 並擋下;AI 續做、在 T1 之後改檔 F;Stop#2(`stop_hook_active=true`)讀 T1、寫 T2;Stop#3 讀 T2。F 的修改時間早於 T2,所以不算「碰過」,續做改的檔永遠不會被查。
  - 範圍 3 這句宣稱為假,天花板 1 說的才是實況。要讓宣稱成立,`stop_hook_active` 那一次不能推進時間戳。
  - 「任何提早離開之前」也沒講清楚:沒有 `lint.json` 的專案、`LUMOS_STOP_LINT_OFF=1` 時是否照樣寫時間戳。若照寫,這支全域鉤子會替每個專案的每個會談在 `~/.cache/lumos/stop-turn/` 建檔。
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:889-899` `stop_block_decision` 對 `stop_hook_active` 直接回 False,現有鉤子沒有「這一次不推進狀態」的先例可抄。

## F3 白名單規則自相矛盾,正規範本與 S3 的正例按字面都過不了
severity: major
blocking: 是——實作者無法同時滿足〈用詞〉的規則與 S3 的正例,而且路徑檢查有可繞的漏洞。
- 位置:〈用詞〉「自動執行白名單」、S3。
引句:「整條命令除了開頭的 `$HOME` 之外不得含」
引句:「它的值(展開 `$HOME` 後)要落在 lumos 工具鏈自己的安裝目錄裡」
引句:「`ast-grep scan --config x.yml --format sarif {LINT_FILES} > {LINT_SARIF_OUT}` 應 通過」
- 問題:
  - 實際範本是 `ast-grep scan --config $HOME/harness/.../sgconfig.yml --format sarif ...`,`$HOME` 出現在 `--config` 的值裡,不在命令開頭。照「開頭的 `$HOME`」字面,範本本身被擋,工作樹模式永遠是 not-checked。
  - S3 的正例用 `--config x.yml`(相對路徑,指向專案自己的檔),卻要求通過,與「值要落在工具鏈安裝目錄」直接衝突。
  - 「安裝目錄」沒定義:是 `LUMOS_HOME`、`~/harness/lumos-toolchain` 還是 `lumos` 腳本所在目錄(`_trusted_lumos` 就有三個候選)。
  - 規格沒要求先對路徑做 `..` 與符號連結正規化。`$HOME/harness/lumos-toolchain/../../<專案>/sgconfig.yml` 只做前綴比對就通過,等於回到「用專案自己的設定檔」。
  - 這道白名單是唯一的防線(宣告檔來自被打開的專案),所以不能留這種缺口。
- 佐證:
  - file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:158` 範本 `--config $HOME/harness/lumos-toolchain/configs/ast-grep/kotlin-android/sgconfig.yml`。
  - file: `scripts/hooks/claude/impact-hook.py:~330` `_trusted_lumos()` 有三個互異的候選來源。

## F4 `git diff --quiet HEAD` 會改寫索引檔,違反 S1 的位元組相同條款
severity: major
blocking: 是——規格指定的指令跟自己的驗收條款互斥,實作者照做就會讓 S1 紅。
- 位置:範圍 2 宣告檔檢查、S1。
引句:「用 `git diff --quiet HEAD -- <檔>` 判,換行轉換設定不影響」
引句:「跑完之後真正的索引檔 應 跟跑之前位元組相同」
- 問題:實測(git 2.39.2)在檔案被 `touch` 過、需要重新比對的狀態下:
  - `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all` 索引不變。
  - `git diff --quiet HEAD -- <檔>` 的索引雜湊從 a25c… 變成 77bd…。
  - `git --no-optional-locks diff --quiet HEAD -- <檔>` 照樣改寫(e5a2…→9284…),`--no-optional-locks` 擋不住它。
  - 換成 `git --no-optional-locks diff-index --quiet HEAD -- <檔>` 則不改寫。
  - 回合結束鉤子每輪都會跑到這一步,會在使用者自己的 git 操作旁邊偷偷改寫索引。
- 佐證:實驗在 `/tmp/lumos-seat-work/android寫法寫完當下自動檢查/邊界-sonnet/t1`,指令與雜湊如上。

## F5 `lint-new` 與鉤子之間沒有機器可讀的通道,「批次雜湊」無從計算
severity: major
blocking: 是——防無限擋的核心(同一批判定)沒有資料來源,實作者必須自己發明介面。
- 位置:範圍 1 的指令旗標與輸出、範圍 3 防無限擋。
引句:「`--diff <範圍>` 或 `--worktree [--only-stdin]` 恰好給一個」
引句:「最多印 20 條、其餘印條數」
引句:「在 `stop-block/` 建 `<會談>.lint-<批次雜湊>`」
- 問題:
  - `lint-new` 的旗標只有 `--diff`、`--worktree`、`--only-stdin`、`--budget`,沒有 `--json`,也沒有像 `LUMOS-BLOCKS:` 那樣的機讀行。
  - 批次雜湊要用「新增告警指紋多重集合」,鉤子只能解析人讀文字,而文字最多印 20 條。第 21 條起指紋進不了雜湊,「同一指紋多出一處 應 算新的一批再擋」在告警超過 20 條時不成立。
  - 擋下原因要「檔:行、訊息、指紋」,同樣得靠解析文字。
- 佐證:file: `scripts/lumos:72135` 到 `72230` `code-loop check --keep-going` 為同一個需求就設了 `LUMOS-BLOCKS:` 機讀行,說明這類介面需要單獨的機讀通道。

## F6 宣告檔「有沒提交的修改」判法抓不到未追蹤的 `.lumos/config.json`
severity: minor
blocking: 否——只是工作樹模式多一個漏檢路徑,推送前閘仍兜底,不會讓系統壞掉。
- 位置:範圍 2 宣告檔條。
引句:「或它與 `.lumos/config.json` 有沒提交的修改」
- 問題:實測 `.lumos/config.json` 是未追蹤檔時,`git diff --quiet HEAD -- .lumos/config.json` 回 rc=0。未追蹤的 `{"lint_new":{"gate":"off"}}` 會被當成「沒修改」而生效,鉤子悄悄不查。`lint.json` 用了 `cat-file -e HEAD:` 所以不會漏,只有 `config.json` 這條漏。
- 佐證:file: `scripts/lumos:40050` 起 `_lint_new_config` 讀工作目錄的 `config.json`,不看 git 版本。

## F7 PRIOR-ART 引用的既有做法並不存在
severity: minor
blocking: 否——不影響實作路徑,但讓「沿用既有」的承諾不實,審查要靠這句判斷風險。
- 位置:範圍 2 改動清單、PRIOR-ART ②。
引句:「沿用既有 `_handoff_files` 那一族的 `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all` 解法」
- 問題:`_handoff_files` 呼叫的是 `status --porcelain -z -uall`,沒有 `--no-optional-locks`。整個 `scripts/lumos` 與 `scripts/hooks` 都沒有這個旗標,所以「沿用既有解法」不實。
- 佐證:
  - file: `scripts/lumos:72868` `_lens_git(root, "status", "--porcelain", "-z", "-uall")`。
  - file: `scripts/lumos:50942` 同族 `_tg_rb_pending`,也無該旗標。

## F8 新增的函式與酬載欄位與既有的重複,而且兩份計劃對「共用」的定義不一致
severity: minor
blocking: 否——是維護與一致性問題,實作者仍能做出可用的系統。
- 位置:範圍 4 的 `delta_new`、`_kotlin_strip`、`_kt_decision_table`、`_kt_trigger_re`。
引句:「payload 多三個鍵:`delta_new`」
引句:「`_kotlin_strip`,新增,兩案共用」
- 問題:
  - 鉤子酬載已經有 `delta_text`,內容同樣是編輯文字、上限同樣 2 MB,只是處理超限的方式不同(截斷對不放)。同一個酬載會帶兩份近乎相同的 2 MB 文字。
  - repo 有註解明寫「全庫只有這一支」的 `_strip_c_comments`(`blank_strings`/`keep_length` 都有),規格另起 `_kotlin_strip`,沒說明為什麼不擴充它。規格列的處理項沒有字元字面值 `'"'` 與 `\"` 跳脫,`_C_STRIP_PAT` 反而都認得,照規格寫會在這兩種寫法之後整段剝錯。
  - 讀決策表已有 `dt_triggers` 與感知反引號的 `_cells`(且處理「(無)」),規格新寫 `_kt_decision_table` 沒提到它們。
  - 〈範圍 4〉的 `_kt_trigger_re` 規則是「前後都不准緊接英數或底線」。母案「Android寫法語意情境表態與盲判」第 36 行寫的是「只在觸發字開頭是英數或底線時才要求前一個字元不是英數或底線」。兩份都說「共用」,實際定義不同。
- 佐證:
  - file: `scripts/hooks/claude/impact-hook.py:417` `extract_delta_text`。
  - file: `scripts/lumos:6795` `_C_STRIP_PAT`。
  - file: `scripts/lumos:6820` `_strip_c_comments`。
  - file: `configs/ast-grep/kotlin-android/check.py:108` `_cells`。
  - file: `configs/ast-grep/kotlin-android/check.py:115` `dt_triggers`。

## F9 專案沒有圖譜時,`cmd_impact` 與鉤子之間的回傳約定沒寫
severity: minor
blocking: 否——S5 的「沒圖譜照樣推」測試會逼實作者找到答案,但規格應先講清楚。
- 位置:範圍 4 第二條。
引句:「在那個提早返回之前先算 `decision_rows` 並回傳(其他輸出照舊為空)」
- 問題:現在沒圖譜時 `cmd_impact` 走 `_no_vault_msg()` 回 rc=3,JSON 一個字都不印;鉤子 `_run_impact` 一看 rc==3 就記成 `no_vault` 失敗、不解析輸出。規格沒說這條路要改回 rc=0 並印 JSON,也沒說 `_no_vault_msg` 往 stderr 的那段話要不要照印(每次改 kt 都印一次)。
- 佐證:
  - file: `scripts/lumos:64949` `return _no_vault_msg()`。
  - file: `scripts/hooks/claude/impact-hook.py:974` `if rc == 3:`。

## F10 「常用字不准當觸發字」的把關擋不住實際型錄裡的常用字
severity: minor
blocking: 否——只是推播偏吵,每列同會談只推一次,不影響功能。
- 位置:範圍 4 末條、〈實務隱患〉。
引句:「型錄的觸發字由第一批的型錄格式檢查把關:不准收一般常用字」
引句:「最多三列、同列同會談 24 小時內只推一次、常用字不准當觸發字」
- 問題:實際型錄的觸發字包含 D-33 的 `Composable`、D-34 的 `Modifier`、`padding`、`clickable`、`background`,D-39 的 `Inject`、`Singleton`,D-56 的 `onCreate` 等,在 Compose 與 Android 檔裡幾乎每支都會出現。把關用的 `STOP_TRIGGERS` 是人工列的短清單,沒收這些字,所以檢查是綠的。第一次改任何 Compose 檔就會推 D-33、D-34。第三道「常用字不准」的緩解實際上形同虛設。
- 佐證:
  - file: `skills/kotlin-idioms/checks-catalog.md:701` D-33 觸發字含 `Composable`。
  - file: `skills/kotlin-idioms/checks-catalog.md:702` D-34 觸發字含 `Modifier、padding、clickable、background`。
  - file: `configs/ast-grep/kotlin-android/check.py:95` `STOP_TRIGGERS` 清單。

## F11 鉤子取「碰過的檔」與組擋下原因都沒說明檔名處理方式
severity: minor
blocking: 否——少報或排版錯亂,不會擋錯人;但現有鉤子已為同一個問題做過防護,新增段落不應退步。
- 位置:範圍 3 呼叫與擋下原因。
引句:「呼叫 `lumos lint-new --worktree --budget 8 --only-stdin`、從標準輸入送這一回合碰過的檔」
引句:「最多 10 條、整段最多 1500 字,結尾一行教放行指令」
- 問題:
  - 鉤子既有的 `_git_status_entries` 用不帶 `-z` 的文字解析,對含換行、尾端空白、` -> ` 的檔名會解析錯,資料夾內任何非 UTF-8 檔名還會讓 `text=True` 解碼失敗、整次回 None 靜默放棄。規格只替 lumos 側指定 `-z`,鉤子取清單的方式沒寫。
  - 擋下原因會變成下一輪的提示,檔名來自工作樹。既有 `stop_block_reason` 用 `_safe_path` 消毒檔名並寫明「檔名寫什麼都不是指令」,新原因沒有同樣要求。
- 佐證:
  - file: `scripts/hooks/claude/check-graph-sync.py:330-362` `_git_status_entries`。
  - file: `scripts/hooks/claude/check-graph-sync.py:928-931` `_safe_path`。

## F12 `lint-new` 沒說怎麼找 repo 根,專案根在子目錄時會永遠 rc3
severity: minor
blocking: 否——只影響子目錄專案(monorepo 的 Android 子專案),落到 rc3 不會擋人。
- 位置:範圍 3 條件、範圍 2 路徑規則、範圍 1 旗標。
引句:「條件:專案根有 `.lumos/lint.json`」
引句:「路徑一律相對 `git rev-parse --show-toplevel`」
- 問題:鉤子判斷的是 `CLAUDE_PROJECT_DIR` 底下有沒有 `lint.json`,但 `lint-new` 沒有 `--repo`,而且宣告檔檢查用的 `HEAD:.lumos/lint.json` 是相對 git 頂層的。專案根不等於頂層時,鉤子條件成立、`lint-new` 卻在頂層找不到宣告檔,每次收工都回 rc3 並印一行,功能永遠不啟用。
- 佐證:
  - file: `scripts/hooks/claude/check-graph-sync.py:750` 既有呼叫 `lumos` 時都帶 `--repo str(project_root)`。
  - file: `scripts/lumos:40050` `_lint_new_changed_files` 的 `cwd` 是 `repo_root`。

## 逐節結論
- 開頭欄位、白話、PRIOR-ART、RETIRE-IF:已讀,只有 F7 一條。
- 〈用詞〉:F1、F2、F3、F8 涉及。
- 〈範圍〉1:F5 涉及。
- 〈範圍〉2:F4、F6、F7、F12 涉及。
- 〈範圍〉3:F1、F2、F5、F11、F12 涉及。
- 〈範圍〉4:F8、F9、F10 涉及。
- 〈範圍〉5:已讀,無 finding。`_codeloop_guard_verdict` 的 `keep_going`、`lint_on_pf_fail` 路徑都存在,沿用可行。
- 〈範圍〉6:已讀,無 finding。
- 〈不做〉:已讀,無 finding。
- 〈開審前的改寫〉:已讀,無 finding。
- 〈實務隱患〉:已讀,F10 涉及;時間公式 55×0.7−12=26.5 算得對。
- 〈驗收條款〉:F1(S7)、F2(S4)、F3(S3)、F4(S1)涉及。
- 〈回退〉與〈天花板〉:已讀,F2 涉及。

交叉引用逐一核對過,目標都存在(五個 `lands_in` 與三個母案節點)。`Systems/回合結束寫法檢查` 是待新建的節點,符合「新開」的預期。

## 實務隱患逐類
- 資安:有問題,見 F3。白名單矛盾與路徑正規化缺口是主要風險。
- 檔案系統與資料量:無新增問題。50 支檔上限與 `git cat-file --batch` 的規劃合理,最壞情況的時間在預算公式內(25.5 秒仍大於需要的 25 秒)。
- 並行與共用工作目錄:無新增問題。規格已列為天花板。
- 邊界(空、新 repo、合併中、detached HEAD、子模組):
  - 沒有 HEAD:規格已明確 rc3。
  - 合併或 rebase 中:規格已明確 rc3,`git rev-parse --git-path` 在 worktree 也正確。
  - 子模組裡的 kt 檔不會被掃,是靜默的漏檢,屬於低嚴重度,未另列。
  - 子目錄專案:F12。
  - 含空白或換行的檔名:F11。
- 終止與殘留:SIGTERM 與 SIGKILL 之後 `.lumos/lintbase-*` 的殘留,規格已承認並沿用一天清理。

## 固定席節點判讀
- `Systems/lumos-cli-lifecycle` 的 INVARIANT(re-inject 只動 sentinel 之間):這份設計只改 `HOOK_BUDGET` 數值與鉤子註冊,不碰 CLAUDE.md 的 sentinel。不影響。
- `Systems/design-loop` 的處置閘 INVARIANT:規格只動 `code-loop pass` 前的機械檢查,沒碰設計審的 `loop status --disposal`。不影響。
- `Systems/canary-audit` 的 INVARIANT(canary record 落盤、second 不影響 gate):規格不碰 canary。不影響。
- `Systems/lumos-cli-read` 的 INVARIANT(search 排除 superseded):規格不碰 search。不影響。
- `Systems/pitfalls-code-loop`(★RISK★):它的 KEY 是風險類別名與詞表的漂移守衛,規格沒有新增或改名風險類別。但這份設計改了 `code-loop pass` 的前置條件,節點沒有記載 pass 的行為,實作後要補。
- `Systems/hook逾時預算` 的 KEY(內層逾時走「天花板 × 0.7 − 已耗」、超時不殺子行程):
  - 把天花板從 40 提到 55,走既有公式,沒有破壞公式。
  - 規格讓 `lint-new` 逾時時殺掉整組檢查工具,這與該節點「超時不殺子行程」那條 KEY 不同。那條 KEY 針對的是派工鏡頭的 20 分鐘快取計算,不是檢查工具;規格的理由(預算硬、結果當場作廢)成立,但規格沒有說明跟那條 KEY 的差異。
  - 該節點寫「收工檢查外層 30」,程式現值是 40,節點本身已過時,與這份設計無關。

最嚴重是 major,blocking 共 5 條(F1 到 F5)。
