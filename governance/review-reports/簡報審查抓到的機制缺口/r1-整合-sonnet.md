severity: major

# 外部審稿:簡報審查抓到的機制缺口_計劃(r1 整合席)

先說白話:這份計劃想補四個洞,但「人工標記調高風險」沒有真的把審查變嚴,「忽略註解進閘」放行一次就能無聲複製,README 實驗句又抄了二手摘要的過度宣稱。計劃更漏列了一整串講分級和放行的文件。以下依序列出。

引用的外部頁面我都抓過:LifecycleService、MediaSessionService、ProcessLifecycleOwner、coroutines-views、SonarQube tracking-inline-comments 的字句都對得上。內部引用的節點、函式、測試名都存在。壞引用沒有。

## 逐條 finding

1. **S2 人工標記只逼出「要有留痕」,不逼出「審得深」**(範圍 2、驗收 S2)
引句:「推送時以 `code-loop check` 為準」
severity: major
blocking: 是,計劃宣稱的價值(人能把風險調高)沒有被任何檢查兜住。
   - 範圍 2 寫「推送時以 `code-loop check` 為準」。但 `code-loop check` 只看留痕是 passed 或 skipped,且 sha 相符。
   - 它不比對那次迴圈定錨的分級。file: `scripts/lumos:75394`(`_codeloop_guard_verdict` 第 4 步)只讀 status 與 head_sha。
   - 輕量迴圈(`--tier light`、零輪次)會被 `_codeloop_pass_shape` 當輕量放行,照樣記出 passed。file: `scripts/lumos:72345`。
   - 同一次推送裡,`spec-gate --push-check` 在計劃風險低時會印「代碼審只派架構對齊席;lumos loop next <編號> --tier light」。file: `scripts/lumos:17341`。
   - 後果:人標了 `Lumos-Risk: high`,編排者照 push-check 開 light 迴圈,推送照過。計劃只講了「不生效處」是 `loop next` 與 push-check 的標籤,沒講 check 收 light 留痕這個縫。
   - S2 的測試只在 `_pitfall_tier` 函式層,沒有 check 端到端的條款。

2. **S2 的 high 牽動的下游沒列,而且推送掛鉤的提示文字對人工標記是錯的**(範圍 2、不生效處)
引句:「生效處:`pitfalls --diff` 的輸出與推送閘的 `code-loop check`(它開子程序跑 pitfalls 取 tier)」
severity: major
blocking: 是,同一個「判 high」在別處會觸發計劃沒列的硬行為。
   - 合約測試從只提醒變成硬擋:pre-push 只在 `_tier_high=0` 時才帶 `--bound-tests-advisory`。file: `scripts/hooks/pre-push:634`。
   - `stack_questions.gate = high-only` 的專案,high 會讓表態閘生效,Kotlin 還要情境題盲判。file: `scripts/lumos:74880`、`scripts/lumos:65579`。
   - 定錨 high 的迴圈必須有資安席,否則處置閘判不過。file: `skills/lumos-code-loop/SKILL.md:33`。
   - 掛鉤在 tier=high 時印死文案:「這次推送的程式碼裡有高風險寫法(像是沒包交易的寫入…),tier=high。命中的地方列在下面」。file: `scripts/hooks/pre-push:574-580`。只改文件加標記時,那份清單是空的,文案是假的。
   - 測試範圍不跟著升:docs 子集只看 `suite`(`scripts/hooks/pre-push:606-615`、`.github/workflows/ci.yml:93-97`)。「只改文件也照 high」的推送,測試仍是子集,計劃沒講這一點。

3. **S4 把二手摘要的過度宣稱抄進 README,而「照原始紀錄寫」沒做到**(範圍 4、依據來源、S4)
引句:「標明以程式碼為準後回到 20/25、筆記正確時還沒量」
severity: major
blocking: 是,公開 README 的實驗結論會比原始紀錄講得更肯定。
   - 計劃的依據是 `Projects/Lumos定位_程式碼為主脈絡為輔_計劃` 的表格,那是二手摘要。原始紀錄 `圖譜效用受控實驗_計劃` 與 `Verification/2026-09-19_受控實驗程式碼為主四組對照` 在 lumos-gvc 工作樹,不在本 repo。
   - 驗證紀錄有一節標題:「丙組那個 20 要打折扣」。
   - 它寫「丙組的 L02 5/5 可能有運氣成分」,「丙+丁 17/25」,以及「有標籤被帶歪 4 場、沒標籤 9 場,方向一致但不到能下定論」。
   - 丙組也不是只加了旁註,而是「乙 + 旁註 + grep 指令」,乙組本身只有 15。
   - 計劃要中英兩版寫「標明以程式碼為準後回到 20 場」,沒有任何保留語。
   - S4 只是 manual,要求對照二手摘要,所以過度宣稱的版本照樣算過。
   - 次要:「Opus 不受影響」比原始紀錄「對 Opus 在天花板」強。
   - 單位「25 場」查原始紀錄是對的(五題各五場),這一點沒問題。

