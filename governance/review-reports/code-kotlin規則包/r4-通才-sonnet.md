severity: minor

## Finding 1
severity: minor
blocking: 否
review-fp 豁免放寬後,放錯目錄的已知誤報檔也會被放過

引句:「if kind == "good" and Path(f).name.startswith(REVIEW_FP_PREFIX) and rule_id in review_ids:」

`configs/ast-grep/kotlin-android/check.py` 的 `check()`,對應 hunk `@@ -269,34 +289,36 @@`。

失敗場景:舊碼要求 `owner == rule_id`,也就是 `review-fp-*.kt` 只能放在自己規則的目錄下才豁免。現在拿掉這個條件。一個放在 `good/kt-A/` 下的 `review-fp-x.kt`,如果意外命中另一條語意覆核級規則 kt-B,不再被當成「規則 kt-A 的好例誤報」。這個命中會被整個吞掉,不計入 `hits[("good", owner, rule_id)]`。放錯位置的誤報樣本因此不會被自我檢查抓到。

我沒有跑變異來實證這個放過。這裡只做了機制分析,找不到具體的改壞測試。這次新加的 fp 樣本都放在對應規則的目錄下,所以眼前沒有錯誤。

歸因:未判定。我沒取出修前版本,另一條路也沒對照。diff 只顯示這個條件被拿掉。

## Finding 2
severity: minor
blocking: 否
`kt-long-lived-scope-plain-job` 新增的加法分支,對括號裡的加法會誤報

引句:「# 用加法接在後面:CoroutineScope(…) + job(CoroutineScope.plus);$J 要是加法的直接運算元(代碼審 r3 規則席 Finding 3)」

`configs/ast-grep/kotlin-android/rules/coroutines.yml`,新增的 `additive_expression` 分支。

最小重現是 `CoroutineScope(Dispatchers.Main) + (Job() + job)`。其中 `job` 是類別裡的 `SupervisorJob()`,不在加法的直接運算元位置,規則因此報 `kt-long-lived-scope-plain-job`。我用 ast-grep 實跑:

- 命中:`+ (Job() + job)` 的那一行(誤報)。
- 命中:`+ Job()` 的那一行(正確)。
- 不命中:`+ job + CoroutineName("x")`、`+ CoroutineName("x") + job`(正確)。

括號裡再包一層加法的寫法很少見,失敗代價低。

歸因:未判定。這是新分支的邊角,我沒取出修前版本比對。

## 核對修補鏡頭三問
我本席是通才,下面的結論只涵蓋我實際跑的部分。

1. **原問題的修復效果有何行為證據?** 有。
   - 命令:`PATH=…/venv/bin:$PATH python3.14 scripts/test_lumos.py -k kotlin_rulepack_samples`,結果 20 passed, 0 failed,13.9 秒。
   - 命令:`-k kotlin_catalog`,結果 18 passed, 0 failed。
   - 這些測試涵蓋三項:兩條逾時路徑各自只等一次(整次在 2.5 秒內)、缺〈來源縮寫〉節時其他問題照報、「(無)」與其他觸發字並列會報。
   - 這只證明修後測試通過,不是修前會紅。修前版本我沒取出對照,所以「修前紅、修後綠」未判定。

2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 部分成立。
   - `got is None` 現在報「讀不到載入條數」,不再印「載入 None 條」。測試涵蓋這點。
   - 三個設定檔都讀不到時會連報三次相同訊息,冗長但不錯。
   - `_files_block_is_test_only` 先去掉整行註解。規則檔裡的 message 都是單行引號字串,我沒有找到頂格 `#` 被誤刪的情境。
   - 新增加法分支的相鄰寫法(多段加法、反序)結果正確,例外見 Finding 2。

3. **新發現的同一案例在修前、修後各是什麼結果?**
   - Finding 1 和 Finding 2 都只做了修後觀察,修前未判定。

## 未驗範圍
- 沒有跑 `kt-okhttp-response-not-closed` 和 `kt-datastore-read-no-catch` 搬到語意覆核級之後的整體行為,只看到樣本測試通過。
- 逾時測試用 2.5 秒的牆鐘門檻。本機沒有出現失敗,高負載機器上有輕微不穩的可能。我沒有實測。
- 型錄和文件補丁(`r4-pack-docs.patch`)不在我這包材料內,沒有審。

臨時目錄 `/tmp/lumos-seat-work/code-kotlin規則包/通才-sonnet` 已刪除。
