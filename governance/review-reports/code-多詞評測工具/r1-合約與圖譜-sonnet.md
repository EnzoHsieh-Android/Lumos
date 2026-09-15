severity: major

# 鏡頭：程式跟文件講的是不是同一件事

材料範圍：凍結的 code-r1.patch（`governance/eval/retrieval_eval_multiword.py` + `scripts/test_lumos.py`），以及派工詞明確要求核對的圖譜節點與卷證（`docs/lumos-toolchain-knowledge/Systems/多詞評測.md`、相關 Verification/Issues/Projects 節點、`governance/eval/multiword/relabel-2026-09-15/`）。這些圖譜節點都在本批改動的提交範圍內（`375585bd..HEAD`），不是舊帳。

## 核對過的東西（沒有問題的部分）

- `python3 scripts/lumos impact --file governance/eval/retrieval_eval_multiword.py` 指到的家是 `Systems/多詞評測.md`。它的 FLOW、候選池三來源、污染守衛、標註檔兩格式、`TEST:` 列的四支測試名，逐條核對都跟 diff 的實作一致，四支測試也真的都在（`python3 scripts/test_lumos.py -k mw_` 18 個斷言全過）。
- 數字核對：528 篇／5.53MB（作者表態）、528 篇圖譜現況掃描出來一致；題庫 10 題、`mw-pool.json` 逐題查詢文字比對相符；重標基線 `nDCG@5 0.653／MRR 0.90／P@5 0.70／6/10 必看／8/10 至少有用` 與 `governance/eval/multiword/relabel-2026-09-15/基線-2026-09-15-釘fb46914c.txt` 逐字相符；`fb46914c` 提交下 `docs/lumos-toolchain-knowledge/` 確實是 521 篇 `.md`（`git ls-tree -r fb46914c` 核對過）；候選池 199 筆與 `mw-pool-2026-09-15.json` 逐題相加相符。當前語料重跑污染檢查，十題全乾淨，與節點「十題重驗全乾淨」一致。
- 合約：`retrieval_eval_multiword.py` 從 `retrieval_eval.py` import 的 `ndcg_at_k/mrr/precision_at_k`，`python3 scripts/lumos contracts retrieval-ranking` 回「合約 0 條」，這次改動也沒有碰這三個函式的呼叫方式，沒有踩線。
- `Issues/評測題目寫進圖譜就毀掉那一題.md` 的 `REVISIT:2026-09-22` 有配回頭條件；`Systems/多詞評測.md` 的 `REVISIT:2026-12-15` 有配。

## 問題 1：節點寫「人只需要看 9 筆」，卷證自己的紀錄卻是那 9 筆全部給了另一個語言模型裁

引句:「多數決收掉 75，只剩 9 筆三席全散。人只需要看 9 筆。」

出處：`docs/lumos-toolchain-knowledge/Projects/評測尺修復_計劃.md:113`（[S9] 條款，本次提交範圍內新增，見 `git show 97a9b7ec` 對該檔的修改）。

同一份卷證引用的驗證節點自己講了誰做的：`docs/lumos-toolchain-knowledge/Verification/2026-09-15_多詞題庫重標與新基線.md:24` 寫「剩 9 筆三席全散，交給完全沒參與評分的第四方逐筆開檔裁決」，第 27 行接著寫「評審是誰：甲是 Claude sonnet，乙是 Codex，第三席是 Fable，第四方是 Opus」。第 25 行的「人放行」只有一句「2026-09-15 Enzo 裁『照判』」——那是對整批結果的事後認可，不是逐筆看過那 9 筆。實際的 9 筆裁決檔 `governance/eval/multiword/relabel-2026-09-15/九筆裁決-第四方.json` 與抽驗檔 `governance/eval/multiword/relabel-2026-09-15/抽驗-第四方盲判.json` 裡每一筆的 `why` 都是模型式的逐句論證（引 docstring、引行號、引 skill 步驟），沒有任何一筆標著是 Enzo 或任何人名。

也就是說：「人只需要看 9 筆」這句話會讓讀的人以為那 9 筆是人親自逐筆判的，但卷證顯示裁決者是 Opus（一個語言模型），不是人。

這條特別站不住腳的地方是：同一篇節點自己在別處知道怎麼誠實講這件事——`docs/lumos-toolchain-knowledge/Projects/評測尺修復_計劃.md:52` 講另一批（主搜尋題庫的 96 筆）時寫的是「★這批★絕大多數★是機器裁定，不是人裁★……[S3]『人裁必須是人』這條★沒有被假裝滿足★」。而 `docs/lumos-toolchain-knowledge/Projects/評測尺修復_計劃.md:106` 明文立了規矩：「[S3] 標註走既有雙評審流程，但★人裁必須是人★……本案的人裁檔要逐筆記明裁決者是誰，且不得是任何一席評審。」這條規矩是同一天稍早（`git log -S"人裁必須是人"` 查到最早在當天 06:33 的提交 `a0c6990a` 就立了）立下的，晚上做多詞題庫重標時（19:24–21:17 的四個提交）卻對第 9 筆的裁決者身分輕輕帶過，跟第 52 行的誠實揭露不是同一個標準。

會做出錯的行為/資料是：這套評測的基線（0.653 nDCG）之後要拿來擋檢索改動要不要上線，如果讀圖譜的人以為分歧最大的那批是人親自裁的，會高估這把尺的可信度；而圖譜自己在另一段話裡明明知道要老實講「機器裁定，不是人裁」卻在這裡沒講。

severity: major
blocking: 是

## 問題 2：Issue 節點還停在「還沒做」，但同一個提交已經把修法做完了

引句:「或者乾脆讓它兩種格式都吃：看到字典就取最終分那個欄位。」

出處：`docs/lumos-toolchain-knowledge/Issues/多詞評測吃錯標註檔直接拋例外.md:31` 附近的「## 修法方向（還沒做）」一節，`status: open`（第 3 行）、frontmatter 的 `DECISION:` 也是空的。

但這正是這次 diff 裡 `load_labels()` 實作的做法（`governance/eval/retrieval_eval_multiword.py` 新增函式：字典型別就取 `v["final"]`）。`git show 2a91e4be` 對這篇 Issue 節點的唯一改動是加一行 `related` 連結到 `Systems/多詞評測`，狀態欄與「還沒做」那段文字都沒有跟著更新——同一個提交裡程式已經把這件事做完，節點卻繼續說沒做。下一個 session 讀到這篇 Issue，會以為這支工具還會在吃錯標註檔時直接拋例外，實際上已經不會了（`t_mw_labels_accept_both_shapes` 測試證實）。

severity: minor
blocking: 否

## 問題 3：「兩席一致不等於可信」這條風險承認沒有配回頭條件

引句:「結論：這把尺在一級之內有雜訊，量大方向可以，量細差距要小心。」

出處：`docs/lumos-toolchain-knowledge/Verification/2026-09-15_多詞題庫重標與新基線.md` 的「三件已知邊界」第一條（抽 17 筆一致樣本給第四方盲判，只同意 12 筆）。這是單次量測（n=17）且承認「量細差距要小心」——照鐵則四，這種只提醒不擋、單次量測的風險承認要配回頭條件。該篇結尾確實有一行 `REVISIT:2026-11-15`，但那行明寫「這兩題的查詢問題」，指的是邊界清單裡第二、三條（查詢語意多義、查詢鑑別度太低），沒有涵蓋第一條（一致樣本抽驗只同意 71%）。第一條目前沒有任何回頭看的條件。

severity: minor
blocking: 否
