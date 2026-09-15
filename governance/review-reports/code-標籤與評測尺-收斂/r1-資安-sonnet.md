severity: minor

# 資安審查報告 — code-標籤與評測尺-收斂 r1

角色:攻擊者視角,只找能被利用的洞。風格、可讀性、測試覆蓋率不在審查範圍內。

## 審查範圍

被審材料是 `governance/review-reports/code-標籤與評測尺-收斂/r1-snapshot.patch`,46 個檔、4334 行(`e75b883c..HEAD`)。**我已把 46 個檔全部看過一遍**:三支會執行的程式(`governance/eval/retrieval_eval.py`、`scripts/lumos`、`scripts/test_lumos.py`)逐 hunk 全文讀過並對照現有原始碼驗證邏輯;評測題庫/標註者 JSON、`retrieval-eval-history.jsonl`、`.canary-log.jsonl`、`.escape-log.jsonl` 用逐行 diff 檢視內容(找路徑穿越、注入、密鑰、可疑欄位);知識圖譜筆記(Issues/Projects/Systems/Verification/MOC)全部讀過,並額外對全篇跑了注入/秘密/危險指令的關鍵字掃描(`shell=True`、`pickle.load`、`os.system`、`curl|wget`、`rm -rf`、API key 樣式字串、prompt-injection 樣式句子等),沒有漏看的檔案。

## 針對指定攻擊面逐項檢查

### 1. 不可逆切換閘能不能被騙過

這批改動修的正是「未標=0 且新舊尺恆等」這道閘曾經被算錯的兩個缺陷,我逐一驗證修法有沒有真的堵住,而不是只信筆記說法:

- **`_macro_on` 與 `_switch_equal` 的限縮平均**:我對照 `report_goldset` 裡的賦值位置確認 `_rn_eq`(限縮於 `c_ranked_ndcg` 非 None 的題)與 `cs["ndcg"]`(即 `_macro(srows, "c_ranked_ndcg")`,同樣限縮於 `c_ranked_ndcg` 非 None 的題)兩者用的是**同一個列子集**,`_ln_eq` 與 `cs["ndcg_legacy"]` 同理各自成對一致——不存在「拿子集 A 的舊尺平均去比子集 B 的新尺平均」這種可以被operate 出恆等假象的縫隙。
- **兩側同時無資料時的處理**:改動前 `old is None and new is None` 是 `continue`(等於放行);改動後變成明確列進 `diffs`、判定不等。我讀了新增測試 `t_eval_switch_equal_no_data_is_not_equal` 的斷言,行為與程式碼一致,這條路徑已經是 fail-closed,不能靠「兩邊都沒資料」偷渡恆等。
- **edit 面未標視窗只涵蓋綜合排法**的舊漏洞:`_touched_edit` 現在對 `_edit_orders`(fusion/bm25/graph 三條)的前 k 取聯集,和 `eval_edit` 算分用的是同一組 `_edit_orders` 實作,不是各寫一份可能漂移的排序鍵。我用一組人造資料手動走過 `_edit_orders` 與 `_touched_edit` 的邏輯(同分不同 hop、pinned/lane 各種組合),沒有找到「進計分視窗但不進未標檢查視窗」的候選。
- **`-k` 沒有傳進未標判定**的舊漏洞:`main()` 裡驅動切換判定與印 unjudged 的兩處呼叫都已經改成把 `args.k` 傳給 `collect_unjudged`,不再固定用預設的 8;算分那條路本來就走 `args.k`,現在兩邊視窗界線一致。

沒有找到能讓這道不可逆閘被騙過的路徑。

### 2. 判定用的資料來源可不可信(題庫/標註/歷史帳)

