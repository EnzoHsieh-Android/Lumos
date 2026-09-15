severity: blocker

（來源：檢索核心重建 設計審 r3 驗收與量測席，2026-09-15；本輪任務＝驗收 r2 六條的折法對不對，不重複列舊條）

## 查證範圍說明

六個查證點逐一自己讀程式、讀既有評測工具（`governance/eval/retrieval_eval_multiword.py`、`governance/eval/retrieval_eval.py`）與卷證（`docs/lumos-toolchain-knowledge/Verification/2026-09-15_多詞題庫重標與新基線.md`）核對，沒有派子代理。以下發現依查證點順序排列。

## F1（查證點 1）[S5] 只點名了主迴圈的兩臂，遺漏了候選池重建那一處同樣寫死的呼叫，且沒交代「改成可設定」要接哪一種機制

severity: blocker
blocking: 是——[S6] 的「把新做法每題的前 k 併進候選池」明確要靠 `--rebuild-pool` 那條路徑撈候選（它是全檔唯一組池的程式碼），但 [S5] 的測試名與 manual 步驟只描述主迴圈的計分兩臂，完全沒提到這第三處同樣寫死的呼叫；照 [S5] 字面去改，[S6] 會撈到不知道是「現況」還是「新做法」的候選。

引句:「不改儀器，改完之後兩臂會退化成同一件事，安靜地印出兩個相同的數字、不報任何錯。」

查證：`any_terms` 這個布林軸在全檔恰好寫死三處，不是兩處——`governance/eval/retrieval_eval_multiword.py:226-227`（主迴圈的 base/fb，S5 有點名）與 `governance/eval/retrieval_eval_multiword.py:148`（`rebuild_pool()` 撈候選用的 `s1 = search_files(vault, q, any_terms=True)[:10]`，S5 完全沒提）。而 `rebuild_pool()` 正是 [S6] 「把新做法每題的前 k 併進候選池」唯一能借用的既有機制（全檔只有它會重組候選池）。[S5] 若只改主迴圈、沒同步改這一行，`--rebuild-pool` 撈到的候選源仍然是「any_terms=True」這個布林值碰巧代表的行為，跟主迴圈那兩臂各自代表什麼完全脫鉤。

進一步：「改成可設定」本身沒有指定機制，而這支檔案目前**沒有任何辦法**指向另一個版本的 `scripts/lumos`——`LUMOS = ROOT / "scripts" / "lumos"`（`governance/eval/retrieval_eval_multiword.py:31-32`）是模組層常數，沒有環境變數或 CLI 覆寫。對照同目錄的姊妹工具 `governance/eval/retrieval_eval.py:13`（`ROOT = Path(os.environ.get("LUMOS_EVAL_ROOT") or _SELF_ROOT)`）——那支工具本來就有「指到另一個原始碼根目錄」的既有機制，`retrieval_eval_multiword.py` 卻沒有；若 [S1]「改動前後都用同一把尺」真的是指「拿同一份 vault、跑兩個不同 commit 的 `scripts/lumos`」，這條既有慣例沒有被沿用，[S5] 也沒點名要補。

反過來，若 [S5] 想走「同一個 binary 裡用旗標切換新舊觸發邏輯」這條路，會撞上 [S2] 自己的候選②——「一律拆詞，把片語命中當成加分而不是開關」——這個寫法會把 `--any`/`--no-any` 現在賴以成立的「開關」語意整個拆掉（現行程式碼用 `if not _fb_seen:` 這種二分判斷決定要不要進入回退分支，見 `scripts/lumos:3093` 附近），屆時 `--no-any` 還剩不剩得下一個乾淨的「off」狀態，本案沒有交代。兩種可能的實作路徑，[S5] 一條都沒選、也沒排除，而其中一條會直接跟 [S2] 自己選的候選互打。

file: `governance/eval/retrieval_eval_multiword.py:31-32`
file: `governance/eval/retrieval_eval_multiword.py:148`
file: `governance/eval/retrieval_eval_multiword.py:226-227`
file: `governance/eval/retrieval_eval.py:13`

## F2（查證點 6，順帶回答查證點 5）[S7] 的「主搜尋金標」那一面，被評測工具自己的既有寫法完全隔絕在本案改動之外——不是「弱證據旗標擋不擋」的問題，是這一面永遠量不到任何差異

