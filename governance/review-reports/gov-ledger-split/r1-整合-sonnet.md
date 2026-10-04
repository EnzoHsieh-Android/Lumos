severity: major

# 治理帳例行紀錄分流_計劃 r1 外部審稿(整合席 sonnet)

立場:三個月後接手的人。逐節讀完,spec 內 5 個 [[連結]] 與 lands_in 目標存在(intake 已查,不重報)。

## Findings

1. 動機達不到:別本進版控的帳照樣讓工作目錄髒,S1 只量治理帳所以測不出來
severity: major
blocking: 是 — 〈白話〉宣稱的目標(平常提交推送完工作目錄乾淨、雲端工作階段不再被打斷)不會達成,屬於設計前提不成立。
spec 段落:白話、〈範圍〉、〈驗收條款〉S1
引句:「平常提交推送完工作目錄就是乾淨的」
問題:本 repo 進版控的帳不只治理帳。`git ls-files docs` 實列 `docs/.bypass-log.jsonl`、`.canary-log.jsonl`、`.escape-log.jsonl`、`.kill-log.jsonl`、`.signoff-log.jsonl`、`.usage-log.jsonl` 都在版控內;審稿當下 `git status` 就是 ` M docs/.canary-log.jsonl` 加 ` M docs/.governance-log.jsonl` 兩檔。`.usage-log.jsonl` 每次 `context`/`show` 都寫,`.bypass-log.jsonl` 每次繞過提交由 post-commit 寫,`.canary-log.jsonl` 每輪審查記帳寫。這幾本都不在本案範圍,spec 沒提。分流後治理帳安靜了,工作目錄仍會因它們而髒,「雲端每回合被打斷」不會消失。S1 只斷言「版控帳一個位元組都不變」,不是斷言「git status 乾淨」,所以驗收綠了、動機仍紅。REVISIT:2026-12-01 的「被打斷次數」會顯示沒改善,但那是 8 週後。
佐證:file: `scripts/lumos:24193`(`_BOOKKEEPING_FILES` 列出八本進版控的簿記檔,本身就承認它們會被提交);file: `scripts/hooks/post-commit:93`(`BYPASS_LOG` 寫 docs/.bypass-log.jsonl);`git ls-files docs` 與 `git status --short` 實跑結果如上。

2. 「check- 開頭全是提醒觀察」與程式不符:有硬擋事件(hard=True)被分到本機帳
severity: major
blocking: 是 — 表的判準句寫錯,照它實作會把 doctor --ci 的硬擋紀錄移出版控帳,與本案「不讓判定相關痕跡消失」的立場及 #19 擋人必留帳的承諾相衝。
spec 段落:〈做法〉2 分流表第一列右欄
引句:「doctor 各段 check-*(只由 doctor --ci 寫,全是提醒觀察)」
問題:doctor --ci 寫的 check-* 事件裡有 kind=blocked、hard=True。`check-r` 在 IRREVERSIBLE 缺回退、標錯型別時寫 blocked/hard;`check-j` 在重建筆記主張沒標出處時寫 blocked/hard。這些是「doctor --ci 會 rc1 擋推送」的事件,不是提醒。分流表用「check- 開頭」一刀切,這些硬擋紀錄會進本機帳;`lumos gov` 的「硬擋/軟」分欄與 #19 的「擋了幾次」可觀測性從此只看得到這台機器的硬擋。spec 自己的 PRIOR 與〈守衛面〉主張「繞道與自動放行的痕跡」留版控,硬擋同理應留。另外,同一句也與〈做法〉2 自己的規矩衝突:「列的是明確的『閘名+種類』,不用萬用字元」,而 check-* 正是萬用字元(`_KNOWN_GATES` 內有 check-r/j/k/s…s16/e1-e3/p2/lint-decl 等二十多個,還有 `check-p2s` 這種不在 `_KNOWN_GATES` 的閘名由 doctor 直接寫)。
佐證:file: `scripts/lumos:1908`、`scripts/lumos:1912`(check-r blocked hard=True);file: `scripts/lumos:3394`(check-j blocked hard=True);file: `scripts/lumos:3224`(check-p2s 不在 `_KNOWN_GATES` 名單,見 `scripts/lumos:7771-7800`)。