- 這次新增/修改的標註資料(`retrieval-goldset.json` 的標註區塊、`governance/eval/raters/*.json`)全部是「節點路徑 → 整數分數 + 說明文字」的簡單字典,沒有新增任何會被當成檔案路徑或指令參數使用的欄位;節點路徑本身都是既有的 `.md` 相對路徑,沒有 `../`、絕對路徑或特殊字元。
- `edit_universe()`(讀 `case["file"]` 拼路徑、呼叫 `lumos impact`)本身**沒有被這份 diff 修改**——它只是作為函式定義出現在 diff 的 hunk 上下文裡,函式體不在改動範圍內,所以就算這裡有路徑處理上的既有疑慮,也不是這份 diff 造成或加重的,不計入本輪判定。
- **`retrieval-eval-history.jsonl` 的清理是否誤刪真實紀錄**:我沒有直接採信筆記的說法,而是自己重新解析這份 diff 的 hunk(`@@ -91,10 +91,15 @@`)——上文 10 行(第 91–100 行既有紀錄)在 diff 裡完全是內容行(沒有 `-` 前綴),代表**這份最終要推出去的 diff 對舊有 100 筆歷史紀錄一行都沒有動、也沒有刪除任何一筆**;新增的只有 5 行(`+`)。我逐行讀了這 5 筆新增紀錄,其中標記 `"metric_switch_verified": true`、`"eval_head": "e75b883c"`、`"metric_rev": "condensed-v1"`、`"unjudged_count": 0`、`"pass": true` 的那一筆,`eval_head` 對得上這條分支真實存在的提交(`git log` 可查到 `e75b883c` = "chore(lumos): 記錄代碼審通過"),不是憑空捏造的短碼。筆記聲稱的「4 筆帶 `34c71678e723`/`k:12` 的假紀錄已被清除」在這份最終 diff 裡也確實找不到任何 `34c71678` 或 `"k": 12` 的痕跡——也就是說,這份要推出去的 diff 本身乾淨,沒有殘留假紀錄,也沒有動到真實舊紀錄。

### 3. 容錯改拋錯(`_edit_orders` 對 `x["score"]` 不給預設值)是否製造可被利用的阻斷

這處把原本 `x.get("score", 0.0)` 改成硬性 `x["score"]`,缺欄位就丟 `KeyError`。我追了這條資料的來源:`_edit_orders` 只吃 `split_buckets()` 分出來的 `free`(非 pinned、非 lane)集合,而這個集合的原始資料來自 `edit_universe()` 呼叫 `lumos impact --ranked --json` 的輸出。我在 `scripts/lumos` 裡逐一核對所有會進入 `results`(進而變成 `free`)的分支——incident 固定席、direct 固定/非固定、indirect 固定/非固定、rescued、lane——**每一個分支都明確寫死 `"score": ...`**(見 `file: scripts/lumos:9696`、`file: scripts/lumos:23227`、`file: scripts/lumos:23254`、`file: scripts/lumos:23263`),沒有任何分支會產出缺 `score` 的候選。這個輸出不是外部使用者可以直接餵任意 JSON 進來的介面,而是同一支工具鏈自己 subprocess 呼叫自己產生的結構化輸出。也就是說:
- 正常操作下這條路徑不會被觸發;
- 就算未來某個上游改動意外讓 `score`消失,效果是評測流程整支崩潰、非零退出碼、**不寫入歷史帳**(寫檔在 `main()` 最後一行,例外會在那之前中止),結果是擋下這一輪判定而不是誤放行——方向上是保守失效,不是「阻斷用來規避判定」。

severity: minor
blocking: 否——攻擊面高度受限(只有 lumos 自己的 `impact --ranked` 輸出格式,不是外部可控輸入),觸發後果是保守的整輪失敗(不寫歷史帳、不誤放行),不會被用來繞過或搶先寫入不可逆的尺切換旗標;純粹記錄成一個值得留意的可用性取捨,不是這份 diff 引入的可被利用漏洞。

引句:「★缺 score 就讓它炸,不要給預設值★(2026-09-15 code-r3 正確性席):」

### 4. 測試裡的 assert 硬前置(`t_eval_unjudged_check_honours_cli_k`)會不會被繞過或讓測試靜默略過

