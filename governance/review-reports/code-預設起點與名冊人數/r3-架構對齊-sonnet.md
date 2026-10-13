severity: minor

1. 新舊迴圈的判法與代問閘分流是同一支謂詞,但寫了兩份
severity: minor
blocking: 否
引句:「    old_panel = panel_fmt and not light and not _panel_retired_for(rounds)」
file: `scripts/lumos:15388`
- 這行和代問閘那段 `disposal = panel_fmt and not light and _panel_retired_for(rounds)`(`scripts/lumos:15690`)用的是同一支 `_panel_retired_for`,連 `panel_fmt and not light` 這個前提也一樣。兩處的 `rounds` 也是同一個變數。
- 我逐路徑對過:`old_panel` 為真時,代問閘走 panel 閘;`old_panel` 為假時,代問閘走處置閘或 legacy/light 閘。
- legacy 和 light 的名冊寬度與 `_TIER_PARAMS` 相同,都是 1(`scripts/lumos:13175`、`scripts/lumos:13526`),所以 `gate_width` 在這些路徑上沒有悄悄變。
- 沒有引入第二種判法。
- 這個判斷在同一函式裡寫了兩遍、一正一反,日後前提若只改其中一邊就會分岔。建議先算出一個布林值,兩處共用;不改也不影響正確性。

2. 同一段註解重複,舊版殘留
severity: minor
blocking: 否
引句:「    # ★人數以應派名冊為準,但已退役 panel 閘的舊迴圈除外★(名冊是編制數字的單一來源,見 _TIER_ROSTER 上方註解)。」
file: `scripts/lumos:15380`
- 上方殘留舊的「★人數以應派名冊為準★…」和「2026-10-13 踩到…」兩行,新增的區塊又從頭寫一遍,「2026-10-13 踩到」那句出現兩次(`scripts/lumos:15381`、`scripts/lumos:15387`)。
- 這是整理疏漏,不是行為問題。刪掉舊的兩行即可。

3. `_codeloop_default_base` 讀 `branch.<名>.remote` 是 repo 裡讀「上游遠端」的第三種做法
severity: minor
blocking: 否
引句:「        rc = _lens_git(repo_root, "config", "--get", f"branch.{br.stdout.strip()}.remote")」
file: `scripts/lumos:50962`
- repo 其他地方取上游都走 `@{upstream}`:`scripts/lumos:34005` 用 `rev-parse --abbrev-ref --symbolic-full-name @{upstream}`,`_push_rev` 在 `scripts/lumos:47225` 用 `rev-parse --symbolic-full-name`,`_mainline_ref` 在 `scripts/lumos:47405` 用 `main@{upstream}`。repo 裡沒有別處讀 `branch.*.remote`。
- 這個做法有理由:`@{upstream}` 切斜線,遇到 `feature/base` 這種分支名會誤切(本分支 r2 單審席的發現),另外一種寫法是 `for-each-ref --format=%(upstream:remotename)`。我沒找到比它更貼近既有做法的單一函式可重用。
- 它用的是同檔既有的 `_lens_git`,`remote` 列表也是 `scripts/lumos:42401` 同樣的讀法,沒有跨層直呼。
- ⚠ 判不準它算不算「第二種做法」,因為它解的是既有做法有缺陷的情況。依你的規則不到 major。若要收斂,建議把「取分支的上游遠端」抽成一支共用函式。

4. 筆記的 WHY 行跟程式現況不符
severity: minor
blocking: 否
引句:「+WHY:手動 `code-loop check` 不帶範圍時,起點改成「主線候選合起來跟 HEAD 的最近共同祖先」:候選沿用推送閘的 `_push_mainlines`(遠端取這條分支上游所在的遠端,沒有就用 origin),只多加本機 main/master(手動檢」
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:218`
- 程式現在是:有登記上游遠端且該遠端真的存在才用它(上游是本機分支不算),其次是 origin,再其次是「只有一個遠端就用它」(`scripts/lumos:50957-50967`)。筆記只寫到「沒有就用 origin」,缺少「只有一個遠端就用它」和「上游是本機分支不算」。
- r3 修補差異裡只有程式的 docstring 同步了,這行筆記沒跟上。建議補一句。

其他核對結果,都相符:
- 兩篇筆記(`pitfalls-code-loop.md`、`loop-convergence-recording.md`)和 `_push_mainlines`、`_mainline_ref` 的 docstring 對 `_codeloop_default_base` 的描述都成立。
- 新增的 REVISIT 說 `_codeloop_guard_verdict` 算表態範圍用 `_mainline_ref`(固定順序),我在 `scripts/lumos:51090` 看到的確如此。
- `loop-convergence-recording.md` 的 WHY 與 `cmd_loop_next` 的新行為一致。

總結:最高等級 minor,blocking 共 0 條
