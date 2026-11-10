severity: major

審查範圍:逐節讀完整份 spec,對照 `scripts/lumos`、`scripts/hooks/pre-push`、`state.yml` 與兩個樣本檔。實驗都在 `/tmp/lumos-seat-work/簡報審查抓到的機制缺口/正確性-sonnet/` 做完,已刪。

## Findings

1. **人工標記會把別人的提交算進來(合過主線後,範圍不只是自己的提交)**
severity: major
   blocking: 是,spec 自己寫的「範圍外的提交不算」在合過主線的推送上不成立,實作者照 `git log 起點..終點` 做就會誤升 high,判準是會做出壞系統。
   - 段落:〈範圍〉2、〈實務隱患〉「順手提到也算」、〈用詞〉這次範圍。
   - 問題:增量推送的範圍是 `遠端舊值..本地頂端`(`scripts/hooks/pre-push` 的 `pp_range_for`)。分支合過主線再推時,這個範圍會含主線上別人的提交。spec 的取捨只算到「實作這個功能的提交本身」,沒算到它進主線之後的傳播。
   - 輸入:主線上有提交訊息提到 `Lumos-Risk`,例如本功能的 feat 提交,或 GitHub 的 `Merge pull request … from …/lumos-risk-…`。另一條純文件的分支合進主線後增量推送,範圍含那筆提交。分級被判 high,理由寫「人工標記高風險」,要走一輪代碼審或 `code-loop skip`。這個使用者常有多條並行分支,每條合主線後的第一次推送都會中。
   - 重現:我用暫存 repo 實跑,`git log 舊頂端..HEAD` 含主線那筆「Lumos-Risk」提交。
   - 既有呼應:`scripts/lumos` 對表態那道已經特地用 `merge-base(主線, at_sha)..at_sha` 避開(「推送範圍…會把主線帶進來的碼算成本次要表態」)。tier 那一行寫「照舊用推送範圍」。同一族問題是 open 的 `Issues/推送前其他閘的範圍在合過主線時會多算`,spec 沒提。
   - 缺口:spec 沒定義遇到合併提交與主線提交時怎麼讀(只讀自己這側、`--first-parent` 還是排除主線可達的提交)。`t_pitfall_tier_human_high` 也沒有合過主線的案例。
   引句:「提交訊息裡只是提到 Lumos-Risk 這個詞(例如實作這個功能的提交本身),也會被判 high」
   file: `scripts/lumos:75341` 附近的註解寫明 tier 用推送範圍,表態另用 merge-base 範圍。

2. **「空樹起點不升」跟 `git log 起點..終點` 的實際行為相反**
severity: major
   blocking: 是,spec 列的保證在它規定的機制下不成立,實作者會被矛盾指示卡住或悄悄多升。
   - 段落:〈實務隱患〉「讀不到提交就不升」對〈範圍〉2 的讀法。
   - 問題:spec 把「範圍起點是空樹」當成「git 讀不出訊息」。實跑 `git log 4b825dc642cb6eb9a060e54bf8d69288fbee4904..HEAD` 回傳碼是 0,而且列出整段歷史(暫存 repo 4 筆全列)。只有全零或不存在的 40 位十六進位才報 `Invalid revision range`(rc 128)。
   - 輸入:`pp_range_for` 在遠端舊值全零,或本機找不到舊頂端(強推)時給 `空樹..本地頂端`。`pp_block_range_for` 的 `push-range` 失敗時也退回空樹。`_codeloop_guard_verdict` 對起點等於 `_EMPTY_TREE_SHA` 的範圍不改寫。照 spec 做,整個 repo 歷史上只要有任何一筆訊息提過 `Lumos-Risk`,這類推送一律被升 high,理由指向一筆古早提交。
   - 缺口:先紅測試沒有空樹案例。實作者要特判 `_EMPTY_TREE_SHA`,spec 沒寫。
   引句:「起點不是一個提交(例如新分支首推、範圍起點是空樹)、git 讀不出訊息時,分級照原本算,不會因為人工標記升級。」
   file: `scripts/lumos:75283` 起點是 `_EMPTY_TREE_SHA` 時不改寫範圍。