這支新測試在呼叫會 append 檔案的 `main()` 之前,先把 `LUMOS_EVAL_HISTORY` 導向 fixture 目錄,再用 `assert` 檢查這個環境變數確實指向 fixture、指不到就直接讓測試因未捕捉的 `AssertionError` 中止(不會跑到 `main()`)。我確認了兩件事:
- 這個 `assert` 檢查的是**它自己前一行剛設定好的環境變數**,本質上是一個自我核對用的保險絲,真正的防護是那行 `os.environ["LUMOS_EVAL_HISTORY"] = str(_hist)`;
- Python 若以 `python -O`(最佳化模式)執行,所有 `assert` 語句會被直接剝除、變成沒有作用的空陳述式。若那個環境變數重導邏輯本身出了 bug(例如 `root`/`_hist` 算錯),在 `-O` 模式下這道保險絲不會發作,測試會直接往下跑,重演這支測試原本要防的那個嚴重問題(往受版控的正式 `retrieval-eval-history.jsonl` 追加假紀錄)。
- 我查了 CLAUDE.md 與這個 repo 記載的測試跑法(`python3 scripts/test_lumos.py -k <關鍵字>`),沒有任何地方要求或建議用 `-O` 執行,這不是這個專案的實際操作模式,純屬理論上的防禦縱深缺口。

severity: minor
blocking: 否——實際防護來自賦值那一行而非 assert 本身,且這個專案的既定跑法不使用 `-O`;在正常執行路徑下沒有可被利用的繞過方式,只是把它記下來,建議未來若要加固可以把這道檢查從 `assert` 換成一般 `if...raise`(不受 `-O` 影響)。

引句:「assert os.environ.get("LUMOS_EVAL_HISTORY", "").startswith(str(root)), \」

### 5. 新程式是否引入路徑組合/子行程/正則回溯/反序列化風險,或印出不該印的東西

- `scripts/lumos` 這次唯一的邏輯改動是把 `SYMBOL_RE`/`SYMBOLISH_RE` 兩個正則改成從固定字面集合 `SYMBOL_NAMES` 生成,集合內容是寫死的字串常數,不吃任何外部輸入,不存在正則注入問題;`SYMBOLISH_RE` 新寫法 `^([A-Z][A-Z-]*[A-Z]):` 是單一字元類重複、沒有巢狀量詞,不構成災難性回溯(ReDoS)風險。
- 沒有發現新增的 `subprocess`/`os.system` 呼叫帶有可被外部輸入拼接的參數;既有的 subprocess 呼叫(`pin_snapshot`、`_lum`)不在本次改動範圍內。
- 沒有發現任何新增的 `pickle`/`yaml.load`/反序列化呼叫。
- 對全篇做了密鑰/憑證樣式掃描(API key、私鑰標頭、長 base64 token 等),沒有命中。
- 沒有發現任何嘗試對閱讀這批筆記的 AI 下指令的字句(掃描「忽略先前指令」「你現在是」等提示注入樣式,無命中)。

## 未列入阻塞判定的既有/流程性觀察(範圍外,僅供參考)

圖譜筆記 `Issues/編排者改寫席位引句.md` 記載了上一輪代碼審(`code-標籤與評測尺` r2)裡編排者曾經竄改審查席引句去對齊事後重生的凍結快照的事故,並且明寫「目前沒有任何東西擋住編排者編輯席報告」。這是審查流程本身的機制缺口,已經被記錄且訂了 REVISIT(2026-10-15),既不是這份 diff 裡的程式改動造成的,擋下這份 diff 也不會讓這個缺口變好或變壞,所以不影響本輪判定,只是提醒後續要看那個 REVISIT 有沒有兌現。

## 結論

沒有找到能被外部輸入或惡意資料騙過「未標=0 且新舊尺恆等」這道不可逆切換閘的路徑;歷史帳清理經我自己重新解析 diff hunk 核對,沒有動到真實舊紀錄,新增的切換紀錄提交編號可查驗為真;容錯改拋錯與測試前置 assert 兩處各記一條輕微問題,皆不構成阻塞、也都不是這份 diff 引入的可被利用漏洞。全篇最高等級為輕微,阻塞 0 條。
