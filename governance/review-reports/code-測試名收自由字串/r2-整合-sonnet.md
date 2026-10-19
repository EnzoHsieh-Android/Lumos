severity: major

我只讀了文件那半修補和對應的程式。找到 1 條 major、5 條 minor。修補有沒有造成行為回歸,我沒獨立驗(見最後)。

**1. 計劃和 Systems 節點都說「Playwright 綁 describe 標題會判證不出」,程式實際判紅**
severity: major
- blocking: 是
- 對象:計劃 做法 4 的「(代碼審 r1 後改)playwright 改成 `regex_tail`…代價:Playwright 綁 describe 標題會選到零支、判證不出」,以及 `Systems/test-profile-multiplatform.md` 新增的「綁 describe 標題在 Playwright 上會選到零支、判證不出」。
- 實測:我用假的 `-g`(只在標題路徑結尾符合才印 `1 passed`)跑修後 `_run_bound_tests`。
  - 檔裡有 `test.describe('結帳流程', …)`,底下有 `test('按鈕會停用')`。
  - 掃描集合是 `['按鈕會停用','結帳流程']`,所以 Check T 看這兩個都是「綁好了」。
  - 綁 `按鈕會停用` 得 `green`。
  - 綁 `結帳流程` 得 `('red','rc=1 Error: No tests found')`,不是 `unproven`。
- 佐證:`file: scripts/lumos:54870` 附近的 `elif rc != 0:` 先判 red,「證不出」只在 rc 為 0 且證據樣式缺席時才會出現。真 Playwright 零支本來就回 1,同一篇 FACT 行自己也寫「對不到印 No tests found 並回 1」。
- 影響:三個月後的人照文件預期看到「證不出」,實際看到紅燈和 `No tests found`。兩種都擋推送,但文件預告的狀態不是程式的狀態。
- 還有一處同病:計劃 做法 4 的「綁的是 describe 標題時,…數出來是 1,照常跑整組;那是作者要的語意」這句沒加 Playwright 例外。修後對 Playwright 是錯的,只有 Jest 和 Vitest 還成立。
- 歸因:有證據的修復造成的文件新錯。這是「Playwright 改錨在結尾」帶來的行為變更,文字是這輪修補寫進去的。修前版本我沒法比,我的假指令只認錨定樣式,修前的未錨定指令兩支都判紅,不能拿來對照。
- 引句:「代價:Playwright 綁 describe 標題會選到零支、判證不出」

**2. 計劃 做法 2 的剝註解,首段還在講一個不存在的新模式,跟緊接著的補丁互相矛盾**
severity: minor
- blocking: 否
- 首段寫「新增 `comment_strip: "c-style-strings-kept"` …node-jest、playwright、dart 改用它;…其餘 profile 不動」,下一條子項卻寫「不另開新模式,直接把 `c-style` 換成…所有用 c-style 的語言一起改」。
- 程式裡只有 `c-style` 和 `c-style+strings` 兩種(`file: scripts/lumos:6412`)。`c-style-strings-kept` 全 repo 只剩計劃這一處(`Projects/測試名收自由字串_計劃.md:74`)。
- 後來的人若只讀首段,會去找或實作一個不存在的模式。
- 歸因:未判定。r1 折入時就留下的矛盾,這輪修補沒清。
- 引句:「新增 `comment_strip: "c-style-strings-kept"`,一趟由左往右的交替比對」

**3. `Systems/規格閘.md` 的撞名那行沒跟上修補**
severity: minor
- blocking: 否
- 該行(`:159`)寫「名稱篩選型平台(regex/plain)…(`_name_filter_collisions`,不分大小寫)」。實際有三處不符:
  - 型別多了 `regex_tail`。
  - 數的是 `_raw_test_titles` 的「篩選選得到的全部標題」,不是只數可綁定的。
  - `plain`(dart)是分大小寫的(`fold = name_filter != "plain"`)。
- 這輪修補只動了 `bound-tests-gate`、`guard-kill`、`test-profile-multiplatform` 等,沒動 `規格閘.md`。
- 歸因:有證據的修復遺漏。修補改了判定,同步清單漏了這一篇。
- 引句:「名稱篩選型平台(regex/plain)跑之前先數撞名(`_name_filter_collisions`,不分大小寫)」

**4. 程式註解還寫 `name_filter=regex`**
severity: minor
- blocking: 否
- `file: scripts/lumos:5831` 寫「name_filter=regex:跑單支用 -g,名字要跳脫」,但同一個 profile 在 `:5837` 已經是 `regex_tail`。
- 計劃 做法 7 要求同步的正是這條 playwright 註解。
- 引句:「name_filter=regex:跑單支用 -g,名字要跳脫(_run_cmd_expand)」