4. **S3 放行綁「規則+檔名+行內容」,第一次放行後同檔相同的忽略行全部無聲通過**(範圍 3、實務隱患)
引句:「同一行改了別的字但留著 `# noqa`,會被算成新加的一條,要再放行一次」
severity: major
blocking: 是,計劃要解的「不留紀錄地繞過」在最常見的重複寫法上仍然成立。
   - `_lint_new_diff_claims` 先按指紋算次數差,再用 `kept = [c for c in new if c.get("key") not in waivers]` 只看 key。file: `scripts/lumos:43267`(`_lint_new_tools`)。
   - 指紋是 `_lint_new_key`(`scripts/lumos:42830`)的「規則+檔+整行文字」,沒有出現序號。
   - 同檔複製貼上的 `except Exception as e:  # noqa: BLE001` 因此只需放行一次。本 repo 的 `scripts/test_lumos.py:56534`、`:57172` 就是同縮排的同一行。
   - 計劃的實務隱患只講「改一行就算新增」,沒講反方向。
   - 另一個放大器:型錄標準接法對 `kt` 宣告兩條 detekt 命令(`Projects/Android現成檢查接上CI與推送前_計劃` 範圍 2)。
   - 計劃寫「一條命令可以同時認到多個工具」,卻沒處理「多條命令認到同一工具」。同一行 `@Suppress(` 會算成兩條同指紋的新增告警。
   - 驗收 S3 停在「多出一條告警」,沒有擋下後經 `lint-waive` 放行的條款。

5. **S3 掛在 `_lint_new_run_cmds`,同時改了「回合結束」收工鉤子那條路,計劃沒提**(範圍 3、lands_in)
引句:「掛點在每條命令真的跑完、記進已跑清單之後(沒跑的、只報不擋的命令不數)」
severity: major
blocking: 是,擋下 AI 每回合收工的行為變了,卻沒條款、沒落點。
   - `_lint_new_run_cmds` 有兩個呼叫端:推送範圍模式 `scripts/lumos:43263`,以及工作樹模式 `scripts/lumos:41607`(`_lint_new_wt_verdict`)。
   - 工作樹模式是 `Systems/回合結束寫法檢查` 的 stop-lint 鉤子在用。
   - 該節點 RULE 寫「收工自動執行的檢查命令只准 lumos 寫死的 ast-grep 白名單形狀」。接上後,AI 在回合內加 `// ast-grep-ignore` 會被收工擋停,擋停訊息叫它「先修」,但此時修法是移除或放行。
   - 該節點既不在 lands_in,S3 也沒有工作樹模式的條款。

6. **S1 的驗收無法驗到它宣稱的東西**(驗收 S1、預期值表第 4 列、範圍 1)
引句:「只看那一層類別,不看裡面的內部類別」
severity: major
blocking: 是,條款字面上驗不到。
   - `t_kotlin_rulepack_samples` 在本機沒有 ast-grep 時只跑靜態半,印「本機沒有 ast-grep…CI 會跑樣本」就 return。file: `scripts/test_lumos.py:126841-126845`。本機也沒裝 ast-grep。
   - 樣本判定是按目錄計數:壞例至少 2 處、好例 0 處、好例至少 2 段。file: `configs/ast-grep/kotlin-android/check.py:1075-1084`。
   - 預期值表第 4 列的「同一支檔裡 SettingsFragment 照報」做不出來。會被報的 Fragment 不能放好例目錄。放壞例目錄時,同檔的 Service「不報」沒有任何斷言,因為只數命中數。
   - 範圍 1 的「只看那一層類別,不看裡面的內部類別」沒有對應的樣本和條款。Fragment 巢在 Service 裡,與 Service 內層類別的區別全沒驗。「祖先任一層」和「最近一層」兩種實作都會綠。
   - 計劃連「外層」或「最近一層」都沒定義清楚。

