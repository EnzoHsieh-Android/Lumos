severity: major

## 逐節結論

- 白話、PRIOR-ART、RETIRE-IF:見 F11。
- 用詞、範圍 1–3:見 F1、F2、F3、F4、F9、F12。
- 範圍 4(盲判):見 F5、F6、F7。
- 範圍 5、6 與〈實務隱患〉:見 F7、F8、F10、F11。
- 驗收條款、回退、天花板:已讀,沒有獨立的 finding。S1–S7 缺的案例分別掛在 F2、F3、F5、F6 底下。

## Findings

### F1 觸發字的把關不存在,現行型錄已違反
severity: major
blocking: 是(違反「一般常用字不准當觸發字」的前提,實作後每次 kt 改動都會出一堆題)
spec 段落:〈用詞〉情境題、〈實務隱患〉常用字當觸發字。
問題:spec 把「不收常用字」整個外包給第一批。第一批的 S3 沒有停用字表。現行型錄〈情境決策表〉已有 56 列,觸發字就含常用字。
引句:「停用字表與檢查由第一批的型錄格式檢查承接」
查證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/docs/lumos-toolchain-knowledge/Projects/Android協程與API寫法機械檢查標準_計劃.md:105`。S3 只要求「每列有列編號與觸發字」,全文 grep 不到「停用」。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/skills/kotlin-idioms/checks-catalog.md:666`。觸發字收了 `flow`、`first`、`take`、`key`、`test`、`version`、`size`、`token`、`edit`、`Unit`、`Result`、`Exception`、`Application`、`Intent`、`remember`、`collect`、`map`、`launch`、`catch`。只要改動行有 `remember` 或 `collect`,D-5、D-13、D-15、D-26、D-30 就會同時命中。
- 觸發字的分隔符不一致:D-1 到 D-21 用「、」,D-22 起用「, 」。
- 含點、空白、連字號的觸發字(`Dispatchers.IO`、`suspend fun`、`proguard-rules`、`chain.proceed`)怎麼跳脫、空白怎麼比,spec 只寫「整詞比對(自己加字界)」,沒說。
- 這個前提沒人擔,RETIRE-IF ③「命中少於 5 次」會永遠不成立,盲判成本也會爆。

### F2 `android_only` 標了也不會生效
severity: major
blocking: 是(Spring 伺服端 Kotlin 專案會被問 Android 情境題)
spec 段落:〈用詞〉情境題、範圍 2。
問題:spec 說情境題「標 `android_only`」,又說情境題不放進 `_STACK_QUESTION_SPECS`,只在四處各接一次。但平台排除是從 `_STACK_QUESTION_SPECS["kt"]` 撈 `android_only` 的題號。情境題不在那張表裡,排除集合裡就不會有它們。
引句:「並標 `android_only`」
查證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/lumos:37848`。`frozenset(sp["id"] for sp in _STACK_QUESTION_SPECS.get("kt", []) if sp.get("android_only"))`。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/lumos:38190`。`_stack_applicability` 靠 exclude 在這裡消化。
- `_stack_platform_excluded` 是第五個要接線的地方,spec 沒列。
- 驗收條款也沒有「伺服端 kt 檔不出情境題」的案例。

### F3 證據樣式的語意沒定義,有幾列根本寫不出正向特徵
severity: major
blocking: 是(S2 的核對規則不能照 spec 實作)
spec 段落:〈用詞〉證據樣式、表態對程式。
問題:
1. `;`(AND)、`|`(OR)和「各一到三條正規式」之間的關係沒說。範例同時用了 `;` 和 `|`。
2. 決策表現在沒有「證據樣式」欄,欄位順序、分隔符都要新定,而 `,` 已經被觸發字欄用掉。
3. 好幾列的標準寫法是「不要寫某樣東西」或「順序」,沒有一定會出現的字面特徵:
   - D-2:循序呼叫,不要包 `async{}.await()`。
   - D-12、D-14 的「不需要共享就不共享」。
   - D-20 的「不要在呼叫端多包一層」。
   - D-34:Modifier 順序。
