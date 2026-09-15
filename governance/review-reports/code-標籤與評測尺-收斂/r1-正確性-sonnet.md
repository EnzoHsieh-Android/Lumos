severity: major

# 正確性審查——code-標籤與評測尺-收斂 r1

白話總結先講:這批改動修對了兩個真的問題(綜合排法漏檢未標、恆等斷言比錯分母),而且都補了會翻紅的測試,我親手把修法拆掉驗證過,測試真的會紅。但恆等斷言背後還有一個更底層的洞沒堵——search 面「舊排序」和「新排序」兩個系統天生候選數不一樣多,同一題可能一邊過了新尺的門檻、另一邊沒過,恆等斷言本身抓不到這個,結果就是「切換後真正拿去把關的那個數字」可以被灌水,我用假資料重現出跟團隊自己在事故筆記裡記的那個「131.5% 對 81.9%,差 50 個百分點」同一種形狀的落差。另外測試檔裡那道號稱「硬前置」的 assert,其實只驗了它自己剛設好的東西,不會擋到「main() 內部不理會重導向」這類回歸——我做了一次模擬,assert 照樣放行,程式碼一路跑進 main()。

## 發現一:恆等斷言只保證「同一臂內」新舊尺一致,不保證「新排序」與「舊排序」兩臂比的是同一組題

引句:「★那是兩組不同題目的平均在比★,未標歸零也不可能相等」

這句話是這次修法(`_macro_on`)的立論基礎,講的是「拿全部題的舊尺平均」對「拿有效題的新尺平均」互比不公平。修法把 `_switch_equal` 的五組配對全部改成用同一個 gate_key 限縮兩側(`_rn_eq` 對 `cs["ndcg"]`、`_ln_eq` 對 `cs["ndcg_legacy"]`……),確實堵住了這一種「分母不對齊」。我實際執行過:只要「未標=0」這個前提成立,`_macro_on` 篩出來的子集裡,原始分數與 condensed 分數在數學上必然逐題相等(因為視窗被完整標過,截前 k 的結果跟 condensed 的已判清單截前 k 是同一批節點)——這部分修得對,也有測試釘住。

但恆等斷言的五組配對,每一組都是「同一個系統、同一組被篩選的題,拿新尺跟舊尺比自己」,從來沒有一組是「拿 ranked 的有效題集合去對比 legacy 的有效題集合」。而 search 面真正拿去把關的數字——`condensed_search["lift_pct"]`(切換之後 `search_gate`/`held-out 不倒退` 兩道 gate 直接吃這個值)——恰恰是拿 `c_rn = _macro(srows, "c_ranked_ndcg")` 對 `c_ln = _macro(srows, "c_legacy_ndcg")` 算出來的:

引句:「c_ln, c_rn = _macro(srows, "c_legacy_ndcg"), _macro(srows, "c_ranked_ndcg")」

這兩個 `_macro` 呼叫各自用自己的 key 過濾 None,而「某一題的 c_ranked_ndcg 是不是 None」與「同一題的 c_legacy_ndcg 是不是 None」是兩個獨立判定——因為 `_condense` 的題級門檻(`len(judged) >= ceil(k/2)`,k 是固定的 SEARCH_TOUCH=10,不是該題實際候選數,這是刻意設計,見 `governance/eval/retrieval_eval.py:440` 附近註解)吃的是「這一臂自己」的視窗長度。legacy 與 ranked 是兩個獨立系統(legacy 沒有 `--top` 上限、預設全量輸出;ranked 明確 `--top 10`),同一題兩邊自然抓回的候選數常常不一樣多。我用真實程式碼(未修改)驗證過:一題如果 legacy 只自然抓回 3 個候選、ranked 抓回 10 個,即使兩邊都 100% 標過(未標整體算 0),legacy 那一題仍會因為 3<5(門檻)被判無效、ranked 那一題不會——於是這一題會被算進 `_rn_eq`/`c_rn` 的分子分母,却完全不出現在 `_ln_eq`/`c_ln` 裡,反之亦然。

我拿三題資料重播了一次完整的 `report_goldset` 流程(見下方變異測試表「情境還原」那列):公平版(全部題、含失敗題)算出來的提升是 50.0%,而恆等斷言通過之後拿去把關的 condensed 版本算出來是 100.0%——整整灌水一倍。這不是我編的極端案例形狀:團隊自己在 `Issues/尺切換恆等斷言反覆不過.md` 裡記過「同一份歷史檔裡另有一組數字……某輪新尺預覽的提升幅度 131.5%,同輪舊尺只有 81.9%,差超過 50 個百分點」,拿來當「切換零重錨、門檻不用動」這個說法站不住的證據——這正是我重現出來的同一種形狀(cross-arm 分母不對齊),而這次修的兩個根因(題級門檻、edit 面漏檢視窗)都不是這個機制,所以這次的修法沒有把它堵起來。

