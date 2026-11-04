severity: major

我是邊界席(極端輸入代言人)。實驗檔都放在 `/tmp/lumos-seat-work/android協程與api寫法機械檢查標準/邊界-sonnet/`,收貨後請編排者刪。

## Findings

**1. 合併衝突的檔用規定的做法偵測不到,S5 那一句過不了**
- 規定做法是「複製索引、暫時索引上 `git add -A`、`git diff --cached --find-renames HEAD`」。
- 我造了 `UU A.kt` 的衝突:
  - 暫時索引做完後,`git diff --cached --name-status HEAD` 只回 `M A.kt`。
  - 對真索引跑 `git diff --name-status HEAD` 也只回 `M`。
  - 狀態 U 在這條路上不存在。
- 後果:帶 `<<<<<<<` 標記的衝突檔會被當一般修改檔掃,S5 的「合併衝突中的檔應列成沒檢查」寫不出來。
- 偵測得在真索引上查,例如 `git ls-files -u`,spec 沒寫。
- 引句:「合併衝突中的檔(狀態 U)不掃」
- 引句:「在暫時索引上 `git add -A`」
severity: major
- blocking: 是(照字面實作,S5 其中一句必紅)

**2. `git add -A` 沒算進預算,而且會把檔案寫進真的物件庫;鉤子裡它排在既有收工點名之前**
- 實驗:repo 裡放一支 400MB 未追蹤檔,在暫時索引上 `git add -A`。
  - 耗時 8.6 秒。
  - `.git` 從 108KB 漲到 410MB(`du -sk`),暫時索引不動真索引,但物件寫進了真的 `.git/objects`。
- 預算不涵蓋這一步:spec 的時間預算只管「命令」,`git add -A` 不是命令。
- 鉤子有 40 秒外層天花板,超過會被整支砍掉(SIGKILL)。檢查插在既有圖譜提醒之前、同一個行程,所以會連既有提醒一起餓死。
- 既有那道用 `status --porcelain -uall`(只看檔案狀態、不算雜湊,不會寫物件),spec 把這個成本從零變成「未追蹤位元組數」。
- `--only` 有給時沒說暫時索引可以只 `add` 那幾支。
- file: `scripts/hooks/claude/check-graph-sync.py:985`(`main()` 單一行程,`_inner_budget` 只管 `_git` 與外部命令)
- 引句:「插在既有那道的所有提早離開(找不到圖譜、動過筆記、同批檔已講過)之前」
severity: major
- blocking: 是(能讓既有 Stop 鉤子的提醒失效)

**3. `--only` 零支檔時的語意沒定義;「這一輪有寫檔動作」的條件太鬆**
- 觸發條件只問「逐字稿裡有寫檔動作」,沒問寫的是不是程式碼檔。
- 輸入:整輪只 Write 了一篇筆記 `.md`(本專案幾乎每輪都這樣)。
  - 鉤子要傳 `--only` 的清單是空的。
  - 照字面「`--only` 給了就只看那幾支」,零支就是沒給,等於掃整個工作樹。
  - 這正好違反同段「不碰別的會談的改動」,還會花掉那半份預算。
- 若 argparse 設 `nargs='+'`,則是 rc2 加例外。
- 路徑形式也沒定:逐字稿給絕對路徑,`mv` 的來源是已不存在的檔。
- S6 沒有「這輪只寫了非程式碼檔」的案例。
- 引句:「條件:專案根有 `.lumos/lint.json`;這一輪逐字稿裡有寫檔動作」
- 引句:「`--only` 給了就只看那幾支」
severity: major
- blocking: 是

**4. 靠逐字稿列舉寫過的檔,漏掉 shell 寫的檔**
- 既有鉤子自己記載過列舉法補不完:「286 次走 shell、31 次走編輯工具」。
- `collect_turn_actions` 只認 Edit/Write/MultiEdit 與 `rm/mv/cp/git rm/git mv`(`BASH_FILE_OPS_PATH_BEARING`)。
- 輸入:Bash 跑 `sed -i 's/a/b/' app/A.kt`、`cat > app/A.kt <<EOF`、`ktlint -F`。這些檔不進 `--only`,甚至整道檢查不觸發(沒有寫檔動作)。
- spec 要的「不碰別的會談的改動」和這件事互相打架,spec 沒承認這個代價。
- file: `scripts/hooks/claude/check-graph-sync.py:21`(說明段)與 `:204`(`collect_turn_actions`)
- 引句:「檢查範圍只限這一輪逐字稿裡寫過的程式碼檔(`--only`),不碰同一工作目錄別的會談的改動」
severity: major
- blocking: 否