3. fail-open 在表裡左右兩欄互相矛盾,優先序沒定義
severity: minor
blocking: 否 — 實作時選哪邊都不會讓任何閘從擋變放,但會讓「繞道痕跡留版控」這條原則在 bound-tests 等閘上悄悄失效。
spec 段落:〈做法〉2 分流表左欄末列與右欄 bound-tests / delguard / note-shape / nodehome-check
引句:「各閘的 fail-open(工具出錯自動放行的痕跡)」
問題:左欄說「各閘」的 fail-open 都留版控;右欄同時寫「bound-tests 全部」「delguard 全部」「note-shape、delguard 全部」「nodehome-check」。`_gate_failopen` 對任一閘名寫的 kind 都是字面 `fail-open`(`bound-tests` 就有四個 fail-open 情境、`lint-new` 也走它)。`bound-tests` + `fail-open` 同時命中左右兩欄,spec 沒說誰贏;表是以「閘名+種類」逐項列,而 fail-open 是「任何閘名+固定種類」,資料結構(一個常數)沒說怎麼表達這條跨閘規則。
佐證:file: `scripts/lumos:43083-43095`(`_gate_failopen` 固定 kind=fail-open);file: `scripts/lumos:42943`(bound-tests 走 `_gate_failopen`);file: `scripts/lumos:43867`、`scripts/lumos:43874`(lint-new 走它)。

4. 既有測試會變紅,spec 沒有逐條改測試的清單
severity: major
blocking: 是 — 三條 CLAUDE.md 鐵則(改完跑相關測試、全套是推送前閘)下,spec 沒盤點要改的既有測試,實作一定先紅一批;規模不是「補五條新測試」。
spec 段落:〈驗收條款〉(只列 S1-S5 新測試)、〈盤點〉
引句:「分流發生在四支直接寫帳的函式決定路徑那一步」
問題:凡是在真 git repo 裡斷言「右欄種類出現在 `docs/.governance-log.jsonl`」的既有測試,分流後讀不到。逐條核對:
 - check-r:`test_lumos.py:5954-5955` 斷言 `--ci` 後治理帳含 `check-r`;`6045` 的 `gov <node>` 命中 governance-log 事件。
 - check-cascade:`test_lumos.py:23716-23719`。
 - check-revisit:`test_lumos.py:35919-35923` 讀 `gate == "check-revisit"`。
 - delguard:`test_lumos.py:38270-38273` 斷言治理帳有 `delguard`/`ok` 一筆。
 - bound-tests:`test_lumos.py:8907-8914`、`8930-8938`、`8972-8973`、`39902-39906`(讀 gate=bound-tests 的 kind/hard)。
 - canary blocked:`test_lumos.py:34108-34110`(三筆 report-not-normalized blocked 必在 `.governance-log.jsonl`)、`34151-34152`(refuted-set-missing)。
 - anchor blocked 寫不進去:`test_lumos.py:40025-40033` 把治理帳 chmod 444 後期望 `anchor verify` 的 stderr 講寫不進去;anchor:blocked 改寫本機帳之後,版控帳唯讀不再影響它,這條「寫不進去仍要擋、仍要明講」的釘子斷言對象變了(S4 只新增一條 `_gate_event` 本機帳失敗測試,沒說這條舊釘子怎麼辦)。
非 git 的臨時目錄會退回版控帳而繼續綠,所以真正紅的是 `git init` 過的沙箱;紅的數量與位置要在計劃裡列表,否則實作者會把「紅」當成回歸去修分流表。
佐證:上列 `scripts/test_lumos.py` 各行號(逐行讀過)。

