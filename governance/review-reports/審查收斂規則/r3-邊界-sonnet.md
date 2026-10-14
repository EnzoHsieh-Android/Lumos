severity: major

我只看第二輪折入後新寫或改寫的內容。三條 finding 是 major(blocking),另有三條 minor。以下兩節已讀,無 finding:第 4 點徽章與第 6 點逃逸參數(只有 S7 測試寫法的小問題,併入 finding 6)、第 7 點要一起改的說法清單。

severity: major
blocking: 是 — 實作者非猜不可,而且照字面做不出來
引句:「另加一行 `checker:<第二個代理的模型>/<日期>`」
問題:計劃要求殘留決策「另加一行 `checker:`」,寫入時還要驗「有一行 `checker:` 而且等於 `--checker` 給的值」。`decision-add` 只有 content、`--context`、`--why`、`--decided` 這幾個入口。`_fmt_decision_value` 遇到任何換行類字元就丟 ValueError「決策開頭欄位的自由文字不能含換行類字元」。`parse_decisions` 解析出來的 content 也是單行字串。所以「另一行」沒有地方可放。計劃沒說 `checker:` 在 content、context、why_chosen 裡的哪一欄,也沒說是不是要在尾端串成同一行。「四欄齊」是哪四欄計劃也沒講。
具體失敗情境:實作者 A 把 `checker:sonnet/2026-10-14` 串在 content 尾端,實作者 B 放進 `--why`。`guard residual` 的驗證就會在兩種寫法之間對不上,S1 的「沒有相符的 `checker:` 行」測試也寫不出固定的先紅夾具。要是真的塞換行,`decision-add` 會直接拒絕。
佐證:file: `scripts/lumos:21462`(`_fmt_decision_value`)、file: `scripts/lumos:21582`(`cmd_decision_add` 的參數)、file: `scripts/lumos:19182`(`parse_decisions`)

severity: major
blocking: 是 — 推送前規格閘缺少計劃要用的輸入
引句:「用**主線版**的圖譜找出帶 `[residual:]` 的合約所在節點」
問題:`_spec_gate_push_check(env, git_range, repo)` 只收範圍和 repo,拿不到 remote、`pushed_ref`、分支名、`--at-sha`。`_push_mainlines(repo_root, remote, pushed_ref)` 需要前兩個。判有效留痕的 `_codeloop_record_valid(repo_root, rec_sha, marker_sha)` 需要 marker_sha 和讀留痕用的分支名。pre-push 呼叫 `spec-gate --push-check "$_brange" --repo` 時,一個都沒傳。計劃沒說這些參數怎麼加,也沒說「主線版」是哪個候選。`_push_mainlines` 會回多個候選,沒有單一主線;而且 `_brange` 的起點可能是分岔點,不是主線頂端。計劃也沒說「主線版圖譜」怎麼載入。現有的 `_drift_tree_env` 是整棵樹讀成記憶體 Env,計劃沒指名要不要重用,也沒說 git 失敗時是擋還是放行。目前這道閘的語意是算不出就 fail-open。
具體失敗情境:實作者看到範圍參數就用 `main` 或 `origin/main` 硬寫。推到 git-flow 的 develop 或 fork 時,主線版圖譜取錯,殘留合約看不到而放行。pre-push 在 for-each-ref 迴圈裡呼叫,多個 ref 時分支名也取不到。
佐證:file: `scripts/lumos:9064`、file: `scripts/lumos:47244`、file: `scripts/lumos:50536`、file: `scripts/hooks/pre-push:429`、file: `scripts/lumos:37605`(`_drift_tree_env`)

