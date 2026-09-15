severity: clean

# 資安審查:code-標籤與評測尺 r3-final.patch

## 涵蓋範圍聲明

**這 46 個檔我全部看過一遍**——三支會執行的程式(`governance/eval/retrieval_eval.py`、`scripts/lumos`、`scripts/test_lumos.py`)逐 hunk 讀完全文並對照原始檔上下文;`governance/eval/retrieval-goldset.json`、`retrieval-eval-history.jsonl`、`raters/*.json`(adj-*/merge-*/rater-*)這類資料檔用逐行 diff 掃描 + 針對性抽樣核對(例如核對新增的 7 筆 `"final"` 標註內容、核對新增的歷史列是否帶 `metric_rev`/`pass`),沒有逐條肉眼複誦每一筆 JSON 記錄的完整內容,但用腳本掃過全部新增行找可疑樣式(密鑰/token/私鑰、`shell=True`/`os.system`/`eval(`/`exec(`/`pickle`/`yaml.load`/路徑穿越等),零命中。文件類(`Issues/*.md`、`Projects/*.md`、`Systems/*.md`、`Verification/*.md`、`MOC/index.md`)全部讀過內容;`.canary-log.jsonl`/`.escape-log.jsonl` 兩個治理帳本用 diff 全文讀過新增列。

## 這批改動在做什麼(審查後的理解)

修兩個讓「未標=0 且新舊尺恆等」這個不可逆切換閘永遠通不過的缺陷:
① 恆等斷言原本拿「全題目的舊尺平均」比「新尺題級門檻篩過的有效題平均」,兩組不同分母的平均本來就不會相等;新增 `_macro_on()` 把舊尺平均也限縮到同一組題再比。
② `_touched_edit()` 的未標檢查視窗原本只涵蓋「綜合」排序臂的前 k,但算分同時對「只比文字」「只比圖」兩條臂各自截前 k——那兩條臂視窗內的未標永遠不會被判定為未標。新增 `_edit_orders()` 作為三條排序鍵的唯一實作,`_touched_edit` 改成三臂前 k 的聯集。

以下逐條記錄「切換閘能不能被騙過」的分析過程,全部結論皆為 clean(沒有殘留可利用漏洞)。

---

### 發現 1:恆等斷言舊版對「雙側皆無資料」誤判為恆等——本分支已修正

`_switch_equal()` 舊版對「新舊兩側都算不出值(None, None)」的處理是直接 `continue`(跳過、不列入 diffs),等於把「完全沒有可比資料」判定成「經檢驗恆等」而放行切換。這正是「什麼樣的輸入能讓恆等條件在不該成立時成立」這一題的真實答案:只要新尺的題級門檻讓所有題都失效(值全部變 None,例如候選集普遍小於半個配置窗寬),舊寫法會把「零證據」誤判成「已驗證恆等」,永久切換評測基準尺。本分支已把這條路徑堵住,新版對 `(None, None)` 明確判定為不恆等、列入差異、中止切換。

引句:「放行切換——★比舊寫法還寬鬆★(舊的全題平均幾乎必為非 None,同情境會被判有 vs 無而擋下)。」

severity: clean
blocking: 否——這是分支修掉的舊缺陷,r3-final.patch 裡的最終行為已 fail-closed,不是殘留漏洞。

---

### 發現 2:新原語 `_macro_on` 的過濾鍵與比較對象分母集合天生一致,沒有可操縱空間

`_macro_on(rows, key, gate_key)` 先用 `r.get(gate_key) is not None` 過濾出「新尺也認可的題」,再取同一批列的 `key` 值取平均。恆等斷言比較的兩側(例如 `_rn_eq` 對 `condensed_search["ndcg"]`)在 `report_goldset` 裡都是對同一批 `srows`、同一個 `gate_key`(`c_ranked_ndcg`)做篩選——分母集合綁死同一個鍵,不存在「讓其中一邊分母偷偷變大或變小」的操縱空間。就算人工把 goldset 標註改到候選全部已判,`_condense` 的視窗也只會變成「真的全判」,此時 condensed 分數在數學上等於同一視窗上算出的 legacy 分數(相同排序、相同 IDCG 基準 `all_rels`)——這是設計要達成的結果,不是繞過。

