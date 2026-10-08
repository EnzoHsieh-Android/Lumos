severity: major

### F1

severity: major  
blocking: 是  
判定: agree；附一項 concern，不改原席等級。

引句：「硬合約要求修 bug 的翻紅測試先證明目標情境確實成立；但下列測試都是執行產品後才斷言結果」

**觀察**

固定提交 `cd0ae310ccf1609a56a2552374eab47b13c55882` 的 AST 記憶體探針確認：

- 控制字元：產品呼叫在 `governance/eval/test_review_convergence.py:199`，此前無獨立 assert。
- token 型別衝突：產品呼叫在 `governance/eval/test_review_convergence.py:217`，此前無獨立 assert。
- 十萬零一筆：`governance/eval/test_review_convergence.py:230` 只有結果型 `assertRaises`，產品呼叫在 `:231`；此前無獨立前置 assert。

**判準**

concern：AST 找不到 assert，只能證明「缺少指定語法守衛」，不能單獨證明現場沒有成立或測試必然無效。最小反證是三者都以程式直接建立情境：

- 控制字元直接組入資料並寫檔：`governance/eval/test_review_convergence.py:194`、`:198`
- `int`／`bool` 衝突直接建 fixture：`governance/eval/test_review_convergence.py:213`、`:215`
- 精確寫入 100001 筆：`governance/eval/test_review_convergence.py:229`

因此，「無 assert ⇒ 現場未成立／守衛無效」推論不成立；AST 也不能證明守衛有效。

但硬合約明文要求必須配一條前置斷言，見 `governance/review-reports/code-review-convergence-eval/r3-graph-lens.txt:12`。三支測試均未符合，所以 F1 的 **major／blocking 維持成立**；不因作者願意補寫而視為已修。