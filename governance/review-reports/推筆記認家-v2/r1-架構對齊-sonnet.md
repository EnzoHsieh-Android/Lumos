severity: major

## 四問逐答

**1. 分層與依賴方向**
S1 抽出的「家對照表」純函式(輸入每篇 type/status/about_code、輸出 檔→家)方向沒問題——開檔核對 `_nodehome_homes`(`scripts/lumos:17995`)本體只讀 `n["type"]`/`n["status"]`/`n["about"]`,不碰 git 快照欄位,兩邊(nodehome 的 `side.notes`、impact 的 `env.notes`)本來就是同形狀字典,抽出來給兩邊各自餵料是往下多一層共用工具,方向正確,這點延續 v1 r2/r3 已核對過的結論。

但新加的「確認過的家」(S2/名詞段)沒有交代要呼叫誰。這支檔的 `_node_code_ref_tokens`(`scripts/lumos:16479`)docstring 明寫「★refcheck、改檔前推筆記、每支檔有家三處共用這一支★——推筆記認得的,跟每支檔有家認得的,一定一樣(兩套算法一定分岔,而分岔時沒有東西會翻紅」(`scripts/lumos:16482-16483`)——這正是「改檔前推筆記」(本案 S2 要改的同一支 hook)現有的「反引號」入口實際呼叫的東西:`_impact_reverse_lookup`(`scripts/lumos:21043`)透過 `_refcheck_scan`/`_node_code_ref_tokens` 掃 inline-code 反引號範圍;`_nodehome_refs`(`scripts/lumos:18094`)也是同一支抽取。但 S2 明寫「不必正文用反引號寫這支檔」(`governance/review-reports/推筆記認家-v2/r1-snapshot.md:61`),名詞段定義是「那篇的摘要或正文出現這支檔的完整路徑或檔名(含副檔名)」(`r1-snapshot.md:49`)——這是不限反引號範圍的全文字串比對,字面上不可能是呼叫現有那支「三處共用」的函式來實作,見 F1。

**2. 命名與錯誤處理**
旋鈕 `LUMOS_IMPACT_HOME`(S7)、顯示標記「★家★」(S8,`r1-snapshot.md:67`)沿用既有 `★關於★`/`★COMBO★` 星號慣例——開檔核對 `scripts/hooks/claude/impact-hook.py:647`(`ab = "★關於★" if x.get("about_hit") else ""`)與 `scripts/hooks/claude/impact-hook.py:578/598/618`(`★COMBO★`)寫法沒變,跟 v1 r3 已核對的結論一致,沒有退步。S11 掛進「每支檔有家」既有違規家族(`_nodehome_evaluate`)、S14 新腳本沿用 `governance/eval/refresh_labels.py` 的子命令殼——這兩處 v1 r2/r3 已核對過,本輪重讀程式沒有發現復發或新的命名分歧。

**3. 第二種做法**
有,見 F1——「確認過的家」是一套新的「文字有沒有提到這支檔」判法,跟既有反引號抽取(`_node_code_ref_tokens`)並存卻不共用。

**4. 落點合不合理**
`r1-snapshot.md:11-14` 的 `lands_in`(retrieval-ranking、節點還原、每支檔有家)跟 `r1-lens.txt:31-34` 列的落點現況三篇完全對上,三篇都已存在、不必另開——這是 v1 三輪已收斂的結論,這次的兩處改寫(分兩級、抽查降級)沒有牽動落點,不需要新增或搬動節點。

## 正式發現

### F1 「確認過的家」引入一套不共用的文字比對法,跟現有「三處共用一支抽取」的明文設計互相矛盾
severity: major
blocking: 是 — 判準:major 錨定「引入了第二種做法」,本案的「確認」判法字面上無法沿用既有共用函式,勢必另外實作一套。

「確認過的家」定義成「那篇的摘要或正文出現這支檔的完整路徑或檔名(含副檔名)」(`r1-snapshot.md:49`),S2 更明寫這條路徑「不必正文用反引號寫這支檔」(`r1-snapshot.md:61`)。但這支檔現有「正文有沒有提到這支檔」只有一套實作:`_node_code_ref_tokens`(`scripts/lumos:16479`)只抽反引號包住的 inline-code span(`INLINE_CODE_RE.findall`),docstring 直接寫死「★refcheck、改檔前推筆記、每支檔有家三處共用這一支★……兩套算法一定分岔,而分岔時沒有東西會翻紅」(`scripts/lumos:16482-16483`)。三個現有呼叫點——`_refcheck_scan`(`scripts/lumos:16505`)、`_impact_reverse_lookup`(`scripts/lumos:21043`,本案 S2 要改的「改檔前推筆記」本尊拿它做既有的反引號入口)、`_nodehome_refs`(`scripts/lumos:18094`,「每支檔有家」拿它判「別人的檔有沒有被正文提到」)——全部走反引號範圍+top_dirs 過濾(完整路徑)或裸檔名跨檔唯一性(裸 token),沒有一個是「摘要或正文任意位置出現路徑/檔名子字串」這種寬鬆比對。

S2/名詞段既沒有指名要重用這支共用函式,字面定義也跟它的行為對不上(有沒有反引號、要不要唯一性都不同)——依現有「同一函式防兩套算法分岔」的慣例,最可能的接法是照字面另寫一支「path/檔名 in text」的獨立子字串檢查,跟本案自己在 S1 才剛立下的「一支算法,兩邊餵料」精神背道而馳,也踩上這支檔明文警告要避免的「分岔且沒有東西翻紅」風險——這條新判法一旦跟既有反引號抽取產生落差(例如同一支檔在正文提到路徑但沒加反引號,或反過來只用裸主檔名而非「檔名含副檔名」),refcheck/nodehome/推筆記三邊也不會有測試機械擋下這個落差。

引句:「那篇的摘要或正文出現這支檔的完整路徑或檔名(含副檔名)」(`governance/review-reports/推筆記認家-v2/r1-snapshot.md:49`)

佐證 file: `governance/review-reports/推筆記認家-v2/r1-snapshot.md:61`(S2「不必正文用反引號寫這支檔」)、`scripts/lumos:16479-16483`(`_node_code_ref_tokens` docstring「三處共用這一支……兩套算法一定分岔」)、`scripts/lumos:21043`(`_impact_reverse_lookup`,改檔前推筆記既有反引號入口)、`scripts/lumos:18094`(`_nodehome_refs`,每支檔有家既有反引號抽取)

---

總結:最高 severity major,blocking 共 1 條
