severity: major

## F1 回退主路徑 git revert 會在共用帳本檔上衝突,spec 沒寫怎麼處理
severity: major
blocking: 是
引句:「主要路徑是 `git revert` 那個功能提交(程式、筆記、測試同一個提交)」
file: `governance/anchor-baseline.json`、`docs/.governance-log.jsonl`、`docs/.canary-log.jsonl`、`scripts/lumos:17870`
1. 本 repo 的功能提交一律夾帶共用簿記檔(前一個同形狀的功能提交 02ea9745 就含 docs/.governance-log.jsonl、.canary-log.jsonl、.escape-log.jsonl、governance/anchor-baseline.json,共 60 支檔)。這份功能提交照專案慣例也會含這幾本帳。
2. 我在 --shared clone 對 02ea9745 實跑 `git revert --no-commit`:docs/.canary-log.jsonl、docs/.governance-log.jsonl 與相關計劃筆記三支 CONFLICT(後面的提交已在帳尾追加)。這是 append-only 檔案:revert 要嘛衝突、要嘛把當時記的審計列(anchor-approve、delguard、代碼審)整段刪掉。
3. `scripts/lumos:17870` 的註解自己記過「stash pop 在帳本留下衝突標記,帳本直接壞掉、之後每次讀都炸」。照 spec 字面做 revert、解衝突時手滑留標記,就是同一個事故。
4. 「回退」節完全沒提這一點;「實務隱患」寫「還原提交後外面不用收拾」也對不上:要收拾的至少有三本帳的衝突、被 revert 掉的審計列(要補回或明說捨棄)、以及 governance/review-reports/漂移修法補強/ 整包卷證被刪(revert 同時抹掉「這條線為何被撤」的證據)。
5. 需要的是:回退節寫明 revert 時對簿記檔取「聯集/保留現況」、卷證與帳只 revert 程式+筆記+測試三類,或改成「反向提交只挑 scripts/、docs 筆記、skills/」的路徑限定寫法。

## F2 revert 後「要重跑 anchor approve」與 revert 本身會還原 baseline 互相矛盾
severity: minor
blocking: 否
引句:「`scripts/test_lumos.py` 是錨點檔,revert 後要重跑 `lumos anchor approve`」
file: `scripts/lumos:19143`、`governance/anchor-baseline.json`
1. baseline.json 版控、且在功能提交裡跟 test_lumos.py 一起改(02ea9745 的 stat 有它)。純 revert 會把 baseline 與 test 檔一起退回前一組配對,那時 anchor verify 是綠的,不需要 approve。
2. 但只要功能提交之後還有別的提交動過 test_lumos.py(常態),revert 對測試檔自動合併成功、baseline 也自動合併成功,兩邊 hash 各自對不上,anchor verify 才紅,這時才需要 approve。spec 沒分這兩種情況,一律叫人 approve;在第 1 種情況多簽一次會多留一筆 anchor-approve 治理列、note 需要理由,沒寫理由範本。
3. 建議把句子改成條件式:revert 後先跑 `lumos anchor verify`,紅了才 approve 並在 --note 寫「撤 漂移修法補強」。

## F3 revert 提交本身過推送閘的路沒寫
severity: minor
blocking: 否
引句:「主要路徑是 `git revert` 那個功能提交」
file: `scripts/hooks/pre-push:405`、`scripts/hooks/pre-push:425`
1. 撤掉一個動 scripts/lumos 上千行的功能,revert 提交的 diff 同樣分成 tier high,pre-push 會要求 code-loop pass 或 skip 留痕;grep 全 repo 對 revert 沒有任何豁免。
2. 收拾殘局的人要撤的當下,被擋在「缺代碼審留痕」;pre-push 訊息有給 `lumos code-loop skip --note`,但 spec 回退節沒寫用它,值班的人只看回退節會誤以為要重跑整輪代碼審或 `--no-verify`(後者 CI 會標紅)。
3. 補一句「revert 提交走 `lumos code-loop skip --note "撤 漂移修法補強"`」即可。