5. 讀者清單漏了 `lumos gov --nags`(14 天空轉升級鏈),而它吃的正是右欄種類
severity: minor
blocking: 否 — 同一台機器上經 cmd_gov 合併讀仍正確,只在換機器/重新 clone 後失效,屬天花板類而非立即回歸。
spec 段落:〈做法〉4、〈天花板〉2
引句:「跨機器的例行統計看不到。」
問題:`_render_gov_nags` 用 `doctor-run`(右欄)判「最近一次 doctor 體檢是哪天」,用 `kind=warned` 的 check-* 與 daily-wrapper(右欄)判「同一道軟閘對同一篇筆記跨 ≥14 天還在喊」,rc1 時 `governance/autonomous-loop.sh` 的 `run_nags` 發 LINE。這是有行為後果的讀者,不是純統計,spec 的〈盤點〉與〈做法〉4 都沒點名;〈做法〉4 只在「`lumos gov`」底下含糊帶到。本機帳在 `.git/lumos/`,重新 clone、換機器、刪工作副本都會讓「第一次提醒」的時間歸零,14 天升級鏈重新計時而且無聲。〈天花板〉2 說跨機器統計「目前沒有讀者需要」與此不符;`run_nags` 還對另一個 repo(`LandmarkMember`)同樣跑一次。
佐證:file: `scripts/lumos:8044-8062`(`_render_gov_nags` 讀 doctor-run 與 warned);file: `governance/autonomous-loop.sh:403-416`、`governance/autonomous-loop.sh:468-471`(`run_nags` 與兩個 repo);file: `governance/daily-governance.sh:258`(doctor --ci 為了讓 nags 有帳可讀才跑)。

6. 本機帳位置與建立的細節沒定義:`.git/lumos/` 目錄誰建、相對路徑怎麼解、無人看管成長
severity: minor
blocking: 否 — 都是實作可補的缺口,但缺了會造成「靜默丟紀錄」的第一手行為。
spec 段落:〈做法〉3、5
引句:「共用資料夾用 `git rev-parse --git-common-dir` 取(worktree 共用同一份)」
問題:(a) `git rev-parse --git-common-dir` 在主工作樹印的是相對路徑(`.git`),要相對於呼叫時的 cwd 解;`_append_governance_log` 現有的 git 呼叫是 `cwd=str(vault)`,`_gate_event` 是 `git -C root`,兩支要用同一種解法,spec 沒講。(b) `.git/lumos/` 不存在,誰 mkdir 沒寫。`_gate_event` 沒建目錄會每次回 False,於是每次提交、推送都喊 telemetry-write-failed,把「只吵一點」變成日常噪音;`_append_governance_log` 本來就 `except OSError: pass`,沒建目錄就是永遠靜默丟掉全部例行紀錄,而 spec 的〈做法〉5 說「判定不受影響」,沒人會發現。(c) 版控帳有 doctor ledger-growth(5 MB 上限、成長倍數)看守,本機帳沒有任何大小看守,〈實務隱患〉「帳本成長」只說版控帳變慢。
佐證:file: `scripts/lumos:1414-1431`(`_append_governance_log` 吞 OSError、git 呼叫用 `cwd=vault`);file: `scripts/lumos:1356-1362`(`_gate_event` 寫入);file: `scripts/lumos:2235-2290`(成長段只量版控帳那個檔)。