實際影響:`_switch_equal` 的五組配對在數學上永遠會通過(只要未標=0),所以它不會攔下這種情況;`condensed_search`/`condensed_edit` 的 lift 一旦在切換之後長期驅動 `search_gate` 與 `held-out 不倒退(lift>0)` 這兩道閘,往後每一輪評測都可能被這個機制悄悄膨脹或壓低,而沒有任何機械訊號會提醒人去查。

severity: major
blocking: 是——這是整條分支的核心安全論證(不可逆切換前必須證明新舊尺恆等),而我用可重現的方式證明了恆等斷言對 search 面的「跨臂」情況完全沒有約束力,且與已知的真實異常數字同形狀,不應該在沒有討論的情況下直接視為已解決。

## 發現二:`t_eval_unjudged_check_honours_cli_k` 那道「硬前置 assert」只驗了測試自己剛設定的環境變數,不驗 main() 有沒有真的遵守它

引句:「導向沒生效就★不准跑到 main★,不然測試翻紅時」

這行註解與旁邊的 assert 一起讀,聲稱的效果是「重導向沒生效就不准進入 main()」。但實際寫法是:

引句:「assert os.environ.get("LUMOS_EVAL_HISTORY", "").startswith(str(root)), \」

這一行的前一行就是 `os.environ["LUMOS_EVAL_HISTORY"] = str(_hist)`,而 `_hist` 本來就是 `root / "fixture-history.jsonl"`。所以這道 assert 檢查的是「我剛剛設定的環境變數,是不是真的被設定成我剛剛設定的樣子」——這在 CPython 裡沒有任何機制會讓它為否,等於恆真。它能且只能擋住「測試自己忘記寫那行重導向」這一種情境(我照著測試自己的翻紅釘描述驗證過,這種情境下 assert 真的會擋下,見下方變異測試表);它完全不能偵測「main() 內部的歷史帳路徑解析不再理會 `LUMOS_EVAL_HISTORY`」這種回歸——而這正是這支測試最初要防的那個 blocker 的真正威脅模型(main() 端的路徑解析出問題,不是測試自己漏寫重導向)。

同一支檔案裡就存在著一個完全不理會 `LUMOS_EVAL_HISTORY` 的路徑當例子:`--auto`(cochange-proxy)模式寫歷史帳時是 `hist = Path(__file__).parent / "retrieval-eval-history.jsonl"`(file: `governance/eval/retrieval_eval.py:789`),完全沒有查環境變數。這條路徑目前沒有任何測試呼叫到(不在這次改動範圍內,我沒有把它算進本項發現的嚴重度),但它證明「main() 的某個進入點不理會重導向」在這支檔案裡是真實存在過的寫法,不是我杜撰的假設。

我做了一次模擬(把 `--goldset` 那條路徑的歷史帳寫入也改成無條件寫死路徑,模擬同類回歸),完整重現這道 assert 的判斷邏輯:assert 照樣通過(因為它驗的是自己剛設定的變數),`m.main()` 被呼叫,fixture 帳(`fixture-history.jsonl`)從頭到尾沒有被建立,而模擬的「正式帳」被寫入了一筆假紀錄——跟 `Issues/尺切換恆等斷言反覆不過.md` 裡記載的那次真實污染事故(「跑一次全套就多一筆假紀錄進受版控的檔……已逐筆清除」)是同一種發生順序:先造成污染,後面的位元組比對才「事後」發現。真正提供保護的是後面那個 `check("★正式的評測歷史帳一個位元都沒被動到★", ...)`,不是這道 assert——但註解把功勞算在 assert 頭上,容易讓之後的人誤以為這裡已經有「事前」防線。

目前 `--goldset` 這條路徑(測試實際走的路徑)確實正確遵守 `LUMOS_EVAL_HISTORY`(file: `governance/eval/retrieval_eval.py:933`),所以今天不會觸發實際污染;這項發現是「安全宣稱與實際機制不符」,不是現在就會出事的功能性錯誤。

severity: minor
blocking: 否——目前實際會被測試呼叫到的路徑(`--goldset`)確實正確遵守重導向,不會造成當下的污染;問題是「assert 硬前置」這個安全宣稱名不副實,建議把這句斷言改成真正驗證 main() 行為(例如比對 main() 內部實際解析出的路徑),或者把註解改成如實反映「真正的防線是事後的位元組比對」,但不需要卡住這次合併。

## 有查但沒找到問題的部分