severity: blocker
blocking: 是——S7「三面退步不得收案」的第二面，字面上跑得動、印得出數字，但那組數字在改動前後保證一模一樣，跟本案有沒有正確實作無關；這面閘等於形同虛設卻沒有人發現，而這正是這份設計自己在 [S5] 花一整條在警告的失效形狀，只是這次發生在作者沒去檢查的另一面。

引句:「三面：多詞尺的四個指標、主搜尋金標的三指標、耗時。」

查證：「主搜尋金標」指 `governance/eval/retrieval_eval.py` 的 34 題 goldset（`report_goldset()` 印的 legacy/ranked 三指標）。這一面的查詢兩臂由 `_search_arms(q)` 產生（`governance/eval/retrieval_eval.py:115-120`），而這支函式**對 legacy 與 ranked 兩臂都寫死顯式帶 `--no-any`**——程式自己在旁邊留的註解已經把理由和後果都講清楚：

file: `governance/eval/retrieval_eval.py:363`（原文：「★兩臂都必須顯式 --no-any★:2026-08-03 起多詞回退是 search 預設...本 gate 是「legacy vs ranked」的受控比較,吃到回退擴召回會讓兩臂同時混入 OR 召回結果、基線失義。...目前 goldset 唯一的多詞題「guard kill」剛好字面存在故回退不觸發——★是還沒踩到,不是沒有★」）

`--no-any` 會讓 `cmd_search()` 整段多詞回退判斷（`scripts/lumos:3093` 起的 `if (any_terms or _fb_kind == "chars") and ...`）完全不進入——[S2] 改的觸發條件、[S3] 改的候選收斂，兩者都只存在於這段回退分支*裡面*。也就是說，不管 [S2]/[S3] 改成什麼樣子，只要 `--no-any` 還在，`_search_arms()` 撈回的 legacy/ranked 候選集在改動前後**逐字元相同**——這一面的 nDCG/MRR/Recall@10 數字必定不動一絲一毫，不是因為改動沒有效果，是因為這條路徑根本沒被餵到改動觸及的程式碼。

這連帶回答查證點 5：S7 提到的「主評測那支自己帶了一個弱證據旗標」確有其事、也確實有接上真正的 gate——`governance/eval/retrieval_eval.py:872,875` 的 `weak=_cs["weak"]` 會在 metric_rev 已切換（實測 `governance/eval/retrieval-eval-history.jsonl` 最近幾筆已是 `metric_rev: "condensed-v1"`，切換已發生）時真的餵進 `_search_gate_ok`／`_hook_gate_ok`，不是死參數。但這面閘既然對本案的改動完全不動，「弱證據旗標會不會擋」這件事對本案來說沒有意義可言——它永遠不會被觸發，不是因為證據夠強，是因為根本沒有新證據進來。S7 要求「確認它真的會擋」，但真正該補的條款其實是：**這一面要嘛換成不帶 `--no-any` 的查法（但那樣就不再是 legacy/ranked 的受控比較，需要另開一支或另傳參數），要嘛老實承認「主搜尋金標」這一面量不到本案的效果、拿掉或换成別的第三面**。目前條款完全沒有處理這件事，等於宣稱三面、實際只有一又不到面在動。

file: `governance/eval/retrieval_eval.py:115-120`
file: `governance/eval/retrieval_eval.py:363`
file: `governance/eval/retrieval-eval-history.jsonl`（tail 5 筆 `metric_rev` 皆為 `condensed-v1`）
file: `scripts/lumos:3093`

## F3（查證點 2）k=10 的推導只保護 nDCG@5／P@5，MRR 這個同樣被 S7 收進門檻的指標，深度多深都護不到

severity: major
blocking: 是——MRR 是 [S7] 明列要看「不退步」的四個指標之一，若 k=10 這個數字實際上護不到它，補標這條紀律對 MRR 而言等於白做，跟 [S3] 原始指控「k 太淺這條白做」是同一種失效，只是原因換成「k 這個維度對這個指標根本不生效」。

引句:「本案定 k＝計分視窗深度（目前是 5）的兩倍，也就是 **10**」

