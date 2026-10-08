severity: major

# r1 邊界席(sonnet)審查報告:治理帳例行紀錄分流_計劃

審查對象:/tmp/gov-ledger-split-r1.md。逐節讀完;5 個 [[連結]] 目標檔都存在(已查);r1-intake 已修項不重報。實驗在 /tmp/gx 的暫時 git repo 做,未動 /home/user/Lumos。

## Findings

1. 分流表自己違反自己的「繞道與自動放行痕跡留版控帳」原則
severity: major
blocking: 是 判準:中央分流表內部自相矛盾,實作者照表編碼會把人表態與繞道痕跡寫到別台機器、CI 讀不到的地方,而表上沒有一條規則能裁哪邊對。
spec 段落:〈做法〉2 分流表左欄首列與右欄
引句:「code-loop:passed、skipped、dispositions、recall-miss、skipped-env(繞過代碼審的痕跡,工具承諾「留在治理帳上」)」
引句:「note-audit:skipped、skipped-env;note-reread:reminded、covered、none、skipped、skipped-env」
問題:左欄把 code-loop 與 fix-check 的 skipped-env(人設 LUMOS_SKIP_* 繞過)留版控帳,理由是「繞道痕跡」;右欄卻把同性質的繞道全丟本機:note-shape 全部(含 LUMOS_SKIP_NOTE_SHAPE 的 skipped-env)、note-audit:skipped-env、note-reread:skipped-env、drift-check:skipped-env、bound-tests 全部(含 LUMOS_SKIP_BOUND_TESTS 的 skipped-env)。更直接的矛盾:`note-audit:skipped` 是人下 `lumos note-audit skip --note <理由>` 的主動表態(帶理由),卻放右欄,違反〈做法〉1「人或 AI 主動做的決定留在版控帳」。重現:別台機器或 CI 想查「誰用環境變數繞過了筆記形狀擋」,版控帳上只剩 code-loop 與 fix-check 的繞道,其餘查不到。判定本身不受影響(沒有判定類讀者讀這些種類),受影響的是稽核面,以及工具對使用者的承諾字樣。
佐證:file: `scripts/lumos:30927`(note-audit skipped,人表態)、`scripts/lumos:29663`(note-shape skipped-env)、`scripts/lumos:30849`(note-audit skipped-env)、`scripts/lumos:31533`(note-reread skipped-env)、`scripts/lumos:34702`(drift-check skipped-env)、`scripts/lumos:42844`(bound-tests skipped-env);對照左欄 file: `scripts/lumos:12474`(fix-check skipped-env 留版控)、`scripts/lumos:43959`(code-loop skipped-env)。使用者可見字樣:file: `scripts/lumos:44948`(「要理由、會留帳」)、file: `scripts/lumos:28915`(「單次跳過(留帳)」)。
修法方向(交編排者決定):要嘛所有 LUMOS_SKIP_* 的 skipped-env 與 note-audit:skipped 統一留左欄,要嘛在 spec 明寫為什麼 code-loop 特例而其他繞道可丟本機。

2. fail-open 優先序與「不用萬用字元」互相打架
severity: minor
blocking: 否 判準:只影響稽核痕跡落哪本,不影響任何判定;表可在實作前補一行優先序。
spec 段落:〈做法〉2 文字與表
引句:「列的是明確的「閘名+種類」,不用萬用字元;唯一例外是 check- 開頭的閘名」
問題:表裡出現至少四處萬用:左欄「各閘的 fail-open」、右欄「bound-tests 全部」「nodehome-check、note-shape、delguard 全部」「fix-check 全部」「design-loop 全部」。優先序未定義時出現衝突:`bound-tests` 的 `_gate_failopen`(kind=fail-open)同時符合左欄「各閘的 fail-open」與右欄「bound-tests 全部」。另外 `escape-auto:escape-auto-failed` 的程式註解與 docstring 都寫它是「fail-open 失敗留痕」,屬於左欄定義的「工具出錯自動放行的痕跡」,表卻放右欄。
重現:呼叫 `_gate_failopen(repo_root, "bound-tests", ...)`,表上兩條規則給出相反答案。
佐證:file: `scripts/lumos:42943`(bound-tests 走 _gate_failopen)、file: `scripts/lumos:43093`(kind="fail-open")、file: `scripts/lumos:10858`(escape-auto-failed docstring「fail-open 的失敗要看得見」)、file: `scripts/lumos:7783`(閘名註解)。