7. **會被改變卻沒列一起改的文件**(整份,用戶指定的重點)
引句:「型錄 STATE-5 那列補一句適用範圍」
severity: major
blocking: 是,下列句子改完就是錯的,或沒人找得到新功能。
   - `skills/lumos-code-loop/SKILL.md:12`:「light 有兩個機械來源:改動裡沒有程式檔(只有文件/圖/資料)」。S2 之後,只改文件帶標記是 high。
   - `skills/lumos-code-loop/SKILL.md:12` 同時沒說 high 的來源可以是人工標記。
   - `skills/lumos-project-notes/commands/06-代碼審與推送.md:5`:「這批改動風險多高?」那列只有 `pitfalls`,沒有「想手動調高」的入口。整份文件沒有任何一處教人寫 `Lumos-Risk`。
   - `docs/指令參考.md:129`(`pitfalls --diff` 的說明)寫「(standard / high)」,已漏 light,也沒人工標記。
   - `README.md:196` 與 `README.en.md:196`:「先判風險:推送前用固定規則掃這次新增的程式碼」。圖 `assets/risk-review-zh.svg`、`assets/risk-review-en.svg` 也畫同一種。
   - `docs/指令參考.md:140` 與 `cmd_lint_waive` docstring(`scripts/lumos:41843`):「新增告警閘擋下的是誤報」。忽略註解被擋時不是誤報,是要求寫理由。
   - `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:63`:「殘留索引升 high 最先判」與計劃範圍 2「`_pitfall_tier` 最先讀」互相打架。
   - `Systems/linter精選目錄` 的工具菜單與計劃的七工具對照表沒有同步守衛,見 finding 10。
   - lands_in 只有 `Systems/kotlin規則包` 和 `Systems/pitfalls-code-loop`。

8. **回退節與 PRIOR-ART 殘留舊設計用詞,正規式與文字不一致**(PRIOR-ART ②、回退、範圍 2)
引句:「人工調高風險:拿掉分級函式讀 trailer 那一段;已寫進提交訊息的 trailer 不影響任何東西」
severity: minor
blocking: 否,文字層級的不一致,不影響行為。
   - 回退寫「拿掉分級函式讀 trailer 那一段;已寫進提交訊息的 trailer 不影響任何東西」,但設計明說不照 trailer 認。這是舊稿殘留。
   - PRIOR-ART 寫「大小寫、連字號、底線、空白都不拘」,正規式 `lumos[-_ ]?risk` 只容許零或一個分隔字元。`Lumos  Risk`、`Lumos--Risk` 不會中。
   - 多行都中時理由取哪一行沒定義。

9. **「最先」的順序與失敗方向跟同函式既有慣例相反,沒說明**(範圍 2、實務隱患「讀不到提交就不升」)
引句:「分級函式 `_pitfall_tier` 最先讀這次範圍內每個提交的完整訊息」
severity: minor
blocking: 否,不影響已定義的行為,但行為有缺。
   - 既有 `_pitfall_tier` 最先判殘留索引,理由句裡帶修法,如 `lumos guard residual --reindex`。file: `scripts/lumos:64523`。
   - 若人工標記先判且提早 return,同時命中殘留時修法理由會消失。計劃沒說是合併還是蓋掉。
   - 同族測試 `t_pitfalls_residual_git_failures` 的規則是「git 出錯一律往多升 high」。計劃對新來源反過來「讀不到就不升」,沒交代為何不同。
   - 範圍 2 用 `_diff_range_ends`,而同函式已經用 `_range_base` 取起點。前者對單一版本回終點 None,計劃沒定義那種輸入。

10. **忽略寫法對照表本身有已知缺口,連本 repo 自己的工具都有**(範圍 3、天花板)
引句:「工具與寫法的對照:ast-grep→`ast-grep-ignore`;ruff→`noqa`;eslint→`eslint-disable`」
severity: minor
blocking: 否,天花板已承認「換寫法就認不出」,但具體缺口今天就存在。
   - 我在本機 ruff 0.16.7 實跑:`import os  # NOQA` 與 `# NoQA: F401` 都被 ruff 認作抑制,即大小寫不拘。計劃 S3 沒寫大小寫規則,S2 卻寫了不分大小寫。
   - `# ruff: disable[F401]` 這種範圍抑制也生效,字串裡沒有 `noqa`,表裡抓不到。
   - 菜單 `Systems/linter精選目錄` 推薦的 biome、mypy(`# type: ignore`)、bandit(`# nosec`)、ktlint 都不在對照表。

11. **Kotlin 的 `@Suppress(` 範圍太寬,量沒估**(範圍 3、實務隱患)
引句:「detekt→`@Suppress(`、`@file:Suppress(`、`@SuppressWarnings(`」
severity: minor
blocking: 否,有放行出口,代價是摩擦。
   - 計劃只用本 repo 的 ruff 量「量小」。
   - `@Suppress("UNCHECKED_CAST")`、`@Suppress("DEPRECATION")` 是 Kotlin 編譯器警告,不是 detekt 的抑制,卻照算新增告警。
   - 新檔含大量這類行時,每行一條指紋,`lint-waive` 一次只收一條。

