severity: major

鏡頭:整合與知識同步。對照碼:/Users/enzo/harness/lumos-firstpush(唯讀;實驗在 scratchpad/fpc 臨時 clone)。
固定席:本次派工沒有 hook 附上的合約/事故節點,不適用;我自己查到相關的是 Issues/推送前其他閘的範圍在合過主線時會多算(開著)、Systems/bound-tests-gate、Systems/pitfalls-code-loop,判斷見 F2、F6。

## F1 pp_touched_file 被歸成「只提醒不擋」,其實餵的是會擋的健檢
severity: major
blocking: 是——餵給會擋的閘,漏分類會讓同一個誤擋換個閘繼續發生(major)。
spec 段落:範圍/不做第一條。
引句:「`pp_touched_file`——只提醒不擋,照舊用 `pp_range_for` 寧可多掃」
問題:`pp_touched_file`(file: `scripts/hooks/pre-push:63`)用 `pp_range_for` 算「這次推送改到哪些檔」,結果由 `scripts/hooks/pre-push:289` 傳成 `doctor --ci --touched-from`;doctor 用它決定逾期預告合約「只擋這次碰到的」(file: `scripts/lumos:46436` 的說明、`scripts/lumos:14195` 附近 `_guard_touched_hits` 命中就回擋)。擋下時 hook 在 `scripts/hooks/pre-push:291-304` 直接 exit 1。
具體例:新分支首推,主線上有別人一條已逾期的預告合約。現況與改後都一樣:touched 清單 = 空樹..頂端 = 整個 repo 的檔,別人的逾期合約被判「你碰到了」→ doctor 擋、exit 1,而且這一步排在 code-loop 之前,先於 spec 想修的那幾道。改後 spec 宣稱「新分支首推的誤擋修好了」,實際只是 rtb 那一種(新增告警)修了,首推仍會被 doctor 擋。
要改:把 `pp_touched_file` 列進「會擋」的呼叫(改吃 `pp_block_range_for`,並處理空字串=沒有新提交時清單為空)。逐一重新分類的完整清單應該是:pp_touched_file(擋)、impact_once(擋)、pitfalls 兩處(擋)、spec-gate、code-loop check、loop escape、home check、note-shape(已是);只提醒:標籤路徑 pitfalls、test-layers、bound_tests_advisory。drift 與 reread-check 另走 lumos。

## F2 把「已知會在合過主線時算錯」的 shell 算法擴到五道會擋的閘,且與開著的 Issue 的收斂方向相反
severity: major
blocking: 是——改動後把已被代碼審判定有洞的起點算法放到更多會擋的閘上,而且新分支開 PR 的流程正是它出錯的形狀(major)。
spec 段落:PRIOR-ART 與做法 1。
引句:「跟現在 `_hrange` 那段逐字同一套判斷」
問題:file: `scripts/hooks/pre-push:336-343` 的 `hold^..頂端` 是兩點的「樹對樹差異」,不是提交集合。功能分支建出後主線前進、又把主線合進來:`hold^`(分支點)到頂端的樹差異會包含主線上別人已在遠端的改動。這正是開著的 Issue 描述的洞(`docs/lumos-toolchain-knowledge/Issues/推送前其他閘的範圍在合過主線時會多算.md`:「可能把主線上別人的改動算成這次推送的」),也是 `scripts/lumos:41782-41786` 與 `scripts/lumos:41867-41870` 兩段說明明寫的:漂移那道因此在代碼審 r2 起改走 `_push_range_start`,hook 的 shell 補法被判「算錯」。Issue 寫的收斂路是 home check/note-shape 改走 lumos 算(加 --push-remote/--pushed-ref),本 spec 走相反方向:把 shell 版複製成共用函式再擴到 impact、pitfalls、spec-gate、code-loop、escape。
具體例:feature 從 main@M0 分出、第一個提交 c1;之後 main 走到 M1(別人加了一個高風險寫法並已過 CI);feature 合入 M1 得 c9;首推。`hold=c1`,`hold^=M0`,範圍 M0..c9 含 M0→M1 的全部改動 → pitfalls 判 high、code-loop check 要審查留痕,擋的是別人已上主線的碼。CI 用 `_lens_push_base`(跟主線的 merge-base=M1)則不會擋——本機擋、CI 過,又是一組本機/CI 判定不一致。
另一個不一致:同一支 hook 裡,漂移檢查與 reread-check 用 lumos 的 `_push_range_start`,其餘用 shell 版,改完後同一次推送同一支 hook 內有兩個不同的起點。
我沒有實際重現「合過主線」的範圍(spec 的天花板只寫了基在別人未合併分支上那種,沒寫這種);Issue 要求先重現,spec 也沒做。
要改:二選一並寫進 spec——(a)實作時在 hook 裡對 `_hrange` 套與 `_push_range_start` 等價的處理(合過主線時取 merge-base);(b)讓這五道的起點交給 lumos 算(帶 --push-remote/--pushed-ref),本 spec 退成只修 hook 層傳空樹這件事。無論哪個,spec 步驟 5 必須同時處理 Issue 推送前其他閘的範圍在合過主線時會多算(它在 related 裡卻沒有對應步驟,REVISIT 2026-10-31 也要跟著動),寫明「這次擴散了該 Issue 的受影響面」。