查證：`governance/eval/retrieval_eval_multiword.py` 的 nDCG@k／P@k 確實只看 `ranked_labels[:k]`（`ndcg_at_k`/`precision_at_k` 定義於 `governance/eval/retrieval_eval.py:35-41,51-53`），所以「計分視窗深度=5」這句話對這兩個指標是對的，補標到 10 名確實有實質保護。但 MRR 的實作（`governance/eval/retrieval_eval.py:44-48`）**沒有任何截窗**，是對整份傳入清單逐一往後掃到第一個 `r>=1` 為止；而 `retrieval_eval_multiword.py:226-227` 餵給 `mrr()` 的 `base_lab`/`fb_lab`（`governance/eval/retrieval_eval_multiword.py:236` 呼叫 `mrr(base_lab)`/`mrr(fb_lab)`）是 `search_files()` 回傳的**未截斷**候選全集——文件自己就引用過一題吃進 452 篇（全庫 87%）的實測數字，換句話說 MRR 這裡實際掃的視窗深度是幾百，不是 5，更不是補標到的 10。

對照姊妹工具 `retrieval_eval.py` 自己是怎麼處理這個問題的：它的 condensed 引擎在丟進 `mrr()` 之前，先明確 `_win = order[:SEARCH_TOUCH]` 把清單截窗到 `SEARCH_TOUCH=10`（`governance/eval/retrieval_eval.py:151`、呼叫處 `governance/eval/retrieval_eval.py:376-378`）——這正是 [S6] 想做但沒做到的事。`retrieval_eval_multiword.py` 的主迴圈沒有這道截窗，所以就算補標補到 k=10、把候選池擴大到涵蓋新系統前 10 名，只要新系統真正第一個相關的答案落在第 11 名以後，`mrr()` 依然會掃到未標候選（預設當 0 分）、繼續往後找，量出來的 MRR 跟「改得好不好」脫鉤——這正是 [S6] 開頭第一句話想堵的那個洞（「改得越好、被罰得越重」），只是這次 k 這個旋鈕轉多深都堵不住它，因為 MRR 的視窗根本不是 k 決定的。

file: `governance/eval/retrieval_eval.py:44-48`（`mrr` 無截窗）
file: `governance/eval/retrieval_eval.py:151`（`SEARCH_TOUCH = 10`，姊妹工具的做法）
file: `governance/eval/retrieval_eval_multiword.py:226-227,236`（未截窗餵給 `mrr()`）

## F4（查證點 3）+0.05 這個門檻有方向正確的立意，但文件承認的雜訊只停在「有多少題」的質化描述，沒有換算成 nDCG 分數量級，門檻沒有被自己引用的數字驗過

severity: major
blocking: 是——本案自己在風險段落點名的雜訊來源（一級內雜訊、第四方只同意 71%）如果換算下來的分數擺動量級接近或超過 0.05，這個「不得宣稱成功」的守門檻就是憑感覺訂的，跟它想防的「任何微小正數都能背書」是同一種問題，只是換了個方向。

引句:「本案定門檻為排序品質相對基線 **+0.05 以上**且其餘指標不退步」

查證：`docs/lumos-toolchain-knowledge/Verification/2026-09-15_多詞題庫重標與新基線.md` 記的雜訊實測是「抽 17 筆一致樣本給第四方盲判，只同意 12 筆（71%）」，且「五筆不同意全是相鄰一級」——這是一份**標籤層級**的分歧率，全篇沒有任何地方把它換算成「這種分歧率會讓 10 題的 nDCG@5 巨集平均擺動多少」。而該篇同時記了另一個可直接對照的實測：工作區未提交的兩篇筆記混進候選池，讓分數差了約 0.008——這是「候選集混進兩筆雜訊」造成的擺動量，跟「71% 標籤一致率」不是同一種雜訊來源，但兩者都指向同一個問題：**這把尺對候選池與標籤的微小擾動有多敏感，從沒被單獨量過、單獨寫成一個數字**。10 題的計分視窗只有約 50 個標籤格位（每題 top-5），依 71% 一致率推算，這 50 格裡有將近三成的格位標籤可能相差一級——[S7] 的門檻要成立，至少要交代「這種量級的標籤擾動，重算出來的巨集 nDCG 通常擺動多少」，而不是引用雜訊存在的事實就直接拍板一個數字。

引句:「這把尺只有十題，而且一級之內有雜訊」

file: `docs/lumos-toolchain-knowledge/Verification/2026-09-15_多詞題庫重標與新基線.md`

## F5（查證點 4）召回那一面的二選一，沒有交代要用哪個 k、也沒有交代要不要繼承既有的池內相對值警語——兩種選法都留了一個會誤導的洞

