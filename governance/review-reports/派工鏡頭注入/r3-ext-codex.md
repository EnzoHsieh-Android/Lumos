## 第 2 輪五條驗收

r2-f1:未解——§60 新增共用格分支說明，但 §93–99 仍同時要求 code-loop §7.6 改標記、design-loop §7.6 不動。

r2-f2:已解——明定將 vault-relative `node` 接成 `docs/<slug>-knowledge/` 下的 repo-relative 路徑；本 repo 實際只有一個 `docs/*-knowledge/`。

r2-f3:未解——第 3 版明確認受審工作樹計算清單，待審者仍可刪改關係隱藏固定席，僅把漏洞改列為界線。

r2-f4:未解——雖新增 ancestor 驗證，但本 repo 的 `refs/remotes/origin/HEAD` 不存在，fallback 到可移動的本地 `main` 並不能證明它是可信主線。

r2-f5:已解——實作清單已要求同步 `Systems/anchor-integrity` 的五錨點合約，並增加 `ANCHOR_FILES` 與 baseline 鍵集合交叉測試。

## Findings

### f1

severity: major  
blocking: 是

引句:「代碼迴圈的架構對齊席 §7.6「圖譜裡相關功能筆記」那格→同一行標記。」

file: `governance/review-reports/派工鏡頭注入/r3-snapshot.md:96`

同一段第 98 行仍要求「設計迴圈 §1/§7.6★不動★」，而 §7.6 是共用一格；第 64 行雖說要改成兩支，後面的具體修改清單仍照字面互斥。

### f2

severity: major  
blocking: 是

引句:「主線 tip=`refs/remotes/origin/HEAD` 解析到的分支,沒有就本地 `main`/`master`」

file: `governance/review-reports/派工鏡頭注入/r3-snapshot.md:83`

本 repo 執行 `git symbolic-ref refs/remotes/origin/HEAD` 實際回報「not a symbolic ref」，因此會落到本地 `main`；本地分支可移動且未驗證與 remote 的關係，用它做 ancestor 只能證明 base 在本地 main 歷史上，不能成立 spec 宣稱的可信主線隔離。

### f3

severity: major  
blocking: 是

引句:「固定席「清單」本身仍用工作樹圖譜算」

file: `governance/review-reports/派工鏡頭注入/r3-snapshot.md:83`

`impact --diff` 仍載入受審工作樹的 vault，分支作者可藉刪改關係或合約標記消除本應注入的固定席；把它寫進「誠實界線」沒有修復第 2 輪指出的清單完整性缺口。

### f4

severity: major  
blocking: 是

引句:「base 那版節點的合約行(`git show` 出來的正文裡以 ★INVARIANT★/★IRREVERSIBLE★/★CHECKPOINT★ 開頭的行)」

file: `governance/review-reports/派工鏡頭注入/r3-snapshot.md:85`

圖譜中的合約實際通常長成 `  KEY:★INVARIANT★...`，不是以標記開頭；照字面篩選會漏掉這些合約行，應沿用解析器語意或允許 frontmatter continuation 的 `KEY:` 前綴。

### f5

severity: minor  
blocking: 否

引句:「`kind` 與 `contract` 只印類別(INVARIANT/IRREVERSIBLE/CHECKPOINT/RISK/事故)」

file: `governance/review-reports/派工鏡頭注入/r3-snapshot.md:85`

`scripts/lumos` 的 `_impact_contract` 實際只產生 `INVARIANT`、`IRREVERSIBLE`、`RISK·<後綴>` 或空值，`CHECKPOINT` 不是該欄位的來源，事故則來自 `kind: incident`；RISK 去後綴可行，但實作者若按此句把五者當成同一 `contract` enum，會寫出與 JSON 現況不符的映射。

最高 severity：major；blocking 4 條。