3. **S1「同一支檔裡 Fragment 照報」被綁定測試放過**
severity: major
   blocking: 是,spec 把驗收綁在抓不到該壞法的測試上。整檔豁免的實作會讓規則在含 Service 的檔裡對所有收集靜默,而測試仍綠。
   - 段落:〈驗收條款〉S1、預期值表第 4 列、樣本。
   - 問題:`check.py` 對壞例只數命中處數(`if n < 2`),不看哪一行、不看標記。壞例檔(`samples/bad/…/kt-lifecycle-collect-without-repeat.kt`)裡根本沒有 Service 類別。檔內註解寫「Service 檔案裡的 Fragment 照樣要報」,但 `FeedFragment` 已有 3 處命中,`SettingsFragment` 命中與否不影響 ≥2。
   - 重現:我寫了「檔內任一 class 直接繼承三個 Service 名之一就整檔不報」的 ast-grep 規則加 Process 豁免,跑真樣本。好例命中 0、壞例命中 4,都合格。同一規則跑 Service 加 Fragment 同檔的檔,結果零命中。
   - 缺口:要綁住這句話,壞例檔必須同時放一個 Service 類別和一個會被報的 Fragment,並且要有逐行斷言(目前只有計數)。
   引句:「同一支檔裡 Fragment 的收集 應 照報 [test:t_kotlin_rulepack_samples]」

4. **「只看那一層類別,不看裡面的內部類別」有兩種讀法,結果不同**
severity: minor
   blocking: 否,只影響內部類別這種罕見結構。
   - 段落:〈範圍〉1 的認法。
   - 問題:最直覺的 ast-grep 寫法是 `not: inside: <繼承 Service 的 class_declaration> stopBy: end`(祖先式)。我實跑它,`class SyncService : LifecycleService() { inner class Panel : Fragment() { … lifecycleScope.launch { vm.state.collect {} } } }` 裡的 Panel 收集不再被報。改成「最近的外層類別決定」才會報。
   - 缺口:還有三處 spec 沒定。完整限定名 `androidx.lifecycle.LifecycleService()`(`^LifecycleService` 的寫法認不得)、`MediaSessionService(), Foo` 多重繼承清單、`object : …`。實作者要自己選。
   引句:「類別宣告的直接繼承清單裡有這三個名字之一,只看那一層類別,不看裡面的內部類別」

5. **ProcessLifecycleOwner 例外無條件套在 Fragment/Activity 裡**
severity: minor
   blocking: 否,範圍小,spec 天花板有承認「判斷不了該不該在背景跑」。
   - 段落:〈範圍〉1 ②。
   - 輸入:`class LeakyFragment : Fragment() { … ProcessLifecycleOwner.get().lifecycleScope.launch { vm.state.collect { binding.title.text = it } } }`。我用現行規則實跑,這行現在會報。照 spec 例外之後不報,但這種收集進程活著就不會停,會漏掉 Fragment 的 view。
   - 缺口:「外層類別是畫面類別」是機械可判的,spec 沒收窄。
   引句:「②`ProcessLifecycleOwner.get().lifecycleScope` 的收集」

6. **對照表漏掉 ruff 已存在的寫法,天花板沒給回頭條件**
severity: minor
   blocking: 否,spec 天花板承認認不全,但漏的是現行版本已有的寫法。
   - 段落:〈範圍〉3 的對照、〈天花板〉第 3 條。
   - 實測:本機 ruff 0.16.7(CI 釘同版 `.github/workflows/ci.yml:73`)。`import os  # NOQA` 和 `# NoQA: F401` 照樣被忽略,字面比對 `noqa` 認不得(spec 沒寫大小寫規則)。`# ruff: disable[F401]` 這種區段忽略也生效,整行沒有 `noqa`。本 repo 的 `lint.json` 正是用 ruff。
   - 缺口:天花板那句是承認風險的話,依專案鐵則 4 該搬成獨立的回頭條件行。目前 REVISIT 只查放行筆數,不查漏認。
   引句:「ast-grep→`ast-grep-ignore`;ruff→`noqa`;eslint→`eslint-disable`」

7. **`lumos[-_ ]?risk` 跟「都不拘」對不上,寫錯仍會靜默失效**
severity: minor
   blocking: 否,少數輸入,但正是 d7 想避免的靜默失敗。
   - 段落:PRIOR-ART ②、〈範圍〉2。
   - 輸入:`Lumos  Risk: high`(兩個空白)、全形空白 `Lumos　Risk`(中文輸入法常見)、`Lumos – Risk`。分隔字元只有一個可選字元,這些都不匹配,結果是標記悄悄沒作用。
   - 缺口:散文說「大小寫、連字號、底線、空白都不拘」,正規式只涵蓋單一分隔字元。要不改散文,要不放寬正規式。
   引句:「大小寫、連字號、底線、空白都不拘」

