severity: major

臨時說明:我在 review-converge 工作樹做過一次 `git checkout 1bb556f8`,隨即切回原分支 `EnzoHsieh-Android/review-converge`。HEAD 同一個提交,沒有改到檔案。

我跑了 `python3.14 scripts/test_lumos.py -k residual`,75 項全過。

## Finding 1
severity: major
blocking: 是 — 手冊與工具寫成的流程互相矛盾,照做的人不是違規蓋章就是走不通殘留這條出口
引句:「只有經第二個獨立代理確認測不到、記成殘留(」
問題:reference.md 的第 3 問寫著,只有已經記成殘留的反例才放行。同一份手冊的判決規則仍是「五項全過才 legal」。但 `guard residual --add` 寫入前要求合約行已經有 `[audit:]`,工具與計劃都寫明「殘留是審計的產物」。
失敗情境:審計員要判定這條合約合法,第 3 問必須已有殘留。要記殘留,合約行必須已有 `[audit:]`。但 `[audit:]` 要等五項全過才能蓋,於是順序走不通。
- 照手冊逐字走:`guard residual --add` 會被擋(沒有 `[audit:]`),殘留永遠記不進去。
- 照工具順序走:審計員得在第 3 問還沒通過時先蓋 `[audit:]`,等於違反「五項全過才 legal」。
- 這會把殘留帶回「提出者自己認證」的老問題。
手冊沒寫順序(先蓋暫時戳記、重審,或殘留與審計一起寫),任何一種都得有明文。S8 測試只檢查關鍵詞存在,抓不到這個矛盾。
佐證:``file: `skills/lumos-project-notes/reference.md:548` ``(第 3 問放行條件)、``file: `skills/lumos-project-notes/reference.md:559` ``(記殘留要求已有 `[audit:]`)、``file: `scripts/lumos:18959` ``附近的 `_residual_add_problem`、``file: `docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:51` ``

## Finding 2
severity: minor
blocking: 否 — 回頭看得出來,有徽章與高風險代碼審兜底,但手冊把話說滿了
引句:「同一條合約同一個反例只准問一次」
問題:手冊、方法論與計劃都把它寫成硬保證,說「不能換代理重問到聽見想要的答案」。實作上「同一個反例」只靠兩樣東西認:自己取的 `--case` 編號,加上合約宣稱文字的指紋。
失敗情境:
- 編排者問過 `c1` 得到 `testable`,再用 `c1b` 或 `c1'` 問同一個壞法,就是新的一筆,可以換代理重問到 `untestable`。
- 改動一個字,指紋就變,舊問答全部對不上。
計劃的〈實作時定下的細節〉把「宣稱文字一改,舊問答對不上」當成特性寫,卻沒承認這是繞過口。〈實務隱患〉只承認「偽造問答」,沒提改編號與改字。
另外,`--add` 沒有檢查該反例對應的配方在 kill 帳上是不是真的 `survived`,「努力補過測試」沒有機械證據。手冊把「殺不掉」寫成可驗證的事,實際只靠第二個代理一句話。這兩點該明講成殘餘風險,並附回頭看的條件。
佐證:``file: `docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:46` ``、``file: `docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:73` ``、``file: `scripts/lumos:18880` ``(`--case` 只驗格式)

## Finding 3
severity: minor
blocking: 否 — 只是舊說法沒跟著改,不影響行為
引句:「風險分級多一條升 high:這次改到的檔」
問題:設計〈做法〉7 要求改 pitfalls-code-loop 講風險分級的段落。這次只新增一行 WHY,同篇 KEY 行仍寫分級只有三種結果:「命中風險型樣/新告警 → high;改動裡沒有程式檔 → light;其餘 standard」,沒提殘留索引命中也升 high。
失敗情境:讀 KEY 行的人(下一個 session 的 AI)會以為只有型樣與新告警能升 high。他們看到 `tier: high` 卻查不到型樣時,不知道是殘留索引造成的。
同一個漏法也出現在 design-loop.md:設計點名的是「講五問與防應試化的 KEY 行」,實際只新增了一行 WHY,KEY 行(69、70 行)沒動。
佐證:``file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:58` ``、``file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:67` ``、``file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:69` ``

## 已核對、沒問題的項目
- 設計〈做法〉7 列的說法:SKILL.md 範本、reference.md(五問段、標記清單、`guard` 指令)、06 指令表、方法論三處(`[audit:]` 列、`[residual:]` 列、Check T 列)、templates.md 徽章句都改到了,內容與程式一致。
- 手冊裡的審計五問沒有變成要人逐字貼的考卷:明寫「派工時照上面防應試化的規則改述措辭,語意不變」,S8 測試也檢查「逐字貼」只出現在否定句。定期無表抽考照舊,並補了「帶殘留通過當不合格」的比較口徑。
- 現有 ★INVARIANT★ 合約沒有被破壞。

最高等級 major,blocking 1 條(Finding 1);另 2 條 minor 不擋。
