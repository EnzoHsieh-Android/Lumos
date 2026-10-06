severity: major

審查範圍:r3-snapshot.md 全文。實測在本機唯讀量(未改 repo,未用暫存區):seat-guard 這個 worktree 的 `git status --porcelain=v1 -z --untracked-files=all` 0.39 秒、164 位元組(只有 3 個條目);主 checkout `/Users/enzo/harness/lumos-toolchain` 同指令 0.12 秒、160 個條目(11900 位元組);`git for-each-ref` 45 行;`git worktree list --porcelain` 68 行(17 個 worktree);五支 git 合計約 1 秒。結論:單次耗時不是問題,問題在「檢查對象與觸發面」。

### F1 事後查的基準照字面讀 `.git/config`、`.git/hooks/`,但本 repo 慣例的 worktree 裡 `.git` 是一個檔,不是資料夾
severity: major
blocking: 是 — 使用者全域規則要求每個任務開獨立 worktree,審查席常在 worktree 裡跑;照字面實作在這種 repo 上基準讀取會直接失敗,事後查整個失效
引句:「`.git/config`、`.git/hooks/` 底下每個檔的大小與修改時間」
- 實測:`/Users/enzo/harness/lumos-toolchain-seat-guard/.git` 是 86 位元組的檔(內容 `gitdir: …/.git/worktrees/lumos-toolchain-seat-guard`),`git rev-parse --git-common-dir` 指到主 checkout 的 `.git`。輸入:在這個 worktree 登記審查席 → 預期:讀 `<repo根>/.git/config` 得到 ENOTDIR。
- 快照只規定「git 失敗 → 基準記成拿不到」,對 `$.fs` 讀檔失敗沒寫。若當成外掛內部錯誤,第 6 點是放行(整個事後查沒做);若當成拿不到,則這個 repo 上每一席答完都附「事後查沒做成」,警告變噪音。兩種都不對。
- 修法:路徑改用 `git rev-parse --git-common-dir` 與 `--git-dir`(config 與 hooks 在 common dir;worktree 自己的 HEAD、index 在 git-dir),並把 `core.hooksPath` 指到的資料夾(本 repo 的 `git config core.hooksPath` 是 `/Users/enzo/harness/lumos-toolchain/scripts/hooks`,真正的掛鉤在那裡,`.git/hooks/` 底下只有 `.sample`)也納入;只看 `.git/hooks/` 對本 repo 等於看著 15 個沒用的範本檔。
- 要附一條先紅的 S13 測試:repo 是 `git worktree add` 出來的、`.git` 是檔,基準應成功、改 common dir 的 config 應被報。
file: `/Users/enzo/harness/lumos-toolchain/.git/config:mtime Oct 6 10:07`(今天就有別的會談改過)
file: `/Users/enzo/harness/lumos-toolchain/.git/hooks`(只有 `.sample`)

### F2 基準的 repo 取自會談 cwd,不是審查席實際工作的 repo;兩者不同時事後查看錯地方
severity: major
blocking: 是 — 本 repo 的標準做法就是「會談在主 checkout、審查在獨立 worktree 或 clone」,事後查對真正被審的那個樹完全沒看
引句:「在會談 cwd 跑 `git rev-parse --show-toplevel` 找 repo 根」
- 同節〈做法〉一已把「工作目錄(輸入的 `cwd`)」登記進表,但基準這一條只說會談 cwd,兩處沒對上。輸入:編排者會談 cwd=`/Users/enzo/harness/lumos-toolchain`,派工 `cwd=/Users/enzo/harness/lumos-toolchain-seat-guard` → 預期:守這個 worktree;字面:守主 checkout,席位改 worktree 的檔查不到,反而把主 checkout 上別人的改動報成這席的。
- 實際就是這次審查的形狀(本會談 cwd 是主 checkout,材料在 seat-guard worktree)。
- 修法:基準的 repo 根從派工 `cwd` 解,沒給才用會談 cwd;並寫明審查席 Bash 內 `cd` 到別的 repo 看不到(已在誠實界線,但這條要連到這裡)。

