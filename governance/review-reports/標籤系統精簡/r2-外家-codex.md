severity: major

（來源：設計審 r2 外家否決席，codex-cli，2026-09-14；逐字稿切出的報告本體）


1. 前輪第 1 條：另有自動召回入口，搜尋提示罩不到
severity: major
blocking: 是；清理會改變自動召回結果，必須納入影響範圍與驗收。
`_el_related_nodes` 自行掃描含 frontmatter 的可見文字，明文不走 `cmd_search`，因此鏡像清理也會改變入口栓的相關節點候選。
只在 `search` 加提示無法涵蓋這條路，應補上入口栓的行為取捨與清理前後驗收。
引句:「字面搜尋那條路由 [S11] 處理」
file: `scripts/lumos:8233`
file: `scripts/lumos:8246`

2. 前輪第 1 條：提示的判準仍未寫完整
severity: minor
blocking: 否；可局部補齊觸發規則及輸出通道。
「看起來像」未界定多詞中的標籤、大小寫及 `--regex`，也未指定提示走 stderr。
既有搜尋明確保護 `--json`／`--files-only` 的 stdout，應沿用此約束並列出正反例。
引句:「搜尋的查詢字串看起來像 `type/…` 或 `status/…` 時，印一行白話提示指向結構化查詢」
file: `scripts/lumos:3008`
file: `scripts/lumos:3122`

3. 前輪第 2 條：鏡像清理仍不能保證排序分數不變
severity: major
blocking: 是；核心驗收承諾已被既有評分函式反例證偽。
拆開退場家族是對的，但 BM25F 的文件數、詞頻統計與平均長度取自候選集，鏡像清理改變候選集後，留下的節點也會改分。
記憶體實驗保持合成後欄位完全相同，查 `doing`、候選由 A/B 減為 A，既有函式給 A 的分數由 0.8838 變成 0.4561。
應把承諾限於固定候選集與其他評分輸入，另驗實際搜尋結果。
引句:「因此一篇節點有沒有做過鏡像清理，排序分數完全相同。」
file: `scripts/lumos:2749`
file: `scripts/lumos:2770`

4. 前輪第 3 條：「沒有家族專屬程式碼」仍是假宣稱
severity: minor
blocking: 否；修正盤點結論並交代既有值域檢查即可。
`priority/` 有專屬 `_PRIORITY_ENUM`，超出 P0–P3 會直接產生錯誤，並非只有通用查詢與排序消費。
應更正此句，並明訂凍結後這道硬錯誤保留或退場，避免與新增警告的規格打架。
引句:「那兩個家族沒有家族專屬程式碼」
file: `scripts/lumos:4376`
file: `scripts/lumos:4389`

第 4 條：已修好

5. 前輪第 5 條：既有鎖不能直接保證批次互斥
severity: major
blocking: 是；照目前設計沿用整批鎖，仍可發生併發覆寫。
既有鎖以 30 秒視為過期，接手時不驗原程序是否存活；整批清理超時仍在執行，也會被另一程序接手。
此外，鎖目錄建立失敗會直接放行寫入，`decision-reindex` 也直接呼叫未自帶鎖的寫入原語，因此「寫入原語都在用」不成立。
應定義逐檔鎖內重讀與寫入，或提供適合批次的鎖生命週期，並明訂拿不到鎖時停止。
引句:「併發靠既有的鎖」
file: `scripts/lumos:11085`
file: `scripts/lumos:11115`
file: `scripts/lumos:24406`
file: `scripts/lumos:11800`

6. 前輪第 6 條：檔名清單無法還原清理前的未提交內容
severity: major
blocking: 是；指定的回滾會連同使用者原有修改一起丟棄。
取消乾淨檢查後，同一檔案可以同時含原有未提交正文與本次標籤刪除，按檔名做 git 還原會把兩者一起退掉。
原子寫入只是替換整份檔案，不會保留清理前版本，檔名也無法重建那些內容。
應保存可恢復的清理前內容或可逆差異，並把中斷時的紀錄持久化順序納入驗收。
引句:「退回就是對那份清單做 git 還原，不依賴「工作目錄本來很乾淨」這個假設。」
file: `scripts/lumos:11038`
file: `scripts/lumos:11057`

第 7 條：已修好
第 8 條：已修好

7. 新洞：S2 沒涵蓋解析器真正產出的空值
severity: major
blocking: 是；核心 helper 的合法輸入邊界尚未封閉。
現有解析器把空白的 `status:`／`type:` 解析成 `[]`，也接受非空清單，並非只會產生字串。
只按條款排除缺席與空字串，仍可合成 `status/[]` 或清單字面值；應明訂非字串與純空白字串的處置，測試須經真解析器進入 helper。
引句:「純量欄位缺席或是空字串時，**不合成該家族的標籤**」
file: `scripts/lumos:275`
file: `scripts/lumos:290`

8. 新洞：S10 把要新增的兩個名稱刪掉了
severity: minor
blocking: 否；補回明確枚舉及驗收即可。
r2 只說「兩個前綴」，卻刪去 r1 明列的 `PRIOR-ART:` 與 `REVISIT:`，留下兩個彼此未綁定的使用實例。
應在 S10 明列新增值，並同時驗證兩者通過快檢、搜尋區域標記正確及錯字仍被提示。
引句:「摘要符號詞彙表：先修正則，再收兩個前綴，而且兩份表要合成一份。」
file: `scripts/lumos:2638`
file: `scripts/lumos:4031`

最嚴重 severity：major；blocking 共 5 條。