**5. 同一輪先寫後提交,「寫完當下」的檢查什麼都看不到**
- 基準取 `HEAD`、現在版取工作樹。本專案規矩是一個功能一個提交,AI 常在同一輪提交。
- 輸入:本輪 Write 一支帶新告警的 `Foo.kt`,然後 `git commit`,再結束。
  - 工作樹等於 `HEAD`,diff 空。
  - 既有鉤子的 `code_entries` 也是空,直接 return。
  - 這批告警只剩推送前閘會看。
- 「天花板」只寫了續做那輪的缺口,沒寫這個。
- 引句:「基準是 HEAD 那一版、現在版直接讀工作樹的檔」
severity: major
- blocking: 否

**6. 規則的 `files`/`ignores` 路徑規則遇到絕對路徑會反轉(對照 `**/test/**` 這類)**
- 閘餵給工具的是絕對路徑:
  - file: `scripts/lumos:38840`(`_lint_new_extract` 回傳 `str(target)`)
  - 這些路徑再被餵進 `{LINT_FILES}`。
- 草稿規則包有 15 條 `files: ['**/test/**','**/androidTest/**']`、9 條 `ignores` 同樣的路徑。
- 實驗,同一份 `src/main/X.kt`、同一份規則:
  - 放在 `.../test/proj/app/src/main/` 下,絕對路徑掃,命中 `kt-test-only`(只該掃測試碼的規則打在正式碼上),`kt-prod-only` 被略過。
  - 放在無 `test` 祖先的目錄,絕對路徑掃,命中 `kt-prod-only`。
  - 在 `test/proj` 內用相對路徑掃,命中 `kt-prod-only`。
- 所以專案放在祖先目錄叫 `test` 的位置(如 `~/test/app`),正式碼規則全部靜默失效、測試規則亂響。
- 另外 spec 的樣本是平鋪的 `samples/bad/`、`samples/good/`。這些 TEST 規則在那個路徑下不會命中,S1「每條至少命中兩個壞例」對它們必紅,除非樣本放在帶 `test` 或 `androidTest` 的子目錄。spec 沒寫。
- 引句:「每條規則的壞例好例樣本 `samples/bad/`、`samples/good/`」
severity: major
- blocking: 是(S1 對測試類規則必紅)

**7. ast-grep 版本不合或規則包壞掉,整道閘靜默轉成環境不可用**
- 實驗,規則檔多一個未知鍵(模擬舊版本不認新語法):整份規則包 rc=8、stdout 0 位元組。
  - `_lint_run_and_parse` 回 `ok=False`,歸進 env 自動放行。
  - 一條規則壞,全部規則失效。
- 實驗,`ruleDirs` 指到空目錄:rc=0、輸出合法的空 SARIF。這會被記成「跑過且乾淨」,印「沒有新增的告警」。
- spec 只寫「釘版本」,沒給版本號,也沒給最低版本檢查。
- 規則包跟工具鏈 clone 一起更新,ast-grep 由各機器自己裝,兩者會脫節。
- 「實務隱患:工具沒裝」只涵蓋沒裝,不涵蓋版本落差,也沒說回合結束鉤子要記帳(`lint-new` 與鉤子不寫治理帳)。
- spec 自己寫了 detekt 那案的「探針」,本案沒對應的規則包可載入檢查。
- 引句:「CI 要先裝 ast-grep-cli(釘版本)並 clone 工具鏈」
severity: major
- blocking: 否

**8. 型錄的 S3 在現檔上第一天就紅,強/弱觸發字沒有欄位**
- `skills/kotlin-idioms/checks-catalog.md` 的〈待查證〉節有 135 列,每列只有 3 欄,編號又重複前面主表。
  - 例:`:653` 與 `:828` 的 `PERF-32`。
- S3 的「欄位數正確、編號唯一」若掃全檔,必紅。spec 沒寫掃哪幾節。
- 〈情境決策表〉(`:662`)現有欄位是「情境|標準寫法|不適用時|觸發字|對應檢查」,觸發字只有一欄。
- 範圍 1 只加「列編號」與「通電批次」,沒有強/弱標記欄。S3 的「至少一個強觸發字」與範圍 9 的強弱門檻都沒有資料來源。
- S7 因此無法照型錄資料實作。
- 引句:「〈情境決策表〉每列 應 有列編號且至少一個強觸發字」
- 引句:「每列 應 欄位數正確(反引號裡的直線不算欄位分隔)、編號唯一、標準寫法與接電方式與通電批次非空」
severity: major
- blocking: 是

