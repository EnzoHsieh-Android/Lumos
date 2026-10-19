severity: major

審查範圍是文件包 `r1-docs.patch`,對照 web-react 工作樹的 `scripts/lumos` 與 `scripts/test_lumos.py`。我跑了 `lumos lint`(5 篇,0 問題)、`lumos doctor` 和 `-k stack_question_triggers`(59 過)。

程式與文件對得上的部分:
- 題數 60 到 68,react 八題 id 與觸發字逐條對上,`min_lines: 2` 只有 react-parallel 帶。
- 計劃裡綁的測試名全部存在,包含 `t_react_idioms_rule_names_known`。
- `_ARCH_IDIOM_SKILL`、`_ROLE_FRONT_KEYS`、`node-vitest` 別名都在。
- Kotlin 判法(Android 跡象優先、只認伺服端外掛、取最近的建置檔)與決策 d2 的文字一致。
- eslint 規則代號 `react-hooks/rules-of-hooks`、`react-hooks/exhaustive-deps`、`react/jsx-key`、`react/no-array-index-key`、`no-floating-promises`、`no-misused-promises` 都是真規則,未實跑的已標明。
- `skills/react-idioms/SKILL.md` 和新範本沒有掛進任何 `about_code`,但 `vue-idioms`、`node-idioms` 也沒有,跟現有慣例一致。

1. 交界計劃的分支名寫錯,兩處
severity: major
blocking: 是
- 問題:計劃兩處寫「`Projects/前端知識與風險詞_計劃`(web-notes 分支)」,實際這篇在 `web-fe-knowledge`。用 `git ls-tree` 查,`web-notes` 上沒有這個檔。`web-gaps` 的標註是對的。
- 例:三個月後的人照「後合者補測試」去找對方分支,會去 `web-notes` 找不到計劃,也對不到 infra 判定的實際內容。
- 佐證:`git ls-tree EnzoHsieh-Android/web-fe-knowledge -- docs/lumos-toolchain-knowledge/Projects/前端知識與風險詞_計劃.md` 有命中;web-notes、web-gaps、web-ledger 都沒有。
- 重現:同一條 `git ls-tree` 對 web-notes 回空。
引句:「`Projects/前端知識與風險詞_計劃`(web-notes 分支)也改同一批地方」
(另一處同誤:「需求風險面的前端面、設計審派工範本的前端改述、前端測試品質指引:`Projects/前端知識與風險詞_計劃`(web-notes 分支)在做」)

2. 交界約定缺角色鏡頭的保留要求,兩邊測試分工也沒對齊
severity: minor
blocking: 否
- 對方計劃的約定是:改 `key == "vue"` 那一行時,要保留「`infra` 回 None」。本計劃的交界節只講 `_stack_key_for_file` 的順序和測試 `t_infra_before_react_stack_key`,沒提這條。
- 對方另有自己的 S11(用 React 依賴的 fixture 斷言回傳值),跟本計劃要補的測試重疊,沒有說誰負責哪一支。
- 目前 `_ROLE_FRONT_KEYS = {"vue","react"}` 沒有碰 infra,不會出錯。
- 本工作樹也沒有 `t_infra_before_react_stack_key`,這是設計上留給後合者的,不算缺漏。
引句:「兩篇誰後合進主線,誰負責接順序並補一支測試斷言「React 專案裡 `e2e/` 底下的 `.ts` 回 infra、`src/` 底下的 `.tsx` 回 react」(`t_infra_before_react_stack_key`)」

3. 活文件裡「React 一律歸 vue」的舊說法沒改
severity: minor
blocking: 否
- `代碼審前後端角色鏡頭_計劃.md` 同一份 diff 已經改了第 62 和 85 行附近,但這幾處沒動:
  - 「React、Svelte、Angular 一律被歸成 vue」
  - 「(b) 題組鍵對應角色:vue → 前端;…`.svelte/.tsx/.jsx/…`(現在沒有題組鍵)→ 前端」
  - S6 條款「沒有 android 匯入的 .kt 判不出」,現在只有找不到可辨認的建置檔時才成立。
- `Systems/arch-alignment-lens.md` 第 18 行還寫「慣例 skill 依副檔名(kotlin/csharp/vue-idioms)」。
- `scripts/lumos` 的 `_stack_key_for_file` 內有一行舊註解:「前端 .ts/.js 原本回 None…改歸 vue 棧」。
- 其餘 grep 的結果:README、ARCHITECTURE、ONBOARDING、`scripts/templates`、`skills/` 都沒有殘留的舊說法。
引句:「React、Svelte、Angular 一律被歸成 vue(另案 [[Projects/前端框架從vue分出_計劃]])。」

4. 棧別提問表態閘裡「八棧各多一題」那句沒改
severity: minor
blocking: 否
- 計劃的散落清單第②項和 SOP 第 9 步都列了這句要改。實際只在後面追加新節,第 113 行原句沒動。
- 現在 `_EXTCODE_STACKS` 有 9 棧,「八棧」和「50→58」已是歷史數字。
引句:「題目表 sql 以外的八棧各多一題 `<棧>-extcode`,全表 id 集合 50→58 題」

5. 計劃的「現況」與「八格盤點」是改動前的現狀,標題沒講
severity: minor
blocking: 否
- 標題是「現況(2026-10-15 讀程式確認)」,內文寫「`.tsx` 判成 vue」「沒有 `react` 鍵」「沒有 `skills/react-idioms`」。
- 這份計劃已是 `status: doing`,有〈實作紀錄〉。不看實作紀錄的人會當成現行程式的樣子。
- 同篇的實作紀錄寫「條款 S1–S29、S31–S42 都綁了真測試」,漏了 S43(它也綁了測試)。
引句:「判棧**:`.ts/.tsx/.js/.jsx` 走 `_stack_key_for_file` → `_node_flavor` → `_node_flavor_of`,依賴裡有 `_NODE_FRONTEND_MARKERS`(vue、nuxt、react、next、svelte、@angular/core、solid-js、preact)任一個就回 `vue`。」

6. 對方計劃還沒合進這個分支,`lumos doctor` 有兩個壞連結
severity: minor
blocking: 否
- `lumos doctor` 回報 `[[Projects/前端知識與風險詞_計劃]]` 和 `[[Projects/測試名收自由字串_計劃]]` 兩個連結連到不存在的筆記。它們住在別的分支,這個分支單獨合進主線就會留下這兩個壞連結。
- 這兩個連結是計劃 `related` 欄新加的。
- 合併順序要先排好,或補一句說明。
引句:「  - "[[Projects/前端知識與風險詞_計劃]]"」

最嚴重 severity:major,blocking 共 1 條(第 1 條;第 2 至 6 條為 minor)。
