severity: major

審查席:合約圖譜(sonnet),第 2 輪。範圍是 `r2-pack-docs.patch`,對照 `r2-repair.patch` 與 repo 現況(`73276ca7b`)。

我發現工作樹的 `configs/ast-grep/kotlin-android/check.py` 在我審查期間被別人改動過。`_DIR_SEVERITY` 的 `rules-hints` 被改成 `("hint", "info")`,`git diff` 看得到。像是別的席在做變異實驗。我一律以 HEAD 版本為準判斷,沒有動它。

**核對過、對得上的**
- 規則包 207 條。用 `load_rules()` 與 `grep -c '^id:'` 都數到 `rules/` 150(error 30、warning 120)、`rules-review/` 7(info)、`rules-hints/` 50(hint)。統計節寫的「207(error 30、warning 120、語意覆核級 info 7、hint 50)」全中。
- 「被會擋的規則守到的列數 132」我用程式數也是 132。
- 型錄 473 列、各主題列數、形狀 367、語意 106、人裁 3、決策表 56 列,都相符。
- 型錄、規則包節點、母計劃、第三批計劃、新計劃提到的 `kt-` 規則 id,都在規則包裡。
- 已刪的兩條(`kt-register-pair-missing`、`kt-viewmodel-depends-on-api-dao`)只出現在型錄 ARCH-35、ARCH-49 的「已併入」說明。
- `kt-situation`、`kt-springdata` 是棧別題,不是規則包規則。
- 摘要行的 `[test:]` 測試名都存在:`t_kotlin_catalog_rows_wired`、`t_kotlin_rulepack_messages_cite_catalog`、`t_kotlin_rulepack_samples`。後者的改壞步驟已改成 `**/src/test*/**`,和 r1 指出的紅燈不再相同。
- `lumos lint` 對新計劃、`Systems/kotlin規則包`、第三批計劃都是 0 問題。
- 上輪已修:母計劃與 linter 目錄的 `src/test*` 錨、型錄「40 條」改 35、API-1 與 STATE-16 的過期實測句、TEST-33 標出處不全。

severity: major
blocking: 是
類型:修補引入
引句:「cd /Users/enzo/orca/workspaces/lumos-toolchain/shearwater && python3.14 scripts/lumos lint "規則包語意覆核級命中走盲判_計劃" | tail -2」
新計劃檔 `規則包語意覆核級命中走盲判_計劃.md` 的結尾混進了一段工具呼叫殘渣。第 7 條「統計門檻」後面接了 `</content></invoke><invoke name="Bash"><parameter name="command">cd … lumos lint …`。最後沒有換行。
重現:`tail -8 docs/lumos-toolchain-knowledge/Projects/規則包語意覆核級命中走盲判_計劃.md`。輸出最後四行是 `</content>`、`</invoke>`、`<invoke name="Bash">`、`<parameter name="command">…lumos lint "規則包語意覆核級命中走盲判_計劃" | tail -2`。
`lumos lint` 抓不到這種髒東西,所以 0 問題。
這是已提交檔案的內容損壞。下一個讀圖譜的 AI 會把它當正文,也可能照著執行。要刪掉那四行。

severity: minor
blocking: 否
類型:修補引入
引句:「出處不全的列:28;人裁的列:3」
統計節的出處不全寫 28,實數是 29。這輪把 TEST-33 補標「(出處不全)」,但統計節沒重算。
我用 `check.py` 的 `_cells` 數主表名稱欄含「(出處不全)」的列,得 29。
母計劃實作紀錄寫的「共 28 列」也是舊數。
統計節自稱「用程式讀本檔……得出」,卻沒有任何測試守這一行。
原本應該標的「引用它們的 5 條規則降提示級」是否仍是 5,沒有重算依據,文件也沒交代。

severity: minor
blocking: 否
類型:修補引入
引句:「接在第三批的盲判機制,[[Projects/Android寫法語意情境表態與盲判_計劃]]),第三批上線前不擋」
母計劃、`check.py` 與新拆出計劃對「語意覆核級」的描述不一致。
母計劃(實作紀錄,diff 內)和 `check.py` 第 21 行註解都說命中由第三批盲判機制接手。
但同一批 diff 裡,第三批計劃的「不做」已寫明拆到 [[Projects/規則包語意覆核級命中走盲判_計劃]]。型錄通電批次欄、`Systems/kotlin規則包` 也指向新計劃。
照母計劃做的人會去第三批計劃找實作,找不到。「第三批上線前不擋」也變成誤導,因為第三批已不含這項。
要把母計劃與 `check.py` 註解改指新計劃。

severity: minor
blocking: 否
類型:上輪沒看的角落
引句:「`rules/`、`rules-hints/` 底下的 yml 依型錄主題分檔」
`Systems/kotlin規則包` 同一節的檔案清單漏了 `rules-review/`。同檔稍早才新增 `sgconfig-review.yml` 那條。
`check.py` 的模組說明寫「讀兩個規則目錄」,「一條規則都沒讀到」的訊息也只提 `rules/` 與 `rules-hints/`。實作其實有三個目錄。
我沒有重現會做錯的後果,只是措辭落後。

severity: minor
blocking: 否
類型:上輪沒看的角落
引句:「自寫 semgrep(提示級)」
型錄 API-1 的「現成規則」欄還寫 semgrep。r1 已指出 semgrep 版不存在,實作改成 ast-grep 規則 `kt-sequential-independent-await`。
這輪只改了該列的實測狀態欄,現成規則欄漏改。
母計劃範圍 2 與範圍 4 的 semgrep 字樣也還在,靠實作紀錄的一條補註交代,可接受。

severity: minor
blocking: 否
類型:上輪沒看的角落
引句:「告警帶寫法=語意覆核級(規則包語意覆核級命中走盲判_計劃接上前不擋)」
通電批次欄的「語意覆核級」是新增的取值,型錄〈輸入與口徑〉沒有定義,`catalog_problems` 也只查通電批次欄非空。
標記並不齊,而且實測狀態欄的說法有問題:
- TEST-5 把會擋的 `kt-test-tolist-not-background` 與覆核級的 `kt-runtest-launch-collect-forever` 併列,通電批次只寫「批一」,實測狀態欄沒標後者是覆核級。API-11 則有標。file: `skills/kotlin-idioms/checks-catalog.md:583`。
- STATE-1、STATE-7、STATE-16 的實測狀態寫「樣本實測中壞例、好例不報」。但這些規則的好例目錄裡有 7 個 `review-fp-*.kt`,是故意會命中的。`check.py` 還特地豁免。字面上與實況相反。file: `skills/kotlin-idioms/checks-catalog.md:232`。

總結:數字與規則 id 大致可信(207 條與四個等級、132、473、56 全中),主要問題是新計劃檔尾混進工具呼叫殘渣必須刪(major),其餘是修補後沒重算的統計(出處不全 28 應為 29)與「語意覆核級」在母計劃、`check.py`、`Systems/kotlin規則包` 之間的描述落差。