4. 「前後各 3 行」的窗太窄。D-1 的標準寫法跨 `async` 宣告到 `.await()` 好幾行,實際排版很容易超過 7 行。
5. `alt` 在 D-1、D-2、D-8 等列的「不適用時」是「見下一列」,改用的是別列的寫法。作者標 D-1/alt,盲判會判成 D-2,在機器看來是 row 不一致。
6. 既有 `_ev` 對 satisfied 也收 `test:<名>`。spec 只說「單一 path:line」,沒說情境題收到 `test:` 時怎麼處理。
引句:「窗裡要有一條符合那列那個 variant 的證據樣式」
查證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/skills/kotlin-idioms/checks-catalog.md:668`。D-1 的「不適用時」寫「見下一列」。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/skills/kotlin-idioms/checks-catalog.md:669`。D-2 的標準寫法是「不要包」。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/lumos:70065`。`test:` 證據在既有驗證裡是合法的。

### F4 改填 tension 或 todo 就能整個繞過,而 tension 恰好是 spec 指定的出口
severity: major
blocking: 是(使用者的原始顧慮「寫了但完全沒參考」被一個狀態切換打穿)
spec 段落:範圍 3、範圍 4 出口。
問題:
- tension 與 todo 都不比證據樣式,也不比盲判。
- tension 只要 `existing` 1 到 20 個 path:line 加兩段過門檻的文字。`chosen=existing` 連 evidence 都不用。
- 盲判不一致時,spec 的出口就是「改成 tension」,所以 tension 數會被盲判分歧灌水。
- RETIRE-IF ② 把 tension 比例讀成「證據樣式誤擋」,是兩種成因混在一起的指標。要到上線八週後才看得到,中間沒有任何機械檢查。
引句:「todo、tension 照既有規則,不跟盲判比」
引句:「某一列的作者表態裡 tension(作者主張證據樣式誤擋)超過該列命中的一成」
查證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/lumos:70097`。tension 的 `existing` 形狀驗證只驗 path:line 是否存在。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/lumos:70722`。tension 驗完就 `return None`。
- 缺口:沒有任何規則限制 tension 的 existing 必須指向「同一列寫法」的既有程式。
- 驗收條款 S4 只測「合法 tension 不擋並印 ⚠」,沒有反向案例。

### F5 盲判記錄的格式與綁定不足,sha256 可能永遠對不上
severity: major
blocking: 是(照 spec 實作,推送前常態性擋下)
spec 段落:範圍 4。
問題:
1. 結果 JSON 每題只有 `{id,row,followed,evidence,reason}`,沒有 sha256 或批次編號。`blind-judge <結果.json>` 怎麼知道它回答的是哪一批材料?
2. `--template` 有 `--diff <範圍>`,寫入指令沒有。也沒說像表態那樣帶 `--branch`、`--at-sha`。
3. 材料(程式段、前後文)從工作樹讀還是從被推的版本讀,沒說。工作樹有未提交改動,或 merge-base 因 fetch、rebase 前進,重算的 sha256 就不同。
4. 結果裡的 `evidence` 沒人驗。盲判給的 `row` 若不在候選列裡,也沒驗。
5. 同一題有多筆盲判記錄(重跑)時取哪一筆,沒說。
6. 仲裁記錄怎麼對應到第一個盲判,沒說。
引句:「記錄綁目標版本與材料 sha256」
查證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/lumos:70152`。表態事件綁 `branch` 與 `head_sha`。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/lumos:70620`。`_dispositions_verdict` 對工作樹與被推版本有明確的 `at_sha` 區分。
- S3 驗收只測「sha256 對不上要擋」,沒測「同範圍重算要穩定」。

### F6 三方多數決有缺口
severity: minor
blocking: 否(實作時會被迫補規則,但不會讓閘放過錯誤)
spec 段落:範圍 4 推送前核對。
問題:
- 作者 D-1,盲判 D-1 但 `followed=false`,仲裁也判 D-1 且 `followed=true`:算不算「跟作者一致」?
- 作者 satisfied D-1,盲判 none:盲判有 `followed` 但沒有 variant,`alt` 怎麼比?
- 三方都不同,但其中兩方 row 相同而 followed 不同:算多數嗎?
引句:「不一致的題要有一筆仲裁盲判」
查證:S4 的案例都是 row 相異,沒有 row 相同而 followed 相異的案例。

### F7 手冊操作與派工材料對不上
severity: major
blocking: 是(編排者照手冊會卡住或洩漏答案)
spec 段落:範圍 4、範圍 5、〈實務隱患〉盲判被帶風向。
問題:
1. spec 說 `--template` 輸出原樣當派工材料,又說一題一份材料。但 `--template` 印的是整批 JSON(最多 8 萬字)加一個批級 sha256。「一題一份」怎麼切、結果怎麼彙總成一個符合批 sha256 的結果檔,沒說。
2. 既有手冊的派工鏡頭會「把這份表態附進派工單」。盲判席走哪條派工路徑、怎麼確保不吃到這段,spec 只靠「手冊寫明禁止」。
3. 手冊現況沒有任何盲判步驟,這份計劃的〈範圍〉也沒寫手冊要改成什麼步驟順序。以下幾種情況盲判記錄要怎麼補,都沒說:
   - `skip` 流程。
   - 修正輪後記錄過期。
   - 推 `HEAD:別名`。
引句:「盲判席用 sonnet,一題一份材料」
引句:「派工詞由 `--template` 的輸出原樣當材料」
查證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/skills/lumos-code-loop/SKILL.md:25`。「派工鏡頭會把這份表態附進派工單」。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/skills/lumos-code-loop/SKILL.md:20`。表態步驟寫在派審查員之前。

### F8 跟第一批與第二批計劃的分工既有重疊也有矛盾
severity: major
blocking: 是(三份計劃的合約互相打架,後做的一份必須改別人的計劃)
spec 段落:範圍 5、〈實務隱患〉跟第二批改同一道表態閘、範圍 1。
問題:
1. 第一批寫批三要把命中情境觸發字的改動以 light 等級拉進迴圈,並多派一席「情境盲判席」。本案卻是分級不動,靠推送前核記錄。兩種機制沒有對齊,也沒說誰覆蓋誰。
2. 第二批的範圍 5 把「新增告警」與「表態」兩道抽成共用函式,`pass` 與推送共用。本案把盲判核對「加在表態那一道裡」,正是第二批抽出的那個函式。spec 卻寫「兩邊改的函式不重疊」,不成立。
3. 第二批自己新寫一套 Kotlin 註解與字串剝除和整詞、分大小寫的比對。本案沿用既有 `_stack_norm_line`,spec 自己寫它剝不掉多行註解與無空白的行尾註解。兩案只共用「讀表」,比對實作兩套。同一個觸發字在改檔前鉤子和推送閘可能一邊命中、一邊不命中。
引句:「分級不動(有 kt 改動本來就至少 standard)」
引句:「兩邊改的函式不重疊」
查證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/docs/lumos-toolchain-knowledge/Projects/Android協程與API寫法機械檢查標準_計劃.md:79`。批三 light 拉進迴圈加情境盲判席。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/docs/lumos-toolchain-knowledge/Projects/Android寫法寫完當下自動檢查_計劃.md:68`。第二批自寫比對。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/docs/lumos-toolchain-knowledge/Projects/Android寫法寫完當下自動檢查_計劃.md:73`。第二批抽出共用函式。