12. **RETIRE-IF ②③ 沒有量法**(RETIRE-IF、REVISIT)
引句:「②半年內沒有任何一次推送讀到 Lumos-Risk 標記 → 檢討是否改成別的人工入口或拿掉」
severity: minor
blocking: 否,撤除條件寫了但量不出來。
   - ② 的「半年內沒有任何一次推送讀到標記」。`_pitfall_tier` 不寫事件,也沒有計數。
   - 「順手提到也算」讓任何討論這功能的提交都算一次,所以用歷史提交數量永遠不會是零。
   - ③ 的「誤認筆數」。放行紀錄的欄位只有 key、rule、file、reason、by、ts、origin、acked,見 `scripts/lumos:42908`。沒有誤認標記,也沒存行內容。
   - 計劃只有 ③ 掛了 REVISIT。
   - 實作提交自己會在 `scripts/lumos` 加對照表,含 `noqa` 字樣,會被 ruff 命令算成新增告警。這也是 ③ 的誤認,卻沒有預告。

13. **天花板少算了放行路徑,也沒提標記會在壓提交時掉光**(天花板、實務隱患)
引句:「推送閘在兩種情況不跑 pitfalls、直接當 standard(推送起點等於現在、算不出推送起點)」
severity: minor
blocking: 否,補寫即可。
   - 「推送閘在兩種情況不跑 pitfalls」。`_codeloop_guard_verdict` 還有:取不到 HEAD sha、算不出 merge-base、pitfalls 非零或例外,三條也 fail-open。
   - 專案規定「做到一半的本機提交,推之前壓成一個」。標記寫在被壓掉的 wip 提交訊息裡就消失,這是少審方向的靜默失效,計劃只談「寫錯格式是多審」。

14. **ProcessLifecycleOwner 的豁免依據是推論,官方頁沒這句**(範圍 1、依據來源第 3 列)
引句:「ProcessLifecycleOwner 官方說明:整個 App 程序的生命週期」
severity: minor
blocking: 否,是設計取捨的證據問題,不是明確錯誤。⚠
   - 依據只引「whole application process」。同頁寫它是 all Activities 的合成,START/RESUME 隨前景進出,STOP 延遲。
   - 官方頁並沒有說它「不是畫面」。「Service 不是畫面」那一列有據,Process 這列沒有。
   - 結果是 `ProcessLifecycleOwner.get().lifecycleScope.launch { collect }` 以後永遠不報,包含 App 進背景仍在收。

15. **引用的決策 d7 自己已經作廢**(依據來源第 6 列、預期值表 S2 第 3 列)
引句:「本 repo 先前 [[Projects/進度從提交推導_計劃]] 用過 trailer,後來翻案(d7)」
severity: minor
blocking: 否,論點仍成立,只是出處標示不準。
   - `進度從提交推導_計劃` 的 d7 標 `valid: false`、`superseded_by: d8`(之後 d10、d12)。
   - 計劃寫「後來翻案(d7)」,沒講 d7 本身也被翻。

16. **S3 告警的訊息與欄位沒定義**(範圍 3)
引句:「當成規則名 `lumos-inline-suppression` 的告警,跟工具本身的告警一起比差」
severity: minor
blocking: 否,實作期補。
   - 擋下訊息與工作樹 JSON 都讀 `message`、`file`、`line`、`rule`(`_lint_new_wt_json`、`_lint_new_key` 弱比對退到訊息)。
   - 計劃沒寫 `lumos-inline-suppression` 告警的訊息要告訴人什麼,「請寫理由放行或移除忽略」。
   - 預期值表 S4 寫死「第 450 行」,README 一改就漂。

## 各節已讀情況

- **標頭、PRIOR-ART、RETIRE-IF**:finding 8、12、15。
- **用詞**:已讀,無 finding。「這次範圍」的單一版本與三點細節見 finding 9。
- **範圍 1**:finding 6、14。
- **範圍 2**:finding 1、2、8、9、13。
- **範圍 3**:finding 4、5、10、11、16。
- **範圍 4**:finding 3。
- **不做**:已讀,無 finding。
- **實務隱患**:finding 4、11、12、13。
- **依據來源**:finding 3、14、15。其餘外部引文逐字核對無誤。
- **驗收條款、預期值表**:finding 1、3、6、16。
- **回退**:finding 8。
- **天花板、REVISIT**:finding 12、13。

## 實驗清理

我的暫存目錄已用字面絕對路徑刪除。

最嚴重 major,blocking 共 7 條(finding 1–7)。