**9. 改檔前推列:新旗標與既有 `--stdin-payload` 的 `delta_text` 重複,且既有做法含舊字串**
- 既有鉤子已經把 `{query, prospective, delta_text, delta_truncated}` 用 `--stdin-payload` 餵給 `lumos impact`(2MB 上限)。
- 既有的 `extract_delta_text` 是 Edit 的舊字串加新字串,另含 MultiEdit 的每個 edit。
- spec 的新旗標 `--delta-stdin` 沒說:
  - 與 `--stdin-payload` 是什麼關係。
  - stdin 只有一條,兩個旗標不能同時讀。
  - 重用 `delta_text` 會讓「只在被刪掉的舊字串裡」也命中,S7 那句就違反。
  - 比對範圍只列「Edit 的新字串、Write 的全文」,MultiEdit 沒寫(鉤子 `EDIT_TOOLS` 有它)。
- file: `scripts/hooks/claude/impact-hook.py:414`(`extract_delta_text`)與 `_impact_for_file` 組 cmd 處(`:~1000`)
- 引句:「鉤子把寫入內容交給 `lumos impact --file <檔> --delta-stdin`(新增旗標)」
severity: major
- blocking: 否

**10. 「同會談只講一次」標記是先標後講,而且在鉤子行程裡,與「只有印出的列才記」對不上;並行的兩個改檔呼叫會重複推**
- file: `scripts/hooks/claude/impact-hook.py:825`(`_voice_once`):檢查當下就建標記,沒有「只標印出的」的版本。
- 選列(取前三)在 `lumos` 行程,標記在鉤子行程,spec 沒說會談編號與標記目錄怎麼傳進 `lumos`。
- 輸入:同一則訊息同時發兩個 Edit(兩個鉤子行程並行)。兩邊都先選出同樣的前三列才標記,結果推兩次,違反 S7「同一會談同一列第二次不推」。
- 標記目錄 24 小時後被惰性清掉(`_ttl_lazy_cleanup`),跨日長會談會重推。
- 引句:「用既有的同會談只講一次標記,鍵是列編號」
severity: minor
- blocking: 否

**11. 擋停的「只提醒」模型看不到**
- 既有鉤子文件寫明 exit 0 的 stderr 模型看不到、只進除錯日誌。
- spec 的「同一批第二次只提醒」與「第四次只提醒」所以完全是靜默。這兩次的告警只剩推送前閘看得到。
- 實務隱患的「推送前閘兜底」成立,但「提醒」兩字讓人誤以為有訊息。
- file: `scripts/hooks/claude/check-graph-sync.py:10`
- 引句:「一個會談這道最多擋三次,之後只提醒」
severity: minor
- blocking: 否

**12. 設定檔把閘設成 warn 時,鉤子仍會擋**
- `_lint_new_classify`:`lint_new.gate="warn"` 時 `status=warn`、`blocked=False`。
- file: `scripts/lumos:38996`
- spec 的擋停條件寫的是「有新增告警」,沒寫「且 `blocked`」。
- 輸入:專案設 `lint_new.gate:"warn"`,本輪新增一處告警。
  - 照字面,鉤子 block。
  - 與設定「只報告、不擋」相反。
  - 同樣沒寫 `lint-new` 的 rc、`code-loop pass` 對 warn 的處理。
- `lint_new.gate="off"` 時,spec 也沒說鉤子怎麼辦(spec 只有自己的 `LUMOS_STOP_LINT_OFF`)。
- 引句:「有新增告警就回 decision:block」
severity: major
- blocking: 否

**13. `lint-new` 的輸出沒涵蓋 off / no-config / no-files / warn / not-checked**
- 既有判定函式有 8 種 status(`:39031` 的 docstring)。
- spec 只定義:有新增 rc1、沒有新增 rc0、環境不可用 rc0、全沒跑「不算乾淨」。
- 輸入:
  - 工作樹只刪檔(只刪不加)。
  - 工作樹零支 kt 檔。
  - 專案沒有 `lint.json`。
  - `LUMOS_SKIP_LINT_NEW` 有設。