**5. S25 的手動 grep 照它自己的詞跑會有殘留,不符「只剩 Maestro 與 scaffold」**
severity: minor
- blocking: 否
- 修補把 grep 詞擴成「必須是識別字」「識別字名」。這兩個詞會命中兩篇 status 為 todo 的計劃:
  - `Projects/Android側UI測試綁圖譜工作流_實作計畫.md:39`、`:167`、`:235`,寫「Kotlin 測試函式名必須是識別字——反引號中文名綁不上」。
  - `Projects/Android側UI測試綁圖譜工作流_計劃.md:123`、`:140`,寫「`guard bind` 當場 rc2 拒收…照抄會直接失敗」。
- 修後 `guard bind` 收句子名,這些說法已經不對。它們既不是 Maestro,也不是 scaffold,做法 7 清單也沒列。
- `Projects/多平台合約測試綁定_計劃.md` L117 的同類句子在 L112 的「已被取代」引言底下,可以算帶註記,不計入。
- 歸因:有證據的原有漏查。這兩篇是舊的待辦計劃,修補只是把 grep 詞擴大才讓它們現形。
- 引句:「只剩 Maestro 那幾處與 scaffold 的識別字限制,且各處指到本篇」

**6. Windows 擋字元的規則只寫進一部分文件**
severity: minor
- blocking: 否
- 程式有 `_WIN_CMD_SPECIAL = "&|<>^%\"!"`,Windows 上含這些字元的名稱判不合法(`file: scripts/lumos:6071`、`:6116`)。
- `bound-tests-gate.md` 和 S64 有寫。但計劃 做法 1 的 `_test_name_ok` 定義,以及 `Systems/test-profile-multiplatform.md` 的 `_test_name_ok` 那條,都還寫「引號…都可以」,沒提 Windows 例外。
- S64 只舉 `& | %`,程式還有 `< > ^ " !`。
- 歸因:有證據的修復遺漏。
- 引句:「中文、空白、括號、冒號、引號、全形標點都可以」

**已核對、不是問題**
- 決策 d1 與修後程式一致:只改名稱規則,`IDENT_RE` 留給 scaffold,多根多 profile 那條決策沒動。
- 撞名看全部標題:`_raw_test_titles` 和 `_name_collision_reason`,推送前閘、規格閘、guard kill 三處共用,文件描述屬實。
- `regex_tail` 的撞名只數結尾符合的測試標題:實測 `relogin`、describe 的 `login` 都不算撞名,而 `regex` 模式會算。
- `file_name_match`:我用多平台設定寫 `["*.e2e.ts"]`,掃描確實掃得到。
- FACT 行帶 `[來源:外部] [confirmed:] [查:]`;新 REVISIT 行格式正確;文件裡綁的 265 個 `t_` 測試名在 `test_lumos.py` 都有 `def`。
- 摘要行分類與每支檔有家沒問題:`lands_in` 裡 Systems 節點的 `about_code` 都有 `scripts/lumos`;計劃把 `lumos-guard` 拿掉的說明是對的。
- 「測試名只能是識別字」舊說法在 `reference.md`、`linter精選目錄`、`test-profile-multiplatform`、`Web示範前端缺口_調研` 已改掉。
- `Web示範前端缺口_調研` 的 W1 列:這輪已補「2026-10-15 已由…處理」,表內計數也已改成 0/0,沒有矛盾。
- 調研筆記連到別分支的三篇計劃,依指示不算 finding。

**三問的回答**
1. 原問題的修復效果:撞名、錨定、`file_name_match` 這幾條,我有跑程式驗證行為;文件描述屬實(第 1 條和第 3 條除外)。
2. 修補處的相鄰路徑:Playwright 綁 describe 的路徑,修補把「通過」變成「紅」,見第 1 條。
3. 新發現在修前、修後各是什麼:
   - 第 1 條的修前結果未判定。我的假 `-g` 只認錨定樣式,不能代表真 Playwright 在修前的行為。
   - 第 2 到 6 條是文字或註解問題,沒有可比的修前執行行為,其中第 5 條是修前就存在的漏查。
   - 我沒跑全套測試,也沒驗 S52 到 S56 的效能與記憶體條款。

我的臨時目錄在 `/tmp/lumos-seat-work/code-測試名收自由字串/整合-sonnet/`(假 repo、探針腳本、修前版 `lumos_before`),沒有程序開著,請編排者收貨後用字面絕對路徑刪。

最嚴重 severity:major;blocking 共 1 條(第 1 條)。
