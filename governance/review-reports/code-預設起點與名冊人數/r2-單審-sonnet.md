severity: major

1. 一般分級代碼審帶輪次時,印出「1 人審」,但收斂閘仍要 3 人,照指示派就過不了閘
severity: major
blocking: 是
引句:「這輪要 {width} 人審,最多跑 {cap} 輪」
file: `scripts/lumos:15579`
- 輸入:`code-*` 編號、standard 分級、帳帶 `--round`(多人審格式)。這正是 2026-10-13 的原始案例。
- 走到哪:`width` 改成名冊數 1,`gate_width` 仍是 3。人讀的輸出寫「這輪要 1 人審」。JSON 是 `width=1, min_seats=3`,兩個欄位互相矛盾。
- 壞在哪:編排者照「1 人審」只派一席,閘卻要每輪 3 個不同審查員,而且 panel 輪有效另需 2 人以上。
  - 我在沙箱用 `code-w4` 實跑:`loop next` 印「這輪要 1 人審」。同一份帳跑 `loop status --gate --panel`,一人一輪印出 `PANEL GATE FAIL ... 記帳的人不夠(... 少於 2 人,這輪無效)`。
  - 修補前印 3 人,與閘一致,只有名冊那一行不一致。現在變成人讀數字與閘衝突。
  - 人讀的文字輸出完全沒提 `min_seats`,看不出閘要幾人。
- 影響範圍:我逐一核對了 seq、light、legacy、design 的 standard 與 high,以及 code 的 high,`width` 與 `gate_width` 都和改動前相同。只有這個組合會分岔。
- 附帶影響:`canary_type` 的槽位數也跟著 `width` 從 3 縮成 1。

2. 上游是本機分支時(名稱含 `/`),遠端名被誤判,`origin` 候選全丟,舊的「本機 main 落後」問題復發
severity: minor
blocking: 否
引句:「remote = up.stdout.strip().split("/", 1)[0]」
file: `scripts/lumos:50955`
- 輸入:分支上游設成本機分支 `feature/base`(`branch.<x>.remote=.`,堆疊分支的常見做法)。
- 走到哪:`@{upstream}` 回 `feature/base`,含 `/`,於是 `remote="feature"`,這個遠端不存在。`_push_mainlines` 的 `refs/remotes/feature/*` 候選全落空,`origin/main` 沒進候選。
- 壞在哪:候選只剩落後的本機 main。我實跑沙箱:`origin/main` 在 `c1580998`,本機 main 在 `5d0d0ec2`,函式回 `5d0d0ec2`。這就是這次要修的「落後 52 個提交、誤判 tier=high」。
- 同類:遠端名本身含 `/` 也會被切錯。
- 也可能少候選:只有一個遠端、名字不是 origin(例如 `github`)、又沒設上游時,遠端候選全沒有。
- 建議:用 `git config branch.<名>.remote`,或 `for-each-ref --format=%(upstream:remotename)` 取遠端名,並確認它是真實遠端;找不到就退到 origin 或唯一的遠端。

3. 測試從沒設上游,「取上游所在遠端」這條分支即使整段刪掉也不會翻紅
severity: minor
blocking: 否
引句:「g("remote", "add", "origin", str(root / "nowhere"))」
- 新測試只有 `origin` 加一個沒上游的 `fork`。以下改壞都會維持綠燈:
  - 刪掉 `@{upstream}` 解析。
  - 改成永遠用 origin。
  - 把上面第 2 點的切字串寫錯。
- 沒有任何案例是「上游在 fork、origin 另有一條較新的 main」。
- 呼叫端那條 `"merge-base == HEAD" not in reason` 的斷言,在 `_codeloop_default_base` 回 None 走 fail-open 時也會過。這條只靠上一個直接斷言撐住。
- 其他我沒找到問題的 git 形狀:
  - detached HEAD、沒有遠端、逾時(`_lens_git` 回 None 會被接住,走 fail-open)、孤兒分支回 None,行為都合理。
  - 多個分岔點由 `_push_pick_base` 處理。
  - 上游指向已刪除的遠端分支時,`@{upstream}` 解析失敗,退到 origin,可接受。

總結:最高等級 major,blocking 共 1 條

我在 `/tmp` 做的沙箱實驗已刪除,repo 沒動。