- 這四種都不是上述四個之一,最後一種直接是 off。
- 若實作歸到「沒有新增的告警」,對 no-config 或 off 是假的安心。
- 引句:「環境不可用(工具沒裝、跑不出結果)rc0 並印哪條命令沒跑、為什麼」
severity: minor
- blocking: 否

**14. 改名加修改:超過 1000 支或相似度不到一半,會退成 D 加 A**
- 實驗,每支改名並改 `package` 行:
  - 900 支:全是 `R`。
  - 1001 支:全是 `A`(各 1001 筆 A 與 D)。
- 這是 `diff.renameLimit` 預設 1000。同時 git 的改名預設相似度 50%,很小的檔改名再大改也會變 A 加 D。
- 退成 A 之後,舊有告警全算新增:`lint-new --worktree` 會吐上百條,放行要一條指紋一條指紋來(`lint-waive` 每次一個)。
- 這條與 spec 說的「配得到 R100」不是同一件事,只覆蓋未改內容的改名。
- 引句:「未追蹤的改名 `mv Foo.kt Bar.kt` 配得到 R100」
severity: minor
- blocking: 否

**15. 擋停原因沒有條數或字數上限**
- 既有 `stop_block_reason` 把整段限在 1500 字,理由是「約 2500 tokens 後會被截成頭尾預覽」。
- 新原因是每條帶「檔:行、訊息、指紋」,加上合成兩道原因。第 14 點的上百條告警會塞滿,中段被截,而放行只能一次一個指紋。
- file: `scripts/hooks/claude/check-graph-sync.py:935`
- 引句:「兩道都要擋時把兩段原因合成一則 decision:block,各自的名額各自記」
severity: minor
- blocking: 否

**16. 零提交的新 repo 整道不檢查**
- 實驗:新 repo 無提交,`git diff --cached --find-renames HEAD` 直接 `fatal: ambiguous argument 'HEAD'`。
- 對照:既有 `_git_status_entries` 對空倉庫回 None 就放行。
- 照 spec,工作樹模式落到環境不可用 rc0。新專案首次提交前寫的 kt 一支都不查,S5 說「未追蹤的新 kt 檔 應算新增」的前提是有 HEAD。
- 引句:「基準是 HEAD 那一版、現在版直接讀工作樹的檔」
severity: minor
- blocking: 否

**17. 「測試路徑一律排除」不全對**
- 閘用的測試判斷在 `scripts/lumos:37574`(`_PITFALL_DIFF_TEST_PAT`),實測:

| 路徑 | 被排除? |
|---|---|
| `app/src/test/…/FooTest.kt` | 是 |
| `app/src/androidTest/…/FooTest.kt` | 否 |
| `shared/src/commonTest/…` | 否 |
| `app/src/testFixtures/…` | 否 |
| `app/src/main/java/a/test/Foo.kt`(正式碼套件叫 `test`) | 是 |

- 所以 TEST 規則在 `androidTest` 本來就會響,不是「永遠不響」。S11 只驗 `src/test/`。
- 正式碼放在叫 `test` 的套件或模組(`test/src/main/…`)會被排除掃描。
- `include_test_paths` 要接在 `_lint_new_verdict` 的 `_stack_changed_ok` 呼叫處;該函式有多個消費者,spec 沒說不影響它們。
- 引句:「新增告警閘現在一律排除測試路徑(`src/test/`、`*_test.*` 這類),型錄 TEST 主題的規則因此在閘裡永遠不響」
severity: minor
- blocking: 否

**18. 規則訊息若含 `$VAR`,SARIF 會換成原始碼,超過 120 字**
- 實驗:`message: "[X-1] 不要呼叫 $F 這支;改用 B"`,`$F` 綁到一個長識別字,SARIF 的 `message.text` 長度是 153,尾巴被截。
- S2 只量規則檔裡的靜態字數。
- 草稿 208 條都沒用 `$`,所以只是 spec 沒禁。
- 引句:「新增告警閘解析 SARIF 時截在 120 字,超過的修法會被切掉」
severity: minor
- blocking: 否

**19. 一千支檔可能超出命令列長度限制(Linux 部分 ⚠)**
- 閘把 `{LINT_FILES}` 展開成同一條 `sh -c` 字串。`_lint_run_and_parse` 只有 `try/finally`,沒接 `OSError`。
- macOS:1000 支 94KB,正常;12000 支 1.1MB 時 `Errno 7 Argument list too long`。
- Linux:我沒機器可實測,`MAX_ARG_STRLEN` 是單一參數 128KB。⚠ 約 1100 支這種長度的路徑就會到。
- 推送前閘外層有 fail-open 接住(`scripts/lumos:67825`)。新的 `lint-new` 與鉤子 spec 沒寫例外怎麼處理。
- 引句:「兩種都加 `--budget 秒`」
severity: minor
- blocking: 否

