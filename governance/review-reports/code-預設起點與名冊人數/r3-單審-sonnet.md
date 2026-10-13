severity: minor

1. 分支名和標籤同名時,`symbolic-ref --short` 回 `heads/<名>`,查不到登記的遠端
severity: minor
blocking: 否
引句:「br = _lens_git(repo_root, "symbolic-ref", "-q", "--short", "HEAD")」
file: `scripts/lumos` 的 `_codeloop_default_base`(本輪新增段)
- 我在暫存 repo 實跑:分支 `foo` 和標籤 `foo` 同時存在時,`git symbolic-ref -q --short HEAD` 印出 `heads/foo`(同時警告 refname ambiguous)。
- 接著查 `branch.heads/foo.remote` 一定落空,因為設定檔裡登記的鍵是 `branch.foo.remote`。結果是 `remote` 退回 origin,或在只有一個遠端時退回那一個;分支明明登記了 fork,卻不會用到。
- 改動前用 `rev-parse --abbrev-ref @{upstream}` 取遠端,不吃本機分支名的縮寫,所以這是本輪造成的退步。
- 影響:同名標籤很少見。落空後只是退到 origin,不會崩潰,也不會讓整條分支被當成沒有改動。
- 修法:改用 `symbolic-ref -q HEAD`(完整參照),自己去掉 `refs/heads/` 前綴。
- 其餘特殊字元我也試了。分支名含 `.`、`/`、`"` 時,`branch.<名>.remote` 的鍵都能正確解析,只有同名標籤這一種會壞。
- 分離 HEAD 時 `symbolic-ref -q` 回 rc 1,走退到 origin 的路,行為和改動前一致。

2. 新測試擋不住「把上游遠端名從斜線切出來」這個舊錯法
severity: minor
blocking: 否
引句:「g("config", "branch.feat.remote", "."); g("config", "branch.feat.merge", "refs/heads/main")」
file: `scripts/test_lumos.py` 的 `t_codeloop_default_base_prefers_newest_mainline`(本輪新增段)
- r2 要擋的錯是 `feature/base` 被切成遠端 `feature`。測試的上游卻是 `refs/heads/main`,縮寫成 `main`,本來就不含斜線。
- 舊寫法(`@{upstream}` 縮寫後切 `/`)在這個夾具下取不到遠端,退到 origin,結果一樣,測試照綠。我是讀碼推得,沒有實際還原舊寫法跑。
- 這條測試因此釘不住「上游是本機分支」這條修補。
- 修法:讓 `branch.feat.merge` 指向帶斜線的本機分支(例如 `refs/heads/feature/base`),並讓 `refs/remotes/feature/main` 之類的假遠端候選存在,舊寫法才會翻紅。
- 同理,測試沒有覆蓋分離 HEAD,也沒有覆蓋分支名與標籤同名。

3. 人數分流(`old_panel`)各情況檢查,沒找到差異
severity: clean
blocking: 否
引句:「old_panel = panel_fmt and not light and not _panel_retired_for(rounds)」
file: `scripts/lumos` 的 `cmd_loop_next`
- `old_panel` 與下游 `disposal = panel_fmt and not light and _panel_retired_for(rounds)` 正好互補,在 light 以外的 panel 格式下,印的人數和送進閘的人數同步。
- 逐一核對各情況,名冊人數與 `_TIER_PARAMS` 原值一致,沒有退步:
  - light:名冊 1,原值 1。
  - 循序 code standard(seq):名冊 1,原值 1。
  - legacy(含無定錨舊帳):名冊 1,原值 1。
  - 還沒有帳、第一次呼叫:design standard 為 3、design high 為 5、code high 為 5,與原值相同。
- 帳的 ts 不像日期時,`_panel_retired_for` 回 False,算舊迴圈,維持 `_TIER_PARAMS` 原值,與閘一致。
- 只有「code standard、panel 格式、新迴圈」從印 3 變成印 1,這是刻意改的。
- 名冊空或 kind 無法判定時,`or width` 會退回原值。

暫存的 repo 已刪,`/tmp/lumos-seat-work/code-預設起點與名冊人數/` 下已無殘留。

總結:最高等級 minor,blocking 共 0 條