3. 「check-* 全是提醒觀察」事實錯誤:doctor --ci 會寫 hard=True 的 blocked
severity: minor
blocking: 否 判準:錯的是一句描述,路由結果(丟本機)與其他 blocked 一致,沒有判定讀者受影響。
spec 段落:〈做法〉2 表右欄首列
引句:「doctor 各段 check-*(只由 doctor --ci 寫,全是提醒觀察)」
問題:check-r 與 check-j 在 doctor --ci 寫 `kind="blocked", hard=True`(會讓 doctor 判錯、CI 紅),另有 check-j 的 shallow-skip。依字面實作,這些「硬擋」事件被當提醒丟本機,而同一份表把 anchor:blocked、nodehome-check:blocked 也丟本機,所以不是不一致,但 spec 的理由句不成立,日後有人以「全是提醒」為由往 check- 底下加硬擋閘就沒有人會發現。
佐證:file: `scripts/lumos:1908`、file: `scripts/lumos:1912`(check-r blocked hard)、file: `scripts/lumos:3394`(check-j blocked hard)、file: `scripts/lumos:5787`(check-j shallow-skip)。

4. 「同一批混兩種」例子不實;而混批時單一 try 會讓本機帳失敗吞掉後面的版控事件
severity: minor
blocking: 否 判準:今天沒有混批呼叫端,只有 spec 自己宣稱的混批情境下才失效。
spec 段落:〈盤點〉寫帳 與〈做法〉5
引句:「同一批裡可能混著兩種(例如 anchor-approve 與 design-loop 也走它)」
問題一:程式裡 anchor-approve 與 design-loop 各自是單筆呼叫(各傳一個元素的 list),doctor --ci 那批 gov_events 全是 check-*/doctor-run/ledger-growth/daily-wrapper,現況全進右欄。「混批」目前不存在,例子錯。
問題二:若依 spec 把 `_append_governance_log` 改成逐筆判,仍沿用現在的單一 `try: ... except OSError: pass`(spec 5 要求「照舊靜默」)。批內先遇到右欄事件而本機帳開不了(.git 唯讀、目錄建不起來)就 OSError,整個迴圈中止,後面該進版控帳的事件一筆不寫,而現在這些是會寫成功的。S4 只驗 `_gate_event` 那一路,這個洞沒有條款。
佐證:file: `scripts/lumos:978`、file: `scripts/lumos:23405`(單筆)、file: `scripts/lumos:3491`(doctor 批)、file: `scripts/lumos:1425`(單一 try 包住整個迴圈)。

5. 本機帳位置的三個未定義點:相對路徑、目錄不存在、巢狀 docs
severity: minor
blocking: 否 判準:S1 與 S5 的測試能抓到大部分;不抓到的是靜默寫錯位置,不影響判定。
spec 段落:〈做法〉3、〈做法〉6
引句:「共用資料夾用 `git rev-parse --git-common-dir` 取(worktree 共用同一份)」
問題:(a)該指令在非 worktree 回相對路徑,實驗:根目錄回 `.git`,子目錄回 `../.git`,只有 worktree 回絕對路徑。spec 沒說要用 `-C <repo_root>` 並對 repo_root 解析;`_gate_event(repo_root, ...)` 的 repo_root 不一定等於行程 cwd,以 cwd 解析會把檔寫進別人的 `.git/lumos/` 或在非 git 目錄建出假 `.git/` 資料夾。S5 只驗 worktree(絕對路徑)那一種,測不到這個。(b)新機器上 `.git/lumos/` 不存在,`open(...,"a")` 不會建目錄,第一筆就 ENOENT,而 spec〈回退〉暗示目錄已存在,沒寫要 mkdir;不寫會讓每台機器每筆例行事件都落到 telemetry-write-failed。(c)docs/ 存在、但 repo_root 不是該 git 專案的頂層(巢狀在別的 repo 裡)時,rev-parse 會成功找到外層 repo,本機帳落到外層 `.git`,跟〈做法〉6「取不到才退回」的二分法對不上。
佐證:實驗 /tmp/gx(子目錄 `../.git`、根 `.git`、worktree `/tmp/gx/main/.git`、submodule `/tmp/gx/main/.git/modules/msub`);file: `scripts/lumos:1358`(現行 `open(..."a")` 不建目錄,因為 docs/ 已存在);file: `scripts/lumos:1417`(既有 rev-parse 用 cwd=vault)。

