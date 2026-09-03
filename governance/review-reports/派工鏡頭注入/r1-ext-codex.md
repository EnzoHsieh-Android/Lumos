## PRIOR-ART／現行裁定

### f1

severity: major  
blocking: 是

引句:「★比照★:本案不進 anchor、永不回 deny。」

file: `docs/lumos-toolchain-knowledge/Verification/2026-09-03_派工攔截點實測.md:71`  
file: `docs/lumos-toolchain-knowledge/Verification/2026-09-03_派工攔截點實測.md:73`

同日實測明定這種輸入改寫與提示注入技術同構，並把「該 hook 本身必須進錨點保護清單」列為硬約束；spec 卻直接排除 anchor。照做會漏掉已記錄的安全合約，且「鄰居 hook 未 anchor」不能推翻針對 `updatedInput` 新立的硬約束。

### f2

severity: major  
blocking: 是

引句:「照 d9:前 8 篇貼內容(節點名+`kind`+`contract`+`files`+該節點的合約行),其餘只列名。」

file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:114`

d9 明定 capped 規則只適用 code 迴圈，並逐字保留「design 迴圈維持原樣」；spec 卻把同一規則用於兩套模板。照做會擅自改掉 design-loop 的既有合約，而不是「直接採用」d9。

## 設計

### f3

severity: major  
blocking: 是

引句:「跑 `lumos impact --diff <範圍> --json`,取 `pinned: true` 的節點」

file: `scripts/lumos:16345`  
file: `scripts/lumos:16351`  
file: `docs/lumos-toolchain-knowledge/Projects/主動影響幅度偵測_計劃.md:241`

spec 沒要求把 hook payload 的 `cwd`／`CLAUDE_PROJECT_DIR` 以 `--repo` 傳給 subprocess；現行 `impact --diff` 省略 `--repo` 時只由 hook 行程 cwd 往上找 repo。這個缺口在鄰居 hook 的既有審查已判為 major，照字面實作會在 cwd 不等於目標專案時查錯 repo 或靜默放行。

### f4

severity: major  
blocking: 是

引句:「來自待審分支的文字若進了筆記,風險與手貼相同,本案不增不減。」

file: `docs/lumos-toolchain-knowledge/Projects/派工時自動補清單_計劃.md:58`  
file: `docs/lumos-toolchain-knowledge/Projects/派工時自動補清單_計劃.md:60`

同日前案已把「注入內容來自待審分支、攻擊者可控」列為兩輪都未處理的載荷安全 blocker；自動讀取並注入不等同編排者手動挑選貼上。照 spec 會把待審者可控的圖譜正文直接送進子代理 prompt，卻沒有來源隔離、內容界線或污染處置合約。

## 驗收

### f5

severity: major  
blocking: 是

引句:「子代理收到的 prompt 含固定標頭與 ≥1 篇固定席」

file: `scripts/lumos:16430`  
file: `scripts/lumos:16432`  
file: `scripts/lumos:16434`

`impact --diff --json` 合法成功時可以回傳 `results: []`、`meta.pinned: 0`；本次指定範圍 `HEAD~5..HEAD` 即是這種結果。驗收硬要求至少一篇，卻沒定義零固定席行為，會使正確的空結果永遠無法驗收，或迫使實作者虛構節點。

## 讓標記被寫的方式

### f6

severity: major  
blocking: 是

引句:「把 `LUMOS-IMPACT: {range}` 寫進派工詞模板當固定一行」

file: `skills/lumos-design-loop/templates.md:20`  
file: `skills/lumos-design-loop/templates.md:90`  
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:114`

design-loop 模板的審材是 spec 工作副本，沒有既定 git diff range；spec 也未定義 `{range}` 的生產者或替換規則。照字面加入固定佔位符會讓 design-loop 派工傳入無效範圍並 fail-open，標記存在但鏡頭永遠不注入。

## 一句話

已讀，無 finding。

## 為什麼是鏡頭，不是閘

已讀，無 finding。

## 措辭與失敗放行

已讀，無 finding。

## 安裝

已讀，無 finding。

## 未解與實務隱患

已讀，無 finding。

最高 severity：major；blocking 6 條。