8. **RETIRE-IF ② 沒有計數來源**
severity: minor
   blocking: 否。
   - 段落:RETIRE-IF ②、〈範圍〉2。
   - 問題:〈範圍〉2 沒有為「推送讀到標記」寫任何帳或事件(spec 只改 `_pitfall_tier` 的回傳)。「半年內沒有任何一次推送讀到」在消費專案裡無法機械判定。
   - 補充:RETIRE-IF ③ 只算「字串常數或說明文字」的誤認。Kotlin 裡 `@Suppress("UNCHECKED_CAST")`、`@Suppress("DEPRECATION")` 這類編譯器警告抑制(不是 detekt 的)也會被 `@Suppress(` 字面比對算成新增,每個都要放行一次。這是更常見的誤認來源,但沒進度量口徑。
   引句:「半年內沒有任何一次推送讀到 Lumos-Risk 標記 → 檢討是否改成別的人工入口或拿掉」

9. **回退段用詞跟設計矛盾,且引用的決策已失效**
severity: minor
   blocking: 否。
   - 段落:〈回退〉、PRIOR-ART ②。
   - 問題:回退寫「拿掉分級函式讀 trailer 那一段;已寫進提交訊息的 trailer…」,但設計明講不照 trailer 格式認。另外 PRIOR-ART 與預期值表引用的 d7,在 `Projects/進度從提交推導_計劃.md` 的 d7(第 77 行)是 `valid: false`、`superseded_by: d8`。引用文字本身仍在,但讀的人會以為它是有效決策。
   引句:「人工調高風險:拿掉分級函式讀 trailer 那一段;已寫進提交訊息的 trailer 不影響任何東西。」

10. **單一版本範圍沒定義終點**
severity: minor
    blocking: 否,文件裡的用法幾乎都是 `A..HEAD`。
    - 段落:〈用詞〉這次範圍。
    - 問題:`_diff_range_ends` 對 `pitfalls --diff HEAD~2` 這種單一版本回 `(HEAD~2, None)`。spec 只講兩點與三點,沒說終點為 None 時讀 `HEAD` 還是不讀,實作者要自己決定,不讀就讓標記悄悄失效。
    引句:「兩點(`A..B`)或三點(`A...B`,起點取共同祖先)都先用 `_diff_range_ends` 拆成起點與終點」

## 逐節與資料狀態五問

- 逐節:前言、PRIOR-ART、用詞、範圍 4(README)、不做、依據來源已讀。範圍 4 的 README 兩版第 450 行已是新句,數字與 `圖譜效用受控實驗_計劃` 一致(Haiku 4.5、12/25 對 20/25),無 finding。S4 的 manual 核對對象(Lumos定位 計劃)只寫「Haiku」,沒有「4.5」,實際出處在 `lumos-gvc` 工作樹,屬可追溯性小缺口,不單列。交叉引用的目標都存在。引用的 LifecycleService 事實我用官方頁驗過:`MediaSessionService extends LifecycleService`,直接與間接子類別與 spec 寫的一致。
- 新舊互讀:全 repo 4286 筆提交無任何「lumos risk」字樣(grep),本 repo 現況沒有舊訊息誤升。舊放行檔沒有 `lumos-inline-suppression`,不互相影響。傳播風險見 finding 1 與 2。
- 寫一半:閘的快照是暫存目錄,沒有新增的半成品狀態。提交訊息還沒存在時讀不到,屬正常。
- 衍生資料:`tier_reason` 會原樣帶進人可讀輸出與 JSON 的「那行字樣後面的字」,沒有長度或字元上限。依 lumos 威脅模型(單人)不算安全 finding,不列。
- 時間:REVISIT 2027-05-09 日期合格。RETIRE-IF ② 缺計數(finding 8)。
- 不可逆:放行紀錄與已推上去的提交訊息不可撤。回退段「整段還原就回到原狀」對放行紀錄成立(讀取端移除即失效),對提交歷史裡已有的標記不成立,但移除讀取後也不再影響分級。

## 實務隱患鏡頭

- 金流、對外送出:無,spec 已排除,我也沒找到走到這兩類的路徑。
- 併發:放行檔讀改寫沿用 `_vault_write_lock`,無新增風險。合併提交的讀取範圍見 finding 1。
- 效能與記憶體:`git log` 沒有筆數與長度上限。空樹起點會讀整段歷史,本 repo 4286 筆量級可接受,但 spec 沒有上限(併入 finding 2)。
- 守衛面:標記升 high 同時帶來合約測試改硬擋(`bound_advisory` 在 tier=high 時不適用)與 `high-only` 表態閘啟用,這些都隨 tier 走,spec 只寫了代碼審。不另列,因為是既有行為的延伸。

最嚴重 severity 是 major,blocking 共 3 條(finding 1、2、3)。