**20. 資安:回合結束鉤子會自動執行打開資料夾裡的宣告命令 ⚠**
- 同一支鉤子的註解寫明「被打開的資料夾不准指使我們執行指令」,並為此收斂了 `_GIT_UNSAFE_CONFIG`。
- spec 的新道讓使用者層鉤子在每次 Stop 自動以 `shell=True` 跑任何 repo 的 `.lumos/lint.json`。
- 輸入:clone 一個不信任的 repo,`kt` 那行寫成任意 shell 命令,Claude 寫任一 kt 檔後該命令就會在收工時跑。
- spec 的資安段已明確依單人、AI 依序操作的威脅模型放行。
- 我只指出它與這支檔自己的先例相反。依威脅模型判不準是否算洞,標 ⚠。
- file: `scripts/hooks/claude/check-graph-sync.py:~808`(`_GIT_UNSAFE_CONFIG` 註解段)
- 引句:「宣告檔是專案自己進版控的,不另防」
severity: minor
- blocking: 否

## 逐節
- 用詞、分批:已讀,無 finding。數字我重算過,型錄 473 列、形狀 367、語意 106 都對,11 欄不含〈待查證〉。
- 範圍 1、5:見 8、17。
- 範圍 2:見 6、7、18。
- 範圍 3:已讀,無 finding。
- 範圍 4:見 7。
- 範圍 6:見 13、16、19。
- 範圍 7:見 1、2、14、16。
- 範圍 8:見 2、3、4、5、11、12、15、20。
- 範圍 9:見 9、10。
- 範圍 10、11:已讀,無 finding。
- 不做、裁決紀錄、批三條件、舊稿去向、實務隱患、驗收條款(S1 到 S11)、回退、天花板:已讀,條款層的缺口併在上面各條。

## 牽連節點逐條判
- `Systems/pitfalls-code-loop`:
  - L245、L247(推送前 keep-going 收尾與新增告警閘照跑):範圍 10 抽共用函式,`pass` 也呼叫,不破壞 `_fin` 的累積語意,不影響。
  - L235(`code-loop check` 預設範圍):範圍 10 說 `pass` 與它同範圍,一致,不影響。
  - L40(壓提交後留痕失效):`pass` 多一道擋下只是更早紅,不改留痕綁版本的規則,不影響。
- `Systems/棧別提問表態閘`:
  - KEY「改檔前=hook 另送的原始 delta_text,≤2 MB」:本案的 `--delta-stdin` 是平行第二條輸入,與它重複,見第 9 點。除此之外,範圍 9 不改表態判定,不影響。
- `Systems/linter精選目錄`:範圍 4 只加範本,無合約行,不影響。
- `Systems/效能檢核目錄`:本案不動,不影響。
- `Systems/graph-sync-coverage`:範圍 8 在同一支鉤子的圖譜提醒之前插新道,被第 2 點的預算與時限問題影響既有提醒。
- `Systems/改檔前推播`:PITFALL(worktree 內改檔要用該 worktree 當 repo)。範圍 9 的 `lumos impact` 呼叫要沿用 `_sibling_worktree_root` 解出的 repo,spec 沒提,不衝突但要接。

## 實務隱患類逐類
- 資安:有,第 20 點。
- 金流:無,只讀程式碼。
- 對外送出:無,全在本機。
- 不可逆:有一點,第 2 點的 `git add -A` 會把物件寫進真的 `.git/objects`,只能靠 `gc` 清。spec 寫的「退提交即回原狀」沒涵蓋這個。
- 併發:有,第 3、4、10 點(共用工作目錄、並行改檔呼叫)。
- 效能:有,第 2、19 點。1000 支檔我實測 `ast-grep` 211 條規則一次掃,Mac 約 4.9 秒牆鐘(2 核機器約 17 秒推算,未實測)。
- 相容性:有,第 7、14、19 點(ast-grep 版本、git 改名上限、Linux 命令列長度)。
- 資料遷移:無,沒有 schema 或舊資料。

總結:最高等級為 major、blocking 共 5 條(第 1、2、3、6、8 點)。
