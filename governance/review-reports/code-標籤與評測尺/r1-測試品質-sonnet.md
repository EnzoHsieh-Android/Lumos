severity: blocker

（來源：代碼審 r1 測試品質席，sonnet，2026-09-15；方法=變異測試，每條附植入內容與實跑結果）

## 1. 新函式有沒有真的被接上去，沒有任何測試會發現

severity: blocker
blocking: 是
判準：這正是本次改動宣稱修好的核心缺陷，若佈線被撤回會悄悄退回原缺陷，而全部 82 支評測測試與唯一的端到端測試都不會翻紅。

引句:「verdict["_rn_eq"] = _macro_on(srows, "ranked_ndcg", "c_ranked_ndcg")」
file: `governance/eval/retrieval_eval.py:541`

★變異★：把報告段裡五個限縮鍵的賦值從限縮版改回全題平均（函式本體不動）。跑 82 個評測案例。★結果：82 passed, 0 failed——全綠★。另對四支相關測試逐一重跑，同樣全綠。

## 2. 新增的上界斷言是空話，且該測試測不出「三臂退化回一臂」

severity: major
blocking: 是
判準：此斷言聲稱驗證上界，但 fixture 裡候選總數只有 12，小於等於 24 在任何實作下都恆真，對「改回單臂或改成五臂」都無鑑別力；且同一測試把原本的嚴格全等弱化成子集，使它測不出這次合約擴張本身有沒有做對。

引句:「check("★仍有上界:free 側至多 3 條窗×k★", len([x for x in te if x.startswith("F")]) <= 3 * 8, str(te))」
file: `scripts/test_lumos.py:27330`

★變異★：把未標判定改回舊版單臂實作。跑該測試。★結果：7 passed, 0 failed——完全沒發現三臂邏輯被拔掉★。同一變異對新測試則是 5 passed, 2 failed（兩條翻紅）——新測試才是真正在守這次改動，舊測試修改後對此無感。

## 3. 「單一來源」斷言只比對原始碼文字，不驗實際辨識行為

severity: major
blocking: 是
判準：測試自稱要擋「兩份表各自寫死」，但用的是對原始碼的文字掃描，只要那個集合名出現在編譯呼叫的括號之間就判定過關，不檢查編譯出的正則實際能不能匹配集合裡的每一個詞。

引句:「_re.search(r"SYMBOL_RE\s*=\s*re\.compile\([^)]*SYMBOL_NAMES", src) is not None」
file: `scripts/test_lumos.py:27024`

★變異★：把正則改成文字上仍引用該集合、但推導時偷偷排除其中一個值（集合本身不動）。跑該測試。★結果：8 passed, 0 failed——全綠★，包含「詞彙表含那兩個值」那條（因為它只查集合、不查正則）。直接執行期驗證：此變異下被排除的那個前綴真的認不出來，production 行為已經壞了，8 條斷言卻無一翻紅。

總結：最嚴重 severity 為 blocker，blocking 共 3 條。