## F3 標籤/分支分流在掛鉤結構上做不到;標籤推送已在遠端的提交會從全套變成只跑文件子集
severity: major
blocking: 是——spec 的做法 3 與實際程式結構不符,照字面實作會改到標籤路徑,且標籤推送少跑全套是未討論的行為變更(major)。
spec 段落:做法 3、實務隱患「全部已在遠端」。
引句:「標籤路徑那處 `pitfalls --diff` 與 `test-layers` 照舊 `_range`」
問題:(1)`impact_once "$_range"`、`pitfalls --json`(`scripts/hooks/pre-push:371-372`)和高風險命中列表(`scripts/hooks/pre-push:384`)都在 `if [[ "$_rref" == refs/heads/* ]]` 之前、分支與標籤共用;標籤路徑只剩 `scripts/hooks/pre-push:458`(技術棧題列表)與 `scripts/hooks/pre-push:462` 的 bound_tests_advisory。spec「分支路徑的兩處 pitfalls」在程式裡不存在,實作者只能整段改 `_brange`,標籤路徑的 `_tier_high`、`pf_json`、suite 分類也跟著變小。(2)標籤路徑 `scripts/hooks/pre-push:456` 用 `pf_json`(新範圍)判有沒有技術棧題,卻在 `scripts/hooks/pre-push:458` 用 `_range`(舊寬範圍)印清單:條件與內容來自兩個範圍,會出現「判有題、列出一堆舊題」或反過來。(3)標籤是 `refs/tags/v1` 零 sha,標籤指向的提交通常已在遠端分支上 → `pp_block_range_for` 輸出空字串 → 設成 `頂端..頂端` → pitfalls 回 `"suite": "docs"`(我在 clone 實測:空範圍 `pitfalls --diff X..X --json` 回 tier light、suite docs、light_ok false)→ `_SUITE_FULL` 不為 1 → 推標籤那次不跑 8 分鐘全套(`scripts/hooks/pre-push:552-560` 的 _AUTOLOOP_ARGS 也只跑 real_claude_md)。舊行為:空樹範圍→全套。spec 的「全部已在遠端」只舉分支改名,沒提標籤;推發布標籤正是常見的「全部已在遠端」。
要改:spec 要明寫標籤路徑的 pf_json/suite 該用哪個範圍(建議標籤與 suite 判定維持 `_range`,會擋的分支路徑另算一份),並把「標籤推送少跑全套」列進實務隱患與驗收條款(S3 目前沒有標籤形狀)。

## F4 新分支首推:本機起點與 CI 起點是兩套,改後仍不一致,spec 沒量
severity: minor
blocking: 否——CI 是後盾、方向上本機多半較鬆,不會把人鎖死;但 spec 的「CI 沒有這個誤擋」說法需要補全(minor)。
spec 段落:範圍/不做第二條。
引句:「CI 傳全零給 lumos,lumos 的 `_lens_push_base` 已經從跟主線的分岔點算,沒有這個誤擋」
問題:CI 的 code-loop 步(file: `.github/workflows/ci.yml:171-195`)走 `_lens_push_base`(merge-base 跟主線);本機改後走 `hold^`。兩者在三種形狀不同:(a)基在別人未合併遠端分支 A 上的分支:本機只算自己的提交,CI 把 A 的提交也算進來,A 若含高風險寫法,本機放行、CI 紅(spec 天花板 1 只講了本機這一側,沒講 CI 會紅);(b)合過主線:見 F2,本機大、CI 小;(c)沒有主線可比的 repo:兩邊各自退成不同的起點。驗收條款 S1–S4 也沒有一條比對「同一個頂端本機範圍與 CI 範圍」。spec 的 RETIRE-IF 認得這個收斂路,但沒有在天花板裡寫 CI 方向。
要改:天花板補一條「(a) 本機放行、CI 可能紅」,並加一條驗收:對同一個頂端,用 `_lens_push_base` 與 hook 算出的起點在「單一提交的分支」下相同。