- **`_edit_orders` 單一實作有沒有漏掉呼叫點**:全檔搜尋只有 `_touched_edit` 與 `eval_edit` 兩處引用 `_edit_orders`,兩處都吃同一個 `split_buckets(res)` 的 `free`,沒有第三處自己另寫排序鍵。`ablation_blocked`、`output_top3_must` 用的是別的、本來就無關排序鍵的邏輯(前者直接呼叫 `collect_unjudged`,後者用的是 impact 原始輸出順序,不是重排序的三條路),沒有混用。
- **未標檢查視窗與計分視窗是否對齊(edit 面 k、search 面 SEARCH_TOUCH)**:`collect_unjudged`、`eval_edit`、`ablation_blocked` 三處呼叫在 main() 裡都吃 `args.k`;search 面兩邊都用模組常數 `SEARCH_TOUCH`,沒有再發現新的不對齊。
- **摘要符號詞彙表合併**:比對修法前後,原本兩處寫死的九個值完全一致、沒有漏值;`PRIOR-ART`/`REVISIT` 有被正確收進單一集合並在兩個使用點(`SYMBOL_RE` 構造、typo 偵測的排除清單)同步使用;放寬後的 `SYMBOLISH_RE` 對含連字號前綴仍要求頭尾都是大寫字母,沒有因為放寬而漏抓純大寫的舊案例。

## 變異測試

以下全部在 `/tmp` 底下的副本上進行(`/tmp/r1review`、`/tmp/r1mut`),沒有修改 repo 內任何檔案;每次修改後都清過 `__pycache__` 才重跑。

| 植入什麼 | 跑哪支(或直接呼叫的函式) | 輸出 |
|---|---|---|
| A:`_edit_orders` 的 fusion 排序鍵從 `x["score"]` 改回 `x.get("score", 0.0)` | 直接呼叫 `_edit_orders([{"node":"Z.md","L":0.1,"kind":"direct"}])`(對應 `t_eval_edit_orders_single_source` 缺 score 那條) | 沒有拋出 `KeyError`,吃到預設值 0.0——對應測試會翻紅 |
| B:`_touched_edit` 改回舊版「只取 free[:k]」 | 直接呼叫 `_touched_edit(res, k=2)`,`res` 取自 `t_eval_touched_edit_covers_all_arms` 的四筆資料 | 只回 `['A.md','B.md']`,只比文字贏家 `C.md`、只比圖贏家 `D.md` 都不在觸及集——對應測試會翻紅 |
| C:main() 兩處 `collect_unjudged(..., k=args.k)` 拿掉 `k=` | 用 `-k 12` 呼叫 `m.main()`,監看 `collect_unjudged` 實際收到的 k | 觀察到 `[8, 8]`(應為 `[12, 12]`)——對應 `t_eval_unjudged_check_honours_cli_k` 的第 2 條斷言會翻紅;未修改版本重跑同一情境確實得到 `[12, 12]` |
| D:`_macro_on` 拿掉 `gate_key` 過濾,等同 `_macro` | 呼叫 `_macro_on(rows, "ranked_ndcg", "c_ranked_ndcg")`,`rows` 取自 `t_eval_switch_equal_same_question_set` | 回 `0.5667`(全題平均),應為 `0.8`(限縮平均)——對應測試會翻紅 |
| E:`_switch_equal` 對兩側皆 `None` 的處理改回 `continue` | 呼叫 `_switch_equal(v_none)`,`v_none` 取自 `t_eval_switch_equal_no_data_is_not_equal` | 回 `(True, [])`,即判定「恆等」,應為 `(False, [...5 條...])`——對應測試會翻紅 |
| 真實測試(未修改)確認上述 A/D/E 三條守衛的正向對照 | `python3 scripts/test_lumos.py -k eval_edit_orders_single_source`、`-k eval_switch_equal`、`-k eval_touched_edit`、`-k eval_eq_keys`、`-k eval_unjudged_check_honours_cli_k`、`-k symbol_vocab_single_source` | 全部通過(共 39 個 check,0 failed),且執行期間確認 `governance/eval/retrieval-eval-history.jsonl` 位元組沒有變動 |
| 情境還原(發現一):3 筆 search 列,一筆 ranked 天生候選少於門檻(視窗自然只有 3 個、全部標過)、一筆 legacy 天生候選少於門檻(視窗自然只有 3 個、全部標過),模擬「兩臂候選數不同」 | 未修改程式碼,直接把 `m.eval_search` 換成回傳這 3 筆的假函式,呼叫真正的 `report_goldset` | 公平版(`_macro(srows,"ranked_ndcg")` 對 `_macro(srows,"legacy_ndcg")`)提升 50.0%;`condensed_search["lift_pct"]` 卻是 100.0%;`_switch_equal` 對 search 那兩組配對回報「無差異」(通過) |
| 情境還原(發現二):模擬 main() 內部歷史帳路徑不理會 `LUMOS_EVAL_HISTORY`(改成寫死路徑,獨立於 repo 的 `/tmp` decoy 檔) | 重播 `t_eval_unjudged_check_honours_cli_k` 的前置 assert 邏輯 + 呼叫 `m.main()` | assert 通過(不擋);`m.main()` 正常執行完;decoy 的「正式帳」被寫入一筆假紀錄,`fixture-history.jsonl` 從未被建立 |

全篇最高等級為重大,其中一條會擋下這次合併。
