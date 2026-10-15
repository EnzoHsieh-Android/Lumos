severity: minor

文件包整體和程式對得上,沒有 major。我核對了這些:
- 門規則版本 13。
- 需求風險面 25 項(10 個前端面加 `verify-infra-script`)。
- `infra` 六題的 id 與觸發寫法。
- `_REQ_FE_WHEN`、`_TEST_INFRA_PATH_RE`。
- `_spec_gate_push_stale` 的第 13 版句子。
- 計劃模式「前端面」段與 `--check` 提醒。
- 文件裡引到的新測試名,全都存在。
- `lint` 九篇都是 0 問題。
- `-k templates/infra/frontend/door_rule/test_quality_standard/push_stale/arch_alignment` 全綠。
- user-event 文件那句「`delay: null` 不建議、v14.1 起建議 `advanceTimers`」,我查過官方頁面,是對的。

以下是我找到的不一致。

1. 規格閘節點的版本號沒跟上。
severity: minor
   - blocking: 否
   - 問題:`Systems/規格閘.md` 第 38 行的 KEY 寫「`_DOOR_RULE_VERSION=12`」,版本沿革只列到 12。
   - 實際:`scripts/lumos:8046` 是 13,`lumos spec-gate --door-rule` 印 `door_rule=13`。
   - 這個 diff 只改了同一節點的「誠實界線」那行,沒改這行;計劃的 `lands_in` 與落點表都說規格閘要記「門規則版本 13」。
   - 關聯:`Projects/規格閘不把不做節的詞算進風險_計劃.md` 的 [S5]「應是 12」綁同一個測試,測試已改釘 13,那條條款現在是錯的。
   - 引句:「門規則版本 `_DOOR_RULE_VERSION` 升到 13(常數旁說明加「13=2026-10-15 送出的前端語境與 PAYMENT 調整參數識別字例外」)」

2. 效能檢核目錄裡的各棧題數沒補 infra。
severity: minor
   - blocking: 否
   - 問題:`Systems/效能檢核目錄.md:201` 的「全表 kt=10/cs=6/…/dart=7」沒有 `infra=6`。
   - 同一行寫著「★這串數字每次加棧都要跟著改★」,這次加了新的棧別鍵 `infra`,卻沒改。
   - 該節點的 summary KEY 也沒提 infra。
   - 引句:「不是語言:起停後端、資料庫、容器的 shell 腳本與 e2e 設定程式。」

3. 計劃裡引用條款編號錯了。
severity: minor
   - blocking: 否
   - 問題:做法 7 的合併約定寫「本計劃的 S11 斷言回傳值本身(fixture 用 React 依賴的 package.json)」。
   - S11 是 `--check` 提醒那條。斷言 `_stack_key_for_file` 回 `infra` 的是 S16(`t_stack_key_e2e_path_is_infra`)。
   - 後合併的人照 S11 去找,會找到不相干的測試。
   - 引句:「本計劃的 S11 斷言回傳值本身(fixture 用 React 依賴的 package.json),順序接錯就紅,不靠「不含 vue 題」間接判。」

4. 計劃說「`tests/e2e/…` 被測試檔規則先擋掉」,實測不是。
severity: minor
   - blocking: 否
   - 問題:`_PITFALL_DIFF_TEST_PAT` 是 `(test_|_test\.|\.spec\.|/tests?/)`,比對的是 repo 相對路徑,根目錄的 `tests/e2e/a.ts` 沒有前導斜線。
   - 重現:`_PITFALL_DIFF_TEST_PAT.search("tests/e2e/a.ts")` 回 None,`_stack_key_for_file("tests/e2e/a.ts", d)` 回 `infra`。
   - 後果:根目錄 `tests/e2e/` 底下的檔其實會進 infra 題,和計劃「不在範圍」的說法相反。
   - 這個漏洞本身是舊的,但文件的宣稱不成立,要嘛改文件,要嘛補規則。
   - 引句:「被 `_PITFALL_DIFF_TEST_PAT` 先擋掉的測試命名檔(`tests/e2e/…`、`*.e2e.spec.ts`、`scripts/test_e2e.sh`)——四個消費者都先用它整支跳過,到不了 infra 規則」

