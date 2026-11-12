severity: minor

審查範圍是 `594f97e..6d53943`。修後 worktree 在 `6d5394398`,git 狀態乾淨,我只在自己的臨時 worktree 改壞型錄,用完已移除。

## 1. 〈叫不出的壞寫法〉標註行的「整行只有註記」只認一層括號,計劃沒寫這個限制
severity: minor
blocking: 否
引句:「_ANNOTATION_ONLY_RE = re.compile(r"^\s*(?:@[\w.:]+(?:\([^()]*\))?\s*)+$")」
file: `/Users/enzo/harness/lumos-d4-triggers/configs/ast-grep/kotlin-android/check.py`(`_ANNOTATION_ONLY_RE`、`_bad_lines`);計劃〈範圍〉`規則 <id>` 一條寫「整行只有 `@` 註記的行跳過」,沒提括號深度,見 `/Users/enzo/harness/lumos-d4-triggers/docs/lumos-toolchain-knowledge/Projects/情境決策點窮舉與壞寫法要叫得出_計劃.md`。
失敗場景:壞例檔寫 `// BAD:x` 後面接 `@Foo(Bar(1))` 再接 `fun z() = 3`,或接多行註記 `@Suppress(` 換行 `"a"` 換行 `)`。
- 修前:BAD 標到第 3 行 `fun z() = 3`。
- 修後:BAD 標到第 2 行 `@Foo(Bar(1))`;多行註記標到 `@Suppress(`。
- 影響:接手者照計劃寫巢狀括號註記,片段比對會落在註記行,「規則」改由查不到而報錯。
- 範圍:`samples/bad/` 全部目錄修前修後輸出一致(diff 0),所以目前真資料不受影響,只是文件與程式不一致。
歸因:有證據的修復回歸(只限巢狀括號註記這一類)。
查證命令:同一份臨時壞例檔,分別用修前 `check_old.py`(取自 `594f97e`)與修後 `check.py` 呼叫 `_bad_lines`。修前輸出 `[(3,'fun z() = 3'),(6,'""')]`,修後輸出 `[(2,'@Foo(Bar(1))'),(5,'@Suppress(')]`。多行註記修前本來就標歪(第 6 行 `""`),所以多行這一類算原有的洞;巢狀括號這一類才是修補造成的。

## 2. 新 WHY 行的代價只寫 flatMapConcat,沒寫這次一起放寬的 flatMapMerge
severity: minor
blocking: 否
引句:「[代價:搜尋框誤用 flatMapConcat 又答例外時,推送前不提醒,只靠盲判抓]」
file: `/Users/enzo/harness/lumos-d4-triggers/docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md`(新 WHY 行);型錄 D-4 例外證據樣式在 `/Users/enzo/harness/lumos-d4-triggers/skills/kotlin-idioms/checks-catalog.md:733` 一帶。
失敗場景:例外證據樣式現在是 `\.collect\s*\{|\bChannel\b|\bflatMapConcat\b|\bflatMapMerge\b`。搜尋框用 `query.flatMapMerge { repo.search(it) }` 且答「例外」時,證據樣式照樣比得到,推送前同樣不提醒。這個漏洞是本次修補才新增的,代價卻沒寫。接手者讀筆記會以為只有 flatMapConcat 這一條漏。
補充:同一行的 `[不選:…也對不上(證據樣式無法從一行程式判出搜尋框還是上傳)]` 句意不通,看不出「不選」的是什麼。
歸因:有證據的修復回歸(文字只寫了一半)。修前樣式沒有 flatMapMerge,patch 的 D-4 hunk 可見;修後樣式含它,修後型錄實測可見。

## 三問的答案

① 原問題的修復效果,各案例的證據如下。
- D-4 例外:在修後 worktree 把例外樣式的 `\bflatMapMerge\b` 拿掉,`-k evidence_samples` 變 24 過 1 紅。紅的是正例「alt-ok 每一次都要做完、順序不重要:flatMapMerge 並行上傳」,`--catalog-only` 同時報 1 個問題。所以新樣本與例外樣式互相綁住。
- 修後原樣跑:`evidence_samples` 25 過、`evidence_patterns` 11 過、`bad_snippets_reach` 47 過、`template_fence_parity` 22 過、`api_decision_points` 38 過、`--catalog-only` 0 個問題。
- 這些數字與驗證紀錄寫的一致。反查單位另外數過:111 個叫不出,其中代碼審 104、規則 5、不是寫法 2。API 決策點 434 個也對得上:D-n 62、撞名 4、決策不問 18、代碼審 95、無決策 266。
- 82 列套版理由「觸發字比對不到這段片段」:我用 `_kt_trigger_re` 逐列把該情境列的每個觸發字套在片段上,0 列比對得到,所以改寫後的說法對每一列都成立。
- flatMapMerge 當例外成立:它並行、不保序、有 concurrency 上限(預設 16),「順序不重要時並行做完」說得通,樣本也帶了 `concurrency = 4`。
- 新寫的行為(換頁字元、字串裡的 `// BAD`、U+2028、沒關的圍欄)我沒另外重現,只確認它們所在的測試組通過。

② 修補處的相鄰路徑,結果如下。
- 既有 `// BAD` 標法照舊:對 `samples/bad/` 全部目錄比修前修後的 `_bad_lines`,輸出完全相同。
- 單獨一行 `@Foo` 註記照樣跳過;巢狀括號註記是問題 1 說的唯一退步。

③ 新發現的同一案例修前修後各是什麼結果,已分別寫在問題 1、2 的歸因行。

兩項已判定的核對:
- `jvm-only.txt` 檔頭指的計劃〈天花板〉第 2 條存在,其中有「JVM 專屬的類別成員與屬性不收」,說法一致。
- `Default` 那列改寫後,「CO-1 的片段寫 Dispatchers.IO、不含這個名稱」與型錄第 282 列相符。

未驗範圍:沒跑全套測試、沒跑帶 ast-grep 的 `--sg` 模式;驗證紀錄裡 `kt_catalog` 310、`kt_situation` 145、`kotlin_rulepack_samples` 29 等數字沒重跑。

總結:最高等級 minor,共 2 條