## F4 舊版工具遇上新文件:skills 文件即時跟 repo,消費專案的工具檔要 lumos update 才換
severity: minor
blocking: 否
引句:「[[Systems/存量漂移守衛]]、[[Systems/lumos-cli-write]]、[[Systems/guard-kill]]、[[Systems/delguard]] 的新句子與 lumos-project-notes 的 commands/04、commands/08 對應處一起改回」
file: `install.sh:3`、`scripts/lumos:27725`
1. install.sh 把 skills 以 symlink 裝進 ~/.claude/skills,所以 commands/04、commands/08 一合併就對所有機器生效;消費專案 scripts/lumos 是複本,要 `lumos update` 才換。
2. 中間期:文件教人 `drift fix --kind c3 --reason …`,消費專案舊工具走 `_drift_fix_args_err` 回「--kind c3 不收 --reason」;反過來 revert 之後,文件已收回、還沒 update 的消費專案工具仍收 --reason,寫入的「;理由:」句就留在專案筆記裡。
3. 舊工具失敗是明確報錯、不寫檔,傷害低;但回退節與誠實界線都沒提這個窗口,也沒說 revert 後消費專案要 `lumos update` 才算退乾淨。

## F5 「不用收拾」的宣稱漏了新工具已寫出去的資料
severity: minor
blocking: 否
引句:「已排除:不可逆:只改本機的工具輸出與檢查,不改筆記內容的寫法;還原提交後外面不用收拾」
file: `scripts/lumos:27917`、`scripts/lumos:29404`
1. 第 4 節讓 c3 把「;理由:<理由>」寫進驗證紀錄正文,這是筆記內容,會留在 rtb 等消費專案裡;舊工具不解析它,不會壞,但「不改筆記內容」與事實不符,「外面不用收拾」也不準。
2. 第 5 節在治理帳 delguard 的 note 加 `vendored-skip=`。revert 後這些列留著(帳是 append-only),舊工具不讀這欄所以無害;RETIRE-IF 第 ② 條的量法本來就靠它,撤除後與其之後重跑 `grep` 會混入撤除前的舊列,判讀時要以撤除日切開。spec 沒寫這一條。
3. 措辭改成「不會壞、但留在筆記與帳裡」並寫明用日期切開,即可。

## F6 代碼審通過的帳本提交不在功能提交裡,revert 後留下指向已撤程式的「通過」
severity: minor
blocking: 否
引句:「主要路徑是 `git revert` 那個功能提交(程式、筆記、測試同一個提交)」
file: `governance/code-loop/`
1. 專案規矩是過代碼審的功能另有一個「記錄代碼審通過」的帳本提交,留痕綁功能版本的 sha。「同一個功能提交」不含它,`git revert <功能提交>` 不會動它。
2. revert 後,帳裡仍有一筆對已撤版本的 pass;之後有人把同一批改動重新做回來、恰好同 diff 指紋時,可能被舊留痕當成已審過。spec 沒要求 revert 同時作廢或註記那筆帳。
3. 建議回退節加一句:revert 同提交以 `code-loop` 的作廢/備註方式標記舊 pass 已失效。

## 其他節
- 做法 1 到 5 各自的「回退」對應條目(卷證目錄、set 常數、c1 訊息、c3、刪除守衛的 skip 預設空集合)逐項核對:都是加法或預設值,單項退回程式面上可行;唯一耦合是第 1 節範本印的 `<卷證>` 與第 2 節的擋字共用常數,單獨只退第 2 節會讓範本句的 `<卷證>` 又能被 `lumos set` 寫進筆記,但那正是改前原行為,不算新洞。
- ★INVARIANT★ 合約:guard-kill 與 lumos-cli-write 的合約行這份設計的回退面不影響——回退只還原程式與句子,不新增寫入路徑、不動鎖。
- RETIRE-IF 觸發後撤得掉:①撤第 1 節只需改回兩函式,②撤第 5 節只需不傳 skip;程式面乾淨,問題都在 F1 的 revert 機制。

最高等級:major;blocking 共 1 條