7. 圖譜與手冊會說錯話:reversibility-governance-ledger 的來源計數、唯一寫者、帳檔都進版控
severity: minor
blocking: 否 — 屬 lands_in 本來就要改的同步項,但 spec 沒列要改哪幾句,三個月後必然漏。
spec 段落:front matter `lands_in`、〈做法〉4
引句:「統計類讀者(`lumos gov`、doctor 的 spec-gate 比例段、S18 度量、lint-new 自動放行計數)改用同一支「兩本一起讀」的小工具」
問題:`Systems/reversibility-governance-ledger` 目前寫:(a) KEY「gov 彙整多本帳(6 源 `<!--lumos:count=6 re=(?m)^\s+load\((?:\"\.|CI_LOG_NAME)`-->」——程式現有六個 `load(".…")`/`load(CI_LOG_NAME…)`,正是 6;若本機帳實作成第七個 `load(".governance-local…")` 這條 count 標記就翻紅(Check N),要在計劃裡寫死「合併在 `.governance-log.jsonl` 那個 load 內、不新增 load 呼叫」或同步改 count;(b) KEY「lumos gov 唯讀彙整器,不合併寫入路徑…六來源」與 decisions d3「doctor 是唯一新寫者」(程式早有多個寫者,本案再加一個「分流寫者」);(c) 「帳檔已被追蹤,非 gitignore」(`reversibility-governance-ledger.md:31,103`)——分流後治理帳「部分」被追蹤。另外 `skills/lumos-project-notes/reference.md:61` 「唯讀彙整 bypass/rot/governance-log」沒提本機帳;`scripts/lumos:10336` 的提示 `git diff HEAD~1 -- docs/.canary-log.jsonl docs/.governance-log.jsonl` 在 canary:blocked 改寫本機後,指不到全部壞行來源。`_gate_event` 的 docstring(`scripts/lumos:1310-1332`)也說「既有的寫入器是 except OSError: pass」,分流後敘述要補。
佐證:file: `docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:30`、`:31`、`:54-59`(d3)、`:103`;file: `scripts/lumos:8158-8216`(六個 load 呼叫);file: `skills/lumos-project-notes/reference.md:61`;file: `scripts/lumos:10336`。

8. lint-new 自動放行計數列為「改成兩本讀」,但它唯一讀的種類留在左欄,改動空轉
severity: minor
blocking: 否 — 多寫一支沒作用的合併讀取,不影響判定,只是 spec 與表自相矛盾。
spec 段落:〈做法〉4 與分流表
引句:「統計類讀者(`lumos gov`、doctor 的 spec-gate 比例段、S18 度量、lint-new 自動放行計數)」
問題:`_lint_new_autopass_count` 只數 `gate=lint-new` 且 `kind=fail-open`;fail-open 在表裡留左欄(版控帳),所以它讀版控帳就完整,不需要改成兩本讀。要嘛從清單移除(少改一處),要嘛承認表會讓 lint-new 其他種類分流(spec 沒列 lint-new 其他種類,只有 `waived`)。
佐證:file: `scripts/lumos:25535-25560`(只數 `lint-new` / `fail-open`)。

## 逐節結論

- front matter / 白話 / 依據 / PRIOR-ART / RETIRE-IF / REVISIT:見 finding 1(動機)。PRIOR-ART 說「沿用 `.git/` 慣例」:`git-common-dir` 在 `scripts/lumos` 目前零處使用(`grep` 為空),不是沿用既有 helper,是新增,但不構成缺陷。
- 〈盤點〉:四支直接寫帳函式與包裝關係核對屬實(`scripts/lumos:978`、`:1310`、`:1410`、`:42412`、`:43239`、`:42447`、`:43083`)。「讀帳十來處」未點名 `--nags`(finding 5)。
- 〈範圍〉:已讀,「不推翻 #18 不分檔」屬實(`scripts/lumos:2226` 四個整檔讀者);無 finding。
- 〈做法〉1:已讀,無 finding。
- 〈做法〉2:finding 2、3、8。
- 〈做法〉3:finding 6。
- 〈做法〉4:finding 5、7、8。
- 〈做法〉5、6:與 `scripts/lumos:1417-1424`、`:1323` 現況一致;缺口見 finding 6。
- 〈實務隱患〉:逐類答覆如下。
  - 守衛面:文字論證成立(判定讀者全在左欄,`_codeloop_read_from_ledger` 只認 passed/skipped,`scripts/lumos:42310-42335`),唯獨 finding 2 的硬擋事件被誤放右欄。
  - 並行/競態:無新風險;本機帳與版控帳一樣是單行 append,沒有 read-modify-write(多行寫入在 `_append_governance_log` 同一 open 內,與現況相同)。
  - 相容(消費專案):`lumos update` 後舊紀錄留版控帳,讀者兩本讀,消費專案不用改 `.gitignore`——屬實;消費專案的 CI 讀的是左欄,不受影響。需注意消費專案釘住舊版 lumos 時,舊版讀者不讀本機帳,其 `lumos gov` 會少一截例行紀錄,只影響統計,不改判定。無獨立 finding。
  - 金流/對外送出:無——只寫本機檔、不呼叫網路。
  - 不可逆:無——兩本帳只追加,還原提交回原行為;但還原後本機帳內的紀錄不再被任何讀者讀(spec 已說「不影響判定」),屬實。
  - 資安/權限:無新增——`.git/lumos/` 與 `.git` 同權限;紀錄內容與原先相同。
- 〈驗收條款〉:S1 的斷言對象與動機脫鉤(finding 1);S4 沒涵蓋舊釘子(finding 4);S2、S3、S5 已讀,無 finding。
- 〈回退〉:已讀,無 finding。
- 〈天花板〉:第 2 點與 finding 5 衝突(漏了 nags);第 1、3 點已讀,無 finding。

最嚴重 severity: major;blocking 條數:3(finding 1、2、4)。