6. 跨 worktree 共用單一本機帳引入新的併發寫入,沒有套用本 repo 自己的並行合約
severity: minor
blocking: 否 判準:損壞只傷本機統計(讀者跳壞行),不傷判定。
spec 段落:〈做法〉3、〈實務隱患〉相容
引句:「共用資料夾用 `git rev-parse --git-common-dir` 取(worktree 共用同一份)」
問題:現在每個 worktree 各有自己的 docs/.governance-log.jsonl,兩個 worktree 不會互寫同一檔。改成共用後,A worktree 跑 `doctor --ci`(單次 `with open(...,"a")` 寫約 500 行、遠超 8192 位元組緩衝,會在非行界切成多次 write)時,B worktree 的 hook 同時寫一行,兩者可能在行中交錯,產生壞行,並讓下一筆黏在半行後面而一起丟。repo 已有 `_ledger_append`(O_APPEND、單次 os.write、4KB 上限)這條並行合約,spec 沒提要不要沿用或為什麼不用。
佐證:file: `scripts/lumos:1427`(逐筆 f.write 的緩衝寫)、file: `scripts/lumos:18507`(`_ledger_append` 並行合約)。實測本 repo 一次提交就產生 510 行例行事件(git diff docs/.governance-log.jsonl)。

7. 「目前沒有讀者需要跨機器例行統計」不成立:`gov --stats` 的「從沒觸發的閘」與 S18 暖機守衛會變質
severity: minor
blocking: 否 判準:都是提醒或統計呈現,spec 〈天花板〉2 已承認 S18 部分,新增的是呈現層誤導。
spec 段落:〈實務隱患〉跨機器 與〈天花板〉2
引句:「跨機器的例行統計看不到(目前沒有讀者需要)」
問題:(a)`gov --stats` 印「這段時間完全沒觸發過的閘」清單,依 `_KNOWN_GATES` 對照聚合。右欄閘(drift-check、bound-tests、delguard、note-reread 等)的新事件不再進版控帳後,在全新副本、雲端工作階段、CI 上 90 天窗口過後,這些閘全會被報成「從沒觸發」,正是 `_bound_tests_log` 註解說要靠「零觸發看得見」發現的失效。(b)S18 `_slot_metric` 的暖機守衛看「讀到的最舊一筆」,兩本合併後最舊筆來自版控帳舊紀錄,守衛放行,但右欄種類的計數只剩本機帳,所以空本機帳加 `<=` 比較會成立,不是〈天花板〉2 說的「別台機器看不到才可能」,而是每個新副本必然。
佐證:file: `scripts/lumos:7859`(absent 計算)、file: `scripts/lumos:7806`(_STATS_ABSENT_DISCLAIMER)、file: `scripts/lumos:3873`、file: `scripts/lumos:3876`(暖機守衛與計數)、file: `scripts/lumos:42435`(「零觸發看得見」設計意圖)。

8. 本機帳無任何成長監看與上限,而它要接走帳的絕大部分體積
severity: minor
blocking: 否 判準:現狀就是整檔讀;只是把成長搬去沒人看的地方,不改判定。
spec 段落:〈實務隱患〉帳本成長
引句:「版控帳成長變慢;本機帳在 `.git` 裡,`git clone` 不帶,不會變成別人的負擔。」
問題:實測版控帳 19,072,097 位元組,check-*、doctor-run、delguard、nodehome-check 等右欄種類佔筆數九成以上。這些會原樣長進本機帳;但 doctor 的帳本成長段與 ledger-growth 事件只量版控帳(spec 自己寫了),本機帳沒有門檻、輪替或告警,而 `lumos gov`、spec-gate 比例段、lint-new 計數都是整檔 read 進記憶體。幾個月後每次 doctor 與 gov 讀數十 MB,且沒有任何提醒會響。
佐證:file: `scripts/lumos:2238`(只量 docs/.governance-log.jsonl)、file: `scripts/lumos:2869`、file: `scripts/lumos:25543`(整檔 read_text)、file: `scripts/lumos:8161`(gov load 整檔 read_bytes)。

9. 本機帳寫不進去時,以前會成功的寫入變成失敗,且沒有退回版控帳
severity: minor
blocking: 否 判準:telemetry 失敗不改判定,spec 已聲明;是可用性退步。
spec 段落:〈做法〉5
引句:「走 `_gate_event` 的回 False,呼叫端照舊講 telemetry-write-failed」
問題:.git 唯讀掛載、而工作樹可寫(容器與沙箱常見),以前 docs/ 可寫就寫成功;分流後所有右欄事件(包含 hard=True 的 code-loop:blocked、canary:blocked,`_gate_event` docstring 承諾「擋人時一定有帳」)每一筆都吐 telemetry-write-failed 並丟失。〈做法〉6 只對「取不到共用資料夾」退回版控帳,對「取到但寫失敗」沒退回,兩者在使用者看來是同一個唯讀環境的兩種表現。
佐證:file: `scripts/lumos:1358`(現行寫 docs/)、file: `scripts/lumos:1394`(telemetry-write-failed 路徑)。