## F5 既有測試不會因這次改動翻紅;但新測試名只有一個、驗收四條共用一支,漏掉最容易壞的形狀
severity: minor
blocking: 否——缺口是測試涵蓋度,不是照做就會壞的錯;補測試即可(minor)。
spec 段落:驗收條款。
逐支核對(grep pre-push、`_EMPTY_TREE`、`pp_range_for`):
- `t_prepush_range_scan`(`scripts/test_lumos.py:17492`):新 ref 那段是根提交單一高風險檔,`hold` 無上一個 → 退回 `空樹..頂端`,仍判 high 擋;tag 那段同形;main 直推 `_rsha` 存在走舊值。三段不翻紅。
- `t_prepush_computes_impact_once`(17422)、`t_prepush_runs_home_check`(47450,①空樹 ②③④ 的期望與新函式輸出相同)、`t_prepush_gates_stop_on_signal`(55755):它用正則數 `pp_stop_if_signaled "$x_rc"` 恰好 6 行(前置斷言 n==6),抽函式不要多加或少掉這種呼叫。不翻紅。
- 讀 hook 原文的測試(`scripts/test_lumos.py:37272` 的正則 `grep -q "…"` 接 `push-gate-unreviewed`、52402、60064、65016)只看旗標字樣與那幾行的結構;把 `--range "$_range"` 改成 `"$_brange"` 不影響。
- 缺口:S1–S4 全綁同一個 `t_prepush_new_branch_block_range`,但要能抓到問題的形狀不在裡面:合過主線(F2)、標籤已在遠端(F3)、`pp_touched_file`/doctor(F1)、多個 ref 同次推送(逐 ref 的 `_brange` 必須在迴圈內重算,別存到迴圈外)。另外 hook 檔頭註解 `scripts/hooks/pre-push:308-312`(「無基準倒向保守掃 empty-tree…非 fail-open」)與 `scripts/hooks/pre-push:330-331` 的「別把兩套合併成一套」會與新設計相反,實作時要改,否則下一個人會照註解把它改回去;現有測試沒有守衛這句註解。

## F6 知識同步與消費端:lands_in 只列一篇,還有至少四處要同步;回退段數字對不上
severity: minor
blocking: 否——同步清單不齊會讓三個月後的人讀到舊說法,但不影響執行(minor)。
spec 段落:前言 lands_in、做法 5、6、回退。
引句:「退回後會擋的三道恢復從空樹算(新分支首推會再被誤擋)」
問題與要同步:
1. 回退段寫「三道」,範圍/做法列的是 impact、pitfalls 兩處、spec-gate、code-loop check、escape 兩處(加上 F1 的 pp_touched_file),數字與清單不一致,實作者無法依回退段驗證改全了。
2. lands_in 只有 `Systems/每支檔有家`;`scripts/hooks/pre-push` 同時是 `Systems/bound-tests-gate`(about_code 列了它;正文 `Systems/bound-tests-gate.md:74` 寫「起點是空樹時改用主線 tip」,改後 hook 傳真起點給 impact,這句說明要補「hook 層已不傳空樹」)、`Systems/存量漂移守衛`、`Systems/筆記內容閘` 與 `Systems/棧別提問表態閘` 的家(grep scripts/hooks/pre-push 命中這些節點)。「改到的每支檔都得先有家,寫說明寫進改到那支檔的家」——pre-push 有多個家,spec 需指定哪篇為主、其餘用連結。
3. `Systems/pitfalls-code-loop.md:32` 的 PITFALL 說「code-loop check --diff 起點 40 個 0 …先照共用判法換成真的起點;CI 原樣交前一版」,改後 hook 層是 hook 自己算真起點,需補一句「本機掛鉤 hook 自算 `hold^`,CI 走 `_lens_push_base`,兩者不同」(對應 F4)。
4. Issues:`推新分支時風險分級拿空樹當起點`(spec 做法 5 已有);`推送前其他閘的範圍在合過主線時會多算`(spec related 有、沒有任何步驟)必須在做法列一步更新;`SHA-256的repo其他閘仍用SHA-1空樹`(hook 用 `git hash-object` 算空樹,不是寫死,但 `pp_block_range_for` 若寫成常數會踩)——spec 沒提到。
5. 消費端:舊 hook 在消費專案要 `lumos update`(file: `scripts/lumos:21108` `cmd_update`)才換;舊 hook 配新 lumos 只是行為不變,新 hook 只用既有子命令與參數,無相容問題;spec 回退段已寫要重跑 update,但沒寫「更新前的消費專案仍會被 715 條誤擋(rtb 的情形),要先通知」。skill 說明(lumos-code-loop、lumos-project-notes commands/06)內我 grep `空樹|empty-tree|保守掃` 皆無命中,不需要同步。
已讀,無 finding:PRIOR-ART 與 RETIRE-IF 的函式引用(`_lens_push_base`、`_push_range_start`、`pp_range_for`、`_hrange`)都存在;做法 1 的「行為不變」對每支檔有家那段屬實(`pp_range_for` 的否定式與 `_hrange` 條件等價);空範圍 `X..X` 實測 impact、pitfalls、code-loop check(rc0)、spec-gate --push-check(rc0)都能跑完,S3 的「照常走完」屬實;`--not --remotes` 沒更新遠端追蹤分支只會變大不會變小,實務隱患第一條屬實。

## 實務隱患逐類
- 資料遺失/金流/對外送出/不可逆:無,只改 hook 腳本(同 spec 的已排除)。
- 守衛面(放寬):有,見 F2(算法有洞)、F3(標籤少跑全套)、F4(CI 與本機不一致)。
- 並行/多 ref:同次推送多個新分支時 `--not --remotes` 看不到同批其他 ref,範圍偏大(保守,可接受),但 `_brange` 要在迴圈內每個 ref 重算,spec 步驟 2 已寫在迴圈內,屬實。
- 效能:`git rev-list --topo-order --reverse` 對每個 ref 多跑一次在大 repo 上與 home check 同成本,現況已承受,不新增。

最嚴重 severity: major;blocking 條數 3(F1、F2、F3)。