### F3 `git status` 預設會拿索引鎖,五支 git 沒帶 `--no-optional-locks`,同時多席答完會讓編排者與別的會談的 git 偶發失敗
severity: major
blocking: 是 — 外掛在別人的 repo 上做讀取卻能讓別人的寫入失敗,等於把隔離的副作用打到合法工作上
引句:「每支 git 都用 `$.process.run`、帶 `-c core.fsmonitor=false`、逾時 10 秒」
- `git status` 為了刷新索引會嘗試寫 `.git/index`(取 `index.lock`),`git -c core.fsmonitor=false` 不阻止這件事。四、五席幾乎同時答完 → 外掛同時跑多個 `git status`;編排者此刻若跑 `git add`/`git commit`(收貨後記帳、`lumos canary record` 之後提交),會偶發 `fatal: Unable to create '.../index.lock': File exists`。使用者全域規則特別寫過「同一個 repo 可能同時有別的會談在做事」,本 repo 17 個 worktree 的真實情況就是如此。
- 修法:`git --no-optional-locks status …`(或環境變數 `GIT_OPTIONAL_LOCKS=0`),並把同一 repo 的事後查序列化(同 repo 一次一支),避免 N 席各跑五支。
- 條款 S13 沒有覆蓋這點;建議補一條:事後查期間編排者的 `git add` 不得因外掛而失敗。

### F4 「登記」含最多 5 支各 10 秒的 git,但 `tool.call` 只等登記 5 秒;大 repo 上審查席在基準做完前不受保護,而且基準取在席位已啟動之後
severity: major
blocking: 是 — 保護窗口與保護範圍倚賴的兩個數字(5 秒、10 秒)自相矛盾,慢 repo 上整席退成放行
引句:「最多等 5 秒讓它們回報完再查表」
引句:「拿到結果的 `agentId` 就登記」
- 登記動作包含取基準(〈做法〉三:「登記審查席(〈做法〉一)時…記下」),基準是五支 git 加讀設定檔,每支上限 10 秒,總上限 50 秒。同一會談的審查席子代理在登記完成前呼叫工具,tool.call 只等 5 秒,逾時放行並跳 toast。輸入:大 repo(`git status` 要 6 秒以上)派一席 → 預期:該席工具仍被擋;字面:5 秒逾時、放行、整席沒有隔離(只剩一個 toast)。本 repo 1 秒內過,所以 S14 在暫存小 repo 上永遠測不到。
- 登記在 `next(e)` 回來之後才做,席位那時已啟動;席位在基準完成前做的改動被吸進基準,事後查報不出來(窗口=基準耗時)。
- 修法:登記表項(席位身分)與取基準分兩步;身分先寫入、tool.call 只等身分;基準非同步補上,補完前的事後查報「基準尚未取得」而不是放行。
- 同族:同時 N 席各自取基準,同一 repo 同時 5N 支 git(見 F3)。

### F5 共用的 refs、worktree 清單、設定檔,加上自動寫手,讓事後查警告在本 repo 幾乎每次都會報
severity: major
blocking: 是 — 警告的訊號價值取決於誤報率;本 repo 實測的背景變動頻率足以讓每席每次答完都附警告,編排者很快學會忽略,事後查等於關掉
引句:「不一樣 → 在 `next(e)` 回來的 `text` 後面附一段固定開頭」
- `git for-each-ref` 與 `git worktree list --porcelain` 看的是整個物件庫(所有 worktree 共用):本 repo 45 個 ref、17 個 worktree,別的會談在別的 worktree 提交、開分支、fetch,都會讓「分支」與「worktree」類報變動,跟這席毫無關係。
- 主 checkout 的 `git status` 有自動寫手:實測今天 `governance/nags-last-week.txt`(09:59)、`governance/scenarios/history.jsonl`(09:59)、`governance/replay/.weekly-stamp`(10:04)都被改過,`.git/config` 10:07 被改過;`lumos canary record`、`lumos loop` 這些收貨指令寫 `docs/.governance-log.jsonl` 等追蹤檔(seat-guard worktree 目前就有一筆 ` M docs/.governance-log.jsonl`)。審查席執行期間編排者收別席貨時一定會動這些檔 → 先答完的席的警告無關,後答完的席必然報。
- `~/.claude/settings.json`(45117 位元組)是 Claude Code 自己會改寫的檔(權限「永遠允許」等),放進指紋會在長會談中誤報。
- 修法:把「檔案狀態」的比對限縮到審查席的相關範圍(例如排除 `governance/` 帳檔、`docs/.*.jsonl`、`governance/runtime/`),或把 repo 全域的 refs/worktree 從 per-seat 警告改成只在 `git for-each-ref` 中該席派工時持有的那條分支變動時報;寫明誤報率的量測口徑,讓 REVISIT 2026-11-06 有數字可比。

