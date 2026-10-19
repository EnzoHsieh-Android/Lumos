severity: major

審的是「整合/知識同步」鏡頭,對象是凍結審材 r1-snapshot.md,對照工作樹 /Users/enzo/orca/workspaces/lumos-toolchain/web-react 與示範專案 order-web。
前掃已修的項目沒有重報。
spec 對 `scripts/lumos` 的現況宣稱(`_node_flavor_of`、`_stack_key_for_file`、`_idiom_skill_for`、`_ROLE_FRONT_EXTS`、`_RAN_EVIDENCE`、`typescript` 的 `code_exts` 缺 `.jsx`、`_EXTCODE_STACKS`)都開檔核對過,與程式一致。下面只列文件和手冊之間對不上、程式對不上的地方。

## F1 吸收逾期清單第 10 節時,「做完」的判準看不到,擋住它的 W1 又被丟給沒有落點的「別的組」
- 位置:〈做法〉F1 的「吸收《逾期回頭條件立案清單2026-10_計劃》第 10 節」,以及〈不做〉的比對表 W1。
- 引句:「新樣式有測試(S4–S7),order-web 下一次推送拿到綠燈」
- 引句:「比對表 W1(測試名寫中文句子會懸空)」
- 問題:本計劃宣稱做完第 10 節,判準有兩半。
  - S4–S7 是單元層,可以驗。
  - 「order-web 下一次推送拿到綠燈」沒有任何 S 條款或手動步驟去驗,而且依現況很可能驗不到。
- 具體例:
  - order-web 的筆記裡沒有任何 INVARIANT、IRREVERSIBLE、CHECKPOINT 合約行。
  - 它的 `[test:]` 全寫在驗收條款上,名字是中文句子,例如 `[test: 商品清單顯示名稱剩餘件…]`。
  - 合約測試閘只跑合約綁的測試,所以 order-web 現在推送時 vitest 那條路根本沒被走到,「綠燈」是空的。
  - 之後一旦加第一條合約並綁中文名,`JEST_TEST_RE` 要求第一字元是 `[A-Za-z_]`,中文名抓不到,測試會被判懸空,照擋。
  - 結果:第 10 節被標成做完,但「vitest 不再被誤擋」並沒有在 order-web 上被證明;擋住它的 W1 只在〈不做〉裡提一句,圖譜裡沒有節點或 REVISIT 接手。
- 佐證:
  - file: `scripts/lumos:5658`(`JEST_TEST_RE` 只收識別字,檔案內註解寫「含空白 NO MATCH」)。
  - file: `/Users/enzo/orca/workspaces/order-web/docs/order-web-knowledge/Projects/搶購下單畫面_計劃.md:214`(中文 `[test:]`)。
  - 在 order-web 知識庫 grep INVARIANT|IRREVERSIBLE|CHECKPOINT 無命中。
- 判準:照 spec 做,第 10 節會被標成做完,但判準沒被驗到,一個已知會擋住它的缺口也沒人追,會讓下一個接手的人誤信 vitest 誤擋已解。
severity: major
blocking: 是

## F2 全表題數、「八棧」字樣、目錄鏡像表與守衛測試的更新沒列進散落清單
- 位置:〈做法〉散落清單、〈提交方式〉第二個提交。
- 引句:「②只有兩份目錄筆記([[Systems/效能檢核目錄]]、[[Systems/linter精選目錄]] 的 React 段)」
- 問題:加第九棧 react 後,下列說法或程式都會過時,計劃一處都沒點名。
  - `Systems/效能檢核目錄.md:201` 的「全表 kt=10/cs=6/vue=6/…/dart=7」那串。SOP 第 9 步第一列就是它,歷史上漏過一次。
  - `Systems/效能檢核目錄.md:227` 起的「題目 id 對觸發字」鏡像表,要加 react 七列。
  - `Systems/棧別提問表態閘.md:112`:「sql 以外的八棧各多一題…全表 id 集合 50→58 題」。
  - `Systems/補新語言SOP.md:86`:「題數參考:kt=7、cs=5、vue=5…」。
  - `scripts/test_lumos.py:44268` 的 `t_extcode_single_source` 把八個棧寫死成 tuple,react-extcode 不在檢查範圍內。
- 具體例:實作者照散落清單做,這串數字不改,內容仍寫 vue=6、九棧缺 react。三個月後的人讀目錄會以為沒有 react 棧。react-extcode 的「同一組常數」守衛沒涵蓋它,有人改壞也不會紅。
- 佐證:
  - file: `scripts/test_lumos.py:44268`。
  - 另外 `t_stack_question_triggers` 的 docstring 寫「前端 .ts 歸 vue」,同一次要改。
- 判準:都是文件和測試同步遺漏,不會做出壞系統,但 SOP 已記錄這類遺漏每次必發生。
severity: minor
blocking: 否