10. 讀者清單兩處與程式對不上
severity: minor
blocking: 否 判準:清單描述不準,不影響實作結果,但會讓 S3 測試對象選錯。
spec 段落:〈做法〉4
引句:「統計類讀者(`lumos gov`、doctor 的 spec-gate 比例段、S18 度量、lint-new 自動放行計數)改用同一支「兩本一起讀」的小工具」
問題:(a)lint-new 自動放行計數只數 `gate=lint-new, kind=fail-open`(左欄,留版控帳),改成兩本合讀沒有任何新增資料,卻被列為需改讀者,會讓實作者白改。(b)「週回放」被列為只讀版控帳的判定類讀者,但在 scripts/lumos 找不到有哪支週回放讀 `.governance-log.jsonl`;`scripts/lumos:2231` 的註解自己說判定回放讀的是 `.canary-log.jsonl`。⚠ 交編排者:週回放是否另在 wrapper 腳本(repo 外)讀這本帳,我這邊查不到;若有,應列路徑。
佐證:file: `scripts/lumos:25555`(只認 lint-new fail-open)、file: `scripts/lumos:2226`、file: `scripts/lumos:2231`。

## 逐節結論
- frontmatter/summary:已讀,無 finding(連結 5/5 存在)。
- 白話與依據:已讀,無 finding。
- 〈盤點〉:finding 4、10。
- 〈範圍〉:已讀,無 finding。
- 〈做法〉1:finding 1(原則被表違反)。
- 〈做法〉2 分流表:finding 1、2、3。
- 〈做法〉3:finding 5、6。
- 〈做法〉4:finding 7、10。
- 〈做法〉5:finding 4、9。
- 〈做法〉6:finding 5、9。
- 〈實務隱患〉:finding 7、8。
- 〈驗收條款〉S1–S5:S1 版控帳「一個位元組都不變」我用本 repo 實際 diff 核過,一次提交的事件種類(check-*、delguard:ok、nodehome-check:passed、ledger-growth、doctor-run、spec-gate-run、bound-tests:green、drift-check:passed、note-reread:reminded、note-shape:hinted)全在右欄,成立;缺的條款見 finding 4(混批加本機失敗)、5(相對路徑)。
- 〈回退〉、〈天花板〉:已讀,無 finding(天花板 2 的缺口見 finding 7)。

## 實務隱患逐類(邊界席視角)
- 空帳/第一次寫(檔不存在):檔不存在 `open("a")` 會建,但 `.git/lumos/` 目錄不存在,finding 5(b)。
- 不在 git/裸倉庫/.git 是檔/子模組/worktree:實驗證實 rev-parse 在 worktree 回絕對路徑、子模組回 `.git/modules/<名>` 絕對路徑、非 worktree 回相對路徑;裸倉庫與無 git 的 docs/ 退回邏輯 spec 已有,但相對路徑解析與巢狀 repo 見 finding 5。
- 唯讀磁碟:finding 9、finding 4。
- 事件批次混兩種:finding 4。
- 超長一行:右欄事件走 `_gate_event_build` 與 `_gate_event_fit`,4096 位元組上限是 `_ledger_append` 的規則,`_gate_event` 本身沒有此上限;分流只換檔案不換組行邏輯,無新風險,無。
- 剛好卡在界線上(分流表邊界):finding 1、2。
- 併發/多 worktree:finding 6。
- 金流/對外送出/不可逆:spec 已排除,我同意(只本機追加、不聯網),無。
- 資安:本機帳在 `.git/` 內,內容與版控帳同形(本來就是 repo 內資料),無新增機密面,無。
- CI:CI 乾淨副本讀代碼審留痕只靠左欄,我核過 `_codeloop_read_from_ledger` 與 `_codeloop_read_dispositions` 只讀 passed/skipped/dispositions,無 finding;`ci.yml` 與 hooks 沒有直接讀這本帳。

總結:最嚴重 severity 為 major,blocking 共 1 條(finding 1);其餘 9 條皆 minor、blocking 否。