引句:「vals = [r[key] for r in rows」

severity: clean
blocking: 否——過濾邏輯的兩側分母集合結構上綁定同一鍵,找不到可構造的輸入能製造假恆等。

---

### 發現 3:`-k` 邊界值(0 與負數)不會讓未標檢查視窗與算分視窗脫鉤

驗證了 CLI 參數 `-k` 的邊界輸入。`-k 0` 時 `_condense` 視窗清空、`valid=False`,搭配發現 1 的修法,`_switch_equal` 對 None 值 fail-closed,不放行切換。負值(例如 `-k -3`)會讓 Python `[:k]` 的負索引語意生效(取「除最後 |k| 個外的全部」而非「前 k 個」),但因為 `_touched_edit` 與 `eval_edit` 的視窗都是對同一個 `_edit_orders(...)` 結果做同一個 `[:k]` 切法,兩邊視窗仍保持自洽一致,沒有找到能讓「未標檢查視窗」與「算分視窗」產生落差、進而騙過恆等斷言的參數值。這條驗證直接對應本分支要修的漏洞類型(視窗不對齊),而修法本身(單一排序實作 `_edit_orders`,兩處共用)天生免疫於 k 值的正負號。

引句:「_unj_all = (collect_unjudged(gs, args.split, k=args.k) if args.split」

severity: clean
blocking: 否——邊界值下修法仍保持視窗自洽,fail-closed 路徑仍生效。

---

### 發現 4:失敗跑的歷史紀錄不會污染棘輪基線(既有防護,本分支未觸碰但與威脅模型相關)

`retrieval-eval-history.jsonl` 本次新增的列裡,有數筆 `metric_rev: "condensed-v1"` 但 `pass: false`(對應 `-k 12` 的探索性跑法,`unjudged_count` 非 0)。sticky 判定 `_history_metric_rev()` 不分 pass/fail,任何一列帶 `metric_rev` 就視為「已切換」——這是既有設計(本分支未改動這段),配合的防護是 `_ratchet_base()` 查基線時只採信 `pass` 為真的紀錄,失敗跑不會成為新的棘輪基線。因此就算歷史檔混入了失敗跑的資料(不論是意外或刻意),也不能拿它降低下一輪的比較門檻。此函式與寫入口 `_history_record()`(只有一處,`metric_rev` 只被切換條件那段賦值)均不在本次 diff 變動範圍內,故以下用 `file:` 標記查證位置而非引句。

file: `governance/eval/retrieval_eval.py:333`
file: `governance/eval/retrieval_eval.py:732`

severity: clean
blocking: 否——既有防護機制存在且未被本次改動削弱,失敗跑資料無法成為棘輪基線。

---

### 發現 5:新增程式碼不含子行程/路徑組合/反序列化等注入面

本次新增或修改的程式邏輯(`_macro_on`、`_edit_orders`、`_touched_edit` 改動、`main()` 內多傳 `k=args.k`)全部是純函式運算與參數傳遞,沒有新增 `subprocess`、檔案路徑字串組合、正則表達式或反序列化呼叫。全檔案掃描(含 `scripts/lumos`、`scripts/test_lumos.py` 新增行)確認沒有 `shell=True`/`os.system`/`eval(`/`exec(`/`pickle`/`yaml.load` 等危險樣式。既有的 `subprocess.run` 呼叫(`_lum`、`pin_snapshot`)本次未被觸碰,且本來就是 list 形式參數(非 shell 字串拼接),不在本次改動的攻擊面內。

引句:「orders = _edit_orders(free)   # ★唯一實作,與 _touched_edit 共用★」

severity: clean
blocking: 否——新增程式碼是純邏輯層改動,沒有新的執行/反序列化路徑。

---

### 發現 6:恆等斷言用的內部鍵不會外洩進被提交的歷史帳本

新增的 `_rn_eq`/`_ln_eq`/`_fp_eq`/`_bp_eq`/`_gp_eq` 等鍵只用於當輪記憶體內的恆等判定,不會被寫進 `retrieval-eval-history.jsonl`——本次改動自己也在註解裡點明這點(該過濾邏輯本身不在此次 diff 範圍,是既有的 `_history_record()` 行為,見下方 `file:` 標記)。沒有發現本次新增欄位被意外放進被提交/被推送的帳本檔。

引句:「★這兩個現在沒人讀★(2026-09-15 code-r1 正確性席):歷史紀錄組裝會濾掉底線開頭的鍵,」

file: `governance/eval/retrieval_eval.py:756`

severity: clean
blocking: 否——新增的內部比較鍵不會流出到被提交的資料檔。

---

## 一個範圍外但值得記錄的觀察(不列入本報告判定)

`docs/lumos-toolchain-knowledge/Issues/編排者改寫席位引句.md` 記載本分支上一輪(r2)代碼審時,編排者曾經改寫過審查席的引句去對齊事後重建的快照,被機械留痕指紋比對抓到,因此才重派這次 r3 全新審查輪。這是關於「審查證據鏈完整性」的既有已知問題(該筆記自己標記「目前沒有任何東西擋住編排者編輯席報告」,附 REVISIT:2026-10-15),與 r3-final.patch 裡實際要上線的程式碼行為無關,不是這份改動本身的可利用漏洞,故不計入本報告的 severity 判定,僅供留意。

## 結論

在會執行的三支程式(`retrieval_eval.py`、`scripts/lumos`、`scripts/test_lumos.py`)裡沒有找到可被利用的安全漏洞。這次改動修的兩個缺陷本身就是在補強「不可逆切換閘」的安全性質(讓它更難被空資料或視窗不對齊騙過),逐條分析確認修法本身沒有引入新的繞過路徑,新增測試(`t_eval_switch_equal_no_data_is_not_equal` 等)也用翻紅驗證釘住了這條攻擊面。資料檔(goldset/raters/history)的新增內容都可追溯到具名人工裁定或對應的真實執行紀錄,沒有發現「讀進來就當真」而未經查核的注入點。

全篇沒有發現可被利用的漏洞,阻塞項 0 條。

## 最終版複查(2026-09-15)

凍結材料更新後(舊版留存為 `r3-final.prev.patch`),用 `diff` 直接比對兩版 patch 全文,確認只有三處內容差異,其餘 43 個檔逐位元組相同(包括 `governance/eval/retrieval_eval.py` 與 `scripts/lumos`——我原本審查的程式邏輯結論不受影響,不需要重審)。改動位置:①`Issues/尺切換恆等斷言反覆不過.md` 新增 4 行 KEY;②`governance/eval/retrieval-eval-history.jsonl` 移除 4 筆記錄;③`scripts/test_lumos.py` 的 `t_eval_unjudged_check_honours_cli_k` 新增歷史帳導向保護。以下逐條回覆三個問題,查證只在 `/tmp` 與 repo 內的唯讀指令(`grep`/`diff`/`wc`/`git rev-parse`/`git log`,沒有 commit/reset/restore/checkout/stash)進行。

### ① 清掉的 5 筆(實測只找到 4 筆)紀錄,有沒有可能誤刪真實紀錄或動到切換那一筆

用兩版 patch 逐行比對(而非只看筆記自己的說法),`governance/eval/retrieval-eval-history.jsonl` 的 hunk 從 `@@ -91,10 +91,19 @@` 變成 `@@ -91,10 +91,15 @@`——上下文的 10 行完全一致,代表舊版本來就有的 100 行歷史紀錄一行都沒被動,這次的異動只發生在新增區塊裡。舊版新增了 9 筆,新版只留 5 筆,差額是被移除的 4 筆:全部帶 `"goldset_rev": "34c71678e723"`、`"k": 12`、`"goldset_snapshot": null`,與筆記聲稱的夾具指紋(沒有語料釘定+題庫雜湊 34c71678+k=12)完全對上;三者同時成立才會命中,不會誤觸其他記錄。用實際檔案(工作樹的 `governance/eval/retrieval-eval-history.jsonl` 已經是這一版內容)複驗:`grep -c '"goldset_rev": "34c71678e723"'` 與 `grep -c '"k": 12'` 都是 0,總行數 105——跟筆記寫的「真實紀錄 105 筆未受影響」核對一致。切換那一筆(`"eval_head": "a0c6990a"`、`"metric_rev": "condensed-v1"`、`"pass": true`)我逐欄位比對過清理前後版本,位元組完全相同,而且 `eval_head` 的值跟這個工作目錄實際的 `git rev-parse HEAD`(`a0c6990a21d6...`)對得上,不是編造的提交編號。

唯一沒對上的地方:筆記寫「已污染 5 筆」,但兩版 patch 之間我只能核對出 4 筆差異。這可能是清理發生在兩個階段(這次 diff 之外還有一筆更早被清掉,不在我能比對的兩個快照之間),也可能是筆記數錯一筆——我沒有更早的快照可以核對,所以判斷不了是哪一種。但這不影響安全結論:我直接查的是「現在的真帳裡還有沒有殘留假紀錄、有沒有動到真紀錄」,兩者答案都是否定的(零殘留、零誤刪),所以就算筆記數字有出入,實際状態是乾淨的。

引句:「實際已污染 5 筆(夾具指紋:沒有語料釘定、題庫雜湊 34c71678、k=12),已逐筆清除;真實紀錄 105 筆未受影響,切換那筆帶真實提交編號與語料釘定」

### ② 新的 assert 前置會不會被繞過,或反過來讓測試靜默略過

讀了 `scripts/test_lumos.py` 裡 `t_eval_unjudged_check_honours_cli_k` 的完整前後文(工作樹目前就是這一版內容,行號約 27130–27152)。關鍵結構是:先無條件把 `os.environ["LUMOS_EVAL_HISTORY"]` 設成 fixture 路徑,緊接著才 `assert` 檢查它確實指向 fixture,再往下才呼叫 `m.main()`;`finally` 區塊保證不管 assert 有沒有炸,環境變數與 `sys.argv` 都會還原,不會外洩到下一支測試。這個 assert 在「程式碼沒被改動」的前提下必然恆真(因為它查的正是自己前兩行剛寫入的值)——但它的用途本來就是「防未來的人手滑刪掉那行設定」的回歸樁,不是要擋外部輸入,所以恆真不是缺陷,是設計。

真正要確認的是「assert 失敗時,測試框架會不會把它吃掉變成靜默略過」。我讀了主 runner(`scripts/test_lumos.py` 第 28347 行附近)呼叫每支測試的迴圈:`except _SrcOnly` 才算「skip」,其餘 `except Exception as e: FAIL += 1; print(f"  ✗ {t.__name__} EXCEPTION: {e}")`——`AssertionError` 是 `Exception` 的子類,會落進後者,判定成 FAILED 並把訊息印出來,不是 SKIP、更不是靜默 PASS。也就是說如果有人手滑拿掉環境變數導向那行,這支測試會在 CI 跟本機都紅、而且訊息就是我們自己寫的「拒跑」句,不會被吞掉。另外用 `_load_retrieval_eval()`(`importlib.util.spec_from_file_location` + 唯一模組名 `retrieval_eval_fx_{id(root)}`)確認每次呼叫都建立獨立模組實例,monkeypatch(`m.collect_unjudged = _spy`)不會外漏到其他測試或真正的正式模組。

我也检查了「同類漏洞是不是只補了這一支」:全檔搜尋所有呼叫 `m.main()`(或 `mi.main()`)的地方,除了這支之外,其餘全部屬於別的模組(`impact-hook.py`、`dispatch-lens-hook.py` 等經 `_load_hook_mod`/`_load_lumos_inproc` 載入的物件,`m` 是變數名重複使用,不是同一個 `retrieval_eval` 模組),另一支明確跑 `retrieval_eval.py` 的測試(`t_refresh_full_chain_and_eval_e2e`)本來就是用 `subprocess.run(..., env={**os.environ, "LUMOS_EVAL_HISTORY": str(hist)}, ...)` 開子行程並顯式覆寫環境變數,是既有的安全寫法,不受這個模組載入方式的影響。所以這個問題類別確實只有這一支測試中招,補丁補在對的地方,沒有漏補的姊妹測試。

唯一沒有機械擋住、只能算通用 Python 常識的邊界情況:如果整個測試進程是用 `python3 -O`(或設 `PYTHONOPTIMIZE`)啟動,`assert` 語句會被直接剝掉,這個前置檢查就形同虛設。我查過 `.github/workflows/ci.yml`,實際呼叫是 `python scripts/test_lumos.py --shard "$i/4"`,沒有 `-O` 旗標,repo 裡也沒有任何地方設定 `PYTHONOPTIMIZE`,所以這條路徑在這個專案目前的用法下不成立;記錄下來是為了完整回答「能不能被繞過」,不是說有實際暴露。

引句:「"拒跑:評測歷史帳沒導向 fixture,跑下去會寫進正式帳"」
引句:「check("★正式的評測歷史帳一個位元都沒被動到★", _real_after == _real_before,」

### ③ 這次治理帳本的清理有沒有留下可追溯的痕跡

有。清理本身就是 r3-final.patch 裡一段正常的 diff(對 `retrieval-eval-history.jsonl` 的 4 行刪除),會跟著這次提交一起進 git 歷史,`git log -p`/`git blame` 都查得到「這幾行何時被誰移除」,不是繞過版控的手改或事後覆寫。而且同一個 commit 裡的知識圖譜筆記(`Issues/尺切換恆等斷言反覆不過.md`)明文寫下了污染的起因(直接呼叫 `main()`、模組從真實路徑載入)、命中的指紋條件、清除的筆數、以及「真實紀錄 105 筆未受影響」的核對結果——這是主動揭露並記錄下來,不是想辦法讓這件事看起來沒發生過。這跟本分支另一篇筆記記載的「編排者改寫席位引句」那種試圖讓證據對齊快照的作法性質不同:這裡清掉的是可驗證的「假資料」(有機械指紋可比對、且真實紀錄可證明未受影響),而且清除動作本身留在版控歷史裡可回溯,不是無痕刪除。

### 涵蓋聲明

**這次複查把 46 個檔的最終版又全部看過一遍**:用 `diff` 逐位元組比對舊版與新版的每一個 `diff --git`區段,確認 43 個檔案沒有任何差異(不需要重讀,結論沿用原報告),另外 3 個有差異的檔案(`Issues/尺切換恆等斷言反覆不過.md`、`governance/eval/retrieval-eval-history.jsonl`、`scripts/test_lumos.py`)則完整讀過變動前後的內容與所在函式的上下文,並且對照工作樹裡的實際檔案(此工作目錄目前就處在這一版狀態)做了獨立的機械核對(記錄筆數、指紋比對、呼叫路徑搜尋、CI 呼叫方式查證),不是只看筆記單方面的敘述。

### 結論(複查)

三處變動都在補救、不在引入新風險:歷史帳清理精準命中夾具指紋、沒有動到任何真實紀錄(含切換那一筆);新的前置 assert 失敗時會被測試框架記成響亮的 FAILED,不會靜默略過,也沒有可從外部輸入操縱的繞過路徑(唯一的理論缺口 `-O` 在本專案實際 CI 用法下不成立);清理動作本身留在正常的 git diff 裡,連同筆記一起可追溯、可核對。判定維持不變。

## 最終版再確認(2026-09-15)

用 `diff` 直接比對 `r3-final.prev2.patch` 與 `r3-final.patch` 全文:兩版只差 8 行 diff 輸出,對應恰好一處實質內容變動——`Issues/尺切換恆等斷言反覆不過.md` 裡那條講污染的 KEY 敘述句被改寫成更精確的版本(另一行是該筆記的 `index` 雜湊,是內容變動的必然副作用,不算獨立改動)。用 `diff <(grep '^diff --git' prev2) <(grep '^diff --git' final)` 核對過兩版涉及的檔案清單完全一致、仍是 46 個檔,沒有新增或刪除任何檔案的變動軌跡。`retrieval_eval.py`、`scripts/lumos`、`scripts/test_lumos.py` 這三支程式碼在這一版裡沒有任何差異,跟我剛確認過的版本逐位元組相同,不需要重審程式邏輯。

### 核對「4 筆 vs 5 筆」與「繼承」的說法

用我自己在上一輪重建的歷史帳寫入順序(依 jsonl 逐行的真實 append 順序,不是憑筆記說法)核對:那一批 2026-09-15 新增的 9 筆裡,第 4 筆(`eval_head: e75b883c`、`goldset_rev: 6620ac6f9970`、`unjudged_count: 0`、`pass: true`)是第一次出現 `"metric_rev": "condensed-v1"` 的紀錄,對應的正是真實評測觸發尺切換的那一輪;第 5 筆(`eval_head: a0c6990a`,同樣 `pass: true`)是切換後又一次真實成功的評測。被清掉的 4 筆(`goldset_rev: 34c71678e723`、`k: 12`、`pass: false`)全部排在第 4、5 筆之後——也就是說,寫下這 4 筆假紀錄的時間點,真實切換早就已經發生、`metric_rev` 已經是 sticky 的 `"condensed-v1"`。這 4 筆的 `metric_rev` 欄位是 `main()` 開頭 `_history_metric_rev(_hist_pre)` 讀到既有的 `"condensed-v1"` 之後原樣寫回,而不是這幾次假跑自己重新判定切換寫上去的(它們的 `unjudged_count` 是 2,不是 0,原本就不滿足觸發切換的前提)。這跟新版說法「那 4 筆帶的 condensed-v1 是繼承自前面真實那一輪,不是假紀錄寫上去的」完全對得上,我自己重建的順序證實了這一點,不是照單全收筆記的敘述。

「4 筆 vs 5 筆」的訂正也合理:我能核對的只有凍結材料兩個快照之間的差異(4 筆),第 5 筆按新版說法是「那版凍結之後、背景那輪全套測試又寫進去的」——發生在我能拿到的兩個快照之外,我沒有更早或更晚的快照能直接核對這一筆,所以無法對「確實有第 5 筆」本身做獨立佐證,但這不影響我在上一輪已經完成的核心查驗:現在的真實歷史帳(工作樹裡的 105 行)不含任何殘留的假紀錄指紋,真實紀錄(含兩筆切換相關的紀錄)逐位元組未受影響。

危險程度的新說法(「若測試先跑、真實切換還沒發生,假紀錄就會是第一個把這個不可逆旗標寫上去的人」)是一句以「若⋯就會」表達的反事實推論,不是對本次實際發生情況的描述——而我重建的順序顯示本次實際情況是真實切換先發生、假紀錄只是繼承 sticky 值,兩者不矛盾:新說法承認了「這次沒有真的觸發假切換」,同時準確指出了這個 bug 修好之前潛在更嚴重的故障模式(測試用合成 fixture 資料觸發一個本該由真實全庫評測才能觸發的不可逆旗標)。這個推論本身邏輯成立(若測試先跑且該次假跑的 `unjudged_count` 剛好是 0、且 `_switch_equal` 剛好判真,switch 區塊確實會被那次假跑觸發並寫入正式帳),沒有跟我查到的事實衝突。

引句:「★危險程度的精確說法★:那 4 筆帶的 condensed-v1 是★繼承★自前面真實那一輪,不是假紀錄寫上去的;但若測試先跑、真實切換還沒發生,假紀錄就會是第一個把這個★不可逆★旗標寫上去的人」

### 這次改動有沒有夾帶別的東西

沒有。8 行 diff 輸出全部落在同一條 KEY 敘述句與它必然連帶的 `index` 雜湊上,沒有新增、刪除或修改任何其他檔案、程式邏輯或歷史帳資料列。

判定不變。

## 折入第四條後的複查(2026-09-15)

用 `diff` 比對 `r3-final.prev3.patch` 與 `r3-final.patch`:總共 73 行差異,分佈在三處,跟派工詞描述的範圍一致——①`Issues/尺切換恆等斷言反覆不過.md` 的那條 minor 敘述句(從「接受不改」改成「已折」)②`governance/eval/retrieval_eval.py` 的 `_edit_orders()`,綜合臂的排序鍵從 `x.get("score", 0.0)` 改回 `x["score"]`,並補了一段解釋為什麼要炸的註解③`scripts/test_lumos.py` 的 `t_eval_edit_orders_single_source` 尾端新增一段守衛斷言。用 `diff <(grep '^diff --git' prev3) <(grep '^diff --git' final)` 核對過檔案清單沒有變化,仍是 46 個檔;其餘看起來像差異的行只是既有 hunk 因為前面插入了 5 行註解而整體位移的行號重新編號(例如 `@@ -432,25 +478,21 @@` 變 `@@ -432,25 +483,21 @@`),不是新的內容改動。

### 容錯改拋錯,會不會製造可被利用的阻斷

讀了 `main()` 的完整執行順序(這是這次審查第一輪就讀過的既有邏輯,這次重新核對執行順序跟這個問題的關係):`report_goldset()`(內部呼叫 `eval_edit()` → `_edit_orders()`,這次改動觸及的那段程式碼)是在迴圈裡對每個 split 先跑完,***之後***才進入尺切換判定的區塊(`_read_history()`、`collect_unjudged()`、`_switch_equal()`),再往後才是 `with open(hist, "a") ...` 寫歷史帳。也就是說,`_edit_orders()` 在計算排序鍵時如果因為缺 `score` 欄位炸成 `KeyError`,這個例外會在尺切換判定與歷史帳寫入***都還沒執行到***的地方就讓整支程式中止——不可能出現「炸出一個看起來像通過的假結果」,因為往下寫判定結果的程式碼根本沒被執行到。這跟「靜默給 0、算出一個好像正常但被污染的分數」是完全不同的失效方向:炸掉是全有或全無,不會留下半調子的假訊號。

接著查了這支工具實際被誰呼叫、呼叫端怎麼處理失敗,而不是只停留在「理論上炸了會怎樣」:全 repo 搜尋 `retrieval_eval.py` 的呼叫點,只有 `scripts/test_lumos.py`(單元測試)、`governance/autonomous-loop.sh`(排程)、`governance/eval/refresh_labels.py`(匯入計分函式)三處,沒有任何 CI workflow 或 push/commit hook 把它接成阻斷式的閘。排程那一處(`governance/autonomous-loop.sh` 的 `run_exam`)原始碼自己寫明「fail-open,考卷失敗只記 log 不阻斷 gap 流程」——呼叫式是 `... || true`,不看退出碼,而是靠 `grep -q 'gate 總判定' "$LOGDIR/exam-$tag-$TODAY.log"` 判定這輪考卷有沒有真的跑完;`gate 總判定` 那一行是 `main()` 執行到最後才印的,`KeyError` 炸在半路的話,log 裡只有 Python traceback,絕對 grep 不到那個字串,於是後面「考卷完成」「未標率通知」那些分支全部不會執行,不會有任何誤判成功的訊息被送出。下游 `refresh_labels.py delta` 那一段更明確地寫著「★rc+產物存在雙查後才通報★(code-r1 資源席 F2:原 `|| true` 吞錯照發「已產表」=假成功)」,兩個條件都要成立才算數,同一套雙保險。

實測驗證(在 repo 裡直接跑測試,沒有 commit/reset/restore/checkout/stash):跑 `python3 scripts/test_lumos.py -k eval_`,116 支全綠,包含真的用 subprocess 端到端跑 `retrieval_eval.py` CLI 的 `t_refresh_full_chain_and_eval_e2e`——證實目前真實輸出的自由候選都帶 `score` 欄位,這次改動沒有讓既有的正常路徑意外炸掉。跑完之後核對 `git diff -- governance/eval/retrieval-eval-history.jsonl` 沒有任何新增內容,證實測試執行沒有意外寫髒真實歷史帳。

會讓這支工具在真實使用情境下炸掉,前提是有能力讓 `impact --ranked` 對某個自由候選漏印 `score` 欄位——這需要能修改被評測的知識圖譜內容或 `scripts/lumos` 本身的輸出格式,屬於「已經有 repo 寫入權限的人」這個等級的威脅模型,跟整個 lumos 治理機制原本就假設的信任邊界(內部貢獻者/agent,不是匿名外部使用者)一致,不是這次改動新開的口子。而且就算真的被觸發,唯一可觀測到的後果是「今天的排程考卷沒有跑完、記到 log 裡等人看,明天 age 條件符合會再試一次」——不可逆切換本身已經在更早之前真實發生過(sticky,寫在歷史帳裡),不會因為之後哪一輪考卷炸掉而被撤銷或被錯誤地重新觸發。方向上跟本分支反覆出現的設計原則一致:寧可炸掉讓人看見,不要靜默算出一個不能信的數字。

引句:「★折而不是放行的理由有兩層★:①這個排序決定的是驅動不可逆尺切換的視窗,悄悄走樣比整支炸掉難發現得多 ②同輪有一席報到 blocker,規矩是整輪不得有附理由放行的項目。」

### 新守衛斷言本身會不會被拿來做什麼

讀了 `t_eval_edit_orders_single_source` 新增的那一段:餵一個沒有 `score` 欄位的自由候選字典進 `_edit_orders()`,用 `try/except KeyError` 接,`_raised` 記有沒有真的炸,再用 `check(...)` 斷言 `_raised` 必須是 `True`。這段新增碼只是在既有函式尾端多加幾行,沿用函式開頭原本就有的 `_need_src("governance/eval")` 保護(這是既有的、跟消費端/來源端有沒有原始碼有關的既有跳過機制,不是這次新開的口子),沒有另外幫這幾行加專屬的條件式跳過。就算 `_edit_orders()` 哪天被改壞成不炸,`_raised` 會是 `False`,`check()` 記一次 FAIL,不是被吞掉或靜默通過;就算 `_edit_orders()` 炸出的不是 `KeyError` 而是別的例外型別,`except KeyError` 接不住,例外會往外傳到測試框架的最外層 `except Exception as e: FAIL += 1`,一樣被記成失敗,不會被誤判成通過。實測直接跑這支測試(`python3 scripts/test_lumos.py -k t_eval_edit_orders_single_source`),11 條斷言全綠,包含新加的這一條,對照我自己讀 `sorted()` 求值語意的判斷(key function 要對每個元素求值,缺鍵的字典在建 `"fusion"` 那個 entry 時就會直接 `KeyError`)完全吻合——沒有另外去改壞程式碼做翻紅實驗,但邏輯推導與現場執行結果一致,足以確認這條斷言不是空氣斷言。

引句:「"fusion": sorted(free, key=lambda x: (-x["score"], x["node"])),」
引句:「★自由候選缺 score 時排序要直接炸,不得靜默當 0★」

### 這次改動有沒有夾帶別的東西

沒有。73 行 diff 精確對應派工詞描述的三處(筆記敘述句、`_edit_orders` 的排序鍵、新增的守衛斷言),其餘位移行號不是實質內容變動;檔案清單仍是 46 個檔,沒有新增或刪除檔案的痕跡。

### 涵蓋聲明

**這次複查把最終版的 46 個檔又全部核對過一遍**:用 `diff` 逐位元組比對這一版與上一版核對過的版本,確認 43 個檔完全沒有差異(沿用先前已完成的審查結論),3 個有差異的檔(`Issues/尺切換恆等斷言反覆不過.md`、`governance/eval/retrieval_eval.py`、`scripts/test_lumos.py`)則完整讀過變動內容與所在函式全文,並且直接在 repo 裡執行了相關測試子集(`-k eval_`、`-k t_eval_edit_orders_single_source`)驗證行為,不是只看程式碼推論或只看筆記說法。

判定不變。

全篇沒有發現可被利用的漏洞,阻塞項 0 條。