### F6 Bash 粗擋的誤擋面:審查本 repo 時最常見的 `git … push` 字樣搜尋全被擋,而教的替代寫法有一半同樣被擋
severity: minor
blocking: 否 — 誤擋的代價是換工具重試,而且決策 d3 已明示「寧可誤擋」
引句:「有詞 `git`,同時有詞 `push` 或 `send-email`。」
- 我用快照的切詞規則(以 `A-Z a-z 0-9 _ . -` 以外的字元為界)跑了真實審查員會下的指令:
  - 擋(誤):`git log --oneline --grep=push -5`、`git grep -n 'push' -- scripts/hooks`、`grep -rn 'git push' docs/lumos-toolchain-knowledge/Systems | head`、`python3.14 scripts/test_lumos.py -k push; git status`、`git diff main...HEAD -- scripts/lumos | grep -n push`、`git ls-files | grep -i push`、`grep -n 'gh ' scripts/lumos`。
  - 放(正確):`git -C /repo log -- scripts/hooks/pre-push`(`pre-push` 因為 `-` 在詞內不是詞 `push`)、`cat .git/hooks/pre-push`。
- 本 repo 的主題就是推送閘(pre-push 掛鉤、`push` 測試名、CI 閘),審查員要搜尋「push」是正常工作;理由文字教的「換寫法」若是 `grep -rn 'git push'`,那條也被擋(字串同時含 `git` 與 `push`)。實際可行的換法只有 `Grep` 工具或 `git` 與 `push` 拆成兩條指令,快照沒寫。建議理由文字直接說「用 `Grep` 工具搜尋」。
- 另有一個放行面(不是誤擋):`scripts/lumos` 裡有 `subprocess.run(["gh"]…)`,`lumos ci-wait` 之類子指令內部會呼叫 `gh`,指令字串裡沒有詞 `gh`,審查席可經 lumos 間接跑 gh;目前那幾個呼叫是唯讀的 `run view`,所以只記為提醒。
file: `scripts/lumos:39799`(`_ci_gh`)

### F7 事後查看不到「已經是髒的檔」被改,而本 repo 的主 checkout 隨時都有髒檔
severity: minor
blocking: 否 — 屬於〈做法〉三字面範圍內的盲區,不違反條款文字,是量測口徑的缺口
引句:「`git status --porcelain=v1 -z --untracked-files=all` 的輸出」
- 主 checkout 實測有 160 個條目(5 個 ` M`、其餘 `??`)。審查席把已是 ` M` 的 `governance/nags-last-week.txt` 再改一次,porcelain 輸出一個字都不變;已是 `??` 的未追蹤檔被改內容也一樣。輸入:髒 repo + 席位用 Bash 追加內容到已修改檔 → 預期:報變動;字面:不報。S14 用乾淨暫存 repo,測不到。
- 建議:基準加上 `git diff --no-ext-diff` 的雜湊或對 porcelain 列出的前 N 個檔取大小與修改時間;或在誠實界線加一句「repo 本來就髒時,改已髒的檔看不到」。