### F9 每次 kt 推送會多出 56 筆自動 na,模板與帳都被灌水
severity: minor
blocking: 否(可用性與帳本膨脹問題,不影響判定正確)
spec 段落:範圍 2。
問題:`_dispositions_template` 對 meta 裡每個未適用的列都產生一筆 `auto` na,理由從 `_STACK_QUESTION_SPECS[棧]` 查。情境題若進 meta,模板會多 56 筆。理由欄也會是空的「未觸發:」,因為情境題不在那張表裡。spec 沒說未觸發的情境題是否進 meta 與模板。
引句:「另有一張第一次用到才讀型錄的情境題表」
查證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/lumos:70800`。

### F10 「語意列必進決策表」的宣稱沒有人驗,型錄現況已有 6 列例外
severity: minor
blocking: 否
spec 段落:〈用詞〉情境題最後一句。
問題:spec 說沒被決策表引用的語意列只能是「出處不全」或「人裁」,並說由第一批格式檢查驗。但第一批 S3 沒有這條檢查。型錄現況有 6 列語意列沒被引用:UI-110、DATA-21、DATA-65、DATA-66、DATA-67、PERF-26。它們的接電方式都寫「表態對程式、盲判席」,實際不會出任何情境題,所以那兩種接電是空的。
引句:「第一批型錄格式檢查驗」
查證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/docs/lumos-toolchain-knowledge/Projects/Android協程與API寫法機械檢查標準_計劃.md:105`。S3 沒有這條。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/skills/kotlin-idioms/checks-catalog.md`。上述 6 列。

### F11 統計口徑與停用條件有水分
severity: minor
blocking: 否
spec 段落:範圍 6、RETIRE-IF。
問題:
- 表態在帳上是每筆事件各算,`--carry` 與重表態會重複算同一題。「命中 ≥ 20 次」和 kappa 的樣本數沒說去重(同版本只算最後一筆),會灌水。
- 多筆盲判記錄與表態配對的鍵(版本)沒定。
- ⚠ 需實測:kappa 在只有 `row` 加 `none` 的類別、單列樣本很小時不穩定。spec 只寫公式,沒寫樣本量門檻,RETIRE-IF ① 的 kappa ≥ 0.9 在 20 筆上幾乎沒有解釋力。
引句:「作者與盲判一致度(相符率與 Cohen's kappa,類別=row 加 none)」
查證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/lumos:16735`。既有統計只對 `carried` 排除背書分母,命中計數沒去重。

### F12 型錄版本在作者機器與 CI 之間可能不一致
severity: minor
blocking: 否(⚠ 只查到來源解析方式,沒驗過 CI 實際怎麼裝 lumos)
spec 段落:範圍 1。
問題:題目集合由 lumos 安裝位置的型錄動態決定。作者本機(`$LUMOS_HOME` 或 `~/harness/lumos-toolchain`)和 CI 的工具鏈版本不同時,適用題集合就不同。CI 會擋作者沒看過的題號或列。spec 沒要求把型錄版本或雜湊記進表態與盲判記錄,也沒有版本不符時的訊息。
引句:「lumos 從自己的安裝位置讀這張表」
查證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/lumos:32596`。來源是 `--source`、`$LUMOS_HOME`、`~/harness/lumos-toolchain`。

最嚴重 severity:major;blocking 共 6 條(F1、F2、F3、F4、F5、F7、F8 中 F1、F2、F3、F4、F5、F7、F8 皆為 blocking:是,實為 7 條)。

更正結尾:blocking 為「是」的共 7 條(F1、F2、F3、F4、F5、F7、F8),其餘 5 條(F6、F9、F10、F11、F12)為 minor。

最嚴重 major,blocking 共 7 條。