## F3 〈提交方式〉的分法和 lands_in 對不上現況的「家」
- 位置:frontmatter `lands_in`,以及〈提交方式〉。
- 問題:
  - `lands_in` 列了 `Systems/pitfalls-code-loop`,但〈提交方式〉第一個提交的家節點清單和各小節都沒說要往那篇寫什麼。
  - `Systems/效能檢核目錄` 的 about_code 現在列了 `scripts/lumos`,它已是主程式的家。前一次的 commit dcd2a0b5 就是它和 `scripts/lumos` 同提交。SOP 第 10 步「兩份目錄筆記不是主程式的家」已過時,計劃照抄 SOP 把它排到第二個提交。
  - `linter精選目錄` 的 about_code 只有 `configs/detekt/android.yml`,它才需要獨立提交。
- 具體例:實作者要在第一個提交補效能檢核目錄的題數串,這時按計劃卻被排到第二個提交,題數串可能被拆到沒有程式的提交裡。`pitfalls-code-loop` 在 lands_in 卻沒內容,doctor 會看到「宣告要落地、實際沒動」。
- 佐證:
  - file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md` 的 about_code。
  - `git show --stat dcd2a0b5`。
- 判準:提交分法和落點宣告有出入,最壞多一輪提交閘,不會做出壞系統。⚠ 沒實際跑「每支檔有家」閘去驗純文件提交是否被擋,交編排者判斷。
severity: minor
blocking: 否

## F4 d2 翻案只記在決策裡,被翻的原筆記沒說要訂正
- 位置:〈做法〉B10「角色」那條、決策 d2。
- 引句:「這翻掉 [[Projects/代碼審前後端角色鏡頭_計劃]]〈已知限制〉裡」
- 問題:被翻的兩處原文仍會讓人讀成「Kotlin 後端判不出」。
  - 原筆記 `Projects/代碼審前後端角色鏡頭_計劃.md:87`:「.kt 判不出」。
  - 原筆記同檔 `:127`:「Kotlin 後端也判不出」。
- 具體例:三個月後有人查「Kotlin 後端的角色怎麼判」,先讀到角色鏡頭計劃的已知限制,和程式、d2 都矛盾。計劃沒要求在原筆記補一句「已被 d2 取代」,該計劃也不在 lands_in。
- 判準:純文件矛盾,不影響實作。
severity: minor
blocking: 否

## F5 「比對表」及其編號無處可查,〈不做〉的項目沒有落點
- 位置:〈現況〉B10 條、〈八格盤點〉、〈做法〉各小節標題(F1、F2、W2、W7、F7、B10)、〈不做〉。
- 引句:「比對表 W1(測試名寫中文句子會懸空)」
- 問題:全篇靠「比對表」的編號分節,但沒連結、也沒內嵌。在 lumos 的 docs、skills、scripts 搜,沒有哪個節點定義 F4、F10、W1、W11,只有本計劃自己提到。
- 具體例:接手的人看到「F4/F10、W11 各在別的組」,找不到「別的組」,也沒有 REVISIT 或 Issue。這違反專案鐵則 4(承認風險要附回頭看的條件)。
- 佐證:grep W11|F10 只在本計劃,以及四篇「世界解重新註解」調研裡出現,且沒有對應定義。
- 判準:對實作沒影響,影響的是三個月後能不能追到被延後的項目。
severity: minor
blocking: 否

## F6 散落清單漏 ARCHITECTURE.md,SOP 的過時列也沒人訂正
- 位置:〈做法〉散落清單。
- 引句:「README 兩份目前沒有支援語言表」
- 問題:
  - `ARCHITECTURE.md:21` 的「跨專案技術棧慣例 *-idioms:kotlin · vue · csharp · swift · node」已經少 python、java、dart,加 react 後更不全。計劃沒提這一處。
  - 計劃自己查出 SOP 第 9 步的「README 支援語言表」已不存在,但 SOP 沒在 lands_in,那一列和第 10 步會繼續誤導下一次補棧。
- 判準:文件精度。
severity: minor
blocking: 否

## F7 「前端值→skill」小表和現有 `_ARCH_IDIOM_SKILL` 的守衛不接
- 位置:〈做法〉`_idiom_skill_for` 那條。
- 引句:「不再用 if/else 夾副檔名表」
- 問題:現有守衛 `scripts/test_lumos.py:28953` 驗的是 `set(m._ARCH_IDIOM_SKILL.values()) | {"node-idioms"}`,每個 skill 都存在。計劃的新小表(react → react-idioms)若另立常數,這條守衛看不到它。
- 具體例:有人把 `skills/react-idioms/` 改名,只有 S16 紅,「對映表指到的每個 skill 都真的存在」那條守衛不會紅。計劃沒說小表放哪、要不要併進現有守衛。
- 佐證:file: `scripts/lumos:46124-46133`。
- 判準:S16 已釘住 react-idioms 存在,缺口小。
severity: minor
blocking: 否

## 風險類逐類
- 守衛面:計劃自己寫了(跑過證據放寬、B10 少問三題)。S5、S7、S24、S25 釘住,未見遺漏。
- 舊資料與舊帳、已在途分支:計劃的〈回退〉和〈實務隱患〉已涵蓋。已讀,無 finding。
- 跟其他計劃的交界:唯一的交界是逾期清單第 10 節,見 F1。其餘 doing 中的計劃(規格落成可驗收條件、雙向門放行等)沒有碰同一批符號。

最嚴重 severity:major。blocking 共 1 條(F1)。