### F8 警告只靠回答文字與 toast;自主迴圈或 `claude -p` 沒有介面時警告可能無人看見
severity: minor
blocking: 否 — 快照已在誠實界線與 REVISIT 自承,這裡只補實作面
引句:「引擎說非主迴圈的 `turn.complete` 文字「顯示在回答下方」」(此句內有「」,改取:引擎說非主迴圈的 `turn.complete` 文字)
- 型別檔 `TurnCompleteResult`:「a text other than a main-loop answer's is shown beneath it」,只保證「顯示」,沒保證併入 Agent 工具回給編排者的結果。無人看顧的 `claude -p`、cron 起的迴圈沒有 toast 介面。
- 建議:事後查有變動時除了附文字,也寫一筆事件帳(`governance/runtime/events/` 已是外掛的既有輸出),這樣收貨時 `lumos events` 查得到,不依賴 S14 的實測結果。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:12695`

### 前輪修復驗收
對 r2 邊界席(F1–F11):
- r2 F1(輪次格式太窄且不合格靜默放行):已修。〈做法〉一改成輪次不限格式(`r3-dref`、`驗收` 列為合格例),第一行以 `LUMOS-SEAT` 開頭卻不合格改成擋下派工;BOM 與全形空白行(trim 後為空)與全形冒號都寫明。
- r2 F2(卷證路徑與迴圈編號對不上、repo 根未定):已修(消失)。卷證資料夾不再保護(名詞節:「卷證資料夾不保護」),只保護席報告暫存處,路徑不再倚賴迴圈編號。
- r2 F3(同輪席報告檔名判定):已修(消失),同上。
- r2 F4(暫存區放行讓 repo 在暫存區時保護全關):已修。寫檔只准席位工作資料夾(暫存根/`lumos-seat-work/<迴圈>/<席名>/`);S14 也改成暫存 repo 建在家目錄下。
- r2 F5(斷詞失敗配 fail-open):已修。不再斷詞;Bash 判斷出錯與超過 1MB 明列為 fail-closed,是第 6 點的例外。
- r2 F6(`bash -lc`、stdin、腳本檔繞過):部分。`bash -lc`、`<<<`、heredoc、子殼層因為改成對整串字串的詞掃描全被涵蓋;「先 Write 腳本再 `bash` 執行」仍擋不到,已寫進誠實界線(「先寫腳本再執行(腳本內容不掃)」),屬接受的風險。
- r2 F7(暫存區內的 git 子指令全放行):已修(轉形)。`git … push` 在任何目錄都被詞規則擋;`remote add`、`commit` 等改狀態動作不事前擋,改由事後查報告,但事後查有 F1、F2、F5、F7 這些缺口。
- r2 F8(唯讀 git 白名單旗標誤擋):已修(消失)。不再解析旗標;新的誤擋面是 F6(整串詞掃描),性質不同。
- r2 F9(席報告暫存處前綴比對、迴圈編號 `..`、祖先目錄搜尋):已修。名詞節「比對一律帶路徑分隔字元」、標記各段不得為 `.`/`..`、含 `\`、空白與控制字元;Grep/Glob 改為祖孫關係判定(`path=/private/tmp` 明列為擋)。
- r2 F10(逾時沒留痕、等整批):部分。逾時放行現在要 `$.ui.toast` 固定開頭字串,但仍只有 toast、沒有事件帳,且仍等整批(快照在效能與併發節承認 5 秒上限)。另見本輪 F4:登記含基準時,5 秒不夠用。
- r2 F11(相對路徑只以會談 cwd 解):部分。`Write`/`Edit` 要求絕對路徑,對寫檔已無影響;`Grep`/`Glob` 相對路徑與 Bash `cd` 後的目錄看不到,已寫進誠實界線(「子代理在 Bash 裡 `cd` 之後的工作目錄外掛看不到」);相對 `path` 仍只以派工時的工作目錄補全,接受。

總結:最嚴重 major,blocking 5 條