severity: major
blocking: 是——「接上並訂基線」讀起來像是把缺口補完整了，但缺口實際上藏在「接哪個 k」與「這個數字算不算得上真的召回率」這兩個沒被問到的問題裡；照著字面隨便接一個 k，量出來的東西要嘛跟既有指標重複、要嘛重新踩進 [S3]／[S6] 想堵的同一個坑。

引句:「連算召回的那個函式都沒被呼叫過」

查證：`retrieval_eval.py:88-91` 的 `recall_at_k(ranked_labels, n_relevant, k)` 分子是 `ranked_labels[:k]` 裡相關項的個數、分母是 `n_relevant`（該題全部已標相關項數）。若接上時 k 取跟 nDCG@5／P@5 一樣的 5，因為分母 `n_relevant` 對同一題是固定值，`recall@5` 會是 `precision@5` 的線性縮放（`recall@5 = precision@5 * 5 / n_relevant`），沒有提供任何 P@5 量不到的新資訊，等於掛了個新名字重印舊數字。若改用比 5 深的 k（例如比照 [S6] 的 10，或乾脆掃全部候選求「真召回」），就會重新踩進 F3 點出的同一個坑——`search_files()` 回傳的候選集常有數百筆，未在池內標過的一律計 0，k 越深、被未標候選拖累的機率越高，而這正是 [S6] 整條款想防的失效模式。

此外，`retrieval_eval_multiword.py` 檔頭自己已經誠實記過一條邊界：「IDCG 以「池內標到的最佳排列」為基準，故分數是★池內相對值★，不是絕對召回品質」（`governance/eval/retrieval_eval_multiword.py:14-16` 附近的檔案說明）。這條警語目前只掛在 nDCG 身上，但「召回率」這個詞對讀者的字面期待就是「找到了全部該找到的裡面的幾成」——如果真的接上 `recall_at_k`，這條「池內相對值、不是絕對值」的警語必須原樣搬過去，否則印出來的「召回率」三個字會比 nDCG 更容易被誤讀成絕對數字。[S7] 的二選一目前完全沒提這兩件事，任何一種選法都要先把 k 與警語定下來才算真的把洞補起來。

file: `governance/eval/retrieval_eval.py:88-91`
file: `governance/eval/retrieval_eval_multiword.py:14-16`

## F6（查證點 6，新洞）「其餘指標不退步」是零容忍的逐項否決，跟同一句話裡的雜訊警覺互相矛盾；耗時這一面連量測方法都沒定義，更談不上容錯

severity: major
blocking: 是——F4 已經指出雜訊量級沒被驗過，這一條再往下一層：就算 +0.05 這個數字本身夠大，門檻句子後半段「其餘指標不退步」對 MRR、P@5、第一名品質、主搜尋金標三指標、耗時**一律要求零負值**，沒有給任何一個留容錯空間——文件自己在同一段承認雜訊存在、承認門檻是為了防雜訊灌水的假陽性，卻沒有處理鏡像的假陰性：一個真正的改善，只要其中任何一個次要指標因為純雜訊掉了 0.001，字面上就要被這句話擋下，跟 [S7] 想避免的「照字面做出錯的行為」是同一件事發生在門檻本身，不是發生在待審的程式碼裡。

引句:「本案定門檻為排序品質相對基線 **+0.05 以上**且其餘指標不退步」

查證：耗時這一面連量測方法都沒被定義——`governance/eval/retrieval_eval_multiword.py`、`governance/eval/retrieval_eval.py` 兩支檔案裡沒有任何一處計時、重跑取中位數，或任何統計處理的程式碼（全域搜尋 `repeat`/`statistics`/`timeit` 等關鍵字皆無命中）。本案摘要引用的四個耗時數字（0.272／0.467／0.989／0.431 秒）本身標的是「最快一次」，不是多次重跑的中位數或帶容錯區間的估計——單次量測拿來跟另一次單次量測比較「有沒有退步」，本來就容易被系統當下的排程雜訊（磁碟快取冷熱、CPU 佔用）決定輸贏，而 [S7] 的「耗時」面同樣被「任一面退步不得收案」這句話罩住，沒有訂出多快算退步、要不要重跑取中位數。

file: `governance/eval/retrieval_eval_multiword.py`（全檔無計時重跑機制）
file: `governance/eval/retrieval_eval.py`（全檔無計時重跑機制）

---

## 統計

六個查證點全部查到具體發現：查證點 1 與 6（含連帶回答查證點 5）判定為阻擋級，查證點 2、3、4 判定為需處理但非阻擋。沒有一條是「查了但沒發現」。
