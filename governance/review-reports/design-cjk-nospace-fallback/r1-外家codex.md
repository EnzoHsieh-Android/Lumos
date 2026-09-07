severity: blocker

1. [blocker] 新題若直接塞進既有 goldset，評測會永遠關掉待測回退，量不到任何改善。blocking:是  
引句:「補 10 題無空白的中文查詢進既有的評測題庫」  
file: `docs/lumos-toolchain-knowledge/Projects/中文無空白查詢回退_計劃.md:33`

既有 search 評測的兩臂都固定傳 `--no-any`：`_search_arms()` 在 `governance/eval/retrieval_eval.py:115-121` 明確如此，`eval_search()` 在 `:348-353` 還特別說這是為了防回退污染 legacy-vs-ranked 尺。因此這 10 題放進既有 `search` 集後，基準與改後都仍是 0 候選；既量不到 bigram fallback，也不能校準 S4 門檻。

前案已經給出正確先例：`governance/eval/retrieval_eval_multiword.py:7-10` 明說「有無回退」必須另開 evaluator，不能塞進既有排序 gate。新題也應另建「無空白回退」實驗集，顯式比較 `--no-any` 與新回退；若要併入主 goldset，只能作不參與既有排序 gate 的獨立 category/metric。

2. [blocker] S4 的兩個候選目前都不可實作，且乙方案使用了已被同 repo 實證否決的分數門檻。blocking:是  
引句:「只把『不跨詞邊界、而且覆蓋率高』的字對標星」  
file: `docs/lumos-toolchain-knowledge/Projects/中文無空白查詢回退_計劃.md:56`

`_rank_tokenize()` 的輸出只有重疊字對，例如「檢索優化」→「檢索、索優、優化」；它不產生詞界資訊，見 `scripts/lumos:2054-2065`。所以甲所需的「不跨詞邊界」無法由這支 tokenizer 判定；若另加斷詞器，便違反本案的零依賴與「直接沿用」前提。

引句:「分數低於門檻的整批不顯示」  
file: `docs/lumos-toolchain-knowledge/Projects/中文無空白查詢回退_計劃.md:58`

乙也不可直接做：`_rank_score_candidates()` 明載 N、df、avgdl 都以每次候選集為 corpus，絕對分數不可跨查詢比較，見 `scripts/lumos:2120-2123`。入口栓前案甚至已因此刪除 top1 分數門檻；`_el_related_nodes()` 現在明定「分數只管排序，不管資格」，見 `scripts/lumos:6428-6441`。用 10 題校準單一門檻會隨候選集大小和詞頻漂移。

第三種還法是保留兩層訊號，不猜詞界也不設分數門檻：

- 永遠明示 `exact_candidates=0`／「原整串 0 命中，以下是弱回退」。
- 對每個 bigram 輸出文件覆蓋數，沿用現有 `_fb_cov` 與 `★token:0★` 機制（`scripts/lumos:2331-2372`）。
- 每筆結果顯示命中的字對數／總字對數，這是查詢內可比的 coverage ratio；可排序或分級，但不要把它偽裝成「圖譜有記」。
- JSON 同時回 `exact_candidates`、`fallback_used`、`query_bigram_coverage`，讓機器端不必解析提示文字。

3. [major] 計劃把排序 tokenizer 說成可直接搬到召回，但漏了召回端必要的清洗與資格語意。blocking:是  
引句:「用既有那支切詞器把整串切成字對，做『有任何一組命中就算』的召回」  
file: `docs/lumos-toolchain-knowledge/Projects/中文無空白查詢回退_計劃.md:41`

`_rank_tokenize()` 本身只是 tokenizer；真正已拿它做召回的入口栓先經 `_el_query_tokens()` 清洗、去重，再由 `_el_related_nodes()` 自行掃可見文字、判候選、最後交 BM25F，見 `scripts/lumos:6234-6253`、`:6408-6443`。入口栓不是「直接拿 `_rank_tokenize` 召回」，也沒有共用的 OR-candidate helper。

兩者語意亦不同：

- 排序層只重排既有候選，`scripts/lumos:2287-2301` 明文如此。
- 召回層需要決定 `--path`、`--code`、superseded、命中行、hidden count 等完整資格與輸出語意。
- 入口栓刻意包含 superseded，search 則有硬合約預設排除 superseded；不能照搬 `_el_related_nodes()`。

計劃必須明定是抽一個具有 scope/filter/hit-detail 合約的候選收集原語，或只在 `cmd_search` 現有預檢與主迴圈內擴 `_fb_terms`。目前「同一支直接用」掩蓋了真正的整合工作。