5. 角色鏡頭的影響範圍,文件寫得比實際窄。
severity: minor
   - blocking: 否
   - 問題:實務隱患節與 `arch-alignment-lens` 只說「e2e 路徑底下的 `.ts` `.js` 改判不出」。
   - 實測:`e2e/helpers.py`、`seed/seed.py` 原本走 py 鍵判後端,現在是 `infra` 判不出;`db/seeds/orders.sql` 原本走 sql 鍵判後端,現在鍵是 None、角色也是 None。
   - 後果:這些檔不會再拿到後端卡,文件沒講。
   - 引句:「角色鏡頭:e2e 路徑底下的 `.ts` `.js` 改判「判不出」、不附前端卡;`.tsx` 照舊附。」

6. templates.md 的家節點沒同步,而且已有一句過期。
severity: minor
   - blocking: 否
   - 問題:`skills/lumos-design-loop/templates.md` 的家是 `Systems/每輪修補差異派工.md`,`impact --file` 只推它。
   - 那篇完全沒提〈前端補充〉、〈網頁前端類〉和 infra 選配行。
   - 它第 75 行還寫「圍欄後…三個 ### 小節」,現在是四個(多了〈網頁前端類〉)。
   - 說明被放在 `design-loop.md`,計劃自己承認這是變通。改 templates.md 的人只會看到家節點的舊版。
   - 建議:在家節點補一行 `SEE:` 指到 design-loop 那一節,並把「三個」改成「四個」。
   - 引句:「templates.md 的家是 [[Systems/每輪修補差異派工]],但那篇的負責範圍是修補差異材料,這兩段的說明寫在設計審流程這篇。」

7. 與 web-react 分支的交界約定:內容對得上,但稱呼有落差。
severity: minor
   - blocking: 否
   - 兩篇的約定一致:infra 判定排在 react/vue 之前、`_review_role_for` 保留 `infra` 回 None、id 集合與對照表各加各的、templates.md 各改各行。
   - web-react 那篇還指定了測試名 `t_infra_before_react_stack_key`。
   - 落差:web-react 那篇把本計劃稱為「web-notes 分支」,實際分支是 `EnzoHsieh-Android/web-fe-knowledge`(`web-notes` 是另一條,內容是 lint 相關提交)。
   - 這是另一個分支的檔,不在這個 diff 裡,合併時要更正。
   - 引句:「那份計劃在 web-react 工作樹、同一天在寫;編排者會請它的作者回指本計劃」

固定席(圖譜鏡頭)逐項判斷:
- `lumos-cli-read`、`測試假綠形態`、`design-loop`、`guard-kill`、`bound-tests-gate`、`lumos-cli-lifecycle` 這幾個 ★INVARIANT★ 都綁在 `scripts/lumos` 與 `scripts/test_lumos.py` 的既有行為上。這個 diff 的文件包沒有改它們宣稱的行為,判不影響。
- `design-loop` 的處置閘第五步只管計劃是否 `.md`、是否有 `[SN]`。本次新計劃是 `.md`,條款都綁測試,不影響。
- `pitfalls-code-loop` 和 `loop-convergence-recording` 是 RISK 節點。前者這次新增一段,內容與程式一致,見上面第 4、5 點的邊角。後者只被 RETIRE-IF 引用,不影響。

表態記錄的 `py-external satisfied — scripts/scenario_probe.py:1077` 屬程式那包,我沒核對。

最嚴重 severity:minor,blocking 共 0 條。

相關檔案(絕對路徑):
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-fe-knowledge/docs/lumos-toolchain-knowledge/Systems/規格閘.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-fe-knowledge/docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-fe-knowledge/docs/lumos-toolchain-knowledge/Projects/前端知識與風險詞_計劃.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-fe-knowledge/docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-react/docs/lumos-toolchain-knowledge/Projects/前端框架從vue分出_計劃.md`