severity: major
blocking: 是 — 這一步放在現有函式裡的位置,字面做會被前面的提前返回跳過
引句:「推送前小改動閘判 light 的情形,這一步照樣跑,碰到就擋。」
問題:`_spec_gate_push_check` 在 `plans = _spec_gate_push_candidates(...)` 之後有 `if not plans: return 0`。改程式但沒有碰到風險低計劃的推送,多半就是 plans 為空,會在殘留檢查之前直接放行。範圍算不出、圖譜不在 repo 底下這幾條路徑也是 fail-open 的 return 0。計劃只寫「放在規格閘那一道」,沒寫插入點必須在這些提前返回之前,也沒寫上述放行路徑對殘留檢查是照放行還是改成擋。
補充:CI 的 ci.yml 只跑 `code-loop check`,不跑 `spec-gate --push-check`。pre-push 裡加的這道只要 `--no-verify` 就能繞過,CI 補不上。計劃把它當唯一的守衛卻沒承認這點,也沒寫回頭條件。
具體失敗情境:實作者把殘留檢查接在 `_spec_gate_push_scan` 之後,或放進 `if bad` 區塊。一個沒有任何風險低計劃的分支,改了帶殘留合約守的檔,推送時被 `if not plans: return 0` 放行,S6 的先紅測試也設計不到這條路。
佐證:file: `scripts/lumos:9064`(`_spec_gate_push_check` 內 `if not plans: return 0`)、file: `.github/workflows/ci.yml:186`

severity: minor
blocking: 否 — 可推斷但容易做歪
引句:「`--remove <節點>#<決策 id>` 拿掉一個」
問題:指令簽名寫成 `guard residual <節點> "<KEY 子字串>" <節點>#<決策 id> --checker <模型>/<日期>`,同時又有 `--remove <節點>#<決策 id>`。移除時第三個位置參數與 `--remove` 的值重複。`--checker` 在移除時要不要給,計劃也沒寫。argparse 的 `nargs` 要怎麼設,字面看不出來。現有的 `guard audit` 是 `node` 加 `invariant` 兩個位置參數,沒有可參考的同形。S1 和 S7 都沒有 `--remove` 的失敗情境。
具體失敗情境:實作者把第三個位置參數設成必填。使用者想移除標記,只能寫 `... <ref> --remove <ref>`,同一個值要打兩遍。

severity: minor
blocking: 否 — 條款可補
引句:「拿掉保留的那段實作時,這支測試應翻紅。」
問題:S2 要求拿掉保留的實作時測試翻紅。S6 的「同一個提交把標記拿掉時也應擋下」需要一個有主線 ref 的 git 夾具,涉及 `main@{upstream}` 或遠端候選,但條款沒寫夾具怎麼造。S6 也沒涵蓋「沒有圖譜的專案什麼都不做」和「git 失敗」兩個分支。S8 只有文字存在性的測試,能抓到字被刪,抓不到語意被改。
具體失敗情境:S6 實作者只造一個本機 `main` 分支做夾具。測試通過,但真實的 `origin/HEAD`、`upstream` 候選路徑沒被碰到。

severity: minor
blocking: 否 — 小地方,實作者可推斷
引句:「決策指標的狀態用既有的 `_pq_decision_state`,不是 `ok` 就不寫、回 2」
問題:`_pq_decision_state` 第一個分支只認 `#dN` 簡寫(本篇)和 `<節點>#dN`。計劃裡的 `--residual-ref` 和標記都要求「節點寫圖譜相對路徑、不帶 `.md`」,但函式也接受短名。短名撞名時回 `bad`,短名唯一時回 `ok`。那就會有人寫 `a_計劃#d12`(不帶路徑)通過寫入,但標記裡的字串在 doctor 或別的呼叫點用 `_dref_norm` 解析,行為可能不一致。計劃沒規定標記裡必須是帶路徑的全名,S1 也沒有短名的案例。
具體失敗情境:使用者寫 `guard residual ... a_計劃#d12`,寫入通過。之後有人在別的資料夾加了同名節點,短名撞名,doctor 報「找不到決策」,卻不是決策真的不見。

最高等級 major,blocking 共 3 條。