4. [major] 「直接查」與「機器呼叫」在實作上沒有可切割的入口，計劃宣稱的隔離不存在。blocking:是  
引句:「回退只加在『使用者直接查』那條路，機器對機器的呼叫不要動」  
file: `docs/lumos-toolchain-knowledge/Projects/中文無空白查詢回退_計劃.md:77`

所有 CLI search 最終都由 argparse dispatch 到同一個 `cmd_search(... any_terms=not args.search_no_any)`，見 `scripts/lumos:19929-19939`；函式沒有 interactive/user/machine 來源參數。換言之，任何沒顯式傳 `--no-any` 的 subprocess、腳本或 agent 都會吃到新預設。

目前正式評測端算安全，因 `build_goldset.py:44-50` 與 `retrieval_eval.py:115-121` 已顯式 `--no-any`；但這不證明「只影響直接查」，只證明兩個已知 consumer 有自行釘舊語意。落地前至少要建立 executable call-site 清單並選一項：

- 把新行為做成獨立旗標，先由人讀入口顯式啟用；或
- 接受 search CLI 預設整體改變，逐一把需要確定性的 consumer 釘上 `--no-any`，並加測試防未來漏接。

5. [major] 「回退後幾乎不可能回 0」不是本 vault 的事實，導致 S4 問題被錯誤建模。blocking:否  
引句:「退成字對召回之後，幾乎不可能再回 0 筆」  
file: `docs/lumos-toolchain-knowledge/Projects/中文無空白查詢回退_計劃.md:49`

我用現行 OR 回退模擬 bigram 召回，實際結果為：

- 「火星殖民氧氣稅率」：7/7 字對零覆蓋，0 候選。
- 「南極企鵝薪資扣繳」：7/7 字對零覆蓋，0 候選。
- 「海底火山租屋補助」：7/7 字對零覆蓋，0 候選。
- 「量子鳳梨保險理賠」：只有「保險」命中，21 候選；top score 2.0241。
- 「木星農場勞健保申報」：只有「申報」命中，1 候選；score 0.3069。

所以真正風險不是「零訊號必然消失」，而是兩態分化：

- 稀有字對仍誠實回 0。
- 只要一個常見字對命中，就可能突然擴成大量貌似合理的候選。

這也進一步否決單一 score threshold：21 候選的 2.02 與 1 候選的 0.31 使用不同 corpus，不能直接比較。評測應專門含三類：全字對零覆蓋、僅一個常見字對命中、多個連續字對命中。

6. [major] 計劃聲稱沿用「完全一樣」的觸發判準，但漢字 tokenizer 與現有 CJK 提示的字元域不同。blocking:否  
引句:「這三個判準跟現在那句提示用的完全一樣，直接沿用」  
file: `docs/lumos-toolchain-knowledge/Projects/中文無空白查詢回退_計劃.md:39`

現有 `_cjk_nospace_hint()` 把漢字、日文假名、韓文諺文都算 CJK，見 `scripts/lumos:2271-2287`；`_rank_tokenize()` 的 `_RANK_CJK_RE` 只接受漢字基本區與 Extension A，見 `scripts/lumos:2050-2065`。若直接共用觸發條件，日文或韓文查詢會進 fallback，tokenizer 卻可能產生空 token；若改成「≥4 漢字」，則已不是「完全一樣」。

計劃需明定本案只支援 Han，並讓提示、觸發與 tokenizer 共用同一判定原語；否則測試至少要覆蓋假名、諺文、混合標點與 Extension A。

7. [major] 翻案目標定得過大；原 d4 的核心建議沒有被新證據推翻。blocking:否  
引句:「這是對 2026-08-22 那條『0 筆時提示加空白』的翻案」  
file: `docs/lumos-toolchain-knowledge/Projects/中文無空白查詢回退_計劃.md:46`

原決定逐字內容位於 `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:58-61`：它同時裁定「中文查詢要在概念之間加空白」、注入操作指引、0 命中時提示改寫，以及同步 skill/index；理由是 Landmark 2026-08-11 的實測規則和 Enzo 要求全專案注入。

本計劃自己在 `:82-84` 又主張那條加空白紀律不要拿掉，因為加空白仍較準。這表示被推翻的只有「0 命中時只提示、不自動弱召回」的產品行為，不是 d4 的核心查詢指引。若整條 d4 標 superseded，會連仍有效的文件與操作紀律一起判死。

較準確的處理是新增補充決定，明示 d4 的①與③仍有效，②從「只提示改寫」演進為「保留加空白建議＋明示 exact=0＋提供弱回退」。只有在新評測證明不再需要空白查詢紀律時，才足以翻掉整條 d4。
